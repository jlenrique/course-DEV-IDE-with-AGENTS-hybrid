"""Continue Tejal P4 fullwalk after in-situ VariantSelectionError patch.

Trial 22b27500… paused at irene.pass2.figure-contradiction; recover to 07
failed because variant picks outlived dropped Gary. Patch: defer apply when
Gary absent; re-apply after Gary dispatch. This script recovers + gate-walks
to completion (fidelity flag ON; no Descript publish).
"""
from __future__ import annotations

import json
import os
import sys
import traceback
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

REPO = Path(r"C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS-hybrid")
EVIDENCE = (
    REPO
    / "_bmad-output/implementation-artifacts/evidence"
    / "tejal-p4-fullwalk-20260710T005021Z"
)
TRIAL_ID = UUID("22b27500-6e67-4dd7-8308-fd89defe3d99")
OPERATOR = "juanl"
MAX_SPECIALIST_CALLS = 50
MAX_GATE_LOOPS = 40
MAX_RECOVERS = 4

sys.path.insert(0, str(REPO))
os.chdir(REPO)
os.environ["PYTHONIOENCODING"] = "utf-8"

from dotenv import load_dotenv  # noqa: E402

load_dotenv(REPO / ".env", override=True)
os.environ["MARCUS_NARRATION_FIGURE_FIDELITY_ACTIVE"] = "1"

from app.marcus.cli.trial import recover_trial  # noqa: E402
from app.marcus.orchestrator.production_runner import resume_production_trial  # noqa: E402
from app.models.state.operator_verdict import OperatorVerdict  # noqa: E402
from app.runtime.economics import RUNS_ROOT  # noqa: E402

RUN_DIR = RUNS_ROOT / str(TRIAL_ID)
LOG = open(EVIDENCE / "continue-log.txt", "a", encoding="utf-8")


def log(msg: str) -> None:
    line = f"[{datetime.now(tz=UTC).isoformat()}] {msg}"
    print(line, flush=True)
    LOG.write(line + "\n")
    LOG.flush()


def read_run() -> dict:
    p = RUN_DIR / "run.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


FIDELITY = {
    "irene.pass2.figure-unsourced",
    "irene.pass2.figure-source-deck-conflict",
    "irene.pass2.figure-positive-carry-miss",
    "irene.pass2.figure-contradiction",
}
REENTER = {
    "irene.pass2.figure-contradiction": "08",  # re-roll Pass-2 after Gary restored
    "irene.pass2.figure-unsourced": "08",
    "irene.pass2.figure-positive-carry-miss": "08",
    "irene.pass2.figure-source-deck-conflict": "07",
    "gamma.export.brief-unmatched": "07",
    "irene.pass2.slide-join-failed": "08",
}


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
    log("=== continue after in-situ VariantSelectionError patch ===")
    run = read_run()
    log(f"start status={run.get('status')} err={run.get('paused_error_tag')}")

    recovers = 0
    # First: restore Gary+ path from 07 (envelope was emptied by failed recover).
    if run.get("status") == "paused-at-error":
        log("RECOVER reenter_at_node=07 (restore Gary path after drop)")
        try:
            payload = recover_trial(
                trial_id=TRIAL_ID,
                runs_root=RUNS_ROOT,
                max_specialist_calls=MAX_SPECIALIST_CALLS,
                reenter_at_node="07",
            )
            recovers += 1
            log(f"recover07 -> {payload.get('status')} err={payload.get('paused_error_tag')}")
        except Exception:
            log("recover07 RAISED:\n" + traceback.format_exc())
            return 1

    for i in range(MAX_GATE_LOOPS):
        run = read_run()
        status, gate, err = run.get("status"), run.get("paused_gate"), run.get(
            "paused_error_tag"
        )
        log(f"[loop {i}] status={status} gate={gate} err={err}")
        if status == "completed":
            log("RUN COMPLETED")
            break
        if status == "paused-at-error":
            if recovers >= MAX_RECOVERS:
                log("max recovers exhausted")
                break
            node = REENTER.get(err or "", "08")
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
            except Exception:
                log("RECOVER RAISED:\n" + traceback.format_exc())
                break
            continue
        if status != "paused-at-gate" or not gate:
            log(f"unexpected {status}")
            break
        env = drive_verdict(gate)
        log(f"  -> {env.status} gate={env.paused_gate} err={env.paused_error_tag}")
        if env.status == "completed":
            break

    run = read_run()
    (EVIDENCE / "continue-final.json").write_text(
        json.dumps(
            {
                "status": run.get("status"),
                "err": run.get("paused_error_tag"),
                "recovers": recovers,
                "at": datetime.now(tz=UTC).isoformat(),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    log(f"FINAL status={run.get('status')} err={run.get('paused_error_tag')}")
    LOG.close()
    return 0 if run.get("status") == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
