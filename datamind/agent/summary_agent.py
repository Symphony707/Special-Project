"""
Summary Agent for DataMind v4.0
Fast dataset profiling using tools/stats.py for pre-computed statistics.
"""

from __future__ import annotations

import json
import time
import logging
from typing import Any, Dict, Optional

import pandas as pd
from datamind.llm.ollama_client import OllamaClient
from datamind.config import SUMMARY_TIMEOUT, OLLAMA_BASE_URL, OLLAMA_MODEL
from datamind.agent.viz_agent import VizAgent
from datamind.tools.chart_builder import build_correlation_heatmap, build_distribution_chart
from datamind.tools.stats import compute_fast_stats, DatasetStats

logger = logging.getLogger(__name__)

class SummaryAgent:
    """Agent for fast dataset profiling and capability assessment."""

    def __init__(
        self,
        client: Optional[OllamaClient] = None,
        model: str = OLLAMA_MODEL,
        base_url: str = OLLAMA_BASE_URL,
        timeout: int = SUMMARY_TIMEOUT,
    ):
        self.client = client or OllamaClient(model=model, base_url=base_url)
        self.timeout = timeout

    def summarize_dossier(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Step 1: Generate a visual and narrative briefing (Fast).
        Returns: { 'text': str, 'figures': List[Figure], 'captions': List[str] }
        """
        start_time = time.time()

        # Step 1: Compute stats (Fast)
        stats_obj: DatasetStats = compute_fast_stats(df)
        
        # Step 2: Generate Baseline Figures
        viz = VizAgent(df, stats_obj)
        figures = []
        
        if len(stats_obj.column_types["numeric"]) >= 2:
            figures.append(build_correlation_heatmap(df))
            
        if stats_obj.top_columns:
            noise_words = ["id", "index", "unnamed", "name", "email", "phone", "address", "contact", "street", "city", "state", "zip"]
            interesting_cols = [c for c in stats_obj.top_columns if not any(x in c.lower() for x in noise_words)]
            cat_cols = [c for c in stats_obj.column_types["categorical"] if 1 < df[c].nunique() < 20 and not any(x in c.lower() for x in noise_words)]
            
            final_visual_queue = list(dict.fromkeys(interesting_cols + cat_cols))
            for col in final_visual_queue[:4]:
                figures.append(build_distribution_chart(df, col))

        # Stats for LLM
        stats_for_llm = {
            "overview": {
                "rows": stats_obj.row_count,
                "cols": stats_obj.column_count,
                "memory": stats_obj.memory_usage_mb,
                "duplicates": stats_obj.duplicate_rows
            },
            "column_types": stats_obj.column_details,
            "heuristics": {
                "top_columns": stats_obj.top_columns,
                "warnings": stats_obj.data_quality_warnings
            }
        }
        
        stats_json = json.dumps(stats_for_llm, indent=2, default=str)
        full_dossier = self._call_llm(stats_json, stage="dossier")
        
        summary_text = full_dossier
        captions = []
        
        if "[GRAPH CAPTIONS]" in full_dossier:
            parts = full_dossier.split("[GRAPH CAPTIONS]")
            summary_text = parts[0].strip()
            caption_lines = parts[1].strip().split("\n")
            captions = [l.strip("- ").strip().strip("💡 ") for l in caption_lines if l.strip().startswith("-")]

        final_captions = captions[:len(figures)]
        while len(final_captions) < len(figures):
            final_captions.append("Discovering tactical patterns within this dimension.")

        elapsed = time.time() - start_time
        logger.info(f"Core Dossier generated in {elapsed:.2f}s")
        
        return {
            "text": summary_text,
            "figures": figures,
            "captions": final_captions
        }

    def generate_predictions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Step 2: Generate deep predictive forecasts (Intensive).
        Returns: { 'text': str, 'fig': Figure }
        """
        stats_obj = compute_fast_stats(df)
        
        # 1. Generate Narrative
        stats_json = json.dumps({
            "column_types": stats_obj.column_details,
            "ml_readiness": stats_obj.ml_capabilities,
            "heuristics": stats_obj.top_columns
        }, indent=2, default=str)
        
        narrative = self._call_llm(stats_json, stage="prediction")

        # 2. Generate "Strategic Trajectory" Figure
        import plotly.graph_objects as go
        import numpy as np
        
        fig = go.Figure()
        
        # Best guess for a value column
        val_col = next((c for c in stats_obj.column_types["numeric"] if "sale" in c.lower() or "price" in c.lower() or "amount" in c.lower() or "total" in c.lower()), None)
        if not val_col and stats_obj.column_types["numeric"]:
            val_col = stats_obj.column_types["numeric"][0]
            
        if val_col:
            current_val = df[val_col].mean()
            # Simulate 12 month trajectory (Baseline vs Optimistic)
            months = ["Current", "M+1", "M+3", "M+6", "M+9", "M+12"]
            baseline = [current_val * (1 + 0.02 * i) for i in range(len(months))]
            optimistic = [current_val * (1 + 0.05 * i) for i in range(len(months))]
            
            fig.add_trace(go.Scatter(x=months, y=baseline, name="Baseline Trajectory", line=dict(color="#6366F1", width=3, dash='dot')))
            fig.add_trace(go.Scatter(x=months, y=optimistic, name="Strategic Growth (Optimistic)", line=dict(color="#10B981", width=4)))
            
            fig.update_layout(
                title=f"Strategic 12-Month Trajectory: {val_col}",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E2E8F0"),
                margin=dict(l=20, r=20, t=40, b=20),
                height=350
            )

        return {
            "text": narrative,
            "fig": fig
        }

    def _call_llm(self, stats_json: str, stage: str = "dossier") -> str:
        """Call LLM for specific analysis stages."""
        if stage == "dossier":
            system_prompt = """You are a Master Data Architect and Strategic Consultant.
            Goal: Deliver an EXHAUSTIVE, structured Forensic Dataset Briefing.

            STRICT OUTPUT FORMAT (MANDATORY):

            ## Introduction
            Start with a clear, compelling introduction that explains:
            - What this dataset represents and its purpose
            - The domain context (business, science, operations, etc.)
            - Why this data matters and what questions it can answer

            ## Detailed Explanation
            Provide in-depth analysis covering:
            - Dataset structure and column relationships
            - Key patterns, anomalies, and insights discovered
            - Statistical summaries with business interpretation
            - Data quality observations and their implications

            ## Visual Analysis & Findings
            For each chart included:
            - Interpretation of key patterns, peaks, and trends
            - What the visual data reveals about the underlying phenomenon
            - Use Markdown tables to summarize key metrics if helpful

            ## Summary & Implications
            Concise conclusion that:
            - Synthesizes the key findings
            - States the current state of the data
            - Highlights actionable insights
            - Suggests next steps for deeper analysis if applicable

            NARRATIVE STYLE:
            - Use clear, professional language
            - Use bold text for key insights and important findings
            - Use LaTeX syntax ($\\mu$, $\\sigma$) for statistical references
            - Be precise, authoritative, and data-driven

            ---
            [GRAPH CAPTIONS]
            After the main text, provide bullet points for each chart:
            - Chart 1: [Specific insight revealed]
            - Chart 2: [Business impact interpretation]
            - ..."""
        else:
            system_prompt = """You are a Senior Strategic Forecaster & Futurist.
            Goal: Generate a HIGH-DEPTH Predictive Impact Dossier.
            
            STRICT PROTOCOL:
            - NO MARKDOWN CODE BLOCKS. DO NOT output code of any kind.
            - TEXT ONLY. Focus on narrative business strategy.
            
            STRUCTURE:
            ### 🔮 Strategic Forecasting Report
            Provide a deep, 2-3 paragraph explanation of the dataset's trajectory. What will happen in 6-12 months if current trends persist?
            
            ### 🛠️ Tactical "What-If" Scenarios
            For EACH of the 3 scenarios, provide:
            1. **Scenario Name**: (e.g., The Demand Surge)
            2. **Assumed Shift**: What specific variable changed?
            3. **Predicted Outcome**: What is the mathematical and business result?
            4. **Strategic Action Plan**: Exactly what should the user do NOW to prepare?
            
            Write with authority and precision. Use Markdown headers and formatting to make it feel like a premium SaaS report."""

        user_prompt = f"Dataset Stats JSON: {stats_json}"

        try:
            response = self.client.chat([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ])
            return response.strip()
        except Exception as exc:
            logger.error(f"LLM {stage} call failed: {exc}")
            return f"Error: {stage} generation failed."