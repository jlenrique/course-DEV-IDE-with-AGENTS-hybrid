---
id: 41-2
epic: 41
status: ready-for-dev
depends_on: 41-1
gate_mode: dual-gate   # block_mode/lockstep + load-bearing runtime invariant
anchor_provenance: HEAD 23480353  # all line anchors verified against this tree; re-verify at dev-open
lockstep: true   # touches app/marcus/orchestrator/production_runner.py (block_mode_trigger_paths)
---

# Story 41.2: Specialist-dispatch fail-loud on silent skip — both walks

Status: ready-for-dev  # green-lit 5/5 2026-07-16; dual-gate; LOCKSTEP; RED-first vs bc747b51

## Story

As the production runtime,
I want a specialist node that is entered and does not emit its contribution to **fail loud at that node** (naming the specialist and the cause) instead of silently marking itself complete,
so that a skipped required specialist (e.g. CD @ 4.75) can never again surface as a misattributed downstream error (`builder.gary.upstream-missing` at §06) three nodes away from the real cause.

## Provenance & Dependencies (BINDING)

- **Epic authority:** `epics-resume-walk-dispatch-integrity-2026-07-16.md` §Story 41-2 (E41-AC2) + the **binding invariant** (Winston P-2).
- **Green-light:** `party-greenlight-post-trial-bc747b51-arc-2026-07-16.md` — P-1 (two-story split), P-2 (invariant, both walks), P-3 (RED-first vs `bc747b51`).
- **Depends on 41-1:** the front-door preflight lands first. 41-2 is the defense-in-depth that makes the CLASS of silent-skip impossible even if a future path (offline-flag slip, budget exhaustion, a new skip branch) reopens it.
- **Two-walk trap (memory `project-production-runner-two-walks`):** the invariant MUST land in BOTH the start walk (`run_production_trial`, specialist branch ~L3595-3637) and the resume/recover walk (`_continue_production_walk`, specialist branch ~L4587-4627). A fix in one copy leaves the other rotten.

## Binding invariant (the spec sentence — Winston P-2)

> In a production run (`allow_offline_cost_report=False`), a specialist node that is **entered** and is **not already-carrying** its contribution MUST emit a contribution or **fail loud at that node**. Silent advance is forbidden.

## T1 Readiness (BINDING readings before any code)

1. **Lockstep gate FIRST:** `docs/dev-guide/pipeline-manifest-regime.md` + `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` (`production_runner.py` IS a trigger row). Read before any code; Cora block-mode hook gates this story.
2. `app/marcus/orchestrator/production_runner.py` — the **two** specialist-dispatch branches:
   - Start walk (`run_production_trial`, L3061): L3595-3637 — `if node_kind == "specialist" and specialist_calls < max_specialist_calls:` → already-carrying skip (L3600-3609) → `if _has_live_openai() and not allow_offline_cost_report:` dispatch (L3610-3636) → **`graph_step_completed = True` (L3637) set unconditionally**.
   - Resume/recover walk (`_continue_production_walk`, L4102): L4587-4627 — same shape; `allow_offline_cost_report` read at L4150 (`runner.get(..., False)`); **`graph_step_completed = True` (L4627) set unconditionally**.
   - `_has_live_openai` (L211), `_active_node_handler` (L1838), `__production_node_kind__`/`__production_specialist_id__` stamping (L2070-area).
3. **The idempotent-resume path is legitimate and must be preserved:** the already-carrying skip (L3600/L4590) is correct — a resumed node that already has its contribution is not re-dispatched. The fail-loud must fire ONLY for entered-and-NOT-carrying-and-NOT-dispatched, never for already-carrying.
4. Frozen `bc747b51` run dir — the RED reproduction substrate (`run.json`, `error-pause.json`, node path 04.55 → 4.75 → 05/05B → 06).
5. Existing offline-harness tests that resume/run with `allow_offline_cost_report=True` — they MUST stay green (the fail-loud is gated on `not allow_offline_cost_report`).

## Acceptance Criteria

1. **Fail-loud at the node — resume/recover walk.** In `_continue_production_walk`, when `node_kind == "specialist"`, the node is NOT already-carrying, and dispatch did NOT run because live was unavailable while `allow_offline_cost_report=False`, the walk raises at that node with a tag `dispatch.live-unavailable` (or a shared, specific tag) and a message naming the specialist_id + node.id + cause — instead of `graph_step_completed = True`. The raise carries enough context to error-pause honestly at that node (specialist_id, node_id, node_index).
2. **Fail-loud at the node — start walk.** The SAME invariant lands in `run_production_trial`'s specialist branch (L3595-3637). Both walks enforce identically (a shared helper is preferred so they cannot drift — Yui/Winston).
3. **RED-first vs the frozen trial (P-3, BLOCKING evidence bar).** A test reconstructs a keyless resume walk (`_has_live_openai()` False, `allow_offline_cost_report=False`) over the `bc747b51` manifest+envelope shape, drives it to node 4.75, and asserts it raises `dispatch.live-unavailable` **at 4.75** — NOT `builder.gary.upstream-missing` at 06. This test must be RED against the current code (proving the misattribution) and GREEN after the fix. No live call.
4. **Idempotent resume preserved.** A node already carrying its contribution still skips cleanly (no raise) — the already-carrying branch is untouched. Pin: a resume where 4.75 already has a `cd` contribution advances past it silently and correctly.
5. **Offline harness preserved.** With `allow_offline_cost_report=True`, specialist nodes still skip dispatch WITHOUT raising (offline reports never dispatch live) — the fail-loud is strictly gated on `not allow_offline_cost_report`. Existing offline-harness suites stay green.
6. **Budget/max-calls is a DISTINCT honest stop (not folded into this tag).** If `specialist_calls >= max_specialist_calls` causes the branch to be skipped, that is a budget condition — it must ALSO not silently advance a required node, but it raises a budget-specific tag (`dispatch.budget-exhausted` or the existing budget-guard path), not `live-unavailable`. Name the two causes distinctly so the operator sees the true reason. (If the existing budget-guard already fail-louds elsewhere, cite it and assert this branch defers to it; do not double-raise.)

## Scope Fences (hard NO)

- **NO change to the already-carrying idempotency contract** (S2 per-node keying) — it stays exactly as-is.
- **NO change to the offline-harness dispatch-skip** except that a required node in a production run raises; offline (`allow_offline_cost_report=True`) is untouched.
- **NO change to `trial.py`** — that's 41-1.
- **NO widening of what counts as "required"** beyond the invariant: entered + not-already-carrying + not-dispatched in a production run. Do not add per-node "required" manifest flags this pass (a specialist node that is traversed in a production run is required by construction — if it were optional it would be composed out of the manifest).
- **NO silent gate/orchestration behavior change** — only the specialist branch of both walks.
- **Mid-dev drift into any OTHER trigger row** (`workbook_wiring.py`, `pipeline-manifest.yaml`, `operator_surface_assembler.py`, `production_trial_envelope.py`, etc.) is a STOP → party-gate.

## Lockstep declaration

| Scoped file | Trigger-path entry? | Touched? |
|---|---|---|
| `app/marcus/orchestrator/production_runner.py` | **trigger (manifest)** | **yes** (both specialist branches — fail-loud invariant) |
| `app/marcus/cli/trial.py` | not listed | **NO** (41-1) |

**Verdict: lockstep regime TRIGGERED.** Read `pipeline-manifest-regime.md` at T1; Cora block-mode hook gates; lockstep checker (`check_pipeline_manifest_lockstep.py`) exit 0 required before review.

## Dev Notes

- Prefer a shared helper, e.g. `_assert_specialist_dispatched_or_raise(*, node, specialist_id, node_index, dispatched, allow_offline_cost_report)` called from both walks right where `graph_step_completed = True` is set today, so the two copies enforce ONE implementation (two-walk trap defense). Track whether dispatch actually ran (the `if _has_live_openai() and not allow_offline_cost_report:` branch) via an explicit local, and raise when required-and-not-dispatched-and-not-already-carrying.
- The raise should produce the same honest error-pause shape the builder path uses (tag + message + node context) so the operator sees `dispatch.live-unavailable @ 4.75 (cd)` instead of `builder.gary.upstream-missing @ 06`.
- Keep the `specialist_calls < max_specialist_calls` outer condition semantics in mind: if that outer guard is False, the branch body (including any new raise) does not run — handle budget as AC-6 specifies (distinct tag or defer to the existing budget-guard), don't let a budget-exhausted required node silently advance either.
- Tests: `tests/marcus/orchestrator/test_dispatch_fail_loud_silent_skip.py` (new) — both-walk RED-first vs `bc747b51` shape (AC-3); idempotent-resume preserved (AC-4); offline preserved (AC-5); budget-distinct-tag (AC-6); start-walk parity (AC-2). Fixtures = mutated copies of the frozen `bc747b51` run shape (live-shape rule), never synthetic. No live LLM/network.

## References

- `_bmad-output/planning-artifacts/epics-resume-walk-dispatch-integrity-2026-07-16.md` (§invariant)
- `_bmad-output/planning-artifacts/party-greenlight-post-trial-bc747b51-arc-2026-07-16.md` (P-1/P-2/P-3)
- `docs/dev-guide/pipeline-manifest-regime.md` · `state/config/pipeline-manifest.yaml::block_mode_trigger_paths`
- memory `project-production-runner-two-walks` (both-walk discipline)
- `state/config/runs/bc747b51-7009-4742-9f65-8de6abc29ca4/{run.json,error-pause.json,cost-report.json,operator-surface.json}`

## Green-Light Round Record (2026-07-16)

**Verdict: 5/5 GREEN** — Winston/John/Amelia/Murat/Sally, orchestrator concurred. Folded: P-1 (two-story split, one head); P-2 (invariant sentence, BOTH walks, shared helper); P-3 (RED-first vs `bc747b51` asserting fail-loud AT 4.75 not at 06); Murat's AC-6 (budget is a distinct honest stop, distinct tag); the idempotent-resume + offline-harness preservation fences. Dual-gate per Winston (lockstep + load-bearing invariant). Status → ready-for-dev.
