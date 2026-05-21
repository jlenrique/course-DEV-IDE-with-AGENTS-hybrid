from __future__ import annotations

from collections.abc import Callable

import pytest

pytestmark = [pytest.mark.live, pytest.mark.timeout(15)]


def test_qualtrics_survey_list_smoke(
    env_value: Callable[..., str | dict[str, str]],
    qualtrics_base_url: str,
    timed_call: Callable,
) -> None:
    """One cheap survey-list call; no survey mutation."""

    api_token = env_value("QUALTRICS_API_TOKEN")

    def _call() -> object:
        import requests

        return requests.get(
            f"{qualtrics_base_url}/API/v3/surveys",
            headers={"X-API-TOKEN": api_token},
            params={"pageSize": 1},
            timeout=10,
        )

    response, _elapsed = timed_call(_call)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert isinstance(payload, dict)
    assert isinstance(payload.get("result", {}).get("elements", []), list)
