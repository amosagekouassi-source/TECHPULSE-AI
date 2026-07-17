"""Stream parsed events from compressed GitHub Archive files."""

from __future__ import annotations

import gzip
import json
import logging
from collections.abc import Iterator
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)


class GitHubArchiveParser:
    """Read GitHub Archive ``.json.gz`` files one event at a time.

    This class is deliberately limited to file reading and JSON decoding. It does
    not filter, transform, persist, or otherwise process the yielded events.
    """

    def parse(self, file_path: Path | str) -> Iterator[dict[str, Any]]:
        """Yield valid JSON events from a compressed GitHub Archive file.

        Args:
            file_path: Path to a GitHub Archive file with a ``.json.gz`` suffix.

        Yields:
            Parsed JSON events, one dictionary per valid line.

        Raises:
            FileNotFoundError: If the archive file does not exist.
            ValueError: If the supplied path is not a ``.json.gz`` file.
            OSError: If the archive cannot be read or is not a valid gzip file.
        """
        archive_path = self._validate_file_path(file_path)
        LOGGER.info("Reading GitHub Archive file: %s", archive_path)

        with gzip.open(
            archive_path, mode="rt", encoding="utf-8", errors="replace"
        ) as archive:
            for line_number, line in enumerate(archive, start=1):
                event = self._parse_line(line, archive_path, line_number)
                if event is not None:
                    yield event

    @staticmethod
    def _validate_file_path(file_path: Path | str) -> Path:
        """Validate that a path exists and points to a ``.json.gz`` file.

        Args:
            file_path: Path supplied by the caller.

        Returns:
            The validated archive path.

        Raises:
            FileNotFoundError: If the path does not exist or is not a file.
            ValueError: If the file extension is not ``.json.gz``.
        """
        archive_path = Path(file_path)

        if archive_path.suffixes[-2:] != [".json", ".gz"]:
            raise ValueError("file_path must point to a .json.gz file")
        if not archive_path.is_file():
            raise FileNotFoundError(f"GitHub Archive file not found: {archive_path}")

        return archive_path

    @staticmethod
    def _parse_line(
        line: str,
        archive_path: Path,
        line_number: int,
    ) -> dict[str, Any] | None:
        """Parse one archive line and safely ignore malformed JSON.

        Args:
            line: Raw line read from the archive.
            archive_path: Archive currently being read, for diagnostic logging.
            line_number: One-based line number in the archive.

        Returns:
            The parsed event dictionary, or ``None`` for an invalid line.
        """
        if not line.strip():
            return None

        try:
            event = json.loads(line)
        except json.JSONDecodeError as error:
            LOGGER.warning(
                "Skipping malformed JSON in %s at line %d: %s",
                archive_path,
                line_number,
                error.msg,
            )
            return None

        if not isinstance(event, dict):
            LOGGER.warning(
                "Skipping non-object JSON in %s at line %d",
                archive_path,
                line_number,
            )
            return None

        return event
