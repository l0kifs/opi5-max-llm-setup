"""Tests for API routes."""

from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from opi5_max_llm_setup.api.routes import get_ollama, get_rkllm
from opi5_max_llm_setup.api.server import create_app


@pytest.fixture
def app() -> FastAPI:
    """Create test app."""
    return create_app()


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_ollama_client() -> MagicMock:
    """Create a mock OllamaClient."""
    mock = MagicMock()
    mock.is_available.return_value = True
    mock.generate.return_value = "Hello! I'm a helpful assistant."
    mock.list_models.return_value = [
        {"name": "qwen2.5:3b", "size": 2000000000, "modified_at": "2024-01-01"}
    ]
    mock.get_model_info.return_value = {"name": "qwen2.5:3b", "size": 2000000000}
    return mock


@pytest.fixture
def mock_rkllm_client() -> MagicMock:
    """Create a mock RKLLMClient."""
    mock = MagicMock()
    mock.is_available.return_value = False  # Default to not available
    mock.generate.return_value = "Hello from NPU!"
    mock.list_models.return_value = []
    mock.get_model_info.return_value = None
    return mock


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client: TestClient) -> None:
        """Test health check returns expected structure."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "llm_backend" in data
        assert "llm_available" in data
        assert "version" in data
        assert data["status"] == "healthy"
        assert data["llm_backend"] in ["ollama", "rkllm"]


class TestRootEndpoint:
    """Test root endpoint."""

    def test_root(self, client: TestClient) -> None:
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data
        assert data["docs"] == "/docs"


class TestModelsEndpoint:
    """Test models endpoint."""

    def test_list_models_with_mock(
        self, app: FastAPI, mock_ollama_client: MagicMock, mock_rkllm_client: MagicMock
    ) -> None:
        """Test list models returns expected structure with mocked client."""
        # Clear caches and override dependencies
        get_ollama.cache_clear()
        get_rkllm.cache_clear()

        app.dependency_overrides[get_ollama] = lambda: mock_ollama_client
        app.dependency_overrides[get_rkllm] = lambda: mock_rkllm_client

        try:
            client = TestClient(app)
            response = client.get("/api/v1/models")
            assert response.status_code == 200

            data = response.json()
            assert "success" in data
            assert data["success"] is True
            assert "models" in data
            assert len(data["models"]) == 1
            assert data["models"][0]["name"] == "qwen2.5:3b"
        finally:
            app.dependency_overrides.clear()
            get_ollama.cache_clear()
            get_rkllm.cache_clear()

    def test_list_models_unavailable(
        self, app: FastAPI, mock_ollama_client: MagicMock, mock_rkllm_client: MagicMock
    ) -> None:
        """Test list models when backend is unavailable."""
        mock_ollama_client.is_available.return_value = False
        get_ollama.cache_clear()
        get_rkllm.cache_clear()

        app.dependency_overrides[get_ollama] = lambda: mock_ollama_client
        app.dependency_overrides[get_rkllm] = lambda: mock_rkllm_client

        try:
            client = TestClient(app)
            response = client.get("/api/v1/models")
            assert response.status_code == 200

            data = response.json()
            assert "success" in data
            assert data["success"] is False
            assert "error" in data
        finally:
            app.dependency_overrides.clear()
            get_ollama.cache_clear()
            get_rkllm.cache_clear()


class TestChatEndpoint:
    """Test chat endpoint."""

    def test_chat_success_with_mock(
        self,
        app: FastAPI,
        mock_ollama_client: MagicMock,
        mock_rkllm_client: MagicMock,
    ) -> None:
        """Test chat returns expected structure with mocked clients."""
        get_ollama.cache_clear()
        get_rkllm.cache_clear()

        app.dependency_overrides[get_ollama] = lambda: mock_ollama_client
        app.dependency_overrides[get_rkllm] = lambda: mock_rkllm_client

        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/chat",
                json={"prompt": "Hello"},
            )
            assert response.status_code == 200

            data = response.json()
            assert "success" in data
            assert data["success"] is True
            assert "response" in data
            assert data["response"] == "Hello! I'm a helpful assistant."
        finally:
            app.dependency_overrides.clear()
            get_ollama.cache_clear()
            get_rkllm.cache_clear()

    def test_chat_backend_unavailable(
        self,
        app: FastAPI,
        mock_ollama_client: MagicMock,
        mock_rkllm_client: MagicMock,
    ) -> None:
        """Test chat when backend is unavailable."""
        mock_ollama_client.is_available.return_value = False
        get_ollama.cache_clear()
        get_rkllm.cache_clear()

        app.dependency_overrides[get_ollama] = lambda: mock_ollama_client
        app.dependency_overrides[get_rkllm] = lambda: mock_rkllm_client

        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/chat",
                json={"prompt": "Hello"},
            )
            assert response.status_code == 200

            data = response.json()
            assert "success" in data
            assert data["success"] is False
            assert "error" in data
        finally:
            app.dependency_overrides.clear()
            get_ollama.cache_clear()
            get_rkllm.cache_clear()


# Note: Document upload tests require HuggingFace model downloads
# which may not be available in all test environments.
# These tests should be run in an environment with network access.
