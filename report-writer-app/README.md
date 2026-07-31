# Pastoral Report Writing Companion

A web tool for Wesley College teachers to draft pastoral report comments quickly. Teachers answer a few questions, the AI drafts a Wesley-style comment, and they copy it into Word.

## Two deployment options

### Option 1: Local development (for testing)

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt

# Create .env with your OpenAI key (see .env.example)
cp .env.example .env
# Then edit .env and paste your OPENAI_API_KEY value

python app.py
```

Open http://localhost:5000 in browser.

### Option 2: Production (API on Vercel, frontend on GitHub)

1. **Push to GitHub:**
   ```bash
   git push origin master
   ```

2. **Deploy API to Vercel:**
   - Connect your GitHub repo to Vercel (https://vercel.com)
   - Set env var `OPENAI_API_KEY` in Vercel project settings
   - Vercel auto-deploys on push

3. **Update frontend API URL** (if your Vercel project name differs):
   Edit `static/script.js` line 1, replace `pastoral-report-writer` with your Vercel URL

4. **Teachers use it:**
   - Clone repo: `git clone https://github.com/...`
   - Open `static/index.html` in browser
   - Frontend calls your Vercel API

## Tech stack

- **Backend:** Flask (local) → Vercel serverless Python (production)
- **Frontend:** Vanilla HTML/CSS/JS, Wesley brand styling
- **AI:** OpenAI `gpt-4o-mini`
- **Reports:** Years 7-12 Tutor (100-150 words) + PYP Semester (180-300 words)

## Privacy

- Student names never entered into the tool
- Teachers add name in Word after copying draft
- No database, no logging of answers/drafts
- Only behavior/learning descriptions sent to OpenAI

## Testing

```bash
pytest tests/ -v
```

31 unit tests, all passing.
