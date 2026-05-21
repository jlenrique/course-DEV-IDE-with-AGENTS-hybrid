from __future__ import annotations

import importlib


def test_root_marcus_package_imports_existing_and_new_modules() -> None:
    module_names = [
        "app.marcus.facade",
        "app.marcus.intake.pre_packet",
        "app.marcus.orchestrator.write_api",
        "app.marcus.orchestrator.supervisor",
        "app.marcus.orchestrator.routing",
        "app.marcus.dispatch.contract",
    ]

    imported = {name: importlib.import_module(name) for name in module_names}

    assert hasattr(imported["app.marcus.dispatch.contract"], "DispatchKind")
    assert hasattr(imported["app.marcus.dispatch.contract"], "DispatchReceipt")
