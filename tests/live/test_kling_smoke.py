from __future__ import annotations

from collections.abc import Callable

import pytest

pytestmark = [pytest.mark.live, pytest.mark.timeout(15)]


def test_kling_capability_smoke(
    env_value: Callable[..., str | dict[str, str]],
    timed_call: Callable,
) -> None:
    """One cheap status probe against a nonexistent task; no generation."""

    creds = env_value("KLING_ACCESS_KEY", "KLING_SECRET_KEY")

    def _call() -> object:
        import requests

        from scripts.api_clients.kling_client import KLING_BASE_URL, generate_jwt_token

        token = generate_jwt_token(
            creds["KLING_ACCESS_KEY"],
            creds["KLING_SECRET_KEY"],
        )
        return requests.get(
            f"{KLING_BASE_URL}/v1/videos/text2video/smoke-test-nonexistent",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )

    response, _elapsed = timed_call(_call)
    assert response.status_code in {200, 400, 404}, response.text
    assert isinstance(response.json(), dict)
