from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from app.marcus.orchestrator import production_runner
from app.marcus.orchestrator import specialist_summary_writer as writer

TRIAL_ID = UUID("12345678-1234-4234-8234-123456789abc")


def _card(tmp_path):
    return production_runner._build_decision_card(
        gate_id="G1",
        trial_id=TRIAL_ID,
        node_id="04",
        operator_id="operator_test",
        pending_nodes=[],
        artifact_paths=[],
        runs_root=tmp_path,
    )


def test_gate_handler_loads_most_recent_summary_into_evidence(tmp_path) -> None:
    writer.emit_summary(
        specialist_id="texas",
        trial_id=TRIAL_ID,
        gate_id="G1",
        runs_root=tmp_path,
        timestamp_utc=datetime(2026, 4, 29, 0, tzinfo=UTC),
    )

    card = _card(tmp_path)

    assert card.evidence[-1]["kind"] == "specialist-summary"
    assert "specialist_id: texas" in card.evidence[-1]["content"]


def test_no_summary_leaves_evidence_unchanged(tmp_path) -> None:
    card = _card(tmp_path)

    assert card.evidence == [{"kind": "production-runner", "node_id": "04"}]


def test_multiple_summaries_load_only_most_recent(tmp_path) -> None:
    writer.emit_summary(
        specialist_id="texas",
        trial_id=TRIAL_ID,
        gate_id="G1",
        runs_root=tmp_path,
        timestamp_utc=datetime(2026, 4, 29, 0, tzinfo=UTC),
    )
    writer.emit_summary(
        specialist_id="irene",
        trial_id=TRIAL_ID,
        gate_id="G2C",
        runs_root=tmp_path,
        timestamp_utc=datetime(2026, 4, 29, 1, tzinfo=UTC),
    )

    card = _card(tmp_path)

    assert len([item for item in card.evidence if item["kind"] == "specialist-summary"]) == 1
    assert "specialist_id: irene" in card.evidence[-1]["content"]
