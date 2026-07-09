"""S3 AC-L LEG-1 driver, phase 3: ONE documented `trial recover` after the
gamma.export.brief-unmatched error pause at gary@07.

POLICY (declared BEFORE this ran; see PROOF.md): the paused error is Gamma
title-slug live variance UPSTREAM of the judged parity surface — the parity
receipt is computed at the resolve site BEFORE dispatch and is deterministic
given directive+SSOT+CD block (all unchanged). `trial recover` is the
production system's own designed verb for this pause family
(app/specialists/gary/_act.py:1222 "Recoverable family: error-pause +
`trial recover` retries"). ONE attempt only; a second same-class failure
stands as the leg-1 result.
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
result: dict = {"leg": 1, "phase": "recover-after-brief-unmatched", "trial_id": str(TRIAL_ID)}

t0 = datetime.now(tz=UTC)
try:
    log(f"recover_production_trial({TRIAL_ID}) — SINGLE documented retry of the "
        "gamma.export.brief-unmatched live-variance pause (cap=40)")
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
(EVIDENCE / "leg1-recover-result.json").write_text(
    json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8"
)
ok = result.get("recover_status") == "paused-at-gate"
log(f"=== LEG1 PHASE3 {'OK' if ok else 'NOT-OK'} after {result['elapsed_s']:.0f}s ===")
timer.cancel()
sys.exit(0 if ok else 1)
