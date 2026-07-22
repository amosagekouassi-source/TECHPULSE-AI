"""
TECHPULSE-AI — Dataset Updater
================================
Merges newly collected CVE records into the existing techpulse_dataset.parquet
and rebuilds the FAISS vector index for the RAG pipeline.

Author: TECHPULSE-AI Engineering
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

LOGGER = logging.getLogger(__name__)

DEFAULT_PARQUET_PATH = Path("data/processed/techpulse_dataset.parquet")
DEFAULT_VECTOR_STORE_DIR = Path("models/vector_store")


class DatasetUpdater:
    """
    Merges new CVE records into the TECHPULSE dataset and rebuilds FAISS index.

    Usage:
        updater = DatasetUpdater()
        stats = updater.update(new_records)
        print(f"Added {stats['new_records']} new CVEs")
    """

    def __init__(
        self,
        parquet_path: Path | str = DEFAULT_PARQUET_PATH,
        vector_store_dir: Path | str = DEFAULT_VECTOR_STORE_DIR,
    ) -> None:
        self.parquet_path = Path(parquet_path)
        self.vector_store_dir = Path(vector_store_dir)

    def update(self, new_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge new CVE records into the dataset and rebuild FAISS index.

        Args:
            new_records: List of normalized CVE dicts from NVDCollector.

        Returns:
            Stats dict: {total_before, total_after, new_records, duplicates_skipped}
        """
        if not new_records:
            LOGGER.info("No new records to merge.")
            return {"total_before": 0, "total_after": 0, "new_records": 0, "duplicates_skipped": 0}

        # 1 — Load existing dataset
        existing_df = self._load_existing()
        total_before = len(existing_df)
        LOGGER.info("Existing dataset: %d records", total_before)

        # 2 — Convert new records to DataFrame
        new_df = pd.DataFrame(new_records)
        new_df = self._normalize_schema(new_df)

        # 3 — Deduplicate on record_id
        if not existing_df.empty and "record_id" in existing_df.columns:
            existing_ids = set(existing_df["record_id"].astype(str))
            new_df = new_df[~new_df["record_id"].astype(str).isin(existing_ids)]

        duplicates_skipped = len(new_records) - len(new_df)
        LOGGER.info(
            "New unique records: %d  |  Duplicates skipped: %d",
            len(new_df), duplicates_skipped,
        )

        if new_df.empty:
            LOGGER.info("All new records already exist in dataset — nothing to merge.")
            return {
                "total_before": total_before,
                "total_after": total_before,
                "new_records": 0,
                "duplicates_skipped": duplicates_skipped,
            }

        # 4 — Merge and save
        merged_df = pd.concat([existing_df, new_df], ignore_index=True)
        self._save_parquet(merged_df)

        total_after = len(merged_df)
        LOGGER.info("Dataset updated: %d → %d records (+%d)", total_before, total_after, len(new_df))

        # 5 — Rebuild FAISS index
        self._rebuild_faiss(merged_df)

        return {
            "total_before": total_before,
            "total_after": total_after,
            "new_records": len(new_df),
            "duplicates_skipped": duplicates_skipped,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    # -----------------------------------------------------------------------
    # Private helpers
    # -----------------------------------------------------------------------

    def _load_existing(self) -> pd.DataFrame:
        """Load the existing parquet dataset or return empty DataFrame."""
        if not self.parquet_path.is_file():
            LOGGER.warning("Parquet dataset not found at %s — starting fresh.", self.parquet_path)
            return pd.DataFrame()
        try:
            df = pd.read_parquet(self.parquet_path)
            return df
        except Exception as err:
            LOGGER.error("Error reading parquet dataset: %s", err, exc_info=True)
            return pd.DataFrame()

    @staticmethod
    def _normalize_schema(df: pd.DataFrame) -> pd.DataFrame:
        """Ensure the DataFrame has all required columns with correct types."""
        required_columns = {
            "record_id":      "",
            "source":         "NVD",
            "description":    "",
            "severity":       "UNKNOWN",
            "cvss_score":     0.0,
            "published_date": "",
            "threat_type":    "Other",
            "affected_system": "N/A",
        }
        for col, default in required_columns.items():
            if col not in df.columns:
                df[col] = default

        df["cvss_score"] = pd.to_numeric(df["cvss_score"], errors="coerce").fillna(0.0)
        df["description"] = df["description"].fillna("").astype(str)
        df["severity"] = df["severity"].fillna("UNKNOWN").str.upper()
        return df[list(required_columns.keys())]

    def _save_parquet(self, df: pd.DataFrame) -> None:
        """Save the merged DataFrame to parquet."""
        self.parquet_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(self.parquet_path, index=False)
        LOGGER.info("Dataset saved to %s", self.parquet_path)

    def _rebuild_faiss(self, df: pd.DataFrame) -> None:
        """Rebuild the FAISS vector index from the updated dataset."""
        LOGGER.info("Rebuilding FAISS vector index...")
        try:
            from app.vector_store.faiss_store import FAISSVectorStore
            store = FAISSVectorStore(index_dir=self.vector_store_dir)
            # Save the merged df temporarily then rebuild
            self._save_parquet(df)
            store.build_from_parquet(parquet_path=self.parquet_path, max_samples=20000)
            LOGGER.info("FAISS index rebuilt successfully.")
        except Exception as err:
            LOGGER.error("FAISS rebuild failed: %s", err, exc_info=True)
            LOGGER.warning("Dataset was saved but FAISS index is NOT updated — run rebuild manually.")
