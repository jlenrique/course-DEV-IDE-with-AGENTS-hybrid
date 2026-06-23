from __future__ import annotations

import json
from pathlib import Path

from app.models.perception.perception_artifact import PerceptionArtifact
from scripts.analysis.reading_path_p2_4b_run import load_gold, score_emitted
from scripts.analysis.reading_path_p2_4b_score import ReadingPathTuple
from scripts.utilities.reading_path_classifier import with_classified_reading_path
from scripts.utilities.reading_path_escalation import run_s3_escalation

ROOT = Path(__file__).resolve().parents[2]
FROZEN_PERCEPTIONS = (
    ROOT
    / "_bmad-output"
    / "implementation-artifacts"
    / "reading-path-holdout-rescan-2026-06-23"
    / "perceptions"
)


def _classified_frozen() -> list[PerceptionArtifact]:
    artifacts: list[PerceptionArtifact] = []
    for slide_id in load_gold():
        payload = json.loads((FROZEN_PERCEPTIONS / f"{slide_id}.json").read_text(
            encoding="utf-8"
        ))
        artifacts.append(
            with_classified_reading_path(
                PerceptionArtifact.model_validate(payload["perception_artifact"])
            )
        )
    return artifacts


def _tuple_from_artifact(artifact: PerceptionArtifact) -> ReadingPathTuple:
    return ReadingPathTuple(
        macro_layout=artifact.macro_layout or "",
        image_role=artifact.dominant_image_role,
        text_substructure=artifact.text_substructure,
        narration_cadence=artifact.narration_cadence,
        callout_intent=artifact.callout_intent,
        derived_primary=artifact.reading_path,
    )


def test_p2_4b_macro_fixture_reaches_success_floor() -> None:
    emitted = {
        artifact.slide_id: _tuple_from_artifact(artifact)
        for artifact in _classified_frozen()
    }
    report = score_emitted(emitted)

    assert report.per_axis_hits["macro_layout"] >= 12
    assert report.per_axis_rate("macro_layout") >= 0.85


def test_p2_4b_image_role_fixture_uses_authoritative_dominant_field() -> None:
    artifacts = _classified_frozen()
    emitted = {artifact.slide_id: _tuple_from_artifact(artifact) for artifact in artifacts}
    report = score_emitted(emitted)

    assert all(hasattr(artifact, "dominant_image_role") for artifact in artifacts)
    assert report.per_axis_hits["image_role"] >= 10
    assert report.per_axis_rate("image_role") >= 0.70


def test_p2_4b_full_tuple_integration_passes_without_s3_retry_to_green() -> None:
    emitted = {
        artifact.slide_id: _tuple_from_artifact(artifact)
        for artifact in _classified_frozen()
    }
    report = score_emitted(emitted)

    assert report.primary_key_hits >= 12
    assert report.primary_key_top1 >= 12 / 14
    assert report.full_tuple_rate >= 0.80


def test_p2_4b_escalation_predicate_is_wired_to_real_ledger_and_bounded() -> None:
    artifacts = _classified_frozen()
    calls: list[str] = []

    def noop_client(artifact: PerceptionArtifact, fired: list[str]) -> str:
        calls.append(artifact.slide_id)
        return json.dumps(
            {
                "layout_delta": None,
                "callout_intents": [],
                "process_kind": None,
                "role_overrides": [],
            }
        )

    result = run_s3_escalation(artifacts, client=noop_client)
    ledger = result.ledger

    assert ledger["total"] == 14
    assert 0 < ledger["escalation_rate"] <= 0.20
    assert len(calls) == ledger["escalated"]
    assert len(calls) <= 2
