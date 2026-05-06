from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from app.gates.errors import GateError
from app.gates.section_04a.poll_surface import (
    apply_plan_unit_edit,
    display_plan_unit,
    load_plan_unit,
    resume_from_verdict,
    submit_verdict,
)
from app.models.operator_verdict_section_04a import (
    PlanUnitEditPayload,
    Section04AOperatorVerdict,
    Section04AVerdictVerb,
)
from marcus.lesson_plan.schema import PlanUnit
from tests.gates.section_04a._helpers import fixture_plan_unit


def _transport_response(
    *,
    transport: str,
    plan_unit: PlanUnit,
    verb: Section04AVerdictVerb,
    operator_id: str,
    edit_payload: dict[str, object] | None = None,
) -> dict[str, object]:
    typed_edit_payload = (
        None if edit_payload is None else PlanUnitEditPayload(updates=edit_payload)
    )
    displayed_plan_unit = (
        plan_unit
        if typed_edit_payload is None
        else apply_plan_unit_edit(plan_unit, typed_edit_payload)
    )
    display = display_plan_unit(displayed_plan_unit)
    verdict = submit_verdict(
        display["plan_unit"]["unit_id"],
        {
            "run_id": display["decision_card"]["trial_id"],
            "verb": verb,
            "operator_id": operator_id,
            "submitted_at": display["decision_card"]["created_at"],
            "decision_card_digest": display["decision_card_digest"],
            "edit_payload": (
                None
                if typed_edit_payload is None
                else typed_edit_payload.model_dump(mode="json")
            ),
        },
        transport,  # type: ignore[arg-type]
    )
    return {
        "transport": transport,
        "display": display,
        "operator_verdict": verdict.model_dump(mode="json"),
        "resume": resume_from_verdict(plan_unit, verdict),
    }


@pytest.mark.parametrize("transport", ["cli", "http", "mcp-stdio"])
def test_g1a_poll_surface_transport_emits_equivalent_operator_verdict(
    transport: str,
) -> None:
    plan_unit = fixture_plan_unit()
    baseline_response = _transport_response(
        transport="cli",
        plan_unit=plan_unit,
        verb="approve",
        operator_id="operator_1",
    )

    response = _transport_response(
        transport=transport,
        plan_unit=plan_unit,
        verb="approve",
        operator_id="operator_1",
    )

    assert response["operator_verdict"] == baseline_response["operator_verdict"]
    assert response["display"]["decision_card_digest"] == baseline_response["display"][
        "decision_card_digest"
    ]
    verdict = Section04AOperatorVerdict.model_validate(response["operator_verdict"])
    resumed = resume_from_verdict(plan_unit, verdict)
    assert resumed["verb"] == "approve"
    assert resumed["plan_unit"] == plan_unit.model_dump(mode="json")


def test_g1a_poll_surface_edit_updates_digest_and_plan_unit() -> None:
    plan_unit = fixture_plan_unit()

    response = _transport_response(
        transport="http",
        plan_unit=plan_unit,
        verb="edit",
        operator_id="operator_1",
        edit_payload={"rationale": "Operator ratified this revised wording."},
    )

    verdict = Section04AOperatorVerdict.model_validate(response["operator_verdict"])
    resumed = resume_from_verdict(plan_unit, verdict)
    assert resumed["plan_unit"]["rationale"] == "Operator ratified this revised wording."
    assert verdict.decision_card_digest == response["display"]["decision_card_digest"]


def test_g1a_poll_surface_resume_rejects_tampered_digest() -> None:
    plan_unit = fixture_plan_unit()
    response = _transport_response(
        transport="http",
        plan_unit=plan_unit,
        verb="approve",
        operator_id="operator_1",
    )
    payload = deepcopy(response["operator_verdict"])
    payload["decision_card_digest"] = "0" * 64
    tampered = Section04AOperatorVerdict.model_validate(payload)

    with pytest.raises(GateError, match="digest_mismatch"):
        resume_from_verdict(plan_unit, tampered)


def test_g1a_poll_surface_loads_plan_unit_yaml_with_utf8(tmp_path: Path) -> None:
    plan_unit = fixture_plan_unit()
    plan_unit_path = tmp_path / "plan_unit.yaml"
    plan_unit_path.write_text(
        yaml.safe_dump(
            plan_unit.model_dump(mode="json"),
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )

    loaded = load_plan_unit(plan_unit_path)
    response = _transport_response(
        transport="cli",
        plan_unit=loaded,
        verb="approve",
        operator_id="operator_1",
    )

    assert loaded == plan_unit
    assert response["operator_verdict"]["plan_unit_id"] == plan_unit.unit_id
