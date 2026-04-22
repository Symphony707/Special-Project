import threading
import time
import logging
import pandas as pd
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

class DataFrameStore:
    """
    Thread-safe singleton for storing in-memory DataFrames.
    Uses a simple access-timestamp based cleanup logic.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DataFrameStore, cls).__new__(cls)
                cls._instance._store = {}
                cls._instance._access_times = {}
                cls._instance._max_size = 20  # Max DataFrames in memory
            return cls._instance

    def set_df(self, file_id: str, df: pd.DataFrame):
        """Stores a DataFrame identified by file_id."""
        with self._lock:
            # Check if we need to evict
            if len(self._store) >= self._max_size and file_id not in self._store:
                self._evict_oldest_unsafe()
            
            self._store[file_id] = df
            self._access_times[file_id] = time.time()
            logger.info(f"Stored DataFrame for file_id: {file_id}. Total cached: {len(self._store)}")

    def get_df(self, file_id: str) -> Optional[pd.DataFrame]:
        """Retrieves a DataFrame by file_id."""
        with self._lock:
            if file_id in self._store:
                self._access_times[file_id] = time.time()
                return self._store[file_id]
            return None

    def get_df_auto(self, file_id: int) -> Optional[pd.DataFrame]:
        """
        Smart retrieval: Tries memory first, fallbacks to disk re-hydration.
        Handles uvicorn reload/restart scenarios where frontend holds a stale file_id.
        """
        # 1. Try memory
        df = self.get_df(str(file_id))
        if df is not None:
            return df

        # 2. Re-hydration logic (lazy-loaded to avoid circular deps)
        logger.info(f"DataFrame for {file_id} missing from RAM. Attempting disk re-hydration...")
        try:
            import os
            import database as db
            from config import UPLOADS_DIR
            from datamind.tools.file_loader import UniversalFileLoader

            global_file = db.get_global_file_by_id(file_id)
            if not global_file:
                logger.error(f"Re-hydration failed: Global file {file_id} not in DB.")
                return None

            file_path = os.path.join(UPLOADS_DIR, global_file["file_hash"])
            if not os.path.exists(file_path):
                logger.error(f"Re-hydration failed: Source file missing at {file_path}")
                return None

            with open(file_path, "rb") as f:
                file_bytes = f.read()
            
            df = UniversalFileLoader.load(file_bytes, global_file["original_filename"])
            if df is not None:
                self.set_df(str(file_id), df)
                logger.info(f"Successfully re-hydrated asset {file_id} into memory.")
                return df

        except Exception as e:
            logger.error(f"Re-hydration exception for {file_id}: {e}")
        
        return None

    def delete(self, file_id: str):
        """Removes a DataFrame from the store."""
        with self._lock:
            if file_id in self._store:
                del self._store[file_id]
                del self._access_times[file_id]
                logger.info(f"Deleted DataFrame for file_id: {file_id}")

    def _evict_oldest_unsafe(self):
        """Internal method to evict the least recently used DataFrame."""
        if not self._access_times:
            return
        oldest_id = min(self._access_times, key=self._access_times.get)
        del self._store[oldest_id]
        del self._access_times[oldest_id]
        logger.info(f"Evicted DataFrame for file_id: {oldest_id} due to capacity limits.")

# Global instance
df_store = DataFrameStore()
