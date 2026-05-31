"""Step 3: Structured extraction — strict JSON fields."""

from __future__ import annotations

from workflow_agent.llm import prompts
from workflow_agent.llm.base import LLMProvider
from workflow_agent.models.schemas import (
    ClassificationResult,
    ExtractionResult,
    IntakeRecord,
    UrgencyLevel,
)
from workflow_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)


def extract_fields(
    intake_record: IntakeRecord,
    classification: ClassificationResult,
    llm: LLMProvider,
) -> ExtractionResult:
    user_prompt = prompts.EXTRACTION_USER.format(
        raw_text=intake_record.raw_text,
        category=classification.category.value,
    )
    payload = llm.complete_json(prompts.EXTRACTION_SYSTEM, user_prompt)

    urgency_raw = str(payload.get("urgency", "medium")).lower()
    try:
        urgency = UrgencyLevel(urgency_raw)
    except ValueError:
        urgency = UrgencyLevel.MEDIUM

    customer_name = payload.get("customer_name")
    if customer_name in ("", "null", "None", None):
        customer_name = None

    result = ExtractionResult(
        customer_name=customer_name,
        urgency=urgency,
        issue_summary=str(payload.get("issue_summary", "Unspecified issue")),
        required_action=str(payload.get("required_action", "Review and assign owner")),
    )
    logger.info(
        "Extraction complete | urgency=%s | customer=%s",
        result.urgency.value,
        result.customer_name or "N/A",
    )
    return result
