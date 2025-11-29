"""Complete RAG pipeline combining document loading, embedding, and retrieval."""

from pathlib import Path
from typing import Any

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from loguru import logger

from opi5_max_llm_setup.config.settings import get_settings
from opi5_max_llm_setup.llm.ollama_client import OllamaClient
from opi5_max_llm_setup.rag.document_loader import DocumentLoader
from opi5_max_llm_setup.rag.vector_store import VectorStoreManager

# RAG prompt template
RAG_PROMPT_TEMPLATE = """Use the following context to answer the question.
If you don't know the answer based on the context, say you don't know.

Context:
{context}

Question: {question}

Answer:"""


def _format_docs(docs: list[Document]) -> str:
    """Format documents for the prompt."""
    return "\n\n".join(doc.page_content for doc in docs)


class RAGPipeline:
    """Complete RAG pipeline for document Q&A."""

    def __init__(self) -> None:
        """Initialize RAG pipeline components."""
        self.settings = get_settings()
        self.document_loader = DocumentLoader()
        self.vector_store_manager = VectorStoreManager()
        self._ollama_client: OllamaClient | None = None
        self._rag_chain: Any | None = None

    @property
    def ollama_client(self) -> OllamaClient:
        """Get or create Ollama client."""
        if self._ollama_client is None:
            self._ollama_client = OllamaClient()
        return self._ollama_client

    @property
    def rag_chain(self) -> Any:
        """
        Get or create the RAG chain using LCEL.

        Returns:
            RAG chain
        """
        if self._rag_chain is None:
            retriever = self.vector_store_manager.get_retriever()
            prompt = PromptTemplate.from_template(RAG_PROMPT_TEMPLATE)

            self._rag_chain = (
                {
                    "context": retriever | _format_docs,
                    "question": RunnablePassthrough(),
                }
                | prompt
                | self.ollama_client.llm
                | StrOutputParser()
            )
        return self._rag_chain

    def add_document(self, file_path: Path | str) -> dict[str, Any]:
        """
        Add a single document to the RAG pipeline.

        Args:
            file_path: Path to the document

        Returns:
            Dictionary with processing results
        """
        file_path = Path(file_path)
        logger.info(f"Adding document to RAG pipeline: {file_path}")

        try:
            # Load and split document
            chunks = self.document_loader.load_and_split(file_path)

            # Add to vector store
            ids = self.vector_store_manager.add_documents(chunks)

            # Reset RAG chain to use updated retriever
            self._rag_chain = None

            return {
                "success": True,
                "file_name": file_path.name,
                "chunks_added": len(chunks),
                "document_ids": ids,
            }
        except (ValueError, OSError, RuntimeError) as e:
            logger.error(f"Error adding document: {e}")
            return {
                "success": False,
                "file_name": file_path.name,
                "error": str(e),
            }

    def add_documents_from_directory(
        self, directory_path: Path | str
    ) -> dict[str, Any]:
        """
        Add all documents from a directory.

        Args:
            directory_path: Path to the directory

        Returns:
            Dictionary with processing results
        """
        directory_path = Path(directory_path)
        logger.info(f"Adding documents from directory: {directory_path}")

        try:
            # Load all documents from directory
            chunks = self.document_loader.load_directory(directory_path)

            if not chunks:
                return {
                    "success": True,
                    "directory": str(directory_path),
                    "chunks_added": 0,
                    "message": "No supported documents found",
                }

            # Add to vector store
            ids = self.vector_store_manager.add_documents(chunks)

            # Reset RAG chain
            self._rag_chain = None

            return {
                "success": True,
                "directory": str(directory_path),
                "chunks_added": len(chunks),
                "document_ids": ids,
            }
        except (ValueError, OSError) as e:
            logger.error(f"Error adding documents from directory: {e}")
            return {
                "success": False,
                "directory": str(directory_path),
                "error": str(e),
            }

    def query(self, question: str) -> dict[str, Any]:
        """
        Query the RAG pipeline.

        Args:
            question: Question to ask

        Returns:
            Dictionary with answer and source documents
        """
        logger.info(f"RAG query: {question[:50]}...")

        try:
            # Get answer using LCEL chain
            answer = self.rag_chain.invoke(question)

            # Get source documents separately for display
            source_docs_raw = self.search_similar(question)
            source_docs = [
                {
                    "content": doc.page_content[:500],
                    "metadata": doc.metadata,
                }
                for doc in source_docs_raw
            ]

            return {
                "success": True,
                "answer": answer,
                "sources": source_docs,
            }
        except Exception as e:
            logger.error(f"Error during RAG query: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def search_similar(self, query: str, k: int | None = None) -> list[Document]:
        """
        Search for similar documents without generating an answer.

        Args:
            query: Search query
            k: Number of results

        Returns:
            List of similar documents
        """
        return self.vector_store_manager.similarity_search(query, k=k)

    def get_stats(self) -> dict[str, Any]:
        """
        Get statistics about the RAG pipeline.

        Returns:
            Dictionary with pipeline statistics
        """
        collection_stats = self.vector_store_manager.get_collection_stats()
        ollama_available = self.ollama_client.is_available()

        return {
            "collection": collection_stats,
            "ollama_available": ollama_available,
            "model": self.settings.ollama_model,
            "embedding_model": self.settings.embedding_model,
        }

    def clear_documents(self) -> dict[str, str]:
        """
        Clear all documents from the vector store.

        Returns:
            Status message
        """
        logger.warning("Clearing all documents from RAG pipeline")
        self.vector_store_manager.delete_collection()
        self._rag_chain = None
        return {"status": "Documents cleared successfully"}
