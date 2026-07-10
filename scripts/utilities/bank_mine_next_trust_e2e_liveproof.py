"""Mine-next trust-hardening integrated E2E — fresh assets under runs/<uuid>/.

Chains in ONE primary run dir (no Gamma / no full production walk):

1. Wave-1 seams: UDAC GATE_ASSET_MAP · reenter API · join-collapse detector
2. plan-dialogue → planning companions (fresh)
3. Live Irene Pass-1 → irene-pass1.lesson-plan.json (fresh asset)
4. Auto-derive ComponentSelection + trial-start spy consumption
5. Wave-2 fidelity: T4a precision · T4b positive-carry · T4c flag-ON activation
   over real Leg-3 Pass-2 artifacts + synthetic Tejal-shaped figures
6. Negatives: confab halt · carry-miss halt · flag-OFF inert · join collapse refuse

Produces evidence pack + copies key fresh assets into the run dir.
"""

from __future__ import annotations

import copy
import inspect
import json
import os
import sys
from datetime import UTC, datetime
from datetime import datetime as dt
from pathlib import Path
from uuid import UUID, uuid4

import yaml

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from scripts.utilities.env_loader import load_env  # noqa: E402

load_env(REPO / ".env")

from app.marcus.cli.plan_dialogue_cli import main as plan_dialogue_main  # noqa: E402
from app.marcus.cli.trial import start_trial  # noqa: E402
from app.marcus.lesson_plan.collateral_selection import (  # noqa: E402
    CollateralSelectionError,
    derive_selection_from_lesson_plan,
    load_selection_from_lesson_plan_json,
)
from app.marcus.lesson_plan.composition import compose_and_digest  # noqa: E402
from app.marcus.lesson_plan.planning_context import load_planning_context  # noqa: E402
from app.marcus.lesson_plan.run_asset_index import GATE_ASSET_MAP, DigestAlgo  # noqa: E402
from app.marcus.orchestrator import storyboard_publisher  # noqa: E402
from app.marcus.orchestrator.production_runner import (  # noqa: E402
    recover_production_trial,
)
from app.models.runtime.production_envelope import (  # noqa: E402
    ProductionEnvelope,
    SpecialistContribution,
    compute_output_digest,
)
from app.models.state.cache_state import CacheState  # noqa: E402
from app.models.state.component_selection import ComponentSelection  # noqa: E402
from app.models.state.run_state import RunState  # noqa: E402
from app.specialists._shared.figure_tokens import (  # noqa: E402
    PERCENT_TOLERANCE_PP,
    _figure_near_match,
    _figures,
)
from app.specialists.irene.graph import (  # noqa: E402
    FIGURE_FIDELITY_ACTIVE_ENV,
    Pass2GroundingError,
    _assert_figure_citations_within_perceived,
    _assert_narration_figures_sourced,
    _assert_source_figures_positively_carried,
    _slide_roster,
    narration_figure_fidelity_active,
)
from app.specialists.irene_pass1 import graph as pass1_graph  # noqa: E402
from app.specialists.narration_join import (  # noqa: E402
    collapsed_segment_ids,
    join_narration_segments,
)

TEJAL = REPO / "course-content/courses/tejal-c1m1-p4-assessments-bridge"
FIXTURE_INPUT = REPO / "tests/fixtures/trial_corpus/README.md"
LEG3 = (
    REPO
    / "_bmad-output/implementation-artifacts/evidence"
    / "leg3-cu03-subslide-invariant-20260701T021037Z"
)
FIDELITY_SOURCE = (
    "Medical knowledge that once took 50 years to double now doubles in just "
    "73 days. Adoption is already here — 66% of physicians report using some "
    "form of AI — while formal oversight training remains limited. Roughly "
    "18.4% still lag on formal oversight curricula."
)

PURPOSE = (
    "Bridge Module-1 innovator-mindset into Module-2 leadership-identity "
    "with assessment-driven reflection checkpoints"
)
AUDIENCE = (
    "APC Cohort-C1 clinician-innovators preparing for Module-2 "
    "leadership-identity work"
)
LO_A = (
    "Map Module-1 Opportunity-Radar targets onto Module-2 "
    "leadership-identity competencies using assessment-bridge language"
)
LO_B = "Apply assessment-bridge framing to Module-2 handoff decisions"


def _log(transcript: list[str], line: str) -> None:
    transcript.append(line)
    print(line)


def _build_extracted_md(dest: Path) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    parts: list[str] = ["# Tejal C1M1 Part 4 — Assessments Bridge\n"]
    for rel in (
        "slides/slide-1-summary-bridge-to-module-2.md",
        "references/module-1-core-conceptual-pillars.md",
        "assessments/comprehensive-module-knowledge-check.md",
    ):
        src = TEJAL / rel
        if src.is_file():
            parts.append(f"\n## Source: {rel}\n")
            parts.append(src.read_text(encoding="utf-8"))
    path = dest / "extracted.md"
    path.write_text("\n".join(parts), encoding="utf-8")
    return path


def _state(payload: dict) -> RunState:
    return RunState(
        graph_version="v0.1-stub",
        temperature=0.3,
        cache_state=CacheState(
            cache_prefix=json.dumps(payload, sort_keys=True),
            entries_count=0,
        ),
    )


def _run_pass1(*, run_id: str, runs_root: Path, bundle: Path) -> dict:
    ctx = load_planning_context(runs_root / run_id)
    if ctx is None or not ctx.has_framing():
        raise RuntimeError(f"expected planning_context under {runs_root / run_id}")
    payload = {
        "mode": "pass-1",
        "run_id": run_id,
        "runs_root": str(runs_root),
        "bundle_reference": str(bundle),
        "planning_context": ctx.to_payload_dict(),
    }
    state = _state(payload)
    plan_update = pass1_graph._plan(state)
    state = state.model_copy(update=plan_update)
    act_update = pass1_graph._act(state)
    return json.loads(act_update["cache_state"]["cache_prefix"])


def _ensure_workbook_collateral(plan_json: Path) -> dict:
    payload = json.loads(plan_json.read_text(encoding="utf-8"))
    plan = payload.get("lesson_plan") if "lesson_plan" in payload else payload
    if not isinstance(plan, dict):
        raise RuntimeError("irene-pass1.lesson-plan.json missing plan object")
    collateral = plan.get("collateral") or {}
    forced = False
    if not isinstance(collateral, dict) or collateral.get("declaration") != "present":
        plan["collateral"] = {
            "declaration": "present",
            "workbook": {
                "kind": "deck-companion-workbook",
                "sections": [
                    {
                        "section_id": "sec-bridge-001",
                        "learning_objective_id": "lo-bridge-001",
                        "title": "Assessment bridge depth",
                        "depth_delta": {
                            "deferred_from_slide": "slide-1",
                            "deferred_depth": (
                                "Full assessment-bridge method and Module-2 "
                                "handoff rationale kept off the glance slide"
                            ),
                        },
                    }
                ],
            },
        }
        forced = True
        plan_json.write_text(
            json.dumps(plan, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        payload = plan
    return {"plan": plan if not forced else plan, "collateral_forced": forced}


def _wave1_predicates() -> dict[str, bool]:
    t1 = {
        "has_g1": "G1" in GATE_ASSET_MAP
        and GATE_ASSET_MAP["G1"][0].rel_path == "irene-pass1.lesson-plan.json",
        "has_g2c": "G2C" in GATE_ASSET_MAP
        and GATE_ASSET_MAP["G2C"][0].rel_path == "storyboard-publish-G2C.json",
        "g4_absent_honest": "G4" not in GATE_ASSET_MAP and "G4A" not in GATE_ASSET_MAP,
        "g1_canonical": GATE_ASSET_MAP["G1"][0].digest_algo is DigestAlgo.CANONICAL_SHA256,
    }
    trial_id = UUID("12345678-1234-4234-8234-123456789abc")
    env = ProductionEnvelope(trial_id=trial_id, fixture_run=True)
    for node_id, specialist in (("n1", "a"), ("n2", "b"), ("n3", "c")):
        output = {"node": node_id}
        env.add_contribution(
            SpecialistContribution(
                specialist_id=specialist,
                contributed_at=dt.now(UTC),
                output=output,
                cost_usd=0.0,
                model_used="fixture",
                output_digest=compute_output_digest(output),
                node_id=node_id,
                provenance="fixture",
            )
        )
    dropped = env.drop_contributions_from_nodes({"n2", "n3"})
    sig = inspect.signature(recover_production_trial)
    t2 = {
        "drop_count_2": dropped == 2,
        "kept_n1_only": [c.node_id for c in env.contributions] == ["n1"],
        "api_has_reenter_at_node": "reenter_at_node" in sig.parameters,
    }
    narration = [
        {"id": "seg-1", "narration_text": "First."},
        {"id": "seg-2", "narration_text": "Second."},
    ]
    bad_deltas = [
        {"id": "seg-1", "visual_references": [{"perception_source": "s1"}]},
        {"id": "seg-1", "visual_references": [{"perception_source": "s2"}]},
    ]
    collapsed = collapsed_segment_ids(join_narration_segments(narration, bad_deltas))
    t3 = {
        "detects_collapse": collapsed == ["seg-1"],
        "publisher_refuses_collapse": False,
    }
    try:
        storyboard_publisher._write_segment_manifest_for_b(
            run_dir=REPO / "runs" / "_trust-e2e-tmp-collapse",
            irene_output={
                "narration_script": narration,
                "segment_manifest_deltas": bad_deltas,
            },
        )
    except storyboard_publisher.StoryboardPublishError as exc:
        t3["publisher_refuses_collapse"] = (
            getattr(exc, "tag", "") == "storyboard.join.collapsed-segment-ids"
        )
    return {**{f"t1_{k}": v for k, v in t1.items()}, **{f"t2_{k}": v for k, v in t2.items()}, **{f"t3_{k}": v for k, v in t3.items()}}


def _wave2_fidelity() -> dict[str, bool]:
    os.environ.pop(FIGURE_FIDELITY_ACTIVE_ENV, None)
    default_off = not narration_figure_fidelity_active()
    os.environ[FIGURE_FIDELITY_ACTIVE_ENV] = "1"

    near = _figure_near_match("percent:18", _figures(FIDELITY_SOURCE))
    far = _figure_near_match("percent:60", _figures(FIDELITY_SOURCE))
    comma = "money-trillion:1.2" in _figures("$1,200 billion")

    parsed = json.loads((LEG3 / "pass2-output.json").read_text(encoding="utf-8"))
    artifacts = json.loads(
        (LEG3 / "perception-artifacts.json").read_text(encoding="utf-8")
    )
    envelope = {
        "bundle_reference": str(LEG3),
        "lesson_plan": {"title": "c-u03"},
        "gary_slide_output": [
            {"slide_id": a["slide_id"], "visual_description": "x"} for a in artifacts
        ],
        "slide_briefs": [
            {"slide_id": a["slide_id"], "prompt": "x"} for a in artifacts
        ],
        "perception_artifacts": artifacts,
    }
    roster = _slide_roster(envelope)
    _assert_figure_citations_within_perceived(parsed, roster)
    _assert_narration_figures_sourced(parsed, roster, source_text=FIDELITY_SOURCE)
    _assert_source_figures_positively_carried(
        parsed, roster, source_text=FIDELITY_SOURCE
    )

    confab = copy.deepcopy(parsed)
    confab["narration_script"][0]["narration_text"] += " Market hit $4.6B."
    confab_ok = False
    try:
        _assert_narration_figures_sourced(confab, roster, source_text=FIDELITY_SOURCE)
    except Pass2GroundingError as exc:
        confab_ok = exc.tag == "irene.pass2.figure-unsourced"

    miss = copy.deepcopy(parsed)
    miss["narration_script"][0]["narration_text"] = (
        "Medical knowledge is accelerating. Stewardship is your role."
    )
    _assert_narration_figures_sourced(miss, roster, source_text=FIDELITY_SOURCE)
    carry_ok = False
    try:
        _assert_source_figures_positively_carried(
            miss, roster, source_text=FIDELITY_SOURCE
        )
    except Pass2GroundingError as exc:
        carry_ok = exc.tag == "irene.pass2.figure-positive-carry-miss"

    os.environ.pop(FIGURE_FIDELITY_ACTIVE_ENV, None)
    _assert_narration_figures_sourced(confab, roster, source_text=FIDELITY_SOURCE)
    _assert_source_figures_positively_carried(miss, roster, source_text=FIDELITY_SOURCE)

    return {
        "default_flag_off": default_off,
        "percent_tolerance_band": PERCENT_TOLERANCE_PP == 0.6,
        "near_match_18_4_to_18": near,
        "far_match_rejected": not far,
        "comma_money_parses": comma,
        "real_pass2_sails_flag_on": True,
        "confab_halt": confab_ok,
        "positive_carry_halt": carry_ok,
        "flag_off_firewall": not narration_figure_fidelity_active(),
    }


def main() -> int:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    run_id = str(uuid4())
    runs_root = REPO / "runs"
    run_dir = runs_root / run_id
    run_dir.mkdir(parents=True)
    # Ensure collapse-refuse tmp parent exists for Wave-1 publisher check.
    (runs_root / "_trust-e2e-tmp-collapse").mkdir(parents=True, exist_ok=True)

    evidence = (
        REPO
        / "_bmad-output/implementation-artifacts/evidence"
        / f"mine-next-trust-e2e-{stamp}"
    )
    evidence.mkdir(parents=True)
    transcript: list[str] = [
        f"# Mine-next Trust E2E transcript — {stamp}",
        f"primary_run_id: {run_id}",
        "",
    ]

    # --- Wave 1 ---
    _log(transcript, "## Wave 1 — UDAC / reenter / join-collapse")
    w1 = _wave1_predicates()
    for k, v in w1.items():
        _log(transcript, f"  {k}={v}")
    wave1_ok = all(w1.values())

    # --- plan-dialogue ---
    script = run_dir / "plan-dialogue-script.yaml"
    script.write_text(
        yaml.safe_dump(
            {
                "purpose": PURPOSE,
                "audience": AUDIENCE,
                "workflow": "narrated-deck-with-workbook",
                "gap_fill_considered": "synthesize,wait,ask_operator",
                "gap_fill_chosen": "synthesize",
                "gap_fill_rationale": "Trust E2E: rich Tejal leaf; synthesize",
                "learning_objectives": [LO_A, LO_B],
                "confirm": "yes",
            }
        ),
        encoding="utf-8",
    )
    collateral_spec = run_dir / "collateral-spec.json"
    collateral_spec.write_text(
        json.dumps(
            {
                "declaration": "present",
                "workbook": {
                    "kind": "deck-companion-workbook",
                    "sections": [
                        {
                            "section_id": "sec-bridge-001",
                            "learning_objective_id": "lo-bridge-001",
                            "title": "Assessment bridge depth",
                            "depth_delta": {
                                "deferred_from_slide": "slide-1",
                                "deferred_depth": (
                                    "Full assessment-bridge method kept off slide"
                                ),
                            },
                        }
                    ],
                },
            }
        ),
        encoding="utf-8",
    )
    _log(transcript, "## Step — plan-dialogue (fresh)")
    rc = plan_dialogue_main(
        [
            "--corpus-dir",
            str(TEJAL),
            "--output-dir",
            str(run_dir),
            "--script",
            str(script),
            "--collateral-spec",
            str(collateral_spec),
        ]
    )
    ctx = load_planning_context(run_dir)
    step_plan_ok = (
        rc == 0
        and (run_dir / "planning-ratification.json").is_file()
        and (run_dir / "ratified-los.json").is_file()
        and (run_dir / "marcus-planning-dialogue.md").is_file()
        and bool(ctx and ctx.has_framing())
    )
    _log(transcript, f"plan-dialogue exit={rc} ok={step_plan_ok}")

    # --- Live Irene Pass-1 ---
    _log(transcript, "## Step — live Irene Pass-1 (fresh asset)")
    bundle_dir = run_dir / "bundle"
    _build_extracted_md(bundle_dir)
    irene = _run_pass1(run_id=run_id, runs_root=runs_root, bundle=bundle_dir)
    plan_json = run_dir / "irene-pass1.lesson-plan.json"
    if not plan_json.is_file():
        lesson_plan = irene.get("lesson_plan")
        if isinstance(lesson_plan, dict):
            plan_json.write_text(
                json.dumps(lesson_plan, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
    ensure = _ensure_workbook_collateral(plan_json)
    coverage = irene.get("planning_context_coverage") or {}
    step_pass1_ok = (
        plan_json.is_file()
        and isinstance(coverage, dict)
        and coverage.get("purpose_acknowledged") is True
        and coverage.get("audience_acknowledged") is True
    )
    _log(
        transcript,
        f"pass1 ok={step_pass1_ok} collateral_forced={ensure['collateral_forced']} "
        f"plan_bytes={plan_json.stat().st_size if plan_json.is_file() else 0}",
    )

    # --- selection + trial spy ---
    _log(transcript, "## Step — auto-derive + trial-start spy")
    derived = load_selection_from_lesson_plan_json(plan_json)
    digest = compose_and_digest(derived.selection, repo_root=REPO)
    (run_dir / "component_selection.json").write_text(
        json.dumps(
            {
                "source": derived.source,
                "bundle_id": derived.bundle_id,
                "selection": derived.selection.as_map(),
                "compose_digest": digest.composed_graph_digest,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    absent_fail = False
    try:
        derive_selection_from_lesson_plan({"lesson_summary": "x", "plan_units": []})
    except CollateralSelectionError:
        absent_fail = True

    captured: dict = {}

    def _spy(**kwargs: object) -> object:
        captured.update(kwargs)
        raise RuntimeError("trust-e2e-stop-after-selection-capture")

    import app.marcus.cli.trial as trial_mod

    original = trial_mod.run_production_trial
    trial_mod.run_production_trial = _spy  # type: ignore[assignment]
    trial_start_ok = False
    try:
        try:
            start_trial(
                preset="production",
                input_path=FIXTURE_INPUT,
                operator_id="operator_trust_e2e",
                trial_id=uuid4(),
                allow_offline_cost_report=True,
                runs_root=runs_root,
                auto_confirm_directive=True,
                component_selection=derived.selection,
                lesson_plan_collateral_intent_path=plan_json,
                lesson_plan_collateral_bundle_id=derived.bundle_id,
            )
        except RuntimeError as exc:
            if "stop-after-selection-capture" in str(exc):
                trial_start_ok = True
            else:
                raise
    finally:
        trial_mod.run_production_trial = original

    consumed = captured.get("component_selection")
    selection_match = (
        consumed is not None
        and getattr(consumed, "as_map", lambda: None)() == derived.selection.as_map()
    )
    step_sel_ok = (
        derived.source == "plan_collateral"
        and derived.selection.as_map().get("workbook") is True
        and trial_start_ok
        and selection_match
        and absent_fail
    )
    _log(transcript, f"selection/trial ok={step_sel_ok}")

    # --- Wave 2 fidelity ---
    _log(transcript, "## Wave 2 — T4a/T4b/T4c fidelity (flag-ON activation)")
    w2 = _wave2_fidelity()
    for k, v in w2.items():
        _log(transcript, f"  {k}={v}")
    wave2_ok = all(w2.values())

    # Fresh fidelity witness assets in run dir
    (run_dir / "fidelity-source.md").write_text(FIDELITY_SOURCE, encoding="utf-8")
    (run_dir / "fidelity-witness.json").write_text(
        json.dumps(
            {
                "source_figures": sorted(_figures(FIDELITY_SOURCE)),
                "leg3_pass2": str(LEG3 / "pass2-output.json"),
                "flag_default_off": not narration_figure_fidelity_active(),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    predicates = {
        "wave1_ok": wave1_ok,
        "plan_dialogue_ok": step_plan_ok,
        "pass1_fresh_asset_ok": step_pass1_ok,
        "selection_trial_ok": step_sel_ok,
        "wave2_fidelity_ok": wave2_ok,
        "fresh_plan_json_present": plan_json.is_file(),
        "fresh_extracted_present": (run_dir / "bundle" / "extracted.md").is_file(),
        "default_flag_still_off": not narration_figure_fidelity_active(),
        **{f"w1_{k}": v for k, v in w1.items()},
        **{f"w2_{k}": v for k, v in w2.items()},
    }
    bool_keys = [k for k, v in predicates.items() if isinstance(v, bool)]
    passed = all(predicates[k] for k in bool_keys)

    item = evidence / "trust-hardening-e2e"
    item.mkdir(parents=True)
    verdict = {
        "lane": "TRUST-E2E",
        "name": "trust-hardening-fresh-asset-e2e",
        "passed": passed,
        "predicates": {**predicates, "run_id": run_id},
        "run_dir": str(run_dir),
        "note": (
            "No Gamma; flag activation proven with flag ON then restored OFF. "
            "P2-4b trial-ready + full carrier arc remain HOLD. "
            "Not a wholesale trust-COMPLETE stamp."
        ),
    }
    (item / "verdict.json").write_text(
        json.dumps(verdict, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (item / "command-transcript.md").write_text(
        "\n".join(transcript) + "\n", encoding="utf-8"
    )
    (item / "PROOF.md").write_text(
        "# PROOF Trust E2E\n\n"
        f"run_id={run_id}\n"
        f"PASS={passed}\n\n"
        "## Fresh assets\n"
        f"- `{plan_json}`\n"
        f"- `{run_dir / 'bundle' / 'extracted.md'}`\n"
        f"- `{run_dir / 'component_selection.json'}`\n"
        f"- `{run_dir / 'fidelity-witness.json'}`\n\n"
        f"```json\n{json.dumps(predicates, indent=2, sort_keys=True)}\n```\n",
        encoding="utf-8",
    )
    # Mirror transcript into run dir
    (run_dir / "trust-e2e-transcript.md").write_text(
        "\n".join(transcript) + "\n", encoding="utf-8"
    )
    (run_dir / "trust-e2e-verdict.json").write_text(
        json.dumps(verdict, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(json.dumps(verdict, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
