# S6 AC-L — Two-lane LIVE witness PROOF (HONEST RED — mid-witness production defect)

**Story:** S6 — Tracy/research Scite-canonical (`MARCUS_RESEARCH_DISPATCH_LIVE` default-ON; Scite-scoped; creds-absent degrade; `narrate_research_result` wired)
**Role:** INDEPENDENT live-witness (two-lane, FROZEN judges, first-run-stands, NO retry-to-green)
**Branch:** `dev/workbook-2026-07-06` · **HEAD:** `6529f76a` + the **uncommitted** S6 diff in the working tree
**Corpus:** `course-content/courses/tejal-apc-c1-m1-p2-trends/` (real APC "trends" lesson — the ideal literature-rich corpus)
**Python:** `.venv/Scripts/python.exe`, `PYTHONIOENCODING=utf-8`

## VERDICT

| Lane | What it would prove | JUDGE verdict |
|------|----------------|---------------|
| **(a)** real cited resolvable-DOI row (the M-wit) | flip live + walk reaches 04.55 + real Scite cited DOI row | **FAIL (1/7)** — no dispatch fired; **blocked by a production defect** (below) |
| **(b)** honest creds-absent degrade | D4 degrade marker at node entry, $0 | **NOT RUN — blocked by the SAME defect** (degrade precondition is gated behind the same unreachable `in_scope_with_gaps`) |

**This witness does NOT close S6. A genuine production-codebase defect surfaced mid-witness (S3/S4 precedent): the live research dispatch is UNREACHABLE on the real production trial path.** Reported honestly; the orchestrator decides. No fake gap injected; no production code edited (per the binding contingency).

## THE DEFECT (headline finding)

**Irene emits research-enrichment intent as `lesson_plan.collateral.research_goals[]`, but the §04.55 dispatch keys on `lesson_plan.plan_units[].gaps[]` (`IdentifiedGap`). The two fields are never bridged — so the live dispatch never fires no matter the corpus or creds.**

- On this trial, the REAL live Irene-pass1 run (`gpt-5.4`, 3 calls) produced **5 real, corpus-grounded, Irene-EMERGENT research goals** at `collateral.research_goals` — e.g. *"Learner needs the primary-source basis for the national expenditure and practice-ownership trend figures to trust the opening structural argument."* This is exactly the M-wit's "real research gap."
- YET all 11 in-scope `plan_units` carried **`gaps = []`** (0 total). `research_wiring.has_research_goals()` / `_plan_dict_for_bridge_from_raw()` read `unit.get("gaps")` → False → `in_scope_with_gaps = False` → the node short-circuited to an empty (non-degrade) `research_entries` and narrated *"no cited sources."* **No Scite dispatch was attempted.**
- `plan_units[].gaps` is populated ONLY by `trial_smoke_harness.py:117` (a smoke fixture — off-limits per "no fake gap"), by tests, or by a manual operator edit at the G1A poll surface (`app/gates/section_04a/poll_surface.py:34`, `gaps` is editable). The real `irene_pass1` producer never populates it (grep of `app/specialists/` finds zero `IdentifiedGap` construction).
- Airtight grep: `collateral.research_goals` is consumed ONLY by `collateral_spec.py` (schema) and `irene_pass1/_act.py` (emit + artifact render). **Nothing** maps `research_goals` → `gaps` / `IdentifiedGap` / the Tracy bridge / the dispatcher. `has_research_goals()` is misleadingly named — it reads `gaps`, never `research_goals`.

**Consequence:** the S6 D1 flip is live and correct, and the walk reaches §04.55 on the continuation walk — but the upstream gap-detection it depends on is not wired to Irene's real output. The live research dispatch (lane a) AND the creds-absent degrade (lane b, gated behind the same `in_scope_with_gaps`) are both unreachable on a pure auto-approve production walk. This is corpus-independent: this corpus produced the ideal 5 real goals and still could not dispatch.

Full evidence: `defect-evidence.json` (the 5 research_goals verbatim, gaps=0, code citations).

## What the witness DID prove live (partial, honest)

- **D1 flip is live (default-ON):** after `load_dotenv(override=True)`, `MARCUS_RESEARCH_DISPATCH_LIVE` was **absent by exact name**; `_research_dispatch_live()` returned **True**. `_scite_creds_present()` returned **True** (real 504-char OAuth Bearer token). Ready retrieval providers: `['consensus','gamma_docs','scite']` (scite sorts last — the exact D2 point the old `ready[:2]` selector would have excluded).
- **Walk reaches §04.55 on the continuation walk:** START on the tejal corpus paused at **G0E**; approve G0E → **G0R** → approve → **G1** → approve → continuation ran nodes 04A/04.5/**04.55**/4.75/05 and paused at **G2B**. The `research_wiring` contribution is present at node `04.55` (JUDGE-a check 7 PASS).
- **D5 narration wired:** `narrate_research_result` rendered the review-only line on the real contribution — but, correctly for the empty state, *"Research dispatch: no cited sources for this lesson."*
- **No silent failure:** `research_entries = []`, `dropped_dispatch_failures = {count:0}`, no degrade marker — consistent with the "no in-scope gap" short-circuit (not an error, not a halt).

## Freeze-time-vs-run-time validity (first-run-stands)

- **Judges frozen at `2026-07-07T09:40:33Z`** — `judges-frozen.json` records the sha256 of `judge_a.py` + `judge_b.py`, written **before any lane ran**.
- **The lane-(a) walk ran AFTER the freeze** (start `09:43:12Z`, 04.55 reached `09:49:37Z`).
- **Integrity re-checked at execution:** `judge_a` sha256 `10df7de0…` and `judge_b` `87729070…` both MATCHED the frozen manifest immediately before running.
- **JUDGE-a executed VERBATIM exactly ONCE** against the on-disk `lane_a-facts.json` → **FAIL (1/7)**. No retry-to-green. JUDGE-b was **not executed** (lane b blocked by the shared root cause; running a walk that cannot exercise the degrade would be theater).

## JUDGE-a result (1/7)

| # | Check | Verdict |
|---|-------|---------|
| 1 | real Scite dispatch, provider==scite | FAIL — entries=0 (no dispatch) |
| 2 | cited entry with real DOI | FAIL — no entries |
| 3 | DOI resolves via doi.org | FAIL — no DOI |
| 4 | source_ref == retrieval:scite:{DOI} | FAIL — no entry |
| 5 | G2 gate passed (not bypassed) | FAIL — no cited entries to gate |
| 6 | narration surfaced cited result | FAIL — narrated "no cited sources" (empty path) |
| 7 | walk proceeded (reached 04.55) | **PASS** — paused-at-gate G2B, contrib at 04.55 |

## Spend

- **Lane (a) total: $0.303360** (real main-walk LLM — `irene_pass1` gpt-5.4 ×3 = $0.286320; `cd` gpt-5 $0.016761; rest negligible). MARCUS_G0_DISPATCH_LIVE kept UNSET → G0 pre-pass deterministic ($0). Full breakdown: `lane_a-cost-report.md`.
- **Scite spend: $0** — no dispatch fired (the defect). Lane (b) not run: **$0**.

## No-mutation attestation

No production code edited; no commits/pushes/stashes. The uncommitted S6 diff was run against and left intact. No fake gap injected; no operator G1A gap-edit workaround used (that would author the gap content, violating the "Irene-emergent, not injected" M-wit requirement). All witness artifacts live under this evidence directory.

## Recommendation to the orchestrator (party decides)

The S6 flip + wiring is internally correct, but the **research-enrichment link from Irene to the dispatch is broken on the real path**: dispatch reads `plan_units[].gaps`; Irene fills `collateral.research_goals`. Options:
1. **Bridge the fields** — map `collateral.research_goals` → the Tracy dispatch (or make `has_research_goals`/`_plan_dict_for_bridge_from_raw` read `collateral.research_goals`). This is the production fix that makes the SPOC research enrichment actually reachable — a genuine product improvement (per the CLAUDE.md guardrail: fix because it improves the SPOC product, not to make a proofing run pass).
2. Confirm whether gap-population at G1A was ever intended to be the ONLY path (operator-declared gaps) — if so, `has_research_goals`'s docstring ("research-enrichment gap") and the D1 default-ON framing are misleading, since the canonical auto-approve run can never dispatch.

Either way, **S6's M-wit cannot be honestly witnessed until the Irene→dispatch gap link is wired.** Do not close S6 on this evidence.

## Artifact index

- `judges-frozen.json` — freeze manifest (ts + sha256, pre-lane)
- `judge_a.py` / `judge_b.py` — FROZEN judges (judge_a executed once → FAIL 1/7; judge_b not run)
- `judge_a-facts.json` — per-check verdicts
- `lane_a_driver.py` — the lane-(a) live driver (start→G0E→G0R→G1→04.55)
- `lane_a-facts.json` — captured lane-(a) facts (entries=0)
- `defect-evidence.json` — **the 5 real Irene research_goals + gaps=0 + code citations (the defect)**
- `lane_a-cost-report.md` / `.json` — spend
- `probe_preflight.py` — creds/flip/provider preflight
- `diag_contributions.py` / `diag_plan_units.py` / `diag_collateral.py` — diagnostic scripts
- `driver-log-lane-a.txt` / `walk-log-lane-a.txt` — logs
