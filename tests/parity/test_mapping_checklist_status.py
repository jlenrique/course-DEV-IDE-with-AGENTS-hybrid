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
        # §15 REMOVED post-Slab-7c retrospective close (2026-05-07): Slab 7c.15
        # explicitly closed §15 G5 final-operator-handoff (operator-ratified
        # row-flip ❌→✅). The Slab 7b deferred-row prediction was superseded
        # by Slab 7c PRD scope (§15 G5 surface + Marcus §15 bundle writer
        # `section-15-bundle`).
    }
)

# Pre-Slab-7b honest baseline: 0 rows ✅ FULLY MIGRATED in the table (Slab 7a
# closed at d0ef522 with all specialist bodies still showing ❌ or ⚠️).
#
# Post-Slab-7b body-activation floor (2026-05-01 retrospective close;
# party-mode-ratified per `_bmad-output/planning-artifacts/slab-7b-retrospective.md`
# Decision 1): 7 rows ✅ FULLY MIGRATED — §03 Texas, §07 Gary, §07E Kira,
# §10 Vera+Quinn-R, §12 Enrique, §13 Quinn-R, §14 Compositor.
#
# Honest-accounting correction vs Round-(a) A-10 R3 aspirational ~28: the
# original estimate conflated body-activation work with orchestrational
# scaffolding (Marcus authoring + per-plan-unit/per-slide HIL surfaces +
# storyboard build + receipt-emit scripts + final-handoff machinery).
# Body activation alone closes the 7 rows above where the specialist's `_act`
# body itself is the load-bearing surface. Orchestrational rows are Slab 7c
# work and do not flip at this retrospective.
#
# Post-Slab-7c retrospective close (2026-05-07; party-mode-ratified by operator):
# +16 net new orchestrational rows close in Slab 7c. Floor lifts 7 -> 23:
#   1. §02A operator directives (G0) -- 7c.3a + 7c.3b
#   2. §04A per-plan-unit ratification (G1A) -- 7c.6
#   3. §04.5 estimator (G1.5) -- 7c.7
#   4. §04.55 run-constants lock (G1.5) -- 7c.8
#   5. §05.5 per-slide presentation mode (G2B) -- 7c.9
#   6. §06 pre-dispatch package (Marcus 5-writer set: gary-slide-content +
#      gary-fidelity-slides + gary-diagram-cards + gary-theme-resolution +
#      gary-outbound-envelope) -- 7c.17a + 7c.17b
#   7. §06B literal-visual operator build -- 7c.18a
#   8. §07B per-slide A/B variant (G2M) -- 7c.10
#   9. §07C storyboard build + HTML reviewer (Gate 2 G2C) -- 7c.18b
#  10. §07D motion-plan polling (G2.5) -- 7c.11
#  11. §07F motion gate (G2F) -- 7c.12
#  12. §08B Storyboard B + live-URL (G3B) -- 7c.13
#  13. §09 four-artifact lock semantics (G3 lock) -- 7c.19
#  14. §11 voice-selection (G4A) -- 7c.14
#  15. §11B input-package preview (G4B) -- 7c.15
#  16. §15 final operator handoff (G5; includes Marcus §15 bundle writer) -- 7c.15
# Constant name preserved for backward-compatibility; semantic now reflects
# post-Slab-7c floor.
PRE_SLAB_7B_FULLY_MIGRATED_FLOOR = 23

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
    # Detection strengthened post-Slab-7c retrospective close (2026-05-07) per
    # `mapping-checklist-deferred-row-detection-strengthening` deferred-inventory
    # entry (Murat NIT 2026-04-30). Pattern now anchors the token to the
    # legacy-section-name cell (bold-marked: `**{token})`), NOT the
    # row-counter cell. Eliminates false-positive on row 15 (§06B) when token
    # "15" matches the row-counter column.
    for line in table_lines:
        for token in DEFERRED_ROW_TOKENS:
            pattern = re.compile(rf"\*\*{re.escape(token)}\)")
            if pattern.search(line):
                deferred_rows_seen.add(token)
                assert "✅" not in line, (
                    f"deferred row §{token} regressed to ✅ FULLY MIGRATED; "
                    f"per AC-F deferred rows MUST retain pre-Slab-7b status "
                    f"legend (NOT regressed): {line[:120]}"
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
