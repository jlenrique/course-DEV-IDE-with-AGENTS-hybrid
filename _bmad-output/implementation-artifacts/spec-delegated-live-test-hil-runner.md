---
title: 'Delegated Marcus-SPOC Live-Test HIL Runner'
type: 'feature'
created: '2026-07-13'
status: 'done'
baseline_commit: 'fc5b05cf60819df2b65d01e986c5d2b0b7539579'
review_loop_iteration: 3
context:
  - '{project-root}/CLAUDE.md'
  - '{project-root}/docs/trials/methodology.md'
  - '{project-root}/_bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Live Marcus-SPOC proof runs repeatedly pause for HIL decisions, forcing the operator to remain at the keyboard even when the purpose is bounded product verification. Existing AFK drivers duplicate this logic and cannot be safely reused.

**Approach:** Add a test-only, policy-driven operator surrogate that Juanl explicitly delegates for Epics 36–40 workbook live tests. It must use the real directive-confirmation and `OperatorVerdict`/resume seams, identify itself as a delegate, bind every action to the current decision card, and preserve an auditable journal.

## Boundaries & Constraints

**Always:** Require an explicit versioned delegation policy bound to the test scope and delegate identity; use `codex_hil_runner` rather than impersonating Juanl; validate trial/gate/card/digest identity immediately before each action; run through production `start_trial` confirmation injection and `resume_production_trial`; use bounded loops and an exclusive per-trial lock; write restart-safe, secret-free evidence; treat only exact `completed` as success; preserve first-run evidence.

**Ask First:** Any use outside Epics 36–40 workbook verification; semantic `edit` or `reject` decisions; automatic recovery/re-entry; changing the production gate inventory, verdict schema, HUD, or runner to accommodate the harness.

**Never:** Bypass or directly resume the graph; accept missing/malformed/stale cards; repeat a consumed card digest; silently default an unknown gate; auto-patch a paused run; log credentials; follow symlinks or copy artifacts outside allowed roots; claim a pause, error, timeout, or batch wait as completion; use this harness for customer-facing production approval.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|---------------|----------------------------|----------------|
| Directive gate | Authorized test start and valid composed directive | Inspect structure, record digest, return confirmed through injected seam | Missing/invalid directive stops before dispatch |
| Standard gate | Paused envelope plus matching card and allowed `approve` policy | Emit strict delegated verdict once, resume, journal identities and transition | Any mismatch makes zero resume calls |
| Selection gate | G2B/G4A with offered choices and explicit deterministic policy | Select only offered IDs and journal selection | Missing/ambiguous choices stop at gate |
| Restart | Journal contains submitted card digest | Reconcile current run state without resubmitting that card | Split-brain/unchanged consumed card stops visibly |
| Non-gate pause | Error, failed, unknown, batch wait, or loop/deadline exhaustion | Preserve state and emit non-success summary | No recovery or fabricated completion |

</frozen-after-approval>

## Code Map

- `scripts/utilities/marcus_spoc_live_test_runner.py` — reusable test-only state machine, directive callback, strict policy loader, lock/journal, and attach CLI.
- `tests/fixtures/marcus_spoc/workbook_live_hil_policy.json` — standing delegation policy for the current workbook goal, citing this approved spec as authority.
- `tests/unit/scripts/test_marcus_spoc_live_test_runner.py` — hermetic policy, binding, restart, path, selection, lock, and state-transition coverage.
- `app/marcus/cli/trial.py` — existing injectable G0 confirmation seam; consume unchanged.
- `app/marcus/orchestrator/production_runner.py` — existing authoritative resume seam; consume unchanged.

## Tasks & Acceptance

**Execution:**
- [x] `scripts/utilities/marcus_spoc_live_test_runner.py` — implement strict models, safe file reads, delegated G0 confirmation, card-bound gate loop, exclusive lock, atomic journal/summary, and CLI attachment.
- [x] `tests/fixtures/marcus_spoc/workbook_live_hil_policy.json` — encode Juanl's bounded standing authorization, known gate actions, budgets, and explicit stop classes.
- [x] `tests/unit/scripts/test_marcus_spoc_live_test_runner.py` — prove every I/O case and that all failures make zero unauthorized engine calls.
- [x] `_bmad-output/implementation-artifacts/spec-delegated-live-test-hil-runner.md` — record verification results and final scope.

**Acceptance Criteria:**
- Given an authorized paused workbook trial, when the runner encounters standard and selection gates, then it reaches the requested terminal state using one valid real verdict per card and no keyboard input.
- Given a malformed, stale, unknown, concurrent, replayed, or out-of-scope state, when the runner evaluates it, then it fails closed, preserves evidence, and performs no unauthorized resume.
- Given a runner restart after a state transition, when its local journal lags the run envelope, then reconciliation advances without duplicating the prior verdict.
- Given focused verification, when tests and lint run, then existing production gate/HUD/CLI behavior remains byte- and contract-compatible because no `app/` code changed.

## Spec Change Log

- **2026-07-13 review remediation (iteration 3):** G2B now validates the full
  offered `variant_candidates` list as nonblank and duplicate-free before
  deriving any per-slide selection. Added explicit proofs for malformed offered
  IDs that are absent from the slide rows, with zero engine calls.
- **2026-07-13 review remediation (iteration 2):** Replaced the partial runtime-
  context check with strict validation of the canonical workbook runtime-context
  model; repeated scope/current-envelope validation after the final card rebind;
  made unknown modes fail closed; recomputed the canonical policy digest at every
  public policy+digest entry; and moved the final cooperative deadline check to
  immediately before the submission journal append. Action accounting now advances
  only after that durable append. Added regression proofs for all five findings.
- **2026-07-13 review remediation (iteration 1):** Hardened the implementation
  without changing approved intent: lexical/parent-traversal containment;
  pre-create evidence validation; required workbook course-root/encounter
  context; delegated attach identity and recursive source-tree checks; canonical
  single-read Directive validation; one shared start-to-terminal deadline;
  authoritative resume-return/run.json equality; public-entry locking; and
  per-slide G2B selections from the card's real offered options. Added regression
  proofs for every amendment. Known-bad state avoided: a caller could previously
  invoke public helpers without a lock/root gate, attach to a non-delegate run,
  select one deck-wide G2B ID, or accept a late/mismatched resume result.

## Design Notes

This is a narrowly authorized test delegate, not removal of HIL. The real gate remains, the real card is inspected, and the real tamper-evident verdict is submitted. The distinction from a human verdict is explicit in `operator_id`, policy authority, and evidence.

## Verification

**Commands:**
- `.venv\Scripts\python.exe -m pytest tests/unit/scripts/test_marcus_spoc_live_test_runner.py -q` — expected: all runner cases pass.
- `.venv\Scripts\python.exe -m pytest tests/unit/marcus/cli/test_next_action.py tests/unit/marcus/orchestrator/test_production_runner_gate_pause_resume.py -q` — expected: existing continuation contracts pass.
- `.venv\Scripts\ruff.exe check scripts/utilities/marcus_spoc_live_test_runner.py tests/unit/scripts/test_marcus_spoc_live_test_runner.py` — expected: clean.

**Results (2026-07-13):**

- Runner cases: **42 passed, 1 skipped**. The skip is the explicit Windows
  symlink-capability case when the local account cannot create a symlink; all
  other path, malformed-card, stale-card, replay, restart, selection, budget,
  lock, G0, and stop-state cases passed.
- Existing CLI continuation contract: **9 passed** in
  `tests/unit/marcus/cli/test_next_action.py`.
- The gate-pause continuation test lives at the repository's actual integration
  path, `tests/integration/marcus/test_production_runner_gate_pause_resume.py`.
  Its **9 cases were blocked before the resume subject** by the known live
  preflight baseline (`openai=fail`, with `hud-server-healthz=fail` on some
  workers). This change touches no `app/` path and does not alter that preflight.
- Focused Ruff check: **all checks passed**.

## Completion Notes

- The delegate identity is always `codex_hil_runner`; the policy cannot authorize
  customer-facing approval or any scope other than Epics 36–40 workbook live
  verification.
- G0 is confirmed through `start_trial(confirm_fn=...)` only after the directive's
  trial, corpus, shape, and bytes are inspected and journaled. Later gates use
  production `OperatorVerdict` and `resume_production_trial` unchanged.
- Selection gates use deterministic `select` verdicts over offered IDs only.
  G2B binds the first offered variant independently for every slide from the
  real `pick_context`, while G4A binds the first offered voice. Missing,
  duplicate, blank, stale, or mutated choices stop before engine entry.
- Each submitted card digest is journaled before the engine call. Restart either
  reconciles an already-advanced envelope or refuses split-brain/replay without a
  second call. Summaries are atomic and immutable per attempt.
- The wall-clock deadline is deliberately cooperative and non-preemptive. It is
  checked around synchronous production calls and rejects late returns, but it
  does not use a thread timeout, `os._exit`, or a child-process kill to interrupt
  a hard-hung in-process call; those mechanisms would risk corrupting production
  state or leaving evidence inconsistent.
- CLI start/attach paths enforce policy roots, a per-trial exclusive lock, bounded
  actions/time/calls, workbook scope, regular-file/no-symlink reads, and exact
  `completed`-only success.
- Start requires and passes a validated `course_source_root` plus
  `encounter_mode`; attach revalidates the delegate identity, production preset,
  corpus/course trees, runtime context, and workbook checkpoint before every
  submission. One deadline begins before start/attach and is checked after each
  blocking engine call and immediately before success.

## File List

- `scripts/utilities/marcus_spoc_live_test_runner.py` (new)
- `tests/fixtures/marcus_spoc/workbook_live_hil_policy.json` (new)
- `tests/unit/scripts/test_marcus_spoc_live_test_runner.py` (new)
- `_bmad-output/implementation-artifacts/spec-delegated-live-test-hil-runner.md`
  (updated outside the frozen block; implementation and adversarial review complete)

## Suggested Review Order

**Public boundary and authority**

- Start here: public mode routing, policy binding, and fail-closed entry behavior.
  [`marcus_spoc_live_test_runner.py:1103`](../../scripts/utilities/marcus_spoc_live_test_runner.py#L1103)

- Bind every attached run to the delegated workbook scope and canonical context.
  [`marcus_spoc_live_test_runner.py:503`](../../scripts/utilities/marcus_spoc_live_test_runner.py#L503)

- Validate the versioned policy before any engine or evidence action.
  [`marcus_spoc_live_test_runner.py:271`](../../scripts/utilities/marcus_spoc_live_test_runner.py#L271)

**Gate execution and recovery**

- Drive real cards through one locked, restart-safe, cooperatively bounded loop.
  [`marcus_spoc_live_test_runner.py:698`](../../scripts/utilities/marcus_spoc_live_test_runner.py#L698)

- Build strict approve or deterministic per-slide/voice selection verdicts.
  [`marcus_spoc_live_test_runner.py:566`](../../scripts/utilities/marcus_spoc_live_test_runner.py#L566)

- Confirm G0 only from one canonical, schema-valid directive byte snapshot.
  [`marcus_spoc_live_test_runner.py:950`](../../scripts/utilities/marcus_spoc_live_test_runner.py#L950)

**Evidence and policy**

- Preserve immutable attempt evidence and reconcile interrupted submissions safely.
  [`marcus_spoc_live_test_runner.py:328`](../../scripts/utilities/marcus_spoc_live_test_runner.py#L328)

- Review the exact Epics 36–40 delegation and gate-action policy.
  [`workbook_live_hil_policy.json:1`](../../tests/fixtures/marcus_spoc/workbook_live_hil_policy.json#L1)

**Regression proof**

- Begin with policy identity and scope-contraction proofs.
  [`test_marcus_spoc_live_test_runner.py:256`](../../tests/unit/scripts/test_marcus_spoc_live_test_runner.py#L256)

- Inspect malformed G2B offered-list zero-engine-call coverage.
  [`test_marcus_spoc_live_test_runner.py:368`](../../tests/unit/scripts/test_marcus_spoc_live_test_runner.py#L368)
