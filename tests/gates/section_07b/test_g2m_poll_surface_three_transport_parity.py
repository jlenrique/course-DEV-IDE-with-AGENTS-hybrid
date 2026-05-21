from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from app.gates.errors import GateError
from app.gates.section_07b.poll_surface import (
    display_per_slide_variant,
    load_per_slide_variant,
    resume_from_verdict,
    submit_verdict,
)
from app.models.operator_verdict_section_07b import Section07BOperatorVerdict
from tests.gates.section_07b._helpers import (
    RUN_ID,
    SLIDE_ID,
    SUBMITTED_AT,
    fixture_per_slide_variant_card,
)


def _verdict_payload(digest: str) -> dict[str, object]:
    return {
        "run_id": RUN_ID,
        "verb": "select",
        "operator_id": "operator_1",
        "submitted_at": SUBMITTED_AT,
        "decision_card_digest": digest,
        "select_payload": {
            "selected_variant": "A",
            "rationale": "Cleaner treatment for this slide.",
        },
    }


@pytest.mark.parametrize("transport", ["cli", "http", "mcp-stdio"])
def test_g2m_poll_surface_transport_emits_equivalent_operator_verdict(
    transport: str,
) -> None:
    variant_card = fixture_per_slide_variant_card()
    display = display_per_slide_variant(variant_card)
    baseline = submit_verdict(
        SLIDE_ID,
        _verdict_payload(display["decision_card_digest"]),
        "cli",
    )

    verdict = submit_verdict(
        SLIDE_ID,
        _verdict_payload(display["decision_card_digest"]),
        transport,  # type: ignore[arg-type]
    )

    assert verdict.model_dump(mode="json") == baseline.model_dump(mode="json")
    assert verdict.decision_card_digest == display["decision_card_digest"]
    resumed = resume_from_verdict(variant_card, verdict)
    assert resumed["verb"] == "select"
    assert resumed["slide_id"] == SLIDE_ID
    assert resumed["per_slide_variant_payload"] == display["per_slide_variant_payload"]


def test_g2m_poll_surface_resume_rejects_tampered_digest() -> None:
    variant_card = fixture_per_slide_variant_card()
    display = display_per_slide_variant(variant_card)
    payload = deepcopy(_verdict_payload(display["decision_card_digest"]))
    payload["decision_card_digest"] = "0" * 64
    tampered = Section07BOperatorVerdict.model_validate(
        {**payload, "slide_id": SLIDE_ID}
    )

    with pytest.raises(GateError, match="digest_mismatch"):
        resume_from_verdict(variant_card, tampered)


def test_g2m_poll_surface_loads_yaml_with_utf8(tmp_path: Path) -> None:
    variant_card = fixture_per_slide_variant_card()
    variant_path = tmp_path / "per-slide-variant.yaml"
    variant_path.write_text(
        yaml.safe_dump(
            variant_card.model_dump(mode="json"),
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )

    loaded = load_per_slide_variant(variant_path)
    display = display_per_slide_variant(variant_path)

    assert loaded == variant_card
    assert display["slide_variant_id"] == str(variant_card.card_id)


def test_g2m_poll_surface_rejects_mismatched_slide_id() -> None:
    variant_card = fixture_per_slide_variant_card()
    display = display_per_slide_variant(variant_card)

    with pytest.raises(GateError, match="slide_id_mismatch"):
        submit_verdict(
            f"{SLIDE_ID}-mismatch",
            {
                **_verdict_payload(display["decision_card_digest"]),
                "slide_id": SLIDE_ID,
            },
            "http",
        )
