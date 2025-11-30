"""Tests for configuration settings."""

from pathlib import Path

from opi5_max_llm_setup.config.settings import get_settings


class TestSettings:
    """Test settings configuration."""

    def test_default_settings(self) -> None:
        """Test that default settings are loaded correctly."""
        settings = get_settings()
        assert settings.app_name == "opi5-max-llm-setup"
        assert settings.app_version == "0.1.0"

    def test_default_ollama_settings(self) -> None:
        """Test default Ollama settings."""
        settings = get_settings()
        assert settings.ollama_base_url == "http://localhost:11434"
        assert settings.ollama_model == "qwen2.5:3b"
        assert settings.ollama_num_parallel == 1

    def test_default_llm_backend_settings(self) -> None:
        """Test default LLM backend settings."""
        settings = get_settings()
        assert settings.llm_backend == "ollama"
        assert settings.llm_backend in ["ollama", "rkllm"]

    def test_default_rkllm_settings(self) -> None:
        """Test default RKLLM settings."""
        settings = get_settings()
        assert settings.rkllm_model_path == Path("./models/model.rkllm")
        assert settings.rkllm_lib_path == Path("./lib")

    def test_default_embedding_settings(self) -> None:
        """Test default embedding settings."""
        settings = get_settings()
        assert settings.embedding_model == "sentence-transformers/all-MiniLM-L6-v2"
        assert settings.embedding_device == "cpu"

    def test_default_rag_settings(self) -> None:
        """Test default RAG settings."""
        settings = get_settings()
        assert settings.chunk_size == 500
        assert settings.chunk_overlap == 50
        assert settings.retrieval_k == 3

    def test_chroma_persist_directory_is_path(self) -> None:
        """Test that chroma_persist_directory is a Path object."""
        settings = get_settings()
        assert isinstance(settings.chroma_persist_directory, Path)

    def test_api_settings(self) -> None:
        """Test API settings."""
        settings = get_settings()
        assert settings.api_host == "0.0.0.0"
        assert settings.api_port == 8000
