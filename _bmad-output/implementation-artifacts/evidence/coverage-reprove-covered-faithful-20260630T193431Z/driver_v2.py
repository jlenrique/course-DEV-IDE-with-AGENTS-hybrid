"""Coverage interlock COVERED arm — faithful positive-control LIVE walk (option C, CORRECTED).

CORRECTION vs v1: v1 launched run_production_trial WITHOUT directive_path, so Texas node 02
raised `dispatch_retrieval missing required input: directive_path` before G3. This version
AUTHORS the launch directive (source-config; run_id bound to the trial) and passes
directive_path so Texas dispatches. Corpus is FROZEN (NOT re-engineered). First-run-stands;
NO retry-to-green; $0 ElevenLabs (gate evaluated on the real G3 receipt before enrique).
"""
from __future__ import annotations
import json, os, sys, time, traceback
from pathlib import Path
from uuid import UUID, uuid4

REPO = Path(r"C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS-hybrid")
os.environ.pop("OPENAI_API_KEY", None)
from dotenv import load_dotenv
load_dotenv(REPO / ".env", override=True)
assert os.environ.get("OPENAI_API_KEY", "").startswith("sk-"), "live key not loaded"

os.environ["MARCUS_G0_ENRICHMENT_ACTIVE"] = "1"
os.environ["MARCUS_G0_DISPATCH_LIVE"] = "1"
os.environ["MARCUS_COVERAGE_PASS_ACTIVE"] = "1"
os.environ["MARCUS_COVERAGE_GATE_ACTIVE"] = "1"
os.environ.pop("MARCUS_COVERAGE_GATE_PROVISIONAL_OK", None)

def log(*a):
    print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)

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
    note_bearing_content_exists,
)
from app.marcus.lesson_plan.coverage_gate import CoverageAssuranceError
from app.runtime.economics import RUNS_ROOT

CORPUS = REPO / "course-content" / "courses" / "coverage-faithful-probe"
TRIAL_ID = uuid4()
OP = "operator_juan"
WALL_BUDGET_S = 2400.0
t0 = time.time()
gate_seq = []
def elapsed():
    return round(time.time() - t0, 1)

# ---- author the launch directive (the v1 omission); run_id bound to TRIAL_ID ----
SCR = Path(__file__).resolve().parent
DIRECTIVE_PATH = SCR / f"directive-faithful-{TRIAL_ID}.yaml"
_directive = f"""run_id: {TRIAL_ID}
corpus_dir: {CORPUS.as_posix()}
sources:
- ref_id: src-001
  locator: slides/slide-1-why-one-number.md
  provider: local_file
  role: primary
  description: 'Framing slide motivating why a single headline number anchors the lesson.'
  expected_min_words: 50
  excluded_reason: null
- ref_id: src-002
  locator: slides/slide-2-the-70-percent-burnout-figure.md
  provider: local_file
  role: primary
  description: 'Focal slide: the 70% clinician burnout headline figure and its meaning.'
  expected_min_words: 50
  excluded_reason: null
composed_at: '2026-06-30T00:00:00Z'
schema_version: 1
"""
DIRECTIVE_PATH.write_text(_directive, encoding="utf-8")
log(f"wrote directive {DIRECTIVE_PATH}")

log(f"TRIAL_ID={TRIAL_ID}")
log(f"CORPUS={CORPUS}  exists={CORPUS.exists()}")

result = {"trial_id": str(TRIAL_ID), "corpus": str(CORPUS),
          "directive_path": str(DIRECTIVE_PATH), "version": "v2-directive-fix"}
run_dir = RUNS_ROOT / str(TRIAL_ID)
try:
    log("START run_production_trial (deck-only, directive_path SET)...")
    env = run_production_trial(
        corpus_path=CORPUS,
        preset="production",
        operator_id=OP,
        trial_id=TRIAL_ID,
        allow_offline_cost_report=False,
        max_specialist_calls=40,
        directive_path=DIRECTIVE_PATH,
        component_selection=ComponentSelection(deck=True, motion=False, workbook=False),
    )
    log(f"  -> status={env.status} gate={env.paused_gate} [{elapsed()}s]")

    for _ in range(40):
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
        kwargs = dict(trial_id=TRIAL_ID, gate_id=gate,
                      card_id=UUID(card["card"]["card_id"]),
                      operator_id=OP, decision_card_digest=card["digest"], verb="approve")
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
        env = resume_production_trial(trial_id=TRIAL_ID, verdict=OperatorVerdict(**kwargs),
                                      runs_root=RUNS_ROOT, max_specialist_calls=40)
        gate_seq.append({"gate": gate, "verb": kwargs["verb"], "next_status": env.status,
                         "next_gate": env.paused_gate, "seg_s": round(time.time() - seg, 1)})
        log(f"  approved {gate} -> status={env.status} next={env.paused_gate} [{elapsed()}s]")

    result["gate_sequence"] = gate_seq
    result["total_seconds_walk"] = elapsed()

    receipt = load_coverage_receipt_from_disk(run_dir)
    if receipt is None:
        result["receipt_present"] = False
        log("NO RECEIPT on disk -> cannot evaluate gate")
        result.setdefault("VERDICT", "NOT-CONVERGED")
    else:
        result["receipt_present"] = True
        rows = receipt.rows
        from collections import Counter
        status_counts = dict(Counter(r.coverage_status for r in rows))
        joined = [r for r in rows if r.anchor_resolved and r.coverage_status in
                  {"both", "covered_on_slide", "covered_in_narration"}]
        figtok_verified = []
        for r in rows:
            rep = r.r7_report or {}
            if (r.anchor_resolved and r.coverage_status in {"both", "covered_in_narration"}
                    and rep.get("figure_facet") and rep.get("figure_surface_verifiable")
                    and rep.get("source_figs") and not rep.get("dropped_figs")):
                figtok_verified.append({
                    "source_point_id": r.source_point_id, "slide_key": r.slide_key,
                    "coverage_status": r.coverage_status, "must_cover": r.must_cover,
                    "vouch_level": r.vouch_level,
                    "source_figs": rep.get("source_figs"), "surface_figs": rep.get("surface_figs")})
        result["receipt"] = {
            "n_rows": len(rows), "status_counts": status_counts,
            "joined_covered": len(joined),
            "joined_covered_figuretoken_verified": len(figtok_verified),
            "figtok_verified_rows": figtok_verified, "is_vacuous": receipt.is_vacuous(),
            "missing_must_cover": [
                {"source_point_id": r.source_point_id, "slide_key": r.slide_key,
                 "verbatim_required": r.verbatim_required} for r in receipt.missing_must_cover()]}
        log(f"RECEIPT rows={len(rows)} status={status_counts} joined={len(joined)} "
            f"figtok_verified={len(figtok_verified)} vacuous={receipt.is_vacuous()}")
        gate_raised, gate_tag, gate_msg = False, None, None
        try:
            enforce_coverage_gate_before_audio(specialist_id="enrique", run_dir=run_dir)
            log("GATE enforce_coverage_gate_before_audio(enrique) -> DID NOT RAISE (PASS)")
        except CoverageAssuranceError as e:
            gate_raised = True; gate_tag = getattr(e, "tag", None); gate_msg = str(e)
            log(f"GATE RAISED tag={gate_tag} :: {gate_msg[:160]}")
        result["gate"] = {"raised": gate_raised, "tag": gate_tag, "message": gate_msg,
                          "note_bearing_content_exists": note_bearing_content_exists(run_dir)}
        converged = (result.get("walk_outcome") == "reached-G3" and len(rows) > 0
                     and not receipt.is_vacuous() and len(figtok_verified) >= 1 and not gate_raised)
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
out = SCR / "faithful_driver_v2_result.json"
out.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
log(f"WROTE {out}")
log(f"DONE total={elapsed()}s VERDICT={result.get('VERDICT')}")
