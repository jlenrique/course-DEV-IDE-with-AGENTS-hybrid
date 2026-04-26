"""Gate verdict and override MCP tools."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.gates.resume_api import build_transport_response, resume_from_verdict
from app.gates.verdict import OperatorVerdict
from app.runtime.override_api import apply_override, decision_card_meta_for_trial, submit_override


@dataclass(frozen=True)
class McpPrincipal:
    id: str


@dataclass(frozen=True)
class McpSession:
    principal: McpPrincipal


def gate_decide_tool(payload: dict[str, Any], *, session: McpSession) -> dict[str, Any]:
    verdict = OperatorVerdict.model_validate({**payload, "operator_id": session.principal.id})
    command = resume_from_verdict(verdict)
    return build_transport_response(
        command=command,
        verdict=verdict,
        transport_kind="mcp",
    )


def override_submit_tool(
    payload: dict[str, Any],
    *,
    session: McpSession,
) -> dict[str, Any]:
    warning = submit_override(
        trial_id=payload["trial_id"],
        node_id=payload["node_id"],
        new_model=payload["new_model"],
    )
    return {
        "status": "warning",
        "warning": warning.model_dump(mode="json"),
        "transport_kind": "mcp",
        "operator_id": session.principal.id,
    }


def override_apply_tool(
    payload: dict[str, Any],
    *,
    session: McpSession,
) -> dict[str, Any]:
    event = apply_override(
        {
            "trial_id": payload["trial_id"],
            "node_id": payload["node_id"],
            "new_model": payload["new_model"],
            "operator_id": session.principal.id,
        },
        str(payload["confirm_token"]),
    )
    trial_id = payload["trial_id"]
    return {
        "status": "accepted",
        "override_event": event.model_dump(mode="json"),
        "decision_card_meta": decision_card_meta_for_trial(trial_id).model_dump(mode="json"),
        "transport_kind": "mcp",
    }


__all__ = [
    "McpPrincipal",
    "McpSession",
    "gate_decide_tool",
    "override_apply_tool",
    "override_submit_tool",
]
