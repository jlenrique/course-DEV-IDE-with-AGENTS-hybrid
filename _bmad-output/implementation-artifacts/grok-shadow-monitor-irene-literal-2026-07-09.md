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
