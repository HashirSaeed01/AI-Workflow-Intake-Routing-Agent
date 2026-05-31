"""Logging setup for workflow steps."""

from __future__ import annotations

import logging
from typing import Any

from workflow_agent.config.settings import load_routing_config


def setup_logging(level: str | None = None) -> None:
    config = load_routing_config()
    log_cfg: dict[str, Any] = config.get("logging", {})
    log_level = (level or log_cfg.get("level", "INFO")).upper()
    log_format = log_cfg.get(
        "format", "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    logging.basicConfig(level=getattr(logging, log_level, logging.INFO), format=log_format)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
