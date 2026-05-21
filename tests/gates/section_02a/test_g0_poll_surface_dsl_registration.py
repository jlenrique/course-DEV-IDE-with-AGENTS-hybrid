from __future__ import annotations

import ast
from pathlib import Path

from app.parity.contracts import iter_registered_surfaces, run_self_registration_audit

POLL_SURFACE = Path("app/gates/section_02a/poll_surface.py")


def test_poll_surface_has_exactly_one_module_level_parity_contract() -> None:
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


def test_poll_surface_registers_three_mandatory_transports() -> None:
    import app.gates.section_02a.poll_surface  # noqa: F401

    surfaces = {
        surface.surface_id: surface for surface in iter_registered_surfaces()
    }

    declaration = surfaces["section_02a_g0_poll"]
    assert declaration.mandatory_transports == ["cli", "http", "mcp-stdio"]
    assert declaration.optional_transports == ["mcp-subprocess"]


def test_self_registration_audit_passes_floor_10(tmp_path: Path) -> None:
    result = run_self_registration_audit(
        declared_floor=10,
        discovery_roots=(
            "app.gates.section_02a",
            "tests.integration.transport_parity",
            "tests.integration.transports",
        ),
        manifest_path=tmp_path / "parity-registration-manifest.json",
    )

    assert result.audit_status == "PASS"
