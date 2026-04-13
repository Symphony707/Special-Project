"""
Diagnostic Agent for DataMind v4.0
Checks feasibility of tasks and returns specialized fallback messages.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
import pandas as pd
from datamind.tools.stats import compute_fast_stats, DatasetStats

logger = logging.getLogger(__name__)

class DiagnosticAgent:
    """Agent for checking task feasibility and returning fallback messages."""

    def __init__(self, stats: Optional[DatasetStats] = None):
        self.stats = stats

    def check_feasibility(self, mode: str, target: Optional[str] = None) -> Dict[str, Any]:
        """
        Check if the requested mode is feasible with the current dataset.
        Returns: {approved: bool, message: str, suggestion: str}
        """
        if not self.stats:
            return {"approved": False, "message": "No data loaded.", "suggestion": "Please upload a CSV."}

        if mode == "forecast":
            if not self.stats.column_types["datetime"]:
                return {
                    "approved": False,
                    "message": "Missing Datetime Column",
                    "suggestion": "Forecasting requires a Date or Timestamp column. Upload data with a chronological field."
                }
            if self.stats.row_count < 30:
                return {
                    "approved": False,
                    "message": "Insufficient Rows",
                    "suggestion": "Forecasting requires at least 30 observations for meaningful trends. Your dataset is too small."
                }

        if mode in ["predict", "regression", "classification"]:
            if not target or target not in self.stats.column_types["all"]:
                return {
                    "approved": False,
                    "message": "Target Not Found",
                    "suggestion": f"Specify a column to predict. Available: {', '.join(self.stats.column_types['all'][:5])}"
                }
            
            # Check target skew or nulls
            if target in self.stats.data_quality_warnings and "High null rate" in self.stats.data_quality_warnings[target]:
                return {
                    "approved": False,
                    "message": "High Data Gaps",
                    "suggestion": f"The target '{target}' has too many missing values (>30%). Clean the data first."
                }

        return {"approved": True, "message": "Ready", "suggestion": None}