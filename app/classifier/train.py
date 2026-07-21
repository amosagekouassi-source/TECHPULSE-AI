"""Train a DistilBERT classifier for cyber-threat severity."""

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
    """Fine-tune DistilBERT and optionally publish it to Hugging Face Hub.

    The selected device defaults to CUDA when available (for example, in Google
    Colab) and otherwise falls back to CPU for local execution.

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
    device = _resolve_device(training_config.device)
    LOGGER.info("Using device: %s", device)

    split = load_and_split_dataset(
        training_config.dataset_path,
        test_size=training_config.test_size,
        random_seed=training_config.random_seed,
        sample_size=training_config.sample_size,
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
    use_pin_memory = device.type == "cuda"
    train_loader = DataLoader(
        train_dataset,
        batch_size=training_config.batch_size,
        shuffle=True,
        pin_memory=use_pin_memory,
    )
    test_loader = DataLoader(
        test_dataset,
        batch_size=training_config.batch_size,
        shuffle=False,
        pin_memory=use_pin_memory,
    )
    optimizer = AdamW(model.parameters(), lr=training_config.learning_rate)

    LOGGER.info(
        "Starting training: %d examples, %d epochs, batch size %d, grad accum %d",
        len(train_dataset),
        training_config.epochs,
        training_config.batch_size,
        training_config.gradient_accumulation_steps,
    )
    start_time = time.perf_counter()
    for epoch in range(training_config.epochs):
        average_loss = _train_epoch(
            model,
            train_loader,
            optimizer,
            device,
            gradient_accumulation_steps=training_config.gradient_accumulation_steps,
        )
        LOGGER.info(
            "Epoch %d/%d completed with average loss %.4f",
            epoch + 1,
            training_config.epochs,
            average_loss,
        )

    evaluation = evaluate_model(model, test_loader, device)
    duration_seconds = time.perf_counter() - start_time
    _save_artifacts(model, tokenizer, training_config, evaluation, duration_seconds, split)
    _publish_model(model, tokenizer, training_config)

    summary = {
        "train_examples": len(train_dataset),
        "test_examples": len(test_dataset),
        "accuracy": evaluation.accuracy,
        "precision": evaluation.precision,
        "recall": evaluation.recall,
        "f1_score": evaluation.f1_score,
        "training_seconds": duration_seconds,
        "device": str(device),
        "huggingface_model_id": training_config.huggingface_model_id,
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
    """Run one complete training epoch and return its average loss."""
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
    """Persist the trained model, tokenizer, and evaluation summary locally."""
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


def _publish_model(
    model: Any,
    tokenizer: Any,
    config: ClassifierConfig,
) -> None:
    """Upload model artifacts when a Hugging Face repository is configured.

    Authentication must be established before calling this function, for example
    with ``huggingface_hub.login()`` in a Google Colab notebook.
    """
    if not config.huggingface_model_id:
        LOGGER.info("No HF_MODEL_ID configured; skipping Hugging Face Hub upload")
        return

    LOGGER.info("Publishing model to Hugging Face Hub: %s", config.huggingface_model_id)
    model.push_to_hub(
        config.huggingface_model_id,
        private=config.huggingface_private,
    )
    tokenizer.push_to_hub(
        config.huggingface_model_id,
        private=config.huggingface_private,
    )


def _resolve_device(requested_device: str) -> torch.device:
    """Resolve an explicit device or select CUDA automatically when available."""
    normalized_device = requested_device.strip().lower()
    if normalized_device == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if normalized_device == "cuda" and not torch.cuda.is_available():
        raise ValueError("CUDA was requested but is not available")
    if normalized_device not in {"cpu", "cuda"}:
        raise ValueError("device must be 'auto', 'cpu', or 'cuda'")
    return torch.device(normalized_device)


def _set_seed(seed: int) -> None:
    """Set random seeds for repeatable training."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    train()
