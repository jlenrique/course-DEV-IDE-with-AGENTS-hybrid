from __future__ import annotations

from uuid import UUID

from app.parity.contracts import parity_contract
from tests.integration.transports._helpers import (
    normalize_response,
    submit_cli,
    submit_http,
    submit_mcp,
)


@parity_contract(
    surface_id="transport_parity",
    mandatory_transports=["cli", "http", "mcp-stdio"],
    optional_transports=[],
)
def _parity_contract_registration() -> str:
    """Module-level parity-contract registration for test_transport_parity.py."""
    return "transport_parity"


def _responses() -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    operator_id = "shared-operator"
    trial_id = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
    mcp = submit_mcp(trial_id=trial_id, operator_id=operator_id)
    http = submit_http(trial_id=trial_id, operator_id=operator_id)["body"]
    cli = submit_cli(trial_id=trial_id, operator_id=operator_id)
    return mcp, http, cli


def test_transport_parity_resume_state() -> None:
    mcp, http, cli = _responses()
    assert mcp["resume"] == http["resume"] == cli["resume"]


def test_transport_parity_ledger_equivalence() -> None:
    mcp, http, cli = _responses()
    for response in (mcp, http, cli):
        response["ledger_event"].pop("transport_kind", None)
    assert mcp["ledger_event"] == http["ledger_event"] == cli["ledger_event"]


def test_transport_parity_trace_equivalence() -> None:
    mcp, http, cli = _responses()
    normalized = [normalize_response(response) for response in (mcp, http, cli)]
    for response in normalized:
        response["trace"]["span_attributes"].pop("transport_kind", None)
    assert normalized[0]["trace"] == normalized[1]["trace"] == normalized[2]["trace"]
