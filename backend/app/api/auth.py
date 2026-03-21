"""
Auth API — register / login with JWT.
Uses bcrypt directly (bypasses passlib compatibility issue).
"""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from jose import jwt
import bcrypt
from email_validator import validate_email, EmailNotValidError
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
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    return jwt.encode(
        {"sub": email, "exp": expire},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


# ── Routes ──────────────────────────────
@router.post("/register", response_model=TokenResponse, status_code=201)
def register(req: RegisterRequest):
    # 1. Robust Email Validation
    try:
        # Check format and deliverability (DNS check)
        email_info = validate_email(req.email, check_deliverability=True)
        email = email_info.normalized
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail=f"Invalid email: {str(e)}")

    # 2. Password Complexity
    if len(req.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")

    # 3. Check Records
    if email in _users:
        raise HTTPException(status_code=400, detail="Email already registered in our records")

    _users[email] = {
        "name": req.name or email.split("@")[0],
        "hashed_password": _hash_password(req.password),
    }
    return TokenResponse(
        access_token=_create_token(email),
        name=_users[email]["name"],
    )


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    # Normalize email
    try:
        email = validate_email(req.email, check_deliverability=False).normalized
    except EmailNotValidError:
        email = req.email.strip().lower()

    user = _users.get(email)
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
