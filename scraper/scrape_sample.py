#!/usr/bin/env python3
"""
Sample BNS scraper - scrapes first 20 sections for testing
"""

import sys
sys.path.insert(0, '/Users/khanjan/Development/birbal/scraper')

from scrape_bns import scrape_index, scrape_section, save_to_json

if __name__ == "__main__":
    print("=" * 60)
    print("BNS Sample Scraper (First 20 sections)")
    print("=" * 60)
    print()

    # Get all section info
    sections_info = scrape_index()

    # Limit to first 20
    sections_info = sections_info[:20]

    all_sections = []

    for i, section_info in enumerate(sections_info, 1):
        print(f"Progress: {i}/{len(sections_info)}")

        section_data = scrape_section(section_info)

        if section_data:
            all_sections.append(section_data)
            print(f"✓ Section {section_data['section_number']}: {section_data['title']}")
            print(f"  Category: {section_data['category']}, Severity: {section_data['severity']}")

        import time
        time.sleep(0.5)  # Be respectful

    if all_sections:
        output_file = "bns_sections_sample.json"
        save_to_json(all_sections, output_file)

        print("\n" + "=" * 60)
        print("SAMPLE SCRAPING COMPLETE")
        print("=" * 60)
        print(f"Total sections scraped: {len(all_sections)}")
        print(f"Output file: {output_file}")
    else:
        print("\nNo sections were scraped. Please check the website structure.")
