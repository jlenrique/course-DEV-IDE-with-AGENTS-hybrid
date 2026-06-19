from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from app.models.perception.perception_artifact import PerceptionArtifact
from app.specialists.quinn_r.fidelity_detector import (
    classify_fidelity_reference,
    detect_fidelity,
)
from app.specialists.quinn_r.quality_control_dispatch import FidelityError

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "specialists" / "quinn_r" / "fidelity"
GREEN = FIXTURES / "green-corpus"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _apply_seeded_defect(spec: dict[str, Any]) -> dict[str, Any]:
    payload = deepcopy(_load(GREEN / spec["source_fixture"]))
    mutation = spec["mutation"]
    segment = payload["narration_segments"][0]
    segment["text"] = segment["text"].replace(mutation["from"], mutation["to"], 1)
    return payload


def test_slide01_red_fixture_blocks_orphan_visual_reference() -> None:
    payload = _load(FIXTURES / "slide01-red.json")

    with pytest.raises(FidelityError) as excinfo:
        detect_fidelity(payload["narration_segments"], payload["perception_artifacts"])

    assert excinfo.value.tag == "quinn_r.g5.fidelity-orphan-reference"
    assert "line" in str(excinfo.value)
    assert "slide-01" in str(excinfo.value)


def test_green_corpus_is_two_sided_and_hash_frozen() -> None:
    manifest = _load(FIXTURES / "green-corpus-manifest.json")
    assert len(manifest["fixtures"]) >= 8
    assert {row["classification"] for row in manifest["fixtures"]} == {
        "fidelity-bearing-faithful",
        "non-visual",
    }

    false_positives = []
    for row in manifest["fixtures"]:
        path = GREEN / row["file"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest == row["sha256"]
        payload = _load(path)
        verdict = detect_fidelity(payload["narration_segments"], payload["perception_artifacts"])
        if verdict["blocking"]:
            false_positives.append(row["file"])

    assert false_positives == []


@pytest.mark.parametrize(
    ("filename", "tag"),
    [
        ("element-drop.json", "quinn_r.g5.fidelity-orphan-reference"),
        ("figure-swap.json", "quinn_r.g5.fidelity-figure-contradiction"),
        ("magnitude-drift.json", "quinn_r.g5.fidelity-figure-contradiction"),
    ],
)
def test_seeded_defects_are_single_mutations_that_block(filename: str, tag: str) -> None:
    payload = _apply_seeded_defect(_load(FIXTURES / "seeded-defects" / filename))

    with pytest.raises(FidelityError) as excinfo:
        detect_fidelity(payload["narration_segments"], payload["perception_artifacts"])

    assert excinfo.value.tag == tag


def test_missing_or_low_confidence_perception_is_non_conformant() -> None:
    with pytest.raises(FidelityError):
        detect_fidelity([{"slide_id": "s1", "text": "The callout shows $4.5T."}], [])

    payload = _load(GREEN / "green-01.json")
    payload["perception_artifacts"][0]["coverage"] = "low-confidence"
    with pytest.raises(FidelityError):
        detect_fidelity(payload["narration_segments"], payload["perception_artifacts"])


def test_classifier_has_two_sided_confusion_pins() -> None:
    cases = {
        "The callout shows $4.5T annual spend.": "fidelity-bearing",
        "The building photo sits beside three stat callouts.": "fidelity-bearing",
        "This is the policy implication of the prior section.": "non-visual",
        "The lesson now shifts to administrative burden.": "non-visual",
        "Independent practice remains under pressure.": "non-visual",
    }

    observed = {text: classify_fidelity_reference(text) for text in cases}

    assert observed == cases


def test_detector_is_idempotent_and_clears_on_corrected_artifact() -> None:
    # AC-13 / M3 (Murat, non-negotiable): the detector holds no latched state.
    # The same bad input raises every time; a corrected artifact returns clean;
    # re-running either does not flip the verdict (P2-3's clearing contract).
    red = _load(FIXTURES / "slide01-red.json")
    bad_segments = red["narration_segments"]
    artifacts = red["perception_artifacts"]

    with pytest.raises(FidelityError):
        detect_fidelity(bad_segments, artifacts)
    with pytest.raises(FidelityError):
        detect_fidelity(bad_segments, artifacts)  # no sticky "passed" state

    # The P2-3 repair: narration grounded on the perceived slide ($4.5T callouts + photo).
    corrected = [
        {
            "slide_id": "slide-01",
            "text": "The building photo sits beside callouts for $4.5T spend, 74%, and 3x growth.",
        }
    ]
    first = detect_fidelity(corrected, artifacts)
    second = detect_fidelity(corrected, artifacts)
    assert first == second
    assert first["blocking"] == []

    # The corrected pass did not latch — the bad input still raises afterward.
    with pytest.raises(FidelityError):
        detect_fidelity(bad_segments, artifacts)


def _hi(slide_id: str, **over: Any) -> dict[str, Any]:
    base = {"slide_id": slide_id, "confidence": "HIGH", "coverage": "perceived"}
    base.update(over)
    return base


def test_bare_dollar_not_conflated_with_trillions() -> None:
    # Blind-Hunter CRITICAL: "$5" must not match "$5 trillion".
    artifacts = [_hi("s1", extracted_text="Total spend $5 trillion.")]
    with pytest.raises(FidelityError) as exc:
        detect_fidelity([{"slide_id": "s1", "text": "The figure is $5."}], artifacts)
    assert exc.value.tag == "quinn_r.g5.fidelity-figure-contradiction"
    # and the faithful unit-bearing claim passes
    ok = detect_fidelity([{"slide_id": "s1", "text": "Spend reached $5 trillion."}], artifacts)
    assert ok["blocking"] == []


def test_duplicate_slide_id_raises_not_last_wins() -> None:
    artifacts = [_hi("s1", extracted_text="bar chart"), _hi("s1", extracted_text="line chart")]
    with pytest.raises(FidelityError, match="duplicate perception artifact"):
        detect_fidelity([{"slide_id": "s1", "text": "ok"}], artifacts)


def test_single_artifact_dict_is_accepted_and_malformed_raises_fidelity_error() -> None:
    # Edge-Hunter HIGH: a single artifact dict must not crash with raw ValidationError.
    single = _hi("s1", extracted_text="A clinic image with detail.")
    ok = detect_fidelity([{"slide_id": "s1", "text": "The clinic image is shown."}], single)
    assert ok["blocking"] == []
    # schema drift surfaces as a tagged FidelityError, not a bare ValidationError.
    with pytest.raises(FidelityError):
        detect_fidelity([{"slide_id": "s1", "text": "ok"}], [{**single, "unexpected": True}])


def test_idioms_are_not_flagged_as_visual_references() -> None:
    # Blind-Hunter MEDIUM: idioms must not trip the blocking visual check.
    for idiom in ("Let's raise the bar this quarter.", "The bottom line is clear.",
                  "We will table that discussion."):
        assert classify_fidelity_reference(idiom) == "non-visual"
    artifacts = [_hi("s1", extracted_text="Decision context.")]
    idiom_text = "Let's raise the bar; the bottom line is clear."
    ok = detect_fidelity([{"slide_id": "s1", "text": idiom_text}], artifacts)
    assert ok["blocking"] == []


def test_tripwire_g5_manifest_does_not_yet_supply_perception() -> None:
    # Edge-1 ratified posture (party 2026-06-19): absent perception is a dormant
    # UNVERIFIED status, NOT a fail, because the production G5 node does not yet
    # project perception_artifacts. THIS TEST IS A TRIPWIRE: when P2-2 wires
    # perception into the G5 node's dependency_projections, this assertion FAILS —
    # at which point flip `run_g5_checks` from dormant-skip to enforce and delete
    # this test. Dormancy cannot silently rot.
    import yaml

    manifest_path = (
        Path(__file__).resolve().parents[3] / "state" / "config" / "pipeline-manifest.yaml"
    )
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    g5_nodes = [n for n in manifest["nodes"] if n.get("gate_code") == "G5"]
    assert g5_nodes, "expected a G5 node in the pipeline manifest"
    for node in g5_nodes:
        projections = node.get("dependency_projections") or {}
        assert "perception_artifacts" not in projections, (
            "P2-2 appears to have wired perception into the G5 node — flip "
            "run_g5_checks from dormant-skip to enforce and delete this tripwire."
        )


def test_perception_artifact_shape_pins_legacy_fields_and_coverage_enum() -> None:
    payload = _load(GREEN / "green-01.json")["perception_artifacts"][0]
    artifact = PerceptionArtifact.model_validate(payload)

    assert set(artifact.model_dump()) == {
        "artifact_path",
        "card_number",
        "confidence",
        "coverage",
        "extracted_text",
        "layout_description",
        "slide_id",
        "slide_title",
        "text_blocks",
        "visual_elements",
    }

    with pytest.raises(ValidationError):
        PerceptionArtifact.model_validate({**payload, "unexpected": True})

    with pytest.raises(ValidationError):
        PerceptionArtifact.model_validate({**payload, "coverage": "maybe"})
