"""RKLLM client for NPU-accelerated LLM inference via RKLLama server.

RKLLama is an Ollama-compatible server that runs LLMs on the RK3588 NPU.
Since it implements the same API as Ollama, we can reuse similar HTTP patterns.
See: https://github.com/NotPunchnox/rkllama
"""

from http import HTTPStatus
from typing import Any

import httpx
from langchain_core.language_models import BaseLLM
from langchain_ollama import OllamaLLM
from loguru import logger

from opi5_max_llm_setup.config.settings import get_settings


class RKLLMNotAvailableError(RuntimeError):
    """Raised when RKLLama server is not available."""

    def __init__(self, message: str = "RKLLama server is not available") -> None:
        """Initialize the error with a message."""
        super().__init__(message)


class RKLLMClient:
    """Client for RKLLama NPU-accelerated LLM inference.

    RKLLama provides an Ollama-compatible API for running LLMs on the RK3588 NPU.
    This client connects to the RKLLama server via HTTP.

    Note:
        RKLLama requires:
        - RKLLama server running (default port 8080)
        - Pre-converted .rkllm model files loaded in the server
        - Running on RK3588 hardware with NPU access (privileged Docker mode)
    """

    _instance: "RKLLMClient | None" = None
    _initialized: bool = False
    _llm: BaseLLM | None = None

    def __new__(cls) -> "RKLLMClient":
        """Singleton pattern to reuse RKLLama client instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize RKLLama client."""
        if self._initialized:
            return

        settings = get_settings()
        self.base_url = settings.rkllm_base_url
        self.model = settings.rkllm_model

        logger.info(f"Initializing RKLLama client: {self.base_url}")
        self._llm = self._create_llm()
        self._initialized = True

    def _create_llm(self) -> BaseLLM:
        """Create the LangChain LLM instance for RKLLama.

        Since RKLLama is Ollama API-compatible, we can use OllamaLLM directly.

        Returns:
            OllamaLLM instance configured for RKLLama
        """
        return OllamaLLM(
            model=self.model,
            base_url=self.base_url,
        )

    @property
    def llm(self) -> BaseLLM:
        """Get the LangChain LLM instance.

        Returns:
            LLM instance

        Raises:
            RKLLMNotAvailableError: If LLM is not initialized
        """
        if self._llm is None:
            raise RKLLMNotAvailableError("RKLLama LLM not initialized")
        return self._llm

    def is_available(self) -> bool:
        """Check if RKLLama server is available.

        Pings the /api/tags endpoint to verify server connectivity.

        Returns:
            True if RKLLama server is reachable
        """
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/api/tags")
                return response.status_code == HTTPStatus.OK
        except httpx.RequestError:
            return False

    def generate(self, prompt: str) -> str:
        """Generate a response using RKLLama NPU inference.

        Args:
            prompt: Input prompt

        Returns:
            Generated response text

        Raises:
            RKLLMNotAvailableError: If RKLLama is not available
        """
        if not self.is_available():
            raise RKLLMNotAvailableError(
                f"RKLLama server is not available at {self.base_url}. "
                "Ensure RKLLama is running. See docs/npu-setup.md for setup."
            )

        logger.debug(f"RKLLama generating response for prompt: {prompt[:50]}...")
        response = self.llm.invoke(prompt)
        return str(response)

    def get_model_info(self, model_name: str | None = None) -> dict[str, Any] | None:
        """Get information about a specific model from RKLLama.

        Args:
            model_name: Model name (defaults to configured model)

        Returns:
            Model information dictionary or None if not available
        """
        model_name = model_name or self.model
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    f"{self.base_url}/api/show",
                    json={"name": model_name},
                )
                if response.status_code == HTTPStatus.OK:
                    data = dict(response.json())
                    data["backend"] = "rkllm"
                    data["accelerator"] = "NPU (RK3588)"
                    return data
        except httpx.RequestError as e:
            logger.error(f"Error getting model info from RKLLama: {e}")
        return None

    def list_models(self) -> list[dict[str, Any]]:
        """List available models from RKLLama server.

        Returns:
            List of model information dictionaries
        """
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(f"{self.base_url}/api/tags")
                if response.status_code == HTTPStatus.OK:
                    data = response.json()
                    return list(data.get("models", []))
        except httpx.RequestError as e:
            logger.error(f"Error listing models from RKLLama: {e}")
        return []
