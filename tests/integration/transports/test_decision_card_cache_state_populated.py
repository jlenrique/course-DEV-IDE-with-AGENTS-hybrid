from __future__ import annotations

from uuid import UUID

import pytest

from tests.integration.transports._helpers import submit_cli, submit_http, submit_mcp


@pytest.mark.parametrize(
    ("adapter", "operator_id"),
    [
        (submit_mcp, "mcp-user"),
        (submit_http, "http-user"),
        (submit_cli, "cli-user"),
    ],
)
def test_decision_card_cache_state_populated(adapter, operator_id: str) -> None:
    response = adapter(
        trial_id=UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"),
        operator_id=operator_id,
    )
    if "body" in response:
        response = response["body"]
    assert response["decision_card_meta"]["cache_state"] in {"healthy", "mixed", "cold"}
