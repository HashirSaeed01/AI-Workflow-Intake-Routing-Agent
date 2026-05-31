"""Step 6: Human-in-the-loop review layer."""

from __future__ import annotations

import json
from typing import Callable, Optional

from workflow_agent.models.schemas import (
    ClassificationResult,
    ExtractionResult,
    HumanReviewRequest,
    ResponseDraft,
    RoutingDecision,
)
from workflow_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

ReviewCallback = Callable[[HumanReviewRequest], HumanReviewRequest]


def build_review_request(
    classification: ClassificationResult,
    extraction: ExtractionResult,
    routing: RoutingDecision,
    response_draft: ResponseDraft,
) -> HumanReviewRequest:
    return HumanReviewRequest(
        structured_extraction=extraction,
        classification=classification,
        routing=routing,
        response_draft=response_draft,
        review_status="pending",
    )


def format_review_summary(review: HumanReviewRequest) -> str:
    payload = {
        "classification": review.classification.model_dump(mode="json"),
        "structured_extraction": review.structured_extraction.model_dump(mode="json"),
        "routing": review.routing.model_dump(mode="json"),
        "response_draft": review.response_draft.model_dump(mode="json"),
    }
    return json.dumps(payload, indent=2)


def auto_approve(review: HumanReviewRequest) -> HumanReviewRequest:
    """Batch/demo mode: skip interactive approval."""
    review.review_status = "approved"
    review.reviewer_notes = "Auto-approved (non-interactive mode)"
    logger.info("Human review auto-approved")
    return review


def interactive_review(
    review: HumanReviewRequest,
    input_fn: Callable[[str], str] = input,
) -> HumanReviewRequest:
    """Present structured output and ask operator to approve or modify."""
    print("\n" + "=" * 72)
    print("HUMAN REVIEW — Approve or modify before finalizing")
    print("=" * 72)
    print(format_review_summary(review))
    print("-" * 72)

    while True:
        choice = input_fn("\nAction [approve / modify]: ").strip().lower()
        if choice == "approve":
            review.review_status = "approved"
            review.reviewer_notes = "Approved by operator"
            logger.info("Human review approved by operator")
            return review

        if choice == "modify":
            print("\nEnter modified response draft (blank line to finish):")
            lines: list[str] = []
            while True:
                line = input_fn()
                if not line:
                    break
                lines.append(line)
            if lines:
                review.response_draft.content = "\n".join(lines)
            notes = input_fn("Reviewer notes (optional): ").strip()
            review.reviewer_notes = notes or "Modified by operator"
            review.review_status = "modified"
            logger.info("Human review modified by operator")
            return review

        print("Invalid choice. Enter 'approve' or 'modify'.")


def run_human_review(
    review: HumanReviewRequest,
    *,
    interactive: bool = False,
    input_fn: Optional[Callable[[str], str]] = None,
    review_callback: Optional[ReviewCallback] = None,
) -> HumanReviewRequest:
    if review_callback:
        return review_callback(review)
    if interactive:
        fn = input_fn or input
        return interactive_review(review, input_fn=fn)
    return auto_approve(review)
