"""
DataMind SaaS - Premium Analytics Workspace
Main Entry Point
"""

from __future__ import annotations
import streamlit as st
from datamind.ui.layout import create_split_layout, apply_custom_styles
from datamind.ui.left_panel import render_left_panel
from datamind.ui.right_panel import render_right_panel
from datamind.memory.session import initialize_session_state
from datamind.llm.ollama_client import OllamaClient
from datamind.config import OLLAMA_MODEL

# 1. Page Config
st.set_page_config(
    page_title="DataMind SaaS",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Initialize State
initialize_session_state()

# 3. Apply Premium SaaS Styles
apply_custom_styles()

# 4. Header Section - Premium Typography without Emojis
st.markdown("""
<div style='padding: 0.75rem 0 0.75rem 0; margin-bottom: 0px; border-bottom: 1px solid rgba(255,255,255,0.08);'>
    <div style='display: flex; align-items: center; gap: 1rem;'>
        <div>
            <h1 style='font-family: "Outfit"; font-weight: 800; color: white; margin: 0; font-size: 2.5rem; letter-spacing: -1px;'>
                DataMind <span style='color: #6366F1; font-size: 2rem;'>SaaS</span>
            </h1>
            <p style='color: #94A3B8; margin: 0.25rem 0 0 0; font-size: 0.95rem; font-weight: 400;'>Advanced analytics workspace for modern data teams</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 5. Sidebar (Premium SaaS Navigation)
with st.sidebar:
    st.image("datamind/ui/logo.jpg", use_container_width=True)

    st.markdown("<div style='height: 1px; background: rgba(255,255,255,0.08); margin: 1.5rem 0;'></div>", unsafe_allow_html=True)

    # Premium Navigation Suite
    nav_selection = st.radio(
        "",
        ["🏠 Dashboard", "📐 Analysis Lab", "🔬 Prediction Lab", "📁 Data Manager", "⚙️ Settings"],
        label_visibility="collapsed",
        key="main_nav"
    )
    st.session_state["nav_view"] = nav_selection

    # Bottom Section - Integrated Utilities
    st.markdown("<div style='margin-top: auto;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='height: 1px; background: rgba(255,255,255,0.08); margin: 1.5rem 0;'></div>", unsafe_allow_html=True)

    # Horizontal Action Bar - Unified Format (No Emojis)
    col_bot1, col_bot2 = st.columns(2)
    with col_bot1:
        if st.button("Refresh", use_container_width=True, help="Refresh workspace", key="sidebar_refresh"):
            st.rerun()
    with col_bot2:
        if st.button("Reset", use_container_width=True, help="Reset session", key="sidebar_reset"):
            from datamind.memory.session import initialize_session_state
            st.session_state.clear()
            initialize_session_state()
            st.rerun()

# 6. Main Workspace Layout
expanded = st.session_state.get("chat_expanded", True)

# Current View Router
view = st.session_state.get("nav_view", "🏠 Dashboard")

# Determine if the Analyst Dialogue (chat) should be rendered
# Data Manager and Settings do NOT show the analyst chat panel
show_chat_lane = view in ["🏠 Dashboard", "📐 Analysis Lab", "🔬 Prediction Lab"]
show_right_panel = show_chat_lane and expanded

if show_right_panel:
    # Split Workspace with Analyst Panel (Dashboard, Analysis Lab, Prediction Lab)
    col_main, col_chat = st.columns([2.5, 1])
    with col_main:
        st.markdown('<div class="main-workspace">', unsafe_allow_html=True)
        if "Dashboard" in view:
            render_left_panel()
        elif "Analysis Lab" in view:
            from datamind.ui.layout import render_main_stage_artifacts, render_summary_section
            from datamind.memory.session import get_chat_history, get_summary_text
            st.markdown("""
                <div style='margin-bottom: 2rem;'>
                    <h2 style='margin: 0; font-family: "Outfit"; font-weight: 700; color: white; letter-spacing: -0.5px;'>Analysis Laboratory</h2>
                    <p style='margin: 0.5rem 0 0 0; color: #94A3B8; font-size: 1rem; font-weight: 400;'>Deep-dive forensic analysis and statistical reasoning</p>
                </div>
            """, unsafe_allow_html=True)
            render_summary_section(get_summary_text(), predictions=None, mode="analysis")
            render_main_stage_artifacts(get_chat_history(), filter_category="analysis")
        elif "Prediction Lab" in view:
            from datamind.ui.layout import render_main_stage_artifacts, render_summary_section
            from datamind.memory.session import get_chat_history, get_summary_text, get_predictions
            st.markdown("""
                <div style='margin-bottom: 2rem;'>
                    <h2 style='margin: 0; font-family: "Outfit"; font-weight: 700; color: white; letter-spacing: -0.5px;'>Prediction Laboratory</h2>
                    <p style='margin: 0.5rem 0 0 0; color: #94A3B8; font-size: 1rem; font-weight: 400;'>Strategic forecasting and business impact simulations</p>
                </div>
            """, unsafe_allow_html=True)
            render_summary_section(get_summary_text(), get_predictions(), mode="prediction")
            render_main_stage_artifacts(get_chat_history(), filter_category="simulation")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_chat:
        render_right_panel()
elif not show_chat_lane:
    # Full Width Workspace for Data Manager and Settings (No Analyst Panel)
    st.markdown('<div class="main-workspace expanded">', unsafe_allow_html=True)
    if "Data Manager" in view:
        st.markdown("""
            <div style='margin-bottom: 2rem;'>
                <h2 style='margin: 0; font-family: "Outfit"; font-weight: 700; color: white; letter-spacing: -0.5px;'>Data Manager</h2>
                <p style='margin: 0.5rem 0 0 0; color: #94A3B8; font-size: 1rem; font-weight: 400;'>Multi-dataset inventory and architectural health metrics</p>
            </div>
        """, unsafe_allow_html=True)
        history = st.session_state.get("dataset_history", [])
        if not history:
            st.info("No datasets managed yet. Upload a file to see it here.")
        else:
            # Styled Data Manager List
            for entry in history:
                st.markdown(f"""
                <div class='data-manager-card'>
                    <div style='display: flex; align-items: center; gap: 1.5rem; width: 100%;'>
                        <div class='file-icon-box'>📄</div>
                        <div style='flex-grow: 1;'>
                            <div style='font-family: "Outfit"; font-weight: 600; color: white; font-size: 1.1rem;'>{entry['file_name']}</div>
                            <div style='color: #94A3B8; font-size: 0.85rem; margin-top: 0.25rem;'>
                                Captured: {entry['timestamp']} | {entry['rows']} rows x {entry['columns']} cols
                            </div>
                        </div>
                        <div class='activate-button-container'>
                """, unsafe_allow_html=True)
                
                if st.button("Activate", key=f"activate_{entry['file_name']}", use_container_width=True):
                    st.toast(f"Context switched to {entry['file_name']}")
                    # Logic for switching context would go here (e.g., set_dataframe)
                
                st.markdown("</div></div></div>", unsafe_allow_html=True)
                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True) # Reduced spacing
    elif "Settings" in view:
        # Premium Dashboard Heading
        st.markdown("""
            <div style='margin-bottom: 2rem;'>
                <h2 style='margin: 0; font-family: "Outfit"; font-weight: 700; color: white; letter-spacing: -1px; font-size: 2.5rem;'>System Overview</h2>
                <p style='margin: 0.5rem 0 0 0; color: #94A3B8; font-size: 1.1rem; font-weight: 400;'>Real-time diagnostics and core platform configuration</p>
            </div>
        """, unsafe_allow_html=True)

        # Robust Data Gathering with Deep Fallbacks
        s = st.session_state.get("settings", {})
        ai_s = s.get("ai_engine", {})
        sys_s = s.get("system", {})
        
        # Safe AI Values
        model_name = ai_s.get("model", OLLAMA_MODEL)
        auto_mode = ai_s.get("autonomous_mode", True)
        reasoning_enabled = ai_s.get("show_reasoning", True)
        
        # Safe Dataset Values
        df = st.session_state.get("df")
        file_name = st.session_state.get("current_file_name", "No Data Loaded")
        
        # Safe Session Values
        last_queries = st.session_state.get("last_queries", [])
        last_q = last_queries[-1].get("query", "None") if last_queries else "None"
        last_t = str(last_queries[-1].get("timestamp", "N/A")) if last_queries else "N/A"
        theme_val = sys_s.get("theme", "Dark").capitalize()

        # Define 2x2 Grid for Dashboard Cards
        col_d1, col_d2 = st.columns(2)
        
        with col_d1:
            # 1. AI CONFIGURATION
            st.markdown(f"""
                <div class='settings-section-card'>
                    <div class='settings-header'>🤖 AI Configuration</div>
                    <div class='dash-row'>
                        <span class='dash-label'>Current Model</span>
                        <span class='dash-value'>{model_name}</span>
                    </div>
                    <div class='dash-row'>
                        <span class='dash-label'>Agent Mode</span>
                        <span class='dash-value'>{"Autonomous Analysis" if auto_mode else "Manual Assistant"}</span>
                    </div>
                    <div class='dash-row'>
                        <span class='dash-label'>Reasoning Steps</span>
                        <span class='dash-value'>{"Enabled" if reasoning_enabled else "Disabled"}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # 2. SYSTEM INFORMATION
            import sys
            import platform
            st.markdown(f"""
                <div class='settings-section-card'>
                    <div class='settings-header'>🖥️ System Information</div>
                    <div class='dash-row'>
                        <span class='dash-label'>Backend</span>
                        <span class='dash-value'>Python {sys.version.split()[0]} ({platform.system()})</span>
                    </div>
                    <div class='dash-row'>
                        <span class='dash-label'>LLM Engine</span>
                        <span class='dash-value'>Ollama (Local)</span>
                    </div>
                    <div class='dash-row'>
                        <span class='dash-label'>Code Execution</span>
                        <span class='dash-value'>Restricted Python Engine</span>
                    </div>
                    <div class='dash-row'>
                        <span class='dash-label'>System Status</span>
                        <span class='dash-status-running'>Running</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with col_d2:
            # 3. DATASET INFORMATION
            if df is not None:
                try:
                    null_count = int(df.isna().sum().sum())
                    row_count = len(df)
                    col_count = len(df.columns)
                except Exception:
                    null_count, row_count, col_count = 0, 0, 0
                    
                st.markdown(f"""
                    <div class='settings-section-card'>
                        <div class='settings-header'>📊 Dataset Information</div>
                        <div class='dash-row'>
                            <span class='dash-label'>Dataset Name</span>
                            <span class='dash-value'>{file_name}</span>
                        </div>
                        <div class='dash-row'>
                            <span class='dash-label'>Number of Rows</span>
                            <span class='dash-value'>{row_count:,}</span>
                        </div>
                        <div class='dash-row'>
                            <span class='dash-label'>Number of Columns</span>
                            <span class='dash-value'>{col_count}</span>
                        </div>
                        <div class='dash-row'>
                            <span class='dash-label'>Missing Values</span>
                            <span class='dash-value'>{null_count:,}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class='settings-section-card'>
                        <div class='settings-header'>📊 Dataset Information</div>
                        <div style='color: #94A3B8; text-align: center; padding: 2rem 0;'>
                            No active dataset loaded.
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            # 4. SESSION INFORMATION
            st.markdown(f"""
                <div class='settings-section-card'>
                    <div class='settings-header'>⏱️ Session Information</div>
                    <div class='dash-row'>
                        <span class='dash-label'>Last Query</span>
                        <span class='dash-value' style='max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;'>{last_q}</span>
                    </div>
                    <div class='dash-row'>
                        <span class='dash-label'>Last Analysis</span>
                        <span class='dash-value'>{last_t[:16] if len(last_t) > 16 else last_t}</span>
                    </div>
                    <div class='dash-row'>
                        <span class='dash-label'>Session Theme</span>
                        <span class='dash-value'>{theme_val}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    # Full Width Workspace (Closed Analyst for Dashboard, Analysis Lab, Prediction Lab)
    st.markdown('<div class="main-workspace expanded">', unsafe_allow_html=True)
    if "Dashboard" in view:
        render_left_panel()
    elif "Analysis Lab" in view:
        from datamind.ui.layout import render_main_stage_artifacts, render_summary_section
        from datamind.memory.session import get_chat_history, get_summary_text
        st.markdown("""
            <div style='margin-bottom: 2rem;'>
                <h2 style='margin: 0; font-family: "Outfit"; font-weight: 700; color: white; letter-spacing: -0.5px;'>Analysis Laboratory</h2>
                <p style='margin: 0.5rem 0 0 0; color: #94A3B8; font-size: 1rem; font-weight: 400;'>Deep-dive forensic analysis and statistical reasoning</p>
            </div>
        """, unsafe_allow_html=True)
        render_summary_section(get_summary_text(), predictions=None, mode="analysis")
        render_main_stage_artifacts(get_chat_history(), filter_category="analysis")
    elif "Prediction Lab" in view:
        from datamind.ui.layout import render_main_stage_artifacts, render_summary_section
        from datamind.memory.session import get_chat_history, get_summary_text, get_predictions
        st.markdown("""
            <div style='margin-bottom: 2rem;'>
                <h2 style='margin: 0; font-family: "Outfit"; font-weight: 700; color: white; letter-spacing: -0.5px;'>Prediction Laboratory</h2>
                <p style='margin: 0.5rem 0 0 0; color: #94A3B8; font-size: 1rem; font-weight: 400;'>Strategic forecasting and business impact simulations</p>
            </div>
        """, unsafe_allow_html=True)
        render_summary_section(get_summary_text(), get_predictions(), mode="prediction")
        render_main_stage_artifacts(get_chat_history(), filter_category="simulation")
    st.markdown('</div>', unsafe_allow_html=True)