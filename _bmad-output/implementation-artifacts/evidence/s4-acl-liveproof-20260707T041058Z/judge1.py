"""JUDGE-1 (S4 AC-L leg 1 — named-variant-styleguide-less flips WARN-seed->HALT).
WRITTEN AND FROZEN BEFORE THE LEG RAN.

Deterministic, read-only. A directive whose gamma_settings names a variant with
NO styleguide key (NOT empty gamma_settings) must, post-S4 Flip A, error-pause at
gamma.styleguide.unbound pre-spend. Reads error-pause.json + the driver's
recover-result.json + run.json + the walk log and asserts: paused-at-error, tag
gamma.styleguide.unbound, node 07, message names the offending variant, ZERO
Gamma generative spend (no gary contribution persisted; no generation_id), walk
did NOT proceed. Exit 0 = PASS, exit 1 = FAIL. First-run-stands; no retry.

Usage: judge1.py <trial_id_leg1> <walk_log_path> <offending_variant>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(r"C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS-hybrid")
RUNS_ROOT = REPO / "state" / "config" / "runs"
EVIDENCE = Path(__file__).resolve().parent

trial_id = sys.argv[1]
walk_log = Path(sys.argv[2])
offending_variant = sys.argv[3] if len(sys.argv) > 3 else "A"
run_dir = RUNS_ROOT / trial_id

failures: list[str] = []
facts: dict[str, object] = {
    "trial_id": trial_id, "walk_log": str(walk_log), "offending_variant": offending_variant,
}


def check(name: str, ok: bool, value: object) -> None:
    facts[name] = {"pass": bool(ok), "value": value}
    print(f"ASSERT {name}: {'PASS' if ok else 'FAIL'} -- {value!r}", flush=True)
    if not ok:
        failures.append(name)


# --- driver-captured recover result -----------------------------------------
rr = json.loads((EVIDENCE / "leg1-recover-result.json").read_text(encoding="utf-8"))
check(
    "r0-recover-status-paused-at-error",
    rr.get("recover_status") == "paused-at-error",
    rr.get("recover_status"),
)
check(
    "r1-recover-tag-unbound",
    rr.get("paused_error_tag") == "gamma.styleguide.unbound",
    rr.get("paused_error_tag"),
)

# --- error-pause.json (runner-persisted) ------------------------------------
ep = json.loads((run_dir / "error-pause.json").read_text(encoding="utf-8"))
check("e0-error-pause-tag", ep.get("tag") == "gamma.styleguide.unbound", ep.get("tag"))
check("e1-error-pause-node-07", str(ep.get("node_id")) == "07", ep.get("node_id"))
check("e2-error-pause-specialist-gary", ep.get("specialist_id") == "gary", ep.get("specialist_id"))
msg = str(ep.get("message") or "")
check(
    "e3-message-names-offending-variant",
    f"variant {offending_variant}" in msg,
    msg[:200],
)
check("e4-message-says-no-bound-styleguide", "no bound styleguide" in msg, "no bound styleguide" in msg)

# --- run.json: walk did NOT proceed; ZERO generative spend ------------------
run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
check(
    "w0-run-status-paused-at-error",
    run.get("status") == "paused-at-error" and run.get("paused_gate") is None,
    {"status": run.get("status"), "paused_gate": run.get("paused_gate")},
)
contribs = (run.get("production_envelope") or {}).get("contributions") or []
gary = [c for c in contribs if c.get("specialist_id") == "gary"]
check(
    "s0-no-gary-contribution-halt-pre-contribution",
    len(gary) == 0,
    f"{len(gary)} gary contribution(s) (expected 0 — halt is pre-contribution)",
)
blob = json.dumps(contribs)
check("s1-no-generation-id-anywhere", "generation_id" not in blob, "generation_id" in blob)

# --- walk log: Flip-A raise fired -------------------------------------------
log_text = walk_log.read_text(encoding="utf-8", errors="replace") if walk_log.is_file() else ""
raise_hits = [ln for ln in log_text.splitlines() if "gamma.styleguide.unbound" in ln or "no bound styleguide" in ln]
check("l0-walk-log-flip-a-fired", len(raise_hits) >= 1, raise_hits[:2])

out_path = EVIDENCE / "judge1-facts.json"
out_path.write_text(json.dumps(facts, indent=2, default=str) + "\n", encoding="utf-8")
verdict = "PASS" if not failures else "FAIL"
print(f"JUDGE-1 VERDICT: {verdict} ({len(failures)} failing: {failures})", flush=True)
sys.exit(0 if not failures else 1)
