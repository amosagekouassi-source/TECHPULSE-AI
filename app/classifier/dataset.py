"""Dataset loading and tokenization for severity classification."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset

from .config import LABEL_TO_ID

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class DatasetSplit:
    """Prepared train and test dataframes for severity classification."""

    train: pd.DataFrame
    test: pd.DataFrame


class SeverityDataset(Dataset[dict[str, torch.Tensor]]):
    """Tokenized PyTorch dataset of descriptions and encoded severity labels."""

    def __init__(
        self,
        dataframe: pd.DataFrame,
        tokenizer: Any,
        max_length: int,
    ) -> None:
        """Create a tokenized dataset from a prepared dataframe.

        Args:
            dataframe: Dataframe containing ``description`` and ``label`` columns.
            tokenizer: Hugging Face tokenizer used to encode descriptions.
            max_length: Fixed maximum sequence length for model inputs.
        """
        self._descriptions = dataframe["description"].tolist()
        self._labels = dataframe["label"].tolist()
        self._tokenizer = tokenizer
        self._max_length = max_length

    def __len__(self) -> int:
        """Return the number of examples in the dataset."""
        return len(self._labels)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        """Return tokenized model inputs and the encoded label for one example."""
        encoded = self._tokenizer(
            self._descriptions[index],
            truncation=True,
            padding="max_length",
            max_length=self._max_length,
            return_tensors="pt",
        )
        item = {name: tensor.squeeze(0) for name, tensor in encoded.items()}
        item["labels"] = torch.tensor(self._labels[index], dtype=torch.long)
        return item


def load_and_split_dataset(
    dataset_path: Path | str,
    test_size: float = 0.2,
    random_seed: int = 42,
) -> DatasetSplit:
    """Load, clean, label-encode, and split the TECHPULSE training dataset.

    Args:
        dataset_path: Path to ``techpulse_dataset.parquet``.
        test_size: Fraction of examples reserved for testing.
        random_seed: Seed used by the stratified split.

    Returns:
        Stratified train and test dataframes with ``description`` and ``label``.

    Raises:
        FileNotFoundError: If the Parquet dataset is missing.
        ValueError: If required columns or enough labeled examples are unavailable.
    """
    path = Path(dataset_path)
    if not path.is_file():
        raise FileNotFoundError(f"Training dataset not found: {path}")
    if not 0 < test_size < 1:
        raise ValueError("test_size must be between zero and one")

    LOGGER.info("Loading classifier dataset from %s", path)
    dataframe = pd.read_parquet(path, columns=["description", "severity"])
    _validate_columns(dataframe)

    prepared = dataframe.copy()
    prepared["severity"] = prepared["severity"].astype("string").str.strip().str.upper()
    prepared["description"] = prepared["description"].astype("string").str.strip()
    prepared = prepared.loc[
        prepared["severity"].isin(LABEL_TO_ID)
        & prepared["description"].notna()
        & prepared["description"].ne("")
    ].copy()
    prepared["label"] = prepared["severity"].map(LABEL_TO_ID).astype("int64")

    if prepared.empty:
        raise ValueError("No valid labeled examples remain after dataset preparation")

    label_counts = prepared["label"].value_counts()
    if (label_counts < 2).any():
        missing = label_counts[label_counts < 2].index.tolist()
        raise ValueError(f"Each label needs at least two examples; insufficient labels: {missing}")

    train, test = train_test_split(
        prepared[["description", "label"]],
        test_size=test_size,
        random_state=random_seed,
        stratify=prepared["label"],
    )
    LOGGER.info("Prepared %d train and %d test examples", len(train), len(test))
    return DatasetSplit(train=train.reset_index(drop=True), test=test.reset_index(drop=True))


def _validate_columns(dataframe: pd.DataFrame) -> None:
    """Ensure the source dataframe contains classifier input columns."""
    required_columns = {"description", "severity"}
    missing_columns = sorted(required_columns.difference(dataframe.columns))
    if missing_columns:
        raise ValueError(
            "Training dataset is missing required columns: " + ", ".join(missing_columns)
        )
