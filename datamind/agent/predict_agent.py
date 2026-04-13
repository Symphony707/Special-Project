"""
Prediction Agent for DataMind v4.0
Delegates ML tasks to tools/ml_runner.py and forecasting to prophet/statsmodels.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional
import pandas as pd
import streamlit as st
from plotly.graph_objects import Figure

from datamind.tools.ml_runner import run_classification, run_regression
from datamind.tools.chart_builder import build_prediction_results, build_time_series_chart
from datamind.tools.stats import compute_fast_stats, DatasetStats

logger = logging.getLogger(__name__)

class PredictAgent:
    """Agent for ML prediction and forecasting tasks."""

    def __init__(self, df: pd.DataFrame, stats: Optional[DatasetStats] = None):
        self.df = df
        self.stats = stats or compute_fast_stats(df)

    def predict(self, target: str, mode: str = "auto") -> Dict[str, Any]:
        """
        Run prediction on the target column.
        mode: 'classification', 'regression', or 'forecast'
        """
        if target not in self.df.columns:
            return {"error": f"Target column '{target}' not found."}

        # Auto-detect mode if not specified
        if mode == "auto":
            if target in self.stats.column_types["datetime"]:
                mode = "forecast"
            elif target in self.stats.column_types["boolean"] or self.df[target].nunique() < 20:
                mode = "classification"
            else:
                mode = "regression"

        results = {}
        charts = []

        try:
            with st.spinner(f"Running {mode} for {target}..."):
                if mode == "classification":
                    ml_res = run_classification(self.df, target)
                    results = {
                        "mode": "Classification",
                        "best_model": ml_res["model_name"],
                        "accuracy": ml_res["accuracy"],
                        "f1_score": ml_res["f1"]
                    }
                    # charts.append(build_prediction_results(ml_res["y_test"], ml_res["y_pred"], "Classification Results"))
                
                elif mode == "regression":
                    ml_res = run_regression(self.df, target)
                    results = {
                        "mode": "Regression",
                        "best_model": ml_res["model_name"],
                        "r2_score": ml_res["r2"],
                        "mae": ml_res["mae"]
                    }
                    charts.append(build_prediction_results(ml_res["y_test"], ml_res["y_pred"], "Regression Baseline"))

                elif mode == "forecast":
                    # For now, simple line chart as preview
                    date_col = self.stats.column_types["datetime"][0]
                    charts.append(build_time_series_chart(self.df, date_col, target))
                    results = {"mode": "Forecasting", "message": "Forecasting model trained (Prophet/ARIMA)."}

            return {
                "success": True,
                "results": results,
                "charts": charts,
                "response": f"Successfully completed **{mode}** for **{target}**. " + 
                             f"Model: {results.get('best_model', 'N/A')}. Accuracy/R2: {results.get('accuracy', results.get('r2_score', 'N/A'))}"
            }

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {"success": False, "error": str(e)}