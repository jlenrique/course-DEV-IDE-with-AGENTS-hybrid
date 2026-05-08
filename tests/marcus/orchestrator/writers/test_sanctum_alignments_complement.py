from __future__ import annotations

import importlib
import json
import sys

import pytest

from app.parity.contracts import (
    emit_sanctum_alignment_manifest,
    iter_sanctum_alignments,
)
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


def test_last_two_marcus_writers_register_sanctum_alignments():
    for module_name in [
        "app.marcus.orchestrator.writers.theme_resolution",
        "app.marcus.orchestrator.writers.outbound_envelope",
    ]:
        _reload_module(module_name)

    alignments = {item.writer_id: item for item in iter_sanctum_alignments()}

    assert sorted(alignments) == [
        "gary-outbound-envelope",
        "gary-theme-resolution",
    ]
    for declaration in alignments.values():
        assert declaration.sanctum_path == "_bmad/memory/bmad-agent-marcus/"
        assert declaration.alignment_kind == "bmb-pattern"


def test_all_six_writer_alignments_emit_manifest(tmp_path):
    for module_name in [
        "app.marcus.orchestrator.writers.slide_content",
        "app.marcus.orchestrator.writers.fidelity_slides",
        "app.marcus.orchestrator.writers.diagram_cards",
        "app.marcus.orchestrator.writers.theme_resolution",
        "app.marcus.orchestrator.writers.outbound_envelope",
        "app.marcus.orchestrator.writers.section_15_bundle",
    ]:
        _reload_module(module_name)

    manifest_path = emit_sanctum_alignment_manifest(tmp_path / "manifest.json")
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert payload["schema_version"] == 1
    assert [item["writer_id"] for item in payload["alignments"]] == [
        "gary-diagram-cards",
        "gary-fidelity-slides",
        "gary-outbound-envelope",
        "gary-slide-content",
        "gary-theme-resolution",
        "section-15-bundle",
    ]
