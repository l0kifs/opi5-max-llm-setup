"""Ollama client for LLM inference."""

from typing import Any

import httpx
from langchain_core.language_models import BaseLLM
from langchain_ollama import OllamaLLM
from loguru import logger

from opi5_max_llm_setup.config.settings import get_settings


class OllamaClient:
    """Client for Ollama LLM server."""

    _instance: "OllamaClient | None" = None
    _llm: BaseLLM | None = None

    def __new__(cls) -> "OllamaClient":
        """Singleton pattern to reuse LLM instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize Ollama client."""
        if self._llm is not None:
            return

        settings = get_settings()
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model

        logger.info(f"Initializing Ollama client: {self.base_url}")
        self._llm = self._create_llm()

    def _create_llm(self) -> BaseLLM:
        """
        Create the Ollama LLM instance.

        Returns:
            Ollama LLM instance
        """
        return OllamaLLM(
            model=self.model,
            base_url=self.base_url,
        )

    @property
    def llm(self) -> BaseLLM:
        """
        Get the LLM instance.

        Returns:
            LLM instance

        Raises:
            RuntimeError: If LLM is not initialized
        """
        if self._llm is None:
            raise RuntimeError("LLM not initialized")
        return self._llm

    def generate(self, prompt: str) -> str:
        """
        Generate a response from the LLM.

        Args:
            prompt: Input prompt

        Returns:
            Generated response text
        """
        logger.debug(f"Generating response for prompt: {prompt[:50]}...")
        response = self.llm.invoke(prompt)
        return str(response)

    def is_available(self) -> bool:
        """
        Check if Ollama server is available.

        Returns:
            True if server is reachable
        """
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except httpx.RequestError:
            return False

    def list_models(self) -> list[dict[str, Any]]:
        """
        List available models from Ollama.

        Returns:
            List of model information dictionaries
        """
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    return list(data.get("models", []))
        except httpx.RequestError as e:
            logger.error(f"Error listing models: {e}")
        return []

    def pull_model(self, model_name: str) -> bool:
        """
        Pull a model from Ollama registry.

        Args:
            model_name: Name of the model to pull

        Returns:
            True if successful
        """
        try:
            with httpx.Client(timeout=300.0) as client:
                response = client.post(
                    f"{self.base_url}/api/pull",
                    json={"name": model_name},
                )
                return response.status_code == 200
        except httpx.RequestError as e:
            logger.error(f"Error pulling model: {e}")
            return False

    def get_model_info(self, model_name: str | None = None) -> dict[str, Any] | None:
        """
        Get information about a specific model.

        Args:
            model_name: Model name (defaults to current model)

        Returns:
            Model information dictionary or None
        """
        model_name = model_name or self.model
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    f"{self.base_url}/api/show",
                    json={"name": model_name},
                )
                if response.status_code == 200:
                    return dict(response.json())
        except httpx.RequestError as e:
            logger.error(f"Error getting model info: {e}")
        return None
