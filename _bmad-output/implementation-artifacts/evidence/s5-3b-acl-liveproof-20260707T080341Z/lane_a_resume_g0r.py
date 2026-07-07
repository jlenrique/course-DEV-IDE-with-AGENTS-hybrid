"""S5-3b AC-L lane (a) — RESUME G0R (approve/ratify) via the real runner resume path.

Reads the persisted decision-card-G0R.json, builds an approve OperatorVerdict, and
resumes; the next pause must be G1 (canonical G0E->G0R->G1 complete).
"""
from __future__ import annotations

import faulthandler
import json
import os
import sys
import threading
import traceback
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

REPO = Path(r"C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS-hybrid")
EVIDENCE = Path(__file__).resolve().parent
GATE = "G0R"
EXPECT_NEXT = "G1"
LANE = "a"
HARD_TIMEOUT_S = 900

sys.path.insert(0, str(REPO))
os.chdir(REPO)
os.environ["PYTHONIOENCODING"] = "utf-8"
LOG = open(EVIDENCE / f"driver-log-lane-{LANE}.txt", "a", encoding="utf-8")


def log(msg: str) -> None:
    line = f"[{datetime.now(tz=UTC).isoformat()}] {msg}"
    print(line, flush=True)
    LOG.write(line + "\n")
    LOG.flush()


os.environ.pop("OPENAI_API_KEY", None)
from dotenv import load_dotenv  # noqa: E402

load_dotenv(REPO / ".env", override=True)
os.environ.pop("MARCUS_G0_ENRICHMENT_ACTIVE", None)
os.environ.pop("MARCUS_G0_DISPATCH_LIVE", None)
key = os.environ.get("OPENAI_API_KEY", "")
assert key.startswith("sk-") and "subst" not in key
assert os.environ.get("GAMMA_API_KEY")

faulthandler.enable(LOG)


def _watchdog() -> None:
    log(f"WATCHDOG TRIPPED at {HARD_TIMEOUT_S}s — exit 3")
    faulthandler.dump_traceback(LOG)
    LOG.flush()
    os._exit(3)


timer = threading.Timer(HARD_TIMEOUT_S, _watchdog)
timer.daemon = True
timer.start()

from app.marcus.orchestrator.production_runner import resume_production_trial  # noqa: E402
from app.models.state.operator_verdict import OperatorVerdict  # noqa: E402
from app.runtime.economics import RUNS_ROOT  # noqa: E402

state = json.loads((EVIDENCE / f"lane_{LANE}-state.json").read_text(encoding="utf-8"))
TRIAL_ID = UUID(state["trial_id"])
run_dir = RUNS_ROOT / str(TRIAL_ID)
result: dict = {"lane": LANE, "phase": f"resume-{GATE}", "trial_id": str(TRIAL_ID), "verdict_gate": GATE}

t0 = datetime.now(tz=UTC)
try:
    card = json.loads((run_dir / f"decision-card-{GATE}.json").read_text(encoding="utf-8"))
    verdict = OperatorVerdict(
        trial_id=TRIAL_ID,
        gate_id=GATE,
        card_id=UUID(card["card"]["card_id"]),
        operator_id="operator_juan",
        decision_card_digest=card["digest"],
        verb="approve",
    )
    log(f"{GATE} verdict: approve (ratify LOs); resuming with cap=12")
    envelope = resume_production_trial(
        trial_id=TRIAL_ID, verdict=verdict, runs_root=RUNS_ROOT, max_specialist_calls=12
    )
    result["resume_status"] = envelope.status
    result["paused_gate"] = envelope.paused_gate
    result["paused_error_tag"] = envelope.paused_error_tag
    log(f"resume returned: status={envelope.status} paused_gate={envelope.paused_gate} err={envelope.paused_error_tag}")
except BaseException:
    log("resume RAISED:\n" + traceback.format_exc())
    result["resume_exception"] = traceback.format_exc()

result["elapsed_s"] = (datetime.now(tz=UTC) - t0).total_seconds()
(EVIDENCE / f"lane_{LANE}-resume-g0r-result.json").write_text(
    json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8"
)
ok = result.get("resume_status") == "paused-at-gate" and result.get("paused_gate") == EXPECT_NEXT
log(f"=== LANE-{LANE} RESUME {GATE} {'OK' if ok else 'NOT-OK'} paused_gate={result.get('paused_gate')} ===")
timer.cancel()
sys.exit(0 if ok else 1)
