import json
from fastapi import APIRouter, Depends, HTTPException
from backend.middleware.auth_middleware import get_current_user
from backend.models.schemas import AnalysisRequest
from backend.utils.df_store import DataFrameStore
from backend.utils.agent_utils import run_agent_async, ForensicEncoder, serialize_agent_result
from backend.utils.response_formatter import format_analysis_response
from datamind.agent.orchestrator import Orchestrator

import database as db

router = APIRouter()
df_store = DataFrameStore()

@router.post("/run")
async def run_analysis(
    data: AnalysisRequest,
    user=Depends(get_current_user)
):
    # 1. Authorization
    ref = db.get_user_file_ref(user["id"], data.file_id)
    if not ref:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # 2. Retrieve Data (with auto-hydration)
    df = df_store.get_df_auto(data.file_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Forensic data could not be retrieved or re-hydrated. Please re-ingest.")
    
    # 3. Meta-information
    gf = db.get_global_file_by_id(data.file_id)
    fingerprint = json.loads(gf["schema_fingerprint"])
    
    # 4. Execute Analysis Async
    orchestrator = Orchestrator(df=df)
    result = await run_agent_async(
        orchestrator.route_query,
        query=data.query,
        fingerprint=fingerprint,
        file_id=data.file_id,
        intent_override=data.intent
    )
    
    # 5. Save results to persistent analysis memory
    db.save_analysis(
        user["id"], data.file_id,
        data.query, result.get("intent", data.intent or "analysis"),
        result.get("agent_used", "analyst"),
        str(result.get("response", ""))[:200], # Summary
        str(result.get("response", "")),       # Full
        result.get("artifact_type"),
        json.dumps(result.get("artifact_data"), cls=ForensicEncoder) if result.get("artifact_data") else None
    )
    
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
        agent_used   = result.get('agent_used','analyst'),
        artifact_data= {'type': 'multi_visual', 'data': agent_figures} if agent_figures else result.get('artifact_data')
    )
    result['structured_response'] = structured

    return result


@router.get("/history/{file_id}")
async def get_history(
    file_id: int,
    user=Depends(get_current_user)
):
    ref = db.get_user_file_ref(user["id"], file_id)
    if not ref:
        raise HTTPException(status_code=403, detail="Access denied")
    
    history = db.get_analysis_history(user["id"], file_id, limit=50)
    
    # Parse artifact_data strings into JSON for frontend
    for h in history:
        if h.get("artifact_data"):
            try:
                h["artifact_data"] = json.loads(h["artifact_data"])
            except:
                pass
                
    return {"history": history}
