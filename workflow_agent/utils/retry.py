"""Retry helper for transient LLM failures."""

from __future__ import annotations

import time
from typing import Callable, TypeVar

from workflow_agent.config.settings import load_routing_config
from workflow_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


def with_retry(
    fn: Callable[[], T],
    *,
    max_retries: int | None = None,
    backoff_seconds: float | None = None,
    operation_name: str = "llm_call",
) -> T:
    config = load_routing_config()
    llm_cfg = config.get("llm", {})
    retries = max_retries if max_retries is not None else llm_cfg.get("max_retries", 3)
    backoff = (
        backoff_seconds
        if backoff_seconds is not None
        else llm_cfg.get("retry_backoff_seconds", 1.5)
    )

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 — retry wrapper catches provider errors
            last_error = exc
            if attempt >= retries:
                logger.error(
                    "%s failed after %d attempts: %s", operation_name, retries, exc
                )
                raise
            sleep_for = backoff * attempt
            logger.warning(
                "%s attempt %d/%d failed (%s). Retrying in %.1fs...",
                operation_name,
                attempt,
                retries,
                exc,
                sleep_for,
            )
            time.sleep(sleep_for)

    raise RuntimeError(f"Unexpected retry state for {operation_name}") from last_error
