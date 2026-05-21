from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from app.gates.errors import GateError
from app.gates.section_02a._transports import TRANSPORT_HANDLERS
from app.gates.section_02a.poll_surface import load_directive, resume_from_verdict
from app.models.operator_verdict_section_02a import Section02AOperatorVerdict
from tests.gates.section_02a._helpers import fixture_directive


@pytest.mark.parametrize("transport", ["cli", "http", "mcp-stdio"])
def test_g0_poll_surface_transport_emits_equivalent_operator_verdict(
    transport: str,
) -> None:
    directive = fixture_directive()
    baseline_response = TRANSPORT_HANDLERS["cli"](
        directive,
        verb="approve",
        operator_id="operator_1",
    )

    response = TRANSPORT_HANDLERS[transport](
        directive,
        verb="approve",
        operator_id="operator_1",
    )

    assert response["operator_verdict"] == baseline_response["operator_verdict"]
    assert response["display"]["decision_card_digest"] == baseline_response["display"][
        "decision_card_digest"
    ]
    verdict = Section02AOperatorVerdict.model_validate(response["operator_verdict"])
    resumed = resume_from_verdict(directive, verdict)
    assert resumed["verb"] == "approve"
    assert resumed["directive"] == directive.model_dump(mode="json")


def test_g0_poll_surface_resume_rejects_tampered_digest() -> None:
    directive = fixture_directive()
    response = TRANSPORT_HANDLERS["http"](
        directive,
        verb="approve",
        operator_id="operator_1",
    )
    payload = deepcopy(response["operator_verdict"])
    payload["decision_card_digest"] = "0" * 64
    tampered = Section02AOperatorVerdict.model_validate(payload)

    with pytest.raises(GateError, match="digest_mismatch"):
        resume_from_verdict(directive, tampered)


def test_g0_poll_surface_loads_directive_yaml_with_utf8(tmp_path: Path) -> None:
    directive = fixture_directive()
    directive_path = tmp_path / "directive.yaml"
    directive_path.write_text(
        yaml.safe_dump(
            directive.model_dump(mode="json"),
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )

    loaded = load_directive(directive_path)
    response = TRANSPORT_HANDLERS["cli"](
        directive_path,
        verb="approve",
        operator_id="operator_1",
    )

    assert loaded == directive
    assert response["operator_verdict"]["run_id"] == str(directive.run_id)
