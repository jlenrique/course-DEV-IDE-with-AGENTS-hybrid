"""Story 37.3 retrieval, grounding, and anti-forgery contract tests."""

from __future__ import annotations

import ast
import json
from collections.abc import Callable
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.marcus.lesson_plan.check_on_learning_projection import (
    CHECK_DEGRADED_MARKER,
    CHECK_UNAVAILABLE_MARKER,
    CheckAnswerClaim,
    CheckOnLearningRequest,
    CheckOnLearningResult,
    CheckOnLearningWriterCandidate,
    CheckSourceClaim,
    CheckSourceSpan,
    RetrievalCheckItem,
    check_authority_digest,
    check_candidate_digest,
    compose_check_on_learning,
    offline_check_on_learning_writer,
)
from app.marcus.lesson_plan.prework_projection import PromiseProjection, PromiseVow
from app.marcus.lesson_plan.promise_projection import (
    PromiseGateReceipt,
    PromiseProjectionResult,
)

ROOT = Path(__file__).resolve().parents[4]
FIXTURES = ROOT / "tests" / "fixtures" / "check_on_learning_37_3"
MODULE = ROOT / "app" / "marcus" / "lesson_plan" / "check_on_learning_projection.py"


def _promise(status: str = "authored") -> PromiseProjectionResult:
    if status == "authored":
        return PromiseProjectionResult(
            projection=PromiseProjection(
                status="authored",
                vows=(
                    PromiseVow(objective_id="ability-a", text="distinguish causes"),
                    PromiseVow(objective_id="ability-b", text="choose a first move"),
                ),
                known_losses=(),
                marker=None,
            ),
            gate_receipt=PromiseGateReceipt(),
            authority_refs=("ratified-los.json#ratified_los/0", "ratified-los.json#ratified_los/1"),
        )
    loss = f"promise_{status}"
    return PromiseProjectionResult(
        projection=PromiseProjection(
            status=status,
            vows=(),
            known_losses=(loss,),
            marker="promise_semantics_not_authored",
        ),
        gate_receipt=PromiseGateReceipt(failures=(loss,)),
    )


def _request(*, promise_status: str = "authored", thin: bool = False) -> CheckOnLearningRequest:
    claims = (
        CheckSourceClaim(
            claim_id="claim-a",
            text="A recurring delay indicates a system-design cause, not an isolated symptom.",
            source_span_refs=("span-a",),
            ability_refs=("ability-a",),
        ),
        CheckSourceClaim(
            claim_id="claim-b",
            text="The first move is to map the handoff before choosing an intervention.",
            source_span_refs=("span-b",),
            ability_refs=("ability-b",),
        ),
    )
    if thin:
        claims = claims[:1]
    spans = (
        CheckSourceSpan(span_id="span-a", text="source A", source_ref="narration#1"),
        CheckSourceSpan(span_id="span-b", text="source B", source_ref="narration#2"),
    )
    if promise_status != "authored":
        claims = ()
        spans = ()
    return CheckOnLearningRequest(
        lesson_ref="part-2",
        promise=_promise(promise_status),
        quantity_unit_tokens=(
            "mg", "%", "kg", "°C", "mol/L", "mol⁻¹", "m·s⁻²",
            "kg/m²/day", "m s⁻²", "Ω", "V",
        ),
        source_spans=spans,
        source_claims=claims,
    )


def _candidate() -> CheckOnLearningWriterCandidate:
    return CheckOnLearningWriterCandidate(
        status="authored",
        items=(
            RetrievalCheckItem(
                item_id="item-a",
                ability_id="ability-a",
                prompt="What distinction would diagnose the recurring delay?",
                expected_answer=(
                    "Treat the recurring delay as a system-design cause, not an isolated symptom."
                ),
                answer_claims=(
                    CheckAnswerClaim(
                        answer_claim_id="answer-a",
                        text=(
                            "Treat the recurring delay as a system-design cause, "
                            "not an isolated symptom."
                        ),
                        source_claim_ref="claim-a",
                        source_span_refs=("span-a",),
                    ),
                ),
            ),
            RetrievalCheckItem(
                item_id="item-b",
                ability_id="ability-b",
                prompt="What should you do first at the handoff?",
                expected_answer="First, map the handoff before choosing an intervention.",
                answer_claims=(
                    CheckAnswerClaim(
                        answer_claim_id="answer-b",
                        text="First, map the handoff before choosing an intervention.",
                        source_claim_ref="claim-b",
                        source_span_refs=("span-b",),
                    ),
                ),
            ),
        ),
        known_losses=(),
        marker=None,
    )


def _request_raw() -> dict:
    return _request().model_dump(mode="python")


def _candidate_raw() -> dict:
    return _candidate().model_dump(mode="python")


def test_eligible_writer_is_called_once_and_every_vow_is_grounded() -> None:
    calls = 0

    def writer(request: CheckOnLearningRequest) -> CheckOnLearningWriterCandidate:
        nonlocal calls
        calls += 1
        assert tuple(v.objective_id for v in request.promise.projection.vows) == (
            "ability-a",
            "ability-b",
        )
        return _candidate()

    result = compose_check_on_learning(_request(), writer)
    assert calls == 1
    assert result.status == "authored"
    assert result.items == _candidate().items
    assert result.gate.status == "pass"
    assert result.gate.declared_ability_ids == ("ability-a", "ability-b")
    assert result.gate.covered_ability_ids == ("ability-a", "ability-b")
    assert result.gate.missing_ability_ids == ()


@pytest.mark.parametrize(
    ("request_factory", "status", "loss", "marker"),
    [
        (
            lambda: _request(promise_status="unavailable"),
            "unavailable",
            "check_promise_authority_unavailable",
            CHECK_UNAVAILABLE_MARKER,
        ),
        (
            lambda: _request(promise_status="degraded"),
            "degraded",
            "check_promise_authority_degraded",
            CHECK_DEGRADED_MARKER,
        ),
        (
            lambda: CheckOnLearningRequest(
                lesson_ref="part-2",
                promise=_promise(),
                quantity_unit_tokens=(),
                source_spans=(),
                source_claims=(),
            ),
            "unavailable",
            "check_source_unavailable",
            CHECK_UNAVAILABLE_MARKER,
        ),
        (
            lambda: _request(thin=True),
            "degraded",
            "check_missing_ability_proof",
            CHECK_DEGRADED_MARKER,
        ),
    ],
)
def test_ineligible_authority_is_honest_and_never_calls_writer(
    request_factory: Callable[[], CheckOnLearningRequest],
    status: str,
    loss: str,
    marker: str,
) -> None:
    called = False

    def writer(request: CheckOnLearningRequest) -> CheckOnLearningWriterCandidate:
        del request
        nonlocal called
        called = True
        return _candidate()

    result = compose_check_on_learning(request_factory(), writer)
    assert called is False
    assert result.status == status
    assert result.items == ()
    assert result.known_losses == (loss,)
    assert result.marker == marker
    assert result.candidate_snapshot is None


def test_offline_writer_is_deterministic_and_honest() -> None:
    assert offline_check_on_learning_writer(_request()) == offline_check_on_learning_writer(
        _request()
    )


def test_models_are_strict_frozen_extra_forbid_and_round_trip() -> None:
    request = _request()
    assert (
        CheckOnLearningRequest.model_validate_json(request.model_dump_json(), strict=True)
        == request
    )
    with pytest.raises(ValidationError):
        CheckSourceSpan(span_id=1, text="x", source_ref="y")  # type: ignore[arg-type]
    with pytest.raises(ValidationError):
        CheckSourceSpan(span_id="x", text="y", source_ref="z", extra="no")  # type: ignore[call-arg]
    with pytest.raises(ValidationError):
        request.lesson_ref = "changed"  # type: ignore[misc]


def test_constructed_request_and_candidate_are_revalidated() -> None:
    forged_request = CheckOnLearningRequest.model_construct(
        lesson_ref="part-2",
        promise=_promise(),
        source_spans=(),
        source_claims=(_request().source_claims[0],),
    )
    with pytest.raises(ValidationError):
        compose_check_on_learning(forged_request, lambda _: _candidate())
    forged_candidate = CheckOnLearningWriterCandidate.model_construct(
        status="authored", items=(), known_losses=(), marker=None
    )
    with pytest.raises(ValidationError):
        compose_check_on_learning(_request(), lambda _: forged_candidate)


def test_result_revalidation_defeats_forged_receipt_and_snapshot() -> None:
    result = compose_check_on_learning(_request(), lambda _: _candidate())
    payload = result.model_dump(mode="python")
    payload["gate"]["covered_ability_ids"] = ("ability-a",)
    with pytest.raises(ValidationError):
        CheckOnLearningResult.model_validate(payload, strict=True)


def test_structured_fixture_exact_dump_schema_round_trip_and_semantic_manifest() -> None:
    request_json = (FIXTURES / "request.json").read_text(encoding="utf-8")
    candidate_json = (FIXTURES / "writer_candidate.json").read_text(encoding="utf-8")
    request = CheckOnLearningRequest.model_validate_json(request_json, strict=True)
    candidate = CheckOnLearningWriterCandidate.model_validate_json(candidate_json, strict=True)
    assert request.model_dump(mode="json") == json.loads(request_json)
    assert candidate.model_dump(mode="json") == json.loads(candidate_json)
    result = compose_check_on_learning(request, lambda _: candidate)
    assert result.status == "authored"
    assert (
        CheckOnLearningResult.model_validate_json(result.model_dump_json(), strict=True) == result
    )
    assert result.authority_digest == check_authority_digest(request)
    assert result.candidate_digest == check_candidate_digest(candidate)
    schema = CheckOnLearningResult.model_json_schema()
    assert schema["additionalProperties"] is False
    assert all(
        definition.get("type") != "object" or definition.get("additionalProperties") is False
        for definition in schema["$defs"].values()
    )
    manifest = json.loads((FIXTURES / "semantic_manifest.json").read_text(encoding="utf-8"))
    request_schema = CheckOnLearningRequest.model_json_schema()
    assert "quantity_unit_tokens" in request_schema["required"]
    assert request_schema["properties"]["quantity_unit_tokens"]["type"] == "array"
    assert manifest["gate_version"] == "check-on-learning-gate.v1"
    assert manifest["declared_abilities"] == ["ability-a", "ability-b"]
    assert manifest["declared_quantity_unit_tokens"] == list(request.quantity_unit_tokens)
    assert "Story 37.5" in manifest["fixture_scope"]


@pytest.mark.parametrize(
    ("factory", "payload"),
    [
        (CheckSourceSpan, {"span_id": " ", "text": "x", "source_ref": "r"}),
        (CheckSourceSpan, {"span_id": "s", "text": 1, "source_ref": "r"}),
        (
            CheckSourceClaim,
            {
                "claim_id": "c",
                "text": "x",
                "source_span_refs": (),
                "ability_refs": ("ability-a",),
            },
        ),
        (
            CheckAnswerClaim,
            {
                "answer_claim_id": "a",
                "text": "x",
                "source_claim_ref": "c",
                "source_span_refs": (),
            },
        ),
        (
            RetrievalCheckItem,
            {
                "item_id": "i",
                "ability_id": "a",
                "prompt": "p",
                "expected_answer": "e",
                "answer_claims": (),
                "extra": True,
            },
        ),
    ],
)
def test_atomic_contracts_reject_blank_coercion_empty_refs_and_extras(
    factory: type, payload: dict
) -> None:
    with pytest.raises(ValidationError):
        factory.model_validate(payload, strict=True)


def test_request_rejects_duplicate_and_unknown_authority_refs() -> None:
    cases = []
    raw = _request_raw()
    raw["source_spans"] += (raw["source_spans"][0],)
    cases.append((raw, "source span IDs"))
    raw = _request_raw()
    raw["source_spans"][1]["source_ref"] = raw["source_spans"][0]["source_ref"]
    cases.append((raw, "source refs"))
    raw = _request_raw()
    raw["source_claims"] += (raw["source_claims"][0],)
    cases.append((raw, "source claim IDs"))
    raw = _request_raw()
    raw["source_claims"][0]["source_span_refs"] = ("unknown",)
    cases.append((raw, "unknown span"))
    raw = _request_raw()
    raw["source_claims"][0]["ability_refs"] = ("unknown",)
    cases.append((raw, "unknown ability"))
    raw = _request_raw()
    raw["source_claims"][0]["ability_refs"] = ("ability-a", "ability-a")
    cases.append((raw, "duplicate ability refs"))
    for payload, match in cases:
        with pytest.raises(ValidationError, match=match):
            CheckOnLearningRequest.model_validate(payload, strict=True)


def test_promise_is_the_only_ability_authority_and_constructed_snapshot_fails() -> None:
    assert "abilities" not in CheckOnLearningRequest.model_fields
    raw = _request_raw()
    raw["promise"]["projection"]["vows"] += (raw["promise"]["projection"]["vows"][0],)
    raw["promise"]["authority_refs"] += ("ratified-los.json#ratified_los/2",)
    with pytest.raises(ValidationError, match="Promise ability IDs"):
        CheckOnLearningRequest.model_validate(raw, strict=True)

    forged = _promise().model_copy(
        update={"gate_receipt": PromiseGateReceipt(failures=("forged",))}
    )
    raw = _request_raw()
    raw["promise"] = forged
    with pytest.raises(ValidationError, match="empty upstream gate"):
        CheckOnLearningRequest.model_validate(raw, strict=True)

    raw = _request_raw()
    raw["promise"]["authority_refs"] = ("same", "same")
    with pytest.raises(ValidationError, match="Promise authority refs"):
        CheckOnLearningRequest.model_validate(raw, strict=True)


@pytest.mark.parametrize("missing", ["ability-a", "ability-b"])
def test_removing_each_promised_ability_proof_pre_gates_exactly(missing: str) -> None:
    raw = _request_raw()
    raw["source_claims"] = tuple(
        claim for claim in raw["source_claims"] if missing not in claim["ability_refs"]
    )
    result = compose_check_on_learning(
        CheckOnLearningRequest.model_validate(raw, strict=True), lambda _: _candidate()
    )
    assert result.status == "degraded"
    assert result.items == ()
    assert result.candidate_snapshot is None
    assert result.gate.missing_ability_ids == (missing,)
    assert result.gate.covered_ability_ids == tuple(
        ability for ability in ("ability-a", "ability-b") if ability != missing
    )


def test_empty_source_receipt_names_every_missing_vow() -> None:
    request = CheckOnLearningRequest(
        lesson_ref="part-2",
        promise=_promise(),
        quantity_unit_tokens=(),
        source_spans=(),
        source_claims=(),
    )
    result = compose_check_on_learning(request, lambda _: _candidate())
    assert result.status == "unavailable"
    assert result.gate.covered_ability_ids == ()
    assert result.gate.missing_ability_ids == ("ability-a", "ability-b")
    assert result.gate.failures == ("source_authority_unavailable",)


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("reordered_items", "ability_order_mismatch"),
        ("unknown_ability", "unknown_ability_reference"),
        ("unknown_claim", "unknown_claim_reference"),
        ("unknown_span", "unknown_source_reference"),
        ("wrong_span_set", "source_trace_mismatch"),
        ("permission", "ability_permission_mismatch"),
        ("answer_divergence", "answer_claim_composition_failed"),
    ],
)
def test_candidate_reference_order_and_composition_mutations_fail_closed(
    mutation: str, expected: str
) -> None:
    raw = _candidate_raw()
    if mutation == "reordered_items":
        raw["items"] = tuple(reversed(raw["items"]))
    elif mutation == "unknown_ability":
        raw["items"][0]["ability_id"] = "ability-unknown"
    elif mutation == "unknown_claim":
        raw["items"][0]["answer_claims"][0]["source_claim_ref"] = "claim-unknown"
    elif mutation == "unknown_span":
        raw["items"][0]["answer_claims"][0]["source_span_refs"] = ("span-unknown",)
    elif mutation == "wrong_span_set":
        raw["items"][0]["answer_claims"][0]["source_span_refs"] = ("span-b",)
    elif mutation == "permission":
        raw["items"][0]["answer_claims"][0]["source_claim_ref"] = "claim-b"
        raw["items"][0]["answer_claims"][0]["source_span_refs"] = ("span-b",)
        raw["items"][0]["answer_claims"][0]["text"] = (
            "First, map the handoff before choosing an intervention."
        )
        raw["items"][0]["expected_answer"] = raw["items"][0]["answer_claims"][0]["text"]
    else:
        raw["items"][0]["expected_answer"] += " Hidden prose."
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    result = compose_check_on_learning(_request(), lambda _: candidate)
    assert result.status in {"degraded", "unavailable"}
    assert result.items == ()
    assert expected in result.gate.failures


def test_duplicate_item_and_atomic_answer_ids_are_rejected() -> None:
    raw = _candidate_raw()
    raw["items"] += (raw["items"][0],)
    with pytest.raises(ValidationError, match="item IDs"):
        CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    raw = _candidate_raw()
    raw["items"][1]["answer_claims"][0]["answer_claim_id"] = "answer-a"
    with pytest.raises(ValidationError, match="answer claim IDs"):
        CheckOnLearningWriterCandidate.model_validate(raw, strict=True)


@pytest.mark.parametrize(
    "prompt",
    [
        "A) symptom B) cause",
        "(A) symptom (B) cause",
        "Choose an option: symptom or cause.",
        "True or false: the delay is isolated.",
        "Hint: think about the handoff.",
        "Reread the source and answer.",
        "Review this transcript before answering.",
        "According to the transcript, what happened?",
        "What does this slide show?",
        "Correct answer: map the handoff.",
        "Solution: map the handoff.",
        "Transcript: the handoff is delayed.",
        "What is shown on slide 3?",
        "# Answer this question",
        "> What happened?",
        "- What happened?",
        "1. What happened?",
    ],
)
def test_choice_hint_reread_deixis_and_injection_prompts_fail(prompt: str) -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = prompt
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    result = compose_check_on_learning(_request(), lambda _: candidate)
    assert "retrieval_posture_failed" in result.gate.failures


def test_prompt_newline_is_rejected_and_complete_answer_or_source_copy_fails() -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = "Question?\nAnswer here."
    with pytest.raises(ValidationError):
        CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    for copied in (
        _candidate().items[0].expected_answer,
        _request().source_claims[0].text,
    ):
        raw = _candidate_raw()
        raw["items"][0]["prompt"] = f"Explain why: {copied}"
        result = compose_check_on_learning(
            _request(),
            lambda _, raw=raw: CheckOnLearningWriterCandidate.model_validate(raw, strict=True),
        )
        assert "answer_leakage_failed" in result.gate.failures


@pytest.mark.parametrize(
    ("source", "same", "different"),
    [
        ("Dose 5 mg then 10 mg.", "Use 5mg and then 10mg.", "Use 10mg and then 5mg."),
        ("Rate .5% to 2.0%.", "Keep .5 % to 2.0 %.", "Keep 0.5% to 2.0%."),
        ("Keep 3–5 kg.", "Maintain 3—5kg.", "Maintain 3-6kg."),
        ("Use twenty-one steps.", "Apply twenty one steps.", "Apply twenty-two steps."),
        (
            "The first move has two stages.",
            "Use the first move in two stages.",
            "Use the second move in two stages.",
        ),
        ("Hold at −5 °C.", "Maintain -5°C.", "Maintain 5°C."),
        ("Use 1.25e−3 mol/L.", "Apply 1.25E-3mol/L.", "Apply 1.25e-2 mol/L."),
        ("Use 6.02 × 10^23 mol⁻¹.", "Apply 6.02×10^23mol⁻¹.", "Apply 6.02×10^22mol⁻¹."),
        ("Acceleration is 9.81 m·s⁻².", "Use 9.81m·s⁻².", "Use 9.81m/s."),
        ("Rate is 4 kg/m²/day.", "Maintain 4kg/m²/day.", "Maintain 4kg/m²."),
    ],
)
def test_atomic_ordered_quantity_fidelity(source: str, same: str, different: str) -> None:
    request_raw = _request_raw()
    request_raw["source_claims"][0]["text"] = source
    request = CheckOnLearningRequest.model_validate(request_raw, strict=True)
    for answer, should_pass in ((same, True), (different, False)):
        candidate_raw = _candidate_raw()
        candidate_raw["items"][0]["answer_claims"][0]["text"] = answer
        candidate_raw["items"][0]["expected_answer"] = answer
        candidate = CheckOnLearningWriterCandidate.model_validate(candidate_raw, strict=True)
        result = compose_check_on_learning(request, lambda _, value=candidate: value)
        assert ("numeric_fidelity_failed" not in result.gate.failures) is should_pass


@pytest.mark.parametrize(
    ("source", "same", "different"),
    [
        (
            "Do not treat the symptom as the cause.",
            "Do not treat it as the cause.",
            "Treat it as the cause.",
        ),
        ("Never skip the handoff.", "Never skip it.", "Skip it."),
        ("Proceed without assuming intent.", "Act without assuming intent.", "Assume intent."),
        (
            "Neither signal nor delay proves cause.",
            "Neither signal nor delay proves it.",
            "The signal and delay prove it.",
        ),
    ],
)
def test_atomic_bounded_negation_fidelity(source: str, same: str, different: str) -> None:
    request_raw = _request_raw()
    request_raw["source_claims"][0]["text"] = source
    request = CheckOnLearningRequest.model_validate(request_raw, strict=True)
    for answer, should_pass in ((same, True), (different, False)):
        candidate_raw = _candidate_raw()
        candidate_raw["items"][0]["answer_claims"][0]["text"] = answer
        candidate_raw["items"][0]["expected_answer"] = answer
        candidate = CheckOnLearningWriterCandidate.model_validate(candidate_raw, strict=True)
        result = compose_check_on_learning(request, lambda _, value=candidate: value)
        assert ("negation_fidelity_failed" not in result.gate.failures) is should_pass


def test_multiple_items_per_vow_shared_authority_and_orphans_are_allowed() -> None:
    candidate_raw = _candidate_raw()
    second_a = json.loads(json.dumps(candidate_raw["items"][0]))
    second_a["item_id"] = "item-a-2"
    second_a["answer_claims"][0]["answer_claim_id"] = "answer-a-2"
    second_a["answer_claims"][0]["source_span_refs"] = tuple(
        second_a["answer_claims"][0]["source_span_refs"]
    )
    second_a["answer_claims"] = tuple(second_a["answer_claims"])
    second_a["prompt"] = "How would you classify the delay before proposing a fix?"
    candidate_raw["items"] = (
        candidate_raw["items"][0],
        second_a,
        candidate_raw["items"][1],
    )
    assert (
        compose_check_on_learning(
            _request(),
            lambda _: CheckOnLearningWriterCandidate.model_validate(candidate_raw, strict=True),
        ).status
        == "authored"
    )

    request_raw = _request_raw()
    request_raw["source_spans"] += (
        {"span_id": "span-orphan-α", "text": "Café context.", "source_ref": "narration#α"},
    )
    request_raw["source_claims"][1]["ability_refs"] = (
        "ability-a",
        "ability-b",
    )
    request = CheckOnLearningRequest.model_validate(request_raw, strict=True)
    candidate_raw = _candidate_raw()
    candidate_raw["items"][0]["answer_claims"] = (
        {
            "answer_claim_id": "answer-a",
            "text": "First, map the handoff before choosing an intervention.",
            "source_claim_ref": "claim-b",
            "source_span_refs": ("span-b",),
        },
    )
    candidate_raw["items"][0]["expected_answer"] = candidate_raw["items"][0]["answer_claims"][0][
        "text"
    ]
    candidate = CheckOnLearningWriterCandidate.model_validate(candidate_raw, strict=True)
    assert compose_check_on_learning(request, lambda _: candidate).status == "authored"


def test_wrong_return_exception_policy_and_non_authored_candidate_snapshot() -> None:
    with pytest.raises(TypeError, match="CheckOnLearningWriterCandidate"):
        compose_check_on_learning(_request(), lambda _: {})  # type: ignore[arg-type,return-value]

    def exploding(_: CheckOnLearningRequest) -> CheckOnLearningWriterCandidate:
        raise RuntimeError("writer exploded")

    with pytest.raises(RuntimeError, match="writer exploded"):
        compose_check_on_learning(_request(), exploding)
    result = compose_check_on_learning(_request(), offline_check_on_learning_writer)
    assert result.status == "unavailable"
    assert result.items == ()
    assert result.candidate_snapshot == offline_check_on_learning_writer(_request())
    assert result.known_losses == ("check_writer_unavailable",)

    contradictory = offline_check_on_learning_writer(_request()).model_dump(mode="python")
    contradictory["status"] = "degraded"
    contradictory["marker"] = CHECK_DEGRADED_MARKER
    with pytest.raises(ValidationError, match="canonical typed loss"):
        CheckOnLearningWriterCandidate.model_validate(contradictory, strict=True)


@pytest.mark.parametrize(
    "generic",
    [
        "Pending",
        "It depends.",
        "Cannot determine.",
        "Insufficient information.",
        "Not enough information.",
    ],
)
def test_pending_or_generic_answers_cannot_be_authored(generic: str) -> None:
    raw = _candidate_raw()
    raw["items"][0]["answer_claims"][0]["text"] = generic
    raw["items"][0]["expected_answer"] = generic
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    result = compose_check_on_learning(_request(), lambda _: candidate)
    assert "unusable_answer_failed" in result.gate.failures


def test_pre_gate_candidate_presence_and_eligible_absence_are_both_rejected() -> None:
    pre_gate = compose_check_on_learning(
        CheckOnLearningRequest(
            lesson_ref="part-2",
            promise=_promise(),
            quantity_unit_tokens=(),
            source_spans=(),
            source_claims=(),
        ),
        lambda _: _candidate(),
    )
    payload = pre_gate.model_dump(mode="python")
    payload["candidate_snapshot"] = _candidate().model_dump(mode="python")
    payload["candidate_digest"] = check_candidate_digest(_candidate())
    with pytest.raises(ValidationError):
        CheckOnLearningResult.model_validate(payload, strict=True)

    eligible = compose_check_on_learning(_request(), lambda _: _candidate())
    payload = eligible.model_dump(mode="python")
    payload["candidate_snapshot"] = None
    payload["candidate_digest"] = "sha256:" + "0" * 64
    with pytest.raises(ValidationError, match="candidate snapshot"):
        CheckOnLearningResult.model_validate(payload, strict=True)


def test_self_consistent_forged_pass_with_unsupported_answer_still_fails() -> None:
    baseline = compose_check_on_learning(_request(), lambda _: _candidate())
    raw = _candidate_raw()
    raw["items"][0]["answer_claims"][0]["text"] = "An unrelated sourced fact."
    raw["items"][0]["expected_answer"] = "An unrelated sourced fact."
    unsupported = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    rejected = compose_check_on_learning(_request(), lambda _: unsupported)
    assert rejected.status == "degraded"
    forged = baseline.model_dump(mode="python")
    forged["items"] = raw["items"]
    forged["candidate_snapshot"] = raw
    forged["candidate_digest"] = rejected.candidate_digest
    forged["gate"]["candidate_digest"] = rejected.candidate_digest
    with pytest.raises(ValidationError, match="deterministic replay"):
        CheckOnLearningResult.model_validate(forged, strict=True)


def test_review_reexports_dedicated_types_without_replacing_legacy_seam() -> None:
    from app.marcus.lesson_plan import review_projection

    assert review_projection.CheckOnLearningRequest is CheckOnLearningRequest
    assert review_projection.CheckOnLearningWriterCandidate is CheckOnLearningWriterCandidate
    assert review_projection.CheckWriter.__name__ == "CheckWriter"
    assert review_projection.offline_check_writer.__name__ == "offline_check_writer"
    brief = review_projection.build_review_brief(None)
    assert brief.check_on_learning.status == "pending"
    assert brief.check_on_learning.content is None


def test_m3_boundary_has_no_runtime_research_render_or_global_state_dependencies() -> None:
    source = MODULE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    forbidden = {
        "openai",
        "litellm",
        "langchain",
        "langgraph",
        "orchestrator",
        "specialists",
        "research_packet",
        "workbook_producer",
        "deep_dive_projection",
        "docx",
    }
    assert not {name for name in imports if any(token in name for token in forbidden)}
    calls = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert not calls & {"open", "Path", "getenv"}
    fields = set(CheckOnLearningRequest.model_fields) | set(
        CheckOnLearningWriterCandidate.model_fields
    )
    assert not fields & {
        "research_packet",
        "ask_a",
        "ask_b",
        "citations",
        "references",
        "model",
        "run_dir",
        "filesystem_path",
        "learner_response",
    }


@pytest.mark.parametrize("leaf", ["span", "claim", "answer_claim", "item"])
def test_review_patch_recursive_constructed_leaf_revalidation(leaf: str) -> None:
    if leaf in {"span", "claim"}:
        request = _request()
        spans = request.source_spans
        claims = request.source_claims
        if leaf == "span":
            spans = (
                CheckSourceSpan.model_construct(
                    span_id="span-a", text=" ", source_ref="narration#1"
                ),
                spans[1],
            )
        else:
            claims = (
                CheckSourceClaim.model_construct(
                    claim_id="claim-a",
                    text=" ",
                    source_span_refs=("span-a",),
                    ability_refs=("ability-a",),
                ),
                claims[1],
            )
        with pytest.raises(ValidationError):
            CheckOnLearningRequest(
                lesson_ref=request.lesson_ref,
                promise=request.promise,
                quantity_unit_tokens=request.quantity_unit_tokens,
                source_spans=spans,
                source_claims=claims,
            )
        return

    candidate = _candidate()
    items = candidate.items
    if leaf == "answer_claim":
        first = items[0]
        bad_answer = CheckAnswerClaim.model_construct(
            answer_claim_id="answer-a",
            text=" ",
            source_claim_ref="claim-a",
            source_span_refs=("span-a",),
        )
        with pytest.raises(ValidationError):
            RetrievalCheckItem(
                item_id=first.item_id,
                ability_id=first.ability_id,
                prompt=first.prompt,
                expected_answer=first.expected_answer,
                answer_claims=(bad_answer,),
            )
    else:
        bad_item = RetrievalCheckItem.model_construct(
            item_id="item-a",
            ability_id="ability-a",
            posture="free_response_from_memory",
            prompt="What happened?",
            expected_answer=" ",
            answer_claims=items[0].answer_claims,
        )
        with pytest.raises(ValidationError):
            CheckOnLearningWriterCandidate(
                status="authored",
                items=(bad_item, items[1]),
                known_losses=(),
                marker=None,
            )


@pytest.mark.parametrize(
    "separator", ["\v", "\f", "\x1c", "\x1d", "\x1e", "\x85", "\u2028", "\u2029"]
)
def test_review_patch_all_control_and_unicode_line_breaks_rejected(
    separator: str,
) -> None:
    with pytest.raises(ValidationError):
        CheckSourceSpan(
            span_id=f"span{separator}a", text="source", source_ref="narration#1"
        )
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = f"Question?{separator}Injected"
    with pytest.raises(ValidationError):
        CheckOnLearningWriterCandidate.model_validate(raw, strict=True)


@pytest.mark.parametrize("bullet", ["•", "‣", "⁃", "◦", "∙", "▪", "●"])
def test_review_patch_unicode_bullet_injection_rejected(bullet: str) -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = f"{bullet} Hidden list answer"
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "retrieval_posture_failed" in compose_check_on_learning(
        _request(), lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    "prompt",
    [
        "Read the passage again before answering.",
        "Refer back to the source and explain the delay.",
        "Look back at the notes and answer.",
        "Consult the source material before responding.",
        "Use the transcript to answer.",
        "Follow the worked example and respond.",
        "Is the rating 1 or 2?",
        "Answer yes or no.",
        "Choose one response.",
        "Select the best response.",
        "Pick which statement applies.",
    ],
)
def test_review_patch_expanded_retrieval_scaffold_proxy(prompt: str) -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = prompt
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "retrieval_posture_failed" in compose_check_on_learning(
        _request(), lambda _: candidate
    ).gate.failures


def test_review_patch_short_answer_and_traced_span_copy_leakage() -> None:
    request_raw = _request_raw()
    request_raw["source_claims"][0]["text"] = "Yes"
    request_raw["source_spans"][0]["text"] = "The recurring delay occurs at the handoff"
    request = CheckOnLearningRequest.model_validate(request_raw, strict=True)
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = "Explain yes from memory."
    raw["items"][0]["expected_answer"] = "Yes"
    raw["items"][0]["answer_claims"][0]["text"] = "Yes"
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "answer_leakage_failed" in compose_check_on_learning(
        request, lambda _: candidate
    ).gate.failures

    request = _request()
    request_raw = request.model_dump(mode="python")
    request_raw["source_spans"][0]["text"] = "The recurring delay occurs at the handoff"
    request = CheckOnLearningRequest.model_validate(request_raw, strict=True)
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = (
        "Why does the recurring delay occur at the handoff?"
    )
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "answer_leakage_failed" in compose_check_on_learning(
        request, lambda _: candidate
    ).gate.failures


def test_review_patch_common_vocabulary_is_not_complete_copy() -> None:
    raw = _candidate_raw()
    raw["items"][1]["prompt"] = "How does the handoff shape your first move?"
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert compose_check_on_learning(_request(), lambda _: candidate).status == "authored"


@pytest.mark.parametrize(
    ("source", "answer"),
    [
        ("Use five mg.", "Use five kg."),
        ("Acceleration is 9.81 m s⁻².", "Acceleration is 9.81 m."),
        ("Use the thirteenth step.", "Use the fourteenth step."),
        ("Resistance is 5 Ω.", "Resistance is 5 V."),
    ],
)
def test_review_patch_closed_unit_and_full_ordinal_mismatches_fail(
    source: str, answer: str
) -> None:
    request_raw = _request_raw()
    request_raw["source_claims"][0]["text"] = source
    request = CheckOnLearningRequest.model_validate(request_raw, strict=True)
    raw = _candidate_raw()
    raw["items"][0]["expected_answer"] = answer
    raw["items"][0]["answer_claims"][0]["text"] = answer
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "numeric_fidelity_failed" in compose_check_on_learning(
        request, lambda _: candidate
    ).gate.failures


def test_review_patch_ordinary_following_words_are_not_units() -> None:
    request_raw = _request_raw()
    request_raw["source_claims"][0]["text"] = "Review five patients."
    request = CheckOnLearningRequest.model_validate(request_raw, strict=True)
    raw = _candidate_raw()
    raw["items"][0]["expected_answer"] = "Review five clinicians."
    raw["items"][0]["answer_claims"][0]["text"] = "Review five clinicians."
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    result = compose_check_on_learning(request, lambda _: candidate)
    assert "numeric_fidelity_failed" not in result.gate.failures


def test_review_patch_contracted_negator_normalizes_but_relocation_fails() -> None:
    request_raw = _request_raw()
    request_raw["source_claims"][0]["text"] = "Do not skip the diagnosis."
    request = CheckOnLearningRequest.model_validate(request_raw, strict=True)
    raw = _candidate_raw()
    raw["items"][0]["expected_answer"] = "Don't skip the diagnosis."
    raw["items"][0]["answer_claims"][0]["text"] = "Don't skip the diagnosis."
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "negation_fidelity_failed" not in compose_check_on_learning(
        request, lambda _: candidate
    ).gate.failures

    request_raw["source_claims"][0]["text"] = "Do not map first; then choose."
    request = CheckOnLearningRequest.model_validate(request_raw, strict=True)
    raw["items"][0]["expected_answer"] = "Map first; then do not choose."
    raw["items"][0]["answer_claims"][0]["text"] = "Map first; then do not choose."
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "negation_fidelity_failed" in compose_check_on_learning(
        request, lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    "generic",
    [
        "The answer is pending review.",
        "This depends on context.",
        "It is unknown at this time.",
        "This cannot be determined from available information.",
        "The answer is not provided yet.",
    ],
)
def test_review_patch_generic_answer_phrase_families_fail(generic: str) -> None:
    raw = _candidate_raw()
    raw["items"][0]["expected_answer"] = generic
    raw["items"][0]["answer_claims"][0]["text"] = generic
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "unusable_answer_failed" in compose_check_on_learning(
        _request(), lambda _: candidate
    ).gate.failures


def test_review_patch_span_trace_is_exact_set_with_deterministic_diagnostics() -> None:
    request_raw = _request_raw()
    request_raw["source_spans"] += (
        {
            "span_id": "span-c",
            "text": "Additional grounded context.",
            "source_ref": "narration#3",
        },
    )
    request_raw["source_claims"][0]["source_span_refs"] = ("span-a", "span-c")
    request = CheckOnLearningRequest.model_validate(request_raw, strict=True)
    raw = _candidate_raw()
    raw["items"][0]["answer_claims"][0]["source_span_refs"] = (
        "span-c",
        "span-a",
    )
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert compose_check_on_learning(request, lambda _: candidate).status == "authored"

    raw = _candidate_raw()
    raw["items"][0]["answer_claims"][0]["source_span_refs"] = ("zzz", "aaa")
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    result = compose_check_on_learning(_request(), lambda _: candidate)
    assert result.gate.unknown_source_refs == ("aaa", "zzz")


@pytest.mark.parametrize("unsafe", ["\x00", "\x07", "\u200d", "\u202e", "\ufeff"])
def test_review_round_two_rejects_unicode_controls_and_formats(unsafe: str) -> None:
    with pytest.raises(ValidationError):
        CheckSourceSpan(
            span_id=f"span{unsafe}a", text="source", source_ref="narration#1"
        )
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = f"What happened{unsafe}?"
    with pytest.raises(ValidationError):
        CheckOnLearningWriterCandidate.model_validate(raw, strict=True)


@pytest.mark.parametrize(
    "prompt",
    [
        "<h2>Recall check</h2>",
        "<div>What caused the delay?</div>",
        "§ Hidden list item",
        "→ Hidden list item",
        "※ Hidden list item",
        "! Hidden list item",
    ],
)
def test_review_round_two_rejects_html_and_leading_symbol_lists(prompt: str) -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = prompt
    if prompt.startswith("<"):
        with pytest.raises(ValidationError):
            CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
        return
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "retrieval_posture_failed" in compose_check_on_learning(
        _request(), lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    "prompt",
    [
        "Review the notes before answering.",
        "Read the source before responding.",
        "Refer to the passage and explain the delay.",
        "Consult the text before answering.",
        "Is the rating 2, 3, or 4?",
        "Is the response yes or no?",
        "Is the value between 2 and 4?",
        "Which is correct: system cause or isolated symptom?",
        "Answer: system cause.",
        "The correct response is system cause.",
    ],
)
def test_review_round_two_closes_syntax_specific_retrieval_scaffolds(
    prompt: str,
) -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = prompt
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "retrieval_posture_failed" in compose_check_on_learning(
        _request(), lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    "prompt",
    [
        "How would you choose a first move under uncertainty?",
        "What options would preserve the handoff evidence?",
        "What makes a transcript reliable evidence?",
    ],
)
def test_review_round_two_allows_domain_words_in_open_questions(prompt: str) -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = prompt
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert compose_check_on_learning(_request(), lambda _: candidate).status == "authored"


def test_review_round_two_short_copy_requires_token_boundaries() -> None:
    request_raw = _request_raw()
    request_raw["source_claims"][0]["text"] = "AI"
    request = CheckOnLearningRequest.model_validate(request_raw, strict=True)
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = "What makes this explainable?"
    raw["items"][0]["expected_answer"] = "AI"
    raw["items"][0]["answer_claims"][0]["text"] = "AI"
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "answer_leakage_failed" not in compose_check_on_learning(
        request, lambda _: candidate
    ).gate.failures

    raw["items"][0]["prompt"] = "Explain AI from memory."
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "answer_leakage_failed" in compose_check_on_learning(
        request, lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    ("source", "answer", "units", "should_fail"),
    [
        ("Dose is 5 mcg.", "Dose is 5 ng.", ("mcg", "ng"), True),
        ("Payload is 5 MB.", "Payload is 5 GB.", ("MB", "GB"), True),
        ("Power is 5 mW.", "Power is 5 MW.", ("mW", "MW"), True),
        ("Resistance is 5 Î©.", "Resistance is 5 ohm.", ("Î©", "ohm"), True),
        ("Use five to seven mcg.", "Use five to eight mcg.", ("mcg",), True),
        ("Use the 13th step.", "Use the 14th step.", (), True),
        ("Complete 5 before lunch.", "Complete 5 after lunch.", (), False),
    ],
)
def test_review_round_two_source_declared_units_and_range_witnesses(
    source: str, answer: str, units: tuple[str, ...], should_fail: bool
) -> None:
    request_raw = _request_raw()
    request_raw["quantity_unit_tokens"] = units
    request_raw["source_claims"][0]["text"] = source
    request = CheckOnLearningRequest.model_validate(request_raw, strict=True)
    raw = _candidate_raw()
    raw["items"][0]["expected_answer"] = answer
    raw["items"][0]["answer_claims"][0]["text"] = answer
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    failures = compose_check_on_learning(request, lambda _: candidate).gate.failures
    assert ("numeric_fidelity_failed" in failures) is should_fail


@pytest.mark.parametrize("units", [("",), (" mg",), ("mg\nkg",), ("mg", "mg")])
def test_review_round_two_unit_authority_is_strict(units: tuple[str, ...]) -> None:
    raw = _request_raw()
    raw["quantity_unit_tokens"] = units
    with pytest.raises(ValidationError):
        CheckOnLearningRequest.model_validate(raw, strict=True)


def test_review_round_two_negation_position_and_lexical_paraphrase() -> None:
    request_raw = _request_raw()
    request_raw["source_claims"][0]["text"] = "Do not skip the diagnosis."
    request = CheckOnLearningRequest.model_validate(request_raw, strict=True)
    raw = _candidate_raw()
    raw["items"][0]["expected_answer"] = "Do not omit the diagnosis."
    raw["items"][0]["answer_claims"][0]["text"] = "Do not omit the diagnosis."
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "negation_fidelity_failed" not in compose_check_on_learning(
        request, lambda _: candidate
    ).gate.failures

    request_raw["source_claims"][0]["text"] = (
        "Map the handoff and do not skip the diagnosis."
    )
    request = CheckOnLearningRequest.model_validate(request_raw, strict=True)
    raw["items"][0]["expected_answer"] = (
        "Do not skip the diagnosis after mapping the handoff."
    )
    raw["items"][0]["answer_claims"][0]["text"] = raw["items"][0][
        "expected_answer"
    ]
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "negation_fidelity_failed" in compose_check_on_learning(
        request, lambda _: candidate
    ).gate.failures

    request_raw["source_claims"][0]["text"] = "Avoid skipping the diagnosis."
    request = CheckOnLearningRequest.model_validate(request_raw, strict=True)
    raw["items"][0]["expected_answer"] = "Do not skip the diagnosis."
    raw["items"][0]["answer_claims"][0]["text"] = "Do not skip the diagnosis."
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "negation_fidelity_failed" not in compose_check_on_learning(
        request, lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    "generic",
    [
        "TBA",
        "N/A",
        "Indeterminate at present.",
        "No answer is available.",
        "The response cannot be established.",
    ],
)
def test_review_round_two_generic_sentinel_families(generic: str) -> None:
    raw = _candidate_raw()
    raw["items"][0]["expected_answer"] = generic
    raw["items"][0]["answer_claims"][0]["text"] = generic
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "unusable_answer_failed" in compose_check_on_learning(
        _request(), lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    "unsafe",
    [
        "\x00",
        "\u200d",
        "<script>x</script>",
        "<iframe>x</iframe>",
        "<details>x</details>",
        "<aside>x</aside>",
    ],
)
def test_review_round_three_rejects_unsafe_prompt_and_answer_claim_text(
    unsafe: str,
) -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = f"What happened? {unsafe}"
    with pytest.raises(ValidationError):
        CheckOnLearningWriterCandidate.model_validate(raw, strict=True)

    raw = _candidate_raw()
    raw["items"][0]["answer_claims"][0]["text"] = f"Grounded answer {unsafe}"
    raw["items"][0]["expected_answer"] = raw["items"][0]["answer_claims"][0][
        "text"
    ]
    with pytest.raises(ValidationError):
        CheckOnLearningWriterCandidate.model_validate(raw, strict=True)


@pytest.mark.parametrize(
    "prompt",
    [
        "Compare 1) system cause and 2) isolated symptom.",
        "If the delay recurs, answer yes; otherwise answer no.",
        "Decide between the system cause and the isolated symptom.",
        "Pick the best response for the handoff.",
        "Listen to the transcript before answering.",
        "Study the worked example before responding.",
        "Answer - map the handoff.",
        "Solution = map the handoff.",
        "Correct response - map the handoff.",
        "The answer is map the handoff.",
    ],
)
def test_review_round_three_closes_remaining_retrieval_syntax(prompt: str) -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = prompt
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "retrieval_posture_failed" in compose_check_on_learning(
        _request(), lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    "prompt",
    [
        "How do teams decide between speed and accuracy?",
        "What makes a transcript reliable evidence?",
        "Why can a worked example conceal the root cause?",
        "How should a facilitator listen for handoff signals?",
    ],
)
def test_review_round_three_allows_legitimate_domain_uses(prompt: str) -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = prompt
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert compose_check_on_learning(_request(), lambda _: candidate).status == "authored"


@pytest.mark.parametrize(
    ("source", "answer", "should_fail"),
    [
        (
            "Map risk and do not skip diagnosis before treatment.",
            "Map risk and skip diagnosis only when treatment is not ready.",
            True,
        ),
        (
            "Do not skip diagnosis and never omit triage.",
            "Never skip diagnosis and do not omit triage.",
            True,
        ),
        ("Do not skip the diagnosis.", "Do not omit the diagnosis.", False),
    ],
)
def test_review_round_three_negation_exact_position_scope_and_paraphrase(
    source: str, answer: str, should_fail: bool
) -> None:
    request_raw = _request_raw()
    request_raw["source_claims"][0]["text"] = source
    request = CheckOnLearningRequest.model_validate(request_raw, strict=True)
    raw = _candidate_raw()
    raw["items"][0]["expected_answer"] = answer
    raw["items"][0]["answer_claims"][0]["text"] = answer
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    failures = compose_check_on_learning(request, lambda _: candidate).gate.failures
    assert ("negation_fidelity_failed" in failures) is should_fail


@pytest.mark.parametrize(
    ("source", "same"),
    [
        ("Use between five and seven mg.", "Use five to seven mg."),
        ("Use five through seven mg.", "Use five\u2013seven mg."),
        ("Use 5 to 7 mg.", "Use 5\u20137mg."),
        ("Use the 13TH step.", "Use the 13th step."),
    ],
)
def test_review_round_three_equivalent_ranges_and_ordinals_pass(
    source: str, same: str
) -> None:
    request_raw = _request_raw()
    request_raw["source_claims"][0]["text"] = source
    request = CheckOnLearningRequest.model_validate(request_raw, strict=True)
    raw = _candidate_raw()
    raw["items"][0]["expected_answer"] = same
    raw["items"][0]["answer_claims"][0]["text"] = same
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "numeric_fidelity_failed" not in compose_check_on_learning(
        request, lambda _: candidate
    ).gate.failures


def test_review_round_three_acronym_punctuation_cannot_bypass_copy_gate() -> None:
    request_raw = _request_raw()
    request_raw["source_claims"][0]["text"] = "AI"
    request = CheckOnLearningRequest.model_validate(request_raw, strict=True)
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = "Explain A.I. from memory."
    raw["items"][0]["expected_answer"] = "AI"
    raw["items"][0]["answer_claims"][0]["text"] = "AI"
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "answer_leakage_failed" in compose_check_on_learning(
        request, lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    "generic",
    ["No response", "None", "Not applicable", "I don't know", "Unavailable", "No idea", "TBC"],
)
def test_review_round_three_whole_answer_generic_sentinels(generic: str) -> None:
    raw = _candidate_raw()
    raw["items"][0]["expected_answer"] = generic
    raw["items"][0]["answer_claims"][0]["text"] = generic
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "unusable_answer_failed" in compose_check_on_learning(
        _request(), lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    "substantive",
    [
        "The pending review will close after the evidence check.",
        "An unknown variable changes the diagnosis.",
    ],
)
def test_review_round_three_substantive_sentinel_words_are_allowed(
    substantive: str,
) -> None:
    raw = _candidate_raw()
    raw["items"][0]["expected_answer"] = substantive
    raw["items"][0]["answer_claims"][0]["text"] = substantive
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "unusable_answer_failed" not in compose_check_on_learning(
        _request(), lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    "prompt",
    [
        "Before answering, carefully consult your source notes.",
        "Please briefly review these notes before responding.",
        "Now reread the original passage.",
        "First, carefully listen to this transcript.",
        "Before responding, study that worked example.",
        "For this check, decide carefully between cause and symptom.",
    ],
)
def test_review_round_four_modifier_and_preamble_tolerant_scaffolds(
    prompt: str,
) -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = prompt
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "retrieval_posture_failed" in compose_check_on_learning(
        _request(), lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    "prompt",
    [
        "Answer no or yes.",
        "Respond no/yes.",
        "If the delay is isolated, answer no; otherwise yes.",
        "Is the cause systemic or isolated?",
        "Is the diagnosis between systemic and isolated?",
        "Compare (1) cause and (2) symptom.",
        "Compare 1: cause and 2: symptom.",
        "Compare A: cause and Z: symptom.",
        "Compare (Q) cause and (R) symptom.",
    ],
)
def test_review_round_four_full_choice_and_enumerator_grammar(prompt: str) -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = prompt
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "retrieval_posture_failed" in compose_check_on_learning(
        _request(), lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    "prompt",
    [
        "Answer: map the handoff.",
        "Solution - map the handoff.",
        "Response = map the handoff.",
        "Key: map the handoff.",
        "Answer-key = map the handoff.",
        "The solution is map the handoff.",
        "Correct key is map the handoff.",
    ],
)
def test_review_round_four_complete_disclosure_header_grammar(prompt: str) -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = prompt
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "retrieval_posture_failed" in compose_check_on_learning(
        _request(), lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    "prompt",
    [
        "How should a reviewer consult source quality evidence?",
        "What makes review notes trustworthy?",
        "Why might a transcript omit the root cause?",
        "How would you decide between interventions without supplied choices?",
        "What response is appropriate when evidence conflicts?",
        "Why is the answer-key format risky for retrieval practice?",
    ],
)
def test_review_round_four_legitimate_open_questions_remain_allowed(
    prompt: str,
) -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = prompt
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert compose_check_on_learning(_request(), lambda _: candidate).status == "authored"


@pytest.mark.parametrize(
    "unsafe",
    ["<!-- hidden -->", "<!DOCTYPE html>", "<?xml version='1.0'?>", "<![CDATA[x]]>"],
)
def test_review_round_four_rejects_html_comments_and_declarations(
    unsafe: str,
) -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = f"What happened? {unsafe}"
    with pytest.raises(ValidationError):
        CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    raw = _candidate_raw()
    raw["items"][0]["answer_claims"][0]["text"] = f"Grounded {unsafe}"
    raw["items"][0]["expected_answer"] = raw["items"][0]["answer_claims"][0][
        "text"
    ]
    with pytest.raises(ValidationError):
        CheckOnLearningWriterCandidate.model_validate(raw, strict=True)


@pytest.mark.parametrize(
    ("source", "same", "units"),
    [
        ("Use 5 mg to 7 mg.", "Use 5 to 7 mg.", ("mg",)),
        ("Use 5 mg through 7 mg.", "Use between 5 and 7 mg.", ("mg",)),
        ("Use 5 mg\u20137 mg.", "Use 5\u20137 mg.", ("mg",)),
        ("Use five kg to seven kg.", "Use five to seven kg.", ("kg",)),
    ],
)
def test_review_round_four_shared_and_repeated_range_units_are_equivalent(
    source: str, same: str, units: tuple[str, ...]
) -> None:
    request_raw = _request_raw()
    request_raw["quantity_unit_tokens"] = units
    request_raw["source_claims"][0]["text"] = source
    request = CheckOnLearningRequest.model_validate(request_raw, strict=True)
    raw = _candidate_raw()
    raw["items"][0]["expected_answer"] = same
    raw["items"][0]["answer_claims"][0]["text"] = same
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "numeric_fidelity_failed" not in compose_check_on_learning(
        request, lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    "generic",
    [
        "...",
        "---",
        "NIL",
        "Not known",
        "Not enough data",
        "No information",
        "Not sure",
        "Undetermined",
    ],
)
def test_review_round_four_punctuation_and_expanded_whole_answer_sentinels(
    generic: str,
) -> None:
    raw = _candidate_raw()
    raw["items"][0]["expected_answer"] = generic
    raw["items"][0]["answer_claims"][0]["text"] = generic
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "unusable_answer_failed" in compose_check_on_learning(
        _request(), lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    "prompt",
    [
        "Which cause best explains the delay?",
        "Decide carefully between cause and symptom.",
        "Choose the best response.",
        "Select one option.",
        "Pick the strongest answer.",
        "Review the source notes.",
        "Reread the original passage.",
        "Consult the provided text.",
        "Refer to the transcript.",
        "Listen carefully to the worked example.",
        "Study the transcript.",
        "Hint: inspect the handoff.",
        "Answer: system cause.",
        "Response - system cause.",
        "Key = system cause.",
        "Solution is system cause.",
        "Please explain the recurring delay.",
        "Carefully describe the handoff.",
        "From memory: explain the delay.",
    ],
)
def test_review_round_five_closed_grammar_rejects_unapproved_stems_and_preambles(
    prompt: str,
) -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = prompt
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "retrieval_posture_failed" in compose_check_on_learning(
        _request(), lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    "prompt",
    [
        "Compare I) system cause and II) isolated symptom.",
        "Compare (i) system cause and (ii) isolated symptom.",
        "Compare A - system cause and B - isolated symptom.",
        "Compare 1 - system cause and 2 - isolated symptom.",
        "Explain the delay. Hint - inspect the handoff.",
        "Explain the delay. Answer: system cause.",
        "What caused the delay? Solution = system cause.",
        "Compare the causes. The key is system cause.",
        "Compare system cause or isolated symptom.",
        "Explain whether the cause is systemic or isolated.",
    ],
)
def test_review_round_five_structural_roman_hyphen_hint_disclosure_guards(
    prompt: str,
) -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = prompt
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "retrieval_posture_failed" in compose_check_on_learning(
        _request(), lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    "prompt",
    [
        "Explain how you would choose a first move.",
        "What options would you generate?",
        "What makes a transcript accurate?",
        "From memory, explain the recurring delay.",
        "Describe the handoff evidence.",
        "Identify the system-design cause.",
        "Name the first move.",
        "State the governing distinction.",
        "Summarize the diagnostic logic.",
        "Outline the handoff map.",
        "Map the evidence chain.",
        "Distinguish cause from symptom.",
        "Compare the two diagnostic approaches without selecting one.",
        "How would you classify the recurring delay?",
        "Why does the handoff matter?",
    ],
)
def test_review_round_five_closed_grammar_approved_productions(prompt: str) -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = prompt
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert compose_check_on_learning(_request(), lambda _: candidate).status == "authored"


@pytest.mark.parametrize(
    ("source", "same"),
    [
        ("Use 5 - 7 mg.", "Use 5 to 7 mg."),
        ("Use five - seven mg.", "Use between five and seven mg."),
    ],
)
def test_review_round_five_spaced_ascii_hyphen_ranges(
    source: str, same: str
) -> None:
    request_raw = _request_raw()
    request_raw["source_claims"][0]["text"] = source
    request = CheckOnLearningRequest.model_validate(request_raw, strict=True)
    raw = _candidate_raw()
    raw["items"][0]["expected_answer"] = same
    raw["items"][0]["answer_claims"][0]["text"] = same
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "numeric_fidelity_failed" not in compose_check_on_learning(
        request, lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    "prompt",
    [
        "What classification applies: systemic or isolated?",
        "How should you classify the delay: systemic or isolated?",
        "Why is the cause systemic or isolated?",
        "Explain whether the cause is systemic or isolated.",
        "Describe the result as yes or no.",
        "Identify whether the signal is primary or secondary.",
        "Name the outcome yes/no.",
        "State systemic or isolated.",
        "Summarize true or false.",
        "Outline the input/output alternatives.",
        "Map cause/symptom.",
        "Distinguish acceptable or unacceptable.",
        "Compare systemic or isolated.",
    ],
)
def test_review_round_six_alternatives_rejected_across_approved_productions(
    prompt: str,
) -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = prompt
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "retrieval_posture_failed" in compose_check_on_learning(
        _request(), lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    "prompt",
    [
        "Explain how one or more signals accumulate.",
        "Describe how errors originate in the handoff.",
        "What options would you generate?",
        "How does the evidence change over time?",
    ],
)
def test_review_round_six_ordinary_prose_is_not_a_supplied_alternative(
    prompt: str,
) -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = prompt
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert compose_check_on_learning(_request(), lambda _: candidate).status == "authored"


@pytest.mark.parametrize(
    "prompt",
    [
        "Explain the delay using the transcript.",
        "Describe the cause after reviewing the source.",
        "Identify the signal by consulting your notes.",
        "What caused the delay according to the transcript?",
        "How would you classify it while referring to the source?",
        "State the cause based on the worked example.",
    ],
)
def test_review_round_six_embedded_source_consultation_clauses(prompt: str) -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = prompt
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "retrieval_posture_failed" in compose_check_on_learning(
        _request(), lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    "prompt",
    [
        "Explain the delay; Hint: inspect the handoff.",
        "Explain the delay: Answer - system cause.",
        "Explain the delay \u2014 Solution = system cause.",
        "State the result - Response is system cause.",
        "What caused the delay? Key: system cause.",
        "Describe the delay and answer: system cause.",
    ],
)
def test_review_round_six_disclosure_after_any_separator_or_mid_production(
    prompt: str,
) -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = prompt
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "retrieval_posture_failed" in compose_check_on_learning(
        _request(), lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    "prompt",
    [
        "Compare \u2460 system cause and \u2461 isolated symptom.",
        "Explain the categories \u2022 system cause \u2022 isolated symptom.",
    ],
)
def test_review_round_six_unicode_enumerators_and_embedded_bullets(prompt: str) -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = prompt
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "retrieval_posture_failed" in compose_check_on_learning(
        _request(), lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    ("source", "same"),
    [
        ("Use -5 - -3 mg.", "Use -5 to -3 mg."),
        ("Use \u22125 - \u22123 mg.", "Use -5 through -3 mg."),
        ("Use .1 - .5 mg.", "Use between .1 and .5 mg."),
        ("Use -5--3 mg.", "Use -5\u2013-3 mg."),
    ],
)
def test_review_round_six_signed_and_leading_decimal_ranges(
    source: str, same: str
) -> None:
    request_raw = _request_raw()
    request_raw["source_claims"][0]["text"] = source
    request = CheckOnLearningRequest.model_validate(request_raw, strict=True)
    raw = _candidate_raw()
    raw["items"][0]["expected_answer"] = same
    raw["items"][0]["answer_claims"][0]["text"] = same
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "numeric_fidelity_failed" not in compose_check_on_learning(
        request, lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    "generic",
    [
        "Not available",
        "The answer is not available",
        "Response unavailable",
        "Information unavailable",
        "No data available",
        "Data not available",
        "Not currently available",
    ],
)
def test_review_round_six_not_available_sentinel_family(generic: str) -> None:
    raw = _candidate_raw()
    raw["items"][0]["expected_answer"] = generic
    raw["items"][0]["answer_claims"][0]["text"] = generic
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "unusable_answer_failed" in compose_check_on_learning(
        _request(), lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    "prompt",
    [
        "Compare systemic versus isolated.",
        "State cause vs symptom.",
        "Identify primary vs. secondary.",
        "Map cause | symptom.",
    ],
)
def test_review_round_seven_versus_vs_and_pipe_choice_scaffolds(prompt: str) -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = prompt
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "retrieval_posture_failed" in compose_check_on_learning(
        _request(), lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    "prompt",
    [
        "Explain how zero or more signals accumulate.",
        "Describe how 2 or more causes interact.",
        "State how twelve or more handoffs compound delay.",
    ],
)
def test_review_round_seven_quantifier_or_more_remains_ordinary_prose(
    prompt: str,
) -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = prompt
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert compose_check_on_learning(_request(), lambda _: candidate).status == "authored"


@pytest.mark.parametrize(
    "prompt",
    [
        "Explain the delay by reading the source.",
        "Describe the cause while reading the transcript.",
        "Identify the signal with the notes.",
        "State the diagnosis with reference to the source.",
        "Summarize the cause drawing from the transcript.",
        "Outline the result after listening to the worked example.",
        "Map the evidence as shown in the notes.",
    ],
)
def test_review_round_seven_structural_embedded_source_consultation(
    prompt: str,
) -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = prompt
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "retrieval_posture_failed" in compose_check_on_learning(
        _request(), lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    "prompt",
    [
        "Explain the delay, the answer is system cause.",
        "Describe the handoff and the answer is map first.",
        "State the result but response is system cause.",
        "What caused the delay, solution is system cause?",
    ],
)
def test_review_round_seven_copular_disclosure_after_comma_or_conjunction(
    prompt: str,
) -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = prompt
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "retrieval_posture_failed" in compose_check_on_learning(
        _request(), lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    "prompt",
    [
        "Compare \u2460 system cause and \u2461 symptom.",
        "Compare \u2776 system cause and \u2777 symptom.",
        "Compare \u24b6 system cause and \u24b7 symptom.",
        "Explain \u2192 cause \u2192 symptom.",
        "Describe \u25aa cause \u25aa symptom.",
    ],
)
def test_review_round_seven_unicode_structural_enumerator_families(
    prompt: str,
) -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = prompt
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "retrieval_posture_failed" in compose_check_on_learning(
        _request(), lambda _: candidate
    ).gate.failures


def test_review_round_seven_single_arrow_in_ordinary_prose_is_allowed() -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = "Explain how evidence \u2192 action mapping works."
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert compose_check_on_learning(_request(), lambda _: candidate).status == "authored"


def test_review_round_seven_unspaced_word_number_range() -> None:
    request_raw = _request_raw()
    request_raw["source_claims"][0]["text"] = "Use five-seven mg."
    request = CheckOnLearningRequest.model_validate(request_raw, strict=True)
    raw = _candidate_raw()
    raw["items"][0]["expected_answer"] = "Use five to seven mg."
    raw["items"][0]["answer_claims"][0]["text"] = "Use five to seven mg."
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "numeric_fidelity_failed" not in compose_check_on_learning(
        request, lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    "generic",
    [
        "Currently unavailable",
        "Temporarily unavailable",
        "Presently unavailable",
        "The answer is currently unavailable",
        "Response temporarily unavailable",
        "Information presently unavailable",
        "Currently not available",
    ],
)
def test_review_round_seven_modifier_before_unavailable_sentinels(
    generic: str,
) -> None:
    raw = _candidate_raw()
    raw["items"][0]["expected_answer"] = generic
    raw["items"][0]["answer_claims"][0]["text"] = generic
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "unusable_answer_failed" in compose_check_on_learning(
        _request(), lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    ("source", "same"),
    [
        ("Use the twenty-first step.", "Use the twenty first step."),
        ("Use the thirty-second step.", "Use the thirty second step."),
        ("Use twenty-one steps.", "Use twenty one steps."),
    ],
)
def test_review_round_eight_compound_ordinal_and_cardinal_equivalence(
    source: str, same: str
) -> None:
    request_raw = _request_raw()
    request_raw["source_claims"][0]["text"] = source
    request = CheckOnLearningRequest.model_validate(request_raw, strict=True)
    raw = _candidate_raw()
    raw["items"][0]["expected_answer"] = same
    raw["items"][0]["answer_claims"][0]["text"] = same
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "numeric_fidelity_failed" not in compose_check_on_learning(
        request, lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    "prompt",
    [
        "Explain * system cause * isolated symptom.",
        "Describe \u25c6 system cause \u25c6 isolated symptom.",
        "Compare \u00a7 system cause \u00a7 isolated symptom.",
        "Outline \u203b system cause \u203b isolated symptom.",
    ],
)
def test_review_round_eight_repeated_standalone_symbol_enumerators(
    prompt: str,
) -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = prompt
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "retrieval_posture_failed" in compose_check_on_learning(
        _request(), lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    "prompt",
    [
        "Explain why *important* evidence matters.",
        "State 2 * 3 * 4 as a product.",
        "Describe why cause, symptom, and context differ.",
        "Outline how x * y * z represents compounding.",
    ],
)
def test_review_round_eight_normal_punctuation_emphasis_and_math_allowed(
    prompt: str,
) -> None:
    raw = _candidate_raw()
    raw["items"][0]["prompt"] = prompt
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert compose_check_on_learning(_request(), lambda _: candidate).status == "authored"


@pytest.mark.parametrize(
    ("source", "same"),
    [
        ("Use one-half mg.", "Use one half mg."),
        ("Use the one-hundredth step.", "Use the one hundredth step."),
    ],
)
def test_review_round_nine_fraction_and_scale_compound_equivalence(
    source: str, same: str
) -> None:
    request_raw = _request_raw()
    request_raw["source_claims"][0]["text"] = source
    request = CheckOnLearningRequest.model_validate(request_raw, strict=True)
    raw = _candidate_raw()
    raw["items"][0]["expected_answer"] = same
    raw["items"][0]["answer_claims"][0]["text"] = same
    candidate = CheckOnLearningWriterCandidate.model_validate(raw, strict=True)
    assert "numeric_fidelity_failed" not in compose_check_on_learning(
        request, lambda _: candidate
    ).gate.failures
