"""Predict cyber-threat severity with a fine-tuned DistilBERT model."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from .config import ClassifierConfig, ID_TO_LABEL


class SeverityPredictor:
    """Load a saved severity classifier and predict from free text.

    Args:
        model_source: Local directory or Hugging Face Hub model identifier.
        max_length: Maximum number of tokens accepted from an input description.
    """

    def __init__(
        self,
        model_source: Path | str | None = None,
        max_length: int = 256,
    ) -> None:
        """Load the saved model on CPU only.

        Raises:
            FileNotFoundError: If the configured model source does not exist locally.
        """
        self._device = torch.device("cpu")
        self._max_length = max_length
        self._model_source = model_source or ClassifierConfig().model_output_dir
        if isinstance(self._model_source, (Path, str)):
            self._model_source = Path(self._model_source)

        if isinstance(self._model_source, Path) and self._model_source.exists():
            model_source = self._model_source
        else:
            model_source = str(self._model_source)

        self._tokenizer = AutoTokenizer.from_pretrained(model_source)
        self._model = AutoModelForSequenceClassification.from_pretrained(
            model_source
        ).to(self._device)
        self._model.eval()

    def predict(self, text: str) -> dict[str, str | float]:
        """Predict severity and confidence from a free-text security description.

        Args:
            text: Security-event or vulnerability description.

        Returns:
            A dictionary containing the predicted severity and confidence score.

        Raises:
            ValueError: If ``text`` is empty or contains only whitespace.
        """
        if not isinstance(text, str) or not text.strip():
            raise ValueError("text must be a non-empty string")

        encoded = self._tokenizer(
            text.strip(),
            truncation=True,
            max_length=self._max_length,
            return_tensors="pt",
        )
        encoded = {key: value.to(self._device) for key, value in encoded.items()}

        with torch.no_grad():
            logits = self._model(**encoded).logits
            probabilities = torch.softmax(logits, dim=1)[0]

        label_id = int(torch.argmax(probabilities).item())
        label = self._model.config.id2label.get(label_id, ID_TO_LABEL[label_id])
        return {
            "severity": str(label),
            "confidence": round(float(probabilities[label_id].item()), 4),
        }


def main() -> int:
    """Run one severity prediction from the command line."""
    argument_parser = argparse.ArgumentParser(
        description="Predict cybersecurity severity with DistilBERT."
    )
    argument_parser.add_argument("text", help="Security description to classify")
    argument_parser.add_argument(
        "--model-source",
        default=ClassifierConfig().model_output_dir,
        help=(
            "Local model directory or Hugging Face Hub model identifier "
            "for the trained classifier"
        ),
    )
    arguments = argument_parser.parse_args()

    result: dict[str, Any] = SeverityPredictor(arguments.model_source).predict(
        arguments.text
    )
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


