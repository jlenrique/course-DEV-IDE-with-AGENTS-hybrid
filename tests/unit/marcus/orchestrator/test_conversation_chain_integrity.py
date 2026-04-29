from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.marcus.orchestrator import conversation_persistence as cp

TRIAL_ID = "12345678-1234-4234-8234-123456789abc"


def _card(index: int = 0) -> dict[str, object]:
    return {
        "decision": "confirm",
        "directive": "accept-as-is",
        "rationale": f"The evidence is complete enough for turn {index}.",
        "confidence": 0.8,
        "confidence_signals": ["complete"],
    }


def _chain(tmp_path: Path, count: int = 3) -> list[Path]:
    run_dir = tmp_path / TRIAL_ID
    run_dir.mkdir(parents=True)
    (run_dir / "directive.yaml").write_text("trial: test\n", encoding="utf-8")
    return [
        cp.write_turn(
            trial_id=TRIAL_ID,
            gate_id="G1",
            decision_card=_card(index),
            free_text_rationale="operator prose",
            operator_id="operator_test",
            runs_root=tmp_path,
            timestamp_utc=datetime(2026, 4, 29, 0, index, tzinfo=UTC),
        )
        for index in range(count)
    ]


def test_valid_three_turn_sequence_verifies(tmp_path: Path) -> None:
    _chain(tmp_path)

    assert cp.verify_chain(TRIAL_ID, tmp_path) is True


def test_tampered_turn_raises_chain_broken(tmp_path: Path) -> None:
    paths = _chain(tmp_path)
    payload = json.loads(paths[2].read_text(encoding="utf-8"))
    payload["decision_card"]["rationale"] = "tampered rationale with enough chars"
    paths[2].write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(cp.ConversationChainBrokenError, match="digest mismatch"):
        cp.verify_chain(TRIAL_ID, tmp_path)


def test_missing_prior_digest_field_raises(tmp_path: Path) -> None:
    paths = _chain(tmp_path, count=1)
    payload = json.loads(paths[0].read_text(encoding="utf-8"))
    payload.pop("prior_envelope_digest")
    paths[0].write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(cp.ConversationChainBrokenError, match="prior_envelope_digest"):
        cp.verify_chain(TRIAL_ID, tmp_path)


def test_recompute_matches_stored_digest(tmp_path: Path) -> None:
    path = _chain(tmp_path, count=1)[0]
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["digest"] == cp.compute_turn_digest(
        prior_envelope_digest=payload["prior_envelope_digest"],
        decision_card=payload["decision_card"],
        timestamp_utc=payload["timestamp_utc"],
        operator_id=payload["operator_id"],
    )


def test_first_turn_anchors_at_directive_yaml_digest(tmp_path: Path) -> None:
    path = _chain(tmp_path, count=1)[0]
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["prior_envelope_digest"] == cp.directive_digest(TRIAL_ID, tmp_path)
