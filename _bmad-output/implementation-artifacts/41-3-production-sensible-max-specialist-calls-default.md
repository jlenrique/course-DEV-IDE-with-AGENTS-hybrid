---
id: 41-3
epic: 41
status: ready-for-dev   # green-lit 4/4 2026-07-16 (Winston/John/Amelia/Murat) — REMOVE the throttle (Option R)
depends_on: 41-2   # rebases on 41-2 (same file production_runner.py, landed 81fdc495)
gate_mode: dual-gate   # LOCKSTEP (production_runner.py) + safety-rail removal
anchor_provenance: HEAD 81fdc495
lockstep: true   # touches app/marcus/orchestrator/production_runner.py (block_mode_trigger_paths)
---

# Story 41.3: Remove the max_specialist_calls throttle — the dollar budget is the guard

Status: done  # 2026-07-16 dev complete (fresh Claude dev agent) + dual-gate review PASS; REMOVE/Option R landed; the bc747b51 completion fix. OPERATOR STEER 2026-07-16: "why have a max specialist calls at all??" → LEADING OPTION = REMOVE it, not default it. Party (Winston) to confirm the safety-rail removal.

> **Operator directive (2026-07-16):** the call-count throttle should probably not exist. There is already a dollar budget guard; the throttle is redundant and its failure mode (default 1, silent, unrecoverable starvation) is a footgun. **Lead with removal**, not with a smarter default. Winston to confirm whether the pre-first-gate "fail cheap" intent needs any replacement (likely not — the dollar budget + gate pauses already bound pre-gate spend; per-node idempotency already prevents dispatch loops).

## Story

As the operator starting a composed Marcus-SPOC production trial (deck + motion + workbook),
I want `max_specialist_calls` to default to a value sufficient for the composed selection — or to fail loud at start when it is provably too low —
so that a real `trial start` never silently runs with a starving call cap that strands the Creative Director (and other specialists) with **no downstream repair possible**.

## Why this story exists (the corrected bc747b51 root cause)

Diagnosis during 41-2 dev proved the **actual** cause of trial `bc747b51`'s §06 CD-miss was **`max_specialist_calls = 1`** (confirmed in the frozen `error-pause.json` runner), NOT a keyless resume. The operator **had** the live key (texas + irene_pass1 dispatched real models); the composed run was starved by a call-count throttle of 1, and CD@4.75 never got a slot.

The throttle default is a footgun the codebase already documents as unrecoverable:
- `run_production_trial(max_specialist_calls: int = 1)` — default **1** (`production_runner.py:3125`); continuation walks re-default to `1` (`or 1`).
- `trial start`'s `--max-specialist-calls` is `required=False` with **no default** → argparse `None` → runner default 1.
- The `--max-specialist-calls` help text itself warns: *"Production starts should open the throttle: under per-node keying, resumes never revisit pre-checkpoint nodes, so **a starved start cannot be repaired downstream.**"*
- The SPOC **interlocutor** already defaults to **12** (`marcus_interlocutor.py:227`), so a run steered through the full interlocutor would not have starved — but the `trial start` path did.

So a composed `trial start` without an explicit `--max-specialist-calls` silently runs at cap 1, starves, and cannot be repaired by resume (per-node keying). 41-2 makes this fail **loud at the node** mid-walk; **41-3 prevents/repairs it at the front door**, which is the only place a starved start CAN be prevented (it can't be repaired downstream).

## Relationship to 41-1 / 41-2

- **41-1** (done) fixes a real but different failure mode (keyless resume). It does NOT fix `bc747b51` (the operator had the key).
- **41-2** (in review) makes the starvation fail **loud at 4.75** (`dispatch.budget-exhausted`) instead of misattributing at §06 — correct, but the run still can't complete.
- **41-3** (this story) makes a composed start **not starve in the first place** — the actual "let the operator complete a trial" fix. Together they cover: fail-loud at start (41-3), fail-loud mid-walk if it slips (41-2), fail-loud on a keyless resume (41-1).

## RATIFIED DECISION — Option R (REMOVE), party 4/4

The party confirmed the operator steer: `max_specialist_calls` is a **tripwire, not a brake** (default 1, silent, unrecoverable starvation). It is removed. The structural bound that remains is **real, not a hand-wave**: the composed manifest is a **finite graph**, **per-node idempotency** dispatches each specialist node at most once (no loops), and **human gate-pauses** give the operator visibility into accumulating spend. The dollar budget stays **advisory (gauge, not brake) for this window** — the real enforced dollar brake is filed as this story's named twin (W-2).

## Acceptance criteria (RATIFIED)

1. **The throttle is gone — no starvation.** The `specialist_calls < max_specialist_calls` condition is removed from BOTH walk specialist branches (`run_production_trial` ~L3650 + `_continue_production_walk` ~L4685 — the same two sites 41-2 touched), and the `or 1` continuation fallbacks (`production_runner.py:3899/4063/4192`) are removed. No specialist node is ever skipped for a call-count reason on a production run. **M-1 pin (1):** a test drives a full composed walk and proves **every** specialist node dispatches with no cap in play (anti-starvation).
2. **The kept brake holds — no dispatch-loop regression.** Per-node idempotency (the already-carrying `get_contribution(specialist_id, node_id)` skip) still prevents any re-dispatch without the call-count counter. **M-1 pin (2):** a test proves a node cannot re-dispatch itself once it carries its contribution, with the counter gone.
3. **`dispatch.budget-exhausted` retires (A-1).** With no call-count budget, that 41-2 tag has nothing to fire on — remove it and its raise path. `dispatch.live-unavailable` (keyless) STAYS (a real fail-loud). **M-1 pin (3):** 41-2's `test_starved_resume_fails_loud_budget_exhausted_at_cd_node` is **retired or repurposed** (e.g. to a keyless `live-unavailable` pin or a full-dispatch anti-starvation pin) — it must NOT be left asserting a tag that can no longer fire.
4. **Interim spend-bound stated in words (W-1, BINDING).** The removal is documented (code comment at the removal site + this AC) with the exact sentence: *"A composed production run's spend is now bounded by the finite composed graph, per-node idempotency, and human gate-pauses; there is no early dollar cutoff until the budget-enforcement follow-on lands."* The operator consents to this interim explicitly; no silent gap.
5. **Inert parameter seam kept (A-1).** `max_specialist_calls` is retained as an inert `None = unbounded` parameter for the test-injection seam (offline/unit tests that want to force starvation may still pass a low value); it just no longer governs production dispatch by default. (Dev may instead delete it entirely if the test seam is not needed — dev's call, documented.)
6. **bc747b51 completes.** Recovering `bc747b51` (or a fresh trial on the same corpus+composition) reaches §06 with a real `cd` contribution because CD@4.75 is no longer starved. (Live-witness owed, operator-gated, post-fix — this is the arc's completion proof.)

## Named twin (W-2 — FILE, do NOT build in this diff)

**`production-runner-dollar-budget-enforced-stop`** — reactivate deferred [`production-runner-07w-budget-guard`] as the real economic **brake**: make `MARCUS_TRIAL_BUDGET_USD` an ENFORCED stop (pause-at-error when a dispatch would cross the budget), not just a `BudgetStatus` report. This is the replacement rail Winston requires; it lands as its own story after 41-3 removes the tripwire. Filed in `deferred-inventory.md` §Named-But-Not-Filed by this story.

## Scope fences (RATIFIED)

- **NO building of dollar-budget enforcement in 41-3** — that is the named twin (W-2), its own diff.
- **NO removal of per-node idempotency** — it is the loop protection that lets the throttle go (AC-2).
- **NO change to gate/orchestration behavior** — only the specialist-branch call-count condition + the `or 1` fallbacks.
- Touches `production_runner.py` (both branches + `or 1` fallbacks) and possibly `app/marcus/cli/marcus_interlocutor.py` (drop the now-moot 12) / `app/marcus/cli/trial.py` (the `--max-specialist-calls` arg — leave it, but its help text updates to "advisory/test seam; no longer starves"). **`production_runner.py` is LOCKSTEP** → dual-gate, pipeline-manifest regime T1 read + Cora block-mode hook + lockstep checker exit 0. Rebases on 41-2 (`81fdc495`).

## References

- `_bmad-output/planning-artifacts/party-greenlight-post-trial-bc747b51-arc-2026-07-16.md` (arc; this story is a during-dev addition)
- `_bmad-output/implementation-artifacts/41-2-specialist-dispatch-fail-loud-silent-skip.md` (the mid-walk twin)
- Frozen: `state/config/runs/bc747b51-…/error-pause.json` (`runner.max_specialist_calls = 1`)
- `app/marcus/cli/trial.py:1299-1308` (the `--max-specialist-calls` help warning), `app/marcus/orchestrator/production_runner.py:3125` (default 1), `app/marcus/cli/marcus_interlocutor.py:227` (interlocutor default 12)

## Green-Light Round Record (2026-07-16)

**Verdict: 4/4 GREEN — REMOVE (Option R)** — Winston (Architect) / John (PM) / Amelia (Dev) / Murat (TEA); orchestrator concurred; no impasse (Quinn/John chain not triggered). Operator steer ("why have a max specialist calls at all?") ratified. Full roundtable in the session record.

| Id | Seat | Amendment | Folded at |
|---|---|---|---|
| W-1 | Winston | Interim spend-bound stated in words (finite graph + idempotency + gate-pauses; no early dollar cutoff until the twin lands); operator consents, no silent gap | AC-4 + Ratified Decision |
| W-2 | Winston/Murat | File the dollar-budget-enforced-stop as 41-3's named twin (the real brake); NOT in this diff | §Named twin + deferred-inventory |
| A-1 | Amelia | Drop the branch condition (both walks) + `or 1` fallbacks; `dispatch.budget-exhausted` retires; keep `max_specialist_calls` as inert `None=unbounded` seam | AC-1/AC-3/AC-5 |
| M-1 | Murat | 3 pins: full-composed-walk anti-starvation; idempotency-still-blocks-re-dispatch; retire/repurpose 41-2's `test_starved_*` (no dead-tag assertion) | AC-1/AC-2/AC-3 |
| J-1 | John | Scope = remove + declare interim + file twin (NOT the brake). Dual-gate, lockstep. Rebases on 41-2 | frontmatter + Scope Fences |

**Why this is the arc's completion fix:** 41-1 fixed keyless resume (a different mode); 41-2 made the starvation fail loud at the node; **41-3 removes the starvation** so a composed trial can actually reach §06 with a real `cd` and complete. It rebases on 41-2 and simplifies it (retires the now-moot budget-exhausted tag). Sequenced ahead of Epic 42 per operator intent (a completable trial soon).

## Dev Agent Record

**Dev complete 2026-07-16 (fresh Claude dev agent). Baseline `81fdc495` (post-41-2). Status → review → done.**

### File List
- `app/marcus/orchestrator/production_runner.py` (M) — removed the `specialist_calls < max_specialist_calls` gate from BOTH walk specialist branches; removed the three `or 1` continuation fallbacks (resume/recover/resume-batch → `runner.get("max_specialist_calls")` = None/unbounded); simplified `_assert_specialist_dispatched_or_raise` (dropped `budget_available` param + the `dispatch.budget-exhausted` branch; `dispatch.live-unavailable` retained); type sigs `int → int | None` throughout; `run_production_trial` default `=1 → =None`; W-1 interim-spend-bound comment at both removal sites.
- `app/marcus/cli/marcus_interlocutor.py` (M) — `max_specialist_calls: int = 12 → int | None = None` (the throttle default is moot).
- `app/marcus/cli/trial.py` (M) — `--max-specialist-calls` help rewritten to "advisory/test seam; no longer starves; omit for unbounded."
- `tests/marcus/orchestrator/test_dispatch_fail_loud_silent_skip.py` (M) — M-1 anti-starvation pins (`test_no_starvation_cd_dispatches_even_when_cap_would_have_starved` cap=0-now-inert; `test_no_starvation_every_specialist_dispatches_uncapped`) + idempotency pin; `dispatch.live-unavailable` keyless pin retained.
- `tests/integration/marcus/test_production_runner_gate_pause_resume.py` (M) — 41-2's `test_starved_resume_fails_loud_budget_exhausted_at_cd_node` **repurposed** to `test_cap_that_used_to_starve_cd_now_dispatches_it_on_resume` (asserts CD dispatches; `!= dispatch.budget-exhausted`; `node != 4.75`) — a durable "throttle didn't come back" pin.
- `tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py` (M) — allowlist note updated for the retirement.

### Completion Notes
- The `max_specialist_calls` throttle is REMOVED (Option R). A specialist node dispatches whenever `_has_live_openai() and not allow_offline_cost_report` — no per-call budget gate. `max_specialist_calls` kept as an inert `None = unbounded` param (test-injection/back-compat seam; no longer governs production dispatch). Interim spend-bound stated in words at both sites (W-1). Dollar-budget-enforced-stop filed as the named twin (W-2).
- `dispatch.budget-exhausted` retired; `dispatch.live-unavailable` (keyless) stays. No test positively asserts the dead tag (verified — remaining refs are negative assertions / docstrings / unrelated `wall-clock-budget-exhausted`).

### Change Log
- 2026-07-16: removed the call-count throttle both walks + `or 1` fallbacks; retired budget-exhausted; anti-starvation + idempotency pins; repurposed the 41-2 starved pin; dual-gate review PASS; done.

## Senior Developer Review (AI) — 2026-07-16 — DUAL-GATE

**Reviewer:** orchestrator, inline adversarial review (run inline, not as parallel test-running subagents, to honor the operator's no-console-window constraint). **Outcome: APPROVE.**

**Correctness:** clean removal — both walk specialist branches now dispatch purely on `_has_live_openai() and not allow_offline_cost_report` (symmetric); guard simplified correctly (offline/dispatched → return; else `live-unavailable`); all three `or 1` continuation fallbacks → `runner.get(...)` (None=unbounded); type sigs consistently `int | None`; default `=None`. **Verified no None-unsafe comparison remains** (`grep` of the current file: zero `specialist_calls < max_specialist_calls` / `budget_available` — a `specialist_calls < None` would have been a latent TypeError on a real run; confirmed absent). W-1 interim comment present both sites.

**Acceptance (AC-1..AC-6):** throttle gone (AC-1) with anti-starvation pins proving CD@4.75 + every specialist dispatch uncapped; idempotency preserved (AC-2, pin); budget-exhausted retired + `test_starved_*` repurposed, no dead-tag assertion (AC-3, M-1.3); W-1 interim declared in words (AC-4); inert param seam kept (AC-5); bc747b51 completion is the owed live-witness (AC-6).

**Verification:** hermetic dispatch test 8/8; targeted regression on the throttle-dependent surface = 45 passed, 8 failed — all 8 **stash-witnessed pre-existing** `PreflightGateFailed @ 3201` (start-preflight environmental, fails before any 41-3 code; identical at the 41-2 baseline with 41-3 stashed); lockstep exit 0; TW-7c-4 audit PASS; ruff clean; import-linter 18/0.

**Findings:** none blocking. One NIT (accepted): `max_specialist_calls` is now a fully inert parameter (kept for the test seam / back-compat) — a mild dead-param smell, intentional per A-1.

**Owed:** the arc's completion proof — an honest recover of `bc747b51` (or fresh trial, same corpus+composition) reaching §06 with a real `cd` — is operator-gated live-witness, post-arc. And the named twin `production-runner-dollar-budget-enforced-stop` (the real dollar brake) is filed HIGH.
