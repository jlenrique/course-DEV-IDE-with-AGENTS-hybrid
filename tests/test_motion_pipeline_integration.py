"""Epic 14 mixed-motion integration proof.

Verifies a 3-slide mini-run with 1 static + 1 Kling video + 1 manual animation,
plus a static control run where motion remains disabled.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock

import yaml

from scripts.utilities.file_helpers import project_root

ROOT = project_root()
for path in (
    ROOT / "skills" / "production-coordination" / "scripts",
    ROOT / "skills" / "kling-video" / "scripts",
    ROOT / "skills" / "compositor" / "scripts",
    ROOT / "skills" / "bmad-agent-content-creator" / "scripts",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from compositor_operations import (
    generate_assembly_guide,
    load_manifest,
    sync_approved_visuals_to_assembly_bundle,
)
from kling_operations import generate_motion_clip
from manifest_visual_enrichment import (
    apply_motion_plan_to_segments,
    enrich_manifest,
    validate_manifest_motion_fields,
    validate_manifest_visual_references,
)
from manual_animation_workflow import import_manual_motion_asset
from motion_plan import apply_motion_designations, build_motion_plan_from_authorized_storyboard
from perception_contract import enforce_motion_perception_contract
from visual_reference_injector import inject_all_slides


def _mock_motion_perceive_high(**kwargs):
    artifact_path = str(kwargs.get("artifact_path", ""))
    label = Path(artifact_path).stem
    return {
        "schema_version": "1.0",
        "modality": kwargs.get("modality", "video"),
        "artifact_path": artifact_path,
        "confidence": "HIGH",
        "confidence_rationale": "integration test mock",
        "perception_timestamp": "2026-04-05T12:00:00Z",
        "extracted_text": "",
        "layout_description": f"Motion clip for {label}",
        "visual_elements": [
            {"type": "motion", "description": f"{label} movement", "position": "center"},
            {"type": "label", "description": f"{label} label", "position": "right"},
        ],
        "slide_title": label,
        "text_blocks": [],
    }


def test_mixed_motion_mini_run_and_static_control(tmp_path: Path) -> None:
    repo = tmp_path
    (repo / ".git").mkdir()

    exports = repo / "exports"
    exports.mkdir()
    for slide_name in ("slide-01.png", "slide-02.png", "slide-03.png"):
        (exports / slide_name).write_bytes(b"png-bytes")

    authorized_storyboard = {
        "run_id": "RUN-MOTION-E2E",
        "authorized_slides": [
            {"slide_id": "slide-01", "card_number": 1},
            {"slide_id": "slide-02", "card_number": 2},
            {"slide_id": "slide-03", "card_number": 3},
        ],
    }
    motion_plan = build_motion_plan_from_authorized_storyboard(
        authorized_storyboard,
        motion_enabled=True,
        motion_budget={"max_credits": 24, "model_preference": "pro"},
    )
    motion_plan = apply_motion_designations(
        motion_plan,
        {
            "slide-01": {
                "motion_type": "static",
            },
            "slide-02": {
                "motion_type": "video",
                "motion_brief": "Animate the chart trend upward",
                "motion_duration_seconds": 5.0,
                "override_reason": "Integration test explicitly exercises the Kling video branch.",
            },
            "slide-03": {
                "motion_type": "animation",
                "motion_brief": "Pulse the labels in sequence",
                "guidance_notes": "Hold the final state for readability",
                "motion_duration_seconds": 7.0,
                "override_reason": "Integration test explicitly exercises the manual animation branch.",
            },
        },
    )

    client = Mock()
    client.image_to_video.return_value = {"data": {"task_id": "task-motion-02"}}
    client.wait_for_completion.return_value = {
        "data": {"task_result": {"videos": [{"url": "https://cdn.example.com/motion.mp4", "duration": "5.0"}]}}
    }
    video_output = repo / "motion-src" / "slide-02_motion.mp4"
    video_output.parent.mkdir()
    client.download_video.return_value = video_output
    video_result = generate_motion_clip(
        {
            "slide_id": "slide-02",
            "source_image_url": "https://example.com/slide-02.png",
            "motion_brief": "Animate the chart trend upward",
            "narration_intent": "Explain the growth pattern clearly",
            "motion_duration_seconds": 5.0,
        },
        motion_budget=motion_plan["motion_budget"],
        output_dir=video_output.parent,
        client=client,
    )
    Path(video_result["mp4_path"]).write_bytes(b"video-bytes")

    manual_motion = repo / "motion-src" / "slide-03_motion.mp4"
    manual_motion.write_bytes(b"manual-bytes")
    imported_animation = import_manual_motion_asset(
        next(row for row in motion_plan["slides"] if row["slide_id"] == "slide-03"),
        manual_motion,
        duration_seconds=7.0,
    )

    for row in motion_plan["slides"]:
        if row["slide_id"] == "slide-02":
            row.update(
                {
                    "motion_asset_path": str(Path(video_result["mp4_path"]).relative_to(repo)).replace("\\", "/"),
                    "motion_source": "kling",
                    "motion_duration_seconds": video_result["duration_seconds"],
                    "motion_status": "approved",
                    "credits_consumed": video_result["credits_consumed"],
                }
            )
        elif row["slide_id"] == "slide-03":
            row.update(imported_animation)
            row["motion_asset_path"] = str(Path(imported_animation["motion_asset_path"]).relative_to(repo)).replace("\\", "/")
            row["motion_status"] = "approved"

    segments = [
        {
            "id": "seg-01",
            "gary_slide_id": "slide-01",
            "gary_card_number": 1,
            "narration_text": "Notice the still comparison chart on the first slide.",
            "narration_duration": 3.0,
            "narration_file": "assembly-bundle/audio/seg-01.mp3",
            "visual_file": "exports/slide-01.png",
            "visual_duration": 3.0,
            "transition_in": "fade",
            "transition_out": "cut",
            "behavioral_intent": "credible",
            "music": "duck",
            "visual_mode": "static-hold",
        },
        {
            "id": "seg-02",
            "gary_slide_id": "slide-02",
            "gary_card_number": 2,
            "narration_text": "[as the animation plays] watch the slide-02_motion movement rise across the graph.",
            "narration_duration": 5.0,
            "narration_file": "assembly-bundle/audio/seg-02.mp3",
            "visual_file": "exports/slide-02.png",
            "visual_duration": 5.0,
            "transition_in": "fade",
            "transition_out": "cut",
            "behavioral_intent": "clear-guidance",
            "music": "duck",
            "visual_mode": "video",
        },
        {
            "id": "seg-03",
            "gary_slide_id": "slide-03",
            "gary_card_number": 3,
            "narration_text": "[during the transition] follow the slide-03_motion labels as they pulse in sequence.",
            "narration_duration": 7.0,
            "narration_file": "assembly-bundle/audio/seg-03.mp3",
            "visual_file": "exports/slide-03.png",
            "visual_duration": 7.0,
            "transition_in": "fade",
            "transition_out": "fade",
            "behavioral_intent": "attention-reset",
            "music": "duck",
            "visual_mode": "video",
        },
    ]
    segments = apply_motion_plan_to_segments(segments, motion_plan)
    motion_validation = validate_manifest_motion_fields(segments)
    assert motion_validation["valid"] is True

    motion_perception = enforce_motion_perception_contract(
        segments,
        repo_root=repo,
        perceive_motion_fn=_mock_motion_perceive_high,
    )
    assert motion_perception["status"] == "ready"
    assert len(motion_perception["motion_perception_artifacts"]) == 2

    static_perception = {
        "slide_id": "slide-01",
        "card_number": 1,
        "visual_elements": [
            {"type": "chart", "description": "still comparison chart", "position": "left"},
        ],
    }
    combined_perception = [static_perception, *motion_perception["motion_perception_artifacts"]]
    injection = inject_all_slides(combined_perception)
    segments = enrich_manifest(
        segments,
        injection["slides"],
        narration_cues_by_segment={
            "seg-01": ["still comparison chart"],
            "seg-02": ["slide-02_motion movement"],
            "seg-03": ["slide-03_motion labels"],
        },
    )
    traceability = validate_manifest_visual_references(segments, combined_perception)
    assert traceability["valid"] is True

    assembly_bundle = repo / "assembly-bundle"
    assembly_bundle.mkdir()
    manifest_path = assembly_bundle / "manifest.yaml"
    manifest_path.write_text(
        yaml.safe_dump(
            {
                "lesson_id": "C1-M1-L1",
                "title": "Motion Integration",
                "segments": segments,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    sync_approved_visuals_to_assembly_bundle(manifest_path, repo_root=repo)
    synced_manifest = load_manifest(manifest_path)
    guide = generate_assembly_guide(synced_manifest, manifest_path)
    assert "slide-02_motion.mp4" in guide
    assert "slide-03_motion.mp4" in guide
    assert "video track" in guide
    assert "still comparison chart" in yaml.safe_dump(synced_manifest)

    static_control = build_motion_plan_from_authorized_storyboard(
        authorized_storyboard,
        motion_enabled=False,
    )
    static_control = apply_motion_designations(
        static_control,
        {
            "slide-01": {"motion_type": "static"},
            "slide-02": {"motion_type": "video", "motion_duration_seconds": 5.0},
            "slide-03": {"motion_type": "static"},
        },
    )
    assert all(row["motion_type"] == "static" for row in static_control["slides"])
