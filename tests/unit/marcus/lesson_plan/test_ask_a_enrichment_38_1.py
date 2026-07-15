from __future__ import annotations

import hashlib
import json

import pytest
from pydantic import ValidationError

from app.marcus.lesson_plan.ask_a_enrichment import (
    AskAContributionOutputV1,
    AskAExecutionReceiptV1,
    AskAKnowledgeEntryV1,
    AskAResearchIntakeV1,
    build_scope,
    canonical_digest,
    evidence_for_body,
    match_scope_associations,
)
from app.marcus.lesson_plan.deep_dive_projection import DeepDiveAbilityInput
from app.marcus.lesson_plan.research_demand import AskAResearchDemandV1

SHA = "sha256:" + "a" * 64


def _demand() -> AskAResearchDemandV1:
    raw = {
        "schema_version": "ask-a-research-demand.v1",
        "status": "ready",
        "specialist_id": "workbook_brief",
        "node_id": "07W.1",
        "workbook_brief_payload_digest": SHA,
        "skeleton_authority_digest": "sha256:" + "b" * 64,
        "skeleton_candidate_digest": "sha256:" + "c" * 64,
        "abilities": (
            DeepDiveAbilityInput(ability_id="lo-2", text="Compare clinical AI risks"),
            DeepDiveAbilityInput(ability_id="lo-1", text="Explain model drift"),
        ),
        "bold_terms": ({"term": "Model Drift"}, {"term": "Automation Bias"}),
        "source_claim_refs": ("claim-2", "claim-1"),
        "known_losses": (),
    }
    raw["demand_digest"] = canonical_digest(raw)
    return AskAResearchDemandV1.model_validate(raw, strict=True)


def _scope():
    return build_scope(
        _demand(),
        provider_config_fingerprint="sha256:" + "d" * 64,
        posture="gap_fill",
    )


def _entry(scope_digest: str) -> AskAKnowledgeEntryV1:
    body = "Model Drift can increase clinical AI risks."
    excerpt, truncated, body_hash = evidence_for_body(body)
    return AskAKnowledgeEntryV1(
        citation_id="ask-a-cite-001",
        source_ref="retrieval:scite:10.1000/x",
        provider="scite",
        source_id="10.1000/x",
        title="Model Drift evidence",
        source_hash="sha256:" + "e" * 64,
        evidence_hierarchy_tier="T4_peer_other",
        peer_reviewed=True,
        provider_provenance=("scite",),
        triangulation_status="single_provider",
        reliability_score=0.8,
        evidence_excerpt=excerpt,
        evidence_truncated=truncated,
        evidence_body_sha256=body_hash,
        scope_digest=scope_digest,
        supports_ability_ids=("lo-2",),
        supports_bold_terms=("Model Drift",),
        association_algorithm="ask-a-association.v1",
        matched_ability_tokens={"lo-2": ("clinical", "risks")},
        matched_bold_terms=("Model Drift",),
    )


def test_scope_preserves_authority_order_and_binds_complete_query() -> None:
    scope = _scope()
    assert [item.ability_id for item in scope.abilities] == ["lo-2", "lo-1"]
    assert scope.bold_terms == ("Model Drift", "Automation Bias")
    # B4a: query is a topical bold-term intent, not the pipe-delimited meta-string.
    assert all(term in scope.query for term in ("Model Drift", "Automation Bias"))
    assert "|" not in scope.query and "ability[" not in scope.query
    assert "lo-2" not in scope.query and "lo-1" not in scope.query
    assert scope.query_digest == canonical_digest(scope.query)
    assert scope.scope_digest == canonical_digest(
        scope.model_dump(mode="json", exclude={"scope_digest"})
    )


def test_evidence_is_exact_unicode_slice_and_full_body_hash() -> None:
    body = "α" * 2001
    excerpt, truncated, digest = evidence_for_body(body)
    assert excerpt == body[:2000]
    assert truncated is True
    assert digest == "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()


def test_association_requires_exact_term_or_nontrivial_ability_tokens() -> None:
    abilities, terms, matched_tokens, matched_terms = match_scope_associations(
        _scope(), title="Automation   Bias review", body="Clinical AI risks are compared."
    )
    assert abilities == ("lo-2",)
    assert terms == ("Automation Bias",)
    assert matched_tokens == {"lo-2": ("clinical", "risks")}
    assert matched_terms == ("Automation Bias",)


def test_entry_rejects_no_scope_association_and_wrong_evidence_hash() -> None:
    raw = _entry(_scope().scope_digest).model_dump(mode="json")
    raw.update(
        supports_ability_ids=[],
        supports_bold_terms=[],
        matched_ability_tokens={},
        matched_bold_terms=[],
    )
    with pytest.raises(ValidationError, match="association"):
        AskAKnowledgeEntryV1.model_validate_json(json.dumps(raw), strict=True)
    raw = _entry(_scope().scope_digest).model_dump(mode="json")
    raw["evidence_body_sha256"] = "not-a-digest"
    with pytest.raises(ValidationError):
        AskAKnowledgeEntryV1.model_validate_json(json.dumps(raw), strict=True)


def test_completed_output_binds_scope_receipt_intake_and_disposition() -> None:
    scope = _scope()
    entry = _entry(scope.scope_digest)
    receipt = AskAExecutionReceiptV1.build(
        scope=scope,
        dispatcher_invocations=1,
        provider_iterations=(1,),
        refinement_logs=(),
        provider_outcomes=("accepted",),
        provider_receipts=({"provider": "scite"},),
    )
    intake = AskAResearchIntakeV1.build(
        scope=scope,
        execution_receipt=receipt,
        entries=(entry,),
    )
    output = AskAContributionOutputV1.build_completed(
        disposition="completed_ready", intake=intake, entries=(entry,), known_losses=()
    )
    assert output.research_intake.scope == scope
    assert output.research_intake.covered_ability_ids == ("lo-2",)
    assert output.research_intake.uncovered_ability_ids == ("lo-1",)
    mutated = output.model_dump(mode="json")
    mutated["research_entries"][0]["evidence_excerpt"] += "!"
    with pytest.raises(ValidationError):
        AskAContributionOutputV1.model_validate_json(json.dumps(mutated), strict=True)


@pytest.mark.parametrize(
    ("disposition", "loss"),
    [
        ("retryable_demand_not_ready", "ask_a_demand_not_ready"),
        ("retryable_dispatch_disabled", "ask_a_dispatch_disabled"),
        ("retryable_credentials_unavailable", "ask_a_credentials_unavailable"),
    ],
)
def test_retryable_dispositions_are_zero_call_and_journal_free(disposition: str, loss: str) -> None:
    output = AskAContributionOutputV1.build_retryable(disposition=disposition, loss=loss)
    assert output.research_entries == ()
    assert output.dispatcher_invocations == 0
    assert output.research_intake is None
