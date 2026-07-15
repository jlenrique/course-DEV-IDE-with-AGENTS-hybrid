from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.marcus.lesson_plan.deep_dive_projection import (
    DEEP_DIVE_UNAVAILABLE_MARKER,
    BoldTermMarker,
    DeepDiveAbilityInput,
    DeepDiveGateReceipt,
    DeepDiveSkeletonClaim,
    DeepDiveSkeletonRequest,
    DeepDiveSkeletonResult,
    DeepDiveSkeletonWriterResult,
    NarrationSourceSpan,
    SourceClaim,
    compose_deep_dive_skeleton,
    deep_dive_authority_digest,
    offline_deep_dive_writer,
)

ROOT = Path(__file__).resolve().parents[4]
FIXTURES = ROOT / "tests" / "fixtures" / "deep_dive_37_2a"
MODULE = ROOT / "app" / "marcus" / "lesson_plan" / "deep_dive_projection.py"


def request() -> DeepDiveSkeletonRequest:
    return DeepDiveSkeletonRequest.model_validate_json(
        (FIXTURES / "request.json").read_text(encoding="utf-8")
    )


def authored_writer_result() -> DeepDiveSkeletonWriterResult:
    return DeepDiveSkeletonWriterResult.model_validate_json(
        (FIXTURES / "writer_result.json").read_text(encoding="utf-8")
    )


def test_fixture_round_trip_schema_strict_frozen_and_authored_pass() -> None:
    req = request()
    result = compose_deep_dive_skeleton(req, lambda _: authored_writer_result())
    assert result.status == "authored"
    assert result.gate.status == "pass"
    assert result.gate.covered_vo_claim_ids == ("claim-vo-1", "claim-vo-2")
    assert result.gate.used_delta_claim_ids == ("claim-delta-1",)
    assert result.gate.operator_warnings == (
        "full_semantic_equivalence_non_contradiction_and_depth_require_operator_spot_check",
    )
    assert result.model_dump(mode="json") == json.loads(result.model_dump_json())
    assert type(result).model_validate_json(result.model_dump_json()) == result
    schema = type(result).model_json_schema()
    assert schema["additionalProperties"] is False
    assert all(
        definition.get("type") != "object"
        or definition.get("additionalProperties") is False
        for definition in schema["$defs"].values()
    )
    with pytest.raises(ValidationError):
        result.status = "degraded"  # type: ignore[misc]


@pytest.mark.parametrize(
    "factory,payload",
    [
        (NarrationSourceSpan, {"span_id": " ", "text": "x", "source_ref": "s"}),
        (NarrationSourceSpan, {"span_id": 1, "text": "x", "source_ref": "s"}),
        (
            SourceClaim,
            {"claim_id": "c", "text": "x", "source_span_refs": [], "role": "vo"},
        ),
        (
            DeepDiveAbilityInput,
            {"ability_id": "a", "text": "x", "unknown": True},
        ),
        (BoldTermMarker, {"term": "two\nlines"}),
    ],
)
def test_atomic_contracts_reject_blank_coercion_empty_refs_and_extras(factory, payload) -> None:
    with pytest.raises(ValidationError):
        factory.model_validate(payload)


def test_request_rejects_duplicate_ids_empty_authority_and_unresolved_claim_spans() -> None:
    payload = request().model_dump()
    payload["source_spans"] += (payload["source_spans"][0],)
    with pytest.raises(ValidationError, match="duplicate source span IDs"):
        DeepDiveSkeletonRequest.model_validate(payload)
    payload = request().model_dump()
    payload["source_claims"][0]["source_span_refs"] = ("missing",)
    with pytest.raises(ValidationError, match="unknown source span"):
        DeepDiveSkeletonRequest.model_validate(payload)
    for field in ("source_spans", "abilities"):
        payload = request().model_dump()
        payload[field] = ()
        with pytest.raises(ValidationError):
            DeepDiveSkeletonRequest.model_validate(payload)
    payload = request().model_dump()
    payload["source_claims"] = tuple(
        claim for claim in payload["source_claims"] if claim["role"] != "vo"
    )
    with pytest.raises(ValidationError, match="VO claim"):
        DeepDiveSkeletonRequest.model_validate(payload)


def test_writer_is_invoked_once_and_stub_is_deterministic_unavailable() -> None:
    calls = 0

    def writer(req: DeepDiveSkeletonRequest) -> DeepDiveSkeletonWriterResult:
        nonlocal calls
        calls += 1
        assert req == request()
        return authored_writer_result()

    assert compose_deep_dive_skeleton(request(), writer).status == "authored"
    assert calls == 1
    first = offline_deep_dive_writer(request())
    assert first == offline_deep_dive_writer(request())
    assert first.status == "unavailable"
    assert first.sections == () and first.bold_terms == ()
    assert first.marker == DEEP_DIVE_UNAVAILABLE_MARKER

    contradictory = first.model_dump()
    contradictory["marker"] = "wrong-marker"
    with pytest.raises(ValidationError, match="canonical marker"):
        DeepDiveSkeletonWriterResult.model_validate(contradictory)


def test_wrong_writer_return_and_constructed_model_bypass_fail_closed() -> None:
    with pytest.raises(TypeError, match="DeepDiveSkeletonWriterResult"):
        compose_deep_dive_skeleton(request(), lambda _: {})  # type: ignore[arg-type,return-value]
    invalid = authored_writer_result().model_copy(
        update={"status": "unavailable", "known_losses": (), "marker": None}
    )
    with pytest.raises(ValidationError):
        compose_deep_dive_skeleton(request(), lambda _: invalid)

    def exploding(_: DeepDiveSkeletonRequest) -> DeepDiveSkeletonWriterResult:
        raise RuntimeError("writer failed")

    with pytest.raises(RuntimeError, match="writer failed"):
        compose_deep_dive_skeleton(request(), exploding)


def test_constructed_request_is_revalidated_before_writer_invocation() -> None:
    invalid = request().model_copy(update={"source_spans": ()})
    invoked = False

    def writer(_: DeepDiveSkeletonRequest) -> DeepDiveSkeletonWriterResult:
        nonlocal invoked
        invoked = True
        return authored_writer_result()

    with pytest.raises(ValidationError, match="narration/source spans"):
        compose_deep_dive_skeleton(invalid, writer)
    assert invoked is False


def test_section_prose_must_be_deterministic_claim_composition() -> None:
    raw = authored_writer_result().model_dump()
    raw["sections"][0]["prose"] += " Hidden unrelated learner-facing prose."
    candidate = DeepDiveSkeletonWriterResult.model_validate(raw)
    result = compose_deep_dive_skeleton(request(), lambda _: candidate)
    assert result.status == "degraded"
    assert "prose_claim_composition_failed" in result.gate.failures


def test_bold_term_requires_authority_in_its_traced_source_claim() -> None:
    raw = authored_writer_result().model_dump()
    raw["sections"][0]["claims"][0]["text"] = "An **invented term** reframes the symptom."
    raw["sections"][0]["prose"] = " ".join(
        claim["text"] for claim in raw["sections"][0]["claims"]
    )
    raw["bold_terms"] = (
        {"term": "invented term"},
        {"term": "two stages"},
    )
    candidate = DeepDiveSkeletonWriterResult.model_validate(raw)
    result = compose_deep_dive_skeleton(request(), lambda _: candidate)
    assert result.status == "degraded"
    assert "bold_term_source_authorization_failed" in result.gate.failures


def test_skeleton_claim_must_trace_exactly_one_source_claim() -> None:
    payload = authored_writer_result().sections[0].claims[0].model_dump()
    payload["source_claim_refs"] = ("claim-vo-1", "claim-delta-1")
    with pytest.raises(ValidationError, match="exactly one source claim"):
        DeepDiveSkeletonClaim.model_validate(payload)


@pytest.mark.parametrize(
    ("source", "same", "different"),
    [
        ("Dose 5 mg then 10 mg.", "Dose 5mg then 10mg.", "Dose 10mg then 5mg."),
        ("Rate .5% to 2.0%.", "Rate .5 % to 2.0 %.", "Rate 0.5% to 2.0%."),
        ("Keep 3–5 kg.", "Keep 3—5kg.", "Keep 3-6 kg."),
        ("Use twenty-one steps.", "Use twenty one steps.", "Use twenty-two steps."),
        ("The one hundred and two cases.", "The one hundred two cases.", "The 102 cases."),
    ],
)
def test_ordered_numeric_witness_variants(source: str, same: str, different: str) -> None:
    req_raw = request().model_dump()
    req_raw["source_claims"][0]["text"] = source
    req = DeepDiveSkeletonRequest.model_validate(req_raw)
    raw = authored_writer_result().model_dump()
    raw["sections"][0]["claims"][0]["text"] = same
    raw["sections"][0]["prose"] = " ".join(
        claim["text"] for claim in raw["sections"][0]["claims"]
    )
    candidate = DeepDiveSkeletonWriterResult.model_validate(raw)
    assert compose_deep_dive_skeleton(req, lambda _: candidate).status == "authored"
    raw["sections"][0]["claims"][0]["text"] = different
    raw["sections"][0]["prose"] = " ".join(
        claim["text"] for claim in raw["sections"][0]["claims"]
    )
    candidate = DeepDiveSkeletonWriterResult.model_validate(raw)
    assert "numeric_fidelity_failed" in compose_deep_dive_skeleton(
        req, lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    ("source", "same", "different"),
    [
        ("Hold at −5 °C.", "Hold at -5°C.", "Hold at 5°C."),
        ("Use 1.25e−3 mol/L.", "Use 1.25E-3mol/L.", "Use 1.25e-2 mol/L."),
        (
            "Use 6.02 × 10^23 mol⁻¹.",
            "Use 6.02×10^23mol⁻¹.",
            "Use 6.02×10^22 mol⁻¹.",
        ),
        ("Acceleration is 9.81 m·s⁻².", "Acceleration is 9.81m·s⁻².", "Acceleration is 9.81m/s."),
        ("Rate is 4 kg/m²/day.", "Rate is 4kg/m²/day.", "Rate is 4kg/m²."),
    ],
)
def test_numeric_unicode_scientific_and_complete_compound_units(
    source: str, same: str, different: str
) -> None:
    req_raw = request().model_dump()
    req_raw["source_claims"][0]["text"] = source
    req = DeepDiveSkeletonRequest.model_validate(req_raw)
    raw = authored_writer_result().model_dump()
    raw["sections"][0]["claims"][0]["text"] = same
    raw["sections"][0]["prose"] = " ".join(
        claim["text"] for claim in raw["sections"][0]["claims"]
    )
    candidate = DeepDiveSkeletonWriterResult.model_validate(raw)
    assert compose_deep_dive_skeleton(req, lambda _: candidate).status == "authored"
    raw["sections"][0]["claims"][0]["text"] = different
    raw["sections"][0]["prose"] = " ".join(
        claim["text"] for claim in raw["sections"][0]["claims"]
    )
    candidate = DeepDiveSkeletonWriterResult.model_validate(raw)
    assert "numeric_fidelity_failed" in compose_deep_dive_skeleton(
        req, lambda _: candidate
    ).gate.failures


@pytest.mark.parametrize(
    ("field", "value", "failure", "message"),
    [
        ("unknown_claim_refs", ("claim",), "unknown_claim_reference", "unknown claim"),
        ("unknown_source_refs", ("span",), "unknown_source_reference", "unknown source"),
        ("unknown_ability_refs", ("ability",), "unknown_ability_reference", "unknown ability"),
    ],
)
def test_gate_receipt_diagnostics_reconcile_bidirectionally(
    field: str, value: tuple[str, ...], failure: str, message: str
) -> None:
    base = compose_deep_dive_skeleton(request(), lambda _: authored_writer_result()).gate
    payload = base.model_dump()
    payload["status"] = "fail"
    payload[field] = value
    payload["failures"] = ("numeric_fidelity_failed",)
    with pytest.raises(ValidationError, match=message):
        DeepDiveGateReceipt.model_validate(payload)

    payload["failures"] = (failure,)
    DeepDiveGateReceipt.model_validate(payload)


def test_gate_receipt_depth_and_coverage_sets_reconcile() -> None:
    base = compose_deep_dive_skeleton(request(), lambda _: authored_writer_result()).gate
    payload = base.model_dump()
    payload["status"] = "fail"
    payload["used_delta_claim_ids"] = ()
    payload["failures"] = ("numeric_fidelity_failed",)
    with pytest.raises(ValidationError, match="delta diagnostics"):
        DeepDiveGateReceipt.model_validate(payload)
    payload["failures"] = ("deep_dive_depth_delta_unavailable",)
    DeepDiveGateReceipt.model_validate(payload)

    payload = base.model_dump()
    payload["status"] = "fail"
    payload["covered_vo_claim_ids"] = ("claim-vo-1",)
    payload["missing_vo_claim_ids"] = ("claim-vo-2",)
    payload["failures"] = ("declared_vo_claim_coverage_failed",)
    DeepDiveGateReceipt.model_validate(payload)

    payload["missing_vo_claim_ids"] = ("claim-vo-1", "claim-vo-2")
    with pytest.raises(ValidationError, match="disjoint"):
        DeepDiveGateReceipt.model_validate(payload)


def test_receipt_authority_inventories_and_exact_partition_are_closed() -> None:
    result = compose_deep_dive_skeleton(request(), lambda _: authored_writer_result())
    gate = result.gate
    assert gate.declared_vo_claim_ids == ("claim-vo-1", "claim-vo-2")
    assert gate.declared_delta_claim_ids == ("claim-delta-1",)
    assert gate.declared_ability_ids == ("ability-1", "ability-2")
    assert gate.declared_span_ids == ("span-1", "span-2")
    assert gate.authority_digest == result.authority_digest
    assert result.authority_digest == deep_dive_authority_digest(request())
    assert gate.candidate_payload_digest == result.candidate_payload_digest

    payload = gate.model_dump()
    payload["covered_vo_claim_ids"] = ("claim-vo-1",)
    with pytest.raises(ValidationError, match="exact partition"):
        DeepDiveGateReceipt.model_validate(payload)

    payload = gate.model_dump()
    payload["used_delta_claim_ids"] = ("fabricated-delta",)
    with pytest.raises(ValidationError, match="declared delta"):
        DeepDiveGateReceipt.model_validate(payload)


def test_result_rejects_fabricated_authority_and_candidate_digests() -> None:
    result = compose_deep_dive_skeleton(request(), lambda _: authored_writer_result())
    payload = result.model_dump()
    payload["authority_digest"] = "sha256:" + "0" * 64
    with pytest.raises(ValidationError, match="authority digest"):
        DeepDiveSkeletonResult.model_validate(payload)

    payload = result.model_dump()
    payload["candidate_payload_digest"] = "sha256:" + "0" * 64
    with pytest.raises(ValidationError, match="candidate payload digest"):
        DeepDiveSkeletonResult.model_validate(payload)

    payload = result.model_dump()
    payload["candidate_payload_digest"] = payload["gate"]["candidate_payload_digest"] = (
        "sha256:" + "0" * 64
    )
    with pytest.raises(ValidationError, match="recomputed candidate payload digest"):
        DeepDiveSkeletonResult.model_validate(payload)


def test_result_rejects_self_consistent_forged_pass_for_unsupported_prose() -> None:
    baseline = compose_deep_dive_skeleton(request(), lambda _: authored_writer_result())
    raw = authored_writer_result().model_dump()
    raw["sections"][0]["claims"][0]["text"] = "An unsupported mechanism changes care."
    raw["sections"][0]["prose"] = " ".join(
        claim["text"] for claim in raw["sections"][0]["claims"]
    )
    unsupported = DeepDiveSkeletonWriterResult.model_validate(raw)
    rejected = compose_deep_dive_skeleton(request(), lambda _: unsupported)
    assert rejected.status == "degraded"

    forged = baseline.model_dump()
    forged["sections"] = raw["sections"]
    forged["candidate_snapshot"] = raw
    forged["candidate_payload_digest"] = rejected.candidate_payload_digest
    forged["gate"]["candidate_payload_digest"] = rejected.candidate_payload_digest
    # All supplied digest and payload fields now reconcile, but the reused PASS
    # receipt did not actually gate this candidate against its authority.
    with pytest.raises(ValidationError, match="recomputed gate receipt"):
        DeepDiveSkeletonResult.model_validate(forged)


def test_canonical_digests_change_only_with_their_bound_payload() -> None:
    baseline = compose_deep_dive_skeleton(request(), lambda _: authored_writer_result())
    req_raw = request().model_dump()
    req_raw["lesson_ref"] = "part-2-revision"
    authority_changed = compose_deep_dive_skeleton(
        DeepDiveSkeletonRequest.model_validate(req_raw), lambda _: authored_writer_result()
    )
    assert authority_changed.authority_digest != baseline.authority_digest
    assert authority_changed.candidate_payload_digest == baseline.candidate_payload_digest

    candidate_raw = authored_writer_result().model_dump()
    candidate_raw["sections"][0]["claims"][0]["text"] = (
        "A workflow symptom can be observed without yet revealing its system-design cause."
    )
    candidate_raw["sections"][0]["prose"] = " ".join(
        claim["text"] for claim in candidate_raw["sections"][0]["claims"]
    )
    candidate = DeepDiveSkeletonWriterResult.model_validate(candidate_raw)
    candidate_changed = compose_deep_dive_skeleton(request(), lambda _: candidate)
    assert candidate_changed.status == "authored"
    assert candidate_changed.authority_digest == baseline.authority_digest
    assert candidate_changed.candidate_payload_digest != baseline.candidate_payload_digest


def test_request_duplicate_claim_and_ability_ids_are_rejected() -> None:
    for field, match in (("source_claims", "claim IDs"), ("abilities", "ability IDs")):
        payload = request().model_dump()
        payload[field] += (payload[field][0],)
        with pytest.raises(ValidationError, match=match):
            DeepDiveSkeletonRequest.model_validate(payload)

    claim = request().source_claims[0].model_dump()
    claim["source_span_refs"] = ("span-1", "span-1")
    with pytest.raises(ValidationError, match="duplicate source span refs"):
        SourceClaim.model_validate(claim)


def test_duplicate_ability_section_is_diagnosed_without_duplicate_claim_identity() -> None:
    raw = authored_writer_result().model_dump()
    raw["sections"][1]["ability_id"] = "ability-1"
    candidate = DeepDiveSkeletonWriterResult.model_validate(raw)
    result = compose_deep_dive_skeleton(request(), lambda _: candidate)
    assert result.status == "degraded"
    assert "duplicate_ability_section" in result.gate.failures


@pytest.mark.parametrize("vo_id", ["claim-vo-1", "claim-vo-2"])
def test_removing_every_declared_vo_claim_is_named(vo_id: str) -> None:
    raw = authored_writer_result().model_dump()
    for section in raw["sections"]:
        section["claims"] = tuple(
            claim for claim in section["claims"] if claim["source_claim_refs"] != (vo_id,)
        )
    raw["sections"] = tuple(section for section in raw["sections"] if section["claims"])
    if len(raw["sections"]) != len(request().abilities):
        # Keep the required section while tracing only a legitimate delta.
        missing_ability = request().abilities[len(raw["sections"])].ability_id
        raw["sections"] += (
            {
                "ability_id": missing_ability,
                "prose": "A first move follows after distinguishing symptom from cause.",
                "claims": ({
                    "skeleton_claim_id": f"replacement-{vo_id}",
                    "text": "A first move follows after distinguishing symptom from cause.",
                    "source_claim_refs": ("claim-delta-1",),
                    "source_span_refs": ("span-2",),
                },),
            },
        )
    raw["bold_terms"] = ({"term": "two stages"},) if vo_id == "claim-vo-1" else ()
    candidate = DeepDiveSkeletonWriterResult.model_validate(raw)
    result = compose_deep_dive_skeleton(request(), lambda _: candidate)
    assert vo_id in result.gate.missing_vo_claim_ids


def test_orphan_span_unicode_boundary_and_explicit_multiability_trace() -> None:
    req_raw = request().model_dump()
    req_raw["source_spans"] += (
        {"span_id": "span-orphan-α", "text": "Orphan context — café.", "source_ref": "deck:α"},
    )
    req_raw["source_claims"] += (
        {
            "claim_id": "claim-orphan-δ",
            "text": "Café context remains source-supported.",
            "source_span_refs": ("span-orphan-α",),
            "role": "source_supported_delta",
        },
    )
    req = DeepDiveSkeletonRequest.model_validate(req_raw)
    raw = authored_writer_result().model_dump()
    repeated = dict(raw["sections"][0]["claims"][1])
    repeated["skeleton_claim_id"] = "skeleton-delta-ability-2"
    raw["sections"][1]["claims"] += (repeated,)
    raw["sections"][1]["prose"] = " ".join(
        claim["text"] for claim in raw["sections"][1]["claims"]
    )
    candidate = DeepDiveSkeletonWriterResult.model_validate(raw)
    assert compose_deep_dive_skeleton(req, lambda _: candidate).status == "authored"


@pytest.mark.parametrize(
    "mutation,expected",
    [
        ("missing_vo", "claim-vo-2"),
        ("missing_delta", "deep_dive_depth_delta_unavailable"),
        ("unknown_claim", "unknown-claim"),
        ("unknown_span", "unknown-span"),
        ("unknown_ability", "unknown-ability"),
        ("ability_order", "ability_order_mismatch"),
        ("numeric", "numeric_fidelity_failed"),
        ("negation", "negation_fidelity_failed"),
        ("source_trace", "source_trace_mismatch"),
    ],
)
def test_mutations_fail_or_degrade_with_inspectable_receipt(mutation: str, expected: str) -> None:
    raw = authored_writer_result().model_dump()
    sections = list(raw["sections"])
    if mutation == "missing_vo":
        sections[1]["claims"][0]["source_claim_refs"] = ("claim-delta-1",)
    elif mutation == "missing_delta":
        sections[0]["claims"] = tuple(
            c for c in sections[0]["claims"] if "claim-delta-1" not in c["source_claim_refs"]
        )
    elif mutation == "unknown_claim":
        sections[0]["claims"][0]["source_claim_refs"] = ("unknown-claim",)
    elif mutation == "unknown_span":
        sections[0]["claims"][0]["source_span_refs"] = ("unknown-span",)
    elif mutation == "unknown_ability":
        sections[0]["ability_id"] = "unknown-ability"
    elif mutation == "ability_order":
        sections.reverse()
        raw["bold_terms"] = tuple(reversed(raw["bold_terms"]))
    elif mutation == "numeric":
        sections[1]["claims"][0]["text"] = "The three stages organize the work."
    elif mutation == "negation":
        sections[0]["claims"][0]["text"] += " This does not expose causes."
    elif mutation == "source_trace":
        sections[0]["claims"][0]["source_span_refs"] = ("span-2",)
    raw["sections"] = tuple(sections)
    candidate = DeepDiveSkeletonWriterResult.model_validate(raw)
    result = compose_deep_dive_skeleton(request(), lambda _: candidate)
    assert result.status in {"degraded", "unavailable"}
    assert result.sections == () and result.bold_terms == ()
    assert expected in result.model_dump_json()


def test_disjoint_rewrite_duplicate_and_missing_ability_cannot_pass() -> None:
    raw = authored_writer_result().model_dump()
    raw["sections"][0]["claims"][0]["source_claim_refs"] = ()
    with pytest.raises(ValidationError):
        DeepDiveSkeletonWriterResult.model_validate(raw)
    raw = authored_writer_result().model_dump()
    raw["sections"] = (raw["sections"][0], raw["sections"][0])
    with pytest.raises(ValidationError, match="duplicate skeleton claim IDs"):
        DeepDiveSkeletonWriterResult.model_validate(raw)


def test_bold_metadata_mismatch_is_rejected_before_adapter() -> None:
    raw = authored_writer_result().model_dump()
    raw["bold_terms"] = ({"term": "different"},)
    with pytest.raises(ValidationError, match="bold marker/metadata mismatch"):
        DeepDiveSkeletonWriterResult.model_validate(raw)


@pytest.mark.parametrize(
    "prose",
    [
        "REVOICE-REQUIRED: draft",
        "> transcript scaffold",
        "As shown on this slide, distinguish symptoms.",
        "Voice-profile: conversational",
        "Narration unavailable.",
    ],
)
def test_non_read_prose_chrome_fails_transform_gate(prose: str) -> None:
    raw = authored_writer_result().model_dump()
    raw["sections"][0]["prose"] = prose
    raw["bold_terms"] = ({"term": "two stages"},)
    candidate = DeepDiveSkeletonWriterResult.model_validate(raw)
    result = compose_deep_dive_skeleton(request(), lambda _: candidate)
    assert result.status == "degraded"
    assert "transform_only_read_prose_failed" in result.gate.failures


@pytest.mark.parametrize(
    "prose,terms",
    [
        ("An unmatched **term appears.", ("term",)),
        ("A nested **outer **inner** marker** appears.", ("outer **inner",)),
        ("A **term** appears.", ("term", "term")),
        ("A **term\nheading** appears.", ("term\nheading",)),
    ],
)
def test_bold_marker_safety(prose: str, terms: tuple[str, ...]) -> None:
    raw = authored_writer_result().model_dump()
    raw["sections"][0]["prose"] = prose
    raw["bold_terms"] = tuple({"term": term} for term in terms)
    with pytest.raises(ValidationError):
        DeepDiveSkeletonWriterResult.model_validate(raw)


def test_reworded_trace_can_pass_and_order_is_stable() -> None:
    result = compose_deep_dive_skeleton(request(), lambda _: authored_writer_result())
    assert "without yet revealing" in result.sections[0].prose
    assert tuple(section.ability_id for section in result.sections) == ("ability-1", "ability-2")
    assert request().source_spans[0].span_id == "span-1"


def test_m3_no_ask_a_model_or_runtime_boundary_and_shapes() -> None:
    source = MODULE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    forbidden = {
        "openai", "litellm", "langchain", "langgraph", "orchestrator",
        "specialists", "research_packet", "workbook_producer", "prose_uplift",
    }
    assert not {name for name in imports if any(token in name for token in forbidden)}
    calls = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert not calls & {"open", "Path", "getenv"}
    fields = set(DeepDiveSkeletonRequest.model_fields) | set(
        DeepDiveSkeletonWriterResult.model_fields
    )
    assert not fields & {
        "research_packet", "ask_a_digest", "citations", "references",
        "model", "model_config", "run_dir", "filesystem_path",
    }
    manifest = json.loads((FIXTURES / "semantic_manifest.json").read_text(encoding="utf-8"))
    assert manifest["gate_version"] == "deep-dive-skeleton-gate.v1"
    assert "full_semantic_equivalence" in manifest["operator_warn"]
