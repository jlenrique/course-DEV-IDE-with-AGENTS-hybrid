"""JUDGE-2 (S4 AC-L leg 2 — parity divergence flips WARN->ERROR; HALT).
WRITTEN AND FROZEN BEFORE THE LEG RAN.

Deterministic, read-only. The S3 witness proved this exact setup WARN-proceeded
to G2B. Post-S4 it must HALT pre-spend. Reads error-pause.json + the driver's
recover-result.json + run.json + the walk log and asserts the halt facts:
paused-at-error, tag gamma.styleguide.parity-divergence, node 07, message
carries the divergence reason + digest summary, ZERO Gamma generative spend
(no gary contribution persisted; no generation_id), walk did NOT proceed.
Also re-probes the resolver to confirm the SSOT was git-restored (amount back to
'minimal'). Exit 0 = PASS, exit 1 = FAIL. First-run-stands; no retry-to-green.

Usage: judge2.py <trial_id_leg2> <walk_log_path>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(r"C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS-hybrid")
RUNS_ROOT = REPO / "state" / "config" / "runs"
SSOT = REPO / "state" / "config" / "gamma-style-guides.yaml"
GUIDE = "hil-2026-apc-crossroads-classic"
EVIDENCE = Path(__file__).resolve().parent

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


# --- driver-captured recover result -----------------------------------------
rr = json.loads((EVIDENCE / "leg2-recover-result.json").read_text(encoding="utf-8"))
check(
    "r0-recover-status-paused-at-error",
    rr.get("recover_status") == "paused-at-error",
    rr.get("recover_status"),
)
check(
    "r1-recover-tag-parity-divergence",
    rr.get("paused_error_tag") == "gamma.styleguide.parity-divergence",
    rr.get("paused_error_tag"),
)

# --- error-pause.json (runner-persisted) ------------------------------------
ep = json.loads((run_dir / "error-pause.json").read_text(encoding="utf-8"))
check("e0-error-pause-tag", ep.get("tag") == "gamma.styleguide.parity-divergence", ep.get("tag"))
check("e1-error-pause-node-07", str(ep.get("node_id")) == "07", ep.get("node_id"))
check("e2-error-pause-specialist-gary", ep.get("specialist_id") == "gary", ep.get("specialist_id"))
msg = str(ep.get("message") or "")
check("e3-message-carries-reason", "resolution-mismatch" in msg, msg[:200])
check(
    "e4-message-carries-digest-summary",
    "cd_resolution_digest=" in msg and "gary_resolution_digest=" in msg,
    [seg for seg in msg.split("[")[-1:]][:1],
)
check("e5-message-says-pre-spend", "pre-spend" in msg.lower(), "pre-spend" in msg.lower())

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
# no generation_id anywhere in the recovered envelope (zero generative spend)
blob = json.dumps(contribs)
check("s1-no-generation-id-anywhere", "generation_id" not in blob, "generation_id" in blob)
# CD stayed (the CD-before / gary-after ordering the divergence depends on)
cd = [c for c in contribs if c.get("specialist_id") == "cd"]
check("w1-cd-contribution-retained", len(cd) >= 1, f"{len(cd)} cd contribution(s)")

# --- walk log: Flip-B raise fired; no Gamma generation success --------------
log_text = walk_log.read_text(encoding="utf-8", errors="replace") if walk_log.is_file() else ""
raise_hits = [ln for ln in log_text.splitlines() if "parity-divergence" in ln or "parity DIVERGENCE" in ln]
check("l0-walk-log-flip-b-fired", len(raise_hits) >= 1, raise_hits[:2])

# --- SSOT restored (resolver re-probe) --------------------------------------
sys.path.insert(0, str(REPO))
try:
    from app.styleguide.resolver import load_style_guides, resolve_styleguide

    guides = load_style_guides(SSOT)["style_guides"]
    resolved = resolve_styleguide(GUIDE, guides=guides)
    amount = resolved.get("amount")
    check("x0-ssot-restored-amount-minimal", amount == "minimal", amount)
except Exception as exc:  # noqa: BLE001
    check("x0-ssot-restored-amount-minimal", False, f"resolver probe raised: {exc!r}")

out_path = EVIDENCE / "judge2-facts.json"
out_path.write_text(json.dumps(facts, indent=2, default=str) + "\n", encoding="utf-8")
verdict = "PASS" if not failures else "FAIL"
print(f"JUDGE-2 VERDICT: {verdict} ({len(failures)} failing: {failures})", flush=True)
sys.exit(0 if not failures else 1)
