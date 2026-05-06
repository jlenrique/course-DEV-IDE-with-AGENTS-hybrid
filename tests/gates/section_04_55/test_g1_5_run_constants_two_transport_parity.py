from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from app.gates.errors import GateError
from app.gates.section_04_55.poll_surface import (
    display_run_constants,
    load_run_constants,
    submit_verdict,
)
from app.models.operator_verdict_section_04_55 import Section04_55OperatorVerdict
from tests.gates.section_04_55._helpers import (
    RUN_ID,
    SUBMITTED_AT,
    fixture_run_constants,
)


def _verdict_payload(digest: str) -> dict[str, object]:
    return {
        "run_id": RUN_ID,
        "verb": "lock",
        "operator_id": "operator_1",
        "submitted_at": SUBMITTED_AT,
        "decision_card_digest": digest,
    }


@pytest.mark.parametrize("transport", ["cli", "http"])
def test_g1_5_run_constants_surface_emits_equivalent_operator_verdict(
    transport: str,
) -> None:
    run_constants = fixture_run_constants()
    display = display_run_constants(run_constants)
    baseline = submit_verdict(
        "RUN-CONSTANTS-001",
        _verdict_payload(display["decision_card_digest"]),
        transport="cli",
    )

    verdict = submit_verdict(
        "RUN-CONSTANTS-001",
        _verdict_payload(display["decision_card_digest"]),
        transport=transport,
    )

    assert verdict.model_dump(mode="json") == baseline.model_dump(mode="json")
    assert verdict.decision_card_digest == display["decision_card_digest"]
    assert Section04_55OperatorVerdict.model_validate(verdict.model_dump()) == verdict


def test_g1_5_run_constants_surface_rejects_mcp_stdio_transport() -> None:
    display = display_run_constants(fixture_run_constants())

    with pytest.raises(GateError, match="unsupported_transport"):
        submit_verdict(
            "RUN-CONSTANTS-001",
            _verdict_payload(display["decision_card_digest"]),
            transport="mcp-stdio",
        )


def test_g1_5_run_constants_surface_loads_yaml_with_utf8(tmp_path: Path) -> None:
    run_constants = fixture_run_constants()
    constants_path = tmp_path / "run-constants.yaml"
    constants_path.write_text(
        yaml.safe_dump(run_constants, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    loaded = load_run_constants(constants_path)
    display = display_run_constants(constants_path)

    assert loaded == run_constants
    assert display["run_constants_id"] == "RUN-CONSTANTS-001"

