from __future__ import annotations

import json
from pathlib import Path

from app.specialists.kira import _act as kira_act


class ExplodingKlingClient:
    def generate_motion(self, **kwargs: object) -> dict[str, object]:
        raise AssertionError(f"budget-exhaust path must not call provider: {kwargs}")


def test_kira_budget_exhaust_aborts_before_subsequent_slides(tmp_path: Path) -> None:
    payload = {
        "bundle_path": str(tmp_path),
        "motion_plan": {
            "slides": [
                {"slide_id": "slide-01", "prompt": "too expensive", "estimated_cost_usd": 0.55},
                {"slide_id": "slide-02", "prompt": "must not run", "estimated_cost_usd": 0.01},
            ]
        },
    }

    verdict = kira_act.generate_motion_from_plan(payload, client=ExplodingKlingClient())

    assert len(verdict["motion_receipts"]) == 1
    receipt_path = tmp_path / "motion" / "slide-01.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["status"] == "budget-exceeded"
    assert not (tmp_path / "motion" / "slide-02.progress.json").exists()
    assert not (tmp_path / "motion" / "slide-02.json").exists()
    inspection = tmp_path / "recovery" / "inspection" / "slide-01" / "budget-exhausted.md"
    assert inspection.is_file()
    assert "Budget Exhausted" in inspection.read_text(encoding="utf-8")
