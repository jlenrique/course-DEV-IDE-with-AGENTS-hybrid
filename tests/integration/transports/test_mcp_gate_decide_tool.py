from __future__ import annotations

from uuid import UUID

from app.parity.contracts import parity_contract
from tests.integration.transports._helpers import submit_mcp


@parity_contract(
    surface_id="mcp_gate_decide_tool",
    mandatory_transports=["mcp-stdio"],
    optional_transports=[],
)
def _parity_contract_registration() -> str:
    """Module-level parity-contract registration for test_mcp_gate_decide_tool.py."""
    return "mcp_gate_decide_tool"


def test_mcp_gate_decide_tool() -> None:
    response = submit_mcp(
        trial_id=UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"),
        operator_id="mcp-user",
    )
    assert response["status"] == "accepted"
    assert response["resume"]["operator_id"] == "mcp-user"
