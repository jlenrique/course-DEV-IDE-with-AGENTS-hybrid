from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from app.gates.errors import GateError
from app.gates.section_07d.poll_surface import (
    display_motion_plan_status,
    load_motion_plan_card,
    resume_from_verdict,
    submit_verdict,
)
from app.models.operator_verdict_section_07d import Section07DOperatorVerdict
from tests.gates.section_07d._helpers import (
    RUN_ID,
    SUBMITTED_AT,
    fixture_motion_plan_card,
)


def _verdict_payload(digest: str) -> dict[str, object]:
    return {
        "run_id": RUN_ID,
        "verb": "approve",
        "operator_id": "operator_1",
        "submitted_at": SUBMITTED_AT,
        "decision_card_digest": digest,
    }


@pytest.mark.parametrize("transport", ["cli", "http", "mcp-stdio"])
def test_g2_5_poll_surface_transport_emits_equivalent_operator_verdict(
    transport: str,
) -> None:
    motion_plan = fixture_motion_plan_card()
    display = display_motion_plan_status(motion_plan)
    baseline = submit_verdict(
        display["motion_plan_id"],
        _verdict_payload(display["decision_card_digest"]),
        "cli",
    )

    verdict = submit_verdict(
        display["motion_plan_id"],
        _verdict_payload(display["decision_card_digest"]),
        transport,  # type: ignore[arg-type]
    )

    assert verdict.model_dump(mode="json") == baseline.model_dump(mode="json")
    assert verdict.decision_card_digest == display["decision_card_digest"]
    resumed = resume_from_verdict(motion_plan, verdict)
    assert resumed["verb"] == "approve"
    assert resumed["motion_plan_status"] == "completed"
    assert resumed["decision_card"] == display["decision_card"]


def test_g2_5_poll_surface_resume_rejects_tampered_digest() -> None:
    motion_plan = fixture_motion_plan_card()
    display = display_motion_plan_status(motion_plan)
    payload = deepcopy(_verdict_payload(display["decision_card_digest"]))
    payload["decision_card_digest"] = "0" * 64
    tampered = Section07DOperatorVerdict.model_validate(
        {**payload, "motion_plan_id": display["motion_plan_id"]}
    )

    with pytest.raises(GateError, match="digest_mismatch"):
        resume_from_verdict(motion_plan, tampered)


def test_g2_5_poll_surface_loads_yaml_with_utf8(tmp_path: Path) -> None:
    motion_plan = fixture_motion_plan_card()
    motion_plan_path = tmp_path / "motion-plan.yaml"
    motion_plan_path.write_text(
        yaml.safe_dump(
            motion_plan.model_dump(mode="json"),
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )

    loaded = load_motion_plan_card(motion_plan_path)
    display = display_motion_plan_status(motion_plan_path)

    assert loaded == motion_plan
    assert display["motion_plan_id"] == str(motion_plan.card_id)
    assert display["motion_plan_status"] == "completed"


def test_g2_5_poll_surface_rejects_mismatched_motion_plan_id() -> None:
    motion_plan = fixture_motion_plan_card()
    display = display_motion_plan_status(motion_plan)

    with pytest.raises(GateError, match="motion_plan_id_mismatch"):
        submit_verdict(
            f"{display['motion_plan_id']}-mismatch",
            {
                **_verdict_payload(display["decision_card_digest"]),
                "motion_plan_id": display["motion_plan_id"],
            },
            "http",
        )
