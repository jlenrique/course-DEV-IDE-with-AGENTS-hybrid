from __future__ import annotations

from app.parity.contracts import parity_contract
from tests.integration.transports._helpers import (
    apply_override_cli,
    apply_override_http,
    apply_override_mcp,
    submit_override_cli,
    submit_override_http,
    submit_override_mcp,
)


@parity_contract(
    surface_id="override_transport_parity",
    mandatory_transports=["cli", "http", "mcp-stdio"],
    optional_transports=[],
)
def _parity_contract_registration() -> str:
    """Module-level parity-contract registration for test_override_transport_parity.py."""
    return "override_transport_parity"


def test_override_submit_transport_parity() -> None:
    operator_id = "override-user"
    mcp = submit_override_mcp(operator_id=operator_id)
    http = submit_override_http(operator_id=operator_id)["body"]
    cli = submit_override_cli(operator_id=operator_id)

    assert (
        mcp["warning"]["trial_id"]
        == http["warning"]["trial_id"]
        == cli["warning"]["trial_id"]
    )
    assert mcp["warning"]["node_id"] == http["warning"]["node_id"] == cli["warning"]["node_id"]
    assert (
        mcp["warning"]["requested_model"]
        == http["warning"]["requested_model"]
        == cli["warning"]["requested_model"]
    )


def test_override_apply_transport_parity() -> None:
    operator_id = "override-user"
    warning = submit_override_mcp(operator_id=operator_id)["warning"]
    mcp = apply_override_mcp(operator_id=operator_id, confirm_token=warning["confirm_token"])

    warning = submit_override_http(operator_id=operator_id)["body"]["warning"]
    http = apply_override_http(
        operator_id=operator_id,
        confirm_token=warning["confirm_token"],
    )["body"]

    warning = submit_override_cli(operator_id=operator_id)["warning"]
    cli = apply_override_cli(operator_id=operator_id, confirm_token=warning["confirm_token"])

    assert (
        mcp["override_event"]["node_id"]
        == http["override_event"]["node_id"]
        == cli["override_event"]["node_id"]
    )
    assert (
        mcp["decision_card_meta"]["cache_state"]
        == http["decision_card_meta"]["cache_state"]
        == cli["decision_card_meta"]["cache_state"]
        == "mixed"
    )
