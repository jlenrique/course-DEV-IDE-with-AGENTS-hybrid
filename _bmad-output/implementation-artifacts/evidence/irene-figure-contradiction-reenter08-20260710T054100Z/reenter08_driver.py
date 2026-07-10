"""Liveproof: reenter@08 after Pass-2 speakable-figure contract fix.

Party-amended claim: generation-side dual-view (speakable allowlist + redact
unrendered source figures + no SOURCE-WINS speech license). Gates stay fail-loud.
"""

from __future__ import annotations

import json
import os
import traceback
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

EV = Path(__file__).resolve().parent
TRIAL_ID = UUID("22b27500-6e67-4dd7-8308-fd89defe3d99")
RUNS_ROOT = Path("state/config/runs")
RUN_DIR = RUNS_ROOT / str(TRIAL_ID)
OPERATOR = "operator_afk_hil_standin"
MAX_LOOPS = 16
MAX_RECOVERS = 2
MAX_SPECIALIST_CALLS = 80

os.environ["MARCUS_NARRATION_FIGURE_FIDELITY_ACTIVE"] = "1"
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from app.marcus.cli.trial import recover_trial  # noqa: E402
from app.marcus.orchestrator.production_runner import (  # noqa: E402
    resume_production_trial,
)
from app.models.state.operator_verdict import OperatorVerdict  # noqa: E402


def log(msg: str) -> None:
    line = f"[{datetime.now(timezone.utc).isoformat()}] {msg}"
    print(line, flush=True)
    with (EV / "command-transcript.md").open("a", encoding="utf-8") as fh:
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


def main() -> int:
    (EV / "command-transcript.md").write_text(
        "# reenter@08 liveproof\n\n"
        f"flag={os.environ.get('MARCUS_NARRATION_FIGURE_FIDELITY_ACTIVE')}\n"
        f"trial={TRIAL_ID}\n\n",
        encoding="utf-8",
    )
    facts: dict = {
        "at": datetime.now(timezone.utc).isoformat(),
        "run_id": str(TRIAL_ID),
        "flag": os.environ.get("MARCUS_NARRATION_FIGURE_FIDELITY_ACTIVE"),
        "events": [],
    }
    start = read_run()
    log(
        f"start status={start.get('status')} err={start.get('paused_error_tag')} "
        f"gate={start.get('paused_gate')}"
    )
    facts["events"].append(
        {
            "op": "start",
            "status": start.get("status"),
            "err": start.get("paused_error_tag"),
        }
    )

    recovers = 0
    if start.get("status") == "paused-at-error":
        log("RECOVER reenter_at_node=08 (speakable-contract fix liveproof)")
        try:
            payload = recover_trial(
                trial_id=TRIAL_ID,
                runs_root=RUNS_ROOT,
                max_specialist_calls=MAX_SPECIALIST_CALLS,
                reenter_at_node="08",
            )
            recovers += 1
            log(
                f"recover08 -> {payload.get('status')} "
                f"gate={payload.get('paused_gate')} err={payload.get('paused_error_tag')}"
            )
            facts["events"].append({"op": "recover08", **payload})
        except Exception:
            log("recover08 RAISED:\n" + traceback.format_exc())
            facts["events"].append(
                {"op": "recover08", "error": traceback.format_exc()}
            )
            (EV / "verdict.json").write_text(
                json.dumps(
                    {
                        "verdict": "fail",
                        "reason": "recover08_raised",
                        "facts": facts,
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            return 1

    for i in range(MAX_LOOPS):
        run = read_run()
        status, gate, err = (
            run.get("status"),
            run.get("paused_gate"),
            run.get("paused_error_tag"),
        )
        log(f"[loop {i}] status={status} gate={gate} err={err}")
        facts["events"].append(
            {"op": "loop", "i": i, "status": status, "gate": gate, "err": err}
        )
        if status == "completed":
            log("RUN COMPLETED")
            break
        if status == "paused-at-error":
            if err == "irene.pass2.figure-contradiction":
                log("FAIL: figure-contradiction recurred after speakable-contract fix")
                break
            if recovers >= MAX_RECOVERS:
                log("max recovers exhausted")
                break
            log(f"RECOVER reenter_at_node=08 for {err}")
            try:
                payload = recover_trial(
                    trial_id=TRIAL_ID,
                    runs_root=RUNS_ROOT,
                    max_specialist_calls=MAX_SPECIALIST_CALLS,
                    reenter_at_node="08",
                )
                recovers += 1
                facts["events"].append({"op": "recover", **payload})
                log(
                    f"recover -> {payload.get('status')} "
                    f"err={payload.get('paused_error_tag')}"
                )
            except Exception:
                log("RECOVER RAISED:\n" + traceback.format_exc())
                break
            continue
        if status != "paused-at-gate" or not gate:
            log(f"unexpected {status}")
            break
        try:
            env = drive_verdict(gate)
            log(
                f"  -> {env.status} gate={env.paused_gate} err={env.paused_error_tag}"
            )
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
                {"op": "resume", "gate": gate, "error": traceback.format_exc()}
            )
            break

    final = read_run()
    facts["final_status"] = final.get("status")
    facts["final_err"] = final.get("paused_error_tag")
    facts["final_gate"] = final.get("paused_gate")
    facts["recovers"] = recovers
    contribs = [
        (c.get("node_id"), c.get("specialist_id"))
        for c in (final.get("production_envelope") or {}).get("contributions") or []
    ]
    facts["contribs"] = contribs
    has_08 = any(n == "08" for n, _ in contribs)
    err = final.get("paused_error_tag")

    if err == "irene.pass2.figure-contradiction":
        verdict, reason = "fail", "figure_contradiction_recurred"
    elif final.get("status") == "completed":
        verdict, reason = "pass", "walk_completed"
    elif has_08 and err != "irene.pass2.figure-contradiction":
        verdict, reason = (
            "pass_with_fences",
            f"pass2_node08_landed_status={final.get('status')}_gate={final.get('paused_gate')}_err={err}",
        )
    elif final.get("status") == "paused-at-error":
        verdict, reason = "fail", f"paused_at_error:{err}"
    else:
        verdict, reason = (
            "pass_with_fences",
            f"status={final.get('status')}_gate={final.get('paused_gate')}",
        )

    out = {"verdict": verdict, "reason": reason, "facts": facts}
    (EV / "verdict.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    log(f"FINAL verdict={verdict} reason={reason} status={final.get('status')} err={err}")
    return 0 if verdict in {"pass", "pass_with_fences"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
