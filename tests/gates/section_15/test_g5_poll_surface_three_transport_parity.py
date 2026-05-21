from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from app.gates.errors import GateError
from app.gates.section_15.poll_surface import (
    display_final_handoff,
    load_final_handoff,
    resume_from_verdict,
    submit_verdict,
)
from app.models.operator_verdict_section_15 import Section15OperatorVerdict
from tests.gates.section_15._helpers import (
    RUN_ID,
    SUBMITTED_AT,
    fixture_final_handoff_card,
)


def _verdict_payload(digest: str) -> dict[str, object]:
    return {
        "run_id": RUN_ID,
        "verb": "complete",
        "operator_id": "operator_1",
        "submitted_at": SUBMITTED_AT,
        "decision_card_digest": digest,
    }


@pytest.mark.parametrize("transport", ["cli", "http", "mcp-stdio"])
def test_g5_poll_surface_transport_emits_equivalent_operator_verdict(
    transport: str,
) -> None:
    final_handoff = fixture_final_handoff_card()
    display = display_final_handoff(final_handoff)
    baseline = submit_verdict(
        display["handoff_id"],
        _verdict_payload(display["decision_card_digest"]),
        "cli",
    )

    verdict = submit_verdict(
        display["handoff_id"],
        _verdict_payload(display["decision_card_digest"]),
        transport,  # type: ignore[arg-type]
    )

    assert verdict.model_dump(mode="json") == baseline.model_dump(mode="json")
    assert verdict.decision_card_digest == display["decision_card_digest"]
    resumed = resume_from_verdict(final_handoff, verdict)
    assert resumed["verb"] == "complete"
    assert resumed["final_handoff_payload"] == display["final_handoff_payload"]


def test_g5_poll_surface_resume_rejects_tampered_digest() -> None:
    final_handoff = fixture_final_handoff_card()
    display = display_final_handoff(final_handoff)
    payload = deepcopy(_verdict_payload(display["decision_card_digest"]))
    payload["decision_card_digest"] = "0" * 64
    tampered = Section15OperatorVerdict.model_validate(
        {**payload, "handoff_id": display["handoff_id"]}
    )

    with pytest.raises(GateError, match="digest_mismatch"):
        resume_from_verdict(final_handoff, tampered)


def test_g5_poll_surface_loads_yaml_with_utf8(tmp_path: Path) -> None:
    final_handoff = fixture_final_handoff_card()
    final_handoff_path = tmp_path / "final-handoff.yaml"
    final_handoff_path.write_text(
        yaml.safe_dump(
            final_handoff.model_dump(mode="json"),
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )

    loaded = load_final_handoff(final_handoff_path)
    display = display_final_handoff(final_handoff_path)

    assert loaded == final_handoff
    assert display["handoff_id"] == str(final_handoff.card_id)


def test_g5_poll_surface_rejects_mismatched_handoff_id() -> None:
    final_handoff = fixture_final_handoff_card()
    display = display_final_handoff(final_handoff)

    with pytest.raises(GateError, match="handoff_id_mismatch"):
        submit_verdict(
            f"{display['handoff_id']}-mismatch",
            {
                **_verdict_payload(display["decision_card_digest"]),
                "handoff_id": display["handoff_id"],
            },
            "http",
        )
