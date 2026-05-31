"""Step 5: Response drafting — customer reply or internal action note."""

from __future__ import annotations

from workflow_agent.llm import prompts
from workflow_agent.llm.base import LLMProvider
from workflow_agent.models.schemas import (
    ClassificationResult,
    ExtractionResult,
    IntakeRecord,
    ResponseDraft,
    RoutingDecision,
)
from workflow_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)


def infer_draft_type(intake_record: IntakeRecord) -> str:
    """Business rule: external senders get customer replies; internal sources get action notes."""
    if intake_record.source in ("slack", "crm_note", "internal"):
        return "internal_action_note"

    sender = str(intake_record.metadata.get("from", "")).lower()
    if sender and not any(tag in sender for tag in ("@rozetalabs", "@internal.")):
        return "customer_reply"

    if "@" in intake_record.raw_text:
        lower = intake_record.raw_text.lower()
        if not any(tag in lower for tag in ("@rozetalabs", "@internal.")):
            return "customer_reply"

    return "internal_action_note"


def draft_response(
    intake_record: IntakeRecord,
    classification: ClassificationResult,
    extraction: ExtractionResult,
    routing: RoutingDecision,
    llm: LLMProvider,
) -> ResponseDraft:
    user_prompt = prompts.RESPONSE_DRAFT_USER.format(
        category=classification.category.value,
        urgency=extraction.urgency.value,
        issue_summary=extraction.issue_summary,
        required_action=extraction.required_action,
        assigned_team=routing.assigned_team.value,
        raw_text=intake_record.raw_text,
    )
    payload = llm.complete_json(prompts.RESPONSE_DRAFT_SYSTEM, user_prompt)

    llm_draft_type = payload.get("draft_type", "internal_action_note")
    if llm_draft_type not in ("customer_reply", "internal_action_note"):
        llm_draft_type = "internal_action_note"

    resolved_type = infer_draft_type(intake_record)
    draft_type = resolved_type if resolved_type in ("customer_reply", "internal_action_note") else llm_draft_type

    result = ResponseDraft(
        draft_type=draft_type,
        content=str(payload.get("content", "Review and respond as appropriate.")),
    )
    logger.info("Response draft complete | type=%s | length=%d", result.draft_type, len(result.content))
    return result
