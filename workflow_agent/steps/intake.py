"""Step 1: Intake — normalize raw incoming text."""

from __future__ import annotations

from workflow_agent.models.schemas import IntakeRecord
from workflow_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)


def intake(raw_text: str, source: str = "email", metadata: dict | None = None) -> IntakeRecord:
    cleaned = raw_text.strip()
    if not cleaned:
        raise ValueError("Intake rejected: empty input text")

    record = IntakeRecord(
        raw_text=cleaned,
        source=source,
        metadata=metadata or {},
    )
    logger.info(
        "Intake complete | source=%s | chars=%d | metadata_keys=%s",
        record.source,
        len(record.raw_text),
        list(record.metadata.keys()),
    )
    return record
