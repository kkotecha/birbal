# BNS Data Scraping Guide

## Overview

I've created a complete web scraper to extract all 358 sections of the Bharatiya Nyaya Sanhita (BNS) 2023 from advocatekhoj.com and format them for your project.

## What's Been Created

### 1. Scraper Scripts (in `/scraper` directory)

- **`scrape_bns.py`** - Main production scraper for all 358 sections
- **`scrape_sample.py`** - Sample scraper (first 20 sections) for testing
- **`test_scraper.py`** - Quick validation script
- **`requirements.txt`** - Python dependencies
- **`README.md`** - Scraper documentation

### 2. Sample Output

- **`bns_sections_sample.json`** - 20 sections successfully scraped and formatted

## How to Complete the Full Scraping

### Option 1: Run the Full Scraper (Recommended)

```bash
cd /Users/khanjan/Development/birbal/scraper

# Install dependencies
pip3 install -r requirements.txt

# Run full scraper (takes ~6 minutes)
python3 scrape_bns.py
```

This will create `bns_sections.json` with all 358 sections.

### Option 2: Run in Batches

If you want to scrape in batches (safer for network issues):

```python
# Modify scrape_bns.py line 243-256 to:
def scrape_all_sections(start=1, end=358):
    sections_info = scrape_index()
    sections_info = sections_info[start-1:end]  # Slice by range
    # ... rest of code
```

Then run:
```bash
python3 scrape_bns.py  # Sections 1-100
# Manually adjust range and run again for 101-200, 201-300, 301-358
# Then merge JSON files
```

### Option 3: Use API/Official Source

If available, check if there's an official API or structured data source:
- Ministry of Home Affairs website
- Legislative department
- eGazette portal

## Data Structure

Each section is formatted as:

```json
{
  "section_number": "103",
  "title": "Murder",
  "description": "Whoever commits murder shall be punished with death or imprisonment for life...",
  "essential_elements": {
    "mens_rea": ["intentional", "knowledge"],
    "actus_reus": [],
    "requirements": ["Causing death", "With intention or knowledge"]
  },
  "punishment": "Death or imprisonment for life, and shall also be liable to fine",
  "category": "violence",
  "severity": "very_serious",
  "keywords": ["murder", "death", "intentionally"]
}
```

## Validation Checklist

After scraping, validate:

- [ ] All 358 sections present
- [ ] No duplicate section numbers
- [ ] All required fields populated
- [ ] Categories assigned correctly
- [ ] Severity levels make sense
- [ ] Descriptions are meaningful (not just titles)
- [ ] Punishment information extracted

Use this script to validate:

```python
import json

with open('bns_sections.json', 'r') as f:
    sections = json.load(f)

print(f"Total sections: {len(sections)}")
print(f"Unique section numbers: {len(set(s['section_number'] for s in sections))}")

# Check for missing fields
for section in sections:
    assert 'section_number' in section
    assert 'title' in section
    assert 'description' in section
    assert 'category' in section
    assert 'severity' in section

print("✓ All validations passed!")
```

## Improvements Needed

The current scraper extracts basic information. You may want to enhance:

1. **Better Category Mapping**: Current mapping is chapter-based. Manual review recommended for accurate categorization.

2. **Mens Rea/Actus Reus Extraction**: Currently basic keyword matching. Consider using LLM for better extraction:

```python
from openai import OpenAI
client = OpenAI()

def extract_legal_elements_with_llm(description):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "system",
            "content": "Extract mens rea and actus reus from BNS section"
        }, {
            "role": "user",
            "content": description
        }]
    )
    return json.loads(response.choices[0].message.content)
```

3. **Punishment Parsing**: Extract structured punishment (years, fine amount, etc.)

4. **Cross-References**: Extract section references ("as per section 103")

5. **Examples/Illustrations**: BNS includes illustrations - extract separately

## Using the Scraped Data

Once you have `bns_sections.json`:

```bash
# Move to project root
mv scraper/bns_sections.json backend/data/

# Seed Supabase database
cd backend
python scripts/seed_bns_data.py data/bns_sections.json
```

## Alternative: Official PDF

If scraping is problematic, you can also extract from the official PDF:

```bash
# Download official BNS PDF
curl -L "https://www.mha.gov.in/sites/default/files/2024-04/250883_english_01042024.pdf" -o bns_official.pdf

# Use PDF parser
pip install pypdf2 pdfplumber

# Parse PDF (requires custom script)
python parse_bns_pdf.py bns_official.pdf
```

## Current Status

✅ Scraper created and tested
✅ Sample data (20 sections) successfully extracted
✅ Data format validated
✅ Project structure ready
⏳ Full 358 section scraping pending (run `python3 scrape_bns.py`)

## Next Steps

1. Run full scraper: `python3 scraper/scrape_bns.py`
2. Validate output: Check all 358 sections
3. Review categories: Manually verify category assignments
4. Seed database: Use `backend/scripts/seed_bns_data.py`
5. Test predictions: Run sample queries through the system
