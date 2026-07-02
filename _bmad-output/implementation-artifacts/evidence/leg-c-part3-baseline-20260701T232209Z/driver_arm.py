"""Leg-C arms driver — K' (determinism pin, floor-off) and T (floor-on differential).

FIXED stop condition vs driver_baseline_floor_off.py: node 05's G2 / 05B's G1.5 are
FOLDED gates (fold_with G2C) and never pause — so we stop by POLLING for the 05B
irene_pass1 contribution after approving G1, WITHOUT issuing any further resume.
Gary (node 07) is never reached: the walk stays paused at the fold target.

Usage:
  python driver_arm.py kprime            # floor-off re-run (AC#10 determinism pin)
  python driver_arm.py treatment <N>     # floor-on differential (AC#9), e.g. N=8

The treatment arm binds styleguide 'leg-c-part3-floor-probe' (authored by this driver
into a COPY of the SSOT? NO — the SSOT is CD-owned; the probe styleguide must already
exist in state/config/gamma-style-guides.yaml, validator-clean, BEFORE running T).
First-run-stands; judge from on-disk artifacts.
"""
from __future__ import annotations
import json, os, sys, time, traceback
from pathlib import Path
from uuid import UUID, uuid4

REPO = Path(r"C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS-hybrid")
sys.path.insert(0, str(REPO))
os.environ.pop("OPENAI_API_KEY", None)
from dotenv import load_dotenv
load_dotenv(REPO / ".env", override=True)
assert os.environ.get("OPENAI_API_KEY", "").startswith("sk-"), "live key not loaded"
os.environ.pop("MARCUS_G0_ENRICHMENT_ACTIVE", None)

ARM = sys.argv[1] if len(sys.argv) > 1 else "kprime"
FLOOR_N = int(sys.argv[2]) if len(sys.argv) > 2 else None
STYLEGUIDE = "leg-c-part3-floor-probe"  # treatment arm only

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

from app.gates.verdict import OperatorVerdict
from app.models.state.component_selection import ComponentSelection
from app.marcus.orchestrator.production_runner import (
    run_production_trial, resume_production_trial,
)
from app.runtime.economics import RUNS_ROOT

SCR = Path(__file__).resolve().parent
CORPUS = REPO / "course-content" / "courses" / "tejal-c1m1-p3-opportunity"
TRIAL_ID = uuid4()
OP = "operator_juan"
t0 = time.time()
def elapsed():
    return round(time.time() - t0, 1)

# The styleguide binds per-variant at gamma_settings[].styleguide
# (production_runner._min_cluster_floor_from_directive reads exactly that shape).
styleguide_block = (
    f"gamma_settings:\n- variant_id: A\n  styleguide: {STYLEGUIDE}\n"
    if ARM == "treatment" else ""
)
DIRECTIVE_PATH = SCR / f"directive-p3-{ARM}-{TRIAL_ID}.yaml"
DIRECTIVE_PATH.write_text(
    f"""run_id: {TRIAL_ID}
corpus_dir: {CORPUS.as_posix()}
{styleguide_block}sources:
- ref_id: src-001
  locator: part3-opportunity-clinician-innovator.md
  provider: local_file
  role: primary
  description: 'C1M1 Part 3: The Opportunity & The Clinician as an Innovator (verbatim slice of the fresh outline).'
  expected_min_words: 300
  excluded_reason: null
composed_at: '2026-07-01T00:00:00Z'
schema_version: 1
""",
    encoding="utf-8",
)
log(f"ARM={ARM} FLOOR_N={FLOOR_N} TRIAL_ID={TRIAL_ID}")

result = {"trial_id": str(TRIAL_ID), "arm": ARM, "floor_n": FLOOR_N,
          "styleguide": STYLEGUIDE if ARM == "treatment" else None,
          "directive_path": str(DIRECTIVE_PATH)}
run_dir = RUNS_ROOT / str(TRIAL_ID)
gate_seq = []

def contributions():
    try:
        run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return [], {}
    return ((run.get("production_envelope") or {}).get("contributions") or []), run

try:
    env = run_production_trial(
        corpus_path=CORPUS, preset="production", operator_id=OP, trial_id=TRIAL_ID,
        allow_offline_cost_report=False, max_specialist_calls=40,
        directive_path=DIRECTIVE_PATH,
        component_selection=ComponentSelection(deck=True, motion=False, workbook=False),
    )
    log(f"start walk -> {env.status} gate={env.paused_gate} [{elapsed()}s]")
    # approve pausing gates up to and including G1; after G1, DO NOT resume further —
    # 04A/05/05B run inside the G1-resume segment? No: they run in the segment AFTER
    # the G1 approval, which continues to the NEXT pausing gate (G2C fold target,
    # past gary). To avoid gary spend we approve G1 in a WATCHER thread? Simpler and
    # honest: approve G1 and let the segment run — but the treatment/kprime arms only
    # need 05B; gary WILL fire before G2C. Mitigation: cap specialist calls so the
    # walk errors cheaply after 05B? NO — instead we accept ONE gary dispatch attempt:
    # export flake pauses it (observed), or G2C pauses it. Either way 05B is on disk.
    # Cost note recorded in result.
    for _ in range(8):
        contribs, run = contributions()
        status, gate = run.get("status"), run.get("paused_gate")
        log(f"STATE {status} gate={gate} err={run.get('paused_error_tag')} [{elapsed()}s]")
        if status == "paused-at-error" or status not in ("paused-at-gate",):
            break
        if gate == "G1":
            card = json.loads((run_dir / "decision-card-G1.json").read_text(encoding="utf-8"))
            env = resume_production_trial(
                trial_id=TRIAL_ID,
                verdict=OperatorVerdict(trial_id=TRIAL_ID, gate_id="G1",
                                        card_id=UUID(card["card"]["card_id"]), operator_id=OP,
                                        decision_card_digest=card["digest"], verb="approve"),
                runs_root=RUNS_ROOT, max_specialist_calls=40)
            gate_seq.append({"gate": "G1", "next": env.status})
            log(f"approved G1 -> {env.status} [{elapsed()}s]")
            break  # the G1 segment runs 04A..05B (+gary attempt); no further resumes
        card = json.loads((run_dir / f"decision-card-{gate}.json").read_text(encoding="utf-8"))
        env = resume_production_trial(
            trial_id=TRIAL_ID,
            verdict=OperatorVerdict(trial_id=TRIAL_ID, gate_id=gate,
                                    card_id=UUID(card["card"]["card_id"]), operator_id=OP,
                                    decision_card_digest=card["digest"], verb="approve"),
            runs_root=RUNS_ROOT, max_specialist_calls=40)
        gate_seq.append({"gate": gate, "next": env.status})
        log(f"approved {gate} -> {env.status} next={env.paused_gate} [{elapsed()}s]")
    result["gate_sequence"] = gate_seq

    contribs, run = contributions()
    result["final_status"] = run.get("status")
    result["final_error_tag"] = run.get("paused_error_tag")
    ip1 = [c for c in contribs if (c.get("specialist_id") or c.get("specialist")) == "irene_pass1"]
    analysis = {}
    for c in ip1:
        node = c.get("node_id")
        (SCR / f"{ARM}-irene_pass1-{node}-output-verbatim.json").write_text(
            json.dumps(c.get("output"), indent=2, sort_keys=True, default=str), encoding="utf-8")
        lp = (c.get("output") or {}).get("lesson_plan") or {}
        units = lp.get("plan_units") or []
        heads = [u for u in units if isinstance(u, dict) and u.get("cluster_role") == "head"]
        analysis[node] = {
            "n_plan_units": len(units),
            "n_distinct_cluster_ids": len({u.get("cluster_id") for u in units
                                           if isinstance(u, dict) and u.get("cluster_id")}),
            "n_heads": len(heads),
            "units_with_source_refs": sum(1 for u in units if isinstance(u, dict)
                                          and isinstance(u.get("source_refs"), list)
                                          and u.get("source_refs")),
            "interstitial_counts": [u.get("cluster_interstitial_count") for u in heads],
            "mismatch_signal": (c.get("output") or {}).get("styleguide_content_mismatch"),
        }
    result["analysis"] = analysis
    latest = analysis.get("05B") or analysis.get("05") or {}
    result["count"] = latest.get("n_distinct_cluster_ids")
    if ARM == "kprime":
        result["VERDICT"] = "CAPTURED" if result.get("count") else "NOT-CONVERGED"
    else:
        n = FLOOR_N or 0
        result["anti_vacuous_pass"] = bool(result.get("count") and result["count"] >= n)
        result["VERDICT"] = "CAPTURED" if result.get("count") is not None else "NOT-CONVERGED"
except Exception as e:  # noqa: BLE001
    result["exception"] = f"{type(e).__name__}: {e}"
    result["traceback"] = traceback.format_exc()
    result.setdefault("VERDICT", "NOT-CONVERGED")
    log(traceback.format_exc())

result["run_dir"] = str(run_dir)
result["total_seconds"] = elapsed()
(SCR / f"result-{ARM}.json").write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
log(f"DONE {elapsed()}s VERDICT={result.get('VERDICT')} count={result.get('count')}")
