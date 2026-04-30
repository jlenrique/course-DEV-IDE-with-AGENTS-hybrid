from __future__ import annotations

import json
from pathlib import Path

from app.specialists.kira import _act as kira_act


class FakeKlingClient:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def generate_motion(self, **kwargs: object) -> dict[str, object]:
        self.calls.append(kwargs)
        index = len(self.calls)
        return {
            "data": {
                "task_id": f"task-{index:03d}",
                "task_status": "succeed",
                "task_result": {
                    "videos": [
                        {
                            "url": f"tests/fixtures/specialist-replay/kira/slide-{index:02d}.mp4",
                            "duration": "5",
                        }
                    ]
                },
            }
        }


def test_kira_motion_generation_writes_progress_and_terminal_receipts(tmp_path: Path) -> None:
    client = FakeKlingClient()
    payload = {
        "bundle_path": str(tmp_path),
        "motion_plan": {
            "slides": [
                {"slide_id": "slide-01", "prompt": "slow pan", "estimated_cost_usd": 0.12},
                {"slide_id": "slide-02", "prompt": "diagram reveal", "estimated_cost_usd": 0.13},
            ]
        },
    }

    verdict = kira_act.generate_motion_from_plan(payload, client=client)

    assert len(client.calls) == 2
    assert verdict["gate_id"] == "G2F"
    for slide_id in ("slide-01", "slide-02"):
        progress = tmp_path / "motion" / f"{slide_id}.progress.json"
        terminal = tmp_path / "motion" / f"{slide_id}.json"
        assert progress.is_file()
        assert terminal.is_file()
        receipt = json.loads(terminal.read_text(encoding="utf-8"))
        assert receipt["status"] == "success"
        assert receipt["cost_tracking"]["actual_cost_usd"] > 0
        assert receipt["provider_response"]["data"]["task_status"] == "succeed"

    assert not (tmp_path / "recovery" / "inspection").exists()


def test_kira_real_client_path_records_terminal_kling_result(tmp_path: Path) -> None:
    class TerminalKlingClient:
        def __init__(self) -> None:
            self.submitted: list[dict[str, object]] = []

        def generate_motion(self, **kwargs: object) -> dict[str, object]:
            self.submitted.append(kwargs)
            return {
                "data": {
                    "task_id": "task-terminal",
                    "task_status": "succeed",
                    "task_result": {
                        "videos": [{"url": "https://cdn.kling.test/slide-01.mp4"}]
                    },
                }
            }

    client = TerminalKlingClient()
    payload = {
        "bundle_path": str(tmp_path),
        "motion_plan": {
            "slides": [
                {
                    "slide_id": "slide-01",
                    "prompt": "slow pan",
                    "visual_file": "https://cdn.test/still.png",
                    "estimated_cost_usd": 0.12,
                }
            ]
        },
    }

    verdict = kira_act.generate_motion_from_plan(payload, client=client)  # type: ignore[arg-type]

    assert client.submitted[0]["image_url"] == "https://cdn.test/still.png"
    assert verdict["motion_receipts"][0]["motion_asset_path"] == (
        "https://cdn.kling.test/slide-01.mp4"
    )
