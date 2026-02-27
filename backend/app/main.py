"""
VidyāMitra — FastAPI Backend
Entry point: uvicorn app.main:app --reload
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# Import all routers
from app.api.auth import router as auth_router
from app.api.ai_chat import router as chat_router
from app.api.resume import router as resume_router
from app.api.interview import router as interview_router
from app.api.quiz import router as quiz_router
from app.api.career import router as career_router
from app.api.jobs import router as jobs_router
from app.api.progress import router as progress_router

app = FastAPI(
    title="VidyāMitra API",
    description="AI-powered career advisor backend — powered by Groq",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.cors_origin,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5500",      # Live Server
        "http://127.0.0.1:5500",
        "null",                       # file:// opened directly in browser
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ─────────────────────────────
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(resume_router)
app.include_router(interview_router)
app.include_router(quiz_router)
app.include_router(career_router)
app.include_router(jobs_router)
app.include_router(progress_router)


# ── Health check ─────────────────────────
@app.get("/", tags=["health"])
def root():
    return {
        "status": "ok",
        "app": "VidyāMitra",
        "version": "1.0.0",
        "powered_by": "Groq",
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=True)
