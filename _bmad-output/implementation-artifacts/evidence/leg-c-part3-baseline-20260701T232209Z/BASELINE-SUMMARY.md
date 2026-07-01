# Leg-C D1 LIVE Part-3 Baseline — floor-off control (2026-07-01)

**Re-judged verdict (from TRUE on-disk artifacts, per arc rule): BASELINE-CAPTURED.**
The driver's inline `NOT-CONVERGED` is a DRIVER STOP-CONDITION DEFECT, not a data defect: it expected a pause at G2, but node 05's G2 (and 05B's G1.5) are **folded** gates (`fold_with: G2C`) that do not pause individually — the walk correctly barreled past 05B into node 07 (gary), where it error-paused on the DOCUMENTED bijective title-matcher flake (`gamma.export.brief-unmatched`, 3 auto-retries). All three irene_pass1 contributions landed on disk BEFORE that pause; the Pass-1 capture is complete and first-run-stands.

- **Trial:** `66ae45d5-3b6b-439b-bad9-2240a0ce0ace` · corpus `course-content/courses/tejal-c1m1-p3-opportunity` (party-ratified, recorded pre-spend) · floor-off, no styleguide bound, default-run posture (G0-enrichment flag unset).
- **Validity conditions:** real production walk (`run_production_trial`) — real adapter payload assembly ✅, real `make_chat_model` binding ✅ (gpt-5.4 per cascade), corpus staged by real texas extraction ✅, first-run-stands ✅ (single run; the surprise IS the data). **Murat condition-5 ✅: `zero_floor_leak: True`** — `min_cluster_floor` appears NOWHERE in the run dir.
- **Winston-iii ✅:** verbatim outputs captured: `irene_pass1-04A-output-verbatim.json`, `irene_pass1-05-output-verbatim.json`, `irene_pass1-05B-output-verbatim.json` (M-2 fixture source; dev agent sha256-pins these).

## What the REAL Pass-1 emitted (the D1 substance, now live-confirmed)

| node | plan_units | distinct clusters | heads | chunked clusters (interstitials) |
|---|---|---|---|---|
| 04A (creation, corpus in prompt) | 17 | **10** | 10 | 3 clusters chunked (2, 2, 3) |
| 05 (refinement) | 12 | **7** | 7 | 2 clusters chunked (2, 3) |
| 05B (cluster plan) | 12 | **7 = count_K** | 7 | 2 clusters chunked (2, 3) |

- **`member_key_hits: []` on all three nodes** — none of the offline `_MEMBER_KEYS` (`source_points/components/beats/members/points/segments`) exist in real output. **`role_tag_hits: []`** — no figure/narration role tags. **D1 CONFIRMED live**: the offline honoring's assumed shape does not exist; the R3 rewire (party-ratified) is the path.
- **Irene's predictions verified:** chunk-by-default FIRED (real chunked clusters at creation); refinement CONSOLIDATES (10 → 7 clusters from 04A → 05) → **binding consequence: the floor must be honored at the LATEST pass (05/05B), not only at creation** — a 04A-only honoring would be silently undone by refinement.
- The two Design Briefs surfaced as distinct units ("The Intrapreneur's Maze…", "Lam's Organizational Reality…") — the party's expected split candidates are visible at the unit level.

## Differential parameters (AC#9, derived from this control)
- **count_K = 7** (05B, the arbiter node). **N = 8** for the differential floor (anti-vacuous: 7 < 8 ≤ achievable via ~2 legitimate seams). **Floor-too-high case: N = 20** (AC#13 honest-refusal).
- AC#10 determinism pin: re-run K through THIS driver (fixed stop condition) before attributing T−K.

## Honest spend accounting
- LLM: **$0.33** (irene_pass1 ×3 gpt-5.4 $0.306; CD ×1 gpt-5 $0.024; texas nano negligible).
- UNPLANNED: node 07 gary ran 4 real Gamma deck generations (1 + 3 auto-retries) before the title-matcher flake paused the run — a consequence of the folded-gate driver defect, not of the baseline design. Fix for the next arms: stop condition = capture-after-05B via run.json contribution presence (or error/G2C pause), not a G2 gate pause.

## Driver defect log (fix before K′/T arms)
`STOP_GATE="G2"` never fires (folded). Next-arm driver: after approving G1, poll run.json for the 05B irene_pass1 contribution and STOP THE WALK THERE (no further resume) — gary must not be reached on baseline arms.
