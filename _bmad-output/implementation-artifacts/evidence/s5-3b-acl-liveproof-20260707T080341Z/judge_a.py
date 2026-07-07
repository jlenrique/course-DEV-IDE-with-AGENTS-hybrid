"""FROZEN JUDGE-a for S5-3b AC-L lane (a) — canonical default-ENV walk (the FLIP proof).

Executed VERBATIM ONCE after lane (a) pauses through G0E->G0R->G1. First-run-stands.
Reads ONLY on-disk artifacts the lane-a drivers produced (no re-run, no live call).

JUDGE-a criteria (frozen per the witness plan + 3b spec AC-L(a)):
  F1804. env MARCUS_G0_ENRICHMENT_ACTIVE was ABSENT by exact name after dotenv load
         (prove the DEFAULT unset->ON, not a set value); MARCUS_G0_DISPATCH_LIVE unset.
  1. FIRST pause == G0E (not G1) — the flip is live.
  2. resume/confirm G0E -> next pause == G0R.
  3. resume/ratify G0R -> next pause == G1 (canonical G0E->G0R->G1).
  4. enrichment result + LO cards are REAL (>=1 typed component, >=1 provisional LO).
  5. persisted g0-enrichment.json receipt enrichment_mode == "deterministic-recorded".
  6. $0 live-LLM model spend on the G0 pre-pass (model_used == offline marker; mode det).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

EVID = Path(__file__).resolve().parent
DET_MARKER = "deterministic-g0-enrichment-offline"
MODE_DET = "deterministic-recorded"


def _load(name: str) -> dict:
    return json.loads((EVID / name).read_text(encoding="utf-8"))


checks: dict[str, dict] = {}


def check(cid: str, passed: bool, detail: str) -> None:
    checks[cid] = {"pass": bool(passed), "detail": detail}


start = _load("lane_a-start-result.json")
res_g0e = _load("lane_a-resume-g0e-result.json")
res_g0r = _load("lane_a-resume-g0r-result.json")
run_dir = Path(start["run_dir"])

# F-1804 — default-witness preamble (env proven UNSET by exact name)
check(
    "F1804_env_enrichment_absent",
    start.get("env_g0_enrichment_active_present") is False,
    f"MARCUS_G0_ENRICHMENT_ACTIVE present-after-dotenv={start.get('env_g0_enrichment_active_present')} "
    f"(must be False: os.environ.get(...) is None)",
)
check(
    "F1804_env_dispatch_live_unset",
    start.get("env_g0_dispatch_live_present") is False,
    f"MARCUS_G0_DISPATCH_LIVE present={start.get('env_g0_dispatch_live_present')} (must be False)",
)

# 1. first pause == G0E
check(
    "1_first_pause_G0E",
    start.get("paused_gate") == "G0E" and start.get("start_status") == "paused-at-gate",
    f"start paused_gate={start.get('paused_gate')!r} status={start.get('start_status')!r} (expect G0E / paused-at-gate)",
)
# 2. resume G0E -> G0R
check(
    "2_G0E_resume_to_G0R",
    res_g0e.get("resume_status") == "paused-at-gate"
    and res_g0e.get("verdict_gate") == "G0E"
    and res_g0e.get("paused_gate") == "G0R",
    f"G0E verdict resume -> status={res_g0e.get('resume_status')!r} paused_gate={res_g0e.get('paused_gate')!r} (expect G0R)",
)
# 3. resume G0R -> G1
check(
    "3_G0R_resume_to_G1",
    res_g0r.get("resume_status") == "paused-at-gate"
    and res_g0r.get("verdict_gate") == "G0R"
    and res_g0r.get("paused_gate") == "G1",
    f"G0R verdict resume -> status={res_g0r.get('resume_status')!r} paused_gate={res_g0r.get('paused_gate')!r} (expect G1)",
)

# 4/5/6 — read the persisted receipt off disk
receipt_path = run_dir / "g0-enrichment.json"
receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
result_block = receipt.get("g0_enrichment_result") or receipt
typed = result_block.get("typed_components") or []
los = result_block.get("provisional_los") or []
mode = receipt.get("enrichment_mode")

check(
    "4_enrichment_real",
    len(typed) >= 1 and len(los) >= 1,
    f"typed_components={len(typed)} provisional_los={len(los)} (expect >=1 each); "
    f"first_component_type={typed[0].get('source_type') if typed else None!r}",
)
check(
    "5_receipt_mode_deterministic",
    mode == MODE_DET,
    f"receipt enrichment_mode={mode!r} (expect {MODE_DET!r})",
)
# 6. $0 live-LLM spend on the pre-pass: the pre-pass model marker is the OFFLINE
#    deterministic marker (no live model), and the resolved mode is deterministic.
model_id = result_block.get("model_id")
check(
    "6_zero_prepass_spend",
    model_id == DET_MARKER and mode == MODE_DET,
    f"pre-pass model_id={model_id!r} mode={mode!r} (offline marker => $0 live-LLM pre-pass)",
)

all_pass = all(c["pass"] for c in checks.values())
facts = {
    "judge": "a",
    "lane": "canonical default-ENV walk (flip proof, deterministic)",
    "verdict": "PASS" if all_pass else "FAIL",
    "trial_id": start.get("trial_id"),
    "run_dir": str(run_dir),
    "receipt_path": str(receipt_path),
    "pause_sequence_observed": [
        start.get("paused_gate"),
        res_g0e.get("paused_gate"),
        res_g0r.get("paused_gate"),
    ],
    "enrichment_mode": mode,
    "n_typed_components": len(typed),
    "n_provisional_los": len(los),
    "checks": checks,
}
(EVID / "judge_a-facts.json").write_text(json.dumps(facts, indent=2) + "\n", encoding="utf-8")
print("=== JUDGE-a VERDICT:", facts["verdict"], "===")
for cid, c in checks.items():
    print(f"  [{'PASS' if c['pass'] else 'FAIL'}] {cid}: {c['detail']}")
print("pause sequence:", facts["pause_sequence_observed"])
sys.exit(0 if all_pass else 1)
