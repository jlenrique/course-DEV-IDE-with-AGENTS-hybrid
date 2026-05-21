from __future__ import annotations

import json

import pytest

from app.specialists.vera.graph import _act
from tests.composition._chain_test_base import ChainTestBase
from tests.specialists.vera._act_helpers import build_vera_state


@pytest.mark.timeout(120)
class TestIrenePass1ToVeraG4Chain(ChainTestBase):
    upstream_specialist = "irene_pass1"
    downstream_specialist = "vera"
    gate_id = "G4"
    cassette_path = "tests/fixtures/composition/irene_pass1_to_vera_g4"

    def test_vera_g4_parses_irene_pass1_plan_fixture(self, tmp_path) -> None:
        plan_path = tmp_path / "irene-pass1.md"
        plan_path.write_text(
            "# Irene Pass-1 Lesson Plan\n\n## unit-1: Mechanism\n",
            encoding="utf-8",
        )
        update = _act(
            build_vera_state(
                {
                    "gate_id": "G4",
                    "runs_root": str(tmp_path),
                    "irene_pass1_plan_path": str(plan_path),
                }
            )
        )
        output = json.loads(update["cache_state"]["cache_prefix"])
        criteria = output["vera_finding"]["rubrics"]["G4"]["criteria"]
        assert len(criteria) == 19
        assert criteria[0]["criterion_id"] == "G4-01"
