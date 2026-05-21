from __future__ import annotations

from collections.abc import Callable

import pytest

pytestmark = [pytest.mark.live, pytest.mark.timeout(15)]


def test_notion_workspace_info_smoke(
    env_value: Callable[..., str | dict[str, str]],
    timed_call: Callable,
) -> None:
    """One cheap current-user/workspace auth check; no page mutation."""

    api_key = env_value("NOTION_API_KEY")

    def _call() -> object:
        import requests

        return requests.get(
            "https://api.notion.com/v1/users/me",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Notion-Version": "2026-03-11",
            },
            timeout=10,
        )

    response, _elapsed = timed_call(_call)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert isinstance(payload, dict)
    assert payload.get("object") == "user"
    assert payload.get("id")
