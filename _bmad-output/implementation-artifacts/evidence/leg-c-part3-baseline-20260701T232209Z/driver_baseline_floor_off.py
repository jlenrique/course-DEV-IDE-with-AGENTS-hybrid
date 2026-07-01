"""Leg-C D1 LIVE PART-3 BASELINE — floor-off control (party-ratified 2026-07-01).

Runs the REAL production walk (run_production_trial) over the Part-3 corpus with NO
styleguide bound (floor-off), weed-clearing approves G0/G0A/G0B/G1, STOPS at G2, and
captures both irene_pass1 contributions (04A creation + 05 refinement) VERBATIM.

Party-binding validity conditions (Murat all-four + condition-5 + Winston-iii):
  (a) real adapter payload assembly (it IS the production walk);
  (b) real make_chat_model binding (no stub);
  (c) corpus staged exactly as node 04A stages it (texas extraction -> bundle);
  (d) FIRST-RUN-STANDS — no retry-to-green; a surprising K is data;
  (5) zero-floor-leak assert: "min_cluster_floor" must appear NOWHERE in the run dir;
  (iii) raw model output captured verbatim into this evidence dir.
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
# Default-run posture: G0-enrichment flag NOT set (party evidence: default OFF).
os.environ.pop("MARCUS_G0_ENRICHMENT_ACTIVE", None)

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
from app.runtime.economics import RUNS_ROOT

SCR = Path(__file__).resolve().parent
CORPUS = REPO / "course-content" / "courses" / "tejal-c1m1-p3-opportunity"
TRIAL_ID = uuid4()
OP = "operator_juan"
WALL_BUDGET_S = 2400.0
APPROVE_GATES = {"G0", "G0A", "G0B", "G1"}
STOP_GATE = "G2"
t0 = time.time()
def elapsed():
    return round(time.time() - t0, 1)

DIRECTIVE_PATH = SCR / f"directive-p3-baseline-{TRIAL_ID}.yaml"
DIRECTIVE_PATH.write_text(
    f"""run_id: {TRIAL_ID}
corpus_dir: {CORPUS.as_posix()}
sources:
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
log(f"TRIAL_ID={TRIAL_ID}")
log(f"CORPUS={CORPUS} exists={CORPUS.exists()}")

result = {"trial_id": str(TRIAL_ID), "corpus": str(CORPUS), "arm": "floor-off-control",
          "directive_path": str(DIRECTIVE_PATH)}
run_dir = RUNS_ROOT / str(TRIAL_ID)
gate_seq = []
try:
    log("START run_production_trial (deck-only, floor-off)...")
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
    for _ in range(12):
        if time.time() - t0 > WALL_BUDGET_S:
            raise TimeoutError(f"wall budget {WALL_BUDGET_S}s exceeded")
        run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
        status, gate = run.get("status"), run.get("paused_gate")
        log(f"STATE status={status} gate={gate} err={run.get('paused_error_tag')} [{elapsed()}s]")
        if status == "paused-at-error":
            result["walk_outcome"] = "paused-at-error"
            result["paused_error_tag"] = run.get("paused_error_tag")
            break
        if status != "paused-at-gate":
            result["walk_outcome"] = f"unexpected-status:{status}"
            break
        if gate == STOP_GATE:
            result["walk_outcome"] = f"reached-{STOP_GATE}"
            break
        if gate not in APPROVE_GATES:
            result["walk_outcome"] = f"unexpected-gate:{gate}"
            break
        card = json.loads((run_dir / f"decision-card-{gate}.json").read_text(encoding="utf-8"))
        seg = time.time()
        env = resume_production_trial(
            trial_id=TRIAL_ID,
            verdict=OperatorVerdict(
                trial_id=TRIAL_ID, gate_id=gate, card_id=UUID(card["card"]["card_id"]),
                operator_id=OP, decision_card_digest=card["digest"], verb="approve",
            ),
            runs_root=RUNS_ROOT, max_specialist_calls=40,
        )
        gate_seq.append({"gate": gate, "next_status": env.status,
                         "next_gate": env.paused_gate, "seg_s": round(time.time() - seg, 1)})
        log(f"  approved {gate} -> {env.status} next={env.paused_gate} [{elapsed()}s]")
    result["gate_sequence"] = gate_seq

    # ---- capture irene_pass1 contributions VERBATIM (Winston-iii) ----
    run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    contribs = (run.get("production_envelope") or {}).get("contributions") or []
    ip1 = [c for c in contribs if (c.get("specialist_id") or c.get("specialist")) == "irene_pass1"]
    result["irene_pass1_nodes"] = [c.get("node_id") for c in ip1]
    analysis = {}
    _MEMBER_KEYS = ("source_points", "components", "beats", "members", "points", "segments")
    for c in ip1:
        node = c.get("node_id")
        (SCR / f"irene_pass1-{node}-output-verbatim.json").write_text(
            json.dumps(c.get("output"), indent=2, sort_keys=True, default=str), encoding="utf-8")
        lp = (c.get("output") or {}).get("lesson_plan") or {}
        units = lp.get("plan_units") or []
        cluster_ids = [u.get("cluster_id") for u in units if isinstance(u, dict)]
        heads = [u for u in units if isinstance(u, dict) and u.get("cluster_role") == "head"]
        member_key_hits = sorted({k for u in units if isinstance(u, dict)
                                  for k in u.keys() if k in _MEMBER_KEYS})
        role_tag_hits = sorted({k for u in units if isinstance(u, dict)
                                for k in u.keys() if k in ("kind", "type", "role_tag")})
        analysis[node] = {
            "n_plan_units": len(units),
            "n_distinct_cluster_ids": len(set(filter(None, cluster_ids))),
            "n_heads": len(heads),
            "unit_field_union": sorted({k for u in units if isinstance(u, dict) for k in u}),
            "member_key_hits": member_key_hits,
            "role_tag_hits": role_tag_hits,
            "interstitial_counts": [u.get("cluster_interstitial_count") for u in heads],
            "titles": [u.get("title") for u in units if isinstance(u, dict)],
        }
    result["analysis"] = analysis
    latest = analysis.get("05") or analysis.get("04A") or {}
    result["count_K"] = latest.get("n_distinct_cluster_ids")

    # ---- Murat condition 5: zero-floor-leak assert over the ENTIRE run dir ----
    leak_hits = []
    for p in run_dir.rglob("*"):
        if p.is_file():
            try:
                if "min_cluster_floor" in p.read_text(encoding="utf-8", errors="ignore"):
                    leak_hits.append(str(p.relative_to(run_dir)))
            except OSError:
                pass
    result["floor_leak_hits"] = leak_hits
    result["zero_floor_leak"] = not leak_hits
    result["VERDICT"] = ("BASELINE-CAPTURED"
                         if result.get("walk_outcome") == f"reached-{STOP_GATE}"
                         and result.get("count_K") and not leak_hits
                         else "NOT-CONVERGED")
except Exception as e:  # noqa: BLE001
    result["exception"] = f"{type(e).__name__}: {e}"
    result["traceback"] = traceback.format_exc()
    result.setdefault("VERDICT", "NOT-CONVERGED")
    log(traceback.format_exc())

result["run_dir"] = str(run_dir)
result["total_seconds"] = elapsed()
(SCR / "result.json").write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
log(f"DONE total={elapsed()}s VERDICT={result.get('VERDICT')} count_K={result.get('count_K')}")
