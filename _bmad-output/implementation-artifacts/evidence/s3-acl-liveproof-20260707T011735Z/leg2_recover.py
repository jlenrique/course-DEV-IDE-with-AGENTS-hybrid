"""S3 AC-L LEG-2 driver, phase 2: recover the rewound copy at gary@07.

Gary re-dispatches LIVE (second REAL PAID Gamma deck) against the MUTATED
SSOT while CD's retained contribution attests the ORIGINAL bytes -> genuine
same-bytes divergence, WARN log line, dispatch proceeds to the G2B pause.
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
HARD_TIMEOUT_S = 2700

sys.path.insert(0, str(REPO))
os.chdir(REPO)
os.environ["PYTHONIOENCODING"] = "utf-8"

LOG = open(EVIDENCE / "driver-log-leg2.txt", "a", encoding="utf-8")


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

handler = logging.FileHandler(EVIDENCE / "walk-log-leg2.txt", encoding="utf-8")
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

from app.marcus.orchestrator.production_runner import recover_production_trial  # noqa: E402
from app.runtime.economics import RUNS_ROOT  # noqa: E402

state = json.loads((EVIDENCE / "leg2-state.json").read_text(encoding="utf-8"))
TRIAL2 = UUID(state["trial2"])
result: dict = {"leg": 2, "phase": "recover", "trial2": str(TRIAL2)}

t0 = datetime.now(tz=UTC)
try:
    log(f"recover_production_trial({TRIAL2}) with cap=40 — gary re-dispatch vs MUTATED SSOT")
    envelope = recover_production_trial(
        trial_id=TRIAL2,
        runs_root=RUNS_ROOT,
        max_specialist_calls=40,
    )
    result["recover_status"] = envelope.status
    result["paused_gate"] = envelope.paused_gate
    result["paused_error_tag"] = envelope.paused_error_tag
    log(f"recover returned: status={envelope.status} paused_gate={envelope.paused_gate} "
        f"paused_error_tag={envelope.paused_error_tag}")
except BaseException:
    log("recover RAISED:\n" + traceback.format_exc())
    result["recover_exception"] = traceback.format_exc()

result["elapsed_s"] = (datetime.now(tz=UTC) - t0).total_seconds()
(EVIDENCE / "leg2-recover-result.json").write_text(
    json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8"
)
ok = result.get("recover_status") == "paused-at-gate"
log(f"=== LEG2 PHASE2 {'OK' if ok else 'NOT-OK'} after {result['elapsed_s']:.0f}s ===")
timer.cancel()
sys.exit(0 if ok else 1)
