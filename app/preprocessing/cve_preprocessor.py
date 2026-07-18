"""Preprocess NVD CVE JSON feeds into tabular records."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd

LOGGER = logging.getLogger(__name__)


class CvePreprocessor:
    """Extract the fields needed by TECHPULSE from NVD CVE JSON feeds."""

    _OUTPUT_COLUMNS = [
        "cve_id",
        "description",
        "base_severity",
        "base_score",
        "affected_vendor",
        "affected_product",
        "published",
    ]
    _CVSS_METRIC_KEYS = ("cvssMetricV40", "cvssMetricV31", "cvssMetricV30")

    def preprocess(self, file_path: Path | str) -> pd.DataFrame:
        """Load one NVD feed and return extracted CVE records.

        Args:
            file_path: Path to an NVD CVE JSON feed.

        Returns:
            A dataframe containing the extracted CVE fields.

        Raises:
            FileNotFoundError: If the feed does not exist.
            ValueError: If the JSON feed does not have the expected structure.
            json.JSONDecodeError: If the feed is not valid JSON.
            OSError: If the feed cannot be read.
        """
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"CVE feed not found: {path}")

        LOGGER.info("Loading NVD CVE feed from %s", path)
        try:
            with path.open("r", encoding="utf-8") as json_file:
                payload = json.load(json_file)
        except (OSError, json.JSONDecodeError) as error:
            LOGGER.error("Unable to load CVE feed %s: %s", path, error)
            raise

        vulnerabilities = self._get_vulnerabilities(payload, path)
        records = [self._extract_record(item) for item in vulnerabilities]
        dataframe = pd.DataFrame(records, columns=self._OUTPUT_COLUMNS)
        LOGGER.info("Extracted %d CVE records from %s", len(dataframe), path.name)
        return dataframe

    @staticmethod
    def _get_vulnerabilities(payload: Any, path: Path) -> list[dict[str, Any]]:
        """Get vulnerability entries from an NVD feed payload.

        Args:
            payload: Decoded JSON payload.
            path: Source path used in diagnostic messages.

        Returns:
            Vulnerability entries from the feed.

        Raises:
            ValueError: If the payload cannot be interpreted as an NVD feed.
        """
        if isinstance(payload, dict):
            vulnerabilities = payload.get("vulnerabilities")
        elif isinstance(payload, list):
            vulnerabilities = payload
        else:
            vulnerabilities = None

        if not isinstance(vulnerabilities, list):
            raise ValueError(f"Invalid NVD feed structure in {path}")

        return [item for item in vulnerabilities if isinstance(item, dict)]

    def _extract_record(self, vulnerability: dict[str, Any]) -> dict[str, Any]:
        """Extract a normalized intermediate record from one NVD entry.

        Args:
            vulnerability: One vulnerability entry from an NVD feed.

        Returns:
            Extracted CVE fields ready for schema mapping.
        """
        cve = vulnerability.get("cve")
        cve_data = cve if isinstance(cve, dict) else vulnerability
        metric_data = self._extract_cvss_metric(cve_data)
        vendors, products = self._extract_affected(cve_data, vulnerability)

        return {
            "cve_id": cve_data.get("id"),
            "description": self._english_description(cve_data.get("descriptions")),
            "base_severity": metric_data.get("baseSeverity"),
            "base_score": metric_data.get("baseScore"),
            "affected_vendor": ", ".join(vendors) or None,
            "affected_product": ", ".join(products) or None,
            "published": cve_data.get("published") or vulnerability.get("published"),
        }

    def _extract_cvss_metric(self, cve: dict[str, Any]) -> dict[str, Any]:
        """Return the first available CVSS v4.0, v3.1, or v3.0 metric.

        Args:
            cve: CVE object from an NVD feed.

        Returns:
            The selected CVSS data dictionary, or an empty dictionary.
        """
        metrics = cve.get("metrics")
        if not isinstance(metrics, dict):
            return {}

        for metric_key in self._CVSS_METRIC_KEYS:
            metric_entries = metrics.get(metric_key)
            if not isinstance(metric_entries, list):
                continue

            for metric_entry in metric_entries:
                if not isinstance(metric_entry, dict):
                    continue
                cvss_data = metric_entry.get("cvssData")
                if isinstance(cvss_data, dict):
                    return cvss_data

        return {}

    @staticmethod
    def _english_description(descriptions: Any) -> str | None:
        """Select the first English description from an NVD description list."""
        if not isinstance(descriptions, list):
            return None

        for description in descriptions:
            if not isinstance(description, dict):
                continue
            if description.get("lang") == "en" and isinstance(description.get("value"), str):
                return description["value"]

        return None

    @staticmethod
    def _extract_affected(
        cve: dict[str, Any],
        vulnerability: dict[str, Any],
    ) -> tuple[list[str], list[str]]:
        """Extract unique vendors and products from affected entries.

        Args:
            cve: CVE object from an NVD feed.
            vulnerability: Parent vulnerability object.

        Returns:
            A tuple containing vendor names and product names.
        """
        affected = cve.get("affected") or vulnerability.get("affected") or []
        if isinstance(affected, dict):
            affected = [affected]
        if not isinstance(affected, list):
            return [], []

        vendors: list[str] = []
        products: list[str] = []
        for item in affected:
            if not isinstance(item, dict):
                continue
            vendor = item.get("vendor")
            product = item.get("product")
            if isinstance(vendor, str) and vendor and vendor not in vendors:
                vendors.append(vendor)
            if isinstance(product, str) and product and product not in products:
                products.append(product)

        return vendors, products
