"""A2 single-decision shim for the woken voice-pick gate G4A (Arc 2, 2026-06-18)."""

from __future__ import annotations

import argparse
import json
import sys

from pydantic import ValidationError

from app.marcus.cli.gate_shims._shim_parser import build_shim_parser
from app.marcus.orchestrator.production_runner import resume_production_trial
from app.models.state.operator_verdict import OperatorVerdict
from app.runtime.economics import RUNS_ROOT

GATE_ID = "G4A"


def shim_main(args: argparse.Namespace) -> int:
    try:
        verdict = OperatorVerdict.model_validate_json(
            args.verdict_file.read_text(encoding="utf-8")
        )
    except ValidationError as exc:
        print(f"ERROR: invalid OperatorVerdict in {args.verdict_file}: {exc}", file=sys.stderr)
        return 2
    if verdict.trial_id != args.trial_id:
        print(
            f"ERROR: verdict trial_id={verdict.trial_id} does not match "
            f"--trial-id={args.trial_id}",
            file=sys.stderr,
        )
        return 1
    runs_root = args.runs_root if args.runs_root else RUNS_ROOT
    try:
        envelope = resume_production_trial(
            trial_id=args.trial_id,
            verdict=verdict,
            runs_root=runs_root,
        )
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    payload = {
        "status": envelope.status,
        "trial_id": str(args.trial_id),
        "gate_id": GATE_ID,
        "paused_gate": envelope.paused_gate,
        "run_registry_path": (runs_root / str(args.trial_id) / "run.json").as_posix(),
        "cost_report_json": envelope.cost_report_path.as_posix()
        if envelope.cost_report_path is not None
        else None,
        "production_clone_launch_evidence": envelope.production_clone_launch_evidence,
        "transport_kind": "cli",
    }
    print(json.dumps(payload, sort_keys=True))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_shim_parser(GATE_ID)
    args = parser.parse_args(argv)
    return shim_main(args)


if __name__ == "__main__":
    raise SystemExit(main())
