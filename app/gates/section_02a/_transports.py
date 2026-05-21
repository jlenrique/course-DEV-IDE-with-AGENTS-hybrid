"""In-process transport handlers for the Section 02A G0 poll surface."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from app.composers.section_02a.directive_model import Directive
from app.gates.section_02a.poll_surface import (
    TransportName,
    display_directive,
    resume_from_verdict,
    submit_verdict,
)
from app.models.operator_verdict_section_02a import (
    DirectiveEditPayload,
    Section02AOperatorVerdict,
    Section02AVerdictVerb,
)


def _transport_response(
    *,
    transport: TransportName,
    directive_or_path: Directive | Path,
    verdict: Section02AOperatorVerdict,
) -> dict[str, Any]:
    return {
        "transport": transport,
        "display": display_directive(directive_or_path),
        "operator_verdict": verdict.model_dump(mode="json"),
        "resume": resume_from_verdict(directive_or_path, verdict),
    }


def submit_cli_verdict(
    directive_or_path: Directive | Path,
    *,
    verb: Section02AVerdictVerb,
    operator_id: str,
    edit_payload: DirectiveEditPayload | dict[str, dict[str, Any]] | None = None,
    reject_reason: str | None = None,
    submitted_at: datetime | None = None,
) -> dict[str, Any]:
    """Submit a verdict through the CLI-equivalent handler."""

    verdict = submit_verdict(
        directive_or_path,
        verb=verb,
        operator_id=operator_id,
        edit_payload=edit_payload,
        reject_reason=reject_reason,
        submitted_at=submitted_at,
    )
    return _transport_response(
        transport="cli",
        directive_or_path=directive_or_path,
        verdict=verdict,
    )


def submit_http_verdict(
    directive_or_path: Directive | Path,
    *,
    verb: Section02AVerdictVerb,
    operator_id: str,
    edit_payload: DirectiveEditPayload | dict[str, dict[str, Any]] | None = None,
    reject_reason: str | None = None,
    submitted_at: datetime | None = None,
) -> dict[str, Any]:
    """Submit a verdict through the HTTP-equivalent handler."""

    verdict = submit_verdict(
        directive_or_path,
        verb=verb,
        operator_id=operator_id,
        edit_payload=edit_payload,
        reject_reason=reject_reason,
        submitted_at=submitted_at,
    )
    return _transport_response(
        transport="http",
        directive_or_path=directive_or_path,
        verdict=verdict,
    )


def submit_mcp_stdio_verdict(
    directive_or_path: Directive | Path,
    *,
    verb: Section02AVerdictVerb,
    operator_id: str,
    edit_payload: DirectiveEditPayload | dict[str, dict[str, Any]] | None = None,
    reject_reason: str | None = None,
    submitted_at: datetime | None = None,
) -> dict[str, Any]:
    """Submit a verdict through the MCP-stdio-equivalent handler."""

    verdict = submit_verdict(
        directive_or_path,
        verb=verb,
        operator_id=operator_id,
        edit_payload=edit_payload,
        reject_reason=reject_reason,
        submitted_at=submitted_at,
    )
    return _transport_response(
        transport="mcp-stdio",
        directive_or_path=directive_or_path,
        verdict=verdict,
    )


TRANSPORT_HANDLERS = {
    "cli": submit_cli_verdict,
    "http": submit_http_verdict,
    "mcp-stdio": submit_mcp_stdio_verdict,
}

__all__ = [
    "TRANSPORT_HANDLERS",
    "submit_cli_verdict",
    "submit_http_verdict",
    "submit_mcp_stdio_verdict",
]
