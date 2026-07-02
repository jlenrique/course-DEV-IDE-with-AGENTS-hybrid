"""AC-T.7 — ``dispatch_intake_pre_packet`` is the sole caller of ``emit_pre_packet_snapshot``.

AST walk of ``marcus/orchestrator/**/*.py`` (excluding ``dispatch.py``,
which is the sanctioned caller, and ``write_api.py``, which DEFINES the
callable and references it by name in docstrings/exports). Asserts no
other orchestrator-side module invokes ``emit_pre_packet_snapshot``.

Pairs with :mod:`tests.contracts.test_30_2b_single_writer_routing`
(Intake-import invariant) to close the single-caller loop: Intake cannot
import the emission surface, and only the dispatch seam calls it from
the Orchestrator side.
"""

from __future__ import annotations

import ast
from pathlib import Path

_ALLOWED_CALLERS: frozenset[str] = frozenset(
    {
        # dispatch.py holds both dispatch_intake_pre_packet (Intake flow)
        # and dispatch_orchestrator_event (Orchestrator flow, 30-3a).
        # Paths repinned marcus/ -> app/marcus/ per the s2-marcus-collapse
        # (accd226d updated the walk root only); see
        # contracts-triage-ledger-2026-07-02 row 12.
        "app/marcus/orchestrator/dispatch.py",
        # write_api.py defines the callable.
        "app/marcus/orchestrator/write_api.py",
    }
)


def _calls_emit_pre_packet_snapshot(tree: ast.AST) -> list[int]:
    """Return line numbers where ``emit_pre_packet_snapshot`` is invoked."""
    lines: list[int] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id == "emit_pre_packet_snapshot" or (
            isinstance(func, ast.Attribute)
            and func.attr == "emit_pre_packet_snapshot"
        ):
            lines.append(getattr(node, "lineno", 0))
    return lines


def test_dispatch_is_sole_orchestrator_caller() -> None:
    """AC-T.7 — only dispatch.py (besides write_api.py) may call emit."""
    repo_root = Path(__file__).parent.parent.parent
    orchestrator_dir = repo_root / "app" / "marcus" / "orchestrator"
    offenders: list[str] = []
    for py in sorted(orchestrator_dir.rglob("*.py")):
        relative = py.relative_to(repo_root).as_posix()
        if relative in _ALLOWED_CALLERS:
            continue
        tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        lines = _calls_emit_pre_packet_snapshot(tree)
        for lineno in lines:
            offenders.append(f"{relative}:{lineno}")

    assert not offenders, (
        "Only marcus/orchestrator/dispatch.py may call "
        "emit_pre_packet_snapshot (aside from write_api.py which defines "
        f"it). Offenders: {offenders}."
    )
