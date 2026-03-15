from fastapi import APIRouter, HTTPException, Depends, status, Form
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import json
import os
import time
from datetime import datetime, timedelta, date
from jose import JWTError, jwt
from passlib.context import CryptContext
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import load_db, save_db

router = APIRouter()

# Configuration
SECRET_KEY = "pdfjin_super_secret_auth_key_2026"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

USERS_DB_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_DB_PATH = os.path.join(os.path.dirname(USERS_DB_DIR), "db.json")

class User(BaseModel):
    full_name: str
    email: EmailStr
    password: str  # Hashed in DB, but raw in request
    created_at: str = ""
    plan: str = "free"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

def load_users():
    db = load_db()
    return db.get("users", [])

def save_users(users):
    db = load_db()
    db["users"] = users
    if "stats" in db:
        db["stats"]["total_users"] = len(users)
    save_db(db)

def get_password_hash(password):
    # Bcrypt has a 72-byte limit. We truncate to 71 chars just to be safe with UTF-8.
    return pwd_context.hash(str(password)[:71])

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def sanitize_name(name: str) -> str:
    if not name:
        return "Subscriber"
    clean_parts = [p for p in str(name).split() if '@' not in p]
    return " ".join(clean_parts) if clean_parts else "Subscriber"

@router.post("/register", response_model=Token)
async def register(user: User):
    users = load_users()
    if any(u['email'] == user.email for u in users):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Sanitize name: remove any space-separated words containing '@'
    sanitized_name = sanitize_name(user.full_name)

    hashed_password = get_password_hash(user.password)
    new_user = {
        "full_name": sanitized_name,
        "email": user.email,
        "password": hashed_password,
        "created_at": datetime.now().isoformat(),
        "plan": "free"
    }
    users.append(new_user)
    save_users(users)
    
    # Generate token
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": new_user["email"],
            "full_name": new_user["full_name"],
            "plan": new_user["plan"]
        }
    }

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    users = load_users()
    user = next((u for u in users if u['email'] == credentials.email), None)
    
    if not user or not verify_password(credentials.password, user['password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user['email']},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": user["email"],
            "full_name": user["full_name"],
            "plan": user.get("plan", "free")
        }
    }

@router.get("/me")
async def get_me(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        users = load_users()
        user = next((u for u in users if u['email'] == email), None)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
            
        return {
            "email": user["email"],
            "full_name": user["full_name"],
            "plan": user.get("plan", "free"),
            "usage": user.get("usage", {"date": date.today().isoformat(), "count": 0}),
            "tasks": user.get("tasks", 0)
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

@router.post("/update-profile")
async def update_profile(token: str = Form(...), full_name: str = Form(...)):
    """User-facing endpoint to update own profile (name only)."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        users = load_users()
        for u in users:
            if u["email"] == email:
                u["full_name"] = sanitize_name(full_name)
                save_users(users)
                return {
                    "status": "success",
                    "full_name": u["full_name"],
                    "email": u["email"],
                    "plan": u.get("plan", "free")
                }
        
        raise HTTPException(status_code=404, detail="User not found")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
@router.get("/admin/users")
async def admin_list_users(admin_key: str):
    # For now, matching the frontend ADMIN_PASS. In prod, use safer auth.
    if admin_key != "pdfjin-admin-2026":
        raise HTTPException(status_code=403, detail="Forbidden")
    
    users = load_users()
    # Clean up users to remove passwords before sending
    safe_users = []
    for u in users:
        safe_users.append({
            "full_name": u.get("full_name", "Unknown"),
            "email": u["email"],
            "plan": u.get("plan", "free"),
            "created_at": u.get("created_at", "N/A"),
            "status": u.get("status", "Active"),
            "tasks": u.get("tasks", 0)
        })
    return safe_users

@router.post("/admin/update-user")
async def admin_update_user(
    admin_key: str = Form(...), 
    email: str = Form(...), 
    tier: Optional[str] = Form(None), 
    status: Optional[str] = Form(None),
    full_name: Optional[str] = Form(None),
    password: Optional[str] = Form(None)
):
    if admin_key != "pdfjin-admin-2026":
        raise HTTPException(status_code=403, detail="Forbidden")
    
    users = load_users()
    for u in users:
        if u["email"] == email:
            if tier: u["plan"] = str(tier).lower()
            if status: u["status"] = str(status)
            if full_name: u["full_name"] = sanitize_name(str(full_name))
            if password and str(password).strip() != "":
                u["password"] = get_password_hash(str(password))
            
            save_users(users)
            return {"status": "success", "user": {"email": email, "plan": u["plan"], "status": u["status"]}}
    
    raise HTTPException(status_code=404, detail="User not found")

@router.post("/admin/add-user")
async def admin_add_user(
    admin_key: str = Form(...), 
    full_name: str = Form(...),
    email: str = Form(...), 
    password: str = Form(...),
    tier: str = Form("free")
):
    if admin_key != "pdfjin-admin-2026":
        raise HTTPException(status_code=403, detail="Forbidden")
    
    users = load_users()
    if any(u['email'] == email for u in users):
        raise HTTPException(status_code=400, detail="User already exists")
    
    hashed_password = get_password_hash(password)
    new_user = {
        "full_name": sanitize_name(full_name),
        "email": email,
        "password": hashed_password,
        "created_at": datetime.now().isoformat(),
        "plan": tier.lower(),
        "status": "Active"
    }
    users.append(new_user)
    save_users(users)
    return {"status": "success"}

@router.post("/admin/delete-user")
async def admin_delete_user(
    admin_key: str = Form(...), 
    email: str = Form(...)
):
    if admin_key != "pdfjin-admin-2026":
        raise HTTPException(status_code=403, detail="Forbidden")
    
    users = load_users()
    new_users = [u for u in users if u["email"] != email]
    
    if len(users) == len(new_users):
        raise HTTPException(status_code=404, detail="User not found")
        
    save_users(new_users)
    return {"status": "success"}

import secrets
import hashlib

# --- API KEY HELPERS ---
def generate_api_key():
    return f"pj_live_{secrets.token_urlsafe(32)}"

def hash_api_key(key: str):
    return hashlib.sha256(key.encode()).hexdigest()

@router.post("/api-keys/generate")
async def generate_user_key(token: str = Form(...), label: str = Form("Primary Key")):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        users = load_users()
        user = next((u for u in users if u["email"] == email), None)
        
        if not user or user.get("plan", "free") != "enterprise":
            raise HTTPException(status_code=403, detail="Enterprise plan required")
            
        new_raw_key = generate_api_key()
        hashed_key = hash_api_key(new_raw_key)
        
        if "api_keys" not in user: user["api_keys"] = []
        
        key_entry = {
            "id": int(time.time() * 1000),
            "label": label,
            "hashed_key": hashed_key,
            "hint": f"pk_...{new_raw_key[-4:]}",
            "created_at": datetime.now().isoformat()
        }
        
        user["api_keys"].append(key_entry)
        save_users(users)
        
        return {"status": "success", "key": new_raw_key, "entry": key_entry}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid session")

@router.get("/api-keys")
async def list_user_keys(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        users = load_users()
        user = next((u for u in users if u["email"] == email), None)
        
        if not user: raise HTTPException(status_code=404, detail="User not found")
        
        return user.get("api_keys", [])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid session")

@router.delete("/api-keys/{key_id}")
async def revoke_user_key(key_id: int, token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        users = load_users()
        user = next((u for u in users if u["email"] == email), None)
        
        if not user: raise HTTPException(status_code=404, detail="User not found")
        
        if "api_keys" in user:
            user["api_keys"] = [k for k in user["api_keys"] if k["id"] != key_id]
            save_users(users)
            
        return {"status": "success"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid session")
