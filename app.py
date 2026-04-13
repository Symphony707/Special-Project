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

# 4. Header Section
st.markdown("""
<div style='padding: 2rem 0 1.5rem 0; margin-bottom: 1rem; border-bottom: 1px solid rgba(255,255,255,0.08);'>
    <div style='display: flex; align-items: center; gap: 1.5rem;'>
        <div style='background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%); width: 60px; height: 60px; border-radius: 16px; display: flex; align-items: center; justify-content: center; box-shadow: 0 10px 40px rgba(99, 102, 241, 0.3);'>
            <span style='font-size: 32px;'>✨</span>
        </div>
        <div>
            <h1 style='font-family: "Outfit"; font-weight: 800; color: white; margin: 0; font-size: 2.5rem; letter-spacing: -0.5px;'>
                DataMind <span style='color: #6366F1; font-size: 2rem;'>SaaS</span>
            </h1>
            <p style='color: #94A3B8; margin: 0.5rem 0 0 0; font-size: 1rem; font-weight: 400;'>Advanced analytics workspace for modern data teams</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 5. Sidebar (Premium SaaS Navigation)
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding: 1.5rem 0 2rem 0;'>
            <div style='background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%); width: 70px; height: 70px; margin: 0 auto 1rem auto; border-radius: 18px; display: flex; align-items: center; justify-content: center; box-shadow: 0 10px 40px rgba(99, 102, 241, 0.3);'>
                <span style='font-size: 36px;'>✨</span>
            </div>
            <h2 style='margin: 0; font-family: "Outfit"; font-weight: 700; color: white; font-size: 1.8rem;'>DataMind</h2>
            <p style='margin: 0.5rem 0 0 0; color: #6366F1; font-weight: 500; font-size: 0.9rem;'>SaaS Edition</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 1px; background: rgba(255,255,255,0.08); margin: 1.5rem 0;'></div>", unsafe_allow_html=True)

    # Premium Navigation Suite
    nav_selection = st.radio(
        "",
        ["🏠 Dashboard", "📐 Analysis Lab", "🔬 Prediction Lab", "📁 Data Manager", "⚙️ Settings"],
        label_visibility="collapsed",
        key="main_nav"
    )
    st.session_state["nav_view"] = nav_selection

    # Bottom Section - Premium Spacing
    st.markdown("<div style='margin-top: auto;'></div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 1px; background: rgba(255,255,255,0.08); margin: 2rem 0;'></div>", unsafe_allow_html=True)

    col_bot = st.columns(2)
    with col_bot[0]:
        if st.button("🔄 Sync", use_container_width=True, help="Sync workspace data"):
            st.rerun()
    with col_bot[1]:
        if st.button("🗑️ Reset", use_container_width=True, type="secondary", help="Reset session"):
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
            for entry in history:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([0.1, 0.7, 0.2])
                    c1.markdown("📄")
                    c2.markdown(f"**{entry['file_name']}**")
                    c2.caption(f"Captured: {entry['timestamp']} | {entry['rows']} rows x {entry['columns']} cols")
                    if c3.button("Activate", key=f"activate_{entry['file_name']}"):
                        st.toast(f"Context switched to {entry['file_name']}")
    elif "Settings" in view:
        st.markdown("""
            <div style='margin-bottom: 2rem;'>
                <h2 style='margin: 0; font-family: "Outfit"; font-weight: 700; color: white; letter-spacing: -0.5px;'>Settings</h2>
                <p style='margin: 0.5rem 0 0 0; color: #94A3B8; font-size: 1rem; font-weight: 400;'>System configuration and specialized user profiles</p>
            </div>
        """, unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("### User Excellence Profile")
            st.write("**Role:** Senior Strategic Analyst")
            st.write("**Access Level:** Level 5 Forensic Authorization")
            st.divider()
            st.markdown("### Engine Configuration")
            st.write(f"**Active Intelligence:** {OLLAMA_MODEL}")
            st.write(f"**Node Context:** Active Persistence")
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