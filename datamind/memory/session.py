"""
DataMind SaaS - Session Memory Subsystem (Headless)
Manages user-scoped state, file deduplication, and database synchronization with PII protection.
"""

import os
import re
import json
import hashlib
import logging
from typing import Any, Optional, Dict, List
import pandas as pd
from plotly.graph_objects import Figure

import database as db
from datamind.tools.file_loader import UniversalFileLoader
from config import UPLOADS_DIR, OLLAMA_MODEL

logger = logging.getLogger(__name__)

def _clean_md_block(t: str) -> str:
    if not isinstance(t, str): return ""
    t = re.sub(r'<<<BRIEF>>>|<<<DETAILED>>>|\[GRAPH CAPTIONS\]', '', t).strip()
    if t.startswith('```'):
        t = re.sub(r'^```[a-zA-Z]*\n?', '', t)
        t = re.sub(r'\n?```$', '', t)
        
    # Prevent multi-space indenting from triggering markdown code blocks
    lines = t.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.lstrip()
        if (line.startswith('    ') or line.startswith('\t')) and not (stripped.startswith('-') or stripped.startswith('*')):
            cleaned_lines.append(stripped)
        else:
            cleaned_lines.append(line)
            
    return '\n'.join(cleaned_lines).strip()

def activate_data_asset(file_id: int, user_id: int) -> Optional[pd.DataFrame]:
    """Activates a past analytical asset by loading from disk."""
    from datamind.security.authorizer import Authorizer
    Authorizer.assert_file_access(user_id, file_id)

    # 1. Fetch metadata
    files = db.get_user_files(user_id)
    file_meta = next((f for f in files if f['global_file_id'] == file_id), None)
    if not file_meta:
        return None
        
    # 2. Load from disk
    file_path = os.path.join(UPLOADS_DIR, file_meta['file_hash'])
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Asset file not found in storage: {file_meta['file_hash']}")
        
    try:
        with open(file_path, "rb") as f:
            file_bytes = f.read()
            
        df = UniversalFileLoader.load(file_bytes, file_meta['original_filename'])
        if df is None:
            return None
            
        db.update_last_accessed(user_id, file_id)
        return df
    except Exception as e:
        logger.error(f"Error activating asset: {e}")
        return None

def handle_file_upload(file_bytes: bytes, filename: str, user_id: Optional[int]) -> Optional[pd.DataFrame]:
    """Processes file upload with SHA256 deduplication and DB mapping."""
    if not file_bytes:
        return None

    if user_id:
        from datamind.security.rate_limiter import RateLimiter
        rate_result = RateLimiter.check_file_upload(user_id)
        if not rate_result["allowed"]:
            raise ValueError(rate_result["message"])

    from datamind.security.sanitizer import InputSanitizer
    safe_name = InputSanitizer.sanitize_filename(filename)
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    
    # 2. Universal Loading (Ingestion Guards)
    df = UniversalFileLoader.load(file_bytes, safe_name)
    if df is None:
        return None

    df, col_mapping = InputSanitizer.sanitize_column_names(df)

    # 3. Generate Fingerprint & Mask PII
    fingerprint = UniversalFileLoader.generate_fingerprint(df)
    safe_fingerprint = UniversalFileLoader.mask_pii_samples(fingerprint)
    
    # 4. Global Registration (Deduplication)
    file_id = db.insert_global_file(
        file_hash=file_hash,
        filename=safe_name,
        fingerprint_json=json.dumps(safe_fingerprint),
        row_count=len(df),
        col_count=len(df.columns),
        domain=safe_fingerprint.get("detected_domain", "generic")
    )

    # 5. Map User to File
    if user_id is not None:
        db.create_user_file_ref(user_id, file_id, safe_name)
    
    # 5b. Persist to Disk if not present
    file_path = os.path.join(UPLOADS_DIR, file_hash)
    if not os.path.exists(file_path):
        with open(file_path, "wb") as f:
            f.write(file_bytes)
    
    # Trigger Learning Loop (Statistical)
    try:
        from datamind.memory.learner import PatternLearner
        if user_id is not None:
            learner = PatternLearner()
            learner.extract_statistical_patterns(df, file_id, user_id)
    except Exception as e:
        logger.warning(f"Pattern learning failed: {e}")

    return df