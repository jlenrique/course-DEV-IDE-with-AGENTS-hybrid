"""Standardized logging configuration for the project.

Provides consistent log formatting across all Python scripts,
with configurable levels for development vs production use.
"""

from __future__ import annotations

import logging
import sys
from datetime import UTC, datetime
from pathlib import Path

from scripts.utilities.file_helpers import project_root

_CONFIGURED = False


def setup_logging(
    name: str = "course-agents",
    level: int = logging.INFO,
    log_to_file: bool = False,
    log_dir: str | Path | None = None,
) -> logging.Logger:
    """Configure and return a logger with standardized formatting.

    Args:
        name: Logger name (typically module or script name).
        level: Logging level (DEBUG for development mode per FR40).
        log_to_file: Whether to also write logs to a timestamped file.
        log_dir: Directory for log files. Defaults to ``{project_root}/logs``.

    Returns:
        Configured logger instance.
    """
    global _CONFIGURED  # noqa: PLW0603

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if _CONFIGURED:
        return logger
    _CONFIGURED = True

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler(sys.stderr)
    console.setFormatter(formatter)
    logger.addHandler(console)

    if log_to_file:
        if log_dir is None:
            log_dir = project_root() / "logs"
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(tz=UTC).strftime("%Y%m%d_%H%M%S")
        file_handler = logging.FileHandler(
            log_dir / f"{name}_{timestamp}.log", encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
