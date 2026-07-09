"""S5-3b AC-L lane (a) driver — phase START (the FLIP proof, deterministic).

Starts a REAL trial on the studio-smoke-min corpus DIRECTORY with the DEFAULT env
(MARCUS_G0_ENRICHMENT_ACTIVE proven ABSENT by exact name AFTER dotenv load — F-1804),
MARCUS_G0_DISPATCH_LIVE unset (deterministic lane). Post-flip the FIRST pause must be
G0E, not G1. $0 live-LLM on the G0 pre-pass (deterministic recorded).
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
CORPUS = REPO / "course-content/courses/studio-smoke-min"
OPERATOR = "operator_juan"
HARD_TIMEOUT_S = 600

sys.path.insert(0, str(REPO))
os.chdir(REPO)
os.environ["PYTHONIOENCODING"] = "utf-8"
LOG = open(EVIDENCE / "driver-log-lane-a.txt", "a", encoding="utf-8")


def log(msg: str) -> None:
    line = f"[{datetime.now(tz=UTC).isoformat()}] {msg}"
    print(line, flush=True)
    LOG.write(line + "\n")
    LOG.flush()


# --- env: pop the sk-subst sentinel; .env wins; PROVE the default is UNSET ---
os.environ.pop("OPENAI_API_KEY", None)
from dotenv import load_dotenv  # noqa: E402

load_dotenv(REPO / ".env", override=True)
# F-1804: assert ABSENT by exact name AFTER dotenv (prove default unset->ON, not a set value)
os.environ.pop("MARCUS_G0_ENRICHMENT_ACTIVE", None)
os.environ.pop("MARCUS_G0_DISPATCH_LIVE", None)
env_enrichment_present = os.environ.get("MARCUS_G0_ENRICHMENT_ACTIVE") is not None
env_dispatch_present = os.environ.get("MARCUS_G0_DISPATCH_LIVE") is not None
assert not env_enrichment_present, "MARCUS_G0_ENRICHMENT_ACTIVE must be ABSENT (default-witness)"
assert not env_dispatch_present, "MARCUS_G0_DISPATCH_LIVE must be unset (deterministic lane)"
key = os.environ.get("OPENAI_API_KEY", "")
assert key.startswith("sk-") and "subst" not in key, "OPENAI_API_KEY sentinel/absent"
assert os.environ.get("GAMMA_API_KEY"), "GAMMA_API_KEY absent"
assert os.environ.get("LANGSMITH_API_KEY") and os.environ.get("LANGSMITH_PROJECT")

from app.marcus.orchestrator.g0_enrichment_wiring import (  # noqa: E402
    g0_dispatch_live,
    g0_enrichment_active,
)

active_fn = g0_enrichment_active()
dispatch_fn = g0_dispatch_live()
log(f"env: enrichment_active_ABSENT={not env_enrichment_present} dispatch_live_unset={not env_dispatch_present}")
log(f"fns: g0_enrichment_active()={active_fn} g0_dispatch_live()={dispatch_fn}")
assert active_fn is True, "flip did not take: g0_enrichment_active() is not True with unset env"
assert dispatch_fn is False, "dispatch_live must be False in lane (a)"

handler = logging.FileHandler(EVIDENCE / "walk-log-lane-a.txt", encoding="utf-8")
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
from app.runtime.economics import RUNS_ROOT  # noqa: E402

TRIAL_ID = uuid4()
run_dir = RUNS_ROOT / str(TRIAL_ID)
state = {
    "lane": "a",
    "phase": "start",
    "trial_id": str(TRIAL_ID),
    "run_dir": str(run_dir),
    "corpus": str(CORPUS),
    "env_g0_enrichment_active_present": env_enrichment_present,
    "env_g0_dispatch_live_present": env_dispatch_present,
    "g0_enrichment_active_fn": active_fn,
    "g0_dispatch_live_fn": dispatch_fn,
    "minted_at": datetime.now(tz=UTC).isoformat(),
}
(EVIDENCE / "lane_a-state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
log(f"trial_id={TRIAL_ID}; starting REAL trial on studio-smoke-min DIR (auto-confirm, expect first pause G0E)")

t0 = datetime.now(tz=UTC)
try:
    result = start_trial(
        preset="production",
        input_path=CORPUS,
        operator_id=OPERATOR,
        trial_id=TRIAL_ID,
        auto_confirm_directive=True,
        max_specialist_calls=8,
    )
except BaseException:
    log("start_trial RAISED:\n" + traceback.format_exc())
    state["start_exception"] = traceback.format_exc()
    result = None
elapsed = (datetime.now(tz=UTC) - t0).total_seconds()
log(f"start_trial returned after {elapsed:.0f}s: {json.dumps(result, default=str) if result else 'EXCEPTION'}")

# read the persisted envelope for the AUTHORITATIVE status + paused_gate. The CLI
# result dict masks envelope.status to "registered-offline" whenever
# production_clone_launch_evidence is False (true at an EARLY gate like G0E, before
# any specialist dispatch emits a LangSmith child-run trace) — so the authoritative
# walk state must come from the persisted envelope, not the CLI dict.
paused_gate = None
start_status = None
run_json = run_dir / "run.json"
if run_json.is_file():
    env = json.loads(run_json.read_text(encoding="utf-8"))
    paused_gate = env.get("paused_gate")
    start_status = env.get("status")
cli_status = (result or {}).get("status")

# carrier shape + receipt model id (divergence-guard inputs)
contribution_output_keys = None
receipt_model_id = None
receipt = run_dir / "g0-enrichment.json"
if receipt.is_file():
    r = json.loads(receipt.read_text(encoding="utf-8"))
    contribution_output_keys = sorted(r.keys())
    rb = r.get("g0_enrichment_result") or r
    receipt_model_id = rb.get("model_id")

state.update(
    {
        "start_status": start_status,
        "cli_masked_status": cli_status,
        "paused_gate": paused_gate,
        "start_elapsed_s": elapsed,
        "start_result": result,
        "contribution_output_keys": contribution_output_keys,
        "receipt_model_id": receipt_model_id,
    }
)
(EVIDENCE / "lane_a-start-result.json").write_text(
    json.dumps(state, indent=2, default=str) + "\n", encoding="utf-8"
)
ok = start_status == "paused-at-gate" and paused_gate == "G0E"
log(f"=== LANE-a START {'OK (paused at G0E)' if ok else 'NOT-OK'} paused_gate={paused_gate} ===")
timer.cancel()
sys.exit(0 if ok else 1)
