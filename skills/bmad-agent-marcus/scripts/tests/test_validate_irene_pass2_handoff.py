from __future__ import annotations

import json
import subprocess
import sys
from importlib import util
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = ROOT / "skills" / "bmad-agent-marcus" / "scripts" / "validate-irene-pass2-handoff.py"


def _load_script_module():
    spec = util.spec_from_file_location(
        "validate_irene_pass2_handoff_module",
        SCRIPT_PATH,
    )
    assert spec is not None
    assert spec.loader is not None
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


module = _load_script_module()
validate_irene_pass2_handoff = module.validate_irene_pass2_handoff


def _write_complete_bundle_outputs(
    bundle_dir: Path,
    *,
    slide_ids: list[str],
    gary_slide_output: list[dict[str, object]],
    perception_artifacts: list[dict[str, object]],
    motion: bool = False,
    omit_slide_id: str | None = None,
    empty_narration_segment: str | None = None,
    empty_visual_cue_segment: str | None = None,
    cue_not_in_text_segment: str | None = None,
    narration_text_overrides: dict[str, str] | None = None,
    cue_overrides: dict[str, str] | None = None,
    script_behavioral_intent_overrides: dict[str, str] | None = None,
    manifest_behavioral_intent_overrides: dict[str, str] | None = None,
    standalone_perception_artifacts: list[dict[str, object]] | None = None,
    wrong_motion_asset: bool = False,
    include_motion_confirmation: bool = True,
    motion_visual_file_uses_motion_asset: bool = False,
    include_runtime_rationale_fields: bool = False,
    runtime_rationale_overrides: dict[str, dict[str, str]] | None = None,
    bridge_type_overrides: dict[str, str] | None = None,
    disable_spoken_bridge_enrichment: bool = False,
) -> dict[str, object]:
    approved_motion_asset = bundle_dir / "motion-approved.mp4"
    approved_motion_asset.write_bytes(b"mp4")
    wrong_motion_path = bundle_dir / "motion-wrong.mp4"
    wrong_motion_path.write_bytes(b"mp4")

    segments: list[dict[str, object]] = []
    motion_perception_artifacts: list[dict[str, object]] = []
    gary_by_slide_id = {
        str(row.get("slide_id") or ""): row
        for row in gary_slide_output
        if isinstance(row, dict)
    }
    for index, slide_id in enumerate(slide_ids, start=1):
        if slide_id == omit_slide_id:
            continue

        seg_id = f"seg-{index:02d}"
        cue = f"notice cue {index}"
        narration_text = f"{cue} and explain the insight on slide {index}."
        if cue_overrides and seg_id in cue_overrides:
            cue = cue_overrides[seg_id]
            narration_text = f"{cue} and explain the insight on slide {index}."
        if seg_id == empty_narration_segment:
            narration_text = ""
        if narration_text_overrides and seg_id in narration_text_overrides:
            narration_text = narration_text_overrides[seg_id]
        if seg_id == cue_not_in_text_segment:
            narration_text = f"Different narration for slide {index}."
        if seg_id == empty_visual_cue_segment:
            cue = ""

        segment: dict[str, object] = {
            "id": seg_id,
            "gary_slide_id": slide_id,
            "gary_card_number": index,
            "narration_text": narration_text,
            "behavioral_intent": "credible",
            "visual_file": str(gary_by_slide_id.get(slide_id, {}).get("file_path") or ""),
            "visual_references": [
                {
                    "element": f"Element {index}",
                    "location_on_slide": "left",
                    "narration_cue": cue,
                    "perception_source": slide_id,
                }
            ],
            "motion_type": "static",
            "motion_asset_path": None,
            "motion_status": None,
        }
        if include_runtime_rationale_fields:
            segment.update(
                {
                    "timing_role": "concept-build",
                    "content_density": "medium",
                    "visual_detail_load": "medium",
                    "duration_rationale": (
                        "Longer because this concept-build slide carries medium detail density "
                        "and the visual needs guided explanation."
                    ),
                    "onset_delay": 0.0,
                    "dwell": 0.25,
                    "cluster_gap": 0.0,
                    "transition_buffer": 0.1,
                    "bridge_type": "none",
                }
            )
        if runtime_rationale_overrides and seg_id in runtime_rationale_overrides:
            segment.update(runtime_rationale_overrides[seg_id])
        if bridge_type_overrides and seg_id in bridge_type_overrides:
            segment["bridge_type"] = bridge_type_overrides[seg_id]

        if not disable_spoken_bridge_enrichment:
            bt_enrich = str(segment.get("bridge_type") or "none").strip().lower()
            narr = str(segment["narration_text"])
            if bt_enrich == "intro":
                segment["narration_text"] = f"In this section we explore the idea. {narr}"
            elif bt_enrich == "outro":
                segment["narration_text"] = (
                    f"{narr} Next, we'll connect this to what comes next."
                )
            elif bt_enrich == "both":
                segment["narration_text"] = (
                    f"In this section we explore the idea. {narr} "
                    "To wrap up, we consolidate before moving forward."
                )
            elif bt_enrich == "cluster_boundary":
                segment["narration_text"] = (
                    f"In this section we synthesize what the prior cluster established. {narr} "
                    "Next, we'll pull that thread into the new topic."
                )

        if motion and index == 1:
            segment["motion_type"] = "video"
            segment["motion_status"] = "approved"
            segment["motion_asset_path"] = str(
                wrong_motion_path if wrong_motion_asset else approved_motion_asset
            )
            if motion_visual_file_uses_motion_asset:
                segment["visual_file"] = str(
                    wrong_motion_path if wrong_motion_asset else approved_motion_asset
                )
            if include_motion_confirmation and not wrong_motion_asset:
                motion_perception_artifacts.append(
                    {
                        "segment_id": seg_id,
                        "slide_id": slide_id,
                        "source_motion_path": str(approved_motion_asset),
                    }
                )

        segments.append(segment)

    script_lines = ["# Narration Script", ""]
    for segment in segments:
        script_behavioral_intent = str(segment["behavioral_intent"])
        if script_behavioral_intent_overrides and segment["id"] in script_behavioral_intent_overrides:
            script_behavioral_intent = script_behavioral_intent_overrides[str(segment["id"])]
        if manifest_behavioral_intent_overrides and segment["id"] in manifest_behavioral_intent_overrides:
            segment["behavioral_intent"] = manifest_behavioral_intent_overrides[str(segment["id"])]
        script_lines.extend(
            [
                f"[SEGMENT: {segment['id']}]",
                "",
                "**Stage Directions:**",
                f"- Behavioral Intent: {script_behavioral_intent}",
                "",
                "**Narration:**",
                str(segment["narration_text"]),
                "",
            ]
        )
    (bundle_dir / "narration-script.md").write_text(
        "\n".join(script_lines).rstrip() + "\n",
        encoding="utf-8",
    )

    (bundle_dir / "segment-manifest.yaml").write_text(
        yaml.safe_dump({"segments": segments}, sort_keys=False),
        encoding="utf-8",
    )

    authorized_storyboard = {
        "slide_ids": slide_ids,
        "authorized_slides": [
            {
                "slide_id": row["slide_id"],
                "card_number": row["card_number"],
                "file_path": row["file_path"],
                "source_ref": row["source_ref"],
            }
            for row in gary_slide_output
        ],
    }
    (bundle_dir / "authorized-storyboard.json").write_text(
        json.dumps(authorized_storyboard),
        encoding="utf-8",
    )
    (bundle_dir / "perception-artifacts.json").write_text(
        json.dumps(
            standalone_perception_artifacts if standalone_perception_artifacts is not None else perception_artifacts
        ),
        encoding="utf-8",
    )

    if motion:
        motion_plan = {
            "motion_enabled": True,
            "slides": [
                {
                    "slide_id": slide_ids[0],
                    "motion_type": "video",
                    "motion_asset_path": str(approved_motion_asset),
                    "motion_status": "approved",
                },
                {
                    "slide_id": slide_ids[1],
                    "motion_type": "static",
                    "motion_asset_path": None,
                    "motion_status": None,
                },
            ],
        }
        (bundle_dir / "motion_plan.yaml").write_text(
            yaml.safe_dump(motion_plan, sort_keys=False),
            encoding="utf-8",
        )

    payload: dict[str, object] = {
        "bundle_path": str(bundle_dir),
        "authorized_storyboard_path": str(bundle_dir / "authorized-storyboard.json"),
        "expected_outputs": [
            str(bundle_dir / "narration-script.md"),
            str(bundle_dir / "segment-manifest.yaml"),
            str(bundle_dir / "perception-artifacts.json"),
        ],
    }
    if motion:
        payload["motion_plan_path"] = str(bundle_dir / "motion_plan.yaml")
        if include_motion_confirmation:
            payload["motion_perception_artifacts"] = motion_perception_artifacts

    return payload


def test_fails_when_perception_artifacts_missing() -> None:
    payload = {
        "gary_slide_output": [
            {
                "slide_id": "s-1",
                "card_number": 1,
                "file_path": "course-content/staging/card-01.png",
                "source_ref": "slide-brief.md#Slide 1",
            },
        ]
    }

    result = validate_irene_pass2_handoff(payload)

    assert result["status"] == "fail"
    assert "perception_artifacts" in result["missing_fields"]
    assert any("Missing required Pass 2 field" in msg for msg in result["errors"])


def test_fails_when_perception_does_not_cover_all_gary_slide_ids() -> None:
    payload = {
        "gary_slide_output": [
            {
                "slide_id": "s-1",
                "card_number": 1,
                "file_path": "course-content/staging/card-01.png",
                "source_ref": "slide-brief.md#Slide 1",
            },
            {
                "slide_id": "s-2",
                "card_number": 2,
                "file_path": "course-content/staging/card-02.png",
                "source_ref": "slide-brief.md#Slide 2",
            },
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "sensory_bridge": "Bridge text",
                "source_image_path": "course-content/staging/card-01.png",
            },
        ],
    }

    result = validate_irene_pass2_handoff(payload)

    assert result["status"] == "fail"
    assert result["consistency"]["missing_perception_for"] == ["s-2"]


def test_passes_when_required_inputs_present_and_aligned() -> None:
    payload = {
        "gary_slide_output": [
            {
                "slide_id": "s-1",
                "card_number": 1,
                "file_path": "course-content/staging/card-01.png",
                "source_ref": "slide-brief.md#Slide 1",
            },
            {
                "slide_id": "s-2",
                "card_number": 2,
                "file_path": "course-content/staging/card-02.png",
                "source_ref": "slide-brief.md#Slide 2",
            },
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "sensory_bridge": "Bridge one",
                "source_image_path": "course-content/staging/card-01.png",
            },
            {
                "slide_id": "s-2",
                "sensory_bridge": "Bridge two",
                "source_image_path": "course-content/staging/card-02.png",
            },
        ],
    }

    result = validate_irene_pass2_handoff(payload, expected_artifact_hint="/tmp/perception.json")

    assert result["status"] == "pass"
    assert result["missing_fields"] == []
    assert result["consistency"]["missing_perception_for"] == []
    assert result["order_check"]["strictly_ascending"] is True
    assert result["order_check"]["contiguous_from_one"] is True
    assert "expected location hint" in result["remediation_hint"]


def test_fails_for_non_contiguous_card_numbers() -> None:
    payload = {
        "gary_slide_output": [
            {
                "slide_id": "s-1",
                "card_number": 2,
                "file_path": "course-content/staging/card-01.png",
                "source_ref": "slide-brief.md#Slide 1",
            },
            {
                "slide_id": "s-2",
                "card_number": 3,
                "file_path": "course-content/staging/card-02.png",
                "source_ref": "slide-brief.md#Slide 2",
            },
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": "course-content/staging/card-01.png",
            },
            {
                "slide_id": "s-2",
                "source_image_path": "course-content/staging/card-02.png",
            },
        ],
    }

    result = validate_irene_pass2_handoff(payload)

    assert result["status"] == "fail"
    assert result["order_check"]["strictly_ascending"] is True
    assert result["order_check"]["contiguous_from_one"] is False
    assert any("contiguous and start at 1" in msg for msg in result["errors"])


def test_fails_when_file_path_or_source_ref_missing() -> None:
    payload = {
        "gary_slide_output": [
            {
                "slide_id": "s-1",
                "card_number": 1,
                "file_path": "",
                "source_ref": "slide-brief.md#Slide 1",
            },
            {
                "slide_id": "s-2",
                "card_number": 2,
                "file_path": "course-content/staging/card-02.png",
                "source_ref": "",
            },
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": "course-content/staging/card-01.png",
            },
            {
                "slide_id": "s-2",
                "source_image_path": "course-content/staging/card-02.png",
            },
        ],
    }

    result = validate_irene_pass2_handoff(payload)

    assert result["status"] == "fail"
    assert result["consistency"]["missing_file_path_for"] == ["s-1"]
    assert result["consistency"]["missing_source_ref_for"] == ["s-2"]


def test_fails_when_card_number_does_not_match_slide_filename() -> None:
    payload = {
        "gary_slide_output": [
            {
                "slide_id": "s-1",
                "card_number": 2,
                "file_path": "course-content/staging/slide_01.png",
                "source_ref": "slide-brief.md#Slide 1",
            }
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": "course-content/staging/slide_01.png",
            }
        ],
    }

    result = validate_irene_pass2_handoff(payload)

    assert result["status"] == "fail"
    assert any("card_number does not match slide_XX.png filename" in msg for msg in result["errors"])


def test_bundle_validation_accepts_multi_artifact_perception_for_same_slide(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide = bundle_dir / "slide-01.png"
    slide.write_bytes(b"png")

    gary_slide_output = [
        {
            "slide_id": "s-1",
            "card_number": 1,
            "file_path": str(slide),
            "source_ref": "slide-brief.md#Slide 1",
            "visual_description": "Slide 1",
        }
    ]
    perception_artifacts = [
        {
            "slide_id": "s-1",
            "source_image_path": str(slide),
            "visual_elements": [{"description": "Element 2"}],
        },
        {
            "slide_id": "s-1",
            "source_image_path": str(slide),
            "visual_elements": [{"description": "Element 1"}],
        },
    ]
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=["s-1"],
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
    )

    # Force segment cue to require the element only present in first artifact.
    manifest_path = bundle_dir / "segment-manifest.yaml"
    manifest_data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest_data["segments"][0]["visual_references"][0]["element"] = "Element 2"
    manifest_path.write_text(yaml.safe_dump(manifest_data, sort_keys=False), encoding="utf-8")

    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(payload, envelope_path=envelope_path)

    assert result["status"] == "pass"


def test_bundle_validation_fails_when_visual_cue_traces_to_other_slide(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide_1 = bundle_dir / "slide-01.png"
    slide_2 = bundle_dir / "slide-02.png"
    slide_1.write_bytes(b"png")
    slide_2.write_bytes(b"png")

    gary_slide_output = [
        {
            "slide_id": "s-1",
            "card_number": 1,
            "file_path": str(slide_1),
            "source_ref": "slide-brief.md#Slide 1",
            "visual_description": "Slide 1",
        },
        {
            "slide_id": "s-2",
            "card_number": 2,
            "file_path": str(slide_2),
            "source_ref": "slide-brief.md#Slide 2",
            "visual_description": "Slide 2",
        },
    ]
    perception_artifacts = [
        {
            "slide_id": "s-1",
            "source_image_path": str(slide_1),
            "visual_elements": [{"description": "Element 1"}],
        },
        {
            "slide_id": "s-2",
            "source_image_path": str(slide_2),
            "visual_elements": [{"description": "Element 2"}],
        },
    ]
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=["s-1", "s-2"],
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
    )

    manifest_path = bundle_dir / "segment-manifest.yaml"
    manifest_data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest_data["segments"][0]["visual_references"][0]["perception_source"] = "s-2"
    manifest_data["segments"][0]["visual_references"][0]["element"] = "Element 2"
    manifest_path.write_text(yaml.safe_dump(manifest_data, sort_keys=False), encoding="utf-8")

    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(payload, envelope_path=envelope_path)

    assert result["status"] == "fail"
    assert any(
        "do not trace to the segment's own slide_id perception lineage" in msg
        for msg in result["errors"]
    )


@pytest.mark.parametrize(
    ("payload", "expected_exit"),
    [
        (
            {
                "gary_slide_output": [
                    {
                        "slide_id": "s-1",
                        "card_number": 1,
                        "file_path": "course-content/staging/card-01.png",
                        "source_ref": "slide-brief.md#Slide 1",
                    }
                ],
            },
            1,
        ),
        (
            {
                "gary_slide_output": [
                    {
                        "slide_id": "s-1",
                        "card_number": 1,
                        "file_path": "course-content/staging/card-01.png",
                        "source_ref": "slide-brief.md#Slide 1",
                    }
                ],
                "perception_artifacts": [
                    {
                        "slide_id": "s-1",
                        "source_image_path": "course-content/staging/card-01.png",
                    }
                ],
            },
            0,
        ),
    ],
)
def test_cli_exit_code_and_json_output(
    tmp_path: Path,
    payload: dict[str, object],
    expected_exit: int,
) -> None:
    if expected_exit == 0:
        card_path = tmp_path / "card-01.png"
        card_path.write_bytes(b"png")
        payload = {
            **payload,
            "gary_slide_output": [
                {
                    **payload["gary_slide_output"][0],  # type: ignore[index]
                    "file_path": str(card_path),
                }
            ],
            "perception_artifacts": [
                {
                    **payload["perception_artifacts"][0],  # type: ignore[index]
                    "source_image_path": str(card_path),
                    "visual_elements": [{"description": "Element 1"}],
                }
            ],
        }
        payload = {
            **payload,
            **_write_complete_bundle_outputs(
                tmp_path,
                slide_ids=["s-1"],
                gary_slide_output=payload["gary_slide_output"],  # type: ignore[arg-type]
                perception_artifacts=payload["perception_artifacts"],  # type: ignore[arg-type]
            ),
        }

    envelope_path = tmp_path / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--envelope", str(envelope_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == expected_exit
    data = json.loads(proc.stdout)
    assert "status" in data
    assert data["status"] in {"pass", "fail"}


def test_cli_strict_runtime_policy_fails_by_default(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide = bundle_dir / "slide-01.png"
    slide.write_bytes(b"png")
    gary_slide_output = [
        {
            "slide_id": "s-1",
            "card_number": 1,
            "file_path": str(slide),
            "source_ref": "slide-brief.md#Slide 1",
            "visual_description": "Opening slide",
        }
    ]
    perception_artifacts = [
        {
            "slide_id": "s-1",
            "source_image_path": str(slide),
            "visual_elements": [{"description": "Element 1"}],
        }
    ]
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=["s-1"],
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
        narration_text_overrides={
            "seg-01": "notice cue 1 brief script that is intentionally too short for runtime strict mode"
        },
    )
    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    payload["runtime_plan"] = {"per_slide_targets": [{"card_number": 1, "target_runtime_seconds": 55.0}]}

    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--envelope", str(envelope_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    data = json.loads(proc.stdout)
    assert proc.returncode == 1
    assert data["status"] == "fail"
    assert data["runtime_policy_mode"] == "strict"
    assert any("runtime_policy_violation:" in msg for msg in data["errors"])


def test_cli_runtime_policy_advisory_flag_allows_runtime_warnings(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide = bundle_dir / "slide-01.png"
    slide.write_bytes(b"png")
    gary_slide_output = [
        {
            "slide_id": "s-1",
            "card_number": 1,
            "file_path": str(slide),
            "source_ref": "slide-brief.md#Slide 1",
            "visual_description": "Opening slide",
        }
    ]
    perception_artifacts = [
        {
            "slide_id": "s-1",
            "source_image_path": str(slide),
            "visual_elements": [{"description": "Element 1"}],
        }
    ]
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=["s-1"],
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
        narration_text_overrides={
            "seg-01": "notice cue 1 brief script that is intentionally too short for runtime advisory mode"
        },
    )
    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    payload["runtime_plan"] = {"per_slide_targets": [{"card_number": 1, "target_runtime_seconds": 55.0}]}

    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--envelope",
            str(envelope_path),
            "--runtime-policy-advisory",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    data = json.loads(proc.stdout)
    assert proc.returncode == 0
    assert data["status"] == "pass"
    assert data["runtime_policy_mode"] == "advisory"
    assert not any("runtime_policy_violation:" in msg for msg in data["errors"])
    assert any("soft runtime band" in msg for msg in data["warnings"])


def test_cli_returns_exit_code_2_on_invalid_envelope_payload(tmp_path: Path) -> None:
    envelope_path = tmp_path / "pass2-envelope.json"
    envelope_path.write_text("{ this is not valid json", encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--envelope", str(envelope_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    data = json.loads(proc.stdout)
    assert proc.returncode == 2
    assert data["status"] == "fail"
    assert any("validator_exception:" in msg for msg in data["errors"])


def test_cli_accepts_yaml_envelope(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide = bundle_dir / "slide-01.png"
    slide.write_bytes(b"png")
    payload = {
        "gary_slide_output": [
            {
                "slide_id": "s-1",
                "card_number": 1,
                "file_path": str(slide),
                "source_ref": "slide-brief.md#Slide 1",
            }
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": str(slide),
                "visual_elements": [{"description": "Element 1"}],
            }
        ],
    }
    payload.update(
        _write_complete_bundle_outputs(
            bundle_dir,
            slide_ids=["s-1"],
            gary_slide_output=payload["gary_slide_output"],  # type: ignore[arg-type]
            perception_artifacts=payload["perception_artifacts"],  # type: ignore[arg-type]
        )
    )

    envelope_path = bundle_dir / "pass2-envelope.yaml"
    envelope_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--envelope", str(envelope_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    data = json.loads(proc.stdout)
    assert proc.returncode == 0
    assert data["status"] == "pass"


def test_bundle_validation_fails_when_authorized_slide_missing_manifest_segment(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    card_1 = bundle_dir / "card-01.png"
    card_2 = bundle_dir / "card-02.png"
    card_1.write_bytes(b"png")
    card_2.write_bytes(b"png")

    payload = {
        "gary_slide_output": [
            {"slide_id": "s-1", "card_number": 1, "file_path": str(card_1), "source_ref": "slide-1"},
            {"slide_id": "s-2", "card_number": 2, "file_path": str(card_2), "source_ref": "slide-2"},
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": str(card_1),
                "visual_elements": [{"description": "Element 1"}],
            },
            {
                "slide_id": "s-2",
                "source_image_path": str(card_2),
                "visual_elements": [{"description": "Element 2"}],
            },
        ],
    }
    payload.update(
        _write_complete_bundle_outputs(
            bundle_dir,
            slide_ids=["s-1", "s-2"],
            gary_slide_output=payload["gary_slide_output"],  # type: ignore[arg-type]
            perception_artifacts=payload["perception_artifacts"],  # type: ignore[arg-type]
            omit_slide_id="s-2",
        )
    )

    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=False,
    )

    assert result["status"] == "fail"
    assert result["pass2_outputs"]["missing_manifest_for_slide_ids"] == ["s-2"]


def test_bundle_validation_fails_when_segment_narration_text_empty(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    card_1 = bundle_dir / "card-01.png"
    card_2 = bundle_dir / "card-02.png"
    card_1.write_bytes(b"png")
    card_2.write_bytes(b"png")

    payload = {
        "gary_slide_output": [
            {"slide_id": "s-1", "card_number": 1, "file_path": str(card_1), "source_ref": "slide-1"},
            {"slide_id": "s-2", "card_number": 2, "file_path": str(card_2), "source_ref": "slide-2"},
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": str(card_1),
                "visual_elements": [{"description": "Element 1"}],
            },
            {
                "slide_id": "s-2",
                "source_image_path": str(card_2),
                "visual_elements": [{"description": "Element 2"}],
            },
        ],
    }
    payload.update(
        _write_complete_bundle_outputs(
            bundle_dir,
            slide_ids=["s-1", "s-2"],
            gary_slide_output=payload["gary_slide_output"],  # type: ignore[arg-type]
            perception_artifacts=payload["perception_artifacts"],  # type: ignore[arg-type]
            empty_narration_segment="seg-02",
        )
    )

    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=False,
    )

    assert result["status"] == "fail"
    assert result["pass2_outputs"]["segments_missing_narration_text"] == ["seg-02"]


def test_bundle_validation_fails_when_visual_narration_cue_missing(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    card_1 = bundle_dir / "card-01.png"
    card_2 = bundle_dir / "card-02.png"
    card_1.write_bytes(b"png")
    card_2.write_bytes(b"png")

    payload = {
        "gary_slide_output": [
            {"slide_id": "s-1", "card_number": 1, "file_path": str(card_1), "source_ref": "slide-1"},
            {"slide_id": "s-2", "card_number": 2, "file_path": str(card_2), "source_ref": "slide-2"},
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": str(card_1),
                "visual_elements": [{"description": "Element 1"}],
            },
            {
                "slide_id": "s-2",
                "source_image_path": str(card_2),
                "visual_elements": [{"description": "Element 2"}],
            },
        ],
    }
    payload.update(
        _write_complete_bundle_outputs(
            bundle_dir,
            slide_ids=["s-1", "s-2"],
            gary_slide_output=payload["gary_slide_output"],  # type: ignore[arg-type]
            perception_artifacts=payload["perception_artifacts"],  # type: ignore[arg-type]
            empty_visual_cue_segment="seg-02",
        )
    )

    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=False,
    )

    assert result["status"] == "fail"
    assert result["pass2_outputs"]["segments_missing_visual_narration_cue"] == ["seg-02"]


def test_bundle_validation_fails_when_meta_slide_language_is_forbidden(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    card_1 = bundle_dir / "card-01.png"
    card_2 = bundle_dir / "card-02.png"
    card_1.write_bytes(b"png")
    card_2.write_bytes(b"png")

    payload = {
        "gary_slide_output": [
            {"slide_id": "s-1", "card_number": 1, "file_path": str(card_1), "source_ref": "slide-1"},
            {"slide_id": "s-2", "card_number": 2, "file_path": str(card_2), "source_ref": "slide-2"},
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": str(card_1),
                "visual_elements": [{"description": "Element 1"}],
            },
            {
                "slide_id": "s-2",
                "source_image_path": str(card_2),
                "visual_elements": [{"description": "Element 2"}],
            },
        ],
    }
    payload.update(
        _write_complete_bundle_outputs(
            bundle_dir,
            slide_ids=["s-1", "s-2"],
            gary_slide_output=payload["gary_slide_output"],  # type: ignore[arg-type]
            perception_artifacts=payload["perception_artifacts"],  # type: ignore[arg-type]
            cue_overrides={"seg-02": "notice how the panel on the right frames the takeaway"},
            narration_text_overrides={
                "seg-02": "notice how the panel on the right frames the takeaway for clinicians."
            },
        )
    )

    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=False,
    )

    assert result["status"] == "fail"
    assert result["pass2_outputs"]["segments_with_forbidden_meta_slide_language"] == ["seg-02"]


def test_bundle_validation_fails_when_standalone_perception_artifacts_drift_from_envelope(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    card_1 = bundle_dir / "card-01.png"
    card_2 = bundle_dir / "card-02.png"
    card_1.write_bytes(b"png")
    card_2.write_bytes(b"png")

    envelope_perception = [
        {
            "slide_id": "s-1",
            "source_image_path": str(card_1),
            "visual_elements": [{"description": "Element 1"}],
        },
        {
            "slide_id": "s-2",
            "source_image_path": str(card_2),
            "visual_elements": [{"description": "Element 2"}],
        },
    ]
    standalone_perception = [
        {
            "slide_id": "s-1",
            "source_image_path": str(card_1),
            "visual_elements": [{"description": "Different Element"}],
        },
        {
            "slide_id": "s-2",
            "source_image_path": str(card_2),
            "visual_elements": [{"description": "Element 2"}],
        },
    ]
    payload = {
        "gary_slide_output": [
            {"slide_id": "s-1", "card_number": 1, "file_path": str(card_1), "source_ref": "slide-1"},
            {"slide_id": "s-2", "card_number": 2, "file_path": str(card_2), "source_ref": "slide-2"},
        ],
        "perception_artifacts": envelope_perception,
    }
    payload.update(
        _write_complete_bundle_outputs(
            bundle_dir,
            slide_ids=["s-1", "s-2"],
            gary_slide_output=payload["gary_slide_output"],  # type: ignore[arg-type]
            perception_artifacts=envelope_perception,  # type: ignore[arg-type]
            standalone_perception_artifacts=standalone_perception,
        )
    )

    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(payload, envelope_path=envelope_path)

    assert result["status"] == "fail"
    assert result["pass2_outputs"]["perception_artifact_mismatches"] == ["s-1"]


def test_bundle_validation_reports_active_narration_profile_controls(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide = bundle_dir / "card-01.png"
    slide.write_bytes(b"png")
    envelope_controls = {
        "narrator_source_authority": "slide-led",
        "slide_content_density": "dense",
        "elaboration_budget": "low",
    }

    payload = {
        "gary_slide_output": [
            {"slide_id": "s-1", "card_number": 1, "file_path": str(slide), "source_ref": "slide-1"},
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": str(slide),
                "visual_elements": [{"description": "Element 1"}],
            },
        ],
        "narration_profile_controls": envelope_controls,
    }
    payload.update(
        _write_complete_bundle_outputs(
            bundle_dir,
            slide_ids=["s-1"],
            gary_slide_output=payload["gary_slide_output"],  # type: ignore[arg-type]
            perception_artifacts=payload["perception_artifacts"],  # type: ignore[arg-type]
        )
    )

    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(payload, envelope_path=envelope_path)

    controls = result["pass2_outputs"]["active_narration_profile_controls"]
    assert controls == envelope_controls


def test_bundle_validation_fails_when_behavioral_intent_drifts_between_script_and_manifest(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    card_1 = bundle_dir / "card-01.png"
    card_2 = bundle_dir / "card-02.png"
    card_1.write_bytes(b"png")
    card_2.write_bytes(b"png")

    payload = {
        "gary_slide_output": [
            {"slide_id": "s-1", "card_number": 1, "file_path": str(card_1), "source_ref": "slide-1"},
            {"slide_id": "s-2", "card_number": 2, "file_path": str(card_2), "source_ref": "slide-2"},
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": str(card_1),
                "visual_elements": [{"description": "Element 1"}],
            },
            {
                "slide_id": "s-2",
                "source_image_path": str(card_2),
                "visual_elements": [{"description": "Element 2"}],
            },
        ],
    }
    payload.update(
        _write_complete_bundle_outputs(
            bundle_dir,
            slide_ids=["s-1", "s-2"],
            gary_slide_output=payload["gary_slide_output"],  # type: ignore[arg-type]
            perception_artifacts=payload["perception_artifacts"],  # type: ignore[arg-type]
            script_behavioral_intent_overrides={"seg-02": "reflective"},
            manifest_behavioral_intent_overrides={"seg-02": "credible"},
        )
    )

    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(payload, envelope_path=envelope_path)

    assert result["status"] == "fail"
    assert result["pass2_outputs"]["segments_with_behavioral_intent_mismatch"] == ["seg-02"]


def test_bundle_validation_fails_when_motion_segment_not_bound_to_approved_asset(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    card_1 = bundle_dir / "card-01.png"
    card_2 = bundle_dir / "card-02.png"
    card_1.write_bytes(b"png")
    card_2.write_bytes(b"png")

    payload = {
        "gary_slide_output": [
            {"slide_id": "s-1", "card_number": 1, "file_path": str(card_1), "source_ref": "slide-1"},
            {"slide_id": "s-2", "card_number": 2, "file_path": str(card_2), "source_ref": "slide-2"},
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": str(card_1),
                "visual_elements": [{"description": "Element 1"}],
            },
            {
                "slide_id": "s-2",
                "source_image_path": str(card_2),
                "visual_elements": [{"description": "Element 2"}],
            },
        ],
    }
    payload.update(
        _write_complete_bundle_outputs(
            bundle_dir,
            slide_ids=["s-1", "s-2"],
            gary_slide_output=payload["gary_slide_output"],  # type: ignore[arg-type]
            perception_artifacts=payload["perception_artifacts"],  # type: ignore[arg-type]
            motion=True,
            wrong_motion_asset=True,
        )
    )

    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(payload, envelope_path=envelope_path)

    assert result["status"] == "fail"
    assert result["pass2_outputs"]["motion_segments_with_unapproved_asset_binding"] == ["seg-01"]


def test_bundle_validation_passes_with_complete_motion_binding_and_confirmation(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    card_1 = bundle_dir / "card-01.png"
    card_2 = bundle_dir / "card-02.png"
    card_1.write_bytes(b"png")
    card_2.write_bytes(b"png")

    payload = {
        "gary_slide_output": [
            {"slide_id": "s-1", "card_number": 1, "file_path": str(card_1), "source_ref": "slide-1"},
            {"slide_id": "s-2", "card_number": 2, "file_path": str(card_2), "source_ref": "slide-2"},
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": str(card_1),
                "visual_elements": [{"description": "Element 1"}],
            },
            {
                "slide_id": "s-2",
                "source_image_path": str(card_2),
                "visual_elements": [{"description": "Element 2"}],
            },
        ],
    }
    payload.update(
        _write_complete_bundle_outputs(
            bundle_dir,
            slide_ids=["s-1", "s-2"],
            gary_slide_output=payload["gary_slide_output"],  # type: ignore[arg-type]
            perception_artifacts=payload["perception_artifacts"],  # type: ignore[arg-type]
            motion=True,
        )
    )

    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(payload, envelope_path=envelope_path)

    assert result["status"] == "pass"
    assert result["pass2_outputs"]["motion_segments_missing_perception_confirmation"] == []


def test_bundle_validation_fails_when_motion_segment_visual_file_points_to_mp4(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    card_1 = bundle_dir / "card-01.png"
    card_2 = bundle_dir / "card-02.png"
    card_1.write_bytes(b"png")
    card_2.write_bytes(b"png")

    payload = {
        "gary_slide_output": [
            {"slide_id": "s-1", "card_number": 1, "file_path": str(card_1), "source_ref": "slide-1"},
            {"slide_id": "s-2", "card_number": 2, "file_path": str(card_2), "source_ref": "slide-2"},
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": str(card_1),
                "visual_elements": [{"description": "Element 1"}],
            },
            {
                "slide_id": "s-2",
                "source_image_path": str(card_2),
                "visual_elements": [{"description": "Element 2"}],
            },
        ],
    }
    payload.update(
        _write_complete_bundle_outputs(
            bundle_dir,
            slide_ids=["s-1", "s-2"],
            gary_slide_output=payload["gary_slide_output"],  # type: ignore[arg-type]
            perception_artifacts=payload["perception_artifacts"],  # type: ignore[arg-type]
            motion=True,
            motion_visual_file_uses_motion_asset=True,
        )
    )

    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(payload, envelope_path=envelope_path)

    assert result["status"] == "fail"
    assert result["pass2_outputs"]["motion_segments_with_noncanonical_visual_file"] == ["seg-01"]


def test_fails_when_perception_source_image_path_missing() -> None:
    payload = {
        "gary_slide_output": [
            {
                "slide_id": "s-1",
                "card_number": 1,
                "file_path": "course-content/staging/card-01.png",
                "source_ref": "slide-brief.md#Slide 1",
            },
        ],
        "perception_artifacts": [
            {"slide_id": "s-1", "sensory_bridge": "Bridge one"},
        ],
    }

    result = validate_irene_pass2_handoff(payload)

    assert result["status"] == "fail"
    assert any("missing non-empty source_image_path" in msg for msg in result["errors"])


def test_fails_when_perception_source_path_does_not_match_gary_slide() -> None:
    payload = {
        "gary_slide_output": [
            {
                "slide_id": "s-1",
                "card_number": 1,
                "file_path": "course-content/staging/card-01.png",
                "source_ref": "slide-brief.md#Slide 1",
            },
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": "course-content/staging/card-99.png",
            },
        ],
    }

    result = validate_irene_pass2_handoff(payload)

    assert result["status"] == "fail"
    assert any("must match gary_slide_output.file_path" in msg for msg in result["errors"])


def test_fails_when_gary_file_path_is_remote() -> None:
    payload = {
        "gary_slide_output": [
            {
                "slide_id": "s-1",
                "card_number": 1,
                "file_path": "https://example.org/card-01.png",
                "source_ref": "slide-brief.md#Slide 1",
            },
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": "https://example.org/card-01.png",
            },
        ],
    }

    result = validate_irene_pass2_handoff(payload)

    assert result["status"] == "fail"
    assert any("must reference local downloaded PNGs" in msg for msg in result["errors"])


def test_runtime_budget_mismatch_fails_in_strict_mode(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide = bundle_dir / "slide-01.png"
    slide.write_bytes(b"png")
    gary_slide_output = [
        {
            "slide_id": "s-1",
            "card_number": 1,
            "file_path": str(slide),
            "source_ref": "slide-brief.md#Slide 1",
            "visual_description": "Opening slide",
        }
    ]
    perception_artifacts = [
        {
            "slide_id": "s-1",
            "source_image_path": str(slide),
            "visual_elements": [{"description": "Element 1"}],
        }
    ]
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=["s-1"],
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
        narration_text_overrides={
            "seg-01": "notice cue 1 brief script that is intentionally too short for the runtime target"
        },
    )
    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    payload["runtime_plan"] = {
        "per_slide_targets": [
            {"card_number": 1, "target_runtime_seconds": 55.0},
        ]
    }
    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(payload, envelope_path=envelope_path)

    assert result["status"] == "fail"
    assert any("runtime_policy_violation:" in error for error in result["errors"])
    assert any("soft runtime band" in warning for warning in result["warnings"])


def test_runtime_rationale_fields_fail_in_strict_mode_when_missing(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide = bundle_dir / "slide-01.png"
    slide.write_bytes(b"png")
    gary_slide_output = [
        {
            "slide_id": "s-1",
            "card_number": 1,
            "file_path": str(slide),
            "source_ref": "slide-brief.md#Slide 1",
            "visual_description": "Opening slide",
        }
    ]
    perception_artifacts = [
        {
            "slide_id": "s-1",
            "source_image_path": str(slide),
            "visual_elements": [{"description": "Element 1"}],
        }
    ]
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=["s-1"],
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
        narration_text_overrides={"seg-01": " ".join(["headword"] * 100)},
        cue_overrides={"seg-01": "headword"},
    )
    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    payload["runtime_plan"] = {
        "per_slide_targets": [
            {"card_number": 1, "target_runtime_seconds": 45.0},
        ]
    }
    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(payload, envelope_path=envelope_path)

    assert result["status"] == "fail"
    assert any("runtime_policy_violation:" in error for error in result["errors"])
    assert any("runtime rationale fields" in warning for warning in result["warnings"])


def test_runtime_rationale_is_not_warned_when_specific(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide = bundle_dir / "slide-01.png"
    slide.write_bytes(b"png")
    gary_slide_output = [
        {
            "slide_id": "s-1",
            "card_number": 1,
            "file_path": str(slide),
            "source_ref": "slide-brief.md#Slide 1",
            "visual_description": "Opening slide",
        }
    ]
    perception_artifacts = [
        {
            "slide_id": "s-1",
            "source_image_path": str(slide),
            "visual_elements": [{"description": "Element 1"}],
        }
    ]
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=["s-1"],
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
        include_runtime_rationale_fields=True,
    )
    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    payload["runtime_plan"] = {
        "per_slide_targets": [
            {"card_number": 1, "target_runtime_seconds": 45.0},
        ]
    }
    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=False,
    )

    assert result["status"] == "pass"
    assert not any("runtime rationale fields" in warning for warning in result["warnings"])
    assert not any("duration_rationale should reference" in warning for warning in result["warnings"])


def test_bridge_cadence_fails_in_strict_mode_when_span_exceeded(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide_ids = [f"s-{index}" for index in range(1, 7)]
    gary_slide_output = []
    perception_artifacts = []
    for index, slide_id in enumerate(slide_ids, start=1):
        slide = bundle_dir / f"slide-{index:02d}.png"
        slide.write_bytes(b"png")
        gary_slide_output.append(
            {
                "slide_id": slide_id,
                "card_number": index,
                "file_path": str(slide),
                "source_ref": f"slide-brief.md#Slide {index}",
                "visual_description": f"Slide {index}",
            }
        )
        perception_artifacts.append(
            {
                "slide_id": slide_id,
                "source_image_path": str(slide),
                "visual_elements": [{"description": f"Element {index}"}],
            }
        )
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=slide_ids,
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
        include_runtime_rationale_fields=True,
    )
    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    payload["runtime_plan"] = {
        "per_slide_targets": [
            {"card_number": index, "target_runtime_seconds": 40.0}
            for index in range(1, 7)
        ]
    }
    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(payload, envelope_path=envelope_path)

    assert result["status"] == "fail"
    assert any("runtime_policy_violation:" in error for error in result["errors"])
    assert any("bridge cadence exceeded" in warning for warning in result["warnings"])


def test_bridge_cadence_passes_when_marked_bridge_resets_span(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide_ids = [f"s-{index}" for index in range(1, 7)]
    gary_slide_output = []
    perception_artifacts = []
    for index, slide_id in enumerate(slide_ids, start=1):
        slide = bundle_dir / f"slide-{index:02d}.png"
        slide.write_bytes(b"png")
        gary_slide_output.append(
            {
                "slide_id": slide_id,
                "card_number": index,
                "file_path": str(slide),
                "source_ref": f"slide-brief.md#Slide {index}",
                "visual_description": f"Slide {index}",
            }
        )
        perception_artifacts.append(
            {
                "slide_id": slide_id,
                "source_image_path": str(slide),
                "visual_elements": [{"description": f"Element {index}"}],
            }
        )
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=slide_ids,
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
        include_runtime_rationale_fields=True,
        bridge_type_overrides={"seg-04": "outro"},
    )
    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    payload["runtime_plan"] = {
        "per_slide_targets": [
            {"card_number": index, "target_runtime_seconds": 40.0}
            for index in range(1, 7)
        ]
    }
    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=False,
    )

    assert result["status"] == "pass"
    assert not any("bridge cadence exceeded" in warning for warning in result["warnings"])


def test_runtime_policy_can_be_downgraded_to_advisory_mode(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide = bundle_dir / "slide-01.png"
    slide.write_bytes(b"png")
    gary_slide_output = [
        {
            "slide_id": "s-1",
            "card_number": 1,
            "file_path": str(slide),
            "source_ref": "slide-brief.md#Slide 1",
            "visual_description": "Opening slide",
        }
    ]
    perception_artifacts = [
        {
            "slide_id": "s-1",
            "source_image_path": str(slide),
            "visual_elements": [{"description": "Element 1"}],
        }
    ]
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=["s-1"],
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
        narration_text_overrides={
            "seg-01": "notice cue 1 brief script that is intentionally too short for the runtime target"
        },
    )
    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    payload["runtime_plan"] = {
        "per_slide_targets": [
            {"card_number": 1, "target_runtime_seconds": 55.0},
        ]
    }
    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=False,
    )

    assert result["status"] == "pass"
    assert result["runtime_policy_mode"] == "advisory"
    assert any("soft runtime band" in warning for warning in result["warnings"])


def test_cli_fails_when_local_png_missing_on_disk(tmp_path: Path) -> None:
    envelope_path = tmp_path / "pass2-envelope.json"
    payload = {
        "gary_slide_output": [
            {
                "slide_id": "s-1",
                "card_number": 1,
                "file_path": "missing/card-01.png",
                "source_ref": "slide-brief.md#Slide 1",
            },
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": "missing/card-01.png",
            },
        ],
    }
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--envelope", str(envelope_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 1
    data = json.loads(proc.stdout)
    assert data["status"] == "fail"
    assert any("does not exist on disk" in msg for msg in data.get("errors", []))


def _bundle_with_intro_bridge_no_spoken_cue(tmp_path: Path) -> tuple[Path, dict]:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide = bundle_dir / "slide-01.png"
    slide.write_bytes(b"png")
    gary_slide_output = [
        {
            "slide_id": "s-1",
            "card_number": 1,
            "file_path": str(slide),
            "source_ref": "slide-brief.md#Slide 1",
            "visual_description": "Slide 1",
        }
    ]
    perception_artifacts = [
        {
            "slide_id": "s-1",
            "source_image_path": str(slide),
            "visual_elements": [{"description": "Element 1"}],
        }
    ]
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=["s-1"],
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
        include_runtime_rationale_fields=True,
        bridge_type_overrides={"seg-01": "intro"},
        disable_spoken_bridge_enrichment=True,
    )
    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")
    return envelope_path, payload


def test_spoken_bridge_warns_in_advisory_mode_when_cues_missing(
    tmp_path: Path,
) -> None:
    envelope_path, payload = _bundle_with_intro_bridge_no_spoken_cue(tmp_path)
    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=False,
    )
    assert result["status"] == "pass"
    assert any("spoken_bridge_policy" in w for w in result["warnings"])


def test_spoken_bridge_strict_mode_fails_when_cues_missing(tmp_path: Path) -> None:
    envelope_path, payload = _bundle_with_intro_bridge_no_spoken_cue(tmp_path)
    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=True,
    )
    assert result["status"] == "pass"
    assert any("spoken_bridge_policy" in w for w in result["warnings"])


def test_spoken_bridge_error_enforcement_fails_without_pattern(
    monkeypatch,
    tmp_path: Path,
) -> None:
    def fake_pedagogical_bridging() -> dict:
        return {
            "spoken_bridge_policy": {
                "enforcement": "error",
                "intro_phrase_patterns": ["in this section"],
                "outro_phrase_patterns": ["next, we'll"],
            }
        }

    monkeypatch.setattr(module, "_load_pedagogical_bridging", fake_pedagogical_bridging)
    envelope_path, payload = _bundle_with_intro_bridge_no_spoken_cue(tmp_path)
    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=False,
    )
    assert result["status"] == "fail"
    assert any("bridge_type is intro" in e for e in result["errors"])


def test_spoken_bridge_passes_when_default_enrichment_matches_patterns(
    tmp_path: Path,
) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide = bundle_dir / "slide-01.png"
    slide.write_bytes(b"png")
    gary_slide_output = [
        {
            "slide_id": "s-1",
            "card_number": 1,
            "file_path": str(slide),
            "source_ref": "slide-brief.md#Slide 1",
            "visual_description": "Slide 1",
        }
    ]
    perception_artifacts = [
        {
            "slide_id": "s-1",
            "source_image_path": str(slide),
            "visual_elements": [{"description": "Element 1"}],
        }
    ]
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=["s-1"],
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
        include_runtime_rationale_fields=True,
        bridge_type_overrides={"seg-01": "intro"},
        disable_spoken_bridge_enrichment=False,
    )
    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=True,
    )
    assert result["status"] == "pass"
    assert not any("spoken_bridge_policy" in w for w in result["warnings"])


def test_cluster_schema_additive_fields_tolerated_flat_manifest(
    tmp_path: Path,
) -> None:
    """Regression test: flat manifest without cluster fields loads without error."""
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide = bundle_dir / "slide-01.png"
    slide.write_bytes(b"png")
    gary_slide_output = [
        {
            "slide_id": "s-1",
            "card_number": 1,
            "file_path": str(slide),
            "source_ref": "slide-brief.md#Slide 1",
            "visual_description": "Slide 1",
        }
    ]
    perception_artifacts = [
        {
            "slide_id": "s-1",
            "source_image_path": str(slide),
            "visual_elements": [{"description": "Element 1"}],
        }
    ]
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=["s-1"],
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
    )
    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    payload["runtime_plan"] = {
        "per_slide_targets": [{"card_number": 1, "target_runtime_seconds": 25.0}]
    }
    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    # Should pass without cluster fields
    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=False,
    )
    assert result["status"] == "pass"


def test_cluster_schema_additive_fields_tolerated_clustered_manifest(
    tmp_path: Path,
) -> None:
    """Regression test: clustered manifest with cluster fields loads without error."""
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide = bundle_dir / "slide-01.png"
    slide.write_bytes(b"png")
    gary_slide_output = [
        {
            "slide_id": "s-1",
            "card_number": 1,
            "file_path": str(slide),
            "source_ref": "slide-brief.md#Slide 1",
            "visual_description": "Slide 1",
        }
    ]
    perception_artifacts = [
        {
            "slide_id": "s-1",
            "source_image_path": str(slide),
            "visual_elements": [{"description": "Element 1"}],
        }
    ]
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=["s-1"],
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
    )
    # Add cluster fields to the on-disk manifest (segments live on disk, not in payload)
    manifest_path = bundle_dir / "segment-manifest.yaml"
    manifest_data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest_data["segments"][0].update({
        "cluster_id": "c1",
        "cluster_role": "head",
        "cluster_position": "establish",
        "parent_slide_id": None,
        "interstitial_type": None,
        "isolation_target": None,
        "narrative_arc": "From confusion to clarity",
        "cluster_interstitial_count": 1,
        "double_dispatch_eligible": True,
    })
    manifest_path.write_text(
        yaml.safe_dump(manifest_data, sort_keys=False), encoding="utf-8"
    )
    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    # Should pass with cluster fields
    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=False,
    )
    assert result["status"] == "pass"


def test_cluster_word_ranges_pass_when_head_and_interstitial_fit_contract(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide_paths = [bundle_dir / "slide-01.png", bundle_dir / "slide-02.png"]
    for slide_path in slide_paths:
        slide_path.write_bytes(b"png")
    gary_slide_output = [
        {
            "slide_id": "s-1",
            "card_number": 1,
            "file_path": str(slide_paths[0]),
            "source_ref": "slide-brief.md#Slide 1",
            "visual_description": "Head slide",
        },
        {
            "slide_id": "s-2",
            "card_number": 2,
            "file_path": str(slide_paths[1]),
            "source_ref": "slide-brief.md#Slide 2",
            "visual_description": "Interstitial slide",
        },
    ]
    perception_artifacts = [
        {
            "slide_id": "s-1",
            "source_image_path": str(slide_paths[0]),
            "visual_elements": [{"description": "Element 1"}],
        },
        {
            "slide_id": "s-2",
            "source_image_path": str(slide_paths[1]),
            "visual_elements": [{"description": "Element 2"}],
        },
    ]
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=["s-1", "s-2"],
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
        narration_text_overrides={
            "seg-01": "bridge " + " ".join(["headword"] * 99),
            "seg-02": " ".join(["bridge"] * 30),
        },
        cue_overrides={"seg-01": "headword", "seg-02": "bridge"},
        include_runtime_rationale_fields=True,
    )
    manifest_path = bundle_dir / "segment-manifest.yaml"
    manifest_data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest_data["segments"][0].update(
        {
            "cluster_id": "c1",
            "cluster_role": "head",
            "cluster_position": "establish",
            "narrative_arc": "From big picture to focused detail",
            "cluster_interstitial_count": 1,
            "master_behavioral_intent": "credible",
        }
    )
    manifest_data["segments"][1].update(
        {
            "cluster_id": "c1",
            "cluster_role": "interstitial",
            "cluster_position": "develop",
            "parent_slide_id": "s-1",
            "interstitial_type": "emphasis-shift",
            "isolation_target": "Element 2",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_path.write_text(yaml.safe_dump(manifest_data, sort_keys=False), encoding="utf-8")
    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=True,
    )

    assert result["status"] == "pass"
    assert not any("cluster_head_word_range" in warning for warning in result["warnings"])
    assert not any("interstitial_word_range" in warning for warning in result["warnings"])


def test_cluster_interstitial_word_range_fails_when_too_long(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide_paths = [bundle_dir / "slide-01.png", bundle_dir / "slide-02.png"]
    for slide_path in slide_paths:
        slide_path.write_bytes(b"png")
    gary_slide_output = [
        {
            "slide_id": "s-1",
            "card_number": 1,
            "file_path": str(slide_paths[0]),
            "source_ref": "slide-brief.md#Slide 1",
            "visual_description": "Head slide",
        },
        {
            "slide_id": "s-2",
            "card_number": 2,
            "file_path": str(slide_paths[1]),
            "source_ref": "slide-brief.md#Slide 2",
            "visual_description": "Interstitial slide",
        },
    ]
    perception_artifacts = [
        {
            "slide_id": "s-1",
            "source_image_path": str(slide_paths[0]),
            "visual_elements": [{"description": "Element 1"}],
        },
        {
            "slide_id": "s-2",
            "source_image_path": str(slide_paths[1]),
            "visual_elements": [{"description": "Element 2"}],
        },
    ]
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=["s-1", "s-2"],
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
        narration_text_overrides={
            "seg-01": "longword " + " ".join(["headword"] * 99),
            "seg-02": " ".join(["longword"] * 46),
        },
        cue_overrides={"seg-01": "headword", "seg-02": "longword"},
        include_runtime_rationale_fields=True,
    )
    manifest_path = bundle_dir / "segment-manifest.yaml"
    manifest_data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest_data["segments"][0].update(
        {
            "cluster_id": "c1",
            "cluster_role": "head",
            "cluster_position": "establish",
            "narrative_arc": "From big picture to focused detail",
            "cluster_interstitial_count": 1,
        }
    )
    manifest_data["segments"][1].update(
        {
            "cluster_id": "c1",
            "cluster_role": "interstitial",
            "cluster_position": "develop",
            "parent_slide_id": "s-1",
            "interstitial_type": "emphasis-shift",
            "isolation_target": "Element 2",
        }
    )
    manifest_path.write_text(yaml.safe_dump(manifest_data, sort_keys=False), encoding="utf-8")
    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=True,
    )

    assert result["status"] == "fail"
    assert any(
        "runtime_policy_violation:" in error and "interstitial_word_range" in error
        for error in result["errors"]
    )


def test_non_tension_interstitial_bridge_fails_under_cluster_policy(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide_paths = [bundle_dir / "slide-01.png", bundle_dir / "slide-02.png"]
    for slide_path in slide_paths:
        slide_path.write_bytes(b"png")
    gary_slide_output = [
        {
            "slide_id": "s-1",
            "card_number": 1,
            "file_path": str(slide_paths[0]),
            "source_ref": "slide-brief.md#Slide 1",
            "visual_description": "Head slide",
        },
        {
            "slide_id": "s-2",
            "card_number": 2,
            "file_path": str(slide_paths[1]),
            "source_ref": "slide-brief.md#Slide 2",
            "visual_description": "Interstitial slide",
        },
    ]
    perception_artifacts = [
        {
            "slide_id": "s-1",
            "source_image_path": str(slide_paths[0]),
            "visual_elements": [{"description": "Element 1"}],
        },
        {
            "slide_id": "s-2",
            "source_image_path": str(slide_paths[1]),
            "visual_elements": [{"description": "Element 2"}],
        },
    ]
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=["s-1", "s-2"],
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
        bridge_type_overrides={"seg-02": "intro"},
        include_runtime_rationale_fields=True,
    )
    manifest_path = bundle_dir / "segment-manifest.yaml"
    manifest_data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest_data["segments"][0].update(
        {
            "cluster_id": "c1",
            "cluster_role": "head",
            "cluster_position": "establish",
            "narrative_arc": "From big picture to focused detail",
            "cluster_interstitial_count": 1,
        }
    )
    manifest_data["segments"][1].update(
        {
            "cluster_id": "c1",
            "cluster_role": "interstitial",
            "cluster_position": "develop",
            "parent_slide_id": "s-1",
            "interstitial_type": "emphasis-shift",
            "isolation_target": "Element 2",
        }
    )
    manifest_path.write_text(yaml.safe_dump(manifest_data, sort_keys=False), encoding="utf-8")
    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=True,
    )

    assert result["status"] == "fail"
    assert any(
        "runtime_policy_violation:" in error and "within-cluster bridges are reserved" in error
        for error in result["errors"]
    )


def test_tension_interstitial_allows_pivot_bridge_under_cluster_policy(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide_paths = [bundle_dir / "slide-01.png", bundle_dir / "slide-02.png"]
    for slide_path in slide_paths:
        slide_path.write_bytes(b"png")
    gary_slide_output = [
        {
            "slide_id": "s-1",
            "card_number": 1,
            "file_path": str(slide_paths[0]),
            "source_ref": "slide-brief.md#Slide 1",
            "visual_description": "Head slide",
        },
        {
            "slide_id": "s-2",
            "card_number": 2,
            "file_path": str(slide_paths[1]),
            "source_ref": "slide-brief.md#Slide 2",
            "visual_description": "Tension interstitial slide",
        },
    ]
    perception_artifacts = [
        {
            "slide_id": "s-1",
            "source_image_path": str(slide_paths[0]),
            "visual_elements": [{"description": "Element 1"}],
        },
        {
            "slide_id": "s-2",
            "source_image_path": str(slide_paths[1]),
            "visual_elements": [{"description": "Element 2"}],
        },
    ]
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=["s-1", "s-2"],
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
        bridge_type_overrides={"seg-02": "pivot"},
        narration_text_overrides={
            "seg-01": " ".join(["headword"] * 100),
            "seg-02": "However " + " ".join(["pivotword"] * 29),
        },
        cue_overrides={"seg-01": "headword", "seg-02": "However"},
        include_runtime_rationale_fields=True,
    )
    manifest_path = bundle_dir / "segment-manifest.yaml"
    manifest_data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest_data["segments"][0].update(
        {
            "cluster_id": "c1",
            "cluster_role": "head",
            "cluster_position": "establish",
            "narrative_arc": "From big picture to focused detail",
            "cluster_interstitial_count": 1,
            "master_behavioral_intent": "credible",
        }
    )
    manifest_data["segments"][1].update(
        {
            "cluster_id": "c1",
            "cluster_role": "interstitial",
            "cluster_position": "tension",
            "parent_slide_id": "s-1",
            "interstitial_type": "emphasis-shift",
            "isolation_target": "Element 2",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_path.write_text(yaml.safe_dump(manifest_data, sort_keys=False), encoding="utf-8")
    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=True,
    )

    assert result["status"] == "pass"
    assert not any("invalid bridge_type pivot" in error for error in result["errors"])
    assert not any("within-cluster bridges are reserved" in warning for warning in result["warnings"])


def test_tension_interstitial_rejects_non_pivot_bridge_under_cluster_policy(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide_paths = [bundle_dir / "slide-01.png", bundle_dir / "slide-02.png"]
    for slide_path in slide_paths:
        slide_path.write_bytes(b"png")
    gary_slide_output = [
        {
            "slide_id": "s-1",
            "card_number": 1,
            "file_path": str(slide_paths[0]),
            "source_ref": "slide-brief.md#Slide 1",
            "visual_description": "Head slide",
        },
        {
            "slide_id": "s-2",
            "card_number": 2,
            "file_path": str(slide_paths[1]),
            "source_ref": "slide-brief.md#Slide 2",
            "visual_description": "Tension interstitial slide",
        },
    ]
    perception_artifacts = [
        {
            "slide_id": "s-1",
            "source_image_path": str(slide_paths[0]),
            "visual_elements": [{"description": "Element 1"}],
        },
        {
            "slide_id": "s-2",
            "source_image_path": str(slide_paths[1]),
            "visual_elements": [{"description": "Element 2"}],
        },
    ]
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=["s-1", "s-2"],
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
        bridge_type_overrides={"seg-02": "intro"},
        include_runtime_rationale_fields=True,
    )
    manifest_path = bundle_dir / "segment-manifest.yaml"
    manifest_data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest_data["segments"][0].update(
        {
            "cluster_id": "c1",
            "cluster_role": "head",
            "cluster_position": "establish",
            "narrative_arc": "From big picture to focused detail",
            "cluster_interstitial_count": 1,
            "master_behavioral_intent": "credible",
        }
    )
    manifest_data["segments"][1].update(
        {
            "cluster_id": "c1",
            "cluster_role": "interstitial",
            "cluster_position": "tension",
            "parent_slide_id": "s-1",
            "interstitial_type": "emphasis-shift",
            "isolation_target": "Element 2",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_path.write_text(yaml.safe_dump(manifest_data, sort_keys=False), encoding="utf-8")
    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=True,
    )

    assert result["status"] == "fail"
    assert any(
        "runtime_policy_violation:" in error and "may only use bridge_type pivot" in error
        for error in result["errors"]
    )


def test_cluster_head_rejects_pivot_bridge_under_cluster_policy(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide_paths = [bundle_dir / "slide-01.png", bundle_dir / "slide-02.png"]
    for slide_path in slide_paths:
        slide_path.write_bytes(b"png")
    gary_slide_output = [
        {
            "slide_id": "s-1",
            "card_number": 1,
            "file_path": str(slide_paths[0]),
            "source_ref": "slide-brief.md#Slide 1",
            "visual_description": "Head slide",
        },
        {
            "slide_id": "s-2",
            "card_number": 2,
            "file_path": str(slide_paths[1]),
            "source_ref": "slide-brief.md#Slide 2",
            "visual_description": "Interstitial slide",
        },
    ]
    perception_artifacts = [
        {
            "slide_id": "s-1",
            "source_image_path": str(slide_paths[0]),
            "visual_elements": [{"description": "Element 1"}],
        },
        {
            "slide_id": "s-2",
            "source_image_path": str(slide_paths[1]),
            "visual_elements": [{"description": "Element 2"}],
        },
    ]
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=["s-1", "s-2"],
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
        bridge_type_overrides={"seg-01": "pivot"},
        narration_text_overrides={
            "seg-01": "However " + " ".join(["headword"] * 99),
            "seg-02": " ".join(["detail"] * 30),
        },
        cue_overrides={"seg-01": "However", "seg-02": "detail"},
        include_runtime_rationale_fields=True,
    )
    manifest_path = bundle_dir / "segment-manifest.yaml"
    manifest_data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest_data["segments"][0].update(
        {
            "cluster_id": "c1",
            "cluster_role": "head",
            "cluster_position": "establish",
            "narrative_arc": "From big picture to focused detail",
            "cluster_interstitial_count": 1,
            "master_behavioral_intent": "credible",
        }
    )
    manifest_data["segments"][1].update(
        {
            "cluster_id": "c1",
            "cluster_role": "interstitial",
            "cluster_position": "tension",
            "parent_slide_id": "s-1",
            "interstitial_type": "emphasis-shift",
            "isolation_target": "Element 2",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_path.write_text(yaml.safe_dump(manifest_data, sort_keys=False), encoding="utf-8")
    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=True,
    )

    assert result["status"] == "fail"
    assert any(
        "runtime_policy_violation:" in error and "only tension interstitials may use bridge_type pivot" in error
        for error in result["errors"]
    )


def test_pivot_bridge_skips_spoken_cue_validation_in_clustered_mode(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide_paths = [bundle_dir / "slide-01.png", bundle_dir / "slide-02.png"]
    for slide_path in slide_paths:
        slide_path.write_bytes(b"png")
    gary_slide_output = [
        {
            "slide_id": "s-1",
            "card_number": 1,
            "file_path": str(slide_paths[0]),
            "source_ref": "slide-brief.md#Slide 1",
            "visual_description": "Head slide",
        },
        {
            "slide_id": "s-2",
            "card_number": 2,
            "file_path": str(slide_paths[1]),
            "source_ref": "slide-brief.md#Slide 2",
            "visual_description": "Tension interstitial slide",
        },
    ]
    perception_artifacts = [
        {
            "slide_id": "s-1",
            "source_image_path": str(slide_paths[0]),
            "visual_elements": [{"description": "Element 1"}],
        },
        {
            "slide_id": "s-2",
            "source_image_path": str(slide_paths[1]),
            "visual_elements": [{"description": "Element 2"}],
        },
    ]
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=["s-1", "s-2"],
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
        bridge_type_overrides={"seg-02": "pivot"},
        narration_text_overrides={
            "seg-01": " ".join(["headword"] * 100),
            "seg-02": " ".join(["pivotword"] * 30),
        },
        cue_overrides={"seg-01": "headword", "seg-02": "pivotword"},
        include_runtime_rationale_fields=True,
    )
    manifest_path = bundle_dir / "segment-manifest.yaml"
    manifest_data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest_data["segments"][0].update(
        {
            "cluster_id": "c1",
            "cluster_role": "head",
            "cluster_position": "establish",
            "narrative_arc": "From big picture to focused detail",
            "cluster_interstitial_count": 1,
            "master_behavioral_intent": "credible",
        }
    )
    manifest_data["segments"][1].update(
        {
            "cluster_id": "c1",
            "cluster_role": "interstitial",
            "cluster_position": "tension",
            "parent_slide_id": "s-1",
            "interstitial_type": "emphasis-shift",
            "isolation_target": "Element 2",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_path.write_text(yaml.safe_dump(manifest_data, sort_keys=False), encoding="utf-8")
    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=True,
    )

    assert result["status"] == "pass"
    assert not any("spoken_bridge_policy" in warning for warning in result["warnings"])
    assert not any("lacks pivot-class cue" in error for error in result["errors"])


def test_pivot_bridge_does_not_reset_clustered_cadence(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide_ids = [f"s-{index}" for index in range(1, 7)]
    gary_slide_output = []
    perception_artifacts = []
    for index, slide_id in enumerate(slide_ids, start=1):
        slide = bundle_dir / f"slide-{index:02d}.png"
        slide.write_bytes(b"png")
        gary_slide_output.append(
            {
                "slide_id": slide_id,
                "card_number": index,
                "file_path": str(slide),
                "source_ref": f"slide-brief.md#Slide {index}",
                "visual_description": f"Slide {index}",
            }
        )
        perception_artifacts.append(
            {
                "slide_id": slide_id,
                "source_image_path": str(slide),
                "visual_elements": [{"description": f"Element {index}"}],
            }
        )
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=slide_ids,
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
        include_runtime_rationale_fields=True,
        bridge_type_overrides={"seg-03": "pivot"},
        narration_text_overrides={
            "seg-01": " ".join(["headone"] * 100),
            "seg-02": " ".join(["tighttwo"] * 30),
            "seg-03": "However " + " ".join(["tightthree"] * 29),
            "seg-04": " ".join(["tightfour"] * 30),
            "seg-05": " ".join(["tightfive"] * 30),
            "seg-06": " ".join(["tightsix"] * 30),
        },
        cue_overrides={
            "seg-01": "headone",
            "seg-02": "tighttwo",
            "seg-03": "However",
            "seg-04": "tightfour",
            "seg-05": "tightfive",
            "seg-06": "tightsix",
        },
    )
    manifest_path = bundle_dir / "segment-manifest.yaml"
    manifest_data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest_data["segments"][0].update(
        {
            "cluster_id": "c1",
            "cluster_role": "head",
            "cluster_position": "establish",
            "master_behavioral_intent": "credible",
        }
    )
    for index, position in enumerate(["tension", "develop", "resolve", "resolve", "resolve"], start=1):
        manifest_data["segments"][index].update(
            {
                "cluster_id": "c1",
                "cluster_role": "interstitial",
                "cluster_position": position,
                "parent_slide_id": "s-1",
                "interstitial_type": "emphasis-shift",
                "master_behavioral_intent": "credible",
            }
        )
    manifest_path.write_text(yaml.safe_dump(manifest_data, sort_keys=False), encoding="utf-8")
    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    payload["runtime_plan"] = {
        "per_slide_targets": [
            {"card_number": index, "target_runtime_seconds": 40.0}
            for index in range(1, 7)
        ]
    }
    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=True,
    )

    assert result["status"] == "fail"
    assert any("bridge cadence exceeded" in warning for warning in result["warnings"])


def test_cluster_boundary_spoken_cue_is_still_required_in_clustered_mode(
    tmp_path: Path,
) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide_ids = [f"s-{index}" for index in range(1, 5)]
    gary_slide_output = []
    perception_artifacts = []
    for index, slide_id in enumerate(slide_ids, start=1):
        slide = bundle_dir / f"slide-{index:02d}.png"
        slide.write_bytes(b"png")
        gary_slide_output.append(
            {
                "slide_id": slide_id,
                "card_number": index,
                "file_path": str(slide),
                "source_ref": f"slide-brief.md#Slide {index}",
                "visual_description": f"Slide {index}",
            }
        )
        perception_artifacts.append(
            {
                "slide_id": slide_id,
                "source_image_path": str(slide),
                "visual_elements": [{"description": f"Element {index}"}],
            }
        )
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=slide_ids,
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
        include_runtime_rationale_fields=True,
        bridge_type_overrides={"seg-03": "cluster_boundary"},
        narration_text_overrides={
            "seg-01": " ".join(["headone"] * 100),
            "seg-02": " ".join(["tighttwo"] * 30),
            "seg-03": " ".join(["boundary"] * 80),
            "seg-04": " ".join(["tightfour"] * 30),
        },
        cue_overrides={
            "seg-01": "headone",
            "seg-02": "tighttwo",
            "seg-03": "boundary",
            "seg-04": "tightfour",
        },
        disable_spoken_bridge_enrichment=True,
    )
    manifest_path = bundle_dir / "segment-manifest.yaml"
    manifest_data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest_data["segments"][0].update(
        {
            "cluster_id": "c1",
            "cluster_role": "head",
            "cluster_position": "establish",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_data["segments"][1].update(
        {
            "cluster_id": "c1",
            "cluster_role": "interstitial",
            "cluster_position": "tension",
            "parent_slide_id": "s-1",
            "interstitial_type": "reveal",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_data["segments"][2].update(
        {
            "cluster_id": "c2",
            "cluster_role": "head",
            "cluster_position": "establish",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_data["segments"][3].update(
        {
            "cluster_id": "c2",
            "cluster_role": "interstitial",
            "cluster_position": "develop",
            "parent_slide_id": "s-3",
            "interstitial_type": "simplification",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_path.write_text(yaml.safe_dump(manifest_data, sort_keys=False), encoding="utf-8")
    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=True,
    )

    assert any("bridge_type is cluster_boundary" in warning for warning in result["warnings"])
    assert not any("bridge_type is cluster_boundary" in error for error in result["errors"])


def test_cluster_boundary_bridge_resets_cadence_at_cluster_seam(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide_ids = [f"s-{index}" for index in range(1, 5)]
    gary_slide_output = []
    perception_artifacts = []
    for index, slide_id in enumerate(slide_ids, start=1):
        slide = bundle_dir / f"slide-{index:02d}.png"
        slide.write_bytes(b"png")
        gary_slide_output.append(
            {
                "slide_id": slide_id,
                "card_number": index,
                "file_path": str(slide),
                "source_ref": f"slide-brief.md#Slide {index}",
                "visual_description": f"Slide {index}",
            }
        )
        perception_artifacts.append(
            {
                "slide_id": slide_id,
                "source_image_path": str(slide),
                "visual_elements": [{"description": f"Element {index}"}],
            }
        )
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=slide_ids,
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
        include_runtime_rationale_fields=True,
        bridge_type_overrides={"seg-03": "cluster_boundary"},
        narration_text_overrides={
            "seg-01": "tighttwo " + " ".join(["headone"] * 99),
            "seg-02": "tighttwo " + " ".join(["tighttwo"] * 29),
            "seg-03": (
                "In this section we synthesize what the prior cluster established. "
                + "tightfour "
                + " ".join(["boundary"] * 79)
                + " Next, we'll pull that thread into the new topic."
            ),
            "seg-04": "tightfour " + " ".join(["tightfour"] * 29),
        },
        cue_overrides={
            "seg-01": "headone",
            "seg-02": "tighttwo",
            "seg-03": "boundary",
            "seg-04": "tightfour",
        },
    )
    manifest_path = bundle_dir / "segment-manifest.yaml"
    manifest_data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest_data["segments"][0].update(
        {
            "cluster_id": "c1",
            "cluster_role": "head",
            "cluster_position": "establish",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_data["segments"][1].update(
        {
            "cluster_id": "c1",
            "cluster_role": "interstitial",
            "cluster_position": "tension",
            "parent_slide_id": "s-1",
            "interstitial_type": "reveal",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_data["segments"][2].update(
        {
            "cluster_id": "c2",
            "cluster_role": "head",
            "cluster_position": "establish",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_data["segments"][3].update(
        {
            "cluster_id": "c2",
            "cluster_role": "interstitial",
            "cluster_position": "develop",
            "parent_slide_id": "s-3",
            "interstitial_type": "simplification",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_path.write_text(yaml.safe_dump(manifest_data, sort_keys=False), encoding="utf-8")
    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=True,
    )

    assert result["status"] == "pass"
    assert not any(
        "cluster boundary transition should use bridge_type cluster_boundary" in warning
        for warning in result["warnings"]
    )


def test_cluster_boundary_cadence_override_fails_when_boundary_bridge_missing(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide_ids = [f"s-{index}" for index in range(1, 5)]
    gary_slide_output = []
    perception_artifacts = []
    for index, slide_id in enumerate(slide_ids, start=1):
        slide = bundle_dir / f"slide-{index:02d}.png"
        slide.write_bytes(b"png")
        gary_slide_output.append(
            {
                "slide_id": slide_id,
                "card_number": index,
                "file_path": str(slide),
                "source_ref": f"slide-brief.md#Slide {index}",
                "visual_description": f"Slide {index}",
            }
        )
        perception_artifacts.append(
            {
                "slide_id": slide_id,
                "source_image_path": str(slide),
                "visual_elements": [{"description": f"Element {index}"}],
            }
        )
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=slide_ids,
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
        include_runtime_rationale_fields=True,
        narration_text_overrides={
            "seg-01": " ".join(["headone"] * 100),
            "seg-02": " ".join(["tighttwo"] * 30),
            "seg-03": " ".join(["headthree"] * 100),
            "seg-04": " ".join(["tightfour"] * 30),
        },
        cue_overrides={
            "seg-01": "headone",
            "seg-02": "tighttwo",
            "seg-03": "headthree",
            "seg-04": "tightfour",
        },
    )
    manifest_path = bundle_dir / "segment-manifest.yaml"
    manifest_data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest_data["segments"][0].update(
        {"cluster_id": "c1", "cluster_role": "head", "cluster_position": "establish"}
    )
    manifest_data["segments"][1].update(
        {
            "cluster_id": "c1",
            "cluster_role": "interstitial",
            "cluster_position": "tension",
            "parent_slide_id": "s-1",
            "interstitial_type": "reveal",
        }
    )
    manifest_data["segments"][2].update(
        {"cluster_id": "c2", "cluster_role": "head", "cluster_position": "establish"}
    )
    manifest_data["segments"][3].update(
        {
            "cluster_id": "c2",
            "cluster_role": "interstitial",
            "cluster_position": "resolve",
            "parent_slide_id": "s-3",
            "interstitial_type": "simplification",
        }
    )
    manifest_path.write_text(yaml.safe_dump(manifest_data, sort_keys=False), encoding="utf-8")
    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=True,
    )

    assert result["status"] == "fail"
    assert any(
        "runtime_policy_violation:" in error
        and "cluster boundary transition should use bridge_type cluster_boundary" in error
        for error in result["errors"]
    )


def test_cluster_boundary_detection_survives_same_slide_aggregated_flat_record(
    tmp_path: Path,
) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide_ids = [f"s-{index}" for index in range(1, 5)]
    gary_slide_output = []
    perception_artifacts = []
    for index, slide_id in enumerate(slide_ids, start=1):
        slide = bundle_dir / f"slide-{index:02d}.png"
        slide.write_bytes(b"png")
        gary_slide_output.append(
            {
                "slide_id": slide_id,
                "card_number": index,
                "file_path": str(slide),
                "source_ref": f"slide-brief.md#Slide {index}",
                "visual_description": f"Slide {index}",
            }
        )
        perception_artifacts.append(
            {
                "slide_id": slide_id,
                "source_image_path": str(slide),
                "visual_elements": [{"description": f"Element {index}"}],
            }
        )
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=slide_ids,
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
        include_runtime_rationale_fields=True,
        bridge_type_overrides={"seg-03": "cluster_boundary"},
        narration_text_overrides={
            "seg-01": "clusterone " + " ".join(["clusterone"] * 99),
            "seg-02": "clusterone " + " ".join(["clusterone"] * 29),
            "seg-03": (
                "In this section we synthesize what the prior cluster established. "
                + "clustertwo "
                + " ".join(["clustertwo"] * 79)
                + " Next, we'll pull that thread into the new topic."
            ),
            "seg-04": "clustertwo " + " ".join(["clustertwo"] * 29),
        },
        cue_overrides={
            "seg-01": "clusterone",
            "seg-02": "clusterone",
            "seg-03": "clustertwo",
            "seg-04": "clustertwo",
        },
    )
    manifest_path = bundle_dir / "segment-manifest.yaml"
    manifest_data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    aggregated_flat_record = dict(manifest_data["segments"][2])
    aggregated_flat_record.update(
        {
            "id": "seg-03-flat",
            "bridge_type": "none",
            "cluster_id": None,
            "cluster_role": None,
            "cluster_position": None,
            "behavioral_intent": "credible",
        }
    )
    manifest_data["segments"].insert(2, aggregated_flat_record)
    manifest_data["segments"][0].update(
        {
            "cluster_id": "c1",
            "cluster_role": "head",
            "cluster_position": "establish",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_data["segments"][1].update(
        {
            "cluster_id": "c1",
            "cluster_role": "interstitial",
            "cluster_position": "tension",
            "parent_slide_id": "s-1",
            "interstitial_type": "reveal",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_data["segments"][3].update(
        {
            "cluster_id": "c2",
            "cluster_role": "head",
            "cluster_position": "establish",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_data["segments"][4].update(
        {
            "cluster_id": "c2",
            "cluster_role": "interstitial",
            "cluster_position": "develop",
            "parent_slide_id": "s-3",
            "interstitial_type": "simplification",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_path.write_text(yaml.safe_dump(manifest_data, sort_keys=False), encoding="utf-8")
    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=True,
    )

    assert result["status"] == "pass"
    assert not any(
        "cluster boundary transition should use bridge_type cluster_boundary" in warning
        for warning in result["warnings"]
    )


def test_mixed_flat_and_clustered_segments_do_not_treat_cluster_edges_as_seams(
    tmp_path: Path,
) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide_ids = [f"s-{index}" for index in range(1, 5)]
    gary_slide_output = []
    perception_artifacts = []
    for index, slide_id in enumerate(slide_ids, start=1):
        slide = bundle_dir / f"slide-{index:02d}.png"
        slide.write_bytes(b"png")
        gary_slide_output.append(
            {
                "slide_id": slide_id,
                "card_number": index,
                "file_path": str(slide),
                "source_ref": f"slide-brief.md#Slide {index}",
                "visual_description": f"Slide {index}",
            }
        )
        perception_artifacts.append(
            {
                "slide_id": slide_id,
                "source_image_path": str(slide),
                "visual_elements": [{"description": f"Element {index}"}],
            }
        )
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=slide_ids,
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
        include_runtime_rationale_fields=True,
        bridge_type_overrides={"seg-01": "intro"},
        narration_text_overrides={
            "seg-02": " ".join(["clusterhead"] * 100),
            "seg-03": " ".join(["clusterhead"] * 30),
        },
        cue_overrides={
            "seg-02": "clusterhead",
            "seg-03": "clusterhead",
        },
    )
    manifest_path = bundle_dir / "segment-manifest.yaml"
    manifest_data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest_data["segments"][1].update(
        {
            "cluster_id": "c1",
            "cluster_role": "head",
            "cluster_position": "establish",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_data["segments"][2].update(
        {
            "cluster_id": "c1",
            "cluster_role": "interstitial",
            "cluster_position": "tension",
            "parent_slide_id": "s-2",
            "interstitial_type": "reveal",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_path.write_text(yaml.safe_dump(manifest_data, sort_keys=False), encoding="utf-8")
    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=True,
    )

    assert result["status"] == "pass"
    assert not any("cluster boundary transition should use bridge_type cluster_boundary" in warning for warning in result["warnings"])
    assert not any("cluster boundary transition should use bridge_type cluster_boundary" in error for error in result["errors"])


def test_clustered_head_intro_does_not_reset_cadence_before_fallback_due(
    tmp_path: Path,
) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide_ids = [f"s-{index}" for index in range(1, 9)]
    gary_slide_output = []
    perception_artifacts = []
    for index, slide_id in enumerate(slide_ids, start=1):
        slide = bundle_dir / f"slide-{index:02d}.png"
        slide.write_bytes(b"png")
        gary_slide_output.append(
            {
                "slide_id": slide_id,
                "card_number": index,
                "file_path": str(slide),
                "source_ref": f"slide-brief.md#Slide {index}",
                "visual_description": f"Slide {index}",
            }
        )
        perception_artifacts.append(
            {
                "slide_id": slide_id,
                "source_image_path": str(slide),
                "visual_elements": [{"description": f"Element {index}"}],
            }
        )
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=slide_ids,
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
        include_runtime_rationale_fields=True,
        bridge_type_overrides={"seg-03": "intro"},
        narration_text_overrides={
            "seg-01": " ".join(["clusterone"] * 100),
            "seg-02": " ".join(["clusterone"] * 30),
            "seg-03": " ".join(["clustertwo"] * 100),
            "seg-04": " ".join(["clustertwo"] * 30),
            "seg-05": " ".join(["clustertwo"] * 30),
            "seg-06": " ".join(["clustertwo"] * 30),
            "seg-07": " ".join(["clustertwo"] * 30),
            "seg-08": " ".join(["clustertwo"] * 30),
        },
        cue_overrides={
            "seg-01": "clusterone",
            "seg-02": "clusterone",
            "seg-03": "clustertwo",
            "seg-04": "clustertwo",
            "seg-05": "clustertwo",
            "seg-06": "clustertwo",
            "seg-07": "clustertwo",
            "seg-08": "clustertwo",
        },
    )
    manifest_path = bundle_dir / "segment-manifest.yaml"
    manifest_data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest_data["segments"][0].update(
        {
            "cluster_id": "c1",
            "cluster_role": "head",
            "cluster_position": "establish",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_data["segments"][1].update(
        {
            "cluster_id": "c1",
            "cluster_role": "interstitial",
            "cluster_position": "tension",
            "parent_slide_id": "s-1",
            "interstitial_type": "reveal",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_data["segments"][2].update(
        {
            "cluster_id": "c2",
            "cluster_role": "head",
            "cluster_position": "establish",
            "master_behavioral_intent": "credible",
        }
    )
    for seg_index, position in zip(range(3, 8), ["tension", "develop", "resolve", "resolve", "resolve"], strict=False):
        manifest_data["segments"][seg_index].update(
            {
                "cluster_id": "c2",
                "cluster_role": "interstitial",
                "cluster_position": position,
                "parent_slide_id": "s-3",
                "interstitial_type": "simplification",
                "master_behavioral_intent": "credible",
            }
        )
    manifest_path.write_text(yaml.safe_dump(manifest_data, sort_keys=False), encoding="utf-8")
    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    payload["runtime_plan"] = {
        "per_slide_targets": [
            {"card_number": index, "target_runtime_seconds": 40.0}
            for index in range(1, 9)
        ]
    }
    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=True,
    )

    assert result["status"] == "fail"
    assert any(
        warning.startswith("seg-06: explicit intro/outro bridge cadence exceeded")
        for warning in result["warnings"]
    )


def test_cluster_behavioral_intent_must_serve_master_behavioral_intent(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    card_1 = bundle_dir / "card-01.png"
    card_2 = bundle_dir / "card-02.png"
    card_1.write_bytes(b"png")
    card_2.write_bytes(b"png")

    payload = {
        "gary_slide_output": [
            {"slide_id": "s-1", "card_number": 1, "file_path": str(card_1), "source_ref": "slide-1"},
            {"slide_id": "s-2", "card_number": 2, "file_path": str(card_2), "source_ref": "slide-2"},
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": str(card_1),
                "visual_elements": [{"description": "Element 1"}],
            },
            {
                "slide_id": "s-2",
                "source_image_path": str(card_2),
                "visual_elements": [{"description": "Element 2"}],
            },
        ],
    }
    payload.update(
        _write_complete_bundle_outputs(
            bundle_dir,
            slide_ids=["s-1", "s-2"],
            gary_slide_output=payload["gary_slide_output"],  # type: ignore[arg-type]
            perception_artifacts=payload["perception_artifacts"],  # type: ignore[arg-type]
            narration_text_overrides={
                "seg-01": " ".join(["headword"] * 100),
                "seg-02": "However " + " ".join(["detail"] * 29),
            },
            cue_overrides={"seg-01": "headword", "seg-02": "However"},
            script_behavioral_intent_overrides={"seg-02": "provocative"},
            manifest_behavioral_intent_overrides={"seg-02": "provocative"},
            include_runtime_rationale_fields=True,
            bridge_type_overrides={"seg-02": "pivot"},
        )
    )

    manifest_path = bundle_dir / "segment-manifest.yaml"
    manifest_data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest_data["segments"][0].update(
        {
            "cluster_id": "c1",
            "cluster_role": "head",
            "cluster_position": "establish",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_data["segments"][1].update(
        {
            "cluster_id": "c1",
            "cluster_role": "interstitial",
            "cluster_position": "tension",
            "parent_slide_id": "s-1",
            "interstitial_type": "emphasis-shift",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_path.write_text(yaml.safe_dump(manifest_data, sort_keys=False), encoding="utf-8")

    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(payload, envelope_path=envelope_path)

    assert result["status"] == "fail"
    assert result["pass2_outputs"]["segments_with_behavioral_intent_mismatch"] == []
    assert result["pass2_outputs"]["segments_with_master_behavioral_intent_violation"] == [
        "seg-02(provocative->credible)"
    ]


def test_cluster_behavioral_intent_allows_documented_subordinate_combination(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    card_1 = bundle_dir / "card-01.png"
    card_2 = bundle_dir / "card-02.png"
    card_1.write_bytes(b"png")
    card_2.write_bytes(b"png")

    payload = {
        "gary_slide_output": [
            {"slide_id": "s-1", "card_number": 1, "file_path": str(card_1), "source_ref": "slide-1"},
            {"slide_id": "s-2", "card_number": 2, "file_path": str(card_2), "source_ref": "slide-2"},
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": str(card_1),
                "visual_elements": [{"description": "Element 1"}],
            },
            {
                "slide_id": "s-2",
                "source_image_path": str(card_2),
                "visual_elements": [{"description": "Element 2"}],
            },
        ],
    }
    payload.update(
        _write_complete_bundle_outputs(
            bundle_dir,
            slide_ids=["s-1", "s-2"],
            gary_slide_output=payload["gary_slide_output"],  # type: ignore[arg-type]
            perception_artifacts=payload["perception_artifacts"],  # type: ignore[arg-type]
            narration_text_overrides={
                "seg-01": " ".join(["headword"] * 100),
                "seg-02": "However " + " ".join(["detail"] * 29),
            },
            cue_overrides={"seg-01": "headword", "seg-02": "However"},
            script_behavioral_intent_overrides={"seg-02": "alarming"},
            manifest_behavioral_intent_overrides={"seg-02": "alarming"},
            include_runtime_rationale_fields=True,
            bridge_type_overrides={"seg-02": "pivot"},
        )
    )

    manifest_path = bundle_dir / "segment-manifest.yaml"
    manifest_data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest_data["segments"][0].update(
        {
            "cluster_id": "c1",
            "cluster_role": "head",
            "cluster_position": "establish",
            "master_behavioral_intent": "clear-guidance",
        }
    )
    manifest_data["segments"][1].update(
        {
            "cluster_id": "c1",
            "cluster_role": "interstitial",
            "cluster_position": "tension",
            "parent_slide_id": "s-1",
            "interstitial_type": "emphasis-shift",
            "master_behavioral_intent": "clear-guidance",
        }
    )
    manifest_path.write_text(yaml.safe_dump(manifest_data, sort_keys=False), encoding="utf-8")

    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(payload, envelope_path=envelope_path)

    assert result["status"] == "pass"
    assert result["pass2_outputs"]["segments_with_behavioral_intent_mismatch"] == []
    assert result["pass2_outputs"]["segments_with_master_behavioral_intent_violation"] == []


def test_cluster_behavioral_intent_uses_head_master_when_interstitial_master_is_omitted(
    tmp_path: Path,
) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    card_1 = bundle_dir / "card-01.png"
    card_2 = bundle_dir / "card-02.png"
    card_1.write_bytes(b"png")
    card_2.write_bytes(b"png")

    payload = {
        "gary_slide_output": [
            {"slide_id": "s-1", "card_number": 1, "file_path": str(card_1), "source_ref": "slide-1"},
            {"slide_id": "s-2", "card_number": 2, "file_path": str(card_2), "source_ref": "slide-2"},
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": str(card_1),
                "visual_elements": [{"description": "Element 1"}],
            },
            {
                "slide_id": "s-2",
                "source_image_path": str(card_2),
                "visual_elements": [{"description": "Element 2"}],
            },
        ],
    }
    payload.update(
        _write_complete_bundle_outputs(
            bundle_dir,
            slide_ids=["s-1", "s-2"],
            gary_slide_output=payload["gary_slide_output"],  # type: ignore[arg-type]
            perception_artifacts=payload["perception_artifacts"],  # type: ignore[arg-type]
            narration_text_overrides={
                "seg-01": " ".join(["headword"] * 100),
                "seg-02": "However " + " ".join(["detail"] * 29),
            },
            cue_overrides={"seg-01": "headword", "seg-02": "However"},
            script_behavioral_intent_overrides={"seg-02": "provocative"},
            manifest_behavioral_intent_overrides={"seg-02": "provocative"},
            include_runtime_rationale_fields=True,
            bridge_type_overrides={"seg-02": "pivot"},
        )
    )

    manifest_path = bundle_dir / "segment-manifest.yaml"
    manifest_data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest_data["segments"][0].update(
        {
            "cluster_id": "c1",
            "cluster_role": "head",
            "cluster_position": "establish",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_data["segments"][1].update(
        {
            "cluster_id": "c1",
            "cluster_role": "interstitial",
            "cluster_position": "tension",
            "parent_slide_id": "s-1",
            "interstitial_type": "emphasis-shift",
            "master_behavioral_intent": None,
        }
    )
    manifest_path.write_text(yaml.safe_dump(manifest_data, sort_keys=False), encoding="utf-8")

    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(payload, envelope_path=envelope_path)

    assert result["status"] == "fail"
    assert result["pass2_outputs"]["segments_with_master_behavioral_intent_violation"] == [
        "seg-02(provocative->credible)"
    ]


def test_cluster_behavioral_intent_does_not_fail_head_only_mismatch(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    card_1 = bundle_dir / "card-01.png"
    card_2 = bundle_dir / "card-02.png"
    card_1.write_bytes(b"png")
    card_2.write_bytes(b"png")

    payload = {
        "gary_slide_output": [
            {"slide_id": "s-1", "card_number": 1, "file_path": str(card_1), "source_ref": "slide-1"},
            {"slide_id": "s-2", "card_number": 2, "file_path": str(card_2), "source_ref": "slide-2"},
        ],
        "perception_artifacts": [
            {
                "slide_id": "s-1",
                "source_image_path": str(card_1),
                "visual_elements": [{"description": "Element 1"}],
            },
            {
                "slide_id": "s-2",
                "source_image_path": str(card_2),
                "visual_elements": [{"description": "Element 2"}],
            },
        ],
    }
    payload.update(
        _write_complete_bundle_outputs(
            bundle_dir,
            slide_ids=["s-1", "s-2"],
            gary_slide_output=payload["gary_slide_output"],  # type: ignore[arg-type]
            perception_artifacts=payload["perception_artifacts"],  # type: ignore[arg-type]
            narration_text_overrides={
                "seg-01": " ".join(["headword"] * 100),
                "seg-02": "However " + " ".join(["detail"] * 29),
            },
            cue_overrides={"seg-01": "headword", "seg-02": "However"},
            script_behavioral_intent_overrides={"seg-01": "provocative", "seg-02": "credible"},
            manifest_behavioral_intent_overrides={"seg-01": "provocative", "seg-02": "credible"},
            include_runtime_rationale_fields=True,
            bridge_type_overrides={"seg-02": "pivot"},
        )
    )

    manifest_path = bundle_dir / "segment-manifest.yaml"
    manifest_data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest_data["segments"][0].update(
        {
            "cluster_id": "c1",
            "cluster_role": "head",
            "cluster_position": "establish",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_data["segments"][1].update(
        {
            "cluster_id": "c1",
            "cluster_role": "interstitial",
            "cluster_position": "tension",
            "parent_slide_id": "s-1",
            "interstitial_type": "emphasis-shift",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_path.write_text(yaml.safe_dump(manifest_data, sort_keys=False), encoding="utf-8")

    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(payload, envelope_path=envelope_path)

    assert result["status"] == "pass"
    assert result["pass2_outputs"]["segments_with_master_behavioral_intent_violation"] == []


def test_cluster_word_budget_allows_plus_minus_five_tolerance(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide_paths = [bundle_dir / "slide-01.png", bundle_dir / "slide-02.png", bundle_dir / "slide-03.png"]
    for slide_path in slide_paths:
        slide_path.write_bytes(b"png")
    gary_slide_output = [
        {
            "slide_id": "s-1",
            "card_number": 1,
            "file_path": str(slide_paths[0]),
            "source_ref": "slide-brief.md#Slide 1",
            "visual_description": "Head slide",
        },
        {
            "slide_id": "s-2",
            "card_number": 2,
            "file_path": str(slide_paths[1]),
            "source_ref": "slide-brief.md#Slide 2",
            "visual_description": "Develop interstitial slide",
        },
        {
            "slide_id": "s-3",
            "card_number": 3,
            "file_path": str(slide_paths[2]),
            "source_ref": "slide-brief.md#Slide 3",
            "visual_description": "Resolve interstitial slide",
        },
    ]
    perception_artifacts = [
        {
            "slide_id": "s-1",
            "source_image_path": str(slide_paths[0]),
            "visual_elements": [{"description": "Element 1"}],
        },
        {
            "slide_id": "s-2",
            "source_image_path": str(slide_paths[1]),
            "visual_elements": [{"description": "Element 2"}],
        },
        {
            "slide_id": "s-3",
            "source_image_path": str(slide_paths[2]),
            "visual_elements": [{"description": "Element 3"}],
        },
    ]
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=["s-1", "s-2", "s-3"],
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
        narration_text_overrides={
            "seg-01": "signal evidence pattern " + " ".join(["headword"] * 76),
            "seg-02": "signal evidence pattern " + " ".join(["detail"] * 38),
            "seg-03": "signal evidence pattern " + " ".join(["detail"] * 27),
        },
        cue_overrides={"seg-01": "headword", "seg-02": "signal", "seg-03": "signal"},
        include_runtime_rationale_fields=True,
    )
    manifest_path = bundle_dir / "segment-manifest.yaml"
    manifest_data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest_data["segments"][0].update(
        {
            "cluster_id": "c1",
            "cluster_role": "head",
            "cluster_position": "establish",
            "narrative_arc": "From confusion to clarity through guided comparison",
            "cluster_interstitial_count": 1,
            "master_behavioral_intent": "credible",
        }
    )
    manifest_data["segments"][1].update(
        {
            "cluster_id": "c1",
            "cluster_role": "interstitial",
            "cluster_position": "develop",
            "parent_slide_id": "s-1",
            "interstitial_type": "emphasis-shift",
            "isolation_target": "Element 2",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_data["segments"][2].update(
        {
            "cluster_id": "c1",
            "cluster_role": "interstitial",
            "cluster_position": "resolve",
            "parent_slide_id": "s-1",
            "interstitial_type": "emphasis-shift",
            "isolation_target": "Element 3",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_path.write_text(yaml.safe_dump(manifest_data, sort_keys=False), encoding="utf-8")
    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=True,
    )

    assert result["status"] == "pass"
    assert result["pass2_outputs"]["cluster_word_range_warnings"] == []


def test_cluster_interstitial_rejects_new_concepts_outside_head_scope(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide_paths = [bundle_dir / "slide-01.png", bundle_dir / "slide-02.png"]
    for slide_path in slide_paths:
        slide_path.write_bytes(b"png")
    slide_brief = bundle_dir / "slide-brief.md"
    slide_brief.write_text(
        "# Slide 1\nHeart rhythm changes and oxygen delivery shape the main explanation.\n",
        encoding="utf-8",
    )
    gary_slide_output = [
        {
            "slide_id": "s-1",
            "card_number": 1,
            "file_path": str(slide_paths[0]),
            "source_ref": str(slide_brief) + "#Slide 1",
            "visual_description": "Head slide",
        },
        {
            "slide_id": "s-2",
            "card_number": 2,
            "file_path": str(slide_paths[1]),
            "source_ref": str(slide_brief) + "#Slide 2",
            "visual_description": "Develop interstitial slide",
        },
    ]
    perception_artifacts = [
        {
            "slide_id": "s-1",
            "source_image_path": str(slide_paths[0]),
            "visual_elements": [{"description": "Element 1"}],
        },
        {
            "slide_id": "s-2",
            "source_image_path": str(slide_paths[1]),
            "visual_elements": [{"description": "Element 2"}],
        },
    ]
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=["s-1", "s-2"],
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
        narration_text_overrides={
            "seg-01": "heart rhythm oxygen delivery " + " ".join(["headword"] * 97),
            "seg-02": "heart rhythm enzyme cascade " + " ".join(["detail"] * 27),
        },
        cue_overrides={"seg-01": "heart", "seg-02": "heart"},
        include_runtime_rationale_fields=True,
    )
    manifest_path = bundle_dir / "segment-manifest.yaml"
    manifest_data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest_data["segments"][0].update(
        {
            "cluster_id": "c1",
            "cluster_role": "head",
            "cluster_position": "establish",
            "narrative_arc": "From rhythm awareness to stable interpretation through guided comparison",
            "cluster_interstitial_count": 1,
            "master_behavioral_intent": "credible",
        }
    )
    manifest_data["segments"][1].update(
        {
            "cluster_id": "c1",
            "cluster_role": "interstitial",
            "cluster_position": "resolve",
            "parent_slide_id": "s-1",
            "interstitial_type": "emphasis-shift",
            "isolation_target": "Element 2",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_path.write_text(yaml.safe_dump(manifest_data, sort_keys=False), encoding="utf-8")
    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=True,
    )

    assert not any("new concept" in error for error in result["errors"])
    assert any(
        "enzyme" in warning for warning in result["warnings"]
    )


def test_cluster_arc_integrity_fails_when_resolve_has_no_establish_callback(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    slide_paths = [bundle_dir / "slide-01.png", bundle_dir / "slide-02.png", bundle_dir / "slide-03.png"]
    for slide_path in slide_paths:
        slide_path.write_bytes(b"png")
    gary_slide_output = [
        {
            "slide_id": "s-1",
            "card_number": 1,
            "file_path": str(slide_paths[0]),
            "source_ref": "slide-brief.md#Slide 1",
            "visual_description": "Head slide",
        },
        {
            "slide_id": "s-2",
            "card_number": 2,
            "file_path": str(slide_paths[1]),
            "source_ref": "slide-brief.md#Slide 2",
            "visual_description": "Develop interstitial slide",
        },
        {
            "slide_id": "s-3",
            "card_number": 3,
            "file_path": str(slide_paths[2]),
            "source_ref": "slide-brief.md#Slide 3",
            "visual_description": "Resolve interstitial slide",
        },
    ]
    perception_artifacts = [
        {
            "slide_id": "s-1",
            "source_image_path": str(slide_paths[0]),
            "visual_elements": [{"description": "Element 1"}],
        },
        {
            "slide_id": "s-2",
            "source_image_path": str(slide_paths[1]),
            "visual_elements": [{"description": "Element 2"}],
        },
        {
            "slide_id": "s-3",
            "source_image_path": str(slide_paths[2]),
            "visual_elements": [{"description": "Element 3"}],
        },
    ]
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=["s-1", "s-2", "s-3"],
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
        narration_text_overrides={
            "seg-01": "signal pattern evidence " + " ".join(["headword"] * 97),
            "seg-02": "signal pattern evidence " + " ".join(["detail"] * 27),
            "seg-03": "enzyme cascade metabolism " + " ".join(["detail"] * 27),
        },
        cue_overrides={"seg-01": "signal", "seg-02": "signal", "seg-03": "enzyme"},
        include_runtime_rationale_fields=True,
    )
    manifest_path = bundle_dir / "segment-manifest.yaml"
    manifest_data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest_data["segments"][0].update(
        {
            "cluster_id": "c1",
            "cluster_role": "head",
            "cluster_position": "establish",
            "narrative_arc": "From signal recognition to evidence-based closure through guided synthesis",
            "cluster_interstitial_count": 1,
            "master_behavioral_intent": "credible",
        }
    )
    manifest_data["segments"][1].update(
        {
            "cluster_id": "c1",
            "cluster_role": "interstitial",
            "cluster_position": "develop",
            "parent_slide_id": "s-1",
            "interstitial_type": "emphasis-shift",
            "isolation_target": "Element 2",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_data["segments"][2].update(
        {
            "cluster_id": "c1",
            "cluster_role": "interstitial",
            "cluster_position": "resolve",
            "parent_slide_id": "s-1",
            "interstitial_type": "emphasis-shift",
            "isolation_target": "Element 3",
            "master_behavioral_intent": "credible",
        }
    )
    manifest_path.write_text(yaml.safe_dump(manifest_data, sort_keys=False), encoding="utf-8")
    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=True,
    )

    assert result["status"] == "fail"
    assert any(
        "arc integrity" in error and "callback" in error
        for error in result["errors"]
    )


def test_runtime_timing_buffer_fields_fail_when_negative_in_strict_mode(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir(parents=True)
    slide_ids = ["s-1"]
    slide_png = bundle_dir / "slide-01.png"
    slide_png.write_bytes(b"png")
    gary_slide_output = [
        {
            "slide_id": "s-1",
            "card_number": 1,
            "file_path": str(slide_png),
            "source_ref": "slide-brief.md#Slide 1",
            "visual_description": "Slide 1",
        }
    ]
    perception_artifacts = [
        {
            "slide_id": "s-1",
            "source_image_path": str(slide_png),
            "visual_elements": [{"description": "Element 1"}],
        }
    ]
    payload = _write_complete_bundle_outputs(
        bundle_dir,
        slide_ids=slide_ids,
        gary_slide_output=gary_slide_output,
        perception_artifacts=perception_artifacts,
        include_runtime_rationale_fields=True,
        runtime_rationale_overrides={
            "seg-01": {
                "onset_delay": -0.5,
            }
        },
    )
    payload["gary_slide_output"] = gary_slide_output
    payload["perception_artifacts"] = perception_artifacts
    envelope_path = bundle_dir / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(
        payload,
        envelope_path=envelope_path,
        runtime_policy_strict=True,
    )

    assert result["status"] == "fail"
    assert any("onset_delay(>=0)" in warning for warning in result["warnings"])
    assert any(
        "runtime_policy_violation:" in error and "onset_delay(>=0)" in error
        for error in result["errors"]
    )
