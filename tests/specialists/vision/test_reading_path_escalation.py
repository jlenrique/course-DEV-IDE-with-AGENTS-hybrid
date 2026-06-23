from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.models.perception import PerceptionArtifact
from scripts.utilities.reading_path_escalation import (
    EscalationBoundsError,
    EscalationThresholds,
    apply_tuple_delta,
    assert_escalation_rate_bounds,
    build_escalation_ledger,
    decide_escalation,
    parse_tuple_delta,
    run_s3_escalation,
)


def _artifact(elements: list[dict[str, object]], **overrides: object) -> PerceptionArtifact:
    payload = {
        "slide_id": "slide-01",
        "confidence": "HIGH",
        "coverage": "perceived",
        "confidence_score": 0.95,
        "visual_elements": elements,
        "extracted_text": "",
        "layout_description": "",
        "slide_title": "Fixture",
        "reading_path": "top_down",
        "macro_layout": "single_text_block",
        "image_roles": ["1" for _ in elements],
        "image_role_flags": None,
        "text_substructure": "dense_exposition",
        "narration_cadence": "moderate",
        "callout_intent": None,
        "reading_path_flags": None,
    }
    payload.update(overrides)
    return PerceptionArtifact.model_validate(payload)


def test_s3_predicate_consumes_reading_path_flags_for_opposition() -> None:
    artifact = _artifact(
        [
            {"id": "left", "kind": "text", "label": "Option A", "bbox": [0.1, 0.2, 0.4, 0.7]},
            {"id": "right", "kind": "text", "label": "Option B", "bbox": [0.6, 0.2, 0.9, 0.7]},
        ],
        macro_layout="multi_column",
        text_substructure="peer_boxes",
        reading_path="multi_column",
        reading_path_flags=["oppositional_cue"],
    )

    decision = decide_escalation(artifact)

    assert decision.escalate
    assert decision.subpredicates["opposition_cue_hit"] is True
    assert decision.fired == ["opposition_cue_hit"]


def test_s3_predicate_flags_each_required_subpredicate() -> None:
    artifact = _artifact(
        [
            {
                "id": "step-list",
                "kind": "callout quiz",
                "label": "1. Intake 2. Route",
                "role_tier": "3",
                "bbox": [0.1, 0.1, 0.4, 0.4],
            },
            {
                "id": "bboxless",
                "kind": "photo",
                "label": "No geometry",
            },
        ],
        confidence="LOW",
        confidence_score=0.2,
        image_roles=["2", None],
        image_role_flags=["tier_3_quarantined"],
        macro_layout="single_text_block",
        text_substructure="peer_boxes",
        reading_path="top_down",
    )

    decision = decide_escalation(
        artifact,
        macro_margin=0.05,
        thresholds=EscalationThresholds(macro_margin=0.10, confidence_score=0.70),
    )

    assert decision.escalate
    assert decision.subpredicates == {
        "macro_margin_low": True,
        "opposition_cue_hit": False,
        "callout_kind_present": True,
        "numbered_without_transform": True,
        "low_conf_role_elements": True,
        "tuple_disagreement": True,
        "low_confidence": True,
        "tier_candidate_hit": True,
    }
    assert decision.low_conf_role_element_count == 1


def test_s3_ledger_is_written_for_true_and_false_decisions(tmp_path: Path) -> None:
    plain = _artifact(
        [{"id": "body", "kind": "text", "label": "Plain text", "bbox": [0.1, 0.1, 0.9, 0.4]}],
        slide_id="plain",
    )
    ambiguous = plain.model_copy(
        update={"slide_id": "ambiguous", "reading_path_flags": ["oppositional_cue"]}
    )
    path = tmp_path / "escalation_ledger.json"

    ledger = build_escalation_ledger([plain, ambiguous], output_path=path)

    assert path.exists()
    assert json.loads(path.read_text(encoding="utf-8")) == ledger
    assert ledger["total"] == 2
    assert ledger["escalation_rate"] == 0.5
    assert [row["escalate"] for row in ledger["slides"]] == [False, True]


def test_s3_tripwires_catch_over_and_zero_escalation() -> None:
    # SCOPE (S3-T11 party rider R1, 2026-06-23): this asserts the tripwire ARITHMETIC
    # on a SYNTHETIC ledger only — it is NOT wired to the real runtime escalation rate.
    # The live S3-T11 dry-run measured a REAL held-out rate of 93% (vs this 20% ceiling),
    # which this test cannot see. Wiring assert_escalation_rate_bounds to the production
    # escalation_ledger is a P2-4b calibration follow-on (the threshold can't precede
    # recalibration of the over-broad callout_kind_present predicate — chicken/egg).
    rows = [
        {"slide_id": "a", "escalate": True},
        {"slide_id": "b", "escalate": True},
        {"slide_id": "c", "escalate": False},
    ]
    with pytest.raises(EscalationBoundsError, match="over-escalation"):
        assert_escalation_rate_bounds({"total": 3, "slides": rows}, max_rate=0.20)

    with pytest.raises(EscalationBoundsError, match="zero-escalation"):
        assert_escalation_rate_bounds(
            {"total": 2, "slides": [{"slide_id": "x", "escalate": False}]},
            known_ambiguous_present=True,
        )


def test_s3_parse_clears_delta_fields_for_unfired_jobs() -> None:
    delta = parse_tuple_delta(
        json.dumps(
            {
                "layout_delta": {"two_pane": True},
                "callout_intents": [{"element_id": "cta", "intent": "directive_cta"}],
                "process_kind": "enumerated_process",
                "role_overrides": [{"element_id": "image", "role_tier": "2"}],
            }
        ),
        fired=["opposition_cue_hit"],
    )

    assert delta.layout_delta is not None
    assert delta.layout_delta.two_pane is True
    assert delta.callout_intents == []
    assert delta.process_kind is None
    assert delta.role_overrides == []


def test_s3_merge_applies_tuple_delta_and_preserves_none_role_sentinel() -> None:
    artifact = _artifact(
        [
            {"id": "left", "kind": "text", "label": "Option A", "bbox": [0.1, 0.2, 0.4, 0.7]},
            {"id": "gap", "kind": "photo", "label": "No geometry"},
        ],
        macro_layout="multi_column",
        text_substructure="peer_boxes",
        reading_path="multi_column",
        image_roles=["1", None],
    )
    delta = parse_tuple_delta(
        json.dumps(
            {
                "layout_delta": {"two_pane": True},
                "callout_intents": [{"element_id": "left", "intent": "directive_cta"}],
                "process_kind": "enumerated_process",
                "role_overrides": [{"element_id": "gap", "role_tier": "2"}],
            }
        ),
        fired=[
            "opposition_cue_hit",
            "callout_kind_present",
            "numbered_without_transform",
            "low_conf_role_elements",
        ],
    )

    merged = apply_tuple_delta(artifact, delta)

    assert merged.macro_layout == "two_pane"
    assert merged.text_substructure == "enumerated_process"
    assert merged.reading_path == "two_up_comparison"
    assert merged.callout_intent == "directive_cta"
    assert merged.image_roles == ["1", None]


def test_s3_run_invokes_client_once_per_escalated_slide_and_degrades_malformed() -> None:
    plain = _artifact(
        [{"id": "body", "kind": "text", "label": "Plain text", "bbox": [0.1, 0.1, 0.9, 0.4]}],
        slide_id="plain",
    )
    ambiguous = plain.model_copy(
        update={"slide_id": "ambiguous", "reading_path_flags": ["oppositional_cue"]}
    )
    calls: list[str] = []

    def malformed_client(artifact: PerceptionArtifact, fired: list[str]) -> str:
        calls.append(artifact.slide_id)
        return "not json"

    result = run_s3_escalation([plain, ambiguous], client=malformed_client)

    assert calls == ["ambiguous"]
    assert result.artifacts == [plain, ambiguous]
    row = next(item for item in result.ledger["slides"] if item["slide_id"] == "ambiguous")
    assert row["degraded"] is True


def test_s3_escalation_api_has_no_gold_or_top1_conditioning() -> None:
    import inspect

    import scripts.utilities.reading_path_escalation as module

    signatures = [
        inspect.signature(module.decide_escalation),
        inspect.signature(module.run_s3_escalation),
    ]
    joined = "\n".join(str(signature) for signature in signatures)

    assert "gold" not in joined.lower()
    assert "top_1" not in joined.lower()
    assert "top1" not in joined.lower()
