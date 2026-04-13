"""
DataMind v4.0 - Autonomous Data Analysis Platform
"""

from datamind.config import OLLAMA_MODEL, OLLAMA_BASE_URL, DEBUG
from datamind.memory.session import (
    get_dataframe,
    set_dataframe,
    get_schema_cache,
    set_schema_cache,
    get_summary_text,
    set_summary_text,
    get_chat_history,
)

__version__ = "4.0.0"
__all__ = [
    "OLLAMA_MODEL",
    "OLLAMA_BASE_URL",
    "DEBUG",
    "get_dataframe",
    "set_dataframe",
    "get_schema_cache",
    "set_schema_cache",
    "get_summary_text",
    "set_summary_text",
    "get_chat_history",
]