"""Canonical-caller grep invariant (Story 29-1, AC-T.11 — Q-1 rider, LOAD-BEARING).

Pins AC-B.5.1: the canonical caller of ``emit_fit_report`` is Marcus-
Orchestrator. Irene (29-2) produces :class:`FitReport` instances and hands
them to Marcus via the orchestration seam; Irene MUST NOT import or call
``emit_fit_report`` directly.

At 29-1 authoring time this test is trivially green (no other module
imports ``emit_fit_report``). The test is load-bearing for 29-2 and
beyond — it fails the moment a contributor adds
``from marcus.lesson_plan.fit_report import emit_fit_report`` in any
production module outside the canonical-caller path.

Production modules outside Marcus-Orchestrator's domain SHOULD NOT import
the symbol at all. Production modules inside Marcus-Orchestrator's domain
SHOULD. Tests under ``tests/`` are exempt (mocking is legitimate). Re-
exports via ``marcus/lesson_plan/__init__.py`` are exempt (that's package
plumbing, not a caller).
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Files inside these prefixes are allowed to import emit_fit_report.
ALLOWED_PRODUCTION_IMPORT_PREFIXES: tuple[str, ...] = (
    # The defining module itself.
    "marcus/lesson_plan/fit_report.py",
    # Package re-exports are plumbing, not a caller.
    "marcus/lesson_plan/__init__.py",
    # Future Marcus-Orchestrator module (30-1 duality split). Pre-seeded
    # here so 29-2 authors see the invariant before the split lands:
    # Marcus-Orchestrator modules are the sanctioned caller surface.
    "marcus/orchestrator/",
)

# Test files are exempt (mocking / direct invocation via isolated log is
# legitimate for test coverage).
TEST_PREFIX = "tests/"

IMPORT_REGEX = re.compile(r"\bemit_fit_report\b")


def _repo_relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _iter_candidate_python_files() -> list[Path]:
    """Yield production .py files under marcus/ (excluding test/cache dirs)."""
    out: list[Path] = []
    for p in (REPO_ROOT / "app" / "marcus").rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        out.append(p)
    return out


def _is_allowed_path(path: Path) -> bool:
    rel = _repo_relative(path)
    if rel.startswith(TEST_PREFIX):
        return True
    return any(rel.startswith(prefix) for prefix in ALLOWED_PRODUCTION_IMPORT_PREFIXES)


def test_emit_fit_report_not_imported_outside_canonical_callers() -> None:
    """AC-T.11 — grep-walk pins the canonical-caller invariant.

    Failure mode: a future contributor adds
    ``from marcus.lesson_plan.fit_report import emit_fit_report`` in a
    module under ``marcus/irene/``, ``marcus/tracy/``, or any specialist
    path. The 31-2 single-writer log would catch the permission violation
    at runtime; this test catches the design-time intent violation
    earlier, at commit review.
    """
    offenders: list[tuple[Path, int, str]] = []
    for path in _iter_candidate_python_files():
        if _is_allowed_path(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if IMPORT_REGEX.search(line):
                offenders.append((path, lineno, line.strip()))

    assert offenders == [], (
        "emit_fit_report imported outside canonical-caller surface "
        "(AC-B.5.1). The canonical caller is Marcus-Orchestrator; Irene "
        "and specialists MUST hand FitReport instances to Marcus via the "
        "orchestration seam. Offenders:\n"
        + "\n".join(
            f"  {_repo_relative(p)}:{lineno}: {txt!r}"
            for p, lineno, txt in offenders
        )
    )
