#!/usr/bin/env python3
"""
Smart BNS scraper - scrapes key crime sections more carefully
Focuses on actual crime sections (not just definitions)
"""

import sys
sys.path.insert(0, '/Users/khanjan/Development/birbal/scraper')

from scrape_bns import scrape_section, save_to_json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.advocatekhoj.com/library/bareacts/bharatiyanyayasanhita"

# Key sections to scrape (major crimes)
KEY_SECTIONS = {
    # Murders and violence (100-115)
    **{str(i): f"Section {i}" for i in range(100, 116)},

    # Assault and hurt (114-127)
    **{str(i): f"Section {i}" for i in range(114, 128)},

    # Kidnapping (137-142)
    **{str(i): f"Section {i}" for i in range(137, 143)},

    # Theft (303-311)
    **{str(i): f"Section {i}" for i in range(303, 312)},

    # Robbery (309-311)
    **{str(i): f"Section {i}" for i in range(309, 312)},

    # Cheating (318-323)
    **{str(i): f"Section {i}" for i in range(318, 324)},

    # Sexual offences (63-79)
    **{str(i): f"Section {i}" for i in range(63, 80)},

    # Defamation (356-358)
    **{str(i): f"Section {i}" for i in range(356, 359)},
}

def get_section_title(section_num):
    """Fetch section title from the page"""
    url = f"{BASE_URL}/{section_num}.php?Title=Bharatiya%20Nyaya%20Sanhita,%202023"

    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()

        # Extract title (it's usually after the section number)
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        for i, line in enumerate(lines):
            if f"{section_num}." in line:
                # Title is usually the line containing section number
                title_parts = line.split(f"{section_num}.")
                if len(title_parts) > 1:
                    return title_parts[1].strip()

        return f"Section {section_num}"
    except:
        return f"Section {section_num}"

if __name__ == "__main__":
    print("=" * 60)
    print("BNS Key Sections Scraper")
    print(f"Scraping {len(KEY_SECTIONS)} key crime sections")
    print("=" * 60)
    print()

    all_sections = []

    for section_num in sorted(KEY_SECTIONS.keys(), key=lambda x: int(x)):
        print(f"Fetching Section {section_num}...")

        title = get_section_title(section_num)

        section_info = {
            'section_number': section_num,
            'title': title,
            'chapter': 'Crime Provisions',
            'url': f"{BASE_URL}/{section_num}.php?Title=Bharatiya%20Nyaya%20Sanhita,%202023"
        }

        section_data = scrape_section(section_info)

        if section_data:
            all_sections.append(section_data)
            print(f"✓ Section {section_num}: {section_data['title']}")

        import time
        time.sleep(0.5)  # Respectful delay

    if all_sections:
        output_file = "bns_sections_key.json"
        save_to_json(all_sections, output_file)

        print("\n" + "=" * 60)
        print("KEY SECTIONS SCRAPING COMPLETE")
        print("=" * 60)
        print(f"Total sections scraped: {len(all_sections)}")
        print(f"Output file: {output_file}")
    else:
        print("\nNo sections were scraped.")
