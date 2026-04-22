import json
import time
import logging
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from backend.middleware.auth_middleware import get_current_user
from backend.models.schemas import ChatRequest
from backend.utils.df_store import DataFrameStore
from backend.utils.agent_utils import run_agent_async
from datamind.agent.orchestrator import Orchestrator
from datamind.agent.chat_classifier import classify_tier
from datamind.agent.instant_responder import handle_tier1
from datamind.security.rate_limiter import RateLimiter
from datamind.security.prompt_guard import PromptGuard
from datamind.llm.ollama_client import stream_ollama
import database as db

router = APIRouter()
logger = logging.getLogger(__name__)
df_store = DataFrameStore()

@router.post("/message")
async def chat_message(
    data: ChatRequest,
    user=Depends(get_current_user)
):
    # 1. Rate limit check
    rate = RateLimiter.check_chat(user["id"])
    if not rate["allowed"]:
        raise HTTPException(status_code=429, detail=rate["message"])
    # 2. Authorization & Data Retrieval
    ref = db.get_user_file_ref(user["id"], data.file_id)
    if not ref:
        raise HTTPException(status_code=403, detail="Access denied")

    df = df_store.get_df_auto(data.file_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Forensic Uplink lost. Re-load from vault.")

    # 3. Security Scan
    scan = PromptGuard.scan_for_injection(data.query)
    if scan["threat_level"] == "high":
        _save_chat(user["id"], data.file_id, data.query, "Request blocked by security guard.", 1, "blocked", 0)
        return {"response": "I cannot process this request due to security policies.", "tier": 1, "latency_ms": 0, "intent": "blocked"}

    # 4. Fingerprint for Agents
    gf = db.get_global_file_by_id(data.file_id)
    fingerprint = json.loads(gf["schema_fingerprint"])

    # 5. Classifier (Lightweight)
    start_time = time.time()
    classification = classify_tier(data.query, list(df.columns))
    tier = classification["tier"]

    # --- Tier 1: Instant Response (Rule-based) ---
    if tier == 1:
        # Wrap sync call in thread pool
        response = await run_agent_async(handle_tier1, data.query, df, fingerprint)
        latency = int((time.time() - start_time) * 1000)
        _save_chat(user["id"], data.file_id, data.query, response, tier, classification.get("intent"), latency)
        return {
            "response": response,
            "tier": tier,
            "latency_ms": latency,
            "intent": classification.get("intent")
        }

    # --- Tier 2: General Chat (Streaming LLM) ---
    if tier == 2:
        async def generate():
            from datamind.memory.context_builder import build_context
            
            context = build_context(
                tier=2, query=data.query,
                fingerprint=fingerprint,
                conversation_history=data.conversation_history[-4:],
                prior_patterns=[],
                target_columns=classification.get("target_columns", [])
            )
            
            full_content = ""
            
            # Use the new async streaming client
            async for chunk in stream_ollama(
                system_prompt=context,
                user_prompt=data.query
            ):
                full_content += chunk
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            latency = int((time.time() - start_time) * 1000)
            _save_chat(user["id"], data.file_id, data.query, full_content, tier, classification.get("intent"), latency)
            yield f"data: {json.dumps({'done': True, 'latency_ms': latency})}\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    # --- Tier 3: Deep Analysis (Multi-Agent Orchestrator) ---
    if tier == 3:
        # Orchestrator is now stateless, we instantiate it for this request
        orchestrator = Orchestrator(df=df, user_id=user["id"])
        
        # Wrap sync orchestrator call in thread pool
        result = await run_agent_async(
            orchestrator.route_query,
            query=data.query,
            fingerprint=fingerprint,
            file_id=data.file_id,
            chat_history=data.conversation_history,
            intent_override=classification.get("intent")
        )
        
        latency = int((time.time() - start_time) * 1000)
        
        # --- State Sync (Persistence) ---
        # If the agent cleaned/modified the data, we update our in-memory store
        if "df" in result:
            logger.info(f"Updating DataFrame store for file {data.file_id} after agent modification.")
            df_store.set_df(data.file_id, result["df"])
            # Remove from result so it doesn't try to serialize to JSON
            del result["df"]
        
        # --- Forensic Formatting for Labs ---
        structured_response = None
        if result.get("category") == "simulation":
            from backend.utils.response_formatter import format_prediction_response
            # Ensure we have the target column info
            result['target_column'] = result.get('target_column') or classification.get('target_columns', [None])[0]
            structured_response = format_prediction_response(result)

        # --- SSE Wrapping for Tier 3 ---
        from fastapi.responses import StreamingResponse
        import json

        async def sse_generator():
            # For Tier 3, we yield the full response in one "chunk" and then the metadata
            yield f"data: {json.dumps({'chunk': result.get('response', '')})}\n\n"
            
            meta = {
                "done": True,
                "tier": tier,
                "latency_ms": latency,
                "intent": classification.get("intent"),
                "figures": result.get("figures", []),
                "captions": result.get("captions", []),
                "lab_narrative": result.get("lab_narrative"),
                "category": result.get("category", "analysis"),
                "structured_response": structured_response,
                "success": result.get("success", True)
            }
            yield f"data: {json.dumps(meta)}\n\n"

        _save_chat(user["id"], data.file_id, data.query, str(result.get("response", "")), tier, classification.get("intent"), latency)
        
        return StreamingResponse(sse_generator(), media_type="text/event-stream")

def _save_chat(user_id, file_id, query, response, tier, intent, latency_ms):
    """Utility to persist chat messages to database."""
    try:
        db.save_chat_message(user_id, file_id, "user", query, tier, intent, 0)
        db.save_chat_message(user_id, file_id, "assistant", response, tier, intent, latency_ms)
    except Exception as e:
        logger.error(f"Database save failed: {e}")
