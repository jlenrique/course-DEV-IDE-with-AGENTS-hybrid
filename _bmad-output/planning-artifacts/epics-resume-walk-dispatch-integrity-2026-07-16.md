# Epic 41 — Resume-Walk Dispatch Integrity (2026-07-16)

**Status:** in-progress (green-lit 2026-07-16; `party-greenlight-post-trial-bc747b51-arc-2026-07-16.md`)
**Class:** S — production-runtime correctness. **Priority: BLOCKING** — no further paid Marcus-SPOC walk past G1 on a composed selection until 41-1 lands.
**Dev posture:** fresh-Claude-dev-agent, per-story fresh context. 41-2 is under the pipeline-manifest lockstep regime.

## Why this epic exists

Production trial `bc747b51` error-paused at node 06 with `§06 builder missing upstream contribution(s): cd`. Diagnosis proved this is a **misattributed downstream symptom**: the Creative Director node (4.75) was *entered* but never dispatched, because the operator resumed the run from a fresh shell with no `OPENAI_API_KEY`, and the specialist-dispatch branch **silently advances** when live dispatch is skipped. The failure surfaced three nodes later at the builder's hard `cd` dependency check.

Two defects, one root cause:
- **Front-door (41-1):** `start_trial` hard-requires the live key; resume/recover do not, so a keyless resume silently degrades to a no-dispatch walk.
- **Load-bearing invariant (41-2):** the walk marks a required specialist node "done" even when it emitted nothing, so the class of "silent specialist skip → misattributed downstream fail-loud" is structurally possible in **both** walk copies.

## Binding invariant (Winston, P-2)

> In a production run (`allow_offline_cost_report=False`), a specialist node that is **entered** and is **not already-carrying** its contribution MUST emit a contribution or **fail loud at that node**. Silent advance is forbidden.

Enforced in **both** walks (`run_production_trial` start walk + `_continue_production_walk` resume/recover walk — the two-walk trap: a fix in one copy leaves the other rotten).

## Stories

| Story | Title | Gate | Depends | Lockstep |
|---|---|---|---|---|
| **41-1** | Resume/recover live-env preflight | single | — | no (`trial.py`) |
| **41-2** | Specialist-dispatch fail-loud on silent skip (both walks) | dual | 41-1 | **yes** (`production_runner.py`) |
| **41-3** | Remove the max_specialist_calls throttle (dollar budget is the guard) | dual (candidate) | 41-2 | **yes** (`production_runner.py`) — PROPOSED, needs Winston green-light |

**Sequence:** 41-1 → 41-2 → 41-3. 41-1 fixes a real but *different* mode (keyless resume). 41-2 makes the silent-skip class fail loud at the node.

> **⚠️ DIAGNOSIS CORRECTION (2026-07-16, during 41-2 dev):** the ORIGINAL diagnosis (keyless resume) was **incomplete**. The frozen `bc747b51` runner shows **`max_specialist_calls = 1`** — the operator HAD the live key (texas + irene_pass1 dispatched real models); the composed run was starved by the call-count throttle, and CD@4.75 never got a slot. So:
> - **41-1** fixes a real but *different* failure mode (keyless resume) — it does NOT fix `bc747b51`.
> - **41-2** correctly makes the starvation fail **loud at 4.75** (`dispatch.budget-exhausted`) instead of misattributing at §06 — but the run still can't complete.
> - **41-3** is the actual "let the operator complete a composed trial" fix. Operator steer: **remove** the throttle (the dollar budget is the real guard; a starved start is unrecoverable), not merely re-default it. The CLI help already warns "production starts should open the throttle… a starved start cannot be repaired downstream," yet the default resolves to 1 — a documented, unrecoverable footgun.

## Acceptance (epic-level)

- E41-AC1: a keyless `trial resume` / `trial recover` **fails loud immediately** with an actionable message (name the missing env), not a silent degraded walk. (41-1)
- E41-AC2: a specialist node entered without live dispatch in a production run raises at that node with a tag naming the specialist + cause (`dispatch.live-unavailable`), reproduced RED-first against the frozen `bc747b51` run. (41-2)
- E41-AC3: with `OPENAI_API_KEY` set, an honest recover/fresh trial on the `bc747b51` corpus+composition dispatches CD at 4.75 and reaches 06 with a real `cd` contribution (live-witness, post-fix; own paid run under the Paid-Run Economy Protocol).

## Retrospective

optional (small correctness epic; fold learnings into the next Marcus-SPOC trial postmortem per `docs/trials/methodology.md`).

## References

- `_bmad-output/planning-artifacts/party-greenlight-post-trial-bc747b51-arc-2026-07-16.md`
- `_bmad-output/implementation-artifacts/evidence/operator-hil-display-requirements-2026-07-16.md` §6
- Frozen run: `state/config/runs/bc747b51-7009-4742-9f65-8de6abc29ca4/`
- `docs/dev-guide/pipeline-manifest-regime.md` · `state/config/pipeline-manifest.yaml::block_mode_trigger_paths`
