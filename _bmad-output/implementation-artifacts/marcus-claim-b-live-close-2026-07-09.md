# CLOSE LETTER — Claim B LIVE Irene Pass-1 (bespoke)

**Date:** 2026-07-09  
**Branch:** `dev/lesson-planning-2026-07-09`  
**Party:** John / Winston / Amelia / Murat (fully spawned)  
**Verdict:** **CLOSE-with-named-fenced-residuals**  
**Claim B:** **UNFENCED COMPLETE (bespoke)**  
**S8:** stays CLOSED

---

## Banked evidence

| Item | Value |
|------|-------|
| Driver | `scripts/utilities/bank_marcus_claim_b_live_irene.py` |
| Evidence | `_bmad-output/implementation-artifacts/evidence/marcus-claim-b-live-20260709T234801Z/` |
| Treatment | `runs/bc8359aa-fdd9-4551-a9a1-e6483941c962/` |
| Control | `runs/b5cd2bc8-50e5-4d0f-9c60-0dbc79664bde/` |
| Predicates | `PASS-bespoke`; `failed_required=[]` |
| `lo_coverage` | `present`; `supported_objective_ids=["lo-bridge-001"]` |
| Digests | all three match companion bytes (`digest-verify.json`) |
| Live path | `make_chat_model(irene_pass1)` (~52s wall) |

Prior mock fence (`_RecordingHandle` for Claim B) is **lifted**.

Claim A remains closed at `318b6b0f` (W5 local compose, no Gamma).

---

## Party concurrence (4/4)

| Seat | Verdict |
|------|---------|
| John | CLOSE-with-named-fenced-residuals; Claim B UNFENCED COMPLETE (bespoke) |
| Winston | GO — pipe + FG-6 + provenance emit; residual = on-read digest verify for downstream trust |
| Amelia | GO — implementably honest; happy-path coverage JSON-to-disk is QoL, not claim gap |
| Murat | GO — FG-1/2/5/6/9 CLEAR; mock fence lifted |

Orchestrator concurs with John CLOSE framing.

---

## Named fenced residuals (MUST NOT claim)

1. Interactive SPOC planning REPL (CLI `plan-ratify` only)
2. Gamma spend / full published asset walk
3. SME / projector / LO UX polish
4. Full lecture / HAI-PHS ingestion
5. Happy-path `act()` write of `planning-context-coverage.json` (fail-loud path + contribution + driver mirror satisfy Claim B)
6. Winston consumer on-read digest verify seam (emit+byte-match banked; durable reader gate = next story if needed)

---

## Success-definition mapping

Per `marcus-solicitation-lesson-plan-success-definition-2026-07-09.md`:

- Claim A: previously MET
- Claim B framing-only: MET (purpose+audience ack + plan≠control + provenance)
- Claim B **bespoke**: MET (non-empty LO + `lo_coverage=present` + LO touch + digests)

False greens FG-1..FG-10: party CLEAR for this bank.
