"""Irene-literal AUTHENTIC liveproof — AFK HIL (no fidelity stamp).

Goal
----
Production walk under classic ``condense``+Minimal where:

1. Irene Pass-1 **emits** at least one ``fidelity: literal-text`` plan unit
   (post emit-recovery ``6783b54b``) — no G1 operator stamp.
2. Package briefs carry that fidelity onto slides.
3. Gary binary-splits cohorts and forces ``text_mode=preserve`` (amount absent)
   on the literal cohort while the bound styleguide remains classic condense.

Authenticity contract
---------------------
- REAL compose / Gamma / OpenAI / LangSmith.
- NO ``--allow-offline-cost-report``; NO ``--auto-confirm-directive``.
- Guide: ``hil-2026-apc-crossroads-classic`` (NOT preserve sibling).
- NO G1 fidelity stamp / mock injection.

Claim envelope (driver-local)
-----------------------------
Closes live wire of Irene-emit → Gary-honor under classic-condense.
Does NOT close L1-per-slide broadly or literal-visual production streamline.
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
    f"env OK; GUIDE={GUIDE}; emit-recovery HEAD expected; "
    f"NO fidelity stamp on this driver"
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
from app.models.runtime.production_trial_envelope import (  # noqa: E402
    ProductionTrialEnvelope,
)
from app.models.state.operator_verdict import OperatorVerdict  # noqa: E402
from app.runtime.economics import RUNS_ROOT  # noqa: E402
from app.styleguide.resolver import resolve_styleguide  # noqa: E402

_classic = resolve_styleguide(GUIDE)
assert _classic.get("text_mode") == "condense", _classic.get("text_mode")
log(
    f"styleguide {GUIDE}: text_mode={_classic.get('text_mode')} "
    f"amount={_classic.get('amount')}"
)

TRIAL_ID = uuid4()
RUN_DIR = RUNS_ROOT / str(TRIAL_ID)
CODE = build_selection_code(TRIAL_ID.hex, {"A": GUIDE})

facts: dict = {
    "story": "irene-literal-authentic-liveproof-classic-condense",
    "claim_envelope": (
        "Authentic Irene Pass-1 fidelity emit + Gary preserve-over-condense under "
        "hil-2026-apc-crossroads-classic. No G1 stamp. Does NOT close L1-per-slide "
        "broadly or literal-visual production streamline."
    ),
    "head_commit_at_launch": "6783b54b",
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
    "irene_fidelity_emit": "authentic-pass1-only-no-stamp",
    "minted_at": datetime.now(tz=UTC).isoformat(),
    "g0_confirm_path": [],
    "pause_sequence": [],
    "verdict_sequence": [],
    "hil_variety_exercised": [],
}


def read_run() -> dict:
    p = RUN_DIR / "run.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def observe_irene_fidelity() -> dict:
    """Read Irene Pass-1 contribution fidelity — observe only, never stamp."""
    obs: dict = {"observed_at": datetime.now(tz=UTC).isoformat()}
    if not (RUN_DIR / "run.json").is_file():
        obs["error"] = "no run.json"
        return obs
    tenv = ProductionTrialEnvelope.model_validate_json(
        (RUN_DIR / "run.json").read_text(encoding="utf-8")
    )
    prod = tenv.production_envelope
    if prod is None:
        obs["error"] = "no production_envelope"
        return obs
    irene = prod.latest_for_specialist("irene_pass1")
    if irene is None:
        obs["error"] = "no irene_pass1 contribution"
        return obs
    output = irene.output or {}
    lesson_plan = output.get("lesson_plan") or {}
    units = lesson_plan.get("plan_units") or []
    counts: dict[str, int] = {}
    rows: list[dict] = []
    for unit in units:
        if not isinstance(unit, dict):
            continue
        fid = unit.get("fidelity")
        key = str(fid) if fid else "missing"
        counts[key] = counts.get(key, 0) + 1
        rows.append(
            {
                "unit_id": unit.get("unit_id"),
                "title": unit.get("title"),
                "fidelity": fid,
            }
        )
    obs["unit_count"] = len(rows)
    obs["fidelity_counts"] = counts
    obs["units"] = rows
    obs["literal_text_n"] = int(counts.get("literal-text") or 0)
    obs["literal_visual_n"] = int(counts.get("literal-visual") or 0)
    obs["creative_n"] = int(counts.get("creative") or 0)
    obs["missing_n"] = int(counts.get("missing") or 0)
    # Copy irene-pass1.md if present under run dir or default runs/
    for candidate in (
        RUN_DIR / "irene-pass1.md",
        REPO / "runs" / str(TRIAL_ID) / "irene-pass1.md",
    ):
        if candidate.is_file():
            shutil.copyfile(candidate, EVIDENCE / "irene-pass1.md")
            obs["irene_pass1_md"] = str(candidate)
            break
    return obs


def capture_gary_irene_proof() -> dict:
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
            {
                "variant_id": s.get("variant_id"),
                "text_mode": s.get("text_mode"),
                "amount": s.get("amount"),
            }
            for s in settings
            if isinstance(s, dict)
        ]
        proof["settings_still_condense"] = any(
            str(s.get("text_mode") or "") == "condense"
            for s in settings
            if isinstance(s, dict)
        )
        # Mixed-cohort export filenames are a live witness of the split.
        export_dir = RUN_DIR / "exports"
        if export_dir.is_dir():
            proof["export_names"] = sorted(p.name for p in export_dir.glob("gary_*.png"))
        else:
            # Gary may write under a nested path — scan run dir lightly.
            proof["export_names"] = sorted(
                p.name for p in RUN_DIR.rglob("gary_*.png")
            )[:20]
    return proof


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
        "\n# irene-literal-authentic-hil-edit: inspected directive; "
        "no semantic source change; NO fidelity stamp\n"
    )
    if "# irene-literal-authentic-hil-edit:" not in raw:
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

    if gate == "G1" and "g1:edit-inspect" not in facts["hil_variety_exercised"]:
        payload = {
            "irene_literal_authentic_note": (
                "AFK HIL inspected G1; observing Irene-emitted fidelity only — "
                "NO operator fidelity stamp."
            ),
            "irene_fidelity_observation": facts.get("irene_fidelity_observation"),
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
            {
                "gate": gate,
                "verb": verb,
                "edit_payload": edit_payload,
                "card_id": str(kwargs["card_id"]),
            },
            indent=2,
            sort_keys=True,
            default=str,
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
    log("=== start_trial (AUTHENTIC Irene-literal; classic-condense; NO stamp) ===")
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

        if gate == "G1" and not facts.get("irene_fidelity_observation"):
            obs = observe_irene_fidelity()
            facts["irene_fidelity_observation"] = obs
            log(f"Irene fidelity observation: {json.dumps(obs.get('fidelity_counts'), default=str)}")
            if int(obs.get("literal_text_n") or 0) == 0:
                log(
                    "WARNING: Irene emitted zero literal-text units — "
                    "Gary honor path may not fire; continuing without stamp"
                )

        env = drive_verdict(gate, MAX_SPECIALIST_CALLS)

        if not facts.get("gary_proof"):
            proof = capture_gary_irene_proof()
            if proof.get("gary_calls_made") is not None:
                facts["gary_proof"] = proof
                log(f"gary_proof captured: {json.dumps(proof, default=str)[:900]}")

        if env.status == "paused-at-error":
            log(f"ERROR-PAUSE after {gate}: {env.paused_error_tag}")
            break
        if env.status == "completed":
            log("RUN COMPLETED after resume")
            break
except BaseException:
    log("DRIVER RAISED:\n" + traceback.format_exc())
    facts["driver_exception"] = traceback.format_exc()

run = read_run()
facts["final_status"] = run.get("status")
facts["final_paused_gate"] = run.get("paused_gate")
facts["final_error_tag"] = run.get("paused_error_tag")
facts["pause_sequence_unique"] = list(dict.fromkeys(facts["pause_sequence"]))
facts["hil_variety_unique"] = list(dict.fromkeys(facts["hil_variety_exercised"]))
facts["finished_at"] = datetime.now(tz=UTC).isoformat()
if not facts.get("irene_fidelity_observation"):
    facts["irene_fidelity_observation"] = observe_irene_fidelity()
if not facts.get("gary_proof"):
    facts["gary_proof"] = capture_gary_irene_proof()

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

for gate in facts["pause_sequence_unique"]:
    src = RUN_DIR / f"decision-card-{gate}.json"
    if src.is_file():
        shutil.copyfile(src, EVIDENCE / f"decision-card-{gate}.json")
        facts.setdefault("copied_artifacts", []).append(f"decision-card-{gate}.json")

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

obs = facts.get("irene_fidelity_observation") or {}
proof = facts.get("gary_proof") or {}
fid_counts = proof.get("package_fidelity_counts") or {}
literal_slides = int(fid_counts.get("literal-text") or 0) + int(
    fid_counts.get("literal-visual") or 0
)
creative_slides = int(fid_counts.get("creative") or 0) + int(fid_counts.get("missing") or 0)
mixed = literal_slides > 0 and creative_slides > 0
calls = proof.get("gary_calls_made")
split_ok = mixed and calls == 2
irene_literal = int(obs.get("literal_text_n") or 0) > 0
cleared_gary = facts.get("final_error_tag") != "gamma.export.brief-unmatched"
past_g1 = any(g not in {"G0E", "G0R", "G1"} for g in facts.get("pause_sequence", [])) or (
    facts.get("final_status") == "completed"
)
exports = proof.get("export_names") or []
literal_export_witness = any("literal" in str(n) for n in exports)

claim_ok = (
    facts.get("g0_confirm_path") == ["e", "c"]
    and facts.get("trial_start_bundle_id") == "narrated-deck-with-workbook"
    and (RUN_DIR / "directive.yaml").is_file()
    and (RUN_DIR / "trial-start.json").is_file()
    and facts.get("driver_exception") is None
    and irene_literal
    and literal_slides > 0
    and proof.get("settings_still_condense") is True
    and cleared_gary
    and past_g1
    and (
        split_ok
        or (literal_slides > 0 and creative_slides == 0 and calls == 1)
        or (
            facts.get("final_status") == "completed"
            and literal_slides > 0
            and (split_ok or literal_export_witness or calls == 2)
        )
    )
)
facts["irene_emitted_literal_text"] = bool(irene_literal)
facts["literal_slide_count"] = literal_slides
facts["creative_or_untagged_slide_count"] = creative_slides
facts["mixed_fidelity_deck"] = mixed
facts["cohort_split_live_ok"] = bool(split_ok)
facts["literal_export_witness"] = bool(literal_export_witness)
facts["cleared_gary_brief_unmatched"] = bool(cleared_gary)
facts["irene_literal_authentic_claim_ok"] = bool(claim_ok)
facts["note"] = (
    "claim_ok requires authentic G0 HIL, classic-condense still bound, "
    "Irene-emitted literal-text (no stamp), package carry-through, and Gary "
    "cohort split (calls_made==2 when mixed) or completed walk with literal "
    "carry. Does NOT close L1-per-slide broadly."
)

(EVIDENCE / "facts.json").write_text(
    json.dumps(facts, indent=2, sort_keys=True, default=str) + "\n",
    encoding="utf-8",
)
log(f"facts written; claim_ok={claim_ok}; final_status={facts.get('final_status')}")
log(f"irene_obs={json.dumps(obs.get('fidelity_counts'), default=str)}")
log(f"gary_proof={json.dumps(proof, default=str)[:1000]}")
log(f"hil_variety={facts.get('hil_variety_unique')}")
log(f"pause_sequence={facts.get('pause_sequence')}")
timer.cancel()
LOG.close()
TRANSCRIPT.close()
sys.exit(0 if claim_ok else 2)
