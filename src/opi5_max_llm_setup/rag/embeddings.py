"""Embedding management for RAG pipeline."""

from typing import Any

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings
from loguru import logger

from opi5_max_llm_setup.config.settings import get_settings


class EmbeddingsNotInitializedError(RuntimeError):
    """Raised when embeddings are accessed before initialization."""

    def __init__(self) -> None:
        """Initialize the error with a default message."""
        super().__init__("Embeddings not initialized")


class EmbeddingManager:
    """Manage embedding model for document vectorization."""

    _instance: "EmbeddingManager | None" = None
    _embeddings: Embeddings | None = None

    def __new__(cls) -> "EmbeddingManager":
        """Singleton pattern to reuse embedding model."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize embedding manager (singleton, runs once)."""
        if self._embeddings is not None:
            return

        settings = get_settings()
        self.model_name = settings.embedding_model
        self.device = settings.embedding_device

        logger.info(f"Initializing embedding model: {self.model_name}")
        self._embeddings = self._create_embeddings()
        logger.info("Embedding model initialized successfully")

    def _create_embeddings(self) -> Embeddings:
        """
        Create the embeddings model.

        Returns:
            HuggingFace embeddings model
        """
        model_kwargs: dict[str, Any] = {"device": self.device}
        encode_kwargs: dict[str, Any] = {"normalize_embeddings": True}

        return HuggingFaceEmbeddings(
            model_name=self.model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs,
        )

    @property
    def embeddings(self) -> Embeddings:
        """
        Get the embeddings model.

        Returns:
            Embeddings model instance

        Raises:
            EmbeddingsNotInitializedError: If embeddings are not initialized
        """
        if self._embeddings is None:
            raise EmbeddingsNotInitializedError
        return self._embeddings

    def embed_query(self, text: str) -> list[float]:
        """
        Embed a single query text.

        Args:
            text: Query text to embed

        Returns:
            List of embedding floats
        """
        return self.embeddings.embed_query(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Embed multiple documents.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        return self.embeddings.embed_documents(texts)
