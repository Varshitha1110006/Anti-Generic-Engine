import os
import uuid
from datetime import datetime, timezone, timedelta

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, EmailStr, Field

JWT_ALGORITHM = "HS256"
LOCKOUT_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(user_id: str, email: str) -> str:
    payload = {"sub": user_id, "email": email, "type": "access", "exp": datetime.now(timezone.utc) + timedelta(days=7)}
    return jwt.encode(payload, os.environ["JWT_SECRET"], algorithm=JWT_ALGORITHM)


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: str
    created_at: str


class AuthResponse(BaseModel):
    token: str
    user: UserOut


def public_user(doc: dict) -> dict:
    return {"id": doc["id"], "name": doc["name"], "email": doc["email"], "created_at": doc["created_at"]}


def build_auth_router(db: AsyncIOMotorDatabase) -> tuple[APIRouter, callable]:
    router = APIRouter(prefix="/auth", tags=["auth"])

    async def get_current_user(request: Request) -> dict:
        token = request.cookies.get("access_token")
        header = request.headers.get("Authorization", "")
        if header.startswith("Bearer "):
            token = header[7:]
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")
        try:
            payload = jwt.decode(token, os.environ["JWT_SECRET"], algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Session expired. Please sign in again.")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid session")
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user = await db.users.find_one({"id": payload["sub"]}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return public_user(user)

    async def check_lockout(identifier: str):
        record = await db.login_attempts.find_one({"identifier": identifier})
        if record and record.get("count", 0) >= LOCKOUT_ATTEMPTS:
            locked_until = datetime.fromisoformat(record["last_attempt"]) + timedelta(minutes=LOCKOUT_MINUTES)
            if datetime.now(timezone.utc) < locked_until:
                raise HTTPException(status_code=429, detail="Too many failed attempts. Try again in 15 minutes.")
            await db.login_attempts.delete_one({"identifier": identifier})

    @router.post("/register", response_model=AuthResponse)
    async def register(payload: RegisterRequest):
        email = payload.email.lower().strip()
        if await db.users.find_one({"email": email}):
            raise HTTPException(status_code=409, detail="An account with this email already exists. Sign in instead.")
        user = {"id": str(uuid.uuid4()), "name": payload.name.strip(), "email": email, "password_hash": hash_password(payload.password), "created_at": datetime.now(timezone.utc).isoformat()}
        await db.users.insert_one({**user})
        return {"token": create_access_token(user["id"], email), "user": public_user(user)}

    @router.post("/login", response_model=AuthResponse)
    async def login(payload: LoginRequest, request: Request):
        email = payload.email.lower().strip()
        identifier = f"{request.client.host if request.client else 'unknown'}:{email}"
        await check_lockout(identifier)
        user = await db.users.find_one({"email": email}, {"_id": 0})
        if not user or not verify_password(payload.password, user["password_hash"]):
            await db.login_attempts.update_one({"identifier": identifier}, {"$inc": {"count": 1}, "$set": {"last_attempt": datetime.now(timezone.utc).isoformat()}}, upsert=True)
            raise HTTPException(status_code=401, detail="Email or password is incorrect.")
        await db.login_attempts.delete_one({"identifier": identifier})
        return {"token": create_access_token(user["id"], email), "user": public_user(user)}

    @router.get("/me", response_model=UserOut)
    async def me(user: dict = Depends(get_current_user)):
        return user

    @router.post("/logout")
    async def logout():
        return {"ok": True}

    return router, get_current_user


async def ensure_auth_indexes(db: AsyncIOMotorDatabase):
    await db.users.create_index("email", unique=True)
    await db.users.create_index("id", unique=True)
    await db.login_attempts.create_index("identifier")


async def seed_demo_user(db: AsyncIOMotorDatabase):
    email = os.environ["DEMO_EMAIL"].lower()
    password = os.environ["DEMO_PASSWORD"]
    existing = await db.users.find_one({"email": email})
    if existing is None:
        await db.users.insert_one({"id": str(uuid.uuid4()), "name": "Demo Founder", "email": email, "password_hash": hash_password(password), "created_at": datetime.now(timezone.utc).isoformat()})
    elif not verify_password(password, existing["password_hash"]):
        await db.users.update_one({"email": email}, {"$set": {"password_hash": hash_password(password)}})
