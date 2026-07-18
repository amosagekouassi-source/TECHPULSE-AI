"""Validation rules for normalized GitHub Archive events."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

LOGGER = logging.getLogger(__name__)


class EventValidator:
    """Validate the schema of normalized GitHub Archive events.

    This class only validates event data. It does not modify, normalize, clean,
    or persist the event supplied by the caller.
    """

    _REQUIRED_FIELD_TYPES: dict[str, type[object]] = {
        "event_id": str,
        "event_type": str,
        "repository": str,
        "actor": str,
        "created_at": str,
        "public": bool,
        "payload": dict,
    }

    _OPTIONAL_FIELD_TYPES: dict[str, type[object]] = {
        "repository_url": str,
        "actor_id": int,
        "organization": str,
    }

    def validate(self, event: dict[str, Any]) -> bool:
        """Validate one normalized GitHub Archive event.

        Args:
            event: Normalized event returned by the extraction layer.

        Returns:
            ``True`` when the event matches the required schema; otherwise
            ``False``. Validation failures are logged and never raise errors.
        """
        if not isinstance(event, dict):
            LOGGER.error("Invalid event: expected a dictionary")
            return False

        if not self._has_valid_required_fields(event):
            return False

        if not self._has_valid_optional_fields(event):
            return False

        return self._is_valid_iso_datetime(event["created_at"])

    def _has_valid_required_fields(self, event: dict[str, Any]) -> bool:
        """Validate required field presence, types, and non-empty strings.

        Args:
            event: Event to validate.

        Returns:
            ``True`` when every required field is valid; otherwise ``False``.
        """
        for field_name, expected_type in self._REQUIRED_FIELD_TYPES.items():
            value = event.get(field_name)

            if value is None:
                LOGGER.error("Invalid event: missing required field '%s'", field_name)
                return False

            if not isinstance(value, expected_type):
                LOGGER.error(
                    "Invalid event: field '%s' must be %s",
                    field_name,
                    expected_type.__name__,
                )
                return False

            if isinstance(value, str) and not value.strip():
                LOGGER.error("Invalid event: field '%s' must not be empty", field_name)
                return False

        return True

    def _has_valid_optional_fields(self, event: dict[str, Any]) -> bool:
        """Validate types for optional fields when they are present.

        Args:
            event: Event to validate.

        Returns:
            ``True`` when optional fields are valid or absent; otherwise
            ``False``.
        """
        for field_name, expected_type in self._OPTIONAL_FIELD_TYPES.items():
            value = event.get(field_name)

            if value is not None and not isinstance(value, expected_type):
                LOGGER.error(
                    "Invalid event: optional field '%s' must be %s when provided",
                    field_name,
                    expected_type.__name__,
                )
                return False

        return True

    @staticmethod
    def _is_valid_iso_datetime(value: str) -> bool:
        """Check that a timestamp is an ISO-8601 datetime with a timezone.

        Args:
            value: Timestamp value from a normalized event.

        Returns:
            ``True`` when the timestamp is a valid timezone-aware ISO-8601
            datetime; otherwise ``False``.
        """
        try:
            parsed_datetime = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            LOGGER.error("Invalid event: created_at is not ISO-8601: %s", value)
            return False

        if parsed_datetime.tzinfo is None:
            LOGGER.error("Invalid event: created_at must include a timezone: %s", value)
            return False

        return True
