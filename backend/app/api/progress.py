"""
Progress API — track user progress across features.
GET /progress
POST /progress
"""
import json
from fastapi import APIRouter, Request
from pydantic import BaseModel
from jose import jwt, JWTError
from app.core.config import settings
from app.core.database import get_db

router = APIRouter(prefix="/progress", tags=["progress"])

# Storage is now backed by SQLite

DEFAULT_PROGRESS = {
    "ats_score": 0,
    "skills_added": 0,
    "interviews_done": 0,
    "quiz_scores": {},
    "skill_bars": {
        "Frontend": 0,
        "Backend": 0,
        "System Design": 0,
        "DevOps": 0,
        "ML / AI": 0,
    },
    "sessions_count": 0,
    "total_solved": 0,
    "best_ats": 0,
    "designation": "Aspiring Professional",
    "memories": [],
    "bookmarks": [],
    "scores": {},
}


class ProgressData(BaseModel):
    ats_score: int = 0
    skills_added: int = 0
    interviews_done: int = 0
    quiz_scores: dict = {}
    skill_bars: dict = {}
    sessions_count: int = 0
    total_solved: int = 0
    best_ats: int = 0
    designation: str = "Aspiring Professional"
    memories: list = []
    bookmarks: list = []
    scores: dict = {}


class ProgressUpdate(BaseModel):
    field: str
    value: int | dict | list | str | None


def _get_user_id(request: Request) -> str:
    """Extract user email (sub) from JWT, or return 'anonymous'."""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth[7:]
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm],
            )
            return payload.get("sub", "anonymous")
        except JWTError:
            pass
    return "anonymous"


@router.get("", response_model=ProgressData)
def get_progress(request: Request):
    uid = _get_user_id(request)
    if uid == "anonymous":
        return ProgressData(**DEFAULT_PROGRESS)
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT progress_json FROM user_progress WHERE email = ?", (uid,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return ProgressData(**json.loads(row["progress_json"]))
    return ProgressData(**DEFAULT_PROGRESS)


@router.post("", response_model=ProgressData)
def update_progress(request: Request, update: ProgressUpdate):
    uid = _get_user_id(request)
    if uid == "anonymous":
        return ProgressData(**DEFAULT_PROGRESS)

    conn = get_db()
    cursor = conn.cursor()
    
    # Get existing
    cursor.execute("SELECT progress_json FROM user_progress WHERE email = ?", (uid,))
    row = cursor.fetchone()
    
    if row:
        store = json.loads(row["progress_json"])
    else:
        store = dict(DEFAULT_PROGRESS)

    # Increment or update
    if update.field == "all" and isinstance(update.value, dict):
        store.update(update.value)
    elif isinstance(update.value, int) and update.field in store and isinstance(store[update.field], int):
        store[update.field] += update.value
    elif isinstance(update.value, dict) and update.field in store and isinstance(store[update.field], dict):
        store[update.field].update(update.value)
    else:
        store[update.field] = update.value

    # Save back
    progress_json = json.dumps(store)
    cursor.execute("""
        INSERT INTO user_progress (email, progress_json, updated_at) 
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(email) DO UPDATE SET 
            progress_json = excluded.progress_json,
            updated_at = CURRENT_TIMESTAMP
    """, (uid, progress_json))
    
    conn.commit()
    conn.close()

    return ProgressData(**store)
