# VidyāMitra — The Renaissance Edition
> AI-powered career advisor for Indian tech professionals · Powered by Claude AI

---

## 📁 Project Structure

```
vidyamitra/
├── frontend/                    # Static HTML/CSS/JS frontend
│   ├── index.html               # Main entry point
│   └── src/
│       ├── styles/
│       │   ├── main.css         # Root variables, nav, hero, layout
│       │   ├── components.css   # All UI components
│       │   └── animations.css   # Keyframe animations
│       ├── components/
│       │   ├── marquee.js       # Scrolling prompt cards
│       │   ├── chat.js          # AI chat (calls /ai/chat)
│       │   ├── interview.js     # Scroll-pinned interview panels
│       │   ├── skills.js        # Skill proficiency bars
│       │   └── jobs.js          # Job card renderer
│       ├── utils/
│       │   ├── api.js           # Central API client
│       │   └── ui.js            # Scroll, reveal, counters, toasts
│       └── main.js              # Entry point
│
└── backend/                     # Python FastAPI backend
    ├── app/
    │   ├── main.py              # FastAPI app + CORS + router registration
    │   ├── core/
    │   │   └── config.py        # Pydantic settings (reads .env)
    │   ├── api/
    │   │   ├── auth.py          # Register / Login / JWT
    │   │   ├── ai_chat.py       # POST /ai/chat  → Claude proxy
    │   │   ├── resume.py        # POST /resume/analyze
    │   │   ├── interview.py     # GET /interview/question, POST /interview/score
    │   │   ├── quiz.py          # POST /quiz/generate, POST /quiz/submit
    │   │   ├── career.py        # POST /career/plan, POST /career/skill-gap
    │   │   ├── jobs.py          # GET /jobs, GET /jobs/trends
    │   │   └── progress.py      # GET /progress, POST /progress/update
    │   └── services/
    │       └── claude_service.py # Anthropic SDK wrapper
    ├── requirements.txt
    └── .env.example
```

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone <your-repo>
cd vidyamitra
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys (at minimum: ANTHROPIC_API_KEY)

# Start the server
uvicorn app.main:app --reload --port 8000
```

The API will be live at: **http://localhost:8000**  
Interactive docs: **http://localhost:8000/docs**

### 3. Frontend Setup

```bash
cd frontend

# Option A: Plain HTML (no build step)
# Just open index.html in a browser, or serve with:
python -m http.server 3000
# Then visit: http://localhost:3000

# Option B: Vite (recommended for development)
npm create vite@latest . -- --template vanilla
npm install
npm run dev
```

---

## 🔑 Required API Keys

| Key | Where to get | Required? |
|-----|-------------|-----------|
| `ANTHROPIC_API_KEY` | https://console.anthropic.com | ✅ Yes |
| `SUPABASE_URL` + `SUPABASE_KEY` | https://supabase.com | Optional (uses memory store) |
| `YOUTUBE_API_KEY` | https://console.cloud.google.com | Optional |
| `NEWS_API_KEY` | https://newsapi.org | Optional |
| `EXCHANGE_API_KEY` | https://exchangerate-api.com | Optional |

---

## 🌐 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login, get JWT token |
| POST | `/ai/chat` | Chat with Claude AI agent |
| POST | `/resume/analyze` | Analyze resume text |
| POST | `/resume/score` | Quick ATS score |
| GET  | `/interview/question?role=` | Get interview question |
| POST | `/interview/score` | Score an interview answer |
| POST | `/quiz/generate` | Generate domain quiz |
| POST | `/quiz/submit` | Submit quiz answers |
| POST | `/career/plan` | Generate career roadmap |
| POST | `/career/skill-gap` | Detect skill gaps |
| GET  | `/jobs?role=` | Get job recommendations |
| GET  | `/jobs/trends` | Market trends |
| GET  | `/progress` | User progress data |
| POST | `/progress/update` | Update progress |

---

## 🛠️ Tech Stack

**Frontend:** Vanilla HTML/CSS/JS (no framework — easily migrated to React)  
**Backend:** Python 3.11+, FastAPI, Uvicorn  
**AI:** Anthropic Claude (claude-sonnet-4-20250514)  
**Database:** Supabase / PostgreSQL (in-memory fallback for dev)  
**Auth:** JWT with bcrypt password hashing  

---

## 📦 Production Deployment

```bash
# Backend (with gunicorn)
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Or with Docker
docker build -t vidyamitra-backend .
docker run -p 8000:8000 --env-file .env vidyamitra-backend
```
