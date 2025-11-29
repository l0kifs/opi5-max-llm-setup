"""FastAPI server for RAG and LLM services."""

import uvicorn
from fastapi import FastAPI

from opi5_max_llm_setup.api.routes import router
from opi5_max_llm_setup.config.logging import setup_logging
from opi5_max_llm_setup.config.settings import get_settings


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI app
    """
    setup_logging()
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description=(
            "Local LLM with RAG (Retrieval-Augmented Generation) API for "
            "Orange Pi 5 Max. Upload documents and query them using local LLMs."
        ),
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.include_router(router, prefix="/api/v1")

    @app.get("/", tags=["Root"])
    def root() -> dict[str, str]:
        """Root endpoint with API information."""
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/api/v1/health",
        }

    return app


def run_server() -> None:
    """Run the API server."""
    settings = get_settings()
    app = create_app()
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
    )


# For running with `uvicorn opi5_max_llm_setup.api.server:app`
app = create_app()


if __name__ == "__main__":
    run_server()
