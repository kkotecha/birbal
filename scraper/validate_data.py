#!/usr/bin/env python3
"""
Validation script for BNS section data
"""

import json
import sys
from collections import Counter

def validate_bns_data(filename):
    """Validate BNS sections JSON file"""

    print("=" * 60)
    print(f"Validating: {filename}")
    print("=" * 60)
    print()

    # Load data
    with open(filename, 'r', encoding='utf-8') as f:
        sections = json.load(f)

    # Basic counts
    print(f"Total sections: {len(sections)}")
    print()

    # Check for duplicates
    section_numbers = [s['section_number'] for s in sections]
    duplicates = [num for num, count in Counter(section_numbers).items() if count > 1]

    if duplicates:
        print(f"❌ Duplicate sections found: {duplicates}")
    else:
        print(f"✓ No duplicate sections")

    # Check required fields
    required_fields = ['section_number', 'title', 'description', 'punishment',
                       'category', 'severity', 'keywords', 'essential_elements']

    missing_fields = {}
    for section in sections:
        for field in required_fields:
            if field not in section:
                if field not in missing_fields:
                    missing_fields[field] = []
                missing_fields[field].append(section.get('section_number', 'unknown'))

    if missing_fields:
        print(f"\n❌ Missing fields:")
        for field, section_nums in missing_fields.items():
            print(f"  {field}: {len(section_nums)} sections")
    else:
        print(f"✓ All required fields present")

    # Category distribution
    print(f"\n📊 Category Distribution:")
    categories = Counter(s['category'] for s in sections)
    for cat, count in categories.most_common():
        print(f"  {cat}: {count}")

    # Severity distribution
    print(f"\n⚖️  Severity Distribution:")
    severities = Counter(s['severity'] for s in sections)
    for sev, count in severities.most_common():
        print(f"  {sev}: {count}")

    # Empty descriptions check
    empty_desc = [s['section_number'] for s in sections
                  if not s.get('description') or s['description'] == s['title']]

    if empty_desc:
        print(f"\n⚠️  Sections with minimal descriptions: {len(empty_desc)}")
        print(f"  Examples: {empty_desc[:5]}")
    else:
        print(f"\n✓ All sections have proper descriptions")

    # Keyword statistics
    total_keywords = sum(len(s.get('keywords', [])) for s in sections)
    avg_keywords = total_keywords / len(sections) if sections else 0

    print(f"\n🔑 Keyword Statistics:")
    print(f"  Total keywords: {total_keywords}")
    print(f"  Average per section: {avg_keywords:.1f}")

    # Most common keywords
    all_keywords = []
    for section in sections:
        all_keywords.extend(section.get('keywords', []))

    print(f"\n  Most common keywords:")
    for keyword, count in Counter(all_keywords).most_common(10):
        print(f"    {keyword}: {count}")

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    issues = []
    if duplicates:
        issues.append(f"Duplicate sections: {len(duplicates)}")
    if missing_fields:
        issues.append(f"Missing fields in some sections")
    if empty_desc:
        issues.append(f"Sections with minimal descriptions: {len(empty_desc)}")

    if issues:
        print("⚠️  Issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ All validations passed!")

    print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_data.py <json_file>")
        print("Example: python validate_data.py bns_sections.json")
        sys.exit(1)

    filename = sys.argv[1]
    validate_bns_data(filename)
