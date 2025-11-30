import sys
from dataclasses import dataclass

from loguru import logger

from opi5_max_llm_setup.config.settings import get_settings


@dataclass
class LoggingState:
    """State for tracking logging configuration."""

    configured: bool = False


_logging_state = LoggingState()


def setup_logging() -> None:
    """Configure logging for the application."""
    if _logging_state.configured:
        return

    settings = get_settings()

    # Remove default handler to avoid duplicate logs
    logger.remove()

    # Console handler - for development/debugging
    logger.add(
        sys.stderr,
        level=settings.logging_level,
        format=settings.logging_format,
        colorize=True,
        backtrace=True,
        diagnose=True,
        enqueue=True,
        catch=True,
    )

    # Configure common context (can be overridden per module)
    logger.configure(extra={"app": settings.app_name, "version": settings.app_version})

    # Log startup message
    logger.info(
        "Logging system initialized",
        log_level=settings.logging_level,
    )

    _logging_state.configured = True
