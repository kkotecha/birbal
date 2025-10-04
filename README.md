# Birbal - BNS Section Predictor

AI assistant for Indian police officers to identify applicable BNS (Bhartiya Nyaya Sanhita) sections from crime descriptions.

## Project Status

### ✅ Completed
- Web scraper for BNS sections from advocatekhoj.com
- Data extraction and formatting pipeline
- Sample dataset (20 sections) validated
- Project structure created

### ⏳ Next Steps
1. Run full BNS scraper (358 sections)
2. Set up Supabase database
3. Implement backend (FastAPI + LangGraph)
4. Create frontend interface
5. Deploy to Railway + Vercel

## Quick Start

### 1. Scrape BNS Data

```bash
cd scraper
pip3 install -r requirements.txt

# Test with sample (20 sections)
python3 scrape_sample.py

# Full scraping (358 sections, ~6 minutes)
python3 scrape_bns.py
```

Output: `bns_sections.json` with all sections

### 2. Set Up Database

See `SCRAPING_GUIDE.md` for complete instructions.

## Project Structure

```
birbal/
├── README.md                    # This file
├── SCRAPING_GUIDE.md           # Detailed scraping instructions
│
├── scraper/                     # BNS data scraper
│   ├── scrape_bns.py           # Main scraper (358 sections)
│   ├── scrape_sample.py        # Sample scraper (20 sections)
│   ├── test_scraper.py         # Test script
│   ├── requirements.txt        # Dependencies
│   ├── README.md               # Scraper docs
│   └── bns_sections_sample.json # Sample output
│
├── backend/                     # FastAPI + LangGraph (TODO)
│   ├── agents/                 # LangGraph agents
│   ├── tools/                  # LangChain tools
│   ├── graph/                  # Workflow definitions
│   └── scripts/                # Utility scripts
│
├── frontend/                    # HTML/CSS/JS UI (TODO)
│
└── supabase/                    # Database migrations (TODO)
    └── migrations/
```

## Data Format

Each BNS section is structured as:

```json
{
  "section_number": "103",
  "title": "Murder",
  "description": "Full section text...",
  "essential_elements": {
    "mens_rea": ["intentional", "knowledge"],
    "actus_reus": [],
    "requirements": ["Detailed requirements..."]
  },
  "punishment": "Death or imprisonment for life, and fine",
  "category": "violence",
  "severity": "very_serious",
  "keywords": ["murder", "death", "intentionally"]
}
```

### Categories
- `violence` - Assault, murder, hurt
- `property` - Theft, robbery, burglary
- `fraud` - Cheating, forgery, breach of trust
- `sexual` - Offences against women/children
- `cyber` - IT-related offences
- `public_order` - Riots, unlawful assembly
- `economic` - Economic offences
- `other` - General provisions

### Severity Levels
- `minor` - Fine only
- `moderate` - Imprisonment < 3 years
- `serious` - Imprisonment 3-7 years
- `very_serious` - > 7 years, life, or death

## Tech Stack

**Backend:**
- FastAPI (Python)
- LangGraph (Agent orchestration)
- OpenAI GPT-4o-mini
- Supabase (PostgreSQL + pgvector)
- Arize Phoenix (Observability)

**Frontend:**
- HTML/CSS/JavaScript
- Tailwind CSS

**Deployment:**
- Backend: Railway ($5/month)
- Frontend: Vercel (free)
- Database: Supabase (free tier)

## Data Source

**Website:** https://www.advocatekhoj.com/library/bareacts/bharatiyanyayasanhita/

**Structure:**
- 20 Chapters
- 358 Sections
- Each section has dedicated page with full text

## Contributing

See `SCRAPING_GUIDE.md` for detailed instructions on:
- Running the scraper
- Validating data
- Improving extraction
- Using official sources

## License

MIT

## Support

For issues with:
- **Scraper**: Check `scraper/README.md`
- **Data format**: See `SCRAPING_GUIDE.md`
- **Project setup**: See original project spec
