"""
Visualization Agent for DataMind v4.0
Delegates chart generation to tools/chart_builder.py. Stateless and backend-agnostic.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
import pandas as pd
from plotly.graph_objects import Figure

from datamind.tools.chart_builder import (
    build_distribution_chart,
    build_correlation_heatmap,
    build_null_map,
    build_time_series_chart,
    build_prediction_results
)
from datamind.tools.stats import compute_fast_stats, DatasetStats

logger = logging.getLogger(__name__)

class VizAgent:
    """Agent for generating Plotly visualizations via tools/chart_builder."""

    def __init__(self, df: pd.DataFrame, stats: Optional[DatasetStats] = None):
        self.df = df
        self.stats = stats or compute_fast_stats(df)

    def generate_top_charts(self) -> Dict[str, Any]:
        """Pre-generate the 3 most useful charts. Returns a dict of serialized figures."""
        figs = {}
        
        # 1. Distribution of top numeric column
        if self.stats.column_types["numeric"]:
            top_col = self.stats.top_columns[0]
            try:
                fig = build_distribution_chart(self.df, top_col)
                if fig: figs[f"dist_{top_col}"] = fig.to_dict()
            except Exception as e:
                logger.warning(f"Failed to generate distribution chart: {e}")

        # 2. Correlation Heatmap
        if len(self.stats.column_types["numeric"]) >= 2:
            try:
                fig = build_correlation_heatmap(self.df)
                if fig: figs["corr_heatmap"] = fig.to_dict()
            except Exception as e:
                logger.warning(f"Failed to generate correlation heatmap: {e}")

        # 3. Null Map
        try:
            fig = build_null_map(self.df)
            if fig: figs["null_map"] = fig.to_dict()
        except Exception as e:
            logger.warning(f"Failed to generate null map: {e}")
            
        return figs

    def handle_request(self, chart_type: str, **kwargs) -> Optional[Figure]:
        """Route specific chart requests to builders."""
        try:
            fig = None
            if chart_type == "distribution":
                fig = build_distribution_chart(self.df, kwargs.get("column"))
            elif chart_type == "correlation":
                fig = build_correlation_heatmap(self.df)
            elif chart_type == "time_series":
                fig = build_time_series_chart(self.df, kwargs.get("date_col"), kwargs.get("value_col"))
            elif chart_type == "missing":
                fig = build_null_map(self.df)
            
            return fig.to_dict() if fig else None
        except Exception as e:
            logger.error(f"Chart generation error ({chart_type}): {e}")
            
        return None