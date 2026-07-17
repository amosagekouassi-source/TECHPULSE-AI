"""Unit tests for the GitHub Archive collector orchestrator."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import logging

import pytest

from app.collector.downloader import GitHubArchiveDownloadError, GitHubArchiveDownloader
from app.collector.extractor import GitHubArchiveExtractor
from app.collector.github_archive import (
    GitHubArchiveCollectionError,
    GitHubArchiveCollector,
)
from app.collector.parser import GitHubArchiveParser


def _build_collector() -> tuple[
    GitHubArchiveCollector,
    MagicMock,
    MagicMock,
    MagicMock,
]:
    """Build a collector with mocked collaborators."""
    downloader = MagicMock(spec=GitHubArchiveDownloader)
    parser = MagicMock(spec=GitHubArchiveParser)
    extractor = MagicMock(spec=GitHubArchiveExtractor)
    collector = GitHubArchiveCollector(
        downloader=downloader,
        parser=parser,
        extractor=extractor,
    )
    return collector, downloader, parser, extractor


def test_collect_orchestrates_download_parse_and_extraction(tmp_path) -> None:
    """The collector delegates each pipeline stage to the appropriate service."""
    collector, downloader, parser, extractor = _build_collector()
    archive_path = tmp_path / "events.json.gz"
    parsed_events: list[dict[str, Any]] = [{"id": "1"}, {"id": "2"}, {"id": "3"}]
    normalized_events = [{"event_id": "1"}, None, {"event_id": "3"}]

    downloader.download.return_value = archive_path
    parser.parse.return_value = iter(parsed_events)
    extractor.extract.side_effect = normalized_events

    result = list(collector.collect("2024-01-01-0.json.gz"))

    assert result == [{"event_id": "1"}, {"event_id": "3"}]
    downloader.download.assert_called_once_with("2024-01-01-0.json.gz")
    parser.parse.assert_called_once_with(archive_path)
    assert extractor.extract.call_count == 3


def test_collect_wraps_download_errors() -> None:
    """Downloader failures are converted into a collection-specific exception."""
    collector, downloader, _, _ = _build_collector()
    downloader.download.side_effect = GitHubArchiveDownloadError("network unavailable")

    with pytest.raises(GitHubArchiveCollectionError, match="Unable to collect"):
        list(collector.collect("2024-01-01-0.json.gz"))


def test_collect_wraps_parser_errors(tmp_path) -> None:
    """Archive read failures are converted into a collection-specific exception."""
    collector, downloader, parser, _ = _build_collector()
    downloader.download.return_value = tmp_path / "events.json.gz"
    parser.parse.side_effect = OSError("corrupted archive")

    with pytest.raises(GitHubArchiveCollectionError, match="Unable to collect"):
        list(collector.collect("2024-01-01-0.json.gz"))


def test_collect_is_lazy_until_iterated() -> None:
    """No download is initiated until the returned collection iterator is consumed."""
    collector, downloader, _, _ = _build_collector()

    events = collector.collect("2024-01-01-0.json.gz")

    assert iter(events) is events
    downloader.download.assert_not_called()


def test_collect_logs_successful_completion(tmp_path, caplog) -> None:
    """A completed collection emits an informative completion log entry."""
    caplog.set_level(logging.INFO)
    collector, downloader, parser, extractor = _build_collector()
    downloader.download.return_value = Path(tmp_path / "events.json.gz")
    parser.parse.return_value = iter([{"id": "1"}])
    extractor.extract.return_value = {"event_id": "1"}

    assert list(collector.collect("2024-01-01-0.json.gz")) == [{"event_id": "1"}]
    assert "Completed collection" in caplog.text
