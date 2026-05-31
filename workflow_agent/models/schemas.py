"""Pydantic schemas for structured workflow outputs."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class Category(str, Enum):
    SUPPORT_ISSUE = "support_issue"
    BILLING_ISSUE = "billing_issue"
    SALES_INQUIRY = "sales_inquiry"
    INTERNAL_OPS_REQUEST = "internal_ops_request"
    TECHNICAL_BUG = "technical_bug"
    UNKNOWN = "unknown"


class UrgencyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Team(str, Enum):
    SUPPORT = "Support"
    SALES = "Sales"
    ENGINEERING = "Engineering"
    OPS = "Ops"


class IntakeRecord(BaseModel):
    """Normalized raw input after intake step."""

    raw_text: str
    source: str = "email"
    received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class ClassificationResult(BaseModel):
    category: Category
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str


class ExtractionResult(BaseModel):
    customer_name: Optional[str] = None
    urgency: UrgencyLevel
    issue_summary: str
    required_action: str


class RoutingDecision(BaseModel):
    assigned_team: Team
    priority_score: int = Field(ge=1, le=5)
    escalation_needed: bool
    escalation_target: Optional[str] = None
    routing_rationale: str


class ResponseDraft(BaseModel):
    draft_type: Literal["customer_reply", "internal_action_note"]
    content: str


class HumanReviewRequest(BaseModel):
    structured_extraction: ExtractionResult
    classification: ClassificationResult
    routing: RoutingDecision
    response_draft: ResponseDraft
    review_status: Literal["pending", "approved", "modified"] = "pending"
    reviewer_notes: Optional[str] = None


class WorkflowResult(BaseModel):
    """Final output after human review (or auto-approved in batch mode)."""

    intake: IntakeRecord
    classification: ClassificationResult
    extraction: ExtractionResult
    routing: RoutingDecision
    response_draft: ResponseDraft
    human_review: HumanReviewRequest
    workflow_id: str
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_json_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")
