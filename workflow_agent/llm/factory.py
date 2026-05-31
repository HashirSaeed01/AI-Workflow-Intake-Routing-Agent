"""LLM provider factory."""

from __future__ import annotations

from workflow_agent.config.settings import use_mock_mode
from workflow_agent.llm.base import LLMProvider
from workflow_agent.llm.mock_provider import MockLLMProvider
from workflow_agent.llm.openai_provider import OpenAIProvider
from workflow_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)


def get_llm_provider(force_mock: bool = False) -> LLMProvider:
    if use_mock_mode(force_mock):
        logger.info("Using mock LLM provider (no API key or force_mock=True)")
        return MockLLMProvider()
    logger.info("Using OpenAI LLM provider")
    return OpenAIProvider()
