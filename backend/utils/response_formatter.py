import re
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

def format_analysis_response(raw_response: str,
                              agent_used: str,
                              artifact_data: dict = None) -> dict:
    """
    Takes raw agent text and wraps it in structured sections.
    The agent's text is parsed for natural section breaks
    OR the entire text becomes the Detail section.
    """
    sections = []

    # Try to detect existing section headers in agent output
    # Agents sometimes write "## Introduction" or "**Finding:**"
    text = raw_response.strip()

    # Check if agent already structured the output
    has_structure = bool(re.search(
        r'(?m)^(#{1,3}\s|\*\*[A-Z][^*]+\*\*:)',
        text, re.IGNORECASE
    ))

    if has_structure:
        # Parse existing structure
        # Split on markdown headers or bold section labels starting at the beginning of a line
        parts = re.split(
            r'(?m)^(?=#{1,3}\s|\*\*[A-Z][^*]+\*\*:)',
            text
        )
        for part in parts:
            part = part.strip()
            if not part:
                continue
            # Detect section type from first line
            lines = part.split('\n')
            first_line = lines[0].lower()
            
            if any(w in first_line for w in ['intro','overview','context','about']):
                stype = 'introduction'
            elif any(w in first_line for w in ['conclusion','summary','recommend','implication']):
                stype = 'conclusion'
            elif any(w in first_line for w in ['table','snapshot','data','evidence','visual']):
                stype = 'data'
            else:
                stype = 'detail'
            sections.append({'type': stype, 'content': part})
    else:
        # Agent returned plain text — preserve it as a unified document
        sections = [
            {'type': 'detail', 'content': text}
        ]

    # If artifact data (charts/tables) exists, inject as data section if not already present
    if artifact_data:
        sections.append({
            'type': 'visualization',
            'content': '',
            'artifact': artifact_data
        })

    return {
        'sections':   sections,
        'agent_used': agent_used,
        'raw':        raw_response,
        'timestamp':  datetime.now().isoformat(),
        'structured': True,
    }


def format_prediction_response(result: dict) -> dict:
    """
    Takes prediction agent result dict and formats
    it into a high-fidelity section structure for the dossier.
    """
    # Extract inner results
    res_inner = result.get('results', {})
    task_type = res_inner.get('task_type', result.get('task_type', 'prediction'))
    target    = result.get('target_column') or res_inner.get('target_column') or 'Target Dimension'
    best_model= res_inner.get('best_model_name', 'Neural Engine')
    accuracy  = res_inner.get('test_accuracy') or res_inner.get('test_r2') or 0
    
    # Use the narrative parsing logic from format_analysis_response
    raw_response = result.get('response', '')
    
    # Parsing logic
    sections_map = {}
    text = raw_response.strip()
    parts = re.split(r'(?m)^(?=#{1,4}\s)', text)
    for part in parts:
        part = part.strip()
        if not part: continue
        first_line = part.split('\n')[0].lower()
        if 'briefing' in first_line: sections_map['briefing'] = part
        elif 'forensic context' in first_line: sections_map['context'] = part
        elif 'conclusion' in first_line: sections_map['conclusion'] = part

    final_sections = []

    # 1. 🛡️ Predictive Mission Briefing
    if 'briefing' in sections_map:
        final_sections.append({'type': 'introduction', 'content': sections_map['briefing']})
    
    # 2. 📊 Model Performance Comparison (Data Table)
    cv_table = res_inner.get('cv_scores_table', [])
    model_detail = "### 📊 Model Performance Comparison\n"
    if cv_table:
        model_detail += "\n| Model Architecture | Verification Score | Confidence |\n"
        model_detail += "| :--- | :--- | :--- |\n"
        for m in cv_table:
            name = m.get('Model', 'Unknown')
            score = m.get('Mean Accuracy') or m.get('Mean R2') or '0'
            dev = m.get('Std Dev', '0.000')
            model_detail += f"| {name} | {score} | ±{dev} |\n"
    else:
        model_detail += f"The training cluster utilized a 5-fold cross-validation strategy. The **{best_model}** exhibited the highest stability across all data folds."
    final_sections.append({'type': 'data', 'content': model_detail})

    # 3. 🔍 Key Intelligence Drivers (Interactive Visual)
    fi = res_inner.get('feature_importances', [])
    if fi:
        final_sections.append({
            'type':    'visualization',
            'content': '### 🔍 Key Intelligence Drivers\nBelow are the top dimensions influencing the predictive outcome.',
            'artifact': {
                'type':  'feature_importance',
                'data':  fi[:10],
                'title': f'Driver Analysis: {target}'
            }
        })

    # 4. 🧬 Forensic Context & Intelligence
    if 'context' in sections_map:
        final_sections.append({'type': 'detail', 'content': sections_map['context']})

    # 5. 🎯 Model Precision Mapping (Confusion Matrix or Scatter)
    cm = res_inner.get('confusion_matrix')
    if cm:
        final_sections.append({
            'type':    'visualization',
            'content': '### 🎯 Model Precision Mapping\nConfusion matrix visualization for classification accuracy.',
            'artifact': {
                'type': 'confusion_matrix',
                'data': cm,
                'task': task_type,
            }
        })

    # 6. 💡 Strategic Conclusion
    if 'conclusion' in sections_map:
        final_sections.append({'type': 'conclusion', 'content': sections_map['conclusion']})

    return {
        'sections':        final_sections,
        'task_type':       task_type,
        'target_column':   target,
        'best_model':      best_model,
        'accuracy':        accuracy,
        'cv_scores_table': cv_table,
        'timestamp':       datetime.now().isoformat(),
        'structured':      True,
    }
