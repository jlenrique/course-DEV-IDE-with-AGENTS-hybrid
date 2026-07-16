"""Hermetic tests for W1 research-packet shape-pin."""

from __future__ import annotations

import ast
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import pytest

from app.marcus.lesson_plan import research_packet as rp
from app.marcus.lesson_plan.ask_a_enrichment import (
    AskAContributionOutputV1,
    AskAExecutionReceiptV1,
    AskAKnowledgeEntryV1,
    AskAResearchIntakeV1,
    AskARetrievalScopeV1,
    canonical_digest,
    evidence_for_body,
)
from app.marcus.lesson_plan.ask_b_hot_topics import (
    AskBAbilityTokenMatchV1,
    AskBContributionOutputV1,
    AskBExecutionReceiptV1,
    AskBKnowledgeEntryV1,
    AskBResearchIntakeV1,
    AskBRetrievalScopeV1,
)
from app.marcus.lesson_plan.deep_dive_projection import DeepDiveAbilityInput
from app.marcus.lesson_plan.workbook_enrichment import RunEnvelopeCorruptError
from app.models.runtime.production_envelope import (
    ProductionEnvelope,
    SpecialistContribution,
    compute_output_digest,
)
from app.models.runtime.production_trial_envelope import ProductionTrialEnvelope


def _valid_entry(**overrides: object) -> dict:
    base = {
        "citation_id": "cite-001",
        "source_ref": "retrieval:scite:10.1000/x",
        "provider": "scite",
        "source_id": "10.1000/x",
        "title": "Example",
        "source_hash": "sha256:abc",
        "evidence_hierarchy_tier": "T4_peer_other",
        "peer_reviewed": True,
        "provider_provenance": ["scite"],
        "triangulation_status": "single_provider",
        "reliability_score": 0.5,
    }
    base.update(overrides)
    return base


def _valid_ask_a_output() -> dict:
    query = "ability[lo-1]=Explain model drift | bold_term=Model Drift"
    scope_raw = {
        "schema_version": "ask-a-retrieval-scope.v1",
        "demand_digest": "sha256:" + "a" * 64,
        "workbook_brief_payload_digest": "sha256:" + "b" * 64,
        "skeleton_authority_digest": "sha256:" + "c" * 64,
        "skeleton_candidate_digest": "sha256:" + "d" * 64,
        "abilities": (DeepDiveAbilityInput(ability_id="lo-1", text="Explain model drift"),),
        "bold_terms": ("Model Drift",),
        "source_claim_refs": ("claim-1",),
        "query": query,
        "query_digest": canonical_digest(query),
        "posture": "gap_fill",
        "provider_config_fingerprint": "sha256:" + "e" * 64,
        "association_algorithm": "ask-a-association.v1",
    }
    scope_raw["scope_digest"] = canonical_digest(scope_raw)
    scope = AskARetrievalScopeV1.model_validate(scope_raw, strict=True)
    body = "Model Drift evidence explains model drift."
    excerpt, truncated, body_hash = evidence_for_body(body)
    entry = AskAKnowledgeEntryV1(
        citation_id="ask-a-cite-001",
        source_ref="retrieval:scite:10.1000/x",
        provider="scite",
        source_id="10.1000/x",
        title="Model Drift",
        source_hash="sha256:" + "f" * 64,
        evidence_hierarchy_tier="T4_peer_other",
        peer_reviewed=True,
        provider_provenance=("scite",),
        triangulation_status="single_provider",
        evidence_excerpt=excerpt,
        evidence_truncated=truncated,
        evidence_body_sha256=body_hash,
        scope_digest=scope.scope_digest,
        supports_ability_ids=("lo-1",),
        supports_bold_terms=("Model Drift",),
        association_algorithm="ask-a-association.v1",
        matched_ability_tokens={"lo-1": ("model", "drift")},
        matched_bold_terms=("Model Drift",),
    )
    receipt = AskAExecutionReceiptV1.build(
        scope=scope,
        dispatcher_invocations=1,
        provider_iterations=(1,),
        refinement_logs=(),
        provider_outcomes=("accepted",),
        provider_receipts=({"provider": "scite"},),
    )
    intake = AskAResearchIntakeV1.build(
        scope=scope, execution_receipt=receipt, entries=(entry,)
    )
    return AskAContributionOutputV1.build_completed(
        disposition="completed_ready", intake=intake, entries=(entry,), known_losses=()
    ).model_dump(mode="json")


def _valid_ask_b_output() -> dict:
    scope_raw = {
        "schema_version": "ask-b-retrieval-scope.v1",
        "demand_digest": "sha256:" + "1" * 64,
        "workbook_brief_payload_digest": "sha256:" + "2" * 64,
        "abilities": (
            DeepDiveAbilityInput(ability_id="lo-1", text="Explain model drift"),
        ),
        "scene_digest": "sha256:" + "3" * 64,
        "scene_text": "A clinic hits model drift.",
        "query": "hot topics: [lo-1] Explain model drift",
        "query_digest": None,
        "posture": "hot_topics",
        "provider_config_fingerprint": "sha256:" + "4" * 64,
        "association_algorithm": "ask-b-association.v1",
        "known_scope_losses": (),
    }
    scope_raw["query_digest"] = canonical_digest(scope_raw["query"])
    scope_raw["scope_digest"] = canonical_digest(
        {k: v for k, v in scope_raw.items() if k != "scope_digest"}
    )
    scope = AskBRetrievalScopeV1.model_validate(scope_raw, strict=True)
    body = "Model drift evidence explains drift risks."
    excerpt, truncated, body_hash = evidence_for_body(body)
    entry = AskBKnowledgeEntryV1(
        citation_id="ask-b-cite-001",
        source_ref="retrieval:scite:10.1000/y",
        provider="scite",
        source_id="10.1000/y",
        title="Model drift trends",
        source_hash="sha256:" + "5" * 64,
        evidence_hierarchy_tier="T4_peer_other",
        peer_reviewed=True,
        provider_provenance=("scite",),
        triangulation_status="single_provider",
        evidence_excerpt=excerpt,
        evidence_truncated=truncated,
        evidence_body_sha256=body_hash,
        scope_digest=scope.scope_digest,
        supports_ability_ids=("lo-1",),
        association_algorithm="ask-b-association.v1",
        # 38-2 T4 R6 (B8): ordered list-of-pairs association evidence.
        matched_ability_tokens=(
            AskBAbilityTokenMatchV1(ability_id="lo-1", tokens=("model", "drift")),
        ),
    )
    receipt = AskBExecutionReceiptV1.build(
        scope=scope,
        dispatcher_invocations=1,
        provider_iterations=(1,),
        refinement_logs=(),
        provider_outcomes=("accepted",),
        provider_receipts=({"provider": "scite"},),
    )
    intake = AskBResearchIntakeV1.build(
        scope=scope, execution_receipt=receipt, entries=(entry,)
    )
    return AskBContributionOutputV1.build_completed(
        disposition="completed_ready", intake=intake, entries=(entry,), known_losses=()
    ).model_dump(mode="json")


def _write_run(
    run_dir: Path,
    *,
    entries: list[dict] | None = None,
    intake: dict | None = None,
    producer_losses: object = None,
    include_contribution: bool = True,
) -> None:
    trial_id = UUID("12345678-1234-4234-8234-123456789abc")
    contributions: list[SpecialistContribution] = []
    if include_contribution:
        output: dict = {
            "research_entries": entries if entries is not None else [],
        }
        if intake is not None:
            output["research_intake"] = intake
        if producer_losses is not None:
            output["known_losses"] = producer_losses
        contributions.append(
            SpecialistContribution.from_output(
                specialist_id="research_wiring",
                output=output,
                model_used="fixture",
                node_id="04.55",
                provenance="fixture",
            )
        )
    envelope = ProductionEnvelope(
        trial_id=trial_id,
        contributions=tuple(contributions),
        fixture_run=True,
    )
    started = datetime(2026, 7, 10, 12, 0, tzinfo=UTC)
    trial = ProductionTrialEnvelope(
        trial_id=trial_id,
        preset="explore",
        corpus_path="fixture",
        operator_id="w1-hermetic",
        started_at=started,
        completed_at=started,
        status="completed",
        production_clone_launch_evidence=True,
        production_envelope=envelope,
    )
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run.json").write_text(
        trial.model_dump_json(),
        encoding="utf-8",
    )


def _write_contributions(
    run_dir: Path,
    contributions: list[tuple[str, str, dict]],
) -> None:
    trial_id = UUID("12345678-1234-4234-8234-123456789abc")
    envelope = ProductionEnvelope(
        trial_id=trial_id,
        contributions=tuple(
            SpecialistContribution.from_output(
                specialist_id=specialist_id,
                output=output,
                model_used="fixture",
                node_id=node_id,
                provenance="fixture",
            )
            for specialist_id, node_id, output in contributions
        ),
        fixture_run=True,
    )
    started = datetime(2026, 7, 10, 12, 0, tzinfo=UTC)
    trial = ProductionTrialEnvelope(
        trial_id=trial_id,
        preset="explore",
        corpus_path="fixture",
        operator_id="w1-hermetic",
        started_at=started,
        completed_at=started,
        status="completed",
        production_clone_launch_evidence=True,
        production_envelope=envelope,
    )
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run.json").write_text(trial.model_dump_json(), encoding="utf-8")


def test_absent_run_is_honest_empty(tmp_path: Path) -> None:
    packet = rp.load_research_packet(tmp_path)
    assert packet.status == "absent"
    assert packet.entries == ()
    assert "run_json_absent" in packet.known_losses


def test_empty_entries_honest(tmp_path: Path) -> None:
    _write_run(tmp_path, entries=[])
    packet = rp.load_research_packet(tmp_path)
    assert packet.status == "empty"
    assert packet.entries == ()


def test_ready_packet_shape_pin(tmp_path: Path) -> None:
    _write_run(tmp_path, entries=[_valid_entry()])
    packet = rp.load_research_packet(tmp_path)
    assert packet.status == "ready"
    assert len(packet.entries) == 1
    assert set(rp.REQUIRED_ENTRY_FIELDS).issubset(packet.entries[0].keys())


def test_malformed_entry_known_loss(tmp_path: Path) -> None:
    bad = _valid_entry()
    del bad["evidence_hierarchy_tier"]
    _write_run(tmp_path, entries=[bad, _valid_entry(citation_id="cite-002")])
    packet = rp.load_research_packet(tmp_path)
    assert packet.status == "degraded"
    assert len(packet.entries) == 1
    assert any(loss.startswith("entry_shape_invalid") for loss in packet.known_losses)


def test_producer_losses_precede_reader_losses_and_dedupe_first_wins(tmp_path: Path) -> None:
    _write_run(
        tmp_path,
        entries=[{"bad": "row"}],
        producer_losses=["provider_tier_excluded:0", "entry_shape_invalid:0"],
    )
    packet = rp.load_research_packet(tmp_path)
    assert packet.known_losses == (
        "provider_tier_excluded:0",
        "entry_shape_invalid:0",
        "research_entries_all_invalid",
    )
    assert packet.status == "empty"


@pytest.mark.parametrize(
    "losses",
    [None, "one", {}, [1], [""], ["  "], ["line\nbreak"]],
)
def test_malformed_producer_losses_fail_loud(tmp_path: Path, losses: object) -> None:
    # ``None`` is represented explicitly by building the contribution directly.
    output = {"research_entries": [_valid_entry()], "known_losses": losses}
    _write_contributions(tmp_path, [("research_wiring", "04.55", output)])
    with pytest.raises(rp.ResearchPacketShapeError, match="known_losses"):
        rp.load_research_packet(tmp_path)


def test_corrupt_run_fail_loud(tmp_path: Path) -> None:
    (tmp_path / "run.json").write_text("{nope", encoding="utf-8")
    with pytest.raises(RunEnvelopeCorruptError):
        rp.load_research_packet(tmp_path)


def test_dual_consumers_share_digest(tmp_path: Path) -> None:
    _write_run(tmp_path, entries=[_valid_entry()])
    glossary = rp.resolve_for_glossary_writer(tmp_path)
    trends = rp.resolve_for_trends_projector(tmp_path)
    assert glossary.packet_digest == trends.packet_digest
    assert glossary.entries == trends.entries


def test_require_usable_fails_closed_on_empty(tmp_path: Path) -> None:
    _write_run(tmp_path, entries=[])
    with pytest.raises(rp.ResearchPacketShapeError, match="requires usable"):
        rp.resolve_for_glossary_writer(tmp_path, require_usable=True)


def test_research_entries_key_wrong_type_fail_loud(tmp_path: Path) -> None:
    trial_id = UUID("12345678-1234-4234-8234-123456789abc")
    output = {"research_entries": {"not": "a-list"}}
    contrib = SpecialistContribution(
        specialist_id="research_wiring",
        contributed_at=datetime(2026, 7, 10, 12, 0, tzinfo=UTC),
        output=output,
        cost_usd=0.0,
        model_used="fixture",
        output_digest=compute_output_digest(output),
        node_id="04.55",
        provenance="fixture",
    )
    envelope = ProductionEnvelope(
        trial_id=trial_id,
        contributions=(contrib,),
        fixture_run=True,
    )
    started = datetime(2026, 7, 10, 12, 0, tzinfo=UTC)
    trial = ProductionTrialEnvelope(
        trial_id=trial_id,
        preset="explore",
        corpus_path="fixture",
        operator_id="w1",
        started_at=started,
        completed_at=started,
        status="completed",
        production_clone_launch_evidence=True,
        production_envelope=envelope,
    )
    (tmp_path / "run.json").write_text(trial.model_dump_json(), encoding="utf-8")
    with pytest.raises(rp.ResearchPacketShapeError, match="must be a list"):
        rp.load_research_packet(tmp_path)


def test_public_packet_coordinates_are_frozen_and_exported() -> None:
    expected = {
        "GENERIC_RESEARCH_SPECIALIST_ID": "research_wiring",
        "GENERIC_RESEARCH_NODE_ID": "04.55",
        "ASK_A_ENRICHMENT_SPECIALIST_ID": "ask_a_enrichment",
        "ASK_A_ENRICHMENT_NODE_ID": "07W.2",
        "ASK_B_HOT_TOPICS_SPECIALIST_ID": "ask_b_hot_topics",
        "ASK_B_HOT_TOPICS_NODE_ID": "07W.4",
    }
    for name, value in expected.items():
        assert getattr(rp, name) == value
        assert name in rp.__all__
    assert "resolve_for_enrichment_pool" in rp.__all__
    assert "resolve_for_hot_topics" in rp.__all__
    assert "RunEnvelopeCorruptError" in rp.__all__


def test_three_packets_select_exact_coordinates_and_witness_digests(tmp_path: Path) -> None:
    # CONSCIOUS FLIP (38-2 AC 3): the bare-fixture Ask-B row this test carried
    # under 38-1 AC 4's interim "current semantics" is replaced by a strict
    # contract output — the exact 07W.4 coordinate is now strict.
    generic = _valid_entry(citation_id="generic", source_hash="sha256:generic")
    ask_a_output = _valid_ask_a_output()
    ask_b_output = _valid_ask_b_output()
    _write_contributions(
        tmp_path,
        [
            ("research_wiring", "04.55", {"research_entries": [generic]}),
            ("ask_a_enrichment", "07W.2", ask_a_output),
            ("ask_b_hot_topics", "07W.4", ask_b_output),
            ("ask_a_enrichment", "collision", {"research_entries": [generic]}),
            ("collision", "07W.2", {"research_entries": [_valid_entry()]}),
        ],
    )

    default = rp.load_research_packet(tmp_path)
    explicit = rp.load_research_packet(
        tmp_path,
        specialist_id="research_wiring",
        node_id="04.55",
    )
    enrichment = rp.resolve_for_enrichment_pool(tmp_path)
    hot_topics = rp.resolve_for_hot_topics(tmp_path)

    assert default == explicit
    assert (default.specialist_id, default.node_id) == ("research_wiring", "04.55")
    assert (enrichment.specialist_id, enrichment.node_id) == (
        "ask_a_enrichment",
        "07W.2",
    )
    assert (hot_topics.specialist_id, hot_topics.node_id) == (
        "ask_b_hot_topics",
        "07W.4",
    )
    assert default.entries[0]["citation_id"] == "generic"
    assert enrichment.entries[0]["citation_id"] == "ask-a-cite-001"
    assert hot_topics.entries[0]["citation_id"] == "ask-b-cite-001"
    assert enrichment == rp.resolve_for_enrichment_pool(tmp_path)
    assert len(
        {default.packet_digest, enrichment.packet_digest, hot_topics.packet_digest}
    ) == 3
    # One-witness-rule shape-pin (38-2 AC 3): every consumer of the Ask-B
    # packet witnesses the SAME digest.
    assert hot_topics.packet_digest == rp.resolve_for_hot_topics(tmp_path).packet_digest
    assert hot_topics.packet_digest == rp.load_research_packet(
        tmp_path, specialist_id="ask_b_hot_topics", node_id="07W.4"
    ).packet_digest


def test_ask_a_present_malformed_contract_fails_loud(tmp_path: Path) -> None:
    _write_contributions(
        tmp_path,
        [("ask_a_enrichment", "07W.2", {"research_entries": [_valid_entry()]})],
    )
    with pytest.raises(rp.ResearchPacketShapeError, match="Ask-A"):
        rp.resolve_for_enrichment_pool(tmp_path)


def test_ask_a_strict_completed_packet_resolves_stably(tmp_path: Path) -> None:
    _write_contributions(tmp_path, [("ask_a_enrichment", "07W.2", _valid_ask_a_output())])
    first = rp.resolve_for_enrichment_pool(tmp_path, require_usable=True)
    second = rp.resolve_for_enrichment_pool(tmp_path, require_usable=True)
    assert first == second
    assert first.packet_digest == second.packet_digest


def test_ask_b_present_malformed_contract_fails_loud(tmp_path: Path) -> None:
    """38-2 AC 3 mirrored strict pin (ruling-d item 2): the Ask-A strict-pin
    analog at the exact ``ask_b_hot_topics@07W.4`` coordinate."""
    _write_contributions(
        tmp_path,
        [("ask_b_hot_topics", "07W.4", {"research_entries": [_valid_entry()]})],
    )
    with pytest.raises(rp.ResearchPacketShapeError, match="Ask-B"):
        rp.resolve_for_hot_topics(tmp_path)


def test_ask_b_entry_missing_credibility_fields_is_rejected(tmp_path: Path) -> None:
    """38-2 AC 9 negative-witness pin (M-8 machine reason): an Ask-B entry
    missing credibility fields must REJECT — only satisfiable under the
    strict reader, which is why the AC 3 mandate is forced."""
    output = _valid_ask_b_output()
    del output["research_entries"][0]["provider_provenance"]
    _write_contributions(tmp_path, [("ask_b_hot_topics", "07W.4", output)])
    with pytest.raises(rp.ResearchPacketShapeError, match="Ask-B"):
        rp.resolve_for_hot_topics(tmp_path)


def test_ask_b_stub_shaped_output_claiming_completion_is_rejected(tmp_path: Path) -> None:
    """38-2 AC 9 negative-witness pin: a stub-shaped output dressed up as a
    completed contribution must REJECT at the strict reader."""
    _write_contributions(
        tmp_path,
        [
            (
                "ask_b_hot_topics",
                "07W.4",
                {
                    "schema_version": "ask-b-contribution-output.v1",
                    "disposition": "completed_ready",
                    "research_entries": [],
                    "known_losses": [],
                    "research_intake": None,
                    "dispatcher_invocations": 1,
                    "output_digest": "sha256:" + "9" * 64,
                },
            )
        ],
    )
    with pytest.raises(rp.ResearchPacketShapeError, match="Ask-B"):
        rp.resolve_for_hot_topics(tmp_path)


def test_duplicate_ask_b_contributions_at_coordinate_fail_loud(tmp_path: Path) -> None:
    """38-2 T4 R4b (B9): the strict Ask-B reader rejects DUPLICATE
    contributions at the exact coordinate — forged-authority paranoia
    mirroring the demand resolver — instead of silently reading the first."""
    output = _valid_ask_b_output()
    _write_contributions(
        tmp_path,
        [
            ("ask_b_hot_topics", "07W.4", output),
            ("ask_b_hot_topics", "07W.4", output),
        ],
    )
    with pytest.raises(rp.ResearchPacketShapeError, match="duplicate Ask-B"):
        rp.resolve_for_hot_topics(tmp_path)


def test_symlinked_run_json_is_corruption_not_honest_absence(tmp_path: Path) -> None:
    """38-2 T4 R9 (B5): the shared ``load_run_envelope`` loader rejects a
    symlinked ``run.json`` (additive containment guard, mirroring every other
    Ask-B disk guard) — never a silent read-through, never honest-absence."""
    from app.marcus.lesson_plan.workbook_enrichment import load_run_envelope

    real_dir = tmp_path / "real"
    _write_contributions(real_dir, [("ask_b_hot_topics", "07W.4", _valid_ask_b_output())])
    linked_dir = tmp_path / "linked"
    linked_dir.mkdir()
    try:
        (linked_dir / "run.json").symlink_to(real_dir / "run.json")
    except OSError as exc:  # WinError 1314: no symlink privilege on this host
        pytest.skip(f"host cannot create symlinks: {exc}")
    with pytest.raises(RunEnvelopeCorruptError, match="symlink"):
        load_run_envelope(linked_dir)
    with pytest.raises(RunEnvelopeCorruptError, match="symlink"):
        rp.resolve_for_hot_topics(linked_dir)


def test_ask_b_strict_completed_packet_resolves_stably(tmp_path: Path) -> None:
    """38-2 AC 3: the same ``packet_digest`` is witnessed on every reload."""
    _write_contributions(tmp_path, [("ask_b_hot_topics", "07W.4", _valid_ask_b_output())])
    first = rp.resolve_for_hot_topics(tmp_path, require_usable=True)
    second = rp.resolve_for_hot_topics(tmp_path, require_usable=True)
    assert first == second
    assert first.packet_digest == second.packet_digest
    assert first.entries[0]["citation_id"] == "ask-b-cite-001"


def test_generic_04_55_leniency_unchanged_by_ask_b_strictness(tmp_path: Path) -> None:
    """38-2 AC 3 (ruling-d item 3): the strictness flip is coordinate-exact —
    the generic ``research_wiring@04.55`` packet keeps its lenient read
    semantics (bare rows accepted; malformed rows drop into losses)."""
    bad = {"bad": "row"}
    _write_contributions(
        tmp_path,
        [("research_wiring", "04.55", {"research_entries": [bad, _valid_entry()]})],
    )
    packet = rp.load_research_packet(tmp_path)
    assert packet.status == "degraded"
    assert len(packet.entries) == 1
    assert packet.known_losses == ("entry_shape_invalid:0",)


@pytest.mark.parametrize(
    ("specialist_id", "node_id", "expected_loss"),
    [
        ("research_wiring", "04.55", "research_wiring_contribution_absent"),
        (
            "ask_a_enrichment",
            "07W.2",
            "packet_contribution_absent:ask_a_enrichment@07W.2",
        ),
        (
            "ask_b_hot_topics",
            "07W.4",
            "packet_contribution_absent:ask_b_hot_topics@07W.4",
        ),
    ],
)
def test_missing_packet_is_coordinate_specific_honest_empty(
    tmp_path: Path, specialist_id: str, node_id: str, expected_loss: str
) -> None:
    _write_contributions(tmp_path, [])
    packet = rp.load_research_packet(
        tmp_path, specialist_id=specialist_id, node_id=node_id
    )
    assert packet.status == "empty"
    assert packet.known_losses == (expected_loss,)
    assert (packet.specialist_id, packet.node_id) == (specialist_id, node_id)


@pytest.mark.parametrize(
    "resolver",
    [rp.resolve_for_enrichment_pool, rp.resolve_for_hot_topics],
)
def test_named_resolvers_require_usable_and_validate_rows(
    tmp_path: Path, resolver: object
) -> None:
    target = (
        ("ask_a_enrichment", "07W.2")
        if resolver is rp.resolve_for_enrichment_pool
        else ("ask_b_hot_topics", "07W.4")
    )
    _write_contributions(
        tmp_path,
        [(target[0], target[1], {"research_entries": [{"bad": "row"}]})],
    )
    # CONSCIOUS FLIP (38-2 AC 3): under 38-1 AC 4's interim semantics the
    # Ask-B branch read this leniently into an empty packet; the exact 07W.4
    # coordinate is now strict and fails loud, mirroring Ask-A.
    expected = "Ask-A" if resolver is rp.resolve_for_enrichment_pool else "Ask-B"
    with pytest.raises(rp.ResearchPacketShapeError, match=expected):
        resolver(tmp_path)  # type: ignore[operator]


def test_non_generic_empty_paths_preserve_requested_coordinates(tmp_path: Path) -> None:
    absent = rp.load_research_packet(
        tmp_path, specialist_id="ask_a_enrichment", node_id="07W.2"
    )
    assert (absent.specialist_id, absent.node_id) == ("ask_a_enrichment", "07W.2")
    assert absent.known_losses == ("run_json_absent",)

    _write_contributions(
        tmp_path,
        [("ask_a_enrichment", "07W.2", {"not_research_entries": []})],
    )
    with pytest.raises(rp.ResearchPacketShapeError, match="Ask-A"):
        rp.resolve_for_enrichment_pool(tmp_path)


def test_named_resolvers_fail_loud_for_wrong_container_and_corrupt_run(
    tmp_path: Path,
) -> None:
    # CONSCIOUS FLIP (38-2 AC 3): the wrong-container Ask-B row now fails the
    # strict contract validation first ("Ask-B"), not the generic list check
    # — 38-1 AC 4 scoped the lenient read as interim.
    _write_contributions(
        tmp_path,
        [("ask_b_hot_topics", "07W.4", {"research_entries": {"bad": "type"}})],
    )
    with pytest.raises(rp.ResearchPacketShapeError, match="Ask-B"):
        rp.resolve_for_hot_topics(tmp_path)
    (tmp_path / "run.json").write_text("{nope", encoding="utf-8")
    with pytest.raises(RunEnvelopeCorruptError):
        rp.resolve_for_enrichment_pool(tmp_path)


def test_research_packet_has_no_orchestrator_import() -> None:
    source = Path(rp.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_roots = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    imported_roots.update(
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    )
    assert not any(
        module == "app.marcus.orchestrator"
        or module.startswith("app.marcus.orchestrator.")
        for module in imported_roots
    )


def test_default_generic_load_equals_explicit_across_all_honest_shapes(
    tmp_path: Path,
) -> None:
    cases: dict[str, list[tuple[str, str, dict]] | None] = {
        "absent-run": None,
        "missing-contribution": [],
        "missing-key": [("research_wiring", "04.55", {"other": []})],
        "empty": [("research_wiring", "04.55", {"research_entries": []})],
        "degraded": [
            (
                "research_wiring",
                "04.55",
                {"research_entries": [{"bad": "row"}, _valid_entry()]},
            )
        ],
        "all-invalid": [
            ("research_wiring", "04.55", {"research_entries": [{"bad": "row"}]})
        ],
        "ready": [
            ("research_wiring", "04.55", {"research_entries": [_valid_entry()]})
        ],
    }
    for name, contributions in cases.items():
        run_dir = tmp_path / name
        if contributions is not None:
            _write_contributions(run_dir, contributions)
        assert rp.load_research_packet(run_dir) == rp.load_research_packet(
            run_dir,
            specialist_id=rp.GENERIC_RESEARCH_SPECIALIST_ID,
            node_id=rp.GENERIC_RESEARCH_NODE_ID,
        )


def test_none_node_id_is_rejected_before_any_node_lookup(tmp_path: Path) -> None:
    _write_contributions(
        tmp_path,
        [
            ("ask_a_enrichment", "wrong-node", {"research_entries": [_valid_entry()]}),
            (
                "ask_a_enrichment",
                "07W.2",
                {"research_entries": [_valid_entry(citation_id="intended")]},
            ),
        ],
    )
    with pytest.raises(rp.ResearchPacketShapeError, match="node_id"):
        rp.load_research_packet(
            tmp_path,
            specialist_id="ask_a_enrichment",
            node_id=None,  # type: ignore[arg-type]
        )


_PACKET_IDENTITIES = [
    ("research_wiring", "04.55", "glossary_writer"),
    ("ask_a_enrichment", "07W.2", "enrichment_pool"),
    ("ask_b_hot_topics", "07W.4", "hot_topics"),
]


@pytest.mark.parametrize(
    ("specialist_id", "node_id", "consumer_id"),
    _PACKET_IDENTITIES,
)
@pytest.mark.parametrize(
    "state",
    ["ready", "empty", "degraded", "missing-key", "wrong-container", "corrupt"],
)
def test_identity_by_state_validation_parity(
    tmp_path: Path,
    specialist_id: str,
    node_id: str,
    consumer_id: rp.ConsumerId,
    state: str,
) -> None:
    if state == "corrupt":
        (tmp_path / "run.json").write_text("{nope", encoding="utf-8")
        with pytest.raises(RunEnvelopeCorruptError):
            rp.load_research_packet(
                tmp_path, specialist_id=specialist_id, node_id=node_id
            )
        return

    outputs = {
        "ready": {"research_entries": [_valid_entry()]},
        "empty": {"research_entries": []},
        "degraded": {
            "research_entries": [{"bad": "row"}, _valid_entry()]
        },
        "missing-key": {"other": []},
        "wrong-container": {"research_entries": {"bad": "type"}},
    }
    # CONSCIOUS FLIP (38-2 AC 3): the Ask-B rows of this parametrized family
    # were pinned lenient under 38-1 AC 4's interim "current semantics"; the
    # exact 07W.4 coordinate is now strict and behaves like the Ask-A rows.
    strict = {"ask_a_enrichment": "Ask-A", "ask_b_hot_topics": "Ask-B"}
    if specialist_id == "ask_a_enrichment" and state == "ready":
        outputs["ready"] = _valid_ask_a_output()
    if specialist_id == "ask_b_hot_topics" and state == "ready":
        outputs["ready"] = _valid_ask_b_output()
    _write_contributions(
        tmp_path,
        [(specialist_id, node_id, outputs[state])],
    )
    if specialist_id in strict and state != "ready":
        with pytest.raises(rp.ResearchPacketShapeError, match=strict[specialist_id]):
            rp.load_research_packet(
                tmp_path, specialist_id=specialist_id, node_id=node_id
            )
        return
    if state == "wrong-container":
        with pytest.raises(rp.ResearchPacketShapeError, match="must be a list"):
            rp.load_research_packet(
                tmp_path, specialist_id=specialist_id, node_id=node_id
            )
        return

    packet = rp.load_research_packet(
        tmp_path, specialist_id=specialist_id, node_id=node_id
    )
    expected_status = {
        "ready": "ready",
        "empty": "empty",
        "degraded": "degraded",
        "missing-key": "empty",
    }[state]
    assert packet.status == expected_status
    assert (packet.specialist_id, packet.node_id) == (specialist_id, node_id)
    if state == "empty":
        assert packet.known_losses == ("research_entries_empty",)
    elif state == "degraded":
        assert packet.known_losses == ("entry_shape_invalid:0",)
    elif state == "missing-key":
        assert packet.known_losses == ("research_entries_key_absent",)

    if not packet.usable:
        with pytest.raises(rp.ResearchPacketShapeError, match="requires usable"):
            rp.resolve_for_consumer(
                tmp_path,
                consumer_id,
                require_usable=True,
                specialist_id=specialist_id,
                node_id=node_id,
            )
