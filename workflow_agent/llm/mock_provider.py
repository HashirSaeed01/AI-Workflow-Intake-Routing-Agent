"""Rule-based mock LLM for offline/demo runs."""

from __future__ import annotations

import json
import re
from typing import Any

from workflow_agent.config.settings import load_routing_config
from workflow_agent.llm.base import LLMProvider
from workflow_agent.llm import prompts


class MockLLMProvider(LLMProvider):
    """Simulates LLM responses using keyword rules and heuristics."""

    def complete_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        if "Classify" in user_prompt or "classify" in system_prompt.lower():
            return self._classify(user_prompt)
        if "Extract" in user_prompt or "extract" in system_prompt.lower():
            return self._extract(user_prompt)
        if "Draft" in user_prompt or "draft" in system_prompt.lower():
            return self._draft(user_prompt)
        return {"error": "unknown_prompt_type"}

    def _classify(self, user_prompt: str) -> dict[str, Any]:
        text = self._extract_block(user_prompt).lower()
        config = load_routing_config()
        keywords: dict[str, list[str]] = config.get("classification_keywords", {})

        scores: dict[str, int] = {cat: 0 for cat in config.get("categories", [])}
        for category, terms in keywords.items():
            for term in terms:
                if str(term).lower() in text:
                    scores[category] = scores.get(category, 0) + 1

        best_category = max(scores, key=lambda k: scores[k]) if scores else "unknown"
        best_score = scores.get(best_category, 0)
        if best_score == 0:
            best_category = "unknown"

        confidence = min(0.95, 0.55 + best_score * 0.12)
        return {
            "category": best_category,
            "confidence": round(confidence, 2),
            "rationale": f"Mock classifier matched {best_score} keyword(s) for '{best_category}'.",
        }

    def _extract(self, user_prompt: str) -> dict[str, Any]:
        text = self._extract_block(user_prompt)
        lower = text.lower()

        urgency = "medium"
        if any(w in lower for w in ["urgent", "asap", "immediately", "down", "critical", "emergency"]):
            urgency = "high"
        elif any(w in lower for w in ["when you can", "no rush", "not urgent", "fyi", "whenever"]):
            urgency = "low"

        customer_name = self._extract_name(text)
        issue_summary = self._first_meaningful_sentence(text)
        required_action = self._infer_action(lower)

        return {
            "customer_name": customer_name,
            "urgency": urgency,
            "issue_summary": issue_summary,
            "required_action": required_action,
        }

    def _draft(self, user_prompt: str) -> dict[str, Any]:
        category = self._parse_field(user_prompt, "Category")
        urgency = self._parse_field(user_prompt, "Urgency")
        issue = self._parse_field(user_prompt, "Issue")
        action = self._parse_field(user_prompt, "Required action")
        team = self._parse_field(user_prompt, "Assigned team")
        raw = self._extract_block(user_prompt, marker="Original message:")

        is_external = "@" in raw and not any(
            d in raw.lower() for d in ["@rozetalabs", "@internal.rozetalabs"]
        )
        draft_type = "customer_reply" if is_external else "internal_action_note"

        if draft_type == "customer_reply":
            content = (
                f"Thank you for reaching out to Rozeta Labs. We understand: {issue}. "
                f"Our {team} team will {action.lower()} and follow up shortly. "
                f"Priority: {urgency}."
            )
        else:
            content = (
                f"[{team}] {action}. Context: {issue}. "
                f"Category={category}, urgency={urgency}. Assign owner and confirm SLA."
            )

        return {"draft_type": draft_type, "content": content}

    @staticmethod
    def _extract_block(text: str, marker: str = "---") -> str:
        if marker == "---":
            parts = text.split("---")
            if len(parts) >= 2:
                return parts[1].strip()
        idx = text.find(marker)
        if idx >= 0:
            block = text[idx + len(marker) :]
            if "---" in block:
                block = block.split("---")[0]
            return block.strip()
        return text.strip()

    @staticmethod
    def _extract_name(text: str) -> str | None:
        patterns = [
            r"(?:this is|i'm|i am|it's)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+from",
            r"(?:hi|hello|hey)[,\s]+(?:this is|i'm|i am|it's)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
            r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+here",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()
        return None

    @staticmethod
    def _first_meaningful_sentence(text: str) -> str:
        sentences = re.split(r"[.!?\n]+", text)
        for sentence in sentences:
            cleaned = sentence.strip()
            if len(cleaned) > 20:
                return cleaned[:200]
        return text.strip()[:200]

    @staticmethod
    def _infer_action(lower: str) -> str:
        if "refund" in lower:
            return "Process refund review and respond within 24h"
        if "invoice" in lower or "billing" in lower:
            return "Audit billing records and reconcile charges"
        if "demo" in lower or "pricing" in lower:
            return "Schedule discovery call and send pricing overview"
        if "bug" in lower or "error" in lower or "crash" in lower:
            return "Reproduce issue, triage severity, and patch or escalate"
        if "access" in lower or "onboarding" in lower:
            return "Provision access and confirm completion with requester"
        if "password" in lower or "login" in lower:
            return "Verify identity and reset account credentials"
        return "Review request details and assign appropriate owner"

    @staticmethod
    def _parse_field(text: str, field: str) -> str:
        match = re.search(rf"{field}:\s*(.+)", text)
        return match.group(1).strip() if match else "unknown"
