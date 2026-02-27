"""
Progress API — track user progress across features.
GET /progress
POST /progress
"""
from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/progress", tags=["progress"])

# In-memory progress store  { user_id: ProgressData }
# In production use a database
_progress_store: dict[str, dict] = {}

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
    "sessions": [],
}


class ProgressData(BaseModel):
    ats_score: int = 0
    skills_added: int = 0
    interviews_done: int = 0
    quiz_scores: dict = {}
    skill_bars: dict = {}
    sessions: list = []


class ProgressUpdate(BaseModel):
    field: str
    value: int | dict | list | str


def _get_user_id(request: Request) -> str:
    """Extract user ID from JWT or use 'anonymous'."""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:20]  # simple hash for demo
    return "anonymous"


@router.get("", response_model=ProgressData)
def get_progress(request: Request):
    uid = _get_user_id(request)
    data = _progress_store.get(uid, dict(DEFAULT_PROGRESS))
    return ProgressData(**data)


@router.post("", response_model=ProgressData)
def update_progress(request: Request, update: ProgressUpdate):
    uid = _get_user_id(request)
    if uid not in _progress_store:
        _progress_store[uid] = dict(DEFAULT_PROGRESS)

    store = _progress_store[uid]

    # Increment numeric fields
    if isinstance(update.value, int) and update.field in store and isinstance(store[update.field], int):
        store[update.field] += update.value
    elif isinstance(update.value, dict) and update.field in store and isinstance(store[update.field], dict):
        store[update.field].update(update.value)
    else:
        store[update.field] = update.value

    return ProgressData(**store)
