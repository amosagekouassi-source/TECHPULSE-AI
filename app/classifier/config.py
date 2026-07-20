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
    """Central configuration for local or Google Colab DistilBERT training.

    Args:
        dataset_path: Unified TECHPULSE dataset used for training.
        model_output_dir: Local directory in which the fine-tuned model is saved.
        model_name: Hugging Face base model identifier.
        max_length: Maximum number of tokenizer tokens per description.
        batch_size: Number of examples processed in each batch.
        epochs: Number of complete training passes over the training split.
        learning_rate: AdamW optimizer learning rate.
        test_size: Fraction reserved for evaluation.
        random_seed: Seed used for reproducible splitting and training.
        device: ``auto`` selects CUDA when available, otherwise CPU.
        huggingface_model_id: Optional Hugging Face Hub repository identifier.
        huggingface_private: Whether a newly created Hub repository is private.
    """

    dataset_path: Path = field(
        default_factory=lambda: Path("data/processed/techpulse_dataset.parquet")
    )
    model_output_dir: Path = field(
        default_factory=lambda: Path("models/distilbert_severity")
    )
    model_name: str = "distilbert-base-uncased"
    max_length: int = 256
    batch_size: int = 16
    epochs: int = 3
    learning_rate: float = 2e-5
    test_size: float = 0.2
    random_seed: int = 42
    device: str = "auto"
    huggingface_model_id: str | None = field(
        default_factory=lambda: os.getenv("HF_MODEL_ID")
    )
    huggingface_private: bool = True
