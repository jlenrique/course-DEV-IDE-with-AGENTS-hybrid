from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient

from app.gates import clear_resume_registry
from app.http.gate_endpoint import create_gate_app
from tests.unit.gates._helpers import sample_verdict


def test_http_operator_id_header_required() -> None:
    clear_resume_registry()
    verdict = sample_verdict(trial_id=UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"))
    payload = verdict.model_dump(mode="json")
    payload.pop("operator_id", None)
    client = TestClient(create_gate_app())
    response = client.post("/gate/verdict", json=payload)
    assert response.status_code == 400
