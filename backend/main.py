"""
════════════════════════════════════════════════
PHASE 0: AUDIT — PROJECT ARCHITECTURE MAP
════════════════════════════════════════════════

0.1 — AGENT FUNCTIONS MAP
------------------------------------------------
- datamind/agent/analyst_agent.py:
  - AnalystAgent.__init__(self, df, client=None, model=OLLAMA_MODEL, file_id=None, fingerprint=None, user_id=None) -> None
  - AnalystAgent.analyze(self, user_query, conversation_history=None) -> Dict[str, Any]
  - AnalystAgent._fuzzy_match_columns(self, query) -> str
  - AnalystAgent._get_prior_intelligence(self) -> str
  - AnalystAgent._build_unsupervised_prompt(self, query, history, intel) -> str
  - AnalystAgent._extract_artifacts(self, text) -> Dict[str, Any]
  - AnalystAgent._clean_narrative(self, text) -> str
  - AnalystAgent._split_response(self, text) -> Dict[str, str]

- datamind/agent/chat_classifier.py:
  - classify_tier(query, active_df_columns) -> Dict[str, Any]
  - find_possible_target_columns(query, fingerprint) -> List[str]

- datamind/agent/cleaning_agent.py:
  - CleaningAgent.__init__(self, df, client=None) -> None
  - CleaningAgent.suggest_cleaning_plan(self) -> str
  - CleaningAgent.apply_auto_clean(self) -> Dict[str, Any]

- datamind/agent/diagnostic_agent.py:
  - DiagnosticAgent.__init__(self, stats=None) -> None
  - DiagnosticAgent.validate_for_prediction(self, df, target_col=None) -> Dict[str, Any]
  - DiagnosticAgent.check_feasibility(self, mode, target=None) -> Dict[str, Any]

- datamind/agent/instant_responder.py:
  - handle_tier1(query, df, fingerprint) -> str
  - _format_column_table(fingerprint) -> str
  - _handle_aggregation(agg_type, col_query, df, fingerprint) -> str
  - _handle_null_summary(df) -> str
  - _handle_column_nulls(col_query, df, fingerprint) -> str

- datamind/agent/orchestrator.py:
  - Orchestrator.__init__(self, client=None) -> None
  - Orchestrator.route_query(self, query, fingerprint=None, file_id=None, intent_override=None) -> Dict[str, Any]
  - Orchestrator._classify_intent(self, query) -> str
  - Orchestrator._normalize_and_extract_target(self, query) -> Tuple[str, Optional[str]]

- datamind/agent/predict_agent.py:
  - PredictAgent.__init__(self, df, stats=None) -> None
  - PredictAgent.run_prediction_mission(self, target_col=None, mode="auto") -> Dict[str, Any]

- datamind/agent/summary_agent.py:
  - SummaryAgent.__init__(self, client=None, model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, timeout=SUMMARY_TIMEOUT) -> None
  - SummaryAgent.summarize_dossier(self, df) -> Dict[str, Any]
  - SummaryAgent.generate_predictions(self, df) -> Dict[str, Any]
  - SummaryAgent._call_llm(self, stats_json, stage="dossier") -> str
  - SummaryAgent._split_response(self, text) -> Dict[str, str]

- datamind/agent/viz_agent.py:
  - VizAgent.__init__(self, df, stats=None) -> None
  - VizAgent.generate_and_cache_top_charts(self) -> None
  - VizAgent.handle_request(self, chart_type, **kwargs) -> Optional[Figure]

0.2 — DATABASE.PY METHODS
------------------------------------------------
- initialize_database() -> None
- create_user(username, email, password_hash) -> int
- get_user_by_email(email) -> Optional[Dict]
- get_user_by_username(username) -> Optional[Dict]
- get_user_by_id(user_id) -> Optional[Dict]
- update_last_login(user_id) -> None
- update_last_active(user_id) -> None
- increment_failed_attempts(email) -> int
- reset_failed_attempts(email) -> None
- set_lockout(email, lockout_until_timestamp) -> None
- get_lockout_status(email) -> Dict
- create_session(user_id, session_token, expires_at) -> int
- get_session(session_token) -> Optional[Dict]
- refresh_session(session_token) -> None
- revoke_session(session_token) -> None
- revoke_all_user_sessions(user_id) -> None
- cleanup_expired_sessions() -> None
- log_event(user_id, event_type, event_detail=None, ip_hint=None) -> None
- create_reset_token(user_id, token_hash, expires_at) -> int
- get_reset_token(token_hash) -> Optional[Dict]
- consume_reset_token(token_hash) -> None
- get_global_file_by_hash(file_hash) -> Optional[Dict]
- insert_global_file(file_hash, filename, fingerprint_json, row_count, col_count, domain) -> int
- get_user_file_ref(user_id, global_file_id) -> Optional[Dict]
- create_user_file_ref(user_id, global_file_id, display_name) -> int
- get_user_files(user_id) -> List[Dict]
- delete_user_file_ref(user_id, global_file_id) -> None
- update_last_accessed(user_id, global_file_id) -> None
- get_patterns_for_user_file(user_id, global_file_id, limit=10) -> List[Dict]
- upsert_pattern(user_id, global_file_id, pattern_type, description, columns_json, confidence) -> int
- update_pattern_decay(user_id=None) -> None
- save_analysis(user_id, global_file_id, query, intent, agent_used, summary, full_response, artifact_type=None, artifact_data=None) -> int
- get_analysis_history(user_id, global_file_id, limit=20) -> List[Dict]
- update_helpfulness(analysis_id, value) -> None
- save_prediction(user_id, global_file_id, target_col, task_type, model_used, accuracy, f1, rmse, importances_json, summary) -> int
- get_best_model(user_id, global_file_id, target_column) -> Optional[Dict]
- get_prediction_history(user_id, global_file_id) -> List[Dict]
- save_chat_message(user_id, global_file_id, role, content, tier, intent, latency_ms, is_lab_artifact=0, lab_target=None) -> None
- get_chat_history(user_id, global_file_id, limit=50, offset=0) -> List[Dict]
- get_analytical_cache(global_file_id) -> Optional[Dict]
- upsert_analytical_cache(global_file_id, summary_text, viz_json) -> None

0.3 — AUTH.PY FUNCTIONS
------------------------------------------------
- validate_email(email: str) -> tuple[bool, str]
- validate_username(username: str) -> tuple[bool, str]
- validate_password(password: str) -> tuple[bool, str]
- hash_token(raw_token: str) -> str
- register_user(username, email, password, confirm_password) -> dict
- login_user(email, password) -> dict
- create_session_for_user(user_id) -> dict
- validate_session(session_token) -> Optional[Dict]
- logout_user(session_token) -> None
- request_password_reset(email) -> dict
- reset_password(raw_token, new_password) -> dict

0.4 — SESSION_STATE KEYS (REACT STATE CANDIDATES)
------------------------------------------------
- current_user: Global Auth State
- _session_token: Cookie (HTTPOnly)
- current_file_id: Selected Asset ID
- current_file_name: Asset Display Name
- df: Server-side DataFrame Cache (By File ID)
- schema_fingerprint: Asset Metadata
- data_domain: Asset Context
- full_chat_input_v5: Local Component State
- chat_in_flight: UI Loading State
- lab_artifacts: Dashboard / Lab History
- query_cache: Local Storage / State
- summary_text: Lab View State
- auth_tab: Router / Local State
- active_page: App Routing (React Router)
- ollama_status: Global System Health

0.5 — STREAMLIT UI COMPONENTS (REPLACEMENTS)
------------------------------------------------
- st.file_uploader -> DropZone.jsx + /api/files/upload
- st.button (Load Asset) -> /api/files/load/{id}
- st.button (ML Train) -> /api/prediction/run
- st.button (Auto Clean) -> /api/analysis/run (intent=clean)
- st.selectbox (Target Col) -> HTML Select + Page State
- st.chat_input -> ChatInput.jsx + /api/chat/message (SSE)

0.6 — OLLAMA CALLS (STREAMING ENDPOINTS)
------------------------------------------------
- OllamaClient.chat -> Analyst, Summary, Cleaning Agents
- OllamaClient.stream_chat -> /api/chat/message (Tier 2 Streaming)
- OllamaClient.is_available -> /health (Ollama status check)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import database as db

logger = logging.getLogger(__name__)

# Agents are now stateless and no longer require Streamlit session shims.

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up DataMind API...")
    db.initialize_database()
    db.cleanup_expired_sessions()
    db.update_pattern_decay()
    db.run_migrations()
    
    # Check Ollama
    from datamind.llm.ollama_client import check_ollama_health
    from config import OLLAMA_MODEL
    if await check_ollama_health():
        logger.info(f"Ollama connected successfully (Model: {OLLAMA_MODEL})")
    else:
        logger.warning("Ollama server not detected. AI agents will be offline.")
        
    yield
    # Shutdown
    logger.info("Shutting down DataMind API...")

app = FastAPI(
    title="DataMind API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React / Vite dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
from backend.routers import auth, files, analysis, chat, prediction, dashboard
app.include_router(auth.router,       prefix="/api/auth",       tags=["auth"])
app.include_router(files.router,      prefix="/api/files",      tags=["files"])
app.include_router(analysis.router,   prefix="/api/analysis",   tags=["analysis"])
app.include_router(chat.router,       prefix="/api/chat",       tags=["chat"])
app.include_router(prediction.router, prefix="/api/prediction", tags=["prediction"])
app.include_router(dashboard.router,  prefix="/api/dashboard",  tags=["dashboard"])

@app.get("/health")
async def health():
    return {"status": "ok"}
