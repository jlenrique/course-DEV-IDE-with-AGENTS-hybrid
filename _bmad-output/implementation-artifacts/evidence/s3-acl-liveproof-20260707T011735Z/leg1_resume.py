"""S3 AC-L LEG-1 driver, phase 2: approve G1 and continue the walk to the next
pause gate (G2B), crossing 4.75 CD (fast LLM), 05/05B irene-pass1 (LLM),
06 builder, §07 gary (REAL PAID Gamma deck), 7.5 vera, 07B quinn-r.

Weed-clearing posture: accept-recommended => verb 'approve' at G1.
"""
from __future__ import annotations

import faulthandler
import json
import logging
import os
import sys
import threading
import traceback
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

REPO = Path(r"C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS-hybrid")
EVIDENCE = Path(__file__).resolve().parent
HARD_TIMEOUT_S = 2700  # 45 min hard watchdog: 3 irene LLM jobs + paid Gamma + vera + quinn-r

sys.path.insert(0, str(REPO))
os.chdir(REPO)
os.environ["PYTHONIOENCODING"] = "utf-8"

LOG = open(EVIDENCE / "driver-log-leg1.txt", "a", encoding="utf-8")


def log(msg: str) -> None:
    line = f"[{datetime.now(tz=UTC).isoformat()}] {msg}"
    print(line, flush=True)
    LOG.write(line + "\n")
    LOG.flush()


os.environ.pop("OPENAI_API_KEY", None)
from dotenv import load_dotenv  # noqa: E402

load_dotenv(REPO / ".env", override=True)
os.environ.pop("MARCUS_G0_ENRICHMENT_ACTIVE", None)
key = os.environ.get("OPENAI_API_KEY", "")
assert key.startswith("sk-") and "subst" not in key, "OPENAI_API_KEY sentinel/absent"
assert os.environ.get("GAMMA_API_KEY"), "GAMMA_API_KEY absent"

handler = logging.FileHandler(EVIDENCE / "walk-log-leg1.txt", encoding="utf-8")
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.INFO)

faulthandler.enable(LOG)


def _watchdog() -> None:
    log(f"WATCHDOG TRIPPED at {HARD_TIMEOUT_S}s — dumping stacks, exit 3")
    faulthandler.dump_traceback(LOG)
    LOG.flush()
    os._exit(3)


timer = threading.Timer(HARD_TIMEOUT_S, _watchdog)
timer.daemon = True
timer.start()

from app.marcus.orchestrator.production_runner import resume_production_trial  # noqa: E402
from app.models.state.operator_verdict import OperatorVerdict  # noqa: E402
from app.runtime.economics import RUNS_ROOT  # noqa: E402

state = json.loads((EVIDENCE / "leg1-state.json").read_text(encoding="utf-8"))
TRIAL_ID = UUID(state["trial_id"])
run_dir = RUNS_ROOT / str(TRIAL_ID)
result: dict = {"leg": 1, "phase": "resume", "trial_id": str(TRIAL_ID)}

t0 = datetime.now(tz=UTC)
try:
    card = json.loads((run_dir / "decision-card-G1.json").read_text(encoding="utf-8"))
    verdict = OperatorVerdict(
        trial_id=TRIAL_ID,
        gate_id="G1",
        card_id=UUID(card["card"]["card_id"]),
        operator_id="operator_juan",
        decision_card_digest=card["digest"],
        verb="approve",
    )
    log("G1 verdict: approve (weed-clearing accept-recommended); resuming with cap=40")
    envelope = resume_production_trial(
        trial_id=TRIAL_ID,
        verdict=verdict,
        runs_root=RUNS_ROOT,
        max_specialist_calls=40,
    )
    result["resume_status"] = envelope.status
    result["paused_gate"] = envelope.paused_gate
    result["paused_error_tag"] = envelope.paused_error_tag
    log(f"resume returned: status={envelope.status} paused_gate={envelope.paused_gate} "
        f"paused_error_tag={envelope.paused_error_tag}")
except BaseException:
    log("resume RAISED:\n" + traceback.format_exc())
    result["resume_exception"] = traceback.format_exc()

result["elapsed_s"] = (datetime.now(tz=UTC) - t0).total_seconds()
(EVIDENCE / "leg1-resume-result.json").write_text(
    json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8"
)
ok = result.get("resume_status") == "paused-at-gate"
log(f"=== LEG1 PHASE2 {'OK' if ok else 'NOT-OK'} after {result['elapsed_s']:.0f}s ===")
timer.cancel()
sys.exit(0 if ok else 1)
