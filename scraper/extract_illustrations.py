#!/usr/bin/env python3
"""
Post-process BNS sections to extract illustrations and explanations separately
"""

import json
import re
from typing import Dict, List

def extract_structured_content(section: Dict) -> Dict:
    """Extract illustrations and explanations from description"""

    description = section.get('description', '')

    # Initialize
    main_text = description
    illustrations = []
    explanations = []

    # Extract Illustrations
    # Pattern: "Illustration." or "Illustrations." followed by (a), (b), etc.
    illustration_pattern = r'Illustrations?\.?\s*(.*?)(?=Explanation|Punishment|$)'
    ill_match = re.search(illustration_pattern, description, re.DOTALL | re.IGNORECASE)

    if ill_match:
        ill_text = ill_match.group(1).strip()

        # Split by (a), (b), (c), etc.
        ill_parts = re.split(r'\(([a-z])\)\s*', ill_text)

        for i in range(1, len(ill_parts), 2):
            if i + 1 < len(ill_parts):
                label = ill_parts[i]
                content = ill_parts[i + 1].strip()
                if content:
                    illustrations.append({
                        'label': f'({label})',
                        'text': content
                    })

        # Remove illustrations from main text
        main_text = re.sub(illustration_pattern, '', main_text, flags=re.DOTALL | re.IGNORECASE)

    # Extract Explanations
    # Pattern: "Explanation" or "Explanation 1", "Explanation 2", etc.
    explanation_pattern = r'Explanation\s*(\d*)\.?\s*[-–—]?\s*(.*?)(?=Explanation|Illustration|Punishment|$)'
    exp_matches = re.finditer(explanation_pattern, description, re.DOTALL | re.IGNORECASE)

    for match in exp_matches:
        num = match.group(1).strip()
        content = match.group(2).strip()
        if content:
            explanations.append({
                'number': num if num else '1',
                'text': content
            })

    # Remove explanations from main text
    main_text = re.sub(r'Explanation.*?(?=Illustration|Punishment|$)', '',
                       main_text, flags=re.DOTALL | re.IGNORECASE)

    # Clean up main text
    main_text = re.sub(r'\s+', ' ', main_text).strip()

    return {
        **section,
        'description': main_text,
        'explanations': explanations,
        'illustrations': illustrations
    }

def process_bns_file(input_file: str, output_file: str):
    """Process BNS sections file to extract structured content"""

    print("=" * 60)
    print("Extracting Illustrations and Explanations")
    print("=" * 60)
    print()

    # Load data
    with open(input_file, 'r', encoding='utf-8') as f:
        sections = json.load(f)

    print(f"Processing {len(sections)} sections...")
    print()

    # Process each section
    processed_sections = []
    stats = {
        'with_illustrations': 0,
        'with_explanations': 0,
        'total_illustrations': 0,
        'total_explanations': 0
    }

    for i, section in enumerate(sections, 1):
        processed = extract_structured_content(section)
        processed_sections.append(processed)

        # Update stats
        if processed.get('illustrations'):
            stats['with_illustrations'] += 1
            stats['total_illustrations'] += len(processed['illustrations'])

        if processed.get('explanations'):
            stats['with_explanations'] += 1
            stats['total_explanations'] += len(processed['explanations'])

        if i % 50 == 0:
            print(f"Processed {i}/{len(sections)} sections...")

    # Save processed data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_sections, f, indent=2, ensure_ascii=False)

    # Print statistics
    print()
    print("=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)
    print(f"Input file:  {input_file}")
    print(f"Output file: {output_file}")
    print()
    print("Statistics:")
    print(f"  Total sections: {len(sections)}")
    print(f"  Sections with illustrations: {stats['with_illustrations']}")
    print(f"  Total illustrations extracted: {stats['total_illustrations']}")
    print(f"  Sections with explanations: {stats['with_explanations']}")
    print(f"  Total explanations extracted: {stats['total_explanations']}")
    print()

    # Show examples
    print("Sample sections with illustrations:")
    for section in processed_sections[:10]:
        if section.get('illustrations'):
            print(f"\n  Section {section['section_number']}: {section['title']}")
            print(f"    Illustrations: {len(section['illustrations'])}")
            for ill in section['illustrations'][:2]:  # Show first 2
                print(f"      {ill['label']} {ill['text'][:80]}...")
            break

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python extract_illustrations.py <input_file> [output_file]")
        print()
        print("Example:")
        print("  python extract_illustrations.py bns_sections.json bns_sections_enhanced.json")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.json', '_enhanced.json')

    process_bns_file(input_file, output_file)
