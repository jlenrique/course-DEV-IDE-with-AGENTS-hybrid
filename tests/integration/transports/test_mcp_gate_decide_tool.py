from __future__ import annotations

from uuid import UUID

from tests.integration.transports._helpers import submit_mcp


def test_mcp_gate_decide_tool() -> None:
    response = submit_mcp(
        trial_id=UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"),
        operator_id="mcp-user",
    )
    assert response["status"] == "accepted"
    assert response["resume"]["operator_id"] == "mcp-user"
