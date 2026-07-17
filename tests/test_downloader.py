"""Unit tests for the GitHub Archive downloader."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
import requests

from app.collector.downloader import (
    GitHubArchiveDownloadError,
    GitHubArchiveDownloader,
)


def _build_session(response: MagicMock | None = None) -> MagicMock:
    """Build a mocked requests session and response context manager."""
    session = MagicMock(spec=requests.Session)
    session.get.return_value.__enter__.return_value = response or MagicMock()
    return session


def test_download_saves_streamed_content_and_returns_path(tmp_path) -> None:
    """The downloader stores streamed archive content in the raw-data directory."""
    response = MagicMock()
    response.iter_content.return_value = [b"first", b"", b"second"]
    session = _build_session(response)
    downloader = GitHubArchiveDownloader(download_dir=tmp_path / "raw", session=session)

    result = downloader.download("2024-01-01-0.json.gz")

    assert result == tmp_path / "raw" / "2024-01-01-0.json.gz"
    assert result.read_bytes() == b"firstsecond"
    assert not result.with_suffix(".gz.part").exists()
    session.get.assert_called_once_with(
        "https://data.gharchive.org/2024-01-01-0.json.gz",
        stream=True,
        timeout=60.0,
    )
    response.raise_for_status.assert_called_once_with()


@pytest.mark.parametrize(
    "filename",
    ["", "archive.json", "archive.gz", "../archive.json.gz", "folder/archive.json.gz"],
)
def test_download_rejects_unsafe_or_invalid_filenames(tmp_path, filename: str) -> None:
    """Only plain GitHub Archive .json.gz filenames are accepted."""
    downloader = GitHubArchiveDownloader(download_dir=tmp_path, session=MagicMock())

    with pytest.raises(ValueError, match="plain .json.gz filename"):
        downloader.download(filename)


def test_download_wraps_http_errors_and_removes_partial_file(tmp_path) -> None:
    """HTTP failures are exposed through the downloader-specific exception."""
    response = MagicMock()
    response.raise_for_status.side_effect = requests.HTTPError("not found")
    session = _build_session(response)
    downloader = GitHubArchiveDownloader(download_dir=tmp_path, session=session)

    with pytest.raises(GitHubArchiveDownloadError, match="Failed to download"):
        downloader.download("2024-01-01-0.json.gz")

    assert not (tmp_path / "2024-01-01-0.json.gz.part").exists()


def test_download_wraps_network_connection_errors(tmp_path) -> None:
    """Connection errors do not leak requests implementation exceptions."""
    session = MagicMock(spec=requests.Session)
    session.get.side_effect = requests.ConnectionError("offline")
    downloader = GitHubArchiveDownloader(download_dir=tmp_path, session=session)

    with pytest.raises(GitHubArchiveDownloadError, match="Failed to download"):
        downloader.download("2024-01-01-0.json.gz")


def test_downloader_rejects_non_positive_timeout() -> None:
    """A timeout must be positive to avoid invalid request configuration."""
    with pytest.raises(ValueError, match="greater than zero"):
        GitHubArchiveDownloader(timeout=0)
