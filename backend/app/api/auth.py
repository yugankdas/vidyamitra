"""
Auth API — register / login with JWT.
Uses bcrypt directly (bypasses passlib compatibility issue).
Backed by SQLite!
"""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from jose import jwt
import bcrypt
from email_validator import validate_email, EmailNotValidError
from app.core.config import settings
from app.core.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

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
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    return jwt.encode(
        {"sub": email, "exp": expire},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

# ── Routes ──────────────────────────────
@router.post("/register", response_model=TokenResponse, status_code=201)
def register(req: RegisterRequest):
    try:
        email_info = validate_email(req.email, check_deliverability=False) # skip net check for speed
        email = email_info.normalized
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail=f"Invalid email: {str(e)}")

    if len(req.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered in our records")

    hashed_password = _hash_password(req.password)
    name = req.name or email.split("@")[0]
    cursor.execute("INSERT INTO users (email, name, hashed_password) VALUES (?, ?, ?)", (email, name, hashed_password))
    conn.commit()
    conn.close()

    return TokenResponse(
        access_token=_create_token(email),
        name=name,
    )

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    try:
        email = validate_email(req.email, check_deliverability=False).normalized
    except EmailNotValidError:
        email = req.email.strip().lower()

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name, hashed_password FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No account found with this email address",
        )

    if not _verify_password(req.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    return TokenResponse(
        access_token=_create_token(email),
        name=user["name"],
    )
