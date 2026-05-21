from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from app.gates.errors import GateError
from app.gates.section_11.poll_surface import (
    display_voice_candidates,
    load_voice_selection,
    resume_from_verdict,
    submit_verdict,
)
from app.models.operator_verdict_section_11 import Section11OperatorVerdict
from tests.gates.section_11._helpers import (
    RUN_ID,
    SUBMITTED_AT,
    fixture_voice_selection_card,
)


def _verdict_payload(digest: str) -> dict[str, object]:
    return {
        "run_id": RUN_ID,
        "verb": "select",
        "operator_id": "operator_1",
        "submitted_at": SUBMITTED_AT,
        "decision_card_digest": digest,
        "select_payload": {
            "selected_voice_id": "en-US-narrator",
            "rationale": "Best pacing match for this lesson.",
        },
    }


@pytest.mark.parametrize("transport", ["cli", "http", "mcp-stdio"])
def test_g4a_poll_surface_transport_emits_equivalent_operator_verdict(
    transport: str,
) -> None:
    voice_card = fixture_voice_selection_card()
    display = display_voice_candidates(voice_card)
    baseline = submit_verdict(
        display["voice_selection_id"],
        _verdict_payload(display["decision_card_digest"]),
        "cli",
    )

    verdict = submit_verdict(
        display["voice_selection_id"],
        _verdict_payload(display["decision_card_digest"]),
        transport,  # type: ignore[arg-type]
    )

    assert verdict.model_dump(mode="json") == baseline.model_dump(mode="json")
    assert verdict.decision_card_digest == display["decision_card_digest"]
    resumed = resume_from_verdict(voice_card, verdict)
    assert resumed["verb"] == "select"
    assert resumed["voice_selection_payload"] == display["voice_selection_payload"]


def test_g4a_poll_surface_resume_rejects_tampered_digest() -> None:
    voice_card = fixture_voice_selection_card()
    display = display_voice_candidates(voice_card)
    payload = deepcopy(_verdict_payload(display["decision_card_digest"]))
    payload["decision_card_digest"] = "0" * 64
    tampered = Section11OperatorVerdict.model_validate(
        {**payload, "voice_selection_id": display["voice_selection_id"]}
    )

    with pytest.raises(GateError, match="digest_mismatch"):
        resume_from_verdict(voice_card, tampered)


def test_g4a_poll_surface_loads_yaml_with_utf8(tmp_path: Path) -> None:
    voice_card = fixture_voice_selection_card()
    voice_path = tmp_path / "voice-selection.yaml"
    voice_path.write_text(
        yaml.safe_dump(
            voice_card.model_dump(mode="json"),
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )

    loaded = load_voice_selection(voice_path)
    display = display_voice_candidates(voice_path)

    assert loaded == voice_card
    assert display["voice_selection_id"] == str(voice_card.card_id)


def test_g4a_poll_surface_rejects_mismatched_voice_selection_id() -> None:
    voice_card = fixture_voice_selection_card()
    display = display_voice_candidates(voice_card)

    with pytest.raises(GateError, match="voice_selection_id_mismatch"):
        submit_verdict(
            f"{display['voice_selection_id']}-mismatch",
            {
                **_verdict_payload(display["decision_card_digest"]),
                "voice_selection_id": display["voice_selection_id"],
            },
            "http",
        )
