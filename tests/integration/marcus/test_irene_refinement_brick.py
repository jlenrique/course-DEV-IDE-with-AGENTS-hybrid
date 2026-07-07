"""Story G0-S3 — Irene refinement loop + ratify-gate #2 + completeness assert.

RED-first behavioral specs for AC-S3-1..AC-S3-6 (the offline surface). AC-S3-7
(the REAL LLM live-segment proof) is the orchestrator's leg and is NOT exercised
here (no mocks of the SUT; the offline refinement is deterministic/recorded).
"""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.marcus.lesson_plan.irene_refinement import (
    CompletenessError,
    LODeltaEntry,
    LODeltaLedger,
    assert_completeness,
    build_refinement_result,
    ratify_refined_los,
    refine_one,
)
from app.marcus.lesson_plan.learning_objective import (
    IllegalTransition,
    LearningObjective,
    SourceAdequacy,
    SourceRef,
    advance_lo,
)
from app.marcus.orchestrator import g0_enrichment_wiring as gw
from app.marcus.orchestrator import irene_refinement_wiring as iw
from app.marcus.orchestrator import production_runner

REPO_ROOT = Path(__file__).resolve().parents[3]
CORPUS = REPO_ROOT / "course-content" / "courses" / "studio-smoke-min"


def _provisional(oid: str, *, span: str = "a verbatim span of more than eighty characters " * 2,
                 src: str = "src-001") -> LearningObjective:
    lo = LearningObjective(
        objective_id=oid,
        statement=f"Understand the material introduced by {src}.",
        status="provisional",
        confidence="low",
        source_refs=(SourceRef(source_id=src, locator="p1", quoted_span=span),),
    )
    return advance_lo(lo, "provisional", actor="g0")


# =========================================================================== #
# AC-S3-1 — Irene refines provisional->refined IN PLACE (same id; irene≠ratified)
# =========================================================================== #


def test_ac_s3_1_refines_in_place_same_id_with_bloom() -> None:
    prov = _provisional("lo-g0-001")
    refined, entry = refine_one(prov)
    assert refined.objective_id == prov.objective_id  # immutable id carried through
    assert refined.status == "refined"
    assert refined.bloom_level is not None  # populated at refine
    assert refined.adequacy is not None  # adequacy present at refined+
    assert entry.disposition == "refined-in-place"
    assert entry.transition == "provisional->refined"


def test_ac_s3_1_irene_can_never_reach_ratified() -> None:
    refined, _ = refine_one(_provisional("lo-g0-002"))
    # irene actor has no edge to ratified (S1 guard); only operator does.
    with pytest.raises(IllegalTransition):
        advance_lo(refined, "ratified", actor="irene")
    assert advance_lo(refined, "ratified", actor="operator").status == "ratified"


def test_ac_s3_1_refinement_result_rejects_non_provisional_input() -> None:
    refined, _ = refine_one(_provisional("lo-g0-003"))
    with pytest.raises(ValueError, match="must be provisional"):
        build_refinement_result(provisional_los=[refined], corpus_fingerprint="fp")


# =========================================================================== #
# AC-S3-2 — per-LO SourceAdequacy is ADVISORY, never a blocker (§3.1)
# =========================================================================== #


def test_ac_s3_2_every_refined_lo_carries_populated_adequacy() -> None:
    result = build_refinement_result(
        provisional_los=[_provisional("lo-g0-010"), _provisional("lo-g0-011")],
        corpus_fingerprint="fp",
    )
    for lo in result.refined_los:
        assert lo.adequacy is not None  # presence (verdict value is advisory)
        assert lo.adequacy.verdict in ("adequate", "thin", "gap")


def test_ac_s3_2_gap_lo_still_advances_and_passes_completeness() -> None:
    # A short span yields a 'gap' verdict — but the LO STILL refines + the
    # completeness assert PASSES on a gap (§3.1, advisory).
    prov = _provisional("lo-g0-012", span="tiny")
    refined, entry = refine_one(prov)
    assert refined.adequacy.verdict == "gap"
    assert refined.status == "refined"  # not blocked by the gap verdict
    assert_completeness(
        refined_los=[refined],
        ledger=LODeltaLedger(g0_objective_ids=("lo-g0-012",), entries=(entry,)),
        enumerated_source_ids={"src-001"},
    )  # gap PASSES (presence asserted, not verdict)


def test_ac_s3_2_thin_gap_adequacy_requires_concrete_missing() -> None:
    # Object well-formedness (distinct from any pipeline gate): thin/gap needs a
    # concrete named gap.
    with pytest.raises(ValidationError):
        SourceAdequacy(verdict="gap", rationale="below floor", missing=[])


# =========================================================================== #
# AC-S3-3 — signed LO-delta contract (all channels + no silent drops + reconcile)
# =========================================================================== #


def test_ac_s3_3_no_silent_drops_unaccounted_id_is_a_block() -> None:
    refined, entry = refine_one(_provisional("lo-g0-020"))
    # Ledger declares TWO g0 ids but only accounts for one → BLOCK.
    with pytest.raises(ValidationError, match="NO silent drops|no disposition"):
        LODeltaLedger(g0_objective_ids=("lo-g0-020", "lo-g0-021"), entries=(entry,))


def test_ac_s3_3_exactly_one_disposition_per_id() -> None:
    refined, entry = refine_one(_provisional("lo-g0-022"))
    with pytest.raises(ValidationError, match="more than one disposition"):
        LODeltaLedger(g0_objective_ids=("lo-g0-022",), entries=(entry, entry))


def test_ac_s3_3_propose_new_channel() -> None:
    new_lo = LearningObjective(
        objective_id="lo-irene-001",
        statement="source teaches an assessable objective the provisional set missed",
        status="provisional",
        confidence="medium",
        origin="irene-proposed",
        source_refs=(SourceRef(source_id="src-002", locator="p2", quoted_span="span"),),
    )
    entry = LODeltaEntry(
        objective_id="lo-irene-001", disposition="proposed-new", lo=new_lo
    )
    # A proposed-new id is NOT a g0 baseline id but is a valid entry id.
    ledger = LODeltaLedger(g0_objective_ids=(), entries=(entry,))
    assert ledger.reconcile_summary()["proposed_new"] == 1
    # Irene cannot self-promote her invention to refined.
    with pytest.raises(ValidationError, match="status='provisional'|self-promote"):
        LODeltaEntry(
            objective_id="lo-irene-001",
            disposition="proposed-new",
            lo=advance_lo(
                new_lo.model_copy(
                    update={
                        "bloom_level": "understand",
                        "adequacy": SourceAdequacy(verdict="adequate", rationale="ok"),
                    }
                ),
                "refined",
                actor="irene",
            ),
        )


def test_ac_s3_3_recommend_drop_channel_held_provisional_gap_drop() -> None:
    held = LearningObjective(
        objective_id="lo-g0-030",
        statement="source cannot support this objective",
        status="provisional",
        confidence="low",
        recommendation="drop",
        adequacy=SourceAdequacy(
            verdict="gap", rationale="no teachable substrate", missing=["the whole topic"]
        ),
        source_refs=(SourceRef(source_id="src-003", locator="p3", quoted_span="span"),),
    )
    entry = LODeltaEntry(objective_id="lo-g0-030", disposition="recommend-drop", lo=held)
    assert entry.is_dropped()
    ledger = LODeltaLedger(g0_objective_ids=("lo-g0-030",), entries=(entry,))
    assert ledger.reconcile_summary()["recommend_drop"] == 1
    # A recommend-drop without verdict=gap is rejected.
    with pytest.raises(ValidationError, match="verdict='gap'"):
        LODeltaEntry(
            objective_id="lo-g0-031",
            disposition="recommend-drop",
            lo=held.model_copy(
                update={
                    "objective_id": "lo-g0-031",
                    "adequacy": SourceAdequacy(verdict="adequate", rationale="ok"),
                }
            ),
        )


def test_ac_s3_3_changed_lo_requires_provenance_bearing_rationale_diff() -> None:
    refined, _ = refine_one(_provisional("lo-g0-040"))
    with pytest.raises(ValidationError, match="rationale_diff"):
        LODeltaEntry(
            objective_id="lo-g0-040",
            disposition="refined-in-place",
            lo=refined,
            rationale_diff="",  # provenance-less diff rejected pre-surface
        )


def test_ac_s3_3_split_and_merge_structural_pairing() -> None:
    refined, _ = refine_one(_provisional("lo-g0-050"))
    # split requires split_into; merged requires merged_from.
    with pytest.raises(ValidationError, match="split_into"):
        LODeltaEntry(
            objective_id="lo-g0-050", disposition="split", lo=refined,
            rationale_diff="split into two", split_into=(),
        )
    with pytest.raises(ValidationError, match="merged_from"):
        LODeltaEntry(
            objective_id="lo-g0-050", disposition="merged", lo=refined,
            rationale_diff="merged in", merged_from=(),
        )


def test_ac_s3_3_count_reconciliation_g0_to_irene() -> None:
    result = build_refinement_result(
        provisional_los=[_provisional("lo-g0-060"), _provisional("lo-g0-061")],
        corpus_fingerprint="fp",
    )
    summary = result.ledger.reconcile_summary()
    assert summary["g0_count"] == 2
    assert summary["irene_count"] == 2  # refined-in-place, no expand/contract
    assert result.ledger.g0_count == result.ledger.irene_count


# =========================================================================== #
# AC-S3-4 — ratify-gate #2 wired into BOTH walks; A8 re-confirm; never auto-ratify
# =========================================================================== #


def test_ac_s3_4_both_walk_sites_invoke_hook_and_gate_traverse() -> None:
    """Static guard: the side-effect + the asleep-gate traverse appear in BOTH walks."""
    src = (REPO_ROOT / "app" / "marcus" / "orchestrator" / "production_runner.py").read_text(
        encoding="utf-8"
    )
    assert src.count("irene_refinement_wiring.run_irene_refinement(") == 2, (
        "the Irene-refinement side-effect must be wired into BOTH walks (two-walk parity)"
    )
    # The asleep-G0R gate-traverse guard (the `not ...active()` form) appears in
    # BOTH walks (the resume handler uses `verdict.gate_id ==`, a distinct form).
    assert src.count("not irene_refinement_wiring.irene_refinement_active()") == 2, (
        "the asleep-G0R gate-traverse must be present in BOTH walks"
    )


def test_ac_s3_4_operator_ratifies_model_never_auto_ratifies() -> None:
    refined = [refine_one(_provisional("lo-g0-070"))[0]]
    ratified = ratify_refined_los(refined)
    assert all(lo.status == "ratified" for lo in ratified)


def test_ac_s3_4_a8_prior_ratified_requires_explicit_reconfirm() -> None:
    refined, _ = refine_one(_provisional("lo-g0-080"))
    prior = {"lo-g0-080": advance_lo(refined, "ratified", actor="operator")}
    # Touching a prior-ratified LO without an explicit re-confirm is rejected
    # (A8 — NOT a silent re-stamp via advance_lo idempotency).
    with pytest.raises(ValueError, match="A8|re-confirm"):
        ratify_refined_los([refined], prior_ratified=prior)
    # With explicit re-confirm it is allowed.
    out = ratify_refined_los([refined], prior_ratified=prior, reconfirmed_ids={"lo-g0-080"})
    assert out[0].status == "ratified"


def test_ac_s3_4_g0r_is_a_production_gate_and_nodes_registered() -> None:
    import yaml

    from app.manifest.compiler import RUNTIME_GATE_IDS, production_gate_ids
    from app.manifest.loader import load as load_manifest
    from app.models.state.specialist_summary_artifacts import CANONICAL_SPECIALIST_IDS

    assert "G0R" in RUNTIME_GATE_IDS
    manifest = load_manifest(REPO_ROOT / "state" / "config" / "pipeline-manifest.yaml")
    node_ids = {n.id for n in manifest.nodes}
    assert {"irene-refinement", "g0-ratify-gate"} <= node_ids
    assert "G0R" in production_gate_ids(manifest)
    assert "irene_refinement" in CANONICAL_SPECIALIST_IDS

    raw = yaml.safe_load(
        (REPO_ROOT / "state" / "config" / "pipeline-manifest.yaml").read_text(encoding="utf-8")
    )
    ids_in_order = [n["id"] for n in raw["nodes"]]
    # G0R follows G0E and both precede node 01 (the front-door order).
    assert ids_in_order.index("g0-enrichment-gate") < ids_in_order.index("irene-refinement")
    assert ids_in_order.index("irene-refinement") < ids_in_order.index("g0-ratify-gate")
    assert ids_in_order.index("g0-ratify-gate") < ids_in_order.index("01")


# =========================================================================== #
# AC-S3-5 — completeness hard-assert (ACCESS + ASSESSMENT-PRESENCE, not verdict)
# =========================================================================== #


def _ledger_for(refined: LearningObjective) -> LODeltaLedger:
    return LODeltaLedger(
        g0_objective_ids=(refined.objective_id,),
        entries=(
            LODeltaEntry(
                objective_id=refined.objective_id,
                disposition="refined-in-place",
                lo=refined,
                rationale_diff="refined against source",
            ),
        ),
    )


def test_ac_s3_5_passes_on_access_and_assessment_presence() -> None:
    refined, _ = refine_one(_provisional("lo-g0-090"))
    assert_completeness(
        refined_los=[refined],
        ledger=_ledger_for(refined),
        enumerated_source_ids={"src-001"},
    )  # no raise


def test_ac_s3_5_unreachable_source_is_red() -> None:
    refined, _ = refine_one(_provisional("lo-g0-091", src="src-001"))
    with pytest.raises(CompletenessError, match="unreachable|not in the enumerated"):
        assert_completeness(
            refined_los=[refined],
            ledger=_ledger_for(refined),
            enumerated_source_ids={"src-999"},  # the LO's src-001 is not reachable
        )


def test_ac_s3_5_missing_adequacy_is_red() -> None:
    # A proposed-new provisional LO with adequacy=None, marked non-dropped → RED.
    new_lo = LearningObjective(
        objective_id="lo-irene-090",
        statement="proposed without an adequacy assessment",
        status="provisional",
        confidence="low",
        origin="irene-proposed",
        source_refs=(SourceRef(source_id="src-001", locator="p", quoted_span="s"),),
    )
    entry = LODeltaEntry(objective_id="lo-irene-090", disposition="proposed-new", lo=new_lo)
    ledger = LODeltaLedger(g0_objective_ids=(), entries=(entry,))
    with pytest.raises(CompletenessError, match="adequacy"):
        assert_completeness(
            refined_los=[new_lo], ledger=ledger, enumerated_source_ids={"src-001"}
        )


def test_ac_s3_5_dropped_lo_is_excluded_from_the_assert() -> None:
    held = LearningObjective(
        objective_id="lo-g0-092",
        statement="recommend drop",
        status="provisional",
        confidence="low",
        recommendation="drop",
        adequacy=SourceAdequacy(verdict="gap", rationale="no support", missing=["all"]),
        source_refs=(SourceRef(source_id="src-001", locator="p", quoted_span="s"),),
    )
    entry = LODeltaEntry(objective_id="lo-g0-092", disposition="recommend-drop", lo=held)
    ledger = LODeltaLedger(g0_objective_ids=("lo-g0-092",), entries=(entry,))
    # The held/dropped LO is excluded (not asserted as a surviving deliverable).
    assert_completeness(refined_los=[held], ledger=ledger, enumerated_source_ids={"src-001"})


# =========================================================================== #
# AC-S3-1/S3-6 — wiring: Irene reads gate-#1 provisional LOs; cache; idempotent
# =========================================================================== #


def test_ac_s3_6_wiring_reads_gate1_provisional_los_and_refines(tmp_path: Path) -> None:
    from app.models.runtime.production_envelope import ProductionEnvelope

    trial_id = UUID("13345678-1234-4234-8234-123456789abc")
    run_dir = tmp_path / str(trial_id)
    # Stage the frozen S2 enrichment result (gate #1 output) on disk.
    env = ProductionEnvelope(trial_id=trial_id)
    gw.run_g0_enrichment(
        node_id=gw.G0_ENRICHMENT_NODE_ID,
        production_envelope=env,
        corpus_dir=CORPUS,
        trial_id=trial_id,
        runs_root=tmp_path,
        dispatch_live=False,
    )
    assert (run_dir / "g0-enrichment.json").is_file()

    # Irene refinement consumes those provisional LOs.
    updated = iw.run_irene_refinement(
        node_id=iw.IRENE_REFINEMENT_NODE_ID,
        production_envelope=ProductionEnvelope(trial_id=trial_id),
        trial_id=trial_id,
        runs_root=tmp_path,
        dispatch_live=False,
    )
    contribution = updated.get_contribution(
        iw.IRENE_REFINEMENT_SPECIALIST_ID, node_id=iw.IRENE_REFINEMENT_NODE_ID
    )
    assert contribution is not None
    payload = contribution.output[iw.REFINEMENT_RESULT_KEY]
    assert payload["refined_los"], "refinement must consume + refine the gate-#1 LOs"
    for lo in payload["refined_los"]:
        assert lo["status"] == "refined"
        assert lo["adequacy"] is not None
    assert (run_dir / "irene-refinement.json").is_file()

    full = iw.load_refinement_full(run_dir)
    assert full is not None
    assert full.ledger.g0_count == full.ledger.irene_count

    # Idempotent: a re-run does not duplicate the contribution (resume-safe).
    again = iw.run_irene_refinement(
        node_id=iw.IRENE_REFINEMENT_NODE_ID,
        production_envelope=updated,
        trial_id=trial_id,
        runs_root=tmp_path,
        dispatch_live=False,
    )
    assert len(again.contributions) == len(updated.contributions)


def test_ac_s3_6_refinement_requires_gate1_result_on_disk(tmp_path: Path) -> None:
    from app.models.runtime.production_envelope import ProductionEnvelope

    trial_id = UUID("23345678-1234-4234-8234-123456789abc")
    with pytest.raises(ValueError, match="no g0-enrichment result"):
        iw.run_irene_refinement(
            node_id=iw.IRENE_REFINEMENT_NODE_ID,
            production_envelope=ProductionEnvelope(trial_id=trial_id),
            trial_id=trial_id,
            runs_root=tmp_path,
            dispatch_live=False,
        )


def test_ac_s3_6_kill_switch_off_parity_with_s2(monkeypatch) -> None:
    """S5-3a.2 re-contract (legacy/kill-switch leg).

    Re-homed behind an EXPLICIT ``setenv("0")`` (was a ``delenv`` premise the 3b
    default flip would invert). Explicit OFF ⇒ refinement OFF; explicit ON ⇒
    refinement ON — both explicit, so the code-default flip cannot invert them. The
    DEFAULT-ON parity premise moves to the skip-until-3b witness below.
    """
    monkeypatch.setenv(gw.G0_ENRICHMENT_ACTIVE_ENV, "0")
    assert iw.irene_refinement_active() is False
    monkeypatch.setenv(gw.G0_ENRICHMENT_ACTIVE_ENV, "1")
    assert iw.irene_refinement_active() is True  # rides the same toggle as the enrichment brick


def test_ac_s3_6_default_on_parity_with_s2(monkeypatch) -> None:
    """S5-3a.2 re-contract (new default-ON witness; un-skipped at the S5-3b flip).

    The MEANINGFUL "feature-flag parity" assertion is that the UNSET default returns
    ``irene_refinement_active() is True`` (refinement rides the same default-ON toggle
    as the enrichment brick post-3b). A ``setenv("1")`` witness would not prove the
    *default* — so this stayed skip-until-3b; the 3b flip (this story) CASHES the
    un-skip obligation.
    """
    monkeypatch.delenv(gw.G0_ENRICHMENT_ACTIVE_ENV, raising=False)
    assert iw.irene_refinement_active() is True


# =========================================================================== #
# Full two-gate integration (offline): woken brick refines + ratifies at G0R
# =========================================================================== #


def test_full_two_gate_offline_refines_and_ratifies(tmp_path: Path, monkeypatch) -> None:
    from app.gates.resume_api import clear_resume_registry
    from app.models.runtime.production_envelope import SpecialistContribution
    from app.models.state.operator_verdict import OperatorVerdict

    clear_resume_registry()
    monkeypatch.setenv(gw.G0_ENRICHMENT_ACTIVE_ENV, "1")
    # Fake key + a stub adapter that lands billable spans on specialist nodes (the
    # S2 pattern) so the post-G0R continuation pauses at the next real gate (G1)
    # without crashing the offline economics emission. The g0/irene bricks still
    # run OFFLINE (dispatch_live is False by default).
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
    # Economics/cost emission is NOT the SUT here: the offline g0/irene bricks emit
    # no billable LLM spans (the LIVE leg does, AC-S3-7), so the continuation
    # pause-at-G0R trips the "no billable spans" economics guard. Neutralize that
    # non-SUT trace-cost emission so the two-gate pause/ratify flow is exercised.
    monkeypatch.setattr(production_runner, "_record_cost", lambda **kwargs: None)
    trial_id = UUID("33345678-1234-4234-8234-123456789abc")

    import json

    # Walk to gate #1 (G0E) and approve.
    started = production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=trial_id,
        runs_root=tmp_path,
        max_specialist_calls=12,
    )
    assert started.paused_gate == "G0E"
    g0e_card = json.loads((tmp_path / str(trial_id) / "decision-card-G0E.json").read_text())
    after_g0e = production_runner.resume_production_trial(
        trial_id=trial_id,
        verdict=OperatorVerdict(
            trial_id=trial_id,
            verb="approve",
            gate_id="G0E",
            card_id=UUID(g0e_card["card"]["card_id"]),
            operator_id="operator_test",
            decision_card_digest=g0e_card["digest"],
        ),
        runs_root=tmp_path,
        max_specialist_calls=12,
    )
    # The refinement node fired and the run now pauses at ratify-gate #2 (G0R).
    assert after_g0e.paused_gate == "G0R", "must pause at the Irene ratify-gate after G0E"
    assert (tmp_path / str(trial_id) / "irene-refinement.json").is_file()
    g0r_card = json.loads((tmp_path / str(trial_id) / "decision-card-G0R.json").read_text())
    assert g0r_card["card"]["gate_id"] == "G0R"
    assert g0r_card["card"]["refined_los"], "G0R card surfaces the refined plan"
    assert g0r_card["card"]["reconcile"]["g0_count"] == g0r_card["card"]["reconcile"]["irene_count"]

    # Operator ratifies at G0R → refined->ratified + completeness assert + advance.
    after_g0r = production_runner.resume_production_trial(
        trial_id=trial_id,
        verdict=OperatorVerdict(
            trial_id=trial_id,
            verb="approve",
            gate_id="G0R",
            card_id=UUID(g0r_card["card"]["card_id"]),
            operator_id="operator_test",
            decision_card_digest=g0r_card["digest"],
        ),
        runs_root=tmp_path,
        max_specialist_calls=12,
    )
    assert after_g0r.paused_gate != "G0R", "operator ratify must advance past gate #2"
    ratified = json.loads((tmp_path / str(trial_id) / "ratified-los.json").read_text())
    assert ratified["ratified_los"], "ratified LOs captured as evidence"
    assert all(lo["status"] == "ratified" for lo in ratified["ratified_los"])
