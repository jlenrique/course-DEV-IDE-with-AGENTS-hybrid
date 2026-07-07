"""FROZEN JUDGE-b for S5-3b AC-L lane (b) — armed live-LLM walk (content-armed).

Executed VERBATIM ONCE after lane (b) pauses. First-run-stands. Reads ONLY on-disk
artifacts the lane-b (and lane-a, for the divergence guard) drivers produced.

JUDGE-b criteria (frozen per the witness plan + 3b spec AC-L(b)):
  1. the G0E pre-pass dispatched a genuine LIVE LLM call (real underlying model id
     resolved for the "marcus" seam + a real parsed response artifact on disk).
  2. the receipt enrichment_mode == "live".
  3. the G0E gate consumed the LIVE enrichment content (typed components present in
     the live receipt/card + the live-model marker on the bundle contribution).
  4. divergence guard: gate structure (first pause G0E; canonical G0E->G0R->G1),
     pause points, and carrier shape are IDENTICAL to lane (a); the ONLY delta is
     the enrichment content SOURCE (live model_id vs the deterministic marker).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

EVID = Path(__file__).resolve().parent
LIVE_MODEL_SEAM = "marcus"
DET_MARKER = "deterministic-g0-enrichment-offline"
MODE_LIVE = "live"
MODE_DET = "deterministic-recorded"


def _load(name: str) -> dict:
    return json.loads((EVID / name).read_text(encoding="utf-8"))


checks: dict[str, dict] = {}


def check(cid: str, passed: bool, detail: str) -> None:
    checks[cid] = {"pass": bool(passed), "detail": detail}


b_start = _load("lane_b-start-result.json")
b_g0e = _load("lane_b-resume-g0e-result.json")
b_g0r = _load("lane_b-resume-g0r-result.json")
a_start = _load("lane_a-start-result.json")
a_g0e = _load("lane_a-resume-g0e-result.json")
a_g0r = _load("lane_a-resume-g0r-result.json")
run_dir = Path(b_start["run_dir"])

receipt_path = run_dir / "g0-enrichment.json"
receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
result_block = receipt.get("g0_enrichment_result") or receipt
typed = result_block.get("typed_components") or []
los = result_block.get("provisional_los") or []
mode = receipt.get("enrichment_mode")
model_id = result_block.get("model_id")

# The frozen full cache dump (the parsed LIVE response artifact on disk).
fp = result_block.get("corpus_fingerprint") or receipt.get("corpus_fingerprint")
cache_path = run_dir / "g0-enrichment-cache" / f"{fp}.json"

# 1. genuine live call: dispatch_live gate armed True, a real underlying model id
#    resolved for the marcus seam, and a parsed response artifact frozen to disk.
resolved_model = b_start.get("resolved_marcus_model")
check(
    "1_live_call_dispatched",
    b_start.get("g0_dispatch_live_fn") is True
    and b_start.get("has_live_openai") is True
    and bool(resolved_model)
    and model_id == LIVE_MODEL_SEAM
    and cache_path.is_file(),
    f"dispatch_live_fn={b_start.get('g0_dispatch_live_fn')} has_live_openai={b_start.get('has_live_openai')} "
    f"resolved_marcus_model={resolved_model!r} receipt_model_id={model_id!r} "
    f"response_artifact_on_disk={cache_path.is_file()} ({cache_path.name})",
)
# 2. receipt mode == live
check(
    "2_receipt_mode_live",
    mode == MODE_LIVE,
    f"receipt enrichment_mode={mode!r} (expect {MODE_LIVE!r})",
)
# 3. G0E consumed live content
check(
    "3_gate_consumed_live_content",
    len(typed) >= 1 and len(los) >= 0 and mode == MODE_LIVE and model_id == LIVE_MODEL_SEAM,
    f"live typed_components={len(typed)} provisional_los={len(los)} mode={mode!r} model_id={model_id!r}",
)
# 4. divergence guard — identical gate structure, only content SOURCE differs
b_seq = [b_start.get("paused_gate"), b_g0e.get("paused_gate"), b_g0r.get("paused_gate")]
a_seq = [a_start.get("paused_gate"), a_g0e.get("paused_gate"), a_g0r.get("paused_gate")]
carrier_ok = set(b_start.get("contribution_output_keys") or []) == set(
    a_start.get("contribution_output_keys") or []
)
source_delta_only = (b_start.get("receipt_model_id") == LIVE_MODEL_SEAM) and (
    a_start.get("receipt_model_id") == DET_MARKER
)
check(
    "4_divergence_guard",
    b_seq == ["G0E", "G0R", "G1"] and b_seq == a_seq and carrier_ok and source_delta_only,
    f"lane_b seq={b_seq} lane_a seq={a_seq} carrier_keys_identical={carrier_ok} "
    f"content_source_delta(only)={source_delta_only} "
    f"[b_model={b_start.get('receipt_model_id')!r} a_model={a_start.get('receipt_model_id')!r}]",
)

all_pass = all(c["pass"] for c in checks.values())
facts = {
    "judge": "b",
    "lane": "armed live-LLM walk (content-armed)",
    "verdict": "PASS" if all_pass else "FAIL",
    "trial_id": b_start.get("trial_id"),
    "run_dir": str(run_dir),
    "receipt_path": str(receipt_path),
    "response_artifact": str(cache_path),
    "resolved_marcus_model": resolved_model,
    "enrichment_mode": mode,
    "receipt_model_id": model_id,
    "n_typed_components": len(typed),
    "n_provisional_los": len(los),
    "lane_b_pause_sequence": b_seq,
    "lane_a_pause_sequence": a_seq,
    "checks": checks,
}
(EVID / "judge_b-facts.json").write_text(json.dumps(facts, indent=2) + "\n", encoding="utf-8")
print("=== JUDGE-b VERDICT:", facts["verdict"], "===")
for cid, c in checks.items():
    print(f"  [{'PASS' if c['pass'] else 'FAIL'}] {cid}: {c['detail']}")
print("lane_b seq:", b_seq, "| lane_a seq:", a_seq)
sys.exit(0 if all_pass else 1)
