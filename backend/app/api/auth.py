"""Authentication endpoints."""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.base import get_db
from app.models.user import User

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class RegisterRequest(BaseModel):
    email: str
    password: str
    display_name: str


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


def create_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check duplicate
    result = await db.execute(select(User).where(User.email == req.email))
    if result.scalar_one_or_none():
        raise HTTPException(400, "Email already registered")

    user = User(
        email=req.email,
        password_hash=pwd_context.hash(req.password),
        display_name=req.display_name,
    )
    db.add(user)
    await db.flush()

    token = create_token(user.id)
    return TokenResponse(
        access_token=token,
        user={"id": user.id, "email": user.email, "display_name": user.display_name},
    )


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()

    if not user or not pwd_context.verify(req.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")

    token = create_token(user.id)
    return TokenResponse(
        access_token=token,
        user={"id": user.id, "email": user.email, "display_name": user.display_name},
    )
