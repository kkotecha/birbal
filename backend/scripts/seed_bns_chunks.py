"""
Script to chunk and upload BNS sections to Supabase with embeddings.
Creates multiple embeddings per section for better semantic search.

Usage: python scripts/seed_bns_chunks.py data/bns_sections_PRODUCTION.json
"""

import json
import sys
from pathlib import Path
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_openai import OpenAIEmbeddings
from tools.supabase_client import get_supabase_client
from config import EMBEDDING_MODEL


def create_chunks(section: dict) -> List[Dict]:
    """
    Create searchable chunks from a BNS section.

    Strategy:
    1. Main chunk: Title + full_text + keywords
    2. Subsection chunks: Each subsection separately
    3. Illustration chunks: Each illustration separately
    """
    chunks = []
    metadata = section['metadata']

    # Chunk 1: Main section (for broad matching)
    main_text = f"{section['title']}\n\n{section['full_text']}"
    if metadata.get('keywords'):
        main_text += f"\n\nKeywords: {', '.join(metadata['keywords'])}"

    chunks.append({
        'chunk_id': section['section_number'],
        'chunk_type': 'main',
        'chunk_text': main_text,
        'metadata': metadata
    })

    # Chunk 2-N: Subsections (for specific provision matching)
    for subsection in section.get('subsections', []):
        chunk_text = f"{section['title']} - {subsection['id']}\n\n{subsection['text']}"

        chunks.append({
            'chunk_id': subsection['id'],
            'chunk_type': 'subsection',
            'chunk_text': chunk_text,
            'metadata': {**metadata, 'subsection_level': subsection['level']}
        })

    # Chunk N+1: Illustrations (for example-based matching)
    for i, illustration in enumerate(section.get('illustrations', []), 1):
        chunk_text = f"{section['title']} - Illustration {i}\n\n{illustration['text']}"

        chunks.append({
            'chunk_id': f"{section['section_number']}_ill_{i}",
            'chunk_type': 'illustration',
            'chunk_text': chunk_text,
            'metadata': metadata
        })

    return chunks


def seed_bns_chunks(json_file_path: str):
    """Upload BNS sections as chunks with embeddings to Supabase"""

    print(f"Loading BNS data from {json_file_path}...")

    with open(json_file_path, 'r', encoding='utf-8') as f:
        sections = json.load(f)

    print(f"Found {len(sections)} sections")

    # Initialize
    embeddings_model = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    supabase = get_supabase_client()

    total_chunks = 0

    for i, section in enumerate(sections, 1):
        print(f"\n[{i}/{len(sections)}] Processing Section {section['section_number']}: {section['title']}")

        # Create chunks
        chunks = create_chunks(section)
        print(f"  Created {len(chunks)} chunks")

        # Process each chunk
        for chunk in chunks:
            # Generate embedding
            embedding = embeddings_model.embed_query(chunk['chunk_text'])

            # Prepare insert data
            insert_data = {
                'section_number': section['section_number'],
                'chunk_id': chunk['chunk_id'],
                'chunk_type': chunk['chunk_type'],
                'chunk_text': chunk['chunk_text'],
                'metadata': chunk['metadata'],
                'embedding': embedding
            }

            # Insert into Supabase
            try:
                supabase.table('bns_chunks').insert(insert_data).execute()
                total_chunks += 1
                print(f"    ✓ {chunk['chunk_type']}: {chunk['chunk_id']}")

            except Exception as e:
                print(f"    ✗ Error on {chunk['chunk_id']}: {e}")

    print(f"\n{'='*60}")
    print(f"✅ Successfully uploaded {total_chunks} chunks from {len(sections)} sections!")
    print(f"{'='*60}")

    # Also seed the main bns_sections table (without embeddings, just for reference)
    print(f"\nSeeding main bns_sections table for reference...")
    for section in sections:
        try:
            supabase.table('bns_sections').insert({
                'section_number': section['section_number'],
                'title': section['title'],
                'full_text': section['full_text'],
                'subsections': section.get('subsections', []),
                'illustrations': section.get('illustrations', []),
                'explanations': section.get('explanations', []),
                'metadata': section['metadata']
            }).execute()
        except Exception as e:
            # Ignore if already exists
            pass

    print("✓ Main table seeded")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/seed_bns_chunks.py data/bns_sections_PRODUCTION.json")
        sys.exit(1)

    json_file = sys.argv[1]
    seed_bns_chunks(json_file)
