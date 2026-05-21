from __future__ import annotations

import json
import re
from collections.abc import Callable
from importlib import util
from pathlib import Path
from typing import Literal, NamedTuple

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


RuleCoverage = Literal["schema", "procedural", "skipped"]
PayloadMutator = Callable[[dict[str, object]], None]


class ValidatorRuleCoverage(NamedTuple):
    rule_id: str
    validator_line: int
    expected_coverage: RuleCoverage
    rationale: str


# 6.4-SP2-EH-1: explicit validator-oracle inventory for all append enforcement
# points in validate-irene-pass2-handoff.py. Coverage meanings:
# - schema: IrenePass2AuthoringEnvelope rejects the shape before oracle runtime.
# - procedural: a runtime/oracle behavior case below exercises the rule family.
# - skipped: the validator rule is outside the authoring-template contract surface
#   or is advisory-only; every skip carries a concrete rationale.
VALIDATOR_RULE_COVERAGE: tuple[ValidatorRuleCoverage, ...] = (
    ValidatorRuleCoverage(
        "err_0778_missing_narration_script_artifact",
        778,
        "skipped",
        "External artifact existence is a bundle filesystem contract, not an "
        "authoring-envelope field.",
    ),
    ValidatorRuleCoverage(
        "err_0783_empty_narration_script_artifact",
        783,
        "skipped",
        "External artifact content is validated after Irene writes files; the "
        "template has no script file body.",
    ),
    ValidatorRuleCoverage(
        "err_0799_missing_perception_artifacts_file",
        799,
        "skipped",
        "External artifact existence is a bundle filesystem contract, not an "
        "authoring-envelope field.",
    ),
    ValidatorRuleCoverage(
        "err_0809_invalid_perception_artifacts_file",
        809,
        "skipped",
        "Standalone JSON parse failure is outside the in-memory authoring-envelope schema.",
    ),
    ValidatorRuleCoverage(
        "err_0814_missing_segment_manifest_file",
        814,
        "skipped",
        "External artifact existence is a bundle filesystem contract, not an "
        "authoring-envelope field.",
    ),
    ValidatorRuleCoverage(
        "err_0821_invalid_segment_manifest_file",
        821,
        "skipped",
        "Standalone YAML parse failure is outside the in-memory authoring-envelope schema.",
    ),
    ValidatorRuleCoverage(
        "err_0827_segment_manifest_segments_not_list",
        827,
        "skipped",
        "Standalone YAML shape is validated by the oracle after file load; "
        "envelope schema owns its own segment list.",
    ),
    ValidatorRuleCoverage(
        "warn_1034_cluster_head_word_range",
        1034,
        "skipped",
        "Advisory narration-density warning; not a fail-loud authoring-envelope invariant.",
    ),
    ValidatorRuleCoverage(
        "warn_1044_interstitial_word_range",
        1044,
        "skipped",
        "Advisory narration-density warning; not a fail-loud authoring-envelope invariant.",
    ),
    ValidatorRuleCoverage(
        "warn_1058_pivot_role_not_eligible",
        1058,
        "skipped",
        "Advisory within-cluster bridge warning; strict runtime escalation is oracle policy.",
    ),
    ValidatorRuleCoverage(
        "warn_1063_tension_pivot_expected",
        1063,
        "skipped",
        "Advisory within-cluster bridge warning; strict runtime escalation is oracle policy.",
    ),
    ValidatorRuleCoverage(
        "warn_1067_interstitial_bridge_not_none",
        1067,
        "skipped",
        "Advisory within-cluster bridge warning; strict runtime escalation is oracle policy.",
    ),
    ValidatorRuleCoverage(
        "err_1094_spoken_bridge_policy_error",
        1094,
        "skipped",
        "Config-dependent spoken-bridge policy is enforced by the oracle, not the static template.",
    ),
    ValidatorRuleCoverage(
        "warn_1096_spoken_bridge_policy_warning",
        1096,
        "skipped",
        "Advisory spoken-bridge warning when policy is not error; not a template rejection.",
    ),
    ValidatorRuleCoverage(
        "warn_1131_runtime_budget_band",
        1131,
        "skipped",
        "Advisory runtime budget warning; strict runtime escalation is oracle policy.",
    ),
    ValidatorRuleCoverage(
        "warn_1411_cluster_boundary_bridge_type",
        1411,
        "procedural",
        "Bridge-cadence procedural rule is covered by the cluster bridge red case.",
    ),
    ValidatorRuleCoverage(
        "warn_1433_intro_outro_bridge_cadence",
        1433,
        "skipped",
        "Advisory cadence warning; no static template field can know elapsed slide/minute cadence.",
    ),
    ValidatorRuleCoverage(
        "err_1542_interstitial_missing_cluster_id",
        1542,
        "skipped",
        "Interstitial classification is oracle-derived from external manifest semantics.",
    ),
    ValidatorRuleCoverage(
        "err_1547_interstitial_missing_timing_role",
        1547,
        "schema",
        "SegmentManifestSegment.timing_role is a required non-empty authoring field.",
    ),
    ValidatorRuleCoverage(
        "err_1553_missing_manifest_for_slide_ids",
        1553,
        "skipped",
        "Authorized-storyboard coverage is external bundle state beyond the envelope schema.",
    ),
    ValidatorRuleCoverage(
        "err_1558_unknown_manifest_slide_ids",
        1558,
        "schema",
        "Envelope cross-artifact validation rejects segments for unknown Gary slide IDs.",
    ),
    ValidatorRuleCoverage(
        "err_1563_empty_segment_narration_text",
        1563,
        "schema",
        "SegmentManifestSegment.narration_text is required and non-empty.",
    ),
    ValidatorRuleCoverage(
        "err_1568_missing_visual_narration_cue",
        1568,
        "procedural",
        "Narration-cue presence is one of the six procedural authoring rules.",
    ),
    ValidatorRuleCoverage(
        "err_1573_untraceable_visual_cues",
        1573,
        "procedural",
        "Traceable visual references are one of the six procedural authoring rules.",
    ),
    ValidatorRuleCoverage(
        "err_1578_manifest_forbidden_meta_language",
        1578,
        "skipped",
        "Forbidden meta-language is policy-text scanning, not a structural template invariant.",
    ),
    ValidatorRuleCoverage(
        "err_1583_script_forbidden_meta_language",
        1583,
        "skipped",
        "Narration script text scanning happens on the emitted file, outside the envelope schema.",
    ),
    ValidatorRuleCoverage(
        "err_1588_behavioral_intent_mismatch",
        1588,
        "procedural",
        "Behavioral-intent parity is one of the six procedural authoring rules.",
    ),
    ValidatorRuleCoverage(
        "err_1593_master_behavioral_intent_violation",
        1593,
        "skipped",
        "Master-intent cluster semantics are oracle-only fields outside the "
        "strict authoring model.",
    ),
    ValidatorRuleCoverage(
        "err_1598_cluster_new_concept_violation",
        1598,
        "skipped",
        "Concept-introduction analysis is semantic oracle behavior, not JSON/Pydantic structure.",
    ),
    ValidatorRuleCoverage(
        "err_1603_cluster_arc_integrity_violation",
        1603,
        "procedural",
        "Cluster arc continuity is one of the six procedural authoring rules.",
    ),
    ValidatorRuleCoverage(
        "warn_1608_missing_behavioral_intent",
        1608,
        "skipped",
        "Advisory warning for missing external intent metadata; not a fail-loud "
        "template invariant.",
    ),
    ValidatorRuleCoverage(
        "warn_1613_static_motion_narration",
        1613,
        "skipped",
        "Advisory motion narration heuristic; not a fail-loud template invariant.",
    ),
    ValidatorRuleCoverage(
        "err_1618_perception_artifact_mismatch",
        1618,
        "skipped",
        "Compares emitted perception file against envelope payload; requires external artifact IO.",
    ),
    ValidatorRuleCoverage(
        "err_1623_missing_motion_perception_artifacts_array",
        1623,
        "skipped",
        "Motion side-channel payload is outside the Pass 2 authoring envelope.",
    ),
    ValidatorRuleCoverage(
        "err_1627_unapproved_motion_asset_binding",
        1627,
        "skipped",
        "Motion-plan approval binding is an external oracle contract.",
    ),
    ValidatorRuleCoverage(
        "err_1632_noncanonical_motion_visual_file",
        1632,
        "schema",
        "Envelope validation rejects noncanonical segment visual_file values against Gary PNGs.",
    ),
    ValidatorRuleCoverage(
        "err_1637_missing_motion_perception_confirmation",
        1637,
        "procedural",
        "Motion perception confirmation is one of the six procedural authoring rules.",
    ),
    ValidatorRuleCoverage(
        "err_1685_missing_required_pass2_fields",
        1685,
        "schema",
        "Required top-level Pass 2 fields are required in the authoring envelope.",
    ),
    ValidatorRuleCoverage(
        "err_1693_gary_slide_output_not_array",
        1693,
        "schema",
        "gary_slide_output is a required list in the authoring envelope.",
    ),
    ValidatorRuleCoverage(
        "err_1696_perception_artifacts_not_array",
        1696,
        "schema",
        "perception_artifacts is a required list in the authoring envelope.",
    ),
    ValidatorRuleCoverage(
        "err_1761_gary_card_sequence_not_contiguous",
        1761,
        "skipped",
        "Contiguous card sequencing is an oracle ordering rule; the template pins "
        "per-segment card parity.",
    ),
    ValidatorRuleCoverage(
        "err_1765_gary_missing_file_path",
        1765,
        "schema",
        "GarySlideOutput.file_path is required and non-empty.",
    ),
    ValidatorRuleCoverage(
        "err_1769_gary_remote_file_path",
        1769,
        "schema",
        "GarySlideOutput.file_path uses the shared local PNG pattern that rejects URL schemes.",
    ),
    ValidatorRuleCoverage(
        "err_1774_gary_non_png_file_path",
        1774,
        "schema",
        "GarySlideOutput.file_path uses the shared local PNG suffix pattern.",
    ),
    ValidatorRuleCoverage(
        "err_1779_gary_missing_local_png_on_disk",
        1779,
        "skipped",
        "Disk existence cannot be represented in portable JSON Schema or static Pydantic fields.",
    ),
    ValidatorRuleCoverage(
        "err_1784_gary_png_card_filename_mismatch",
        1784,
        "skipped",
        "Filename/card-number convention is an oracle filesystem convention outside the template.",
    ),
    ValidatorRuleCoverage(
        "err_1789_gary_missing_source_ref",
        1789,
        "schema",
        "GarySlideOutput.source_ref is required and non-empty.",
    ),
    ValidatorRuleCoverage(
        "err_1807_missing_perception_for_gary_slide",
        1807,
        "schema",
        "Envelope cross-artifact validation requires perception for every Gary slide.",
    ),
    ValidatorRuleCoverage(
        "err_1829_missing_source_image_path",
        1829,
        "schema",
        "PerceptionArtifact.source_image_path is required and non-empty.",
    ),
    ValidatorRuleCoverage(
        "err_1834_mismatched_source_image_path",
        1834,
        "schema",
        "Envelope cross-artifact validation matches perception source images to Gary PNGs.",
    ),
)


PROCEDURAL_RULE_RED_CASE_IDS = {
    "behavioral_intent_parity",
    "bridge_cadence",
    "cluster_arc_continuity",
    "motion_perception_confirmation",
    "narration_cue_presence",
    "traceable_visual_references",
}

PROCEDURAL_ALIGNMENT_COVERAGE = {
    "warn_1411_cluster_boundary_bridge_type": "bridge_cadence",
    "err_1568_missing_visual_narration_cue": "narration_cue_presence",
    "err_1573_untraceable_visual_cues": "traceable_visual_references",
    "err_1588_behavioral_intent_mismatch": "behavioral_intent_parity",
    "err_1603_cluster_arc_integrity_violation": "cluster_arc_continuity",
    "err_1637_missing_motion_perception_confirmation": "motion_perception_confirmation",
}


def _set_payload_path(
    payload: dict[str, object],
    path: tuple[object, ...],
    value: object,
) -> None:
    cursor: object = payload
    for part in path[:-1]:
        cursor = cursor[part]  # type: ignore[index]
    cursor[path[-1]] = value  # type: ignore[index]


def _delete_payload_path(payload: dict[str, object], path: tuple[object, ...]) -> None:
    cursor: object = payload
    for part in path[:-1]:
        cursor = cursor[part]  # type: ignore[index]
    del cursor[path[-1]]  # type: ignore[index]


def _schema_mutator_for_path(path: tuple[object, ...], value: object) -> PayloadMutator:
    def mutate(payload: dict[str, object]) -> None:
        _set_payload_path(payload, path, value)

    return mutate


SCHEMA_RULE_MUTATORS: dict[str, PayloadMutator] = {
    "err_1547_interstitial_missing_timing_role": _schema_mutator_for_path(
        ("segment_manifest", "segments", 0, "timing_role"),
        "",
    ),
    "err_1558_unknown_manifest_slide_ids": _schema_mutator_for_path(
        ("segment_manifest", "segments", 0, "slide_id"),
        "unknown-slide",
    ),
    "err_1563_empty_segment_narration_text": _schema_mutator_for_path(
        ("segment_manifest", "segments", 0, "narration_text"),
        "",
    ),
    "err_1632_noncanonical_motion_visual_file": _schema_mutator_for_path(
        ("segment_manifest", "segments", 0, "visual_file"),
        "bundle/motion-clip.mp4",
    ),
    "err_1685_missing_required_pass2_fields": lambda payload: _delete_payload_path(
        payload,
        ("run_id",),
    ),
    "err_1693_gary_slide_output_not_array": _schema_mutator_for_path(
        ("gary_slide_output",),
        "not-an-array",
    ),
    "err_1696_perception_artifacts_not_array": _schema_mutator_for_path(
        ("perception_artifacts",),
        "not-an-array",
    ),
    "err_1765_gary_missing_file_path": _schema_mutator_for_path(
        ("gary_slide_output", 0, "file_path"),
        "",
    ),
    "err_1769_gary_remote_file_path": _schema_mutator_for_path(
        ("gary_slide_output", 0, "file_path"),
        "https://example.com/slide.png",
    ),
    "err_1774_gary_non_png_file_path": _schema_mutator_for_path(
        ("gary_slide_output", 0, "file_path"),
        "bundle/slide-01.jpg",
    ),
    "err_1789_gary_missing_source_ref": _schema_mutator_for_path(
        ("gary_slide_output", 0, "source_ref"),
        "",
    ),
    "err_1807_missing_perception_for_gary_slide": _schema_mutator_for_path(
        ("perception_artifacts",),
        [],
    ),
    "err_1829_missing_source_image_path": _schema_mutator_for_path(
        ("perception_artifacts", 0, "source_image_path"),
        "",
    ),
    "err_1834_mismatched_source_image_path": _schema_mutator_for_path(
        ("perception_artifacts", 0, "source_image_path"),
        "bundle/other.png",
    ),
}


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


def _validator_append_rule_lines() -> list[int]:
    text = SCRIPT_PATH.read_text(encoding="utf-8")
    return [
        line_number
        for line_number, line in enumerate(text.splitlines(), start=1)
        if re.search(r"\berrors\.append\(", line)
        or re.search(r"\b\w*warnings\.append\(", line)
    ]


def test_validator_alignment_enumeration_covers_all_validator_rules() -> None:
    """6.4-SP2-EH-1: inventory must drift with validator append sites."""
    actual_lines = _validator_append_rule_lines()
    expected_lines = [rule.validator_line for rule in VALIDATOR_RULE_COVERAGE]

    assert len(actual_lines) == 50
    assert len(VALIDATOR_RULE_COVERAGE) == 50
    assert actual_lines == expected_lines


@pytest.mark.parametrize(
    "rule",
    VALIDATOR_RULE_COVERAGE,
    ids=[rule.rule_id for rule in VALIDATOR_RULE_COVERAGE],
)
def test_validator_oracle_alignment_parametrized_by_rule(
    rule: ValidatorRuleCoverage,
) -> None:
    assert rule.rationale.strip(), rule.rule_id

    if rule.expected_coverage == "schema":
        mutator = SCHEMA_RULE_MUTATORS[rule.rule_id]
        authoring = json.loads(GOLDEN.read_text(encoding="utf-8"))
        mutator(authoring)

        with pytest.raises(ValidationError):
            IrenePass2AuthoringEnvelope.model_validate(authoring)
    elif rule.expected_coverage == "procedural":
        covered_case = PROCEDURAL_ALIGNMENT_COVERAGE[rule.rule_id]
        assert covered_case in PROCEDURAL_RULE_RED_CASE_IDS
    else:
        assert rule.expected_coverage == "skipped"


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
def test_validator_procedural_rule_red_cases(
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
