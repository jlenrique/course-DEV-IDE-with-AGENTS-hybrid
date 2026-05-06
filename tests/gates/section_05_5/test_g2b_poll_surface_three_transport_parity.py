from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from app.gates.errors import GateError
from app.gates.section_05_5.poll_surface import (
    display_per_slide_mode,
    load_per_slide_mode,
    resume_from_verdict,
    submit_verdict,
)
from app.models.operator_verdict_section_05_5 import Section05_5OperatorVerdict
from tests.gates.section_05_5._helpers import (
    RUN_ID,
    SUBMITTED_AT,
    fixture_per_slide_mode_card,
)


def _verdict_payload(digest: str) -> dict[str, object]:
    return {
        "run_id": RUN_ID,
        "verb": "select",
        "operator_id": "operator_1",
        "submitted_at": SUBMITTED_AT,
        "decision_card_digest": digest,
        "select_payload": {
            "selected_mode": "motion-enabled-narrated-lesson",
            "rationale": "This slide benefits from motion-first narration.",
        },
    }


@pytest.mark.parametrize("transport", ["cli", "http", "mcp-stdio"])
def test_g2b_poll_surface_transport_emits_equivalent_operator_verdict(
    transport: str,
) -> None:
    per_slide_card = fixture_per_slide_mode_card()
    display = display_per_slide_mode(per_slide_card)
    baseline = submit_verdict(
        display["slide_id"],
        _verdict_payload(display["decision_card_digest"]),
        "cli",
    )

    verdict = submit_verdict(
        display["slide_id"],
        _verdict_payload(display["decision_card_digest"]),
        transport,  # type: ignore[arg-type]
    )

    assert verdict.model_dump(mode="json") == baseline.model_dump(mode="json")
    assert verdict.decision_card_digest == display["decision_card_digest"]
    resumed = resume_from_verdict(per_slide_card, verdict)
    assert resumed["verb"] == "select"
    assert resumed["per_slide_mode_payload"] == display["per_slide_mode_payload"]


def test_g2b_poll_surface_resume_rejects_tampered_digest() -> None:
    per_slide_card = fixture_per_slide_mode_card()
    display = display_per_slide_mode(per_slide_card)
    payload = deepcopy(_verdict_payload(display["decision_card_digest"]))
    payload["decision_card_digest"] = "0" * 64
    tampered = Section05_5OperatorVerdict.model_validate(
        {**payload, "slide_id": display["slide_id"]}
    )

    with pytest.raises(GateError, match="digest_mismatch"):
        resume_from_verdict(per_slide_card, tampered)


def test_g2b_poll_surface_loads_yaml_with_utf8(tmp_path: Path) -> None:
    per_slide_card = fixture_per_slide_mode_card()
    mode_path = tmp_path / "per-slide-mode.yaml"
    mode_path.write_text(
        yaml.safe_dump(
            per_slide_card.model_dump(mode="json"),
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )

    loaded = load_per_slide_mode(mode_path)
    display = display_per_slide_mode(mode_path)

    assert loaded == per_slide_card
    assert display["slide_id"] == str(per_slide_card.card_id)


def test_g2b_poll_surface_rejects_mismatched_slide_id() -> None:
    per_slide_card = fixture_per_slide_mode_card()
    display = display_per_slide_mode(per_slide_card)

    with pytest.raises(GateError, match="slide_id_mismatch"):
        submit_verdict(
            f"{display['slide_id']}-mismatch",
            {
                **_verdict_payload(display["decision_card_digest"]),
                "slide_id": display["slide_id"],
            },
            "http",
        )

