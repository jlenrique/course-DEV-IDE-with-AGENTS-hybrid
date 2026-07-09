"""S7 AC-L live witness — FULL composed Part-3 walk to node 07W (workbook_producer).

First-ever in-graph 07W reach. Starts a NEW production trial on the curated
non-tejal Part-3 corpus with the narrated-deck-with-workbook bundle (keeps 07W in
the graph), scripted standard-A styleguide pick (avoids S4 unbound-halt), drives
EVERY HIL gate to 'approve' until the walk completes (07W terminal sidecar), then
captures the produced workbook + collateral + research for AC-L judging.
FIRST-RUN-STANDS. Weed-clearing accept posture. Enrichment + research default-ON.
"""
from __future__ import annotations

import faulthandler
import json
import logging
import os
import shutil
import sys
import threading
import traceback
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

REPO = Path(r"C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS-hybrid")
EVIDENCE = Path(__file__).resolve().parent
CORPUS = REPO / "course-content/courses/tejal-c1m1-p3-opportunity"
GUIDE = "hil-2026-apc-crossroads-classic"  # canonical standard-A (S2-proven)
OPERATOR = "operator_juan"
HARD_TIMEOUT_S = 3000  # full deck+TTS+composite walk is long

sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "skills" / "bmad-agent-texas" / "scripts"))
os.chdir(REPO)
os.environ["PYTHONIOENCODING"] = "utf-8"
LOG = open(EVIDENCE / "driver-log.txt", "a", encoding="utf-8")


def log(msg: str) -> None:
    line = f"[{datetime.now(tz=UTC).isoformat()}] {msg}"
    print(line, flush=True)
    LOG.write(line + "\n")
    LOG.flush()


# --- env: dotenv override gotcha; leave feature flags UNSET => default-ON ---
os.environ.pop("OPENAI_API_KEY", None)
from dotenv import load_dotenv  # noqa: E402

load_dotenv(REPO / ".env", override=True)
os.environ.pop("MARCUS_G0_DISPATCH_LIVE", None)        # keep G0 pre-pass deterministic ($0)
os.environ.pop("MARCUS_G0_ENRICHMENT_ACTIVE", None)    # default-ON (S5-3b) => G0E/G0R fire
os.environ.pop("MARCUS_RESEARCH_DISPATCH_LIVE", None)  # default-ON (S6) => live Scite at 04.55
key = os.environ.get("OPENAI_API_KEY", "")
assert key.startswith("sk-") and "subst" not in key, "OPENAI_API_KEY sentinel/absent"
assert os.environ.get("LANGSMITH_API_KEY") and os.environ.get("LANGSMITH_PROJECT"), "LANGSMITH env"
assert os.environ.get("GAMMA_API_KEY"), "GAMMA_API_KEY absent"
log(f"env: OPENAI={key[:7]}...{key[-4:]} (len {len(key)}); LANGSMITH+GAMMA present")

handler = logging.FileHandler(EVIDENCE / "walk-log.txt", encoding="utf-8")
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

from app.marcus.cli.front_door import front_door_select  # noqa: E402
from app.marcus.cli.trial import start_trial  # noqa: E402
from app.marcus.orchestrator.production_runner import resume_production_trial  # noqa: E402
from app.marcus.orchestrator.picker_html_emitter import build_selection_code  # noqa: E402
from app.models.state.operator_verdict import OperatorVerdict  # noqa: E402
from app.runtime.economics import RUNS_ROOT  # noqa: E402

TRIAL_ID = uuid4()
RUN_DIR = RUNS_ROOT / str(TRIAL_ID)
CODE = build_selection_code(TRIAL_ID.hex, {"A": GUIDE})
sel = front_door_select(
    operator_pick="narrated-deck-with-workbook",
    confirmed=True,
    seeds={"corpus_path": str(CORPUS)},
    allow_unproven=True,
).selection
log(f"trial_id={TRIAL_ID} bundle=narrated-deck-with-workbook selection={sel}")
log(f"selection_code (standard-A pick)={CODE}")

facts: dict = {
    "story": "S7-AC-L",
    "trial_id": str(TRIAL_ID),
    "corpus": str(CORPUS),
    "run_dir": str(RUN_DIR),
    "bundle": "narrated-deck-with-workbook",
    "guide": GUIDE,
    "minted_at": datetime.now(tz=UTC).isoformat(),
    "pause_sequence": [],
}


def read_run() -> dict:
    p = RUN_DIR / "run.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def approve(gate: str, cap: int):
    card = json.loads((RUN_DIR / f"decision-card-{gate}.json").read_text(encoding="utf-8"))
    verdict = OperatorVerdict(
        trial_id=TRIAL_ID, gate_id=gate, card_id=UUID(card["card"]["card_id"]),
        operator_id=OPERATOR, decision_card_digest=card["digest"], verb="approve",
    )
    log(f"resume approve {gate} (cap={cap})")
    env = resume_production_trial(
        trial_id=TRIAL_ID, verdict=verdict, runs_root=RUNS_ROOT, max_specialist_calls=cap,
    )
    log(f"  -> status={env.status} paused_gate={env.paused_gate} err={env.paused_error_tag}")
    return env

env = None
try:
    log("=== start_trial (REAL composed Part-3 walk; first pause expected G0E) ===")
    t0 = datetime.now(tz=UTC)
    start_trial(
        preset="production", input_path=CORPUS, operator_id=OPERATOR, trial_id=TRIAL_ID,
        auto_confirm_directive=True, component_selection=sel, selection_code=CODE,
        max_specialist_calls=40,
    )
    log(f"start_trial returned after {(datetime.now(tz=UTC)-t0).total_seconds():.0f}s")

    for i in range(30):
        run = read_run()
        status, gate = run.get("status"), run.get("paused_gate")
        log(f"[loop {i}] status={status} gate={gate} err={run.get('paused_error_tag')}")
        if status == "completed":
            log("RUN COMPLETED — 07W ran as terminal sidecar")
            break
        if status == "paused-at-error":
            log(f"ERROR-PAUSE at {gate} tag={run.get('paused_error_tag')} — stopping for orchestrator triage")
            break
        if status != "paused-at-gate" or not gate:
            log(f"UNEXPECTED terminal state status={status} gate={gate}")
            break
        facts["pause_sequence"].append(gate)
        cap = 40  # generous for deck/audio/compositor legs
        env = approve(gate, cap)
        if env.status == "paused-at-error":
            log(f"ERROR-PAUSE after {gate}: {env.paused_error_tag}")
            break
except BaseException:
    log("DRIVER RAISED:\n" + traceback.format_exc())
    facts["driver_exception"] = traceback.format_exc()

# ---------------------------------------------------------------- capture facts
run = read_run()
facts["final_status"] = run.get("status")
facts["final_paused_gate"] = run.get("paused_gate")
facts["final_error_tag"] = run.get("paused_error_tag")

try:
    from app.models.runtime.production_trial_envelope import ProductionTrialEnvelope  # noqa: E402
    rj = (RUN_DIR / "run.json").read_text(encoding="utf-8")
    tenv = ProductionTrialEnvelope.model_validate_json(rj)
    prod = tenv.production_envelope

    # workbook 07W contribution
    try:
        wb = prod.latest_for_specialist("workbook_producer")
        wb_out = wb.output if wb else {}
        facts["workbook_contribution"] = json.loads(json.dumps(wb_out, default=str))
        md_path = (wb_out.get("workbook") or {}).get("markdown_path") or (wb_out.get("workbook_producer") or {}).get("markdown_path")
        docx_path = (wb_out.get("workbook") or {}).get("docx_path") or (wb_out.get("workbook_producer") or {}).get("docx_path")
        facts["workbook_markdown_path"] = md_path
        facts["workbook_docx_path"] = docx_path
        log(f"workbook md={md_path} docx={docx_path}")
        if md_path and Path(md_path).is_file():
            text = Path(md_path).read_text(encoding="utf-8")
            facts["workbook_md_len"] = len(text)
            low = text.lower()
            facts["ac1_tejal_leak"] = {
                "present-trends": "present-trends" in low,
                "tejal-apc-c1-m1-p2": "tejal-apc-c1-m1-p2" in low,
                "macro-trends": "macro-trends" in low,
            }
            facts["ac1_no_tejal_leak"] = not any(facts["ac1_tejal_leak"].values())
            facts["has_doi_org_link"] = "https://doi.org/" in text
            shutil.copyfile(md_path, EVIDENCE / "workbook.md")
        if docx_path and Path(docx_path).is_file():
            shutil.copyfile(docx_path, EVIDENCE / "workbook.docx")
            facts["workbook_docx_bytes"] = Path(docx_path).stat().st_size
    except Exception:  # noqa: BLE001
        facts["workbook_capture_error"] = traceback.format_exc()

    # Irene collateral (blueprint provenance)
    try:
        irene = prod.latest_for_specialist("irene_pass1")
        lp = (irene.output.get("lesson_plan") if irene else {}) or {}
        coll = lp.get("collateral") or {}
        facts["collateral_declaration"] = coll.get("declaration")
        wbspec = coll.get("workbook") or {}
        secs = wbspec.get("sections") or []
        facts["collateral_section_count"] = len(secs)
        facts["collateral_section_titles"] = [s.get("title") for s in secs][:8]
        facts["collateral_kind"] = wbspec.get("kind")
        facts["collateral_research_goals"] = [g.get("goal_id") for g in (coll.get("research_goals") or [])]
    except Exception:  # noqa: BLE001
        facts["collateral_capture_error"] = traceback.format_exc()

    # research_wiring contribution + DOI
    try:
        rc = prod.get_contribution("research_wiring", node_id="04.55")
        if rc is not None:
            entries = rc.output.get("research_entries") or []
            facts["research_entries_count"] = len(entries)
            if entries:
                facts["primary_doi"] = entries[0].get("source_id")
                facts["primary_source_ref"] = entries[0].get("source_ref")
                facts["primary_title"] = entries[0].get("title")
        else:
            facts["research_entries_count"] = 0
    except Exception:  # noqa: BLE001
        facts["research_capture_error"] = traceback.format_exc()
except Exception:  # noqa: BLE001
    facts["envelope_capture_error"] = traceback.format_exc()

# DOI resolution (best-effort)
doi = facts.get("primary_doi")
if doi:
    try:
        import httpx  # noqa: PLC0415
        r = httpx.get(f"https://doi.org/{doi}", follow_redirects=True, timeout=45,
                      headers={"User-Agent": "Mozilla/5.0 (S7-witness)"})
        facts["doi_resolution"] = {"status": r.status_code, "final_url": str(r.url)}
        log(f"DOI {doi} -> {r.status_code} {r.url}")
    except Exception as exc:  # noqa: BLE001
        facts["doi_resolution"] = {"error": repr(exc)}

for name in ("cost-report.json", "cost_report.json", "economics.json"):
    p = RUN_DIR / name
    if p.is_file():
        try:
            facts["cost_report"] = json.loads(p.read_text(encoding="utf-8"))
            shutil.copyfile(p, EVIDENCE / "cost-report.json")
        except Exception:  # noqa: BLE001
            pass
        break

(EVIDENCE / "s7-acl-facts.json").write_text(json.dumps(facts, indent=2, default=str) + "\n", encoding="utf-8")
log(f"=== S7 AC-L facts written: final_status={facts.get('final_status')} "
    f"workbook_md={facts.get('workbook_markdown_path')} "
    f"no_tejal_leak={facts.get('ac1_no_tejal_leak')} "
    f"sections={facts.get('collateral_section_count')} "
    f"research_entries={facts.get('research_entries_count')} doi={facts.get('primary_doi')} ===")
timer.cancel()
sys.exit(0)
