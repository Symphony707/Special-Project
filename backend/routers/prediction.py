import json
from fastapi import APIRouter, Depends, HTTPException
from backend.middleware.auth_middleware import get_current_user
from backend.models.schemas import PredictionRequest
from backend.utils.df_store import DataFrameStore
from backend.utils.agent_utils import run_agent_async, ForensicEncoder, serialize_agent_result
from backend.utils.response_formatter import format_prediction_response, format_analysis_response
from datamind.agent.predict_agent import PredictAgent
from datamind.agent.diagnostic_agent import DiagnosticAgent
from datamind.agent.orchestrator import Orchestrator
import database as db
import logging
import pandas as pd

from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()
df_store = DataFrameStore()

@router.post("/run")
async def run_prediction(
    data: PredictionRequest,
    user=Depends(get_current_user)
):
    # 1. Authorization
    ref = db.get_user_file_ref(user["id"], data.file_id)
    if not ref:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # 2. Retrieve Data (with auto-hydration)
    df = df_store.get_df_auto(data.file_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Simulated data could not be retrieved or re-hydrated. Please re-ingest.")

    # 3. Validation (Lightweight diagnostic)
    gf = db.get_global_file_by_id(data.file_id)
    fingerprint = json.loads(gf["schema_fingerprint"])
    
    # Run the agent
    predictor = PredictAgent(df)
    result = await run_agent_async(
        predictor.run_prediction_mission,
        target_col=data.target_column,
        mode="auto"
    )
    
    # 5. Persist prediction results
    if result.get("success"):
        res_data = result.get("results", {})
        db.save_prediction(
            user["id"], data.file_id,
            data.target_column,
            res_data.get("task_type"),
            res_data.get("best_model_name"),
            res_data.get("test_accuracy", 0),
            res_data.get("f1_score", 0),
            res_data.get("test_rmse", 0),
            json.dumps(res_data.get("feature_importances", {}), cls=ForensicEncoder),
            result.get("response", "")
        )
        
    result = serialize_agent_result(result or {})
    structured = format_prediction_response(result)
    result['structured_response'] = structured
    return result

@router.get("/suggest-target/{file_id}")
async def suggest_target(
    file_id: int,
    user=Depends(get_current_user)
):
    ref = db.get_user_file_ref(user["id"], file_id)
    if not ref:
        raise HTTPException(status_code=403,detail="Access denied")

    df = df_store.get_df_auto(file_id)
    if df is None:
        raise HTTPException(status_code=404,
                           detail="File not loaded")

    # Auto-suggest: find best candidate target column
    # Heuristic: numeric col with most variance, not an ID column
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    id_keywords  = ['id','key','code','index','uuid','hash']
    candidates   = [
        c for c in numeric_cols
        if not any(k in c.lower() for k in id_keywords)
    ]

    if not candidates and df.select_dtypes(
            include='object').columns.tolist():
        # Fall back to categorical columns
        obj_cols   = df.select_dtypes(include='object').columns
        candidates = [
            c for c in obj_cols
            if df[c].nunique() <= 20
        ]

    suggested = candidates[0] if candidates else \
                (df.columns[-1] if len(df.columns) > 0 else None)

    # Determine task type for suggested target
    task_type = 'regression'
    if suggested and suggested in df.columns:
        col = df[suggested].dropna()
        if str(col.dtype) == 'object' or col.nunique() <= 15:
            task_type = 'classification'

    return {
        'suggested_target': suggested,
        'task_type':        task_type,
        'all_candidates':   candidates[:10],
        'columns':          list(df.columns),
    }

@router.post("/quick-summary/{file_id}")
async def quick_summary(
    file_id: int,
    user=Depends(get_current_user)
):
    """Auto-runs a summary analysis on the dataset"""
    ref = db.get_user_file_ref(user["id"], file_id)
    if not ref:
        raise HTTPException(status_code=403,detail="Access denied")

    df = df_store.get_df_auto(file_id)
    if df is None:
        raise HTTPException(status_code=404,
                           detail="File not loaded")

    gf          = db.get_global_file_by_id(file_id)
    fingerprint = json.loads(gf["schema_fingerprint"])

    # Use summary agent with sampled data for speed
    sample_df = df.sample(min(5000, len(df)),
                          random_state=42)

    context_pkg = {
        "schema_fingerprint":   fingerprint,
        "conversation_history": [],
        "file_id":              file_id,
        "prior_patterns":       [],
    }

    try:
        orch   = Orchestrator(df=sample_df)
        result = await run_agent_async(
            orch.route_query,
            "Give me a comprehensive forensic overview "
            "of this dataset including key statistics, "
            "patterns, and actionable insights.",
            fingerprint=fingerprint,
            file_id=file_id
        )
    except Exception as e:
        logger.error(f"Quick summary error: {e}")
        raise HTTPException(status_code=500,
                           detail="Summary failed")

    # NEW: Wrap with formatter (Prioritizing the detailed narrative for the dossier)
    full_narrative = result.get('lab_narrative') or result.get('response', '')
    
    # If the response contains distinct info not in lab_narrative, prefix it
    if result.get('lab_narrative') and result.get('response') and len(result['response']) > 20:
        if result['response'][:50] not in result['lab_narrative'][:200]:
            full_narrative = f"{result['response']}\n\n{result['lab_narrative']}"

    result = serialize_agent_result(result)
    
    # Map figures to artifact_data for the formatter
    agent_figures = result.get('figures', [])

    structured = format_analysis_response(
        raw_response = full_narrative,
        agent_used   = result.get('agent_used','summary'),
        artifact_data= {'type': 'multi_visual', 'data': agent_figures} if agent_figures else result.get('artifact_data')
    )
    result['structured_response'] = structured
    return result

@router.get("/history/{file_id}")
async def pred_history(
    file_id: int,
    user=Depends(get_current_user)
):
    ref = db.get_user_file_ref(user["id"], file_id)
    if not ref:
        raise HTTPException(status_code=403, detail="Access denied")
    return {"history": db.get_prediction_history(user["id"], file_id)}
