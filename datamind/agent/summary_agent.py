"""
Summary Agent for DataMind v4.0
Fast dataset profiling using tools/stats.py for pre-computed statistics.
"""

from __future__ import annotations

import re
import json
import time
import logging
from typing import Any, Dict, Optional

import pandas as pd
from datamind.llm.ollama_client import call_ollama_sync
from config import SUMMARY_TIMEOUT, OLLAMA_BASE_URL, OLLAMA_MODEL
from datamind.agent.viz_agent import VizAgent
from datamind.tools.chart_builder import build_correlation_heatmap, build_distribution_chart
from datamind.tools.stats import compute_fast_stats, DatasetStats

logger = logging.getLogger(__name__)

class SummaryAgent:
    """Agent for fast dataset profiling and capability assessment."""

    def __init__(self, model: str = OLLAMA_MODEL):
        self.model = model

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

        # Condensed Stats for LLM to avoid context overflow
        stats_for_llm = {
            "overview": {
                "rows": stats_obj.row_count,
                "cols": stats_obj.column_count,
                "memory_mb": stats_obj.memory_usage_mb,
                "duplicates": stats_obj.duplicate_rows
            },
            "column_types": { k: len(v) for k, v in stats_obj.column_types.items() if k != "all" },
            "key_columns": { col: stats_obj.column_details[col] for col in stats_obj.top_columns if col in stats_obj.column_details },
            "heuristics": {
                "ml_capabilities": stats_obj.ml_capabilities,
                "quality_warnings": stats_obj.data_quality_warnings
            }
        }
        
        stats_json = json.dumps(stats_for_llm, indent=2, default=str)
        full_dossier = self._call_llm(stats_json, stage="dossier")
        
        # Step 4: Split Response and Extract Captions
        result_parts = self._split_response(full_dossier)
        
        final_captions = result_parts.get("captions", [])[:len(figures)]
        while len(final_captions) < len(figures):
            final_captions.append("Discovering tactical patterns within this dimension.")

        elapsed = time.time() - start_time
        logger.info(f"Core Dossier generated in {elapsed:.2f}s")
        
        return {
            "response": result_parts["brief"],
            "lab_narrative": result_parts["detailed"],
            "figures": [f if isinstance(f, dict) else f.to_dict() for f in figures],
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
            "column_types": { k: len(v) for k, v in stats_obj.column_types.items() if k != "all" },
            "ml_readiness": stats_obj.ml_capabilities,
            "heuristics": stats_obj.top_columns
        }, indent=2, default=str)
        
        narrative = self._call_llm(stats_json, stage="prediction")

        # 2. Generate "Strategic Trajectory" Figure
        import plotly.graph_objects as go
        
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

        # 3. Split Response
        result_parts = self._split_response(narrative)
        
        return {
            "response": result_parts["brief"],
            "lab_narrative": result_parts["detailed"],
            "fig": fig if isinstance(fig, dict) else (fig.to_dict() if fig else None)
        }

    def _call_llm(self, stats_json: str, stage: str = "dossier") -> str:
        """Call LLM for specific analysis stages."""
        if stage == "dossier":
            system_prompt = """You are an expert data analyst writing a forensic intelligence report.

Write your report in this EXACT structure with these EXACT section headers:

<<<BRIEF>>>
- [one-line finding]
- [one-line finding]
- [one-line finding]

<<<DETAILED>>>

## Introduction
[Write 2-3 paragraphs about what this dataset is, its domain, and strategic purpose.]

## Forensic Investigation
[Write 4-5 detailed paragraphs analyzing the data: column types, distributions, anomalies, interesting patterns. Name specific column names. No bullet points here — full paragraphs only.]

## Data Summary
[Write a Markdown table with columns: Column Name | Type | Key Insight]

## Strategic Conclusion
[Write 2 paragraphs: key takeaways and recommended next steps.]"""
        else:
            system_prompt = """You are an expert data scientist writing a predictive analysis report.

Write your report in this EXACT structure:

<<<BRIEF>>>
- [one-line finding]
- [one-line finding]
- [one-line finding]

<<<DETAILED>>>

## Introduction
[Write 2 paragraphs explaining what this prediction task involves and the dataset context.]

## Model Analysis
[Write 4-5 detailed paragraphs about: ML capabilities identified, which columns could be targets, expected model performance, key feature signals. Write in full paragraphs, no bullets.]

## Feature Impact Table
[Write a Markdown table: Column | Type | ML Role | Key Signal]

## Strategic Conclusion
[Write 2 paragraphs with specific recommendations and next steps.]"""

        user_prompt = f"Dataset Stats JSON: {stats_json}"

        try:
            response = call_ollama_sync(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=self.model
            )
            
            # Validate response
            if not response or len(response) < 50:
                 logger.warning(f"LLM {stage} returned short response: {response}")
            
            return response.strip()
        except Exception as exc:
            logger.error(f"LLM {stage} call failure: {exc}")
            error_type = "Timeout" if "timeout" in str(exc).lower() else "Connection Error"
            return f"""### ⚠️ Forensic Engine Offline
The local AI node (Ollama: {self.model}) is currently unresponsive. 

**Error Type:** {error_type}
**Technical Details:** {str(exc)}
 
 *Tip: Ensure Ollama is running (`ollama serve`) and the model is fully loaded.*"""

    def _split_response(self, text: str) -> Dict[str, str]:
        """Splits LLM output into brief chat response and detailed lab narrative."""
        # Debug: log the raw LLM output so we can see what the model produces
        logger.info(f"[RAW LLM OUTPUT] length={len(text)}, preview={text[:300]!r}")
        
        # 1. Clean common LLM-generated garbage
        text = re.sub(r'(Response Structure Requirement:|STRICT PROTOCOL:|STRICT FORMAT:).*?\n', '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # 2. Extract Captions if present and remove them from the body
        captions = []
        if "[GRAPH CAPTIONS]" in text:
            try:
                parts = text.split("[GRAPH CAPTIONS]")
                body = parts[0]
                caption_text = parts[1]
                lines = caption_text.strip().split("\n")
                captions = [l.strip("- ").strip().strip("💡 ") for l in lines if l.strip().startswith("-") or l.strip().startswith("💡")]
                text = body
            except:
                pass
            
        brief = ""
        detailed = ""
        
        # 3. Handle tags — robust splitting
        if "<<<BRIEF>>>" in text and "<<<DETAILED>>>" in text:
            try:
                parts = text.split("<<<DETAILED>>>")
                detailed = parts[1].strip()
                brief = parts[0].replace("<<<BRIEF>>>", "").strip()
            except:
                pass
        elif "<<<BRIEF>>>" in text:
            # LLM gave brief but no DETAILED tag — use everything after brief as detailed
            parts = text.split("<<<BRIEF>>>", 1)
            remaining = parts[1] if len(parts) > 1 else ""
            # The brief is first block before ##, detailed is everything from first ## heading
            heading_match = re.search(r'^##\s', remaining, re.MULTILINE)
            if heading_match:
                brief = remaining[:heading_match.start()].strip()
                detailed = remaining[heading_match.start():].strip()
            else:
                brief = remaining[:200].strip()
                detailed = remaining.strip()
        else:
            # LLM ignored all tags — use full output as detailed, extract brief from start
            detailed = text.strip()
            heading_match = re.search(r'^##\s', text, re.MULTILINE)
            if heading_match:
                brief = text[:heading_match.start()].strip()[:300]
                detailed = text[heading_match.start():].strip()
            
        # 4. Final cleanup of any lingering tags in detailed
        detailed = re.sub(r'<<<BRIEF>>>|<<<DETAILED>>>', '', detailed).strip()
        
        # Fallback brief if empty
        if not brief:
            paras = (detailed or text).split("\n\n")
            brief = paras[0].strip() if paras else text
            if len(brief) > 150:
                brief = brief[:147] + "..."
            
        logger.info(f"[SPLIT RESULT] brief_len={len(brief)}, detailed_len={len(detailed)}, captions={len(captions)}")
        return {"brief": brief, "detailed": detailed, "captions": captions}