"""AC-C.2 — `marcus/lesson_plan/__init__.py` exposes the 13 new 31-3 names.

G6 Acceptance Auditor SHOULD-FIX: pin that the package-level public surface
includes the 31-3 registry + ABC + payload exports. If the `__init__.py`
loses an export (e.g., refactor), consumer stories (30-3 / 29-2 / 28-2 /
31-4) break at import. This test catches drift at merge time.
"""

from __future__ import annotations

import app.marcus.lesson_plan as pkg
EXPECTED_31_3_EXPORTS = {
    # modality_registry
    "MODALITY_REGISTRY",
    "ModalityEntry",
    "ModalityRef",
    "get_modality_entry",
    "list_ready_modalities",
    "list_pending_modalities",
    # component_type_registry
    "COMPONENT_TYPE_REGISTRY",
    "ComponentTypeEntry",
    "get_component_type_entry",
    # modality_producer
    "ModalityProducer",
    # produced_asset
    "ProducedAsset",
    "ProductionContext",
}


def test_marcus_lesson_plan_exports_all_31_3_names() -> None:
    actual = set(pkg.__all__)
    missing = EXPECTED_31_3_EXPORTS - actual
    assert not missing, (
        f"marcus.lesson_plan.__init__.py missing 31-3 exports: {missing}"
    )


def test_marcus_lesson_plan_31_3_exports_are_importable() -> None:
    for name in EXPECTED_31_3_EXPORTS:
        assert hasattr(pkg, name), (
            f"marcus.lesson_plan.{name} is declared in __all__ but not importable"
        )
