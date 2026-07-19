"""Train a CPU-only DistilBERT classifier for cyber-threat severity."""

from __future__ import annotations

import json
import logging
import random
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch.optim import AdamW
from torch.utils.data import DataLoader
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from .config import ClassifierConfig, ID_TO_LABEL, LABEL_TO_ID
from .dataset import SeverityDataset, load_and_split_dataset
from .evaluate import EvaluationResult, evaluate_model

LOGGER = logging.getLogger(__name__)


def train(config: ClassifierConfig | None = None) -> dict[str, Any]:
    """Fine-tune DistilBERT and save the best available local artifacts.

    Args:
        config: Optional training configuration. Defaults match Sprint 5.

    Returns:
        A serializable training summary with dataset sizes, metrics, and duration.

    Raises:
        FileNotFoundError: If the prepared TECHPULSE dataset is missing.
        ValueError: If valid labels or descriptions are unavailable.
        OSError: If model artifacts cannot be saved.
    """
    training_config = config or ClassifierConfig()
    _set_seed(training_config.random_seed)
    device = torch.device("cpu")
    LOGGER.info("Using device: %s", device)

    split = load_and_split_dataset(
        training_config.dataset_path,
        test_size=training_config.test_size,
        random_seed=training_config.random_seed,
    )
    tokenizer = AutoTokenizer.from_pretrained(training_config.model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        training_config.model_name,
        num_labels=len(LABEL_TO_ID),
        id2label=ID_TO_LABEL,
        label2id=LABEL_TO_ID,
    ).to(device)

    train_dataset = SeverityDataset(split.train, tokenizer, training_config.max_length)
    test_dataset = SeverityDataset(split.test, tokenizer, training_config.max_length)
    train_loader = DataLoader(train_dataset, batch_size=training_config.batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=training_config.batch_size, shuffle=False)
    optimizer = AdamW(model.parameters(), lr=training_config.learning_rate)

    LOGGER.info(
        "Starting CPU training: %d examples, %d epochs, batch size %d",
        len(train_dataset),
        training_config.epochs,
        training_config.batch_size,
    )
    start_time = time.perf_counter()
    for epoch in range(training_config.epochs):
        average_loss = _train_epoch(model, train_loader, optimizer, device)
        LOGGER.info(
            "Epoch %d/%d completed with average loss %.4f",
            epoch + 1,
            training_config.epochs,
            average_loss,
        )

    evaluation = evaluate_model(model, test_loader, device)
    duration_seconds = time.perf_counter() - start_time
    _save_artifacts(model, tokenizer, training_config, evaluation, duration_seconds, split)

    summary = {
        "train_examples": len(train_dataset),
        "test_examples": len(test_dataset),
        "accuracy": evaluation.accuracy,
        "precision": evaluation.precision,
        "recall": evaluation.recall,
        "f1_score": evaluation.f1_score,
        "training_seconds": duration_seconds,
        "confusion_matrix": evaluation.confusion_matrix,
    }
    LOGGER.info("Training completed: %s", json.dumps(summary, indent=2))
    return summary


def _train_epoch(
    model: torch.nn.Module,
    dataloader: DataLoader[dict[str, torch.Tensor]],
    optimizer: AdamW,
    device: torch.device,
) -> float:
    """Run one complete CPU training epoch and return its average loss."""
    model.train()
    total_loss = 0.0

    for batch in dataloader:
        optimizer.zero_grad()
        model_inputs = {key: value.to(device) for key, value in batch.items()}
        loss = model(**model_inputs).loss
        loss.backward()
        optimizer.step()
        total_loss += float(loss.item())

    return total_loss / max(len(dataloader), 1)


def _save_artifacts(
    model: torch.nn.Module,
    tokenizer: Any,
    config: ClassifierConfig,
    evaluation: EvaluationResult,
    duration_seconds: float,
    split: Any,
) -> None:
    """Persist the trained model, tokenizer, and evaluation summary."""
    output_directory = Path(config.model_output_dir)
    output_directory.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(output_directory)
    tokenizer.save_pretrained(output_directory)

    metrics_path = output_directory / "training_metrics.json"
    metrics = evaluation.as_dict() | {
        "train_examples": len(split.train),
        "test_examples": len(split.test),
        "training_seconds": duration_seconds,
        "model_name": config.model_name,
    }
    with metrics_path.open("w", encoding="utf-8") as metrics_file:
        json.dump(metrics, metrics_file, indent=2)


def _set_seed(seed: int) -> None:
    """Set random seeds for repeatable CPU-only training."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    train()
