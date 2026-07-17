"""Unit tests for the GitHub Archive parser."""

from __future__ import annotations

import gzip
import json
from pathlib import Path

import pytest

from app.collector.parser import GitHubArchiveParser


def _write_archive(path: Path, lines: list[str]) -> Path:
    """Create a compressed test archive containing the supplied lines."""
    with gzip.open(path, mode="wt", encoding="utf-8") as archive:
        archive.write("\n".join(lines))
    return path


def test_parse_yields_valid_json_objects_and_skips_invalid_lines(
    tmp_path, caplog
) -> None:
    """Valid object lines are streamed while malformed and non-object lines are ignored."""
    archive_path = _write_archive(
        tmp_path / "events.json.gz",
        [
            json.dumps({"id": "1", "type": "PushEvent"}),
            "not-json",
            "",
            json.dumps(["not", "an", "event"]),
            json.dumps({"id": "2", "type": "WatchEvent"}),
        ],
    )

    events = list(GitHubArchiveParser().parse(archive_path))

    assert events == [
        {"id": "1", "type": "PushEvent"},
        {"id": "2", "type": "WatchEvent"},
    ]
    assert "Skipping malformed JSON" in caplog.text
    assert "Skipping non-object JSON" in caplog.text


def test_parse_is_lazy_and_returns_an_iterator(tmp_path) -> None:
    """The parser exposes a streaming iterator rather than a preloaded list."""
    archive_path = _write_archive(
        tmp_path / "events.json.gz", [json.dumps({"id": "1"})]
    )

    events = GitHubArchiveParser().parse(archive_path)

    assert iter(events) is events
    assert next(events) == {"id": "1"}
    with pytest.raises(StopIteration):
        next(events)


def test_parse_rejects_non_gzip_json_filename(tmp_path) -> None:
    """Parser input must identify a compressed JSON archive."""
    file_path = tmp_path / "events.json"
    file_path.write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError, match=".json.gz"):
        list(GitHubArchiveParser().parse(file_path))


def test_parse_raises_for_missing_archive_file(tmp_path) -> None:
    """A missing archive is reported before attempting decompression."""
    missing_path = tmp_path / "missing.json.gz"

    with pytest.raises(FileNotFoundError, match="not found"):
        list(GitHubArchiveParser().parse(missing_path))


def test_parse_raises_for_corrupted_gzip_file(tmp_path) -> None:
    """Corrupted compressed content is surfaced as a read error."""
    archive_path = tmp_path / "corrupted.json.gz"
    archive_path.write_bytes(b"not a gzip archive")

    with pytest.raises(OSError):
        list(GitHubArchiveParser().parse(archive_path))
