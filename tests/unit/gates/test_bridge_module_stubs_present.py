from __future__ import annotations

import argparse
from uuid import UUID

from app.gates import clear_resume_registry
from app.http.gate_endpoint import gate_verdict_endpoint
from app.marcus.cli.gate_cli import gate_decide_cli
from tests.unit.gates._helpers import sample_verdict


def test_gate_cli_stub_is_callable(capsys) -> None:
    clear_resume_registry()
    verdict = sample_verdict(trial_id=UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"))
    exit_code = gate_decide_cli(argparse.Namespace(verdict=verdict))
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "[transport=stub]" in captured.out


def test_gate_endpoint_stub_is_callable() -> None:
    clear_resume_registry()
    verdict = sample_verdict(trial_id=UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"))
    response = gate_verdict_endpoint(verdict.model_dump(mode="json"))
    assert response["status"] == "accepted"
    assert response["headers"]["X-Gate-Transport"] == "stub"
