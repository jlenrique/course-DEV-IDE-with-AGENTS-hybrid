# Leg-3 — CLUSTERING verify + harden (NARROW-SCOPE)

**Arc:** Concierge Production Substrate (branch `dev/concierge-production-substrate-2026-06-29`).
**Class:** S. **Status:** ready-for-dev (party GREEN-LIGHT 6/6 NARROW-SCOPE, 2026-07-01; Winston/John/Amelia/Murat + Irene/Vera).
**Gate mode:** single-gate structural (Murat) + the NON-WAIVABLE 07G VO↔on-screen fidelity check (Vera) on any chunked slide.

## Reframe (confirm-spike + party)

The read-only confirm-spike proved **clustering is LIVE in code, not dormant** — Pass-1 cluster emission is unconditional (`app/specialists/irene_pass1/_act.py:156,161-201`), unit-tested + trial-proven (52890be7, c2c6dcbf). It has been FLAT since 2026-06-24 by **operator opt-out** (operational, not structural). The current 2026-06-30 substrate (coverage-interlock, warm_callback, 16:9, Descript-receipt — all landed after c2c6dcbf) has never carried a real clustered run.

**GUARDRAIL RULING (John PM, decisive):** exercising clustering does NOT earn its place on its own — flatness is an operator choice, not a defect. The clustered run is a **diagnostic instrument, not the deliverable.** Leg-3 funds only the genuine SPOC-runtime hardening the clustered probe exposes. **Every Leg-3 commit must name the specific product defect/invariant it closes; any that can't is out of scope.**

**Critical finding (Amelia, guardrail-decisive):** the storyboard `cluster_id:null` is emitted by the CONCIERGE script `generate-storyboard.py` (a proofing vehicle, `raw.get("cluster_id")` join-miss), NOT the production publisher. The production path `storyboard_publisher._write_segment_manifest_for_b` (:102-181) already re-attaches all four cluster labels from Pass-2 deltas + `_cluster_arc_by_id` and is green + covered by `test_storyboard_publisher_cluster_carry.py`. → Candidate (b) is NOT a production defect; fixing the concierge script is the exact guardrail anti-pattern. **DECLINED.**

## Scope (ratified)

| Item | Disposition |
|------|-------------|
| **(d) 07G VO↔on-screen PER-SUB-SLIDE** | **IN** — non-waivable. *Verify* (not modify) the protected invariant holds when a slide chunks. |
| **(c) downstream survival** (05B/6.2/6.3/7.5 + Gary `_derive_clusters`) | **IN, OFFLINE** node-level on the c2c6dcbf fixture; fix only concrete breakage surfaced. |
| **(a) live emission on current substrate** | **VEHICLE/probe** for (d); prove both heuristic arms; bank a current-substrate clustered witness golden. |
| **(b) storyboard label-carry** | **DECLINED** — concierge-script wiring, not a production defect (publisher green+tested). |
| **(e) teaches_after/warm_callback × cluster boundary** | **DEFER** → inventory; promote only if the live probe surfaces concrete breakage. |
| skill-scripts vs runtime cluster derivers (two-SSOT smell) | **DEFER** → inventory (Winston); separate arc. |

## Prove-path: B (targeted) — unanimous

Live sub-chain **Pass-1(clustered) → Gary → 07G → Pass-2** over ONE dense tejal slide with ≥2 interstitials proves (d) live; downstream (c) offline node-level on the fixture. No fresh full walk (no clustered golden for rewind; a full walk burns first-run-stands on Texas/Gamma infra flakes + Leg-4's budget).

## Close bar (Murat + Vera; die-on-this = ⛔)

1. ⛔ **Live clusters emitted on the current substrate** — ≥1 multi-member cluster AND ≥1 correctly-held keep-dense singleton (BOTH heuristic arms; not a fixture).
2. ⛔ **07G VO↔on-screen read-path holds PER SUB-SLIDE** — each interstitial has its OWN rendered PNG + a DISTINCT `perception_source` (no head-slide reuse), every Pass-2 narration segment maps to a perceived element on ITS sub-slide (`traceable_visual_references`, `narration_cue_presence`), and the figure-citation gate holds per sub-slide (0 contradictions, matching c2c6dcbf's clean bar). UNSAFE-to-ship trip-wire: any sub-slide whose narration references an element/numeral on the ORIGINAL dense slide but NOT on that sub-slide's PNG.
3. (c) downstream 05B/6.2/6.3/7.5 + Gary `_derive_clusters` survive the clustered shape (offline).
4. Bank the live clustered witness as the current-substrate golden (Murat's (e)/full-walk down-payment).
5. First-run-stands; NO MOCKS on the live sub-chain.
6. Additive-safety: a flat run still writes a valid manifest (already covered; keep green).

## Governance amendments (party)

- Every Leg-3 commit names the specific product defect/invariant it hardens (John).
- Distinct `perception_source` per sub-slide — no head-slide reuse — is a hard close assertion (Vera; recycled artifacts = green-over-stub).
- Prove BOTH heuristic arms; if nothing chunks live, that's NEEDS-MORE-INVESTIGATION on the heuristic, not a silent green (Irene).
- Witness the app-path; do NOT rebuild the concierge `generate-storyboard.py` (Amelia).
- File the two-SSOT consolidation + (e) to deferred-inventory (Winston/John).

## Honest expectation

Because the production clustering paths are already largely correct + tested, Leg-3 may close primarily as **"the non-waivable VO↔on-screen invariant proven to hold per-sub-slide on a live clustered slice + downstream verified + witness banked + deferred items filed,"** WITHOUT manufacturing fixes. If the probe surfaces a concrete production defect (downstream bit-rot, a sub-slide VO regression), that fix scopes in and earns its place. If it does not, that clean result is the honest close — we do not invent work to "do Leg-3."
