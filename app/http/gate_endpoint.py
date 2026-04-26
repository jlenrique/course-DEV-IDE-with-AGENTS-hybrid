"""HTTP bridge stub for gate verdict resume."""

from __future__ import annotations

from typing import Any

from app.gates.resume_api import resume_from_verdict
from app.gates.verdict import OperatorVerdict


def gate_verdict_endpoint(payload: dict[str, Any]) -> dict[str, Any]:
    verdict = OperatorVerdict.model_validate(payload)
    command = resume_from_verdict(verdict)
    return {
        "status": "accepted",
        "headers": {"X-Gate-Transport": "stub"},
        "resume": command.resume,
    }


__all__ = ["gate_verdict_endpoint"]
