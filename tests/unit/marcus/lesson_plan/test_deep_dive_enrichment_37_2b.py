"""Story 37.2b — Deep Dive enrichment contracts + the A2 coverage gate.

Every pool/skeleton/render shape derives from the two real runs (protocol
plank 2): the frozen ``a940c5eb`` brief + Ask-A journal output and the
``8b275e5b`` rendered workbook. Mutants are mutated COPIES of those shapes.
"""

from __future__ import annotations

import ast
import hashlib
import json
import shutil
from pathlib import Path

import pytest

from app.marcus.lesson_plan.deep_dive_enrichment import (
    DEEP_DIVE_ENRICHMENT_DEGRADED_MARKER,
    OPERATOR_SEMANTIC_ENRICHMENT_WARNING,
    DeepDiveEnrichedResultV1,
    DeepDiveEnrichedWriterResult,
    DeepDiveEnrichmentAuthorityError,
    DeepDiveEnrichmentExecutionReceiptV1,
    EnrichedDeepDiveClaim,
    WorkbookReviewContributionV1,
    build_deep_dive_enrichment_request,
    build_overlay_covered_input,
    build_workbook_review_contribution,
    compose_deep_dive_enrichment,
    deep_dive_enrichment_gate,
    load_workbook_review_contribution,
    offline_deep_dive_enrichment_writer,
    render_deep_dive_markdown,
    render_deep_dive_reference_lines,
)
from app.marcus.lesson_plan.research_packet import resolve_for_enrichment_pool
from tests.helpers.deep_dive_enrichment_37_2b import (
    ASK_A_OUTPUT_FIXTURE,
    BRIEF_FIXTURE,
    ENRICHMENT_SENTENCE,
    FIXTURE_DIR,
    FIXTURE_MANIFEST,
    LIVE_CITATION_ID,
    RENDERED_WORKBOOK_FIXTURE,
    ask_a_output_payload,
    degraded_candidate,
    enriched_candidate,
    install_brief,
    install_run_json,
    live_pool_entry,
    live_skeleton_binding,
    make_request,
)

# ---------------------------------------------------------------------------
# AC1 — typed claim boundary + strict request binding
# ---------------------------------------------------------------------------


def test_claim_boundary_skeleton_xor_enrichment() -> None:
    with pytest.raises(ValueError, match="requires at least one citation ref"):
        EnrichedDeepDiveClaim(
            enriched_claim_id="c1",
            text="uncited enrichment sentence",
            role="enrichment",
            source_claim_refs=(),
            citation_refs=(),
        )
    with pytest.raises(ValueError, match="requires inherited source claim refs"):
        EnrichedDeepDiveClaim(
            enriched_claim_id="c1",
            text="orphan skeleton sentence",
            role="skeleton",
            source_claim_refs=(),
            citation_refs=(),
        )
    with pytest.raises(ValueError, match="cannot carry citation refs"):
        EnrichedDeepDiveClaim(
            enriched_claim_id="c1",
            text="both-typed sentence",
            role="skeleton",
            source_claim_refs=("claim:vo:seg-01",),
            citation_refs=(LIVE_CITATION_ID,),
        )


def test_duplicate_citation_refs_within_one_claim_reject_named() -> None:
    """Amendment M2b: duplicate citation_refs within one claim is a named reject."""
    with pytest.raises(ValueError, match="duplicate citation refs"):
        EnrichedDeepDiveClaim(
            enriched_claim_id="c1",
            text=f"twice cited. [{LIVE_CITATION_ID}] [{LIVE_CITATION_ID}]",
            role="enrichment",
            source_claim_refs=(),
            citation_refs=(LIVE_CITATION_ID, LIVE_CITATION_ID),
        )


def test_request_digest_and_pool_consistency_reject() -> None:
    request = make_request()
    tampered = request.model_dump(mode="json")
    tampered["pool_packet_digest"] = "b" * 64
    from tests.helpers.deep_dive_enrichment_37_2b import _validate_json

    with pytest.raises(ValueError, match="request digest mismatch"):
        _validate_json(type(request), tampered)


def test_request_rejects_rows_without_scope_or_wrong_status() -> None:
    with pytest.raises(ValueError, match="ready/degraded packet status"):
        make_request(pool_rows=(live_pool_entry(),), pool_status="empty")
    with pytest.raises(ValueError, match="requires usable pool rows"):
        make_request(pool_rows=(), pool_status="ready", pool_scope_digest=None)
    with pytest.raises(ValueError, match="require the bound scope digest"):
        make_request(pool_rows=(live_pool_entry(),), pool_scope_digest=None)


def test_module_imports_lesson_plan_only() -> None:
    """AC1 import guard: the contract module never imports the orchestrator."""
    source = Path("app/marcus/lesson_plan/deep_dive_enrichment.py").read_text("utf-8")
    tree = ast.parse(source)
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    for module in modules:
        assert not module.startswith("app.marcus.orchestrator"), module
        assert not module.startswith("app.specialists"), module


def test_pool_rows_bind_as_the_real_ask_a_knowledge_entry() -> None:
    """Amendment A2: the REAL AskAKnowledgeEntryV1 — no re-typed subset."""
    request = make_request()
    from app.marcus.lesson_plan.ask_a_enrichment import AskAKnowledgeEntryV1

    assert isinstance(request.pool_rows[0], AskAKnowledgeEntryV1)
    assert request.pool_rows[0].evidence_hierarchy_tier == "T4_peer_other"
    # T7/T8 exclusion is model-enforced by the entry's tier Literal.
    mutant = request.pool_rows[0].model_dump(mode="json")
    mutant["evidence_hierarchy_tier"] = "T7_secondary_media"
    with pytest.raises(ValueError):
        AskAKnowledgeEntryV1.model_validate_json(
            json.dumps(mutant, separators=(",", ":")), strict=True
        )


# ---------------------------------------------------------------------------
# AC2 — the A2 coverage matrix (full amended set)
# ---------------------------------------------------------------------------


def test_matrix_row_a_uncited_enrichment_sentence_fails() -> None:
    request = make_request()
    good = enriched_candidate(request)
    section = good.sections[4]
    bad_claim = EnrichedDeepDiveClaim.model_construct(
        enriched_claim_id="mutant",
        text="uncited enrichment sentence",
        role="enrichment",
        source_claim_refs=(),
        citation_refs=(),
    )
    mutated = good.model_construct(
        status="enriched",
        sections=(
            *good.sections[:4],
            section.model_construct(
                ability_id=section.ability_id,
                prose=section.prose + " uncited enrichment sentence",
                claims=(*section.claims, bad_claim),
            ),
            *good.sections[5:],
        ),
        bold_terms=good.bold_terms,
        known_losses=(),
        marker=None,
    )
    receipt = deep_dive_enrichment_gate(request, mutated)
    assert receipt.status == "fail"
    assert "enrichment_claim_uncited" in receipt.failures


def test_matrix_row_b_phantom_citation_fails() -> None:
    request = make_request()
    candidate = enriched_candidate(
        request,
        citation_refs=("ask-a-cite-777",),
        enrichment_text=f"{ENRICHMENT_SENTENCE} [ask-a-cite-777]",
    )
    receipt = deep_dive_enrichment_gate(request, candidate)
    assert receipt.status == "fail"
    assert "unknown_citation_reference" in receipt.failures
    assert receipt.unknown_citation_refs == ("ask-a-cite-777",)
    assert receipt.excluded_citation_refs == ()
    result = compose_deep_dive_enrichment(request, lambda _: candidate)
    assert result.status == "unavailable"
    assert result.known_losses == ("deep_dive_enrichment_reference_validation_failed",)


def test_matrix_row_c_cross_scope_citation_fails() -> None:
    request = make_request(pool_scope_digest="sha256:" + "f" * 64)
    candidate = enriched_candidate(request)
    receipt = deep_dive_enrichment_gate(request, candidate)
    assert receipt.status == "fail"
    assert "cross_scope_citation" in receipt.failures
    assert receipt.cross_scope_citation_refs == (LIVE_CITATION_ID,)


def test_matrix_row_d_empty_pool_empty_honesty_passes_as_degraded() -> None:
    request = make_request(pool_rows=(), pool_status="empty", pool_scope_digest=None)
    candidate = degraded_candidate("deep_dive_enrichment_pool_empty")
    receipt = deep_dive_enrichment_gate(request, candidate)
    assert (receipt.status, receipt.disposition) == ("pass", "degraded_pool_empty")
    assert receipt.available_citation_ids == ()
    result = compose_deep_dive_enrichment(request, lambda _: candidate)
    assert result.status == "degraded"
    assert result.known_losses == ("deep_dive_enrichment_pool_empty",)
    assert result.marker == DEEP_DIVE_ENRICHMENT_DEGRADED_MARKER
    # Skeleton prose intact: the digest-bound skeleton rides the request.
    assert result.request.skeleton.sections == live_skeleton_binding().sections


def test_matrix_row_d_prime_honest_decline_passes_as_degraded() -> None:
    """Amendment J1: pool non-empty + usable, writer uses ZERO rows, honestly."""
    request = make_request()
    candidate = degraded_candidate("deep_dive_enrichment_pool_unused")
    receipt = deep_dive_enrichment_gate(request, candidate)
    assert (receipt.status, receipt.disposition) == ("pass", "degraded_pool_unused")
    assert receipt.unused_citation_ids == (LIVE_CITATION_ID,)
    assert receipt.used_citation_ids == ()
    # M2c: 1-row-pool arithmetic (uncited branch): used + unused == available.
    assert (
        receipt.used_citation_count + receipt.unused_citation_count
        == receipt.available_citation_count
        == 1
    )
    result = compose_deep_dive_enrichment(request, lambda _: candidate)
    assert result.status == "degraded"
    assert result.known_losses == ("deep_dive_enrichment_pool_unused",)


def test_degraded_shape_dishonesty_fails_both_directions() -> None:
    nonempty = make_request()
    receipt = deep_dive_enrichment_gate(
        nonempty, degraded_candidate("deep_dive_enrichment_pool_empty")
    )
    assert receipt.status == "fail"
    assert "degraded_shape_dishonest" in receipt.failures
    empty = make_request(pool_rows=(), pool_status="empty", pool_scope_digest=None)
    receipt = deep_dive_enrichment_gate(
        empty, degraded_candidate("deep_dive_enrichment_pool_unused")
    )
    assert receipt.status == "fail"
    assert "degraded_shape_dishonest" in receipt.failures


def test_matrix_row_e_claiming_enrichment_without_pool_use_fails() -> None:
    request = make_request()
    candidate = enriched_candidate(request, enrichment_ability="none-of-them")
    receipt = deep_dive_enrichment_gate(request, candidate)
    assert receipt.status == "fail"
    assert "enrichment_claimed_without_pool_use" in receipt.failures


def test_matrix_row_f_partial_coverage_reports_unused_rows_exactly() -> None:
    second = live_pool_entry().model_dump(mode="json")
    second["citation_id"] = "ask-a-cite-002"
    from app.marcus.lesson_plan.ask_a_enrichment import AskAKnowledgeEntryV1
    from tests.helpers.deep_dive_enrichment_37_2b import _validate_json

    request = make_request(
        pool_rows=(live_pool_entry(), _validate_json(AskAKnowledgeEntryV1, second))
    )
    candidate = enriched_candidate(request)
    receipt = deep_dive_enrichment_gate(request, candidate)
    assert receipt.status == "pass"
    assert receipt.used_citation_ids == (LIVE_CITATION_ID,)
    assert receipt.unused_citation_ids == ("ask-a-cite-002",)
    assert (
        receipt.used_citation_count + receipt.unused_citation_count
        == receipt.available_citation_count
        == 2
    )


def test_matrix_row_g_declared_refs_must_match_prose_markers() -> None:
    request = make_request()
    # Declared ref with NO inline marker in prose (coverage is measured from
    # prose, never asserted by the writer).
    candidate = enriched_candidate(
        request, enrichment_text=f"{ENRICHMENT_SENTENCE}"
    )
    receipt = deep_dive_enrichment_gate(request, candidate)
    assert receipt.status == "fail"
    assert "citation_declaration_prose_mismatch" in receipt.failures
    # Marker present but not trailing the sentence.
    candidate = enriched_candidate(
        request,
        enrichment_text=f"[{LIVE_CITATION_ID}] {ENRICHMENT_SENTENCE}",
    )
    receipt = deep_dive_enrichment_gate(request, candidate)
    assert "citation_declaration_prose_mismatch" in receipt.failures


def test_matrix_row_h_skeleton_vo_coverage_regression_fails() -> None:
    # lo-g0-003's single skeleton claim traces the covered VO claim
    # claim:vo:seg-02 — dropping it regresses the A3 proper-superset.
    request = make_request()
    candidate = enriched_candidate(request, drop_skeleton_claims_for="lo-g0-003")
    receipt = deep_dive_enrichment_gate(request, candidate)
    assert receipt.status == "fail"
    assert "skeleton_vo_coverage_regressed" in receipt.failures
    assert "skeleton_prose_not_preserved" in receipt.failures


def test_matrix_row_i_a_ability_attribution_honesty_fails() -> None:
    """Amendment M1: citing only rows whose supports_ability_ids exclude X FAILS."""
    entry = live_pool_entry()
    assert "lo-g0-002" not in entry.supports_ability_ids
    request = make_request()
    candidate = enriched_candidate(request, enrichment_ability="lo-g0-002")
    receipt = deep_dive_enrichment_gate(request, candidate)
    assert receipt.status == "fail"
    assert "enrichment_ability_attribution_failed" in receipt.failures
    assert "lo-g0-002" not in receipt.prose_association_covered_ability_ids


def test_matrix_row_i_b_skeleton_side_phantom_ref_fails() -> None:
    """Amendment F1: inherited refs naming claim-ids absent from the skeleton."""
    request = make_request()
    good = enriched_candidate(request)
    first = good.sections[0]
    mutated_claim = first.claims[0].model_construct(
        enriched_claim_id=first.claims[0].enriched_claim_id,
        text=first.claims[0].text,
        role="skeleton",
        source_claim_refs=("claim:phantom:seg-99",),
        citation_refs=(),
    )
    mutated = good.model_construct(
        status="enriched",
        sections=(
            first.model_construct(
                ability_id=first.ability_id,
                prose=first.prose,
                claims=(mutated_claim, *first.claims[1:]),
            ),
            *good.sections[1:],
        ),
        bold_terms=good.bold_terms,
        known_losses=(),
        marker=None,
    )
    receipt = deep_dive_enrichment_gate(request, mutated)
    assert receipt.status == "fail"
    assert "skeleton_claim_phantom_reference" in receipt.failures


def test_amendment_m2a_excluded_citation_distinguishable_from_invented() -> None:
    request = make_request(excluded_citation_ids=("ask-a-cite-009",))
    candidate = enriched_candidate(
        request,
        citation_refs=("ask-a-cite-009",),
        enrichment_text=f"{ENRICHMENT_SENTENCE} [ask-a-cite-009]",
    )
    receipt = deep_dive_enrichment_gate(request, candidate)
    assert receipt.status == "fail"
    assert "excluded_citation_reference" in receipt.failures
    assert "unknown_citation_reference" not in receipt.failures
    assert receipt.excluded_citation_refs == ("ask-a-cite-009",)
    assert receipt.unknown_citation_refs == ()


def test_stray_marker_in_skeleton_claim_fails() -> None:
    request = make_request()
    good = enriched_candidate(request)
    first = good.sections[0]
    tampered_text = f"{first.claims[0].text} [{LIVE_CITATION_ID}]"
    mutated_claim = first.claims[0].model_construct(
        enriched_claim_id=first.claims[0].enriched_claim_id,
        text=tampered_text,
        role="skeleton",
        source_claim_refs=first.claims[0].source_claim_refs,
        citation_refs=(),
    )
    mutated = good.model_construct(
        status="enriched",
        sections=(
            first.model_construct(
                ability_id=first.ability_id,
                prose=first.prose,
                claims=(mutated_claim, *first.claims[1:]),
            ),
            *good.sections[1:],
        ),
        bold_terms=good.bold_terms,
        known_losses=(),
        marker=None,
    )
    receipt = deep_dive_enrichment_gate(request, mutated)
    assert "stray_citation_marker_in_skeleton_claim" in receipt.failures


def test_one_row_pool_arithmetic_cited_branch() -> None:
    """Amendment M2c (cited branch): used + unused == available at available=1."""
    request = make_request()
    receipt = deep_dive_enrichment_gate(request, enriched_candidate(request))
    assert receipt.status == "pass"
    assert (receipt.used_citation_count, receipt.unused_citation_count) == (1, 0)
    assert receipt.available_citation_count == 1


def test_receipt_is_inspectable_never_only_boolean() -> None:
    request = make_request()
    receipt = deep_dive_enrichment_gate(request, enriched_candidate(request))
    assert receipt.claim_bindings  # per-claim citation bindings
    assert receipt.intake_covered_ability_ids  # 38.1 association-covered lists
    assert receipt.prose_association_covered_ability_ids == ("lo-g0-005",)
    assert receipt.operator_warnings == (OPERATOR_SEMANTIC_ENRICHMENT_WARNING,)


def test_honesty_boundary_declared_verbatim_in_module_docstring() -> None:
    import app.marcus.lesson_plan.deep_dive_enrichment as module

    doc = module.__doc__ or ""
    assert "operator prose spot-check WARN" in doc
    assert "claim-typing / citation-binding / coverage arithmetic" in doc
    assert "association-covered" in doc


# ---------------------------------------------------------------------------
# AC4 — bold-term continuity for 39.1
# ---------------------------------------------------------------------------


def test_skeleton_bold_terms_preserved_exactly() -> None:
    request = make_request()
    good = enriched_candidate(request)
    skeleton_terms = tuple(term.term for term in request.skeleton.bold_terms)
    candidate_terms = tuple(term.term for term in good.bold_terms)
    assert set(skeleton_terms) <= set(candidate_terms)
    receipt = deep_dive_enrichment_gate(request, good)
    assert "skeleton_bold_terms_not_preserved" not in receipt.failures


def test_dropping_a_skeleton_bold_term_fails() -> None:
    request = make_request()
    good = enriched_candidate(request)
    target = None
    for index, section in enumerate(good.sections):
        if "**spending**" in section.prose:
            target = index
            break
    assert target is not None
    section = good.sections[target]
    stripped_prose = section.prose.replace("**spending**", "spending")
    new_claims = tuple(
        claim.model_construct(
            enriched_claim_id=claim.enriched_claim_id,
            text=claim.text.replace("**spending**", "spending"),
            role=claim.role,
            source_claim_refs=claim.source_claim_refs,
            citation_refs=claim.citation_refs,
        )
        for claim in section.claims
    )
    mutated = good.model_construct(
        status="enriched",
        sections=(
            *good.sections[:target],
            section.model_construct(
                ability_id=section.ability_id, prose=stripped_prose, claims=new_claims
            ),
            *good.sections[target + 1 :],
        ),
        bold_terms=tuple(t for t in good.bold_terms if t.term != "spending"),
        known_losses=(),
        marker=None,
    )
    receipt = deep_dive_enrichment_gate(request, mutated)
    assert receipt.status == "fail"
    assert "skeleton_bold_terms_not_preserved" in receipt.failures


def test_new_bold_term_traced_to_used_citation_passes() -> None:
    request = make_request()
    text = (
        "Digital health tools face many challenges and **hurdles** on the "
        f"path to healthcare quality. [{LIVE_CITATION_ID}]"
    )
    candidate = enriched_candidate(request, enrichment_text=text)
    receipt = deep_dive_enrichment_gate(request, candidate)
    assert receipt.status == "pass"
    assert "untraced_new_bold_term" not in receipt.failures


def test_new_bold_term_without_citation_trace_rejects() -> None:
    request = make_request()
    text = (
        "Digital health tools face many challenges in the **metaverse** era. "
        f"[{LIVE_CITATION_ID}]"
    )
    candidate = enriched_candidate(request, enrichment_text=text)
    receipt = deep_dive_enrichment_gate(request, candidate)
    assert receipt.status == "fail"
    assert "untraced_new_bold_term" in receipt.failures


def test_marker_metadata_mismatch_and_unmatched_markup_reject_at_model() -> None:
    request = make_request()
    good = enriched_candidate(request)
    with pytest.raises(ValueError, match="bold marker/metadata mismatch"):
        DeepDiveEnrichedWriterResult(
            status="enriched",
            sections=good.sections,
            bold_terms=good.bold_terms[:-1],
            known_losses=(),
            marker=None,
        )
    with pytest.raises(ValueError, match="unmatched bold marker"):
        enriched_candidate(
            request,
            enrichment_text=f"Unbalanced **bold marker. [{LIVE_CITATION_ID}]",
        )


def test_citation_markers_excluded_from_bold_parity_text() -> None:
    request = make_request()
    candidate = enriched_candidate(request)
    receipt = deep_dive_enrichment_gate(request, candidate)
    assert "bold_term_parity_failed" not in receipt.failures


# ---------------------------------------------------------------------------
# Numeric fidelity over enriched prose (37.2a witnesses re-run)
# ---------------------------------------------------------------------------


def test_enrichment_numeral_from_cited_excerpt_passes() -> None:
    request = make_request()
    text = (
        "The 4th Industrial Revolution reshapes healthcare quality delivery. "
        f"[{LIVE_CITATION_ID}]"
    )
    candidate = enriched_candidate(request, enrichment_text=text)
    receipt = deep_dive_enrichment_gate(request, candidate)
    assert receipt.status == "pass"


def test_enrichment_numeral_absent_from_cited_excerpt_fails() -> None:
    request = make_request()
    text = (
        "Digital tools deliver a 99% improvement in healthcare quality. "
        f"[{LIVE_CITATION_ID}]"
    )
    candidate = enriched_candidate(request, enrichment_text=text)
    receipt = deep_dive_enrichment_gate(request, candidate)
    assert receipt.status == "fail"
    assert "enrichment_numeric_fidelity_failed" in receipt.failures


# ---------------------------------------------------------------------------
# Result reconciliation + constructed-model revalidation
# ---------------------------------------------------------------------------


def test_result_roundtrips_and_rejects_tampered_gate() -> None:
    request = make_request()
    result = compose_deep_dive_enrichment(request, lambda _: enriched_candidate(request))
    reloaded = DeepDiveEnrichedResultV1.model_validate_json(
        result.model_dump_json(), strict=True
    )
    assert reloaded == result
    tampered = json.loads(result.model_dump_json())
    tampered["gate"]["used_citation_ids"] = []
    tampered["gate"]["used_citation_count"] = 0
    tampered["gate"]["unused_citation_ids"] = [LIVE_CITATION_ID]
    tampered["gate"]["unused_citation_count"] = 1
    with pytest.raises(ValueError):
        DeepDiveEnrichedResultV1.model_validate_json(
            json.dumps(tampered, separators=(",", ":")), strict=True
        )


def test_enriched_status_with_zero_citations_cannot_persist() -> None:
    """Negative shape: an enriched-status result claiming no used rows rejects."""
    request = make_request()
    result = compose_deep_dive_enrichment(request, lambda _: enriched_candidate(request))
    tampered = json.loads(result.model_dump_json())
    for section in tampered["sections"]:
        section["claims"] = [
            claim for claim in section["claims"] if claim["role"] == "skeleton"
        ]
        section["prose"] = " ".join(claim["text"] for claim in section["claims"])
    for section in tampered["candidate_snapshot"]["sections"]:
        section["claims"] = [
            claim for claim in section["claims"] if claim["role"] == "skeleton"
        ]
        section["prose"] = " ".join(claim["text"] for claim in section["claims"])
    with pytest.raises(ValueError):
        DeepDiveEnrichedResultV1.model_validate_json(
            json.dumps(tampered, separators=(",", ":")), strict=True
        )


def test_offline_writer_composes_honest_unavailable() -> None:
    request = make_request()
    result = compose_deep_dive_enrichment(request, offline_deep_dive_enrichment_writer)
    assert result.status == "unavailable"
    assert result.known_losses == ("deep_dive_enrichment_writer_unavailable",)
    assert result.gate.disposition == "unavailable"
    assert result.gate.status == "pass"


# ---------------------------------------------------------------------------
# AC3 — pool consumption is digest-bound and sole-sourced
# ---------------------------------------------------------------------------


def _generic_research_output() -> dict[str, object]:
    return {
        "research_entries": [
            {
                "citation_id": "cite-001",
                "source_ref": "retrieval:scite:10.9999/not-ask-a",
                "provider": "scite",
                "source_id": "10.9999/not-ask-a",
                "source_hash": "sha256:" + "1" * 64,
                "evidence_hierarchy_tier": "T4_peer_other",
                "peer_reviewed": True,
                "provider_provenance": ["scite"],
                "triangulation_status": "single_provider",
            }
        ]
    }


def test_builder_binds_the_exact_ask_a_packet_and_witnesses_same_digest(
    tmp_path: Path,
) -> None:
    install_brief(tmp_path)
    install_run_json(
        tmp_path,
        ask_a_output=ask_a_output_payload(),
        extra_contributions=(
            ("research_wiring", "04.55", _generic_research_output(), "deterministic"),
        ),
    )
    request = build_deep_dive_enrichment_request(tmp_path)
    packet = resolve_for_enrichment_pool(tmp_path)
    # Sole-sourced: ONLY the ask_a_enrichment@07W.2 packet; the generic 04.55
    # row never appears.
    assert request.pool_packet_digest == packet.packet_digest
    assert [row.citation_id for row in request.pool_rows] == [LIVE_CITATION_ID]
    assert all(row.source_id != "10.9999/not-ask-a" for row in request.pool_rows)
    # Reload witnesses the identical digest.
    assert build_deep_dive_enrichment_request(tmp_path) == request
    assert request.pool_scope_digest == request.pool_rows[0].scope_digest
    assert request.intake_covered_ability_ids == tuple(
        ask_a_output_payload()["research_intake"]["covered_ability_ids"]
    )


def test_builder_accepts_empty_pool_as_degraded_path_not_failure(
    tmp_path: Path,
) -> None:
    install_brief(tmp_path)
    install_run_json(tmp_path, ask_a_output=None)
    request = build_deep_dive_enrichment_request(tmp_path)
    assert request.pool_status == "empty"
    assert request.pool_rows == ()
    assert "packet_contribution_absent:ask_a_enrichment@07W.2" in request.pool_known_losses


def test_builder_requires_authored_skeleton(tmp_path: Path) -> None:
    install_run_json(tmp_path, ask_a_output=ask_a_output_payload())
    with pytest.raises(DeepDiveEnrichmentAuthorityError):
        build_deep_dive_enrichment_request(tmp_path)


def test_t7_t8_rows_are_excluded_upstream_into_known_losses(tmp_path: Path) -> None:
    """AC3 fixture pin: credibility-excluded rows land in known_losses, never
    in the pool — and the exclusion record shape (index-keyed, no citation id)
    is pinned so M2a's DISTINGUISHABLE path stays honest."""
    from types import SimpleNamespace

    from app.marcus.orchestrator import ask_a_research_wiring

    journal = ask_a_output_payload()
    scope_payload = journal["research_intake"]["scope"]
    from app.marcus.lesson_plan.ask_a_enrichment import AskARetrievalScopeV1

    scope = AskARetrievalScopeV1.model_validate_json(
        json.dumps(scope_payload, separators=(",", ":")), strict=True
    )
    live_row = {
        "provider": "scite",
        "source_id": "10.5772/intechopen.94054",
        "title": journal["research_entries"][0]["title"],
        "body": journal["research_entries"][0]["evidence_excerpt"],
        "provider_metadata": {"scite": {"venue": "IntechOpen"}},
        "authority_tier": "peer_reviewed",
    }
    # Mutated copy of the frozen live row: a non-indexed provider with no
    # usable identifier classifies T8_unknown -> credibility-excluded.
    excluded_row = dict(live_row)
    excluded_row.update({"provider": "webnews", "source_id": "  ", "authority_tier": None})
    tier, _ = __import__(
        "app.marcus.orchestrator.research_credibility", fromlist=["x"]
    ).classify_evidence_hierarchy(SimpleNamespace(**excluded_row))
    assert tier in {"T7_secondary_media", "T8_unknown"}
    output, records = ask_a_research_wiring._build_completed(
        scope,
        raw_rows=[live_row, excluded_row],
        provider_iterations=(1,),
        refinement_logs=(),
        provider_outcomes=("accepted",),
        provider_receipts=(
            {"provider": "scite", "acceptance_met": True, "iterations_used": 1, "row_count": 2},
        ),
    )
    assert any(
        loss.startswith("ask_a_row_") and ":1" in loss for loss in output.known_losses
    )
    assert all(
        entry.evidence_hierarchy_tier
        not in {"T7_secondary_media", "T8_unknown"}
        for entry in output.research_entries
    )
    # The request built over this packet carries the loss record and no
    # excluded row — pinning that upstream exclusions carry NO citation id.
    install_brief(tmp_path)
    install_run_json(tmp_path, ask_a_output=output.model_dump(mode="json"))
    request = build_deep_dive_enrichment_request(tmp_path)
    assert any(loss.startswith("ask_a_row_") for loss in request.pool_known_losses)
    assert request.excluded_citation_ids == ()
    assert len(request.pool_rows) == 1


# ---------------------------------------------------------------------------
# D2.4 — overlay-covered dedup INPUT threading
# ---------------------------------------------------------------------------


def test_overlay_covered_input_present_from_real_card(tmp_path: Path) -> None:
    shutil.copy2(FIXTURE_DIR / "g0-enrichment.json", tmp_path / "g0-enrichment.json")
    overlay = build_overlay_covered_input(tmp_path)
    assert overlay.card_present is True
    assert len(overlay.covered_learning_objectives) == 10
    assert overlay.covered_exercise_facts
    install_brief(tmp_path)
    install_run_json(tmp_path, ask_a_output=ask_a_output_payload())
    request = build_deep_dive_enrichment_request(tmp_path)
    assert request.overlay_covered == overlay


def test_overlay_covered_input_honest_empty_without_card(tmp_path: Path) -> None:
    overlay = build_overlay_covered_input(tmp_path)
    assert overlay.card_present is False
    assert overlay.covered_learning_objectives == ()
    assert overlay.covered_exercise_facts == ()
    with pytest.raises(ValueError, match="honest-empty"):
        type(overlay)(
            card_present=False,
            covered_learning_objectives=(),
            covered_exercise_facts=("leaked fact",),
        )


# ---------------------------------------------------------------------------
# Contribution contract + disk reader + render seam
# ---------------------------------------------------------------------------


def _live_result_and_receipt() -> tuple[
    DeepDiveEnrichedResultV1, DeepDiveEnrichmentExecutionReceiptV1
]:
    request = make_request()
    result = compose_deep_dive_enrichment(request, lambda _: enriched_candidate(request))
    receipt = DeepDiveEnrichmentExecutionReceiptV1(
        mode="live",
        calls=1,
        idempotency_key="sha256:" + "2" * 64,
        request_digest=request.request_digest,
        pool_packet_digest=request.pool_packet_digest,
        model="gpt-5",
        model_config_digest="sha256:" + "3" * 64,
        cost_usd=0.05,
    )
    return result, receipt


def test_contribution_roundtrip_and_typed_losses() -> None:
    result, receipt = _live_result_and_receipt()
    contribution = build_workbook_review_contribution(result, receipt)
    assert contribution.known_losses == (
        "check_writer_not_yet_wired",
        "reflection_writer_not_yet_wired",
    )
    unavailable = build_workbook_review_contribution(None, None)
    assert unavailable.known_losses == (
        "deep_dive_enrichment_skeleton_unavailable",
        "check_writer_not_yet_wired",
        "reflection_writer_not_yet_wired",
    )
    tampered = json.loads(contribution.model_dump_json())
    tampered["known_losses"] = ["check_writer_not_yet_wired"]
    with pytest.raises(ValueError):
        WorkbookReviewContributionV1.model_validate_json(
            json.dumps(tampered, separators=(",", ":")), strict=True
        )


def test_load_contribution_reads_activated_and_ignores_stub(tmp_path: Path) -> None:
    result, receipt = _live_result_and_receipt()
    contribution = build_workbook_review_contribution(result, receipt)
    install_run_json(
        tmp_path,
        ask_a_output=None,
        extra_contributions=(
            (
                "workbook_review",
                "07W.3",
                json.loads(contribution.model_dump_json()),
                "gpt-5",
            ),
        ),
    )
    loaded = load_workbook_review_contribution(tmp_path)
    assert loaded == contribution
    stub_dir = tmp_path / "stub-run"
    stub_dir.mkdir()
    install_run_json(
        stub_dir,
        ask_a_output=None,
        extra_contributions=(
            (
                "workbook_review",
                "07W.3",
                {
                    "stub_status": "not_yet_wired",
                    "review_payload": {},
                    "known_losses": ["semantic_writers_not_yet_wired"],
                },
                "deterministic-workbook-band-stub",
            ),
        ),
    )
    assert load_workbook_review_contribution(stub_dir) is None
    assert load_workbook_review_contribution(tmp_path / "absent") is None


def test_load_contribution_fails_loud_on_invalid_activated_payload(
    tmp_path: Path,
) -> None:
    result, receipt = _live_result_and_receipt()
    contribution = json.loads(build_workbook_review_contribution(result, receipt).model_dump_json())
    contribution["output_digest"] = "sha256:" + "9" * 64
    install_run_json(
        tmp_path,
        ask_a_output=None,
        extra_contributions=(("workbook_review", "07W.3", contribution, "gpt-5"),),
    )
    with pytest.raises(ValueError, match="workbook review contribution contract"):
        load_workbook_review_contribution(tmp_path)


def test_render_enriched_carries_markers_bold_and_ability_order() -> None:
    result, receipt = _live_result_and_receipt()
    contribution = build_workbook_review_contribution(result, receipt)
    markdown = render_deep_dive_markdown(contribution)
    ability_order = [s.ability_id for s in result.sections]
    positions = [markdown.index(f"### {ability}") for ability in ability_order]
    assert positions == sorted(positions)
    assert f"[{LIVE_CITATION_ID}]" in markdown
    assert "**spending**" in markdown
    assert "Deep Dive enrichment loss:" not in markdown
    references = render_deep_dive_reference_lines(contribution)
    assert len(references) == 1
    assert f"citation_id: `{LIVE_CITATION_ID}`" in references[0]
    assert "https://doi.org/10.5772/intechopen.94054" in references[0]
    assert "tier=T4_peer_other" in references[0]


def test_render_degraded_is_honest_note_with_zero_markers() -> None:
    request = make_request()
    result = compose_deep_dive_enrichment(
        request, lambda _: degraded_candidate("deep_dive_enrichment_pool_unused")
    )
    receipt = DeepDiveEnrichmentExecutionReceiptV1(
        mode="offline_stub",
        calls=0,
        idempotency_key="sha256:" + "2" * 64,
        request_digest=request.request_digest,
        pool_packet_digest=request.pool_packet_digest,
    )
    contribution = build_workbook_review_contribution(result, receipt)
    markdown = render_deep_dive_markdown(contribution)
    assert "Deep Dive enrichment loss: deep_dive_enrichment_pool_unused" in markdown
    assert "ask-a-cite-" not in markdown
    # Skeleton prose stands without pool citations.
    assert "### lo-g0-001" in markdown
    assert render_deep_dive_reference_lines(contribution) == ()


def test_render_not_run_and_skeleton_unavailable_notes() -> None:
    assert "ask-a-cite-" not in render_deep_dive_markdown(None)
    unavailable = build_workbook_review_contribution(None, None)
    markdown = render_deep_dive_markdown(unavailable)
    assert "deep_dive_enrichment_skeleton_unavailable" in markdown
    assert "ask-a-cite-" not in markdown


# ---------------------------------------------------------------------------
# Fixture digest tripwire (protocol drift-flags amendment)
# ---------------------------------------------------------------------------


def test_fixture_manifest_digests_and_schema_versions_pinned() -> None:
    manifest = json.loads(FIXTURE_MANIFEST.read_text("utf-8"))
    for name, row in manifest["fixtures"].items():
        data = (FIXTURE_DIR / name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == row["sha256"], (
            f"fixture {name} drifted from its frozen live shape — a schema_version "
            "bump requires deliberately re-freezing the fixture + this manifest"
        )
    brief = json.loads(BRIEF_FIXTURE.read_text("utf-8"))
    assert brief["payload"]["schema_version"] == (
        manifest["fixtures"]["workbook-brief.v1.json"]["pinned_schema_version"]
    )
    output = json.loads(ASK_A_OUTPUT_FIXTURE.read_text("utf-8"))
    assert output["schema_version"] == (
        manifest["fixtures"]["ask-a-contribution-output.v1.json"]["pinned_schema_version"]
    )
    assert output["research_entries"][0]["schema_version"] == (
        manifest["fixtures"]["ask-a-contribution-output.v1.json"]["entry_schema_version"]
    )
    assert RENDERED_WORKBOOK_FIXTURE.read_text("utf-8").startswith("# Workbook:")


# ---------------------------------------------------------------------------
# Remediation pins (orchestrator-triaged set, 2026-07-15)
# ---------------------------------------------------------------------------


def _live_receipt_for(request) -> DeepDiveEnrichmentExecutionReceiptV1:
    return DeepDiveEnrichmentExecutionReceiptV1(
        mode="live",
        calls=1,
        idempotency_key="sha256:" + "2" * 64,
        request_digest=request.request_digest,
        pool_packet_digest=request.pool_packet_digest,
        model="gpt-5",
        model_config_digest="sha256:" + "3" * 64,
        cost_usd=0.05,
    )


def test_r8_non_supporting_extra_citation_fails_citation_ability_mismatch() -> None:
    """R8: EVERY cited row must support the section's ability — one supporting
    row plus one irrelevant row fails ``citation_ability_mismatch``, a tag
    DISTINCT from the all-rows ``enrichment_ability_attribution_failed``."""
    from tests.helpers.deep_dive_enrichment_37_2b import mutated_pool_entry

    irrelevant = mutated_pool_entry(
        citation_id="ask-a-cite-002",
        supports_ability_ids=["lo-g0-001"],
        matched_ability_tokens={"lo-g0-001": ["healthcare"]},
    )
    assert "lo-g0-005" not in irrelevant.supports_ability_ids
    request = make_request(pool_rows=(live_pool_entry(), irrelevant))
    candidate = enriched_candidate(
        request,
        citation_refs=(LIVE_CITATION_ID, "ask-a-cite-002"),
        enrichment_text=(
            f"{ENRICHMENT_SENTENCE} [{LIVE_CITATION_ID}] [ask-a-cite-002]"
        ),
    )
    receipt = deep_dive_enrichment_gate(request, candidate)
    assert receipt.status == "fail"
    assert "citation_ability_mismatch" in receipt.failures
    # Distinct from the all-rows case: at least one cited row DOES support.
    assert "enrichment_ability_attribution_failed" not in receipt.failures


def test_r8_all_rows_case_carries_both_tags() -> None:
    """The all-rows failure subsumes the per-row tag; both are recorded."""
    request = make_request()
    candidate = enriched_candidate(request, enrichment_ability="lo-g0-002")
    receipt = deep_dive_enrichment_gate(request, candidate)
    assert "citation_ability_mismatch" in receipt.failures
    assert "enrichment_ability_attribution_failed" in receipt.failures


def test_r11_marker_only_claim_fails_empty_sentence() -> None:
    request = make_request()
    candidate = enriched_candidate(request, enrichment_text=f"[{LIVE_CITATION_ID}]")
    receipt = deep_dive_enrichment_gate(request, candidate)
    assert receipt.status == "fail"
    assert "enrichment_claim_empty_sentence" in receipt.failures
    whitespace = enriched_candidate(
        request, enrichment_text=f"   [{LIVE_CITATION_ID}]"
    )
    receipt = deep_dive_enrichment_gate(request, whitespace)
    assert "enrichment_claim_empty_sentence" in receipt.failures


def test_r16_cross_claim_bold_term_laundering_fails() -> None:
    """R16: a NEW bold term must trace to a row cited by the CLAIM containing
    it — a different claim citing a term-bearing row cannot launder it."""
    from tests.helpers.deep_dive_enrichment_37_2b import mutated_pool_entry

    lacking = mutated_pool_entry(
        citation_id="ask-a-cite-002",
        evidence_excerpt=live_pool_entry().evidence_excerpt.replace(
            "hurdles", "obstacles"
        ),
    )
    assert "hurdles" not in lacking.evidence_excerpt
    request = make_request(pool_rows=(live_pool_entry(), lacking))
    candidate = enriched_candidate(
        request,
        # Claim A bolds **hurdles** but cites ONLY the excerpt that lacks it.
        citation_refs=("ask-a-cite-002",),
        enrichment_text=(
            "Digital health tools face many challenges and **hurdles** on the "
            "path to healthcare quality. [ask-a-cite-002]"
        ),
        # Claim B cites the term-bearing row — under the removed
        # document-global fallback this laundered the trace.
        extra_enrichment_claims=(
            (f"{ENRICHMENT_SENTENCE} [{LIVE_CITATION_ID}]", (LIVE_CITATION_ID,)),
        ),
    )
    receipt = deep_dive_enrichment_gate(request, candidate)
    assert receipt.status == "fail"
    assert "untraced_new_bold_term" in receipt.failures
    # Control: the SAME term bolded in the claim that cites the term-bearing
    # row passes (claim-local trace satisfied).
    control = enriched_candidate(
        request,
        citation_refs=(LIVE_CITATION_ID,),
        enrichment_text=(
            "Digital health tools face many challenges and **hurdles** on the "
            f"path to healthcare quality. [{LIVE_CITATION_ID}]"
        ),
    )
    receipt = deep_dive_enrichment_gate(request, control)
    assert "untraced_new_bold_term" not in receipt.failures


def test_r9_non_doi_source_id_renders_source_ref_only_entry() -> None:
    """R9: no fabricated doi.org link for a non-DOI source_id; a blank title
    renders the source_ref as the line label (no '- . ' artifacts)."""
    from tests.helpers.deep_dive_enrichment_37_2b import mutated_pool_entry

    non_doi = mutated_pool_entry(
        source_id="PMC7654321",
        source_ref="retrieval:pubmed:PMC7654321",
        title="",
    )
    request = make_request(pool_rows=(non_doi,))
    result = compose_deep_dive_enrichment(request, lambda _: enriched_candidate(request))
    assert result.status == "enriched"
    contribution = build_workbook_review_contribution(result, _live_receipt_for(request))
    lines = render_deep_dive_reference_lines(contribution)
    assert len(lines) == 1
    assert "https://doi.org" not in lines[0]
    assert lines[0].startswith("- retrieval:pubmed:PMC7654321.")
    assert "- . " not in lines[0]
    assert "source_ref: `retrieval:pubmed:PMC7654321`" in lines[0]
    # A DOI-shaped source_id keeps its resolvable link (existing live shape).
    request = make_request()
    result = compose_deep_dive_enrichment(request, lambda _: enriched_candidate(request))
    lines = render_deep_dive_reference_lines(
        build_workbook_review_contribution(result, _live_receipt_for(request))
    )
    assert "https://doi.org/10.5772/intechopen.94054" in lines[0]


def test_r2_unavailable_shape_dishonest_rejected_at_receipt_seam() -> None:
    """R2: live receipt with calls>=1 + a writer-unavailable candidate is
    dishonest; honest OFFLINE unavailable still passes."""
    request = make_request()
    result = compose_deep_dive_enrichment(request, offline_deep_dive_enrichment_writer)
    assert result.status == "unavailable"
    with pytest.raises(ValueError, match="unavailable_shape_dishonest"):
        build_workbook_review_contribution(result, _live_receipt_for(request))
    offline_receipt = DeepDiveEnrichmentExecutionReceiptV1(
        mode="offline_stub",
        calls=0,
        idempotency_key="sha256:" + "2" * 64,
        request_digest=request.request_digest,
        pool_packet_digest=request.pool_packet_digest,
    )
    contribution = build_workbook_review_contribution(result, offline_receipt)
    assert contribution.deep_dive_enrichment is not None
    assert contribution.deep_dive_enrichment.status == "unavailable"


def test_r5_skeleton_binding_raises_typed_not_authored_error() -> None:
    from app.marcus.lesson_plan.deep_dive_enrichment import (
        DeepDiveSkeletonNotAuthoredError,
        skeleton_binding_from_result,
    )
    from app.marcus.lesson_plan.deep_dive_projection import (
        DEEP_DIVE_DEGRADED_MARKER,
        DeepDiveSkeletonWriterResult,
        compose_deep_dive_skeleton,
    )
    from app.marcus.lesson_plan.prework_artifact import read_workbook_brief

    authored = read_workbook_brief(FIXTURE_DIR).payload.deep_dive_skeleton
    assert authored is not None
    degraded = compose_deep_dive_skeleton(
        authored.authority,
        lambda _: DeepDiveSkeletonWriterResult(
            status="degraded",
            sections=(),
            bold_terms=(),
            known_losses=("deep_dive_execution_failed",),
            marker=DEEP_DIVE_DEGRADED_MARKER,
        ),
    )
    assert degraded.status == "degraded"
    with pytest.raises(DeepDiveSkeletonNotAuthoredError) as caught:
        skeleton_binding_from_result(degraded)
    assert caught.value.skeleton_status == "degraded"


def test_r5_render_not_authored_skeleton_names_state_not_missing_note() -> None:
    from app.marcus.lesson_plan.deep_dive_enrichment import skeleton_not_authored_loss

    contribution = build_workbook_review_contribution(
        None, None, skeleton_loss=skeleton_not_authored_loss("degraded")
    )
    markdown = render_deep_dive_markdown(contribution)
    assert "deep_dive_enrichment_skeleton_not_authored_degraded" in markdown
    assert "status=degraded" in markdown
    assert "carries no Deep Dive skeleton" not in markdown
    assert "ask-a-cite-" not in markdown
    # The missing-skeleton note stays distinct.
    missing = render_deep_dive_markdown(build_workbook_review_contribution(None, None))
    assert "deep_dive_enrichment_skeleton_unavailable" in missing
    assert "not_authored" not in missing


def test_r7_g2_prose_structure_divergence_fails() -> None:
    """R7: G2 audits citation ids parsed from the RENDERED markdown against the
    manifest built from the contribution's used rows — divergence FAILS."""
    from app.marcus.lesson_plan.deep_dive_enrichment import used_pool_rows
    from app.marcus.lesson_plan.workbook_producer import (
        WorkbookFidelityError,
        audit_citation_fidelity,
        deep_dive_g2_citation_entries,
    )

    request = make_request()
    result = compose_deep_dive_enrichment(request, lambda _: enriched_candidate(request))
    contribution = build_workbook_review_contribution(result, _live_receipt_for(request))
    manifest = {row.source_ref: row.source_hash for row in used_pool_rows(result)}
    conforming = f"Deep dive prose. [{LIVE_CITATION_ID}]"
    audit_citation_fidelity(
        deep_dive_g2_citation_entries(conforming, contribution), manifest
    )
    # Prose-vs-structure divergence mutant: a rendered marker no used row backs.
    divergent = f"Deep dive prose. [{LIVE_CITATION_ID}] Laundered. [ask-a-cite-777]"
    with pytest.raises(WorkbookFidelityError, match="G2 FAIL-mode"):
        audit_citation_fidelity(
            deep_dive_g2_citation_entries(divergent, contribution), manifest
        )
    # A stray marker with NO activated contribution is unresolvable too.
    with pytest.raises(WorkbookFidelityError, match="G2 FAIL-mode"):
        audit_citation_fidelity(
            deep_dive_g2_citation_entries(f"Stray. [{LIVE_CITATION_ID}]", None),
            manifest,
        )


def test_r17_matrix_row_honesty_documented_in_module_and_gate() -> None:
    import app.marcus.lesson_plan.deep_dive_enrichment as module

    doc = module.__doc__ or ""
    assert "Row a is defense-in-depth" in doc
    assert "Row h subsumption ordering" in doc
    gate_doc = module.deep_dive_enrichment_gate.__doc__ or ""
    assert "defense-in-depth" in gate_doc
    receipt_doc = module.DeepDiveEnrichmentGateReceipt.__doc__ or ""
    assert "construction-rejects" in receipt_doc
    assert "skeleton_prose_not_preserved" in receipt_doc
