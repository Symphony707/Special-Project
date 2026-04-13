"""
Right Panel for DataMind SaaS
Handles Conversational Interaction with Premium UI.
"""

from __future__ import annotations
import streamlit as st
from datamind.agent.orchestrator import Orchestrator
from datamind.memory.session import get_chat_history, add_chat_message
from datamind.ui.layout import render_chat_interface
from datamind.config import OLLAMA_MODEL

def render_right_panel():
    """Main rendering loop for right panel with lab-aware context."""
    view = st.session_state.get("nav_view", "Dashboard")
    filter_cat = None
    if "Analysis Lab" in view: filter_cat = "analysis"
    elif "Prediction Lab" in view: filter_cat = "simulation"
    
    chat_history = get_chat_history()
    
    # Render history + get new input
    user_query = render_chat_interface(chat_history, filter_category=filter_cat)
    
    if user_query:
        # 1. Process via Orchestrator
        with st.spinner("Synthesizing answer..."):
            orch = Orchestrator(model=st.session_state.get("selected_model", OLLAMA_MODEL))
            res = orch.route_request(user_query)
            
            # 2. Add System Category Tagging
            category = res.get("category", "analysis")
            
            # 3. Add User Message (tagged with detected category)
            add_chat_message("user", user_query, category=category)
            
            # 4. Add Assistant Response
            add_chat_message(
                "assistant", 
                res.get("response", "No response generated."),
                figures=res.get("charts", []),
                captions=res.get("captions", []),
                lab_narrative=res.get("lab_narrative"),
                code=res.get("code"),
                category=category
            )
        
        st.rerun()