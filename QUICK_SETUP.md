# Quick Setup - API Keys for PersonaLab

## 🎯 What You Need

### REQUIRED:
**Google Gemini API** (for simulations)
- Get it: https://makersuite.google.com/app/apikey
- Add to: `backend/.env`
- Format: `GOOGLE_API_KEY=AIzaSy...`

### OPTIONAL (for better personas):
**OpenAI API** (recommended)
- Get it: https://platform.openai.com/api-keys  
- Add to: `backend/.env`
- Format: `OPENAI_API_KEY=sk-...`

**OR Anthropic Claude** (alternative)
- Get it: https://console.anthropic.com/
- Add to: `backend/.env`
- Format: `ANTHROPIC_API_KEY=sk-ant-...`

---

## 📝 Create Backend .env File

```bash
cd backend
nano .env
```

**Paste this (replace with your keys):**
```env
GOOGLE_API_KEY=your_google_key_here
OPENAI_API_KEY=your_openai_key_here
```

**Save**: Ctrl+O, Enter, Ctrl+X

---

## ✅ Test It Works

```bash
# Start backend
cd backend
uvicorn app.main:app --reload

# Start frontend (in new terminal)
cd frontend
npm run dev
```

**Open**: http://localhost:3000

---

## 💰 Costs

- **Google Gemini**: FREE (60 requests/min)
- **OpenAI**: ~$0.002 per persona
- **Anthropic**: Similar to OpenAI

---

## 🆘 Quick Fixes

**"API key not found"**
→ Check `.env` file is in `/backend/` folder

**"Rate limit"**  
→ Wait 1 minute, Gemini has 60/min limit

**"Invalid key"**
→ Copy entire key, no spaces

---

**Full docs**: See `AI_API_SETUP_GUIDE.md`
