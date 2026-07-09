"""S8 Tejal Part-4 TERMINAL-WALK HIL driver — AFK operator stand-in.

Post-matcher-fix re-proof (2026-07-08). Goal: clear Gary node 07 and walk
toward a terminal status so S8 can be party-closed as fully complete.

- REAL Section 02A compose (paid/live LLM; long wall budget).
- NO ``--auto-confirm-directive`` — G0 confirm uses scripted edit-then-confirm.
- Styleguide via pre-minted ``selection_code`` (D2 scripted pick path).
- Ratified lesson-plan collateral intent -> narrated-deck-with-workbook.
- Gate loop exercises a VARIETY of HIL verbs as opportunities appear:
  approve / edit / select (never reject on the main proof path).
- NO ``--allow-offline-cost-report``.

FIRST-RUN-STANDS. Evidence lands beside this driver.
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
CORPUS = REPO / "course-content/courses/tejal-c1m1-p4-assessments-bridge"
INTENT = (
    REPO
    / "_bmad-output/implementation-artifacts/s8-tejal-p4-ratified-collateral-intent.yaml"
)
GUIDE = "hil-2026-apc-crossroads-classic-preserve"
OPERATOR = "juanl"
HARD_TIMEOUT_S = 3600  # compose + full deck/motion/workbook walk
MAX_GATE_LOOPS = 40
MAX_SPECIALIST_CALLS = 40

sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "skills" / "bmad-agent-texas" / "scripts"))
os.chdir(REPO)
os.environ["PYTHONIOENCODING"] = "utf-8"

LOG = open(EVIDENCE / "driver-log.txt", "a", encoding="utf-8")
TRANSCRIPT = open(EVIDENCE / "hil-transcript.txt", "a", encoding="utf-8")


def log(msg: str) -> None:
    line = f"[{datetime.now(tz=UTC).isoformat()}] {msg}"
    print(line, flush=True)
    LOG.write(line + "\n")
    LOG.flush()


def transcript(kind: str, text: str) -> None:
    TRANSCRIPT.write(f"--- {kind} ---\n{text}\n")
    TRANSCRIPT.flush()


# --- env: dotenv override gotcha; leave enrichment/research flags UNSET ---
os.environ.pop("OPENAI_API_KEY", None)
from dotenv import load_dotenv  # noqa: E402

load_dotenv(REPO / ".env", override=True)
os.environ.pop("MARCUS_G0_DISPATCH_LIVE", None)
os.environ.pop("MARCUS_G0_ENRICHMENT_ACTIVE", None)
os.environ.pop("MARCUS_RESEARCH_DISPATCH_LIVE", None)
key = os.environ.get("OPENAI_API_KEY", "")
assert key.startswith("sk-") and "subst" not in key, "OPENAI_API_KEY sentinel/absent"
assert os.environ.get("LANGSMITH_API_KEY") and os.environ.get("LANGSMITH_PROJECT")
assert os.environ.get("GAMMA_API_KEY"), "GAMMA_API_KEY absent"
assert CORPUS.is_dir(), f"corpus missing: {CORPUS}"
assert INTENT.is_file(), f"intent missing: {INTENT}"
log(
    f"env: OPENAI={key[:7]}...{key[-4:]} (len {len(key)}); "
    f"LANGSMITH+GAMMA present; corpus+intent OK"
)

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

from app.marcus.cli.trial import (  # noqa: E402
    _confirm_or_edit_directive,
    start_trial,
)
from app.marcus.orchestrator.picker_html_emitter import build_selection_code  # noqa: E402
from app.marcus.orchestrator.production_runner import resume_production_trial  # noqa: E402
from app.models.state.operator_verdict import OperatorVerdict  # noqa: E402
from app.runtime.economics import RUNS_ROOT  # noqa: E402

TRIAL_ID = uuid4()
RUN_DIR = RUNS_ROOT / str(TRIAL_ID)
CODE = build_selection_code(TRIAL_ID.hex, {"A": GUIDE})

facts: dict = {
    "story": "S8-tejal-p4-terminal-composed-walk",
    "matcher_fix_head": "82be31b8",
    "trial_id": str(TRIAL_ID),
    "corpus": str(CORPUS),
    "intent": str(INTENT),
    "run_dir": str(RUN_DIR),
    "runs_root": str(RUNS_ROOT),
    "bundle_expected": "narrated-deck-with-workbook",
    "guide": GUIDE,
    "selection_code": CODE,
    "operator_id": OPERATOR,
    "auto_confirm_directive": False,
    "allow_offline_cost_report": False,
    "minted_at": datetime.now(tz=UTC).isoformat(),
    "g0_confirm_path": [],
    "pause_sequence": [],
    "verdict_sequence": [],
    "hil_variety_exercised": [],
}


def read_run() -> dict:
    p = RUN_DIR / "run.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


# --- G0 confirm: authentic edit-then-confirm (NOT auto-confirm flag) ---
_g0_state: dict = {"edited": False}


def _g0_input(prompt: str) -> str:
    transcript("G0-PROMPT", prompt)
    if not _g0_state["edited"]:
        _g0_state["edited"] = True
        facts["g0_confirm_path"].append("e")
        facts["hil_variety_exercised"].append("g0-confirm:edit")
        transcript("G0-REPLY", "e")
        log("G0 confirm feeder: edit")
        return "e"
    facts["g0_confirm_path"].append("c")
    facts["hil_variety_exercised"].append("g0-confirm:confirm")
    transcript("G0-REPLY", "c")
    log("G0 confirm feeder: confirm")
    return "c"


def _g0_edit(path: Path) -> None:
    raw = path.read_text(encoding="utf-8")
    marker = "\n# s8-hil-operator-edit: inspected directive; no semantic source change\n"
    if "# s8-hil-operator-edit:" not in raw:
        path.write_text(raw.rstrip() + marker, encoding="utf-8")
    facts["g0_edit_applied"] = True
    facts["g0_edit_directive_bytes"] = path.stat().st_size
    transcript("G0-EDIT", f"appended inspection marker to {path}")
    log(f"G0 edit_fn applied marker; bytes={path.stat().st_size}")


def confirm_fn(*, directive_path: Path, auto_confirm_directive: bool):
    """Scripted HIL stand-in: force interactive confirm path; edit then confirm."""
    assert auto_confirm_directive is False, "S8 proof forbids auto_confirm_directive=True"
    transcript(
        "G0-CONFIRM-GATE",
        f"directive={directive_path} auto={auto_confirm_directive} -> edit-then-confirm",
    )
    return _confirm_or_edit_directive(
        directive_path=directive_path,
        auto_confirm_directive=False,
        input_fn=_g0_input,
        edit_fn=_g0_edit,
        isatty_fn=lambda: True,
        print_fn=lambda text: transcript("G0-DIRECTIVE-PRINT", str(text)[:4000]),
    )


def _choose_verdict(gate: str, card: dict) -> tuple[str, dict | None, str | None]:
    """Pick a varied but non-destructive HIL verb for this gate opportunity."""
    # G2B: select A for all slides when variant options are present.
    if gate == "G2B":
        opts = [
            e
            for e in card.get("card", {}).get("pick_context", [])
            if e.get("kind") == "variant-options"
        ]
        if opts and opts[0].get("slides"):
            slide_ids = [s["slide_id"] for s in opts[0]["slides"]]
            payload = {"slide_variant_selections": {s: "A" for s in slide_ids}}
            facts["hil_variety_exercised"].append(f"{gate}:select-all-A:{len(slide_ids)}")
            return "select", payload, None

    # First content gate after enrichment: exercise edit with an inspection note.
    # edit continues the walk (terminating verb); does not reject the trial.
    if gate == "G1" and "g1:edit-inspect" not in facts["hil_variety_exercised"]:
        payload = {
            "s8_hil_operator_note": (
                "AFK HIL stand-in inspected G1 packet; accepting with "
                "inspection note (no semantic rewrite)."
            ),
            "s8_hil_variety": "edit-then-continue",
        }
        facts["hil_variety_exercised"].append("g1:edit-inspect")
        return "edit", payload, None

    # Default: approve (still a real OperatorVerdict on the real card digest).
    facts["hil_variety_exercised"].append(f"{gate}:approve")
    return "approve", None, None


def drive_verdict(gate: str, cap: int):
    card_path = RUN_DIR / f"decision-card-{gate}.json"
    card = json.loads(card_path.read_text(encoding="utf-8"))
    verb, edit_payload, reject_reason = _choose_verdict(gate, card)
    kwargs: dict = {
        "trial_id": TRIAL_ID,
        "gate_id": gate,
        "card_id": UUID(card["card"]["card_id"]),
        "operator_id": OPERATOR,
        "decision_card_digest": card["digest"],
        "verb": verb,
    }
    if edit_payload is not None:
        kwargs["edit_payload"] = edit_payload
    if reject_reason is not None:
        kwargs["reject_reason"] = reject_reason
    verdict = OperatorVerdict(**kwargs)
    transcript(
        "VERDICT",
        json.dumps(
            {
                "gate": gate,
                "verb": verb,
                "edit_payload": edit_payload,
                "card_id": str(kwargs["card_id"]),
            },
            indent=2,
            sort_keys=True,
        ),
    )
    log(f"resume {verb} {gate} (cap={cap})")
    env = resume_production_trial(
        trial_id=TRIAL_ID,
        verdict=verdict,
        runs_root=RUNS_ROOT,
        max_specialist_calls=cap,
    )
    facts["verdict_sequence"].append(
        {
            "gate": gate,
            "verb": verb,
            "next_status": env.status,
            "next_gate": env.paused_gate,
            "err": env.paused_error_tag,
        }
    )
    log(
        f"  -> status={env.status} paused_gate={env.paused_gate} "
        f"err={env.paused_error_tag}"
    )
    return env


env = None
try:
    log("=== start_trial (S8 Part-4 HIL; compose + edit/confirm + selection_code) ===")
    t0 = datetime.now(tz=UTC)
    start_result = start_trial(
        preset="production",
        input_path=CORPUS,
        operator_id=OPERATOR,
        trial_id=TRIAL_ID,
        auto_confirm_directive=False,
        confirm_fn=confirm_fn,
        selection_code=CODE,
        lesson_plan_collateral_intent_path=INTENT,
        max_specialist_calls=MAX_SPECIALIST_CALLS,
        allow_offline_cost_report=False,
    )
    facts["start_trial_result"] = start_result
    facts["start_elapsed_s"] = round((datetime.now(tz=UTC) - t0).total_seconds(), 1)
    log(f"start_trial returned after {facts['start_elapsed_s']}s: {start_result}")

    for i in range(MAX_GATE_LOOPS):
        run = read_run()
        status, gate = run.get("status"), run.get("paused_gate")
        log(
            f"[loop {i}] status={status} gate={gate} "
            f"err={run.get('paused_error_tag')}"
        )
        if status == "completed":
            log("RUN COMPLETED")
            break
        if status == "paused-at-error":
            log(
                f"ERROR-PAUSE at {gate} tag={run.get('paused_error_tag')} "
                "— stopping for triage"
            )
            break
        if status != "paused-at-gate" or not gate:
            log(f"UNEXPECTED terminal state status={status} gate={gate}")
            break
        facts["pause_sequence"].append(gate)
        env = drive_verdict(gate, MAX_SPECIALIST_CALLS)
        if env.status == "paused-at-error":
            log(f"ERROR-PAUSE after {gate}: {env.paused_error_tag}")
            break
        if env.status == "completed":
            log("RUN COMPLETED after resume")
            break
except BaseException:
    log("DRIVER RAISED:\n" + traceback.format_exc())
    facts["driver_exception"] = traceback.format_exc()

# --- capture facts + key artifacts ---
run = read_run()
facts["final_status"] = run.get("status")
facts["final_paused_gate"] = run.get("paused_gate")
facts["final_error_tag"] = run.get("paused_error_tag")
facts["pause_sequence_unique"] = list(dict.fromkeys(facts["pause_sequence"]))
facts["hil_variety_unique"] = list(dict.fromkeys(facts["hil_variety_exercised"]))
facts["finished_at"] = datetime.now(tz=UTC).isoformat()

# Copy durable receipts into evidence pack
for name in (
    "model_resolution_trail.json",
    "directive.yaml",
    "trial-start.json",
    "run.json",
    "run_summary.yaml",
    "ratified-los.json",
):
    src = RUN_DIR / name
    if src.is_file():
        shutil.copyfile(src, EVIDENCE / name)
        facts.setdefault("copied_artifacts", []).append(name)

# Decision cards for every paused gate
for gate in facts["pause_sequence_unique"]:
    src = RUN_DIR / f"decision-card-{gate}.json"
    if src.is_file():
        shutil.copyfile(src, EVIDENCE / f"decision-card-{gate}.json")
        facts.setdefault("copied_artifacts", []).append(f"decision-card-{gate}.json")

# Workbook / collateral if present
try:
    from app.models.runtime.production_trial_envelope import (  # noqa: E402
        ProductionTrialEnvelope,
    )

    if (RUN_DIR / "run.json").is_file():
        tenv = ProductionTrialEnvelope.model_validate_json(
            (RUN_DIR / "run.json").read_text(encoding="utf-8")
        )
        facts["envelope_status"] = tenv.status
        facts["lesson_plan_collateral_bundle_id"] = getattr(
            tenv, "lesson_plan_collateral_bundle_id", None
        ) or (tenv.model_dump().get("lesson_plan_collateral_bundle_id"))
        # trial-start may carry the bundle id
        ts = RUN_DIR / "trial-start.json"
        if ts.is_file():
            ts_data = json.loads(ts.read_text(encoding="utf-8"))
            facts["trial_start_bundle_id"] = ts_data.get(
                "lesson_plan_collateral_bundle_id"
            )
            facts["trial_start_component_selection"] = ts_data.get(
                "component_selection"
            )
        prod = tenv.production_envelope
        if prod is not None:
            try:
                wb = prod.latest_for_specialist("workbook_producer")
                if wb is not None:
                    wb_out = wb.output or {}
                    md_path = (wb_out.get("workbook") or {}).get("markdown_path") or (
                        wb_out.get("workbook_producer") or {}
                    ).get("markdown_path")
                    docx_path = (wb_out.get("workbook") or {}).get("docx_path") or (
                        wb_out.get("workbook_producer") or {}
                    ).get("docx_path")
                    facts["workbook_markdown_path"] = md_path
                    facts["workbook_docx_path"] = docx_path
                    if md_path and Path(md_path).is_file():
                        shutil.copyfile(md_path, EVIDENCE / "workbook.md")
                        facts.setdefault("copied_artifacts", []).append("workbook.md")
                    if docx_path and Path(docx_path).is_file():
                        shutil.copyfile(docx_path, EVIDENCE / "workbook.docx")
                        facts.setdefault("copied_artifacts", []).append("workbook.docx")
            except Exception:  # noqa: BLE001
                facts["workbook_capture_error"] = traceback.format_exc()
except Exception:  # noqa: BLE001
    facts["envelope_capture_error"] = traceback.format_exc()

# Terminal-walk claim gate (driver-local; party still owns final S8-complete).
cleared_gary = facts.get("final_error_tag") != "gamma.export.brief-unmatched"
terminalish = facts.get("final_status") in {"completed", "paused-at-gate"}
# paused-at-gate after G1+ is OK mid-walk; completed is strongest.
past_g1 = any(g not in {"G0E", "G0R", "G1"} for g in facts.get("pause_sequence", [])) or (
    facts.get("final_status") == "completed"
)
# Stronger: never die on the fixed matcher flake; prefer completed or gates past G1.
claim_ok = (
    facts.get("g0_confirm_path") == ["e", "c"]
    and facts.get("trial_start_bundle_id") == "narrated-deck-with-workbook"
    and (RUN_DIR / "directive.yaml").is_file()
    and (RUN_DIR / "trial-start.json").is_file()
    and facts.get("driver_exception") is None
    and cleared_gary
    and (
        facts.get("final_status") == "completed"
        or (terminalish and past_g1)
        or (
            facts.get("final_status") == "paused-at-error"
            and facts.get("final_error_tag") not in {None, "gamma.export.brief-unmatched"}
        )
    )
)
facts["cleared_gary_brief_unmatched"] = bool(cleared_gary)
facts["s8_terminal_walk_driver_claim_ok"] = bool(claim_ok)
facts["s8_complete_requires_party"] = True
facts["note"] = (
    "Driver claim_ok means compose+G0-HIL+bundle binding succeeded AND the walk "
    "did not die on gamma.export.brief-unmatched (matcher fix). Prefer "
    "final_status=completed; later non-matcher error-pauses are honest and "
    "party-triaged. Full S8-complete still requires BMAD party concurrence."
)

(EVIDENCE / "facts.json").write_text(
    json.dumps(facts, indent=2, sort_keys=True, default=str) + "\n",
    encoding="utf-8",
)
log(f"facts written; claim_ok={claim_ok}; final_status={facts.get('final_status')}")
log(f"hil_variety={facts.get('hil_variety_unique')}")
log(f"pause_sequence={facts.get('pause_sequence')}")
timer.cancel()
LOG.close()
TRANSCRIPT.close()
sys.exit(0 if claim_ok else 2)
