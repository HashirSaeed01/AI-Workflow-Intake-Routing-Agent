"""Step 4: Routing — business rules for team assignment and priority."""

from __future__ import annotations

from workflow_agent.config.settings import load_routing_config
from workflow_agent.models.schemas import (
    ClassificationResult,
    ExtractionResult,
    RoutingDecision,
    Team,
)
from workflow_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)


def route_request(
    classification: ClassificationResult,
    extraction: ExtractionResult,
) -> RoutingDecision:
    config = load_routing_config()
    matrix: dict[str, str] = config.get("routing_matrix", {})
    category_priority: dict[str, int] = config.get("category_priority", {})
    urgency_modifiers: dict[str, int] = config.get("urgency_modifiers", {})
    escalation_cfg: dict = config.get("escalation", {})

    category_key = classification.category.value
    team_name = matrix.get(category_key, "Support")

    try:
        assigned_team = Team(team_name)
    except ValueError:
        assigned_team = Team.SUPPORT
        logger.warning("Unknown team '%s', defaulting to Support", team_name)

    base_priority = category_priority.get(category_key, 2)
    modifier = urgency_modifiers.get(extraction.urgency.value, 0)
    priority_score = max(1, min(5, base_priority + modifier))

    escalate_urgency = escalation_cfg.get("escalate_if_urgency", "high")
    escalate_priority = escalation_cfg.get("escalate_if_priority_at_least", 5)
    escalate_targets: dict[str, str] = escalation_cfg.get("escalate_teams", {})

    escalation_needed = (
        extraction.urgency.value == escalate_urgency
        or priority_score >= escalate_priority
        or classification.confidence < 0.6
    )
    escalation_target = escalate_targets.get(category_key) if escalation_needed else None

    rationale_parts = [
        f"Category '{category_key}' maps to {assigned_team.value}.",
        f"Base priority {base_priority} with urgency modifier {modifier:+d} → score {priority_score}.",
    ]
    if escalation_needed:
        rationale_parts.append(
            f"Escalation triggered (urgency={extraction.urgency.value}, "
            f"confidence={classification.confidence:.2f})."
        )

    result = RoutingDecision(
        assigned_team=assigned_team,
        priority_score=priority_score,
        escalation_needed=escalation_needed,
        escalation_target=escalation_target,
        routing_rationale=" ".join(rationale_parts),
    )
    logger.info(
        "Routing complete | team=%s | priority=%d | escalate=%s",
        result.assigned_team.value,
        result.priority_score,
        result.escalation_needed,
    )
    return result
