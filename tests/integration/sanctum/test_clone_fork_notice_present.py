"""Sanctum CLONE-FORK-NOTICE.md presence test.

Skips:
- `_archive/` and any other underscore-prefixed sibling dir (operator-managed
  archive locations created during sanctum-ceremony transitions; e.g.,
  `_bmad/memory/_archive/bmad-agent-content-creator-pre-2a2-*/` from Story 2a.2
  pre-T1 sanctum clear per D2 SYNTHESIS).
- Empty sanctum dirs (activation-baseline epoch per
  `docs/dev-guide/sanctum-reference-conventions.md §3`; e.g., the
  `bmad-agent-content-creator/` sanctum that's empty for Story 2a.2's
  cache-hit-rate baseline measurement window).
"""

from pathlib import Path


def test_clone_fork_notice_present_for_all_sanctum_dirs() -> None:
    memory_root = Path("_bmad/memory")
    sanctum_dirs = [
        p
        for p in memory_root.iterdir()
        if p.is_dir() and not p.name.startswith("_")
    ]

    missing = [
        p.name
        for p in sanctum_dirs
        if any(p.iterdir())  # non-empty sanctum (steady-state epoch)
        and not (p / "CLONE-FORK-NOTICE.md").is_file()
    ]

    assert not missing, (
        f"Missing CLONE-FORK-NOTICE.md for: {', '.join(sorted(missing))}. "
        "Empty sanctum dirs (activation-baseline epoch per "
        "docs/dev-guide/sanctum-reference-conventions.md) are exempt; only "
        "populated sanctums must carry the notice."
    )
