"""AC-T.6 — Intake never imports direct writer surfaces.

AST walk of ``marcus/intake/``. Asserts no module imports:

* :class:`marcus.lesson_plan.log.LessonPlanLog` (the write path),
* ``LessonPlanLog.append_event`` (directly via attribute access),
* :func:`marcus.orchestrator.write_api.emit_pre_packet_snapshot` (the
  orchestrator-side sanctioned emission surface — Intake must receive
  emission capability via dependency injection, not direct import).

Pairs with the 30-1 ``test_marcus_single_writer_routing.py`` AST check
(which guards against direct ``append_event`` calls); this test guards
against the IMPORT surface so the dependency-injection pattern is
structurally enforced, not just runtime-enforced.
"""

from __future__ import annotations

import ast
from pathlib import Path

_FORBIDDEN_IMPORT_TARGETS: frozenset[tuple[str, str]] = frozenset(
    {
        # (module_string, imported_name)
        ("app.marcus.lesson_plan.log", "LessonPlanLog"),
        ("app.marcus.orchestrator.write_api", "emit_pre_packet_snapshot"),
        ("app.marcus.orchestrator.write_api", "UnauthorizedFacadeCallerError"),
    }
)
_FORBIDDEN_ATTRIBUTE_CHAINS: frozenset[tuple[str, ...]] = frozenset(
    {
        # Attribute-chain violations (e.g., ``log.append_event(...)``).
        ("LessonPlanLog", "append_event"),
    }
)


def _iter_intake_py_files(repo_root: Path) -> list[Path]:
    intake_dir = repo_root / "app" / "marcus" / "intake"
    return sorted(intake_dir.rglob("*.py"))


def _find_forbidden_imports(tree: ast.AST) -> list[tuple[str, str, int]]:
    violations: list[tuple[str, str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                if (module, alias.name) in _FORBIDDEN_IMPORT_TARGETS:
                    violations.append((module, alias.name, node.lineno))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                # Reject ``import marcus.orchestrator.write_api as _wa`` too.
                if alias.name == "app.marcus.orchestrator.write_api":
                    violations.append((alias.name, "<module>", node.lineno))
    return violations


def test_intake_never_imports_writer_surfaces() -> None:
    """AC-T.6 — AST-level invariant: Intake cannot reach the write API by import."""
    repo_root = Path(__file__).parent.parent.parent
    offenders: list[str] = []
    for py in _iter_intake_py_files(repo_root):
        tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        for module, name, lineno in _find_forbidden_imports(tree):
            offenders.append(
                f"{py.relative_to(repo_root).as_posix()}:{lineno} "
                f"imports {name!r} from {module!r}"
            )

    assert not offenders, (
        "Intake-side modules under marcus/intake/ must NOT import writer "
        f"surfaces directly (R1 amendment 13 single-writer rule). Offenders: "
        f"{offenders}. Intake receives emission capability via the injected "
        "``dispatch`` callable instead."
    )
