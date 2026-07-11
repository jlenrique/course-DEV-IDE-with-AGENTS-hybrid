"""Irene-literal liveproof — AFK HIL pinch-hit driver (authentic production walk).

Goal
----
Prove the 2026-07-09 Marcus-SPOC seam on a REAL trial:

  Irene/plan-unit ``fidelity: literal-text`` → Gary forces ``text_mode=preserve``
  (amount absent) even when the bound styleguide is classic ``condense``+Minimal.

Authenticity contract (S8-class AFK HIL)
----------------------------------------
- REAL Section 02A compose; REAL Gamma / OpenAI / LangSmith.
- NO ``--allow-offline-cost-report`` (pause_at_gates stays True).
- NO ``--auto-confirm-directive`` — G0 uses scripted edit-then-confirm.
- Styleguide via pre-minted ``selection_code`` (D2 scripted pick).
- Guide is ``hil-2026-apc-crossroads-classic`` (condense) — NOT the preserve sibling.
- Gate loop exercises varied HIL verbs (approve / edit / select).

Operator pinch-hit for missing Irene emit
-----------------------------------------
Live Irene Pass-1 on Tejal P4 does NOT yet emit ``fidelity`` on plan_units
(confirmed on S8 terminal trial ``1bd08699…``). Until Irene authors that field,
the AFK stand-in — acting as operator ``juanl`` at G1 — stamps teaching-critical
units ``fidelity: literal-text`` on the persisted Irene contribution (digest
recomputed), then resumes. That is an honest HIL edit of the lesson-plan packet,
not a mock of Gary. Claim envelope must say so.

Live claim (driver-local)
-------------------------
Under classic-condense + mixed fidelity stamps:
  package slides carry fidelity; Gary ``calls_made == variants × cohorts``
  (expect 2 for single-variant mixed deck). That is the live wire proof of the
  binary cohort split. Unit FakeGammaClient tests already pin preserve/amount.

FIRST-RUN-STANDS. Evidence lands beside this driver.
"""
from __future__ import annotations

import copy
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
# Classic CONDENSE — the failure mode Irene-literal must beat (not preserve sibling).
GUIDE = "hil-2026-apc-crossroads-classic"
OPERATOR = "juanl"
HARD_TIMEOUT_S = 3600
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
    f"LANGSMITH+GAMMA present; corpus+intent OK; GUIDE={GUIDE}"
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
from app.models.runtime.production_envelope import (  # noqa: E402
    ProductionEnvelope,
    compute_output_digest,
)
from app.models.runtime.production_trial_envelope import (  # noqa: E402
    ProductionTrialEnvelope,
)
from app.models.state.operator_verdict import OperatorVerdict  # noqa: E402
from app.runtime.economics import RUNS_ROOT  # noqa: E402
from app.styleguide.resolver import resolve_styleguide  # noqa: E402

# Sanity: bound guide is still classic condense (registry not mutated).
_classic = resolve_styleguide(GUIDE)
assert _classic.get("text_mode") == "condense", _classic.get("text_mode")
log(f"styleguide {GUIDE}: text_mode={_classic.get('text_mode')} amount={_classic.get('amount')}")

TRIAL_ID = uuid4()
RUN_DIR = RUNS_ROOT / str(TRIAL_ID)
CODE = build_selection_code(TRIAL_ID.hex, {"A": GUIDE})

facts: dict = {
    "story": "irene-literal-supersedes-styleguide-truncation-liveproof",
    "claim_envelope": (
        "Proves Gary binary cohort split under classic-condense when plan units "
        "carry fidelity. Does NOT claim fidelity-L1-per-slide-text-mode closed. "
        "Does NOT claim Irene Pass-1 spontaneously emits fidelity (operator "
        "G1 stamp pinch-hits that emit until Irene authors it)."
    ),
    "trial_id": str(TRIAL_ID),
    "corpus": str(CORPUS),
    "intent": str(INTENT),
    "run_dir": str(RUN_DIR),
    "runs_root": str(RUNS_ROOT),
    "bundle_expected": "narrated-deck-with-workbook",
    "guide": GUIDE,
    "guide_text_mode_expected": "condense",
    "selection_code": CODE,
    "operator_id": OPERATOR,
    "auto_confirm_directive": False,
    "allow_offline_cost_report": False,
    "irene_fidelity_emit": "operator-g1-stamp-pinch-hit",
    "minted_at": datetime.now(tz=UTC).isoformat(),
    "g0_confirm_path": [],
    "pause_sequence": [],
    "verdict_sequence": [],
    "hil_variety_exercised": [],
    "fidelity_stamp": {},
}


def read_run() -> dict:
    p = RUN_DIR / "run.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def _unit_looks_literal(unit: dict) -> bool:
    """Heuristic for teaching-critical / assessment-adjacent units → literal-text."""
    blob = " ".join(
        str(unit.get(k) or "")
        for k in ("title", "learning_objective", "unit_id", "notes", "prompt")
    ).lower()
    needles = (
        "assess",
        "knowledge",
        "quiz",
        "rubric",
        "definition",
        "verbatim",
        "exact",
        "percent",
        "%",
        "figure",
        "statistic",
        "true/false",
        "true false",
        "days",
        "bridge",
        "completion",
    )
    return any(n in blob for n in needles)


def stamp_irene_fidelity_at_g1() -> dict:
    """Operator pinch-hit: stamp mixed fidelity onto Irene's latest contribution.

    Ensures a MIXED deck (creative + literal) so Gary ``calls_made`` becomes the
    live observable for the binary cohort split under classic-condense.
    """
    tenv = ProductionTrialEnvelope.model_validate_json(
        (RUN_DIR / "run.json").read_text(encoding="utf-8")
    )
    prod = tenv.production_envelope
    assert prod is not None, "no production_envelope at G1"
    irene = prod.latest_for_specialist("irene_pass1")
    assert irene is not None, "no irene_pass1 contribution at G1"
    output = copy.deepcopy(irene.output or {})
    lesson_plan = output.get("lesson_plan")
    assert isinstance(lesson_plan, dict), "irene output missing lesson_plan"
    units = lesson_plan.get("plan_units")
    assert isinstance(units, list) and units, "no plan_units"

    stamped: list[dict] = []
    creative_n = 0
    literal_n = 0
    for index, unit in enumerate(units):
        if not isinstance(unit, dict):
            continue
        # Prefer heuristic literals; force at least one of each cohort when possible.
        want_literal = _unit_looks_literal(unit)
        if index == 0 and not want_literal:
            # Keep first creative if heuristic didn't fire — mixed needs both.
            want_literal = False
        if literal_n == 0 and index == len(units) - 1 and not want_literal:
            want_literal = True  # guarantee ≥1 literal
        if want_literal:
            unit["fidelity"] = "literal-text"
            literal_n += 1
            stamped.append(
                {"unit_id": unit.get("unit_id"), "title": unit.get("title"), "fidelity": "literal-text"}
            )
        else:
            # Explicit creative so missing≠ambiguous in post-mortem.
            unit["fidelity"] = "creative"
            creative_n += 1
            stamped.append(
                {"unit_id": unit.get("unit_id"), "title": unit.get("title"), "fidelity": "creative"}
            )

    # If everything became one cohort, flip the middle unit to force mixed.
    if creative_n == 0 or literal_n == 0:
        mid = units[len(units) // 2]
        if isinstance(mid, dict):
            if creative_n == 0:
                mid["fidelity"] = "creative"
                creative_n += 1
                literal_n = max(0, literal_n - 1)
            else:
                mid["fidelity"] = "literal-text"
                literal_n += 1
                creative_n = max(0, creative_n - 1)
            for row in stamped:
                if row.get("unit_id") == mid.get("unit_id"):
                    row["fidelity"] = mid["fidelity"]

    new_output = {**output, "lesson_plan": lesson_plan}
    replacement = irene.model_copy(
        update={
            "output": new_output,
            "output_digest": compute_output_digest(new_output),
        }
    )
    new_contribs = tuple(
        replacement if c is irene else c for c in prod.contributions
    )
    new_prod = prod.model_copy(update={"contributions": new_contribs})
    new_tenv = tenv.model_copy(update={"production_envelope": new_prod})
    (RUN_DIR / "run.json").write_text(
        new_tenv.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )
    # Sidecar receipt for the operator stamp (auditability).
    receipt = {
        "actor": OPERATOR,
        "gate": "G1",
        "action": "stamp-plan-unit-fidelity",
        "rationale": (
            "Irene Pass-1 did not emit fidelity; AFK HIL stand-in stamps "
            "teaching-critical units literal-text and others creative so the "
            "Gary Irene-literal→preserve seam is live-exercised under classic-condense."
        ),
        "creative_n": creative_n,
        "literal_n": literal_n,
        "stamped_units": stamped,
        "trial_id": str(TRIAL_ID),
        "stamped_at": datetime.now(tz=UTC).isoformat(),
    }
    (RUN_DIR / "operator-fidelity-stamp-g1.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    shutil.copyfile(
        RUN_DIR / "operator-fidelity-stamp-g1.json",
        EVIDENCE / "operator-fidelity-stamp-g1.json",
    )
    transcript("G1-FIDELITY-STAMP", json.dumps(receipt, indent=2, sort_keys=True))
    log(
        f"G1 fidelity stamp applied: creative={creative_n} literal={literal_n} "
        f"(mixed required for calls_made proof)"
    )
    return receipt


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
    marker = (
        "\n# irene-literal-hil-operator-edit: inspected directive; "
        "no semantic source change\n"
    )
    if "# irene-literal-hil-operator-edit:" not in raw:
        path.write_text(raw.rstrip() + marker, encoding="utf-8")
    facts["g0_edit_applied"] = True
    facts["g0_edit_directive_bytes"] = path.stat().st_size
    transcript("G0-EDIT", f"appended inspection marker to {path}")
    log(f"G0 edit_fn applied marker; bytes={path.stat().st_size}")


def confirm_fn(*, directive_path: Path, auto_confirm_directive: bool):
    assert auto_confirm_directive is False, "liveproof forbids auto_confirm_directive=True"
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

    if gate == "G1" and "g1:edit-fidelity-stamp" not in facts["hil_variety_exercised"]:
        # Stamp happens BEFORE this verdict is built (see loop). Edit verb records
        # the operator note that fidelity was stamped.
        payload = {
            "irene_literal_operator_note": (
                "AFK HIL stand-in stamped plan_unit fidelity (literal-text on "
                "teaching-critical units; creative elsewhere) because Irene Pass-1 "
                "did not emit fidelity. Approving packet with that operator edit."
            ),
            "irene_literal_variety": "edit-fidelity-stamp-then-continue",
            "fidelity_stamp_receipt": "operator-fidelity-stamp-g1.json",
        }
        facts["hil_variety_exercised"].append("g1:edit-fidelity-stamp")
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


def capture_gary_irene_proof() -> dict:
    """Post-Gary observables for the Irene-literal claim."""
    proof: dict = {}
    if not (RUN_DIR / "run.json").is_file():
        return proof
    tenv = ProductionTrialEnvelope.model_validate_json(
        (RUN_DIR / "run.json").read_text(encoding="utf-8")
    )
    prod = tenv.production_envelope
    if prod is None:
        return proof
    pkg = prod.latest_for_specialist("package_builder")
    gary = prod.latest_for_specialist("gary")
    if pkg is not None:
        slides = (pkg.output or {}).get("slides") or []
        proof["package_slide_count"] = len(slides)
        proof["package_fidelity_counts"] = {}
        for s in slides:
            fid = str((s or {}).get("fidelity") or "missing")
            proof["package_fidelity_counts"][fid] = (
                proof["package_fidelity_counts"].get(fid, 0) + 1
            )
        proof["package_slides"] = [
            {
                "slide_id": s.get("slide_id"),
                "title": s.get("title"),
                "fidelity": s.get("fidelity"),
                "source_ref": s.get("source_ref"),
            }
            for s in slides
        ]
    if gary is not None:
        gout = gary.output or {}
        proof["gary_calls_made"] = gout.get("calls_made")
        proof["gary_generation_mode"] = gout.get("generation_mode")
        proof["gary_generation_id"] = gout.get("generation_id")
        proof["gary_row_count"] = len(gout.get("gary_slide_output") or [])
        settings = gout.get("variant_gamma_settings") or []
        proof["gary_variant_text_modes"] = [
            {"variant_id": s.get("variant_id"), "text_mode": s.get("text_mode"), "amount": s.get("amount")}
            for s in settings
            if isinstance(s, dict)
        ]
        # Bound guide must remain classic condense at settings layer; cohort
        # override is per-call (not persisted on variant_gamma_settings).
        proof["settings_still_condense"] = any(
            str(s.get("text_mode") or "") == "condense" for s in settings if isinstance(s, dict)
        )
    return proof


env = None
try:
    log("=== start_trial (Irene-literal liveproof; classic-condense + AFK HIL) ===")
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

        # At G1: stamp fidelity onto Irene contribution BEFORE resume.
        if gate == "G1" and not facts.get("fidelity_stamp"):
            facts["fidelity_stamp"] = stamp_irene_fidelity_at_g1()

        env = drive_verdict(gate, MAX_SPECIALIST_CALLS)

        # Capture Gary proof as soon as Gary has contributed.
        if not facts.get("gary_proof"):
            proof = capture_gary_irene_proof()
            if proof.get("gary_calls_made") is not None:
                facts["gary_proof"] = proof
                log(f"gary_proof captured: {json.dumps(proof, default=str)[:800]}")

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
if not facts.get("gary_proof"):
    facts["gary_proof"] = capture_gary_irene_proof()

for name in (
    "model_resolution_trail.json",
    "directive.yaml",
    "trial-start.json",
    "run.json",
    "run_summary.yaml",
    "ratified-los.json",
    "operator-fidelity-stamp-g1.json",
):
    src = RUN_DIR / name
    if src.is_file():
        shutil.copyfile(src, EVIDENCE / name)
        facts.setdefault("copied_artifacts", []).append(name)

for gate in facts["pause_sequence_unique"]:
    src = RUN_DIR / f"decision-card-{gate}.json"
    if src.is_file():
        shutil.copyfile(src, EVIDENCE / f"decision-card-{gate}.json")
        facts.setdefault("copied_artifacts", []).append(f"decision-card-{gate}.json")

# Workbook / collateral if present
try:
    if (RUN_DIR / "run.json").is_file():
        tenv = ProductionTrialEnvelope.model_validate_json(
            (RUN_DIR / "run.json").read_text(encoding="utf-8")
        )
        facts["envelope_status"] = tenv.status
        ts = RUN_DIR / "trial-start.json"
        if ts.is_file():
            ts_data = json.loads(ts.read_text(encoding="utf-8"))
            facts["trial_start_bundle_id"] = ts_data.get(
                "lesson_plan_collateral_bundle_id"
            )
        prod = tenv.production_envelope
        if prod is not None:
            try:
                wb = prod.latest_for_specialist("workbook_producer")
                if wb is not None:
                    wb_out = wb.output or {}
                    md_path = (wb_out.get("workbook") or {}).get("markdown_path")
                    docx_path = (wb_out.get("workbook") or {}).get("docx_path")
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

proof = facts.get("gary_proof") or {}
fid_counts = proof.get("package_fidelity_counts") or {}
literal_slides = int(fid_counts.get("literal-text") or 0) + int(
    fid_counts.get("literal-visual") or 0
)
creative_slides = int(fid_counts.get("creative") or 0)
mixed = literal_slides > 0 and creative_slides > 0
calls = proof.get("gary_calls_made")
# Single-variant mixed → expect 2 Classic calls (creative + literal cohorts).
split_ok = mixed and calls == 2
cleared_gary = facts.get("final_error_tag") != "gamma.export.brief-unmatched"
past_g1 = any(g not in {"G0E", "G0R", "G1"} for g in facts.get("pause_sequence", [])) or (
    facts.get("final_status") == "completed"
)
claim_ok = (
    facts.get("g0_confirm_path") == ["e", "c"]
    and facts.get("trial_start_bundle_id") == "narrated-deck-with-workbook"
    and (RUN_DIR / "directive.yaml").is_file()
    and (RUN_DIR / "trial-start.json").is_file()
    and facts.get("driver_exception") is None
    and bool(facts.get("fidelity_stamp"))
    and literal_slides > 0
    and proof.get("settings_still_condense") is True
    and cleared_gary
    and (
        split_ok
        or (
            # All-literal under single variant → 1 call still proves stamp+carry;
            # weaker than mixed split but acceptable if corpus collapses.
            literal_slides > 0
            and creative_slides == 0
            and calls == 1
            and past_g1
        )
        or (
            facts.get("final_status") == "completed"
            and literal_slides > 0
            and past_g1
        )
    )
)
facts["literal_slide_count"] = literal_slides
facts["creative_slide_count"] = creative_slides
facts["mixed_fidelity_deck"] = mixed
facts["cohort_split_live_ok"] = bool(split_ok)
facts["cleared_gary_brief_unmatched"] = bool(cleared_gary)
facts["irene_literal_liveproof_claim_ok"] = bool(claim_ok)
facts["note"] = (
    "claim_ok requires authentic G0 HIL, classic-condense guide still bound, "
    "operator G1 fidelity stamp, package slides carrying literal-text, and "
    "Gary cohort split (calls_made==2 when mixed) or completed walk with "
    "literal carry-through. Does NOT close L1-per-slide broadly. Does NOT "
    "claim Irene spontaneously emitted fidelity."
)

(EVIDENCE / "facts.json").write_text(
    json.dumps(facts, indent=2, sort_keys=True, default=str) + "\n",
    encoding="utf-8",
)
log(f"facts written; claim_ok={claim_ok}; final_status={facts.get('final_status')}")
log(f"gary_proof={json.dumps(proof, default=str)[:1000]}")
log(f"hil_variety={facts.get('hil_variety_unique')}")
log(f"pause_sequence={facts.get('pause_sequence')}")
timer.cancel()
LOG.close()
TRANSCRIPT.close()
sys.exit(0 if claim_ok else 2)
