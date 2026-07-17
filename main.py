"""Run a Sprint 2 integration check for the GitHub Archive ingestion pipeline."""

from __future__ import annotations

import json
import logging
from typing import Any

from app.collector.downloader import GitHubArchiveDownloader
from app.collector.extractor import GitHubArchiveExtractor
from app.collector.github_archive import (
    GitHubArchiveCollectionError,
    GitHubArchiveCollector,
)
from app.collector.parser import GitHubArchiveParser

ARCHIVE_FILENAME = "2024-01-01-0.json.gz"
MAX_EVENTS_TO_DISPLAY = 10

LOGGER = logging.getLogger(__name__)


def configure_logging() -> None:
    """Configure application logging for the integration check."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def display_event(event_number: int, event: dict[str, Any]) -> None:
    """Display one normalized event in a readable JSON format.

    Args:
        event_number: Position of the event in the displayed result set.
        event: Normalized event returned by the collector.
    """
    print(f"\n--- Normalized event {event_number} ---")
    print(json.dumps(event, indent=2, ensure_ascii=False, default=str))


def main() -> int:
    """Run the GitHub Archive ingestion integration test.

    Returns:
        Zero when the pipeline runs successfully, otherwise one.
    """
    configure_logging()
    LOGGER.info("Starting Sprint 2 ingestion integration test")

    downloader = GitHubArchiveDownloader()
    parser = GitHubArchiveParser()
    extractor = GitHubArchiveExtractor()
    collector = GitHubArchiveCollector(
        downloader=downloader,
        parser=parser,
        extractor=extractor,
    )

    try:
        LOGGER.info("Collecting events from %s", ARCHIVE_FILENAME)
        for event_number, event in enumerate(
            collector.collect(ARCHIVE_FILENAME), start=1
        ):
            display_event(event_number, event)
            if event_number >= MAX_EVENTS_TO_DISPLAY:
                break

        LOGGER.info("Sprint 2 ingestion integration test completed successfully")
        return 0

    except GitHubArchiveCollectionError as error:
        LOGGER.error("Integration test stopped because collection failed: %s", error)
        return 1
    except Exception:
        LOGGER.exception("Integration test stopped because of an unexpected error")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
