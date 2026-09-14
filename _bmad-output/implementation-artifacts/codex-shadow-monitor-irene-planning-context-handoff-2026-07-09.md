# Codex Shadow Monitor - Planning-context to Irene Pass-1 handoff - 2026-07-09

**Arc:** Step 2->3 - purpose, audience, LOs, and source assessment -> Irene Pass-1 -> `lesson_plan` -> downstream assets  
**Branch:** `dev/lesson-planning-2026-07-09`  
**Baseline:** `5be7de46` (`docs: close Phase-2 bridge step-1 and park Irene handoff`)  
**Story:** `_bmad-output/implementation-artifacts/planning-context-to-irene-pass1-handoff.md`  
**Companion monitor:** `_bmad-output/implementation-artifacts/claude-shadow-monitor-irene-planning-context-handoff-2026-07-09.md`  
**Status:** ACTIVE MONITOR / WAITING ON IMPLEMENTATION EVIDENCE

## Standing Watchpoints

1. **Real BMAD seats only.** Party gate and close must name John, Winston, Amelia, and Murat; no `generalPurpose` stand-ins.
2. **Story amendments must stay folded.** Soft LO coverage receipt, fail-loud total LO ignore, merge rules, absent-path compatibility, corpus non-replacement, and no prompt-substring-only proof are binding.
3. **Corpus remains source-of-truth.** Planning context may frame purpose/audience/LO emphasis; it must not become a second corpus or topic substitute.
4. **Optional key, backward compatible.** Absent planning artifacts must preserve current Irene behavior and must not require `planning_context`.
5. **Merge must be deterministic and fail-loud.** `ratified-los.json` owns non-empty LOs; `planning-ratification.json` owns purpose/audience/source assessment; malformed JSON and conflicting non-empty purpose/audience must fail loudly.
6. **Plan emission must show consideration.** Prompt section alone is insufficient; emitted plan/receipt must show context was considered, and total LO ignore with non-empty LOs must fail.
7. **Receipt must not be always-green.** Partial LO coverage may proceed only with a structured supported/weak/missing receipt.
8. **Runner scoping matters.** `planning_context` should thread to Irene Pass-1 only unless a party-approved reason expands scope.
9. **Downstream continuity is load-bearing.** Existing `lesson_plan` through `run.json` / package-builder / specialist paths must remain the continuity path; no parallel selection engine.
10. **S8 and step-1 bridge remain closed.** Do not redesign S8, rebuild the selection bridge, or mutate approved styleguide registry guides.
11. **Per-component live-test evidence is required.** Loader, runner, prompt/receipt, absent path/corpus pin, and downstream continuity should be tested as built, not only at final close.
12. **Scope honesty.** Interactive SPOC REPL, full lecture ingestion, SME routing, projector family, and full compose liveproof are not claimed unless new party-approved evidence lands.
13. **Review and monitor findings must be dispositioned.** `bmad-code-review` MUST-FIX items and shadow-monitor findings must be fixed, deferred-with-ticket, or marked false alarm before done.
14. **Durability.** Story/code/tests/evidence/monitor updates must be committed and pushed before final close is durable.

## Poll Log

### SOP-H000 - arc activated / story ready-for-dev but implementation not yet scoreable - 2026-07-09T18:00:00-04:00

**Scope reviewed:** user-supplied Step 2->3 session goal, `git status --short --branch --untracked-files=all`, latest git log, remote branch tip via `git ls-remote`, promoted story `_bmad-output/implementation-artifacts/planning-context-to-irene-pass1-handoff.md`, companion Claude monitor `_bmad-output/implementation-artifacts/claude-shadow-monitor-irene-planning-context-handoff-2026-07-09.md`, binding SSOT `_bmad-output/planning-artifacts/lesson-plan-rationale-platform-positioning-2026-07-07.md` section 4 and 4.1, and `_bmad-output/planning-artifacts/deferred-inventory.md` entries for the selection spine and course-purpose/LO inputs. No tests were run. No production/test/runtime files were edited by this monitor; this new Codex monitor ledger is the only write.

**Current repo state:** branch `dev/lesson-planning-2026-07-09` is synced with `origin/dev/lesson-planning-2026-07-09` at `5be7de46` (`docs: close Phase-2 bridge step-1 and park Irene handoff`). The worktree already had modified handoff story and Claude handoff monitor files before this Codex ledger was created, plus modified prior Codex Phase-2 monitor and old Irene-literal monitor files. Old Irene-literal untracked evidence/runtime residue remains present under `_bmad-output/implementation-artifacts/evidence/irene-literal-liveproof-20260709T143510/` and `runs/235f2b82-5989-4a6f-9e6b-22e9697f58d2/`.

**Gate evidence:** the handoff story is promoted from `backlog-next` to `ready-for-dev`, baseline updated to `5be7de46`, and the story asserts fully spawned John / Winston / Amelia / Murat party-mode with 4/4 `GO-WITH-AMENDMENTS`. The folded amendments match the operator's requested gate: soft receipt plus fail-loud total ignore, deterministic merge rules, absent-path compatibility, corpus non-replacement, downstream continuity, no full compose DoD, no S8 reopen, no step-1 rebuild, and per-component live-test discipline.

**Companion monitor evidence:** the Claude handoff ledger is now ACTIVE at POLL-000. It names watchpoints for prompt-substring-only false green, receipt always-true, corpus replacement/hash drift, missing fail-loud total-ignore behavior, scope creep into full compose/S8/step-1 rebuild, absent path breakage, and skipped per-component live-test. Its live-test ledger is still all PENDING.

**Implementation/evidence visibility:** no new production code, tests, evidence bundle, local Marcus-SPOC transcript, run artifact, pytest transcript, ruff transcript, or code-review artifact for this handoff is visible in `git status`. The active implementation is not yet scoreable beyond story/gate shape.

**Positive baseline:** the story is correctly scoped to the Step 2->3 claim. It does not try to reopen S8 or replace the step-1 selection bridge, and it keeps planning context as additive framing over the existing corpus-grounded Irene path. The party amendments close several likely false-green routes before code starts.

**F-HANDOFF-0001 [P1] Implementation is not yet scoreable.** The story and monitor are active, but no code/test/liveproof artifacts are visible for PlanningContext loading, runner threading, prompt/receipt behavior, fail-loud total-ignore handling, absent-path compatibility, corpus hash pinning, or downstream continuity.

**F-HANDOFF-0002 [P2] Gate evidence is currently embedded, not independently banked as a party transcript.** The story contains the 4/4 GO-WITH-AMENDMENTS assertion and folded decisions. That is acceptable as the active story gate if banked, but final close should cite either this story record or a separate party record so the party decision remains auditable.

**F-HANDOFF-0003 [P2] Active handoff artifacts are uncommitted.** The story promotion and Claude monitor activation are modified in the worktree. This is normal mid-session, but final close is not durable until story/code/tests/evidence/monitor updates are committed and pushed.

**Scoreability:** story/gate shape is scoreable and aligned with the session goal. Implementation is not scoreable yet. The full Step 2->3 goal remains open until structured planning context reaches Irene Pass-1, shapes emitted plan/receipt behavior, preserves absent/corpus behavior, and proves downstream continuity on the Marcus-SPOC path.

**Verdict: ARC ACTIVATED / READY-FOR-DEV SHAPE GOOD / NO IMPLEMENTATION PROOF YET.** Next monitor poll should look for RED-first tests, loader implementation, runner payload threading, prompt/receipt behavior, corpus hash/absent-path pins, and the first component live-test evidence.

---

### SOP-H001 - concurrent loader slice appeared; AC-H1 partially scoreable by code shape only - 2026-07-09T18:03:00-04:00

**Scope reviewed:** post-baseline `git status --short --branch --untracked-files=all`, new untracked `app/marcus/lesson_plan/planning_context.py`, new untracked `tests/marcus/lesson_plan/test_planning_context.py`, and companion Claude handoff ledger. No tests were run by this monitor poll. No production/test/runtime files were edited by this monitor; this SOP append is the only write.

**Concurrency note:** `planning_context.py` and `test_planning_context.py` appeared after SOP-H000's read point and before this monitor response completed. SOP-H000's "no production code/tests visible" statement was accurate at its read point but is now superseded for AC-H1 only.

**Current repo state:** branch still points at `5be7de46` / `origin/dev/lesson-planning-2026-07-09`. The handoff story and Claude monitor remain modified and uncommitted. This Codex handoff ledger is new/untracked. The first handoff implementation slice is also untracked: `app/marcus/lesson_plan/planning_context.py` and `tests/marcus/lesson_plan/test_planning_context.py`. No runner, Irene contract, prompt/receipt, downstream continuity, evidence bundle, raw pytest, raw ruff, or code-review artifacts are visible yet.

**Loader slice evidence:** `planning_context.py` adds `PlanningContext`, `LearningObjectiveBrief`, `PlanningContextError`, constants for `planning-ratification.json` and `ratified-los.json`, and `load_planning_context(run_dir)`. The loader returns `None` when both artifacts are absent, fails loud on malformed/non-object JSON, loads purpose/audience/source assessment from `planning-ratification.json`, loads non-empty LO statements from `ratified-los.json`, preserves empty LO list without blocking ratification-only context, and returns a JSON-shaped payload.

**Test slice evidence:** `test_planning_context.py` covers absent artifacts, ratification-only load, ratified-LO-only load, merged ratification+LOs, empty `ratified_los`, malformed ratification JSON, and malformed ratified-LO JSON. These are plausible AC-H1 tests, but no raw RED/GREEN transcript or live-test evidence is banked yet.

**F-HANDOFF-0001 status: partially improved for AC-H1 only.** Loader code and tests are now visible. The handoff remains not scoreable as a whole because runner threading, Irene prompt/receipt behavior, fail-loud total-ignore, absent-path corpus pin, downstream continuity, evidence bundle, and review are still absent.

**F-HANDOFF-0003 remains open.** The active story/monitor/code/test artifacts are uncommitted.

**F-HANDOFF-0004 [P1] Merge-rule conflict handling is specified but not visible in the loader slice.** The story says conflicting non-empty purpose/audience across `planning-ratification.json` and `ratified-los.json` must fail loud. The current loader only reads purpose/audience from `planning-ratification.json`; it ignores any such fields in `ratified-los.json`, and the tests do not cover conflict behavior. Required before AC-H1 close: either implement/test the conflict rule or explicitly amend the story to state `ratified-los.json` cannot carry purpose/audience and therefore cannot conflict.

**F-HANDOFF-0005 [P2] No raw component live-test evidence is banked for the loader.** The test file describes RED/GREEN live tests, but no command output, exit code, or evidence artifact is visible. This can be resolved by banking the focused pytest output when the component is tested.

**Scoreability:** AC-H1 is partially scoreable by code/test shape only, not by executed evidence. The overall Step 2->3 handoff remains open and not scoreable as implemented.

**Verdict: FIRST LOADER SLICE VISIBLE / WHOLE HANDOFF NOT SCOREABLE.** Next monitor poll should look for AC-H1 test output and remediation/clarification of the purpose/audience conflict rule before the lane moves on to runner threading.

---

### SOP-H002 - runner-threading slice appeared; AC-H2 partially scoreable by code shape only - 2026-07-09T18:06:00-04:00

**Scope reviewed:** post-SOP-H001 `git status --short --branch --untracked-files=all`, diff for `app/marcus/orchestrator/production_runner.py` and `app/specialists/irene_pass1/payload_contract.py`, new untracked `tests/marcus/orchestrator/test_runner_planning_context_thread.py`, and companion Claude handoff ledger. No tests were run by this monitor poll. No production/test/runtime files were edited by this monitor; this SOP append is the only write.

**Concurrency note:** runner and contract changes appeared after SOP-H001's read point. SOP-H001's "no runner / Irene contract visible" statement is now superseded for AC-H2 only.

**Current repo state:** branch still points at `5be7de46` / `origin/dev/lesson-planning-2026-07-09`. Modified tracked files now include `app/marcus/orchestrator/production_runner.py` and `app/specialists/irene_pass1/payload_contract.py`, in addition to story/monitor docs. Untracked files now include the Codex handoff ledger, `planning_context.py`, loader tests, and runner-thread tests. No Irene prompt/receipt implementation, evidence bundle, raw pytest, raw ruff, downstream continuity proof, live Marcus-SPOC artifact, or code-review artifact is visible yet.

**Runner slice evidence:** `_runner_payload_for_specialist` now builds an Irene-only payload for `irene-pass1` / `irene_pass1`, preserves existing `min_cluster_floor`, lazy-loads `load_planning_context(runs_root / trial_id)`, adds `planning_context` only when present, omits explicit `None` values, and returns `None` for empty payloads. `payload_contract.py` adds `planning_context` to the Irene Pass-1 consumed-key list and documents it as advisory framing while corpus remains the only topic basis.

**Runner test evidence:** `test_runner_planning_context_thread.py` seeds a run dir with `planning-ratification.json` and `ratified-los.json`, asserts both Irene specialist id spellings receive `planning_context`, asserts absent artifacts do not leak the key, and asserts several other specialists do not receive `planning_context`. These are plausible AC-H2 tests, but no raw RED/GREEN transcript or live-test artifact is banked yet.

**F-HANDOFF-0001 status: improved for AC-H1/AC-H2 only.** Loader and runner threading code/tests are now visible by shape. The full handoff remains not scoreable because prompt/receipt behavior, fail-loud total-ignore, plan-emission proof, absent-path corpus hash pin, downstream continuity, review, and committed evidence remain absent.

**F-HANDOFF-0003 remains open.** Story/monitor/code/test artifacts remain uncommitted.

**F-HANDOFF-0004 remains open.** Purpose/audience conflict handling across artifacts remains unspecified in code/tests beyond the story text.

**F-HANDOFF-0005 remains open and now covers AC-H1/AC-H2.** No raw test output or component live-test evidence is visible for the loader or runner-threading slices.

**Scoreability:** AC-H2 is partially scoreable by code/test shape only, not by executed evidence. The overall Step 2->3 handoff remains open and not scoreable as implemented.

**Verdict: LOADER + RUNNER SLICES VISIBLE / PROMPT-TO-PLAN PROOF ABSENT.** Next monitor poll should look for banked test output plus Irene prompt/receipt implementation and fail-loud total-ignore behavior.

---

### SOP-H003 - prompt/receipt slice and focused evidence landed; close still open - 2026-07-09T18:09:11-04:00

**Scope reviewed:** `git status --short --branch --untracked-files=all`, latest git log, remote branch tip via `git ls-remote`, current Codex handoff ledger tail, companion Claude handoff ledger, diff for `app/specialists/irene_pass1/_act.py`, full `tests/specialists/irene_pass1/test_planning_context_handoff.py`, current `app/marcus/lesson_plan/planning_context.py`, evidence bundle `_bmad-output/implementation-artifacts/evidence/irene-planning-context-handoff-20260709T180555/`, and targeted search for the remaining conflict/continuity assertions. No tests were run by this monitor poll; banked test output was inspected. No production/test/runtime files were edited by this monitor; this SOP append is the only write.

**Current repo state:** branch `dev/lesson-planning-2026-07-09` remains synced with `origin/dev/lesson-planning-2026-07-09` at `5be7de46` (`docs: close Phase-2 bridge step-1 and park Irene handoff`). No newer local or remote commit is visible. The worktree is active and uncommitted: story/monitor docs, `production_runner.py`, `irene_pass1/_act.py`, `irene_pass1/payload_contract.py`, new `planning_context.py`, new loader/runner/Pass-1 tests, and a new handoff evidence bundle are present. Old Irene-literal untracked residue remains separate.

**Prompt/receipt implementation evidence:** `irene_pass1/_act.py` now adds a labeled `## Operator planning context (FRAMING ONLY - not corpus)` section when `planning_context` is present. The section states corpus remains the only topic/source-of-truth and includes purpose, audience, source-assessment richness/tags, and LO lines. `act()` now validates `PlanningContext`, computes LO coverage via `assess_lo_coverage`, fails loud on total LO ignore, and emits `planning_context_coverage` in the output when context is present.

**Coverage implementation evidence:** `planning_context.py` now adds `PlanningContextCoverageReceipt`, `assess_lo_coverage()`, and `assert_lo_coverage_or_fail()`. Coverage status is `present`, `partial`, or `absent`; partial coverage proceeds with supported/missing IDs; absent coverage with non-empty LOs raises `SpecialistDispatchError` tagged `irene_pass1.planning_context.lo_ignore`.

**Focused test/evidence visibility:** new `tests/specialists/irene_pass1/test_planning_context_handoff.py` covers labeled prompt section, absent prompt section, partial receipt, fail-loud total ignore, fail-loud empty plan units with LOs, `act()` emitting partial coverage receipt, `act()` failing on total ignore, absent-path `act()` with no receipt, corpus hash unchanged after prompt assembly, and lesson-plan artifact continuity. Evidence bundle `irene-planning-context-handoff-20260709T180555/` contains `PROOF.md` and `pytest-handoff.txt`; the raw pytest output reports `20 passed in 9.07s`.

**Positive scoreable movement:** AC-H1 through AC-H5 now have visible code/test/evidence coverage by focused tests. AC-H4 and part of AC-H6 have focused evidence through absent-path prompt behavior, absent-path `act()` behavior, corpus hash pinning, and lesson-plan artifact writing. The proof correctly fences out interactive SPOC REPL, full lecture ingestion, S8 redesign, step-1 rebuild, and full compose liveproof.

**F-HANDOFF-0001 status: mostly resolved for focused component proof, still open for final close.** The main handoff behaviors are now covered by local focused tests and banked raw output. The story is still not done because review, final party close, inventory/STATE/project-context updates, commit/push, and complete downstream continuity proof remain outstanding.

**F-HANDOFF-0003 remains open.** All handoff implementation/evidence artifacts remain uncommitted and unpushed.

**F-HANDOFF-0004 remains open.** The story requires conflicting non-empty purpose/audience across artifacts to fail loud. Current code comments say this is "reserved for future," and `ratified-los.json` purpose/audience conflict behavior is not implemented or tested. Required before AC-H1 close: implement/test the conflict rule or explicitly amend the story/party decision so this is not a required behavior for the current artifact schema.

**F-HANDOFF-0005 status: improved but not fully closed.** Raw focused pytest output is now banked (`20 passed`). No ruff output is visible, and no separate RED-first transcript is visible. Per-component live-test evidence is present as a focused suite and proof note, but the live-test ledger in the companion Claude monitor still shows PENDING rows.

**F-HANDOFF-0006 [P1] Package-builder continuity is not directly proven.** The story's downstream done-bar calls for prompt+plan+receipt+package-builder continuity. The visible tests prove `lesson_plan` remains in the output and a lesson-plan artifact is written, but they do not exercise an existing package-builder or specialist consumer path. Required before close: add/cite direct package-builder continuity evidence, or amend the done-bar to state artifact/output continuity is the accepted downstream pin.

**F-HANDOFF-0007 [P2] No code-review or close-party evidence is visible yet.** No `bmad-code-review` artifact, review transcript, remediation log, final BMAD close, or updated inventory/STATE/project-context for the handoff is visible in this poll.

**Scoreability:** the implementation is now scoreable as an uncommitted focused component implementation for loader -> runner -> Irene prompt/coverage receipt -> lesson-plan artifact continuity. It is not yet scoreable as a completed Step 2->3 handoff because package-builder continuity, review/close, durable docs, and commit/push are still missing.

**Verdict: COMPONENT PROOF LANDED / HANDOFF NOT CLOSED.** The arc made real progress since SOP-H002, but final scoring should remain open until the conflict-rule and package-builder continuity gaps are resolved or explicitly fenced, review/party close lands, and the full close set is committed and pushed.
