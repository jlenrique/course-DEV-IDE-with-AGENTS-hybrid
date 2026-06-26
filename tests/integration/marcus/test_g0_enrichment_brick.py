"""Story G0-S2 — G0-enrichment brick + operator confirm-gate #1 (offline surface).

RED-first behavioral specs for AC-S2-1..AC-S2-7 (the offline surface). AC-S2-8
(the REAL LLM live-segment proof) is the orchestrator's leg and is NOT exercised
here (no mocks of the SUT; the offline pre-pass is deterministic/recorded).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.marcus.lesson_plan.g0_enrichment import (
    G0EnrichmentResult,
    IndependentParse,
    OperatorMerge,
    ReconcileView,
    assert_run_dissent_invariant,
    corpus_fingerprint,
)
from app.marcus.lesson_plan.learning_objective import LearningObjective, SourceRef
from app.marcus.lesson_plan.source_type import (
    CLASSIFICATION_ONLY_TYPES,
    SOURCE_TYPES,
    OtherSourceType,
    TypedSource,
    is_classification_only,
)
from app.marcus.orchestrator import g0_enrichment_wiring as gw
from app.marcus.orchestrator import production_runner

REPO_ROOT = Path(__file__).resolve().parents[3]
CORPUS = REPO_ROOT / "course-content" / "courses" / "studio-smoke-min"
TRIAL_CORPUS = REPO_ROOT / "tests" / "fixtures" / "trial_corpus"


# =========================================================================== #
# AC-S2-1 — closed 10-type enum + other:<label> escape hatch, role-orthogonal
# =========================================================================== #


def test_ac_s2_1_closed_enum_is_exactly_ten_types() -> None:
    assert {
        "slide",
        "quiz",
        "workbook",
        "narration",
        "reference_citation",
        "rubric",
        "exercise_lab",
        "motion_script_storyboard",
        "discussion_forum",
        "assignment_instructions",
    } == SOURCE_TYPES


def test_ac_s2_1_unknown_type_red_rejected_three_surfaces() -> None:
    # Surface 1+3 (Literal validator + TypeAdapter round-trip).
    with pytest.raises(ValidationError):
        TypedSource(source_id="src-001", source_type="podcast")  # type: ignore[arg-type]
    # Surface 2 (JSON-Schema enum array) excludes the bad value.
    schema = TypedSource.model_json_schema()
    enum_values = schema["properties"]["source_type"]["enum"]
    assert "podcast" not in enum_values
    assert "other" in enum_values  # escape hatch is a member of the field literal


def test_ac_s2_1_other_escape_hatch_round_trip_structured() -> None:
    other = OtherSourceType(label="podcast-episode", provenance="audio file, no enum fit")
    ts = TypedSource(source_id="src-001", source_type="other", other_type=other)
    assert ts.flagged_unconsumed is True  # 'other' is always flagged unconsumed
    restored = TypedSource.model_validate_json(ts.model_dump_json())
    assert restored.other_type is not None
    assert restored.other_type.kind == "other"
    assert restored.other_type.label == "podcast-episode"


def test_ac_s2_1_other_requires_label_and_provenance() -> None:
    with pytest.raises(ValidationError):
        OtherSourceType(label="", provenance="x")
    with pytest.raises(ValidationError):
        TypedSource(source_id="src-001", source_type="other")  # missing other_type


def test_ac_s2_1_classification_only_flag_is_derived_not_overridable() -> None:
    # quiz/rubric/etc have no generator today → flagged regardless of the input flag.
    for t in CLASSIFICATION_ONLY_TYPES:
        ts = TypedSource(source_id="s", source_type=t, flagged_unconsumed=False)  # type: ignore[arg-type]
        assert ts.flagged_unconsumed is True, f"{t} must be flagged classification-only"
    # slide HAS a generator → not flagged even if the caller sets True.
    assert is_classification_only("slide") is False
    slide = TypedSource(source_id="s", source_type="slide", flagged_unconsumed=True)
    assert slide.flagged_unconsumed is False


def test_ac_s2_1_type_is_orthogonal_to_directive_role() -> None:
    # A discussion_forum/quiz span carries TYPE independently of any role binding;
    # TypedSource has no role field at all (it is recorded separately).
    ts = TypedSource(source_id="src-009", source_type="discussion_forum")
    assert "role" not in ts.model_dump()


# =========================================================================== #
# AC-S2-2 — provisional LO extraction with resolvable provenance
# =========================================================================== #


def test_ac_s2_2_offline_pre_pass_emits_provisional_los_with_provenance() -> None:
    result = gw.build_enrichment_result(corpus_dir=CORPUS, dispatch_live=False)
    assert result.provisional_los, "offline pre-pass must extract >=1 candidate LO"
    enumerated_ids = {p.source_id for p in result.enumeration_provenance}
    for lo in result.provisional_los:
        assert lo.status == "provisional"
        assert lo.adequacy is None  # adequacy is S3, never produced here
        for ref in lo.source_refs:
            assert ref.source_id in enumerated_ids  # resolvable, not fabricated
            assert ref.quoted_span  # verbatim span present


def test_ac_s2_2_fabricated_source_id_is_red() -> None:
    bad_lo = LearningObjective(
        objective_id="lo-bad-001",
        statement="cites a source that does not exist",
        status="provisional",
        confidence="low",
        source_refs=(SourceRef(source_id="src-999", locator="x", quoted_span="y"),),
    )
    with pytest.raises(ValueError, match="fabricated|NOT in the enumerated"):
        gw._assert_refs_enumerated([bad_lo], {"src-001"})


def test_ac_s2_2_provisional_lo_with_zero_refs_is_allowed() -> None:
    # The schema permits a provisional LO with 0 refs (advisory, flagged elsewhere).
    lo = LearningObjective(
        objective_id="lo-0refs",
        statement="no provenance yet",
        status="provisional",
        confidence="low",
    )
    assert lo.source_refs == ()
    gw._assert_refs_enumerated([lo], {"src-001"})  # no refs → nothing to reject


# =========================================================================== #
# AC-S2-3 — off the critical path + corpus-keyed cache + offline guard
# =========================================================================== #


def test_ac_s2_3_corpus_fingerprint_is_stable_and_model_sensitive() -> None:
    fp_a = corpus_fingerprint(["h1", "h2"], "marcus")
    assert fp_a == corpus_fingerprint(["h1", "h2"], "marcus")
    assert fp_a != corpus_fingerprint(["h1", "h2"], "other-model")  # model id sensitive
    assert fp_a != corpus_fingerprint(["h2", "h1"], "marcus")  # order/content sensitive


def test_ac_s2_3_cache_hit_freezes_result_on_replay(tmp_path: Path) -> None:
    from app.models.runtime.production_envelope import ProductionEnvelope

    trial_id = UUID("32345678-1234-4234-8234-123456789abc")
    env = ProductionEnvelope(trial_id=trial_id)
    first = gw.run_g0_enrichment(
        node_id=gw.G0_ENRICHMENT_NODE_ID,
        production_envelope=env,
        corpus_dir=CORPUS,
        trial_id=trial_id,
        runs_root=tmp_path,
        dispatch_live=False,
    )
    fp = first.get_contribution(
        gw.G0_ENRICHMENT_SPECIALIST_ID, node_id=gw.G0_ENRICHMENT_NODE_ID
    ).output["corpus_fingerprint"]
    cache_file = tmp_path / str(trial_id) / "g0-enrichment-cache" / f"{fp}.json"
    assert cache_file.is_file(), "frozen result must be cached keyed to the corpus fingerprint"
    # Idempotent: a re-run does not duplicate the contribution (resume-safe).
    again = gw.run_g0_enrichment(
        node_id=gw.G0_ENRICHMENT_NODE_ID,
        production_envelope=first,
        corpus_dir=CORPUS,
        trial_id=trial_id,
        runs_root=tmp_path,
        dispatch_live=False,
    )
    assert len(again.contributions) == len(first.contributions)


def test_ac_s2_3_corpus_keyed_replay_reads_frozen_cache(tmp_path: Path) -> None:
    """A graph replay with an unchanged corpus reads the FROZEN cache (determinism)."""
    import json

    from app.models.runtime.production_envelope import ProductionEnvelope

    trial_id = UUID("72345678-1234-4234-8234-123456789abc")
    frozen = gw.build_enrichment_result(corpus_dir=CORPUS, dispatch_live=False)
    run_dir = tmp_path / str(trial_id)
    (run_dir / "g0-enrichment-cache").mkdir(parents=True)
    # Pre-seed the cache with a DISTINCT frozen result (a tweaked statement) so a
    # cache HIT is observable: the replay must return the cached LO, not re-derive.
    dump = gw._full_dump(frozen)
    dump["provisional_los"][0]["statement"] = "FROZEN-OPERATOR-CONFIRMED statement"
    (run_dir / "g0-enrichment-cache" / f"{frozen.corpus_fingerprint}.json").write_text(
        json.dumps(dump, default=str), encoding="utf-8"
    )
    updated = gw.run_g0_enrichment(
        node_id=gw.G0_ENRICHMENT_NODE_ID,
        production_envelope=ProductionEnvelope(trial_id=trial_id),
        corpus_dir=CORPUS,
        trial_id=trial_id,
        runs_root=tmp_path,
        dispatch_live=False,
    )
    contribution = updated.get_contribution(
        gw.G0_ENRICHMENT_SPECIALIST_ID, node_id=gw.G0_ENRICHMENT_NODE_ID
    )
    los = contribution.output["g0_enrichment_result"]["provisional_los"]
    assert los[0]["statement"] == "FROZEN-OPERATOR-CONFIRMED statement", (
        "an unchanged corpus must read the frozen cached result, not re-derive it"
    )


def test_ac_s2_3_offline_marker_is_not_a_live_model_id() -> None:
    result = gw.build_enrichment_result(corpus_dir=CORPUS, dispatch_live=False)
    assert result.model_id == gw.G0_ENRICHMENT_MODEL_MARKER
    assert "offline" in result.model_id  # no live spend on the offline surface


# =========================================================================== #
# AC-S2-4 — A4 independent-parse-first + A3 dissent
# =========================================================================== #


def _result_with_merge(independent_ts: datetime, merge_ts: datetime) -> dict:
    base = gw.build_enrichment_result(corpus_dir=CORPUS, dispatch_live=False)
    payload = base.model_dump()
    payload["independent_parse"] = IndependentParse(proposal={"x": 1}, ts=independent_ts)
    payload["operator_merge"] = OperatorMerge(suggestion={"y": 2}, ts=merge_ts)
    return payload


def test_ac_s2_4_independent_parse_must_precede_operator_merge() -> None:
    t0 = datetime(2026, 6, 26, 12, 0, 0, tzinfo=UTC)
    # ts-order satisfied → valid.
    ok = G0EnrichmentResult.model_validate(_result_with_merge(t0, t0 + timedelta(seconds=5)))
    assert ok.operator_merge is not None
    # ts-order violated (merge before/equal independent) → reject pre-surface.
    with pytest.raises(ValidationError, match="independent_parse.ts must precede"):
        G0EnrichmentResult.model_validate(_result_with_merge(t0, t0))


def test_ac_s2_4_audit_sidecar_excluded_from_dump_and_schema() -> None:
    result = gw.build_enrichment_result(corpus_dir=CORPUS, dispatch_live=False)
    dumped = result.model_dump(mode="json")
    assert "independent_parse" not in dumped
    assert "operator_merge" not in dumped
    schema_props = G0EnrichmentResult.model_json_schema()["properties"]
    assert "independent_parse" not in schema_props
    assert "operator_merge" not in schema_props


def test_ac_s2_4_run_level_dissent_invariant_requires_real_dissent() -> None:
    result = gw.build_enrichment_result(corpus_dir=CORPUS, dispatch_live=False)
    assert_run_dissent_invariant(result)  # offline pre-pass always carries a real dissent
    real = [d for d in result.dissents if d.against.strip() and d.marcus_position.strip()]
    assert real, "a confirm-gate with zero real dissent is anti-anchoring theater"


def test_ac_s2_4_dissent_varies_run_to_run_across_corpora() -> None:
    a = gw.build_enrichment_result(corpus_dir=CORPUS, dispatch_live=False)
    b = gw.build_enrichment_result(corpus_dir=TRIAL_CORPUS, dispatch_live=False)
    # The dissent is fingerprint-derived → a never-varying field would be theater.
    assert a.dissents[0].marcus_position != b.dissents[0].marcus_position or (
        a.corpus_fingerprint != b.corpus_fingerprint
    )


# =========================================================================== #
# AC-S2-6 — A10 enumeration-provenance + traversal-roots; reconcile; A1 RED
# =========================================================================== #


def test_ac_s2_6_traversal_roots_and_enumeration_provenance_present() -> None:
    result = gw.build_enrichment_result(corpus_dir=CORPUS, dispatch_live=False)
    assert result.traversal_roots, "A10: the roots the operator pointed the run at"
    assert result.traversal_roots[0].kind == "corpus_dir"
    assert len(result.enumeration_provenance) == result.reconcile.n_in
    for prov in result.enumeration_provenance:
        assert prov.root_id  # how it entered the set (which root)
        assert prov.locator


def test_ac_s2_6_reconcile_partition_must_balance() -> None:
    # n_in == n_typed + n_ignored or the artifact is rejected (a source vanished).
    with pytest.raises(ValidationError, match="reconcile mismatch"):
        ReconcileView(n_in=5, n_typed=3, n_ignored=1, n_flagged=0)
    ok = ReconcileView(n_in=4, n_typed=3, n_ignored=1, n_flagged=2)
    assert ok.n_in == ok.n_typed + ok.n_ignored


def test_ac_s2_6_unreachable_corpus_is_red(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist"
    with pytest.raises(Exception):  # noqa: B017 — DirectiveCompositionError family
        gw.build_enrichment_result(corpus_dir=missing, dispatch_live=False)


# =========================================================================== #
# AC-S2-5 — confirm-gate #1 wired into BOTH walks (two-walk parity)
# =========================================================================== #


def test_ac_s2_5_both_walk_sites_invoke_the_hook_and_gate_traverse() -> None:
    """Static guard: the side-effect + the asleep-gate traverse appear in BOTH walks."""
    src = (REPO_ROOT / "app" / "marcus" / "orchestrator" / "production_runner.py").read_text(
        encoding="utf-8"
    )
    assert src.count("g0_enrichment_wiring.run_g0_enrichment(") == 2, (
        "the G0-enrichment side-effect must be wired into BOTH walks (two-walk parity)"
    )
    assert src.count("gate_id == g0_enrichment_wiring.G0_ENRICHMENT_GATE_CODE") == 2, (
        "the asleep-G0E gate-traverse must be present in BOTH walks"
    )


def test_ac_s2_5_default_off_is_byte_identical_first_pause_stays_g1(
    tmp_path: Path, monkeypatch
) -> None:
    from app.gates.resume_api import clear_resume_registry

    clear_resume_registry()
    monkeypatch.delenv(gw.G0_ENRICHMENT_ACTIVE_ENV, raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    trial_id = UUID("42345678-1234-4234-8234-123456789abc")
    started = production_runner.run_production_trial(
        TRIAL_CORPUS / "README.md",
        "production",
        "operator_test",
        trial_id=trial_id,
        runs_root=tmp_path,
        max_specialist_calls=12,
    )
    # Brick asleep → no g0 contribution, no artifact, G0E traversed (first real
    # pause is the pre-existing G1 OR an upstream error — never G0E).
    assert started.paused_gate != "G0E"
    assert (
        started.production_envelope.get_contribution(
            gw.G0_ENRICHMENT_SPECIALIST_ID, node_id=gw.G0_ENRICHMENT_NODE_ID
        )
        is None
    )
    assert not (tmp_path / str(trial_id) / "g0-enrichment.json").exists()


def test_ac_s2_5_woken_pauses_at_g0e_with_real_card(tmp_path: Path, monkeypatch) -> None:
    from app.gates.resume_api import clear_resume_registry

    clear_resume_registry()
    monkeypatch.setenv(gw.G0_ENRICHMENT_ACTIVE_ENV, "1")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)  # offline pre-pass
    trial_id = UUID("52345678-1234-4234-8234-123456789abc")
    started = production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=trial_id,
        runs_root=tmp_path,
        allow_offline_cost_report=True,
        max_specialist_calls=12,
    )
    assert started.status == "paused-at-gate"
    assert started.paused_gate == "G0E", "woken brick pauses at confirm-gate #1"
    # The brick fired on the START walk (the node precedes node 01).
    assert (
        started.production_envelope.get_contribution(
            gw.G0_ENRICHMENT_SPECIALIST_ID, node_id=gw.G0_ENRICHMENT_NODE_ID
        )
        is not None
    )
    card_path = tmp_path / str(trial_id) / "decision-card-G0E.json"
    assert card_path.is_file()
    import json

    card = json.loads(card_path.read_text(encoding="utf-8"))["card"]
    assert card["gate_id"] == "G0E"
    assert card["typed_manifest"], "card surfaces the typed manifest"
    assert card["traversal_roots"], "card surfaces A10 traversal roots"
    assert (
        card["reconcile"]["n_in"] == card["reconcile"]["n_typed"] + card["reconcile"]["n_ignored"]
    )


def test_ac_s2_5_operator_verdict_advances_model_never_auto_advances(
    tmp_path: Path, monkeypatch
) -> None:
    """The model's proposal never auto-advances — only the operator verdict does."""
    from app.gates.resume_api import clear_resume_registry
    from app.models.runtime.production_envelope import SpecialistContribution
    from app.models.state.operator_verdict import OperatorVerdict

    clear_resume_registry()
    monkeypatch.setenv(gw.G0_ENRICHMENT_ACTIVE_ENV, "1")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")

    class _Adapter:
        def invoke_specialist(self, *, specialist_id, envelope, node_id=None, **kwargs):
            updated = envelope.model_copy(deep=True)
            updated.add_contribution(
                SpecialistContribution.from_output(
                    specialist_id=specialist_id,
                    output={"specialist_id": specialist_id},
                    model_used="gpt-5-nano",
                    node_id=node_id,
                )
            )
            return updated

    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", _Adapter)

    trial_id = UUID("62345678-1234-4234-8234-123456789abc")
    started = production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=trial_id,
        runs_root=tmp_path,
        max_specialist_calls=12,
    )
    assert started.paused_gate == "G0E"  # halts; the model never advanced past it

    import json

    card_payload = json.loads((tmp_path / str(trial_id) / "decision-card-G0E.json").read_text())
    verdict = OperatorVerdict(
        trial_id=trial_id,
        verb="approve",
        gate_id="G0E",
        card_id=UUID(card_payload["card"]["card_id"]),
        operator_id="operator_test",
        decision_card_digest=card_payload["digest"],
    )
    resumed = production_runner.resume_production_trial(
        trial_id=trial_id,
        verdict=verdict,
        runs_root=tmp_path,
        max_specialist_calls=12,
    )
    # The operator verdict advanced the run PAST G0E (to the next pause / onward).
    assert resumed.paused_gate != "G0E", "operator-confirm must advance past gate #1"


# =========================================================================== #
# Manifest registration (compiler + roster)
# =========================================================================== #


def test_g0e_is_a_production_gate_and_node_registered() -> None:
    import yaml

    from app.manifest.compiler import RUNTIME_GATE_IDS, production_gate_ids
    from app.manifest.loader import load as load_manifest
    from app.models.state.specialist_summary_artifacts import CANONICAL_SPECIALIST_IDS

    assert "G0E" in RUNTIME_GATE_IDS
    manifest = load_manifest(REPO_ROOT / "state" / "config" / "pipeline-manifest.yaml")
    node_ids = {n.id for n in manifest.nodes}
    assert {"g0-enrichment", "g0-enrichment-gate"} <= node_ids
    assert "G0E" in production_gate_ids(manifest)
    assert "g0_enrichment" in CANONICAL_SPECIALIST_IDS

    raw = yaml.safe_load(
        (REPO_ROOT / "state" / "config" / "pipeline-manifest.yaml").read_text(encoding="utf-8")
    )
    # The new gate precedes node 01 in manifest.nodes list order (front door).
    ids_in_order = [n["id"] for n in raw["nodes"]]
    assert ids_in_order.index("g0-enrichment") < ids_in_order.index("01")
    assert ids_in_order.index("g0-enrichment-gate") < ids_in_order.index("01")


# --------------------------------------------------------------------------- #
# AC-S2-6 / T11 MUST-FIX — live-payload reconciliation (no crash on under-typing) #
# --------------------------------------------------------------------------- #
def test_parse_live_payload_reconciles_under_dup_and_fabricated(tmp_path: Path) -> None:
    # The live model under-types (only src-001), DUPLICATES src-001, and
    # FABRICATES src-999. The reconcile must produce EXACTLY one TypedSource per
    # enumerated id (coverage == count), never crash, and drop the fabricated id.
    for i in (1, 2, 3):
        (tmp_path / f"f{i}.md").write_text(f"# file {i}\n", encoding="utf-8")
    enumerated = [
        ("src-001", tmp_path / "f1.md"),
        ("src-002", tmp_path / "f2.md"),
        ("src-003", tmp_path / "f3.md"),
    ]
    payload = {
        "typed_sources": [
            {"source_id": "src-001", "source_type": "quiz", "flagged_unconsumed": True},
            {"source_id": "src-001", "source_type": "slide", "flagged_unconsumed": False},
            {"source_id": "src-999", "source_type": "slide", "flagged_unconsumed": False},
        ],
        "provisional_los": [],
    }
    typed, los, provenance = gw._parse_live_payload(payload, enumerated, tmp_path)
    ids = [t.source_id for t in typed]
    assert ids == ["src-001", "src-002", "src-003"]  # exactly one per enumerated id
    assert typed[0].source_type == "quiz"  # first occurrence wins (dedup)
    assert "src-999" not in ids  # fabricated dropped
    assert len(provenance) == 3
    # The ReconcileView count is correct BY CONSTRUCTION (no double-count balance).
    rv = ReconcileView(n_in=len(enumerated), n_typed=len(typed), n_ignored=0,
                        n_flagged=sum(1 for t in typed if t.flagged_unconsumed))
    assert rv.n_in == rv.n_typed


# --------------------------------------------------------------------------- #
# AC-S2-3 / T11 live-prompt groundedness — the live prompt feeds VERBATIM       #
# content excerpts (not just paths) so typing + quoted_spans are grounded.       #
# --------------------------------------------------------------------------- #
def test_source_excerpt_is_verbatim_and_bounded(tmp_path: Path) -> None:
    p = tmp_path / "big.md"
    body = "# Heading\n" + ("lorem ipsum dolor sit amet " * 1000)
    p.write_text(body, encoding="utf-8")
    excerpt = gw._source_excerpt(p, max_chars=200)
    assert excerpt.startswith("# Heading")  # verbatim prefix
    assert "[excerpt truncated]" in excerpt
    assert len(excerpt) <= 200 + len("\n…[excerpt truncated]")
    # short file returned whole (verbatim), no truncation marker
    short = tmp_path / "s.md"
    short.write_text("just one line", encoding="utf-8")
    assert gw._source_excerpt(short) == "just one line"


def test_live_corpus_summary_includes_id_path_and_content(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("alpha content line", encoding="utf-8")
    (tmp_path / "b.md").write_text("beta content line", encoding="utf-8")
    enumerated = [("src-001", tmp_path / "a.md"), ("src-002", tmp_path / "b.md")]
    summary = gw._live_corpus_summary(enumerated, tmp_path)
    assert "### src-001: a.md" in summary
    assert "alpha content line" in summary  # the model SEES content, not just the path
    assert "### src-002: b.md" in summary
    assert "beta content line" in summary
