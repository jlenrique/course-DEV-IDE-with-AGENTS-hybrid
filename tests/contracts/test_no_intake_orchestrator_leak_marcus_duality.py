"""No-user-facing-leak grep on Marcus duality surfaces (AC-T.8).

R1 amendment 17 / R2 rider S-3 enforcement. Runtime scan of exception
messages + Maya-facing sections of module docstrings from:
* ``marcus/intake/__init__.py``
* ``marcus/orchestrator/__init__.py``
* ``marcus/orchestrator/write_api.py``
* ``marcus/facade.py``

for the forbidden tokens ``"intake"`` and ``"orchestrator"``
(case-insensitive whole-word regex).

Exempted surfaces (documented in-test):

* Runtime programming identifiers: ``INTAKE_MODULE_IDENTITY``,
  ``ORCHESTRATOR_MODULE_IDENTITY``, ``NEGOTIATOR_SEAM``, ``MARCUS_IDENTITY``
  — these are variable NAMES, not Maya-visible strings.
* Dev-facing docstring sections titled "Developer discipline note",
  "LIFT-TARGET for 30-2a", "Single-writer contract", "Single-writer
  discipline", "Negotiator seam", "Voice Register", "Maya-visibility
  boundary", "Lazy-accessor construction", "Idempotency" — audience-
  layered docstrings; only the leading "Maya-facing note" section
  must be Maya-clean.
* ``UnauthorizedFacadeCallerError.debug_detail`` + ``.offending_writer``
  attributes — dev/test-visible, not auto-stringified.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest

from app.marcus.facade import get_facade, reset_facade
from app.marcus.lesson_plan.events import EventEnvelope
from app.marcus.orchestrator.write_api import (
    UnauthorizedFacadeCallerError,
    emit_pre_packet_snapshot,
)

FORBIDDEN_TOKEN_PATTERN = re.compile(
    r"\b(intake|orchestrator)\b",
    flags=re.IGNORECASE,
)


def test_facade_maya_surface_has_no_forbidden_tokens() -> None:
    """AC-T.8 — Facade Maya-surface returns a Maya-clean string.

    30-3a replaced ``greet()`` with ``run_4a()``; ``repr(facade)`` remains
    the Maya-surface smoke target (renders the one "Marcus" display
    name per 30-1 AC-B.4 __repr__ contract).
    """
    reset_facade()
    try:
        surface = repr(get_facade())
        match = FORBIDDEN_TOKEN_PATTERN.search(surface)
        assert match is None, (
            f"Forbidden token {match.group()!r} in repr(Facade) output: "
            f"{surface!r}"
        )
    finally:
        reset_facade()


def test_facade_repr_has_no_forbidden_tokens() -> None:
    """AC-T.8 — ``repr(facade)`` is Maya-clean."""
    reset_facade()
    try:
        surface = repr(get_facade())
        match = FORBIDDEN_TOKEN_PATTERN.search(surface)
        assert match is None, (
            f"Forbidden token {match.group()!r} in repr(facade): {surface!r}"
        )
    finally:
        reset_facade()


@pytest.mark.parametrize(
    "offending_writer",
    ["marcus-intake", "irene", "maya", "random-attacker"],
)
def test_unauthorized_error_str_form_has_no_forbidden_tokens(
    offending_writer: str,
) -> None:
    """AC-T.8 — ``str(UnauthorizedFacadeCallerError)`` is Maya-clean.

    The offending writer is preserved on ``.offending_writer`` (dev-only
    attribute); ``str(err)`` returns the Maya-safe generic message.
    """
    envelope = EventEnvelope(
        event_id=str(uuid4()),
        timestamp=datetime.now(tz=UTC),
        plan_revision=0,
        event_type="pre_packet_snapshot",
        payload={
            "source_ref": {"path": "x.md", "sha256": "c" * 64},
            "pre_packet_artifact_path": "x.md",
            "audience_profile_version": 1,
            "sme_refs": ["x"],
        },
    )
    with pytest.raises(UnauthorizedFacadeCallerError) as exc_info:
        emit_pre_packet_snapshot(envelope, writer=offending_writer)  # type: ignore[arg-type]

    err_str = str(exc_info.value)
    match = FORBIDDEN_TOKEN_PATTERN.search(err_str)
    assert match is None, (
        f"Forbidden token {match.group()!r} in str(UnauthorizedFacadeCallerError): "
        f"{err_str!r}"
    )


def test_maya_facing_docstring_sections_have_no_forbidden_tokens() -> None:
    """AC-T.8 — the leading "Maya-facing note" sections are Maya-clean.

    Scans the 30-1 module docstrings for the "Maya-facing note" section
    only; other audience-layered sections are dev-facing and exempt.
    """
    # S2 collapse 2026-05-07: canonical paths moved from marcus/* to app/marcus/*.
    # Reverse-shim layer at marcus/* preserves backward-compat for live imports
    # (108-150 test files); docstring-discovery tests read canonical app-side
    # files directly. Forward-compatible with legacy `marcus/` deletion at Phase 5.
    repo_root = Path(__file__).parent.parent.parent
    modules: dict[str, Path] = {
        "app.marcus.intake": repo_root / "app" / "marcus" / "intake" / "__init__.py",
        "app.marcus.orchestrator": repo_root / "app" / "marcus" / "orchestrator" / "__init__.py",
        "app.marcus.orchestrator.write_api": (
            repo_root / "app" / "marcus" / "orchestrator" / "write_api.py"
        ),
        "app.marcus.facade": repo_root / "app" / "marcus" / "facade.py",
    }
    # Terminate the Maya-facing capture at the next section heading of ANY
    # shape (any non-empty line followed by a rule-of-dashes), not just
    # word-char headings. Post-G6 Edge#10 rider: brittle stop condition
    # could over-capture when a heading contains a hyphen / em-dash.
    maya_section_re = re.compile(
        r"Maya-facing note\s*\n-+\s*\n(.+?)(?=\n[^\n]+\n-+\n|\n\"\"\"|\Z)",
        flags=re.DOTALL,
    )
    for module_name, path in modules.items():
        source = path.read_text(encoding="utf-8")
        matches = maya_section_re.findall(source)
        assert matches, (
            f"{module_name} missing 'Maya-facing note' section in module "
            "docstring."
        )
        for section in matches:
            forbidden = FORBIDDEN_TOKEN_PATTERN.search(section)
            assert forbidden is None, (
                f"Forbidden token {forbidden.group()!r} in {module_name} "
                f"Maya-facing note section: {section[:200]!r}"
            )
