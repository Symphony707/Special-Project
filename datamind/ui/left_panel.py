"""
Left Panel for DataMind SaaS
Handles Uploads and Dataset Profiling with Premium UI.
"""

from __future__ import annotations
import streamlit as st
import pandas as pd
from datamind.memory.session import (
    set_dataframe, set_summary_text, get_dataframe, get_summary_text, get_chat_history,
    get_predictions, clear_predictions, add_to_dataset_history
)
from datamind.tools.stats import compute_fast_stats
from datamind.agent.summary_agent import SummaryAgent
from datamind.agent.viz_agent import VizAgent
from datamind.ui.layout import render_left_panel_metrics, render_summary_section, render_main_stage_artifacts
from datamind.config import OLLAMA_MODEL

def render_left_panel():
    """Main rendering loop for left panel with premium UI."""
    # Premium Header Section
    st.markdown("""
        <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem;'>
            <div>
                <h3 style='margin: 0; font-family: "Outfit"; font-weight: 700; color: white;'>Source Data</h3>
                <p style='margin: 0.25rem 0 0 0; color: #94A3B8; font-size: 0.875rem;'>Upload your CSV dataset to begin analysis</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        
        # Check if new file
        if st.session_state.get("current_file") != uploaded_file.name:
            st.session_state["current_file"] = uploaded_file.name
            st.session_state["current_file_size"] = uploaded_file.size # Fix: Capture actual file size
            set_dataframe(df)
            add_to_dataset_history(uploaded_file.name, len(df), len(df.columns), pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"))
            
            # 1. Trigger Summary Agent (Fast) - Returns Dossier Dict
            with st.spinner("Analyzing dataset..."):
                agent = SummaryAgent(model=st.session_state.get("selected_model", OLLAMA_MODEL))
                dossier = agent.summarize_dossier(df)
                set_summary_text(dossier) 
                clear_predictions() # Reset for new file
            
            # 2. Trigger Viz Cache (Fast)
            viz = VizAgent(df)
            viz.generate_and_cache_top_charts()
            
            st.rerun()

    # Render Stats if data exists
    df = get_dataframe()
    if df is not None:
        file_size_kb = st.session_state.get("current_file_size", 0) / 1000 # Fix: Use decimal KB to match system reporting
        render_left_panel_metrics(df, file_size_kb)
        
        # Manual Trigger for Deep Analysis
        if not get_summary_text():
            if st.button("🚀 Generate Core Analysis Report", width="stretch"):
                with st.spinner("Executing Core Data Analysis Process..."):
                    agent = SummaryAgent(model=st.session_state.get("selected_model", OLLAMA_MODEL))
                    dossier = agent.summarize_dossier(df)
                    set_summary_text(dossier)
                    clear_predictions()
                st.rerun()

        # Dashboard Core Execution: Interleaved Scientific Routing
        # 1. Forensic Forensic Layer (Generated Analysis + Forensic Chat Q&A)
        render_summary_section(get_summary_text(), predictions=None, mode="analysis")
        render_main_stage_artifacts(get_chat_history(), filter_category="analysis")
        
        # 2. Strategic Prediction Layer (Generated Forecast + Predictive Chat Q&A)
        render_summary_section(None, get_predictions(), mode="prediction")
        render_main_stage_artifacts(get_chat_history(), filter_category="simulation")
    else:
        st.info("Upload a dataset to see metrics.")