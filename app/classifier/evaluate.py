"""Evaluation utilities for the DistilBERT severity classifier."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import torch
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
from torch.utils.data import DataLoader

from .config import ID_TO_LABEL


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    """Metrics and confusion matrix returned after model evaluation."""

    accuracy: float
    precision: float
    recall: float
    f1_score: float
    confusion_matrix: list[list[int]]

    def as_dict(self) -> dict[str, Any]:
        """Return metrics in a serializable dictionary format."""
        return {
            "accuracy": self.accuracy,
            "precision": self.precision,
            "recall": self.recall,
            "f1_score": self.f1_score,
            "confusion_matrix": self.confusion_matrix,
            "labels": [ID_TO_LABEL[index] for index in sorted(ID_TO_LABEL)],
        }


def evaluate_model(
    model: torch.nn.Module,
    dataloader: DataLoader[dict[str, torch.Tensor]],
    device: torch.device,
) -> EvaluationResult:
    """Evaluate a classifier and calculate weighted classification metrics.

    Args:
        model: Fine-tuned sequence-classification model.
        dataloader: Test dataloader producing tokenized batches.
        device: CPU device on which inference is executed.

    Returns:
        Accuracy, weighted precision/recall/F1, and a fixed-label confusion matrix.
    """
    model.eval()
    predictions: list[int] = []
    labels: list[int] = []

    with torch.no_grad():
        for batch in dataloader:
            model_inputs = {
                key: value.to(device)
                for key, value in batch.items()
                if key != "labels"
            }
            logits = model(**model_inputs).logits
            predictions.extend(torch.argmax(logits, dim=1).cpu().tolist())
            labels.extend(batch["labels"].cpu().tolist())

    precision, recall, f1_score, _ = precision_recall_fscore_support(
        labels,
        predictions,
        average="weighted",
        zero_division=0,
    )
    label_ids = sorted(ID_TO_LABEL)
    matrix = confusion_matrix(labels, predictions, labels=label_ids)
    return EvaluationResult(
        accuracy=float(accuracy_score(labels, predictions)),
        precision=float(precision),
        recall=float(recall),
        f1_score=float(f1_score),
        confusion_matrix=np.asarray(matrix).astype(int).tolist(),
    )
