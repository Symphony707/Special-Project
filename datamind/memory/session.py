"""
Session Memory Subsystem for DataMind v4.0

Manages in-memory caching of dataframes, schema, summary, and chat history
using Streamlit's session_state for persistence across reruns.
"""

from __future__ import annotations

from typing import Any, Optional
import streamlit as st  # type: ignore[import-untyped]
import pandas as pd  # type: ignore[import-untyped]
from plotly.graph_objects import Figure
from datamind.database import save_lesson, get_lessons, clear_lessons as db_clear_lessons


def get_session_state() -> dict[str, Any]:
    """Get or initialize the session state dictionary."""
    return st.session_state


def initialize_session_state() -> None:
    """Initialize all session state variables with defaults."""
    defaults = {
        "df": None,
        "schema_cache": None,
        "summary_text": None,
        "chat_history": [],
        "feedback_log": [],
        "pre_generated_charts": {},
        "last_summary": None,
        "dataset_history": [],
        "last_queries": [],
        "current_file_name": None,
        "current_file_size": 0,
        "theme": "dark",
        "analyst_lessons": [],
        "predictions": {},  # Changed to dict for {text, fig}
        # Settings Dashboard State
        "settings": {
            "profile": {
                "role": "Senior Strategic Analyst",
                "access_level": "Level 5 Forensic Authorization"
            },
            "ai_engine": {
                "model": "qwen2.5-coder:1.5b",
                "autonomous_mode": True,
                "show_reasoning": True,
                "temperature": 0.7
            },
            "system": {
                "theme": "dark",
                "auto_refresh": True
            }
        }
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ── Dataframe Accessors ───────────────────────────────────────────

def get_dataframe() -> Optional[pd.DataFrame]:
    """Get the currently loaded DataFrame."""
    return st.session_state.get("df")


def set_dataframe(df: pd.DataFrame) -> None:
    """Store the DataFrame in session state."""
    st.session_state["df"] = df


def clear_dataframe() -> None:
    """Clear the DataFrame from session state."""
    st.session_state["df"] = None
    st.session_state["schema_cache"] = None
    st.session_state["summary_text"] = None
    st.session_state["pre_generated_charts"] = {}


# ── Schema Cache Accessors ────────────────────────────────────────

def get_schema_cache() -> Optional[dict[str, Any]]:
    """Get the cached schema dictionary."""
    return st.session_state.get("schema_cache")


def set_schema_cache(schema: dict[str, Any]) -> None:
    """Store the schema in session state cache."""
    st.session_state["schema_cache"] = schema


def clear_schema_cache() -> None:
    """Clear the schema cache."""
    st.session_state["schema_cache"] = None


def compute_schema_cache(df: pd.DataFrame) -> dict[str, Any]:
    """Compute and return schema cache for a DataFrame."""
    schema = {
        "columns": [],
        "numeric": [],
        "categorical": [],
        "datetime": [],
        "boolean": [],
        "null_counts": {},
        "sample_values": {},
        "memory_usage_kb": round(df.memory_usage(deep=True).sum() / 1024, 2),
    }

    for col in df.columns:
        dtype = str(df[col].dtype)
        col_info = {"name": col, "dtype": dtype}

        # Type classification
        if pd.api.types.is_numeric_dtype(df[col]):
            schema["numeric"].append(col)
            col_info["type"] = "numeric"
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            schema["datetime"].append(col)
            col_info["type"] = "datetime"
        elif pd.api.types.is_bool_dtype(df[col]) or set(df[col].dropna().unique()) <= {True, False, None}:
            schema["boolean"].append(col)
            col_info["type"] = "boolean"
        else:
            schema["categorical"].append(col)
            col_info["type"] = "categorical"

        schema["columns"].append(col_info)
        schema["null_counts"][col] = int(df[col].isna().sum())
        schema["sample_values"][col] = df[col].dropna().head(3).tolist()

    return schema


# ── Summary Text Accessors ────────────────────────────────────────

def get_summary_text() -> Optional[str]:
    """Get the cached summary text."""
    return st.session_state.get("summary_text")


def set_summary_text(summary: str) -> None:
    """Store the summary text in session state."""
    st.session_state["summary_text"] = summary


def clear_summary_text() -> None:
    """Clear the summary text."""
    st.session_state["summary_text"] = None


# ── Predictive Forecast Accessors ─────────────────────────────────

def get_predictions() -> dict[str, Any]:
    """Get the cached predictive impact scenarios {text, fig}."""
    return st.session_state.get("predictions", {})


def set_predictions(predictions: dict[str, Any]) -> None:
    """Store the predictive impact scenarios."""
    st.session_state["predictions"] = predictions


def clear_predictions() -> None:
    """Clear the predictions."""
    st.session_state["predictions"] = {}


# ── Chat History Accessors ────────────────────────────────────────

def get_chat_history() -> list[dict[str, Any]]:
    """Get the chat history as a list of message dicts."""
    return st.session_state.get("chat_history", [])


def set_chat_history(history: list[dict[str, Any]]) -> None:
    """Set the chat history."""
    st.session_state["chat_history"] = history


def add_chat_message(role: str, content: str, figures: Optional[list] = None, captions: Optional[list[str]] = None, lab_narrative: Optional[str] = None, code: Optional[str] = None, category: str = "analysis") -> None:
    """Add a message to chat history with optional figures and context category."""
    history = get_chat_history()

    message = {
        "role": role,
        "content": content,
        "timestamp": pd.Timestamp.now().isoformat(),
        "category": category,
    }

    if figures:
        message["figures"] = figures
    
    if captions:
        message["captions"] = captions
    
    if lab_narrative:
        message["lab_narrative"] = lab_narrative
    
    if code:
        message["code"] = code

    # Keep only last MAX_HISTORY_MESSAGES
    history.append(message)
    if len(history) > st.session_state.get("MAX_HISTORY_MESSAGES", 20):
        history = history[-st.session_state.get("MAX_HISTORY_MESSAGES", 20):]

    st.session_state["chat_history"] = history


def clear_chat_history() -> None:
    """Clear the chat history."""
    st.session_state["chat_history"] = []


# ── Pre-generated Charts Accessors ────────────────────────────────

def get_pre_generated_charts() -> dict[str, Figure]:
    """Get the cached Plotly charts."""
    return st.session_state.get("pre_generated_charts", {})


def set_pre_generated_chart(name: str, fig: Figure) -> None:
    """Store a pre-generated chart in cache."""
    charts = get_pre_generated_charts()
    charts[name] = fig
    st.session_state["pre_generated_charts"] = charts


def get_pre_generated_chart(name: str) -> Optional[Figure]:
    """Get a pre-generated chart by name, or None if not cached."""
    return get_pre_generated_charts().get(name)


def clear_pre_generated_charts() -> None:
    """Clear all pre-generated charts."""
    st.session_state["pre_generated_charts"] = {}


# ── Dataset History Accessors ─────────────────────────────────────

def get_dataset_history() -> list[dict[str, Any]]:
    """Get the last 5 uploaded datasets."""
    return st.session_state.get("dataset_history", [])


def add_to_dataset_history(file_name: str, rows: int, columns: int, timestamp: str) -> None:
    """Add a dataset to the history."""
    history = get_dataset_history()
    entry = {
        "file_name": file_name,
        "rows": rows,
        "columns": columns,
        "timestamp": timestamp,
    }
    history.insert(0, entry)
    # Keep only last MAX_SESSIONS_TO_CACHE
    history = history[:st.session_state.get("MAX_SESSIONS_TO_CACHE", 5)]
    st.session_state["dataset_history"] = history


# ── Last Queries Accessors ────────────────────────────────────────

def get_last_queries() -> list[dict[str, Any]]:
    """Get the last 20 user queries and their handlers."""
    return st.session_state.get("last_queries", [])


def add_last_query(query: str, agent: str, timestamp: str) -> None:
    """Add a query to the query history."""
    history = get_last_queries()
    entry = {
        "query": query,
        "agent": agent,
        "timestamp": timestamp,
    }
    history.append(entry)
    # Keep only last 20
    history = history[-20:]
    st.session_state["last_queries"] = history


# ── Theme Accessors ───────────────────────────────────────────────

def get_theme() -> str:
    """Get the current theme (dark/light)."""
    return st.session_state.get("theme", "dark")


def set_theme(theme: str) -> None:
    """Set the current theme."""
    st.session_state["theme"] = theme


def toggle_theme() -> str:
    """Toggle between dark and light theme, returns new theme."""
    current = get_theme()
    new = "light" if current == "dark" else "dark"
    set_theme(new)
    return new


# ── Analyst Lessons Accessors (Auto-Learning Loop) ───────────────

def get_analyst_lessons() -> list[str]:
    """Get the list of lessons learned (error fixes) during the session, synced with DB."""
    session_lessons = st.session_state.get("analyst_lessons", [])
    file_name = st.session_state.get("current_file_name", "global")
    
    # Sync with DB if empty in session
    if not session_lessons and file_name:
        db_lessons = get_lessons(file_name)
        if db_lessons:
            st.session_state["analyst_lessons"] = db_lessons
            return db_lessons
            
    return session_lessons


def add_analyst_lesson(lesson: str) -> None:
    """Add a lesson learned to the session state registry and persist to DB."""
    lessons = get_analyst_lessons()
    file_name = st.session_state.get("current_file_name", "global")

    if lesson not in lessons:
        lessons.append(lesson)
        # Keep only the last 10 important lessons for prompt optimization
        if len(lessons) > 10:
            lessons = lessons[-10:]
        st.session_state["analyst_lessons"] = lessons
        
        # Persist to DB
        if file_name:
            save_lesson(file_name, "training", lesson)


def clear_analyst_lessons() -> None:
    """Clear the analyst lessons registry."""
    st.session_state["analyst_lessons"] = []