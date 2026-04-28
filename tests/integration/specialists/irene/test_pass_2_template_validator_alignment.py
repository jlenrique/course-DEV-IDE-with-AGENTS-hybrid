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


def _write_oracle_bundle(tmp_path: Path, *, cue_in_text: bool = True) -> dict[str, object]:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    slide = bundle / "slide-01.png"
    slide.write_bytes(b"png")
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
    segments = [
        {
            "id": "seg-01",
            "gary_slide_id": "slide-01",
            "slide_id": "slide-01",
            "gary_card_number": 1,
            "card_number": 1,
            "narration_text": narration,
            "behavioral_intent": "credible",
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
                    "perception_source": "slide-01",
                }
            ],
        }
    ]
    (bundle / "narration-script.md").write_text(
        "\n".join(
            [
                "# Narration Script",
                "",
                "[SEGMENT: seg-01]",
                "",
                "**Stage Directions:**",
                "- Behavioral Intent: credible",
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


def test_schema_valid_but_procedural_rejected_fails_loud(tmp_path: Path) -> None:
    payload = _write_oracle_bundle(tmp_path, cue_in_text=False)
    authoring = json.loads(GOLDEN.read_text(encoding="utf-8"))
    IrenePass2AuthoringEnvelope.model_validate(authoring)
    envelope_path = tmp_path / "bundle" / "pass2-envelope.json"
    envelope_path.write_text(json.dumps(payload), encoding="utf-8")

    result = validate_irene_pass2_handoff(payload, envelope_path=envelope_path)

    assert result["status"] == "fail"
    assert any("visual narration_cue" in error for error in result["errors"])


def test_authoring_schema_catches_structural_rule_before_oracle(tmp_path: Path) -> None:
    authoring = json.loads(GOLDEN.read_text(encoding="utf-8"))
    authoring["gary_slide_output"][0]["file_path"] = "https://example.com/slide.png"

    with pytest.raises(ValidationError, match="must not be remote"):
        IrenePass2AuthoringEnvelope.model_validate(authoring)


def test_bridge_cadence_and_cluster_arc_named_as_procedural_rules() -> None:
    model = IrenePass2AuthoringEnvelope.model_validate_json(GOLDEN.read_text(encoding="utf-8"))

    assert "bridge_cadence" in model.procedural_rules
    assert "cluster_arc_continuity" in model.procedural_rules
