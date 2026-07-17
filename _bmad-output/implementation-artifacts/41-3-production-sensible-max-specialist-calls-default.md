---
id: 41-3
epic: 41
status: proposed   # NEW finding surfaced during 41-2 dev; needs party green-light confirmation (emerged after the 5/5 arc green-light)
depends_on: null   # independent of 41-1/41-2; addresses the ACTUAL bc747b51 completion blocker
gate_mode: single-gate   # candidate; party to confirm (CLI + a start-preflight check; not the lockstep dispatch branch)
anchor_provenance: HEAD 3919c7fb
---

# Story 41.3: Remove the max_specialist_calls throttle — the dollar budget is the guard

Status: proposed  # surfaced 2026-07-16 during 41-2 dev; the REAL bc747b51 completion blocker. OPERATOR STEER 2026-07-16: "why have a max specialist calls at all??" → LEADING OPTION = REMOVE it, not default it. Party (Winston) to confirm the safety-rail removal.

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

## Option space (party to choose; operator leans REMOVE)

- **Option R (REMOVE — operator-preferred, leading):** eliminate `max_specialist_calls` as a live throttle. The dollar budget (`MARCUS_TRIAL_BUDGET_USD` / cost-report budget guard) becomes the sole economic guard; per-node idempotency already prevents dispatch loops. The `specialist_calls < max_specialist_calls` branch condition and the `or 1` continuation fallbacks are removed; the parameter is either deleted or retained as an inert `None = unbounded` for test injection only. 41-2's `dispatch.budget-exhausted` tag then keys off the **dollar** budget, not a call count.
- **Option D (DEFAULT — fallback if the pre-first-gate fail-cheap intent must survive):** keep the throttle but resolve a production-sensible value at start (≥ composed specialist-node count, or the interlocutor floor 12) and fail loud at start when explicitly set too low. Only if Winston shows the dollar guard doesn't cover pre-gate spend.

## Proposed acceptance criteria (written for Option R; adjust if the party picks D)

1. **The call-count throttle no longer starves runs.** Under Option R, no specialist node is skipped for a `specialist_calls < max_specialist_calls` reason on a production run; the dollar budget is the only economic gate. Under Option D, a composed production `trial start` resolves a cap ≥ the composed specialist-node count (never 1) and fails loud at start if set below it (a starved start is unrecoverable → catch before spend).
2. **The dollar budget is the real, tested guard.** A run that would exceed `MARCUS_TRIAL_BUDGET_USD` still stops honestly (existing budget guard) — verified this remains the enforced economic cap after the throttle is removed/neutralized.
3. **Continuation walks never silently re-throttle to 1.** The `or 1` fallbacks in `_continue_production_walk` / resume / recover / resume-batch (`production_runner.py:3899/4063/4192`) are removed (R) or made a fail-loud-on-missing (D) — a resume never silently re-throttles a production run.
4. **No dispatch-loop regression.** Confirm per-node idempotency (the already-carrying skip) still prevents any runaway re-dispatch without the call-count cap (R) — a pin proving a node cannot re-dispatch itself.
5. **bc747b51 completes.** Recovering `bc747b51` (or a fresh trial on the same corpus+composition) reaches §06 with a real `cd` contribution because CD@4.75 is no longer starved. (Live-witness owed, operator-gated, post-fix.)
6. **41-2 alignment.** 41-2's mid-walk `dispatch.budget-exhausted` fail-loud is re-keyed to the dollar budget (R) so the two stories tell one consistent story; the `test_starved_*` contract tests updated in 41-2 are revisited to match the final guard.

## Scope fences (proposed)

- **NO change to the dollar-budget guard's enforcement** — it becomes the sole/primary economic cap.
- **NO removal of per-node idempotency** — it is the runaway-loop protection that lets the throttle go.
- Touches `app/marcus/cli/trial.py`, `app/marcus/cli/marcus_interlocutor.py` (drop the 12), and `production_runner.py` (branch condition + `or 1` fallbacks) — **`production_runner.py` is LOCKSTEP** → dual-gate, pipeline-manifest regime. Coordinate with 41-2 (same file) to avoid a shared-file collision — likely land 41-2 first, then 41-3 rebases onto it.

## References

- `_bmad-output/planning-artifacts/party-greenlight-post-trial-bc747b51-arc-2026-07-16.md` (arc; this story is a during-dev addition)
- `_bmad-output/implementation-artifacts/41-2-specialist-dispatch-fail-loud-silent-skip.md` (the mid-walk twin)
- Frozen: `state/config/runs/bc747b51-…/error-pause.json` (`runner.max_specialist_calls = 1`)
- `app/marcus/cli/trial.py:1299-1308` (the `--max-specialist-calls` help warning), `app/marcus/orchestrator/production_runner.py:3125` (default 1), `app/marcus/cli/marcus_interlocutor.py:227` (interlocutor default 12)

## Status note

**PROPOSED — needs party green-light.** This finding emerged during 41-2 dev, after the 5/5 arc green-light, so it is not yet ratified. It is arguably the highest-value fix for the operator's actual goal (completing a composed trial), since a starved start is unrecoverable. Recommend green-lighting into Epic 41 and sequencing ahead of further Epic 42 work if the operator wants a completable trial soon.
