"""S6 AC-L lane (a) driver — real cited resolvable-DOI row (the M-wit).

One process: start trial on tejal-apc-c1-m1-p2-trends -> pause G0E -> approve
(G0R) -> approve (G1) -> approve G1 -> continuation runs node 04.55 which fires a
REAL Scite dispatch (default-ON, creds present) -> pause at the next gate (G2B).
Captures the research_wiring contribution, resolves the primary DOI via doi.org,
invokes the real narrate_research_result (the SPOC D5 surface), emits lane_a-facts.json.

Env: MARCUS_RESEARCH_DISPATCH_LIVE proven UNSET by exact name (default-ON flip);
MARCUS_G0_DISPATCH_LIVE UNSET (G0 stays deterministic to save cost); real sk- key
+ Scite Bearer token live.
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

sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "skills" / "bmad-agent-texas" / "scripts"))
os.chdir(REPO)
os.environ["PYTHONIOENCODING"] = "utf-8"
LOG = open(EVIDENCE / "driver-log-lane-a.txt", "a", encoding="utf-8")


def log(msg: str) -> None:
    line = f"[{datetime.now(tz=UTC).isoformat()}] {msg}"
    print(line, flush=True)
    LOG.write(line + "\n")
    LOG.flush()


# --- env: pop sk- sentinel; .env wins; PROVE dispatch default UNSET by name ---
os.environ.pop("OPENAI_API_KEY", None)
from dotenv import load_dotenv  # noqa: E402

load_dotenv(REPO / ".env", override=True)
# keep G0 deterministic (save cost); research dispatch stays DEFAULT (unset)
os.environ.pop("MARCUS_G0_DISPATCH_LIVE", None)
os.environ.pop("MARCUS_G0_ENRICHMENT_ACTIVE", None)
env_dispatch_present = os.environ.get("MARCUS_RESEARCH_DISPATCH_LIVE") is not None
assert not env_dispatch_present, "MARCUS_RESEARCH_DISPATCH_LIVE must be ABSENT by name (default-ON witness)"
key = os.environ.get("OPENAI_API_KEY", "")
assert key.startswith("sk-") and "subst" not in key, "OPENAI_API_KEY sentinel/absent"
assert os.environ.get("GAMMA_API_KEY"), "GAMMA_API_KEY absent"

from app.marcus.orchestrator.production_runner import (  # noqa: E402
    _research_dispatch_live,
    resume_production_trial,
)
from app.marcus.orchestrator.research_wiring import (  # noqa: E402
    RESEARCH_WIRING_NODE_ID,
    RESEARCH_WIRING_SPECIALIST_ID,
    _scite_creds_present,
)
from retrieval.provider_directory import list_providers  # noqa: E402

dispatch_fn = _research_dispatch_live()
creds = _scite_creds_present()
ready = sorted(p.id for p in list_providers(shape="retrieval") if p.status in {"ready", "stub"})
log(f"env: MARCUS_RESEARCH_DISPATCH_LIVE absent-by-name={not env_dispatch_present}")
log(f"fns: _research_dispatch_live()={dispatch_fn} _scite_creds_present()={creds} ready={ready}")
assert dispatch_fn is True, "flip did not take: _research_dispatch_live() not True with unset env"
assert creds is True, "Scite bearer creds absent — lane (a) requires live creds"

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

from app.marcus.cli.marcus_spoc import narrate_research_result  # noqa: E402
from app.marcus.cli.trial import start_trial  # noqa: E402
from app.models.state.operator_verdict import OperatorVerdict  # noqa: E402
from app.runtime.economics import RUNS_ROOT  # noqa: E402

TRIAL_ID = uuid4()
run_dir = RUNS_ROOT / str(TRIAL_ID)
pause_sequence: list[str] = []
facts: dict = {
    "lane": "a",
    "trial_id": str(TRIAL_ID),
    "run_dir": str(run_dir),
    "corpus": str(CORPUS),
    "env_dispatch_live_present_by_name": env_dispatch_present,
    "research_dispatch_live_fn": dispatch_fn,
    "scite_creds_present": creds,
    "ready_providers": ready,
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
    log(f"trial_id={TRIAL_ID}; START on tejal-apc-c1-m1-p2-trends (expect first pause G0E)")
    t0 = datetime.now(tz=UTC)
    start_trial(
        preset="production",
        input_path=CORPUS,
        operator_id=OPERATOR,
        trial_id=TRIAL_ID,
        auto_confirm_directive=True,
        max_specialist_calls=8,
    )
    run = read_run()
    g = run.get("paused_gate")
    pause_sequence.append(g)
    log(f"START paused at {g} (status={run.get('status')}) after {(datetime.now(tz=UTC)-t0).total_seconds():.0f}s")

    # Drive the canonical gate chain to the continuation walk that reaches 04.55.
    # Approve whatever gate we pause at until we get PAST 04.55 (research contrib
    # appears) or hit an error. Guard against runaway with a bounded loop.
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
        # after this resume, is the research contribution present yet?
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
    if contrib is None:
        log("NO research_wiring contribution — corpus yielded no in-scope research gap OR walk did not reach 04.55")
        facts["research_contribution_present"] = False
    else:
        out = contrib.output
        facts["research_contribution_present"] = True
        facts["research_contribution_node_id"] = getattr(contrib, "node_id", None) or RESEARCH_WIRING_NODE_ID
        entries = out.get("research_entries") or []
        facts["research_entries"] = entries
        facts["entries_count"] = len(entries)
        l2 = out.get("l2_citation_report")
        facts["l2_citation_report"] = l2
        facts["citation_manifest"] = out.get("citation_manifest")
        facts["g2_unsourced_citations"] = (l2 or {}).get("unsourced_citations")
        facts["dropped_dispatch_failures"] = out.get("dropped_dispatch_failures")
        if entries:
            primary = entries[0]
            facts["primary_doi"] = primary.get("source_id")
            facts["primary_source_ref"] = primary.get("source_ref")
            facts["primary_title"] = primary.get("title")
        # D5 narration — the exact SPOC function on the real contribution output
        narration = narrate_research_result(out)
        facts["narration_line"] = narration
        log(f"NARRATION: {narration}")

    # --- resolve the primary DOI via doi.org (content-inspect) ---
    doi = facts.get("primary_doi")
    if doi:
        import httpx  # noqa: PLC0415
        import re as _re  # noqa: PLC0415
        url = f"https://doi.org/{doi}"
        log(f"resolving DOI: {url}")
        try:
            r = httpx.get(url, follow_redirects=True, timeout=45,
                          headers={"User-Agent": "Mozilla/5.0 (S6-witness)"})
            title_m = _re.search(r"<title[^>]*>(.*?)</title>", r.text, _re.IGNORECASE | _re.DOTALL)
            snippet = (title_m.group(1).strip()[:200] if title_m else r.text[:200]).replace("\n", " ")
            facts["doi_resolution"] = {
                "url": url,
                "status_code": r.status_code,
                "final_url": str(r.url),
                "resolved_title_snippet": snippet,
            }
            log(f"  DOI resolved: {r.status_code} -> {r.url} :: {snippet[:120]}")
        except Exception as exc:  # noqa: BLE001
            facts["doi_resolution"] = {"url": url, "error": repr(exc)}
            log(f"  DOI resolution error: {exc!r}")

    # --- capture cost report if present ---
    for name in ("cost-report.json", "cost_report.json", "economics.json"):
        p = run_dir / name
        if p.is_file():
            try:
                facts["cost_report"] = json.loads(p.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                pass
            break

except BaseException:
    log("lane-a driver RAISED:\n" + traceback.format_exc())
    facts["driver_exception"] = traceback.format_exc()

(EVIDENCE / "lane_a-facts.json").write_text(json.dumps(facts, indent=2, default=str) + "\n", encoding="utf-8")
log(f"=== LANE-a facts written: entries={facts.get('entries_count')} "
    f"primary_doi={facts.get('primary_doi')} final_gate={facts.get('final_paused_gate')} ===")
timer.cancel()
sys.exit(0)
