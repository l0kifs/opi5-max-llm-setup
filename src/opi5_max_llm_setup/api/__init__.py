"""REST API module for RAG and LLM services."""

from opi5_max_llm_setup.api.routes import router
from opi5_max_llm_setup.api.server import create_app

__all__ = ["create_app", "router"]
