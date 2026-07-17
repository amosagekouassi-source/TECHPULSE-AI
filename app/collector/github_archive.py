"""Orchestrate GitHub Archive file ingestion."""

from __future__ import annotations

import logging
from collections.abc import Iterator
from typing import Any

from .downloader import GitHubArchiveDownloadError, GitHubArchiveDownloader
from .extractor import GitHubArchiveExtractor
from .parser import GitHubArchiveParser

LOGGER = logging.getLogger(__name__)


class GitHubArchiveCollectionError(RuntimeError):
    """Raised when GitHub Archive event collection cannot be completed."""


class GitHubArchiveCollector:
    """Coordinate downloading, parsing, and extraction of GitHub Archive events.

    Args:
        downloader: Service responsible for downloading archive files.
        parser: Service responsible for streaming parsed archive events.
        extractor: Service responsible for normalizing parsed events.
    """

    def __init__(
        self,
        downloader: GitHubArchiveDownloader,
        parser: GitHubArchiveParser,
        extractor: GitHubArchiveExtractor,
    ) -> None:
        """Initialize the collector with its required collaborators."""
        self._downloader = downloader
        self._parser = parser
        self._extractor = extractor

    def collect(self, archive_filename: str) -> Iterator[dict[str, Any]]:
        """Yield normalized events from a GitHub Archive file.

        The method delegates each responsibility to its dedicated collaborator:
        downloading, parsing, then extraction. No event data is persisted.

        Args:
            archive_filename: Name of the GitHub Archive ``.json.gz`` file.

        Yields:
            Normalized GitHub Archive events.

        Raises:
            GitHubArchiveCollectionError: If downloading or reading the archive
                fails.
        """
        LOGGER.info("Starting collection for GitHub Archive file %s", archive_filename)

        try:
            archive_path = self._downloader.download(archive_filename)
            LOGGER.info("Parsing downloaded GitHub Archive file %s", archive_path)

            for event in self._parser.parse(archive_path):
                normalized_event = self._extractor.extract(event)
                if normalized_event is not None:
                    yield normalized_event

        except (
            GitHubArchiveDownloadError,
            FileNotFoundError,
            OSError,
            ValueError,
        ) as error:
            LOGGER.error(
                "GitHub Archive collection failed for %s: %s",
                archive_filename,
                error,
            )
            raise GitHubArchiveCollectionError(
                f"Unable to collect GitHub Archive file: {archive_filename}"
            ) from error

        LOGGER.info("Completed collection for GitHub Archive file %s", archive_filename)
