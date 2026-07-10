"""Tejal Part-4 FULL production walk — AFK HIL stand-in (operator spend OK).

Demonstrates post–Mine-next / trust-hardening path:

1. Plan-dialogue (fresh LOs + framing) into the trial run dir
2. Production trial: narrated-deck-with-workbook (deck + motion + workbook)
3. Styleguide: hil-2026-apc-crossroads-classic-preserve
4. MARCUS_NARRATION_FIGURE_FIDELITY_ACTIVE=1 through Pass-2
5. Gate loop through Desmond (14.5); NO Descript publish
6. Score against SUCCESS-METRICS.md

Operator policy (2026-07-10): on mid-run BUG (not product fidelity halt),
attempt in-situ quick-dev patch, recover to last known-good checkpoint
(``reenter_at_node``), and continue to completion. Fidelity gate teeth are
honest product behavior — recover/re-roll, do not disable the flag.

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
HARD_TIMEOUT_S = 7200  # compose + full deck/motion/audio/workbook/Desmond
MAX_GATE_LOOPS = 50
MAX_SPECIALIST_CALLS = 50
MAX_RECOVERS = 3

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


# --- env ---
os.environ.pop("OPENAI_API_KEY", None)
from dotenv import load_dotenv  # noqa: E402

load_dotenv(REPO / ".env", override=True)
os.environ.pop("MARCUS_G0_DISPATCH_LIVE", None)
os.environ.pop("MARCUS_G0_ENRICHMENT_ACTIVE", None)
os.environ.pop("MARCUS_RESEARCH_DISPATCH_LIVE", None)
# Trust T4c: live Pass-2 with figure fidelity ON for this process only.
os.environ["MARCUS_NARRATION_FIGURE_FIDELITY_ACTIVE"] = "1"

key = os.environ.get("OPENAI_API_KEY", "")
assert key.startswith("sk-") and "subst" not in key, "OPENAI_API_KEY sentinel/absent"
assert os.environ.get("LANGSMITH_API_KEY") and os.environ.get("LANGSMITH_PROJECT")
assert os.environ.get("GAMMA_API_KEY"), "GAMMA_API_KEY absent"
assert os.environ.get("KLING_ACCESS_KEY") and os.environ.get("KLING_SECRET_KEY")
assert os.environ.get("ELEVENLABS_API_KEY"), "ELEVENLABS_API_KEY absent"
assert CORPUS.is_dir(), f"corpus missing: {CORPUS}"
assert INTENT.is_file(), f"intent missing: {INTENT}"
log(
    f"env OK; FIDELITY_FLAG=ON; OPENAI={key[:7]}...{key[-4:]}; "
    f"GAMMA+KLING+ELEVENLABS present"
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

import yaml  # noqa: E402
from app.marcus.cli.plan_dialogue_cli import main as plan_dialogue_main  # noqa: E402
from app.marcus.cli.trial import (  # noqa: E402
    _confirm_or_edit_directive,
    recover_trial,
    start_trial,
)
from app.marcus.orchestrator.picker_html_emitter import build_selection_code  # noqa: E402
from app.marcus.orchestrator.production_runner import resume_production_trial  # noqa: E402
from app.models.state.operator_verdict import OperatorVerdict  # noqa: E402
from app.runtime.economics import RUNS_ROOT  # noqa: E402
from app.specialists.irene.graph import (  # noqa: E402
    FIGURE_FIDELITY_ACTIVE_ENV,
    narration_figure_fidelity_active,
)

assert narration_figure_fidelity_active(), "fidelity flag must be ON for this walk"

TRIAL_ID = uuid4()
RUN_DIR = RUNS_ROOT / str(TRIAL_ID)
CODE = build_selection_code(TRIAL_ID.hex, {"A": GUIDE})

facts: dict = {
    "story": "tejal-p4-fullwalk-fidelity-on-desmond",
    "trial_id": str(TRIAL_ID),
    "corpus": str(CORPUS),
    "intent": str(INTENT),
    "run_dir": str(RUN_DIR),
    "runs_root": str(RUNS_ROOT),
    "evidence": str(EVIDENCE),
    "bundle_expected": "narrated-deck-with-workbook",
    "guide": GUIDE,
    "selection_code": CODE,
    "operator_id": OPERATOR,
    "fidelity_flag_env": FIGURE_FIDELITY_ACTIVE_ENV,
    "fidelity_flag_on": True,
    "descript_publish_required": False,
    "auto_confirm_directive": False,
    "allow_offline_cost_report": False,
    "minted_at": datetime.now(tz=UTC).isoformat(),
    "g0_confirm_path": [],
    "pause_sequence": [],
    "verdict_sequence": [],
    "recover_sequence": [],
    "in_situ_patches": [],
    "known_good_checkpoint": None,
    "hil_variety_exercised": [],
}


def read_run() -> dict:
    p = RUN_DIR / "run.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


# --- plan-dialogue into trial run dir (before start; no run.json yet) ---
def run_plan_dialogue() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    script = EVIDENCE / "plan-dialogue-script.yaml"
    script.write_text(
        yaml.safe_dump(
            {
                "purpose": (
                    "Bridge Module-1 innovator-mindset into Module-2 "
                    "leadership-identity with assessment-driven reflection"
                ),
                "audience": (
                    "APC Cohort-C1 clinician-innovators preparing for "
                    "Module-2 leadership-identity work"
                ),
                "workflow": "narrated-deck-with-workbook",
                "gap_fill_considered": "synthesize,wait,ask_operator",
                "gap_fill_chosen": "synthesize",
                "gap_fill_rationale": (
                    "Part-4 assessment-heavy leaf; synthesize gap-aware workbook"
                ),
                "learning_objectives": [
                    (
                        "Map Module-1 Opportunity-Radar targets onto Module-2 "
                        "leadership-identity competencies using assessment-bridge language"
                    ),
                    "Apply assessment-bridge framing to Module-2 handoff decisions",
                    (
                        "Diagnose a recurring operational failure with 5 Whys and "
                        "reframe it as an actionable opportunity"
                    ),
                ],
                "confirm": "yes",
            }
        ),
        encoding="utf-8",
    )
    # Workbook workflow needs collateral-spec for dialogue ratify path
    collateral_spec = EVIDENCE / "collateral-spec-from-intent.json"
    intent_raw = yaml.safe_load(INTENT.read_text(encoding="utf-8"))
    collateral_spec.write_text(
        json.dumps(intent_raw.get("collateral") or intent_raw, indent=2) + "\n",
        encoding="utf-8",
    )
    log("=== plan-dialogue (fresh LOs into trial run dir) ===")
    rc = plan_dialogue_main(
        [
            "--corpus-dir",
            str(CORPUS),
            "--output-dir",
            str(RUN_DIR),
            "--script",
            str(script),
            "--collateral-spec",
            str(collateral_spec),
        ]
    )
    facts["plan_dialogue_exit"] = rc
    facts["plan_companions"] = {
        "planning_ratification": (RUN_DIR / "planning-ratification.json").is_file(),
        "ratified_los": (RUN_DIR / "ratified-los.json").is_file(),
        "dialogue_md": (RUN_DIR / "marcus-planning-dialogue.md").is_file(),
    }
    log(f"plan-dialogue exit={rc} companions={facts['plan_companions']}")
    if rc != 0:
        raise RuntimeError(f"plan-dialogue failed exit={rc}")


# --- G0 confirm stand-in ---
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
    marker = (
        "\n# tejal-p4-fullwalk-operator-edit: inspected directive; "
        "no semantic source change\n"
    )
    if "# tejal-p4-fullwalk-operator-edit:" not in raw:
        path.write_text(raw.rstrip() + marker, encoding="utf-8")
    facts["g0_edit_applied"] = True
    transcript("G0-EDIT", f"appended inspection marker to {path}")
    log(f"G0 edit_fn applied; bytes={path.stat().st_size}")


def confirm_fn(*, directive_path: Path, auto_confirm_directive: bool):
    assert auto_confirm_directive is False
    return _confirm_or_edit_directive(
        directive_path=directive_path,
        auto_confirm_directive=False,
        input_fn=_g0_input,
        edit_fn=_g0_edit,
        isatty_fn=lambda: True,
        print_fn=lambda text: transcript("G0-DIRECTIVE-PRINT", str(text)[:4000]),
    )


def _choose_verdict(gate: str, card: dict) -> tuple[str, dict | None, str | None]:
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
    if gate == "G1" and "g1:edit-inspect" not in facts["hil_variety_exercised"]:
        payload = {
            "fullwalk_operator_note": (
                "AFK HIL stand-in inspected G1; accepting with inspection note."
            ),
        }
        facts["hil_variety_exercised"].append("g1:edit-inspect")
        return "edit", payload, None
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
            {"gate": gate, "verb": verb, "edit_payload": edit_payload},
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


FIDELITY_TAGS = {
    "irene.pass2.figure-unsourced",
    "irene.pass2.figure-source-deck-conflict",
    "irene.pass2.figure-positive-carry-miss",
    "irene.pass2.figure-contradiction",
}
# Product/LLM variance: recover+re-roll (no code patch).
RETRYABLE_REENTER = {
    "gamma.export.brief-unmatched": "07",
    "irene.pass2.slide-join-failed": "08",
    "irene.pass2.figure-unsourced": "08",
    "irene.pass2.figure-positive-carry-miss": "08",
    "irene.pass2.figure-contradiction": "07",
    "irene.pass2.figure-source-deck-conflict": "07",
}
# Substrate bugs: note for in-situ patch, then recover to last good node.
BUG_CLASS_REENTER = {
    "storyboard.join.collapsed-segment-ids": "08",
    "elevenlabs.join.collapsed-segment-ids": "08",
    "quinn_r.g5.join-collapsed": "08",
    "udac.asset-stale": None,  # do not skip UDAC; log for patch
    "cd.directive.malformed": "directive-composer",
}


def _note_checkpoint(gate: str | None, status: str | None) -> None:
    """Remember last successful gate pause as known-good for recover targeting."""
    if status == "paused-at-gate" and gate:
        facts["known_good_checkpoint"] = {
            "gate": gate,
            "at": datetime.now(tz=UTC).isoformat(),
        }


def _attempt_in_situ_note(tag: str | None, detail: str) -> None:
    """Record that an in-situ quick-dev patch was warranted (orchestrator applies)."""
    entry = {
        "tag": tag,
        "detail": detail,
        "known_good": facts.get("known_good_checkpoint"),
        "at": datetime.now(tz=UTC).isoformat(),
    }
    facts["in_situ_patches"].append(entry)
    (EVIDENCE / "IN-SITU-PATCH-NEEDED.md").write_text(
        "# In-situ patch needed mid-walk\n\n"
        f"```json\n{json.dumps(entry, indent=2)}\n```\n\n"
        "Policy: quick-dev patch → recover to known-good → continue.\n",
        encoding="utf-8",
    )
    log(f"IN-SITU PATCH NEEDED: tag={tag} detail={detail[:200]}")


def maybe_recover(tag: str | None) -> bool:
    if not tag or len(facts["recover_sequence"]) >= MAX_RECOVERS:
        return False
    node = RETRYABLE_REENTER.get(tag)
    if node is None and tag in BUG_CLASS_REENTER:
        _attempt_in_situ_note(tag, "bug-class error; recover after patch if possible")
        node = BUG_CLASS_REENTER.get(tag)
        if node is None:
            # Fall back to last known-good gate's upstream specialist if mapped.
            kg = facts.get("known_good_checkpoint") or {}
            log(f"no reenter node for bug tag={tag}; known_good={kg}")
            return False
    if node is None:
        _attempt_in_situ_note(tag, "unmapped error — needs quick-dev triage")
        return False
    log(f"RECOVER reenter_at_node={node} for tag={tag}")
    # Ensure fidelity flag still ON across recover (dotenv reload must not clear).
    os.environ["MARCUS_NARRATION_FIGURE_FIDELITY_ACTIVE"] = "1"
    try:
        payload = recover_trial(
            trial_id=TRIAL_ID,
            runs_root=RUNS_ROOT,
            max_specialist_calls=MAX_SPECIALIST_CALLS,
            reenter_at_node=node,
        )
        facts["recover_sequence"].append(
            {
                "tag": tag,
                "reenter_at_node": node,
                "next_status": payload.get("status"),
                "next_gate": payload.get("paused_gate"),
                "err": payload.get("paused_error_tag"),
            }
        )
        log(
            f"  recover -> status={payload.get('status')} "
            f"err={payload.get('paused_error_tag')}"
        )
        return True
    except Exception:  # noqa: BLE001
        facts["recover_sequence"].append(
            {"tag": tag, "reenter_at_node": node, "error": traceback.format_exc()}
        )
        _attempt_in_situ_note(tag, traceback.format_exc()[-1500:])
        log("RECOVER RAISED:\n" + traceback.format_exc())
        return False


def _find_artifacts() -> dict:
    found: dict = {
        "pngs": [],
        "mp4s": [],
        "audio": [],
        "workbook_md": None,
        "workbook_docx": None,
        "desmond_brief": None,
        "assembly_guide": None,
        "extracted_md": None,
        "irene_pass1_json": None,
        "ratified_los": None,
    }
    if not RUN_DIR.is_dir():
        return found
    for p in RUN_DIR.rglob("*"):
        if not p.is_file():
            continue
        name = p.name.lower()
        rel = str(p.relative_to(RUN_DIR)).replace("\\", "/")
        if name.endswith(".png") and ("slide" in name or "gamma" in rel or "visual" in rel):
            found["pngs"].append(rel)
        if name.endswith(".mp4"):
            found["mp4s"].append(rel)
        if name.endswith((".mp3", ".wav", ".m4a")):
            found["audio"].append(rel)
        if name == "workbook.md":
            found["workbook_md"] = rel
        if name == "workbook.docx":
            found["workbook_docx"] = rel
        if name == "desmond-operator-brief.md":
            found["desmond_brief"] = rel
        if name == "descript-assembly-guide.md":
            found["assembly_guide"] = rel
        if name == "extracted.md":
            found["extracted_md"] = rel
        if name == "irene-pass1.lesson-plan.json":
            found["irene_pass1_json"] = rel
        if name == "ratified-los.json":
            found["ratified_los"] = rel
    return found


def score_metrics(artifacts: dict) -> dict:
    run = read_run()
    status = run.get("status")
    err = run.get("paused_error_tag")
    fidelity_halt = err in FIDELITY_TAGS if err else False
    checks = {
        "c1_terminal_completed": status == "completed",
        "c2_no_descript_publish_required": True,
        "c3_plan_companions_present": bool(
            facts.get("plan_companions", {}).get("ratified_los")
        ),
        "c3_ratified_los_on_disk": bool(artifacts.get("ratified_los")),
        "c4_fidelity_flag_was_on": bool(facts.get("fidelity_flag_on")),
        "c4_fidelity_sail_or_honest_halt": (
            status == "completed"
            or fidelity_halt
            or err is None
        ),
        "c5_deck_png": len(artifacts.get("pngs") or []) >= 1,
        "c5_motion_mp4": len(artifacts.get("mp4s") or []) >= 1,
        "c5_audio": len(artifacts.get("audio") or []) >= 1,
        "c5_workbook_md": bool(artifacts.get("workbook_md")),
        "c5_workbook_docx": bool(artifacts.get("workbook_docx")),
        "c5_desmond_brief": bool(artifacts.get("desmond_brief")),
        "g0_edit_confirm": facts.get("g0_confirm_path") == ["e", "c"],
        "bundle_id_ok": facts.get("trial_start_bundle_id")
        == "narrated-deck-with-workbook",
        "cleared_gamma_brief_unmatched": err != "gamma.export.brief-unmatched",
        "extracted_md_present": bool(artifacts.get("extracted_md")),
        "no_driver_exception": facts.get("driver_exception") is None,
    }
    critical = [
        "c1_terminal_completed",
        "c5_deck_png",
        "c5_motion_mp4",
        "c5_audio",
        "c5_workbook_md",
        "c5_desmond_brief",
        "g0_edit_confirm",
        "no_driver_exception",
    ]
    if checks["c1_terminal_completed"] and all(checks[k] for k in critical):
        grade = "PASS"
    elif checks["c1_terminal_completed"] and facts.get("recover_sequence"):
        grade = "PASS-WITH-RECOVER"
    elif any(
        [
            checks["c5_deck_png"],
            checks["c5_workbook_md"],
            checks["c5_desmond_brief"],
        ]
    ):
        grade = "PARTIAL"
    else:
        grade = "FAIL"
    if fidelity_halt and status != "completed":
        grade = "PARTIAL" if grade == "FAIL" else grade
        checks["c4_note"] = f"fidelity halt tag={err}"
    return {
        "grade": grade,
        "checks": checks,
        "artifact_counts": {
            "pngs": len(artifacts.get("pngs") or []),
            "mp4s": len(artifacts.get("mp4s") or []),
            "audio": len(artifacts.get("audio") or []),
        },
        "final_status": status,
        "final_error_tag": err,
        "fidelity_halt": fidelity_halt,
    }


env = None
try:
    run_plan_dialogue()

    log("=== start_trial (fullwalk; fidelity ON; preserve styleguide) ===")
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
        err = run.get("paused_error_tag")
        log(f"[loop {i}] status={status} gate={gate} err={err}")
        if status == "completed":
            log("RUN COMPLETED")
            break
        if status == "paused-at-error":
            if maybe_recover(err):
                continue
            log(f"ERROR-PAUSE at {gate} tag={err} — stopping")
            break
        if status != "paused-at-gate" or not gate:
            log(f"UNEXPECTED state status={status} gate={gate}")
            break
        facts["pause_sequence"].append(gate)
        _note_checkpoint(gate, status)
        env = drive_verdict(gate, MAX_SPECIALIST_CALLS)
        if env.status == "paused-at-error":
            if maybe_recover(env.paused_error_tag):
                continue
            log(f"ERROR-PAUSE after {gate}: {env.paused_error_tag}")
            break
        if env.status == "completed":
            log("RUN COMPLETED after resume")
            break
except BaseException:
    log("DRIVER RAISED:\n" + traceback.format_exc())
    facts["driver_exception"] = traceback.format_exc()
    _attempt_in_situ_note(
        "driver_exception",
        traceback.format_exc()[-2000:],
    )
    # Best-effort recover to last known-good if run exists and is error-paused.
    try:
        run = read_run()
        if run.get("status") == "paused-at-error":
            maybe_recover(run.get("paused_error_tag"))
    except Exception:  # noqa: BLE001
        log("post-exception recover attempt failed:\n" + traceback.format_exc())

# --- capture ---
run = read_run()
facts["final_status"] = run.get("status")
facts["final_paused_gate"] = run.get("paused_gate")
facts["final_error_tag"] = run.get("paused_error_tag")
facts["pause_sequence_unique"] = list(dict.fromkeys(facts["pause_sequence"]))
facts["hil_variety_unique"] = list(dict.fromkeys(facts["hil_variety_exercised"]))
facts["finished_at"] = datetime.now(tz=UTC).isoformat()
facts["fidelity_flag_still_on"] = narration_figure_fidelity_active()

ts = RUN_DIR / "trial-start.json"
if ts.is_file():
    ts_data = json.loads(ts.read_text(encoding="utf-8"))
    facts["trial_start_bundle_id"] = ts_data.get("lesson_plan_collateral_bundle_id")
    facts["trial_start_component_selection"] = ts_data.get("component_selection")

for name in (
    "model_resolution_trail.json",
    "directive.yaml",
    "trial-start.json",
    "run.json",
    "run_summary.yaml",
    "ratified-los.json",
    "planning-ratification.json",
    "marcus-planning-dialogue.md",
    "irene-pass1.lesson-plan.json",
    "irene-pass1.md",
):
    src = RUN_DIR / name
    if src.is_file():
        shutil.copyfile(src, EVIDENCE / name)
        facts.setdefault("copied_artifacts", []).append(name)

for gate in facts["pause_sequence_unique"]:
    src = RUN_DIR / f"decision-card-{gate}.json"
    if src.is_file():
        shutil.copyfile(src, EVIDENCE / f"decision-card-{gate}.json")
        facts.setdefault("copied_artifacts").append(f"decision-card-{gate}.json")

artifacts = _find_artifacts()
facts["artifacts_found"] = artifacts

# Copy key deliverables into evidence
for key_name, rel in (
    ("workbook_md", artifacts.get("workbook_md")),
    ("workbook_docx", artifacts.get("workbook_docx")),
    ("desmond_brief", artifacts.get("desmond_brief")),
    ("assembly_guide", artifacts.get("assembly_guide")),
):
    if rel:
        src = RUN_DIR / rel
        if src.is_file():
            dest_name = src.name
            shutil.copyfile(src, EVIDENCE / dest_name)
            facts.setdefault("copied_artifacts", []).append(dest_name)

score = score_metrics(artifacts)
facts["scorecard"] = score
(EVIDENCE / "metrics-scorecard.json").write_text(
    json.dumps(score, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
(EVIDENCE / "facts.json").write_text(
    json.dumps(facts, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8"
)

proof = [
    f"# Tejal P4 fullwalk PROOF — {facts['finished_at']}",
    "",
    f"**Trial:** `{TRIAL_ID}`",
    f"**Grade:** {score['grade']}",
    f"**Final status:** {facts.get('final_status')} err={facts.get('final_error_tag')}",
    f"**Fidelity flag ON:** {facts.get('fidelity_flag_on')}",
    f"**Recovers:** {len(facts.get('recover_sequence') or [])}",
    f"**Descript publish:** not required / not performed",
    "",
    "## Scorecard",
    "```json",
    json.dumps(score, indent=2, sort_keys=True),
    "```",
    "",
    "## Artifacts",
    "```json",
    json.dumps(artifacts, indent=2, sort_keys=True),
    "```",
    "",
]
(EVIDENCE / "PROOF.md").write_text("\n".join(proof) + "\n", encoding="utf-8")

log(f"SCORE grade={score['grade']} status={facts.get('final_status')}")
log(f"evidence={EVIDENCE}")
timer.cancel()
LOG.close()
TRANSCRIPT.close()

# Restore product default OFF in this process (does not affect other shells).
os.environ.pop(FIGURE_FIDELITY_ACTIVE_ENV, None)

raise SystemExit(0 if score["grade"] in {"PASS", "PASS-WITH-RECOVER"} else 1)
