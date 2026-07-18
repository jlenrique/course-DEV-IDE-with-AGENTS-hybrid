"""Integration + live + retention guards for the status-surface consolidation.

These tests bridge the two generators and the ``progress_map`` consumer, and
pin two live-repo invariants surfaced by the 6-reviewer party:

* T-int  — a generated ``next-session-start-here.md`` parses NON-EMPTY through
  ``progress_map._extract_section`` for BOTH shared heading constants.
* T-live — the REAL repo ``SESSION-HANDOFF.md`` current section parses
  NON-EMPTY (guards the case-insensitive silent-drop from recurring).
* T-retention — a tripwire that the three hot SSOTs stay trimmed and carry a
  resolvable ``History archived to`` pointer to an existing sibling.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

from scripts.utilities import progress_map as pm
from scripts.utilities.progress_map import (
    IMMEDIATE_NEXT_ACTION_HEADING,
    KEY_RISKS_HEADING,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_generate_next_session():
    path = _REPO_ROOT / "scripts" / "utilities" / "generate_next_session.py"
    spec = importlib.util.spec_from_file_location("generate_next_session", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_HANDOFF = """\
# Session close 2026-07-17 (NIGHT) — latest

## What is next

1. Run the fresh session's first action.

## Unresolved issues / risks

- A carried risk to watch.
"""

_DEFERRED = """\
# Deferred Inventory

| Epic | Focus | Stories | Count | Trigger |
|---|---|---|---|---|
| **Epic 15** | Learning | 15-1 | 1 | trigger |
"""


# ── T-int (Murat #1): generated view round-trips through the consumer ────────


def test_generated_next_session_parses_through_progress_map(tmp_path, monkeypatch):
    gen = _load_generate_next_session()
    monkeypatch.setenv(gen._ENV_BRANCH, "trial/test-branch")
    monkeypatch.setenv(gen._ENV_HEAD, "abc1234")

    root = tmp_path / "repo"
    (root / "_bmad-output" / "planning-artifacts").mkdir(parents=True)
    (root / "SESSION-HANDOFF.md").write_text(_HANDOFF, encoding="utf-8")
    (root / "_bmad-output" / "planning-artifacts" / "deferred-inventory.md").write_text(
        _DEFERRED, encoding="utf-8"
    )

    assert gen.main(["--root", str(root)]) == 0
    target = root / "next-session-start-here.md"

    # Both shared heading constants (P2) resolve NON-EMPTY through the consumer.
    for key in (IMMEDIATE_NEXT_ACTION_HEADING, KEY_RISKS_HEADING):
        extracted = pm._extract_section(target, key)
        assert extracted.strip(), f"progress_map extracted nothing for '{key}'"


# ── T-live (Murat #2): the real handoff current section still parses ─────────


def test_real_session_handoff_current_section_parses_non_empty():
    """Guards the live silent-drop: sentence-case headings must still match."""
    if not pm.SESSION_HANDOFF.exists():
        pytest.skip("SESSION-HANDOFF.md not present in this checkout")
    what_next = pm._extract_section(pm.SESSION_HANDOFF, "What Is Next")
    unresolved = pm._extract_section(pm.SESSION_HANDOFF, "Unresolved Issues")
    assert what_next.strip(), "real SESSION-HANDOFF '## What is next' parsed empty"
    assert unresolved.strip(), "real SESSION-HANDOFF '## Unresolved issues' parsed empty"


# ── T-retention (Murat #3): re-accretion tripwire + resolvable pointer ───────

# Ceilings ~3x current size so the tripwire only fires on real re-accretion.
_RETENTION_CEILINGS = {
    "SESSION-HANDOFF.md": 60_000,
    "docs/STATE-OF-THE-APP.md": 200_000,
    "docs/project-context.md": 300_000,
}

_HISTORY_TOKEN_RE = re.compile(r"([\w.\-]+\.history\.md)")


@pytest.mark.parametrize("rel_path, ceiling", sorted(_RETENTION_CEILINGS.items()))
def test_hot_ssot_stays_trimmed_and_points_to_existing_sibling(rel_path, ceiling):
    path = _REPO_ROOT / rel_path
    if not path.exists():
        pytest.skip(f"{rel_path} not present in this checkout")

    size = path.stat().st_size
    assert size < ceiling, (
        f"{rel_path} is {size} bytes (ceiling {ceiling}) — history has "
        "re-accreted into the hot file; run the WRAPUP arc-close roll-down."
    )

    text = path.read_text(encoding="utf-8")
    # At least one 'archived to … <file>.history.md' line must resolve to an existing
    # sibling. Scan ALL candidate lines rather than assuming the first is the pointer —
    # prose that merely mentions *.history.md files (e.g. an addendum listing archives)
    # names non-existent tokens and is harmlessly skipped; the real pointer resolves.
    candidates = [
        ln for ln in text.splitlines() if "archived to" in ln.lower() and ".history.md" in ln
    ]
    assert candidates, f"{rel_path} has no 'archived to …' history pointer"
    resolved = any(
        (path.parent / Path(tok).name).exists()
        for ln in candidates
        for tok in _HISTORY_TOKEN_RE.findall(ln)
    )
    assert resolved, (
        f"{rel_path} has no 'archived to …' pointer resolving to an existing "
        "*.history.md sibling"
    )
