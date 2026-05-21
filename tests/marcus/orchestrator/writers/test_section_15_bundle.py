from __future__ import annotations

import hashlib
import importlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.gates.errors import GateError
from app.marcus.orchestrator.writers.outbound_envelope import (
    GaryOutboundEnvelope,
    OutboundEnvelopeEntry,
)
from app.marcus.orchestrator.writers.section_15_bundle import (
    Section15Bundle,
    emit_section_15_bundle,
    render_descript_assembly_guide,
)
from app.models.operator_verdict_section_15 import Section15OperatorVerdict
from app.parity.contracts import iter_sanctum_alignments
from app.parity.contracts._sanctum import _clear_sanctum_alignments_for_tests

SCHEMA_HASH = "1fa1fe90f68932f2d41423f9d6e5d35fe4fb6323f5bb4b81cba675e643f6b1a3"
DISPATCHED_AT = datetime(2026, 5, 6, 16, 0, tzinfo=UTC)
RUN_ID = "dddddddd-dddd-4ddd-8ddd-dddddddddddd"


def _entry(writer_id: str, payload_ref: str) -> OutboundEnvelopeEntry:
    return OutboundEnvelopeEntry(
        writer_id=writer_id,
        target_section="section-15",
        payload_ref=payload_ref,
        dispatched_at=DISPATCHED_AT,
        operator_id="operator_1",
    )


def _envelope() -> GaryOutboundEnvelope:
    return GaryOutboundEnvelope(
        plan_unit_id="unit-15",
        target_section="section-15",
        entries=[
            _entry("gary-theme-resolution", "gary-theme-resolution.json"),
            _entry("gary-slide-content", "gary-slide-content.json"),
        ],
        dispatched_at=DISPATCHED_AT,
        operator_id="operator_1",
    )


def _complete_verdict() -> Section15OperatorVerdict:
    return Section15OperatorVerdict(
        run_id=RUN_ID,
        verb="complete",
        handoff_id="handoff-15",
        operator_id="operator_1",
        submitted_at=DISPATCHED_AT,
        decision_card_digest="f" * 64,
    )


def test_section_15_bundle_shape_and_schema_hash_are_stable() -> None:
    schema = json.dumps(Section15Bundle.model_json_schema(), sort_keys=True).encode()

    assert hashlib.sha256(schema).hexdigest() == SCHEMA_HASH


def test_render_descript_assembly_guide_is_deterministic_and_ordered() -> None:
    envelope = _envelope()
    rendered = render_descript_assembly_guide(envelope)

    assert rendered == render_descript_assembly_guide(envelope)
    assert rendered.index("### gary-slide-content") < rendered.index(
        "### gary-theme-resolution"
    )
    assert "plan_unit_id: unit-15" in rendered


def test_emit_section_15_bundle_writes_guide_anchor_and_evidence(tmp_path: Path) -> None:
    transcript_path = tmp_path / "trial-3-transcript.md"
    transcript_path.write_text("Trial 3 transcript\n", encoding="utf-8", newline="\n")
    evidence_path = tmp_path / "slab-close-evidence.json"

    bundle = emit_section_15_bundle(
        _complete_verdict(),
        _envelope(),
        assembly_bundle_path=tmp_path / "assembly-bundle",
        trial_3_transcript_path=transcript_path,
        slab_close_evidence_path=evidence_path,
    )

    guide_path = tmp_path / "assembly-bundle" / "DESCRIPT-ASSEMBLY-GUIDE.md"
    assert guide_path.exists()
    assert b"\r\n" not in guide_path.read_bytes()
    assert bundle.descript_assembly_guide_md_digest == hashlib.sha256(
        guide_path.read_bytes()
    ).hexdigest()
    assert bundle.trial_3_transcript_anchor == hashlib.sha256(
        transcript_path.read_bytes()
    ).hexdigest()
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["handoff_id"] == "handoff-15"
    assert evidence["plan_unit_id"] == "unit-15"
    assert evidence["trial_3_transcript_anchor"] == bundle.trial_3_transcript_anchor


def test_emit_section_15_bundle_is_byte_deterministic(tmp_path: Path) -> None:
    transcript_path = tmp_path / "trial-3-transcript.md"
    transcript_path.write_text("Trial 3 transcript\n", encoding="utf-8", newline="\n")
    evidence_path = tmp_path / "slab-close-evidence.json"
    guide_path = tmp_path / "assembly-bundle" / "DESCRIPT-ASSEMBLY-GUIDE.md"

    first = emit_section_15_bundle(
        _complete_verdict(),
        _envelope(),
        assembly_bundle_path=tmp_path / "assembly-bundle",
        trial_3_transcript_path=transcript_path,
        slab_close_evidence_path=evidence_path,
    )
    first_guide = guide_path.read_bytes()
    first_evidence = evidence_path.read_bytes()
    second = emit_section_15_bundle(
        _complete_verdict(),
        _envelope(),
        assembly_bundle_path=tmp_path / "assembly-bundle",
        trial_3_transcript_path=transcript_path,
        slab_close_evidence_path=evidence_path,
    )

    assert second == first
    assert guide_path.read_bytes() == first_guide
    assert evidence_path.read_bytes() == first_evidence


def test_emit_section_15_bundle_rejects_non_complete_verdict(tmp_path: Path) -> None:
    transcript_path = tmp_path / "trial-3-transcript.md"
    transcript_path.write_text("Trial 3 transcript\n", encoding="utf-8", newline="\n")
    edit_verdict = Section15OperatorVerdict(
        run_id=RUN_ID,
        verb="edit",
        handoff_id="handoff-15",
        operator_id="operator_1",
        submitted_at=DISPATCHED_AT,
        decision_card_digest="f" * 64,
        edit_payload={"edits": {"guide": "revise intro"}},
    )

    with pytest.raises(GateError, match="section_15_handoff_not_complete"):
        emit_section_15_bundle(
            edit_verdict,
            _envelope(),
            assembly_bundle_path=tmp_path / "assembly-bundle",
            trial_3_transcript_path=transcript_path,
            slab_close_evidence_path=tmp_path / "slab-close-evidence.json",
        )


def test_section_15_bundle_registers_marcus_sanctum_alignment() -> None:
    _clear_sanctum_alignments_for_tests()
    module_name = "app.marcus.orchestrator.writers.section_15_bundle"
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
    else:
        importlib.import_module(module_name)

    alignments = {item.writer_id: item for item in iter_sanctum_alignments()}
    declaration = alignments["section-15-bundle"]

    assert declaration.sanctum_path == "_bmad/memory/bmad-agent-marcus/"
    assert declaration.alignment_kind == "bmb-pattern"
