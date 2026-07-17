"""Extract normalized fields from parsed GitHub Archive events."""

from __future__ import annotations

import logging
from typing import Any

LOGGER = logging.getLogger(__name__)


class GitHubArchiveExtractor:
    """Extract AI-pipeline fields from one parsed GitHub Archive event.

    The extractor only normalizes the event supplied by its caller. It does not
    read files, download data, or persist the extracted result.
    """

    def extract(self, event: dict[str, Any]) -> dict[str, Any] | None:
        """Extract useful fields from a single GitHub Archive event.

        Args:
            event: Parsed GitHub Archive event.

        Returns:
            A normalized event dictionary, or ``None`` when the input is invalid.
        """
        if not isinstance(event, dict):
            LOGGER.warning(
                "Skipping invalid GitHub Archive event: expected a dictionary"
            )
            return None

        repository = self._as_mapping(event.get("repo"))
        actor = self._as_mapping(event.get("actor"))
        organization = self._as_mapping(event.get("org"))
        payload = event.get("payload")

        return {
            "event_id": event.get("id"),
            "event_type": event.get("type"),
            "repository": repository.get("name"),
            "repository_url": repository.get("html_url") or repository.get("url"),
            "actor": actor.get("login") or actor.get("display_login"),
            "actor_id": actor.get("id"),
            "created_at": event.get("created_at"),
            "public": event.get("public"),
            "payload": payload if isinstance(payload, dict) else {},
            "organization": organization.get("login"),
        }

    @staticmethod
    def _as_mapping(value: Any) -> dict[str, Any]:
        """Return a dictionary value, or an empty dictionary when unavailable.

        Args:
            value: Value extracted from an event field.

        Returns:
            The value as a dictionary, or an empty dictionary if it is not one.
        """
        return value if isinstance(value, dict) else {}
