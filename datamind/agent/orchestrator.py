"""
Orchestrator for DataMind v4.0
Coordinates routing between specialized agents and implements feasibility gates.
"""

import logging
import re
import streamlit as st
from typing import Any, Dict, Optional

import pandas as pd
from datamind.agent.summary_agent import SummaryAgent
from datamind.agent.diagnostic_agent import DiagnosticAgent
from datamind.agent.viz_agent import VizAgent
from datamind.agent.predict_agent import PredictAgent
from datamind.agent.analyst_agent import AnalystAgent
from datamind.agent.cleaning_agent import CleaningAgent
from datamind.memory.session import get_dataframe, get_summary_text
from datamind.tools.stats import compute_fast_stats, DatasetStats
from datamind.llm.ollama_client import OllamaClient
from datamind.config import OLLAMA_BASE_URL, OLLAMA_MODEL

logger = logging.getLogger(__name__)

class Orchestrator:
    """Master router for agent orchestration."""

    def __init__(
        self,
        client: Optional[OllamaClient] = None,
        model: str = OLLAMA_MODEL,
        base_url: str = OLLAMA_BASE_URL
    ):
        self.client = client or OllamaClient(model=model, base_url=base_url)
        self.df = get_dataframe()
        self.stats: Optional[DatasetStats] = compute_fast_stats(self.df) if self.df is not None else None

    def route_request(self, user_request: str) -> Dict[str, Any]:
        """Route user requests to the appropriate specialized agent."""
        if self.df is None:
            return {"response": "Please upload a dataset on the left to begin.", "charts": []}

        req = user_request.lower()

        # 1. Summary Requests
        if any(x in req for x in ["summary", "profile", "overview"]):
            agent = SummaryAgent(client=self.client)
            dossier = agent.summarize_dossier(self.df)
            return {"response": dossier["text"], "charts": dossier["figures"]}

        # 2. Prediction / Forecast Requests (Gated by Diagnostic)
        if any(x in req for x in ["predict", "forecast", "regression", "classification"]):
            mode = "forecast" if "forecast" in req else "predict"
            target = self._extract_target(req)
            
            diagnostic = DiagnosticAgent(self.stats)
            check = diagnostic.check_feasibility(mode, target)
            
            if not check["approved"]:
                return {
                    "response": f"### ⚠️ {check['message']}\n\n{check['suggestion']}",
                    "charts": []
                }
            
            agent = PredictAgent(self.df, self.stats)
            res = agent.predict(target, mode=mode)
            return {"response": res.get("response", ""), "charts": res.get("charts", [])}

        # 3. Viz Requests
        if any(x in req for x in ["chart", "plot", "graph", "histogram", "heatmap"]):
            agent = VizAgent(self.df, self.stats)
            # Basic routing for viz
            if "heatmap" in req or "correlation" in req:
                fig = agent.handle_request("correlation")
            elif "null" in req or "missing" in req:
                fig = agent.handle_request("missing")
            else:
                target = self._extract_target(req)
                fig = agent.handle_request("distribution", column=target)
            
            return {
                "response": "Here is the requested visualization:",
                "charts": [fig] if fig else []
            }

        # 4. Cleaning / Audit Requests
        if any(x in req for x in ["clean", "fix", "audit", "duplicates", "nulls", "missing"]):
            agent = CleaningAgent(self.df, self.client)
            if any(x in req for x in ["fix", "apply", "automatic"]):
                res = agent.apply_auto_clean()
                return {"response": res["response"], "charts": []}
            return {"response": agent.suggest_cleaning_plan(), "charts": []}

        # 5. Default: Deep Analyst Agent (NL to Code)
        file_name = st.session_state.get("current_file_name", "global")
        agent = AnalystAgent(self.df, self.client, dataset_name=file_name)
        res = agent.analyze(user_request)
        return res

    def _extract_target(self, text: str) -> Optional[str]:
        """Extract column target from request text with aggressive semantic matching."""
        import difflib
        if self.df is None: return None
        
        all_cols = self.df.columns.tolist()
        lower_cols = [c.lower() for c in all_cols]
        text_lower = text.lower()
        
        # 1. First, check if any column name is explicitly in the text
        for i, c in enumerate(lower_cols):
            if c in text_lower:
                return all_cols[i]
        
        # 2. Tokenize and check for plurals or typos
        tokens = re.findall(r'\w+', text_lower)
        for token in tokens:
            # Handle common pluralization by a simple 's' strip
            normalized = token[:-1] if token.endswith('s') else token
            
            # Exact match on normalized token
            if normalized in lower_cols:
                return all_cols[lower_cols.index(normalized)]
                
            # Fuzzy match on token
            matches = difflib.get_close_matches(token, lower_cols, n=1, cutoff=0.7)
            if matches:
                return all_cols[lower_cols.index(matches[0])]
                
            # Fuzzy match on normalized token
            matches = difflib.get_close_matches(normalized, lower_cols, n=1, cutoff=0.7)
            if matches:
                return all_cols[lower_cols.index(matches[0])]

        # 3. Fallback to the original regex if no eager match found
        match = re.search(r"(?:predict|for|on|of|column|about)\s+([a-zA-Z0-9_\s]+)", text_lower)
        if match:
            candidate = match.group(1).strip()
            matches = difflib.get_close_matches(candidate, lower_cols, n=1, cutoff=0.6)
            if matches:
                 return all_cols[lower_cols.index(matches[0])]

        return None

    def _handle_general_query(self, query: str) -> Dict[str, Any]:
        """Fallback to LLM for general data questions."""
        summary = get_summary_text() or "No summary available."
        prompt = f"User is asking about their dataset. Summary: {summary}\nUser Query: {query}\nProvide a concise analysis."
        
        try:
            resp = self.client.chat([{"role": "user", "content": prompt}])
            return {"response": resp, "charts": []}
        except:
            return {"response": "I'm not sure how to handle that request. Try asking for a 'summary' or 'predict [column]'.", "charts": []}