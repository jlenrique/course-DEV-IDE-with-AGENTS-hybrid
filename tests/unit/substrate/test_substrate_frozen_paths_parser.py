"""Boundary tests for substrate-frozen-paths hunk parser.

Story 7b.12 T11 PATCH-4 cycle-1 remediation 2026-04-30. Per Codex T11
review: explicit boundary fixtures for `+70`, `+95`, `+69`, `+96`,
`-70,1 +69,0`, `-95,1 +94,0` to catch off-by-one regressions and
deletion-only-old-range coverage.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = REPO_ROOT / "scripts" / "utilities"
sys.path.insert(0, str(SCRIPTS_DIR))

from check_substrate_frozen_paths import (  # noqa: E402
    FROZEN_RANGE_END,
    FROZEN_RANGE_START,
    collect_hunks_for_path,
    hunk_touches_frozen,
    parse_hunk_header,
)


def test_parse_hunk_with_explicit_count() -> None:
    hunk = parse_hunk_header("@@ -70,5 +70,5 @@")
    assert hunk is not None
    assert hunk.old_start == 70
    assert hunk.old_count == 5
    assert hunk.new_start == 70
    assert hunk.new_count == 5
    assert hunk.old_end == 74
    assert hunk.new_end == 74


def test_parse_hunk_with_implicit_count_one() -> None:
    hunk = parse_hunk_header("@@ -72 +72 @@")
    assert hunk is not None
    assert hunk.old_count == 1
    assert hunk.new_count == 1
    assert hunk.old_end == 72
    assert hunk.new_end == 72


def test_boundary_plus_70_inside() -> None:
    """Single-line edit at line 70 (inside frozen range)."""
    hunk = parse_hunk_header("@@ -70 +70 @@")
    assert hunk is not None
    assert hunk_touches_frozen([hunk], FROZEN_RANGE_START, FROZEN_RANGE_END)


def test_boundary_plus_95_inside() -> None:
    """Single-line edit at line 95 (inside frozen range)."""
    hunk = parse_hunk_header("@@ -95 +95 @@")
    assert hunk is not None
    assert hunk_touches_frozen([hunk], FROZEN_RANGE_START, FROZEN_RANGE_END)


def test_boundary_plus_69_outside() -> None:
    """Single-line edit at line 69 (just outside; below frozen range)."""
    hunk = parse_hunk_header("@@ -69 +69 @@")
    assert hunk is not None
    assert not hunk_touches_frozen([hunk], FROZEN_RANGE_START, FROZEN_RANGE_END)


def test_boundary_plus_96_outside() -> None:
    """Single-line edit at line 96 (just outside; above frozen range)."""
    hunk = parse_hunk_header("@@ -96 +96 @@")
    assert hunk is not None
    assert not hunk_touches_frozen([hunk], FROZEN_RANGE_START, FROZEN_RANGE_END)


def test_deletion_only_at_line_70() -> None:
    """Deletion-only hunk: removes original line 70; new-side reports count 0.

    Pattern `-70,1 +69,0` means "delete 1 line at original 70; nothing on
    new side". The gawk parser would have missed this because it only
    parsed the `+...,...` half. Our parser MUST detect the old-side touch.
    """
    hunk = parse_hunk_header("@@ -70,1 +69,0 @@")
    assert hunk is not None
    assert hunk.old_start == 70
    assert hunk.old_count == 1
    assert hunk.new_count == 0
    assert hunk_touches_frozen([hunk], FROZEN_RANGE_START, FROZEN_RANGE_END)


def test_deletion_only_at_line_95() -> None:
    """Deletion-only at line 95 (top boundary of frozen range)."""
    hunk = parse_hunk_header("@@ -95,1 +94,0 @@")
    assert hunk is not None
    assert hunk_touches_frozen([hunk], FROZEN_RANGE_START, FROZEN_RANGE_END)


def test_pure_addition_at_inserted_line() -> None:
    """Pure addition: original count 0, new lines fall inside frozen range."""
    hunk = parse_hunk_header("@@ -69,0 +70,5 @@")
    assert hunk is not None
    assert hunk.old_count == 0
    assert hunk.new_count == 5
    assert hunk.new_start == 70
    assert hunk.new_end == 74
    assert hunk_touches_frozen([hunk], FROZEN_RANGE_START, FROZEN_RANGE_END)


def test_multi_line_diff_spanning_frozen_range() -> None:
    """Hunk spans frozen range; old + new ranges both detected."""
    hunk = parse_hunk_header("@@ -65,40 +65,40 @@")
    assert hunk is not None
    assert hunk_touches_frozen([hunk], FROZEN_RANGE_START, FROZEN_RANGE_END)


def test_hunk_far_below_frozen_range() -> None:
    """Edit at lines 1-50; should NOT trigger."""
    hunk = parse_hunk_header("@@ -10,40 +10,40 @@")
    assert hunk is not None
    assert not hunk_touches_frozen([hunk], FROZEN_RANGE_START, FROZEN_RANGE_END)


def test_hunk_far_above_frozen_range() -> None:
    """Edit at lines 200+; should NOT trigger."""
    hunk = parse_hunk_header("@@ -200,5 +200,5 @@")
    assert hunk is not None
    assert not hunk_touches_frozen([hunk], FROZEN_RANGE_START, FROZEN_RANGE_END)


def test_collect_hunks_for_path_skips_non_hunk_lines() -> None:
    diff_text = """diff --git a/foo b/foo
index abc..def 100644
--- a/foo
+++ b/foo
@@ -10,1 +10,1 @@
-old
+new
@@ -70,5 +70,5 @@
-old line in frozen
+new line in frozen
"""
    hunks = collect_hunks_for_path(diff_text)
    assert len(hunks) == 2
    assert hunks[0].new_start == 10
    assert hunks[1].new_start == 70
    assert hunk_touches_frozen(hunks, FROZEN_RANGE_START, FROZEN_RANGE_END)


def test_malformed_hunk_header_returns_none() -> None:
    assert parse_hunk_header("not a hunk header") is None
    assert parse_hunk_header("@@ malformed @@") is None
    assert parse_hunk_header("") is None
