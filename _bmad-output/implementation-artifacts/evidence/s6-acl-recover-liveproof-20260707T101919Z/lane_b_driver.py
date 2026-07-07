"""S6 AC-L RECOVER lane (b) driver — honest creds-absent degrade ($0) + R1.

Same walk as lane (a) but Scite Bearer forced ABSENT via the sanctioned
SCITE_OAUTH_TOKEN_PATH override pointed at a NONEXISTENT file, so
load_bearer_token() -> None -> _scite_creds_present() -> False. With the D7 flip
default-ON and research_goals present, node 04.55 hits the D4 creds-precondition
at run_research_wiring ENTRY and records a VISIBLE recorded-empty degrade envelope
(no dispatch, $0, walk proceeds).

BONUS R1: restore the real Bearer (pop the override), re-verify creds present, and
RE-INVOKE run_research_wiring on the real DEGRADED envelope with dispatch_live=True
— proving the degrade contribution FALLS THROUGH the idempotency guard and
re-dispatches (research_entries non-empty) instead of being stuck. R1 intentionally
spends ~1 Scite dispatch (the core lane-b degrade is $0-Scite).
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
from uuid import UUID, uuid4

REPO = Path(r"C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS-hybrid")
EVIDENCE = Path(__file__).resolve().parent
CORPUS = REPO / "course-content/courses/tejal-apc-c1-m1-p2-trends"
OPERATOR = "operator_juan"
HARD_TIMEOUT_S = 1500
NONEXISTENT_TOKEN = EVIDENCE / "no-such-scite-token-forced-absent.json"

sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "skills" / "bmad-agent-texas" / "scripts"))
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
os.environ.pop("MARCUS_G0_DISPATCH_LIVE", None)
os.environ.pop("MARCUS_G0_ENRICHMENT_ACTIVE", None)
env_dispatch_present = os.environ.get("MARCUS_RESEARCH_DISPATCH_LIVE") is not None
assert not env_dispatch_present, "MARCUS_RESEARCH_DISPATCH_LIVE must be ABSENT by name (default-ON witness)"
key = os.environ.get("OPENAI_API_KEY", "")
assert key.startswith("sk-") and "subst" not in key, "OPENAI_API_KEY sentinel/absent"

# --- FORCE creds absent (sanctioned override → nonexistent token file) ---
assert not NONEXISTENT_TOKEN.exists(), "forced-absent token path must not exist"
os.environ["SCITE_OAUTH_TOKEN_PATH"] = str(NONEXISTENT_TOKEN)

from app.marcus.orchestrator.production_runner import (  # noqa: E402
    _research_dispatch_live,
    resume_production_trial,
)
from app.marcus.orchestrator.research_wiring import (  # noqa: E402
    DeterministicPostureSelector,
    RESEARCH_DEGRADE_KEY,
    RESEARCH_ENTRIES_KEY,
    RESEARCH_WIRING_NODE_ID,
    RESEARCH_WIRING_SPECIALIST_ID,
    _scite_creds_present,
    run_research_wiring,
)

dispatch_fn = _research_dispatch_live()
creds_absent = _scite_creds_present()
log(f"env: dispatch_live_fn={dispatch_fn} creds_present(forced-absent)={creds_absent}")
assert dispatch_fn is True, "flip did not take"
assert creds_absent is False, "creds not forced absent — override failed"

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

from app.marcus.cli.marcus_spoc import narrate_research_result  # noqa: E402
from app.marcus.cli.trial import start_trial  # noqa: E402
from app.models.state.operator_verdict import OperatorVerdict  # noqa: E402
from app.runtime.economics import RUNS_ROOT  # noqa: E402

TRIAL_ID = uuid4()
run_dir = RUNS_ROOT / str(TRIAL_ID)
pause_sequence: list[str] = []
facts: dict = {
    "lane": "b",
    "trial_id": str(TRIAL_ID),
    "run_dir": str(run_dir),
    "corpus": str(CORPUS),
    "research_dispatch_live_fn": dispatch_fn,
    "scite_creds_present": creds_absent,
    "forced_absent_token_path": str(NONEXISTENT_TOKEN),
    "minted_at": datetime.now(tz=UTC).isoformat(),
}


def read_run() -> dict:
    p = run_dir / "run.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def approve(gate: str, cap: int):
    card = json.loads((run_dir / f"decision-card-{gate}.json").read_text(encoding="utf-8"))
    verdict = OperatorVerdict(
        trial_id=TRIAL_ID,
        gate_id=gate,
        card_id=UUID(card["card"]["card_id"]),
        operator_id=OPERATOR,
        decision_card_digest=card["digest"],
        verb="approve",
    )
    log(f"resume: approve {gate} (cap={cap})")
    env = resume_production_trial(
        trial_id=TRIAL_ID, verdict=verdict, runs_root=RUNS_ROOT, max_specialist_calls=cap
    )
    log(f"  -> status={env.status} paused_gate={env.paused_gate} err={env.paused_error_tag}")
    return env


try:
    log(f"trial_id={TRIAL_ID}; START on tejal (creds FORCED absent; expect first pause G0E)")
    start_trial(
        preset="production",
        input_path=CORPUS,
        operator_id=OPERATOR,
        trial_id=TRIAL_ID,
        auto_confirm_directive=True,
        max_specialist_calls=8,
    )
    run = read_run()
    pause_sequence.append(run.get("paused_gate"))
    log(f"START paused at {run.get('paused_gate')} (status={run.get('status')})")

    env = None
    for _ in range(8):
        run = read_run()
        status, gate = run.get("status"), run.get("paused_gate")
        if status != "paused-at-gate" or not gate:
            log(f"stop drive: status={status} gate={gate}")
            break
        cap = 12 if gate in {"G0R", "G1"} else 8
        env = approve(gate, cap)
        nxt = env.paused_gate
        if nxt:
            pause_sequence.append(nxt)
        prod = getattr(env, "production_envelope", None)
        contrib = prod.get_contribution(RESEARCH_WIRING_SPECIALIST_ID, node_id=RESEARCH_WIRING_NODE_ID) if prod else None
        if contrib is not None:
            log(f"research_wiring contribution PRESENT after approving up to {gate}; now paused {nxt}")
            break
        if env.status == "paused-at-error":
            log(f"ERROR-PAUSE at {env.paused_gate} tag={env.paused_error_tag}")
            break

    facts["pause_sequence"] = pause_sequence
    run = read_run()
    facts["final_status"] = run.get("status")
    facts["final_paused_gate"] = run.get("paused_gate")
    facts["final_error_tag"] = run.get("paused_error_tag")

    prod = getattr(env, "production_envelope", None) if env else None
    contrib = prod.get_contribution(RESEARCH_WIRING_SPECIALIST_ID, node_id=RESEARCH_WIRING_NODE_ID) if prod else None
    degraded_env = prod  # keep a handle for R1

    if contrib is None:
        log("NO research_wiring contribution at 04.55")
        facts["research_entries_present"] = False
    else:
        out = contrib.output
        entries = out.get(RESEARCH_ENTRIES_KEY)
        facts["research_entries_present"] = RESEARCH_ENTRIES_KEY in out
        facts["research_entries"] = entries
        degrade = out.get(RESEARCH_DEGRADE_KEY)
        facts["research_degrade"] = degrade
        # dispatch_reached: independent of the degrade flag — no cited entries were
        # minted (degrade path returns BEFORE _dispatch_intents_to_texas).
        facts["dispatch_reached"] = bool(entries)
        # $0 Scite: the degrade path never calls the Scite adapter. Recorded 0
        # BECAUSE the degrade envelope provably short-circuited before dispatch.
        facts["scite_spend"] = 0 if (isinstance(degrade, dict) and degrade.get("degraded")) else -1
        narration = narrate_research_result(out)
        facts["narration_line"] = narration
        log(f"DEGRADE narration: {narration}")

    # --- BONUS R1 — restore creds, re-invoke node 04.55 on the DEGRADED envelope ---
    try:
        os.environ.pop("SCITE_OAUTH_TOKEN_PATH", None)  # restore real Bearer path
        creds_restored = _scite_creds_present()
        log(f"R1: creds restored -> _scite_creds_present()={creds_restored}")
        r1: dict = {"attempted": True, "creds_restored": creds_restored}
        if creds_restored and degraded_env is not None:
            updated = run_research_wiring(
                node_id=RESEARCH_WIRING_NODE_ID,
                production_envelope=degraded_env,
                posture_selector=DeterministicPostureSelector(),
                dispatch_live=True,
            )
            new_contrib = updated.get_contribution(
                RESEARCH_WIRING_SPECIALIST_ID, node_id=RESEARCH_WIRING_NODE_ID
            )
            new_entries = (new_contrib.output.get(RESEARCH_ENTRIES_KEY) or []) if new_contrib else []
            r1["redispatched"] = len(new_entries) >= 1
            r1["entries_count"] = len(new_entries)
            if new_entries:
                r1["primary_doi"] = new_entries[0].get("source_id")
                r1["primary_source_ref"] = new_entries[0].get("source_ref")
                r1["primary_title"] = new_entries[0].get("title")
            log(f"R1: re-dispatch entries={len(new_entries)} primary_doi={r1.get('primary_doi')}")
        else:
            r1["redispatched"] = False
            r1["entries_count"] = 0
        facts["r1_redispatch"] = r1
    except Exception:  # noqa: BLE001
        facts["r1_redispatch"] = {"attempted": True, "error": traceback.format_exc()}
        log("R1 RAISED:\n" + traceback.format_exc())

except BaseException:
    log("lane-b driver RAISED:\n" + traceback.format_exc())
    facts["driver_exception"] = traceback.format_exc()

(EVIDENCE / "lane_b-facts.json").write_text(json.dumps(facts, indent=2, default=str) + "\n", encoding="utf-8")
log(f"=== LANE-b facts written: degrade={bool(facts.get('research_degrade'))} "
    f"dispatch_reached={facts.get('dispatch_reached')} final_gate={facts.get('final_paused_gate')} "
    f"r1={facts.get('r1_redispatch', {}).get('redispatched')} ===")
timer.cancel()
sys.exit(0)
