"""JUDGE-2 (S3 AC-L leg 2 — forced-divergence WARN). WRITTEN BEFORE THE LEG RAN.

Deterministic, read-only. Reads the persisted run.json of the leg-2
(rewind-recovered) trial plus the captured walk log and asserts the exact
expected divergence receipt facts. Exit 0 = PASS, exit 1 = FAIL.
First-run-stands: assertions FROZEN before the leg executes.

Usage: judge2.py <trial_id_leg2> <walk_log_path>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(r"C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS-hybrid")
RUNS_ROOT = REPO / "state" / "config" / "runs"

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

gary = [c for c in contribs if c.get("specialist_id") == "gary"]
check("g0-gary-contribution-present", len(gary) >= 1, f"{len(gary)} gary contribution(s)")
receipt = ((gary[-1] if gary else {}).get("output") or {}).get("styleguide_parity")
check("g1-receipt-present", isinstance(receipt, dict), type(receipt).__name__)
receipt = receipt if isinstance(receipt, dict) else {}

check("g2-outcome-divergence", receipt.get("outcome") == "divergence", receipt.get("outcome"))
check(
    "g3-reason-resolution-mismatch",
    receipt.get("reason") == "resolution-mismatch",
    receipt.get("reason"),
)

# detail carries BOTH envelopes (cd_block + gary_view)
detail = receipt.get("detail")
detail = detail if isinstance(detail, dict) else {}
check(
    "g4-detail-carries-both-envelopes",
    isinstance(detail.get("cd_block"), dict) and isinstance(detail.get("gary_view"), dict),
    sorted(detail.keys()),
)

# the three directive digests are EQUAL and non-null (directive untouched —
# that is what makes the divergence genuine, not drift)
ts_d = receipt.get("trial_start_directive_digest")
cd_d = receipt.get("cd_directive_digest")
gy_d = receipt.get("gary_directive_digest")
all_nonnull = all(isinstance(d, str) and len(d) == 64 for d in (ts_d, cd_d, gy_d))
check("g5-three-digests-nonnull-sha256", all_nonnull, {"trial_start": ts_d, "cd": cd_d, "gary": gy_d})
check("g6-three-digests-equal", all_nonnull and ts_d == cd_d == gy_d, {"trial_start": ts_d, "cd": cd_d, "gary": gy_d})

# the resolutions genuinely disagree (mutated SSOT reached gary)
check(
    "g7-resolution-digests-differ",
    isinstance(receipt.get("cd_resolution_digest"), str)
    and isinstance(receipt.get("gary_resolution_digest"), str)
    and receipt.get("cd_resolution_digest") != receipt.get("gary_resolution_digest"),
    {"cd": receipt.get("cd_resolution_digest"), "gary": receipt.get("gary_resolution_digest")},
)

# WARN log line was emitted (captured walk log)
log_text = walk_log.read_text(encoding="utf-8", errors="replace") if walk_log.is_file() else ""
needle = "styleguide parity DIVERGENCE (resolution-mismatch)"
check(
    "w0-warn-line-emitted",
    "WARNING" in log_text and needle in log_text,
    [ln for ln in log_text.splitlines() if needle in ln][:2],
)

# the run did NOT halt: it reached its next pause cleanly (gate pause, no error)
check(
    "w1-run-did-not-halt",
    run.get("status") == "paused-at-gate"
    and run.get("paused_gate") == "G2B"
    and run.get("paused_error_tag") is None,
    {"status": run.get("status"), "paused_gate": run.get("paused_gate"),
     "paused_error_tag": run.get("paused_error_tag")},
)

out = Path(__file__).resolve().parent / "judge2-facts.json"
out.write_text(json.dumps(facts, indent=2, default=str) + "\n", encoding="utf-8")
verdict = "PASS" if not failures else "FAIL"
print(f"JUDGE-2 VERDICT: {verdict} ({len(failures)} failing: {failures})", flush=True)
sys.exit(0 if not failures else 1)
