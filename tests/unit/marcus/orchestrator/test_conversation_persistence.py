from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from app.marcus.orchestrator import conversation_persistence as cp

TRIAL_ID = "12345678-1234-4234-8234-123456789abc"


def _directive(tmp_path: Path) -> None:
    run_dir = tmp_path / TRIAL_ID
    run_dir.mkdir(parents=True)
    (run_dir / "directive.yaml").write_text("trial: test\n", encoding="utf-8")


def _card() -> dict[str, object]:
    return {
        "decision": "confirm",
        "directive": "accept-as-is",
        "rationale": "The evidence is complete enough.",
        "confidence": 0.9,
        "confidence_signals": ["complete"],
    }


def test_write_turn_creates_gate_directory_and_zero_padded_file(tmp_path: Path) -> None:
    _directive(tmp_path)

    path = cp.write_turn(
        trial_id=TRIAL_ID,
        gate_id="G1",
        decision_card=_card(),
        free_text_rationale="operator prose",
        operator_id="operator_test",
        runs_root=tmp_path,
        timestamp_utc=datetime(2026, 4, 29, tzinfo=UTC),
    )

    assert path == tmp_path / TRIAL_ID / "conversation" / "G1" / "0000.json"
    assert path.exists()


def test_turn_json_contains_structured_record_fields(tmp_path: Path) -> None:
    _directive(tmp_path)

    path = cp.write_turn(
        trial_id=TRIAL_ID,
        gate_id="G1",
        decision_card=_card(),
        free_text_rationale="operator prose",
        operator_id="operator_test",
        runs_root=tmp_path,
        timestamp_utc=datetime(2026, 4, 29, tzinfo=UTC),
    )
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["_schema_version"] == "1.0"
    assert payload["turn_index"] == 0
    assert payload["decision_card"]["directive"] == "accept-as-is"
    assert len(payload["prior_envelope_digest"]) == 64
    assert len(payload["digest"]) == 64


def test_next_turn_index_is_gate_local(tmp_path: Path) -> None:
    _directive(tmp_path)
    for index, gate_id in enumerate(["G1", "G1", "G2C"]):
        cp.write_turn(
            trial_id=TRIAL_ID,
            gate_id=gate_id,
            decision_card=_card(),
            free_text_rationale="operator prose",
            operator_id="operator_test",
            runs_root=tmp_path,
            timestamp_utc=datetime(2026, 4, 29, 0, index, tzinfo=UTC),
        )

    assert (tmp_path / TRIAL_ID / "conversation" / "G1" / "0001.json").exists()
    assert (tmp_path / TRIAL_ID / "conversation" / "G2C" / "0000.json").exists()


def test_digest_matches_canonical_formula(tmp_path: Path) -> None:
    _directive(tmp_path)
    timestamp = datetime(2026, 4, 29, tzinfo=UTC)

    path = cp.write_turn(
        trial_id=TRIAL_ID,
        gate_id="G1",
        decision_card=_card(),
        free_text_rationale="operator prose",
        operator_id="operator_test",
        runs_root=tmp_path,
        timestamp_utc=timestamp,
    )
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["digest"] == cp.compute_turn_digest(
        prior_envelope_digest=payload["prior_envelope_digest"],
        decision_card=payload["decision_card"],
        timestamp_utc=payload["timestamp_utc"],
        operator_id="operator_test",
    )
