"""Two-mode lifecycle-invariant pins for ProductionTrialEnvelope.

Drift micro-batch 2026-06-12 (Dr. Quinn "witness, don't gate" synthesis,
party 4/4 ACCEPT-WITH-CONDITION, operator GO). Order matters and is itself
the contract (Murat sequencing):

1. CHARACTERIZATION FIRST — every persisted run.json we can see round-trips
   through default (witness) validation without raising. This pins the
   compat surface before anything tightens.
2. Strict red/green twins per invariant — strict mode raises with the
   violation named; satisfied states pass.
3. Witness-path coverage — a violation in default mode is RECORDED, never
   raised (a witness that silently swallows is the next quality theater).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.models.runtime import ProductionEnvelope
from app.models.runtime.production_trial_envelope import ProductionTrialEnvelope

REPO_ROOT = Path(__file__).resolve().parents[3]
GOLDEN = REPO_ROOT / "tests" / "fixtures" / "runtime" / "production_trial_envelope_golden.json"
STRICT = {"invariant_mode": "strict"}
TRIAL_ID = UUID("52345678-1234-4234-8234-123456789abc")


def _base_payload(**overrides) -> dict:
    payload = {
        "trial_id": TRIAL_ID,
        "preset": "production",
        "corpus_path": "tests/fixtures/trial_corpus/README.md",
        "operator_id": "operator_test",
        "started_at": datetime.now(tz=UTC),
        "status": "in-flight",
        "production_clone_launch_evidence": False,
        "production_envelope": ProductionEnvelope(trial_id=TRIAL_ID),
    }
    payload.update(overrides)
    return payload


# ---------------------------------------------------------------------------
# 1. Characterization: persisted artifacts round-trip in witness mode
# ---------------------------------------------------------------------------

def _persisted_run_jsons() -> list[Path]:
    # Live trial run dirs (gitignored; present only on the operator machine).
    runs_root = REPO_ROOT / "state" / "config" / "runs"
    paths = sorted(runs_root.glob("*/run.json")) if runs_root.exists() else []
    if GOLDEN.exists():
        paths.append(GOLDEN)
    return paths


def test_every_persisted_run_json_round_trips_in_witness_mode() -> None:
    paths = _persisted_run_jsons()
    if not paths:
        pytest.skip("no persisted run.json artifacts visible in this checkout")
    for path in paths:
        envelope = ProductionTrialEnvelope.model_validate_json(
            path.read_text(encoding="utf-8-sig")
        )
        # dump→validate stability via the JSON path (strict mode rejects
        # plain-dict string UUIDs/datetimes — the known S2 trap).
        again = ProductionTrialEnvelope.model_validate_json(envelope.model_dump_json())
        assert again.trial_id == envelope.trial_id, path


# ---------------------------------------------------------------------------
# 2. Strict mode: red/green twins per invariant
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("overrides", "fragment"),
    [
        ({"status": "paused-at-gate", "paused_gate": None}, "requires paused_gate"),
        ({"status": "paused-at-error", "paused_error_tag": None}, "requires paused_error_tag"),
        ({"status": "completed", "completed_at": None}, "requires completed_at"),
    ],
)
def test_strict_mode_rejects_impossible_lifecycle_state(overrides, fragment) -> None:
    with pytest.raises(ValidationError, match=fragment):
        ProductionTrialEnvelope.model_validate(_base_payload(**overrides), context=STRICT)


@pytest.mark.parametrize(
    "overrides",
    [
        {"status": "paused-at-gate", "paused_gate": "G1"},
        {"status": "paused-at-error", "paused_error_tag": "gamma.input.missing"},
        {"status": "completed", "completed_at": datetime.now(tz=UTC)},
        {"status": "registered"},
        {"status": "in-flight"},
        {"status": "failed"},
    ],
)
def test_strict_mode_accepts_satisfied_lifecycle_state(overrides) -> None:
    envelope = ProductionTrialEnvelope.model_validate(_base_payload(**overrides), context=STRICT)
    assert envelope.status == overrides["status"]


# ---------------------------------------------------------------------------
# 3. Witness mode: violation recorded, never raised
# ---------------------------------------------------------------------------

def test_witness_mode_records_violation_without_raising(tmp_path: Path, caplog) -> None:
    sink = tmp_path / "anomalies.jsonl"
    with caplog.at_level("WARNING"):
        envelope = ProductionTrialEnvelope.model_validate(
            _base_payload(status="paused-at-error", paused_error_tag=None),
            context={"anomaly_sink": sink},
        )
    assert envelope.status == "paused-at-error"  # construction survived
    assert "lifecycle invariant violation" in caplog.text
    rows = [json.loads(line) for line in sink.read_text(encoding="utf-8").splitlines()]
    assert rows and rows[0]["violations"] == ["status=paused-at-error requires paused_error_tag"]
    assert rows[0]["trial_id"] == str(TRIAL_ID)


def test_witness_mode_without_sink_only_logs(caplog) -> None:
    with caplog.at_level("WARNING"):
        envelope = ProductionTrialEnvelope.model_validate(
            _base_payload(status="completed", completed_at=None)
        )
    assert envelope.status == "completed"
    assert "requires completed_at" in caplog.text


def test_witness_mode_silent_on_satisfied_state(tmp_path: Path, caplog) -> None:
    sink = tmp_path / "anomalies.jsonl"
    with caplog.at_level("WARNING"):
        ProductionTrialEnvelope.model_validate(
            _base_payload(status="paused-at-gate", paused_gate="G1"),
            context={"anomaly_sink": sink},
        )
    assert not sink.exists()
    assert "lifecycle invariant violation" not in caplog.text
