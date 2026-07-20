"""Predict cyber-threat severity with a local or Hugging Face DistilBERT model."""

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
        model_reference: Local model directory or Hugging Face Hub repository ID.
        max_length: Maximum number of tokens accepted from an input description.
    """

    def __init__(
        self,
        model_reference: Path | str | None = None,
        max_length: int = 256,
    ) -> None:
        """Load the specified model on the best available local device.

        A repository ID such as ``account/techpulse-distilbert-severity`` is
        downloaded from Hugging Face Hub and cached by Transformers.
        """
        configuration = ClassifierConfig()
        use_default_local_model = (
            model_reference is None and configuration.huggingface_model_id is None
        )
        resolved_reference = (
            model_reference
            or configuration.huggingface_model_id
            or configuration.model_output_dir
        )
        self._validate_model_reference(resolved_reference, use_default_local_model)
        self._model_reference = str(resolved_reference)

        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._max_length = max_length
        self._tokenizer = AutoTokenizer.from_pretrained(self._model_reference)
        self._model = AutoModelForSequenceClassification.from_pretrained(
            self._model_reference
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

    @staticmethod
    def _validate_model_reference(
        model_reference: Path | str,
        require_local_directory: bool,
    ) -> None:
        """Validate local paths while allowing Hugging Face repository identifiers."""
        path = Path(model_reference)
        is_explicit_local_path = (
            path.is_absolute()
            or str(model_reference).startswith(".")
            or require_local_directory
        )
        if is_explicit_local_path and not path.is_dir():
            raise FileNotFoundError(f"Local model directory not found: {path}")


def main() -> int:
    """Run one severity prediction from the command line."""
    argument_parser = argparse.ArgumentParser(
        description="Predict cybersecurity severity with DistilBERT."
    )
    argument_parser.add_argument("text", help="Security description to classify")
    argument_parser.add_argument(
        "--model-reference",
        default=None,
        help="Local model directory or Hugging Face Hub repository ID",
    )
    arguments = argument_parser.parse_args()

    result: dict[str, Any] = SeverityPredictor(arguments.model_reference).predict(
        arguments.text
    )
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
