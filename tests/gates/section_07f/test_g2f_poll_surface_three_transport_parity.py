from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from app.gates.errors import GateError
from app.gates.section_07f.poll_surface import (
    display_motion_clip,
    load_motion_clip,
    resume_from_verdict,
    submit_verdict,
)
from app.models.operator_verdict_section_07f import Section07FOperatorVerdict
from tests.gates.section_07f._helpers import (
    RUN_ID,
    SUBMITTED_AT,
    fixture_motion_clip_card,
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
def test_g2f_poll_surface_transport_emits_equivalent_operator_verdict(
    transport: str,
) -> None:
    motion_clip = fixture_motion_clip_card()
    display = display_motion_clip(motion_clip)
    baseline = submit_verdict(
        display["motion_clip_id"],
        _verdict_payload(display["decision_card_digest"]),
        "cli",
    )

    verdict = submit_verdict(
        display["motion_clip_id"],
        _verdict_payload(display["decision_card_digest"]),
        transport,  # type: ignore[arg-type]
    )

    assert verdict.model_dump(mode="json") == baseline.model_dump(mode="json")
    assert verdict.decision_card_digest == display["decision_card_digest"]
    resumed = resume_from_verdict(motion_clip, verdict)
    assert resumed["verb"] == "approve"
    assert resumed["decision_card"] == display["decision_card"]


def test_g2f_poll_surface_resume_rejects_tampered_digest() -> None:
    motion_clip = fixture_motion_clip_card()
    display = display_motion_clip(motion_clip)
    payload = deepcopy(_verdict_payload(display["decision_card_digest"]))
    payload["decision_card_digest"] = "0" * 64
    tampered = Section07FOperatorVerdict.model_validate(
        {**payload, "motion_clip_id": display["motion_clip_id"]}
    )

    with pytest.raises(GateError, match="digest_mismatch"):
        resume_from_verdict(motion_clip, tampered)


def test_g2f_poll_surface_loads_yaml_with_utf8(tmp_path: Path) -> None:
    motion_clip = fixture_motion_clip_card()
    motion_clip_path = tmp_path / "motion-clip.yaml"
    motion_clip_path.write_text(
        yaml.safe_dump(
            motion_clip.model_dump(mode="json"),
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )

    loaded = load_motion_clip(motion_clip_path)
    display = display_motion_clip(motion_clip_path)

    assert loaded == motion_clip
    assert display["motion_clip_id"] == str(motion_clip.card_id)


def test_g2f_poll_surface_rejects_mismatched_motion_clip_id() -> None:
    motion_clip = fixture_motion_clip_card()
    display = display_motion_clip(motion_clip)

    with pytest.raises(GateError, match="motion_clip_id_mismatch"):
        submit_verdict(
            f"{display['motion_clip_id']}-mismatch",
            {
                **_verdict_payload(display["decision_card_digest"]),
                "motion_clip_id": display["motion_clip_id"],
            },
            "http",
        )
