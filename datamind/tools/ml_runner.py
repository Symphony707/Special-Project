"""
Universal ML Runner for DataMind v4.0 (Headless)
Handles automated task selection, preprocessing, and model training.
"""

from __future__ import annotations
import logging
import time
import json
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, KFold, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, Ridge, LinearRegression
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    mean_squared_error, mean_absolute_error, r2_score
)
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

try:
    from statsmodels.tsa.arima.model import ARIMA
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False

from datamind.llm.ollama_client import call_ollama_sync

logger = logging.getLogger(__name__)

class UniversalMLRunner:
    """Universal ML Engine with automated task selection and model optimization."""

    def __init__(self):
        pass

    def auto_select_task(self, df: pd.DataFrame, target_col: Optional[str]) -> str:
        """Determines the ML task type based on target characteristics."""
        if target_col is None:
            return "clustering"
        
        if target_col not in df.columns:
            return "regression" # Fallback

        series = df[target_col].dropna()
        unique_count = series.nunique()
        dtype = series.dtype

        # Check for Time Series
        datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        if datetime_cols and pd.api.types.is_numeric_dtype(dtype):
            return "timeseries"

        # Check for Classification
        if 2 <= unique_count <= 15 and (pd.api.types.is_integer_dtype(dtype) or pd.api.types.is_object_dtype(dtype) or pd.api.types.is_categorical_dtype(dtype)):
            return "classification"
        
        # Check for Regression
        if pd.api.types.is_numeric_dtype(dtype) and unique_count > 15:
            return "regression"
        
        return "regression" # Safe fallback

    def preprocess(self, df: pd.DataFrame, target_col: Optional[str], task: str) -> Dict[str, Any]:
        """Prepares data for training: null handling, encoding, scaling."""
        df = df.copy()
        
        # 1. Drop columns with >60% nulls
        null_mask = df.isnull().mean() > 0.6
        df.drop(columns=df.columns[null_mask], inplace=True)
        
        # 2. Impute Nulls
        for col in df.columns:
            if df[col].isnull().any():
                if pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].fillna(df[col].median())
                else:
                    df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else "Unknown")

        # 3. Temporal Feature Extraction
        datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        for col in datetime_cols:
            df[f"{col}_year"] = df[col].dt.year
            df[f"{col}_month"] = df[col].dt.month
            df[f"{col}_day"] = df[col].dt.day
            df[f"{col}_dow"] = df[col].dt.dayofweek
            df.drop(columns=[col], inplace=True)

        # 4. Separate X and y
        if task == "clustering":
            X = df.select_dtypes(include=[np.number])
            y = None
        else:
            if target_col not in df.columns:
                target_col = df.columns[-1] # Fallback
            X = df.drop(columns=[target_col])
            y = df[target_col]

        # 5. Encode Categorical Features
        cat_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
        for col in cat_cols:
            if X[col].nunique() <= 20:
                dummies = pd.get_dummies(X[col], prefix=col)
                X = pd.concat([X, dummies], axis=1)
                X.drop(columns=[col], inplace=True)
            else:
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col].astype(str))

        if task == "classification" and y is not None:
            le_target = LabelEncoder()
            y = le_target.fit_transform(y.astype(str))

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        X_final = pd.DataFrame(X_scaled, columns=X.columns)

        if task == "clustering":
            return {"X": X_final, "feature_names": X.columns.tolist()}
        
        X_train, X_test, y_train, y_test = train_test_split(X_final, y, test_size=0.2, random_state=42)
        return {
            "X_train": X_train, "X_test": X_test, 
            "y_train": y_train, "y_test": y_test,
            "feature_names": X.columns.tolist()
        }

    def run_classification(self, X_train, X_test, y_train, y_test, feature_names):
        """Trains and picks the best classification model."""
        models = [
            ("RandomForest", RandomForestClassifier(n_estimators=100, random_state=42)),
            ("GradientBoosting", GradientBoostingClassifier(random_state=42)),
            ("LogisticRegression", LogisticRegression(max_iter=1000, random_state=42))
        ]
        
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        best_mean_acc = 0
        best_model = None
        best_name = ""
        cv_results = []

        # Optimization: Sample for CV if dataset is large
        X_train_cv, y_train_cv = X_train, y_train
        if len(X_train) > 15000:
            X_train_cv = X_train.sample(15000, random_state=42)
            y_train_cv = y_train[X_train_cv.index]
            logger.info(f"Large dataset detected ({len(X_train)} rows). Sampling to 15k for cross-validation selection.")

        for name, model in models:
            scores = cross_val_score(model, X_train_cv, y_train_cv, cv=cv, scoring='accuracy')
            mean_score = scores.mean()
            cv_results.append({"Model": name, "Mean Accuracy": f"{mean_score:.3f}", "Std Dev": f"{scores.std():.3f}"})
            if mean_score > best_mean_acc:
                best_mean_acc = mean_score
                best_model = model
                best_name = name

        # Optimization: Cap final training size for responsiveness
        X_train_final, y_train_final = X_train, y_train
        if len(X_train) > 50000:
            X_train_final = X_train.sample(50000, random_state=42)
            y_train_final = y_train[X_train_final.index]
            logger.info(f"Capping final training to 50k rows for engine responsiveness.")

        best_model.fit(X_train_final, y_train_final)
        y_pred = best_model.predict(X_test)
        
        fi_df = None
        if hasattr(best_model, 'feature_importances_'):
            fi_df = pd.DataFrame({'feature': feature_names, 'importance': best_model.feature_importances_})
            fi_df = fi_df.sort_values(by='importance', ascending=False)

        return {
            "best_model_name": best_name,
            "cv_scores_table": cv_results, # already a list of dicts
            "test_accuracy": float(accuracy_score(y_test, y_pred)),
            "report": classification_report(y_test, y_pred, output_dict=True),
            "feature_importances": fi_df.to_dict(orient="records") if fi_df is not None else [],
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist()
        }

    def run_regression(self, X_train, X_test, y_train, y_test, feature_names):
        """Trains and picks the best regression model."""
        models = [
            ("RandomForest", RandomForestRegressor(n_estimators=100, random_state=42)),
            ("GradientBoosting", GradientBoostingRegressor(random_state=42)),
            ("Ridge", Ridge(random_state=42))
        ]
        
        cv = KFold(n_splits=5, shuffle=True, random_state=42)
        best_r2 = -float('inf')
        best_model = None
        best_name = ""
        cv_results = []

        # Optimization: Sample for CV if dataset is large
        X_train_cv, y_train_cv = X_train, y_train
        if len(X_train) > 15000:
            X_train_cv = X_train.sample(15000, random_state=42)
            y_train_cv = y_train[X_train_cv.index]
            logger.info(f"Large dataset detected ({len(X_train)} rows). Sampling to 15k for cross-validation selection.")

        for name, model in models:
            scores = cross_val_score(model, X_train_cv, y_train_cv, cv=cv, scoring='r2')
            mean_score = scores.mean()
            cv_results.append({"Model": name, "Mean R2": f"{mean_score:.3f}"})
            if mean_score > best_r2:
                best_r2 = mean_score
                best_model = model
                best_name = name

        # Optimization: Cap final training size for responsiveness
        X_train_final, y_train_final = X_train, y_train
        if len(X_train) > 50000:
            X_train_final = X_train.sample(50000, random_state=42)
            y_train_final = y_train[X_train_final.index]
            logger.info(f"Capping final training to 50k rows for engine responsiveness.")

        best_model.fit(X_train_final, y_train_final)
        y_pred = best_model.predict(X_test)

        fi_df = None
        if hasattr(best_model, 'feature_importances_'):
            fi_df = pd.DataFrame({'feature': feature_names, 'importance': best_model.feature_importances_})
            fi_df = fi_df.sort_values(by='importance', ascending=False)

        return {
            "best_model_name": best_name,
            "cv_scores_table": cv_results,
            "test_r2": float(r2_score(y_test, y_pred)),
            "test_rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
            "test_mae": float(mean_absolute_error(y_test, y_pred)),
            "feature_importances": fi_df.to_dict(orient="records") if fi_df is not None else []
        }

    def run_clustering(self, df: pd.DataFrame, feature_names: List[str]):
        """Runs KMeans clustering with elbow optimization and LLM labeling."""
        n_samples = min(len(df), 10000)
        df_sample = df.sample(n_samples, random_state=42)
        X = df_sample[feature_names]

        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X)

        k_limit = min(8, int(np.sqrt(n_samples)))
        inertias = []
        for k in range(2, k_limit + 1):
            km = KMeans(n_clusters=k, random_state=42, n_init=10)
            km.fit(X)
            inertias.append(km.inertia_)

        deltas = np.diff(inertias)
        optimal_k = 2
        if len(deltas) > 0:
            optimal_k = np.argmin(deltas) + 2

        kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X)
        centroids = kmeans.cluster_centers_

        cluster_descriptions = {}
        for i in range(optimal_k):
            c_vals = centroids[i]
            global_means = X.mean().values
            diffs = c_vals - global_means
            
            top_idx = np.argsort(np.abs(diffs))[-3:]
            labels = []
            for idx in top_idx:
                direction = "High" if diffs[idx] > 0 else "Low"
                labels.append(f"{direction} {feature_names[idx]}")
            
            summary = ", ".join(labels)
            label_prompt = f"Given these characteristics: {summary}. Generate a 5-word business label for this customer/data cluster."
            try:
                label = call_ollama_sync(
                    system_prompt="You are a dataset cluster labeling agent.",
                    user_prompt=label_prompt
                )
                if label:
                    label = label.strip()
                else:
                    label = f"Cluster {i+1}"
            except:
                label = f"Cluster {i+1} Characteristics"
            
            cluster_descriptions[i] = {"label": label, "summary": summary}

        return {
            "optimal_k": int(optimal_k),
            "cluster_labels": clusters.tolist(),
            "pca_2d_coords": X_pca.tolist(),
            "cluster_descriptions": cluster_descriptions
        }

    def run_timeseries(self, df: pd.DataFrame, date_col: str, target_col: str):
        """Forecasting using ARIMA or LinearRegression fallback."""
        df_ts = df[[date_col, target_col]].dropna().sort_values(date_col)
        df_ts.set_index(date_col, inplace=True)
        df_ts = df_ts.resample('D').mean().ffill()
        
        history = df_ts[target_col].values
        model_used = "ARIMA(1,1,1)"
        forecast_vals = []
        conf_intervals = None

        if HAS_STATSMODELS and len(history) > 10:
            try:
                model = ARIMA(history, order=(1,1,1))
                model_fit = model.fit()
                forecast = model_fit.get_forecast(steps=10)
                forecast_vals = forecast.predicted_mean
                conf_intervals = forecast.conf_int()
            except:
                model_used = "Linear Trend Fallback"
        else:
            model_used = "Linear Trend Fallback"

        if model_used == "Linear Trend Fallback":
            X = np.arange(len(history)).reshape(-1, 1)
            lr = LinearRegression()
            lr.fit(X, history)
            X_future = np.arange(len(history), len(history) + 10).reshape(-1, 1)
            forecast_vals = lr.predict(X_future)

        last_date = df_ts.index[-1]
        forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=10)

        return {
            "model_used": model_used,
            "forecast_values": forecast_vals.tolist() if hasattr(forecast_vals, 'tolist') else list(forecast_vals),
            "forecast_dates": [str(d) for d in forecast_dates],
            "confidence_intervals": conf_intervals.tolist() if conf_intervals is not None else None
        }
