"""
Feedback Loop Subsystem for DataMind v4.0 (Headless)
Manages user ratings and learning over time.
"""

from __future__ import annotations

import json
import os
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from config import OLLAMA_BASE_URL, OLLAMA_MODEL

logger = logging.getLogger(__name__)

# Path for feedback storage
FEEDBACK_DIR = os.path.join(os.path.dirname(__file__), "..", "feedback_data")
FEEDBACK_FILE = os.path.join(FEEDBACK_DIR, "user_ratings.json")


def ensure_feedback_dir() -> None:
    """Ensure feedback directory exists."""
    os.makedirs(FEEDBACK_DIR, exist_ok=True)


def load_all_ratings() -> List[Dict[str, Any]]:
    """Load all ratings from the feedback file."""
    ensure_feedback_dir()

    if not os.path.exists(FEEDBACK_FILE):
        return []

    try:
        with open(FEEDBACK_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_ratings(ratings: List[Dict[str, Any]]) -> None:
    """Save ratings to the feedback file."""
    ensure_feedback_dir()

    with open(FEEDBACK_FILE, "w") as f:
        json.dump(ratings, f, indent=2, default=str)


def add_rating(
    session_id: str,
    content_type: str,
    content_id: str,
    rating: int,  # 1 for thumbs up, 0 for thumbs down
    feedback_text: Optional[str] = None,
) -> None:
    """
    Add a rating to the feedback store.
    """
    ensure_feedback_dir()

    all_ratings = load_all_ratings()

    rating_entry = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "content_type": content_type,
        "content_id": content_id,
        "rating": rating,
        "feedback_text": feedback_text or "",
        "feedback_vector": get_feedback_vector(rating, content_type),
    }

    all_ratings.append(rating_entry)

    # Keep only last 1000 ratings
    if len(all_ratings) > 1000:
        all_ratings = all_ratings[-1000:]

    save_ratings(all_ratings)


def get_feedback_vector(rating: int, content_type: str) -> Dict[str, float]:
    """
    Convert a rating to a feedback vector for learning.
    """
    vector = {}

    if content_type == "chart":
        vector["chart_preference"] = 1.0 if rating else -1.0
    elif content_type == "model":
        vector["model_preference"] = 1.0 if rating else -1.0
    elif content_type == "explanation":
        vector["verbosity_preference"] = 1.0 if rating else -0.5

    return vector


def get_user_preferences() -> Dict[str, Any]:
    """
    Analyze feedback history to extract user preferences.
    """
    all_ratings = load_all_ratings()

    if not all_ratings:
        return {}

    preferences = {
        "preferred_chart_types": [],
        "rejected_chart_types": [],
        "preferred_models": [],
        "rejected_models": [],
        "verbosity_pref": "balanced",  # Default
    }

    # Analyze ratings by type
    for rating in all_ratings:
        content_type = rating["content_type"]
        content_id = rating["content_id"]
        is_positive = rating["rating"] == 1

        if content_type == "chart":
            if is_positive:
                preferences["preferred_chart_types"].append(content_id)
            else:
                preferences["rejected_chart_types"].append(content_id)

        elif content_type == "model":
            if is_positive:
                preferences["preferred_models"].append(content_id)
            else:
                preferences["rejected_models"].append(content_id)

    # Check verbosity preference
    explanation_ratings = [
        r for r in all_ratings if r["content_type"] == "explanation"
    ]
    if explanation_ratings:
        avg_rating = sum(r["rating"] for r in explanation_ratings) / len(explanation_ratings)
        if avg_rating > 0.7:
            preferences["verbosity_pref"] = "detailed"
        elif avg_rating < 0.3:
            preferences["verbosity_pref"] = "concise"

    # Remove duplicates
    for key in ["preferred_chart_types", "rejected_chart_types", "preferred_models", "rejected_models"]:
        seen = set()
        unique = []
        for item in preferences[key]:
            if item not in seen:
                seen.add(item)
                unique.append(item)
        preferences[key] = unique

    return preferences


def get_chart_recommendations() -> List[str]:
    """Get chart recommendations based on user preferences."""
    preferences = get_user_preferences()
    rejected = preferences.get("rejected_chart_types", [])
    default_types = ["distribution", "correlation", "time_series", "scatter_matrix"]
    recommendations = [c for c in default_types if c not in rejected]
    return recommendations or default_types


def get_model_recommendations(task_type: str) -> List[str]:
    """Get model recommendations based on user preferences."""
    preferences = get_user_preferences()
    rejected = preferences.get("rejected_models", [])
    model_order = {
        "classification": ["RandomForest", "LogisticRegression", "XGBoost"],
        "regression": ["RandomForest", "Ridge", "LinearRegression"],
        "forecasting": ["Prophet", "ARIMA"],
    }
    default_order = model_order.get(task_type, ["RandomForest", "LogisticRegression"])
    recommendations = [m for m in default_order if m not in rejected]
    return recommendations or default_order


def get_verbosity_preference() -> str:
    """Get user's preferred explanation verbosity."""
    preferences = get_user_preferences()
    return preferences.get("verbosity_pref", "balanced")


def clear_feedback_data() -> None:
    """Clear all feedback data."""
    if os.path.exists(FEEDBACK_FILE):
        os.remove(FEEDBACK_FILE)