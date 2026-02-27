"""
Auth API — register / login with JWT.
Uses bcrypt directly (bypasses passlib compatibility issue).
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from jose import jwt
import bcrypt
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

# In-memory user store  { email: { name, hashed_password } }
_users: dict[str, dict] = {}


# ── Models ──────────────────────────────
class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str = ""


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    name: str


# ── Helpers ─────────────────────────────
def _hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def _verify_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed)


def _create_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    return jwt.encode(
        {"sub": email, "exp": expire},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


# ── Routes ──────────────────────────────
@router.post("/register", response_model=TokenResponse, status_code=201)
def register(req: RegisterRequest):
    if req.email in _users:
        raise HTTPException(status_code=400, detail="Email already registered")
    _users[req.email] = {
        "name": req.name or req.email.split("@")[0],
        "hashed_password": _hash_password(req.password),
    }
    return TokenResponse(
        access_token=_create_token(req.email),
        name=_users[req.email]["name"],
    )


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    user = _users.get(req.email)
    if not user or not _verify_password(req.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return TokenResponse(
        access_token=_create_token(req.email),
        name=user["name"],
    )
