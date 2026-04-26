"""CLI bridge stub for gate verdict resume."""

from __future__ import annotations

import argparse
import json
from typing import Any

from app.gates.resume_api import build_transport_response, resume_from_verdict
from app.gates.verdict import OperatorVerdict


def run_gate_decide(payload: dict[str, Any]) -> dict[str, Any]:
    verdict = OperatorVerdict.model_validate(payload)
    command = resume_from_verdict(verdict)
    response = build_transport_response(
        command=command,
        verdict=verdict,
        transport_kind="cli",
    )
    response["transport_marker"] = "[transport=stub]"
    return response


def gate_decide_cli(args: argparse.Namespace) -> int:
    payload = getattr(args, "verdict", None)
    if payload is None:
        payload = {
            "trial_id": args.trial_id,
            "gate_id": args.gate_id,
            "verb": args.verb,
            "card_id": args.card_id,
            "decision_card_digest": args.decision_card_digest,
            "operator_id": args.operator_id,
        }
        if args.edit_payload:
            payload["edit_payload"] = json.loads(args.edit_payload)
    elif isinstance(payload, OperatorVerdict):
        payload = payload.model_dump(mode="python")
    response = run_gate_decide(payload)
    print(f"[transport=stub] {json.dumps(response, sort_keys=True)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gate decide")
    parser.add_argument("--trial-id", required=True)
    parser.add_argument("--gate-id", required=True)
    parser.add_argument("--verb", required=True)
    parser.add_argument("--card-id", required=True)
    parser.add_argument("--decision-card-digest", required=True)
    parser.add_argument("--operator-id", required=True)
    parser.add_argument("--edit-payload", required=False)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return gate_decide_cli(args)


__all__ = ["build_parser", "gate_decide_cli", "main", "run_gate_decide"]
