#!/usr/bin/env python3
"""R7 live evidence — hard-pause teeth before Irene Pass-2.

Proves on the real production seam (shared dispatch enforce + disposition I/O):

1. Flag ON → landing-point written
2. Pass-2 enforce raises (blocked)
3. Real disposition (approve|reject|defer) written
4. Pass-2 enforce proceeds
5. Advisory cannot unlock

Does not claim resume/recover completeness (TRAIL: tracy-gate-resume-recover).

Usage::

    python scripts/utilities/run_research_r7_live_evidence.py
"""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env", override=True)


def _stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def main() -> int:
    from app.marcus.orchestrator import research_detective_gate as gate
    from app.marcus.orchestrator.research_wiring import RESEARCH_DETECTIVE_LIVE_ENV
    from app.specialists.dispatch_errors import SpecialistDispatchError

    out_dir = (
        ROOT
        / "_bmad-output"
        / "implementation-artifacts"
        / "evidence"
        / f"research-r7-{_stamp()}"
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    run_dir = out_dir / "run"
    run_dir.mkdir(parents=True, exist_ok=True)
    trial_id = str(uuid4())

    # --- LIVE arm: flag ON ---
    os.environ[RESEARCH_DETECTIVE_LIVE_ENV] = "1"

    steps: list[dict] = []

    # 1) Landing point
    landing = gate.write_landing_point(run_dir, trial_id=trial_id, node_id="08")
    steps.append(
        {
            "step": "landing_point",
            "pass": landing.is_file(),
            "path": landing.as_posix(),
        }
    )

    # 2) Pass-2 blocked
    blocked = False
    block_tag = None
    try:
        gate.enforce_before_pass2(
            specialist_id="irene",
            node_id="08",
            run_dir=run_dir,
        )
    except gate.ResearchDetectiveGateError as exc:
        blocked = True
        block_tag = exc.tag
        assert isinstance(exc, SpecialistDispatchError)
    steps.append(
        {
            "step": "pass2_blocked",
            "pass": blocked and block_tag == gate.GATE_PENDING_TAG,
            "tag": block_tag,
        }
    )

    # 3) Advisory cannot unlock (write rejected by API + planted receipt)
    advisory_api_rejected = False
    try:
        gate.write_disposition(run_dir, "advisory")
    except ValueError:
        advisory_api_rejected = True
    gate.disposition_path(run_dir).write_text(
        json.dumps({"disposition": "advisory"}),
        encoding="utf-8",
    )
    advisory_still_blocked = False
    try:
        gate.enforce_before_pass2(
            specialist_id="irene",
            node_id="08",
            run_dir=run_dir,
        )
    except gate.ResearchDetectiveGateError as exc:
        advisory_still_blocked = exc.tag == gate.GATE_ADVISORY_TAG
    steps.append(
        {
            "step": "advisory_cannot_unlock",
            "pass": advisory_api_rejected and advisory_still_blocked,
        }
    )

    # 4) Real disposition unlocks
    disp_path = gate.write_disposition(
        run_dir,
        "approve",
        operator_id="live-r7",
        rationale="R7 live teeth proof — operator disposition after landing block",
        trial_id=trial_id,
    )
    proceeded = False
    try:
        gate.enforce_before_pass2(
            specialist_id="irene",
            node_id="08",
            run_dir=run_dir,
        )
        proceeded = True
    except gate.ResearchDetectiveGateError:
        proceeded = False
    steps.append(
        {
            "step": "disposition_then_proceed",
            "pass": proceeded and disp_path.is_file(),
            "disposition": "approve",
            "path": disp_path.as_posix(),
        }
    )

    # 5) Flag-OFF firewall (no raise even with empty sibling run)
    os.environ.pop(RESEARCH_DETECTIVE_LIVE_ENV, None)
    flag_off_ok = True
    try:
        gate.enforce_before_pass2(
            specialist_id="irene",
            node_id="08",
            run_dir=out_dir / "flag-off-empty",
        )
    except Exception:  # noqa: BLE001 — live verdict captures any leak
        flag_off_ok = False
    steps.append({"step": "flag_off_noop", "pass": flag_off_ok})

    # 6) Shared-dispatch import seam (production_runner wires the call)
    from app.marcus.orchestrator import production_runner as pr

    wired = "research_detective_gate" in pr.__dict__ or hasattr(
        pr, "research_detective_gate"
    )
    # Confirm source contains the enforce call (live seam presence).
    src = Path(pr.__file__).read_text(encoding="utf-8")
    seam_present = (
        "research_detective_gate.enforce_before_pass2" in src
        and "ResearchDetectiveGateError" in Path(gate.__file__).read_text(encoding="utf-8")
    )
    steps.append(
        {
            "step": "production_runner_seam",
            "pass": wired and seam_present,
            "wired_import": wired,
            "enforce_call_in_source": "research_detective_gate.enforce_before_pass2" in src,
        }
    )

    all_pass = all(bool(s.get("pass")) for s in steps)
    verdict = {
        "story": "research-r7",
        "pass": all_pass,
        "trial_id": trial_id,
        "flag": "MARCUS_RESEARCH_DETECTIVE_LIVE",
        "trail_non_claim": "tracy-gate-resume-recover",
        "teeth": "approve|reject|defer required before Pass-2 when detective ON",
        "steps": steps,
        "artifacts": {
            "landing": str(gate.landing_path(run_dir).relative_to(ROOT)),
            "disposition": str(gate.disposition_path(run_dir).relative_to(ROOT)),
        },
    }
    (out_dir / "verdict.json").write_text(
        json.dumps(verdict, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "PROOF.md").write_text(
        "\n".join(
            [
                "# R7 Hard-pause teeth — live proof",
                "",
                f"- pass: `{all_pass}`",
                f"- trial_id: `{trial_id}`",
                f"- trail non-claim: `tracy-gate-resume-recover`",
                "",
                "## Steps",
                "",
                *[
                    f"- **{s['step']}**: `{'PASS' if s.get('pass') else 'FAIL'}`"
                    for s in steps
                ],
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(verdict, indent=2))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
