"""Hermetic tests for the strict Ask-B contract family (38.2 AC 1-4)."""

from __future__ import annotations

import hashlib
import json
from typing import Any

import pytest

from app.marcus.lesson_plan.ask_b_hot_topics import (
    AskBAbilityTokenMatchV1,
    AskBContributionOutputV1,
    AskBExecutionReceiptV1,
    AskBKnowledgeEntryV1,
    AskBResearchIntakeV1,
    AskBRetrievalScopeV1,
    build_scope,
    canonical_digest,
    derive_hot_topics_query,
    evidence_for_body,
    match_ability_associations,
)
from app.marcus.lesson_plan.research_demand import AskBHotTopicsDemandV1


def _digest(payload: object) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _demand(*, scene: bool = True, abilities: list[dict[str, str]] | None = None):
    raw: dict[str, Any] = {
        "schema_version": "ask-b-hot-topics-demand.v1",
        "status": "ready",
        "specialist_id": "workbook_brief",
        "node_id": "07W.1",
        "workbook_brief_payload_digest": "sha256:" + "1" * 64,
        "abilities": abilities
        or [
            {"ability_id": "LO-1", "text": "I will distinguish workflow symptoms."},
            {"ability_id": "LO-2", "text": "I can choose a first automation move."},
        ],
        "scene_digest": ("sha256:" + "2" * 64) if scene else None,
        "scene_text": (
            "A clinic drowns in prior-auth\nfaxes and workflow friction."
            if scene
            else None
        ),
        "known_losses": [] if scene else ["scene_identity_absent"],
    }
    raw["demand_digest"] = _digest({k: v for k, v in raw.items() if k != "demand_digest"})
    return AskBHotTopicsDemandV1.model_validate_json(json.dumps(raw), strict=True)


def _scope(*, scene: bool = True) -> AskBRetrievalScopeV1:
    return build_scope(_demand(scene=scene), provider_config_fingerprint="sha256:" + "e" * 64)


def _entry(scope: AskBRetrievalScopeV1, **overrides: Any) -> AskBKnowledgeEntryV1:
    body = "Workflow symptoms and automation move research evidence."
    excerpt, truncated, body_hash = evidence_for_body(body)
    abilities, matched = match_ability_associations(
        scope, title="Workflow automation", body=excerpt
    )
    base: dict[str, Any] = {
        "citation_id": "ask-b-cite-001",
        "source_ref": "retrieval:scite:10.1000/x",
        "provider": "scite",
        "source_id": "10.1000/x",
        "title": "Workflow automation",
        "source_hash": "sha256:" + "f" * 64,
        "evidence_hierarchy_tier": "T4_peer_other",
        "peer_reviewed": True,
        "provider_provenance": ("scite",),
        "triangulation_status": "single_provider",
        "evidence_excerpt": excerpt,
        "evidence_truncated": truncated,
        "evidence_body_sha256": body_hash,
        "scope_digest": scope.scope_digest,
        "supports_ability_ids": abilities,
        "association_algorithm": "ask-b-association.v1",
        "matched_ability_tokens": matched,
    }
    base.update(overrides)
    return AskBKnowledgeEntryV1(**base)


def _receipt(scope: AskBRetrievalScopeV1) -> AskBExecutionReceiptV1:
    return AskBExecutionReceiptV1.build(
        scope=scope,
        dispatcher_invocations=1,
        provider_iterations=(1,),
        refinement_logs=(),
        provider_outcomes=("accepted",),
        provider_receipts=({"provider": "scite"},),
    )


def test_query_carries_complete_ordered_ability_scope_and_scene() -> None:
    demand = _demand(scene=True)
    query = derive_hot_topics_query(demand)
    first = query.index("[LO-1] I will distinguish workflow symptoms.")
    second = query.index("[LO-2] I can choose a first automation move.")
    assert first < second
    # Multiline scene prose is whitespace-collapsed to one line — no content
    # dropped, no truncation.
    assert "scene: A clinic drowns in prior-auth faxes and workflow friction." in query
    assert "\n" not in query


def test_query_without_scene_omits_scene_clause() -> None:
    query = derive_hot_topics_query(_demand(scene=False))
    assert "scene:" not in query
    assert "[LO-1]" in query and "[LO-2]" in query


def test_scope_binds_demand_and_mirrors_scene_loss() -> None:
    with_scene = _scope(scene=True)
    assert with_scene.known_scope_losses == ()
    assert with_scene.scene_digest is not None
    assert with_scene.query_digest == canonical_digest(with_scene.query)

    without_scene = _scope(scene=False)
    assert without_scene.known_scope_losses == ("scene_identity_absent",)
    assert without_scene.scene_digest is None
    assert without_scene.scope_digest != with_scene.scope_digest


def test_scope_requires_ready_demand() -> None:
    raw = _demand().model_dump(mode="json")
    raw.update(
        status="unavailable",
        abilities=[],
        scene_digest=None,
        scene_text=None,
        workbook_brief_payload_digest="sha256:" + "1" * 64,
        known_losses=["promise_vows_unavailable"],
    )
    raw["demand_digest"] = _digest({k: v for k, v in raw.items() if k != "demand_digest"})
    non_ready = AskBHotTopicsDemandV1.model_validate_json(json.dumps(raw), strict=True)
    with pytest.raises(ValueError, match="ready demand"):
        build_scope(non_ready, provider_config_fingerprint="sha256:" + "e" * 64)


@pytest.mark.parametrize(
    ("mutation", "match"),
    [
        ({"query_digest": "sha256:" + "9" * 64}, "digest mismatch"),
        ({"scope_digest": "sha256:" + "9" * 64}, "scope digest mismatch"),
        ({"scene_text": None}, "together"),
        ({"known_scope_losses": ["scene_identity_absent"]}, "mirror"),
        ({"abilities": []}, "abilities"),
    ],
)
def test_scope_tamper_fails_loud(mutation: dict[str, Any], match: str) -> None:
    raw = _scope().model_dump(mode="json")
    raw.update(mutation)
    with pytest.raises(ValueError, match=match):
        AskBRetrievalScopeV1.model_validate_json(json.dumps(raw), strict=True)


def test_association_is_deterministic_over_stored_window() -> None:
    scope = _scope()
    abilities, matched = match_ability_associations(
        scope,
        title="Automation of workflow symptoms",
        body="Evidence on automation and symptoms in clinics.",
    )
    assert abilities == ("LO-1", "LO-2")
    # R6 (B8): evidence pairs are an ORDERED LIST mirroring the ability order.
    assert tuple(match.ability_id for match in matched) == ("LO-1", "LO-2")
    assert set(matched[0].tokens) <= set(("will", "distinguish", "workflow", "symptoms"))
    assert matched[0].tokens  # nonempty token evidence
    none_abilities, none_matched = match_ability_associations(
        scope, title="Quantum chromodynamics", body="Nothing relevant here."
    )
    assert none_abilities == ()
    assert none_matched == ()


def test_entry_requires_ability_association_and_namespace() -> None:
    scope = _scope()
    entry = _entry(scope)
    assert entry.supports_ability_ids
    with pytest.raises(ValueError, match="ability association"):
        _entry(scope, supports_ability_ids=(), matched_ability_tokens=())
    with pytest.raises(ValueError, match="namespaced"):
        _entry(scope, citation_id="ask-a-cite-001")
    with pytest.raises(ValueError, match="evidence mismatch"):
        _entry(scope, supports_ability_ids=("LO-1",))


def test_entry_rejects_empty_matched_tokens_and_oversized_excerpt() -> None:
    scope = _scope()
    with pytest.raises(ValueError, match="matched tokens"):
        # R6: an empty-token pair fails at the pair model itself.
        _entry(
            scope,
            supports_ability_ids=("LO-1",),
            matched_ability_tokens=(
                AskBAbilityTokenMatchV1.model_construct(ability_id="LO-1", tokens=()),
            ),
        )
    with pytest.raises(ValueError, match="excerpt invalid"):
        _entry(scope, evidence_excerpt="x" * 2001)


def test_citation_namespace_grows_naturally_past_999() -> None:
    """R1c (E5): the citation regex is [0-9]{3,} — 'ask-b-cite-1000' (the
    natural f'{n:03d}' widening at row 1000) validates; a 2-digit id or a
    foreign namespace still rejects."""
    scope = _scope()
    entry = _entry(scope, citation_id="ask-b-cite-1000")
    assert entry.citation_id == "ask-b-cite-1000"
    with pytest.raises(ValueError, match="namespaced"):
        _entry(scope, citation_id="ask-b-cite-01")


def test_association_evidence_is_ordered_pairs_not_object_key_order() -> None:
    """R6 (B8): a sort_keys rewrite of the serialized entry cannot flip
    validity — the evidence rides in an ordered list of {ability_id, tokens}
    pairs, and a reordered pair list fails loud against supports order."""
    scope = _scope()
    body = "Workflow symptoms and automation move research evidence."
    excerpt, truncated, body_hash = evidence_for_body(body)
    abilities, matched = match_ability_associations(
        scope, title="Workflow automation", body=excerpt
    )
    assert len(matched) >= 2  # both LO-1 and LO-2 associate on this window
    entry = _entry(scope)
    rewritten = json.dumps(entry.model_dump(mode="json"), sort_keys=True)
    survived = AskBKnowledgeEntryV1.model_validate_json(rewritten, strict=True)
    assert survived == entry
    with pytest.raises(ValueError, match="evidence mismatch"):
        _entry(
            scope,
            supports_ability_ids=abilities,
            matched_ability_tokens=tuple(reversed(matched)),
        )


def test_forged_association_outside_scope_is_rejected_in_output() -> None:
    """R4a (E8): an entry whose supports_ability_ids names an ability OUTSIDE
    the dispatch scope (a forged association carrying the right scope digest)
    is rejected by the output validator."""
    scope = _scope()
    receipt = _receipt(scope)
    forged = _entry(
        scope,
        supports_ability_ids=("LO-9",),
        matched_ability_tokens=(
            AskBAbilityTokenMatchV1(ability_id="LO-9", tokens=("workflow",)),
        ),
    )
    intake = AskBResearchIntakeV1.build(
        scope=scope, execution_receipt=receipt, entries=(forged,)
    )
    with pytest.raises(ValueError, match="outside the dispatch scope"):
        AskBContributionOutputV1.build_completed(
            disposition="completed_ready",
            intake=intake,
            entries=(forged,),
            known_losses=(),
        )


def test_acronym_only_ability_records_association_basis_loss() -> None:
    """R11 (E6): an ability with ZERO association-basis tokens (acronym-only
    'AI' vow) records a per-ability known_loss at scope build and the scope
    continues — visible, never silent."""
    demand = _demand(
        abilities=[
            {"ability_id": "LO-1", "text": "I will distinguish workflow symptoms."},
            {"ability_id": "LO-2", "text": "AI"},
        ]
    )
    scope = build_scope(demand, provider_config_fingerprint="sha256:" + "e" * 64)
    assert scope.known_scope_losses == ("ability_association_basis_absent:LO-2",)
    # The loss is validator-recomputed: dropping it fails loud.
    raw = scope.model_dump(mode="json")
    raw["known_scope_losses"] = []
    with pytest.raises(ValueError, match="mirror"):
        AskBRetrievalScopeV1.model_validate_json(json.dumps(raw), strict=True)


def test_query_neutralizes_scope_delimiters_from_vow_and_scene_text() -> None:
    """R5b (B7, live-repro'd injection): vow/scene prose cannot spoof a query
    segment — the delimiters `| ; [ ]` are neutralized in the derived-display
    query while the structured fields keep identity authority."""
    demand = _demand(
        abilities=[
            {"ability_id": "LO-1", "text": "Choose ] [LO-9] a | move ; now"},
            {"ability_id": "LO-2", "text": "I can choose a first automation move."},
        ]
    )
    query = derive_hot_topics_query(demand)
    assert "[LO-9]" not in query  # spoofed segment neutralized
    assert "[LO-1] Choose LO-9 a move now" in query
    # exactly one scene delimiter (the real one) and one inter-ability ';'
    assert query.count("|") == 1
    assert query.count(";") == 1
    # structured identity is untouched by display projection
    assert demand.abilities[0].text == "Choose ] [LO-9] a | move ; now"


def test_trailing_space_vow_resolves_to_working_scope() -> None:
    """R5c (B6, live-repro'd): a trailing-space vow is contract-legal upstream
    and must resolve to a WORKING scope (whitespace-collapse symmetric with
    the scene treatment), never crash the single-line query contract."""
    demand = _demand(
        abilities=[
            {"ability_id": "LO-1", "text": "I will distinguish workflow symptoms. "},
        ],
    )
    scope = build_scope(demand, provider_config_fingerprint="sha256:" + "e" * 64)
    assert "[LO-1] I will distinguish workflow symptoms." in scope.query
    assert scope.query == scope.query.strip()


def test_evidence_is_exact_unicode_slice_and_full_body_hash() -> None:
    body = "é" * 2500
    excerpt, truncated, body_hash = evidence_for_body(body)
    assert excerpt == "é" * 2000
    assert truncated is True
    assert body_hash == "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()
    with pytest.raises(ValueError, match="nonblank"):
        evidence_for_body("   ")


def test_intake_orders_and_exhausts_ability_coverage() -> None:
    scope = _scope()
    receipt = _receipt(scope)
    entry = _entry(scope)
    intake = AskBResearchIntakeV1.build(
        scope=scope, execution_receipt=receipt, entries=(entry,)
    )
    assert intake.covered_ability_ids == entry.supports_ability_ids
    assert set(intake.covered_ability_ids) | set(intake.uncovered_ability_ids) == {
        "LO-1",
        "LO-2",
    }
    empty = AskBResearchIntakeV1.build(
        scope=scope, execution_receipt=receipt, entries=()
    )
    assert empty.covered_ability_ids == ()
    assert empty.uncovered_ability_ids == ("LO-1", "LO-2")


def test_receipt_binds_scope_and_digest() -> None:
    scope = _scope()
    receipt = _receipt(scope)
    assert receipt.scope_digest == scope.scope_digest
    raw = receipt.model_dump(mode="json")
    raw["receipt_digest"] = "sha256:" + "9" * 64
    with pytest.raises(ValueError, match="digest mismatch"):
        AskBExecutionReceiptV1.model_validate_json(json.dumps(raw), strict=True)


@pytest.mark.parametrize(
    ("disposition", "loss"),
    [
        ("retryable_demand_not_ready", "ask_b_demand_not_ready"),
        ("retryable_dispatch_disabled", "ask_b_dispatch_disabled"),
        ("retryable_credentials_unavailable", "ask_b_credentials_unavailable"),
    ],
)
def test_retryable_outputs_are_zero_call_and_intake_free(
    disposition: str, loss: str
) -> None:
    output = AskBContributionOutputV1.build_retryable(disposition=disposition, loss=loss)
    assert output.dispatcher_invocations == 0
    assert output.research_intake is None
    assert output.known_losses == (loss,)
    with pytest.raises(ValueError, match="retryable disposition shape"):
        AskBContributionOutputV1.build_retryable(
            disposition=disposition, loss="wrong_loss_code"
        )


def test_completed_dispositions_track_entries_and_losses() -> None:
    scope = _scope()
    receipt = _receipt(scope)
    entry = _entry(scope)
    intake = AskBResearchIntakeV1.build(
        scope=scope, execution_receipt=receipt, entries=(entry,)
    )
    ready = AskBContributionOutputV1.build_completed(
        disposition="completed_ready", intake=intake, entries=(entry,), known_losses=()
    )
    assert ready.dispatcher_invocations == 1
    degraded = AskBContributionOutputV1.build_completed(
        disposition="completed_degraded",
        intake=intake,
        entries=(entry,),
        known_losses=("ask_b_row_ability_unassociated:1",),
    )
    assert degraded.known_losses == ("ask_b_row_ability_unassociated:1",)
    empty_intake = AskBResearchIntakeV1.build(
        scope=scope, execution_receipt=receipt, entries=()
    )
    empty = AskBContributionOutputV1.build_completed(
        disposition="completed_empty",
        intake=empty_intake,
        entries=(),
        known_losses=("ask_b_row_evidence_invalid:0",),
    )
    assert empty.research_entries == ()
    with pytest.raises(ValueError, match="disposition/content mismatch"):
        AskBContributionOutputV1.build_completed(
            disposition="completed_ready",
            intake=intake,
            entries=(entry,),
            known_losses=("ask_b_row_duplicate:1",),
        )


def test_completed_scope_losses_lead_the_loss_order() -> None:
    scope = _scope(scene=False)
    receipt = _receipt(scope)
    entry = _entry(scope)
    intake = AskBResearchIntakeV1.build(
        scope=scope, execution_receipt=receipt, entries=(entry,)
    )
    degraded = AskBContributionOutputV1.build_completed(
        disposition="completed_degraded",
        intake=intake,
        entries=(entry,),
        known_losses=("scene_identity_absent", "ask_b_row_duplicate:2"),
    )
    assert degraded.known_losses[0] == "scene_identity_absent"
    with pytest.raises(ValueError, match="scope losses must lead"):
        AskBContributionOutputV1.build_completed(
            disposition="completed_degraded",
            intake=intake,
            entries=(entry,),
            known_losses=("ask_b_row_duplicate:2",),
        )


def test_output_digest_tamper_fails_loud() -> None:
    scope = _scope()
    receipt = _receipt(scope)
    entry = _entry(scope)
    intake = AskBResearchIntakeV1.build(
        scope=scope, execution_receipt=receipt, entries=(entry,)
    )
    output = AskBContributionOutputV1.build_completed(
        disposition="completed_ready", intake=intake, entries=(entry,), known_losses=()
    )
    raw = output.model_dump(mode="json")
    raw["output_digest"] = "sha256:" + "9" * 64
    with pytest.raises(ValueError, match="output digest mismatch"):
        AskBContributionOutputV1.model_validate_json(json.dumps(raw), strict=True)


def test_entry_scope_digest_mismatch_fails_in_output() -> None:
    scope = _scope()
    other = _scope(scene=False)
    receipt = _receipt(scope)
    foreign = _entry(other)
    intake = AskBResearchIntakeV1.build(
        scope=scope, execution_receipt=receipt, entries=(foreign,)
    )
    with pytest.raises(ValueError, match="entry scope mismatch"):
        AskBContributionOutputV1.build_completed(
            disposition="completed_ready",
            intake=intake,
            entries=(foreign,),
            known_losses=(),
        )


def test_ask_b_module_has_no_orchestrator_import() -> None:
    import ast
    from pathlib import Path

    import app.marcus.lesson_plan.ask_b_hot_topics as module

    tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
    imported = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    imported.update(
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    )
    assert not any(
        name == "app.marcus.orchestrator" or name.startswith("app.marcus.orchestrator.")
        for name in imported
    )
