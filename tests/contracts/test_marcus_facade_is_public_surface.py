"""Facade is the only public Maya-facing top-level surface (AC-C.2).

Scans ``marcus/__init__.py`` for top-level exports; asserts the ONE
re-exported name reachable from ``marcus`` is ``get_facade`` (from
``marcus.facade``). Sub-packages ``marcus.intake`` and
``marcus.orchestrator`` are NOT re-exported at top level.

Dev-side imports like ``from marcus.orchestrator.write_api import
emit_pre_packet_snapshot`` remain valid (Intake-side caller at 30-2b
uses them internally, not via the Maya-facing surface).
"""

from __future__ import annotations

import ast
from pathlib import Path


def test_root_marcus_init_only_exports_get_facade() -> None:
    """AC-C.2 — ``marcus.__all__`` is exactly ``("get_facade",)``."""
    import marcus

    assert hasattr(marcus, "__all__"), (
        "marcus/__init__.py must define __all__ to pin public surface."
    )
    assert tuple(marcus.__all__) == ("get_facade",), (
        f"marcus.__all__ must be exactly ('get_facade',); got {marcus.__all__}"
    )


def test_root_marcus_init_does_not_star_import_sub_packages() -> None:
    """AC-C.2 — no ``from marcus.intake/orchestrator import *`` at root."""
    root_init = Path(__file__).parent.parent.parent / "app" / "marcus" / "__init__.py"
    tree = ast.parse(root_init.read_text(encoding="utf-8"))

    star_import_targets: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                if alias.name == "*":
                    star_import_targets.append(node.module)

    forbidden_modules = {
        mod
        for mod in star_import_targets
        if mod.startswith("marcus.intake") or mod.startswith("marcus.orchestrator")
    }
    assert not forbidden_modules, (
        f"marcus/__init__.py must not re-export sub-packages via `import *`; "
        f"found: {sorted(forbidden_modules)}"
    )


def test_intake_and_orchestrator_are_importable_as_sub_packages() -> None:
    """AC-C.2 — ``marcus.intake`` and ``marcus.orchestrator`` remain
    importable as sub-packages (dev-side usage), even though they are
    not re-exported at the top level.
    """
    import marcus.intake as intake  # noqa: F401
    import marcus.orchestrator as orchestrator  # noqa: F401
    import marcus.orchestrator.write_api as write_api  # noqa: F401

    # Pin the module identity constants so the dev-side import surface
    # exposes what 30-2a expects.
    assert intake.INTAKE_MODULE_IDENTITY == "marcus-intake"
    assert orchestrator.ORCHESTRATOR_MODULE_IDENTITY == "marcus-orchestrator"
    assert callable(write_api.emit_pre_packet_snapshot)
