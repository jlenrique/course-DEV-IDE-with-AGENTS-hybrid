from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from app.parity.contracts._sanctum import (
    DuplicateSanctumAlignmentError,
    SanctumAlignmentDeclaration,
    _clear_sanctum_alignments_for_tests,
    declare_sanctum_alignment,
    emit_sanctum_alignment_manifest,
    iter_sanctum_alignments,
)


@pytest.fixture(autouse=True)
def clear_sanctum_registry():
    _clear_sanctum_alignments_for_tests()
    yield
    _clear_sanctum_alignments_for_tests()


def test_bmb_pattern_declaration_validates():
    declaration = SanctumAlignmentDeclaration(
        writer_id="gary-slide-content",
        sanctum_path="_bmad/memory/bmad-agent-gary/",
    )

    assert declaration.alignment_kind == "bmb-pattern"


def test_cora_sidecar_exception_requires_rationale():
    with pytest.raises(ValidationError):
        SanctumAlignmentDeclaration(
            writer_id="cora-writer",
            sanctum_path="_bmad/memory/cora-sidecar/",
            alignment_kind="cora-sidecar-exception",
        )


def test_cora_sidecar_exception_with_rationale_validates():
    declaration = SanctumAlignmentDeclaration(
        writer_id="cora-writer",
        sanctum_path="_bmad/memory/cora-sidecar/",
        alignment_kind="cora-sidecar-exception",
        exception_rationale="Operator-ratified exception.",
    )

    assert declaration.exception_rationale


def test_declare_sanctum_alignment_registers_and_rejects_duplicate():
    declare_sanctum_alignment(
        writer_id="gary-slide-content",
        sanctum_path="_bmad/memory/bmad-agent-gary/",
    )

    with pytest.raises(DuplicateSanctumAlignmentError):
        declare_sanctum_alignment(
            writer_id="gary-slide-content",
            sanctum_path="_bmad/memory/bmad-agent-gary/",
        )


def test_iter_sanctum_alignments_returns_deterministic_order():
    declare_sanctum_alignment(writer_id="writer_b", sanctum_path="_bmad/memory/b/")
    declare_sanctum_alignment(writer_id="writer_a", sanctum_path="_bmad/memory/a/")

    assert [item.writer_id for item in iter_sanctum_alignments()] == [
        "writer_a",
        "writer_b",
    ]


def test_emit_sanctum_alignment_manifest_round_trips_json(tmp_path):
    declare_sanctum_alignment(writer_id="writer_a", sanctum_path="_bmad/memory/a/")

    manifest_path = emit_sanctum_alignment_manifest(tmp_path / "sanctum.json")
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert payload["schema_version"] == 1
    assert payload["alignments"][0]["writer_id"] == "writer_a"
