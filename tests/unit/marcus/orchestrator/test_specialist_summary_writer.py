from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from app.marcus.orchestrator import specialist_summary_writer as writer

TRIAL_ID = UUID("12345678-1234-4234-8234-123456789abc")


def test_writer_emits_for_texas_completion(tmp_path) -> None:
    path = writer.emit_summary(
        specialist_id="texas",
        trial_id=TRIAL_ID,
        gate_id="G1",
        runs_root=tmp_path,
        timestamp_utc=datetime(2026, 4, 29, tzinfo=UTC),
    )

    assert path.name.startswith("texas-")
    assert "# Texas - G1 - 2026-04-29T00:00:00Z" in path.read_text(encoding="utf-8")


def test_writer_emits_for_irene_completion(tmp_path) -> None:
    path = writer.emit_summary(
        specialist_id="irene",
        trial_id=TRIAL_ID,
        gate_id="G2C",
        runs_root=tmp_path,
        timestamp_utc=datetime(2026, 4, 29, 1, tzinfo=UTC),
    )

    assert path.name.startswith("irene-")
    assert "specialist_id: irene" in path.read_text(encoding="utf-8")


def test_deferred_specialist_emits_noop_marker(tmp_path) -> None:
    path = writer.emit_summary(
        specialist_id="dan",
        trial_id=TRIAL_ID,
        gate_id="G3",
        runs_root=tmp_path,
        timestamp_utc=datetime(2026, 4, 29, 2, tzinfo=UTC),
    )

    assert "<deferred per Slab 7b roadmap>" in path.read_text(encoding="utf-8")


def test_timestamp_is_iso_utc_in_summary_header(tmp_path) -> None:
    path = writer.emit_summary(
        specialist_id="vera",
        trial_id=TRIAL_ID,
        gate_id="G4",
        runs_root=tmp_path,
        timestamp_utc=datetime(2026, 4, 29, 3, 4, 5, tzinfo=UTC),
    )

    assert "2026-04-29T03:04:05Z" in path.read_text(encoding="utf-8").splitlines()[0]


def test_canonical_specialist_id_alias_is_used(tmp_path) -> None:
    path = writer.emit_summary(
        specialist_id="quinn-r",
        trial_id=TRIAL_ID,
        gate_id="G4",
        runs_root=tmp_path,
        timestamp_utc=datetime(2026, 4, 29, 4, tzinfo=UTC),
    )

    assert path.name.startswith("quinn_r-")
