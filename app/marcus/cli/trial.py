"""CLI shim for production-clone trial launches."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Literal
from uuid import UUID, uuid4

from app.marcus.orchestrator.production_runner import run_production_trial
from app.runtime.economics import RUNS_ROOT


def _load_env_if_available() -> None:
    try:
        from scripts.utilities.env_loader import load_env

        load_env()
    except (FileNotFoundError, ImportError):
        pass


def _has_langsmith_env() -> bool:
    return bool(os.getenv("LANGSMITH_API_KEY") and os.getenv("LANGSMITH_PROJECT"))


def start_trial(
    *,
    preset: Literal["production", "explore"],
    input_path: Path,
    operator_id: str,
    trial_id: UUID | None = None,
    allow_offline_cost_report: bool = False,
    runs_root: Path = RUNS_ROOT,
) -> dict[str, Any]:
    _load_env_if_available()
    if not input_path.exists():
        raise FileNotFoundError(f"trial input path does not exist: {input_path}")
    if not allow_offline_cost_report and (
        not os.getenv("OPENAI_API_KEY") or not _has_langsmith_env()
    ):
        raise RuntimeError(
            "OPENAI_API_KEY plus LANGSMITH_API_KEY and LANGSMITH_PROJECT are required "
            "before production trial start. Use --allow-offline-cost-report only "
            "for local harness checks; offline reports do not close production "
            "clone-launch equivalence."
        )
    effective_trial_id = trial_id or uuid4()
    envelope = run_production_trial(
        corpus_path=input_path,
        preset=preset,
        operator_id=operator_id,
        trial_id=effective_trial_id,
        runs_root=runs_root,
        allow_offline_cost_report=allow_offline_cost_report,
        pause_at_gates=not allow_offline_cost_report,
    )

    run_dir = runs_root / str(effective_trial_id)
    run_json = run_dir / "run.json"
    cost_json = envelope.cost_report_path
    trace_status = (
        "measured-from-langsmith"
        if envelope.production_clone_launch_evidence
        else "skipped-no-langsmith-env"
    )

    result = {
        "status": (
            envelope.status
            if envelope.production_clone_launch_evidence
            else "registered-offline"
        ),
        "trial_id": str(effective_trial_id),
        "preset": preset,
        "input": str(input_path),
        "operator_id": operator_id,
        "run_registry_path": str(run_json),
        "cost_report_json": str(cost_json) if cost_json is not None else None,
        "cost_report_markdown": (
            str(cost_json.with_suffix(".md")) if cost_json is not None else None
        ),
        "langsmith_trace_status": trace_status,
        "production_clone_launch_evidence": envelope.production_clone_launch_evidence,
        "transport_kind": "cli",
    }
    (run_dir / "trial-start.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def start_trial_cli(args: argparse.Namespace) -> int:
    payload = start_trial(
        preset=args.preset,
        input_path=Path(args.input),
        operator_id=args.operator_id,
        trial_id=args.trial_id,
        allow_offline_cost_report=args.allow_offline_cost_report,
        runs_root=Path(args.runs_root) if args.runs_root else RUNS_ROOT,
    )
    print(json.dumps(payload, sort_keys=True))
    return 0


def build_trial_parser(parser: argparse.ArgumentParser) -> None:
    subparsers = parser.add_subparsers(dest="trial_command")
    start = subparsers.add_parser("start")
    start.add_argument("--preset", choices=["production", "explore"], default="production")
    start.add_argument("--input", required=True)
    start.add_argument("--operator-id", default="operator_cli")
    start.add_argument("--trial-id", required=False, type=UUID)
    start.add_argument("--runs-root", required=False, help=argparse.SUPPRESS)
    start.add_argument(
        "--allow-offline-cost-report",
        action="store_true",
        help=(
            "Write a zero-cost deterministic local report when LangSmith env is absent. "
            "Does not count as production clone-launch evidence."
        ),
    )


__all__ = [
    "build_trial_parser",
    "start_trial",
    "start_trial_cli",
]
