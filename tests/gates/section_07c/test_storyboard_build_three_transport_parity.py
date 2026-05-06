from __future__ import annotations

from copy import deepcopy

import pytest

from app.gates.errors import GateError
from app.gates.section_07c.poll_surface import display_storyboard_targets, submit_verdict
from app.models.operator_verdict_section_07c import Section07COperatorVerdict
from tests.gates.section_07c._helpers import (
    PLAN_UNIT_ID,
    RUN_ID,
    SUBMITTED_AT,
    fixture_build_payload,
    fixture_storyboard_targets,
)


def _verdict_payload(digest: str) -> dict[str, object]:
    return {
        "run_id": RUN_ID,
        "verb": "submit",
        "operator_id": "operator_1",
        "submitted_at": SUBMITTED_AT,
        "decision_card_digest": digest,
        "build_payload": fixture_build_payload(),
    }


@pytest.mark.parametrize("transport", ["cli", "http", "mcp-stdio"])
def test_section_07c_transports_emit_equivalent_verdict(transport: str) -> None:
    displayed = display_storyboard_targets(fixture_storyboard_targets())
    baseline = submit_verdict(
        PLAN_UNIT_ID,
        _verdict_payload(displayed["decision_card_digest"]),
        "cli",
    )

    verdict = submit_verdict(
        PLAN_UNIT_ID,
        _verdict_payload(displayed["decision_card_digest"]),
        transport,  # type: ignore[arg-type]
    )

    assert verdict.model_dump(mode="json") == baseline.model_dump(mode="json")
    assert verdict.decision_card_digest == displayed["decision_card_digest"]


def test_section_07c_rejects_mismatched_plan_unit_id() -> None:
    displayed = display_storyboard_targets(fixture_storyboard_targets())

    with pytest.raises(GateError, match="plan_unit_id_mismatch"):
        submit_verdict(
            "other-unit",
            {
                **_verdict_payload(displayed["decision_card_digest"]),
                "plan_unit_id": PLAN_UNIT_ID,
            },
            "http",
        )


def test_section_07c_rejects_tampered_digest_shape() -> None:
    payload = deepcopy(_verdict_payload("a" * 64))
    payload["decision_card_digest"] = "not-a-digest"

    with pytest.raises(ValueError, match="decision_card_digest"):
        Section07COperatorVerdict.model_validate({**payload, "plan_unit_id": PLAN_UNIT_ID})
