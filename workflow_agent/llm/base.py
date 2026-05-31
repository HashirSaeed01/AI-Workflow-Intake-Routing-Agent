"""Abstract LLM provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    @abstractmethod
    def complete_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        """Return parsed JSON object from the model."""
