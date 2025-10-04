# ⚠️ IMPORTANT: BNS Data File Reference

## 🎯 PRODUCTION FILE TO USE

**File:** `backend/data/bns_sections_PRODUCTION.json`

**Size:** 874KB

**Contains:**
- ✅ All 358 BNS sections
- ✅ Hierarchical subsection structure
- ✅ Illustrations extracted
- ✅ Explanations extracted
- ✅ Full text for embeddings
- ✅ Complete metadata

## Usage

### For Database Seeding:
```bash
cd backend
python scripts/seed_bns_data.py data/bns_sections_PRODUCTION.json
```

### For Testing:
```python
import json

with open('backend/data/bns_sections_PRODUCTION.json', 'r') as f:
    bns_data = json.load(f)

print(f"Loaded {len(bns_data)} sections")
```

## ❌ DO NOT USE These Files

Archive files (for reference only):
- `scraper/_ARCHIVE_bns_sections_raw.json`
- `scraper/_ARCHIVE_bns_sections_enhanced.json`
- `scraper/_ARCHIVE_bns_sections_sample.json`
- `scraper/_ARCHIVE_bns_sections_sample_test.json`

These are intermediate processing files kept for reference.

## Quick Validation

To verify you're using the correct file:

```bash
# Should show: 358 sections
cat backend/data/bns_sections_PRODUCTION.json | python3 -c "import sys, json; print(len(json.load(sys.stdin)), 'sections')"

# Should show hierarchical structure
cat backend/data/bns_sections_PRODUCTION.json | python3 -c "import sys, json; data=json.load(sys.stdin); print('Keys:', list(data[0].keys()))"
# Expected: ['section_number', 'title', 'full_text', 'subsections', 'illustrations', 'explanations', 'metadata']
```

## File Location

```
birbal/
├── backend/
│   ├── data/
│   │   └── bns_sections_PRODUCTION.json  ← USE THIS
│   └── ...
├── scraper/
│   ├── _ARCHIVE_*.json                    ← DO NOT USE (reference only)
│   └── ...
```

---

**See `DATA_READY.md` for complete data documentation**
