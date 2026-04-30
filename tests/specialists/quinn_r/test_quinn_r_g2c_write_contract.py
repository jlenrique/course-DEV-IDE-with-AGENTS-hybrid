from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from app.specialists.quinn_r.graph import _act
from tests.specialists.quinn_r.conftest import make_state


def test_g2c_writes_schema_valid_authorized_storyboard(tmp_path: Path) -> None:
    state = make_state(
        json.dumps(
            {
                "gate_id": "G2C",
                "gate_phase": "pre-composition",
                "runs_root": str(tmp_path),
                "slides": [{"slide_id": "s1", "title": "Opening"}],
            }
        )
    )
    output = json.loads(_act(state)["cache_state"]["cache_prefix"])
    artifact = Path(output["quinn_r_review"]["artifact_paths"][0])
    schema = json.loads(
        Path("state/config/schemas/authorized-storyboard.schema.json").read_text(
            encoding="utf-8"
        )
    )
    payload = json.loads(artifact.read_text(encoding="utf-8"))
    validate(instance=payload, schema=schema)
    assert payload["slides"][0]["quinn_r_verdict"] == "approved"

