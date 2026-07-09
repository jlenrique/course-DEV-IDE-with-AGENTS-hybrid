"""JUDGE-3 (S4 AC-L leg 3 — happy path STILL dispatches; anti-outage proof).
WRITTEN AND FROZEN BEFORE THE LEG RAN.

Deterministic, read-only. Reads the persisted run.json of the leg-3 happy-path
trial + the captured walk log and asserts: §07 dispatched a REAL Gamma deck,
the parity receipt is ok/match/clock-eligible/cd-resolved (UNCHANGED from S3
leg-1 — proves the S4 flip did NOT manufacture an outage), the walk proceeded
past §07 to G2B, and NO gamma.styleguide.* error tag appears anywhere.
Exit 0 = PASS, exit 1 = FAIL. First-run-stands; no retry-to-green.

Usage: judge3.py <trial_id_leg3> <walk_log_path>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(r"C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS-hybrid")
RUNS_ROOT = REPO / "state" / "config" / "runs"
GUIDE = "hil-2026-apc-crossroads-classic"

trial_id = sys.argv[1]
walk_log = Path(sys.argv[2])
run_dir = RUNS_ROOT / trial_id

failures: list[str] = []
facts: dict[str, object] = {"trial_id": trial_id, "walk_log": str(walk_log)}


def check(name: str, ok: bool, value: object) -> None:
    facts[name] = {"pass": bool(ok), "value": value}
    print(f"ASSERT {name}: {'PASS' if ok else 'FAIL'} -- {value!r}", flush=True)
    if not ok:
        failures.append(name)


run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
contribs = (run.get("production_envelope") or {}).get("contributions") or []

# latest gary contribution
gary = [c for c in contribs if c.get("specialist_id") == "gary"]
check("g0-gary-contribution-present", len(gary) >= 1, f"{len(gary)} gary contribution(s)")
out = (gary[-1] if gary else {}).get("output") or {}

# --- REAL deck dispatched (generate call present + PNG export) ---------------
gen_id = out.get("generation_id")
check(
    "d0-real-generation-id",
    isinstance(gen_id, str) and len(gen_id) > 0,
    gen_id,
)
calls_made = out.get("calls_made")
check("d1-calls-made-ge-1", isinstance(calls_made, int) and calls_made >= 1, calls_made)
gso = out.get("gary_slide_output")
gso = gso if isinstance(gso, list) else []
check("d2-slide-output-nonempty", len(gso) >= 1, f"{len(gso)} slide rows")
pngs = [
    r.get("file_path")
    for r in gso
    if isinstance(r, dict) and isinstance(r.get("file_path"), str)
    and r.get("file_path").lower().endswith(".png")
]
check(
    "d3-png-exports-present",
    len(pngs) >= 1 and len(pngs) == len(gso),
    {"png_count": len(pngs), "slide_count": len(gso), "sample": pngs[:1]},
)

# --- parity receipt UNCHANGED from S3 leg-1 (ok/match) -----------------------
receipt = out.get("styleguide_parity")
check("g1-receipt-present", isinstance(receipt, dict), type(receipt).__name__)
receipt = receipt if isinstance(receipt, dict) else {}
check("g2-outcome-ok", receipt.get("outcome") == "ok", receipt.get("outcome"))
check("g3-reason-match", receipt.get("reason") == "match", receipt.get("reason"))
check("g4-clock-eligible-true", receipt.get("clock_eligible") is True, receipt.get("clock_eligible"))
check("g5-cd-status-resolved", receipt.get("cd_status") == "resolved", receipt.get("cd_status"))

# --- walk PROCEEDED past §07 to the next gate -------------------------------
check(
    "w0-paused-at-gate-post-07",
    run.get("status") == "paused-at-gate"
    and run.get("paused_gate") == "G2B"
    and run.get("paused_error_tag") is None,
    {"status": run.get("status"), "paused_gate": run.get("paused_gate"),
     "paused_error_tag": run.get("paused_error_tag")},
)

# --- NO gamma.styleguide.* error tag anywhere -------------------------------
# (a) run envelope carries no styleguide error tag
tag = run.get("paused_error_tag")
check(
    "n0-run-no-styleguide-error-tag",
    not (isinstance(tag, str) and tag.startswith("gamma.styleguide.")),
    tag,
)
# (b) no error-pause.json with a styleguide tag persisted
ep = run_dir / "error-pause.json"
ep_tag = None
if ep.is_file():
    try:
        ep_tag = json.loads(ep.read_text(encoding="utf-8")).get("tag")
    except Exception:  # noqa: BLE001
        ep_tag = "<unreadable>"
check(
    "n1-no-error-pause-styleguide-tag",
    not (isinstance(ep_tag, str) and ep_tag.startswith("gamma.styleguide.")),
    ep_tag,
)
# (c) walk log carries no styleguide fail-loud raise
log_text = walk_log.read_text(encoding="utf-8", errors="replace") if walk_log.is_file() else ""
sg_err_hits = [
    ln for ln in log_text.splitlines()
    if "gamma.styleguide.unbound" in ln or "gamma.styleguide.parity-divergence" in ln
]
check("n2-walk-log-no-styleguide-fail-loud", len(sg_err_hits) == 0, sg_err_hits[:3])

# --- CD block sanity (matching pick) ----------------------------------------
cd = [c for c in contribs if c.get("specialist_id") == "cd"]
cd_block = ((cd[-1] if cd else {}).get("output") or {}).get("styleguide_resolution")
cd_block = cd_block if isinstance(cd_block, dict) else {}
names = [e.get("name") for e in (cd_block.get("bound_guides") or []) if isinstance(e, dict)]
check("c0-cd-bound-guides-exactly-picked-guide", names == [GUIDE], names)

out_path = Path(__file__).resolve().parent / "judge3-facts.json"
out_path.write_text(json.dumps(facts, indent=2, default=str) + "\n", encoding="utf-8")
verdict = "PASS" if not failures else "FAIL"
print(f"JUDGE-3 VERDICT: {verdict} ({len(failures)} failing: {failures})", flush=True)
sys.exit(0 if not failures else 1)
