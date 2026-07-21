"""Configuration for DistilBERT severity classification."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

LABEL_TO_ID: dict[str, int] = {
    "LOW": 0,
    "MEDIUM": 1,
    "HIGH": 2,
    "CRITICAL": 3,
}
ID_TO_LABEL: dict[int, str] = {label_id: label for label, label_id in LABEL_TO_ID.items()}


@dataclass(frozen=True, slots=True)
class ClassifierConfig:
    """Central configuration for local or Google Colab DistilBERT training."""

    dataset_path: Path = field(
        default_factory=lambda: Path("data/processed/techpulse_dataset.parquet")
    )
    model_output_dir: Path = field(
        default_factory=lambda: Path("models/distilbert-severity")
    )
    model_name: str = "distilbert-base-uncased"
    max_length: int = 128
    batch_size: int = 8
    gradient_accumulation_steps: int = 4
    epochs: int = 1
    sample_size: int = 10000
    learning_rate: float = 2e-5
    test_size: float = 0.2
    random_seed: int = 42
    device: str = "auto"
    huggingface_model_id: str | None = field(
        default_factory=lambda: os.getenv("HF_MODEL_ID")
    )
    huggingface_private: bool = True
