# BNS Section Scraper

This scraper extracts all 358 sections of the Bharatiya Nyaya Sanhita (BNS) 2023 from advocatekhoj.com and formats them for the BNS Predictor project.

## Files

- `scrape_bns.py` - Main scraper for all 358 sections
- `scrape_sample.py` - Sample scraper for testing (first 20 sections)
- `test_scraper.py` - Quick test script
- `requirements.txt` - Python dependencies

## Usage

### Install Dependencies

```bash
pip3 install -r requirements.txt
```

### Run Full Scraper

```bash
python3 scrape_bns.py
```

This will:
1. Fetch the index page to get all section links
2. Scrape each section (358 total)
3. Extract section details (title, description, punishment)
4. Categorize each section (violence, property, fraud, etc.)
5. Determine severity (minor, moderate, serious, very_serious)
6. Extract keywords and legal elements
7. Save to `bns_sections.json`

**Expected time**: ~6 minutes (1 second delay between requests)

### Run Sample Scraper (Testing)

```bash
python3 scrape_sample.py
```

Scrapes only first 20 sections to `bns_sections_sample.json`.

## Output Format

Each section in the JSON has:

```json
{
  "section_number": "103",
  "title": "Murder",
  "description": "Whoever commits murder shall be punished...",
  "essential_elements": {
    "mens_rea": ["intentional", "knowledge"],
    "actus_reus": [],
    "requirements": ["..."]
  },
  "punishment": "Death or imprisonment for life, and shall also be liable to fine",
  "category": "violence",
  "severity": "very_serious",
  "keywords": ["murder", "death", "intentionally", "voluntarily"]
}
```

## Categories

- `violence` - Offences against human body, assault, murder
- `property` - Theft, robbery, burglary
- `fraud` - Cheating, forgery, criminal breach of trust
- `sexual` - Offences against women and children
- `cyber` - IT-related offences
- `public_order` - Public tranquillity, riots
- `economic` - Economic offences
- `other` - General provisions, definitions, etc.

## Severity Levels

- `minor` - Fine only, small penalties
- `moderate` - Imprisonment < 3 years
- `serious` - Imprisonment 3-7 years
- `very_serious` - Imprisonment > 7 years, life, or death

## Notes

- Scraper adds 1 second delay between requests to be respectful
- Some sections may have empty/minimal descriptions (e.g., definition sections)
- Punishment extraction is basic - manual review recommended
- Category mapping is based on chapter names and may need refinement

## Next Steps

After scraping, use the output file with:

```bash
python backend/scripts/seed_bns_data.py scraper/bns_sections.json
```

This will upload the sections to Supabase with embeddings.
