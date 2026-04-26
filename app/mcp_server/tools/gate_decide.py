"""Gate decide MCP tool."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.gates.resume_api import build_transport_response, resume_from_verdict
from app.gates.verdict import OperatorVerdict


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


__all__ = ["McpPrincipal", "McpSession", "gate_decide_tool"]
