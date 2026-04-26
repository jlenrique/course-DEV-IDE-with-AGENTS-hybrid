from __future__ import annotations

import importlib


def test_root_marcus_package_imports_existing_and_new_modules() -> None:
    module_names = [
        "marcus.facade",
        "marcus.intake.pre_packet",
        "marcus.orchestrator.write_api",
        "marcus.orchestrator.supervisor",
        "marcus.orchestrator.routing",
        "marcus.dispatch.contract",
    ]

    imported = {name: importlib.import_module(name) for name in module_names}

    assert hasattr(imported["marcus.dispatch.contract"], "DispatchKind")
    assert hasattr(imported["marcus.dispatch.contract"], "DispatchReceipt")
