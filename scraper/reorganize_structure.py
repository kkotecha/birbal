#!/usr/bin/env python3
"""
Reorganize BNS sections into hierarchical structure
Extracts subsections, clauses, and sub-clauses with proper hierarchy
"""

import json
import re
from typing import Dict, List, Optional, Tuple

def extract_subsections(text: str, section_number: str) -> List[Dict]:
    """
    Extract hierarchical subsections from text

    Patterns to match:
    - Level 1: (1), (2), (3)... or 1., 2., 3...
    - Level 2: (a), (b), (c)...
    - Level 3: (i), (ii), (iii)...
    """

    subsections = []

    # Pattern for main subsections: (1), (2), (3) etc.
    # Using lookahead to capture until next subsection or end
    pattern_level1 = r'\((\d+)\)\s*(.*?)(?=\(\d+\)|$)'

    matches = list(re.finditer(pattern_level1, text, re.DOTALL))

    if not matches:
        # No subsections found, return whole text as single item
        return [{
            'id': section_number,
            'text': text.strip(),
            'level': 0,
            'parent': None,
            'children': []
        }]

    for match in matches:
        subsec_num = match.group(1)
        subsec_text = match.group(2).strip()
        subsec_id = f"{section_number}({subsec_num})"

        # Check for level 2 clauses: (a), (b), (c)
        clauses = extract_clauses(subsec_text, subsec_id)

        if clauses:
            # Has sub-clauses
            # Extract the preamble (text before first clause)
            first_clause_match = re.search(r'\([a-z]\)', subsec_text)
            preamble = subsec_text[:first_clause_match.start()].strip() if first_clause_match else subsec_text

            subsections.append({
                'id': subsec_id,
                'text': preamble,
                'level': 1,
                'parent': section_number,
                'children': [c['id'] for c in clauses]
            })

            # Add clauses
            subsections.extend(clauses)
        else:
            # No sub-clauses, simple subsection
            subsections.append({
                'id': subsec_id,
                'text': subsec_text,
                'level': 1,
                'parent': section_number,
                'children': []
            })

    return subsections

def extract_clauses(text: str, parent_id: str) -> List[Dict]:
    """Extract level 2 clauses: (a), (b), (c)"""

    clauses = []

    # Pattern for clauses: (a), (b), (c) etc.
    pattern_level2 = r'\(([a-z])\)\s*(.*?)(?=\([a-z]\)|$)'

    matches = list(re.finditer(pattern_level2, text, re.DOTALL))

    for match in matches:
        clause_letter = match.group(1)
        clause_text = match.group(2).strip()
        clause_id = f"{parent_id}({clause_letter})"

        # Check for level 3 sub-clauses: (i), (ii), (iii) or (1), (2)
        subclauses = extract_subclauses(clause_text, clause_id)

        if subclauses:
            # Has sub-clauses
            first_subclause = re.search(r'\((?:i+|\d+)\)', clause_text)
            preamble = clause_text[:first_subclause.start()].strip() if first_subclause else clause_text

            clauses.append({
                'id': clause_id,
                'text': preamble,
                'level': 2,
                'parent': parent_id,
                'children': [sc['id'] for sc in subclauses]
            })

            clauses.extend(subclauses)
        else:
            clauses.append({
                'id': clause_id,
                'text': clause_text,
                'level': 2,
                'parent': parent_id,
                'children': []
            })

    return clauses

def extract_subclauses(text: str, parent_id: str) -> List[Dict]:
    """Extract level 3 sub-clauses: (i), (ii), (iii) or (1), (2)"""

    subclauses = []

    # Try roman numerals first
    pattern_roman = r'\((i+)\)\s*(.*?)(?=\(i+\)|$)'
    matches = list(re.finditer(pattern_roman, text, re.DOTALL))

    if matches:
        for match in matches:
            roman = match.group(1)
            sc_text = match.group(2).strip()
            sc_id = f"{parent_id}({roman})"

            subclauses.append({
                'id': sc_id,
                'text': sc_text,
                'level': 3,
                'parent': parent_id,
                'children': []
            })
        return subclauses

    # Try numbers
    pattern_num = r'\((\d+)\)\s*(.*?)(?=\(\d+\)|$)'
    matches = list(re.finditer(pattern_num, text, re.DOTALL))

    for match in matches:
        num = match.group(1)
        sc_text = match.group(2).strip()
        sc_id = f"{parent_id}({num})"

        subclauses.append({
            'id': sc_id,
            'text': sc_text,
            'level': 3,
            'parent': parent_id,
            'children': []
        })

    return subclauses

def reorganize_section(section: Dict) -> Dict:
    """Reorganize a single section into hierarchical structure"""

    section_number = section['section_number']

    # Combine description and punishment for full text
    description = section.get('description', '')
    punishment = section.get('punishment', '')

    # Create full text for embeddings
    full_text = f"{description} {punishment}".strip()

    # Extract hierarchical subsections from combined text
    subsections = extract_subsections(full_text, section_number)

    # Build new structure
    reorganized = {
        'section_number': section_number,
        'title': section.get('title', ''),

        # Full text for embeddings
        'full_text': full_text,

        # Hierarchical subsections
        'subsections': subsections,

        # Keep existing extracted data
        'illustrations': section.get('illustrations', []),
        'explanations': section.get('explanations', []),

        # Metadata
        'metadata': {
            'category': section.get('category', 'other'),
            'severity': section.get('severity', 'moderate'),
            'keywords': section.get('keywords', []),
            'essential_elements': section.get('essential_elements', {})
        }
    }

    return reorganized

def process_all_sections(input_file: str, output_file: str):
    """Process all BNS sections"""

    print("=" * 60)
    print("Reorganizing BNS Sections - Hierarchical Structure")
    print("=" * 60)
    print()

    # Load data
    with open(input_file, 'r', encoding='utf-8') as f:
        sections = json.load(f)

    print(f"Processing {len(sections)} sections...")
    print()

    # Process each section
    reorganized_sections = []
    stats = {
        'with_subsections': 0,
        'total_subsections': 0,
        'with_clauses': 0,
        'total_clauses': 0,
        'max_depth': 0
    }

    for i, section in enumerate(sections, 1):
        reorganized = reorganize_section(section)
        reorganized_sections.append(reorganized)

        # Update stats
        subsections = reorganized['subsections']
        if len(subsections) > 1:  # More than just the section itself
            stats['with_subsections'] += 1
            stats['total_subsections'] += len([s for s in subsections if s['level'] == 1])
            stats['total_clauses'] += len([s for s in subsections if s['level'] == 2])

            max_level = max(s['level'] for s in subsections)
            stats['max_depth'] = max(stats['max_depth'], max_level)

        if i % 50 == 0:
            print(f"Processed {i}/{len(sections)} sections...")

    # Save
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(reorganized_sections, f, indent=2, ensure_ascii=False)

    # Print stats
    print()
    print("=" * 60)
    print("REORGANIZATION COMPLETE")
    print("=" * 60)
    print(f"Input file:  {input_file}")
    print(f"Output file: {output_file}")
    print()
    print("Statistics:")
    print(f"  Total sections: {len(sections)}")
    print(f"  Sections with subsections: {stats['with_subsections']}")
    print(f"  Total subsections (level 1): {stats['total_subsections']}")
    print(f"  Total clauses (level 2): {stats['total_clauses']}")
    print(f"  Maximum hierarchy depth: {stats['max_depth']}")
    print()

    # Show example
    print("Example - Section 8 structure:")
    sec8 = next((s for s in reorganized_sections if s['section_number'] == '8'), None)
    if sec8:
        print(f"  Title: {sec8['title']}")
        print(f"  Subsections: {len(sec8['subsections'])}")
        for subsec in sec8['subsections'][:5]:
            indent = "  " * (subsec['level'] + 1)
            text_preview = subsec['text'][:60] + "..." if len(subsec['text']) > 60 else subsec['text']
            print(f"{indent}{subsec['id']}: {text_preview}")
        if len(sec8['subsections']) > 5:
            print(f"    ... and {len(sec8['subsections']) - 5} more")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python reorganize_structure.py <input_file> [output_file]")
        print()
        print("Example:")
        print("  python reorganize_structure.py _ARCHIVE_bns_sections_enhanced.json bns_sections_PRODUCTION.json")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.json', '_final.json')

    process_all_sections(input_file, output_file)
