"""Train a CPU-only DistilBERT classifier for cyber-threat severity."""

from __future__ import annotations

import argparse
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
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
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
    """Persist the trained model, tokenizer, evaluation summary, and optionally push to Hugging Face Hub."""
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

    if config.push_to_hub:
        if not config.hub_model_id:
            raise ValueError(
                "hub_model_id is required when push_to_hub is enabled"
            )
        LOGGER.info(
            "Pushing model and tokenizer to Hugging Face Hub repository %s",
            config.hub_model_id,
        )
        model.push_to_hub(config.hub_model_id, use_auth_token=True)
        tokenizer.push_to_hub(config.hub_model_id, use_auth_token=True)


def _set_seed(seed: int) -> None:
    """Set random seeds for repeatable CPU-only training."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def main() -> int:
    """Train the classifier from the command line and optionally push artifacts to Hugging Face Hub."""
    argument_parser = argparse.ArgumentParser(
        description=(
            "Train DistilBERT for TECHPULSE-AI and optionally push the trained model to Hugging Face Hub."
        )
    )
    argument_parser.add_argument(
        "--dataset-path",
        type=Path,
        default=ClassifierConfig().dataset_path,
        help="Path to the prepared Parquet dataset.",
    )
    argument_parser.add_argument(
        "--model-output-dir",
        type=Path,
        default=ClassifierConfig().model_output_dir,
        help="Directory where the trained model artifacts will be saved.",
    )
    argument_parser.add_argument(
        "--model-name",
        default=ClassifierConfig().model_name,
        help="Hugging Face base model identifier to fine-tune.",
    )
    argument_parser.add_argument(
        "--hub-model-id",
        default=ClassifierConfig().hub_model_id,
        help="Hugging Face Hub repository identifier for pushing the model.",
    )
    argument_parser.add_argument(
        "--push-to-hub",
        action="store_true",
        help="Push the trained model and tokenizer to Hugging Face Hub.",
    )
    argument_parser.add_argument(
        "--epochs",
        type=int,
        default=ClassifierConfig().epochs,
        help="Number of training epochs.",
    )
    argument_parser.add_argument(
        "--batch-size",
        type=int,
        default=ClassifierConfig().batch_size,
        help="Batch size used during training.",
    )
    argument_parser.add_argument(
        "--learning-rate",
        type=float,
        default=ClassifierConfig().learning_rate,
        help="Learning rate for the optimizer.",
    )
    argument_parser.add_argument(
        "--max-length",
        type=int,
        default=ClassifierConfig().max_length,
        help="Maximum tokenizer sequence length.",
    )
    argument_parser.add_argument(
        "--test-size",
        type=float,
        default=ClassifierConfig().test_size,
        help="Fraction of the dataset reserved for testing.",
    )
    argument_parser.add_argument(
        "--random-seed",
        type=int,
        default=ClassifierConfig().random_seed,
        help="Random seed for repeatability.",
    )

    arguments = argument_parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    config = ClassifierConfig(
        dataset_path=arguments.dataset_path,
        model_output_dir=arguments.model_output_dir,
        model_name=arguments.model_name,
        hub_model_id=arguments.hub_model_id,
        push_to_hub=arguments.push_to_hub,
        epochs=arguments.epochs,
        batch_size=arguments.batch_size,
        learning_rate=arguments.learning_rate,
        max_length=arguments.max_length,
        test_size=arguments.test_size,
        random_seed=arguments.random_seed,
    )

    try:
        train(config)
        return 0
    except Exception as error:
        LOGGER.exception("Training failed: %s", error)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
