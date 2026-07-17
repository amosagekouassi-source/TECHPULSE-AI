"""Unit tests for the GitHub Archive extractor."""

from __future__ import annotations

from typing import Any, cast

from app.collector.extractor import GitHubArchiveExtractor


def test_extract_normalizes_a_complete_event() -> None:
    """All useful fields are extracted from a complete GitHub Archive event."""
    event: dict[str, Any] = {
        "id": "event-1",
        "type": "PushEvent",
        "repo": {
            "name": "octocat/hello-world",
            "html_url": "https://github.com/octocat/hello-world",
            "url": "https://api.github.com/repos/octocat/hello-world",
        },
        "actor": {"login": "octocat", "id": 42},
        "created_at": "2024-01-01T00:00:00Z",
        "public": True,
        "payload": {"size": 1},
        "org": {"login": "github"},
    }

    result = GitHubArchiveExtractor().extract(event)

    assert result == {
        "event_id": "event-1",
        "event_type": "PushEvent",
        "repository": "octocat/hello-world",
        "repository_url": "https://github.com/octocat/hello-world",
        "actor": "octocat",
        "actor_id": 42,
        "created_at": "2024-01-01T00:00:00Z",
        "public": True,
        "payload": {"size": 1},
        "organization": "github",
    }


def test_extract_uses_available_fallback_fields() -> None:
    """API repository URLs and display logins are used when primary fields are absent."""
    event: dict[str, Any] = {
        "repo": {"url": "https://api.github.com/repos/example/project"},
        "actor": {"display_login": "example-user"},
    }

    result = GitHubArchiveExtractor().extract(event)

    assert result is not None
    assert result["repository_url"] == "https://api.github.com/repos/example/project"
    assert result["actor"] == "example-user"


def test_extract_handles_missing_or_wrongly_typed_nested_fields() -> None:
    """Incomplete events are normalized without raising exceptions."""
    event: dict[str, Any] = {
        "repo": "invalid",
        "actor": None,
        "org": [],
        "payload": ["invalid"],
    }

    result = GitHubArchiveExtractor().extract(event)

    assert result is not None
    assert result["repository"] is None
    assert result["repository_url"] is None
    assert result["actor"] is None
    assert result["actor_id"] is None
    assert result["organization"] is None
    assert result["payload"] == {}


def test_extract_returns_none_for_an_invalid_event(caplog) -> None:
    """Non-dictionary input is rejected safely and logged."""
    invalid_event = cast(dict[str, Any], None)

    result = GitHubArchiveExtractor().extract(invalid_event)

    assert result is None
    assert "Skipping invalid GitHub Archive event" in caplog.text
