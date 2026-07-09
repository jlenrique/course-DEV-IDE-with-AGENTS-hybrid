"""JUDGE-1 (S3 AC-L leg 1 — matching-pick PASS). WRITTEN BEFORE THE LEG RAN.

Deterministic, read-only. Reads the persisted run.json + trial-start.json of
the leg-1 trial and asserts the exact expected receipt facts. Exit 0 = PASS,
exit 1 = FAIL. First-run-stands: this script's assertions are FROZEN before
the leg executes; no retry-to-green.

Usage: judge1.py <trial_id>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(r"C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS-hybrid")
RUNS_ROOT = REPO / "state" / "config" / "runs"
GUIDE = "hil-2026-apc-crossroads-classic"

trial_id = sys.argv[1]
run_dir = RUNS_ROOT / trial_id

failures: list[str] = []
facts: dict[str, object] = {"trial_id": trial_id}


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
receipt = ((gary[-1] if gary else {}).get("output") or {}).get("styleguide_parity")
check("g1-receipt-present", isinstance(receipt, dict), type(receipt).__name__)
receipt = receipt if isinstance(receipt, dict) else {}

check("g2-outcome-ok", receipt.get("outcome") == "ok", receipt.get("outcome"))
check("g3-reason-match", receipt.get("reason") == "match", receipt.get("reason"))
check("g4-clock-eligible-true", receipt.get("clock_eligible") is True, receipt.get("clock_eligible"))
check("g5-cd-status-resolved", receipt.get("cd_status") == "resolved", receipt.get("cd_status"))

ts_d = receipt.get("trial_start_directive_digest")
cd_d = receipt.get("cd_directive_digest")
gy_d = receipt.get("gary_directive_digest")
all_nonnull = all(isinstance(d, str) and len(d) == 64 for d in (ts_d, cd_d, gy_d))
check("g6-three-digests-nonnull-sha256", all_nonnull, {"trial_start": ts_d, "cd": cd_d, "gary": gy_d})
check("g7-three-digests-equal", all_nonnull and ts_d == cd_d == gy_d, {"trial_start": ts_d, "cd": cd_d, "gary": gy_d})

trial_start = json.loads((run_dir / "trial-start.json").read_text(encoding="utf-8"))
on_disk = trial_start.get("directive_digest")
check(
    "g8-trial-start-digest-matches-on-disk",
    isinstance(on_disk, str) and on_disk == ts_d,
    {"on_disk": on_disk, "receipt": ts_d},
)

# CD block from the LATEST cd contribution
cd = [c for c in contribs if c.get("specialist_id") == "cd"]
check("c0-cd-contribution-present", len(cd) >= 1, f"{len(cd)} cd contribution(s)")
cd_block = ((cd[-1] if cd else {}).get("output") or {}).get("styleguide_resolution")
cd_block = cd_block if isinstance(cd_block, dict) else {}
check("c1-cd-block-status-resolved", cd_block.get("status") == "resolved", cd_block.get("status"))
names = [e.get("name") for e in (cd_block.get("bound_guides") or []) if isinstance(e, dict)]
check("c2-cd-bound-guides-exactly-picked-guide", names == [GUIDE], names)

# walk integrity: crossed §07 and paused cleanly at the next pause gate
check(
    "w0-paused-at-gate-post-07",
    run.get("status") == "paused-at-gate" and run.get("paused_gate") == "G2B",
    {"status": run.get("status"), "paused_gate": run.get("paused_gate"),
     "paused_error_tag": run.get("paused_error_tag")},
)

out = Path(__file__).resolve().parent / "judge1-facts.json"
out.write_text(json.dumps(facts, indent=2, default=str) + "\n", encoding="utf-8")
verdict = "PASS" if not failures else "FAIL"
print(f"JUDGE-1 VERDICT: {verdict} ({len(failures)} failing: {failures})", flush=True)
sys.exit(0 if not failures else 1)
