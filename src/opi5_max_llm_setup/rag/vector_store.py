"""Vector store management using ChromaDB."""

from pathlib import Path
from typing import Any

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from loguru import logger

from opi5_max_llm_setup.config.settings import get_settings
from opi5_max_llm_setup.rag.embeddings import EmbeddingManager


class VectorStoreManager:
    """Manage ChromaDB vector store for document retrieval."""

    def __init__(self) -> None:
        """Initialize vector store manager."""
        settings = get_settings()
        self.persist_directory = Path(settings.chroma_persist_directory)
        self.collection_name = settings.chroma_collection_name
        self.retrieval_k = settings.retrieval_k

        # Ensure directory exists
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize embedding manager
        self.embedding_manager = EmbeddingManager()

        # Initialize or load vector store
        self._vector_store: Chroma | None = None

    @property
    def vector_store(self) -> Chroma:
        """
        Get or create the vector store.

        Returns:
            Chroma vector store instance
        """
        if self._vector_store is None:
            logger.info(f"Initializing ChromaDB at {self.persist_directory}")
            self._vector_store = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embedding_manager.embeddings,
                persist_directory=str(self.persist_directory),
            )
        return self._vector_store

    def add_documents(self, documents: list[Document]) -> list[str]:
        """
        Add documents to the vector store.

        Args:
            documents: List of Document objects to add

        Returns:
            List of document IDs
        """
        if not documents:
            logger.warning("No documents to add")
            return []

        logger.info(f"Adding {len(documents)} documents to vector store")
        ids = self.vector_store.add_documents(documents)
        logger.info(f"Successfully added {len(ids)} documents")
        return ids

    def similarity_search(self, query: str, k: int | None = None) -> list[Document]:
        """
        Search for similar documents.

        Args:
            query: Search query text
            k: Number of results to return (defaults to settings.retrieval_k)

        Returns:
            List of similar Document objects
        """
        k = k or self.retrieval_k
        logger.debug(f"Searching for: {query[:50]}... (k={k})")
        results = self.vector_store.similarity_search(query, k=k)
        logger.debug(f"Found {len(results)} results")
        return results

    def similarity_search_with_score(
        self, query: str, k: int | None = None
    ) -> list[tuple[Document, float]]:
        """
        Search for similar documents with relevance scores.

        Args:
            query: Search query text
            k: Number of results to return

        Returns:
            List of (Document, score) tuples
        """
        k = k or self.retrieval_k
        return self.vector_store.similarity_search_with_score(query, k=k)

    def delete_collection(self) -> None:
        """Delete the entire collection."""
        logger.warning(f"Deleting collection: {self.collection_name}")
        self.vector_store.delete_collection()
        self._vector_store = None

    def get_collection_stats(self) -> dict[str, Any]:
        """
        Get statistics about the collection.

        Returns:
            Dictionary with collection statistics
        """
        collection = self.vector_store._collection
        return {
            "name": self.collection_name,
            "count": collection.count(),
        }

    def get_retriever(self, k: int | None = None) -> VectorStoreRetriever:
        """
        Get a retriever for the vector store.

        Args:
            k: Number of documents to retrieve

        Returns:
            Retriever object
        """
        k = k or self.retrieval_k
        return self.vector_store.as_retriever(search_kwargs={"k": k})
