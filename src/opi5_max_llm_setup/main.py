"""Main entry point for the Orange Pi 5 Max LLM Setup application."""

from opi5_max_llm_setup.api.server import run_server
from opi5_max_llm_setup.config.logging import setup_logging


def main() -> None:
    """Main entry point for the application."""
    setup_logging()
    print("Starting Orange Pi 5 Max LLM Setup...")
    print("API server starting at http://0.0.0.0:8000")
    print("OpenAPI docs available at http://0.0.0.0:8000/docs")
    run_server()


if __name__ == "__main__":
    main()
