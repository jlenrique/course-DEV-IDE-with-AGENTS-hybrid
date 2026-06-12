"""Composition-spec docs-version lockstep pin (drift micro-batch 2026-06-12).

The dev-guide contract doc described production-envelope.v1 + "first
contribution wins" for ~6 weeks after the live code moved to v2 per-node
keying with retry-overwrite — opposite semantics for duplicate
contributions, and exactly the artifact-vs-reality divergence class that
produced the G2C VOID. Murat's ruling: a contract doc the build cannot
catch lying is a rumor, not a contract.

Rules pinned here:
1. The CURRENT envelope version token (read from the code constant, not
   hardcoded twice) must appear in the doc.
2. Any line mentioning the retired v1 token WITHOUT the current token must
   sit inside a RETIRED-HISTORY fence. (The as-built §3.1 snippet shows the
   dual literal — v1 stays parseable for legacy reads — so dual-mention
   lines are current truth, not history.)
3. The retired "first contribution wins" semantics may be named only
   inside RETIRED-HISTORY fences.
"""

from __future__ import annotations

import re
from pathlib import Path

from app.models.runtime.production_envelope import ProductionEnvelope

REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC = REPO_ROOT / "docs" / "dev-guide" / "composition-specification.md"

FENCE_BEGIN = "<!-- RETIRED-HISTORY:BEGIN -->"
FENCE_END = "<!-- RETIRED-HISTORY:END -->"
RETIRED_TOKEN = "production-envelope.v1"
FCW_PATTERN = re.compile(r"first[ -]contribution[ -]wins|first contribution wins", re.IGNORECASE)


def _current_token() -> str:
    return ProductionEnvelope.model_fields["schema_version"].default


def _fence_state_per_line(text: str) -> list[tuple[int, str, bool]]:
    rows: list[tuple[int, str, bool]] = []
    inside = False
    for idx, line in enumerate(text.splitlines(), start=1):
        if FENCE_BEGIN in line:
            inside = True
        rows.append((idx, line, inside))
        if FENCE_END in line:
            inside = False
    return rows


def test_spec_doc_carries_current_envelope_version_token() -> None:
    token = _current_token()
    assert token == "production-envelope.v2"  # belt: the constant itself moved as expected
    assert token in SPEC.read_text(encoding="utf-8"), (
        f"{SPEC.name} does not mention the current envelope version {token!r} — "
        "the envelope version bumped without a doc touch (lockstep broken)"
    )


def test_retired_v1_token_confined_to_history_fences() -> None:
    token = _current_token()
    offenders = [
        f"{SPEC.name}:{idx}: {line.strip()[:100]}"
        for idx, line, inside in _fence_state_per_line(SPEC.read_text(encoding="utf-8"))
        if RETIRED_TOKEN in line and token not in line and not inside
    ]
    assert offenders == [], (
        "retired envelope token outside RETIRED-HISTORY fences (and not on a "
        f"dual-literal as-built line): {offenders}"
    )


def test_retired_first_contribution_wins_confined_to_history_fences() -> None:
    offenders = [
        f"{SPEC.name}:{idx}: {line.strip()[:100]}"
        for idx, line, inside in _fence_state_per_line(SPEC.read_text(encoding="utf-8"))
        if FCW_PATTERN.search(line) and not inside
    ]
    assert offenders == [], (
        "retired 'first contribution wins' semantics described outside "
        f"RETIRED-HISTORY fences: {offenders}"
    )


def test_history_fences_are_balanced() -> None:
    text = SPEC.read_text(encoding="utf-8")
    assert text.count(FENCE_BEGIN) == text.count(FENCE_END) >= 1
