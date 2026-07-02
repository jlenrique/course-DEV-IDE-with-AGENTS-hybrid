"""DIAGNOSTIC (not proof evidence): instrument the floor threading in a live resume walk.

Wraps _runner_payload_for_specialist to log (specialist_id, directive_path, result)
per dispatch, and halts gary BEFORE any Gamma call (SpecialistDispatchError) so the
walk error-pauses right after 05B with zero paid Gamma spend. LLM spend: the normal
texas/irene_pass1/cd calls (~$0.35). Purpose: find where the treatment arm lost the
min_cluster_floor payload.
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

def log(*a):
    print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)

import app.models.adapter as adapter_mod
_Orig = adapter_mod.ChatOpenAI
class _GuardedChat(_Orig):
    def __init__(self, *a, **kw):
        kw.setdefault("timeout", 900.0)
        kw.setdefault("max_retries", 0)
        kw.setdefault("max_tokens", 64000)
        super().__init__(*a, **kw)
adapter_mod.ChatOpenAI = _GuardedChat

import app.marcus.orchestrator.production_runner as pr
from app.specialists.dispatch_errors import SpecialistDispatchError

PAYLOAD_LOG: list[dict] = []
_orig_payload_fn = pr._runner_payload_for_specialist
def _instrumented(*, specialist_id, directive_path, bundle_dir, **kw):
    res = _orig_payload_fn(specialist_id=specialist_id, directive_path=directive_path,
                           bundle_dir=bundle_dir, **kw)
    entry = {"specialist_id": specialist_id,
             "directive_path": str(directive_path) if directive_path else None,
             "result_keys": sorted(res.keys()) if isinstance(res, dict) else None,
             "min_cluster_floor": (res or {}).get("min_cluster_floor") if isinstance(res, dict) else None}
    PAYLOAD_LOG.append(entry)
    log("PAYLOAD-CALL", json.dumps(entry))
    return res
pr._runner_payload_for_specialist = _instrumented

# Halt gary pre-Gamma: diagnostic only — zero paid Gamma spend.
import app.specialists.gary.graph as gary_graph
class _DiagnosticHalt(SpecialistDispatchError):
    def __init__(self):
        super().__init__("diagnostic-halt before any Gamma call", tag="diagnostic.gary-halt")
def _halt(*a, **kw):
    raise _DiagnosticHalt()
for attr in ("_act", "act"):
    if hasattr(gary_graph, attr):
        setattr(gary_graph, attr, _halt)
        log(f"gary {attr} -> diagnostic halt")
        break

from app.gates.verdict import OperatorVerdict
from app.models.state.component_selection import ComponentSelection
from app.runtime.economics import RUNS_ROOT

SCR = Path(__file__).resolve().parent
CORPUS = REPO / "course-content" / "courses" / "tejal-c1m1-p3-opportunity"
TRIAL_ID = uuid4()
OP = "operator_juan"
STYLEGUIDE = "leg-c-part3-floor-probe"
t0 = time.time()

DIRECTIVE_PATH = SCR / f"directive-p3-diag-{TRIAL_ID}.yaml"
DIRECTIVE_PATH.write_text(
    f"""run_id: {TRIAL_ID}
corpus_dir: {CORPUS.as_posix()}
gamma_settings:
- variant_id: A
  styleguide: {STYLEGUIDE}
sources:
- ref_id: src-001
  locator: part3-opportunity-clinician-innovator.md
  provider: local_file
  role: primary
  description: 'C1M1 Part 3 diagnostic threading run.'
  expected_min_words: 300
  excluded_reason: null
composed_at: '2026-07-01T00:00:00Z'
schema_version: 1
""",
    encoding="utf-8",
)
log(f"DIAG TRIAL_ID={TRIAL_ID}")
result = {"trial_id": str(TRIAL_ID), "arm": "diagnostic-threading"}
run_dir = RUNS_ROOT / str(TRIAL_ID)
try:
    env = pr.run_production_trial(
        corpus_path=CORPUS, preset="production", operator_id=OP, trial_id=TRIAL_ID,
        allow_offline_cost_report=False, max_specialist_calls=40,
        directive_path=DIRECTIVE_PATH,
        component_selection=ComponentSelection(deck=True, motion=False, workbook=False),
    )
    log(f"start walk -> {env.status} gate={env.paused_gate} [{round(time.time()-t0,1)}s]")
    for _ in range(8):
        run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
        status, gate = run.get("status"), run.get("paused_gate")
        log(f"STATE {status} gate={gate} err={run.get('paused_error_tag')}")
        if status != "paused-at-gate":
            break
        card = json.loads((run_dir / f"decision-card-{gate}.json").read_text(encoding="utf-8"))
        env = pr.resume_production_trial(
            trial_id=TRIAL_ID,
            verdict=OperatorVerdict(trial_id=TRIAL_ID, gate_id=gate,
                                    card_id=UUID(card["card"]["card_id"]), operator_id=OP,
                                    decision_card_digest=card["digest"], verb="approve"),
            runs_root=RUNS_ROOT, max_specialist_calls=40)
        log(f"approved {gate} -> {env.status} next={env.paused_gate}")
        if gate == "G1":
            break
    run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    result["final_status"] = run.get("status")
    result["final_error_tag"] = run.get("paused_error_tag")
except Exception as e:  # noqa: BLE001
    result["exception"] = f"{type(e).__name__}: {e}"
    log(traceback.format_exc())

result["payload_log"] = PAYLOAD_LOG
result["run_dir"] = str(run_dir)
(SCR / "result-diag-threading.json").write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
log("DONE", json.dumps({k: v for k, v in result.items() if k != 'payload_log'}, default=str)[:200])
log("PAYLOAD_LOG entries:", len(PAYLOAD_LOG))
for e in PAYLOAD_LOG:
    log("  ", json.dumps(e))
