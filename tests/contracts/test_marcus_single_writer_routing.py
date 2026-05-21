"""Single-writer routing contract (AC-C.1).

AST + grep scan of ``marcus/intake/`` and ``marcus/orchestrator/`` for
direct ``append_event`` calls outside ``marcus/orchestrator/write_api.py``.

The invariant: all Marcus-side writes to the Lesson Plan log route
through ``marcus.orchestrator.write_api.emit_pre_packet_snapshot``. Intake
never calls the 31-2 log directly. R1 amendment 13 (Quinn single-writer
rule).

At 30-1 close: zero matches expected (30-1 ships no Intake pipeline
code). 30-2a's lift preserves the invariant; this contract test guards
against regression.
"""

from __future__ import annotations

import ast
from pathlib import Path

_ALLOWED_APPEND_EVENT_CALLERS: frozenset[str] = frozenset(
    {
        # The write_api.py module is the canonical Intake-originated-flow
        # caller of append_event (via emit_pre_packet_snapshot).
        "marcus/orchestrator/write_api.py",
        # The dispatch.py module is the Orchestrator-originated-flow caller
        # of append_event (via dispatch_orchestrator_event) — 30-3a.
        # Both modules are Orchestrator-side; Intake-side modules are still
        # forbidden from append_event by this test's scan scope.
        "marcus/orchestrator/dispatch.py",
    }
)


def _find_append_event_callsites(root: Path) -> list[tuple[Path, int]]:
    """Return (file_path, line_number) for every append_event call site."""
    findings: list[tuple[Path, int]] = []
    for py in root.rglob("*.py"):
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            is_attribute_call = (
                isinstance(func, ast.Attribute) and func.attr == "append_event"
            )
            is_bare_call = isinstance(func, ast.Name) and func.id == "append_event"
            if is_attribute_call or is_bare_call:
                findings.append((py, getattr(node, "lineno", 0)))
    return findings


def test_intake_and_orchestrator_packages_route_through_write_api() -> None:
    """AC-C.1 — no direct append_event calls in intake/orchestrator except
    write_api.py.
    """
    repo_root = Path(__file__).parent.parent.parent
    intake_dir = repo_root / "app" / "marcus" / "intake"
    orchestrator_dir = repo_root / "app" / "marcus" / "orchestrator"

    violations: list[str] = []
    for scan_root in (intake_dir, orchestrator_dir):
        if not scan_root.is_dir():
            continue
        for file_path, line_no in _find_append_event_callsites(scan_root):
            relative = file_path.relative_to(repo_root).as_posix()
            if relative not in _ALLOWED_APPEND_EVENT_CALLERS:
                violations.append(f"{relative}:{line_no}")

    assert not violations, (
        "Direct append_event call sites outside "
        f"marcus/orchestrator/write_api.py: {violations}. "
        "Intake and non-write_api orchestrator code MUST route log writes "
        "through emit_pre_packet_snapshot (R1 amendment 13 single-writer)."
    )
