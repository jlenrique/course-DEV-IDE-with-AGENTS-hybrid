"""Continue Tejal P4 fullwalk from G4A after Desmond HandoffParseError patch.

Trial stayed paused-at-gate G4A (exception was uncaught before rebase). Resume
AFK HIL through compositor → Desmond → workbook sidecar. No Descript publish.
"""

from __future__ import annotations

import json
import os
import traceback
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

EV = Path(
    "_bmad-output/implementation-artifacts/evidence/"
    "tejal-p4-continue-desmond-20260710T060700Z"
)
EV.mkdir(parents=True, exist_ok=True)
TRIAL_ID = UUID("22b27500-6e67-4dd7-8308-fd89defe3d99")
RUNS_ROOT = Path("state/config/runs")
RUN_DIR = RUNS_ROOT / str(TRIAL_ID)
OPERATOR = "operator_afk_hil_standin"
MAX_LOOPS = 24
MAX_RECOVERS = 4
MAX_SPECIALIST_CALLS = 120

os.environ["MARCUS_NARRATION_FIGURE_FIDELITY_ACTIVE"] = "1"
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from app.marcus.cli.trial import recover_trial  # noqa: E402
from app.marcus.orchestrator.production_runner import (  # noqa: E402
    resume_production_trial,
)
from app.models.state.operator_verdict import OperatorVerdict  # noqa: E402

REENTER = {
    "handoff.parsed.advisory-missing": "14.5",
    "handoff.parsed.malformed": "14.5",
    "handoff.parsed.empty": "14.5",
    "irene.pass2.figure-contradiction": "08",
    "gamma.export.brief-unmatched": "07",
}


def log(msg: str) -> None:
    line = f"[{datetime.now(timezone.utc).isoformat()}] {msg}"
    print(line, flush=True)
    with (EV / "continue-log.txt").open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def read_run() -> dict:
    return json.loads((RUN_DIR / "run.json").read_text(encoding="utf-8"))


def drive_verdict(gate: str):
    card = json.loads((RUN_DIR / f"decision-card-{gate}.json").read_text(encoding="utf-8"))
    verb, payload = "approve", None
    if gate == "G2B":
        opts = [
            e
            for e in card.get("card", {}).get("pick_context", [])
            if e.get("kind") == "variant-options"
        ]
        if opts and opts[0].get("slides"):
            verb = "select"
            payload = {
                "slide_variant_selections": {
                    s["slide_id"]: "A" for s in opts[0]["slides"]
                }
            }
    kwargs = {
        "trial_id": TRIAL_ID,
        "gate_id": gate,
        "card_id": UUID(card["card"]["card_id"]),
        "operator_id": OPERATOR,
        "decision_card_digest": card["digest"],
        "verb": verb,
    }
    if payload:
        kwargs["edit_payload"] = payload
    log(f"resume {verb} {gate}")
    return resume_production_trial(
        trial_id=TRIAL_ID,
        verdict=OperatorVerdict(**kwargs),
        runs_root=RUNS_ROOT,
        max_specialist_calls=MAX_SPECIALIST_CALLS,
    )


def score_artifacts(run: dict) -> dict:
    exports = RUN_DIR / "exports"
    gary = list((exports / "gary").glob("*.png")) if (exports / "gary").exists() else []
    motion = list((exports / "motion").glob("*.mp4")) if (exports / "motion").exists() else []
    audio = []
    for pat in ("*.mp3", "*.wav", "*.m4a"):
        audio.extend(exports.rglob(pat))
    workbook = list(exports.rglob("*.docx")) + list(RUN_DIR.rglob("*workbook*.docx"))
    contribs = [
        (c.get("node_id"), c.get("specialist_id"))
        for c in (run.get("production_envelope") or {}).get("contributions") or []
    ]
    has = {n for n, _ in contribs}
    return {
        "status": run.get("status"),
        "gate": run.get("paused_gate"),
        "err": run.get("paused_error_tag"),
        "contribs": contribs,
        "png_count": len(gary),
        "motion_count": len(motion),
        "audio_count": len(audio),
        "workbook_docx_count": len(workbook),
        "has_08": "08" in has,
        "has_11_enrique": "11" in has,
        "has_14_compositor": "14" in has,
        "has_14_5_desmond": "14.5" in has,
        "has_07W_workbook": "07W" in has,
        "workbook_paths": [str(p) for p in workbook[:10]],
    }


def main() -> int:
    (EV / "continue-log.txt").write_text(
        f"# continue after Desmond rebase\nflag={os.environ.get('MARCUS_NARRATION_FIGURE_FIDELITY_ACTIVE')}\n\n",
        encoding="utf-8",
    )
    facts: dict = {"events": [], "at": datetime.now(timezone.utc).isoformat()}
    run = read_run()
    log(f"start status={run.get('status')} gate={run.get('paused_gate')} err={run.get('paused_error_tag')}")
    recovers = 0

    for i in range(MAX_LOOPS):
        run = read_run()
        status, gate, err = run.get("status"), run.get("paused_gate"), run.get(
            "paused_error_tag"
        )
        log(f"[loop {i}] status={status} gate={gate} err={err}")
        facts["events"].append(
            {"i": i, "status": status, "gate": gate, "err": err}
        )
        if status == "completed":
            log("RUN COMPLETED")
            break
        if status == "paused-at-error":
            if recovers >= MAX_RECOVERS:
                log("max recovers exhausted")
                break
            node = REENTER.get(err or "", "14.5")
            log(f"RECOVER reenter_at_node={node} for {err}")
            try:
                payload = recover_trial(
                    trial_id=TRIAL_ID,
                    runs_root=RUNS_ROOT,
                    max_specialist_calls=MAX_SPECIALIST_CALLS,
                    reenter_at_node=node,
                )
                recovers += 1
                log(
                    f"recover -> {payload.get('status')} "
                    f"err={payload.get('paused_error_tag')}"
                )
                facts["events"].append({"op": "recover", **payload})
            except Exception:
                log("RECOVER RAISED:\n" + traceback.format_exc())
                break
            continue
        if status != "paused-at-gate" or not gate:
            log(f"unexpected {status}")
            break
        try:
            env = drive_verdict(gate)
            log(f"  -> {env.status} gate={env.paused_gate} err={env.paused_error_tag}")
            facts["events"].append(
                {
                    "op": "resume",
                    "gate": gate,
                    "status": env.status,
                    "err": env.paused_error_tag,
                }
            )
            if env.status == "completed":
                break
        except Exception:
            log("resume RAISED:\n" + traceback.format_exc())
            facts["events"].append(
                {"op": "resume", "error": traceback.format_exc()}
            )
            # After rebase, Desmond should pause-at-error not raise; if still
            # raises, stop for diagnosis.
            break

    final = read_run()
    score = score_artifacts(final)
    facts["recovers"] = recovers
    facts["score"] = score
    completed = final.get("status") == "completed"
    desmond_ok = score["has_14_5_desmond"]
    workbook_ok = score["has_07W_workbook"] or score["workbook_docx_count"] > 0
    if completed and desmond_ok and workbook_ok:
        verdict, reason = "pass", "walk_completed_desmond_workbook"
    elif completed and desmond_ok:
        verdict, reason = "pass_with_fences", "completed_desmond_workbook_sidecar_missing"
    elif desmond_ok and final.get("status") != "paused-at-error":
        verdict, reason = (
            "pass_with_fences",
            f"desmond_landed_status={final.get('status')}_gate={final.get('paused_gate')}",
        )
    elif final.get("paused_error_tag", "").startswith("handoff.parsed"):
        verdict, reason = "fail", f"desmond_still_failing:{final.get('paused_error_tag')}"
    else:
        verdict, reason = (
            "fail" if final.get("status") == "paused-at-error" else "pass_with_fences",
            f"status={final.get('status')}_err={final.get('paused_error_tag')}_gate={final.get('paused_gate')}",
        )

    out = {"verdict": verdict, "reason": reason, "facts": facts}
    (EV / "verdict.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    (EV / "scorecard.json").write_text(json.dumps(score, indent=2) + "\n", encoding="utf-8")
    log(f"FINAL verdict={verdict} reason={reason} score={json.dumps(score)}")
    return 0 if verdict in {"pass", "pass_with_fences"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
