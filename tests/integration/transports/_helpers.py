from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient

from app.gates import clear_resume_registry
from app.http.gate_endpoint import create_gate_app
from app.marcus.cli.gate_cli import run_gate_decide, run_override_apply, run_override_submit
from app.mcp_server.tools.gate_decide import (
    McpPrincipal,
    McpSession,
    gate_decide_tool,
    override_apply_tool,
    override_submit_tool,
)
from app.runtime.override_api import clear_override_registry as clear_runtime_override_registry
from app.runtime.override_api import register_run_state
from tests.unit.gates._helpers import sample_verdict
from tests.unit.runtime._helpers import TRIAL_ID, sample_run_state


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


def register_override_state() -> None:
    clear_runtime_override_registry()
    register_run_state(trial_id=TRIAL_ID, state=sample_run_state())


def submit_override_mcp(*, operator_id: str) -> dict[str, object]:
    register_override_state()
    session = McpSession(principal=McpPrincipal(id=operator_id))
    return override_submit_tool(
        {"trial_id": str(TRIAL_ID), "node_id": "04", "new_model": "gpt-5.5"},
        session=session,
    )


def submit_override_http(*, operator_id: str) -> dict[str, object]:
    register_override_state()
    client = TestClient(create_gate_app())
    response = client.post(
        "/gate/override/submit",
        json={"trial_id": str(TRIAL_ID), "node_id": "04", "new_model": "gpt-5.5"},
        headers={"X-Operator-Id": operator_id},
    )
    return {"status_code": response.status_code, "body": response.json()}


def submit_override_cli(*, operator_id: str) -> dict[str, object]:
    register_override_state()
    return run_override_submit(
        {
            "trial_id": str(TRIAL_ID),
            "node_id": "04",
            "new_model": "gpt-5.5",
            "operator_id": operator_id,
        }
    )


def apply_override_cli(*, operator_id: str, confirm_token: str) -> dict[str, object]:
    return run_override_apply(
        {
            "trial_id": str(TRIAL_ID),
            "node_id": "04",
            "new_model": "gpt-5.5",
            "confirm_token": confirm_token,
            "operator_id": operator_id,
        }
    )


def apply_override_mcp(*, operator_id: str, confirm_token: str) -> dict[str, object]:
    session = McpSession(principal=McpPrincipal(id=operator_id))
    return override_apply_tool(
        {
            "trial_id": str(TRIAL_ID),
            "node_id": "04",
            "new_model": "gpt-5.5",
            "confirm_token": confirm_token,
        },
        session=session,
    )


def apply_override_http(*, operator_id: str, confirm_token: str) -> dict[str, object]:
    client = TestClient(create_gate_app())
    response = client.post(
        "/gate/override/apply",
        json={
            "trial_id": str(TRIAL_ID),
            "node_id": "04",
            "new_model": "gpt-5.5",
            "confirm_token": confirm_token,
        },
        headers={"X-Operator-Id": operator_id},
    )
    return {"status_code": response.status_code, "body": response.json()}


def normalize_response(response: dict[str, object]) -> dict[str, object]:
    normalized = dict(response)
    normalized.pop("resumed_at", None)
    normalized.pop("headers", None)
    normalized.pop("transport_marker", None)
    return normalized
