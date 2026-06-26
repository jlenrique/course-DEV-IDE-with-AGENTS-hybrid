from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.models.state.cache_state import CacheState
from app.models.state.run_state import RunState
from app.specialists.kira.graph import _act, _plan


class FakeKlingClient:
    def generate_motion(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "data": {
                "task_id": "task-kira-act",
                "task_status": "succeed",
                "task_result": {
                    "videos": [
                        {
                            "url": "tests/fixtures/specialist-replay/kira/slide-01.mp4",
                            "duration": "5",
                        }
                    ]
                },
            }
        }

    def download_video(self, video_url: object, output_path: object) -> Path:
        p = Path(str(output_path))
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"\x00\x00\x00\x18ftypmp42moovmdat")
        return p


def test_kira_act_node_uses_api_bound_motion_generation(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        "app.specialists.kira._act.KlingClient",
        lambda: FakeKlingClient(),
    )
    envelope_payload = {
        "bundle_path": str(tmp_path),
        "motion_plan": {
            "slides": [
                {
                    "slide_id": "slide-001",
                    "prompt": "show smooth camera pan over anatomy diagram",
                    "estimated_cost_usd": 0.12,
                    "visual_file": "artifacts/segment-001.png",
                }
            ]
        },
    }
    payload_blob = json.dumps(
        envelope_payload, sort_keys=True, ensure_ascii=True, separators=(",", ":")
    )
    state = RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        cache_state=CacheState(cache_prefix=payload_blob, entries_count=0),
    )
    state = state.model_copy(update=_plan(state))

    act_update = _act(state)

    output = json.loads(act_update["cache_state"]["cache_prefix"])
    assert output["motion_receipts"][0]["motion_asset_path"].endswith(".mp4")
    assert output["motion_receipts"][0]["status"] == "success"
    assert output["model_id"] == "gpt-5-nano"
    assert output["compositor_invocation"]["gate_id"] == "G3"
