# Birbal — AI Legal Section Predictor (Domain-Specific RAG)

An AI assistant that predicts applicable **BNS (Bharatiya Nyaya Sanhita)** sections from natural language crime descriptions. Uses a **LangGraph multi-agent workflow** with **pgvector similarity search** across a complete, pre-built legal corpus of all 358 BNS sections.

**Ships with the entire BNS corpus** — all 358 sections pre-chunked, structured with metadata (severity, category, keywords, essential elements), and ready to seed into Supabase with a single command. No data collection needed to get started.

## Why This Project

India's new criminal code (BNS, replacing IPC) has 358 sections across 20 chapters. Police officers filing FIRs need to identify the correct legal sections from a verbal crime description — often under time pressure, sometimes in Hindi or Hinglish. This project explores whether a multi-agent AI system with vector search can reliably map unstructured crime narratives to structured legal provisions.

The core product question: **Can an LLM combined with vector similarity search provide accurate, explainable legal section predictions from informal language inputs?**

## What It Does

1. Officer describes a crime in natural language (English, Hindi, or Hinglish)
2. A **Crime Refiner agent** normalizes and translates the input
3. A **BNS Predictor agent** performs vector similarity search across 358 sections, then uses LLM reasoning to rank matches
4. Returns 3-7 applicable sections with confidence scores (0.60-0.95) and legal reasoning

## The BNS Legal Corpus (Included)

This project ships with a **complete, production-ready legal corpus** — you don't need to scrape, collect, or prepare any data.

**What's included in `backend/data/bns_sections_PRODUCTION.json`:**

| Metric | Value |
|--------|-------|
| Total BNS sections | 358 (complete coverage) |
| Sections with subsections | 85 (370 subsections total) |
| Sections with illustrations | 17 (36 legal examples) |
| Sections with explanations | 24 (39 explanatory notes) |
| Hierarchy depth | Up to 3 levels (section → subsection → clause) |
| File size | 874 KB |

**Each section is structured with:**
```json
{
  "section_number": "103",
  "title": "Punishment for murder",
  "full_text": "[complete section text — used for embeddings]",
  "subsections": [
    { "id": "103(1)", "text": "...", "level": 1, "parent": "103" }
  ],
  "illustrations": [
    { "label": "(a)", "text": "[legal example illustrating the provision]" }
  ],
  "explanations": [
    { "number": "1", "text": "[judicial interpretation guidance]" }
  ],
  "metadata": {
    "category": "violence",
    "severity": "very_serious",
    "keywords": ["murder", "death", "intention"],
    "essential_elements": {
      "mens_rea": ["intention to cause death"],
      "actus_reus": ["causing death"],
      "requirements": ["...]"]
    }
  }
}
```

**Why this structure matters for RAG:** The `full_text` field is what gets embedded for vector search. But the structured metadata (category, severity, keywords, essential elements) enables **hybrid retrieval** — combining vector similarity with metadata filtering. The illustrations and explanations give the LLM additional legal context for reasoning, improving prediction accuracy.

**To seed the database:** One command generates embeddings for all 358 sections and loads them into Supabase:
```bash
python scripts/seed_bns_data.py data/bns_sections_PRODUCTION.json
```

For finer-grained search, `seed_bns_chunks.py` creates multiple embeddings per section — main text, individual subsections, and illustrations as separate chunks.

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
┌─────────────────────┐     ┌──────────────────────────────┐
│   BNS Predictor     │────▶│  Supabase pgvector            │
│   (LangGraph Node)  │     │  358 BNS sections + metadata  │
└────────┬────────────┘     │  (pre-built, ready to seed)   │
         │                  └──────────────────────────────┘
         ▼
   Ranked Sections + Confidence Scores + Legal Reasoning
```

**Orchestration:** LangGraph (two-node sequential workflow)

## AI & LLM Concepts

### Domain-Specific RAG: Legal Corpus as Knowledge Base

Unlike generic chatbots that retrieve from unstructured text, Birbal retrieves from a **curated, structured legal corpus**. This changes the RAG dynamics:

- **Precision matters more than recall.** In legal contexts, returning a wrong section is worse than returning fewer sections. The confidence scoring system (0.60-0.95) reflects this.
- **The corpus is finite and complete.** All 358 sections are known upfront — no ingestion pipeline needed for new documents. This simplifies the retrieval layer significantly.
- **Metadata enables hybrid search.** Vector similarity finds semantically related sections, but category and severity metadata can filter results before the LLM sees them. This reduces hallucination risk.

### LangGraph: Agent Decomposition for Legal Reasoning

Even a two-agent pipeline demonstrates the value of separating concerns:

**Crime Refiner Agent:** Handles the messy input layer — translating Hindi/Hinglish, normalizing informal language, extracting the core legal elements from a narrative description. This is pure NLP, no legal reasoning required.

**BNS Predictor Agent:** Handles the legal reasoning — takes the refined input, performs vector search, then reasons about which sections apply and why. The system prompt is tuned for legal precision: explain the reasoning, provide confidence scores, flag edge cases.

**Why separate them:** A single prompt that tries to translate AND do legal reasoning produces worse results than two focused agents. The refiner ensures the predictor always gets clean, structured English input — regardless of what the user typed.

### Vector Search: Bridging Informal Language and Legal Text

The core RAG challenge in this domain: a police officer says "someone broke into a house and stole jewelry" but the BNS says "whoever commits lurking house-trespass or house-breaking, in order to the committing of any offence punishable with imprisonment..."

**pgvector bridges this gap** through embedding similarity — the semantic meaning of the crime description is close to the legal provision, even though the words are completely different. The `search_knowledge_chunks` function in Supabase performs cosine similarity search across all 358 section embeddings.

### Confidence Scoring: Making LLM Outputs Actionable

Rather than returning binary yes/no, the system provides **calibrated confidence scores** (0.60-0.95) for each predicted section. This is critical for legal applications:

- **0.85+**: High confidence — section is very likely applicable
- **0.70-0.84**: Moderate confidence — section may apply depending on specifics
- **0.60-0.69**: Low confidence — section is worth considering but needs verification

The LLM is prompted to provide legal reasoning alongside each score, making the predictions explainable and verifiable.

## Tech Stack

| Layer | Technology | Role |
|-------|-----------|------|
| Agent Orchestration | **LangGraph** | Two-agent workflow (refine → predict) |
| LLM | **OpenAI GPT-4o-mini** | Crime refinement + legal reasoning |
| Vector Database | **Supabase pgvector** | Similarity search across 358 BNS sections |
| Embeddings | **OpenAI text-embedding-3-small** | 1536-dimensional vectors for legal text |
| Backend | FastAPI (Python) | API server |
| Frontend | HTML, Tailwind CSS, Vanilla JS | Prediction UI |

## Key Concepts Explored

**1. Domain-Specific RAG with a Complete Corpus**
The BNS corpus is finite (358 sections), structured (with metadata), and complete (every section included). This is a different RAG challenge than open-ended document retrieval — and the techniques (hybrid search, metadata filtering, structured chunking) are directly applicable to any domain with a bounded knowledge base: medical codes, tax regulations, compliance frameworks.

**2. Multi-Agent Workflow for Input Normalization + Domain Reasoning**
Separating input processing from domain reasoning improves both. The Crime Refiner handles multilingual, informal input. The BNS Predictor handles precise legal matching. Neither agent needs to handle both concerns.

**3. Confidence Scoring for High-Stakes AI**
Legal applications can't tolerate black-box predictions. The confidence scoring system with explainable reasoning shows how to make LLM outputs auditable — a pattern applicable to any domain where incorrect predictions have consequences.

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
```

### Database Setup

```bash
# 1. Run the migration in Supabase SQL Editor
#    Copy contents of supabase/migrations/001_initial_schema.sql

# 2. Seed the BNS corpus (generates embeddings + loads all 358 sections)
python scripts/seed_bns_data.py data/bns_sections_PRODUCTION.json
# Takes ~2-3 minutes (generates OpenAI embeddings for each section)

# 3. Start the backend
python main.py
# API available at http://localhost:8000
```

```bash
# Frontend (separate terminal)
cd frontend
python3 -m http.server 3000
# Visit http://localhost:3000
```

## For Practitioners: How to Use This Repo

If you're a product manager or developer exploring domain-specific AI, legal tech, or RAG with structured corpora, here's a suggested path.

**Step 1: Explore the corpus**
Open `backend/data/bns_sections_PRODUCTION.json` and browse a few sections. Notice the structure: hierarchical subsections, illustrations with legal examples, metadata with category/severity/keywords. This is what "well-structured data for RAG" looks like — and it's the foundation everything else builds on.

**Step 2: Understand the seeding process**
Read `backend/scripts/seed_bns_data.py` — see how each section's `full_text` is embedded using OpenAI's embedding model and stored in pgvector. Then look at `seed_bns_chunks.py` for the alternative approach: multiple embeddings per section (main text, subsections, illustrations as separate chunks). The trade-off: more chunks = better recall but higher cost and latency.

**Step 3: Trace a single prediction**
Read `backend/graph/bns_workflow.py` to understand the LangGraph workflow. Then follow the flow: `agents/crime_refiner.py` (input processing) → `tools/vector_search.py` (retrieval from pgvector) → `agents/bns_predictor.py` (LLM reasoning + confidence scoring).

**Step 4: Experiment with prompts**
The agent prompts in `agents/bns_predictor.py` are where legal reasoning happens. Try modifying them — adjust confidence thresholds, change the number of returned sections, or add additional reasoning criteria. See how output quality changes.

**Step 5: Adapt to your domain**
The pattern here (structured corpus → embed → retrieve → reason with confidence scores) works for any specialized knowledge base: medical codes (ICD-10), tax regulations, compliance rules, product catalogs. Replace the BNS data with your domain corpus, adjust the agent prompts for your reasoning requirements, and the pipeline works the same way.

## Project Structure

```
birbal/
├── backend/
│   ├── main.py                    # FastAPI application
│   ├── config.py                  # Model, embedding, rate limit config
│   ├── agents/
│   │   ├── bns_predictor.py       # Legal reasoning agent
│   │   └── crime_refiner.py       # Input normalization agent
│   ├── graph/
│   │   └── bns_workflow.py        # LangGraph workflow definition
│   ├── tools/
│   │   ├── vector_search.py       # pgvector similarity search
│   │   └── supabase_client.py     # Database client
│   ├── scripts/
│   │   ├── seed_bns_data.py       # Seed all 358 sections with embeddings
│   │   └── seed_bns_chunks.py     # Seed with chunk-level granularity
│   └── data/
│       └── bns_sections_PRODUCTION.json  # Complete BNS corpus (358 sections)
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── supabase/
│   └── migrations/
│       └── 001_initial_schema.sql  # Database schema with pgvector
└── README.md
```

## License

MIT
