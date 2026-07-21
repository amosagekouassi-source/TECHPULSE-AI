"""Sentence Transformer embeddings encoder for TECHPULSE-AI."""

from __future__ import annotations

import logging
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

LOGGER = logging.getLogger(__name__)


class TextEmbedder:
    """Encoder for generating dense vector embeddings using all-MiniLM-L6-v2."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        """Initialize the sentence transformer model.

        Args:
            model_name: Hugging Face model identifier for sentence embeddings.
        """
        LOGGER.info("Loading embedding model: %s", model_name)
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        if hasattr(self.model, "get_embedding_dimension"):
            self.dimension = self.model.get_embedding_dimension()
        else:
            self.dimension = self.model.get_sentence_embedding_dimension()

    def embed_texts(
        self,
        texts: List[str],
        batch_size: int = 64,
        show_progress_bar: bool = False,
    ) -> np.ndarray:
        """Embed a list of text strings into a numpy matrix.

        Args:
            texts: List of text descriptions or queries.
            batch_size: Batch size for encoding.
            show_progress_bar: Whether to display progress.

        Returns:
            Numpy array of shape (N, dimension) with float32 embeddings.
        """
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress_bar,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embeddings.astype(np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        """Embed a single query string into a 2D numpy matrix of shape (1, dimension).

        Args:
            query: Input user query.

        Returns:
            Numpy array of shape (1, dimension).
        """
        return self.embed_texts([query], batch_size=1, show_progress_bar=False)
