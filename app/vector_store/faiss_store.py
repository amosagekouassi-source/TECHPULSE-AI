"""FAISS vector store for semantic vulnerability search in TECHPULSE-AI."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import faiss
import numpy as np
import pandas as pd

from app.embeddings.encoder import TextEmbedder

LOGGER = logging.getLogger(__name__)


class FAISSVectorStore:
    """FAISS index manager for vulnerability and incident semantic search."""

    def __init__(
        self,
        index_dir: Path | str = Path("models/vector_store"),
        embedder: Optional[TextEmbedder] = None,
    ) -> None:
        """Initialize FAISS vector store.

        Args:
            index_dir: Directory where index and metadata are saved/loaded.
            embedder: Optional TextEmbedder instance.
        """
        self.index_dir = Path(index_dir)
        self.embedder = embedder or TextEmbedder()
        self.index: Optional[faiss.Index] = None
        self.metadata: Optional[pd.DataFrame] = None
        self.index_file = self.index_dir / "faiss_index.bin"
        self.metadata_file = self.index_dir / "metadata.parquet"

    def build_from_parquet(
        self,
        parquet_path: Path | str = Path("data/processed/techpulse_dataset.parquet"),
        max_samples: Optional[int] = 20000,
        batch_size: int = 256,
    ) -> None:
        """Build FAISS vector index from TECHPULSE parquet dataset.

        Args:
            parquet_path: Path to dataset parquet file.
            max_samples: Optional limit on rows to index for rapid Demo Day build.
            batch_size: Embedding batch size.
        """
        path = Path(parquet_path)
        if not path.is_file():
            raise FileNotFoundError(f"Parquet dataset not found at {path}")

        LOGGER.info("Reading parquet dataset from %s", path)
        df = pd.read_parquet(path)

        # Filter rows with valid descriptions
        df = df[df["description"].notna() & df["description"].str.strip().ne("")].copy()
        if max_samples and len(df) > max_samples:
            LOGGER.info("Subsampling %d records for vector index", max_samples)
            df = df.sample(n=max_samples, random_state=42).reset_index(drop=True)
        else:
            df = df.reset_index(drop=True)

        descriptions = df["description"].tolist()
        LOGGER.info("Generating embeddings for %d descriptions...", len(descriptions))
        embeddings = self.embedder.embed_texts(descriptions, batch_size=batch_size, show_progress_bar=True)

        dimension = embeddings.shape[1]
        LOGGER.info("Building FAISS Inner Product (Cosine) index (dim=%d)...", dimension)
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings)
        self.metadata = df

        self.save()
        LOGGER.info("FAISS vector store built and saved successfully!")

    def save(self) -> None:
        """Save FAISS index and metadata dataframe to index_dir."""
        self.index_dir.mkdir(parents=True, exist_ok=True)
        if self.index is not None:
            faiss.write_index(self.index, str(self.index_file))
        if self.metadata is not None:
            self.metadata.to_parquet(self.metadata_file, index=False)
        LOGGER.info("Vector store saved to %s", self.index_dir)

    def load(self) -> bool:
        """Load prebuilt FAISS index and metadata if available.

        Returns:
            True if loaded successfully, False otherwise.
        """
        if self.index_file.is_file() and self.metadata_file.is_file():
            LOGGER.info("Loading prebuilt FAISS index from %s", self.index_dir)
            self.index = faiss.read_index(str(self.index_file))
            self.metadata = pd.read_parquet(self.metadata_file)
            return True
        return False

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Perform semantic search for top k matching vulnerabilities.

        Args:
            query: Natural language query description.
            k: Number of nearest neighbors to retrieve.

        Returns:
            List of matching records with similarity scores.
        """
        if self.index is None or self.metadata is None:
            if not self.load():
                raise RuntimeError("FAISS index is not built or loaded.")

        query_vec = self.embedder.embed_query(query)
        scores, indices = self.index.search(query_vec, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            row = self.metadata.iloc[idx].to_dict()
            row["similarity_score"] = float(score)
            results.append(row)

        return results
