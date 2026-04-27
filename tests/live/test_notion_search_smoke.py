"""Notion search-pages live smoke test (operator-confirmed pattern).

Mirrors the operator's M3 Texas ceremony pattern (`scripts/operator/m3_texas_ceremony_notion.py`)
that closed M5 condition #2 on 2026-04-27. The ceremony exercised
`NotionClient.search_pages(query="", page_size=5)` and got 1 real page back
from the operator's workspace — proving end-to-end auth + endpoint + response
shape work as authored.

This live-smoke test mirrors that pattern so future runs catch any regression
in NotionClient against the real Notion API. Sibling to `test_notion_smoke.py`
which does the lighter `/users/me` auth-only check.

Note: returns may be empty (`len(pages) == 0`) if the operator's Notion
integration has no pages shared with it. That's NOT a test failure — auth
worked + the API responded. Operator-decision: share at least one page with
the integration in the Notion UI for richer smoke evidence.
"""

from __future__ import annotations

from collections.abc import Callable

import pytest

pytestmark = [pytest.mark.live, pytest.mark.timeout(15)]


def test_notion_search_pages_smoke(
    env_value: Callable[..., str | dict[str, str]],
    timed_call: Callable,
) -> None:
    """One cheap empty-query search; auth + endpoint + response shape verified."""

    env_value("NOTION_API_KEY")  # skip if absent

    from scripts.api_clients.notion_client import NotionClient

    client = NotionClient()

    def _call() -> object:
        return client.search_pages(query="", page_size=5)

    pages, _elapsed = timed_call(_call)
    assert isinstance(pages, list), f"search_pages must return list, got {type(pages).__name__}"
    # Pages may be empty if integration has no shared pages — that's fine.
    # If non-empty, validate response shape per Notion API v1 spec.
    if pages:
        first = pages[0]
        assert isinstance(first, dict)
        assert first.get("object") == "page"
        assert first.get("id"), "Notion page must have an id"
