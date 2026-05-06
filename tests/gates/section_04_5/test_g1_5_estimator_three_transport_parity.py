from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path

import pytest
import yaml

from app.gates.errors import GateError
from app.gates.section_04_5.poll_surface import (
    display_estimator,
    load_estimator,
    resume_from_verdict,
    submit_verdict,
)
from app.models.operator_verdict_section_04_5 import Section04_5OperatorVerdict
from tests.gates.section_04_5._helpers import RUN_ID, fixture_estimator_card


def _verdict_payload() -> dict[str, object]:
    estimator = fixture_estimator_card()
    displayed = display_estimator(estimator)
    return {
        "run_id": RUN_ID,
        "verb": "acknowledged",
        "operator_id": "operator_1",
        "submitted_at": datetime(2026, 5, 5, 12, 5, tzinfo=UTC),
        "decision_card_digest": displayed["decision_card_digest"],
    }


@pytest.mark.parametrize("transport", ["cli", "http", "mcp-stdio"])
def test_g1_5_estimator_transport_emits_equivalent_operator_verdict(
    transport: str,
) -> None:
    estimator = fixture_estimator_card()
    displayed = display_estimator(estimator)
    baseline = submit_verdict(
        displayed["estimator_id"],
        _verdict_payload(),
        "cli",
    ).model_dump(mode="json")

    verdict = submit_verdict(
        displayed["estimator_id"],
        _verdict_payload(),
        transport,  # type: ignore[arg-type]
    )

    assert verdict.model_dump(mode="json") == baseline
    resumed = resume_from_verdict(estimator, verdict)
    assert resumed["verb"] == "acknowledged"
    assert resumed["estimator"] == displayed["estimator"]


def test_g1_5_estimator_resume_rejects_tampered_digest() -> None:
    estimator = fixture_estimator_card()
    displayed = display_estimator(estimator)
    payload = _verdict_payload()
    payload["decision_card_digest"] = "0" * 64
    tampered = Section04_5OperatorVerdict.model_validate(
        {**payload, "estimator_id": displayed["estimator_id"]}
    )

    with pytest.raises(GateError, match="digest_mismatch"):
        resume_from_verdict(estimator, tampered)


def test_g1_5_estimator_loads_yaml_with_utf8(tmp_path: Path) -> None:
    estimator = fixture_estimator_card()
    estimator_path = tmp_path / "estimator.yaml"
    estimator_path.write_text(
        yaml.safe_dump(
            estimator.model_dump(mode="json"),
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )

    loaded = load_estimator(estimator_path)
    displayed = display_estimator(estimator_path)

    assert loaded == estimator
    assert displayed["estimator_id"] == str(estimator.card_id)


def test_g1_5_estimator_rejects_mismatched_estimator_id() -> None:
    estimator = fixture_estimator_card()
    displayed = display_estimator(estimator)
    payload = deepcopy(_verdict_payload())
    payload["estimator_id"] = displayed["estimator_id"]

    with pytest.raises(GateError, match="estimator_id_mismatch"):
        submit_verdict(f"{displayed['estimator_id']}-mismatch", payload, "http")
