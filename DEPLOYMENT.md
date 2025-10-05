# Birbal - Deployment Guide

Complete guide to deploy Birbal (BNS Section Predictor) to production.

## Architecture

```
Frontend (Vercel)  →  Backend (Railway)  →  Database (Supabase)
   HTML/JS              FastAPI + LangGraph     PostgreSQL + pgvector
```

## Prerequisites

- Supabase account (free tier)
- Railway account ($5/month)
- Vercel account (free tier)
- OpenAI API key

---

## 1. Deploy Database (Supabase) ✅

**Already deployed!**

- **URL:** `https://udbezwcubmdeulwbkukx.supabase.co`
- **Database:** 358 BNS sections, 848 chunks
- **Extensions:** pgvector enabled

---

## 2. Deploy Backend (Railway)

### 2.1 Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your `birbal` repository
4. Set root directory: `backend`

### 2.2 Configure Environment Variables

In Railway dashboard, add these variables:

```bash
# OpenAI
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.3

# Supabase
SUPABASE_URL=https://udbezwcubmdeulwbkukx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIs...
DATABASE_URL=postgresql://postgres...

# Optional: Arize Phoenix
ARIZE_SPACE_ID=...
ARIZE_API_KEY=...
```

### 2.3 Create `Procfile`

In `backend/` directory:

```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 2.4 Create `runtime.txt`

```
python-3.9
```

### 2.5 Update `requirements.txt`

Make sure it includes:

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
langchain==0.1.0
langchain-openai==0.0.2
langgraph==0.0.20
supabase==2.3.0
sqlalchemy
python-dotenv
```

### 2.6 Deploy

Railway will automatically:
1. Install dependencies
2. Start the server
3. Assign a public URL (e.g., `https://birbal-backend.up.railway.app`)

**Note your backend URL!**

---

## 3. Deploy Frontend (Vercel)

### 3.1 Update API URL

Edit `frontend/app.js`:

```javascript
// Change from localhost to Railway URL
const API_BASE_URL = 'https://birbal-backend.up.railway.app';
```

### 3.2 Deploy to Vercel

**Option A: Vercel CLI**

```bash
cd frontend
npm install -g vercel
vercel
```

**Option B: Vercel Dashboard**

1. Go to [vercel.com](https://vercel.com)
2. Click **"New Project"**
3. Import your GitHub repo
4. Set root directory: `frontend`
5. Click **"Deploy"**

**Your frontend URL:** `https://birbal.vercel.app`

---

## 4. Enable CORS

Update `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://birbal.vercel.app",  # Your Vercel URL
        "http://localhost:3000"       # For local dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Redeploy backend after this change.

---

## 5. Testing Production

### Test Backend

```bash
curl https://birbal-backend.up.railway.app/
```

Expected response:
```json
{
  "service": "Birbal BNS Predictor",
  "status": "healthy",
  "version": "1.0.0"
}
```

### Test Prediction

```bash
curl -X POST https://birbal-backend.up.railway.app/predict \
  -H "Content-Type: application/json" \
  -d '{"crime_description": "A person stole gold"}'
```

### Test Frontend

Visit your Vercel URL and try a prediction.

---

## 6. Monitoring

### Railway Dashboard

- View logs
- Monitor memory/CPU
- Check request metrics

### Supabase Dashboard

- Monitor database queries
- Check vector search performance
- Review storage usage

### Costs Estimate

| Service | Tier | Cost |
|---------|------|------|
| Supabase | Free | $0 |
| Railway | Hobby | $5/month |
| Vercel | Free | $0 |
| OpenAI API | Pay-as-go | ~$10/month (1000 queries) |
| **Total** | | **~$15/month** |

---

## 7. Custom Domain (Optional)

### Frontend (Vercel)

1. Go to Vercel project settings
2. Click **"Domains"**
3. Add custom domain (e.g., `birbal.yourdomain.com`)
4. Update DNS records as instructed

### Backend (Railway)

1. Go to Railway project settings
2. Click **"Domains"**
3. Add custom domain (e.g., `api.yourdomain.com`)
4. Update DNS records

Then update frontend `API_BASE_URL` to your custom backend domain.

---

## 8. Security Checklist

- [ ] Environment variables secured
- [ ] CORS properly configured
- [ ] HTTPS enabled (automatic on Railway/Vercel)
- [ ] Rate limiting enabled (optional)
- [ ] API key rotation policy
- [ ] Database backups enabled (Supabase auto-backup)

---

## 9. Troubleshooting

### "Cannot connect to backend"

- Check Railway logs for errors
- Verify environment variables
- Test backend health endpoint

### "CORS error"

- Verify `allow_origins` in `main.py`
- Check frontend is using correct URL
- Redeploy backend after CORS changes

### "No predictions returned"

- Check OpenAI API key is valid
- Verify database has chunks (848 chunks expected)
- Check Supabase connection

---

## 10. Scaling

### If traffic increases:

1. **Railway:** Upgrade to Pro plan ($20/month)
2. **Supabase:** Upgrade to Pro ($25/month) for better performance
3. **OpenAI:** Consider caching common queries
4. **Add Redis:** Cache predictions for identical queries

---

## Support

- Backend logs: Railway dashboard
- Database: Supabase dashboard → Logs
- API errors: Check Railway logs for stack traces

**Your Birbal deployment is ready! 🎉**
