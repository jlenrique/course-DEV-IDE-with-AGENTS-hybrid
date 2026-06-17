---
title: 'Taxonomy re-base — tranche 2: BuilderInputError re-base + node-06 builder-node error-pause wrap (close the live-walk KILL asymmetry)'
type: 'bugfix'
created: '2026-06-17'
status: 'done'
baseline_commit: '262101a'
checkpoint_1: 'RATIFIED 2026-06-17 — bmad-party-mode green-light (Winston/Amelia/Murat/John: APPROVE / APPROVE-WITH-AMENDMENTS, unanimous live-path-only Q2) + conflict-adjudication round (COMPATIBLE — error-pause honors the S5-crit-5/Finding-#8 fail-loud intent; mechanism migrated crash→error-pause, contract preserved)'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/spec-taxonomy-rebase-live-path.md'
  - '{project-root}/_bmad-output/planning-artifacts/deferred-inventory.md'
  - '{project-root}/next-session-start-here.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem (the live-walk KILL asymmetry):** Tranche 1 (`37f8323`) re-based the five live-path specialist classes so a mid-walk dispatch failure error-pauses recoverably. But `BuilderInputError` (`app/marcus/orchestrator/package_builders.py:44`) is still a bare `RuntimeError`, AND its only live invocation — `run_builder_node` at the §06 manifest node — is called at `production_runner.py:1332` (start-walker) and `:1771` (recover-walker) **outside any `except SpecialistDispatchError` guard.** Edge-review of tranche 1 proved this is the *only* remaining live-walk dispatch leg not in the error-pause family: a node-06 starvation (missing `irene_pass1`/`cd` upstream, malformed lesson-plan, contract violation) **kills the whole trial cycle** and loses paid work, while the sibling node-07 (gary) now pauses. This is the sharpest tranche-2 robustness win (rider `tagged-error-taxonomy-systematic-rebase`; deferred finding from the tranche-1 review).

**Approach (two coupled moves):**
1. **Re-base** `BuilderInputError(RuntimeError)` → `BuilderInputError(SpecialistDispatchError)`. The base's `(message, *, tag)` constructor is byte-identical to `BuilderInputError`'s, so the redundant `__init__` is deleted and every existing handler is preserved (`SpecialistDispatchError` is `RuntimeError`-derived). This alone is necessary-but-not-sufficient — re-basing makes it *catchable* by the family handler, but nothing catches it at the builder node yet.
2. **Wrap** both `run_builder_node` call sites in `try/except SpecialistDispatchError → _pause_at_error(... specialist_id=BUILDER_SPECIALIST_ID ...)`, mirroring the existing specialist-dispatch and storyboard-publisher pause branches verbatim. This converts node-06 crash→error-pause; `trial recover` re-enters the failed builder node (the helper stores `node_index` unshifted, exactly the recover contract for a non-gate failed node).

Retire the `BuilderInputError` EXCLUSIONS row (the reverse-existence pin `test_exclusions_rows_still_name_live_bare_classes` demands retirement once it re-bases).

**SCOPE DECISION DEFERRED TO PARTY-MODE:** whether tranche 2 also sweeps the remaining 12 off-live-path EXCLUSIONS classes (aria/kim/mira/tamara/vyx `OperatorInstructionsParseError`, cd `CdDirectiveParseError`, dan `DanAuxParseError`, desmond `HandoffParseError`, tracy `ManifestParseError`/`RetrievalIntentParseError`, wanda `WandaActError`, enrique legacy-probe `ElevenlabsDispatchError`) or defers them to a tranche 3. Author's recommendation: **live-path-only tranche 2** (tight diff, single anchor; the 12 are unexercised parser seams / legacy probe, each needing its own catch-site grep audit per tranche-1 discipline). See §Tasks.

## Boundaries & Constraints

**Always:** `BuilderInputError` keeps its name, docstring, and tag-carrying constructor semantics (base provides them — delete the redundant `__init__`). The builder-node wrap is a verbatim mirror of the proven specialist/storyboard pause branches — same `_pause_at_error` kwargs, same control flow (`return _pause_at_error(...)`). Live-path **success** behavior byte-identical; only the failure path changes crash→error-pause. EXCLUSIONS shrink-only. Catch-site evidence recorded.

**Ask First (party-mode):** Sweeping any of the 12 off-path classes (the scope decision above). Any change to `run_builder_node`'s success-path return shape or the `_pause_at_error` signature. Touching the §6.2/§6.3/§06B orchestration no-op builders.

**Never:** No gate-engine / manifest / pack changes (engine FROZEN for Trial A — zero production-walk behavior change on success). No new fixture branches. No change to builder idempotency / skip-rule semantics.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| node-06 builder raises mid-walk (start) | live trial, missing `irene_pass1`/`cd`, or bad lesson-plan | Runner error-pauses; `error-pause.json` persisted; `trial recover` re-enters node-06 | `BuilderInputError` tag persisted; walk progress kept |
| node-06 builder raises mid-walk (recover) | recovered trial re-running §06 | Same as start-walker | Same |
| node-06 builder succeeds | live path, grounded upstream | Unchanged — contribution added, walk continues | N/A |
| node already carries builder contribution | resume/recover idempotency | Unchanged — `run_builder_node` short-circuits, no raise | N/A |
| `issubclass(BuilderInputError, ...)` | type check | `SpecialistDispatchError` AND `RuntimeError` both hold | N/A |
| EXCLUSIONS still names `BuilderInputError` | post-re-base | reverse-existence pin FAILS until row retired | row deleted in same diff |

</frozen-after-approval>

## Code Map

- `app/specialists/dispatch_errors.py:15` — base is `RuntimeError`-derived; identical `(message, *, tag)` ctor
- `app/marcus/orchestrator/package_builders.py:44` — `BuilderInputError`; re-base + drop redundant `__init__`; import the base
- `app/marcus/orchestrator/production_runner.py:1322-1340` — start-walker §06 builder branch (wrap target)
- `app/marcus/orchestrator/production_runner.py:1764-1779` — recover-walker §06 builder branch (wrap target)
- `app/marcus/orchestrator/production_runner.py:1058` — `_pause_at_error` helper (already imports `SpecialistDispatchError` at `:62`; `package_builders` already imported)
- `tests/contracts/test_specialist_error_taxonomy.py:39` — retire the `BuilderInputError` EXCLUSIONS row; add to `test_known_rebased_classes`
- `tests/integration/marcus/test_production_runner_error_pause_recover.py` — extend with a builder-node error-pause pin (already TW-7c-4-allowlisted)

## Tasks & Acceptance

**Execution:**
- [x] `app/marcus/orchestrator/package_builders.py` — re-base `BuilderInputError(SpecialistDispatchError)`; redundant `__init__` dropped; base imported — crash class joined the recoverable family
- [x] `app/marcus/orchestrator/production_runner.py` (start-walker) — wrapped `run_builder_node` in `try/except SpecialistDispatchError → return _pause_at_error(specialist_id=package_builders.BUILDER_SPECIALIST_ID, ...)` (trial_id=effective_trial_id)
- [x] `app/marcus/orchestrator/production_runner.py` (recover-walker) — same wrap, mirrored (trial_id=trial_id)
- [x] `tests/contracts/test_specialist_error_taxonomy.py` — deleted the `BuilderInputError` EXCLUSIONS row (reverse-existence red observed first); added `BuilderInputError` to `test_known_rebased_classes` (inherited-ctor semantics pinned) — EXCLUSIONS 13→12
- [x] `tests/integration/marcus/test_production_runner_gate_pause_resume.py` — rewrote BOTH ratified pins (renamed) crash→error-pause; anti-theater assertions preserved verbatim + recover-determinism + status-not-paused-at-gate
- [x] `tests/integration/marcus/test_production_runner_error_pause_recover.py` — NEW structural both-walker pin (`test_builder_node_error_pause_wraps_both_walkers`): both call sites wrapped under the `package_builder` identity
- [x] `_bmad-output/planning-artifacts/deferred-inventory.md` — annotated tranche-2 execution + filed `tagged-error-taxonomy-tranche-3-offpath-sweep` (the 12 by name) per John A7
- [x] (party-decided) the 12 off-path classes → DEFERRED to tranche 3 (unanimous live-path-only)

**Acceptance Criteria:**
- Given `BuilderInputError`, then `issubclass(cls, SpecialistDispatchError)` AND `issubclass(cls, RuntimeError)` both hold; `cls("m", tag="t").tag == "t"` and `str() == "m"`
- Given a node-06 builder raise on the start-walker, then the runner returns a `paused-at-error` envelope with `paused_error_tag` set and `error-pause.json` written — NOT an unhandled exception
- Given a node-06 builder raise on the recover-walker, then the same error-pause behavior holds
- Given the success path (grounded upstream), then the §06 contribution is added and the walk continues — byte-identical to pre-change
- Given the EXCLUSIONS list, then it no longer names `BuilderInputError` and `test_exclusions_rows_still_name_live_bare_classes` passes
- Given the full battery (contracts + audit + marcus integration + lockstep + lint-imports + ruff), then green with no new failures vs the ambient roster

## Spec Change Log

**2026-06-17 — conflict adjudication (party-ratified).** Amelia's mandatory catch-site grep surfaced two party-ratified pins (`test_starved_resume_fails_loud_at_06_builder` / Finding-#8 MUST-FIX; `test_broken_brief_fails_the_gate_not_quality_theater` / S5-crit-5) that pinned §06 `BuilderInputError` to PROPAGATE (fail-loud-as-crash) — on its face contradicting the wrap. Re-convened Winston + the pin co-authors (Murat, John). Unanimous ruling **COMPATIBLE**: the pins ratified *invariants* (non-silent, no-theater-gate, no-publish), not the crash *mechanism*; `_pause_at_error` (no DecisionCard, halts BEFORE G2C, tagged error-pause.json, recover re-enters) honors all three invariants and is strictly more recoverable than a crash. Murat (co-author) on record: *"I meant fail-loud-AS-NOT-SILENT-AND-NO-THEATER, not fail-loud-AS-CRASH."* John (co-ratifier): the raise was the *delivery* of the guarantee, not the guarantee. **Binding amendments executed:** both pins renamed + rewritten to assert paused-at-error + specific tag + `specialist_id == "package_builder"` + **no G2C card / no storyboard publish (preserved VERBATIM)** + status-not-paused-at-gate + recover-determinism (re-pause same tag, no card, no publish) [Murat MUST-FIX]; per-condition tag granularity preserved into error-pause.json [Amelia]; both call sites wrapped + structural both-walker pin [Amelia/Murat]; reverse-existence EXCLUSIONS red observed before row deletion [Murat]; kill-the-mutant verified (behavioral pins go red when the wrap's catch type is broken). The 12 off-path classes filed as tranche-3 inventory entry `tagged-error-taxonomy-tranche-3-offpath-sweep` [John A7]. §06 recorded as the edge-proven last live-walk dispatch leg [Winston A8].

## Review Findings

bmad-code-review 2026-06-17 (3-lane: Blind Hunter / Edge Case Hunter / Acceptance Auditor). Acceptance Auditor verdict: **PASS** — every AC + binding amendment confirmed against working-tree source. Triage: 2 patch, 1 defer, 6 dismissed.

- [x] [Review][Patch] Honest tag-taxonomy note for defensive programmer-error tags — `package_builders.py` BuilderInputError docstring — Edge Case Hunter SHOULD-FIX: `unknown-node` + `contract-violation` are programmer-errors funneled into a recoverable pause. Party already ruled don't-split (Amelia Trap 1); fix is honesty-only, distinguishing transient vs defensive tag classes. Applied.
- [x] [Review][Patch] Broken-brief recover block omits `paused_gate is None` re-assertion — `test_production_runner_gate_pause_resume.py` — Acceptance Auditor advisory: symmetry with the resume block + starved-resume test; tightens the "recover is not an escape hatch into the gate" guarantee. Applied.
- [x] [Review][Defer] error-pause evidence flag uses per-segment `specialist_calls` vs gate-pause's `len(contributions)` [production_runner.py:1148/_pause_at_error] — deferred, pre-existing shared-helper convention; changing it affects ALL error-pause callers on a frozen engine, out of tranche-2 scope. Filed to deferred-work.md.

Dismissed (6): Blind Hunter base-ctor MUST-FIX (false positive — verified `SpecialistDispatchError(RuntimeError)` ctor + green ctor-semantics pin; documented blind-hunter-lacks-context pattern); pre-call envelope (Edge confirmed pure-until-success); trial_id vars (correct by design); offline false-pass (disproven by green run + kill-mutant); textual count test (matches the file's `test_single_shared_dispatch_call_site == N` idiom; real property carried by kill-mutant-verified behavioral pins); last-write-wins error-pause.json (pre-existing, self-consistent). Acceptance Auditor node_index advisory dismissed: behavioral re-pause-same-tag proves §06 re-entry more strongly than an int-check.

## Verification

**Commands:**
- `.\.venv\Scripts\python.exe -m pytest tests/audit/ tests/contracts/test_specialist_error_taxonomy.py tests/integration/marcus/ -q` — expected: green (ambient roster aside)
- `.\.venv\Scripts\python.exe scripts/utilities/check_pipeline_manifest_lockstep.py` — expected: exit 0
- `.\.venv\Scripts\lint-imports.exe` — expected: 13 kept, 0 broken
- `.\.venv\Scripts\ruff.exe check <touched files>` — expected: clean

## Suggested Review Order

**The re-base (crash → catchable)**
- `BuilderInputError` joins the family; redundant ctor deleted (base is identical)
  [`package_builders.py:44`](../../app/marcus/orchestrator/package_builders.py#L44)

**The wrap (catchable → actually caught — the real fix)**
- Start-walker §06 builder now error-pauses (mirror of the specialist/storyboard branches)
  [`production_runner.py:1332`](../../app/marcus/orchestrator/production_runner.py#L1332)
- Recover-walker §06 builder, same mirror
  [`production_runner.py:1771`](../../app/marcus/orchestrator/production_runner.py#L1771)
- The helper both branches call — `node_index` unshifted = recover re-enters the failed node
  [`production_runner.py:1058`](../../app/marcus/orchestrator/production_runner.py#L1058)

**Ratchet turn**
- EXCLUSIONS row retired; membership + ctor-semantics pinned
  [`test_specialist_error_taxonomy.py:39`](../../tests/contracts/test_specialist_error_taxonomy.py#L39)

**Behavior pin**
- Builder-node error-pause + recover re-entry pinned end-to-end
  [`test_production_runner_error_pause_recover.py`](../../tests/integration/marcus/test_production_runner_error_pause_recover.py)
