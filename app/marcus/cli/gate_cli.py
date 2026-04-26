"""CLI bridge for gate verdict and override flow."""

from __future__ import annotations

import argparse
import json
from typing import Any

from app.gates.resume_api import build_transport_response, resume_from_verdict
from app.gates.verdict import OperatorVerdict
from app.runtime.override_api import apply_override, decision_card_meta_for_trial, submit_override


def run_gate_decide(payload: dict[str, Any]) -> dict[str, Any]:
    verdict = OperatorVerdict.model_validate(payload)
    command = resume_from_verdict(verdict)
    response = build_transport_response(
        command=command,
        verdict=verdict,
        transport_kind="cli",
    )
    return response


def run_override_submit(payload: dict[str, Any]) -> dict[str, Any]:
    warning = submit_override(
        trial_id=payload["trial_id"],
        node_id=payload["node_id"],
        new_model=payload["new_model"],
    )
    return {
        "status": "warning",
        "warning": warning.model_dump(mode="json"),
        "transport_kind": "cli",
        "operator_id": payload.get("operator_id"),
    }


def run_override_apply(payload: dict[str, Any]) -> dict[str, Any]:
    event = apply_override(
        {
            "trial_id": payload["trial_id"],
            "node_id": payload["node_id"],
            "new_model": payload["new_model"],
            "operator_id": payload["operator_id"],
        },
        str(payload["confirm_token"]),
    )
    trial_id = payload["trial_id"]
    return {
        "status": "accepted",
        "override_event": event.model_dump(mode="json"),
        "decision_card_meta": decision_card_meta_for_trial(trial_id).model_dump(mode="json"),
        "transport_kind": "cli",
    }


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
    print(json.dumps(response, sort_keys=True))
    return 0


def override_submit_cli(args: argparse.Namespace) -> int:
    payload = {
        "trial_id": args.trial_id,
        "node_id": args.node_id,
        "new_model": args.new_model,
        "operator_id": args.operator_id,
    }
    print(json.dumps(run_override_submit(payload), sort_keys=True))
    return 0


def override_apply_cli(args: argparse.Namespace) -> int:
    payload = {
        "trial_id": args.trial_id,
        "node_id": args.node_id,
        "new_model": args.new_model,
        "confirm_token": args.confirm_token,
        "operator_id": args.operator_id,
    }
    print(json.dumps(run_override_apply(payload), sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gate")
    subparsers = parser.add_subparsers(dest="command")

    verdict = subparsers.add_parser("decide")
    verdict.add_argument("--trial-id", required=True)
    verdict.add_argument("--gate-id", required=True)
    verdict.add_argument("--verb", required=True)
    verdict.add_argument("--card-id", required=True)
    verdict.add_argument("--decision-card-digest", required=True)
    verdict.add_argument("--operator-id", required=True)
    verdict.add_argument("--edit-payload", required=False)

    override_submit_parser = subparsers.add_parser("override-submit")
    override_submit_parser.add_argument("--trial-id", required=True)
    override_submit_parser.add_argument("--node-id", required=True)
    override_submit_parser.add_argument("--new-model", required=True)
    override_submit_parser.add_argument("--operator-id", required=True)

    override_apply_parser = subparsers.add_parser("override-apply")
    override_apply_parser.add_argument("--trial-id", required=True)
    override_apply_parser.add_argument("--node-id", required=True)
    override_apply_parser.add_argument("--new-model", required=True)
    override_apply_parser.add_argument("--confirm-token", required=True)
    override_apply_parser.add_argument("--operator-id", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "decide":
        return gate_decide_cli(args)
    if args.command == "override-submit":
        return override_submit_cli(args)
    if args.command == "override-apply":
        return override_apply_cli(args)
    parser.error("a command is required")
    return 2


__all__ = [
    "build_parser",
    "gate_decide_cli",
    "main",
    "override_apply_cli",
    "override_submit_cli",
    "run_gate_decide",
    "run_override_apply",
    "run_override_submit",
]
