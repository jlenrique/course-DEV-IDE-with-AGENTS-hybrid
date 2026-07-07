"""Braid S3 — thin Irene→Tracy→Texas research-wiring (AC-D1..D10).

RED-first. Verifies the bridge is wired through `production_runner.py` at the
§04.55 plan-lock fanout node (option A — no manifest node added), with TWO-WALK
parity proven by EXECUTING a real continuation walk (AC-D2), and the G2
FAIL-mode citation-fidelity gate (AC-D6) distinct from the warn-only numeric
drift rate.

Live retrieval (Scite/Consensus) is operator-gated: AC-D4 dispatches a
Tracy-authored RetrievalIntent through the dispatcher and `pytest.skip(...)`s
when provider creds are unset / the service is unreachable; no mocks.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from uuid import UUID

import pytest
import yaml

from app.marcus.orchestrator import production_runner, research_wiring
from app.marcus.orchestrator.research_citation import (
    CitationFidelityError,
    assemble_l2_citation_report,
    audit_research_supplements,
    build_retrieval_source_refs,
    compute_source_hash,
    derive_source_ref,
    gate_citation_fidelity,
    mint_cited_entry,
)
from app.marcus.orchestrator.research_wiring import (
    DeterministicPostureSelector,
    run_research_wiring,
)
from app.models.runtime.production_envelope import (
    ProductionEnvelope,
    SpecialistContribution,
)
from scripts.utilities.slide_production_gate import (
    fresh_gamma_required,
    reuse_stamp,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
TEXAS_SCRIPTS = REPO_ROOT / "skills" / "bmad-agent-texas" / "scripts"
if str(TEXAS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(TEXAS_SCRIPTS))

from retrieval.fake_provider import make_row  # noqa: E402

TRIAL_ID = UUID("12345678-1234-4234-8234-123456789abc")
CORPUS = Path("tests/fixtures/trial_corpus/README.md")


@pytest.fixture(autouse=True)
def _pin_g0_enrichment_off(monkeypatch: pytest.MonkeyPatch) -> None:
    """Canonical-arc S5-3a — flip-robustness pin (D-migrate-canonical, pin OFF).

    Pins the G0-enrichment kill-switch explicitly OFF so every walk in this suite
    first-pauses at G1 deterministically, regardless of the process default (3b
    flips ``MARCUS_G0_ENRICHMENT_ACTIVE`` default OFF->ON). G0-enrichment is
    irrelevant to these subjects (two-walk research-wiring parity, dispatch-toggle
    threading, FAIL-mode citation gate) — they reach/cross G1 directly. Explicit
    ``"0"`` (not ``delenv``) is what survives the 3b code-default flip.
    """
    monkeypatch.setenv("MARCUS_G0_ENRICHMENT_ACTIVE", "0")


# --------------------------------------------------------------------------- #
# Fixtures: a locked lesson plan with an in-scope research-enrichment gap.
# --------------------------------------------------------------------------- #


def _locked_plan_dict(include_gap: bool = True) -> dict:
    """Raw (serialized) locked lesson plan as the runner holds it."""
    gaps = (
        [
            {
                "gap_id": "gap-1",
                "description": "Need peer-reviewed evidence for the trend claim",
                "suggested_posture": "corroborate",
            }
        ]
        if include_gap
        else []
    )
    return {
        "plan_units": [
            {
                "unit_id": "u1",
                "scope_decision": {"scope": "in-scope"},
                "gaps": gaps,
            },
            {
                "unit_id": "u2",
                "scope_decision": {"scope": "out-of-scope"},
                "gaps": [],
            },
        ]
    }


def _contribution(specialist_id: str, output: dict, node_id: str | None = None):
    return SpecialistContribution.from_output(
        specialist_id=specialist_id,
        output=output,
        model_used="gpt-5-nano",
        node_id=node_id,
    )


def _envelope_with_plan(include_gap: bool = True) -> ProductionEnvelope:
    envelope = ProductionEnvelope(trial_id=TRIAL_ID)
    envelope.add_contribution(
        _contribution(
            "irene_pass1",
            {"lesson_plan": _locked_plan_dict(include_gap=include_gap)},
            node_id="04A",
        )
    )
    return envelope


# --------------------------------------------------------------------------- #
# AC-D1 — bridge constructed + dispatched on the trial path (local, no network).
# --------------------------------------------------------------------------- #


def test_ac_d1_bridge_dispatched_with_real_posture_selector() -> None:
    """The real bridge + real DeterministicPostureSelector dispatch ≥1 gap."""
    sys.path.insert(0, str(REPO_ROOT / "skills" / "bmad_agent_tracy" / "scripts"))
    from irene_bridge import IreneTracyBridge

    plan = research_wiring._plan_dict_for_bridge_from_raw(_locked_plan_dict())
    bridge = IreneTracyBridge(DeterministicPostureSelector())
    results = bridge.process_plan_locked(plan)
    # One in-scope unit with one gap → exactly one bridge result.
    assert len(results) == 1
    # The posture selector shapes the brief into a real RetrievalIntent.
    assert research_wiring._is_retrieval_intent(results[0])
    assert results[0].provider_hints  # non-empty


def test_ac_d1_run_research_wiring_records_first_class_contribution() -> None:
    """run_research_wiring lands a research_entries contribution at §04.55."""
    envelope = _envelope_with_plan()
    updated = run_research_wiring(
        node_id=research_wiring.RESEARCH_WIRING_NODE_ID,
        production_envelope=envelope,
        posture_selector=DeterministicPostureSelector(),
        dispatch_live=False,
    )
    contribution = updated.get_contribution(
        research_wiring.RESEARCH_WIRING_SPECIALIST_ID,
        node_id=research_wiring.RESEARCH_WIRING_NODE_ID,
    )
    assert contribution is not None
    assert research_wiring.RESEARCH_ENTRIES_KEY in contribution.output
    # Idempotent (resume-safe): a re-run does not duplicate the contribution.
    again = run_research_wiring(
        node_id=research_wiring.RESEARCH_WIRING_NODE_ID,
        production_envelope=updated,
        posture_selector=DeterministicPostureSelector(),
        dispatch_live=False,
    )
    assert len(again.contributions) == len(updated.contributions)


# --------------------------------------------------------------------------- #
# AC-D2 — TWO-WALK parity (BINDING): execute a REAL continuation walk.
# --------------------------------------------------------------------------- #


_RESEARCH_GAP_OUTPUTS: dict[str, dict] = {
    # irene_pass1 lands a locked plan carrying an in-scope research-enrichment
    # gap pre-G1; cd lands the directive the §06 builder needs downstream.
    "irene_pass1": {"lesson_plan": _locked_plan_dict(include_gap=True)},
    "cd": {"cd_directive": {"experience_profile": "text-led"}},
}


def _install_research_adapter(monkeypatch) -> None:
    """Strict-signature fake adapter landing the research-gap lesson plan."""

    class _Adapter:
        def invoke_specialist(
            self,
            *,
            specialist_id: str,
            envelope: ProductionEnvelope,
            dependency_map: dict | None = None,
            cost_usd: float = 0.0,
            base_state=None,
            node_id: str | None = None,
            runner_supplied_payload: dict | None = None,
            projection_map: dict | None = None,
        ) -> ProductionEnvelope:
            del dependency_map, base_state, runner_supplied_payload, projection_map
            updated = envelope.model_copy(deep=True)
            updated.add_contribution(
                SpecialistContribution.from_output(
                    specialist_id=specialist_id,
                    output=_RESEARCH_GAP_OUTPUTS.get(
                        specialist_id, {"specialist_id": specialist_id}
                    ),
                    model_used="gpt-5-nano",
                    cost_usd=cost_usd,
                    node_id=node_id,
                )
            )
            return updated

    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", _Adapter)


def _g1_verdict(tmp_path: Path):
    from app.models.state.operator_verdict import OperatorVerdict

    payload = json.loads(
        (tmp_path / str(TRIAL_ID) / "decision-card-G1.json").read_text()
    )
    return OperatorVerdict(
        trial_id=TRIAL_ID,
        verb="approve",
        gate_id="G1",
        card_id=UUID(payload["card"]["card_id"]),
        operator_id="operator_test",
        decision_card_digest=payload["digest"],
    )


def test_ac_d2_two_walk_parity_fires_on_real_continuation(
    tmp_path: Path, monkeypatch
) -> None:
    """Start walk pauses at G1; the side-effect fires on the continuation walk.

    Executes (NOT greps) a real continuation against the REAL manifest: run →
    pause-at-G1 → resume past G1 → assert the research_wiring contribution exists
    at §04.55 (which the start walk never reaches). Mirrors the storyboard/chooser
    publisher both-walks precedent.
    """
    from app.gates.resume_api import clear_resume_registry

    clear_resume_registry()
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    _install_research_adapter(monkeypatch)

    # --- Start walk: must PAUSE at G1 and NOT yet have the side-effect ---
    started = production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        max_specialist_calls=12,
    )
    assert started.status == "paused-at-gate"
    assert started.paused_gate == "G1"
    assert (
        started.production_envelope.get_contribution(
            research_wiring.RESEARCH_WIRING_SPECIALIST_ID,
            node_id=research_wiring.RESEARCH_WIRING_NODE_ID,
        )
        is None
    ), "§04.55 is after G1; the start walk must NOT reach the research-wiring hook"

    # --- Continuation walk: resume past G1 → the side-effect MUST fire ---
    resumed = production_runner.resume_production_trial(
        trial_id=TRIAL_ID,
        verdict=_g1_verdict(tmp_path),
        runs_root=tmp_path,
        max_specialist_calls=12,
    )
    continuation_side_effect = resumed.production_envelope.get_contribution(
        research_wiring.RESEARCH_WIRING_SPECIALIST_ID,
        node_id=research_wiring.RESEARCH_WIRING_NODE_ID,
    )
    assert continuation_side_effect is not None, (
        "TWO-WALK parity: the research-wiring side-effect MUST fire on the "
        "continuation walk (it never fires on the start walk for §04.55)"
    )
    assert research_wiring.RESEARCH_ENTRIES_KEY in continuation_side_effect.output


# --------------------------------------------------------------------------- #
# AC-D3 — RetrievalIntent shape conformance (registered providers only).
# --------------------------------------------------------------------------- #


def test_ac_d3_intent_names_only_registered_providers() -> None:
    from retrieval.provider_directory import list_providers

    selector = DeterministicPostureSelector()
    intent = selector.select_posture(
        {"gap_description": "trend evidence", "target_element": "u1"}
    )
    registered = {
        p.id for p in list_providers(shape="retrieval") if p.status in {"ready", "stub"}
    }
    named = {hint.provider for hint in intent.provider_hints}
    assert named  # non-empty (provider_hints REQUIRED v1)
    assert named <= registered, "intent names only registered live providers"


def test_ac_d3_malformed_intent_raises_no_silent_drop() -> None:
    """A malformed Tracy intent raises (no silent drop).

    Empty ``retrieval_intents`` raises the typed ``RetrievalIntentParseError``;
    a structurally-broken intent raises a ``ValidationError`` from the contract
    validator. Either way the malformed intent is NEVER silently dropped.
    """
    from pydantic import ValidationError

    from app.specialists.tracy._act import (
        RetrievalIntentParseError,
        parse_retrieval_intents,
    )

    with pytest.raises(RetrievalIntentParseError):
        parse_retrieval_intents({"retrieval_intents": []})

    with pytest.raises((RetrievalIntentParseError, ValidationError)):
        parse_retrieval_intents({"retrieval_intents": [{"provider_hints": []}]})


# --------------------------------------------------------------------------- #
# AC-D4 — Texas dispatch reached (live; skip-gated on creds/reachability).
# --------------------------------------------------------------------------- #


def _live_creds_present() -> bool:
    scite = os.environ.get("SCITE_USER_NAME") and os.environ.get("SCITE_PASSWORD")
    consensus = os.environ.get("CONSENSUS_API_KEY")
    return bool(scite or consensus)


def test_ac_d4_texas_dispatch_live_or_skip() -> None:
    if not _live_creds_present():
        pytest.skip(
            "live Scite/Consensus creds unset — operator-gated leg (AC-O1/AC-O4)"
        )
    from retrieval.dispatcher import dispatch as dispatch_intent

    selector = DeterministicPostureSelector()
    intent = selector.select_posture(
        {"gap_description": "exercise improves memory", "target_element": "u1"}
    )
    try:
        result = dispatch_intent(intent)
    except Exception as exc:  # service unreachable → skip, not fail
        pytest.skip(f"live retrieval service unreachable: {type(exc).__name__}: {exc}")
    results = result if isinstance(result, list) else [result]
    rows = [row for pr in results for row in pr.rows]
    assert any(r.source_id and r.provider for r in rows)


# --------------------------------------------------------------------------- #
# AC-D5 — cited-entry minting + source_ref derivation.
# --------------------------------------------------------------------------- #


def test_ac_d5_source_ref_is_pure_function_and_hash_stable() -> None:
    row = make_row("10.1234/abc", provider="scite", title="A study", body="findings")
    assert derive_source_ref("scite", "10.1234/abc") == derive_source_ref(
        "scite", "10.1234/abc"
    )
    assert compute_source_hash(row) == compute_source_hash(row)
    entry = mint_cited_entry(row, citation_index=1)
    assert entry.source_ref == derive_source_ref("scite", "10.1234/abc")
    assert entry.provider == "scite"
    assert entry.source_id == "10.1234/abc"
    assert entry.source_hash.startswith("sha256:")


# --------------------------------------------------------------------------- #
# AC-D6 — L2 citation channel: unsourced==0 in FAIL mode (THE gate).
# --------------------------------------------------------------------------- #


def test_ac_d6_unsourced_zero_passes_one_fails() -> None:
    rows = [make_row("10.1/a", provider="scite"), make_row("10.2/b", provider="consensus")]
    resolvable = build_retrieval_source_refs(rows)
    citations_clean = [
        {"source_ref": derive_source_ref("scite", "10.1/a")},
        {"source_ref": derive_source_ref("consensus", "10.2/b")},
    ]
    # All resolve → unsourced == 0 → PASS.
    assert gate_citation_fidelity(citations_clean, resolvable_source_refs=resolvable) == 0

    citations_dirty = citations_clean + [{"source_ref": "retrieval:scite:does-not-exist"}]
    with pytest.raises(CitationFidelityError) as excinfo:
        gate_citation_fidelity(citations_dirty, resolvable_source_refs=resolvable)
    assert excinfo.value.unsourced_citations == 1


def test_ac_d6_gate_is_distinct_from_numeric_drift_rate() -> None:
    """The citation gate is a resolvability count, NOT the warn-only drift rate."""
    report = audit_research_supplements(
        "Sales rose to $4.5 trillion.",
        "The corpus mentions $4.5 trillion in revenue.",
        retrieved_figures=set(),
    )
    # The L2 numeric report carries drift_rate; the citation gate carries no such
    # key — they are orthogonal checks.
    assert "drift_rate" in report
    rows = [make_row("10.1/a", provider="scite")]
    resolvable = build_retrieval_source_refs(rows)
    assert (
        gate_citation_fidelity(
            [{"source_ref": derive_source_ref("scite", "10.1/a")}],
            resolvable_source_refs=resolvable,
        )
        == 0
    )


# --------------------------------------------------------------------------- #
# AC-D7 — research_supplements channel populated, classified, not drift.
# --------------------------------------------------------------------------- #


def test_ac_d7_retrieved_figure_classifies_as_research_supplement() -> None:
    # Source carries $2.1 billion (so the audit is performable — non-zero
    # denominator); the narration's $4.5 trillion is NOT in source but IS a
    # declared retrieved supplement → research_supplement, not drift.
    report = audit_research_supplements(
        "The market reached $4.5 trillion, up from $2.1 billion.",
        "The corpus reports a baseline of $2.1 billion.",
        retrieved_figures={"$4.5 trillion"},
    )
    buckets = report["buckets"]
    supplement_count = buckets["research_supplement"]["count"]
    assert supplement_count >= 1, "retrieved figure must land in research_supplement"
    # The retrieved figure is NOT counted as unsourced drift.
    assert "money-trillion:4.5" not in [
        p["narration_normalized"] for p in buckets["unsourced_numeric"]["pairs"]
    ]


def test_ac_d7_l2_engine_called_read_only_no_signature_change() -> None:
    """source_fidelity_audit is a pure read-only caller — frozen-engine discipline."""
    import inspect

    from app.specialists._shared import source_fidelity_audit

    sig = inspect.signature(source_fidelity_audit.audit_numeric_provenance)
    # The L2 signature is unchanged: (narration_text, source_text, *, research_supplements).
    assert list(sig.parameters) == [
        "narration_text",
        "source_text",
        "research_supplements",
    ]
    assert source_fidelity_audit.SEMANTIC_TRIPWIRE is None  # semantic leg still STUB


# --------------------------------------------------------------------------- #
# AC-D8 — run-record handoff to S2 (research_entries key + shape).
# --------------------------------------------------------------------------- #


def test_ac_d8_research_entries_handoff_shape() -> None:
    envelope = _envelope_with_plan()
    rows = [make_row("10.1/a", provider="scite", title="Study A")]
    entries = [mint_cited_entry(r, citation_index=i) for i, r in enumerate(rows, 1)]
    output = {
        research_wiring.RESEARCH_ENTRIES_KEY: [e.model_dump(mode="json") for e in entries]
    }
    envelope.add_contribution(
        _contribution(
            research_wiring.RESEARCH_WIRING_SPECIALIST_ID,
            output,
            node_id=research_wiring.RESEARCH_WIRING_NODE_ID,
        )
    )
    read_back = research_wiring.research_entries_from_envelope(envelope)
    assert len(read_back) == 1
    entry = read_back[0]
    assert set(entry) == {
        "citation_id",
        "source_ref",
        "provider",
        "source_id",
        "title",
        "source_hash",
    }


# --------------------------------------------------------------------------- #
# AC-D9 — DP6 stamp.
#
# T1 FINDING (overrides spec §3.5's "none in slide_production_paths" assumption,
# per the task prompt): the REAL slide-production-paths.yaml lists
# `app/marcus/orchestrator/production_runner.py` (Class 6 chooser path), which
# the S3 diff touches. DP6 therefore FLIPS to fresh-required for an S3 diff —
# conservatively correct. The live AC-O1 run needs a FRESH Gamma render, not a
# frozen reuse; the run record stamps accordingly (no empty-intersection stamp).
# --------------------------------------------------------------------------- #


def test_ac_d9_dp6_flips_fresh_because_production_runner_is_slide_path() -> None:
    s3_diff = [
        "app/marcus/orchestrator/production_runner.py",
        "app/marcus/orchestrator/research_wiring.py",
        "app/marcus/orchestrator/research_citation.py",
        "tests/integration/marcus/test_braid_s3_research_wiring.py",
    ]
    assert fresh_gamma_required(s3_diff) is True, (
        "production_runner.py is in slide_production_paths → DP6 fresh-required "
        "(conservatively correct; the live leg mints a fresh render)"
    )


def test_ac_d9_reuse_stamp_shape_for_empty_intersection() -> None:
    # The reuse stamp helper is exercised on the hypothetical empty-intersection
    # path (a diff that touches ONLY the new non-slide wiring modules); the stamp
    # value is what an empty-intersection run would record.
    non_slide_only_diff = [
        "app/marcus/orchestrator/research_wiring.py",
        "app/marcus/orchestrator/research_citation.py",
    ]
    assert fresh_gamma_required(non_slide_only_diff) is False
    assert reuse_stamp("deadbeef") == "empty-intersection@deadbeef"


# --------------------------------------------------------------------------- #
# AC-D10 — no regression on the unwired path (no research gaps).
# --------------------------------------------------------------------------- #


def test_ac_d10_degenerate_empty_records_empty_but_present() -> None:
    envelope = _envelope_with_plan(include_gap=False)
    assert research_wiring.has_research_goals(envelope) is False
    updated = run_research_wiring(
        node_id=research_wiring.RESEARCH_WIRING_NODE_ID,
        production_envelope=envelope,
        posture_selector=DeterministicPostureSelector(),
        dispatch_live=False,
    )
    entries = research_wiring.research_entries_from_envelope(updated)
    assert entries == [], "no gaps → empty-but-present research_entries section"
    # The section is PRESENT (contribution exists), just empty.
    assert (
        updated.get_contribution(
            research_wiring.RESEARCH_WIRING_SPECIALIST_ID,
            node_id=research_wiring.RESEARCH_WIRING_NODE_ID,
        )
        is not None
    )


def test_ac_d10_no_plan_no_dispatch() -> None:
    envelope = ProductionEnvelope(trial_id=TRIAL_ID)  # no irene_pass1 contribution
    assert research_wiring.has_research_goals(envelope) is False
    updated = run_research_wiring(
        node_id=research_wiring.RESEARCH_WIRING_NODE_ID,
        production_envelope=envelope,
        posture_selector=DeterministicPostureSelector(),
        dispatch_live=False,
    )
    assert research_wiring.research_entries_from_envelope(updated) == []


# --------------------------------------------------------------------------- #
# Run-record L2 report assembly (AC-O2 shape; resolvability-only boundary).
# --------------------------------------------------------------------------- #


def test_l2_citation_report_shape_and_named_boundary() -> None:
    rows = [make_row("10.1/a", provider="scite", title="A")]
    entries = [mint_cited_entry(r, citation_index=1) for r in rows]
    resolvable = build_retrieval_source_refs(rows)
    l2_numeric = audit_research_supplements(
        "Figure $4.5 trillion.", "Corpus $4.5 trillion.", retrieved_figures=set()
    )
    report = assemble_l2_citation_report(
        entries, resolvable_source_refs=resolvable, l2_numeric_report=l2_numeric
    )
    assert report["unsourced_citations"] == 0
    assert report["citation_manifest"][0]["citation_id"] == "cite-001"
    assert "support" in report["scope_note"].lower()  # named boundary stated
    # JSON-serializable (run-record attach).
    json.dumps(report)


# --------------------------------------------------------------------------- #
# No manifest node added (option A confirmation).
# --------------------------------------------------------------------------- #


def test_no_manifest_node_added_option_a() -> None:
    manifest = yaml.safe_load(
        (REPO_ROOT / "state" / "config" / "pipeline-manifest.yaml").read_text(
            encoding="utf-8"
        )
    )
    node_ids = {node["id"] for node in manifest["nodes"]}
    # The hook keys off the EXISTING §04.55 node; no new node was introduced.
    assert research_wiring.RESEARCH_WIRING_NODE_ID in node_ids
    assert "research_wiring" not in node_ids
    assert "tracy-fanout" not in node_ids


# =========================================================================== #
# T11 HAND-BACK remediation — RED-first wiring proofs.
#
# Two HAND-BACK lanes found the library pieces unit-tested but NOT wired to the
# runner's actual execution. The tests below FAIL on the pre-remediation code
# (proving the orphan) and pass once each fix is wired.
# =========================================================================== #


# --------------------------------------------------------------------------- #
# M1 — live Texas dispatch toggle reaches BOTH walk sites (was literal False).
# --------------------------------------------------------------------------- #


def _spy_run_research_wiring(monkeypatch):
    """Replace run_research_wiring with a spy capturing dispatch_live per call.

    NOT a mock of the system under test — it stands in for the wiring callee so
    the test can assert the runner THREADS the toggle through to both walks. The
    spy still records the §04.55 contribution so the walk proceeds normally.
    """
    seen: list[bool] = []
    real = research_wiring.run_research_wiring

    def _spy(*, dispatch_live: bool, **kwargs):
        seen.append(dispatch_live)
        # Force dispatch_live=False inside the real callee so no live network
        # call fires regardless of the toggle (we only assert on the THREADING).
        return real(dispatch_live=False, **kwargs)

    monkeypatch.setattr(research_wiring, "run_research_wiring", _spy)
    return seen


def test_m1_toggle_off_by_default_threads_false_to_both_walks(
    tmp_path: Path, monkeypatch
) -> None:
    """With the toggle UNSET, dispatch_live=False reaches both walks (safe default)."""
    from app.gates.resume_api import clear_resume_registry

    clear_resume_registry()
    monkeypatch.delenv("MARCUS_RESEARCH_DISPATCH_LIVE", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    _install_research_adapter(monkeypatch)
    seen = _spy_run_research_wiring(monkeypatch)

    production_runner.run_production_trial(
        CORPUS, "production", "operator_test",
        trial_id=TRIAL_ID, runs_root=tmp_path, max_specialist_calls=12,
    )
    production_runner.resume_production_trial(
        trial_id=TRIAL_ID, verdict=_g1_verdict(tmp_path),
        runs_root=tmp_path, max_specialist_calls=12,
    )
    # §04.55 is reached only on the continuation walk → at least one call, all OFF.
    assert seen, "research-wiring hook never fired across either walk"
    assert all(flag is False for flag in seen)


def test_m1_toggle_on_threads_true_to_continuation_walk(
    tmp_path: Path, monkeypatch
) -> None:
    """RED on literal-False code: with the toggle ON, dispatch_live=True must reach
    the §04.55 hook on the continuation walk (the only walk that reaches it)."""
    from app.gates.resume_api import clear_resume_registry

    clear_resume_registry()
    monkeypatch.setenv("MARCUS_RESEARCH_DISPATCH_LIVE", "1")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    _install_research_adapter(monkeypatch)
    seen = _spy_run_research_wiring(monkeypatch)

    production_runner.run_production_trial(
        CORPUS, "production", "operator_test",
        trial_id=TRIAL_ID, runs_root=tmp_path, max_specialist_calls=12,
    )
    production_runner.resume_production_trial(
        trial_id=TRIAL_ID, verdict=_g1_verdict(tmp_path),
        runs_root=tmp_path, max_specialist_calls=12,
    )
    assert seen, "research-wiring hook never fired on the continuation walk"
    assert any(flag is True for flag in seen), (
        "toggle ON must thread dispatch_live=True to the §04.55 hook — the "
        "literal-False wiring never does (M1 orphan)"
    )


def test_m1_both_hook_sites_read_the_toggle_not_a_literal() -> None:
    """Static guard: neither walk passes a literal dispatch_live=False (M1)."""
    src = (
        REPO_ROOT / "app" / "marcus" / "orchestrator" / "production_runner.py"
    ).read_text(encoding="utf-8")
    assert "dispatch_live=False" not in src, (
        "a literal dispatch_live=False at a hook site means the toggle is dead"
    )
    assert src.count("dispatch_live=_research_dispatch_live()") == 2, (
        "both walk sites must read the operator-gated toggle (two-walk parity)"
    )


# --------------------------------------------------------------------------- #
# M2 — G2 gate + L2 report + manifest run ON THE TRIAL PATH (were orphaned).
# --------------------------------------------------------------------------- #


def _injected_entries():
    rows = [
        make_row("10.1/a", provider="scite", title="Study A", body="x"),
        make_row("10.2/b", provider="consensus", title="Study B", body="y"),
    ]
    return [mint_cited_entry(r, citation_index=i) for i, r in enumerate(rows, 1)]


def test_m2_manifest_and_l2_report_attached_on_trial_path() -> None:
    """RED on orphaned code: the wired hook must STAMP the manifest + L2 report
    onto the §04.55 contribution when cited entries exist (not just unit-tested)."""
    from app.marcus.orchestrator.research_citation import CitedResearchEntry  # noqa: F401

    envelope = _envelope_with_plan()
    updated = run_research_wiring(
        node_id=research_wiring.RESEARCH_WIRING_NODE_ID,
        production_envelope=envelope,
        posture_selector=DeterministicPostureSelector(),
        dispatch_live=False,
        injected_cited_entries=_injected_entries(),
    )
    contribution = updated.get_contribution(
        research_wiring.RESEARCH_WIRING_SPECIALIST_ID,
        node_id=research_wiring.RESEARCH_WIRING_NODE_ID,
    )
    assert contribution is not None
    out = contribution.output
    assert research_wiring.CITATION_MANIFEST_KEY in out, "citation manifest not stamped"
    assert research_wiring.L2_CITATION_REPORT_KEY in out, "L2 report not stamped"
    manifest = out[research_wiring.CITATION_MANIFEST_KEY]
    assert {m["citation_id"] for m in manifest} == {"cite-001", "cite-002"}
    assert all("source_ref" in m and "source_hash" in m for m in manifest)
    assert out[research_wiring.L2_CITATION_REPORT_KEY]["unsourced_citations"] == 0


def test_m2_unsourced_citation_fail_mode_gates_on_trial_path() -> None:
    """RED on orphaned code: an unsourced citation must raise the FAIL-mode gate
    on the wired hook (the gate had ZERO callers outside tests)."""
    envelope = _envelope_with_plan()
    entries = _injected_entries()
    # Resolvable set is MISSING the second entry's source_ref → unsourced → FAIL.
    resolvable = {entries[0].source_ref}
    with pytest.raises(CitationFidelityError) as excinfo:
        run_research_wiring(
            node_id=research_wiring.RESEARCH_WIRING_NODE_ID,
            production_envelope=envelope,
            posture_selector=DeterministicPostureSelector(),
            dispatch_live=False,
            injected_cited_entries=entries,
            injected_resolvable_source_refs=resolvable,
        )
    assert excinfo.value.unsourced_citations == 1


def test_m2_fail_mode_gate_error_pauses_the_trial_walk(
    tmp_path: Path, monkeypatch
) -> None:
    """The FAIL-mode gate on the continuation walk must error-pause (recoverable),
    not crash the cycle. Wires an unsourced injected set via a runner monkeypatch."""
    from app.gates.resume_api import clear_resume_registry

    clear_resume_registry()
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    _install_research_adapter(monkeypatch)

    real = research_wiring.run_research_wiring

    def _force_unsourced(**kwargs):
        kwargs.pop("injected_cited_entries", None)
        kwargs.pop("injected_resolvable_source_refs", None)
        entries = _injected_entries()
        return real(
            **kwargs,
            injected_cited_entries=entries,
            injected_resolvable_source_refs=set(),  # nothing resolves → FAIL
        )

    monkeypatch.setattr(production_runner, "_research_dispatch_live", lambda: False)
    monkeypatch.setattr(research_wiring, "run_research_wiring", _force_unsourced)

    production_runner.run_production_trial(
        CORPUS, "production", "operator_test",
        trial_id=TRIAL_ID, runs_root=tmp_path, max_specialist_calls=12,
    )
    resumed = production_runner.resume_production_trial(
        trial_id=TRIAL_ID, verdict=_g1_verdict(tmp_path),
        runs_root=tmp_path, max_specialist_calls=12,
    )
    assert resumed.status == "paused-at-error", (
        "FAIL-mode citation gate must error-pause the walk, not crash it"
    )


# --------------------------------------------------------------------------- #
# M3 — no-silent-drop: a shaping failure leaves a run-record trace (AC-D3).
# --------------------------------------------------------------------------- #


def test_m3_dropped_shaping_failure_is_recorded_on_contribution() -> None:
    """RED: a select_posture failure is caught by the bridge into {"status":
    "failed"} and filtered by the wiring with NO record. The wiring must record
    the dropped COUNT + reason so the failure leaves a run-record trace."""

    class _BoomSelector:
        def select_posture(self, brief):  # noqa: ANN001, ANN201
            raise RuntimeError("posture shaping blew up")

    envelope = _envelope_with_plan()  # one in-scope gap → one bridge dispatch
    updated = run_research_wiring(
        node_id=research_wiring.RESEARCH_WIRING_NODE_ID,
        production_envelope=envelope,
        posture_selector=_BoomSelector(),
        dispatch_live=False,
    )
    contribution = updated.get_contribution(
        research_wiring.RESEARCH_WIRING_SPECIALIST_ID,
        node_id=research_wiring.RESEARCH_WIRING_NODE_ID,
    )
    dropped = contribution.output[research_wiring.DROPPED_DISPATCH_KEY]
    assert dropped["count"] == 1, "the shaping failure must be COUNTED, not silent"
    assert dropped["failures"][0]["status"] == "failed"
    assert "blew up" in dropped["failures"][0]["reason"]


# --------------------------------------------------------------------------- #
# Zero-denominator L2 status surfaced (S2-analogue).
# --------------------------------------------------------------------------- #


def test_l2_report_surfaces_unauditable_status_not_silently_clean() -> None:
    """RED: assemble_l2_citation_report embedded a status="FAIL" (zero-denominator)
    numeric leg without surfacing its status — it read as clean. The report must
    surface the L2 numeric status + an explicit auditable flag."""
    rows = [make_row("10.1/a", provider="scite", title="A")]
    entries = [mint_cited_entry(r, citation_index=1) for r in rows]
    resolvable = build_retrieval_source_refs(rows)
    # Empty narration/source → zero-denominator → L2 numeric status == "FAIL".
    l2_unauditable = audit_research_supplements("", "", retrieved_figures=set())
    assert l2_unauditable["status"] == "FAIL"
    report = assemble_l2_citation_report(
        entries, resolvable_source_refs=resolvable, l2_numeric_report=l2_unauditable
    )
    assert report["l2_numeric_status"] == "FAIL"
    assert report["l2_numeric_auditable"] is False, (
        "an un-auditable numeric leg must NOT read as a clean attachment"
    )


# --------------------------------------------------------------------------- #
# Unregistered-provider fail-soft (one bad hint must not kill the node).
# --------------------------------------------------------------------------- #


def test_unregistered_provider_intent_is_fail_soft() -> None:
    """RED: _dispatch_intents_to_texas called dispatch with no try/except — a
    DispatchError (unregistered/dead provider) killed the node. It must be
    fail-soft: record + continue, so one bad provider hint doesn't kill the trial."""
    from retrieval import AcceptanceCriteria, ProviderHint, RetrievalIntent

    bad_intent = RetrievalIntent(
        intent="find evidence",
        provider_hints=[
            ProviderHint(provider="no-such-provider-xyz", params={"mode": "search"})
        ],
        acceptance_criteria=AcceptanceCriteria(
            mechanical={"min_results": 1}, provider_scored={}, semantic_deferred="n/a"
        ),
        cross_validate=False,
    )
    # Must NOT raise — the bad hint is recorded + skipped, yielding zero rows.
    rows = research_wiring._dispatch_intents_to_texas([bad_intent])
    assert rows == []


# --------------------------------------------------------------------------- #
# AC-D7 negative assertion — dropping the supplement declaration → drift.
# --------------------------------------------------------------------------- #


def test_ac_d7_negative_without_supplement_declaration_is_drift() -> None:
    """The DISCRIMINATING assertion: drop the research_supplement declaration and
    the figure becomes unsourced_numeric drift — proving the supplement channel
    (not some other path) is what reclassifies the retrieved figure."""
    # WITH declaration → research_supplement (the positive case, AC-D7).
    with_decl = audit_research_supplements(
        "The market reached $4.5 trillion, up from $2.1 billion.",
        "The corpus reports a baseline of $2.1 billion.",
        retrieved_figures={"$4.5 trillion"},
    )
    assert with_decl["buckets"]["research_supplement"]["count"] >= 1
    # WITHOUT declaration → the SAME figure is now unsourced_numeric drift.
    without_decl = audit_research_supplements(
        "The market reached $4.5 trillion, up from $2.1 billion.",
        "The corpus reports a baseline of $2.1 billion.",
        retrieved_figures=set(),
    )
    assert without_decl["buckets"]["research_supplement"]["count"] == 0
    drift_norms = [
        p["narration_normalized"]
        for p in without_decl["buckets"]["unsourced_numeric"]["pairs"]
    ]
    assert any("4.5" in n for n in drift_norms), (
        "without the supplement declaration the retrieved figure must drift"
    )


# --------------------------------------------------------------------------- #
# Duplicate source_ref — distinct citation_ids for identical refs collapse.
# --------------------------------------------------------------------------- #


def test_duplicate_source_refs_are_deduped_in_manifest() -> None:
    """RED: the minter assigns distinct citation_ids to identical (provider,
    source_id) rows; build_retrieval_source_refs collapses dupes but the manifest
    carried twins. The wiring must de-dup (first-wins)."""
    from app.marcus.orchestrator.research_citation import (
        dedupe_cited_entries,
        find_duplicate_citations,
    )

    rows = [
        make_row("10.1/a", provider="scite", title="A"),
        make_row("10.1/a", provider="scite", title="A"),  # identical ref
    ]
    entries = [mint_cited_entry(r, citation_index=i) for i, r in enumerate(rows, 1)]
    # Pre-dedupe the two entries point at one (provider, source_id).
    assert find_duplicate_citations(entries) == [("scite", "10.1/a")]
    deduped = dedupe_cited_entries(entries)
    assert len(deduped) == 1, "identical source_refs must collapse first-wins"

    # And the wired hook de-dups on the trial path too.
    envelope = _envelope_with_plan()
    updated = run_research_wiring(
        node_id=research_wiring.RESEARCH_WIRING_NODE_ID,
        production_envelope=envelope,
        posture_selector=DeterministicPostureSelector(),
        dispatch_live=False,
        injected_cited_entries=entries,
    )
    contribution = updated.get_contribution(
        research_wiring.RESEARCH_WIRING_SPECIALIST_ID,
        node_id=research_wiring.RESEARCH_WIRING_NODE_ID,
    )
    manifest = contribution.output[research_wiring.CITATION_MANIFEST_KEY]
    refs = [m["source_ref"] for m in manifest]
    assert len(refs) == len(set(refs)), "manifest must carry no duplicate source_refs"
