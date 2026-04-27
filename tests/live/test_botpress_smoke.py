from __future__ import annotations

from collections.abc import Callable

import pytest

pytestmark = [pytest.mark.live, pytest.mark.timeout(15)]


def test_botpress_bot_list_smoke(
    env_value: Callable[..., str | dict[str, str]],
    timed_call: Callable,
) -> None:
    """One cheap bot-list reachability call; no bot mutation."""

    env_value("BOTPRESS_API_KEY")

    def _call() -> dict[str, object]:
        from scripts.api_clients.botpress_client import BotpressClient

        return BotpressClient().check_connectivity()

    payload, _elapsed = timed_call(_call)
    assert payload["reachable"] is True
    assert int(payload["status_code"]) < 500
    assert str(payload["url"]).startswith("http")
