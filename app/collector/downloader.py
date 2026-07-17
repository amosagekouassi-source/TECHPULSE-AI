"""Download GitHub Archive files to the project's raw-data directory."""

from __future__ import annotations

import logging
from pathlib import Path

import requests

LOGGER = logging.getLogger(__name__)


class GitHubArchiveDownloadError(RuntimeError):
    """Raised when a GitHub Archive file cannot be downloaded."""


class GitHubArchiveDownloader:
    """Download compressed GitHub Archive files.

    Args:
        download_dir: Directory in which downloaded ``.json.gz`` files are saved.
        base_url: Base URL of the GitHub Archive service.
        timeout: Maximum number of seconds to wait for the HTTP request.
        session: Optional HTTP session injected for connection reuse and testability.
    """

    def __init__(
        self,
        download_dir: Path | str = Path("data/raw"),
        base_url: str = "https://data.gharchive.org",
        timeout: float = 60.0,
        session: requests.Session | None = None,
    ) -> None:
        """Initialize the downloader configuration."""
        if timeout <= 0:
            raise ValueError("timeout must be greater than zero")

        self._download_dir = Path(download_dir)
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = session or requests.Session()

    def download(self, archive_filename: str) -> Path:
        """Download one GitHub Archive ``.json.gz`` file.

        Args:
            archive_filename: Archive filename, for example
                ``2026-07-17-0.json.gz``.

        Returns:
            The path of the successfully downloaded file.

        Raises:
            ValueError: If ``archive_filename`` is not a plain ``.json.gz`` filename.
            GitHubArchiveDownloadError: If the HTTP request or file download fails.
        """
        filename = self._validate_filename(archive_filename)
        self._download_dir.mkdir(parents=True, exist_ok=True)

        destination = self._download_dir / filename
        temporary_destination = destination.with_suffix(destination.suffix + ".part")
        url = f"{self._base_url}/{filename}"

        LOGGER.info("Downloading GitHub Archive file from %s", url)

        try:
            with self._session.get(url, stream=True, timeout=self._timeout) as response:
                response.raise_for_status()
                with temporary_destination.open("wb") as output_file:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            output_file.write(chunk)

            # A temporary file prevents incomplete downloads appearing as valid data.
            temporary_destination.replace(destination)
        except requests.RequestException as error:
            LOGGER.error(
                "Unable to download GitHub Archive file %s: %s", filename, error
            )
            self._remove_partial_file(temporary_destination)
            raise GitHubArchiveDownloadError(
                f"Failed to download GitHub Archive file: {filename}"
            ) from error
        except OSError as error:
            LOGGER.error("Unable to save GitHub Archive file %s: %s", filename, error)
            self._remove_partial_file(temporary_destination)
            raise GitHubArchiveDownloadError(
                f"Failed to save GitHub Archive file: {filename}"
            ) from error

        LOGGER.info("GitHub Archive file saved to %s", destination)
        return destination

    @staticmethod
    def _validate_filename(archive_filename: str) -> str:
        """Validate and normalize a GitHub Archive filename.

        Args:
            archive_filename: Filename provided by the caller.

        Returns:
            The validated filename.

        Raises:
            ValueError: If the input is not a safe ``.json.gz`` filename.
        """
        filename = Path(archive_filename)
        if (
            not archive_filename
            or filename.name != archive_filename
            or not archive_filename.endswith(".json.gz")
        ):
            raise ValueError("archive_filename must be a plain .json.gz filename")
        return filename.name

    @staticmethod
    def _remove_partial_file(file_path: Path) -> None:
        """Remove an incomplete download when it exists."""
        try:
            file_path.unlink(missing_ok=True)
        except OSError as error:
            LOGGER.warning("Unable to remove partial file %s: %s", file_path, error)
