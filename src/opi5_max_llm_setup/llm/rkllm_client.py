"""RKLLM client for NPU-accelerated LLM inference on RK3588."""

from pathlib import Path
from typing import Any

from loguru import logger

from opi5_max_llm_setup.config.settings import get_settings


class RKLLMNotAvailableError(RuntimeError):
    """Raised when RKLLM runtime is not available."""

    def __init__(self, message: str = "RKLLM runtime is not available") -> None:
        """Initialize the error with a message."""
        super().__init__(message)


class RKLLMClient:
    """Client for RKLLM NPU-accelerated LLM inference.

    This client provides an interface for running LLM inference on the RK3588's
    Neural Processing Unit (NPU) using the RKLLM runtime.

    Note:
        RKLLM requires:
        - Pre-converted .rkllm model files from the RKLLM Model Zoo
        - RKLLM runtime libraries from the rknn-llm repository
        - Running on RK3588 hardware with NPU drivers
    """

    _instance: "RKLLMClient | None" = None
    _initialized: bool = False

    def __new__(cls) -> "RKLLMClient":
        """Singleton pattern to reuse RKLLM instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize RKLLM client."""
        if self._initialized:
            return

        settings = get_settings()
        self.model_path = Path(settings.rkllm_model_path)
        self.lib_path = Path(settings.rkllm_lib_path)

        logger.info(f"Initializing RKLLM client with model: {self.model_path}")

        self._available = self._check_availability()
        self._initialized = True

    def _check_availability(self) -> bool:
        """Check if RKLLM runtime and model are available.

        Returns:
            True if RKLLM is ready for inference
        """
        # Check if model file exists
        if not self.model_path.exists():
            logger.warning(f"RKLLM model not found: {self.model_path}")
            logger.info(
                "Download models from RKLLM Model Zoo: "
                "https://console.box.lenovo.com/l/l0tXb8 (fetch code: rkllm)"
            )
            return False

        # Check if library path exists
        if not self.lib_path.exists():
            logger.warning(f"RKLLM library path not found: {self.lib_path}")
            logger.info(
                "Clone RKLLM repository: git clone https://github.com/airockchip/rknn-llm.git"
            )
            return False

        # Check for NPU device
        npu_device = Path("/dev/rknpu_dev")
        if not npu_device.exists():
            logger.warning("NPU device not found at /dev/rknpu_dev")
            logger.info(
                "Ensure you are running on RK3588 hardware with NPU drivers installed"
            )
            return False

        logger.info("RKLLM runtime available")
        return True

    def is_available(self) -> bool:
        """Check if RKLLM is available for inference.

        Returns:
            True if RKLLM runtime and model are ready
        """
        return self._available

    def generate(self, prompt: str) -> str:
        """Generate a response using RKLLM NPU inference.

        Args:
            prompt: Input prompt

        Returns:
            Generated response text

        Raises:
            RKLLMNotAvailableError: If RKLLM is not available
        """
        if not self._available:
            raise RKLLMNotAvailableError(
                "RKLLM is not available. Ensure model file exists at "
                f"{self.model_path} and RKLLM libraries are at {self.lib_path}. "
                "See docs/npu-setup.md for setup instructions."
            )

        logger.debug(f"RKLLM generating response for prompt: {prompt[:50]}...")

        # TODO: Implement actual RKLLM inference when runtime is available
        # This requires integration with the RKLLM C++ runtime via ctypes or
        # a Python wrapper. For now, return a placeholder indicating setup needed.
        raise RKLLMNotAvailableError(
            "RKLLM inference not yet implemented. "
            "Use Ollama backend (LLM_BACKEND=ollama) or contribute RKLLM integration."
        )

    def get_model_info(self, model_name: str | None = None) -> dict[str, Any] | None:
        """Get information about the loaded RKLLM model.

        Args:
            model_name: Optional model name (for API compatibility, ignored for RKLLM
                       as only one model is loaded at a time)

        Returns:
            Model information dictionary or None if not available
        """
        if not self._available:
            return None

        return {
            "name": model_name or self.model_path.stem,
            "model_path": str(self.model_path),
            "lib_path": str(self.lib_path),
            "backend": "rkllm",
            "accelerator": "NPU (RK3588)",
        }

    def list_models(self) -> list[dict[str, Any]]:
        """List available RKLLM models in the models directory.

        Returns:
            List of model information dictionaries
        """
        models: list[dict[str, Any]] = []
        models_dir = self.model_path.parent

        if not models_dir.exists():
            return models

        for model_file in models_dir.glob("*.rkllm"):
            models.append(
                {
                    "name": model_file.stem,
                    "path": str(model_file),
                    "size": model_file.stat().st_size if model_file.exists() else 0,
                }
            )

        return models
