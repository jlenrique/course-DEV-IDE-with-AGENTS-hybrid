from __future__ import annotations

import json

import pytest

from app.specialists.vera.graph import _act
from tests.specialists.vera._act_helpers import build_vera_state


@pytest.mark.timeout(30)
def test_critical_oia_finding_halts_and_does_not_silently_advance(tmp_path) -> None:
    update = _act(
        build_vera_state(
            {
                "gate_id": "G0",
                "runs_root": str(tmp_path),
                "injected_findings": [
                    {
                        "category": "A",
                        "severity": "critical",
                        "evidence_anchor": "source:line-4",
                        "description": "clinical meaning changed",
                    }
                ],
            }
        )
    )
    output = json.loads(update["cache_state"]["cache_prefix"])
    verdict = output["vera_finding"]["verdict"]

    assert verdict["status"] == "HALT-AND-REMEDIATE"
    assert verdict["verb"] == "halt"
    assert "clinical meaning changed" in verdict["failure_reason"]
    assert update["model_resolution_trail"][-1].reason == "ftr.halt.oia-hard-fail"
