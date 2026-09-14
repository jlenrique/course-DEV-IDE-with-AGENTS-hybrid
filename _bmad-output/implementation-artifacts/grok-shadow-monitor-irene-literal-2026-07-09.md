# Shadow Monitor - `irene-text-literal-supersedes-styleguide-truncation` (Grok 4.5 Cursor-led session)

Started: 2026-07-09T13:58:46-04:00
Branch: `dev/lesson-planning-2026-07-09` - baseline HEAD `c6871da0`.
Driver lane: Grok 4.5 in Cursor.

## Monitor Lane (read-only, independent)

This is an independent shadow-monitoring lane for the Grok-led dev session. Each poll reads the current repository state and appends a time-stamped report with findings (`SOP-NNN`). The monitor writes only this log. It does not modify production code, tests, runtime state, commits, branches, Grok/Cursor-owned artifacts, or BMAD-owned decision records.

The lane's job is to catch regressions, unratified drift, vacuous-green, claim-envelope overreach, and SPOC product-boundary violations before the active driver claims a gate or done-bar.

## Product Boundary (binding)

The only product goal is the Marcus-SPOC runtime orchestrator and its production Gary dispatch path. This story is valid only because Irene literal fidelity must be honored by the real SPOC Gary path. Do not design for proofing convenience, do not mutate approved styleguide registry records as a workaround, and do not claim broader `fidelity-L1-per-slide-text-mode` closure from this slice.

## Standing Watchpoints (this arc)

1. **Spec approval and party governance.** The visible goal requires operator approve/edit on the draft spec and a fully spawned BMAD party-mode round using real personas before further design/green-light concurrence. General-purpose stand-ins do not satisfy the gate.
2. **No styleguide-registry mutation workaround.** Approved guide records, including the classic condense guide and the classic-preserve sibling, must not be edited in place to make the symptom disappear.
3. **Production seam only.** The implementation must affect `build_gary_briefs` and `generate_gamma_variants`; legacy mixed-fidelity helpers are reference only.
4. **Literal cohort contract.** `literal-text` and `literal-visual` form one literal cohort for this slice: API `text_mode=preserve`, and `text_options.amount` is absent, not `null`, `0`, or an empty placeholder.
5. **Creative cohort isolation.** Creative and untagged slides must keep the selected styleguide `text_mode` and `amount`; no whole-deck preserve bleed.
6. **Cohort-scoped dispatch.** Mixed decks require separate Gamma calls with cohort-scoped `_input_text` and `num_cards=len(cohort)`, then reassembly by stable `slide_id` / original brief order, not fuzzy title matching across cohorts.
7. **Fail-loud honor failure.** If a literal-tagged slide cannot be dispatched with preserve, including the in-scope studio+literal case, the path must raise before sending a condense fallback.
8. **RED-first tests are load-bearing.** T1-T8 should fail for the intended pre-fix reasons before production edits, then pass against next-layer observable behavior such as carried slide fields and captured Gamma-client kwargs.
9. **Literal-visual scope discipline.** This slice is text-preserve only for `literal-visual`; image URL injection and broader literal-visual payload policy remain out of scope.
10. **Claim envelope.** Closeout may mark `irene-text-literal-supersedes-styleguide-truncation` met only if the focused behavior is proven. It must leave `fidelity-L1-per-slide-text-mode` open/yellow with residual scope explicit.
11. **Live/seam validation.** Focused pytest/ruff is necessary but not sufficient if the active story claims live seam exercise; the evidence must show each authored seam was exercised honestly.
12. **Stray hygiene.** Existing untracked goal/spec/session artifacts must be deliberately banked or explicitly left local; do not sweep unrelated runtime/evidence strays into this story.

## Poll Log

### SOP-000 - baseline / first shadow report - 2026-07-09T13:58:46-04:00

**Scope reviewed:** `git status --short --branch`, recent git log, canonical shadow-monitor examples in `_bmad-output/implementation-artifacts/`, `goal-irene-literal-preserve-2026-07-09.txt`, draft spec `_bmad-output/implementation-artifacts/spec-irene-literal-supersedes-styleguide-truncation.md`, and repo references to `irene-text-literal-supersedes-styleguide-truncation` / `fidelity-L1-per-slide-text-mode`. No tests were run. No production/test/runtime files were edited by this monitor; this ledger entry is the only write.

**Current repo state:** branch `dev/lesson-planning-2026-07-09` is at `c6871da0` (`Merge branch 'dev/workbook-2026-07-06'`) and tracks `origin/dev/lesson-planning-2026-07-09`. The only visible untracked session files before this ledger were:

- `_bmad-output/implementation-artifacts/spec-irene-literal-supersedes-styleguide-truncation.md`
- `goal-irene-literal-preserve-2026-07-09.txt`

No tracked production-code or test diff is visible yet (`git diff --stat` empty at this poll).

**Positive baseline signal:** the draft spec is already strong and aligned with the S8 close envelope: binary creative/literal cohorting, preserve + amount-absent for literal slides, cohort-scoped input, stable `slide_id` reassembly, studio+literal fail-loud, no approved styleguide registry mutation, and no claim that `fidelity-L1-per-slide-text-mode` is fully closed. The goal file also correctly requires BMAD workflows, fully spawned party gates, live/seam validation, shadow-monitor consultation, and final party concurrence.

**Main risk at baseline:** the repo has a spec-shaped and goal-shaped start, not an implementation. There is no evidence yet of operator approve/edit, no new party record beyond the spec's embedded comment, no RED-first test output, no production seam edit, no focused green output, no ruff output, and no closeout/inventory disposition. This is expected for a first poll, but it means no implementation claim is currently scoreable.

**F-0001 [P1] Governance evidence is ambiguous until the operator approval and real-party record are externally visible.** The spec contains an HTML comment saying a 4-seat party green-light happened and that a prior generalPurpose-only round was voided, while the goal says the immediate next task is still operator approve/edit and a fully spawned BMAD party before further green-light/design concurrence. That may be a harmless sequencing artifact, but the active driver should make the gate state explicit before dev dispatch: either mark the spec operator-approved and cite the fully spawned party record, or keep it in draft and stop before implementation.

**F-0002 [P2] The S7 Phase-2 monitor ledger referenced in `SESSION-HANDOFF.md` is not present in this checkout.** The handoff names `_bmad-output/implementation-artifacts/claude-shadow-monitor-s7-phase2-2026-07-08.md` as active/untracked, but this file is absent locally. This does not block the Irene literal story, but any closeout that says all relevant shadow-monitor notes were consulted should either cite this new ledger and the canonical-arc ledger actually present, or explain that the referenced S7 Phase-2 ledger was unavailable in this checkout.

**Watchpoint verdicts at baseline:** WP2, WP3, WP4, WP5, WP6, WP7, WP8, WP9, WP10, and WP12 are not violated by current visible state. WP1 is open pending explicit approval/party evidence. WP11 is open pending seam/test/live evidence.

**Recommendation to Grok/Cursor lane:** before production edits, resolve the spec approval state and party-record ambiguity, then proceed RED-first on T1-T8. The first implementation poll should show failing tests for the intended reasons and no styleguide registry mutation. Do not claim progress beyond "spec/green-light preparation" from the current repo state.

**Verdict: MONITOR INITIALIZED / WAITING ON GATE EVIDENCE.** The story direction is product-valid and the draft spec has the right constraints, but the implementation is not yet visible or scoreable.

---

### SOP-001 - first implementation/commit poll - 2026-07-09T14:09:42-04:00

**Scope reviewed:** `git status --short --branch`, latest commit metadata/stat/name-only for `0fb2b2cf`, committed diffs for `app/marcus/orchestrator/package_builders.py`, `app/specialists/gary/_act.py`, `tests/integration/marcus/test_package_builders.py`, `tests/specialists/gary/test_gary_gamma_dispatch.py`, the updated spec, deferred inventory, and deferred-work entry. No tests were run by this monitor poll. No production/test/runtime files were edited by this monitor; this ledger entry is the only write after the Grok/Cursor commit.

**State note:** the repo changed while this poll was reading it. Initial status showed the implementation dirty in six tracked files plus the untracked spec/goal/monitor ledger. By the final status check, those changes had been committed as `0fb2b2cf` (`fix(gary): Irene literal fidelity supersedes styleguide condense`). Branch `dev/lesson-planning-2026-07-09` is now **ahead of origin by 1**; working tree was otherwise clean before this SOP entry.

**Committed surface:** the commit includes the intended production seams (`package_builders.py`, `gary/_act.py`), T1-T8 tests, the spec, goal file, deferred inventory, deferred-work notes, and this monitor ledger. No `state/config/gamma-style-guides.yaml` or other styleguide registry file is in the commit, so WP2 is satisfied at the file-surface level.

**Positive implementation-shape verification:**

- `build_gary_briefs` now carries only recognized `fidelity` values (`creative`, `literal-text`, `literal-visual`) onto Gary slide rows; missing/unknown values are omitted, matching the spec's creative-default behavior.
- `generate_gamma_variants` now partitions binary cohorts once per payload: creative vs literal (`literal-text` and `literal-visual` together).
- Classic literal cohorts force `text_mode="preserve"` and remove only `text_options.amount`; non-amount text options are preserved if present.
- Mixed decks issue separate cohort-scoped `generate_deck` calls with `num_cards=len(cohort)` and reassemble rows in original brief order by `slide_id`.
- Studio+literal raises `GaryActError(tag="gamma.fidelity.literal-honor-failure")` before any Studio template call, matching the fail-loud honor-failure requirement.
- T1-T8 tests exist and assert the main watchpoints: carry-through, unknown omission, creative no-bleed, literal preserve/amount-absent, mixed split/rejoin, island isolation, A/B x cohorts call count, and Studio+literal no-spend failure.
- Deferred inventory language marks only `irene-text-literal-supersedes-styleguide-truncation` MET and explicitly leaves `fidelity-L1-per-slide-text-mode` yellow/open with residual scope.

**F-0001 status:** partially resolved. The commit/spec now claim operator approval and a 4/4 skill-activated BMAD green-light, and the commit message says F-0001 was resolved. However, the only visible evidence in this commit is the spec's embedded HTML comment; no standalone party record or close/done-bar party concurrence is visible. Because the goal's definition of done requires a fully spawned BMAD party-mode team to concur at close, this monitor cannot externally corroborate final done-bar governance yet.

**F-0003 [P1] Done claim is ahead of visible close-party and verification evidence.** The spec is now `status: 'done'`, all task checkboxes are marked `[x]`, and deferred inventory marks the item MET, but this commit does not include visible focused pytest output, ruff output, RED-first transcript/evidence, or final close-party concurrence. The implementation shape is strong, but the active goal's process bar is stricter than "code committed." **Required before deleting this monitor or treating the story externally closed:** publish/cite the focused pytest + ruff results and the final fully spawned BMAD close-party concurrence, or revise the status to "implemented/pending close evidence."

**F-0004 [P2] Branch is committed but not remote-banked.** `HEAD` is `0fb2b2cf`, while `origin/dev/lesson-planning-2026-07-09` remains `c6871da0`. If this story is being handed across tools, push the branch or explicitly record that the commit is local-only.

**F-0005 [P3] Mixed-cohort fallback IDs remain a known edge, filed but not fixed.** `deferred-work.md` notes that mixed-cohort slides lacking `slide_id` can synthesize colliding `slide-01` ids across cohorts. This is acceptable if the production contract guarantees Gary brief slides always carry unique `slide_id`, and the main builder does emit them. It should not be allowed to become a broad "arbitrary payload" claim.

**Test/evidence visibility:** no terminal output or evidence artifact for the stated pytest/ruff commands is visible in the committed files. The tests themselves are present; their execution is asserted by checkboxes/commit prose, not externally witnessed by this poll.

**Watchpoint verdicts:** WP2-WP10 pass by committed shape. WP1 remains open for final close-party evidence, though green-light evidence is now claimed. WP11 remains open until test/ruff/live-seam evidence is externally visible. WP12 is mostly clean; remaining issue is local-only commit banking.

**Verdict: IMPLEMENTED IN SHAPE / NOT EXTERNALLY CLOSE-CORROBORATED.** The code diff appears aligned with the product requirement and avoids the styleguide-registry workaround, but final done should wait for visible test/ruff output, close-party concurrence, and push/banking of `0fb2b2cf`.

---

### SOP-002 - pushed branch + CI-muting follow-up poll - 2026-07-09T14:19:37-04:00

**Scope reviewed:** `git status --short --branch`, latest git log, commit metadata/stat/diffs for `1be59406`, workflow-trigger diffs, always-on instruction diffs, grep for verification/party/test evidence, and the current monitor ledger tail. No tests were run by this monitor poll. No production/test/runtime files were edited by this monitor; this ledger entry is the only write.

**Current repo state:** branch `dev/lesson-planning-2026-07-09` is clean and synced with `origin/dev/lesson-planning-2026-07-09` at `1be59406` (`chore(ci): mute auto GitHub Actions for solo no-PR workflow`). The prior Irene implementation commit `0fb2b2cf` is now remote-banked under that pushed branch.

**What changed since SOP-001:** a second commit landed and pushed. It documents solo-operator/no-formal-PR delivery in `AGENTS.md`, `CLAUDE.md`, and `.github/copilot-instructions.md`, converts the listed GitHub Actions workflows to manual `workflow_dispatch` only, removes the scheduled `trial-replay`, and banks the SOP-001 monitor entry.

**F-0004 closed.** The Irene implementation commit is no longer local-only: `HEAD` and `origin/dev/lesson-planning-2026-07-09` now resolve to the same pushed commit chain (`1be59406` includes `0fb2b2cf`). No untracked/dirty file residue is visible at this poll.

**F-0003 remains open.** I still see no externally visible focused pytest output, ruff output, RED-first transcript/evidence, or final fully spawned BMAD close-party concurrence. The spec remains `status: 'done'`, but this monitor still cannot corroborate the active goal's process DoD. Because the new CI commit mutes automatic GitHub Actions, local verification evidence becomes more important, not less.

**F-0006 [P2] Broad CI/governance change is outside the Irene-literal product slice.** The workflow muting may match operator preference and is now documented in always-on instructions, but it is a repo-governance change unrelated to `build_gary_briefs` / `generate_gamma_variants`. It should be reviewed/accepted on its own merits and not treated as evidence for the Irene literal story. It also means future "pushed branch" does not imply automatic CI coverage.

**F-0007 [P3] Manual substrate workflow may skip its core check under `workflow_dispatch`.** `substrate-frozen-paths-check.yml` now has only `workflow_dispatch`, but its base/head selection still relies on `github.event.before` in the non-PR path and then skips if base/head is empty. On a manual run, that can produce a no-op instead of a useful frozen-path check. This is not an Irene-literal blocker, but it is a follow-on if the manual workflow is expected to remain a usable tool.

**Irene implementation scoreability:** code shape remains scoreable as "implemented in shape" from SOP-001, with no new Irene-code changes in this poll. External close is still not scoreable because WP1 final close-party evidence and WP11 test/ruff/live-seam evidence remain absent from the visible repo state.

**Verdict: PUSH/BANKING RESOLVED; CLOSE EVIDENCE STILL MISSING.** Keep the monitor active. Next useful signal should be local pytest + ruff output and final fully spawned BMAD close-party concurrence, or an explicit status downgrade from `done` to pending-close-evidence.

---

### SOP-003 - master merge poll with close evidence still absent - 2026-07-09T14:29:07-04:00

**Scope reviewed:** `git status --short --branch`, latest git log, merge commit metadata/stat for `f30c88c9`, SOP-002 bank commit `4ed2b917`, grep for pytest/ruff/close-party evidence in the monitor/spec/goal/handoff/project-context surfaces, and current working diff. No tests were run by this monitor poll. No production/test/runtime files were edited by this monitor; this ledger entry is the only write.

**Current repo state:** branch `dev/lesson-planning-2026-07-09` is clean and synced with `origin/dev/lesson-planning-2026-07-09` at `f30c88c9`. `origin/master`, `origin/HEAD`, local `master`, and the current branch also point at `f30c88c9`. The dev branch has been merged to master.

**What changed since SOP-002:** `4ed2b917` banked SOP-002 into the monitor ledger, then `f30c88c9` merged `dev/lesson-planning-2026-07-09` into master with message "Land Irene literal->Gary preserve override and solo-operator CI mute". The merge carries the Irene implementation, the CI-muting governance change, the spec/goal files, and the monitor ledger through SOP-002.

**Positive state:** F-0004 remains closed. The work is remote-banked and now consolidated to master. No untracked or dirty residue was visible before this SOP entry.

**F-0003 remains open and now matters more.** The merge to master did not add the missing focused pytest output, ruff output, RED-first transcript/evidence, or final fully spawned BMAD close-party concurrence. The grep surface still only shows expected command text and checkbox/prose assertions, not actual results or a close-party record. The implementation remains code-shape-scoreable, but the story's own process DoD remains externally uncorroborated.

**F-0008 [P1] Master now carries a `done` story without visible close corroboration.** Because the implementation/spec/inventory have been merged to master while `F-0003` is still open, downstream readers will see `irene-text-literal-supersedes-styleguide-truncation` as MET/done even though the monitor cannot verify the final close bar. **Required remediation:** either append/bank the missing local verification + close-party evidence promptly, or add a corrective record explaining that the master merge is code-landed but governance-close evidence is still pending. Do not delete this monitor while this mismatch remains.

**F-0006 remains open as separate-governance review.** The CI-muting change is now also on master. This monitor still treats it as outside the Irene-literal product slice; it may be operator-intended, but it should not count as Irene validation.

**F-0007 remains open as non-blocking workflow usability follow-on.** The manual substrate workflow still appears likely to skip its core check under `workflow_dispatch` because it derives base/head from `github.event.before` in the non-PR path.

**Irene implementation scoreability:** no new Irene code changes since SOP-001. Code shape remains aligned and registry-safe, but external close remains not scoreable. Master merge does not substitute for test/ruff and BMAD done-bar evidence, especially with automatic CI muted.

**Verdict: MASTER MERGED / CLOSE-CORROBORATION GAP ESCALATED.** Keep the monitor active. The next poll should look specifically for banked pytest+ruff output and a final fully spawned close-party concurrence, or for a corrective "code-landed, close-evidence pending" record.

---

### SOP-004 - liveproof witness started / not yet scoreable - 2026-07-09T14:39:27-04:00

**Scope reviewed:** `git status --short --branch`, latest git log, current monitor diff, new evidence directory `_bmad-output/implementation-artifacts/evidence/irene-literal-liveproof-20260709T143510/`, its driver/log files, active Python processes, newest `state/config/runs/*` directory, and current walk log tail. No tests were run by this monitor poll. No production/test/runtime files were edited by this monitor; this ledger entry is the only write.

**Current repo state:** `HEAD` remains `f30c88c9`, synced with `origin/dev/lesson-planning-2026-07-09` and `origin/master`. Working tree has this monitor ledger dirty from SOP-003 and a new untracked liveproof evidence directory. No new commit has landed since the master merge.

**New signal:** a real liveproof attempt has started under `_bmad-output/implementation-artifacts/evidence/irene-literal-liveproof-20260709T143510/`. Files currently visible:

- `irene_literal_liveproof_driver.py` (26,860 bytes)
- `driver-log.txt` (379 bytes)
- `walk-log.txt` (currently logging OpenAI chat completions)
- `hil-transcript.txt` (0 bytes at this poll)

The driver explicitly targets an AFK HIL production walk on `tejal-c1m1-p4-assessments-bridge` using `hil-2026-apc-crossroads-classic` (classic condense, not preserve sibling), with a scripted/operator pinch-hit that stamps mixed `fidelity: literal-text` into Irene output because live Irene does not yet emit the field. That is an honest and important claim-boundary detail: it can prove the Marcus-SPOC Gary seam after a HIL edit, but not that Irene independently emits the fidelity field.

**Execution state:** Python processes from 14:36 are active, and `walk-log.txt` shows live OpenAI calls at 14:38 and 14:39. The newest run directory `state/config/runs/e9ab808e-9157-4085-b14c-dbc0669721e7/` currently contains only `model_resolution_trail.json`; no `run.json` was present when polled. No facts JSON, proof JSON, cost report, Gary proof, workbook, or terminal status artifact exists yet in the evidence directory.

**Positive movement:** F-0008 is being addressed in the right direction: the team is gathering real live/seam evidence rather than relying only on checked boxes. The guide choice is correctly the classic condense guide, which directly targets the failure mode this story is meant to fix.

**F-0003 remains open.** The liveproof is in progress and not scoreable yet. Focused pytest/ruff output is still not visible, and the final fully spawned close-party concurrence is still absent. A running liveproof cannot close the previous done/MET mismatch until it produces terminal facts and those facts are banked/cited.

**F-0009 [P2] Liveproof claim envelope must stay precise about the operator fidelity stamp.** Because the driver states Irene Pass-1 does not yet emit `fidelity` and the AFK stand-in will stamp it into the persisted Irene contribution, close language must not imply "Irene independently emits literal fidelity in production." The valid claim is narrower: when the Marcus-SPOC runtime receives literal fidelity on Gary-bound plan units/slides, Gary honors it under classic-condense by splitting/preserving the literal cohort.

**F-0010 [P2] Evidence directory is untracked while the story is already merged to master.** This is normal for an in-progress witness, but if the liveproof succeeds, terminal artifacts and the monitor ledger need a deliberate bank/push or explicit convention-based exclusion. Do not let the live witness remain only local if it is used to justify the done/MET state already on master.

**Verdict: LIVEPROOF IN PROGRESS / DO NOT SCORE YET.** Keep monitoring. Next poll should look for terminal facts/proof artifacts, focused pytest+ruff output, and final close-party concurrence; until then, F-0003/F-0008 remain open.

---

### SOP-005 - liveproof progressed to G0R / still pre-Gary - 2026-07-09T14:49:07-04:00

**Scope reviewed:** `git status --short --branch`, latest git log, liveproof evidence directory file list, `driver-log.txt`, `walk-log.txt`, `hil-transcript.txt`, active Python processes, run registry files under `state/config/runs/e9ab808e-9157-4085-b14c-dbc0669721e7/`, `run.json` status, and the `state/config/gamma-styleguide-picks.jsonl` diff. No tests were run by this monitor poll. No production/test/runtime files were edited by this monitor; this ledger entry is the only write.

**Current repo state:** `HEAD` remains `f30c88c9`, synced with origin/master and origin/dev. Working tree has the monitor ledger dirty, a modified `state/config/gamma-styleguide-picks.jsonl`, and the untracked liveproof evidence directory.

**Liveproof state:** the liveproof is running and has progressed from start-up into the gate loop. `driver-log.txt` records:

- `start_trial` returned after 636.9s with trial `e9ab808e-9157-4085-b14c-dbc0669721e7`;
- G0 directive review used the scripted edit-then-confirm path;
- loop 0 approved `G0E`;
- run then paused at `G0R`;
- loop 1 started `resume approve G0R`.

The run registry now contains `run.json`, `checkpoint.json`, `decision-card-G0E.json`, `decision-card-G0R.json`, `g0-enrichment.json`, `irene-refinement.json`, `ratified-los.json`, `cost-report.*`, and related start/resume artifacts. At poll time, `run.json` still reported `status=paused-at-gate`, `paused_gate=G0R`, and no error tag. The active Python process is still running, so this may be a moment-in-time read during the next resume.

**Evidence state:** the evidence directory still has no facts/proof JSON and no Gary proof artifact. It now has non-empty HIL transcript content and longer driver/walk logs, but the witness has not reached the Gary/package-builder seam that this story needs to prove.

**Positive signal:** the styleguide pick is correctly recorded as `hil-2026-apc-crossroads-classic`, and the transcript shows the generated directive carrying that classic guide with `styleguide_picker_provenance`. The liveproof is still targeting the correct condense failure mode.

**F-0011 [P2] Runtime styleguide pick ledger is dirty.** The liveproof appended a real pick row for trial `e9ab808e...` to `state/config/gamma-styleguide-picks.jsonl`. This is expected runtime residue for a picker/liveproof run, but it is a tracked file. It needs explicit disposition before any later bank: include it deliberately if the run record is part of the proof, or leave/revert it by established runtime-ledger convention if not. Do not let it be swept into an unrelated monitor/evidence commit accidentally.

**F-0003 / F-0008 remain open.** No focused pytest output, ruff output, terminal liveproof facts, Gary proof, or final close-party concurrence is visible yet. The implementation is still only scoreable in code shape, not externally closed.

**F-0009 remains open.** The operator-pinch-hit claim boundary still needs to be preserved in any close language. This poll has not yet seen the actual G1 fidelity-stamp moment or downstream Gary result.

**Verdict: LIVEPROOF PROGRESSING / STILL PRE-GARY AND NOT SCOREABLE.** Keep monitoring. Next useful signal is progression past G1 into package-builder/Gary, with facts proving literal fidelity reached Gary and caused mixed-cohort preserve behavior under classic condense.

---

### SOP-006 - liveproof stalled; Pass-1 emit recovery story opened - 2026-07-09T14:59:07-04:00

**Scope reviewed:** `git status --short --branch`, latest git log, liveproof evidence directory file list, `driver-log.txt`, `walk-log.txt`, run registry state for trial `e9ab808e-9157-4085-b14c-dbc0669721e7`, active Python processes, dirty diffs for `deferred-work.md`, `deferred-inventory.md`, `state/config/gamma-styleguide-picks.jsonl`, and new spec `_bmad-output/implementation-artifacts/spec-irene-pass1-fidelity-emit-recovery.md`. No tests were run by this monitor poll. No production/test/runtime files were edited by this monitor; this ledger entry is the only write.

**Current repo state:** `HEAD` remains `f30c88c9`, synced with origin/master and origin/dev. Working tree now has dirty monitor ledger, dirty `deferred-work.md`, dirty `deferred-inventory.md`, dirty `state/config/gamma-styleguide-picks.jsonl`, untracked liveproof evidence, and untracked Pass-1 recovery spec.

**Liveproof state:** the liveproof has not advanced since SOP-005. Evidence file timestamps are still around 14:48; `driver-log.txt` still ends immediately after `resume approve G0R (cap=40)`. `walk-log.txt` has no new OpenAI/Gamma activity after the G0R resume. The liveproof-specific Python processes that were present earlier are no longer visible. The persisted `run.json` still reports `status=paused-at-gate`, `paused_gate=G0R`, and no error tag. No terminal facts/proof/Gary artifact exists.

**Interpretation:** treat the liveproof as stalled or aborted at G0R until the driver records otherwise. It did not reach G1, did not stamp fidelity, did not reach package-builder/Gary, and did not prove the Irene-literal seam.

**New story signal:** `_bmad-output/implementation-artifacts/spec-irene-pass1-fidelity-emit-recovery.md` has appeared with `status: 'in-progress'`. It correctly identifies the deeper defect surfaced by the liveproof attempt: live Irene Pass-1 does not emit `plan_units[].fidelity`, so the already-landed Gary preserve path has no organic production input. The new spec says operator rejected G1 stamp workarounds and scopes a real recovery: restore Irene Pass-1 emission/normalization of `fidelity` on dict-shaped plan units, with literal-text prioritized and literal-visual production streamlining deferred.

**Positive direction:** this is the right product correction. It moves away from proving the Gary seam with an AFK fidelity stamp and toward making the real Marcus-SPOC runtime produce the field Gary now honors. The new deferred `literal-visual-production-streamline` entry also keeps classification separate from image-production claims.

**F-0003 remains open.** Still no focused pytest/ruff output, no final close-party concurrence, and no terminal liveproof proof. The original `irene-text-literal-supersedes-styleguide-truncation` story remains marked done/MET on master, but now the live witness has exposed that the organic end-to-end runtime path still lacks Irene fidelity emission.

**F-0008 escalated / reframed.** Master carries the Gary-side done/MET story, but the liveproof attempt has produced a follow-on recovery spec showing the product path is not end-to-end complete without Irene Pass-1 emit. The prior story may remain valid as the Gary consumption seam, but close language must not imply organic Irene→Gary literal preservation is complete until the Pass-1 emit recovery lands and is proven without a stamp.

**F-0009 partially resolved by new scope, not by proof.** The new spec explicitly forbids G1/AFK fidelity stamps for proof and requires a no-stamp liveproof after implementation. This is the correct disposition, but no implementation or proof exists yet.

**F-0011 remains open.** `state/config/gamma-styleguide-picks.jsonl` still carries the liveproof runtime pick row. Its disposition remains required.

**F-0012 [P1] Do not close the monitor on the Gary-side story alone.** Because the active session has opened Pass-1 fidelity emit recovery as the product path needed to make the Gary seam fire organically, this monitor should continue across that recovery story unless the operator explicitly narrows the monitor to "Gary seam only." The next scoreable event is RED-first Irene Pass-1 tests/code, not the stalled G0R liveproof.

**Verdict: LIVEPROOF STALLED / PRODUCT GAP REFRAMED UPSTREAM.** The monitor should stay active. Next poll should look for Pass-1 emit implementation/tests and a restarted no-stamp liveproof; the current liveproof does not support close.

---

### SOP-007 - Pass-1 emit implementation commit poll - 2026-07-09T15:09:08-04:00

**Scope reviewed:** `git status --short --branch`, latest git log, commit metadata/stat/name-only for `6783b54b`, committed diffs for `app/specialists/irene_pass1/_act.py` and `tests/specialists/irene_pass1/test_irene_pass1_fidelity_emission.py`, updated Pass-1 recovery spec, instruction/governance text changes in `AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md`, liveproof evidence directory, and trial `e9ab808e-9157-4085-b14c-dbc0669721e7` run status. No tests were run by this monitor poll. No production/test/runtime files were edited by this monitor; this ledger entry is the only write.

**Current repo state:** `HEAD` is now `6783b54b` (`fix(irene): restore Pass-1 per-unit fidelity emission`) and is **ahead of origin by 1**. Working tree has this monitor ledger dirty, `state/config/gamma-styleguide-picks.jsonl` still dirty from the earlier liveproof pick, and the untracked stalled liveproof evidence directory. The Pass-1 recovery implementation/spec/tests/deferred entries were committed; the monitor and runtime pick were not.

**Committed surface:** `6783b54b` adds the Pass-1 recovery spec, new tests, and Irene Pass-1 code changes. It also changes always-on governance text to codify "party consensus = approval" for solo workflow. The commit does not include the liveproof evidence directory or styleguide-pick runtime residue.

**Positive implementation-shape verification:**

- `assemble_pass1_prompt` now injects a dedicated per-unit fidelity classification instruction block between cluster and collateral instructions.
- The instruction block explicitly requests `fidelity` on every plan unit, with the three recognized modes: `creative`, `literal-text`, and `literal-visual`.
- `normalize_fidelity` soft-canonicalizes recognized values and aliases (`literal_text`, `literal-image`, etc.) while omitting missing/unknown/empty values rather than inventing tags.
- `parse_pass1_response` applies `normalize_fidelity` after collateral normalization.
- `write_lesson_plan` normalizes before writing and surfaces `- Fidelity: ...` lines only for recognized values.
- The new test file covers prompt contract, guidance visibility, recognized values, omitted/unknown values, alias coercion, parse preservation vs prose theater, and artifact lines.
- The spec/deferred entries keep literal-visual production streamlining separate from classification emit and explicitly avoid claiming L1-per-slide or literal-image production closure.

**F-0012 direction is being addressed.** The right upstream code surface is now changed: Irene Pass-1 can request and preserve `fidelity`, which gives the Gary seam an organic input path. This is a materially better product shape than the stalled G1/AFK stamp liveproof.

**F-0013 [P1] Pass-1 emit story is marked done without visible verification or close-party evidence.** The recovery spec is now `status: 'done'` and all task checkboxes are marked `[x]`, but I still see no focused pytest output, ruff output, RED-first transcript/evidence, bmad-code-review record, or final done-bar party concurrence in the visible repo. This repeats the earlier close-corroboration pattern. **Required before treating the recovery story as externally closed:** bank or cite the verification commands' actual output and the review/close-party decision, or downgrade the spec to pending verification.

**F-0014 [P2] Pass-1 recovery commit is local-only.** `6783b54b` is ahead of `origin/dev/lesson-planning-2026-07-09` / `origin/master`. Push/bank it before using it as durable evidence or handoff state.

**F-0015 [P2] No no-stamp liveproof yet.** The earlier `irene-literal-liveproof-20260709T143510` remains stalled at G0R and was stamp-oriented. After this Pass-1 recovery, the valid liveproof is the one named in the new spec: authentic Tejal P4 classic-condense with **no** G1/AFK fidelity stamp, proving real Pass-1 artifacts carry structured `fidelity` and Gary consumes it. That proof is not visible yet.

**F-0016 [P2] Governance change is broader than this story.** The commit also codifies "BMAD party consensus = operator approval" in always-on instructions. That may reflect operator intent, but it is a repo-governance rule change broader than Pass-1 fidelity emit. It should be accepted/reviewed as governance, not treated as validation of the product code.

**Open carried findings:** F-0003/F-0008 remain open until the original Gary-side done/MET claim is reconciled with upstream emit recovery and no-stamp proof. F-0011 remains open for the dirty `gamma-styleguide-picks.jsonl` row. F-0010 remains open for liveproof evidence disposition.

**Verdict: PASS-1 EMIT IMPLEMENTED IN SHAPE / NOT EXTERNALLY CLOSE-CORROBORATED.** The code shape looks aligned with the upstream product fix, but the story is not externally close-scoreable until test/ruff/review/party evidence is visible, the commit is pushed, and a no-stamp liveproof proves the organic Irene->Gary path.

---

### SOP-008 - pushed Pass-1 recovery + authentic no-stamp liveproof started - 2026-07-09T15:19:08-04:00

**Scope reviewed:** `git status --short --branch`, latest git log, current evidence directories, authentic liveproof `driver-log.txt`, `walk-log.txt`, `hil-transcript.txt`, active Python processes, run registry for trial `235f2b82-5989-4a6f-9e6b-22e9697f58d2`, and the `state/config/gamma-styleguide-picks.jsonl` diff. No tests were run by this monitor poll. No production/test/runtime files were edited by this monitor; this ledger entry is the only write.

**Current repo state:** `HEAD` is `6783b54b` (`fix(irene): restore Pass-1 per-unit fidelity emission`) and is now synced with `origin/dev/lesson-planning-2026-07-09`. `origin/master` / local `master` remain at `f30c88c9`, so master still does not include the Pass-1 recovery commit at this poll. Working tree has this monitor ledger dirty, `state/config/gamma-styleguide-picks.jsonl` dirty, and two untracked liveproof evidence directories:

- `_bmad-output/implementation-artifacts/evidence/irene-literal-liveproof-20260709T143510/`
- `_bmad-output/implementation-artifacts/evidence/irene-literal-authentic-liveproof-20260709T151200/`

**F-0014 closed.** The Pass-1 recovery commit is no longer local-only: `HEAD` and `origin/dev/lesson-planning-2026-07-09` both point at `6783b54b`. Durability on the dev branch is restored. Master banking remains a separate integration decision.

**Authentic liveproof state:** a new no-stamp liveproof is running under `_bmad-output/implementation-artifacts/evidence/irene-literal-authentic-liveproof-20260709T151200/`. The driver log explicitly records `NO fidelity stamp on this driver` and selects `hil-2026-apc-crossroads-classic` with `text_mode=condense` / `amount=minimal`. Trial `235f2b82-5989-4a6f-9e6b-22e9697f58d2` is registered in `state/config/runs/.../run.json` with `status: in-flight`, no paused gate, no paused error tag, no cost report path, and no artifact paths yet. Active Python processes from 15:12 remain visible.

**Evidence visibility:** the authentic evidence directory currently contains `irene_literal_authentic_driver.py`, `driver-log.txt`, `walk-log.txt`, and a non-empty `hil-transcript.txt`. The visible transcript reaches G0 directive review/confirm only. No terminal facts JSON, Gary proof JSON, package-builder artifact, workbook evidence, final cost report, or close record exists in the evidence directory at this poll.

**Positive signal:** this is the right proof shape for the reframed product gap. Unlike the earlier stalled liveproof, this driver is attempting to prove the organic Irene Pass-1 emit -> Gary consume path under the classic condense guide without an operator/AFK fidelity stamp.

**F-0015 remains open but is now in progress.** A no-stamp liveproof has started, but it is not scoreable until it reaches the Irene/Gary seam and produces terminal artifacts showing real Pass-1 `fidelity` values carried into Gary, with mixed-cohort literal preservation under classic condense.

**F-0013 remains open.** I still see no banked focused pytest output, ruff output, RED-first transcript/evidence, bmad-code-review record, or final done-bar party concurrence for the Pass-1 recovery story. The pushed commit improves durability, but push status is not verification evidence.

**F-0011 remains open and has expanded.** `state/config/gamma-styleguide-picks.jsonl` now has two dirty runtime pick rows for Tejal P4: the stalled `e9ab808e...` run and the active authentic `235f2b82...` run. These may be legitimate runtime evidence, but because the file is tracked they need deliberate disposition before any later bank.

**Carried findings:** F-0003/F-0008 remain open until the original Gary-side done/MET claim is reconciled with the upstream Pass-1 recovery and authenticated no-stamp proof. F-0010 remains open for liveproof evidence disposition. F-0016 remains open as broader governance-change review, not product validation.

**Verdict: RECOVERY COMMIT PUSHED / AUTHENTIC PROOF IN FLIGHT / NOT SCOREABLE YET.** The repo is in a better state than SOP-007 because the recovery commit is remote-banked and the correct no-stamp proof run has started. The active implementation is still not externally scoreable until terminal liveproof artifacts, focused test/ruff output, and close-party/review evidence are visible.

---

### SOP-009 - authentic no-stamp run reached G1 with fidelity-observation mismatch - 2026-07-09T15:29:08-04:00

**Scope reviewed:** `git status --short --branch`, latest git log, authentic liveproof evidence directory, `driver-log.txt`, `walk-log.txt`, `hil-transcript.txt`, active Python processes, run registry for trial `235f2b82-5989-4a6f-9e6b-22e9697f58d2`, `rg` search for `fidelity` / `literal-text` / `literal-visual` across the run/evidence surfaces, and current verification/governance evidence visibility. No tests were run by this monitor poll. No production/test/runtime files were edited by this monitor; this ledger entry is the only write.

**Current repo state:** `HEAD` remains `6783b54b` (`fix(irene): restore Pass-1 per-unit fidelity emission`) and is synced with `origin/dev/lesson-planning-2026-07-09`. `origin/master` / local `master` remain at `f30c88c9`. Working tree has this monitor ledger dirty, `state/config/gamma-styleguide-picks.jsonl` dirty, two untracked liveproof evidence directories, and a new untracked `runs/235f2b82-5989-4a6f-9e6b-22e9697f58d2/` directory.

**Authentic liveproof state:** the no-stamp run advanced past G0E and G0R and is now paused at `G1`. `run.json` reports `status: paused-at-gate`, `paused_gate: G1`, no paused error tag, `production_clone_launch_evidence: true`, and recorded live specialist calls. Active Python processes from 15:12 remain visible, so treat the run as still in progress.

**Key G1 observation:** `driver-log.txt` records `Irene fidelity observation: null` followed by `WARNING: Irene emitted zero literal-text units — Gary honor path may not fire; continuing without stamp`. The HIL transcript's G1 edit payload records the same root detail as `{"error": "no irene_pass1 contribution"}` and explicitly says AFK HIL is observing Irene-emitted fidelity only with **no operator fidelity stamp**.

**Important ambiguity:** `runs/235f2b82-5989-4a6f-9e6b-22e9697f58d2/irene-pass1.md` exists as an untracked run artifact and visibly contains `- Fidelity: literal-text` for `u01` and `u09`, plus `- Fidelity: literal-visual` for `u05`. However, the production registry surface that the liveproof driver inspected does not expose an `irene_pass1` contribution at G1 and therefore the driver could not count those values as production-envelope proof. Until the proof driver or banked evidence explains this artifact/registry mismatch, the untracked markdown is a useful diagnostic signal but not sufficient closure evidence for the organic Irene -> Gary path.

**F-0017 [P1] Authentic proof currently contradicts the recovery close claim at the production-envelope seam.** The recovery code may be producing a markdown artifact with fidelity lines, but the liveproof's own G1 observation could not find the `irene_pass1` contribution in the production envelope and recorded zero literal-text units. **Required before scoreable close:** reconcile where the authoritative Irene Pass-1 structured output lives, make the no-stamp proof read the same surface Gary consumes, and show that literal fidelity is carried into package/Gary without a manual stamp.

**Additional runtime caveat:** `walk-log.txt` also records an Irene collateral degradation warning: a workbook exercise used `bloom_level='reflective'`, which failed `CollateralSpec` validation and caused the present/workbook block to be dropped. This is not the primary Irene-literal fidelity watchpoint, but it limits any broad claim about the run's collateral quality.

**F-0015 remains open.** The no-stamp liveproof is now materially useful because it reached G1 and surfaced the right seam, but it has not produced terminal package/Gary proof. At this poll, the proof trend is negative/ambiguous rather than closing.

**F-0013 remains open.** No banked focused pytest output, ruff output, RED-first transcript/evidence, bmad-code-review record, or final done-bar party concurrence is visible for the Pass-1 recovery story.

**F-0011 remains open.** `state/config/gamma-styleguide-picks.jsonl` still carries dirty runtime pick rows for both the stalled and active Tejal P4 runs. The new untracked `runs/235f2b82.../` directory is also runtime residue/evidence that needs explicit disposition if used for proof.

**Carried findings:** F-0003/F-0008 remain open for the original Gary-side done/MET reconciliation. F-0010 remains open for liveproof evidence banking. F-0016 remains open as broader governance-change review, not product validation.

**Verdict: AUTHENTIC PROOF IN PROGRESS / G1 EVIDENCE AMBIGUOUS-NEGATIVE / NOT SCOREABLE.** The active run is the right kind of proof, but it currently shows a production-envelope mismatch: human-readable Irene markdown has fidelity lines while the driver-observed envelope says no `irene_pass1` contribution. Do not score the implementation closed until that seam is reconciled and terminal Gary proof exists.

---

### SOP-010 - Gary reached with split-like exports but no visible preserve override - 2026-07-09T15:39:08-04:00

**Scope reviewed:** `git status --short --branch`, latest git log, authentic liveproof evidence directory, `driver-log.txt`, `walk-log.txt`, trial `235f2b82-5989-4a6f-9e6b-22e9697f58d2` run status, Gary export directory, G2B/G2C decision cards, specialist summaries, and `rg` search for `gary_proof`, `text_mode`, `preserve`, `condense`, `amount`, `literal-text`, and `literal-visual` across run/evidence surfaces. No tests were run by this monitor poll. No production/test/runtime files were edited by this monitor; this ledger entry is the only write.

**Current repo state:** `HEAD` remains `6783b54b` (`fix(irene): restore Pass-1 per-unit fidelity emission`) and is synced with `origin/dev/lesson-planning-2026-07-09`. `origin/master` / local `master` remain at `f30c88c9`. Working tree has this monitor ledger dirty, `state/config/gamma-styleguide-picks.jsonl` dirty with two runtime pick rows, two untracked liveproof evidence directories, and untracked `runs/235f2b82-5989-4a6f-9e6b-22e9697f58d2/`.

**Authentic liveproof state:** the run progressed beyond the G1 mismatch into Gary/G2. `run.json` currently reports `status: paused-at-gate`, `paused_gate: G2C`, no paused error tag, `artifact_count=10`, and `contribution_count=13`. `walk-log.txt` shows live Gamma completions for two generation IDs and downloaded Gary exports, then downstream storyboard/Kling activity after G2C approval. `driver-log.txt` has not yet recorded a terminal status after `resume approve G2C`, so treat this as still in progress.

**Positive evidence now visible:** Gary/package artifacts contain fidelity-bearing slides. `driver-log.txt` captured `package_fidelity_counts` as `{"literal-text": 2, "creative": 6, "literal-visual": 1}`. The Gary export directory contains separate-looking output groups/files: `gary_A_creative.png`, `gary_A_literal.png`, `A-creative_slide-02/03/04/06/07/08.png`, and `A-literal_slide-01/05/09.png`. This is evidence that literal-vs-creative grouping reached Gary packaging/export naming.

**Blocking evidence:** the visible Gamma settings do **not** show the required literal preserve override. `decision-card-G2B.json` lists every variant option, including `A-literal_slide-01.png`, `A-literal_slide-05.png`, and `A-literal_slide-09.png`, with `text_mode: "condense"` and `amount: "brief"`. `checkpoint.json` / `run.json` surfaces likewise show `generation_mode: "single-dispatch"` and `variant_gamma_settings` with `text_mode: "condense"` / `amount: "brief"`. I found no visible `text_mode: "preserve"` setting and no evidence that `amount` was omitted for the literal cohort.

**F-0018 [P1] Gary liveproof currently proves carry-through/grouping, not preserve-over-condense.** The active story requires Gary to force API `text_mode=preserve` and omit styleguide condensing `amount` for `literal-text` / `literal-visual` cohorts under the classic condense guide. Current live artifacts show literal slide names and two exported groups, but the recorded settings for literal outputs are still `condense` with `amount=brief`. **Required before scoreable close:** produce a terminal proof artifact that shows the actual literal cohort request used `text_mode=preserve` with no `amount`, or fix the runtime/reporting seam if the export metadata is wrong.

**F-0019 [P2] The proof harness appears at risk of over-scoring split evidence as preserve evidence.** The authentic driver states the proof target as "Gary binary-splits cohorts and forces `text_mode=preserve` (amount absent)", but its captured surfaces emphasize package fidelity counts, literal export filenames, and call count. The visible code also references `settings_still_condense`, which is not the same as proving the literal override. Close language must not treat `A-literal_*` filenames or two Gamma generations as equivalent to literal preserve settings.

**F-0017 remains open but is partially clarified.** The production envelope later contains fidelity-bearing package/Gary surfaces even though the G1 observer reported `no irene_pass1 contribution`. This reduces the concern from "fidelity absent everywhere" to "authoritative source/observation seam is inconsistent." The proof still needs to explain why the G1 observation failed and identify the exact surface Gary consumed.

**F-0015 remains open.** The no-stamp liveproof is valuable and progressed materially, but it has not produced terminal facts/claim verdicts and currently fails or contradicts the key preserve-over-condense claim.

**F-0013 remains open.** No banked focused pytest output, ruff output, RED-first transcript/evidence, bmad-code-review record, or final done-bar party concurrence is visible for the Pass-1 recovery story.

**F-0011 remains open.** Runtime residue remains dirty/untracked: the tracked styleguide pick ledger has two new rows and the active `runs/235f2b82.../` plus liveproof evidence directories remain untracked. If any of these are proof artifacts, they need deliberate banking; otherwise they need explicit runtime-residue disposition.

**Carried findings:** F-0003/F-0008 remain open for the original Gary-side done/MET reconciliation. F-0010 remains open for liveproof evidence banking. F-0016 remains open as broader governance-change review, not product validation. The collateral degradation warning from SOP-009 remains a separate caveat on broad run-quality claims.

**Verdict: LIVE GARY EVIDENCE EXISTS / PRESERVE OVERRIDE NOT PROVEN / NOT SCOREABLE.** The active proof now shows literal fidelity made it far enough to influence Gary grouping/export names, but the visible API settings still show condense+amount for literal slides. The implementation cannot be scored closed until literal preserve/no-amount is actually evidenced and the run reaches terminal proof.

---

### SOP-011 - Gary call count confirmed; request settings still contradict preserve - 2026-07-09T15:49:08-04:00

**Scope reviewed:** `git status --short --branch`, latest git log, authentic liveproof evidence directory, `driver-log.txt`, `walk-log.txt`, trial `235f2b82-5989-4a6f-9e6b-22e9697f58d2` run status, Gary contribution fields from `run.json`, Gary `gary_slide_output`, package-builder slides, specialist summaries, process list, and search for persisted Gamma request/settings evidence. No tests were run by this monitor poll. No production/test/runtime files were edited by this monitor; this ledger entry is the only write.

**Current repo state:** `HEAD` remains `6783b54b` (`fix(irene): restore Pass-1 per-unit fidelity emission`) and is synced with `origin/dev/lesson-planning-2026-07-09`. `origin/master` / local `master` remain at `f30c88c9`. Working tree has this monitor ledger dirty, `state/config/gamma-styleguide-picks.jsonl` dirty with two runtime pick rows, two untracked liveproof evidence directories, and untracked `runs/235f2b82-5989-4a6f-9e6b-22e9697f58d2/`.

**Authentic liveproof state:** the run has not advanced in the registry since SOP-010. `run.json` still reports `status: paused-at-gate`, `paused_gate: G2C`, no paused error tag, `completed_at: null`, `artifact_count=10`, and `contribution_count=13`. `driver-log.txt` still ends after `resume approve G2C`; no terminal facts/claim verdict have appeared in the evidence directory. `walk-log.txt` has additional OpenAI activity through 15:43:58 and specialist summaries now include `vision-20260709T194358910618Z.md`, but those later steps do not add Gary preserve proof.

**New concrete Gary extraction:** the Gary contribution in `run.json` explicitly reports `calls_made: 2`, `generation_mode: single-dispatch`, `generation_id: j3kuMip6KOXx16Zoo2viH`, and one persisted `variant_gamma_settings` block: `text_mode: "condense"` with `amount: "brief"`. This confirms a two-call/split-like Gary execution, but the persisted top-level settings remain the classic condense settings.

**Per-slide Gary output:** `gary_slide_output` contains nine exported cards. The literal-named cards `A-literal_slide-01.png`, `A-literal_slide-05.png`, and `A-literal_slide-09.png` use generation id `2xh2jtpTgAWzP2fB2KGsz`; creative cards use `j3kuMip6KOXx16Zoo2viH`. However, every card's embedded `gamma_settings`, including the literal cards, records `text_mode: "condense"` and `amount: "brief"`. No `text_mode: "preserve"` and no omitted-`amount` literal request is visible in the persisted Gary output.

**Request-level evidence visibility:** I found no separate raw Gary-to-Gamma request artifact beyond the Gary output fields, decision cards, checkpoint/resume/run JSON, and walk-log completion/download messages. The walk log confirms Gamma generation/downloads for the two generation IDs, but does not print request bodies. Therefore this poll can score `calls_made=2` as visible, but cannot score the required preserve/no-amount API request as visible.

**F-0018 remains open and is strengthened.** The prior "maybe metadata only" caveat is narrower now: the authoritative Gary contribution itself records two calls but still records condense/brief for literal outputs. Unless a later terminal proof artifact shows a lower-level request body with preserve/no-amount and explains why `gary_slide_output` is misleading, the visible live evidence does not satisfy the story's Gary override requirement.

**F-0019 remains open.** The proof harness risk is now concrete: `calls_made=2` is real and useful, but it is not sufficient by itself. The driver can only claim cohort splitting unless it also captures the literal cohort request settings.

**F-0017 remains open.** Package-builder slides show the expected fidelity distribution (`literal-text` on slide-01 and slide-09, `literal-visual` on slide-05), but the earlier G1 observation still said `no irene_pass1 contribution`. The exact authoritative surface Gary consumed still needs explanation if this evidence is used to close the upstream Irene emit claim.

**F-0015 remains open.** The no-stamp liveproof is still in progress and has useful partial evidence, but it is not terminal and does not currently prove preserve-over-condense.

**F-0013 remains open.** No banked focused pytest output, ruff output, RED-first transcript/evidence, bmad-code-review record, or final done-bar party concurrence is visible for the Pass-1 recovery story.

**F-0011 remains open.** Runtime/evidence residue remains unbanked and dirty/untracked: the tracked styleguide pick ledger has two new rows, and the active `runs/235f2b82.../` plus liveproof evidence directories remain untracked.

**Carried findings:** F-0003/F-0008 remain open for the original Gary-side done/MET reconciliation. F-0010 remains open for liveproof evidence banking. F-0016 remains open as broader governance-change review, not product validation. The collateral degradation warning from SOP-009 remains a separate caveat on broad run-quality claims.

**Verdict: SPLIT/CALL COUNT CONFIRMED / PRESERVE REQUEST STILL NOT VISIBLE / NOT SCOREABLE.** This poll improves confidence that Gary split or at least made two Gamma generations, but the only persisted Gary settings still show condense+amount on literal cards. The implementation remains unscoreable until request-level or terminal proof shows literal preserve with no amount, or the team fixes the runtime/reporting seam and reruns proof.

---

### SOP-012 - run still nonterminal; node 08 retry warning; governance surfaces dirty - 2026-07-09T15:59:08-04:00

**Scope reviewed:** `git status --short --branch`, latest git log, authentic liveproof evidence directory, `driver-log.txt`, `walk-log.txt`, trial `235f2b82-5989-4a6f-9e6b-22e9697f58d2` run status, run directory timestamps, specialist summaries, active Python processes, diffs for newly dirty governance/instruction files, untracked Cursor rule/agent stubs, and search for node 08 retry/error evidence. No tests were run by this monitor poll. No production/test/runtime files were edited by this monitor; this ledger entry is the only write.

**Current repo state:** `HEAD` remains `6783b54b` (`fix(irene): restore Pass-1 per-unit fidelity emission`) and is synced with `origin/dev/lesson-planning-2026-07-09`. `origin/master` / local `master` remain at `f30c88c9`. Working tree is now broader-dirty than SOP-011:

- modified: `.cursor/rules/bmad-sprint-governance.mdc`
- modified: `AGENTS.md`
- modified: `CLAUDE.md`
- modified: `bmad-session-protocol-session-START.md`
- modified: `bmad-session-protocol-session-WRAPUP.md`
- modified: `_bmad-output/implementation-artifacts/grok-shadow-monitor-irene-literal-2026-07-09.md`
- modified: `state/config/gamma-styleguide-picks.jsonl`
- untracked: `.cursor/agents/`
- untracked: `.cursor/rules/bmad-dual-agent-families.mdc`
- untracked: both liveproof evidence directories and `runs/235f2b82-5989-4a6f-9e6b-22e9697f58d2/`

**Authentic liveproof state:** no terminal status has landed. `run.json` still reports `status: paused-at-gate`, `paused_gate: G2C`, no paused error tag, `completed_at: null`, `artifact_count=10`, and `contribution_count=13`. `driver-log.txt` still ends after `resume approve G2C`; the evidence directory has no facts JSON, terminal claim verdict, or banked Gary request proof. The main run registry files remain timestamped around 15:35, while `walk-log.txt` advanced to 15:50.

**New runtime signal:** `walk-log.txt` records a retryable dispatch variance after SOP-011: `irene.pass2.slide-join-failed` at node `08`, auto-retry `1/3`. `run.json` still shows no paused error tag, and a live Python process from 15:12 remains active, so this is not yet a terminal failure. It is, however, a new proof-quality caveat: the run has moved into downstream composition activity with a retry warning, while the monitor still has no terminal proof.

**Gary preserve evidence unchanged:** no new raw Gary-to-Gamma request artifact appeared. SOP-011's state still stands: `calls_made=2` is visible, but persisted Gary settings and per-card `gary_slide_output` still show `text_mode: "condense"` and `amount: "brief"` for literal cards. F-0018 remains open.

**Governance/instruction changes:** new uncommitted edits add a Cursor "dual agent families" rule and optional `.cursor/agents/*.md` stubs for stock seats/custom Marcus routing. The visible diffs touch always-on rules and session protocols, not the Irene/Gary runtime code path. These changes may be operator-intended governance support, but they are not validation evidence for the current product claim and should be reviewed/banked separately from liveproof artifacts.

**F-0020 [P2] Proof run now has a downstream retry warning without terminal disposition.** The node 08 `irene.pass2.slide-join-failed` retry means the active no-stamp run is not cleanly terminal and may still be recovering. Required before scoreable close: wait for terminal success/failure and inspect any retry aftermath; do not score from partial G2/Gary evidence alone.

**F-0021 [P2] Broad Cursor/BMAD governance edits are mixed into the dirty worktree during the proof.** The new dual-agent-family rule/stubs and session-protocol edits are process governance, not Irene literal preserve proof. They need deliberate review and banking/disposition so they do not get swept into an evidence or monitor commit as incidental residue.

**F-0018 remains open.** Split/call-count evidence exists, but preserve/no-amount request evidence is still absent or contradicted by persisted Gary settings.

**F-0019 remains open.** The proof harness still risks over-scoring split/call-count and literal filenames as preserve-over-condense.

**F-0017 remains open.** The authoritative Irene-emission surface is still inconsistent: G1 observer saw `no irene_pass1 contribution`, while package/Gary surfaces later carry fidelity.

**F-0015 remains open.** The no-stamp liveproof has useful partial evidence but remains nonterminal and not scoreable.

**F-0013 remains open.** No banked focused pytest output, ruff output, RED-first transcript/evidence, bmad-code-review record, or final done-bar party concurrence is visible for the Pass-1 recovery story.

**F-0011 remains open.** Runtime/evidence residue remains unbanked and dirty/untracked: tracked styleguide picks, evidence dirs, active `runs/235f2b82.../`, and now the new Cursor governance surfaces.

**Carried findings:** F-0003/F-0008 remain open for the original Gary-side done/MET reconciliation. F-0010 remains open for liveproof evidence banking. F-0016 remains open as broader governance-change review, now reinforced by new process-surface edits. The collateral degradation warning from SOP-009 remains a separate caveat on broad run-quality claims.

**Verdict: NONTERMINAL RUN / RETRY WARNING / STILL NOT SCOREABLE.** The run is alive but not closed, and the new evidence does not resolve the Gary preserve request gap. Current score remains: partial split/call-count evidence only; no terminal proof; no visible preserve/no-amount request; no verification/close-party evidence.

---

### SOP-013 - terminal error + self-assessment overclaims MET - 2026-07-09T16:09:09-04:00

**Scope reviewed:** `git status --short --branch`, latest git log, authentic liveproof evidence directory, `driver-log.txt`, `walk-log.txt`, `facts.json`, `CLAIM-ASSESSMENT.md`, copied decision cards/run artifacts, run status from `state/config/runs/235f2b82-5989-4a6f-9e6b-22e9697f58d2/run.json`, Gary contribution/settings extraction, package-builder fidelity slides, contribution roster, and grep for `claim_ok`, `preserve`, `condense`, `amount`, `calls_made`, and `figure-contradiction`. No tests were run by this monitor poll. No production/test/runtime files were edited by this monitor; this ledger entry is the only write.

**Current repo state:** `HEAD` remains `6783b54b` (`fix(irene): restore Pass-1 per-unit fidelity emission`) and is synced with `origin/dev/lesson-planning-2026-07-09`. `origin/master` / local `master` remain at `f30c88c9`. Dirty/untracked surfaces are unchanged from SOP-012: the monitor ledger, tracked styleguide-picks, Cursor/BMAD governance docs/rules, untracked `.cursor/agents/`, untracked `.cursor/rules/bmad-dual-agent-families.mdc`, both liveproof evidence dirs, and untracked `runs/235f2b82.../`.

**Authentic liveproof terminal state:** the run is now terminally paused, not merely in-flight. `run.json` reports `status: paused-at-error`, `paused_error_tag: irene.pass2.figure-contradiction`, `completed_at: null`, `artifact_count=11`, and `contribution_count=17`. `driver-log.txt` records `ERROR-PAUSE after G2C: irene.pass2.figure-contradiction`, then `facts written; claim_ok=False; final_status=paused-at-error`. `walk-log.txt` records the same node 08 dispatch error: slide `slide-04` narration figures not present in perceived authority (`percent:10`).

**New evidence artifacts:** the evidence directory now contains copied run artifacts plus `facts.json` and `CLAIM-ASSESSMENT.md`. `facts.json` records:

- `final_status: paused-at-error`
- `final_error_tag: irene.pass2.figure-contradiction`
- `irene_literal_authentic_claim_ok: false`
- `irene_emitted_literal_text: false`
- G1 `irene_fidelity_observation.error: no irene_pass1 contribution`
- `gary_proof.gary_calls_made: 2`
- `gary_proof.package_fidelity_counts: {literal-text: 2, creative: 6, literal-visual: 1}`
- `gary_proof.gary_variant_text_modes: [{text_mode: condense, amount: brief, variant_id: A}]`
- `gary_proof.settings_still_condense: true`

**Positive evidence confirmed:** package/Gary still prove that fidelity-bearing slide grouping reached Gary packaging and that Gary made two calls. The contribution roster contains three `irene_pass1` contributions, package-builder slides carry `literal-text` on slide-01 and slide-09 plus `literal-visual` on slide-05, and Gary reports `calls_made=2`.

**Blocking evidence confirmed:** no preserve/no-amount request proof appeared. The Gary contribution still reports top-level `variant_gamma_settings` as `text_mode: "condense"` / `amount: "brief"`, and every `gary_slide_output` card, including `A-literal_slide-01.png`, `A-literal_slide-05.png`, and `A-literal_slide-09.png`, carries embedded `gamma_settings` with `text_mode: "condense"` / `amount: "brief"`. There is still no raw Gary->Gamma request body proving `text_mode=preserve` with `amount` omitted.

**F-0022 [P1] `CLAIM-ASSESSMENT.md` overclaims relative to the live facts and original story bar.** The self-assessment says driver `claim_ok=False` is "over-strict / observer bug" and declares the core product claim "MET." However, the same artifact narrows the proven claim to Gary binary-splitting cohorts while styleguide settings remained `condense`; it does not prove the original requirement that Gary force literal cohorts to `text_mode=preserve` with `amount` absent. The monitor treats this as a claim-envelope downgrade, not closure.

**F-0023 [P1] Terminal liveproof result is paused-at-error, not pass.** Even if the Pass-2 figure contradiction is out of scope for the Irene->Gary seam, the run is not a clean terminal success and the driver-authored `facts.json` marks `irene_literal_authentic_claim_ok: false`. This cannot be used as full done-bar proof without an explicit, scoped waiver and separate evidence that the required Gary API override actually happened.

**F-0018 remains open.** Split/call-count is proven; preserve/no-amount remains absent/contradicted.

**F-0019 remains open.** The proof harness/self-assessment now demonstrably over-scores split evidence as "Gary honor-over-styleguide" without showing the literal request override.

**F-0017 remains open but partially mitigated.** Later `irene_pass1` contributions exist and carry fidelity, but the G1 observer still failed, so the proof harness needs repair if it is to be relied on as an automated acceptance witness.

**F-0015 remains open as failed/nonpassing proof, not merely in progress.** The no-stamp liveproof produced useful artifacts, but the current terminal result is error-paused and `claim_ok=false`.

**F-0013 remains open.** No banked focused pytest output, ruff output, RED-first transcript/evidence, bmad-code-review record, or final done-bar party concurrence is visible for the Pass-1 recovery story.

**F-0011 / F-0021 remain open.** Runtime/evidence residue and broader Cursor/BMAD governance edits remain dirty/untracked and need deliberate disposition.

**Carried findings:** F-0003/F-0008 remain open for the original Gary-side done/MET reconciliation. F-0010 remains open for evidence banking. F-0016 remains open as broader governance-change review. The collateral degradation warning from SOP-009 remains a separate caveat on broad run-quality claims.

**Verdict: TERMINAL ERROR / PARTIAL SEAM EVIDENCE / CLAIM NOT SCOREABLE AS DONE.** The liveproof confirms authentic fidelity carry-through into packaging and two Gary calls, but it ends `paused-at-error`, has `claim_ok=false`, and still lacks the required literal `preserve`/no-`amount` API evidence. The active implementation is not externally scoreable as closed.

---

### SOP-014 - post-terminal no-change poll; overclaim still uncorrected - 2026-07-09T16:19:09-04:00

**Scope reviewed:** `git status --short --branch`, latest git log, authentic liveproof evidence directory listing, `driver-log.txt`, `walk-log.txt`, run status for trial `235f2b82-5989-4a6f-9e6b-22e9697f58d2`, and comparison against SOP-013's recorded facts/claim assessment. No tests were run by this monitor poll. No production/test/runtime files were edited by this monitor; this ledger entry is the only write.

**Current repo state:** no new commits have landed. `HEAD` remains `6783b54b` (`fix(irene): restore Pass-1 per-unit fidelity emission`) and is synced with `origin/dev/lesson-planning-2026-07-09`. `origin/master` / local `master` remain at `f30c88c9`. The dirty/untracked worktree shape is unchanged from SOP-013: Cursor/BMAD governance docs/rules/stubs, this monitor ledger, tracked `state/config/gamma-styleguide-picks.jsonl`, both liveproof evidence dirs, and untracked `runs/235f2b82.../`.

**Evidence state:** the authentic evidence directory is unchanged since SOP-013. It still contains `facts.json`, `CLAIM-ASSESSMENT.md`, copied run artifacts through G2C, and the driver/walk logs. `driver-log.txt` still ends with `facts written; claim_ok=False; final_status=paused-at-error`; `walk-log.txt` still ends with the node 08 `irene.pass2.figure-contradiction` dispatch error. No corrected claim assessment, raw Gamma request proof, close-party record, or banked verification output appeared.

**Run status:** `state/config/runs/235f2b82-5989-4a6f-9e6b-22e9697f58d2/run.json` still reports `status: paused-at-error`, `paused_error_tag: irene.pass2.figure-contradiction`, `completed_at: null`, `artifact_count=11`, and `contribution_count=17`.

**Scoreability:** unchanged from SOP-013. The run provides partial seam evidence: three `irene_pass1` contributions exist, package/Gary surfaces carry `literal-text:2`, `creative:6`, `literal-visual:1`, and Gary made two calls. It does not provide scoreable done evidence because the run ended error-paused, the driver facts say `claim_ok=false`, and the visible Gary settings remain `condense` with `amount=brief` for literal outputs.

**F-0022 remains open.** `CLAIM-ASSESSMENT.md` still declares the core claim "MET" despite the live facts and original requirement gap. No correction or narrowed claim envelope is visible.

**F-0023 remains open.** Terminal liveproof result remains paused-at-error, not pass.

**F-0018 remains open.** Preserve/no-amount request evidence is still absent or contradicted.

**F-0019 remains open.** The proof package still risks over-scoring split/call-count as preserve-over-condense.

**F-0017 remains open.** The G1 observer false-negative remains unresolved, though later Irene contributions mitigate the "no fidelity exists" interpretation.

**F-0015 remains open as failed/nonpassing proof.** The no-stamp liveproof has not been converted into passing evidence.

**F-0013 remains open.** No banked focused pytest output, ruff output, RED-first transcript/evidence, bmad-code-review record, or final done-bar party concurrence is visible.

**F-0011 / F-0021 remain open.** Runtime/evidence residue and broader Cursor/BMAD governance edits remain dirty/untracked and need deliberate disposition.

**Verdict: NO MATERIAL CHANGE / STILL NOT SCOREABLE.** Since SOP-013, no new evidence has corrected the terminal error, the `claim_ok=false` result, or the missing literal preserve/no-amount proof. Continue monitoring only if the Grok/Cursor team resumes the run, patches the proof harness, or banks a narrowed/corrected evidence record.
