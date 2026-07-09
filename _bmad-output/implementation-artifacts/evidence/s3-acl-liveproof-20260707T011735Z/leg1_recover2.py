"""S3 AC-L LEG-1 driver, phase 4: ONE recover through the FIXED matcher.

Matcher fix committed at 59a9a48a (party-ratified §10 amendment: normalize_title
apostrophe-family deletion; live pair probe-verified). Per the §10 ruling this
is the legitimate error-pause -> recover product path — the frozen judge-1 has
never executed. ONE attempt; the outcome stands.
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
HARD_TIMEOUT_S = 2400

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

from app.marcus.orchestrator.production_runner import recover_production_trial  # noqa: E402
from app.runtime.economics import RUNS_ROOT  # noqa: E402

state = json.loads((EVIDENCE / "leg1-state.json").read_text(encoding="utf-8"))
TRIAL_ID = UUID(state["trial_id"])
result: dict = {
    "leg": 1,
    "phase": "recover-post-matcher-fix",
    "matcher_fix_commit": "59a9a48a",
    "trial_id": str(TRIAL_ID),
}

t0 = datetime.now(tz=UTC)
try:
    log(f"recover_production_trial({TRIAL_ID}) — ONE recover through FIXED matcher "
        "(59a9a48a), cap=40")
    envelope = recover_production_trial(
        trial_id=TRIAL_ID,
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
(EVIDENCE / "leg1-recover2-result.json").write_text(
    json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8"
)
ok = result.get("recover_status") == "paused-at-gate"
log(f"=== LEG1 PHASE4 {'OK' if ok else 'NOT-OK'} after {result['elapsed_s']:.0f}s ===")
timer.cancel()
sys.exit(0 if ok else 1)
