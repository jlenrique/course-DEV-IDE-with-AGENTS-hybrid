from __future__ import annotations

from collections.abc import Callable

import pytest

pytestmark = [pytest.mark.live, pytest.mark.timeout(15)]


def test_wondercraft_account_smoke(
    env_value: Callable[..., str | dict[str, str]],
    timed_call: Callable,
) -> None:
    """One cheap account/capability reachability call; no generation."""

    env_value("WONDERCRAFT_API_KEY")

    def _call() -> dict[str, object]:
        from scripts.api_clients.wondercraft_client import WondercraftClient

        return WondercraftClient().check_connectivity()

    payload, _elapsed = timed_call(_call)
    assert payload["reachable"] is True
    assert int(payload["status_code"]) < 500
    assert str(payload["url"]).startswith("http")
