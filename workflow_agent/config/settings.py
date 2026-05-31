"""Configuration loader for routing rules and runtime settings."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

load_dotenv()

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "routing_rules.yaml"


@lru_cache(maxsize=1)
def load_routing_config(config_path: str | Path | None = None) -> dict[str, Any]:
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    if not path.exists():
        raise FileNotFoundError(f"Routing config not found: {path}")
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def get_openai_api_key() -> str | None:
    return os.getenv("OPENAI_API_KEY")


def use_mock_mode(force_mock: bool = False) -> bool:
    if force_mock:
        return True
    return not bool(get_openai_api_key())
