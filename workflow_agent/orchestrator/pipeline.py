"""Workflow orchestration — coordinates all pipeline steps."""

from __future__ import annotations

import uuid
from typing import Callable, Optional

from workflow_agent.llm.base import LLMProvider
from workflow_agent.llm.factory import get_llm_provider
from workflow_agent.models.schemas import HumanReviewRequest, WorkflowResult
from workflow_agent.steps.classification import classify
from workflow_agent.steps.extraction import extract_fields
from workflow_agent.steps.human_review import build_review_request, run_human_review
from workflow_agent.steps.intake import intake
from workflow_agent.steps.response_drafting import draft_response
from workflow_agent.steps.routing import route_request
from workflow_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)


class WorkflowOrchestrator:
    """Production-style pipeline coordinator with clear step boundaries."""

    def __init__(
        self,
        llm: LLMProvider | None = None,
        *,
        force_mock: bool = False,
    ) -> None:
        self.llm = llm or get_llm_provider(force_mock=force_mock)

    def run(
        self,
        raw_text: str,
        *,
        source: str = "email",
        metadata: dict | None = None,
        interactive_review: bool = False,
        input_fn: Callable[[str], str] | None = None,
        workflow_id: str | None = None,
    ) -> WorkflowResult:
        wf_id = workflow_id or str(uuid.uuid4())
        logger.info("Starting workflow %s", wf_id)

        # Step 1: Intake
        intake_record = intake(raw_text, source=source, metadata=metadata)

        # Step 2: Classification
        classification = classify(intake_record, self.llm)

        # Step 3: Structured extraction
        extraction = extract_fields(intake_record, classification, self.llm)

        # Step 4: Routing (pure business rules)
        routing = route_request(classification, extraction)

        # Step 5: Response drafting
        response_draft = draft_response(
            intake_record, classification, extraction, routing, self.llm
        )

        # Step 6: Human-in-the-loop
        review_request = build_review_request(
            classification, extraction, routing, response_draft
        )
        reviewed = run_human_review(
            review_request,
            interactive=interactive_review,
            input_fn=input_fn,
        )

        result = WorkflowResult(
            intake=intake_record,
            classification=classification,
            extraction=extraction,
            routing=routing,
            response_draft=reviewed.response_draft,
            human_review=reviewed,
            workflow_id=wf_id,
        )
        logger.info("Workflow %s completed | status=%s", wf_id, reviewed.review_status)
        return result
