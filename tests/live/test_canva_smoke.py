from __future__ import annotations

from collections.abc import Callable

import pytest

pytestmark = [pytest.mark.live, pytest.mark.timeout(15)]


def test_canva_auth_smoke(
    env_value: Callable[..., str | dict[str, str]],
    timed_call: Callable,
) -> None:
    """One cheap current-user auth check; no design mutation."""

    access_token = env_value("CANVA_ACCESS_TOKEN")

    def _call() -> object:
        import requests

        return requests.get(
            "https://api.canva.com/rest/v1/users/me",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )

    response, _elapsed = timed_call(_call)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert isinstance(payload, dict)
    assert payload.get("user_id") or payload.get("team_id")
