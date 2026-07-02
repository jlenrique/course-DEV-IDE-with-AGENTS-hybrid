"""Resume the T2 treatment run (4289ffb7) at G1 and capture the floored Pass-1 outputs."""
from __future__ import annotations
import json, os, sys, time, traceback
from pathlib import Path
from uuid import UUID

REPO = Path(r"C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS-hybrid")
sys.path.insert(0, str(REPO))
os.environ.pop("OPENAI_API_KEY", None)
from dotenv import load_dotenv
load_dotenv(REPO / ".env", override=True)
assert os.environ.get("OPENAI_API_KEY", "").startswith("sk-"), "live key not loaded"
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

from app.gates.verdict import OperatorVerdict
from app.marcus.orchestrator.production_runner import resume_production_trial
from app.specialists.irene_pass1.cluster_floor import GROUPING_KEYS  # noqa: F401 (import sanity)
from app.runtime.economics import RUNS_ROOT

SCR = Path(__file__).resolve().parent
TRIAL_ID = UUID("4289ffb7-030c-467c-9bcc-a4bae0adab3f")
OP = "operator_juan"
t0 = time.time()
run_dir = RUNS_ROOT / str(TRIAL_ID)
result = {"trial_id": str(TRIAL_ID), "arm": "treatment-T2", "floor_n": 8}
try:
    card = json.loads((run_dir / "decision-card-G1.json").read_text(encoding="utf-8"))
    env = resume_production_trial(
        trial_id=TRIAL_ID,
        verdict=OperatorVerdict(trial_id=TRIAL_ID, gate_id="G1",
                                card_id=UUID(card["card"]["card_id"]), operator_id=OP,
                                decision_card_digest=card["digest"], verb="approve"),
        runs_root=RUNS_ROOT, max_specialist_calls=40)
    log(f"approved G1 -> {env.status} [{round(time.time()-t0,1)}s]")
    run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    result["final_status"] = run.get("status")
    result["final_error_tag"] = run.get("paused_error_tag")
    contribs = (run.get("production_envelope") or {}).get("contributions") or []
    ip1 = [c for c in contribs if (c.get("specialist_id") or "") == "irene_pass1"]
    analysis = {}
    for c in ip1:
        node = c.get("node_id")
        (SCR / f"t2-irene_pass1-{node}-output-verbatim.json").write_text(
            json.dumps(c.get("output"), indent=2, sort_keys=True, default=str), encoding="utf-8")
        lp = (c.get("output") or {}).get("lesson_plan") or {}
        units = lp.get("plan_units") or []
        heads = [u for u in units if isinstance(u, dict) and u.get("cluster_role") == "head"]
        ids = sorted({u.get("cluster_id") for u in units if isinstance(u, dict) and u.get("cluster_id")})
        analysis[node] = {
            "n_plan_units": len(units),
            "n_distinct_cluster_ids": len(ids),
            "minted_ids": [i for i in ids if "#f" in str(i)],
            "units_with_floor_subdivision_index": [u.get("unit_id") for u in units
                                                   if isinstance(u, dict) and "floor_subdivision_index" in u],
            "units_with_source_refs": sum(1 for u in units if isinstance(u, dict)
                                          and isinstance(u.get("source_refs"), list) and u["source_refs"]),
            "n_heads": len(heads),
        }
    result["analysis"] = analysis
    latest = analysis.get("05B") or analysis.get("05") or {}
    result["count_T"] = latest.get("n_distinct_cluster_ids")
    result["anti_vacuous_pass"] = bool(result.get("count_T") and result["count_T"] >= 8)
    result["floor_fired"] = bool(latest.get("minted_ids"))
    result["VERDICT"] = "CAPTURED" if result.get("count_T") is not None else "NOT-CONVERGED"
except Exception as e:  # noqa: BLE001
    result["exception"] = f"{type(e).__name__}: {e}"
    result["traceback"] = traceback.format_exc()
    result.setdefault("VERDICT", "NOT-CONVERGED")
    log(traceback.format_exc())

result["total_seconds"] = round(time.time() - t0, 1)
(SCR / "result-treatment-t2.json").write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
log(f"DONE {result['total_seconds']}s VERDICT={result.get('VERDICT')} count_T={result.get('count_T')} "
    f"floor_fired={result.get('floor_fired')} minted={((result.get('analysis') or {}).get('05B') or {}).get('minted_ids')}")
