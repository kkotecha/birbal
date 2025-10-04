#!/usr/bin/env python3
"""
BNS Section Scraper for advocatekhoj.com
Extracts all 358 sections of Bharatiya Nyaya Sanhita, 2023
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from typing import Dict, List, Optional
from urllib.parse import quote

BASE_URL = "https://www.advocatekhoj.com/library/bareacts/bharatiyanyayasanhita"

# Category mapping based on chapter names
CATEGORY_MAP = {
    "preliminary": "other",
    "punishments": "other",
    "general exceptions": "other",
    "abetment": "other",
    "woman and child": "sexual",
    "human body": "violence",
    "state": "other",
    "army": "other",
    "elections": "other",
    "coin": "fraud",
    "public tranquillity": "public_order",
    "public servants": "other",
    "contempts": "other",
    "false evidence": "fraud",
    "public health": "public_order",
    "religion": "other",
    "property": "property",
    "documents": "fraud",
    "intimidation": "violence",
}

def get_category(chapter_name: str) -> str:
    """Determine category based on chapter name"""
    chapter_lower = chapter_name.lower()
    for key, value in CATEGORY_MAP.items():
        if key in chapter_lower:
            return value
    return "other"

def get_severity(section_text: str) -> str:
    """Determine severity based on punishment"""
    text_lower = section_text.lower()

    if "death" in text_lower or "life imprisonment" in text_lower:
        return "very_serious"
    elif "imprisonment" in text_lower:
        # Check years
        years_match = re.search(r'(\d+)\s*years?', text_lower)
        if years_match:
            years = int(years_match.group(1))
            if years >= 7:
                return "serious"
            elif years >= 3:
                return "moderate"
        return "moderate"
    elif "fine" in text_lower:
        return "minor"

    return "moderate"

def extract_keywords(section_data: Dict) -> List[str]:
    """Extract keywords from section"""
    keywords = set()

    text = f"{section_data['title']} {section_data['description']}".lower()

    # Common legal terms
    legal_terms = [
        "murder", "theft", "assault", "fraud", "cheating", "robbery",
        "rape", "kidnapping", "wrongful restraint", "defamation",
        "criminal breach of trust", "extortion", "forgery", "bribery",
        "criminal conspiracy", "criminal intimidation", "hurt", "grievous hurt",
        "voluntarily", "intentionally", "knowledge", "negligence", "rash",
        "death", "imprisonment", "fine", "property", "dishonestly",
        "public servant", "government", "document", "evidence"
    ]

    for term in legal_terms:
        if term in text:
            keywords.add(term)

    return sorted(list(keywords))

def extract_essential_elements(description: str) -> Dict:
    """Extract essential elements from section description"""
    # This is a basic extraction - in production, you'd use LLM for better extraction
    elements = {
        "mens_rea": [],
        "actus_reus": [],
        "requirements": []
    }

    desc_lower = description.lower()

    # Mens rea indicators
    if "intentionally" in desc_lower or "voluntarily" in desc_lower:
        elements["mens_rea"].append("intentional")
    if "knowledge" in desc_lower or "knowing" in desc_lower:
        elements["mens_rea"].append("knowledge")
    if "rashly" in desc_lower or "negligently" in desc_lower:
        elements["mens_rea"].append("rash/negligent")
    if "dishonestly" in desc_lower:
        elements["mens_rea"].append("dishonest intent")

    # Keep description as main requirement
    elements["requirements"].append(description[:200])

    return elements

def scrape_index() -> List[Dict]:
    """Scrape the index page to get all section links"""
    url = f"{BASE_URL}/index.php?Title=Bharatiya%20Nyaya%20Sanhita,%202023"

    print(f"Fetching index page: {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    sections_info = []
    current_chapter = ""

    # Find all section links
    links = soup.find_all('a', href=True)

    for link in links:
        href = link['href']

        # Check if this is a chapter header
        text = link.get_text(strip=True)
        if text.startswith('Chapter'):
            current_chapter = text
            continue

        # Only process section links
        if 'STitle=' in href and '.php' in href and not href.startswith('index.php'):
            # Extract section number from href (e.g., "1.php" -> "1")
            section_match = re.match(r'^(\d+[A-Z]?)\.php', href)
            if section_match:
                section_num = section_match.group(1)
                title = text

                # Build full URL
                full_url = f"{BASE_URL}/{href}" if not href.startswith('http') else href

                sections_info.append({
                    'section_number': section_num,
                    'title': title,
                    'chapter': current_chapter,
                    'url': full_url
                })

    print(f"Found {len(sections_info)} sections")
    return sections_info

def scrape_section(section_info: Dict) -> Optional[Dict]:
    """Scrape individual section details"""
    url = section_info['url']
    section_num = section_info['section_number']

    print(f"Scraping Section {section_num}...")

    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract main content
        content = soup.get_text(separator='\n', strip=True)

        # Split into lines
        lines = [line.strip() for line in content.split('\n') if line.strip()]

        # Find where the actual section content starts
        # It's usually after the section number and title
        start_idx = 0
        for i, line in enumerate(lines):
            if f"{section_num}." in line and section_info['title'] in line:
                start_idx = i + 1
                break

        # Extract description (stop at footer indicators)
        description_lines = []
        punishment_lines = []
        capture_punishment = False

        for line in lines[start_idx:]:
            # Stop at footer
            if any(footer in line for footer in ['Back', 'Index', 'Next', 'Client Area', 'Advocate Area', 'Powered by']):
                break

            # Skip navigation
            if line in ['Login', 'Advocate', 'Client', 'Follow @SCJudgments']:
                continue

            # Check for punishment indicators
            if any(keyword in line.lower() for keyword in ['shall be punished', 'punishment', 'imprisonment', 'fine only', 'shall be liable']):
                capture_punishment = True

            if capture_punishment:
                punishment_lines.append(line)
            else:
                description_lines.append(line)

        # Join lines
        description = ' '.join(description_lines) if description_lines else section_info['title']
        punishment = ' '.join(punishment_lines) if punishment_lines else "Not specified"

        # Clean up description (max 1000 chars)
        if len(description) > 1000:
            description = description[:1000] + "..."

        # Determine category and severity
        category = get_category(section_info.get('chapter', ''))
        severity = get_severity(description + ' ' + punishment)

        # Build section data
        section_data = {
            'section_number': section_num,
            'title': section_info['title'],
            'description': description,
            'essential_elements': extract_essential_elements(description),
            'punishment': punishment,
            'category': category,
            'severity': severity,
            'keywords': []
        }

        # Extract keywords
        section_data['keywords'] = extract_keywords(section_data)

        return section_data

    except Exception as e:
        print(f"Error scraping section {section_num}: {e}")
        return None

def scrape_all_sections() -> List[Dict]:
    """Main function to scrape all BNS sections"""

    # First, get all section info from index
    sections_info = scrape_index()

    if not sections_info:
        print("No sections found in index. Trying alternative approach...")
        # Fallback: try sections 1-358 directly
        sections_info = []
        for i in range(1, 359):
            sections_info.append({
                'section_number': str(i),
                'title': f"Section {i}",
                'url': f"{BASE_URL}/{i}.php?Title=Bharatiya%20Nyaya%20Sanhita,%202023"
            })

    all_sections = []

    for i, section_info in enumerate(sections_info, 1):
        print(f"Progress: {i}/{len(sections_info)}")

        section_data = scrape_section(section_info)

        if section_data:
            all_sections.append(section_data)

        # Be respectful - add delay
        time.sleep(1)

    return all_sections

def save_to_json(sections: List[Dict], filename: str):
    """Save sections to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(sections, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(sections)} sections to {filename}")

if __name__ == "__main__":
    print("=" * 60)
    print("BNS Section Scraper")
    print("=" * 60)
    print()

    sections = scrape_all_sections()

    if sections:
        output_file = "bns_sections.json"
        save_to_json(sections, output_file)

        print("\n" + "=" * 60)
        print("SCRAPING COMPLETE")
        print("=" * 60)
        print(f"Total sections scraped: {len(sections)}")
        print(f"Output file: {output_file}")
        print()
        print("You can now use this file with:")
        print("python backend/scripts/seed_bns_data.py bns_sections.json")
    else:
        print("\nNo sections were scraped. Please check the website structure.")
