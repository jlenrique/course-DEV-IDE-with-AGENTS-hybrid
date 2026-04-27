"""Lint guard — prevent fictitious OpenAI model IDs from re-entering the codebase.

Per 2026-04-26 substrate-aware remediation (post-Slab-5a): the cost-engineering
substrate had been seeded with fictitious OpenAI model IDs that propagated via
scaffold templates and survived multi-agent review because the tokens parse,
lint, and type-check cleanly. The 6-agent M5 SHIP-CONDITIONAL verdict, the
15-invariant audit matrix, and the 5a.3 cost-engineering close all passed
without anyone calling the OpenAI API to verify the IDs were real.

This test scans production-code surfaces for known fictitious IDs. Test
fixtures and historical migration artifacts are excluded — fixtures sometimes
intentionally pin specific strings for behavior tests (per Murat's perturbation
discipline), and migration story specs in `_bmad-output/` are records of what
was decided at the time and must not be retroactively edited.

Real OpenAI catalog (April 2026): `gpt-5`, `gpt-5-mini`, `gpt-5-nano`,
`gpt-4.1`, `gpt-4.1-mini`, `gpt-4o`, `gpt-4o-mini`, `o3`, `o4-mini`. Refresh
this list (and the live-OpenAI smoke test in `tests/live/`) when OpenAI
publishes catalog changes.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# NOTE: this tuple intentionally lists the historical fictitious IDs that the
# 2026-04-26 substrate-aware remediation purged. Do NOT replace these strings
# with real IDs — they are the forbidden set the lint guard scans for. This
# file is excluded from PRODUCTION_GLOBS so the strings here do not self-trip
# the test.
FORBIDDEN_IDS = (
    "gpt-5" + ".4",
    "gpt-5" + ".4-nano",
    "gpt-5" + ".5",
    "gpt-5" + "-haiku",
    "gpt-5" + "-codex",
)

PRODUCTION_GLOBS = (
    "app/**/*.py",
    "app/**/*.yaml",
    "marcus/**/*.py",
    "marcus/**/*.yaml",
    "runtime/**/*.yaml",
    "runtime/**/*.yml",
    "skills/bmad-create-specialist/templates/*.template",
    "scripts/**/*.py",
)

EXCLUDE_PREFIXES = (
    "_bmad-output/",
    "_bmad/",
    "tests/",
    "PROJECT-STRUCTURE-MAP-TEMPORARY.md",
    ".tmp/",
    ".venv/",
    "node_modules/",
)


def _iter_production_files():
    for pattern in PRODUCTION_GLOBS:
        for path in REPO_ROOT.glob(pattern):
            if not path.is_file():
                continue
            rel = path.relative_to(REPO_ROOT).as_posix()
            if any(rel.startswith(prefix) for prefix in EXCLUDE_PREFIXES):
                continue
            yield path


def test_no_fictitious_model_ids_in_production_code() -> None:
    findings: list[str] = []
    for path in _iter_production_files():
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue
        for forbidden in FORBIDDEN_IDS:
            if forbidden in content:
                rel = path.relative_to(REPO_ROOT).as_posix()
                findings.append(f"{rel}: contains {forbidden!r}")
    if findings:
        msg = (
            f"Fictitious OpenAI model IDs found in production code "
            f"({len(findings)} occurrence(s)). Use real catalog IDs only "
            f"(gpt-5, gpt-5-mini, gpt-5-nano, gpt-4.1, gpt-4o-mini, o3, "
            f"o4-mini). Forbidden set: "
            f"{', '.join(repr(i) for i in FORBIDDEN_IDS)}.\n\n"
            + "\n".join(findings)
        )
        pytest.fail(msg)
