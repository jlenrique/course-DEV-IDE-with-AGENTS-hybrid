from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path

from app.parity.contracts import iter_registered_surfaces, run_self_registration_audit
from app.parity.contracts._registry import _clear_registered_surfaces_for_tests

POLL_SURFACE = Path("app/gates/section_15/poll_surface.py")
MODULE_NAME = "app.gates.section_15.poll_surface"


def _reload_poll_surface_registration() -> None:
    _clear_registered_surfaces_for_tests()
    module = sys.modules.get(MODULE_NAME)
    if module is None:
        importlib.import_module(MODULE_NAME)
    else:
        importlib.reload(module)


def test_g5_surface_has_exactly_one_module_level_parity_contract() -> None:
    tree = ast.parse(POLL_SURFACE.read_text(encoding="utf-8"))
    decorated = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        for decorator in node.decorator_list
        if isinstance(decorator, ast.Call)
        and getattr(decorator.func, "id", "") == "parity_contract"
    ]

    assert len(decorated) == 1


def test_g5_surface_registers_declared_transports_and_alias() -> None:
    _reload_poll_surface_registration()

    surfaces = {surface.surface_id: surface for surface in iter_registered_surfaces()}
    declaration = surfaces["section_15_g5_final_handoff"]

    assert declaration.mandatory_transports == ["cli", "http", "mcp-stdio"]
    assert declaration.optional_transports == []
    assert declaration.alias_of == "G5"


def test_self_registration_audit_passes_for_section_15(tmp_path: Path) -> None:
    _reload_poll_surface_registration()

    result = run_self_registration_audit(
        declared_floor=1,
        discovery_roots=("app.gates.section_15",),
        include_reference_surface=False,
        manifest_path=tmp_path / "parity-registration-manifest.json",
    )

    assert result.audit_status == "PASS"
