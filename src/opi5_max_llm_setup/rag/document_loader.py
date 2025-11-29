"""Document loading and processing utilities."""

from pathlib import Path
from typing import Any

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader,
)
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger

from opi5_max_llm_setup.config.settings import get_settings


class DocumentLoader:
    """Load and process various document formats for RAG."""

    def __init__(self) -> None:
        """Initialize the document loader with settings."""
        settings = get_settings()
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )

    def load_document(self, file_path: Path | str) -> list[Document]:
        """
        Load a document from file path.

        Args:
            file_path: Path to the document file

        Returns:
            List of Document objects

        Raises:
            ValueError: If file type is not supported
        """
        file_path = Path(file_path)
        suffix = file_path.suffix.lower()

        loader: Any
        if suffix == ".pdf":
            loader = PyPDFLoader(str(file_path))
        elif suffix == ".txt":
            loader = TextLoader(str(file_path))
        elif suffix in [".docx", ".doc"]:
            loader = UnstructuredWordDocumentLoader(str(file_path))
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

        logger.info(f"Loading document: {file_path}")
        documents: list[Document] = loader.load()
        logger.info(f"Loaded {len(documents)} pages/sections from {file_path}")

        return documents

    def split_documents(self, documents: list[Document]) -> list[Document]:
        """
        Split documents into smaller chunks.

        Args:
            documents: List of Document objects

        Returns:
            List of chunked Document objects
        """
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Split into {len(chunks)} chunks")
        return chunks

    def load_and_split(self, file_path: Path | str) -> list[Document]:
        """
        Load a document and split it into chunks.

        Args:
            file_path: Path to the document file

        Returns:
            List of chunked Document objects
        """
        documents = self.load_document(file_path)
        return self.split_documents(documents)

    def load_directory(self, directory_path: Path | str) -> list[Document]:
        """
        Load all supported documents from a directory.

        Args:
            directory_path: Path to the directory

        Returns:
            List of chunked Document objects from all files
        """
        directory_path = Path(directory_path)
        supported_extensions = [".pdf", ".txt", ".docx", ".doc"]

        all_documents: list[Document] = []
        for ext in supported_extensions:
            for file_path in directory_path.glob(f"*{ext}"):
                try:
                    chunks = self.load_and_split(file_path)
                    all_documents.extend(chunks)
                except (ValueError, OSError) as e:
                    logger.error(f"Error loading {file_path}: {e}")

        logger.info(f"Loaded {len(all_documents)} total chunks from {directory_path}")
        return all_documents
