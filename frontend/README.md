# Birbal Frontend

Simple, clean HTML/CSS/JS interface for BNS Section Predictor.

## Features

- ✅ Hindi & English input support
- ✅ Real-time BNS section predictions
- ✅ Confidence scoring with color-coding
- ✅ Legal hierarchy display (Primary → Aggravating → Related)
- ✅ Expandable section details
- ✅ Responsive design
- ✅ No build step required

## Tech Stack

- **HTML5** - Semantic structure
- **Tailwind CSS** - Utility-first styling
- **Vanilla JavaScript** - No frameworks
- **Fetch API** - Backend communication

## Usage

### 1. Start Backend

```bash
cd backend
python3 main.py
```

Backend runs on http://localhost:8000

### 2. Open Frontend

Simply open `index.html` in your browser:

```bash
open index.html
```

Or use a local server:

```bash
python3 -m http.server 3000
```

Then visit http://localhost:3000

## How It Works

1. **User enters crime description** (Hindi or English)
2. **Frontend calls `/predict` API**
3. **Backend processes:**
   - Agent 0: Translates to English
   - Agent 1: Predicts BNS sections
4. **Results displayed** with:
   - Primary offense (90-95% confidence)
   - Aggravating factors (80-90%)
   - Related sections (70-80%)

## Color Coding

- 🟢 **Green** - Very High Confidence (>90%)
- 🔵 **Blue** - High Confidence (80-90%)
- 🟡 **Yellow** - Medium Confidence (70-80%)
- ⚪ **Gray** - Low Confidence (<70%)

## API Integration

The frontend connects to the backend API at `http://localhost:8000`:

**Endpoint:** `POST /predict`

**Request:**
```json
{
  "crime_description": "A person entered a house and stole gold"
}
```

**Response:**
```json
{
  "refined_description": "A person entered a house and stole gold",
  "predictions": [
    {
      "section_number": "303",
      "section_title": "Theft",
      "confidence": 0.95,
      "reasoning": "Primary offense: Theft...",
      "section_text": "...",
      "metadata": {...}
    }
  ]
}
```

## Customization

### Change API URL

Edit `app.js`:

```javascript
const API_BASE_URL = 'http://your-backend-url.com';
```

### Styling

Uses Tailwind CSS via CDN. Modify classes in `index.html` or add custom styles.

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Deployment

For production, deploy to:
- **Vercel** (recommended)
- **Netlify**
- **GitHub Pages**

Update `API_BASE_URL` to your production backend URL.
