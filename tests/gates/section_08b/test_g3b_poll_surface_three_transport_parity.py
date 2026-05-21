from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from app.gates.errors import GateError
from app.gates.section_08b.poll_surface import (
    display_storyboard_b,
    load_storyboard_b,
    resume_from_verdict,
    submit_verdict,
)
from app.models.operator_verdict_section_08b import Section08BOperatorVerdict
from tests.gates.section_08b._helpers import (
    RUN_ID,
    SUBMITTED_AT,
    fixture_storyboard_b_card,
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
def test_g3b_poll_surface_transport_emits_equivalent_operator_verdict(
    transport: str,
) -> None:
    storyboard = fixture_storyboard_b_card()
    display = display_storyboard_b(storyboard)
    baseline = submit_verdict(
        display["storyboard_id"],
        _verdict_payload(display["decision_card_digest"]),
        "cli",
    )

    verdict = submit_verdict(
        display["storyboard_id"],
        _verdict_payload(display["decision_card_digest"]),
        transport,  # type: ignore[arg-type]
    )

    assert verdict.model_dump(mode="json") == baseline.model_dump(mode="json")
    assert verdict.decision_card_digest == display["decision_card_digest"]
    resumed = resume_from_verdict(storyboard, verdict)
    assert resumed["verb"] == "approve"
    assert resumed["decision_card"] == display["decision_card"]


def test_g3b_poll_surface_resume_rejects_tampered_digest() -> None:
    storyboard = fixture_storyboard_b_card()
    display = display_storyboard_b(storyboard)
    payload = deepcopy(_verdict_payload(display["decision_card_digest"]))
    payload["decision_card_digest"] = "0" * 64
    tampered = Section08BOperatorVerdict.model_validate(
        {**payload, "storyboard_id": display["storyboard_id"]}
    )

    with pytest.raises(GateError, match="digest_mismatch"):
        resume_from_verdict(storyboard, tampered)


def test_g3b_poll_surface_loads_yaml_with_utf8(tmp_path: Path) -> None:
    storyboard = fixture_storyboard_b_card()
    storyboard_path = tmp_path / "storyboard-b.yaml"
    storyboard_path.write_text(
        yaml.safe_dump(
            storyboard.model_dump(mode="json"),
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )

    loaded = load_storyboard_b(storyboard_path)
    display = display_storyboard_b(storyboard_path)

    assert loaded == storyboard
    assert display["storyboard_id"] == str(storyboard.card_id)


def test_g3b_poll_surface_rejects_mismatched_storyboard_id() -> None:
    storyboard = fixture_storyboard_b_card()
    display = display_storyboard_b(storyboard)

    with pytest.raises(GateError, match="storyboard_id_mismatch"):
        submit_verdict(
            f"{display['storyboard_id']}-mismatch",
            {
                **_verdict_payload(display["decision_card_digest"]),
                "storyboard_id": display["storyboard_id"],
            },
            "http",
        )
