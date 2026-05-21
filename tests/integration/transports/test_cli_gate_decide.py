from __future__ import annotations

from uuid import UUID

import pytest

from app.gates import clear_resume_registry
from app.marcus.cli.gate_cli import main
from app.parity.contracts import parity_contract
from tests.unit.gates._helpers import sample_verdict


@parity_contract(
    surface_id="cli_gate_decide",
    mandatory_transports=["cli"],
    optional_transports=[],
)
def _parity_contract_registration() -> str:
    """Module-level parity-contract registration for test_cli_gate_decide.py."""
    return "cli_gate_decide"


def test_cli_gate_decide_happy_path(capsys) -> None:
    clear_resume_registry()
    verdict = sample_verdict(trial_id=UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"))
    exit_code = main(
        [
            "decide",
            "--trial-id",
            str(verdict.trial_id),
            "--gate-id",
            verdict.gate_id,
            "--verb",
            verdict.verb,
            "--card-id",
            str(verdict.card_id),
            "--decision-card-digest",
            verdict.decision_card_digest,
            "--operator-id",
            "cli-user",
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "\"operator_id\": \"cli-user\"" in captured.out


def test_cli_gate_decide_invalid_args() -> None:
    with pytest.raises(SystemExit):
        main(["decide", "--trial-id", "only-one-arg"])
