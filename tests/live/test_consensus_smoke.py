from __future__ import annotations

from collections.abc import Callable

import pytest

pytestmark = [pytest.mark.live, pytest.mark.timeout(15)]


def test_consensus_quota_smoke(
    env_value: Callable[..., str | dict[str, str]],
    timed_call: Callable,
) -> None:
    """One cheap MCP tools/quota reachability call; no search query."""

    env_value("CONSENSUS_API_KEY")

    def _call() -> list[dict[str, object]]:
        from retrieval.mcp_client import MCPClient, MCPServerConfig

        client = MCPClient(
            {
                "consensus": MCPServerConfig(
                    url="https://mcp.consensus.app/mcp",
                    auth_env=["CONSENSUS_API_KEY"],
                    auth_style="bearer",
                )
            }
        )
        return client.list_tools("consensus")

    tools, _elapsed = timed_call(_call)
    assert isinstance(tools, list)
    assert tools
    assert all(isinstance(tool, dict) for tool in tools)
