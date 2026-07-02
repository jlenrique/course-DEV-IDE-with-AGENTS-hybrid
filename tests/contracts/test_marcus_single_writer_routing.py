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
        # Paths repinned marcus/ -> app/marcus/ per the s2-marcus-collapse
        # (accd226d updated the scan roots only); see
        # contracts-triage-ledger-2026-07-02 row 11.
        "app/marcus/orchestrator/write_api.py",
        # The dispatch.py module is the Orchestrator-originated-flow caller
        # of append_event (via dispatch_orchestrator_event) — 30-3a.
        # Both modules are Orchestrator-side; Intake-side modules are still
        # forbidden from append_event by this test's scan scope.
        "app/marcus/orchestrator/dispatch.py",
    }
)

# The S2 merge (2026-05-07) placed a state-machine TEST HELPER named
# ``append_event(state, event)`` in write_api.py that appends to a
# ``state.events`` list and, by construction, never touches the Lesson Plan
# log (write_api.py documents it as "NOT a production write surface for
# Lesson Plan log events"). Bare-name calls that resolve to THAT import are
# exempt; the invariant this contract protects — no intake/orchestrator
# module appends to the 31-2 LessonPlanLog outside write_api/dispatch —
# keeps full teeth because (a) real log writes are attribute calls on a
# LessonPlanLog instance and remain flagged everywhere, and (b) bare
# ``append_event`` imported from ANY other module remains flagged.
# Follow-on filed (contracts-triage-ledger-2026-07-02 footer): rename the
# helper so this exemption can retire.
_STATE_HELPER_MODULE = "app.marcus.orchestrator.write_api"


def _bare_append_event_import_sources(tree: ast.AST) -> set[str]:
    """Modules from which this file imports a bare ``append_event`` name."""
    sources: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                if alias.name == "append_event":
                    sources.add(node.module)
    return sources


def _find_append_event_callsites(root: Path) -> list[tuple[Path, int]]:
    """Return (file_path, line_number) for every append_event call site."""
    findings: list[tuple[Path, int]] = []
    for py in root.rglob("*.py"):
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        except SyntaxError:
            continue
        import_sources = _bare_append_event_import_sources(tree)
        bare_is_state_helper = import_sources == {_STATE_HELPER_MODULE}
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            is_attribute_call = (
                isinstance(func, ast.Attribute) and func.attr == "append_event"
            )
            is_bare_call = isinstance(func, ast.Name) and func.id == "append_event"
            if is_bare_call and bare_is_state_helper:
                # Resolves to the write_api state-machine helper (non-log).
                continue
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
