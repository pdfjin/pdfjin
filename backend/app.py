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
from fastapi.staticfiles import StaticFiles
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
    # Robust origin matching for all pdfjin.com variants and local dev
    allowed_origins = ["https://pdfjin.com", "https://www.pdfjin.com", "http://localhost:3000", "http://localhost:5000", "http://localhost:8080"]
    cors_origin = "https://pdfjin.com"
    if origin:
        if any(o in origin for o in ["pdfjin.com", "localhost", "127.0.0.1"]) or origin == "null":
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
        size_limit_key = f"{plan}_limit_size"
        if plan == "enterprise": 
            limit_key = "ent_limit"
            size_limit_key = "ent_limit_size"
        
        # Convert limits to int to be safe
        try:
            max_tasks = int(pricing.get(limit_key, 50 if plan == "pro" else (500 if plan == "enterprise" else 3)))
            max_size_mb = int(pricing.get(size_limit_key, 50))
        except:
            max_tasks = 3
            max_size_mb = 50

        # 2a. Check File Size (via Content-Length)
        content_length = request.headers.get("Content-Length")
        if content_length:
            if int(content_length) > max_size_mb * 1024 * 1024:
                return add_cors(Response(
                    content=json.dumps({"detail": f"File too large. Max allowed for your plan: {max_size_mb}MB"}),
                    status_code=413, media_type="application/json"
                ))

        # 2b. Check Task Usage
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
    
    # Google SEO Optimization: Force ETag over Last-Modified
    if "last-modified" in response.headers:
        del response.headers["last-modified"]
    
    return add_cors(response)

# ─── ROOT & HEALTH ────────────────────────────────────────────

@app.get("/site-settings")
async def get_settings():
    db = load_db()
    # Expose only the publishable key (safe for frontend) — never the secret key
    result = dict(db)
    result["stripe_pub_key"] = db.get("stripe_pub_key", "")
    result["paypal_client_id"] = db.get("paypal_client_id", "")
    return result

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
    pro_monthly: float = Form(None),
    pro_yearly: float = Form(None),
    pro_limit: int = Form(None),
    pro_limit_size: int = Form(None),
    pro_data_limit: int = Form(None),
    ent_monthly: float = Form(None),
    ent_yearly: float = Form(None),
    ent_limit: int = Form(None),
    ent_limit_size: int = Form(None),
    free_limit: int = Form(None),
    free_limit_size: int = Form(None),
    flexi_plan: float = Form(None),
    flexi_credits: int = Form(None),
    flexi_validity: int = Form(None),
    flexi_size: int = Form(None)
):
    if admin_key != ADMIN_PASS:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    db = load_db()
    if "pricing" not in db: db["pricing"] = {}
    p = db["pricing"]
    
    # Pro updates
    if "pro" not in p: p["pro"] = {}
    if pro_monthly is not None: p["pro"]["monthly"] = pro_monthly
    if pro_yearly is not None: p["pro"]["yearly"] = pro_yearly
    if pro_limit is not None: p["pro_limit"] = pro_limit
    if pro_limit_size is not None: p["pro_limit_size"] = pro_limit_size
    if pro_data_limit is not None: p["pro_data_limit"] = pro_data_limit
    
    # Enterprise updates
    if "enterprise" not in p: p["enterprise"] = {}
    if ent_monthly is not None: p["enterprise"]["monthly"] = ent_monthly
    if ent_yearly is not None: p["enterprise"]["yearly"] = ent_yearly
    if ent_limit is not None: p["ent_limit"] = ent_limit
    if ent_limit_size is not None: p["ent_limit_size"] = ent_limit_size
    
    # Free updates
    if free_limit is not None: p["free_limit"] = free_limit
    if free_limit_size is not None: p["free_limit_size"] = free_limit_size
    
    # Flexi updates
    if flexi_plan is not None: p["flexi-plan"] = flexi_plan
    if flexi_credits is not None: p["flexi_credits"] = flexi_credits
    if flexi_validity is not None: p["flexi_validity"] = flexi_validity
    if flexi_size is not None: p["flexi_size"] = flexi_size
    
    save_db(db)
    return {"status": "success", "pricing": db["pricing"]}

# ─── ADMIN: SITE SETTINGS (Announcement, Maintenance, Tool Status) ────────────
@app.post("/admin/update-settings")
async def update_settings(
    admin_key: str = Form(...),
    announcement: str = Form(None),
    maintenance: str = Form(None),
    allow_registrations: str = Form(None),
    tool_status: str = Form(None)
):
    if admin_key != ADMIN_PASS:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    db = load_db()
    
    if announcement is not None:
        db["announcement"] = announcement.strip()
    
    if maintenance is not None:
        db["maintenance"] = maintenance.lower() in ("true", "1", "yes")
    
    if allow_registrations is not None:
        db["allow_registrations"] = allow_registrations.lower() in ("true", "1", "yes")
    
    if tool_status is not None:
        try:
            db["tool_status"] = json.loads(tool_status)
        except Exception:
            pass
    
    save_db(db)
    return {"status": "success", "announcement": db.get("announcement", ""), "maintenance": db.get("maintenance", False)}

# ─── ADMIN: INFRASTRUCTURE CONFIG (Stripe/PayPal pub keys) ────────────────
@app.post("/admin/update-infra")
async def update_infra(
    admin_key: str = Form(...),
    stripe_pub_key: str = Form(None),
    paypal_client_id: str = Form(None),
    api_url: str = Form(None)
):
    if admin_key != ADMIN_PASS:
        raise HTTPException(status_code=403, detail="Forbidden")

    db = load_db()
    # Only store public-safe keys — secret key stays in Cloud Run env vars
    if stripe_pub_key is not None:
        db["stripe_pub_key"] = stripe_pub_key.strip()
    if paypal_client_id is not None:
        db["paypal_client_id"] = paypal_client_id.strip()
    if api_url is not None:
        db["api_url_override"] = api_url.strip()

    save_db(db)
    return {"status": "success", "stripe_pub_key_set": bool(db.get("stripe_pub_key"))}

# ─── ADMIN: CLEANUP ──────────────────────────────────────────────────────────
@app.post("/admin/cleanup")
async def admin_cleanup(admin_key: str = Form(...)):
    if admin_key != ADMIN_PASS:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    cleaned = 0
    try:
        temp_dir = tempfile.gettempdir()
        for f in os.listdir(temp_dir):
            f_path = os.path.join(temp_dir, f)
            try:
                if os.path.isfile(f_path):
                    os.remove(f_path)
                    cleaned += 1
                elif os.path.isdir(f_path):
                    shutil.rmtree(f_path)
                    cleaned += 1
            except Exception:
                pass
    except Exception as e:
        return {"status": "partial", "detail": str(e), "cleaned": cleaned}
    
    return {"status": "success", "cleaned": cleaned}

# ─── CLEAN URLS & FRONTEND ROUTES ─────────────────────────────
@app.get("/pages/{page_name}")
async def serve_clean_page(page_name: str):
    # Support extensionless URLs like /pages/admin -> /pages/admin.html
    # but also handle cases where .html is already present
    safe_name = os.path.basename(page_name)
    
    if safe_name.endswith(".html"):
        filename = safe_name
    else:
        filename = f"{safe_name}.html"
        
    target = os.path.join("static_frontend", "pages", filename)
    if os.path.exists(target):
        return FileResponse(target)
    raise HTTPException(status_code=404)

@app.get("/admin")
async def admin_shortcut():
    # Shortcut for /admin -> /pages/admin.html
    return FileResponse(os.path.join("static_frontend", "pages", "admin.html"))

@app.get("/blog-admin.html")
async def blog_admin_shortcut():
    return FileResponse(os.path.join("static_frontend", "pages", "blog-admin.html"))

@app.get("/social-callback.html")
async def social_callback_shortcut():
    return FileResponse(os.path.join("static_frontend", "pages", "social-callback.html"))


# ─── INCLUDE MODULAR ROUTERS ──────────────────────────────────
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(ai_studio.router, tags=["AI Studio"])
app.include_router(pdf_ops.router, tags=["PDF Operations"])
app.include_router(converters.router, tags=["Converters"])
app.include_router(payments.router, tags=["Payments"])
app.include_router(editor.router, tags=["Editor"])

# ─── SERVE FRONTEND ───────────────────────────────────────────
# Mount static files at the end so it doesn't shadow API routes
app.mount("/", StaticFiles(directory="static_frontend", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    # Use $PORT environment variable for Cloud Run compatibility
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
