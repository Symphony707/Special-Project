"""
ML Runner tools for scikit-learn model training and evaluation.
Aligns with Phase 5 requirements.
"""

from __future__ import annotations

import logging
import time
from typing import Dict, List, Optional, Any, Tuple

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (
    accuracy_score, f1_score, confusion_matrix, 
    mean_squared_error, mean_absolute_error, r2_score
)

from datamind.config import TRAIN_TEST_SPLIT_RATIO, CROSS_VALIDATION_FOLDS

try:
    from xgboost import XGBClassifier, XGBRegressor
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

logger = logging.getLogger(__name__)

def run_classification(df: pd.DataFrame, target: str, features: List[str]) -> Dict[str, Any]:
    """Runs auto-ML classification task."""
    X = df[features]
    y = df[target]
    
    # Handle missing values simply for now (Phase 5 constraints)
    X = X.fillna(X.median(numeric_only=True))
    if y.dtype == 'object' or y.nunique() <= 20:
        y = pd.FactorEncoder().fit_transform(y) if hasattr(pd, 'FactorEncoder') else pd.factorize(y)[0]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, train_size=TRAIN_TEST_SPLIT_RATIO, random_state=42
    )
    
    # Models to try
    models = [
        ("LogisticRegression", LogisticRegression(max_iter=1000)),
        ("RandomForest", RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42))
    ]
    if HAS_XGB:
        models.append(("XGBoost", XGBClassifier(use_label_encoder=False, eval_metric='logloss')))
        
    best_model_name = ""
    best_model = None
    best_score = -1
    
    start_time = time.time()
    for name, model in models:
        if time.time() - start_time > 15: # Phase 5 timeout
            logger.warning(f"ML training timed out at {name}")
            break
            
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        score = accuracy_score(y_test, y_pred)
        
        if score > best_score:
            best_score = score
            best_model_name = name
            best_model = model
            
    # Final eval
    y_pred = best_model.predict(X_test)
    cv_scores = cross_val_score(best_model, X, y, cv=CROSS_VALIDATION_FOLDS)
    
    # Feature Importance
    importance = []
    if hasattr(best_model, "feature_importances_"):
        importance = [
            {"feature": f, "importance": float(i)} 
            for f, i in zip(features, best_model.feature_importances_)
        ]
        importance.sort(key=lambda x: x["importance"], reverse=True)
    
    return {
        "model_type": "classification",
        "best_model": best_model_name,
        "accuracy": float(best_score),
        "f1_score": float(f1_score(y_test, y_pred, average='weighted')),
        "cross_validation": {
            "mean": float(cv_scores.mean()),
            "std": float(cv_scores.std())
        },
        "feature_importance": importance,
        "y_test": y_test.tolist(),
        "y_pred": y_pred.tolist(),
        "classes": list(map(str, np.unique(y)))
    }

def run_regression(df: pd.DataFrame, target: str, features: List[str]) -> Dict[str, Any]:
    """Runs auto-ML regression task."""
    X = df[features]
    y = df[target]
    
    X = X.fillna(X.median(numeric_only=True))
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, train_size=TRAIN_TEST_SPLIT_RATIO, random_state=42
    )
    
    models = [
        ("LinearRegression", LinearRegression()),
        ("Ridge", Ridge()),
        ("RandomForest", RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42))
    ]
    if HAS_XGB:
        models.append(("XGBoost", XGBRegressor()))
        
    best_model_name = ""
    best_model = None
    best_score = -float('inf')
    
    start_time = time.time()
    for name, model in models:
        if time.time() - start_time > 15:
            break
            
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        score = r2_score(y_test, y_pred)
        
        if score > best_score:
            best_score = score
            best_model_name = name
            best_model = model
            
    y_pred = best_model.predict(X_test)
    
    importance = []
    if hasattr(best_model, "feature_importances_"):
        importance = [
            {"feature": f, "importance": float(i)} 
            for f, i in zip(features, best_model.feature_importances_)
        ]
        importance.sort(key=lambda x: x["importance"], reverse=True)

    return {
        "model_type": "regression",
        "best_model": best_model_name,
        "r2_score": float(best_score),
        "mae": float(mean_absolute_error(y_test, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
        "feature_importance": importance,
        "y_test": y_test.tolist(),
        "y_pred": y_pred.tolist()
    }
