# Shadow Monitor - Phase-2 evolutionary step: assessed source -> purpose/audience -> conversational plan -> selection

Started: 2026-07-09T16:49:00-04:00
Branch: `dev/lesson-planning-2026-07-09`.
Driver lane: Grok 4.5 in Cursor.
Monitor lane: Codex independent shadow monitor.

## Monitor Lane (read-only, independent)

This is an independent shadow-monitoring lane for the Phase-2 evolutionary-step dev session. Each poll reads the current repository state and appends a time-stamped report with findings (`SOP-NNN`). The monitor writes only this log. It does not modify production code, tests, runtime state, commits, branches, Grok/Cursor-owned artifacts, or BMAD-owned decision records.

The lane's job is to catch regressions, unratified drift, vacuous-green, claim-envelope overreach, and Marcus-SPOC product-boundary violations before the active driver claims a gate or done-bar.

## Product Boundary (binding)

The product is the Marcus-SPOC local runtime orchestrator: a local operator-facing runtime that drives a real app instance and its production pipeline. The goal is not to make concierge/proofing runs convenient. Do not reopen S8 to make this arc pass, do not distort approved styleguide registry guides, and do not treat proofing-driver accommodations as product requirements.

## Claim Envelope Under Watch

The active session goal is the next Phase-2 evolutionary step: variable source arrives; ingestion assesses/tags what is available and what is missing; Marcus-SPOC elicits or finds instructional purpose and audience; the operator-facing conversation reasons about asset choices, workflow choices, and production gap-fill tradeoffs; the ratified outcome drives `ComponentSelection` into composed local production. The monitor treats this as a spine claim, not a static front-door bundle-pick claim.

Binding SSOT:

- `_bmad-output/planning-artifacts/lesson-plan-rationale-platform-positioning-2026-07-07.md` §4.
- `_bmad-output/planning-artifacts/deferred-inventory.md` §Lesson-Plan-as-Rationale Platform.
- Spine item: `lesson-plan-directs-production-collateral-to-selection-edge`.
- Already-landed foundation: S7 Phase-2 A-D course-source substrate and S8 selection/planning-input contracts.

## Standing Watchpoints (this arc)

1. **Fully spawned BMAD governance first.** The first visible gate should be real BMAD party-mode with John, Winston, Amelia, and Murat. `generalPurpose` stand-ins do not satisfy the green-light or close gate. Impasse routes to Dr. Quinn synthesis, then John PM decision if needed.
2. **Claim envelope before code.** The party must green-light what is IN vs fenced, including existing seams, missing glue, residuals, validation bar, and done definition before implementation proceeds.
3. **Existing seams must be named and reused.** The implementation should build on course-source registry/gaps/bundles, Irene collateral, S8 selection edge, and SPOC interlocution rather than inventing a parallel planning path.
4. **Missing glue is the target.** Watch for honest implementation of conversational derivation from assessed source + purpose/audience + gap-fill tradeoff into `ComponentSelection`, not just another static bundle selector.
5. **Variable-source proof is required.** Validation should exercise different source types/amounts, preferably thin HAI/PHS syllabus-only plus richer curated Tejal fixtures already on disk. One overfit corpus does not prove the claim.
6. **Purpose/audience must be first-class enough to affect planning.** The work may fence full LO ratification or purpose plumbing if needed, but it must not claim purpose/audience-driven planning if those inputs are decorative.
7. **Gap-fill tradeoffs must surface honestly.** The conversation should distinguish what the pipeline can synthesize now, what must wait, and what lighter collateral/workflow alternatives are available.
8. **Ratification must drive selection.** The ratified plan/build/workflow outcome must produce or alter `ComponentSelection` consumed by composed local production. Closeout must not score a transcript-only conversation.
9. **Residuals need explicit disposition.** LO/purpose residue, SME routing, projector family, ingestion/tag robustness, and emergent items must be landed if in-envelope or fenced by name if out-of-envelope.
10. **Styleguide registry discipline.** Approved styleguide registry guides must not be ad-hoc edited to get through a proof; SME/styleguide fallback must be explicit and marked if used.
11. **RED-first and live-test cadence.** New seams need RED-first evidence and live/component validation as they are authored, not only late smoke tests.
12. **Code review is load-bearing.** `bmad-code-review` findings, especially MUST-FIX items and shadow-monitor notes, must be remediated before final close.
13. **Liveproof must be local Marcus-SPOC.** At least one local Marcus-SPOC path must show assessed source + purpose/audience context yielding ratified build/workflow/gap-fill selection that honestly composes production components.
14. **Close can be COMPLETE-with-fenced-residuals only if named.** Any residual must be explicit, scoped, and recorded in letter/inventory/STATE/project-context; otherwise the claim remains open.
15. **No inherited overclaim from the Irene-literal watch.** This arc should not rely on the prior Irene-literal "MET" wording as proof of any Phase-2 spine behavior. Treat the old monitor findings as historical caveats.
16. **Stray hygiene.** Existing untracked evidence/runtime residue and local-only commits must be deliberately banked, pushed, or explicitly left local; do not sweep unrelated residue into this arc's proof.

## Poll Log

### SOP-000 - baseline / new Phase-2 monitor opened - 2026-07-09T16:49:00-04:00

**Scope reviewed:** user-supplied session goal, current git status/log context from the prior poll, old Irene-literal monitor ledger header and terminal state through SOP-016, `_bmad-output/planning-artifacts/lesson-plan-rationale-platform-positioning-2026-07-07.md` §3-§5, and `_bmad-output/planning-artifacts/deferred-inventory.md` §Lesson-Plan-as-Rationale Platform. No tests were run. No production/test/runtime files were edited by this monitor; this new ledger and the old-ledger transition marker are the only repo writes.

**Current repo state at monitor open:** branch `dev/lesson-planning-2026-07-09` was last observed at local `HEAD` `1f48fbf6` (`docs: close S8 books and bank Irene-literal liveproof`) and `ahead 1` of `origin/dev/lesson-planning-2026-07-09`, whose remote tip was still `6783b54b`. The worktree already had the old Irene-literal monitor ledger modified from SOP-016, plus untracked `_bmad-output/implementation-artifacts/evidence/irene-literal-liveproof-20260709T143510/` and `runs/235f2b82-5989-4a6f-9e6b-22e9697f58d2/`. This new ledger adds a fresh tracked-uncommitted monitor artifact.

**SSOT baseline:** the positioning artifact says the front half generalizes well, but the governance spine is aspirational. The explicit blocker is that Irene emits rich collateral while the operator separately picks a static bundle whose fixed `ComponentSelection` decides the run; nothing reads the lesson plan/collateral to derive selection. The deferred inventory marks the spine trigger fired on 2026-07-09 and carries neighboring residuals: course/SME styleguide/approval routing, purpose/LO ratification, projector family, and ingestion/enrichment robustness.

**Initial scoreability:** no Phase-2 evolutionary implementation evidence is visible yet in this monitor lane. There is no new party green-light record, story/spec artifact, RED-first output, code diff, live component evidence, or local Marcus-SPOC liveproof for the new claim envelope at baseline.

**F-P2-0001 [P1] Green-light evidence is required before implementation is scoreable.** The operator explicitly requires fully spawned John/Winston/Amelia/Murat party-mode to green-light the Phase-2 evolutionary claim envelope before story/code work. Until that record is visible and names IN vs fenced scope, this monitor will score implementation movement as premature or ungoverned.

**F-P2-0002 [P1] The central proof must be derivation into `ComponentSelection`, not conversation alone.** The SSOT's named blocker is `collateral -> ComponentSelection -> composed graph`. Any story that only captures source assessment or planning dialogue without proving ratified selection consumption will not satisfy the spine.

**F-P2-0003 [P2] Baseline repo hygiene carries old-session residue.** The old Irene-literal monitor ledger, an old stalled evidence directory, and the `runs/235f2b82...` mirror are still present in the worktree. They are not blockers for starting the new monitor, but closeout should not sweep them into Phase-2 proof or leave local-only state ambiguous.

**Watchpoint verdicts at baseline:** WP1, WP2, WP11, WP12, WP13, and WP14 are open pending party/story/test/live evidence. WP3-WP10 are not yet violated but need active monitoring. WP15 is active because the prior Irene-literal close language remains historically contested. WP16 is open pending hygiene disposition.

**Recommendation to Grok/Cursor lane:** begin with the requested fully spawned BMAD green-light and a claim-envelope record that explicitly lists existing seams, missing glue, in/out residuals, and liveproof bar. Do not code from the high-level goal alone; make the derivation-to-selection acceptance test concrete before implementation.

**Verdict: MONITOR OPENED / WAITING ON PHASE-2 CLAIM-ENVELOPE GATE.** The new arc is product-valid and aligned with the SSOT, but no Phase-2 implementation claim is currently scoreable.

---

### SOP-001 - claim envelope and Claude ledger appeared; pre-spec still not scoreable - 2026-07-09T16:56:00-04:00

**Scope reviewed:** new untracked `_bmad-output/implementation-artifacts/phase2-evolutionary-claim-envelope-2026-07-09.md`, new untracked `_bmad-output/implementation-artifacts/claude-shadow-monitor-phase2-evolutionary-2026-07-09.md`, git status, and comparison against this ledger's baseline watchpoints. No tests were run. No production/test/runtime files were edited by this monitor; this SOP append is the only additional write.

**Current repo state:** branch remains `dev/lesson-planning-2026-07-09`, local `HEAD` previously observed at `1f48fbf6` and ahead of origin by one. Working tree now includes this Codex monitor ledger, the transitioned Irene-literal ledger, untracked Phase-2 claim envelope, untracked Claude monitor ledger, old stalled Irene evidence, and `runs/235f2b82...`. The Phase-2 artifacts are not yet committed/banked.

**Claim-envelope evidence:** `_bmad-output/implementation-artifacts/phase2-evolutionary-claim-envelope-2026-07-09.md` asserts fully spawned John/Winston/Amelia/Murat party-mode with 4/4 `GO-WITH-AMENDMENTS`. It names the correct product boundary, the SSOT, the IN claim envelope, fenced residuals, existing seams vs missing glue, binding amendments, and a Murat witness matrix W1-W5.

**Positive gate signal:** the envelope addresses the core monitor requirements better than the raw user goal alone. It keeps `ComponentSelection` as the production contract, requires thin and rich source witnesses, requires a gap-fill tradeoff witness, requires a selection delta, fences SME routing/projector/full lecture ingestion, and selects `bmad-create-story -> bmad-dev-story` over quick-dev. This substantially satisfies the shape of WP1-WP2 for the pre-code gate, subject to banking and downstream story conformance.

**Claude monitor signal:** `_bmad-output/implementation-artifacts/claude-shadow-monitor-phase2-evolutionary-2026-07-09.md` exists as an untracked companion ledger with standing watchpoints and POLL-000. It currently has no findings and names required gate actions. This Codex ledger remains the active ledger for this thread's heartbeat automation; the two ledgers should be reconciled at close so findings are not split or lost.

**F-P2-0001 status: partially resolved / still needs banking.** The claim envelope asserts the required real-seat party green-light and names the gate amendments. This is enough to move the monitor from "waiting on claim-envelope gate" to "waiting on story/spec conformance," but the artifact is untracked and no separate party transcript/record is visible. Before close, the envelope needs to be banked and cited, and any story must inherit its MUST amendments.

**F-P2-0002 remains open.** The envelope correctly defines derivation into `ComponentSelection` as the central claim, but no story, tests, code, or liveproof exist yet.

**F-P2-0003 remains open.** Worktree hygiene now includes additional Phase-2 untracked artifacts plus prior Irene residue. This is acceptable during active authoring but needs explicit banking/disposition before final done.

**F-P2-0004 [P2] Dual shadow-monitor ledgers can split findings if not reconciled.** The repo now has both a Claude monitor ledger and this Codex monitor ledger. Required before close: either designate one as canonical and cross-reference the other, or explicitly reconcile open findings from both.

**F-P2-0005 [P2] Claim envelope inherits "Irene-literal MET" wording despite prior monitor caveat.** The envelope says "Do not reopen: S8; Irene-literal MET; Pass-2 figure/numeral HELR parked." For this Phase-2 arc, that should be treated as an upstream state assertion, not proof of the new spine. The story/closeout must not use the prior Irene-literal claim to satisfy any Phase-2 witness.

**Watchpoint updates:** WP1-WP2 are improved by the claim envelope but remain open until banked and reflected in the actual story. WP3-WP9 are positively addressed in the envelope but unproven. WP11-WP13 remain open pending RED-first, code, and local Marcus-SPOC liveproof. WP15 remains active due to inherited Irene-literal wording. WP16 remains open.

**Verdict: CLAIM-ENVELOPE SHAPE IS GOOD / IMPLEMENTATION STILL NOT SCOREABLE.** The pre-code gate has a strong untracked artifact, but the active implementation has no scoreable story/spec, tests, code, or liveproof yet. Next monitor poll should inspect whether `bmad-create-story` produced ACs that faithfully carry the envelope into an executable slice.

---

### SOP-002 - story and first library slice visible; no test/liveproof evidence yet - 2026-07-09T16:49:24-04:00

**Timestamp note:** this heartbeat arrived at 2026-07-09T16:49:09-04:00 after SOP-001 had already been appended during the manual monitor retarget. Entry order follows SOP sequence; the absolute heartbeat time is recorded here to preserve the automation chronology.

**Scope reviewed:** local clock, `git status --short --branch`, `git status --short --untracked-files=all`, latest git log, current ledger tail, new story `_bmad-output/implementation-artifacts/phase2-evolutionary-planning-to-selection-bridge.md`, new source files `app/marcus/lesson_plan/source_assessment.py` and `app/marcus/lesson_plan/planning_ratification.py`, new tests `tests/marcus/lesson_plan/test_source_assessment.py` and `tests/marcus/lesson_plan/test_planning_ratification.py`, fixture path existence for HAI/PHS/Tejal, evidence-directory scan for Phase-2 proof artifacts, and grep for trial/front-door/selection integration references. No tests were run by this monitor poll. No production/test/runtime files were edited by this monitor; this ledger entry is the only write.

**Current repo state:** no new commit has landed. Local `HEAD` remains `1f48fbf6` (`docs: close S8 books and bank Irene-literal liveproof`) and branch `dev/lesson-planning-2026-07-09` remains ahead of `origin/dev/lesson-planning-2026-07-09` by one. Expanded status shows:

- modified: `_bmad-output/implementation-artifacts/grok-shadow-monitor-irene-literal-2026-07-09.md`
- untracked: `_bmad-output/implementation-artifacts/phase2-evolutionary-claim-envelope-2026-07-09.md`
- untracked: `_bmad-output/implementation-artifacts/phase2-evolutionary-planning-to-selection-bridge.md`
- untracked: `_bmad-output/implementation-artifacts/claude-shadow-monitor-phase2-evolutionary-2026-07-09.md`
- untracked: this Codex monitor ledger
- untracked: `app/marcus/lesson_plan/source_assessment.py`
- untracked: `app/marcus/lesson_plan/planning_ratification.py`
- untracked: `tests/marcus/lesson_plan/test_source_assessment.py`
- untracked: `tests/marcus/lesson_plan/test_planning_ratification.py`
- old residue: `_bmad-output/implementation-artifacts/evidence/irene-literal-liveproof-20260709T143510/*` and `runs/235f2b82-5989-4a6f-9e6b-22e9697f58d2/irene-pass1.md`

**Story/spec evidence:** the new story is `ready-for-dev`, names the correct spine, carries a dual-gate mode, cites the claim envelope/SSOT/S8 contract/Story-D close context, and folds the party amendments into ACs. Positives: it keeps `ComponentSelection` and the S8 resolver as the selection contract, requires HAI + PHS thin and Tejal rich coverage, requires structured gap-fill tradeoff, requires a machine-checkable selection delta, rejects Tejal-only proof, fences SME routing/projectors/full lecture ingestion/Irene reshape/S8 redesign, and names shadow-monitor findings as a Gate-2 DoD input.

**Implementation surface:** two new untracked library files are present. `source_assessment.py` adds a strict `SourceAssessment` model, an input-bundle assessment path, a curated-corpus assessment path, and a non-cosmetic differ helper. `planning_ratification.py` adds a strict ratification record, closed gap-fill vocabulary, purpose/audience checks, overclaim rejection, S8 intent emission, artifact writers, and selection-delta computation via existing resolver functions. This is a plausible first slice and stays in the intended `app/marcus/lesson_plan/**` area.

**Test surface:** two new untracked tests are present and appear to cover the main library behaviors: HAI/PHS thin assessment, Tejal rich assessment, thin-vs-rich difference, refusal of course-root-as-corpus, source-assessment requirement, purpose/audience requirement, lighter collateral intent, rich workbook intent, selection delta, missing-delta rejection, S8 resolver compatibility, overclaim rejection, and structured gap-fill alternatives. `git ls-files` does not yet know these test files, so they remain unbanked.

**Fixture visibility:** the referenced HAI, PHS, Tejal, and S7 evidence fixture paths exist locally. Tejal rich leaf has `slides/`, `references/`, `assessments/`, `README.md`, and `urls.txt`, so the curated-corpus test path is plausible from file shape.

**Evidence/liveproof visibility:** no Phase-2 evidence directory was visible under `_bmad-output/implementation-artifacts/evidence/`. No W1-W4 witness artifact, selection-delta artifact, ratified-collateral-intent artifact, test-output transcript, ruff output, local Marcus-SPOC transcript, or compose/trial-start proof has appeared. Current implementation is library-level; no `front_door.py`, `trial.py`, CLI helper, runner, or SPOC surface change is visible in git status.

**F-P2-0001 status: improved but still open.** The story now inherits the party claim envelope and folds amendments into ACs. It still needs banking, and close still needs fully spawned party concurrence after implementation.

**F-P2-0002 status: partially improved but open.** The ratification library emits S8 intent and computes a selection delta, which is the right derivation shape. It is not yet proven through a production/SPOC path or live evidence.

**F-P2-0003 remains open.** Worktree hygiene now includes additional untracked story/code/test artifacts plus old-session residue. This is normal mid-dev but must be disposed before close.

**F-P2-0004 remains open.** Dual Claude/Codex monitor ledgers remain split and untracked. Close must reconcile findings from both.

**F-P2-0005 remains open.** The story and envelope still carry "Irene-literal MET" as upstream posture. This must not be used as evidence for any Phase-2 witness.

**F-P2-0006 [P1] W5 compose scope is now explicitly optional in the story, which narrows the ambitious session goal if not acknowledged.** The claim envelope says W5 is required to claim composed local production, while the user's session goal and Definition of Done describe `ComponentSelection -> composed local production`. The story makes W5 stretch/diagnostic unless explicitly claimed. Required before close: either produce W5 if claiming composed production, or explicitly close as selection-edge-only / COMPLETE-with-fenced compose residual so the done claim does not overreach.

**F-P2-0007 [P1] RED-first/test evidence is absent.** Tests and code are visible together, but no failing-first transcript, green pytest output, or ruff output is banked. Required before scoreable implementation: focused RED/GREEN evidence for the new tests plus ruff or equivalent lint evidence.

**F-P2-0008 [P1] No Marcus-SPOC/live path is wired or proven yet.** The current code is a good library-level start, but the claim requires a lesson-planning conversation/ratification outcome that drives selection. No SPOC transcript, CLI/helper, trial-start, or local compose evidence is visible.

**F-P2-0009 [P2] New tests are untracked and easy to miss in short status.** `git status --short` only showed untracked directories, while expanded status shows the test files. They need to be banked with the implementation or explicitly removed if superseded.

**Scoreability:** not scoreable as done. The story/spec is now scoreable for shape and is mostly aligned with the claim envelope. The implementation is not scoreable beyond "first library slice present" because it lacks banked test evidence, liveproof, selection artifacts, and SPOC/compose integration.

**Verdict: STORY SHAPE GOOD / FIRST LIBRARY SLICE PRESENT / NOT YET SCOREABLE.** Continue monitoring for the next gate: focused RED/GREEN + ruff output, W1-W4 evidence artifacts, explicit W5/compose claim decision, and a real SPOC or trial-start path proving ratified selection consumption.

---

### SOP-003 - concurrent W1-W4 evidence bundle appeared; still not final done-bar - 2026-07-09T16:52:00-04:00

**Scope reviewed:** post-SOP-002 expanded git status, new evidence directory `_bmad-output/implementation-artifacts/evidence/phase2-evolutionary-bridge-20260709T204500/`, `WITNESS-SUMMARY.json`, `CLAIM-ASSESSMENT.md`, W1/W2/W3/W4 artifact files, and new utility script `scripts/utilities/bank_phase2_evolutionary_bridge_evidence.py`. No tests were run by this monitor poll. No production/test/runtime files were edited by this monitor; this ledger entry is the only write.

**Concurrency note:** the evidence bundle appeared during the post-write verification for SOP-002. SOP-002's "no Phase-2 evidence directory" statement was accurate at its read point but is now superseded by this SOP-003.

**Current repo state:** no commit has landed; local `HEAD` remains `1f48fbf6` and the branch remains ahead of origin by one. The worktree now includes all prior untracked Phase-2 story/code/test artifacts plus:

- `_bmad-output/implementation-artifacts/evidence/phase2-evolutionary-bridge-20260709T204500/CLAIM-ASSESSMENT.md`
- `_bmad-output/implementation-artifacts/evidence/phase2-evolutionary-bridge-20260709T204500/WITNESS-SUMMARY.json`
- W1 HAI/PHS assessment JSONs
- W2 Tejal assessment JSON and rich ratification artifacts
- W3 thin ratification artifacts
- W4 selection-delta JSON
- `scripts/utilities/bank_phase2_evolutionary_bridge_evidence.py`

**Evidence summary:** `WITNESS-SUMMARY.json` claims W1 thin HAI/PHS true, W2 rich Tejal true, W3 structured gap-fill tradeoff true, W4 selection delta true, `thin_ne_rich: true`, and `W5_compose: stretch-not-claimed`. The thin ratification records purpose/audience, HAI source gaps, workflow `narrated-deck`, gap-fill choice `wait`, and emits a canonical S8 intent with `bundle_id: narrated-deck`. The delta changes baseline `narrated-deck-with-motion` to `narrated-deck`, with motion true->false. The rich ratification records Tejal rich source, workflow `narrated-deck-with-workbook`, and emits workbook collateral.

**Positive movement:** W1-W4 are now materially better than SOP-002: there are machine-checkable artifacts for thin/rich source variability, purpose/audience, structured gap-fill, canonical S8 intent emission, and a selection delta. This directly improves F-P2-0002 and partially satisfies the story's minimum witness matrix.

**Test evidence caveat:** the witness summary contains the string `tests/marcus/lesson_plan/test_source_assessment.py + test_planning_ratification.py = 14 passed`, but no raw pytest transcript, command line, exit code, RED-first transcript, or ruff output is visible in the evidence bundle. The monitor did not run tests.

**Live/SPOC caveat:** the evidence was generated by `bank_phase2_evolutionary_bridge_evidence.py`. It is a useful scripted witness, but it is not a visible Marcus-SPOC conversation transcript, not a local trial-start proof, and not a compose proof. The story allows scripted SPOC/HIL witness for this slice, but the user-level goal still asks for Marcus-SPOC lesson-planning conversation and composed local production unless explicitly fenced.

**F-P2-0002 status: partially resolved / not closed.** W1-W4 artifacts now exist and use the right S8 intent/selection shape. The remaining gap is production-path proof: no front-door/trial/SPOC consumption evidence or compose evidence is visible.

**F-P2-0006 remains open.** `CLAIM-ASSESSMENT.md` says `MET (W1-W4)` and W5 is `stretch / not claimed this close`. This is acceptable only as a planning-to-selection bridge claim. It must not be reported as "composed local production" or full session DoD unless W5 is produced or the compose residual is explicitly fenced and accepted.

**F-P2-0007 remains open.** Raw RED/GREEN and ruff evidence remain absent despite the self-reported `14 passed` string.

**F-P2-0008 remains open but narrowed.** The generated ratification artifacts prove selection-edge shape, but no Marcus-SPOC conversation/live path or trial-start consumption is visible.

**F-P2-0010 [P1] `CLAIM-ASSESSMENT.md` is premature if treated as final close.** It declares `MET (W1-W4)` before visible bmad-code-review, monitor finding disposition, dual-gate party close, or banking/commit. Required before done: explicitly scope it as pre-close witness evidence or complete the missing close gates.

**F-P2-0011 [P2] Evidence is untracked and generated by an untracked script.** The evidence bundle and banking script need to be committed or otherwise deliberately disposed. If the script is part of the proof method, bank it with the artifacts or include a raw execution transcript so the artifact provenance is reproducible.

**Scoreability:** partially scoreable for W1-W4 artifact shape only. Not scoreable as final done, not scoreable as composed production, and not scoreable as a live Marcus-SPOC workflow yet.

**Verdict: W1-W4 ARTIFACTS LANDED / CLAIM MUST STAY NARROW.** The arc has made real progress since SOP-002, but the current evidence supports only a scoped planning-to-selection bridge witness. Final close still needs raw test/ruff evidence, code review, monitor disposition, party close, banking/commit/push, and either W5 compose or an explicit compose residual fence.

---

### SOP-004 - local close docs mark PARTIAL-MET / done; close remains narrow and unbanked - 2026-07-09T16:59:09-04:00

**Scope reviewed:** `git status --short --branch --untracked-files=all`, latest git log, evidence bundle listing and updated W1-W4 artifacts, `WITNESS-SUMMARY.json`, `CLAIM-ASSESSMENT.md`, revised `scripts/utilities/bank_phase2_evolutionary_bridge_evidence.py`, `planning_ratification.py` remediation surface, diffs for `_bmad-output/planning-artifacts/deferred-inventory.md`, `docs/STATE-OF-THE-APP.md`, and `docs/project-context.md`, companion Claude shadow ledger, and the story close record in `phase2-evolutionary-planning-to-selection-bridge.md`. No tests were run by this monitor poll. No production/test/runtime files were edited by this monitor; this ledger entry is the only write.

**Current repo state:** no new commit has landed. Local `HEAD` remains `1f48fbf6` and branch `dev/lesson-planning-2026-07-09` remains ahead of origin by one. The worktree now has additional modified tracked docs: `_bmad-output/planning-artifacts/deferred-inventory.md`, `docs/STATE-OF-THE-APP.md`, and `docs/project-context.md`. The Phase-2 story, code, tests, monitor ledgers, evidence bundle, and banking script remain untracked. Old Irene-literal residue remains untracked.

**Close/status movement:** the story frontmatter is now `status: done`, with a close record declaring party close by John/Winston/Amelia/Murat and disposition `COMPLETE-with-named-fenced-residuals`. `docs/project-context.md` adds the same close claim. `deferred-inventory.md` marks the spine `PARTIAL-MET 2026-07-09`, and `docs/STATE-OF-THE-APP.md` now calls the live frontier `Phase-2 evolutionary bridge PARTIAL-MET`. This is better claim hygiene than a full-MET claim because it explicitly carries residuals.

**Evidence remediation since SOP-003:** W4 was corrected from default-vs-one-ratification into same-thin-fixture two-disposition delta. The evidence now contains `w3-thin-ratification-wait/` and `w3-thin-ratification-lighter/`; W4 delta is `narrated-deck` -> `narrated-deck-with-motion`. `CLAIM-ASSESSMENT.md` says a Gate-1 MUST-FIX for two-disposition delta, claim-fence affirmative hole, and gap_fill/workflow consistency was remediated. `planning_ratification.py` now includes stricter claim-fence validation and workflow/gap-fill contradiction checks.

**Companion monitor signal:** the Claude ledger reports POLL-000 through POLL-004 as dispositioned, 16 focused tests green, Gate-1 Amelia fail remediated, W1-W4 liveproof evidence banked, and F-P2-005 deferred-with-ticket. This is useful corroborating process evidence, but it is a compact ledger, not a raw pytest/ruff/code-review transcript.

**Positive scoreable slice:** W1-W4 planning-to-selection artifact evidence is now meaningfully scoreable in shape: thin HAI/PHS source assessment, rich Tejal assessment, purpose/audience-bearing ratification records, structured gap-fill tradeoffs, canonical S8 intent files, and same-fixture selection delta. The docs now correctly call this `PARTIAL-MET` rather than full Phase-2 completion.

**F-P2-0002 status: mostly resolved for W1-W4, still open for production-path proof.** The artifact bridge into S8 intent and selection is now credible for the scoped W1-W4 slice. It is still not proof of interactive SPOC REPL, trial-start consumption, or composed local production.

**F-P2-0006 status: dispositioned only if PARTIAL-MET wording holds.** W5 compose is explicitly fenced in story/evidence/docs. This is acceptable for a W1-W4 bridge close, but any future summary must not call it final composed local production.

**F-P2-0007 remains partly open.** The Claude ledger reports 16 focused tests green, but no raw pytest command/output, ruff command/output, or RED-first transcript is visible in the evidence bundle. If the team relies on the compact Claude ledger as sufficient, close should say that explicitly; otherwise raw test evidence should be banked.

**F-P2-0008 remains open but fenced.** The close record fences interactive pre-start SPOC planning REPL and W5 compose liveproof. That prevents overclaim, but means the user's ambitious Marcus-SPOC conversation/composed-production goal is not fully complete.

**F-P2-0010 status: improved but still needs banking.** `CLAIM-ASSESSMENT.md` now aligns with PARTIAL-MET/W1-W4 scope. Remaining issue is durability: all Phase-2 artifacts are untracked and uncommitted.

**F-P2-0011 remains open.** Evidence and the banking script remain untracked.

**F-P2-0012 [P1] Done/party-close claims are present, but no standalone bmad-code-review record is visible.** The story DoD requires `bmad-code-review`; the visible files show Gate-1 Amelia findings and party close, but no dedicated bmad-code-review artifact or raw review transcript appeared. Required before robust final scoring: bank the review record or explicitly cite the Claude monitor/close record as the review authority.

**F-P2-0013 [P2] Close docs are modified before the implementation/evidence is committed.** `STATE`, `project-context`, and `deferred-inventory` now point to Phase-2 bridge PARTIAL-MET while the implementation, tests, evidence, and story are still untracked. This is acceptable mid-close only if a commit follows promptly; otherwise the repo can advertise a state that does not exist on the branch.

**Scoreability:** scoreable as a local, uncommitted W1-W4 planning-to-selection bridge PARTIAL-MET, subject to accepting the compact Claude monitor as test/review process evidence. Not scoreable as final Phase-2 completion, not scoreable as W5 composed production, and not durable until committed/pushed.

**Verdict: LOCAL PARTIAL-MET CLOSE SHAPE IS HONEST BUT NOT BANKED.** The team corrected the earlier delta issue and narrowed the claim properly. Remaining monitor asks: commit/push the Phase-2 artifacts, reconcile/keep both monitor ledgers, bank or cite raw test/ruff/code-review evidence, and keep interactive SPOC REPL + W5 compose listed as residuals unless actually proven.

---

### SOP-005 - no material change; local partial close still unbanked - 2026-07-09T17:09:10-04:00

**Scope reviewed:** `git status --short --branch --untracked-files=all`, latest git log, remote branch tip via `git ls-remote`, current Codex ledger tail, search for raw pytest/ruff/review output, report directory scan for Phase-2 test/review artifacts, and recursive listing of `_bmad-output/implementation-artifacts/evidence/phase2-evolutionary-bridge-20260709T204500/`. No tests were run by this monitor poll. No production/test/runtime files were edited by this monitor; this ledger entry is the only write.

**Current repo state:** unchanged from SOP-004. Local `HEAD` remains `1f48fbf6` (`docs: close S8 books and bank Irene-literal liveproof`) and `origin/dev/lesson-planning-2026-07-09` still points at `6783b54b`. The branch remains ahead of origin by one, and the Phase-2 bridge implementation/story/evidence/monitor artifacts remain untracked. Modified tracked docs remain `_bmad-output/planning-artifacts/deferred-inventory.md`, `docs/STATE-OF-THE-APP.md`, `docs/project-context.md`, plus the old Irene-literal monitor ledger transition.

**Evidence state:** no new W5 compose, trial-start, SPOC transcript, raw test transcript, ruff transcript, or standalone bmad-code-review artifact appeared. The evidence bundle still supports the W1-W4 scoped bridge: HAI/PHS thin assessments, Tejal rich assessment, wait vs lighter-collateral same-thin-fixture ratifications, W4 selection delta, and PARTIAL-MET claim assessment.

**Minor hygiene caveat:** the evidence bundle still contains the older superseded `w3-thin-ratification/` directory from the pre-remediation shape alongside the corrected `w3-thin-ratification-wait/` and `w3-thin-ratification-lighter/` directories. The summary/assessment now point to the corrected pair, so this is not blocking if left as provenance, but close should avoid citing the obsolete single-ratification path as W4 evidence.

**F-P2-0002 remains mostly resolved for W1-W4 only.** No production-path proof has appeared.

**F-P2-0006 remains dispositioned only under PARTIAL-MET wording.** W5 remains unclaimed/fenced.

**F-P2-0007 remains partly open.** The only visible test evidence remains the compact Claude ledger claim of 16 focused tests; no raw pytest/ruff output is banked.

**F-P2-0008 remains open but fenced.** Interactive pre-start SPOC planning and compose liveproof are not present.

**F-P2-0011 remains open.** Evidence and banking script remain untracked.

**F-P2-0012 remains open.** No standalone bmad-code-review record or raw review transcript appeared.

**F-P2-0013 remains open.** State docs advertise PARTIAL-MET while the implementation/evidence remains uncommitted.

**F-P2-0014 [P3] Obsolete pre-remediation W3 artifact remains inside the evidence bundle.** If the evidence bundle is committed as-is, mark `w3-thin-ratification/` as superseded or remove it before banking to reduce ambiguity.

**Scoreability:** unchanged from SOP-004. Scoreable locally as an uncommitted W1-W4 planning-to-selection bridge PARTIAL-MET, not as final Phase-2 completion or composed production. Not durable until committed/pushed.

**Verdict: NO MATERIAL CHANGE / STILL LOCAL PARTIAL-MET ONLY.** The right next step remains banking the Phase-2 close set and either adding raw test/review evidence or explicitly declaring the compact Claude ledger as the accepted evidence source.
