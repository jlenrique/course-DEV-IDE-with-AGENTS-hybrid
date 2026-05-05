from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient

from app.gates import clear_resume_registry
from app.http.gate_endpoint import create_gate_app
from app.parity.contracts import parity_contract
from tests.unit.gates._helpers import sample_verdict


@parity_contract(
    surface_id="http_gate_endpoint",
    mandatory_transports=["http"],
    optional_transports=[],
)
def _parity_contract_registration() -> str:
    """Module-level parity-contract registration for test_http_gate_endpoint.py."""
    return "http_gate_endpoint"


def test_http_gate_endpoint_happy_path() -> None:
    clear_resume_registry()
    verdict = sample_verdict(trial_id=UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"))
    payload = verdict.model_dump(mode="json")
    payload.pop("operator_id", None)
    client = TestClient(create_gate_app())
    response = client.post(
        "/gate/verdict",
        json=payload,
        headers={"X-Operator-Id": "http-user"},
    )
    assert response.status_code == 200
    assert response.json()["resume"]["operator_id"] == "http-user"


def test_http_gate_endpoint_invalid_verdict_returns_400() -> None:
    clear_resume_registry()
    verdict = sample_verdict(trial_id=UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"))
    payload = verdict.model_dump(mode="json")
    payload.pop("operator_id", None)
    payload["verb"] = "timeout"
    client = TestClient(create_gate_app())
    response = client.post(
        "/gate/verdict",
        json=payload,
        headers={"X-Operator-Id": "http-user"},
    )
    assert response.status_code == 400


def test_http_gate_endpoint_digest_mismatch_returns_409() -> None:
    clear_resume_registry()
    verdict = sample_verdict(trial_id=UUID("cccccccc-cccc-4ccc-8ccc-cccccccccccc"))
    payload = verdict.model_dump(mode="json")
    payload.pop("operator_id", None)
    payload["decision_card_digest"] = "0" * 64
    client = TestClient(create_gate_app())
    response = client.post(
        "/gate/verdict",
        json=payload,
        headers={"X-Operator-Id": "http-user"},
    )
    assert response.status_code == 409
