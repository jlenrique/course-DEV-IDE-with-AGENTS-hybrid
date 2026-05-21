from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from app.specialists.vera.graph import _act
from tests.specialists.vera._act_helpers import build_vera_state

G4_PATH = Path("state/config/fidelity-contracts/g4-narration-script.yaml")
G4_IDS = [item["id"] for item in yaml.safe_load(G4_PATH.read_text())["criteria"]]


@pytest.mark.timeout(30)
@pytest.mark.parametrize("criterion_id", G4_IDS)
def test_g4_emits_each_canonical_criterion(criterion_id: str, tmp_path: Path) -> None:
    update = _act(build_vera_state({"gate_id": "G4", "runs_root": str(tmp_path)}))
    output = json.loads(update["cache_state"]["cache_prefix"])
    criteria = output["vera_finding"]["rubrics"]["G4"]["criteria"]
    by_id = {item["criterion_id"]: item for item in criteria}

    assert len(criteria) == 19
    assert sorted(by_id) == [f"G4-{index:02d}" for index in range(1, 20)]
    assert {"severity", "description", "evidence_anchor"} <= set(by_id[criterion_id])
