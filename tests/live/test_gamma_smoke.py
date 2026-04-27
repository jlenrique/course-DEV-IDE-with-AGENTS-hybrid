from __future__ import annotations

from collections.abc import Callable

import pytest

pytestmark = [pytest.mark.live, pytest.mark.timeout(15)]


def test_gamma_capability_smoke(
    env_value: Callable[..., str | dict[str, str]],
    timed_call: Callable,
) -> None:
    """One cheap capability list call; no generation."""

    env_value("GAMMA_API_KEY")

    def _call() -> list[dict[str, object]]:
        from scripts.api_clients.gamma_client import GammaClient

        return GammaClient().list_themes(limit=1)

    themes, _elapsed = timed_call(_call)
    assert isinstance(themes, list)
    if themes:
        first = themes[0]
        assert isinstance(first, dict)
        assert first.get("id") or first.get("name")
