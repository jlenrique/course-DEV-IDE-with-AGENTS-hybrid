"""Hermetic tests for W1 research-packet shape-pin."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import pytest

from app.marcus.lesson_plan import research_packet as rp
from app.marcus.lesson_plan.workbook_enrichment import RunEnvelopeCorruptError
from app.models.runtime.production_envelope import (
    ProductionEnvelope,
    SpecialistContribution,
    compute_output_digest,
)
from app.models.runtime.production_trial_envelope import ProductionTrialEnvelope


def _valid_entry(**overrides: object) -> dict:
    base = {
        "citation_id": "cite-001",
        "source_ref": "retrieval:scite:10.1000/x",
        "provider": "scite",
        "source_id": "10.1000/x",
        "title": "Example",
        "source_hash": "sha256:abc",
        "evidence_hierarchy_tier": "T4_peer_other",
        "peer_reviewed": True,
        "provider_provenance": ["scite"],
        "triangulation_status": "single_provider",
        "reliability_score": 0.5,
    }
    base.update(overrides)
    return base


def _write_run(
    run_dir: Path,
    *,
    entries: list[dict] | None = None,
    intake: dict | None = None,
    include_contribution: bool = True,
) -> None:
    trial_id = UUID("12345678-1234-4234-8234-123456789abc")
    contributions: list[SpecialistContribution] = []
    if include_contribution:
        output: dict = {
            "research_entries": entries if entries is not None else [],
        }
        if intake is not None:
            output["research_intake"] = intake
        contributions.append(
            SpecialistContribution.from_output(
                specialist_id="research_wiring",
                output=output,
                model_used="fixture",
                node_id="04.55",
                provenance="fixture",
            )
        )
    envelope = ProductionEnvelope(
        trial_id=trial_id,
        contributions=tuple(contributions),
        fixture_run=True,
    )
    started = datetime(2026, 7, 10, 12, 0, tzinfo=UTC)
    trial = ProductionTrialEnvelope(
        trial_id=trial_id,
        preset="explore",
        corpus_path="fixture",
        operator_id="w1-hermetic",
        started_at=started,
        completed_at=started,
        status="completed",
        production_clone_launch_evidence=True,
        production_envelope=envelope,
    )
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run.json").write_text(
        trial.model_dump_json(),
        encoding="utf-8",
    )


def test_absent_run_is_honest_empty(tmp_path: Path) -> None:
    packet = rp.load_research_packet(tmp_path)
    assert packet.status == "absent"
    assert packet.entries == ()
    assert "run_json_absent" in packet.known_losses


def test_empty_entries_honest(tmp_path: Path) -> None:
    _write_run(tmp_path, entries=[])
    packet = rp.load_research_packet(tmp_path)
    assert packet.status == "empty"
    assert packet.entries == ()


def test_ready_packet_shape_pin(tmp_path: Path) -> None:
    _write_run(tmp_path, entries=[_valid_entry()])
    packet = rp.load_research_packet(tmp_path)
    assert packet.status == "ready"
    assert len(packet.entries) == 1
    assert set(rp.REQUIRED_ENTRY_FIELDS).issubset(packet.entries[0].keys())


def test_malformed_entry_known_loss(tmp_path: Path) -> None:
    bad = _valid_entry()
    del bad["evidence_hierarchy_tier"]
    _write_run(tmp_path, entries=[bad, _valid_entry(citation_id="cite-002")])
    packet = rp.load_research_packet(tmp_path)
    assert packet.status == "degraded"
    assert len(packet.entries) == 1
    assert any(loss.startswith("entry_shape_invalid") for loss in packet.known_losses)


def test_corrupt_run_fail_loud(tmp_path: Path) -> None:
    (tmp_path / "run.json").write_text("{nope", encoding="utf-8")
    with pytest.raises(RunEnvelopeCorruptError):
        rp.load_research_packet(tmp_path)


def test_dual_consumers_share_digest(tmp_path: Path) -> None:
    _write_run(tmp_path, entries=[_valid_entry()])
    glossary = rp.resolve_for_glossary_writer(tmp_path)
    trends = rp.resolve_for_trends_projector(tmp_path)
    assert glossary.packet_digest == trends.packet_digest
    assert glossary.entries == trends.entries


def test_require_usable_fails_closed_on_empty(tmp_path: Path) -> None:
    _write_run(tmp_path, entries=[])
    with pytest.raises(rp.ResearchPacketShapeError, match="requires usable"):
        rp.resolve_for_glossary_writer(tmp_path, require_usable=True)


def test_research_entries_key_wrong_type_fail_loud(tmp_path: Path) -> None:
    trial_id = UUID("12345678-1234-4234-8234-123456789abc")
    output = {"research_entries": {"not": "a-list"}}
    contrib = SpecialistContribution(
        specialist_id="research_wiring",
        contributed_at=datetime(2026, 7, 10, 12, 0, tzinfo=UTC),
        output=output,
        cost_usd=0.0,
        model_used="fixture",
        output_digest=compute_output_digest(output),
        node_id="04.55",
        provenance="fixture",
    )
    envelope = ProductionEnvelope(
        trial_id=trial_id,
        contributions=(contrib,),
        fixture_run=True,
    )
    started = datetime(2026, 7, 10, 12, 0, tzinfo=UTC)
    trial = ProductionTrialEnvelope(
        trial_id=trial_id,
        preset="explore",
        corpus_path="fixture",
        operator_id="w1",
        started_at=started,
        completed_at=started,
        status="completed",
        production_clone_launch_evidence=True,
        production_envelope=envelope,
    )
    (tmp_path / "run.json").write_text(trial.model_dump_json(), encoding="utf-8")
    with pytest.raises(rp.ResearchPacketShapeError, match="must be a list"):
        rp.load_research_packet(tmp_path)
