import json
import os
import sys
import time

# Cloud Run ephemeral sync to Google Cloud Storage
DB_PATH = "db.json"
GCS_BUCKET = "pdgjin-db-v1" # Use a dedicated bucket for DB
GCS_DB_BLOB = "db.json"

_gcs_client = None

def _get_client():
    global _gcs_client
    if _gcs_client is None:
        try:
            from google.cloud import storage
            # Explicit project ID for Cloud Run
            _gcs_client = storage.Client(project="pdgjin")
            print("GCS: Storage client initialized.")
        except Exception as e:
            print(f"GCS: Failed to init client: {e}")
    return _gcs_client

def _gcs_available():
    return _get_client() is not None

def _load_from_gcs():
    """Try to load db.json from GCS bucket with retry/logging."""
    client = _get_client()
    if not client: return None
    try:
        from google.cloud import storage
        bucket = client.bucket(GCS_BUCKET)
        blob = bucket.blob(GCS_DB_BLOB)
        if blob.exists():
            content = blob.download_as_text()
            print(f"GCS: Successfully loaded from gs://{GCS_BUCKET}/{GCS_DB_BLOB}")
            return json.loads(content)
        else:
            print(f"GCS: Blob gs://{GCS_BUCKET}/{GCS_DB_BLOB} not found.")
    except Exception as e:
        print(f"GCS Error (Load): {e}", file=sys.stderr)
    return None

def _save_to_gcs(data):
    """Save db.json to GCS bucket for persistence."""
    client = _get_client()
    if not client: return False
    try:
        from google.cloud import storage
        bucket = client.bucket(GCS_BUCKET)
        
        # Auto-create bucket if missing (first run)
        if not bucket.exists():
            print(f"GCS: Creating bucket {GCS_BUCKET}...")
            client.create_bucket(bucket, location="ASIA")
            
        blob = bucket.blob(GCS_DB_BLOB)
        blob.upload_from_string(
            json.dumps(data, indent=2),
            content_type="application/json"
        )
        print(f"GCS: Successfully saved to gs://{GCS_BUCKET}/{GCS_DB_BLOB}")
        return True
    except Exception as e:
        print(f"GCS Error (Save): {e}", file=sys.stderr)
        return False

DEFAULT_DB = {
    "stats": {"total_revenue": 0, "total_users": 0, "conversions_today": 0},
    "announcement": "",
    "maintenance": False, 
    "pricing": {"free_limit": 3},
    "users": []
}

_cached_db = None
_cached_db_time = 0

def load_db():
    global _cached_db, _cached_db_time
    is_cloud_run = bool(os.environ.get("K_SERVICE"))

    # If cache is valid (less than 10 seconds old in prod, infinite locally unless updated), return it
    if _cached_db is not None:
        if not is_cloud_run or (time.time() - _cached_db_time < 10):
            return _cached_db

    if is_cloud_run:
        # In Cloud Run, GCS is the source of truth
        gcs_data = _load_from_gcs()
        if gcs_data:
            try:
                with open(DB_PATH, "w") as f:
                    json.dump(gcs_data, f, indent=2)
            except:
                pass
            _cached_db = gcs_data
            _cached_db_time = time.time()
            return gcs_data
            
        # Fallback to local bundled db.json if GCS fails
        if os.path.exists(DB_PATH):
            try:
                with open(DB_PATH, "r") as f:
                    _cached_db = json.load(f)
                    _cached_db_time = time.time()
                    return _cached_db
            except:
                pass
    else:
        # Local dev: Try local file first (to prevent old GCS data from overwriting new local data)
        if os.path.exists(DB_PATH):
            try:
                with open(DB_PATH, "r") as f:
                    _cached_db = json.load(f)
                    _cached_db_time = time.time()
                    return _cached_db
            except:
                pass

        # Try GCS (Persistence fallback)
        gcs_data = _load_from_gcs()
        if gcs_data:
            # Cache locally for performance/fallback
            with open(DB_PATH, "w") as f:
                json.dump(gcs_data, f, indent=2)
            _cached_db = gcs_data
            _cached_db_time = time.time()
            return gcs_data

    # 3. Fall back to default
    print(f"DATABASE: Creating new local db.json")
    with open(DB_PATH, "w") as f:
        json.dump(DEFAULT_DB, f)
    _cached_db = DEFAULT_DB.copy()
    _cached_db_time = time.time()
    return _cached_db

def save_db(db_data):
    global _cached_db, _cached_db_time
    _cached_db = db_data
    _cached_db_time = time.time()

    # 1. Save locally (Ephemeral)
    with open(DB_PATH, "w") as f:
        json.dump(db_data, f, indent=2)
    
    # 2. Persist to GCS (Global)
    _save_to_gcs(db_data)

