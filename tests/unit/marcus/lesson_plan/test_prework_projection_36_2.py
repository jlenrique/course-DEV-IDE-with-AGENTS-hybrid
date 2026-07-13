from __future__ import annotations

import ast
import inspect
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.marcus.lesson_plan.lesson_type_classifier import (
    LessonTypeClassification,
    LessonTypeEvidence,
    classify_lesson_type,
)
from app.marcus.lesson_plan.prework_projection import SceneBrief, SceneComposeRequest
from app.marcus.lesson_plan.scene_extraction import (
    SCENE_SOURCE_REQUEST_MARKER,
    SceneProjectionRequest,
    SceneProjectionResult,
    SceneSeed,
    compose_scene_projection,
    normalize_scene_candidates,
    select_scene_seed,
)

ROOT = Path(__file__).resolve().parents[4]
FIXTURES = ROOT / "tests" / "fixtures" / "prework_36_2"


def _load(name: str) -> SceneProjectionRequest:
    return SceneProjectionRequest.model_validate_json(
        (FIXTURES / f"{name}.json").read_text(encoding="utf-8")
    )


class _SpyComposer:
    def __init__(self, text: str | None = None) -> None:
        self.requests: list[SceneComposeRequest] = []
        self.text = text

    def __call__(self, request: SceneComposeRequest) -> SceneBrief:
        self.requests.append(request)
        return SceneBrief(
            status="authored",
            text=self.text or request.seed_text,
            source_refs=request.source_refs,
            known_losses=(),
            marker=None,
            lesson_type=request.lesson_type,
            archetype=request.archetype,
        )


def test_fixture_families_are_strict_round_trippable_and_receipts_deterministic() -> None:
    for name in ("part2_gem", "part4_bridge", "skill_build", "ambiguous_boundary"):
        raw = (FIXTURES / f"{name}.json").read_text(encoding="utf-8")
        request = SceneProjectionRequest.model_validate_json(raw)
        assert SceneProjectionRequest.model_validate_json(request.model_dump_json()) == request
        json.dumps(request.model_dump(mode="json"), sort_keys=True)

    receipt = classify_lesson_type(_load("part2_gem").lesson_type_evidence)
    assert receipt.model_dump_json() == receipt.model_dump_json()


def test_fixture_families_pin_selection_classification_gates_and_losses() -> None:
    for name in ("part2_gem", "part4_bridge", "skill_build", "ambiguous_boundary"):
        expected = json.loads((FIXTURES / f"{name}.expected.json").read_text(encoding="utf-8"))
        result = compose_scene_projection(_load(name), _SpyComposer())
        assert {
            "selected_seed_id": result.selected_seed_id,
            "classification_status": result.classification.status,
            "lesson_type": result.classification.lesson_type,
            "archetype": result.classification.archetype,
            "scene_status": result.scene.status,
            "failures": list(result.gate_receipt.failures),
        } == expected


@pytest.mark.parametrize(
    ("flags", "status", "lesson_type", "archetype", "confidence"),
    [
        ((True, False, False), "decisive", "fresh_pain", "external_friction", 1.0),
        ((False, True, False), "decisive", "bridge_identity", "introspective_threshold", 1.0),
        ((False, False, True), "decisive", "skill_build", "difficulty_practice", 1.0),
        ((False, False, False), "insufficient", None, None, None),
        ((True, True, False), "ambiguous", None, None, None),
        ((True, True, True), "ambiguous", None, None, None),
    ],
)
def test_pure_classifier_has_closed_no_tiebreak_truth_table(
    flags: tuple[bool, bool, bool],
    status: str,
    lesson_type: str | None,
    archetype: str | None,
    confidence: float | None,
) -> None:
    evidence = LessonTypeEvidence(
        fresh_pain=flags[0],
        bridge_identity=flags[1],
        skill_build=flags[2],
        evidence_refs=("assessment:q5",),
    )
    receipt = classify_lesson_type(evidence)
    assert (receipt.status, receipt.lesson_type, receipt.archetype, receipt.confidence) == (
        status,
        lesson_type,
        archetype,
        confidence,
    )


def test_part2_selects_actual_q5_scenario_before_generic_narration() -> None:
    request = _load("part2_gem")
    selected = select_scene_seed(request)
    assert selected.seed_id == "chapter-2-q5"
    assert selected.source_ref.endswith("chapter-2-knowledge-check.md#q5")
    assert selected.sme_scenario is True


def test_selection_is_lexical_within_priority_and_duplicate_inventory_is_invalid() -> None:
    request = _load("part2_gem")
    seeds = (
        SceneSeed(
            seed_id="z",
            text="Scenario z",
            source_ref="ref:b",
            source_kind="assessment_scenario",
            slide_key=None,
            sme_scenario=True,
        ),
        SceneSeed(
            seed_id="a",
            text="Scenario a",
            source_ref="ref:a",
            source_kind="assessment_scenario",
            slide_key=None,
            sme_scenario=True,
        ),
    )
    lexical = request.model_copy(update={"seeds": seeds, "candidate_ids": ("z", "a")})
    assert select_scene_seed(lexical).seed_id == "a"
    with pytest.raises(ValidationError):
        SceneProjectionRequest.model_validate(
            request.model_dump(mode="python") | {"seeds": (request.seeds[0], request.seeds[0])}
        )


def test_sme_scenario_flag_cannot_be_attached_to_non_scenario_source() -> None:
    with pytest.raises(ValidationError):
        SceneSeed(
            seed_id="forged",
            text="Narration pretending to be an SME scenario.",
            source_ref="slide:1:narration",
            source_kind="slide_narration",
            slide_key="slide-01",
            sme_scenario=True,
        )


def test_adequate_request_forms_exact_closed_request_and_calls_composer_once() -> None:
    request = _load("part2_gem")
    spy = _SpyComposer(
        "A recurring patient transport delay is not an isolated mishap; it blocks discharge work."
    )
    result = compose_scene_projection(request, spy)
    assert result.scene.status == "authored"
    assert result.selected_seed_id == "chapter-2-q5"
    assert result.selected_seed_ref.endswith("chapter-2-knowledge-check.md#q5")
    assert result.gate_receipt.failures == ()
    assert len(spy.requests) == 1
    formed = spy.requests[0]
    assert formed.source_refs == (result.selected_seed_ref,)
    assert formed.lesson_type == "fresh_pain"
    assert formed.archetype == "external_friction"
    assert formed.payoff_slide_keys == request.payoff_slide_keys
    assert "actual_payoff_sufficiency_operator_check" in result.operator_warnings
    assert "semantic_faithfulness_operator_check" in result.operator_warnings


@pytest.mark.parametrize(
    ("fixture", "expected_status", "expected_loss", "calls"),
    [
        ("ambiguous_boundary", "degraded", "scene_lesson_type_ambiguous", 0),
        ("part4_bridge", "authored", None, 1),
    ],
)
def test_adequacy_paths_are_honest(
    fixture: str, expected_status: str, expected_loss: str | None, calls: int
) -> None:
    request = _load(fixture)
    spy = _SpyComposer()
    result = compose_scene_projection(request, spy)
    assert result.scene.status == expected_status
    assert len(spy.requests) == calls
    if expected_loss:
        assert expected_loss in result.gate_receipt.failures
        assert result.scene.text is None
        assert result.scene.marker == SCENE_SOURCE_REQUEST_MARKER


def test_part4_narrow_bridge_is_supported_but_full_deck_motion_degrades_precompose() -> None:
    narrow = _load("part4_bridge")
    spy = _SpyComposer()
    assert compose_scene_projection(narrow, spy).scene.status == "authored"
    broad = narrow.model_copy(
        update={"requested_coverage": "full_deck", "required_capabilities": ("scene", "motion")}
    )
    broad_spy = _SpyComposer()
    result = compose_scene_projection(broad, broad_spy)
    assert result.scene.status == "degraded"
    assert result.gate_receipt.failures == ("scene_source_scope_unsupported",)
    assert result.scene.marker == SCENE_SOURCE_REQUEST_MARKER
    assert broad_spy.requests == []


def test_absent_or_unresolved_source_is_unavailable_without_inference_or_call() -> None:
    request = _load("part2_gem")
    absent = request.model_copy(update={"seeds": (), "candidate_ids": ()})
    spy = _SpyComposer()
    result = compose_scene_projection(absent, spy)
    assert result.scene.status == "unavailable"
    assert result.gate_receipt.failures == (
        "scene_seed_unavailable",
        "scene_lesson_evidence_unresolved",
    )
    assert result.selected_seed_id is result.selected_seed_ref is None
    assert spy.requests == []
    unresolved = request.model_copy(update={"candidate_ids": ("missing",)})
    result = compose_scene_projection(unresolved, spy)
    assert result.scene.status == "unavailable"
    assert result.gate_receipt.failures == ("scene_candidate_unresolved", "scene_seed_unavailable")


def test_unresolvable_lesson_evidence_ref_degrades_before_composition() -> None:
    request = _load("part2_gem")
    evidence = request.lesson_type_evidence.model_copy(update={"evidence_refs": ("missing",)})
    request = request.model_copy(update={"lesson_type_evidence": evidence})
    spy = _SpyComposer()
    result = compose_scene_projection(request, spy)
    assert result.scene.status == "degraded"
    assert result.gate_receipt.failures == ("scene_lesson_evidence_unresolved",)
    assert spy.requests == []


def test_payoff_membership_is_separate_from_seed_provenance_and_fails_precompose() -> None:
    request = _load("part2_gem")
    bad = request.model_copy(update={"payoff_slide_keys": ("slide:not-in-inventory",)})
    spy = _SpyComposer()
    result = compose_scene_projection(bad, spy)
    assert result.scene.status == "degraded"
    assert result.gate_receipt.failures == ("scene_payoff_unresolved",)
    assert result.selected_seed_ref.endswith("#q5")
    assert spy.requests == []


@pytest.mark.parametrize(
    ("mutator", "loss"),
    [
        (lambda r: r.model_copy(update={"source_refs": ("wrong",)}), "scene_provenance_mismatch"),
        (
            lambda r: r.model_copy(update={"archetype": "difficulty_practice"}),
            "scene_archetype_mismatch",
        ),
        (
            lambda r: r.model_copy(update={"lesson_type": "skill_build"}),
            "scene_lesson_type_mismatch",
        ),
    ],
)
def test_postcompose_binding_and_archetype_mismatch_discards_authored_text(
    mutator, loss: str
) -> None:
    request = _load("part2_gem")

    def composer(formed: SceneComposeRequest) -> SceneBrief:
        valid = SceneBrief(
            status="authored",
            text=formed.seed_text,
            source_refs=formed.source_refs,
            known_losses=(),
            marker=None,
            lesson_type=formed.lesson_type,
            archetype=formed.archetype,
        )
        return mutator(valid)

    result = compose_scene_projection(request, composer)
    assert result.scene.status == "degraded"
    assert loss in result.gate_receipt.failures
    assert result.scene.text is None


@pytest.mark.parametrize(
    ("seed", "scene", "expected_loss"),
    [
        (
            "The team can't ignore 10 delayed transfers.",
            "The team can’t ignore 10 delayed transfers.",
            None,
        ),
        ("Never ignore 10 delayed transfers.", "Never overlook 10 delayed transfers.", None),
        (
            "Never ignore 10 delayed transfers.",
            "Ignore 10 delayed transfers.",
            "scene_faithfulness_negator",
        ),
        (
            "Never ignore 10 delayed transfers.",
            "Never ignore delayed transfers.",
            "scene_faithfulness_numeral",
        ),
        (
            "Never ignore 10 delayed transfers.",
            "Never ignore 11 delayed transfers.",
            "scene_faithfulness_numeral",
        ),
        (
            "Never ignore delayed transfers.",
            "Never ignore 10 delayed transfers.",
            "scene_faithfulness_numeral",
        ),
        (
            "Recurring transport delays block discharge.",
            "A musical interlude opens.",
            "scene_faithfulness_overlap",
        ),
    ],
)
def test_faithfulness_proxy_handles_normalization_anchors_and_overlap(
    seed: str, scene: str, expected_loss: str | None
) -> None:
    request = _load("skill_build")
    revised_seed = request.seeds[0].model_copy(update={"text": seed})
    request = request.model_copy(update={"seeds": (revised_seed,)})
    result = compose_scene_projection(request, _SpyComposer(scene))
    if expected_loss is None:
        assert result.scene.status == "authored"
    else:
        assert result.scene.status == "degraded"
        assert expected_loss in result.gate_receipt.failures


def test_word_digit_equivalence_is_warn_not_guessed_and_negation_scope_is_warn() -> None:
    request = _load("part4_bridge")
    result = compose_scene_projection(
        request, _SpyComposer("A champion influences 10% directly and 90% through others.")
    )
    assert result.scene.status == "authored"
    # Fixture seed deliberately uses digit forms, so only the general semantic warnings apply.
    assert "negation_scope_operator_check" not in result.operator_warnings
    word_seed = request.seeds[0].model_copy(update={"text": "Ten percent lead directly."})
    word_request = request.model_copy(update={"seeds": (word_seed,)})
    result = compose_scene_projection(word_request, _SpyComposer("10 percent lead directly."))
    assert result.scene.status == "authored"
    assert "word_digit_equivalence_operator_check" in result.operator_warnings


def test_reserved_heading_is_rejected_by_scene_contract() -> None:
    with pytest.raises(ValidationError):
        SceneBrief(
            status="authored",
            text="Grounded.\n\n## Promise\nForged",
            source_refs=("ref",),
            known_losses=(),
            marker=None,
            lesson_type="fresh_pain",
            archetype="external_friction",
        )


@pytest.mark.parametrize(
    ("payload", "model"),
    [
        (
            {
                "fresh_pain": 1,
                "bridge_identity": False,
                "skill_build": False,
                "evidence_refs": ("r",),
            },
            LessonTypeEvidence,
        ),
        (
            {
                "fresh_pain": True,
                "bridge_identity": False,
                "skill_build": False,
                "evidence_refs": ["r"],
            },
            LessonTypeEvidence,
        ),
        (
            {
                "seed_id": "x",
                "text": "t",
                "source_ref": "r",
                "source_kind": "made_up",
                "slide_key": None,
                "sme_scenario": False,
            },
            SceneSeed,
        ),
    ],
)
def test_new_contracts_reject_coercion_lists_extra_and_open_vocab(
    payload: dict, model: type
) -> None:
    with pytest.raises(ValidationError):
        model.model_validate(payload)


def test_result_serialization_and_m3_boundary() -> None:
    result = compose_scene_projection(_load("part2_gem"), _SpyComposer())
    assert SceneProjectionResult.model_validate_json(result.model_dump_json()) == result
    import app.marcus.lesson_plan.lesson_type_classifier as classifier
    import app.marcus.lesson_plan.scene_extraction as extraction

    denied = ("orchestrator", "specialists", "terminal", "render", "openai", "anthropic", "litellm")
    for module in (classifier, extraction):
        tree = ast.parse(inspect.getsource(module))
        imported = [
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        ] + [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        assert not any(term in name.lower() for name in imported for term in denied)


def test_real_fixture_coordinates_resolve_against_authoritative_course_sources() -> None:
    for name in ("part2_gem", "part4_bridge"):
        request = _load(name)
        coordinates = [seed.source_ref for seed in request.seeds]
        coordinates.extend(request.payoff_slide_inventory)
        for coordinate in coordinates:
            path_text, _, anchor = coordinate.partition("#")
            path = ROOT / path_text
            assert path.is_file(), coordinate
            if anchor:
                content = path.read_text(encoding="utf-8").lower().replace("**", "")
                assert anchor.lower() in content, coordinate


@pytest.mark.parametrize("wrong", [None, {}, "scene", object()])
def test_wrong_composer_return_type_degrades_contract_invalid(wrong: object) -> None:
    result = compose_scene_projection(
        _load("part2_gem"),
        lambda request: wrong,  # type: ignore[arg-type,return-value]
    )
    assert result.scene.status == "degraded"
    assert result.gate_receipt.failures == ("scene_composer_contract_invalid",)


def test_composer_runtime_exception_is_not_swallowed() -> None:
    def exploding(request: SceneComposeRequest) -> SceneBrief:
        del request
        raise RuntimeError("composer failed")

    with pytest.raises(RuntimeError, match="composer failed"):
        compose_scene_projection(_load("part2_gem"), exploding)


@pytest.mark.parametrize(
    ("lesson_type", "archetype"),
    [
        ("fresh_pain", "difficulty_practice"),
        ("bridge_identity", "external_friction"),
        ("skill_build", "introspective_threshold"),
    ],
)
def test_decisive_classification_rejects_mismatched_exact_mapping(
    lesson_type: str, archetype: str
) -> None:
    with pytest.raises(ValidationError):
        LessonTypeClassification(
            status="decisive",
            lesson_type=lesson_type,
            archetype=archetype,
            confidence=1.0,
            evidence_refs=("ref",),
        )


@pytest.mark.parametrize("refs", [(), ("ref", "ref")])
def test_classification_receipt_requires_nonempty_unique_evidence_refs(
    refs: tuple[str, ...],
) -> None:
    with pytest.raises(ValidationError):
        LessonTypeClassification(
            status="insufficient",
            lesson_type=None,
            archetype=None,
            confidence=None,
            evidence_refs=refs,
        )


@pytest.mark.parametrize(
    ("seed", "scene", "expected_loss"),
    [
        (
            "Ten cases and 7 delays remain.",
            "10 cases and 8 delays remain.",
            "scene_faithfulness_numeral",
        ),
        ("Ten cases and 7 delays remain.", "10 cases and 7 delays remain.", None),
        ("There are 7 delays.", "There are 7 and 7 delays.", "scene_faithfulness_numeral"),
        ("There are 7 delays.", "There are delays.", "scene_faithfulness_numeral"),
        ("There are delays.", "There are 7 delays.", "scene_faithfulness_numeral"),
        ("Teams improve flow.", "Teams do not improve flow.", "scene_faithfulness_negator"),
        ("Never ignore delays.", "Never never ignore delays.", "scene_faithfulness_negator"),
    ],
)
def test_protected_anchor_multisets_and_mixed_word_digit_uncertainty(
    seed: str, scene: str, expected_loss: str | None
) -> None:
    request = _load("skill_build")
    seed_model = request.seeds[0].model_copy(update={"text": seed})
    request = request.model_copy(update={"seeds": (seed_model,)})
    result = compose_scene_projection(request, _SpyComposer(scene))
    if expected_loss is None:
        assert result.scene.status == "authored"
        assert "word_digit_equivalence_operator_check" in result.operator_warnings
    else:
        assert result.scene.status == "degraded"
        assert expected_loss in result.gate_receipt.failures


@pytest.mark.parametrize(
    ("seed", "scene"),
    [
        ("Équipes améliorent le débit clinique.", "Équipes améliorent le débit clinique."),
        ("患者搬送の遅延が退院を妨げる。", "患者搬送の遅延は退院を妨げる。"),
    ],
)
def test_unicode_alphanumeric_faithfulness_does_not_false_degrade(seed: str, scene: str) -> None:
    request = _load("skill_build")
    seed_model = request.seeds[0].model_copy(update={"text": seed})
    request = request.model_copy(update={"seeds": (seed_model,)})
    assert compose_scene_projection(request, _SpyComposer(scene)).scene.status == "authored"


def test_raw_candidate_normalization_excludes_bad_inputs_with_stable_losses() -> None:
    base = _load("skill_build")
    valid = base.seeds[0].model_dump(mode="python")
    raw = (
        valid,
        valid | {"seed_id": " "},
        {key: value for key, value in valid.items() if key != "source_ref"},
        valid | {"seed_id": "bad-kind", "source_kind": "unknown"},
    )
    receipt = normalize_scene_candidates(raw)
    assert receipt.seeds == base.seeds
    assert receipt.rejection_losses == (
        "scene_candidate_blank:1",
        "scene_candidate_unreferenced:2",
        "scene_candidate_malformed:3",
    )
    request = SceneProjectionRequest.from_raw_candidates(
        raw_candidates=raw,
        candidate_ids=("procedure-delay-practice",),
        lesson_type_evidence=base.lesson_type_evidence,
        payoff_slide_inventory=base.payoff_slide_inventory,
        payoff_slide_keys=base.payoff_slide_keys,
        requested_coverage=base.requested_coverage,
        required_capabilities=base.required_capabilities,
        available_coverage=base.available_coverage,
        available_capabilities=base.available_capabilities,
    )
    result = compose_scene_projection(request, _SpyComposer())
    assert result.scene.status == "authored"
    assert result.extraction_losses == receipt.rejection_losses
