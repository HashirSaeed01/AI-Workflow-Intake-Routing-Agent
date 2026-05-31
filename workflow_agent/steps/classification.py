"""Step 2: Classification — LLM or rule-based category assignment."""

from __future__ import annotations

from workflow_agent.llm import prompts
from workflow_agent.llm.base import LLMProvider
from workflow_agent.models.schemas import Category, ClassificationResult, IntakeRecord
from workflow_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)


def classify(intake_record: IntakeRecord, llm: LLMProvider) -> ClassificationResult:
    user_prompt = prompts.CLASSIFICATION_USER.format(raw_text=intake_record.raw_text)
    payload = llm.complete_json(prompts.CLASSIFICATION_SYSTEM, user_prompt)

    category_raw = str(payload.get("category", "unknown")).lower().replace(" ", "_")
    try:
        category = Category(category_raw)
    except ValueError:
        category = Category.UNKNOWN
        logger.warning("Unknown category '%s', defaulting to unknown", category_raw)

    result = ClassificationResult(
        category=category,
        confidence=float(payload.get("confidence", 0.5)),
        rationale=str(payload.get("rationale", "No rationale provided")),
    )
    logger.info(
        "Classification complete | category=%s | confidence=%.2f",
        result.category.value,
        result.confidence,
    )
    return result
