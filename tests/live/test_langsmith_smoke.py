from __future__ import annotations

from collections.abc import Callable

import pytest

pytestmark = [pytest.mark.live, pytest.mark.timeout(15)]


def test_langsmith_projects_smoke(
    env_value: Callable[..., str | dict[str, str]],
    timed_call: Callable,
) -> None:
    api_key = env_value("LANGSMITH_API_KEY")

    def _call() -> list[object]:
        from langsmith import Client

        client = Client(api_key=api_key)
        return list(client.list_projects(limit=1))

    projects, _elapsed = timed_call(_call)
    assert isinstance(projects, list)
    if projects:
        first = projects[0]
        assert getattr(first, "id", None) or getattr(first, "name", None)
