"""Configuration for DistilBERT severity classification."""

from __future__ import annotations

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
    """Central configuration for DistilBERT training and Hugging Face integration.

    Args:
        dataset_path: Unified TECHPULSE dataset used for training.
        model_output_dir: Directory in which the fine-tuned model is saved.
        model_name: Hugging Face base model identifier.
        hub_model_id: Optional Hugging Face Hub repository identifier.
        push_to_hub: Whether to push trained artifacts to the Hub after training.
        max_length: Maximum number of tokenizer tokens per description.
        batch_size: Number of examples processed in each batch.
        epochs: Number of complete training passes over the training split.
        learning_rate: AdamW optimizer learning rate.
        test_size: Fraction reserved for evaluation.
        random_seed: Seed used for reproducible splitting and training.
    """

    dataset_path: Path = field(
        default_factory=lambda: Path("data/processed/techpulse_dataset.parquet")
    )
    model_output_dir: Path = field(
        default_factory=lambda: Path("models/distilbert_severity")
    )
    model_name: str = "distilbert-base-uncased"
    hub_model_id: str = ""
    push_to_hub: bool = False
    max_length: int = 256
    batch_size: int = 16
    epochs: int = 3
    learning_rate: float = 2e-5
    test_size: float = 0.2
    random_seed: int = 42
