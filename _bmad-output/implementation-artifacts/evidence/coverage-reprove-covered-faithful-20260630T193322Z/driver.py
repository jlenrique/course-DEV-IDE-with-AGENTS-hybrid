"""Coverage interlock COVERED arm — faithful positive-control LIVE walk (option C).

Engineered corpus: course-content/courses/coverage-faithful-probe (single 70% focal slide).
Fresh full walk G0->G3 (live gpt-5 enrichment + gary deck + irene narration), then run the
EXACT runner gate predicate enforce_coverage_gate_before_audio(specialist_id="enrique") on the
real G3 receipt (no ElevenLabs spend). First-run-stands; NO retry-to-green.
"""
from __future__ import annotations
import json, os, sys, time, traceback
from pathlib import Path
from uuid import UUID, uuid4

# ---- live key (dotenv override recipe) ----
REPO = Path(r"C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS-hybrid")
os.environ.pop("OPENAI_API_KEY", None)
from dotenv import load_dotenv
load_dotenv(REPO / ".env", override=True)
assert os.environ.get("OPENAI_API_KEY", "").startswith("sk-"), "live key not loaded"

# ---- interlock flags ----
os.environ["MARCUS_G0_ENRICHMENT_ACTIVE"] = "1"
os.environ["MARCUS_G0_DISPATCH_LIVE"] = "1"
os.environ["MARCUS_COVERAGE_PASS_ACTIVE"] = "1"
os.environ["MARCUS_COVERAGE_GATE_ACTIVE"] = "1"
os.environ.pop("MARCUS_COVERAGE_GATE_PROVISIONAL_OK", None)  # enforcement LIVE

def log(*a):
    print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)

# ---- gpt-5 hard per-request timeout guard (patch adapter.ChatOpenAI) ----
import app.models.adapter as adapter
_Orig = adapter.ChatOpenAI
class _GuardedChat(_Orig):
    def __init__(self, *a, **kw):
        kw.setdefault("timeout", 900.0)
        kw.setdefault("max_retries", 0)
        kw.setdefault("max_tokens", 64000)
        super().__init__(*a, **kw)
adapter.ChatOpenAI = _GuardedChat
log("patched adapter.ChatOpenAI -> timeout=900 max_retries=0 max_tokens=64000")

from app.gates.verdict import OperatorVerdict
from app.models.state.component_selection import ComponentSelection
from app.marcus.orchestrator.production_runner import (
    run_production_trial, resume_production_trial,
)
from app.marcus.orchestrator.coverage_gate_wiring import (
    enforce_coverage_gate_before_audio, load_coverage_receipt_from_disk,
    note_bearing_content_exists, coverage_receipt_path,
)
from app.marcus.lesson_plan.coverage_gate import CoverageAssuranceError
from app.runtime.economics import RUNS_ROOT

CORPUS = REPO / "course-content" / "courses" / "coverage-faithful-probe"
TRIAL_ID = uuid4()
OP = "operator_juan"
WALL_BUDGET_S = 2400.0  # 40 min hard guard
t0 = time.time()
gate_seq = []

def elapsed():
    return round(time.time() - t0, 1)

log(f"TRIAL_ID={TRIAL_ID}")
log(f"CORPUS={CORPUS}  exists={CORPUS.exists()}")

result = {
    "trial_id": str(TRIAL_ID), "corpus": str(CORPUS),
    "flags": {k: os.environ.get(k) for k in
              ["MARCUS_G0_ENRICHMENT_ACTIVE","MARCUS_G0_DISPATCH_LIVE",
               "MARCUS_COVERAGE_PASS_ACTIVE","MARCUS_COVERAGE_GATE_ACTIVE"]},
}
run_dir = RUNS_ROOT / str(TRIAL_ID)
try:
    log("START run_production_trial (deck-only, motion/workbook off)...")
    env = run_production_trial(
        corpus_path=CORPUS,
        preset="production",
        operator_id=OP,
        trial_id=TRIAL_ID,
        allow_offline_cost_report=False,
        max_specialist_calls=40,
        component_selection=ComponentSelection(deck=True, motion=False, workbook=False),
    )
    log(f"  -> status={env.status} gate={env.paused_gate} [{elapsed()}s]")

    # ---- gate-driving loop to G3 ----
    for _ in range(30):
        if time.time() - t0 > WALL_BUDGET_S:
            raise TimeoutError(f"wall budget {WALL_BUDGET_S}s exceeded")
        run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
        status, gate = run.get("status"), run.get("paused_gate")
        log(f"STATE status={status} gate={gate} err={run.get('paused_error_tag')} [{elapsed()}s]")
        if status == "paused-at-error":
            result["walk_outcome"] = "paused-at-error-before-G3"
            result["paused_error_tag"] = run.get("paused_error_tag")
            break
        if status != "paused-at-gate":
            result["walk_outcome"] = f"unexpected-status:{status}"
            break
        if gate == "G3":
            result["walk_outcome"] = "reached-G3"
            break
        card = json.loads((run_dir / f"decision-card-{gate}.json").read_text(encoding="utf-8"))
        kwargs = dict(
            trial_id=TRIAL_ID, gate_id=gate,
            card_id=UUID(card["card"]["card_id"]),
            operator_id=OP, decision_card_digest=card["digest"], verb="approve",
        )
        if gate == "G2B":
            opts = [e for e in card["card"].get("pick_context", [])
                    if e.get("kind") == "variant-options"]
            if opts and opts[0].get("slides"):
                slide_ids = [s["slide_id"] for s in opts[0]["slides"]]
                kwargs["verb"] = "select"
                kwargs["edit_payload"] = {"slide_variant_selections": {s: "A" for s in slide_ids}}
                log(f"  G2B select-all-A for {len(slide_ids)} slides")
            else:
                log("  G2B no variant-options -> plain approve")
        seg = time.time()
        env = resume_production_trial(
            trial_id=TRIAL_ID, verdict=OperatorVerdict(**kwargs),
            runs_root=RUNS_ROOT, max_specialist_calls=40,
        )
        gate_seq.append({"gate": gate, "verb": kwargs["verb"],
                         "next_status": env.status, "next_gate": env.paused_gate,
                         "seg_s": round(time.time() - seg, 1)})
        log(f"  approved {gate} -> status={env.status} next={env.paused_gate} [{elapsed()}s]")

    result["gate_sequence"] = gate_seq
    result["total_seconds_walk"] = elapsed()

    # ---- evaluate the REAL gate predicate at the enrique audio seam ----
    receipt = load_coverage_receipt_from_disk(run_dir)
    if receipt is None:
        result["receipt_present"] = False
        log("NO RECEIPT on disk -> cannot evaluate gate")
    else:
        result["receipt_present"] = True
        rows = receipt.rows
        from collections import Counter
        status_counts = dict(Counter(r.coverage_status for r in rows))
        joined = [r for r in rows if r.anchor_resolved and r.coverage_status in
                  {"both","covered_on_slide","covered_in_narration"}]
        figtok_verified = []
        for r in rows:
            rep = r.r7_report or {}
            if (r.anchor_resolved and r.coverage_status in {"both","covered_in_narration"}
                    and rep.get("figure_facet") and rep.get("figure_surface_verifiable")
                    and rep.get("source_figs") and not rep.get("dropped_figs")):
                figtok_verified.append({
                    "source_point_id": r.source_point_id, "slide_key": r.slide_key,
                    "coverage_status": r.coverage_status, "must_cover": r.must_cover,
                    "vouch_level": r.vouch_level,
                    "source_figs": rep.get("source_figs"), "surface_figs": rep.get("surface_figs"),
                })
        result["receipt"] = {
            "n_rows": len(rows), "status_counts": status_counts,
            "joined_covered": len(joined),
            "joined_covered_figuretoken_verified": len(figtok_verified),
            "figtok_verified_rows": figtok_verified,
            "is_vacuous": receipt.is_vacuous(),
            "missing_must_cover": [
                {"source_point_id": r.source_point_id, "slide_key": r.slide_key,
                 "verbatim_required": r.verbatim_required}
                for r in receipt.missing_must_cover()
            ],
        }
        log(f"RECEIPT rows={len(rows)} status={status_counts} joined={len(joined)} "
            f"figtok_verified={len(figtok_verified)} vacuous={receipt.is_vacuous()}")

        # THE GATE: identical to the runner's pre-enrique-dispatch interlock
        gate_raised, gate_tag, gate_msg = False, None, None
        try:
            enforce_coverage_gate_before_audio(specialist_id="enrique", run_dir=run_dir)
            log("GATE enforce_coverage_gate_before_audio(enrique) -> DID NOT RAISE (PASS)")
        except CoverageAssuranceError as e:
            gate_raised = True
            gate_tag = getattr(e, "tag", None)
            gate_msg = str(e)
            log(f"GATE RAISED tag={gate_tag} :: {gate_msg[:160]}")
        result["gate"] = {
            "raised": gate_raised, "tag": gate_tag, "message": gate_msg,
            "note_bearing_content_exists": note_bearing_content_exists(run_dir),
        }

        # ---- deterministic judge ----
        converged = (
            result["walk_outcome"] == "reached-G3"
            and len(rows) > 0
            and not receipt.is_vacuous()
            and len(figtok_verified) >= 1
            and not gate_raised
        )
        result["VERDICT"] = "CONVERGED" if converged else "NOT-CONVERGED"
        log(f"VERDICT={result['VERDICT']}")
except Exception as e:  # noqa: BLE001
    result["exception"] = f"{type(e).__name__}: {e}"
    result["traceback"] = traceback.format_exc()
    result.setdefault("VERDICT", "NOT-CONVERGED")
    log(f"EXCEPTION {type(e).__name__}: {e}")
    log(traceback.format_exc())

result["run_dir"] = str(run_dir)
result["total_seconds"] = elapsed()
out = REPO / "_bmad-output" / "implementation-artifacts" / "evidence" / "_faithful_driver_result.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
log(f"WROTE {out}")
log(f"DONE total={elapsed()}s VERDICT={result.get('VERDICT')}")
