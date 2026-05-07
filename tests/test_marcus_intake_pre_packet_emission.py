"""Tests for Story 30-2b ``prepare_and_emit_irene_packet``.

Covers:
* AC-T.2 — happy-path emission (packet file + log entry + path pair equality).
* AC-T.3 — parametrized payload field wiring across sme_refs branches + digest determinism.
* AC-T.4 — parametrized zero-emission-on-failure across missing-input paths.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from app.marcus.intake import pre_packet
from app.marcus.intake.pre_packet import prepare_and_emit_irene_packet
from app.marcus.lesson_plan.events import EventEnvelope
from app.marcus.lesson_plan.log import LessonPlanLog
from app.marcus.orchestrator.dispatch import dispatch_intake_pre_packet


def _write_bundle(
    bundle_dir: Path,
    *,
    include_ingestion_receipt: bool = True,
    metadata_overrides: dict[str, Any] | None = None,
    extracted_content: str = "# Extracted Content\n\nSection 1 body.\n",
) -> None:
    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "extracted.md").write_text(extracted_content, encoding="utf-8")
    metadata: dict[str, Any] = {
        "primary_source": "example.pdf",
        "total_sections": 3,
        "overall_confidence": 0.92,
    }
    if metadata_overrides:
        metadata.update(metadata_overrides)
    (bundle_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )
    (bundle_dir / "operator-directives.md").write_text(
        "# Operator Directives\n\n- Focus on Part 1.\n",
        encoding="utf-8",
    )
    if include_ingestion_receipt:
        (bundle_dir / "ingestion-quality-gate-receipt.md").write_text(
            "# Ingestion Quality Gate Receipt\n\nStatus: pass.\n",
            encoding="utf-8",
        )


def _tmp_log(tmp_path: Path) -> LessonPlanLog:
    return LessonPlanLog(path=tmp_path / "lesson_plan_log.jsonl")


# ---------------------------------------------------------------------------
# AC-T.2 — happy-path emission
# ---------------------------------------------------------------------------


def test_prepare_and_emit_happy_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC-T.2 — build packet + emit one pre_packet_snapshot + Irene handshake pair.

    Treats ``tmp_path`` as the repo root so the repo-relative path validator
    on :class:`PrePacketSnapshotPayload.pre_packet_artifact_path` accepts
    the test's output path.
    """
    monkeypatch.setattr(pre_packet, "_REPO_ROOT", tmp_path)
    bundle_dir = tmp_path / "bundle"
    _write_bundle(bundle_dir)
    output_path = tmp_path / "out" / "irene-packet.md"
    log = _tmp_log(tmp_path)
    assert list(log.read_events()) == []  # precondition

    result = prepare_and_emit_irene_packet(
        bundle_dir=bundle_dir,
        run_id="TEST-RUN-001",
        output_path=output_path,
        dispatch=lambda envelope: dispatch_intake_pre_packet(envelope, log=log),
        plan_revision=0,
    )

    # Return shape pin — byte-identical to prepare_irene_packet (30-2a contract).
    assert set(result.keys()) == {
        "packet_path",
        "sections",
        "has_directives",
        "has_ingestion_receipt",
    }
    assert result["packet_path"] == str(output_path)

    # Packet file exists (AC-T.1 precedent).
    assert output_path.is_file()

    # Exactly-one emission invariant (AC-B.3).
    events = list(log.read_events())
    assert len(events) == 1
    envelope = events[0]
    assert isinstance(envelope, EventEnvelope)
    assert envelope.event_type == "pre_packet_snapshot"
    assert envelope.plan_revision == 0

    # Irene handshake artifact-pair equality (AC-B.6).
    payload_path = envelope.payload["pre_packet_artifact_path"]
    assert (tmp_path / payload_path).resolve() == output_path.resolve()


# ---------------------------------------------------------------------------
# AC-T.3 — payload field wiring (parametrized over sme_refs branches + determinism)
# ---------------------------------------------------------------------------


_EXPLICIT_SME_REFS = [
    {
        "source_id": "pdf-001",
        "path": "course-content/source.pdf",
        "content_digest": "a" * 64,
    }
]


@pytest.mark.parametrize(
    ("case", "metadata_overrides"),
    [
        ("explicit_sme_refs", {"sme_refs": _EXPLICIT_SME_REFS}),
        ("synthesized_from_primary_source", None),
        ("deterministic_digest_rerun", None),
    ],
)
def test_prepare_and_emit_payload_field_wiring(
    case: str,
    metadata_overrides: dict[str, Any] | None,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """AC-T.3 — sme_refs branch matrix + digest determinism across cases."""
    monkeypatch.setattr(pre_packet, "_REPO_ROOT", tmp_path)
    bundle_dir = tmp_path / "bundle"
    _write_bundle(bundle_dir, metadata_overrides=metadata_overrides)
    output_path = tmp_path / "out" / "irene-packet.md"
    log = _tmp_log(tmp_path)

    prepare_and_emit_irene_packet(
        bundle_dir=bundle_dir,
        run_id="TEST-RUN-FIELDS",
        output_path=output_path,
        dispatch=lambda envelope: dispatch_intake_pre_packet(envelope, log=log),
        plan_revision=0,
    )

    events = list(log.read_events())
    assert len(events) == 1
    payload = events[0].payload
    extracted_bytes = (bundle_dir / "extracted.md").read_bytes()
    metadata_bytes = (bundle_dir / "metadata.json").read_bytes()
    directives_bytes = (bundle_dir / "operator-directives.md").read_bytes()

    # Determinism: ingestion_digest == sha256(extracted + metadata + directives).
    expected_ingestion = hashlib.sha256(
        extracted_bytes + metadata_bytes + directives_bytes
    ).hexdigest()
    assert payload["ingestion_digest"] == expected_ingestion

    # step_03_extraction_checksum is a distinct narrower digest.
    expected_step_03 = hashlib.sha256(extracted_bytes).hexdigest()
    assert payload["step_03_extraction_checksum"] == expected_step_03
    assert payload["step_03_extraction_checksum"] != payload["ingestion_digest"]

    # sme_refs branch assertions.
    sme_refs = payload["sme_refs"]
    assert len(sme_refs) >= 1
    if case == "explicit_sme_refs":
        assert sme_refs[0]["source_id"] == "pdf-001"
        assert sme_refs[0]["path"] == "course-content/source.pdf"
        assert sme_refs[0]["content_digest"] == "a" * 64
    else:
        # Synthesized branch — uses primary_source as source_id + extracted digest.
        assert sme_refs[0]["source_id"] == "example.pdf"
        assert sme_refs[0]["path"] is None
        assert sme_refs[0]["content_digest"] == expected_step_03

    # Re-run determinism: second call with identical bundle produces identical digests.
    if case == "deterministic_digest_rerun":
        log2 = _tmp_log(tmp_path / "second_log")
        prepare_and_emit_irene_packet(
            bundle_dir=bundle_dir,
            run_id="TEST-RUN-FIELDS-REPEAT",
            output_path=tmp_path / "out2" / "irene-packet.md",
            dispatch=lambda envelope: dispatch_intake_pre_packet(envelope, log=log2),
            plan_revision=0,
        )
        rerun_payload = next(iter(log2.read_events())).payload
        assert rerun_payload["ingestion_digest"] == payload["ingestion_digest"]
        assert (
            rerun_payload["step_03_extraction_checksum"]
            == payload["step_03_extraction_checksum"]
        )


# ---------------------------------------------------------------------------
# AC-T.4 — zero-emission on prepare_irene_packet failure
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "missing_file",
    ["extracted.md", "metadata.json", "operator-directives.md"],
)
def test_prepare_and_emit_zero_emission_on_failure(
    missing_file: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC-T.4 — missing required input → FileNotFoundError + zero log entries."""
    monkeypatch.setattr(pre_packet, "_REPO_ROOT", tmp_path)
    bundle_dir = tmp_path / "bundle"
    _write_bundle(bundle_dir)
    (bundle_dir / missing_file).unlink()
    log = _tmp_log(tmp_path)

    with pytest.raises(FileNotFoundError) as exc_info:
        prepare_and_emit_irene_packet(
            bundle_dir=bundle_dir,
            run_id="TEST-RUN-FAIL",
            output_path=tmp_path / "out" / "irene-packet.md",
            dispatch=lambda envelope: dispatch_intake_pre_packet(envelope, log=log),
            plan_revision=0,
        )
    assert missing_file in str(exc_info.value)
    assert list(log.read_events()) == []
