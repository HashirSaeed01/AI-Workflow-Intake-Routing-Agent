"""CLI entry point for the AI Workflow Intake & Routing Agent."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from workflow_agent.orchestrator.pipeline import WorkflowOrchestrator
from workflow_agent.utils.logging_setup import setup_logging


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AI Workflow Intake & Routing Agent — Rozeta Labs prototype",
    )
    parser.add_argument(
        "--text",
        type=str,
        help="Raw incoming message text to process",
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Path to a text file containing the incoming message",
    )
    parser.add_argument(
        "--source",
        type=str,
        default="email",
        help="Intake source label (email, ticket, crm_note, slack)",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Enable human-in-the-loop approve/modify step",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Force mock LLM mode even if OPENAI_API_KEY is set",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run all bundled example inputs in batch mode",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=None,
        help="Override logging level (DEBUG, INFO, WARNING)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    setup_logging(args.log_level)

    orchestrator = WorkflowOrchestrator(force_mock=args.mock)

    if args.demo:
        from examples.sample_inputs import SAMPLE_MESSAGES

        results = []
        for idx, sample in enumerate(SAMPLE_MESSAGES, start=1):
            print(f"\n{'#' * 72}\nDEMO RUN {idx}/{len(SAMPLE_MESSAGES)}: {sample['label']}\n{'#' * 72}")
            result = orchestrator.run(
                sample["text"],
                source=sample.get("source", "email"),
                metadata=sample.get("metadata", {}),
            )
            results.append(result.to_json_dict())
            print(json.dumps(result.to_json_dict(), indent=2, default=str))

        output_path = Path(__file__).resolve().parent.parent / "examples" / "sample_outputs.json"
        output_path.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
        print(f"\nSaved batch outputs to {output_path}")
        return 0

    raw_text = args.text
    if args.file:
        raw_text = args.file.read_text(encoding="utf-8")
    if not raw_text:
        parser.error("Provide --text, --file, or --demo")

    result = orchestrator.run(
        raw_text,
        source=args.source,
        interactive_review=args.interactive,
    )
    print(json.dumps(result.to_json_dict(), indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
