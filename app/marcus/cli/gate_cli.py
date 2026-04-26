"""CLI bridge stub for gate verdict resume."""

from __future__ import annotations

import argparse

from app.gates.resume_api import resume_from_verdict
from app.gates.verdict import OperatorVerdict


def gate_decide_cli(args: argparse.Namespace) -> int:
    payload = getattr(args, "verdict", None)
    verdict = (
        payload
        if isinstance(payload, OperatorVerdict)
        else OperatorVerdict.model_validate(payload)
    )
    command = resume_from_verdict(verdict)
    print(f"[transport=stub] resumed gate {verdict.gate_id} via CLI bridge: {command!r}")
    return 0


__all__ = ["gate_decide_cli"]
