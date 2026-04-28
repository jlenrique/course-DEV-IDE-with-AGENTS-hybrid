from __future__ import annotations

import json
from importlib import util
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from app.specialists.irene.authoring.pass_2_template import IrenePass2AuthoringEnvelope

ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = (
    ROOT.parent
    / "skills"
    / "bmad-agent-marcus"
    / "scripts"
    / "validate-irene-pass2-handoff.py"
)
GOLDEN = ROOT / "fixtures" / "specialists" / "irene" / "pass_2_template_golden.json"


def _load_validator():
    spec = util.spec_from_file_location("validate_irene_pass2_handoff_module", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate_irene_pass2_handoff


validate_irene_pass2_handoff = _load_validator()


def _write_oracle_bundle(
    tmp_path: Path,
    *,
    cue_in_text: bool = True,
    script_behavioral_intent: str = "credible",
    manifest_behavioral_intent: str = "credible",
    trace_source: str = "slide-01",
    include_trace_source_perception: bool = False,
    include_motion_segment: bool = False,
) -> dict[str, object]:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    slide = bundle / "slide-01.png"
    slide.write_bytes(b"png")
    motion = bundle / "slide-01-motion.mp4"
    if include_motion_segment:
        motion.write_bytes(b"mp4")
    cue = "clinician at the workstation"
    narration = (
        f"Notice the {cue} as the systems signal appears."
        if cue_in_text
        else "Notice the systems signal as the visual context appears."
    )
    gary = [
        {
            "slide_id": "slide-01",
            "card_number": 1,
            "file_path": str(slide),
            "source_ref": "slide-brief.md#Slide 1",
        }
    ]
    perception = [
        {
            "slide_id": "slide-01",
            "source_image_path": str(slide),
            "visual_elements": [{"description": "Clinician at workstation"}],
        }
    ]
    if include_trace_source_perception:
        perception.append(
            {
                "slide_id": trace_source,
                "source_image_path": str(slide),
                "visual_elements": [{"description": "Clinician at workstation"}],
            }
        )
    segments = [
        {
            "id": "seg-01",
            "gary_slide_id": "slide-01",
            "slide_id": "slide-01",
            "gary_card_number": 1,
            "card_number": 1,
            "narration_text": narration,
            "behavioral_intent": manifest_behavioral_intent,
            "visual_file": str(slide),
            "visual_detail_load": "medium",
            "timing_role": "concept-build",
            "content_density": "medium",
            "duration_rationale": (
                "Medium density needs guided explanation because the visual burden is moderate "
                "and the purpose is concept-building."
            ),
            "bridge_type": "none",
            "visual_references": [
                {
                    "element": "Clinician at workstation",
                    "location_on_slide": "center",
                    "narration_cue": cue,
                    "perception_source": trace_source,
                }
            ],
        }
    ]
    if include_motion_segment:
        segments[0].update(
            {
                "motion_type": "video",
                "visual_mode": "video",
                "motion_asset_path": str(motion),
                "motion_status": "approved",
            }
        )
        (bundle / "motion_plan.yaml").write_text(
            yaml.safe_dump(
                {
                    "slides": [
                        {
                            "slide_id": "slide-01",
                            "motion_asset_path": str(motion),
                            "motion_status": "approved",
                        }
                    ]
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )
    (bundle / "narration-script.md").write_text(
        "\n".join(
            [
                "# Narration Script",
                "",
                "[SEGMENT: seg-01]",
                "",
                "**Stage Directions:**",
                f"- Behavioral Intent: {script_behavioral_intent}",
                "",
                "**Narration:**",
                narration,
                "",
            ]
        ),
        encoding="utf-8",
    )
    (bundle / "segment-manifest.yaml").write_text(
        yaml.safe_dump({"segments": segments}, sort_keys=False),
        encoding="utf-8",
    )
    (bundle / "perception-artifacts.json").write_text(json.dumps(perception), encoding="utf-8")
    (bundle / "authorized-storyboard.json").write_text(
        json.dumps({"slide_ids": ["slide-01"], "authorized_slides": gary}),
        encoding="utf-8",
    )
    payload: dict[str, object] = {
        "bundle_path": str(bundle),
        "authorized_storyboard_path": str(bundle / "authorized-storyboard.json"),
        "expected_outputs": [
            str(bundle / "narration-script.md"),
            str(bundle / "segment-manifest.yaml"),
            str(bundle / "perception-artifacts.json"),
        ],
        "gary_slide_output": gary,
        "perception_artifacts": perception,
    }
    if include_motion_segment:
        payload["motion_plan_path"] = str(bundle / "motion_plan.yaml")
        payload["motion_perception_artifacts"] = []
    return payload


def _write_cluster_bundle(
    tmp_path: Path,
    *,
    bridge_failure: bool = False,
    arc_failure: bool = False,
) -> dict[str, object]:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    slide_paths = []
    for index in range(1, 4):
        path = bundle / f"slide-0{index}.png"
        path.write_bytes(b"png")
        slide_paths.append(path)
    gary = [
        {
            "slide_id": f"slide-0{index}",
            "card_number": index,
            "file_path": str(slide_paths[index - 1]),
            "source_ref": f"slide-brief.md#Slide {index}",
        }
        for index in range(1, 4)
    ]
    perception = [
        {
            "slide_id": f"slide-0{index}",
            "source_image_path": str(slide_paths[index - 1]),
            "visual_elements": [{"description": f"Cluster visual {index}"}],
        }
        for index in range(1, 4)
    ]
    cluster_positions = ["establish", "resolve" if arc_failure else "develop", "resolve"]
    cluster_roles = ["head", "interstitial", "interstitial"]
    cluster_ids = ["c1", "c1", "c2" if bridge_failure else "c1"]
    bridge_types = ["none", "none", "none" if bridge_failure else "cluster_boundary"]
    segments = []
    script_lines = ["# Narration Script", ""]
    for index in range(1, 4):
        seg_id = f"seg-0{index}"
        cue = f"Cluster visual {index}"
        narration = (
            f"In this section, {cue} returns to clinician systems and next, we'll connect it."
            if bridge_types[index - 1] == "cluster_boundary"
            else f"Notice the {cue} as clinician systems develop."
        )
        segments.append(
            {
                "id": seg_id,
                "gary_slide_id": f"slide-0{index}",
                "slide_id": f"slide-0{index}",
                "gary_card_number": index,
                "card_number": index,
                "narration_text": narration,
                "behavioral_intent": "credible",
                "master_behavioral_intent": "credible",
                "visual_file": str(slide_paths[index - 1]),
                "visual_detail_load": "medium",
                "timing_role": "concept-build",
                "content_density": "medium",
                "duration_rationale": "Medium density supports visual concept development.",
                "bridge_type": bridge_types[index - 1],
                "cluster_id": cluster_ids[index - 1],
                "cluster_role": cluster_roles[index - 1],
                "cluster_position": cluster_positions[index - 1],
                "visual_references": [
                    {
                        "element": cue,
                        "location_on_slide": "center",
                        "narration_cue": cue,
                        "perception_source": f"slide-0{index}",
                    }
                ],
            }
        )
        script_lines.extend(
            [
                f"[SEGMENT: {seg_id}]",
                "",
                "**Stage Directions:**",
                "- Behavioral Intent: credible",
                "",
                "**Narration:**",
                narration,
                "",
            ]
        )
    (bundle / "narration-script.md").write_text("\n".join(script_lines), encoding="utf-8")
    (bundle / "segment-manifest.yaml").write_text(
        yaml.safe_dump({"segments": segments}, sort_keys=False),
        encoding="utf-8",
    )
    (bundle / "perception-artifacts.json").write_text(json.dumps(perception), encoding="utf-8")
    (bundle / "authorized-storyboard.json").write_text(
        json.dumps({"slide_ids": ["slide-01", "slide-02", "slide-03"], "authorized_slides": gary}),
        encoding="utf-8",
    )
    return {
        "bundle_path": str(bundle),
        "authorized_storyboard_path": str(bundle / "authorized-storyboard.json"),
        "expected_outputs": [
            str(bundle / "narration-script.md"),
            str(bundle / "segment-manifest.yaml"),
            str(bundle / "perception-artifacts.json"),
        ],
        "gary_slide_output": gary,
        "perception_artifacts": perception,
    }


def test_validator_oracle_alignment_full(tmp_path: Path) -> None:
    payload = _write_oracle_bundle(tmp_path)
    envelope_path = tmp_path / "bundle" / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(payload, envelope_path=envelope_path)

    assert result["status"] == "pass"
    assert result["pass2_outputs"]["segments_missing_visual_narration_cue"] == []
    assert result["pass2_outputs"]["segments_with_behavioral_intent_mismatch"] == []


def test_schema_valid_but_procedural_rejected_narration_cue(tmp_path: Path) -> None:
    payload = _write_oracle_bundle(tmp_path, cue_in_text=False)
    authoring = json.loads(GOLDEN.read_text(encoding="utf-8"))
    IrenePass2AuthoringEnvelope.model_validate(authoring)
    envelope_path = tmp_path / "bundle" / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(payload, envelope_path=envelope_path)

    assert result["status"] == "fail"
    assert any("visual narration_cue" in error for error in result["errors"])


@pytest.mark.parametrize(
    ("rule_name", "payload_factory", "expected_error"),
    [
        (
            "behavioral_intent_parity",
            lambda path: _write_oracle_bundle(
                path,
                script_behavioral_intent="credible",
                manifest_behavioral_intent="reflective",
            ),
            "behavioral_intent",
        ),
        (
            "bridge_cadence",
            lambda path: _write_cluster_bundle(path, bridge_failure=True),
            "bridge_type cluster_boundary",
        ),
        (
            "cluster_arc_continuity",
            lambda path: _write_cluster_bundle(path, arc_failure=True),
            "cluster arc integrity",
        ),
        (
            "motion_perception_confirmation",
            lambda path: _write_oracle_bundle(path, include_motion_segment=True),
            "motion perception confirmation",
        ),
        (
            "narration_cue_presence",
            lambda path: _write_oracle_bundle(path, cue_in_text=False),
            "visual narration_cue",
        ),
        (
            "traceable_visual_references",
            lambda path: _write_oracle_bundle(
                path,
                trace_source="slide-02",
                include_trace_source_perception=True,
            ),
            "visual narration cues",
        ),
    ],
)
def test_validator_oracle_alignment_parametrized_by_rule(
    tmp_path: Path,
    rule_name: str,
    payload_factory,
    expected_error: str,
) -> None:
    authoring = json.loads(GOLDEN.read_text(encoding="utf-8"))
    model = IrenePass2AuthoringEnvelope.model_validate(authoring)
    assert rule_name in model.procedural_rules
    payload = payload_factory(tmp_path)
    envelope_path = Path(str(payload["bundle_path"])) / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(payload, envelope_path=envelope_path)

    assert result["status"] == "fail", rule_name
    assert any(expected_error in error for error in result["errors"])


def test_schema_valid_but_procedural_rejected_bridge_cadence(tmp_path: Path) -> None:
    payload = _write_cluster_bundle(tmp_path, bridge_failure=True)
    authoring = json.loads(GOLDEN.read_text(encoding="utf-8"))
    IrenePass2AuthoringEnvelope.model_validate(authoring)
    envelope_path = Path(str(payload["bundle_path"])) / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(payload, envelope_path=envelope_path)

    assert result["status"] == "fail"
    assert any("bridge_type cluster_boundary" in error for error in result["errors"])


def test_schema_valid_but_procedural_rejected_cluster_arc(tmp_path: Path) -> None:
    payload = _write_cluster_bundle(tmp_path, arc_failure=True)
    authoring = json.loads(GOLDEN.read_text(encoding="utf-8"))
    IrenePass2AuthoringEnvelope.model_validate(authoring)
    envelope_path = Path(str(payload["bundle_path"])) / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(payload, envelope_path=envelope_path)

    assert result["status"] == "fail"
    assert any("cluster arc integrity" in error for error in result["errors"])


def test_authoring_schema_catches_structural_rule_before_oracle(tmp_path: Path) -> None:
    authoring = json.loads(GOLDEN.read_text(encoding="utf-8"))
    authoring["gary_slide_output"][0]["file_path"] = "https://example.com/slide.png"

    with pytest.raises(ValidationError, match="must not be remote"):
        IrenePass2AuthoringEnvelope.model_validate(authoring)


def test_bridge_cadence_and_cluster_arc_named_as_procedural_rules() -> None:
    model = IrenePass2AuthoringEnvelope.model_validate_json(GOLDEN.read_text(encoding="utf-8"))

    assert "bridge_cadence" in model.procedural_rules
    assert "cluster_arc_continuity" in model.procedural_rules
