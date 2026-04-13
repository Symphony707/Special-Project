"""
Analyst Agent for DataMind v4.0
Answers user queries with text, tables, and visual guidance - NO CODE execution.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, Optional
import pandas as pd

from datamind.llm.ollama_client import OllamaClient
from datamind.tools.stats import compute_fast_stats
from datamind.memory.session import get_analyst_lessons

logger = logging.getLogger(__name__)


class AnalystAgent:
    """Agent that answers complex data questions with text, tables, and insights - NO CODE."""

    def __init__(self, df: pd.DataFrame, client: Optional[OllamaClient] = None, model: str = "qwen2.5-coder:3b", dataset_name: str = "global"):
        self.df = df
        self.client = client or OllamaClient(model=model)
        self.stats = compute_fast_stats(df)
        self.dataset_name = dataset_name
        
        # Autonomous Phase: Learn the domain if we don't know it yet
        self.autonomous_discovery()

    def _categorize_query(self, user_query: str) -> str:
        """Categorize query as 'analysis' (forensic) or 'simulation' (prediction)."""
        import difflib
        q_lower = user_query.lower()
        words = re.findall(r'\w+', q_lower)

        # Simulation / Prediction / What-If Indicators (goes to Simulation Lab)
        sim_keywords = [
            "what if", "predict", "prediction", "impact", "scenario", "forecast",
            "increase", "decrease", "change", "would happen", "then",
            "future", "projection", "simulate", "model", "estimates",
            "project", "expect", "hypothetical", "trend analysis",
            "if we increase", "if we decrease", "future projection",
            "forecasted", "predicted", "projected", "estimation", "what-if",
            "growth", "reduction", "simulation", "scenario analysis",
            "predictive", "simulator", "whatif", "forecasts"
        ]

        # Analysis / Forensic / Current State Indicators (goes to Analysis Lab)
        analysis_keywords = [
            "about", "summary", "overview", "what is", "columns", "structure",
            "missing", "distribution", "correlation", "pattern", "insight",
            "analyze", "analysis", "explain", "describe", "compare", "breakdown",
            "current state", "actual", "real", "observed", "seen",
            "relationship", "distribution", "frequency", "characteristics",
            "profile", "tell me about", "what's the", "how does", "describe the",
            "metadata", "column list", "field", "feature", "schema",
            "contents", "information", "details"
        ]

        # 1. Direct checks (highest priority)
        if any(k in q_lower for k in sim_keywords):
            return "simulation"
        if any(k in q_lower for k in analysis_keywords):
            return "analysis"
            
        # 2. Fuzzy checks (handle spelling/tense)
        for word in words:
            if len(word) < 4: continue # Skip short words for fuzzy matching
            
            # Check if word is close to any sim keyword
            sim_matches = difflib.get_close_matches(word, sim_keywords, n=1, cutoff=0.8)
            if sim_matches:
                return "simulation"
                
            # Check if word is close to any analysis keyword
            ana_matches = difflib.get_close_matches(word, analysis_keywords, n=1, cutoff=0.8)
            if ana_matches:
                return "analysis"

        # Default to analysis for general queries
        return "analysis"

    def analyze(self, user_query: str) -> Dict[str, Any]:
        """Answer user queries with proper text, tables, and visual guidance - NO CODE."""

        # 1. Build the prompt with schema context and Session Lessons
        schema_info = self._get_schema_context()
        lessons = get_analyst_lessons()
        lessons_text = "\n".join([f"- {l}" for l in lessons]) if lessons else "None yet. Maintain perfection."

        # Determine category based on query type - BEFORE building prompt
        category = self._categorize_query(user_query)

        prompt = f"""You are a Global Elite Data Strategist.
Your goal is to deliver mission-critical insights with mathematical precision.

SESSION PROGRESS & LESSONS:
{lessons_text}

DATASET CONTEXT & AUTHORIZED COLUMNS:
{schema_info}

STRICT PROTOCOL:
- SECURITY: Data is ALWAYS in memory as `df`. NEVER use `pd.read_csv()`.
- ZERO HALLUCINATION: Use ONLY columns from AUTHORIZED COLUMNS.
- NO CODE OUTPUT: NEVER output Python code, code blocks, or code snippets.
- NO EXPLANATION OF TOOLS: Only deliver insights, not how you obtained them.
- NO INTERNAL KEYS: Never output code variables like 'ans =', 'lab =', 'fig =', 'cat ='.

OUTPUT FORMAT (MANDATORY):
Provide your response in this structure:

## Introduction
Brief introduction setting the context for the user's question.
- What the user is asking about
- Why this matters in the context of the dataset

## Detailed Analysis
In-depth explanation of findings, patterns, and insights.
- Use bullet points for clarity
- Include key statistics with interpretations
- Reference specific columns and their relationships
- Explain what the data reveals about the topic

## Key Findings (Data Summary)
Summarized insights with data-driven conclusions.
- Use Markdown tables for comparative data or statistics
- Highlight important patterns, correlations, or anomalies
- Show actual numbers from the dataset

## Conclusion
Concise summary with actionable takeaways.
- Restate the core insight
- Suggest implications or next steps if relevant

EXECUTIVE BRIEFING MANDATE:
- BE CONCISE. Deliver insights immediately.
- BE PRECISE. Use exact numbers and specific column references.
- VISUALS: Suggest appropriate visualizations (line chart, bar chart, scatter plot, histogram).
- TABLES: Always use Markdown tables for numerical comparisons or multiple values.
- STYLE: High-fidelity, professional, and bold.
- DO NOT explain the technology. Explain the business impact.
- DO NOT output any code under any circumstances.
- DO NOT include Python code, function definitions, or import statements.

---
### CURRENT MISSION:
User Question: "{user_query}"

### STRATEGIC REFLECTION (MANDATORY):
Before providing the MISSION CRITICAL RESPONSE, perform a silent self-reflection:
1. Is my current interpretation of the query accurate based on the AUTHORIZED COLUMNS?
2. Did I inadvertently reference any Python code variables or keys?
3. Is my analysis grounded in the statistical reality provided in the SNAPSHOT metrics?
4. How can I ensure total zero-hallucination?

REMEMBER: Provide text, tables, and visual guidance only. NO CODE.
"""

        max_retries = 2
        last_error = ""

        for attempt in range(max_retries):
            try:
                # 2. Add error context if this is a retry
                current_prompt = prompt
                if last_error:
                    current_prompt += f"\n\n⚠️ PREVIOUS ATTEMPT FAILED WITH ERROR: {last_error}\n"
                    if "CRITICAL DIMENSION ERROR" in last_error:
                        auth_cols = list(self.df.columns)
                        current_prompt += f"HALLUCINATION ALERT: Your previous response used columns that DO NOT EXIST in our authorized set: {auth_cols}. PLEASE ONLY USE THESE AUTHORIZED COLUMNS."
                    elif "No such file or directory" in last_error:
                        current_prompt += "CRITICAL ERROR: You attempted to reference a file path. STOP. The data is ALREADY in memory as 'df'. ONLY use 'df'."
                    current_prompt += "\nRefine your strategic logic and try again."

                # 3. Get response from LLM
                llm_resp = self.client.chat([{"role": "user", "content": current_prompt}])

                # 4. Clean up the response - remove any code that might have been included
                clean_narrative = re.sub(r'```python.*?```', '', llm_resp, flags=re.DOTALL)
                clean_narrative = re.sub(r'```.*?```', '', clean_narrative, flags=re.DOTALL)  # Remove any code blocks
                clean_narrative = re.sub(r'\{.*?"data":.*?\}', '', clean_narrative, flags=re.DOTALL)
                clean_narrative = re.sub(r'\[.*?"values":.*?\]', '', clean_narrative, flags=re.DOTALL)
                clean_narrative = re.sub(r'(ans|lab|fig|cat)\s*[:=]\s*(["\']{3}).*?\2', '', clean_narrative, flags=re.DOTALL | re.IGNORECASE)
                clean_narrative = re.sub(r'^(ans|lab|fig|cat|answer|lab_narrative|category|fig_caption):\s*', '', clean_narrative, flags=re.IGNORECASE | re.MULTILINE)
                clean_narrative = re.sub(r'#.*?\n', '\n', clean_narrative)
                clean_narrative = clean_narrative.strip()

                # 5. Ensure proper structure
                narrative = clean_narrative if clean_narrative else "Detailed analysis generated."

                # Structure Polish: Ensure narrative has proper structure
                if narrative:
                    # Check if it already has headers
                    if "## " not in narrative[:200]:
                        # Try to add proper headers if missing
                        if not narrative.startswith("## Introduction"):
                            narrative = f"## Introduction\n\nBased on the user's query about '{user_query}', here are the key findings:\n\n{narrative}"

                # Final Polishing
                chat_response = narrative[:300].strip() + "..." if len(narrative) > 300 else narrative.strip()

                # Auto-Learning: Record this successful methodology as a "Precision Pattern"
                if len(narrative) > 500: # Only record quality, substantive responses
                    from datamind.memory.session import add_analyst_lesson
                    topic_hint = user_query[:30]
                    add_analyst_lesson(f"SUCCESS PATTERN: Excellent analysis of '{topic_hint}...'. Maintaining high-fidelity narrative structure and bold conclusions.")

                return {
                    "response": chat_response,
                    "lab_narrative": narrative,
                    "figures": [],
                    "captions": [],
                    "category": category,
                    "code": None  # No code generated
                }

            except Exception as e:
                last_error = str(e)
                logger.error(f"AnalystAgent attempt {attempt+1} failed: {e}")
                
                # Auto-Learning: Record the failure as a lesson for next time if it involves column errors
                if "column" in last_error.lower() or "not found" in last_error.lower():
                    from datamind.memory.session import add_analyst_lesson
                    add_analyst_lesson(f"CRITICAL: Failed to locate columns in previous attempt. Context: {last_error}. Ensure you ONLY use AUTHORIZED COLUMNS.")

        return {"response": f"Sorry, I encountered a persistent error during analysis: {last_error}", "lab_narrative": "", "figures": [], "captions": [], "category": "analysis", "code": None}

    def autonomous_discovery(self):
        """Silently figure out the dataset's domain and establish analytical ground rules."""
        from datamind.memory.session import get_analyst_lessons, add_analyst_lesson
        
        # If we already have lessons (beyond just 1-2 errors), skip to avoid redundant LLM calls
        existing = get_analyst_lessons()
        if len([l for l in existing if "DOMAIN" in l]) >= 2:
            return

        logger.info(f"Starting autonomous discovery for {self.dataset_name}...")
        
        schema_info = self._get_schema_context()
        prompt = f"""You are the DataMind Autonomous Intelligence Core.
Analyze this dataset snapshot and establish 3-5 MISSION CRITICAL rules for absolute analytical precision.
Your goal is to "figure out" the domain, the likely business/scientific context, and the exact constraints of this file.

DATASET SNAPSHOT:
{schema_info}

TASKS:
1. Identify the likely Topic/Domain (e.g. "SaaS Subscription Data", "Genomic Sequences", "Supply Chain Logistics").
2. Establish strict rules for precision (e.g. "Always prioritize column X for trend analysis", "Nulls in Y indicate inactive status").
3. Determine the "Master Strategy" for answering questions about this specific file.

OUTPUT: A bulleted list of 3-5 rules.
Each must start with "DOMAIN RULE:".
Be authoritative. Ensure the rules guarantee high accuracy for ANY query on this topic.
NO CODE. NO INTRO.
"""
        try:
            discovery_resp = self.client.chat([{"role": "user", "content": prompt}])
            rules = re.findall(r'DOMAIN RULE:.*', discovery_resp)
            for rule in rules:
                add_analyst_lesson(rule.strip())
            logger.info(f"Autonomous discovery complete. Established {len(rules)} rules.")
        except Exception as e:
            logger.warning(f"Autonomous discovery failed: {e}")

    def _get_schema_context(self) -> str:
        """Create a deep statistical snapshot for maximum model accuracy."""
        cols = self.stats.column_types["all"]
        col_metadata = self.stats.column_details # Richer details from stats.py
        
        # Build a statistical briefing for the LLM
        stats_briefing = []
        for col, details in col_metadata.items():
            brief = f"- {col} ({details['type']}): {details['unique_count']} unique values. "
            if details['sample_values']:
                brief += f"Examples: {details['sample_values']}"
            if details['null_pct'] > 0:
                brief += f" [Warning: {details['null_pct']:.1f}% Nulls]"
            stats_briefing.append(brief)
            
        stats_text = "\n".join(stats_briefing)

        # PROBE: Give exactly 1 row for semantic variety
        probe = self.df.head(1).to_dict(orient='records')

        return f"""
AUTHORIZED COLUMNS: {list(self.df.columns)} (ONLY use these columns. DO NOT guess others.)
COLUMN PROFILES & SNAPSHOTS:
{stats_text}

SHAPE: {self.df.shape}
ML READINESS: {self.stats.ml_capabilities}

SEMANTIC PROBE (Row 1 Only):
{probe}

--- SECURITY FIREWALL: Any column name NOT in the AUTHORIZED COLUMNS list above is strictly FORBIDDEN. ---
"""