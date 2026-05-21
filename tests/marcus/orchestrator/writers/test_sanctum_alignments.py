from __future__ import annotations

import importlib
import sys

import pytest

from app.parity.contracts import iter_sanctum_alignments
from app.parity.contracts._sanctum import _clear_sanctum_alignments_for_tests


@pytest.fixture(autouse=True)
def clear_sanctum_registry():
    _clear_sanctum_alignments_for_tests()
    yield
    _clear_sanctum_alignments_for_tests()


def _reload_module(module_name: str) -> None:
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
        return
    importlib.import_module(module_name)


def test_first_three_marcus_writers_register_sanctum_alignments():
    for module_name in [
        "app.marcus.orchestrator.writers.slide_content",
        "app.marcus.orchestrator.writers.fidelity_slides",
        "app.marcus.orchestrator.writers.diagram_cards",
    ]:
        _reload_module(module_name)

    alignments = {item.writer_id: item for item in iter_sanctum_alignments()}

    assert sorted(alignments) == [
        "gary-diagram-cards",
        "gary-fidelity-slides",
        "gary-slide-content",
    ]
    for declaration in alignments.values():
        assert declaration.sanctum_path == "_bmad/memory/bmad-agent-marcus/"
        assert declaration.alignment_kind == "bmb-pattern"
