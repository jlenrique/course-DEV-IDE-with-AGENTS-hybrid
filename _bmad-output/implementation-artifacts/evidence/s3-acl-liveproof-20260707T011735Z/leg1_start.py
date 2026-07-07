"""S3 AC-L LEG-1 driver, phase 1: REAL trial start via the S2 scripted path.

Mints trial_id + selection code (build_selection_code), starts the trial with
--selection-code semantics (start_trial(selection_code=...)) and
auto_confirm_directive=True (the CLI's non-interactive mechanics). REAL spend:
G0 directive composition LLM + start-walk specialists to the G1 pause.
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
from uuid import uuid4

REPO = Path(r"C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS-hybrid")
EVIDENCE = Path(__file__).resolve().parent
CORPUS = REPO / "course-content/courses/tejal-apc-c1-m1-p2-trends"
GUIDE = "hil-2026-apc-crossroads-classic"
OPERATOR = "operator_juan"
HARD_TIMEOUT_S = 540  # phase-1 watchdog (S2 start took 179s)

sys.path.insert(0, str(REPO))
os.chdir(REPO)
os.environ["PYTHONIOENCODING"] = "utf-8"

LOG = open(EVIDENCE / "driver-log-leg1.txt", "a", encoding="utf-8")


def log(msg: str) -> None:
    line = f"[{datetime.now(tz=UTC).isoformat()}] {msg}"
    print(line, flush=True)
    LOG.write(line + "\n")
    LOG.flush()


# env override (sk-subst sentinel gotcha): drop shell value, .env wins
os.environ.pop("OPENAI_API_KEY", None)
from dotenv import load_dotenv  # noqa: E402

load_dotenv(REPO / ".env", override=True)
os.environ.pop("MARCUS_G0_ENRICHMENT_ACTIVE", None)  # first pause must be G1
key = os.environ.get("OPENAI_API_KEY", "")
assert key.startswith("sk-") and "subst" not in key, "OPENAI_API_KEY sentinel/absent"
assert os.environ.get("GAMMA_API_KEY"), "GAMMA_API_KEY absent"
assert os.environ.get("LANGSMITH_API_KEY") and os.environ.get("LANGSMITH_PROJECT")
log(f"env loaded: OPENAI_API_KEY={key[:8]}...{key[-4:]} (len {len(key)}); GAMMA+LANGSMITH present")

# capture the walk's log stream (INFO+) for the evidence pack
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

from app.marcus.cli.trial import start_trial  # noqa: E402
from app.marcus.orchestrator.picker_html_emitter import build_selection_code  # noqa: E402

TRIAL_ID = uuid4()
CODE = build_selection_code(TRIAL_ID.hex, {"A": GUIDE})
state = {
    "leg": 1,
    "trial_id": str(TRIAL_ID),
    "run_tag": TRIAL_ID.hex,
    "selection_code": CODE,
    "guide": GUIDE,
    "minted_at": datetime.now(tz=UTC).isoformat(),
}
# state written BEFORE the walk: binds the judge input pre-result
(EVIDENCE / "leg1-state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
log(f"trial_id={TRIAL_ID} run_tag={TRIAL_ID.hex}")
log(f"selection code (pre-minted): {CODE}")

log("=== start_trial (REAL: scripted --selection-code path, auto-confirm, walk to G1) ===")
t0 = datetime.now(tz=UTC)
try:
    result = start_trial(
        preset="production",
        input_path=CORPUS,
        operator_id=OPERATOR,
        trial_id=TRIAL_ID,
        selection_code=CODE,
        auto_confirm_directive=True,
        max_specialist_calls=8,
    )
except BaseException:
    log("start_trial RAISED:\n" + traceback.format_exc())
    state["start_exception"] = traceback.format_exc()
    result = None
elapsed = (datetime.now(tz=UTC) - t0).total_seconds()
log(f"start_trial returned after {elapsed:.0f}s: {json.dumps(result, default=str) if result else 'EXCEPTION'}")
state["start_result"] = result
state["start_elapsed_s"] = elapsed
(EVIDENCE / "leg1-start-result.json").write_text(
    json.dumps(state, indent=2, default=str) + "\n", encoding="utf-8"
)
ok = bool(result) and result.get("status") == "paused-at-gate"
log(f"=== LEG1 PHASE1 {'OK (paused at gate)' if ok else 'NOT-OK'} ===")
timer.cancel()
sys.exit(0 if ok else 1)
