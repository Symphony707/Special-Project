# Force Refresh: Proactive UI v4.2
"""
DataMind v4.0 - Workspace Layout Utilities
Provides premium styling and fixed-drawer components.
"""

from __future__ import annotations
import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional
from plotly.graph_objects import Figure

from datamind.memory.session import (
    get_dataframe,
    get_schema_cache,
    get_summary_text,
    get_pre_generated_chart
)

def create_split_layout():
    """Deprecated: UI now uses a fixed-drawer approach."""
    return st.columns([1, 2.3])

def apply_custom_styles():
    """Inject premium SaaS-style CSS with glassmorphism and modern design principles."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@500;600;700;800&display=swap');

        :root {
            --primary: #6366F1;
            --primary-hover: #4F46E5;
            --secondary: #10B981;
            --accent: #8B5CF6;
            --warning: #F59E0B;
            --bg-dark: #0F172A;
            --bg-card: rgba(30, 41, 59, 0.7);
            --card-glass: rgba(255, 255, 255, 0.05);
            --border-glass: rgba(255, 255, 255, 0.1);
            --border-glass-light: rgba(255, 255, 255, 0.06);
            --gradient-primary: linear-gradient(135deg, #6366F1 0%, #8B5CFD 50%, #EC4899 100%);
            --drawer-width: 320px;
        }

        .stApp {
            background: var(--bg-dark);
            color: #E2E8F0;
            font-family: 'Inter', sans-serif;
            overflow-x: hidden;
        }

        /* Sidebar styling - Premium Glassmorphism */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(15,23,42,0.95) 0%, rgba(15,23,42,0.85) 100%) !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
            border-right: 1px solid var(--border-glass) !important;
        }

        /* Sidebar Navigation Elements */
        [data-testid="stSidebar"] .radio-label {
            color: #CBD5E1 !important;
            font-weight: 500 !important;
            padding: 12px 16px !important;
            margin: 4px 0 !important;
            border-radius: 10px !important;
            transition: all 0.2s ease !important;
        }
        [data-testid="stSidebar"] .radio-label:hover {
            background: rgba(255, 255, 255, 0.05) !important;
        }
        [data-testid="stSidebar"] .radio-label[selected] {
            background: var(--gradient-primary) !important;
            color: white !important;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
        }

        /* Target the Right Column in a 2-column layout - Premium Style */
        [data-testid="stHorizontalBlock"] > div:last-child {
            background: var(--bg-card) !important;
            backdrop-filter: blur(15px) !important;
            -webkit-backdrop-filter: blur(15px) !important;
            border-left: 1px solid var(--border-glass) !important;
            border-radius: 24px !important;
            padding: 1.5rem !important;
            box-shadow: -15px 0 50px rgba(0,0,0,0.3) !important;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        /* Main Workspace Adjustment */
        .main-workspace {
            padding: 2rem;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            max-width: 100%;
            overflow-x: auto;
            word-wrap: break-word;
            background: linear-gradient(180deg, rgba(15,23,42,0) 0%, rgba(15,23,42,0.3) 100%);
        }

        .main-workspace.expanded {
            padding: 2rem !important;
            max-width: 100%;
            overflow-x: auto;
            background: linear-gradient(180deg, rgba(15,23,42,0) 0%, rgba(15,23,42,0.5) 100%);
        }

        /* Premium Button Styling */
        .stButton button {
            background: var(--gradient-primary) !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 10px 20px !important;
            color: white !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
        }
        .stButton button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4) !important;
        }
        .stButton button:active {
            transform: translateY(0) !important;
        }
        .stButton button[data-baseweb="button-secondary"] {
            background: rgba(255, 255, 255, 0.1) !important;
            box-shadow: none !important;
        }
        .stButton button[data-baseweb="button-secondary"]:hover {
            background: rgba(255, 255, 255, 0.15) !important;
        }

        /* Premium File Uploader */
        .stFileUploader {
            background: var(--card-glass) !important;
            border: 2px dashed var(--border-glass) !important;
            border-radius: 16px !important;
            padding: 2rem !important;
            transition: all 0.3s ease !important;
        }
        .stFileUploader:hover {
            border-color: var(--primary) !important;
            background: rgba(255, 255, 255, 0.08) !important;
        }

        /* Pinned Chat Input */
        .stChatInput {
            border-radius: 16px !important;
            border: 1px solid var(--border-glass) !important;
            background: rgba(15, 23, 42, 0.6) !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2) !important;
        }
        .stChatInput:focus-within {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
        }

        /* Premium Summary Section Styling */
        .summary-box {
            background: var(--card-glass) !important;
            border: 1px solid var(--border-glass) !important;
            border-radius: 24px !important;
            padding: 2.5rem !important;
            margin: 1.5rem 0 !important;
            font-family: 'Inter', sans-serif !important;
            line-height: 1.8 !important;
            box-shadow: 0 15px 50px rgba(0,0,0,0.3) !important;
            backdrop-filter: blur(15px) !important;
            -webkit-backdrop-filter: blur(15px) !important;
            word-wrap: break-word !important;
            overflow-wrap: break-word !important;
            background: linear-gradient(180deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.03) 100%);
        }
        .summary-box h1, .summary-box h2, .summary-box h3 {
            font-family: 'Outfit', sans-serif !important;
            color: white !important;
            margin-top: 1.8rem !important;
            font-weight: 700 !important;
            letter-spacing: -0.5px !important;
        }
        .summary-box h1 { color: var(--primary) !important; font-size: 2rem !important; }
        .summary-box h2 { color: #E2E8F0 !important; font-size: 1.5rem !important; margin-top: 2rem !important; }
        .summary-box h3 { color: #94A3B8 !important; font-size: 1.25rem !important; margin-top: 1.5rem !important; }
        .summary-box table {
            display: block !important;
            overflow-x: auto !important;
            width: 100% !important;
            border-collapse: collapse !important;
            margin: 1.5rem 0 !important;
            background: rgba(15,23,42,0.5) !important;
            border-radius: 16px !important;
            overflow: hidden !important;
        }
        .summary-box th {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.15) 100%) !important;
            padding: 14px 16px !important;
            text-align: left !important;
            color: #fff !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            border-bottom: 1px solid var(--border-glass) !important;
        }
        .summary-box td {
            padding: 14px 16px !important;
            border-bottom: 1px solid var(--border-glass) !important;
            color: #CBD5E1 !important;
            font-size: 14px !important;
            border-top: 1px solid rgba(255,255,255,0.03) !important;
        }
        .summary-box tr:hover td {
            background: rgba(255,255,255,0.05) !important;
        }

        /* Premium Metrics Cards */
        .element-container .metric-card {
            background: var(--card-glass) !important;
            border: 1px solid var(--border-glass) !important;
            border-radius: 16px !important;
            padding: 1.5rem !important;
            text-align: center !important;
            transition: all 0.3s ease !important;
        }
        .element-container .metric-card:hover {
            background: rgba(255,255,255,0.08) !important;
            transform: translateY(-2px) !important;
        }
        .element-container .metric-card .metric-value {
            font-size: 2rem !important;
            font-weight: 700 !important;
            color: white !important;
            font-family: 'Outfit', sans-serif !important;
        }
        .element-container .metric-card .metric-label {
            color: #94A3B8 !important;
            font-size: 0.875rem !important;
            margin-top: 0.25rem !important;
        }

        /* Premium Info Box Styling */
        .stInfo {
            background: rgba(99, 102, 241, 0.1) !important;
            border: 1px solid rgba(99, 102, 241, 0.3) !important;
            border-radius: 12px !important;
            padding: 1rem !important;
        }
        .stWarning {
            background: rgba(245, 158, 11, 0.1) !important;
            border: 1px solid rgba(245, 158, 11, 0.3) !important;
            border-radius: 12px !important;
            padding: 1rem !important;
        }

        /* Premium Expander */
        details[data-testid="stExpander"] {
            background: var(--card-glass) !important;
            border: 1px solid var(--border-glass) !important;
            border-radius: 12px !important;
            margin: 1rem 0 !important;
        }
        details[data-testid="stExpander"] summary {
            color: var(--primary) !important;
            font-weight: 600 !important;
        }

        /* Premium Divider */
        hr {
            border: 0 !important;
            height: 1px !important;
            background: var(--border-glass) !important;
            margin: 2rem 0 !important;
        }

        /* Premium Caption */
        .stCaption {
            color: #94A3B8 !important;
            font-size: 0.875rem !important;
        }

        /* Premium Table Fix for Main Workspace */
        [data-testid="stMarkdownContainer"] table {
            display: block !important;
            overflow-x: auto !important;
            width: 100% !important;
            border-collapse: collapse !important;
            margin: 1rem 0 !important;
            background: rgba(15,23,42,0.5) !important;
            border-radius: 12px !important;
        }
        [data-testid="stMarkdownContainer"] table th,
        [data-testid="stMarkdownContainer"] table td {
            padding: 10px 12px !important;
            border: 1px solid rgba(255,255,255,0.05) !important;
        }
        [data-testid="stMarkdownContainer"] table th {
            background: rgba(99, 102, 241, 0.15) !important;
            color: white !important;
            font-weight: 600 !important;
        }
        </style>
    """, unsafe_allow_html=True)

def render_left_panel_metrics(df: pd.DataFrame, file_size_kb: float):
    """Render top metrics in a premium grid."""
    st.markdown("""
        <div style='margin-bottom: 1.5rem;'>
            <h3 style='margin: 0; font-family: "Outfit"; font-weight: 700; color: white; letter-spacing: -0.5px;'>Dataset Essentials</h3>
            <p style='margin: 0.5rem 0 0 0; color: #94A3B8; font-size: 0.875rem;'>Quick overview of your dataset statistics</p>
        </div>
    """, unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
            <div style='background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 1.25rem; text-align: center; transition: all 0.3s ease;'>
                <div style='font-size: 2rem; font-weight: 700; color: white; font-family: "Outfit"; margin-bottom: 0.5rem;'>{len(df):,}</div>
                <div style='color: #94A3B8; font-size: 0.875rem;'>Rows</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div style='background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 1.25rem; text-align: center; transition: all 0.3s ease;'>
                <div style='font-size: 2rem; font-weight: 700; color: white; font-family: "Outfit"; margin-bottom: 0.5rem;'>{len(df.columns):,}</div>
                <div style='color: #94A3B8; font-size: 0.875rem;'>Columns</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div style='background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 1.25rem; text-align: center; transition: all 0.3s ease;'>
                <div style='font-size: 2rem; font-weight: 700; color: white; font-family: "Outfit"; margin-bottom: 0.5rem;'>{file_size_kb:.1f}</div>
                <div style='color: #94A3B8; font-size: 0.875rem;'>KB</div>
            </div>
        """, unsafe_allow_html=True)
    with c4:
        mem = df.memory_usage(deep=True).sum() / (1000 * 1000)
        st.markdown(f"""
            <div style='background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 1.25rem; text-align: center; transition: all 0.3s ease;'>
                <div style='font-size: 2rem; font-weight: 700; color: white; font-family: "Outfit"; margin-bottom: 0.5rem;'>{mem:.1f}</div>
                <div style='color: #94A3B8; font-size: 0.875rem;'>MB</div>
            </div>
        """, unsafe_allow_html=True)

def render_summary_section(dossier: Any, predictions: dict = None, mode: str = "all"):
    """Render the dossier and/or predictions based on the current Lab mode."""
    # Guard: Only exit early if everything is missing AND we aren't specifically initializing projections
    if not dossier and not predictions and mode != "prediction":
        st.info("👋 Welcome! Upload a dataset to generate insights.")
        return

    # 1. CORE BRIEFING (Analysis Lab or All)
    if mode in ["all", "analysis"]:
        if isinstance(dossier, str):
            st.markdown(f'<div class="summary-box">{dossier}</div>', unsafe_allow_html=True)
        else:
            st.markdown("### 🔍 Automated Insight Briefing")
            with st.container(border=True):
                text = dossier.get("text", "")

                # Ensure proper structure: Introduction, Explanation, Visuals
                # If the text doesn't have proper headers, add them
                if text:
                    if "## " not in text[:200]:
                        # Check if it has Introduction section
                        if not text.startswith("## Introduction") and not text.startswith("# Introduction"):
                            # Add Introduction header and wrap text
                            st.markdown(f"## Introduction\n\n{text}")
                        else:
                            st.markdown(text)
                    else:
                        st.markdown(text)

                if dossier.get("figures"):
                    st.divider()
                    st.markdown("#### 📐 Data Distributions & Evidence")
                    figs = dossier["figures"]
                    captions = dossier.get("captions", [])

                    # SINGLE COLUMN FEED for better vertical storytelling
                    for idx, fig in enumerate(figs):
                        st.plotly_chart(fig, use_container_width=True, key=f"summary_dossier_fig_{idx}_{id(fig)}")
                        if idx < len(captions):
                            # Premium Caption Styling
                            st.markdown(f"""
                            <div style="background: rgba(99, 102, 241, 0.05); border-left: 4px solid #6366F1; padding: 1rem; border-radius: 8px; margin-bottom: 2rem;">
                                <span style="color: #6366F1; font-weight: 600;">💡 TACTICAL INSIGHT:</span> {captions[idx]}
                            </div>
                            """, unsafe_allow_html=True)

    # 2. PREDICTIVE FORECAST (Prediction Lab or All)
    if mode in ["all", "prediction"]:
        if predictions:
            st.markdown("---")
            st.markdown("### 🔮 Strategic Forecasting Report")
            with st.container(border=True):
                if predictions.get("fig"):
                    st.plotly_chart(predictions["fig"], width="stretch")
                st.markdown(predictions.get("text", ""))
        elif mode == "prediction" or (mode == "all" and not predictions):
            st.markdown("---")
            st.markdown("#### 🔮 Strategic Forecasting Lab")
            st.caption("Initialize the deep-dive predictive forecast to simulate business impact scenarios.")
            if st.button("🚀 Initialize Predictive Impact Forecast", width="stretch", type="primary"):
                from datamind.agent.summary_agent import SummaryAgent
                from datamind.memory.session import get_dataframe, set_predictions
                df = get_dataframe()
                if df is not None:
                    with st.spinner("Simulating Strategic \"What-If\" Scenarios..."):
                        agent = SummaryAgent()
                        preds = agent.generate_predictions(df)
                        set_predictions(preds)
                        st.rerun()

def render_chat_interface(chat_history: List[Dict[str, Any]], filter_category: Optional[str] = None):
    """Render text-only chat history in the right drawer with premium UI."""
    # Anchor for CSS to find this container
    st.markdown('<div class="chat-drawer-anchor"></div>', unsafe_allow_html=True)

    # Premium Header
    st.markdown("""
        <div style='margin-bottom: 1.5rem;'>
            <h3 style='margin: 0; font-family: "Outfit"; font-weight: 700; color: white; letter-spacing: -0.5px;'>Analyst Dialogue</h3>
            <p style='margin: 0.5rem 0 0 0; color: #94A3B8; font-size: 0.875rem;'>Dialogue history and reasoning</p>
        </div>
    """, unsafe_allow_html=True)

    # Render messages
    for i, msg in enumerate(chat_history):
        if filter_category and msg.get("category") != filter_category:
            continue
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            if "figures" in msg or "lab_narrative" in msg:
                st.info("Detailed analysis and visualizations have been pushed to your Lab. Check the left sidebar to view the full report.")

    # Premium Chat Input
    st.markdown('<div style="margin-top: auto;"></div>', unsafe_allow_html=True)
    query = st.chat_input("Ask DataMind...", key="chat_input")

    return query

def render_main_stage_artifacts(chat_history: List[Dict[str, Any]], filter_category: Optional[str] = None):
    """Render large artifacts filtered by their scientific context (forensics vs simulation)."""
    artifacts_found = False
    
    # Only show if there's history
    if not chat_history:
        return

    st.markdown("---")
    header_text = "🧪 Analysis Laboratory" if filter_category != "simulation" else "🔬 Simulation Laboratory"
    st.markdown(f"### {header_text}")
    
    for i, msg in enumerate(chat_history):
        # Apply filtering logic
        if filter_category and msg.get("category") != filter_category:
            continue
        if "figures" in msg or "lab_narrative" in msg:
            artifacts_found = True
            with st.container():
                session_type = "Forensic" if msg.get("category") == "analysis" else "Simulation"
                st.markdown(f"**{session_type} Session {i+1}**")
                charts = msg.get("figures", [])
                captions = msg.get("captions", [])
                
                # 1. Render Visual Artifacts (Charts/Tables)
                for j, chart in enumerate(charts):
                    if isinstance(chart, Figure):
                        st.plotly_chart(chart, width="stretch", key=f"lab_artifact_fig_{i}_{j}_{id(chart)}")
                        if j < len(captions):
                            st.info(f"💡 {captions[j]}")
                
                # 2. Render Deep Analytical Narrative (Persistent Workspace)
                if msg.get("lab_narrative"):
                    with st.expander("📖 View Strategic Deep-Dive Narrative", expanded=True):
                        narrative = msg["lab_narrative"]
                        # Ensure proper header format
                        if narrative and "## " not in narrative[:200]:
                            # If no headers, wrap in Introduction header
                            st.markdown(f"## Introduction\n\n{narrative}")
                        else:
                            st.markdown(narrative)
                
                st.markdown("---")
    
    if not artifacts_found:
        st.caption("Request a chart or table in chat to see it rendered here in high resolution.")