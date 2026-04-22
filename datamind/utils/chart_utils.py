"""
DataMind v5.0 - Visualization Utilities
Unified Plotly themes and chart generation helpers.
"""

from __future__ import annotations
from typing import Any
import plotly.graph_objects as go

def apply_datamind_theme(fig: Any) -> Any:
    """
    Apply the definitive DataMind design system theme to a Plotly figure.
    This ensures consistent dark-mode aesthetics across the platform.
    """
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='DM Sans, sans-serif', color='#94a3b8', size=12),
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(
            bgcolor='rgba(13,21,38,0.8)',
            bordercolor='rgba(255,255,255,0.05)',
            borderwidth=1,
            font=dict(color='#f1f5f9', size=11),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.03)',
            zerolinecolor='rgba(255,255,255,0.06)',
            tickfont=dict(color='#475569', size=11),
            showgrid=True,
            linecolor='rgba(255,255,255,0.05)'
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.03)',
            zerolinecolor='rgba(255,255,255,0.06)',
            tickfont=dict(color='#475569', size=11),
            showgrid=True,
            linecolor='rgba(255,255,255,0.05)'
        ),
        colorway=['#06b6d4', '#818cf8', '#10b981', '#f43f5e', '#f59e0b', '#ec4899'],
        hoverlabel=dict(
            bgcolor='#111d35',
            font_size=12,
            font_family="DM Sans",
            bordercolor='rgba(6,182,212,0.3)'
        ),
        dragmode='pan'
    )
    
    # Update traces for better look
    if hasattr(fig, 'update_traces'):
        fig.update_traces(
            marker=dict(line=dict(width=0)),
            hoverlabel=dict(namelength=-1)
        )
        
    return fig
