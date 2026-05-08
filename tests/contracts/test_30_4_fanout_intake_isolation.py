"""AC-3 / AC-4 — Story 30-4 single-writer enforcement on ``emit_plan_lock_fanout``.

AST walk of ``marcus/intake/**/*.py`` asserting that:
    1. No Intake-side module imports ``marcus.orchestrator.fanout``.
    2. No Intake-side module invokes ``emit_plan_lock_fanout`` by any binding
       (direct name, attribute access, or aliased import).

Mirrors the 30-2b dispatch-monopoly pattern (``test_30_2b_dispatch_monopoly``
+ ``test_30_2b_single_writer_routing``) for 30-4's fanout emission seam.
Plan-lock fanout is an Orchestrator-only concern: Intake produces the
pre-packet snapshot and hands off to Maya via the 4A loop; the locked plan
that triggers fanout is constructed strictly inside the Orchestrator. Any
Intake-side reach into the fanout emitter would violate the single-writer
discipline (R1 ruling amendment 13) the same way as a direct
``emit_pre_packet_snapshot`` call would.

Authored 2026-04-19 as a party-mode follow-on remediation closing the AST
contract gap surfaced by the independent G6 review on Story 30-4.
"""

from __future__ import annotations

import ast
from pathlib import Path

_FORBIDDEN_MODULE: str = "app.marcus.orchestrator.fanout"
_FORBIDDEN_CALL: str = "emit_plan_lock_fanout"


def _intake_files(repo_root: Path) -> list[Path]:
    intake_dir = repo_root / "app" / "marcus" / "intake"
    return [p for p in sorted(intake_dir.rglob("*.py")) if p.is_file()]


def _imports_fanout(tree: ast.AST) -> list[int]:
    lines: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == _FORBIDDEN_MODULE or module.startswith(
                _FORBIDDEN_MODULE + "."
            ):
                lines.append(getattr(node, "lineno", 0))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == _FORBIDDEN_MODULE or alias.name.startswith(
                    _FORBIDDEN_MODULE + "."
                ):
                    lines.append(getattr(node, "lineno", 0))
    return lines


def _calls_emit_plan_lock_fanout(tree: ast.AST) -> list[int]:
    lines: list[int] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id == _FORBIDDEN_CALL or (
            isinstance(func, ast.Attribute) and func.attr == _FORBIDDEN_CALL
        ):
            lines.append(getattr(node, "lineno", 0))
    return lines


def test_intake_does_not_import_fanout_module() -> None:
    """Intake-side modules MUST NOT import marcus.orchestrator.fanout."""
    repo_root = Path(__file__).parent.parent.parent
    offenders: list[str] = []
    for py in _intake_files(repo_root):
        relative = py.relative_to(repo_root).as_posix()
        tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        for lineno in _imports_fanout(tree):
            offenders.append(f"{relative}:{lineno}")

    assert not offenders, (
        "Story 30-4 single-writer invariant: Intake-side modules MUST NOT "
        f"import {_FORBIDDEN_MODULE!r}. Offending import sites:\n  "
        + "\n  ".join(offenders)
    )


def test_intake_does_not_call_emit_plan_lock_fanout() -> None:
    """Intake-side modules MUST NOT invoke emit_plan_lock_fanout."""
    repo_root = Path(__file__).parent.parent.parent
    offenders: list[str] = []
    for py in _intake_files(repo_root):
        relative = py.relative_to(repo_root).as_posix()
        tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        for lineno in _calls_emit_plan_lock_fanout(tree):
            offenders.append(f"{relative}:{lineno}")

    assert not offenders, (
        "Story 30-4 single-writer invariant: Intake-side modules MUST NOT "
        f"invoke {_FORBIDDEN_CALL!r}. Offending call sites:\n  "
        + "\n  ".join(offenders)
    )
