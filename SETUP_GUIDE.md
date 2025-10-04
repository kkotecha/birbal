# Setup Guide - BNS Section Predictor

## Step 1: Complete BNS Data Scraping

The scraper may take 5-10 minutes due to network delays. Run it manually:

```bash
cd /Users/khanjan/Development/birbal/scraper
python3 scrape_bns.py
```

**Expected output:** `bns_sections.json` with 358 sections

**Validate:**
```bash
python3 validate_data.py bns_sections.json
```

## Step 2: Set Up Supabase

### 2.1 Create Supabase Project

1. Go to https://supabase.com
2. Sign up/Sign in
3. Click "New Project"
4. Fill in:
   - Name: `bns-predictor`
   - Database Password: (generate strong password - save it!)
   - Region: Choose closest to India
5. Click "Create new project"
6. Wait 2-3 minutes for provisioning

### 2.2 Run Database Migration

1. In Supabase dashboard, go to **SQL Editor**
2. Click "New query"
3. Copy entire content from `supabase/migrations/001_initial_schema.sql`
4. Paste and click "Run"
5. Verify tables created: Go to **Table Editor**, you should see:
   - `bns_sections`
   - `predictions`
   - `rate_limits`

### 2.3 Get API Keys

1. In Supabase dashboard, go to **Settings** → **API**
2. Copy:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **anon/public key** (starts with `eyJ...`)

## Step 3: Set Up Backend

### 3.1 Install Dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3.2 Configure Environment

1. Create `.env` file:
```bash
cp .env.example .env
```

2. Edit `.env` with your keys:
```env
# Required
OPENAI_API_KEY=sk-proj-xxxxx  # Get from https://platform.openai.com/api-keys
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJxxxxx

# Optional (for observability)
ARIZE_SPACE_ID=
ARIZE_API_KEY=
```

### 3.3 Seed BNS Data

```bash
# Use the PRODUCTION file (from backend directory)
python scripts/seed_bns_data.py data/bns_sections_PRODUCTION.json
```

This will:
- Generate embeddings for each section
- Upload to Supabase
- Create vector index for similarity search

**Expected time:** ~2-3 minutes for 358 sections

## Step 4: Implement Backend Agents

The backend uses 6 agents in a LangGraph workflow:

```
Input → Agent 0 (Text Refinement) → Agent 1 (Crime Classifier) →
Agent 2 (Element Extractor) → Agent 3 (Section Searcher) →
Agent 4 (Legal Reasoner) → Agent 5 (Compiler) → Output
```

Create these files (templates provided in original spec):
- `backend/agents/text_refinement.py`
- `backend/agents/crime_classifier.py`
- `backend/agents/element_extractor.py`
- `backend/agents/section_searcher.py`
- `backend/agents/legal_reasoner.py`
- `backend/agents/compiler.py`

## Step 5: Test Locally

```bash
cd backend
uvicorn main:app --reload
```

Visit: http://localhost:8000/docs

Test the `/predict-sections` endpoint with:
```json
{
  "description": "व्यक्ति ने जानबूझकर दूसरे व्यक्ति को चाकू से हमला किया और मार डाला"
}
```

## Step 6: Deploy

### 6.1 Deploy Backend to Railway

1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select `birbal` repo
5. Railway will auto-detect Python
6. Add environment variables in Railway dashboard
7. Deploy

### 6.2 Deploy Frontend to Vercel

```bash
cd frontend
vercel --prod
```

Or via Vercel dashboard:
1. Import GitHub repo
2. Set root directory to `frontend`
3. Deploy

### 6.3 Update Frontend API URL

Edit `frontend/script.js`:
```javascript
const API_URL = 'https://your-railway-app.railway.app';
```

## Troubleshooting

### Scraper Issues
- **Timeout:** Increase delay in `scrape_bns.py` to 2-3 seconds
- **Empty output:** Check network connectivity
- **Missing sections:** Run validation script

### Database Issues
- **Vector extension error:** Ensure pgvector is enabled in Supabase
- **Permission denied:** Use service_role key for migrations
- **Embedding errors:** Verify OpenAI API key

### Backend Issues
- **Import errors:** Ensure all dependencies installed
- **Rate limit:** Check Supabase connection limits
- **Slow responses:** Optimize agent prompts

## Next Steps After Setup

1. Test with various inputs (Hindi, English, Hinglish)
2. Validate predictions against actual BNS
3. Monitor costs (OpenAI usage)
4. Set up monitoring with Arize Phoenix
5. Add more test cases
6. Optimize for production

## Quick Validation Checklist

- [ ] Scraper completed (358 sections)
- [ ] Supabase project created
- [ ] Database migration successful
- [ ] BNS data seeded with embeddings
- [ ] Backend runs locally
- [ ] Test prediction works
- [ ] Frontend connects to backend
- [ ] Deployed to production
- [ ] Environment variables configured
- [ ] Monitoring set up
