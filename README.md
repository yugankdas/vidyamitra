# VidyāMitra
> AI-powered career advisor for Indian tech professionals · Powered by Groq AI

[![Deploy to GitHub Pages](https://github.com/codewrappy/NewVidyaMitra/actions/workflows/deploy.yml/badge.svg)](https://github.com/codewrappy/NewVidyaMitra/actions/workflows/deploy.yml)

**🌐 Live Demo:** [vidyamitra2026.netlify.app](https://vidyamitra2026.netlify.app)  
**🔧 Backend API:** [newvidyamitra.onrender.com](https://newvidyamitra.onrender.com/docs)

---

## ✨ Features

| Module | Description |
|--------|-------------|
| 🤖 **AI Chat** | Conversational career advisor powered by Groq (Llama 3.3 70B) |
| 📄 **Resume Analyzer** | AI-powered resume critique and ATS scoring |
| 🎤 **Mock Interview** | Role-specific interview questions with AI scoring |
| 🧠 **Skill Quizzes** | Domain knowledge quizzes with instant feedback |
| 🗺️ **Career Planner** | AI-generated career roadmaps and skill-gap analysis |
| 💼 **Job Board** | Live job listings via Adzuna API (AI fallback if unavailable) |
| 📚 **Learning Journey** | Adaptive AI learning paths with YouTube & Coursera recommendations |
| 📊 **Progress Tracker** | Persistent progress tracking across all modules |

---

## 📁 Project Structure

```
NewVidyaMitra/
├── frontend/                    # Legacy vanilla HTML/CSS/JS frontend
│   ├── index.html
│   └── src/
│       ├── components/          # chat.js, interview.js, jobs.js, etc.
│       ├── styles/
│       └── utils/
│
├── src/                         # Main React + TypeScript frontend (Vite)
│   ├── components/
│   │   ├── chat.js              # AI chat interface
│   │   ├── interview.js         # Mock interview panels
│   │   ├── jobs.js              # Job card renderer
│   │   ├── learn.js             # AI learning journey (adaptive paths)
│   │   ├── marquee.js           # Scrolling prompt cards
│   │   └── skills.js            # Skill proficiency bars
│   ├── styles/                  # CSS modules
│   ├── utils/                   # API client, UI helpers
│   └── main.js / main.tsx       # App entry points
│
├── backend/                     # Python FastAPI backend
│   ├── app/
│   │   ├── main.py              # FastAPI app + CORS + router registration
│   │   ├── core/
│   │   │   ├── config.py        # Pydantic settings (reads .env)
│   │   │   └── database.py      # PostgreSQL connection + table init
│   │   ├── api/
│   │   │   ├── auth.py          # Register / Login / JWT
│   │   │   ├── ai_chat.py       # POST /ai/chat → Groq proxy
│   │   │   ├── resume.py        # POST /resume/analyze, /resume/score
│   │   │   ├── interview.py     # GET /interview/question, POST /interview/score
│   │   │   ├── quiz.py          # POST /quiz/generate, /quiz/submit
│   │   │   ├── career.py        # POST /career/plan, /career/skill-gap
│   │   │   ├── jobs.py          # GET /jobs, /jobs/trends (Adzuna + AI)
│   │   │   ├── learn.py         # POST /learn/generate, /learn/adapt
│   │   │   └── progress.py      # GET /progress, POST /progress/update
│   │   └── services/
│   │       ├── groq_service.py  # Groq SDK wrapper (chat + JSON completions)
│   │       └── memory_service.py
│   ├── requirements.txt
│   └── .env.example
│
├── .github/workflows/
│   └── deploy.yml               # GitHub Actions: build + deploy to GitHub Pages
├── netlify.toml                 # Netlify deployment config
├── vite.config.ts               # Vite bundler config
├── tailwind.config.ts           # TailwindCSS config
└── package.json
```

---

## 🚀 Quick Start

### Prerequisites
- **Node.js** v20+
- **Python** 3.11+
- A **PostgreSQL** database (e.g. [Neon](https://neon.tech), [Supabase](https://supabase.com), or local)
- A **Groq API key** — free at [console.groq.com](https://console.groq.com)

---

### 1. Clone the repo

```bash
git clone https://github.com/codewrappy/NewVidyaMitra.git
cd NewVidyaMitra
```

---

### 2. Backend Setup

```bash
cd backend

# Create & activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your keys (see Required Keys section below)

# Start the backend server
uvicorn app.main:app --reload --port 8000
```

- API docs: **http://localhost:8000/docs**
- Health check: **http://localhost:8000/health**

---

### 3. Frontend Setup

```bash
# From the project root
npm install
npm run dev
```

Frontend runs at: **http://localhost:5173**

---

### ⚡ One-command start (PowerShell / Bash)

```powershell
# Windows
.\start.ps1

# Mac/Linux
./start.sh
```

---

## 🔑 Required API Keys

Configure these in `backend/.env`:

| Variable | Where to get | Required? |
|----------|-------------|-----------|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) | ✅ Yes |
| `DATABASE_URL` | Your PostgreSQL connection string | ✅ Yes (for auth & progress) |
| `JWT_SECRET` | Any random secret string | ✅ Yes |
| `ADZUNA_APP_ID` + `ADZUNA_APP_KEY` | [developer.adzuna.com](https://developer.adzuna.com) | Optional (AI fallback used if missing) |

**Example `.env`:**
```env
GROQ_API_KEY=gsk_...
DATABASE_URL=postgresql://user:pass@host:5432/dbname
JWT_SECRET=your-random-secret-here
ADZUNA_APP_ID=your_id
ADZUNA_APP_KEY=your_key
```

---

## 🌐 API Endpoints

### Auth
| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and receive JWT token |

### AI & Career
| Method | Path | Description |
|--------|------|-------------|
| POST | `/ai/chat` | Chat with Groq AI advisor |
| POST | `/resume/analyze` | Full resume analysis |
| POST | `/resume/score` | Quick ATS score |
| GET | `/interview/question?role=` | Get a role-specific interview question |
| POST | `/interview/score` | Score an interview answer |
| POST | `/quiz/generate` | Generate a domain quiz |
| POST | `/quiz/submit` | Submit and score quiz answers |
| POST | `/career/plan` | Generate a career roadmap |
| POST | `/career/skill-gap` | Detect skill gaps for a target role |

### Learning Journey (new!)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/learn/generate` | Generate an adaptive learning path |
| POST | `/learn/adapt` | Re-adapt path based on new quiz scores |

### Jobs & Progress
| Method | Path | Description |
|--------|------|-------------|
| GET | `/jobs?role=` | Get job recommendations (Adzuna + AI) |
| GET | `/jobs/trends` | Market trends for a role |
| GET | `/progress` | Fetch user progress |
| POST | `/progress/update` | Update user progress |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 19, TypeScript, Vite, TailwindCSS, Framer Motion |
| **Frontend (legacy)** | Vanilla HTML / CSS / JS |
| **Backend** | Python 3.11+, FastAPI, Uvicorn |
| **AI** | Groq API — `llama-3.3-70b-versatile` |
| **Database** | PostgreSQL (via psycopg2) |
| **Auth** | JWT (python-jose) + bcrypt password hashing |
| **Job Data** | Adzuna API (AI-generated fallback) |
| **CI/CD** | GitHub Actions → GitHub Pages |
| **Hosting** | Netlify (frontend) · Render (backend) |

---

## 🚢 Deployment

### Frontend — GitHub Pages (auto via CI/CD)
Pushes to `main` automatically trigger the GitHub Actions workflow (`.github/workflows/deploy.yml`), which builds the Vite app and deploys `dist/` to GitHub Pages.

### Frontend — Netlify
Configured via `netlify.toml`. Connect your repo on [netlify.com](https://netlify.com) — it will run `npm run build` and serve `dist/`.

### Backend — Render
Deploy the `backend/` directory as a Web Service on [Render](https://render.com):

```
Build command:  pip install -r requirements.txt
Start command:  uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Set environment variables (`GROQ_API_KEY`, `DATABASE_URL`, `JWT_SECRET`) in the Render dashboard.

---

## 📜 License

[MIT](./LICENSE)
