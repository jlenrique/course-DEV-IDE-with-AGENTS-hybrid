"""Facade is the only public Maya-facing top-level surface (AC-C.2).

Scans ``app/marcus/__init__.py`` for top-level exports; asserts the ONE
re-exported name reachable from ``app.marcus`` is ``get_facade`` (from
``app.marcus.facade``). Sub-packages ``app.marcus.intake`` and
``app.marcus.orchestrator`` are NOT re-exported at top level.

S2 collapse 2026-05-07: legacy ``marcus/`` package retired; canonical
namespace is ``app.marcus.*``. 30-1 contract identities preserved verbatim
under the new home (R1 amendments 12+13+17 binding).

Dev-side imports like ``from app.marcus.orchestrator.write_api import
emit_pre_packet_snapshot`` remain valid (Intake-side caller at 30-2b
uses them internally, not via the Maya-facing surface).
"""

from __future__ import annotations

import ast
from pathlib import Path


def test_root_marcus_init_only_exports_get_facade() -> None:
    """AC-C.2 — ``app.marcus.__all__`` includes ``get_facade`` as the
    Maya-facing top-level surface. Post-S2 the package is no longer a
    pure shim — `app.marcus` retains its module-level helpers (e.g.
    `get_facade`) as the canonical Maya entry point."""
    import app.marcus as marcus_pkg

    assert callable(getattr(marcus_pkg, "get_facade", None)), (
        "app/marcus/__init__.py must export `get_facade` for the Maya-facing surface."
    )


def test_root_marcus_init_does_not_star_import_sub_packages() -> None:
    """AC-C.2 — no ``from app.marcus.intake/orchestrator import *`` at root."""
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
        if mod.startswith("app.marcus.intake") or mod.startswith("app.marcus.orchestrator")
    }
    assert not forbidden_modules, (
        f"app/marcus/__init__.py must not re-export sub-packages via `import *`; "
        f"found: {sorted(forbidden_modules)}"
    )


def test_intake_and_orchestrator_are_importable_as_sub_packages() -> None:
    """AC-C.2 — ``app.marcus.intake`` and ``app.marcus.orchestrator`` remain
    importable as sub-packages (dev-side usage), even though they are
    not re-exported at the top level. S2 collapse preserves 30-1 module
    identities under the new app.marcus.* home.
    """
    import app.marcus.intake as intake  # noqa: F401
    import app.marcus.orchestrator as orchestrator  # noqa: F401
    import app.marcus.orchestrator.write_api as write_api  # noqa: F401

    # Pin the module identity constants — 30-1 R1 amendment 13 (Quinn)
    # WriterIdentity Literal values; preserved verbatim across S2 collapse.
    assert intake.INTAKE_MODULE_IDENTITY == "marcus-intake"
    assert orchestrator.ORCHESTRATOR_MODULE_IDENTITY == "marcus-orchestrator"
    assert callable(write_api.emit_pre_packet_snapshot)
