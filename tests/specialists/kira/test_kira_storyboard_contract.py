from __future__ import annotations

from app.specialists.kira import _act as kira_act


def test_storyboard_b_visual_file_is_preserved_in_provider_request(tmp_path) -> None:
    class FakeKlingClient:
        def __init__(self) -> None:
            self.kwargs: dict[str, object] = {}

        def generate_motion(self, **kwargs: object) -> dict[str, object]:
            self.kwargs = kwargs
            return {
                "data": {
                    "task_status": "succeed",
                    "task_result": {
                        "videos": [{"url": "artifacts/segment-001-motion.mp4"}]
                    },
                }
            }

    client = FakeKlingClient()
    payload = {
        "bundle_path": str(tmp_path),
        "motion_plan": {
            "slides": [
                {
                    "slide_id": "s1",
                    "prompt": "cinematic pan across the slide visual",
                    "visual_file": "artifacts/segment-001.png",
                    "estimated_cost_usd": 0.10,
                }
            ]
        },
    }

    verdict = kira_act.generate_motion_from_plan(payload, client=client)

    assert client.kwargs["image_url"] == "artifacts/segment-001.png"
    assert verdict["motion_receipts"][0]["motion_asset_path"] == (
        "artifacts/segment-001-motion.mp4"
    )
