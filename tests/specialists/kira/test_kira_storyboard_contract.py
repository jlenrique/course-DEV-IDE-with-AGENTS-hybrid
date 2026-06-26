from __future__ import annotations

from pathlib import Path

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

        def download_video(self, video_url: object, output_path: object) -> Path:
            p = Path(str(output_path))
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b"\x00\x00\x00\x18ftypmp42moovmdat")
            return p

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
    # The provider url is recorded as motion_source_url; the asset is materialized locally.
    receipt = verdict["motion_receipts"][0]
    assert receipt["motion_source_url"] == "artifacts/segment-001-motion.mp4"
    assert receipt["motion_asset_path"] == str((tmp_path / "motion" / "s1.mp4").resolve())
