"""Map source datasets into the unified TECHPULSE schema."""

from __future__ import annotations

import hashlib
import logging
from typing import Any

import pandas as pd

LOGGER = logging.getLogger(__name__)


class SchemaMapper:
    """Transform CVE and incident records into one TECHPULSE schema."""

    COLUMNS = [
        "record_id",
        "source",
        "description",
        "severity",
        "threat_type",
        "affected_system",
        "industry",
        "published_date",
        "cvss_score",
    ]

    def map_cves(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Map CVE records to the TECHPULSE schema.

        Args:
            dataframe: Extracted CVE dataframe.

        Returns:
            A dataframe with the canonical TECHPULSE columns.
        """
        self._require_columns(
            dataframe,
            {
                "cve_id",
                "description",
                "base_severity",
                "base_score",
                "affected_vendor",
                "affected_product",
                "published",
            },
            "CVE dataframe",
        )

        mapped = pd.DataFrame(index=dataframe.index)
        mapped["record_id"] = dataframe["cve_id"].astype("string")
        mapped["source"] = "CVE"
        mapped["description"] = dataframe["description"].astype("string")
        mapped["severity"] = dataframe["base_severity"].map(self.normalize_severity)
        mapped["threat_type"] = "VULNERABILITY"
        mapped["affected_system"] = self._combine_system_fields(
            dataframe["affected_vendor"],
            dataframe["affected_product"],
        )
        mapped["industry"] = pd.NA
        mapped["published_date"] = self._parse_datetime(dataframe["published"])
        mapped["cvss_score"] = pd.to_numeric(dataframe["base_score"], errors="coerce")
        return self._finalize(mapped)

    def map_incident_dataset_1(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Map the first incident dataset to the TECHPULSE schema.

        Args:
            dataframe: Incident dataframe containing title-case source columns.

        Returns:
            A dataframe with the canonical TECHPULSE columns.
        """
        columns = {
            "Timestamp",
            "Attack Type",
            "Attack Severity",
            "Response Action",
            "Destination IP",
        }
        self._require_columns(dataframe, columns, "incident dataset 1")

        mapped = pd.DataFrame(index=dataframe.index)
        mapped["source"] = "INCIDENT"
        mapped["description"] = dataframe["Attack Type"].astype("string")
        mapped["severity"] = dataframe["Attack Severity"].map(self.normalize_severity)
        mapped["threat_type"] = dataframe["Attack Type"].astype("string")
        mapped["affected_system"] = dataframe["Destination IP"].astype("string")
        mapped["industry"] = pd.NA
        mapped["published_date"] = self._parse_datetime(dataframe["Timestamp"])
        mapped["cvss_score"] = pd.NA
        mapped["record_id"] = self._incident_ids(mapped, "incident_dataset_1")
        return self._finalize(mapped)

    def map_incident_dataset_2(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Map the synthesized incident dataset to the TECHPULSE schema.

        Args:
            dataframe: Incident dataframe containing snake-case source columns.

        Returns:
            A dataframe with the canonical TECHPULSE columns.
        """
        columns = {
            "attack_type",
            "attack_severity",
            "target_system",
            "industry",
            "timestamp",
        }
        self._require_columns(dataframe, columns, "incident dataset 2")

        mapped = pd.DataFrame(index=dataframe.index)
        mapped["source"] = "INCIDENT"
        mapped["description"] = dataframe["attack_type"].astype("string")
        mapped["severity"] = dataframe["attack_severity"].map(self.normalize_severity)
        mapped["threat_type"] = dataframe["attack_type"].astype("string")
        mapped["affected_system"] = dataframe["target_system"].astype("string")
        mapped["industry"] = dataframe["industry"].astype("string")
        mapped["published_date"] = self._parse_datetime(dataframe["timestamp"])
        mapped["cvss_score"] = pd.NA
        mapped["record_id"] = self._incident_ids(mapped, "incident_dataset_2")
        return self._finalize(mapped)

    @staticmethod
    def normalize_severity(value: Any) -> str:
        """Normalize source severity values to the TECHPULSE vocabulary.

        Args:
            value: Source severity value, possibly missing or numeric.

        Returns:
            One of ``CRITICAL``, ``HIGH``, ``MEDIUM``, ``LOW``, or ``UNKNOWN``.
        """
        if pd.isna(value):
            return "UNKNOWN"

        normalized = str(value).strip().upper()
        aliases = {
            "CRITICAL": "CRITICAL",
            "HIGH": "HIGH",
            "MEDIUM": "MEDIUM",
            "MODERATE": "MEDIUM",
            "LOW": "LOW",
            "1": "LOW",
            "2": "MEDIUM",
            "3": "HIGH",
            "4": "CRITICAL",
        }
        return aliases.get(normalized, "UNKNOWN")

    @staticmethod
    def _require_columns(
        dataframe: pd.DataFrame,
        required_columns: set[str],
        dataframe_name: str,
    ) -> None:
        """Raise a descriptive error when expected source columns are absent."""
        missing_columns = sorted(required_columns.difference(dataframe.columns))
        if missing_columns:
            raise ValueError(
                f"{dataframe_name} is missing required columns: {', '.join(missing_columns)}"
            )

    @staticmethod
    def _combine_system_fields(vendors: pd.Series, products: pd.Series) -> pd.Series:
        """Combine vendor and product columns without introducing null strings."""
        vendor_values = vendors.fillna("").astype(str).str.strip()
        product_values = products.fillna("").astype(str).str.strip()
        combined = (vendor_values + " " + product_values).str.strip()
        return combined.mask(combined.eq(""), pd.NA).astype("string")

    @staticmethod
    def _parse_datetime(values: pd.Series) -> pd.Series:
        """Parse timestamps to timezone-aware datetimes while preserving invalid nulls."""
        return pd.to_datetime(values, errors="coerce", utc=True)

    @staticmethod
    def _incident_ids(dataframe: pd.DataFrame, dataset_name: str) -> pd.Series:
        """Create deterministic identifiers for incident records without native IDs."""
        identifier_columns = [
            "description",
            "severity",
            "threat_type",
            "affected_system",
            "industry",
            "published_date",
        ]

        def build_identifier(row: pd.Series) -> str:
            values = "|".join(str(row.get(column, "")) for column in identifier_columns)
            digest = hashlib.sha256(f"{dataset_name}|{values}".encode("utf-8")).hexdigest()
            return f"INC-{digest}"

        return dataframe.apply(build_identifier, axis=1).astype("string")

    def _finalize(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Return columns in canonical order and enforce normalized severities."""
        finalized = dataframe.reindex(columns=self.COLUMNS).copy()
        finalized["severity"] = finalized["severity"].fillna("UNKNOWN").astype("string")
        return finalized
