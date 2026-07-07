"""S5-3b AC-L lane (b) driver — phase START (armed live-LLM, content-armed).

Arms the REAL production switch MARCUS_G0_DISPATCH_LIVE=1 (the value the
`--g0-dispatch-live` CLI flag resolves to) with a real OpenAI key, so the G0E
pre-pass dispatches a genuine LIVE LLM component-extraction call. First pause is
still G0E (structure identical to lane (a)); the receipt stamps `live`.
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
HARD_TIMEOUT_S = 900  # extra headroom: one live gpt-5 extraction call

sys.path.insert(0, str(REPO))
os.chdir(REPO)
os.environ["PYTHONIOENCODING"] = "utf-8"
LOG = open(EVIDENCE / "driver-log-lane-b.txt", "a", encoding="utf-8")


def log(msg: str) -> None:
    line = f"[{datetime.now(tz=UTC).isoformat()}] {msg}"
    print(line, flush=True)
    LOG.write(line + "\n")
    LOG.flush()


os.environ.pop("OPENAI_API_KEY", None)
from dotenv import load_dotenv  # noqa: E402

load_dotenv(REPO / ".env", override=True)
# lane (b): default enrichment (unset -> ON), but ARM the live production switch.
os.environ.pop("MARCUS_G0_ENRICHMENT_ACTIVE", None)
os.environ["MARCUS_G0_DISPATCH_LIVE"] = "1"  # the value the --g0-dispatch-live CLI flag sets
env_enrichment_present = os.environ.get("MARCUS_G0_ENRICHMENT_ACTIVE") is not None
env_dispatch_present = os.environ.get("MARCUS_G0_DISPATCH_LIVE") is not None
assert not env_enrichment_present, "MARCUS_G0_ENRICHMENT_ACTIVE must be ABSENT (default-witness)"
assert env_dispatch_present, "MARCUS_G0_DISPATCH_LIVE must be SET (armed lane)"
key = os.environ.get("OPENAI_API_KEY", "")
assert key.startswith("sk-") and "subst" not in key, "OPENAI_API_KEY sentinel/absent"
assert os.environ.get("GAMMA_API_KEY"), "GAMMA_API_KEY absent"
assert os.environ.get("LANGSMITH_API_KEY") and os.environ.get("LANGSMITH_PROJECT")

from app.marcus.orchestrator.g0_enrichment_wiring import (  # noqa: E402
    g0_dispatch_live,
    g0_enrichment_active,
)
from app.marcus.orchestrator.production_runner import _has_live_openai  # noqa: E402

active_fn = g0_enrichment_active()
dispatch_fn = g0_dispatch_live()
has_live = _has_live_openai()
log(f"fns: g0_enrichment_active()={active_fn} g0_dispatch_live()={dispatch_fn} _has_live_openai()={has_live}")
assert active_fn is True and dispatch_fn is True and has_live is True, "armed live gates not all True"

# Introspect the REAL model the 'marcus' seam resolves to (read-only; no call).
resolved_marcus_model = None
requested_marcus_model = None
try:
    from app.models.adapter import make_chat_model

    handle = make_chat_model("marcus")
    resolved_marcus_model = handle.entry.resolved
    requested_marcus_model = handle.entry.requested
    log(f"marcus seam resolves: requested={requested_marcus_model!r} resolved={resolved_marcus_model!r}")
except Exception as exc:  # noqa: BLE001
    log(f"marcus-model introspection failed (non-fatal): {exc!r}")

handler = logging.FileHandler(EVIDENCE / "walk-log-lane-b.txt", encoding="utf-8")
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
    "lane": "b",
    "phase": "start",
    "trial_id": str(TRIAL_ID),
    "run_dir": str(run_dir),
    "corpus": str(CORPUS),
    "env_g0_enrichment_active_present": env_enrichment_present,
    "env_g0_dispatch_live_present": env_dispatch_present,
    "g0_enrichment_active_fn": active_fn,
    "g0_dispatch_live_fn": dispatch_fn,
    "has_live_openai": has_live,
    "resolved_marcus_model": resolved_marcus_model,
    "requested_marcus_model": requested_marcus_model,
    "minted_at": datetime.now(tz=UTC).isoformat(),
}
(EVIDENCE / "lane_b-state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
log(f"trial_id={TRIAL_ID}; starting ARMED live trial on studio-smoke-min DIR (expect first pause G0E, live receipt)")

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
log(f"start_trial returned after {elapsed:.0f}s")

paused_gate = None
start_status = None
run_json = run_dir / "run.json"
if run_json.is_file():
    env = json.loads(run_json.read_text(encoding="utf-8"))
    paused_gate = env.get("paused_gate")
    start_status = env.get("status")

contribution_output_keys = None
receipt_model_id = None
receipt_mode = None
receipt = run_dir / "g0-enrichment.json"
if receipt.is_file():
    r = json.loads(receipt.read_text(encoding="utf-8"))
    contribution_output_keys = sorted(r.keys())
    rb = r.get("g0_enrichment_result") or r
    receipt_model_id = rb.get("model_id")
    receipt_mode = r.get("enrichment_mode")

state.update(
    {
        "start_status": start_status,
        "cli_masked_status": (result or {}).get("status"),
        "paused_gate": paused_gate,
        "start_elapsed_s": elapsed,
        "start_result": result,
        "contribution_output_keys": contribution_output_keys,
        "receipt_model_id": receipt_model_id,
        "receipt_mode": receipt_mode,
    }
)
(EVIDENCE / "lane_b-start-result.json").write_text(
    json.dumps(state, indent=2, default=str) + "\n", encoding="utf-8"
)
ok = start_status == "paused-at-gate" and paused_gate == "G0E" and receipt_mode == "live"
log(f"=== LANE-b START {'OK (paused G0E, live receipt)' if ok else 'NOT-OK'} paused_gate={paused_gate} mode={receipt_mode} ===")
timer.cancel()
sys.exit(0 if ok else 1)
