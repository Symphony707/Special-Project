import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from backend.middleware.auth_middleware import get_current_user, get_optional_user
from backend.utils.df_store import DataFrameStore
from backend.utils.agent_utils import run_agent_async, ForensicEncoder
from datamind.agent.summary_agent import SummaryAgent
import database as db

router = APIRouter()
logger = logging.getLogger(__name__)
df_store = DataFrameStore()

@router.get("/stats")
async def get_stats(user=Depends(get_optional_user)):
    if not user:
        return {
            "total_files": 0,
            "total_analyses": 0,
            "total_patterns": 0,
            "files": []
        }
    user_id = user["id"]
    files   = db.get_user_files(user_id)

    total_analyses = 0
    total_patterns = 0
    for f in files:
        fid = f.get("global_file_id")
        if fid:
            # Note: This is an expensive operation if many files
            # For a production app, we would cache these counts in a table.
            h = db.get_analysis_history(user_id, fid, limit=1000)
            total_analyses += len(h)
            p = db.get_patterns_for_user_file(user_id, fid, limit=100)
            total_patterns += len(p)

    return {
        "total_files":     len(files),
        "total_analyses":  total_analyses,
        "total_patterns":  total_patterns,
        "files":           files
    }

@router.get("/activity/{file_id}")
async def get_activity(
    file_id: int,
    user=Depends(get_current_user)
):
    ref = db.get_user_file_ref(user["id"], file_id)
    if not ref:
        return {"activity": [], "patterns": []}
    return {
        "activity": db.get_analysis_history(
            user["id"], file_id, limit=6),
        "patterns": db.get_patterns_for_user_file(
            user["id"], file_id, limit=5)
    }

@router.post("/initialize/{file_id}")
async def initialize_asset(
    file_id: int,
    user=Depends(get_current_user)
):
    # 1. Authorization
    ref = db.get_user_file_ref(user["id"], file_id)
    if not ref:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # 2. Retrieve Data
    df = df_store.get_df(file_id)
    if df is None:
        # Attempt reload logic (mirrored from files.py for robustness)
        global_file = db.get_global_file_by_id(file_id)
        if global_file:
            from config import UPLOADS_DIR
            import os
            from datamind.tools.file_loader import UniversalFileLoader
            file_path = os.path.join(UPLOADS_DIR, global_file["file_hash"])
            if os.path.exists(file_path):
                try:
                    with open(file_path, "rb") as f:
                        file_bytes = f.read()
                    df = UniversalFileLoader.load(file_bytes, global_file["original_filename"])
                    df_store.set_df(file_id, df)
                except Exception as e:
                    logger.error(f"Auto-reload fallback failed in dashboard: {e}")

    if df is None:
        raise HTTPException(status_code=404, detail="File not found in storage. Please re-upload.")

    # 3. Trigger Agent Analysis (Async)
    # We want to run a Summary scan
    agent = SummaryAgent()
    result = await run_agent_async(agent.summarize_dossier, df)
    
    # 4. Persistence
    # Save the summary to analysis memory
    db.save_analysis(
        user["id"], file_id,
        "System Initialization Scan", "summary",
        "summary_agent",
        result.get("response", "")[:200],
        result.get("response", ""),
        "dossier",
        json.dumps({"figures": result.get("figures", [])}, cls=ForensicEncoder)
    )
    
    # Extract initial patterns if possible (Simple heuristics for now)
    # In a more advanced version, we'd have a specific Agent for this.
    brief = result.get("response", "")
    findings = [line.strip("- ").strip() for line in brief.split("\n") if line.strip().startswith("-")]
    
    for finding in findings[:3]:
        db.upsert_pattern(
            user["id"], file_id,
            "Forensic Insight",
            finding,
            json.dumps(list(df.columns[:5])), # Placeholder columns
            0.85
        )

    return {"success": True, "brief": result.get("response")}

@router.get("/ollama-status")
async def get_ollama_status():
    from datamind.llm.ollama_client import check_ollama_health
    from config import OLLAMA_MODEL
    available = await check_ollama_health()
    return {
        "status": "online" if available else "offline",
        "model": OLLAMA_MODEL if available else None
    }

