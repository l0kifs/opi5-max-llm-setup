"""Tests for API routes."""

import pytest
from fastapi.testclient import TestClient

from opi5_max_llm_setup.api.server import create_app


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    app = create_app()
    return TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client: TestClient) -> None:
        """Test health check returns expected structure."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "ollama_available" in data
        assert "version" in data
        assert data["status"] == "healthy"


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

    def test_list_models(self, client: TestClient) -> None:
        """Test list models returns expected structure."""
        response = client.get("/api/v1/models")
        # Response structure should be valid even if Ollama is not running
        assert response.status_code == 200

        data = response.json()
        assert "success" in data


class TestChatEndpoint:
    """Test chat endpoint."""

    def test_chat_structure(self, client: TestClient) -> None:
        """Test chat returns expected structure."""
        response = client.post(
            "/api/v1/chat",
            json={"prompt": "Hello"},
        )
        # Will fail if Ollama not running, but structure should be valid
        assert response.status_code == 200

        data = response.json()
        assert "success" in data


class TestDocumentsEndpoint:
    """Test documents endpoints."""

    def test_upload_invalid_file_type(self, client: TestClient) -> None:
        """Test upload rejects invalid file types."""
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("test.exe", b"content", "application/octet-stream")},
        )
        assert response.status_code == 400
        data = response.json()
        assert "Unsupported file type" in data.get("detail", "")
