from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient

from app.gates import clear_resume_registry
from app.http.gate_endpoint import create_gate_app
from app.marcus.cli.gate_cli import run_gate_decide
from app.mcp_server.tools.gate_decide import McpPrincipal, McpSession, gate_decide_tool
from tests.unit.gates._helpers import sample_verdict


def _body_without_operator_id(trial_id: UUID) -> dict[str, object]:
    verdict = sample_verdict(trial_id=trial_id)
    payload = verdict.model_dump(mode="json")
    payload.pop("operator_id", None)
    return payload


def submit_mcp(*, trial_id: UUID, operator_id: str) -> dict[str, object]:
    clear_resume_registry()
    payload = _body_without_operator_id(trial_id)
    session = McpSession(principal=McpPrincipal(id=operator_id))
    return gate_decide_tool(payload, session=session)


def submit_http(*, trial_id: UUID, operator_id: str) -> dict[str, object]:
    clear_resume_registry()
    payload = _body_without_operator_id(trial_id)
    client = TestClient(create_gate_app())
    response = client.post(
        "/gate/verdict",
        json=payload,
        headers={"X-Operator-Id": operator_id},
    )
    return {
        "status_code": response.status_code,
        "body": response.json(),
    }


def submit_cli(*, trial_id: UUID, operator_id: str) -> dict[str, object]:
    clear_resume_registry()
    verdict = sample_verdict(trial_id=trial_id)
    payload = verdict.model_dump(mode="json")
    payload["operator_id"] = operator_id
    return run_gate_decide(payload)


def normalize_response(response: dict[str, object]) -> dict[str, object]:
    normalized = dict(response)
    normalized.pop("resumed_at", None)
    normalized.pop("headers", None)
    normalized.pop("transport_marker", None)
    return normalized
