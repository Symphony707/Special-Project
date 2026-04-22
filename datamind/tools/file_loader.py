"""
Universal File Ingestion Guard for DataMind v4.0.
Handles multi-format loading, schema fingerprinting, and PII detection.
"""

from __future__ import annotations
import os
import io
import json
import csv
import hashlib
import re
import logging
from typing import Any, Dict, Optional, Tuple

import pandas as pd
import chardet

logger = logging.getLogger(__name__)

from config import MAX_FILE_SIZE_MB, MAX_ROWS
PII_KEYWORDS = [
    "email", "phone", "ssn", "dob", "salary", 
    "address", "national_id", "passport", "age",
    "credit_card", "account_number", "mobile"
]

class FileLoadError(Exception):
    """Custom exception for file loading failures."""
    pass

class UniversalFileLoader:
    """Universal data ingestion engine with guardrails and fingerprinting. Stateless and backend-agnostic."""

    @staticmethod
    def load(file_bytes: bytes, file_name: str, user_id: Optional[int] = None) -> pd.DataFrame:
        """Load file bytes into a DataFrame with safety checks. Raises FileLoadError on failure."""
        from datamind.security.upload_guard import UploadGuard
        
        # 1. Pre-read Validation
        guard_result = UploadGuard.validate_before_read(file_bytes, file_name)
        if not guard_result["safe"]:
            error_msg = guard_result.get("error", "Unknown validation error before read.")
            logger.error(f"UploadGuard rejected file {file_name}: {error_msg}")
            
            if user_id:
                try:
                    from database import log_event
                    log_event(user_id, 'invalid_file_type', error_msg)
                except ImportError:
                    pass
            raise FileLoadError(error_msg)

        ext = os.path.splitext(file_name)[1].lower()
        df = None

        try:
            if ext == ".csv":
                df = UniversalFileLoader._load_csv(file_bytes)
            elif ext in [".xlsx", ".xls"]:
                df = pd.read_excel(io.BytesIO(file_bytes))
            elif ext == ".json":
                df = pd.read_json(io.BytesIO(file_bytes))
            elif ext == ".parquet":
                df = pd.read_parquet(io.BytesIO(file_bytes))
            else:
                raise FileLoadError(f"Unsupported file format: {ext}")
        except Exception as e:
            if isinstance(e, FileLoadError): raise
            raise FileLoadError(f"Error reading {ext} file: {str(e)}")

        if df is not None:
            # 2. Post-read Validation
            guard_result = UploadGuard.validate_after_read(df, file_name)
            if not guard_result["safe"]:
                error_msg = guard_result.get("error", "Unknown validation error after read.")
                logger.error(f"UploadGuard rejected parsed file {file_name}: {error_msg}")
                
                if user_id:
                    try:
                        from database import log_event
                        log_event(user_id, 'file_bomb_detected', error_msg)
                    except ImportError:
                        pass
                raise FileLoadError(error_msg)
            
            # 3. Data Coercion
            df = UniversalFileLoader._run_data_coercer(df)
            
        return df

    @staticmethod
    def _load_csv(file_bytes: bytes) -> pd.DataFrame:
        """Helper to load CSV with auto-detection of encoding and delimiter."""
        rawdata = file_bytes[:10000] # Sample for detection
        result = chardet.detect(rawdata)
        enc = result['encoding'] or 'utf-8'
        
        try:
            decoded_snippet = file_bytes[:2048].decode(enc)
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(decoded_snippet)
            delim = dialect.delimiter
        except Exception:
            delim = "," # Fallback

        return pd.read_csv(io.BytesIO(file_bytes), encoding=enc, sep=delim)

    @staticmethod
    def _run_data_coercer(df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and casts columns automatically."""
        df = df.copy()
        
        # Remove 95%+ null columns
        null_threshold = 0.95
        cols_to_drop = [c for c in df.columns if df[c].isnull().mean() > null_threshold]
        if cols_to_drop:
            logger.info(f"Dropping high-null columns: {cols_to_drop}")
            df.drop(columns=cols_to_drop, inplace=True)

        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                continue
            
            if df[col].dtype == "object":
                sample = df[col].dropna().astype(str).head(100)
                if sample.empty: continue
                
                if sample.str.contains(r'[$£₹€%,\']', regex=True).any():
                    cleaned = df[col].astype(str).str.replace(r'[$£₹€%,\']', '', regex=True)
                    is_pct = sample.str.contains('%').any()
                    try:
                        numeric_s = pd.to_numeric(cleaned, errors='coerce')
                        if is_pct:
                            numeric_s = numeric_s / 100
                        if numeric_s.notnull().mean() > 0.5:
                            df[col] = numeric_s
                            continue
                    except:
                        pass
            
            if df[col].dtype == "object":
                try:
                    if df[col].dropna().astype(str).str.contains(r'\d{2,4}[-/]\d{1,2}[-/]\d{1,2}').any():
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                except:
                    pass
        
        return df

    @staticmethod
    def generate_fingerprint(df: pd.DataFrame) -> Dict[str, Any]:
        """Generate a stable schema fingerprint and detect PII."""
        cols_meta = {}
        pii_columns = []
        pii_detected = False

        for col in df.columns:
            dtype_label = "text"
            if pd.api.types.is_numeric_dtype(df[col]): dtype_label = "numeric"
            elif pd.api.types.is_datetime64_any_dtype(df[col]): dtype_label = "datetime"
            elif pd.api.types.is_bool_dtype(df[col]): dtype_label = "boolean"
            
            unique_count = int(df[col].nunique())
            if unique_count == len(df) and len(df) > 100:
                dtype_label = "id_like"

            is_pii = any(k in col.lower() for k in PII_KEYWORDS)
            if is_pii:
                pii_columns.append(col)
                pii_detected = True

            cols_meta[col] = {
                "dtype": dtype_label,
                "null_pct": float(df[col].isnull().mean() * 100),
                "unique_count": unique_count,
                "sample_values": df[col].dropna().head(3).tolist(),
                "is_pii": is_pii
            }

        full_text = " ".join(df.columns).lower()
        domain = "generic"
        if any(x in full_text for x in ["price", "revenue", "sale", "cost", "invoice"]): domain = "finance"
        elif any(x in full_text for x in ["patient", "diagnosis", "doctor", "health"]): domain = "health"
        elif any(x in full_text for x in ["customer", "order", "sku", "cart"]): domain = "ecommerce"
        elif any(x in full_text for x in ["employee", "salary", "hiring", "leave"]): domain = "hr"
        elif any(x in full_text for x in ["shipment", "warehouse", "tracking"]): domain = "logistics"
        elif any(x in full_text for x in ["student", "grade", "course"]): domain = "education"

        fingerprint_ids = sorted([f"{c}{cols_meta[c]['dtype']}" for c in df.columns])
        hash_str = "|".join(fingerprint_ids)
        fingerprint_hash = hashlib.sha256(hash_str.encode()).hexdigest()

        return {
            "version": 2,
            "columns": cols_meta,
            "row_count": len(df),
            "detected_domain": domain,
            "has_datetime_column": any(v["dtype"] == "datetime" for v in cols_meta.values()),
            "fingerprint_hash": fingerprint_hash,
            "pii_detected": pii_detected,
            "pii_columns": pii_columns
        }

    @staticmethod
    def mask_pii_samples(fingerprint: dict) -> dict:
        """Masks all sample_values for PII-flagged columns."""
        masked = json.loads(json.dumps(fingerprint))  # deep copy
        for col_name, col_info in masked.get("columns", {}).items():
            if col_info.get("is_pii"):
                col_info["sample_values"] = ["[REDACTED]", "[REDACTED]", "[REDACTED]"]
        return masked
