"""Build and persist the unified TECHPULSE preprocessing dataset."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd

from .schema_mapper import SchemaMapper

LOGGER = logging.getLogger(__name__)


class DatasetBuilder:
    """Merge mapped source datasets and generate preprocessing artifacts.

    Args:
        schema_mapper: Mapper used to transform source dataframes into the
            canonical TECHPULSE schema.
    """

    def __init__(self, schema_mapper: SchemaMapper | None = None) -> None:
        """Initialize the builder with an optional injected schema mapper."""
        self._schema_mapper = schema_mapper or SchemaMapper()

    def build(
        self,
        cve_2025: pd.DataFrame,
        cve_2026: pd.DataFrame,
        incident_dataset_1: pd.DataFrame,
        incident_dataset_2: pd.DataFrame,
    ) -> pd.DataFrame:
        """Map, merge, and deduplicate all preprocessing sources.

        Args:
            cve_2025: Extracted CVE records for 2025.
            cve_2026: Extracted CVE records for 2026.
            incident_dataset_1: Loaded records from the first incident CSV.
            incident_dataset_2: Loaded records from the synthesized incident CSV.

        Returns:
            A unified dataframe matching the TECHPULSE schema.
        """
        LOGGER.info("Mapping source datasets to the TECHPULSE schema")
        frames = [
            self._schema_mapper.map_cves(cve_2025),
            self._schema_mapper.map_cves(cve_2026),
            self._schema_mapper.map_incident_dataset_1(incident_dataset_1),
            self._schema_mapper.map_incident_dataset_2(incident_dataset_2),
        ]
        unified_dataframe = pd.concat(frames, ignore_index=True)
        initial_count = len(unified_dataframe)
        unified_dataframe = unified_dataframe.drop_duplicates(
            subset=["record_id"],
            keep="first",
        ).reset_index(drop=True)
        LOGGER.info(
            "Built %d unified records (%d duplicates removed)",
            len(unified_dataframe),
            initial_count - len(unified_dataframe),
        )
        return unified_dataframe

    @staticmethod
    def save_dataset(dataframe: pd.DataFrame, output_path: Path | str) -> Path:
        """Save the unified dataset as a Parquet file.

        Args:
            dataframe: Unified TECHPULSE dataframe.
            output_path: Destination path for the Parquet artifact.

        Returns:
            The written Parquet path.

        Raises:
            OSError: If the output cannot be written.
            ImportError: If the required Parquet engine is unavailable.
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        LOGGER.info("Saving unified dataset to %s", path)
        try:
            dataframe.to_parquet(path, index=False, engine="pyarrow")
        except (OSError, ImportError) as error:
            LOGGER.error("Unable to save Parquet dataset %s: %s", path, error)
            raise
        return path

    @staticmethod
    def generate_report(dataframe: pd.DataFrame, output_path: Path | str) -> dict[str, Any]:
        """Generate and save a report about the unified dataset.

        Args:
            dataframe: Unified TECHPULSE dataframe.
            output_path: Destination path for the JSON report.

        Returns:
            The report data written to disk.
        """
        source_counts = dataframe["source"].value_counts(dropna=False)
        severity_counts = dataframe["severity"].fillna("UNKNOWN").value_counts()
        report: dict[str, Any] = {
            "total_cve_records": int(source_counts.get("CVE", 0)),
            "total_incident_records": int(source_counts.get("INCIDENT", 0)),
            "total_records": int(len(dataframe)),
            "severity_distribution": {
                str(severity): int(count) for severity, count in severity_counts.items()
            },
            "missing_values_by_column": {
                column: int(count) for column, count in dataframe.isna().sum().items()
            },
        }

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        LOGGER.info("Saving preprocessing report to %s", path)
        with path.open("w", encoding="utf-8") as report_file:
            json.dump(report, report_file, indent=2, ensure_ascii=False)

        return report
