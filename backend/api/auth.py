"""
Auth API — register / login with JWT.
Uses an in-memory user store for simplicity.
Replace with a real DB (SQLite, Postgres) for production.
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import jwt
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
        "hashed_password": pwd_ctx.hash(req.password),
    }
    return TokenResponse(
        access_token=_create_token(req.email),
        name=_users[req.email]["name"],
    )


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    user = _users.get(req.email)
    if not user or not pwd_ctx.verify(req.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return TokenResponse(
        access_token=_create_token(req.email),
        name=user["name"],
    )
