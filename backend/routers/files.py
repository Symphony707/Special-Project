import os
import hashlib
import json
import io
import logging
from typing import Optional

from fastapi import (APIRouter, UploadFile, File,
                     Depends, HTTPException)
from backend.middleware.auth_middleware import get_current_user, get_optional_user
from datamind.security.upload_guard import UploadGuard
from datamind.security.sanitizer import InputSanitizer
from datamind.tools.file_loader import UniversalFileLoader, FileLoadError
from backend.utils.df_store import DataFrameStore
import database as db
from config import UPLOADS_DIR

router = APIRouter()
logger = logging.getLogger(__name__)
df_store = DataFrameStore()

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    # Enforce 1-file limit for Guests
    if user.get("is_guest"):
        count = db.get_user_file_count(user["id"])
        if count >= 1:
            raise HTTPException(status_code=403, detail="Guest limit reached (1 file). Register to unlock full vault capacity.")

    file_bytes = await file.read()
    safe_name = InputSanitizer.sanitize_filename(file.filename)

    # 1. Pre-calculate hash
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    
    # 2. Check for global existence
    existing = db.get_global_file_by_hash(file_hash)
    if existing:
        user_ref = db.get_user_file_ref(user["id"], existing["id"])
        if user_ref:
            # Re-load into memory if needed
            if not df_store.get_df(existing["id"]):
                try:
                    df = UniversalFileLoader.load(file_bytes, safe_name, user_id=user["id"])
                    df_store.set_df(existing["id"], df)
                except FileLoadError as e:
                    raise HTTPException(status_code=400, detail=str(e))
            
            return {
                "duplicate": True,
                "message": f"Already uploaded on {user_ref['uploaded_at'][:10]}",
                "file_id": existing["id"],
                "fingerprint": json.loads(existing["schema_fingerprint"])
            }
        else:
            db.create_user_file_ref(user["id"], existing["id"], safe_name)
            # Load into memory
            try:
                df = UniversalFileLoader.load(file_bytes, safe_name, user_id=user["id"])
                df_store.set_df(existing["id"], df)
            except FileLoadError as e:
                raise HTTPException(status_code=400, detail=str(e))
                
            return {
                "duplicate": False,
                "reused": True,
                "file_id": existing["id"],
                "fingerprint": json.loads(existing["schema_fingerprint"])
            }

    # 3. Fresh Upload
    try:
        df = UniversalFileLoader.load(file_bytes, safe_name, user_id=user["id"])
    except FileLoadError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 4. Success -> Process & Store
    fingerprint = UniversalFileLoader.generate_fingerprint(df)
    pii = fingerprint.get("pii_detected", False)
    safe_fp = UniversalFileLoader.mask_pii_samples(fingerprint) if pii else fingerprint

    global_id = db.insert_global_file(
        file_hash, safe_name, json.dumps(safe_fp),
        len(df), len(df.columns),
        fingerprint.get("detected_domain", "generic")
    )
    db.create_user_file_ref(user["id"], global_id, safe_name)

    # Persist to disk
    if not os.path.exists(UPLOADS_DIR):
        os.makedirs(UPLOADS_DIR, exist_ok=True)
    
    file_path = os.path.join(UPLOADS_DIR, file_hash)
    if not os.path.exists(file_path):
        with open(file_path, "wb") as f:
            f.write(file_bytes)

    # Key memory cache
    df_store.set_df(global_id, df)

    return {
        "duplicate": False,
        "file_id": global_id,
        "fingerprint": safe_fp,
        "row_count": len(df),
        "col_count": len(df.columns),
        "pii_detected": pii
    }

@router.get("/list")
async def list_files(user=Depends(get_optional_user)):
    if not user:
        return {"files": []}
    files = db.get_user_files(user["id"])
    return {"files": files}

@router.post("/load/{file_id}")
async def load_file(file_id: int, user=Depends(get_current_user)):
    # 1. Authorize
    ref = db.get_user_file_ref(user["id"], file_id)
    if not ref:
        raise HTTPException(status_code=403, detail="Access denied")

    # 2. Retrieve Data (with auto-hydration)
    df = df_store.get_df_auto(file_id)
    if df is None:
        raise HTTPException(status_code=404, detail="File could not be retrieved or re-hydrated. Please re-ingest.")

    # 4. Return Metadata
    gf = db.get_global_file_by_id(file_id)
    fp = json.loads(gf["schema_fingerprint"])
    db.update_last_accessed(user["id"], file_id)
    
    return {
        "file_id": file_id,
        "fingerprint": fp,
        "row_count": len(df),
        "col_count": len(df.columns),
        "columns": list(df.columns),
        "preview": df.head(10).to_dict(orient="records")
    }

@router.delete("/{file_id}")
async def delete_file(file_id: int, user=Depends(get_current_user)):
    ref = db.get_user_file_ref(user["id"], file_id)
    if not ref:
        raise HTTPException(status_code=403, detail="Access denied")
    
    db.delete_user_file_ref(user["id"], file_id)
    # Note: We don't delete from df_store immediately as other users might be using it,
    # and we don't delete from disk (global storage).
    return {"success": True}
