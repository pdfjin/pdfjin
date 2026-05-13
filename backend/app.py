import os
import io
import json
import time
import asyncio
import tempfile
import shutil
from typing import List, Dict
from datetime import datetime, date
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import hashlib
from jose import jwt, JWTError
from routers.auth import load_users, ALGORITHM, SECRET_KEY, hash_api_key

from routers import ai_studio, pdf_ops, converters, auth, payments, editor
from database import load_db, save_db

# ─── AUTHENTICATION ──────────────────────────────────────────
API_KEY = "pdfjin_dev_secret_key_2026"
auth_scheme = HTTPBearer()

def validate_api_key(auth: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    if auth.credentials != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

# ─── CLEANUP TASK ─────────────────────────────────────────────
async def cleanup_temp_files():
    while True:
        try:
            now = time.time()
            temp_dir = tempfile.gettempdir()
            for f in os.listdir(temp_dir):
                f_path = os.path.join(temp_dir, f)
                if os.stat(f_path).st_mtime < now - 3600:
                    if os.path.isfile(f_path): os.remove(f_path)
                    elif os.path.isdir(f_path): shutil.rmtree(f_path)
        except Exception: pass
        await asyncio.sleep(3600)

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(cleanup_temp_files())
    yield

# ─── MAIN APP INITIALIZATION ──────────────────────────────────
app = FastAPI(title="PDFjin API - Modular Engine", lifespan=lifespan)

# Note: We will handle CORS manually in a middleware to ensure it works for ALL status codes (including 429)

# ─── RATE LIMITING & CORS MIDDLEWARE (UNIFIED) ────────────────
rate_limit_store: Dict[str, Dict] = {} # Fallback for IPs

@app.middleware("http")
async def unified_middleware(request: Request, call_next):
    origin = request.headers.get("origin")
    # Robust origin matching for all pdfjin.com variants
    allowed_origins = ["https://pdfjin.com", "https://www.pdfjin.com", "http://localhost:3000"]
    cors_origin = "https://pdfjin.com"
    if origin:
        if any(o in origin for o in ["pdfjin.com", "localhost:3000"]):
            cors_origin = origin
    
    # Helper to ensure CORS headers are on EVERY response
    def add_cors(resp):
        resp.headers["Access-Control-Allow-Origin"] = cors_origin
        resp.headers["Access-Control-Allow-Credentials"] = "true"
        resp.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, DELETE, PUT"
        resp.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, X-API-Key"
        resp.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
        return resp

    # 1. Handle Preflight (OPTIONS)
    if request.method == "OPTIONS":
        return add_cors(Response(status_code=204))

    # 2. Rate Limiting Logic (only for POST/Write ops)
    path = request.url.path
    if request.method == "POST" and not any(p in path for p in ["/admin", "/auth", "/site-settings", "/health"]):
        today = date.today().isoformat()
        user_id = None
        plan = "free"
        
        # Identify User
        api_key = request.headers.get("X-API-Key")
        auth_header = request.headers.get("Authorization")
        
        db = load_db()
        identified_user = None
        
        if api_key:
            h_key = hash_api_key(api_key)
            for u in db.get("users", []):
                if any(k["hashed_key"] == h_key for k in u.get("api_keys", [])):
                    identified_user = u
                    plan = "enterprise"
                    break
        elif auth_header and auth_header.startswith("Bearer "):
            try:
                token = auth_header.split(" ")[1]
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                email = payload.get("sub")
                identified_user = next((u for u in db.get("users", []) if u["email"] == email), None)
                if identified_user:
                    plan = identified_user.get("plan", "free")
            except: pass

        # Assign Limits
        pricing = db.get("pricing", {})
        limit_key = f"{plan}_limit"
        if plan == "enterprise": limit_key = "ent_limit"
        
        # Convert limits to int to be safe
        try:
            max_tasks = int(pricing.get(limit_key, 50 if plan == "pro" else (500 if plan == "enterprise" else 3)))
        except:
            max_tasks = 3

        # Check Usage
        if identified_user:
            if "usage" not in identified_user: identified_user["usage"] = {}
            if identified_user["usage"].get("date") != today:
                identified_user["usage"] = {"date": today, "count": 0}
            
            current_count = int(identified_user["usage"].get("count", 0))
            if current_count >= max_tasks:
                return add_cors(Response(
                    content=json.dumps({"detail": f"Daily limit of {max_tasks} reached. Please upgrade."}),
                    status_code=429, media_type="application/json"
                ))
            
            identified_user["usage"]["count"] = current_count + 1
            identified_user["tasks"] = identified_user.get("tasks", 0) + 1
            save_db(db)
        else:
            ip = request.client.host if request.client else "127.0.0.1"
            usage = rate_limit_store.get(ip, {"date": today, "count": 0})
            if usage["date"] != today: usage = {"date": today, "count": 0}
            
            current_guest_count = int(usage.get("count", 0))
            if current_guest_count >= 3:
                return add_cors(Response(
                    content=json.dumps({"detail": "Guest limit (3/day) reached. Sign in for more."}),
                    status_code=429, media_type="application/json"
                ))
            usage["count"] = current_guest_count + 1
            rate_limit_store[ip] = usage

    # 3. Call Process & Add CORS to normal response
    try:
        response = await call_next(request)
    except Exception as e:
        import traceback
        print(f"CRITICAL MIDDLEWARE ERROR: {str(e)}\n{traceback.format_exc()}")
        return add_cors(JSONResponse(
            status_code=500,
            content={"detail": f"System Error: {str(e)}"}
        ))
    
    return add_cors(response)

# ─── ROOT & HEALTH ────────────────────────────────────────────
@app.get("/")
async def health_check():
    return {"status": "online", "engine": "modular_v2", "version": "2.0-CORS-POWER"}

@app.get("/site-settings")
async def get_settings():
    return load_db()

@app.get("/health")
async def health_status():
    users = auth.load_users()
    return {
        "status": "online", 
        "timestamp": time.time(),
        "user_count": len(users)
    }

# ─── ADMIN ROUTES ─────────────────────────────────────────────
ADMIN_PASS = "pdfjin-admin-2026"

@app.post("/admin/update-pricing")
async def update_pricing(
    admin_key: str = Form(...),
    pro_limit: int = Form(None),
    ent_limit: int = Form(None),
    free_limit: int = Form(None)
):
    if admin_key != ADMIN_PASS:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    db = load_db()
    if "pricing" not in db: db["pricing"] = {}
    if pro_limit is not None: db["pricing"]["pro_limit"] = pro_limit
    if ent_limit is not None: db["pricing"]["ent_limit"] = ent_limit
    if free_limit is not None: db["pricing"]["free_limit"] = free_limit
    save_db(db)
    return {"status": "success", "pricing": db["pricing"]}

# ─── INCLUDE MODULAR ROUTERS ──────────────────────────────────
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(ai_studio.router, tags=["AI Studio"])
app.include_router(pdf_ops.router, tags=["PDF Operations"])
app.include_router(converters.router, tags=["Converters"])
app.include_router(payments.router, tags=["Payments"])
app.include_router(editor.router, tags=["Editor"])

if __name__ == "__main__":
    import uvicorn
    # Use $PORT environment variable for Cloud Run compatibility
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
