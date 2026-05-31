"""OpenAI API provider with JSON-mode responses."""

from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from workflow_agent.config.settings import get_openai_api_key, load_routing_config
from workflow_agent.llm.base import LLMProvider
from workflow_agent.utils.logging_setup import get_logger
from workflow_agent.utils.retry import with_retry

logger = get_logger(__name__)


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        key = api_key or get_openai_api_key()
        if not key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI provider")
        config = load_routing_config()
        llm_cfg = config.get("llm", {})
        self.model = model or llm_cfg.get("model", "gpt-4o-mini")
        self.temperature = llm_cfg.get("temperature", 0.2)
        self.client = OpenAI(api_key=key)

    def complete_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        def _call() -> dict[str, Any]:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            content = response.choices[0].message.content or "{}"
            logger.debug("OpenAI raw response: %s", content[:500])
            return json.loads(content)

        return with_retry(_call, operation_name="openai_complete_json")
