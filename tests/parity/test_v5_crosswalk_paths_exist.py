"""Crosswalk-vs-disk parity test for production-prompt-pack-v5 (Murat post-S4 amendment #2).

Asserts that every path-string in the v5 TL;DR Crosswalk's "Marcus module" column
resolves to an actual file (or directory) on disk. Catches Crosswalk drift the
moment it surfaces — prevents the failure mode Murat surfaced at post-S4 review
where 2/6 spot-checked paths were stale (§02A composer; §06 writer aggregator).

Excluded: rows explicitly marked `(placeholder; NOT MIGRATED - see deferred-inventory)`
or `(PARTIAL;` or `(body absent;` — these are operator-known deferred placeholders.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
V5_PACK = (
    REPO_ROOT
    / "docs"
    / "workflow"
    / "production-prompt-pack-v5-narrated-lesson-with-video-or-animation.md"
)


def _extract_crosswalk_paths() -> list[tuple[str, str]]:
    """Return list of (section_id, path_string) tuples from the v5 TL;DR Crosswalk."""
    text = V5_PACK.read_text(encoding="utf-8")
    crosswalk_start = text.index("## 0) TL;DR Crosswalk")
    next_header = text.index("## 0.5)", crosswalk_start)
    crosswalk_block = text[crosswalk_start:next_header]

    rows: list[tuple[str, str]] = []
    for line in crosswalk_block.splitlines():
        if not line.startswith("| "):
            continue
        if "Marcus module" in line or "---" in line:
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) < 3:
            continue
        section_id, _, path_cell, *_ = cells
        if section_id.lower() in {"pack §", "pack §"} or section_id == "":
            continue
        # Skip explicit placeholders + PARTIAL / body-absent markers
        if "placeholder" in path_cell.lower() or "PARTIAL" in path_cell or "body absent" in path_cell.lower():
            continue
        # Extract path tokens — split on `+` for multi-path rows
        # Path tokens look like `app/.../foo.py` or `app/.../{a,b,c}.py` for brace-expansion
        for token in re.split(r"\s*\+\s*", path_cell):
            token = token.strip()
            # Strip trailing parenthetical comments like " (Class-C two-SKILL.md; 7b.6)"
            token = re.sub(r"\s*\([^)]*\)\s*$", "", token).strip()
            if not token:
                continue
            # Brace-expansion: writers/{a, b, c}.py → 3 paths
            brace_match = re.match(r"^(.+/)\{([^}]+)\}\.py$", token)
            if brace_match:
                base = brace_match.group(1)
                names = [n.strip() for n in brace_match.group(2).split(",")]
                for name in names:
                    rows.append((section_id, f"{base}{name}.py"))
            else:
                rows.append((section_id, token))
    return rows


def test_v5_crosswalk_paths_resolve_on_disk() -> None:
    """Every Crosswalk path token must exist on disk (file OR directory)."""
    rows = _extract_crosswalk_paths()
    assert rows, "Crosswalk extraction returned zero paths — parser drift?"

    missing: list[tuple[str, str]] = []
    for section_id, path_str in rows:
        # Some path tokens reference SKILL.md files under skills/; others reference
        # python source files under app/. Both should exist as files.
        target = REPO_ROOT / path_str
        if not target.exists():
            missing.append((section_id, path_str))

    assert not missing, (
        f"v5 Crosswalk has {len(missing)} stale path(s) — Crosswalk-vs-disk drift detected:\n"
        + "\n".join(f"  §{s}: {p}" for s, p in missing)
    )
