"""
TECHPULSE-AI — Full Monitoring Entry Point
===========================================
Starts the NVD background scheduler and the Streamlit dashboard simultaneously.

Usage:
    python scripts/start_monitoring.py

This script:
    1. Starts the NVD scheduler (background thread, polls every 6h)
    2. Triggers an immediate collection on first launch
    3. Launches the Streamlit dashboard
    4. Handles graceful shutdown (Ctrl+C)
"""

from __future__ import annotations

import logging
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
LOGGER = logging.getLogger("start_monitoring")


def main() -> None:
    LOGGER.info("=" * 60)
    LOGGER.info("  TECHPULSE-AI — Monitoring Platform Starting")
    LOGGER.info("=" * 60)

    # ── 1. Start NVD Background Scheduler ────────────────────────────
    from app.collector.nvd_scheduler import NVDScheduler

    scheduler = NVDScheduler(interval_hours=6)
    scheduler.start()

    # ── 2. Trigger first collection immediately ───────────────────────
    LOGGER.info("Triggering initial NVD collection...")
    try:
        stats = scheduler.run_now()
        LOGGER.info(
            "Initial collection done: +%d new CVEs (total: %d)",
            stats.get("new_records", 0),
            stats.get("total_after", 0),
        )
    except Exception as err:
        LOGGER.warning("Initial collection failed (non-fatal): %s", err)

    # ── 3. Launch Streamlit dashboard ────────────────────────────────
    dashboard_path = Path("app/dashboard/app.py")
    if not dashboard_path.is_file():
        LOGGER.error("Dashboard not found at %s", dashboard_path)
        scheduler.stop()
        sys.exit(1)

    LOGGER.info("Launching Streamlit dashboard at http://localhost:8501")
    streamlit_proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", str(dashboard_path), "--server.headless=true"],
        env={**os.environ, "PYTHONPATH": str(Path.cwd())},
    )

    # ── 4. Graceful shutdown on Ctrl+C ───────────────────────────────
    def _shutdown(signum, frame):
        LOGGER.info("Shutdown signal received — stopping...")
        scheduler.stop()
        streamlit_proc.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    LOGGER.info(
        "TECHPULSE-AI is running. Dashboard: http://localhost:8501 | Press Ctrl+C to stop."
    )

    try:
        while True:
            status = scheduler.get_status()
            LOGGER.debug("Scheduler status: %s", status)
            time.sleep(300)  # Log status every 5 minutes
    except KeyboardInterrupt:
        _shutdown(None, None)


if __name__ == "__main__":
    main()
