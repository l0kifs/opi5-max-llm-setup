from enum import Enum
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMBackend(str, Enum):
    """Supported LLM backends."""

    OLLAMA = "ollama"
    RKLLM = "rkllm"


class Settings(BaseSettings):
    """Main application settings"""

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application settings
    app_name: str = Field(default="opi5-max-llm-setup", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")

    # Logging settings
    logging_level: str = Field(default="INFO", description="Logging level")
    logging_format: str = Field(
        default=(
            "{time:YYYY-MM-DD HH:mm:ss} | {extra[app]} v{extra[version]} | "
            "{level: <8} | {name}:{function}:{line} - {message} | {extra}"
        ),
        description="Console log format",
    )

    # API settings
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")

    # LLM Backend settings
    llm_backend: LLMBackend = Field(
        default=LLMBackend.RKLLM,
        description="LLM backend to use: 'rkllm' (NPU, default) or 'ollama' (CPU)",
    )

    # Ollama settings
    ollama_base_url: str = Field(
        default="http://localhost:11434", description="Ollama server URL"
    )
    ollama_model: str = Field(
        default="qwen2.5:3b", description="Default Ollama model for inference"
    )
    ollama_num_parallel: int = Field(
        default=1, description="Number of parallel Ollama requests"
    )
    ollama_max_loaded_models: int = Field(
        default=1, description="Maximum number of loaded Ollama models"
    )

    # RKLLM/RKLLama settings (NPU acceleration via RKLLama server)
    rkllm_base_url: str = Field(
        default="http://localhost:8080",
        description="RKLLama server URL (Ollama-compatible API for RK3588 NPU)",
    )
    rkllm_model: str = Field(
        default="qwen2.5:1b",
        description="Default RKLLama model for NPU inference (qwen2.5:1b = 1.5B ~15tok/s, qwen2.5 = 3B ~8tok/s)",
    )

    # Embedding settings
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Embedding model for RAG",
    )
    embedding_device: str = Field(
        default="cpu", description="Device for embedding model (cpu/cuda)"
    )

    # Vector database settings
    chroma_persist_directory: Path = Field(
        default=Path("./data/chroma_db"),
        description="ChromaDB persistence directory",
    )
    chroma_collection_name: str = Field(
        default="documents", description="ChromaDB collection name"
    )

    # RAG settings
    chunk_size: int = Field(default=500, description="Text chunk size for splitting")
    chunk_overlap: int = Field(default=50, description="Overlap between text chunks")
    retrieval_k: int = Field(
        default=3, description="Number of documents to retrieve for RAG"
    )

    # Document upload settings
    upload_directory: Path = Field(
        default=Path("./data/uploads"),
        description="Directory for uploaded documents",
    )
    max_upload_size_mb: int = Field(
        default=50, description="Maximum upload file size in MB"
    )


@lru_cache
def get_settings() -> Settings:
    """Retrieve application settings (cached for performance)."""
    return Settings()
