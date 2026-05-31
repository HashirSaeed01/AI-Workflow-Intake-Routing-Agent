"""LLM prompt templates."""

CLASSIFICATION_SYSTEM = """You classify incoming business requests for Rozeta Labs.
Return ONLY valid JSON with keys: category, confidence, rationale.

Allowed categories:
- support_issue
- billing_issue
- sales_inquiry
- internal_ops_request
- technical_bug
- unknown

confidence must be a float between 0 and 1."""

CLASSIFICATION_USER = """Classify this incoming message:

---
{raw_text}
---"""

EXTRACTION_SYSTEM = """You extract structured fields from business requests for Rozeta Labs.
Return ONLY valid JSON with keys:
- customer_name (string or null)
- urgency (low | medium | high)
- issue_summary (string, one sentence)
- required_action (string, imperative verb phrase)"""

EXTRACTION_USER = """Extract fields from this message (category hint: {category}):

---
{raw_text}
---"""

RESPONSE_DRAFT_SYSTEM = """You draft concise professional responses for Rozeta Labs operators.
Return ONLY valid JSON with keys:
- draft_type ("customer_reply" or "internal_action_note")
- content (string, 2-4 sentences max)

Use customer_reply when the sender appears external; otherwise internal_action_note."""

RESPONSE_DRAFT_USER = """Draft a response/action note.

Category: {category}
Urgency: {urgency}
Issue: {issue_summary}
Required action: {required_action}
Assigned team: {assigned_team}

Original message:
---
{raw_text}
---"""
