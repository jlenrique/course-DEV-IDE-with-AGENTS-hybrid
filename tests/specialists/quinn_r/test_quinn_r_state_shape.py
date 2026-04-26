"""State-shape pins for generated specialist quinn_r."""

from __future__ import annotations

import json
from pathlib import Path

from app.specialists.quinn_r.state import QuinnREnvelope, QuinnRReturn

FIXTURE_ROOT = Path("tests") / "fixtures" / "specialists" / "quinn_r"


def test_quinn_r_envelope_and_return_subclass_bases() -> None:
    assert QuinnREnvelope._SPECIALIST_ID == "quinn_r"
    assert QuinnRReturn._SPECIALIST_ID == "quinn_r"


def test_quinn_r_golden_envelope_round_trip() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_envelope.json").read_text(encoding="utf-8"))
    model = QuinnREnvelope.model_validate(payload)
    assert model.specialist_id == "quinn_r"


def test_quinn_r_golden_return_round_trip() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    model = QuinnRReturn.model_validate(payload)
    assert model.specialist_id == "quinn_r"


def test_quinn_r_return_accepts_quinn_r_review_mapping() -> None:
    model = QuinnRReturn(
        specialist_id="quinn_r",
        verb="proceed",
        payload={},
        quinn_r_review={"status": "pass", "findings": [{"id": "Q-1"}]},
    )
    assert model.quinn_r_review is not None


def test_quinn_r_envelope_rejects_non_mapping_payload() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_envelope.json").read_text(encoding="utf-8"))
    payload["payload_in"] = "not-a-mapping"
    try:
        QuinnREnvelope.model_validate(payload)
    except Exception as exc:  # pragma: no cover - pydantic validation detail
        assert "payload_in" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("expected payload_in validation to fail")
