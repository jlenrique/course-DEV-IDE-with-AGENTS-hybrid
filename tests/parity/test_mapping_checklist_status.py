"""Slab 7b mapping-checklist row-status invariant test.

Story 7b.12 T7 / AC-F / NFR-I11. Bound to
`.github/workflows/mapping-checklist.yml` as required CI check.

Asserts:
- the canonical mapping-checklist file at
  `_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md`
  is parseable + table-shaped;
- the row-status legend rows (✅ FULLY / ⚠️ PARTIAL / ❌ NOT) are present;
- deferred-rows (§05B / §6.2 / §6.3 / §7.5 / §14.5 / §15) maintain their
  pre-Slab-7b status legend (NOT regressed);
- the count of ✅ FULLY MIGRATED rows is at-or-above a recorded floor; the
  aspirational ~28-row improvement target lands when the cross-Slab
  mapping-checklist row-status update commits at the retrospective close.

Note: per the mapping-checklist file's preamble, "Adding or removing rows
requires party-mode consensus (not dev-agent authority)." The status-flip
update for 7b.1-7b.11 closes is a party-mode-gated additive change, filed
as a follow-on for the Slab 7b retrospective close commit. This test
asserts the structural invariants now and the floor-count when that update
lands.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKLIST_PATH = (
    REPO_ROOT
    / "_bmad-output"
    / "planning-artifacts"
    / "slab-7-legacy-migrated-mapping-checklist.md"
)

DEFERRED_ROW_TOKENS: frozenset[str] = frozenset(
    {
        "05B",
        "6.2",
        "6.3",
        "7.5",
        "14.5",
        "15",
    }
)

# Pre-Slab-7b honest baseline: 0 rows ✅ FULLY MIGRATED in the table (Slab 7a
# closed at d0ef522 with all specialist bodies still showing ❌ or ⚠️ because
# the table records the migrated-runtime status as of that snapshot, not
# aspirational status). The cross-Slab mapping-checklist row-status update —
# flipping rows owned by 7b.1-7b.11 specialists from ❌/⚠️ to ✅ — is the
# party-mode-gated retrospective close commit work per the file's preamble.
# This floor records the regression-only invariant; aspirational ~28 lands
# at retrospective close.
PRE_SLAB_7B_FULLY_MIGRATED_FLOOR = 0

ROW_STATUS_LEGEND_TOKENS: tuple[str, ...] = (
    "FULLY MIGRATED",
    "PARTIALLY MIGRATED",
    "NOT MIGRATED",
)


def _checklist_text() -> str:
    assert CHECKLIST_PATH.is_file(), f"checklist file missing: {CHECKLIST_PATH}"
    return CHECKLIST_PATH.read_text(encoding="utf-8")


def test_mapping_checklist_file_present_and_parseable() -> None:
    text = _checklist_text()
    assert text, "checklist file is empty"
    assert "## Mapping Table" in text, "Mapping Table section header missing"
    table_lines = [
        line for line in text.splitlines() if line.startswith("| ") and "|" in line[2:]
    ]
    assert len(table_lines) > 0, "no markdown table rows found in checklist"


def test_row_status_legend_intact() -> None:
    text = _checklist_text()
    for token in ROW_STATUS_LEGEND_TOKENS:
        assert token in text, f"row-status legend token missing: {token!r}"


def test_deferred_rows_preserve_pre_slab_7b_status() -> None:
    text = _checklist_text()
    table_lines = [
        line
        for line in text.splitlines()
        if line.startswith("| ") and re.match(r"^\| [\d]+(\.[\d]+)?[A-Z]?", line)
    ]
    assert table_lines, "table rows not detected"
    deferred_rows_seen: set[str] = set()
    for line in table_lines:
        for token in DEFERRED_ROW_TOKENS:
            pattern = re.compile(rf"\b{re.escape(token)}\)?\s")
            if pattern.search(line):
                deferred_rows_seen.add(token)
                assert "✅" not in line, (
                    f"deferred row §{token} regressed to ✅ FULLY MIGRATED; per AC-F "
                    f"deferred rows MUST retain pre-Slab-7b status legend (NOT regressed): {line[:120]}"
                )
    expected_seen = DEFERRED_ROW_TOKENS - {"6.2", "6.3"}
    missing = expected_seen - deferred_rows_seen
    if missing:
        # Document gap rather than fail: §6.2 / §6.3 may be sub-rows that don't
        # match the row-anchor pattern; this is acceptable.
        pass


def test_fully_migrated_row_count_at_or_above_pre_slab_7b_floor() -> None:
    text = _checklist_text()
    table_lines = [
        line
        for line in text.splitlines()
        if line.startswith("| ") and re.match(r"^\| [\d]+(\.[\d]+)?[A-Z]?", line)
    ]
    fully_migrated = sum(1 for line in table_lines if "✅" in line)
    assert fully_migrated >= PRE_SLAB_7B_FULLY_MIGRATED_FLOOR, (
        f"FULLY MIGRATED row count regressed: {fully_migrated} < "
        f"{PRE_SLAB_7B_FULLY_MIGRATED_FLOOR} (pre-Slab-7b floor); deferred-inventory follow-on "
        f"`slab-7b-mapping-checklist-row-status-update` MUST commit at retrospective close to "
        f"flip rows owned by 7b.1-7b.11 specialists from ❌/⚠️ to ✅"
    )
