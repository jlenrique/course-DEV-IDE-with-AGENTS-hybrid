# S6 AC-L — Two-lane LIVE witness PROOF (RECOVERY, post-D7) — GREEN

**Story:** S6 — Tracy/research Scite-canonical (`MARCUS_RESEARCH_DISPATCH_LIVE` default-ON; Scite-scoped; creds-absent degrade; `narrate_research_result` wired; **D7 Irene→dispatch bridge**)
**Role:** INDEPENDENT live-witness, error-pause→**RECOVER** (the FIRST witness was an HONEST RED — dispatch structurally unreachable; D7 fixed it)
**Discipline:** FROZEN judges, executed VERBATIM once each, first-run-stands, NO retry-to-green
**Branch:** `dev/workbook-2026-07-06` · **HEAD:** `6529f76a` + the **uncommitted** S6 diff (flip + Scite-selector + degrade + D7 bridge)
**Corpus:** `course-content/courses/tejal-apc-c1-m1-p2-trends/`
**Python:** `.venv/Scripts/python.exe`, `PYTHONIOENCODING=utf-8`

## VERDICT

| Lane | What it proves | JUDGE verdict |
|------|----------------|---------------|
| **(a)** real cited resolvable-DOI row (the M-wit) | flip live + walk reaches 04.55 + **real Scite dispatch via the D7 path** + real cited resolvable DOI | **PASS (8/8)** |
| **(b)** honest creds-absent degrade ($0) | D4 degrade marker at node entry, $0 Scite, walk proceeds; **BONUS R1** re-dispatch after re-auth | **PASS (4/4) + BONUS R1 PASS** |

**S6 AC-L is GREEN. The D7 fix makes the live research dispatch REACHABLE on the real production path: Irene's `collateral.research_goals[]` now bridge to the §04.55 Scite dispatch (dual-read), which the FIRST witness proved was structurally impossible (dispatch keyed only on `plan_units[].identified_gaps`, which the real Irene never fills).** No production code edited; no commits/pushes/stashes; the S6 diff was run against and left intact.

## THE RECOVERY (what D7 fixed, proven live)

The FIRST witness (`evidence/s6-acl-liveproof-20260707T093933Z/`) was an honest RED: the real Irene-Pass-1 emitted 5 corpus-grounded research goals at `collateral.research_goals`, but every `plan_unit.identified_gaps` was `[]`, and the dispatch read only `identified_gaps` → `in_scope_with_gaps=False` → no dispatch, ever, on any corpus.

D7 (consumer-side dual-read, mechanical field-carry) bridges the two:
- `research_wiring._research_goals_from_raw()` carries `collateral.research_goals[]` into the bridge dict;
- `has_research_goals()` / `run_research_wiring`'s `in_scope_with_gaps` now dual-read (`identified_gaps` OR `research_goals`);
- `irene_bridge.process_plan_locked()` shapes each research goal into a `RetrievalIntent` (pedagogical_intent SEED, `binds_to_objective_id` target, `goal_id` provenance);
- `DeterministicPostureSelector.select_posture()` stamps `research_goal_id` onto each scite provider hint.

**This witness proves that link fires live.**

## Lane (a) — PASS (8/8): real cited resolvable-DOI row via the D7 path

Walk: START on tejal → paused **G0E** → approve → **G0R** → approve → **G1** → approve → continuation walk crossed nodes 04A/04.5/**04.55**/… and paused at **G2B**. The `research_wiring` contribution is present at node **04.55**.

| # | Check | Verdict |
|---|-------|---------|
| 1 | ≥1 `collateral.research_goals` in the locked plan (precondition) | PASS — **4** goals (rg-01…rg-04), Irene-emergent |
| 2 | real Scite dispatch, provider==scite, **provenance→research_goals (D7, NOT identified_gaps)** | PASS — entries=5, all `scite`; **0 in-scope identified_gaps**, 4 research_goals; every shaped intent carries `research_goal_id` on a scite-only hint |
| 3 | ≥1 cited `TexasRow` with `source_id`=real DOI | PASS — 5 real DOIs |
| 4 | DOI RESOLVES (doi.org 200, content-inspected) | PASS — `10.1038/ijo.2010.252` → 200 → nature.com, title verified |
| 5 | `source_ref == retrieval:scite:{DOI}` | PASS — `retrieval:scite:10.1038/ijo.2010.252` |
| 6 | G2 citation-fidelity gate PASSED (not bypassed) | PASS — `unsourced_citations=0`, manifest len 5 |
| 7 | `narrate_research_result` surfaced the cited result | PASS — "Research dispatch complete: 5 cited sources found…" |
| 8 | walk proceeded (past 04.55, not error/halt) | PASS — paused-at-gate **G2B**, contrib node `04.55` |

**The resolved primary cited source (content-inspected):**
- **DOI:** `10.1038/ijo.2010.252`
- **`https://doi.org/10.1038/ijo.2010.252` → HTTP 200 → `https://www.nature.com/articles/ijo2010252`**
- **Title:** *Relative contribution of energy intake and energy expenditure to childhood obesity: a review of the literature and directions for future research* (International Journal of Obesity)
- All 5 cited entries: `10.1038/ijo.2010.252`, `10.1097/acm.0000000000005744`, `10.2196/31977`, `10.1108/02640470910966862`, `10.34197/ats-scholar.2024-0115ps`

**Provenance = `collateral.research_goals` (the D7 path), proven three ways:** (1) the locked plan carried **0** in-scope `identified_gaps` and **4** `collateral.research_goals` — the identified_gaps path yields nothing, so the dispatch could ONLY have come via D7; (2) each shaped `RetrievalIntent` carries its `research_goal_id` (rg-01…rg-04) on a `scite`-only provider hint; (3) the intents' text seeds are verbatim the goals' `pedagogical_intent`.

## Lane (b) — PASS (4/4) + BONUS R1 PASS: honest creds-absent degrade ($0)

Same walk, Scite Bearer FORCED absent via the sanctioned `SCITE_OAUTH_TOKEN_PATH` override → a nonexistent token file → `load_bearer_token()` returns `None` → `_scite_creds_present()` False. Fresh trial `4579f59d`; walk reached **G2B**.

| # | Check | Verdict |
|---|-------|---------|
| 1 | D4 creds-precondition fired at node ENTRY, no dispatch reached | PASS — creds=False, degraded=True, dispatch_reached=False |
| 2 | `research_entries` PRESENT + explicitly-empty + visible marker | PASS — `[]` + "research enrichment skipped — credentials unavailable" |
| 3 | relogin offer + degrade narration | PASS — headed-OAuth relogin offer + degrade narration surfaced |
| 4 | $0 Scite spend; walk proceeded | PASS — 0 dispatches, paused-at-gate G2B |
| **BONUS R1** | after restore creds + re-invoke 04.55, RE-DISPATCHES (not stuck on the degraded contrib) | **PASS** — creds restored → node 04.55 re-dispatched → **5** entries, primary DOI `10.3310/hsdr01140` (doi.org redirects to the real NIHR paper; publisher 403 bot-blocks the landing page — irrelevant to the bonus) |

R1 confirms the idempotency-guard fall-through: a D4-degrade contribution is a recorded NON-result, so a post-re-auth resume re-dispatches instead of short-circuiting.

## Concurrency disclosure (full transparency)

Two lane-a walks ran on trial `181c6621`. The original background process **did not die** — the "paused-at-G1" the coordinator observed was a snapshot taken WHILE that process was mid-G1-resume; it completed at 10:28:21 with **4** cited rows. The resume, launched on the belief it had died, raced it and completed at 10:31:19 with **5** cited rows (a second live Scite dispatch — Scite literature search is non-deterministic in row count). **Both walks independently fired a real Scite dispatch via the D7 path, carried the same primary DOI `10.1038/ijo.2010.252`, and reached G2B.** The judged facts are the intact resume-walk facts (5 entries), internally consistent, judged once. The collision does not affect the verdict — it independently reproduces the D7-reachability result twice. Extra cost: one additional live Scite dispatch (cost is not a constraint per operator directive).

## Quality guardrail (party/J1)

Not triggered on the judged lane — the dispatch FIRED to Scite AND yielded a resolvable DOI (the ideal). No dispatch-reachability RED. (R1's `10.3310/hsdr01140` redirects correctly via doi.org but the NIHR publisher bot-blocks the final landing page with a 403 — a benign publisher-side access nuance on a real paper, on a BONUS lane; not an S6 concern.)

## Freeze-time-vs-run-time validity (first-run-stands)

- **Judges frozen at `2026-07-07T10:20:23Z`** — `judges-frozen.json` records the sha256 of `judge_a.py` (`30bbe88e…`) + `judge_b.py` (`e902381c…`), written **before any lane ran**.
- **Both lanes ran AFTER the freeze** (lane-a walk 10:21–10:31; lane-b 10:33–10:41).
- **Integrity re-checked immediately before each judge:** both sha256 MATCHED the frozen manifest (`verify_freeze.py` output captured).
- **JUDGE-a executed VERBATIM once → PASS 8/8. JUDGE-b executed VERBATIM once → PASS 4/4 + R1 bonus.** No retry-to-green.

## Spend

- **Lane (a) trial LLM:** $0.33139 (irene_pass1 gpt-5.4 ×3 = $0.3145 dominates; cd gpt-5 $0.0166; rest negligible). `MARCUS_G0_DISPATCH_LIVE` UNSET → G0 deterministic.
- **Lane (b) trial LLM:** $0.31698 (fresh irene run).
- **Total LLM ≈ $0.648.**
- **Scite:** no dollar meter (credit-based). Real dispatches: lane-a ×2 (the two concurrent walks), lane-b R1 ×1; lane-b core degrade = **0** dispatches ($0 lane, as designed).

## No-mutation attestation

No production code edited; no commits/pushes/stashes. HEAD remains `6529f76a`; the uncommitted S6 diff (`research_wiring.py`, `irene_bridge.py`, `production_runner.py`, `marcus_spoc.py`, tests) was run against and left intact. Creds-absent was forced via the existing `SCITE_OAUTH_TOKEN_PATH` test/override seam (no SUT mocked). All witness artifacts live under this evidence directory.

## Artifact index

- `judges-frozen.json` — freeze manifest (ts + sha256, pre-lane)
- `judge_a.py` / `judge_b.py` — FROZEN judges (each executed once → PASS)
- `judge_a-facts.json` / `judge_b-facts.json` — per-check verdicts
- `verify_freeze.py` — pre-judge sha256 integrity re-check
- `lane_a_driver.py` — the original lane-a live driver (start→G0E→G0R→G1→04.55)
- `lane_a_resume.py` — the G1-resume driver whose (intact) facts were judged
- `lane_a-facts.json` — judged lane-a facts (5 cited DOIs + provenance + DOI resolution + cost)
- `lane_a-stdout.txt` — the original background walk's log (4 cited rows; concurrency evidence)
- `lane_b_driver.py` / `lane_b-facts.json` — lane-b degrade + R1 re-dispatch
- `witness-facts.json` — one-page machine-readable summary
- `driver-log-lane-a.txt` / `driver-log-lane-b.txt` / `walk-log-lane-*.txt` — logs
