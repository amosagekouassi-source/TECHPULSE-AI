"""
TECHPULSE-AI — Manual NVD Collection CLI
=========================================
Run this script to trigger an immediate CVE collection from NVD API v2.

Usage:
    python scripts/run_collector.py                    # collect last 24h
    python scripts/run_collector.py --hours 48         # collect last 48h
    python scripts/run_collector.py --hours 720        # collect last 30 days
    python scripts/run_collector.py --start 2025-01-01 # collect since date
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
LOGGER = logging.getLogger("run_collector")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Manually trigger a TECHPULSE-AI NVD CVE collection cycle."
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Number of hours to look back (default: 24)",
    )
    parser.add_argument(
        "--start",
        type=str,
        default=None,
        help="Start date for collection (ISO format: 2025-01-01)",
    )
    parser.add_argument(
        "--no-faiss",
        action="store_true",
        help="Skip FAISS rebuild after collection (faster, for testing)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    from app.collector.nvd_collector import NVDCollector
    from app.collector.dataset_updater import DatasetUpdater

    collector = NVDCollector()

    if args.start:
        start_dt = datetime.fromisoformat(args.start).replace(tzinfo=timezone.utc)
        LOGGER.info("Collecting CVEs since %s", start_dt.isoformat())
        records = collector.fetch_since(start=start_dt)
    else:
        LOGGER.info("Collecting CVEs from the last %dh", args.hours)
        records = collector.fetch_recent(hours=args.hours)

    LOGGER.info("Fetched %d CVE records from NVD.", len(records))

    if not records:
        LOGGER.info("No new CVEs found for the specified period.")
        return

    updater = DatasetUpdater()
    stats = updater.update(records)

    print("\n" + "=" * 50)
    print("  TECHPULSE-AI — NVD Collection Results")
    print("=" * 50)
    print(f"  Records before : {stats.get('total_before', 'N/A')}")
    print(f"  New CVEs added : {stats.get('new_records', 0)}")
    print(f"  Duplicates     : {stats.get('duplicates_skipped', 0)}")
    print(f"  Total now      : {stats.get('total_after', 'N/A')}")
    if "updated_at" in stats:
        print(f"  Updated at     : {stats['updated_at']}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
