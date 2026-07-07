"""FROZEN JUDGE-b — S6 AC-L RECOVER lane (b): honest creds-absent degrade ($0).

Executed VERBATIM exactly once against the on-disk lane_b-facts.json. First-run-
stands; NO retry-to-green.

JUDGE-b (frozen):
 1. the D4 creds-precondition fired at run_research_wiring ENTRY (no dispatch
    reached): research_degrade.degraded == True AND dispatch_reached == False,
    with creds proven absent.
 2. research_entries PRESENT + explicitly-empty ([] in the contribution output)
    with the VISIBLE RESEARCH_DEGRADE_KEY marker ("...credentials unavailable").
 3. relogin offer surfaced + narrate_research_result showed the degrade.
 4. $0 Scite spend; walk PROCEEDED (paused-at-gate; never halted/errored).
 BONUS R1 (only scored if attempted): after restore creds + resume, 04.55
    RE-DISPATCHES (research_entries non-empty) — not stuck on the degraded contrib.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

EVID = Path(__file__).resolve().parent
FACTS = json.loads((EVID / "lane_b-facts.json").read_text(encoding="utf-8"))

PAST_0455_GATES = {"G2B", "G2", "G2C", "G3", "G4", "G4A", "G5", "G1.5", "G2A"}
MARKER_SUBSTR = "credentials unavailable"

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str) -> None:
    results.append((name, bool(ok), detail))


degrade = FACTS.get("research_degrade") or {}
entries = FACTS.get("research_entries")

# 1 — D4 precondition fired at node entry; no dispatch reached
c1 = (
    FACTS.get("scite_creds_present") is False
    and isinstance(degrade, dict)
    and degrade.get("degraded") is True
    and FACTS.get("dispatch_reached") is False
)
check("1_d4_precondition_fired_no_dispatch", c1,
      f"creds_present={FACTS.get('scite_creds_present')} "
      f"degraded={degrade.get('degraded')} dispatch_reached={FACTS.get('dispatch_reached')}")

# 2 — research_entries PRESENT + explicitly empty + visible marker
c2 = (
    FACTS.get("research_entries_present") is True
    and isinstance(entries, list)
    and len(entries) == 0
    and MARKER_SUBSTR in str(degrade.get("reason", ""))
)
check("2_present_empty_with_marker", c2,
      f"entries_present={FACTS.get('research_entries_present')} "
      f"entries={entries!r} reason={degrade.get('reason')!r}")

# 3 — relogin offer surfaced + narration showed degrade
narr = FACTS.get("narration_line") or ""
c3 = (
    bool(str(degrade.get("relogin_offer", "")).strip())
    and isinstance(narr, str)
    and MARKER_SUBSTR in narr.lower()
)
check("3_relogin_and_narration", c3,
      f"relogin_offer_present={bool(degrade.get('relogin_offer'))} narration={narr!r}")

# 4 — $0 Scite spend; walk proceeded
c4 = (
    FACTS.get("scite_spend") == 0
    and FACTS.get("final_status") == "paused-at-gate"
    and FACTS.get("final_paused_gate") in PAST_0455_GATES
)
check("4_zero_spend_walk_proceeded", c4,
      f"scite_spend={FACTS.get('scite_spend')} final_status={FACTS.get('final_status')} "
      f"final_gate={FACTS.get('final_paused_gate')}")

# BONUS R1 — only scored if attempted
r1 = FACTS.get("r1_redispatch")
r1_attempted = isinstance(r1, dict) and r1.get("attempted") is True
r1_ok = r1_attempted and r1.get("redispatched") is True and (r1.get("entries_count") or 0) >= 1
bonus_str = (
    f"attempted={r1_attempted} redispatched={r1.get('redispatched') if r1_attempted else None} "
    f"entries_count={r1.get('entries_count') if r1_attempted else None} "
    f"r1_primary_doi={r1.get('primary_doi') if r1_attempted else None}"
)

core_ok = all(ok for _, ok, _ in results)
out = {
    "judge": "b",
    "verdict": "PASS" if core_ok else "FAIL",
    "n_pass": sum(1 for _, ok, _ in results if ok),
    "n_total": len(results),
    "checks": [{"name": n, "ok": ok, "detail": d} for n, ok, d in results],
    "bonus_r1": {"attempted": r1_attempted, "ok": r1_ok, "detail": bonus_str},
}
(EVID / "judge_b-facts.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
for n, ok, d in results:
    print(f"[{'PASS' if ok else 'FAIL'}] {n}: {d}")
print(f"[BONUS-R1 {'PASS' if r1_ok else ('FAIL' if r1_attempted else 'N/A')}] {bonus_str}")
print(f"=== JUDGE-b {out['verdict']} ({out['n_pass']}/{out['n_total']}) ===")
sys.exit(0 if core_ok else 1)
