"""
TECHPULSE-AI — NVD Scheduler (APScheduler Background Polling)
=============================================================
Runs a background job every 6 hours to:
    1. Fetch new CVEs from NVD API v2 (only the delta since last run)
    2. Merge them into techpulse_dataset.parquet
    3. Rebuild the FAISS vector index

The scheduler is designed to run alongside Streamlit without blocking the UI.

Author: TECHPULSE-AI Engineering
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

LOGGER = logging.getLogger(__name__)

# Persistent state file to track last successful collection
_STATE_FILE = Path("data/processed/.nvd_last_run.txt")


class NVDScheduler:
    """
    Background scheduler for continuous NVD CVE monitoring.

    Usage:
        scheduler = NVDScheduler(interval_hours=6)
        scheduler.start()          # non-blocking
        scheduler.run_now()        # trigger immediately once
        scheduler.stop()           # graceful shutdown
    """

    def __init__(
        self,
        interval_hours: int = 6,
        nvd_api_key: Optional[str] = None,
        parquet_path: Path | str = Path("data/processed/techpulse_dataset.parquet"),
        vector_store_dir: Path | str = Path("models/vector_store"),
    ) -> None:
        self.interval_hours = interval_hours
        self.nvd_api_key = nvd_api_key or os.getenv("NVD_API_KEY")
        self.parquet_path = Path(parquet_path)
        self.vector_store_dir = Path(vector_store_dir)
        self._scheduler = None
        self._last_run: Optional[datetime] = self._load_last_run()

    # -----------------------------------------------------------------------
    # Lifecycle
    # -----------------------------------------------------------------------

    def start(self) -> None:
        """Start the background scheduler (non-blocking)."""
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from apscheduler.triggers.interval import IntervalTrigger

            self._scheduler = BackgroundScheduler(
                job_defaults={"coalesce": True, "max_instances": 1},
                timezone="UTC",
            )
            self._scheduler.add_job(
                func=self._collection_cycle,
                trigger=IntervalTrigger(hours=self.interval_hours),
                id="nvd_collector",
                name=f"NVD CVE Collection (every {self.interval_hours}h)",
                replace_existing=True,
            )
            self._scheduler.start()
            LOGGER.info(
                "NVD Scheduler started — polling every %dh. Next run: %s",
                self.interval_hours,
                self._scheduler.get_job("nvd_collector").next_run_time,
            )
        except ImportError:
            LOGGER.error(
                "APScheduler not installed. Run: pip install apscheduler>=3.10"
            )
        except Exception as err:
            LOGGER.error("Failed to start NVD Scheduler: %s", err, exc_info=True)

    def stop(self) -> None:
        """Gracefully stop the background scheduler."""
        if self._scheduler and self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            LOGGER.info("NVD Scheduler stopped.")

    def run_now(self) -> dict:
        """
        Trigger one immediate collection cycle (blocking).

        Returns:
            Stats dict from DatasetUpdater.update()
        """
        LOGGER.info("Manual NVD collection triggered.")
        return self._collection_cycle()

    def get_status(self) -> dict:
        """Return scheduler status for the dashboard."""
        running = bool(self._scheduler and self._scheduler.running)
        next_run = None
        if running and self._scheduler:
            job = self._scheduler.get_job("nvd_collector")
            if job:
                next_run = str(job.next_run_time)

        return {
            "running": running,
            "interval_hours": self.interval_hours,
            "last_run": str(self._last_run) if self._last_run else "Never",
            "next_run": next_run or "Not scheduled",
            "api_key_configured": bool(self.nvd_api_key),
        }

    # -----------------------------------------------------------------------
    # Core collection cycle
    # -----------------------------------------------------------------------

    def _collection_cycle(self) -> dict:
        """
        Execute one full collection → merge → FAISS rebuild cycle.

        Returns:
            Stats dict from DatasetUpdater.update()
        """
        cycle_start = datetime.now(timezone.utc)
        LOGGER.info("=" * 60)
        LOGGER.info("NVD Collection Cycle — %s", cycle_start.isoformat())
        LOGGER.info("=" * 60)

        stats: dict = {}
        try:
            from app.collector.nvd_collector import NVDCollector
            from app.collector.dataset_updater import DatasetUpdater

            # Determine look-back window
            if self._last_run:
                look_back_hours = max(
                    self.interval_hours + 1,  # +1h overlap to avoid gaps
                    int((cycle_start - self._last_run).total_seconds() / 3600) + 1,
                )
            else:
                look_back_hours = 48  # First run: fetch last 48h

            LOGGER.info("Look-back window: %dh", look_back_hours)

            # Step 1 — Fetch from NVD
            collector = NVDCollector(api_key=self.nvd_api_key)
            records = collector.fetch_recent(hours=look_back_hours)

            # Step 2 — Merge + rebuild FAISS
            updater = DatasetUpdater(
                parquet_path=self.parquet_path,
                vector_store_dir=self.vector_store_dir,
            )
            stats = updater.update(records)

            # Step 3 — Persist state
            self._last_run = cycle_start
            self._save_last_run(cycle_start)

            elapsed = (datetime.now(timezone.utc) - cycle_start).total_seconds()
            LOGGER.info(
                "Cycle complete in %.1fs — +%d new CVEs (total: %d)",
                elapsed,
                stats.get("new_records", 0),
                stats.get("total_after", 0),
            )

        except Exception as err:
            LOGGER.error("Collection cycle failed: %s", err, exc_info=True)
            stats = {"error": str(err)}

        return stats

    # -----------------------------------------------------------------------
    # Persistence helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _load_last_run() -> Optional[datetime]:
        """Load last successful run timestamp from state file."""
        if _STATE_FILE.is_file():
            try:
                ts = _STATE_FILE.read_text(encoding="utf-8").strip()
                return datetime.fromisoformat(ts)
            except Exception:
                pass
        return None

    @staticmethod
    def _save_last_run(ts: datetime) -> None:
        """Persist last successful run timestamp."""
        try:
            _STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            _STATE_FILE.write_text(ts.isoformat(), encoding="utf-8")
        except Exception as err:
            LOGGER.warning("Could not save last-run timestamp: %s", err)
