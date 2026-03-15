# Birbal - AI-Powered Legal Section Predictor

An AI assistant that predicts applicable BNS (Bharatiya Nyaya Sanhita) sections from natural language crime descriptions. Built for Indian law enforcement to quickly identify relevant legal provisions using semantic search and LLM reasoning.

**Live Demo:** [neobirbal.vercel.app](https://neobirbal.vercel.app)

## Why This Project

India's new criminal code (BNS, replacing IPC) has 358 sections across 20 chapters. Police officers filing FIRs need to identify the correct legal sections from a verbal crime description — often under time pressure, sometimes in Hindi or Hinglish. This project explores whether a multi-agent AI system with vector search can reliably map unstructured crime narratives to structured legal provisions.

The core product question: **Can an LLM combined with vector similarity search provide accurate, explainable legal section predictions from informal language inputs?**

## What It Does

1. Officer describes a crime in natural language (English, Hindi, or Hinglish)
2. A **Crime Refiner agent** normalizes and translates the input
3. A **BNS Predictor agent** performs vector similarity search across 358 sections, then uses LLM reasoning to rank matches
4. Returns 3-7 applicable sections with confidence scores (0.60–0.95) and legal reasoning

## Architecture

```
User Input (Hindi/English/Hinglish)
        │
        ▼
┌─────────────────────┐
│   Crime Refiner     │  ← Translates, normalizes input
│   (LangGraph Node)  │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐     ┌──────────────────────┐
│   BNS Predictor     │────▶│  Supabase pgvector    │
│   (LangGraph Node)  │     │  (358 BNS sections)   │
└────────┬────────────┘     └──────────────────────┘
         │
         ▼
   Ranked Sections + Confidence Scores + Legal Reasoning
```

**Orchestration:** LangGraph (two-node sequential workflow)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python) |
| Agent Orchestration | LangGraph |
| LLM | OpenAI GPT-4o-mini |
| Vector Database | Supabase (PostgreSQL + pgvector) |
| Frontend | HTML, Tailwind CSS, Vanilla JS |
| Deployment | Railway (backend) + Vercel (frontend) |

## Key Concepts Explored

This project is a practical case study in several areas relevant to AI product development:

**1. Domain-Specific RAG (Retrieval-Augmented Generation)**
Unlike generic chatbots, this system retrieves from a curated legal corpus. The challenge is that legal language is precise but crime descriptions are messy — the retrieval layer must bridge that gap.

**2. Multi-Agent Workflows with LangGraph**
Even a simple two-agent pipeline (refiner → predictor) demonstrates the value of separating concerns: one agent handles input normalization, another handles domain reasoning. This pattern scales to more complex workflows.

**3. Data Pipeline: Web Scraping → Structured Data → Embeddings**
The scraper extracts 358 sections from advocatekhoj.com, structures them with metadata (severity, category, keywords), and seeds them into pgvector. This end-to-end pipeline is reusable for any domain corpus.

**4. Confidence Scoring for LLM Outputs**
Rather than returning binary yes/no, the system provides calibrated confidence scores — critical for legal applications where false positives have real consequences.

## Getting Started

### Prerequisites
- Python 3.9+
- OpenAI API key
- Supabase account (free tier works)

### Setup

```bash
# Clone the repo
git clone https://github.com/kkotecha/birbal.git
cd birbal

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add your OPENAI_API_KEY, SUPABASE_URL, SUPABASE_KEY

# Seed the database (first time only)
python scripts/seed_bns_data.py

# Start the backend
python main.py
# API available at http://localhost:8000
```

```bash
# Frontend (separate terminal)
cd frontend
python3 -m http.server 3000
# Visit http://localhost:3000
```

### Data: Scraping BNS Sections

```bash
cd scraper
pip install -r requirements.txt

# Quick test (20 sections)
python3 scrape_sample.py

# Full scrape (358 sections, ~6 minutes)
python3 scrape_bns.py
```

## For Practitioners: How to Use This Repo

If you're a product manager or developer looking to understand AI-powered domain search, here's a suggested path:

**Step 1: Understand the data layer**
Start with `scraper/scrape_bns.py` — see how raw HTML becomes structured JSON with categories, severity levels, and keywords. Then look at `backend/scripts/seed_bns_data.py` to see how that data gets embedded and stored in pgvector.

**Step 2: Trace a single request**
Read `backend/graph/bns_workflow.py` to understand the LangGraph workflow. Then follow the flow: `agents/crime_refiner.py` (input processing) → `tools/vector_search.py` (retrieval) → `agents/bns_predictor.py` (LLM reasoning).

**Step 3: Experiment with prompts**
The agent prompts in `agents/bns_predictor.py` are where the legal reasoning happens. Try modifying them — adjust confidence thresholds, change the number of returned sections, or add additional reasoning criteria.

**Step 4: Adapt to your domain**
The pattern here (scrape domain data → embed → retrieve → reason) works for any specialized corpus: medical codes, tax regulations, compliance rules, product catalogs. Replace the BNS data with your domain and the agents with your reasoning logic.

## Project Structure

```
birbal/
├── backend/
│   ├── main.py                    # FastAPI application
│   ├── agents/
│   │   ├── bns_predictor.py       # Legal reasoning agent
│   │   └── crime_refiner.py       # Input normalization agent
│   ├── graph/
│   │   └── bns_workflow.py        # LangGraph workflow
│   ├── tools/
│   │   ├── vector_search.py       # pgvector similarity search
│   │   └── supabase_client.py     # Database client
│   ├── scripts/
│   │   └── seed_bns_data.py       # Database seeding with embeddings
│   └── data/
│       └── bns_sections_PRODUCTION.json  # 358 BNS sections
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── scraper/
│   ├── scrape_bns.py              # Full scraper (358 sections)
│   ├── scrape_sample.py           # Test scraper (20 sections)
│   └── validate_data.py           # Data quality checks
└── supabase/
    └── migrations/
        └── 001_initial_schema.sql  # Database schema with pgvector
```

## License

MIT
