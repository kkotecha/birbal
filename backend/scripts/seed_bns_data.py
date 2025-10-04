"""
Script to upload BNS sections to Supabase with embeddings.
Run once after setting up database.

Usage: python scripts/seed_bns_data.py data/bns_sections_PRODUCTION.json
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_openai import OpenAIEmbeddings
from tools.supabase_client import get_supabase_client
from config import EMBEDDING_MODEL

def seed_bns_data(json_file_path: str):
    """Upload BNS sections with embeddings to Supabase"""

    print(f"Loading BNS data from {json_file_path}...")

    with open(json_file_path, 'r', encoding='utf-8') as f:
        sections = json.load(f)

    print(f"Found {len(sections)} sections")

    embeddings_model = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    supabase = get_supabase_client()

    for i, section in enumerate(sections, 1):
        print(f"Processing {i}/{len(sections)}: Section {section['section_number']}...")

        # Create text for embedding (use full_text)
        embedding_text = section['full_text']

        # Generate embedding
        embedding = embeddings_model.embed_query(embedding_text)

        # Prepare data for insertion
        metadata = section['metadata']

        insert_data = {
            'section_number': section['section_number'],
            'title': section['title'],
            'full_text': section['full_text'],
            'subsections': section['subsections'],
            'illustrations': section.get('illustrations', []),
            'explanations': section.get('explanations', []),
            'category': metadata['category'],
            'severity': metadata['severity'],
            'keywords': metadata.get('keywords', []),
            'essential_elements': metadata['essential_elements'],
            'embedding': embedding
        }

        # Insert into Supabase
        try:
            supabase.table('bns_sections').insert(insert_data).execute()
            print(f"✅ Uploaded Section {section['section_number']}: {section['title']}")

        except Exception as e:
            print(f"❌ Error uploading Section {section['section_number']}: {e}")

    print(f"\n🎉 Successfully uploaded {len(sections)} BNS sections!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/seed_bns_data.py path/to/bns_sections_final.json")
        sys.exit(1)

    json_file = sys.argv[1]
    seed_bns_data(json_file)
