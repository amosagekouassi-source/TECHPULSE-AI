"""Sentence Transformer embeddings encoder for TECHPULSE-AI.

Memory-optimized: SentenceTransformer is lazy-loaded on first use only,
so torch (~400MB) and transformers (~200MB) are NOT loaded at server startup.
This keeps Render free-tier (512MB) usage within safe limits.
"""

from __future__ import annotations

import logging
from typing import List, Optional

import numpy as np

LOGGER = logging.getLogger(__name__)

# Global singleton — loaded once on first call, None until then
_MODEL_CACHE: Optional[object] = None


def _get_model(model_name: str = "all-MiniLM-L6-v2"):
    """Return cached SentenceTransformer instance, loading it on first call."""
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        LOGGER.info("Lazy-loading embedding model: %s (first request only)", model_name)
        from sentence_transformers import SentenceTransformer  # noqa: PLC0415
        _MODEL_CACHE = SentenceTransformer(model_name)
        LOGGER.info("Embedding model loaded successfully.")
    return _MODEL_CACHE


class TextEmbedder:
    """Encoder for generating dense vector embeddings using all-MiniLM-L6-v2."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        """Store model name only — actual model loaded on first use.

        Args:
            model_name: Hugging Face model identifier for sentence embeddings.
        """
        self.model_name = model_name
        self._dimension: Optional[int] = None  # resolved lazily

    @property
    def model(self):
        """Lazily return the loaded SentenceTransformer model."""
        return _get_model(self.model_name)

    @property
    def dimension(self) -> int:
        if self._dimension is None:
            m = self.model
            if hasattr(m, "get_embedding_dimension"):
                self._dimension = m.get_embedding_dimension()
            else:
                self._dimension = m.get_sentence_embedding_dimension()
        return self._dimension

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
