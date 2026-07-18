"""Preprocess cybersecurity incident CSV datasets."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

LOGGER = logging.getLogger(__name__)


class IncidentPreprocessor:
    """Load only the relevant fields from supported incident datasets."""

    _DATASET_1_COLUMNS = [
        "Timestamp",
        "Attack Type",
        "Attack Severity",
        "Response Action",
        "Destination IP",
    ]
    _DATASET_2_COLUMNS = [
        "attack_type",
        "attack_severity",
        "target_system",
        "industry",
        "timestamp",
    ]

    def load_dataset_1(self, file_path: Path | str) -> pd.DataFrame:
        """Load the first incident dataset with its required columns.

        Args:
            file_path: Path to ``cybersecurity_dataset.csv``.

        Returns:
            A dataframe containing the selected dataset columns.
        """
        return self._load_csv(file_path, self._DATASET_1_COLUMNS, "incident dataset 1")

    def load_dataset_2(self, file_path: Path | str) -> pd.DataFrame:
        """Load the synthesized incident dataset with its required columns.

        Args:
            file_path: Path to ``cybersecurity_synthesized_data.csv``.

        Returns:
            A dataframe containing the selected dataset columns.
        """
        return self._load_csv(file_path, self._DATASET_2_COLUMNS, "incident dataset 2")

    @staticmethod
    def _load_csv(
        file_path: Path | str,
        required_columns: list[str],
        dataset_name: str,
    ) -> pd.DataFrame:
        """Load a CSV and retain only explicitly required columns.

        Args:
            file_path: CSV file path.
            required_columns: Columns required by the downstream schema mapper.
            dataset_name: Human-readable name used in logs and errors.

        Returns:
            A dataframe restricted to ``required_columns``.

        Raises:
            FileNotFoundError: If the CSV file does not exist.
            ValueError: If one or more required columns are missing.
            pandas.errors.ParserError: If the CSV cannot be parsed.
        """
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"{dataset_name} not found: {path}")

        LOGGER.info("Loading %s from %s", dataset_name, path)
        try:
            dataframe = pd.read_csv(path)
        except (OSError, pd.errors.ParserError) as error:
            LOGGER.error("Unable to load %s: %s", dataset_name, error)
            raise

        missing_columns = sorted(set(required_columns).difference(dataframe.columns))
        if missing_columns:
            raise ValueError(
                f"{dataset_name} is missing required columns: {', '.join(missing_columns)}"
            )

        selected_dataframe = dataframe.loc[:, required_columns].copy()
        LOGGER.info("Loaded %d records from %s", len(selected_dataframe), dataset_name)
        return selected_dataframe
