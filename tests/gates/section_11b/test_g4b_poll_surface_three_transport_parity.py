from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from app.gates.errors import GateError
from app.gates.section_11b.poll_surface import (
    display_input_package,
    load_input_package,
    resume_from_verdict,
    submit_verdict,
)
from app.models.operator_verdict_section_11b import Section11BOperatorVerdict
from tests.gates.section_11b._helpers import (
    RUN_ID,
    SUBMITTED_AT,
    fixture_input_package_card,
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
def test_g4b_poll_surface_transport_emits_equivalent_operator_verdict(
    transport: str,
) -> None:
    input_package = fixture_input_package_card()
    display = display_input_package(input_package)
    baseline = submit_verdict(
        display["input_package_id"],
        _verdict_payload(display["decision_card_digest"]),
        "cli",
    )

    verdict = submit_verdict(
        display["input_package_id"],
        _verdict_payload(display["decision_card_digest"]),
        transport,  # type: ignore[arg-type]
    )

    assert verdict.model_dump(mode="json") == baseline.model_dump(mode="json")
    assert verdict.decision_card_digest == display["decision_card_digest"]
    resumed = resume_from_verdict(input_package, verdict)
    assert resumed["verb"] == "approve"
    assert resumed["input_package_payload"] == display["input_package_payload"]


def test_g4b_poll_surface_resume_rejects_tampered_digest() -> None:
    input_package = fixture_input_package_card()
    display = display_input_package(input_package)
    payload = deepcopy(_verdict_payload(display["decision_card_digest"]))
    payload["decision_card_digest"] = "0" * 64
    tampered = Section11BOperatorVerdict.model_validate(
        {**payload, "input_package_id": display["input_package_id"]}
    )

    with pytest.raises(GateError, match="digest_mismatch"):
        resume_from_verdict(input_package, tampered)


def test_g4b_poll_surface_loads_yaml_with_utf8(tmp_path: Path) -> None:
    input_package = fixture_input_package_card()
    input_package_path = tmp_path / "input-package.yaml"
    input_package_path.write_text(
        yaml.safe_dump(
            input_package.model_dump(mode="json"),
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )

    loaded = load_input_package(input_package_path)
    display = display_input_package(input_package_path)

    assert loaded == input_package
    assert display["input_package_id"] == str(input_package.card_id)


def test_g4b_poll_surface_rejects_mismatched_input_package_id() -> None:
    input_package = fixture_input_package_card()
    display = display_input_package(input_package)

    with pytest.raises(GateError, match="input_package_id_mismatch"):
        submit_verdict(
            f"{display['input_package_id']}-mismatch",
            {
                **_verdict_payload(display["decision_card_digest"]),
                "input_package_id": display["input_package_id"],
            },
            "http",
        )
