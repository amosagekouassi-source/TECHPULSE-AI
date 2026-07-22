"""
TECHPULSE-AI — NVD Collector (NIST NVD API v2)
===============================================
Fetches CVE records from the official NIST National Vulnerability Database API v2.

Features:
    - Full pagination (resultsPerPage up to 2 000)
    - Delta mode: only fetch CVEs published/modified since last run
    - Optional NVD_API_KEY for 50 req/30s rate limit (vs 5 without)
    - Normalized output compatible with techpulse_dataset.parquet schema
    - Graceful error handling with exponential backoff

API reference: https://nvd.nist.gov/developers/vulnerabilities

Author: TECHPULSE-AI Engineering
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

LOGGER = logging.getLogger(__name__)

NVD_BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
RESULTS_PER_PAGE = 2000
DEFAULT_RATE_DELAY = 6.5    # seconds between requests without API key (5 req/30s)
KEYED_RATE_DELAY = 0.6      # seconds between requests with API key (50 req/30s)
MAX_RETRIES = 3


class NVDCollector:
    """
    Client for the NIST NVD CVE API v2.

    Usage:
        collector = NVDCollector(api_key="your_nvd_key")  # key optional
        records = collector.fetch_recent(hours=24)
        records = collector.fetch_since(datetime(2025, 1, 1))
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        """
        Args:
            api_key:  Optional NVD API key. Without it, rate limit is 5 req/30s.
                      Get a free key at https://nvd.nist.gov/developers/request-an-api-key
            session:  Optional requests.Session for connection reuse / testing.
        """
        self.api_key = api_key
        self._session = session or requests.Session()
        self._rate_delay = KEYED_RATE_DELAY if api_key else DEFAULT_RATE_DELAY

        if api_key:
            self._session.headers.update({"apiKey": api_key})
            LOGGER.info("NVDCollector initialised with API key (rate: 50 req/30s)")
        else:
            LOGGER.info("NVDCollector initialised without API key (rate: 5 req/30s)")

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def fetch_recent(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Fetch CVEs published or modified in the last N hours.

        Args:
            hours: Look-back window in hours (default: 24).

        Returns:
            List of normalized CVE records.
        """
        end = datetime.now(timezone.utc)
        start = end - timedelta(hours=hours)
        return self.fetch_since(start, end)

    def fetch_since(
        self,
        start: datetime,
        end: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch CVEs published between start and end datetimes.

        Args:
            start: Inclusive start datetime (UTC).
            end:   Inclusive end datetime (UTC). Defaults to now.

        Returns:
            List of normalized CVE records.
        """
        if end is None:
            end = datetime.now(timezone.utc)

        start_str = start.strftime("%Y-%m-%dT%H:%M:%S.000")
        end_str = end.strftime("%Y-%m-%dT%H:%M:%S.000")

        LOGGER.info(
            "Fetching CVEs from NVD: pubStartDate=%s pubEndDate=%s", start_str, end_str
        )

        all_records: List[Dict[str, Any]] = []
        start_index = 0

        while True:
            params = {
                "pubStartDate": start_str,
                "pubEndDate": end_str,
                "resultsPerPage": RESULTS_PER_PAGE,
                "startIndex": start_index,
            }

            data = self._request(params)
            if data is None:
                LOGGER.error("NVD API request failed — stopping pagination.")
                break

            total = data.get("totalResults", 0)
            vulnerabilities = data.get("vulnerabilities", [])

            batch = [self._normalize(v) for v in vulnerabilities]
            batch = [r for r in batch if r is not None]
            all_records.extend(batch)

            LOGGER.info(
                "Page %d/%d — fetched %d records (total so far: %d / %d)",
                (start_index // RESULTS_PER_PAGE) + 1,
                max(1, -(-total // RESULTS_PER_PAGE)),
                len(batch),
                len(all_records),
                total,
            )

            start_index += RESULTS_PER_PAGE
            if start_index >= total:
                break

            time.sleep(self._rate_delay)

        LOGGER.info("NVD fetch complete: %d CVE records collected.", len(all_records))
        return all_records

    # -----------------------------------------------------------------------
    # HTTP Layer
    # -----------------------------------------------------------------------

    def _request(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make a single paginated API request with retry logic."""
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = self._session.get(
                    NVD_BASE_URL,
                    params=params,
                    timeout=30,
                )
                response.raise_for_status()
                time.sleep(self._rate_delay)
                return response.json()
            except requests.exceptions.HTTPError as err:
                if err.response is not None and err.response.status_code == 403:
                    LOGGER.error("NVD API returned 403 Forbidden — check your API key.")
                    return None
                backoff = 2 ** attempt
                LOGGER.warning(
                    "NVD API HTTP error (attempt %d/%d): %s — retrying in %ds",
                    attempt, MAX_RETRIES, err, backoff,
                )
                time.sleep(backoff)
            except requests.exceptions.RequestException as err:
                backoff = 2 ** attempt
                LOGGER.warning(
                    "NVD API request error (attempt %d/%d): %s — retrying in %ds",
                    attempt, MAX_RETRIES, err, backoff,
                )
                time.sleep(backoff)

        return None

    # -----------------------------------------------------------------------
    # Normalisation — maps NVD v2 JSON → techpulse_dataset.parquet schema
    # -----------------------------------------------------------------------

    def _normalize(self, vuln: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Map one NVD v2 vulnerability object to the TECHPULSE dataset schema.

        Returns None if the record is structurally invalid.
        """
        try:
            cve = vuln.get("cve", {})
            cve_id: str = cve.get("id", "")
            if not cve_id:
                return None

            # Description — prefer English
            descriptions = cve.get("descriptions", [])
            description = next(
                (d["value"] for d in descriptions if d.get("lang") == "en"),
                next((d["value"] for d in descriptions), ""),
            )

            # CVSS score — try v3.1 then v3.0 then v2
            metrics = cve.get("metrics", {})
            cvss_score, severity = self._extract_cvss(metrics)

            # Published date
            published = cve.get("published", "")

            # Affected products → affected_system summary
            configurations = cve.get("configurations", [])
            affected_system = self._extract_affected_system(configurations)

            # Threat type heuristic from description keywords
            threat_type = self._classify_threat_type(description)

            return {
                "record_id":        cve_id,
                "source":           "NVD",
                "description":      description,
                "severity":         severity,
                "cvss_score":       cvss_score,
                "published_date":   published,
                "threat_type":      threat_type,
                "affected_system":  affected_system,
            }

        except Exception as err:
            LOGGER.warning("Failed to normalize CVE record: %s", err)
            return None

    @staticmethod
    def _extract_cvss(metrics: Dict[str, Any]) -> tuple[float, str]:
        """Extract the best available CVSS score and severity label."""
        # Ordered preference: v3.1 → v3.0 → v2
        for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
            entries = metrics.get(key, [])
            if entries:
                cvss_data = entries[0].get("cvssData", {})
                score = float(cvss_data.get("baseScore", 0.0))
                # V2 uses "baseScore" but severity label is in different field
                severity = (
                    entries[0].get("baseSeverity")
                    or cvss_data.get("baseSeverity", "")
                ).upper()
                if not severity:
                    # Map score to label if API doesn't include it
                    if score >= 9.0:
                        severity = "CRITICAL"
                    elif score >= 7.0:
                        severity = "HIGH"
                    elif score >= 4.0:
                        severity = "MEDIUM"
                    else:
                        severity = "LOW"
                return score, severity

        return 0.0, "UNKNOWN"

    @staticmethod
    def _extract_affected_system(configurations: list) -> str:
        """Extract a concise affected system label from CPE configurations."""
        products: List[str] = []
        for config in configurations[:2]:  # Limit to first 2 configs
            for node in config.get("nodes", [])[:3]:
                for match in node.get("cpeMatch", [])[:2]:
                    criteria = match.get("criteria", "")
                    # cpe:2.3:a:vendor:product:version... → vendor:product
                    parts = criteria.split(":")
                    if len(parts) >= 5:
                        products.append(f"{parts[3]}:{parts[4]}")
        return ", ".join(dict.fromkeys(products))[:200] if products else "N/A"

    @staticmethod
    def _classify_threat_type(description: str) -> str:
        """Classify threat type from description keywords."""
        desc = description.lower()
        mapping = [
            ("Remote Code Execution",  ["remote code execution", "rce", "arbitrary code"]),
            ("SQL Injection",          ["sql injection", "sqli"]),
            ("XSS",                    ["cross-site scripting", "xss"]),
            ("Buffer Overflow",        ["buffer overflow", "heap overflow", "stack overflow"]),
            ("Privilege Escalation",   ["privilege escalation", "elevation of privilege"]),
            ("SSRF",                   ["server-side request forgery", "ssrf"]),
            ("Authentication Bypass",  ["authentication bypass", "auth bypass", "improper authentication"]),
            ("Denial of Service",      ["denial of service", "dos", "resource exhaustion"]),
            ("Path Traversal",         ["path traversal", "directory traversal", "lfi", "rfi"]),
            ("Ransomware",             ["ransomware", "ransom"]),
            ("Information Disclosure", ["information disclosure", "information exposure", "data leak"]),
            ("CSRF",                   ["cross-site request forgery", "csrf"]),
            ("XXE",                    ["xml external entity", "xxe"]),
        ]
        for threat_type, keywords in mapping:
            if any(kw in desc for kw in keywords):
                return threat_type
        return "Other"
