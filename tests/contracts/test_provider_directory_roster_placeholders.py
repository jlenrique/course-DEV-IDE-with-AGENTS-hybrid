"""AC-T.11 — Roster placeholders surface in the provider directory.

Epic 27 ratified-stub providers and the operator-directed `openai_chatgpt`
backlog placeholder MUST appear in the directory even when no adapter class
has been authored yet. This prevents silent-drop — a story can go live-then-
removed without the directory catching the absence.
"""

from __future__ import annotations

import pytest
from retrieval import get_provider, list_providers


@pytest.mark.parametrize(
    "provider_id,expected_shape,expected_status",
    [
        # Story 27-2 (2026-04-18): scite adapter shipped; live PROVIDER_INFO
        # supersedes the placeholder, so status flips `ratified` → `ready`.
        # Supersession is the merge-order contract in provider_directory.py
        # lines 265-273 (registered-first, placeholder-second). Every future
        # retrieval-shape story will flip its row here the same way.
        ("scite", "retrieval", "ready"),
        # Story 27-2.5: ConsensusProvider adapter shipped (absorbed at
        # severance, 835e6503) -> live PROVIDER_INFO supersedes the
        # placeholder, ratified -> ready (same supersession contract as
        # scite above). Repin per contracts-triage-ledger-2026-07-02 row 15.
        ("consensus", "retrieval", "ready"),
        ("jefferson_library", "retrieval", "ready"),
        ("image", "retrieval", "ratified"),
        ("youtube", "retrieval", "ratified"),
        ("openai_chatgpt", "retrieval", "backlog"),
        ("notion_mcp", "locator", "ratified"),
        ("box_api", "locator", "ratified"),
        ("playwright_mcp", "locator", "ratified"),
    ],
)
def test_roster_placeholder_present_with_expected_status(
    provider_id: str, expected_shape: str, expected_status: str
) -> None:
    info = get_provider(provider_id)
    assert info is not None, (
        f"Roster placeholder {provider_id!r} missing from provider directory. "
        f"Add an entry to provider_directory.py — this is a silent-drop guard."
    )
    assert info.shape == expected_shape
    assert info.status == expected_status


def test_openai_chatgpt_placeholder_names_operator_directive() -> None:
    """The backlog entry must carry the operator-directive breadcrumb."""
    info = get_provider("openai_chatgpt")
    assert info is not None
    assert "operator directive" in info.notes.lower()


def test_backlog_entries_isolated_by_status_filter() -> None:
    """`status='backlog'` surfaces only the forward-looking placeholders."""
    backlog = list_providers(status="backlog")
    assert len(backlog) >= 1
    assert all(p.status == "backlog" for p in backlog)
    assert any(p.id == "openai_chatgpt" for p in backlog)
