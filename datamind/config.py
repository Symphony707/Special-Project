"""
DataMind v4.0 Configuration

Centralized configuration for model names, timeouts, thresholds, and system behavior.
"""

import os
from typing import Final
from dotenv import load_dotenv

# Load environment variables from .env if it exists
load_dotenv()

# ── LLM Configuration ─────────────────────────────────────────────
OLLAMA_MODEL: Final[str] = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:1.5b")
OLLAMA_BASE_URL: Final[str] = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

# ── Timeout Settings ──────────────────────────────────────────────
SUMMARY_TIMEOUT: Final[int] = int(os.getenv("SUMMARY_TIMEOUT", "5"))
DIAGNOSTIC_TIMEOUT: Final[int] = int(os.getenv("DIAGNOSTIC_TIMEOUT", "3"))
VIZ_TIMEOUT: Final[int] = int(os.getenv("VIZ_TIMEOUT", "10"))
PREDICT_TIMEOUT: Final[int] = int(os.getenv("PREDICT_TIMEOUT", "30"))
CHAT_TIMEOUT: Final[int] = int(os.getenv("CHAT_TIMEOUT", "15"))

# ── Threshold Settings ────────────────────────────────────────────
NULL_RATE_THRESHOLD: Final[float] = float(os.getenv("NULL_RATE_THRESHOLD", "0.3"))
MIN_NUMERIC_FOR_CLUSTERING: Final[int] = int(os.getenv("MIN_NUMERIC_FOR_CLUSTERING", "2"))
MIN_NULL_RATE_FOR_ID: Final[float] = float(os.getenv("MIN_NULL_RATE_FOR_ID", "0.9"))
CORRELATION_MIN_NUMERIC: Final[int] = int(os.getenv("CORRELATION_MIN_NUMERIC", "3"))

# ── ML Settings ───────────────────────────────────────────────────
TRAIN_TEST_SPLIT_RATIO: Final[float] = float(os.getenv("TRAIN_TEST_SPLIT_RATIO", "0.8"))
CROSS_VALIDATION_FOLDS: Final[int] = int(os.getenv("CROSS_VALIDATION_FOLDS", "5"))
FORECAST_HORIZON_DAYS: Final[int] = int(os.getenv("FORECAST_HORIZON_DAYS", "30"))
FORECAST_CONFIDENCE_LEVEL: Final[float] = float(os.getenv("FORECAST_CONFIDENCE_LEVEL", "0.95"))

# ── Session Settings ──────────────────────────────────────────────
MAX_HISTORY_MESSAGES: Final[int] = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))
MAX_SESSIONS_TO_CACHE: Final[int] = int(os.getenv("MAX_SESSIONS_TO_CACHE", "5"))

# ── Debug Settings ────────────────────────────────────────────────
DEBUG: Final[bool] = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL: Final[str] = os.getenv("LOG_LEVEL", "INFO" if not DEBUG else "DEBUG")