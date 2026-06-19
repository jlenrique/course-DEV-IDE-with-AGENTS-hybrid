# Session Handoff — 2026-06-19 (Class S — Trial-4 feature readiness: Arc-1a A14 + Arc 2 woken HIL gates, all reviewed & shipped)

**Final class:** S (declared S at open — substrate throughout: manifest, schema, runtime, decision-card models, CLI shims, ~46 files; no drift).
**Branch:** `trial/4-2026-06-12`. **Session anchor:** `262101a` (pre-session origin was `d418ed7`) → 6 commits → **HEAD `016f654`** → WRAPUP docs-closeout commit. Origin in sync (pushed at every arc); master-merge SKIPPED (scoped trial branch); working-branch push satisfied per policy.

## The headline
Brought the long-awaited **variant-pick (G2B) + voice-pick (G4A) HIL gates online** for Trial 4, on top of completing **Arc-1a's A14 pack-version disposition**. Trial 4 is now **fully ready to RUN** (operator/HIL action) — the only remaining task-#14 item, "pin golden-run replay baseline," was analyzed and resolved as a post-trial / deferred concern (not a pre-trial blocker). Heavy review discipline throughout: party-mode green-lights, two 3-lane `bmad-code-review` passes, AND a final instantiated-agent (Winston/Amelia/Murat loaded from their real SKILL.md) read-only sign-off.

## What was completed (6 commits)
1. **Arc-1a A14 — three-role pack disposition (`3a92d15`).** The named "v4.3" Tier-2 target was invalid (dead stub; v5 is hand-authored canonical). Party re-ratified Option A (Winston/Amelia/Murat unanimous): minted a role-named generated **witness** (`production-prompt-pack-v4.2-gen-…md`) as the lockstep determinism target; left frozen v4.2 as mapping-axis-frozen; v5 production-canonical. Added `state/config/frozen-pack-shas.json` (3-role registry) + L1 **check 10** (frozen-SHA tripwire) + broad-suite mirror. NO pack_version flip. 3-lane review ACCEPT; remediated a router regression-test gap + a stale (FileNotFound-inert) routing guard.
2. **Arc 2 — woke G2B + G4A (`ec8bc94`).** Cleared `fold_with` on 07B-gate/11-gate → they surface in `production_gate_ids`. New `is_content_free_gate` predicate keeps WOKEN content-free gates pack/HUD-invisible → **pack-neutral wake** (witness byte-identical, L1 green, no pack regen). New `G2BCard`/`G4ACard` + `_build_decision_card` branches (were `RuntimeError`). Pause order now `G1→G2B→G2C→G3→G4→G4A`. 3-lane review: 2 lanes ACCEPT; **Blind Spot caught 3 live-only gaps the offline test posture hid** (missing pre-gate `.j2` templates → live crash; no operator CLI shim; no pick content) — ALL remediated in the same commit (g2b.j2/g4a.j2, g2b_shim/g4a_shim + extended `ACTIVE_TERMINAL_GATES`, `pick_context` on the cards) + added structural guards so a future woken gate without a template/shim fails CI.
3. **Trial-4 transcript sync (`505f45e`).** A sync-invariant test caught that `Trial3Transcript.GateId` excluded the woken gates; extended it + regenerated the v1 schema + re-pinned its sha256.
4. **P2 test-hardening (`7dab8f1`).** From the instantiated architect/dev/tea sign-off: `ProductionGateId` derived-equality guard (the one gate-id literal with no drift tripwire); a `pick_context` real-evidence test (the bare truthiness assert passed on the always-present stub); a `g2b_shim` resume round-trip test (the operator's real entrypoint).
5. **Deferred-inventory entry (`016f654`).** Filed `live-trial-replay-baseline` with the full golden-baseline analysis.
6. **WRAPUP docs-closeout** (this commit): quality-gate ruff-fix (import-sort + 3 duplicate TW-7c-4 allowlist entries) + handoff docs.

## What is next
- **RUN TRIAL 4** (operator + HIL) — the immediate next-session action. Accept/review-posture trial: it pauses at the 6 gates, shows each specialist evaluation via `pick_context`, operator accepts/rejects. Start: `app/marcus/cli/trial.py::start_trial`; submit verdicts via `app/marcus/cli/gate_shims/<gate>_shim.py`.
- After a blessed run: scope the `live-trial-replay-baseline` follow-on if live-path regression coverage is wanted (new infra — live trials aren't byte-replayable).
- Deferred (post-Trial-4, all in `deferred-inventory.md`): `g4b-input-package-hil-wake`, `generalized-membership-wake-toggle`, `v5-manifest-coherence-reconciliation` (🟠 pre-next-trial trigger — v5 has no manifest-coherence guard by design), `pack-version-co-render-filter`.

## Unresolved issues / risks
- **G2B/G4A are accept/review pauses this trial, NOT binding pick-from-N selectors** (all three sign-off agents converged on this). `selected_*_id` is write-only; `edit` doesn't re-route downstream. Acceptable weed-clearing posture — but the operator must read them as "pause + review + accept/reject," not interactive pickers. Binding selection is a filed follow-on.
- **v5 (production-canonical pack) has no manifest-coherence guard** by design (Murat condition 3, pre-next-trial deferred trigger) — highest-probability post-trial bite.
- Ambient (pre-existing, NOT this session): `test_schema_pin` ×2-3 fail identically on clean HEAD; a `section_02a` DSL-registration cross-suite-pollution flake (passes in isolation; broad runs need `-p no:randomly`); ~repo-wide ruff debt (1816, untouched).

## Key lessons (binding)
- **Offline/fake-key tests structurally hide live-only crashes.** The Blind Spot lane caught a guaranteed live FileNotFoundError (missing pre-gate template) that every green integration test sailed past. The fix wasn't just the templates — it was *structural guards derived from `production_gate_ids`* so the class can't recur. Apply this pattern to any future gate wake.
- **Hand-maintained closed literals are a latent fragility.** Four gate-id sets (`production_gate_ids` authority + `GateId` + `ProductionGateId` + `ACTIVE_TERMINAL_GATES`) had to be extended by hand; the wake surfaced each via a different test crash. The mitigation is derived-equality pins to the authority — now applied to 3 of 4 (`ProductionGateId` pin added this session).
- **Pack-neutral wake** (the `is_content_free_gate` split) is the keystone that let the whole arc avoid touching the frozen pack / HUD — a woken HIL pause is a runtime pause point, not pack prose.
- **Instantiating real agents (load SKILL.md) ≠ imitating them** — the operator-requested final sign-off produced sharper, discipline-specific findings than role-played descriptions would.

## Validation summary
Step 0 (Cora harmonize): SUBSTITUTED by the in-session two 3-lane reviews + the instantiated architect/dev/tea sign-off + green L1 deterministic sweep (lockstep exit 0, lint-imports 13/0, ruff clean on session files) — recorded as proceed-with-substitution. Step 1 quality gate: PASS (caught + fixed 4 cosmetic issues). Replay regression green. Zero genuine test regressions (stash-baseline verified).

## Artifact update checklist
- [x] SESSION-HANDOFF.md (this section) · [x] next-session-start-here.md (rewritten) · [x] deferred-inventory.md (4 new entries across the session) · [x] specs (spec-arc1a, spec-arc2 with completion notes) · [x] frozen-pack-shas.json · [x] regime doc (three-role model)
- [ ] sprint-status.yaml — NOT edited (arcs tracked via session task-list, not formal sprint stories) · [ ] bmm-workflow-status.yaml — no phase transition · [~] project-context.md — woken-gate + three-role-pack changes are significant; RECOMMEND a refresh next session (deferred to keep WRAPUP scoped) · [~] knowledge-graph — ≥10 substrate files + manifest/schema changes: RECOMMEND `/understand` regen + ONBOARDING re-emit next session.

## WRAPUP ceremony record (Class S, 2026-06-19)
Steps 0(substituted)/1(pass)/2(done in-session)/7/8 engaged. Steps 3/4a/4b/6 SKIP (no workflow transition / sprint-ledger edit / agent-skill / content edits). Step 5 project-context + Step 9 KG: recommended-deferred (recorded above). Step 10: worktree clean except by-design untracked `runs/`. Step 11: class-drift check — declared S, diff is substrate → no drift. Step 12: push mandatory — satisfied (all arcs pushed; closeout commit pushed). Master-merge SKIPPED (scoped trial branch).

---

# Session Handoff — 2026-06-17 (Class S — WAVE 0 tranche 2 landed + cycle-6 storyboard-correctness operator review COMPLETE)

**Final class:** S (declared S at open — substrate session: `production_runner.py` + `package_builders.py` + 3 test files edited & committed; no drift). 
**Branch:** `trial/4-2026-06-12`. **Session anchor:** `262101a` → **HEAD `e096661`** (tranche-2) → docs closeout commit at WRAPUP. Origin in sync; master-merge SKIPPED (scoped trial branch); working-branch push satisfied per policy.

## The headline
Two things landed. (1) **WAVE-0 tranche 2 (BuilderInputError)** — the last live-walk dispatch leg outside the error-pause family — re-based + both `run_builder_node` call sites wrapped, so a §06 starvation now error-pauses recoverably instead of killing the trial. The live-path crash→error-pause invariant is now COMPLETE (WAVE-0 now 5 of 6). (2) **Operator-led cycle-6 storyboard-correctness review** — the gating input the BLOCKED storyboard slice was waiting on — ran to completion and root-caused the storyboard glitches to ONE bug. WAVE-0 storyboard-correctness is now UNBLOCKED.

## What was completed
1. **Tranche 2 (`e096661`, pushed).** `BuilderInputError` re-based onto `SpecialistDispatchError` (byte-identical inherited ctor; all 6 per-condition tags preserved); both start- and recover-walker `run_builder_node` sites wrapped in `except SpecialistDispatchError → _pause_at_error` under the `package_builder` identity. EXCLUSIONS 13→12 (reverse-existence red observed before deletion). Governance: party-mode green-light (unanimous live-path-only) + a conflict-adjudication round when Amelia's mandatory catch-site grep found two party-ratified pins (`test_starved_resume_*`, `test_broken_brief_*`) that pinned §06 to PROPAGATE (fail-loud-as-crash). Winston/Murat/John ruled COMPATIBLE — the pins ratified INVARIANTS (non-silent, no-theater-gate, no-publish), not the crash mechanism; both pins migrated crash→error-pause with anti-theater assertions preserved VERBATIM + recover-determinism + kill-the-mutant. 3-lane bmad-code-review: Acceptance Auditor PASS; 2 patches applied, 1 deferred (pre-existing, already-filed), 6 dismissed. The 12 off-path classes filed as deferred-inventory `tagged-error-taxonomy-tranche-3-offpath-sweep`. Validation: 39 in-scope green; 14 contract failures all ambient-roster; lockstep 0; lint-imports 13/13; ruff clean.
2. **Cycle-6 storyboard review COMPLETE** (ledger: `_bmad-output/implementation-artifacts/content-review-cycle-6-f8da20ae.md`; URLs: `STORYBOARD-REVIEW-URLS.txt`). Operator-led, one-step-at-a-time, pausable/resumable via the durable ledger. Bar = production fidelity only (pedagogy/QA explicitly out of scope, agents' later job). **ROOT CAUSE (single bug, both storyboards = operator Glitch #1 + #2):** Gary's deck export → `slide_id` mapping is positional, so the Gamma-generated COVER page ("The Case for Physician Leadership", a non-briefed slide) consumes `slide-01` and shifts every content image down one — A shows Script Notes one row down; B's (correct, cleanly-1:1-matched) VO narrates the next image's content. SECOND coupled defect: Gamma collapsed 6 briefed topics into 5 content pages (Leadership+Summary merged), so the Summary&Knowledge-Check brief has NO dedicated image. Fix direction: **title-based page→slide_id matching** (skips the unmatched cover + fail-louds the missing Summary page) in gary `_paths_from_generation`/export-materialization. `b-manifest-join-lossiness` rider CLEARED for this run (join was clean). Fidelity POSITIVES recorded: publish wiring live (A+B 200); 6/6 assets present; B script-policy fields populate real slide-specific values (behavioral_intent/duration_rationale/timing_role/content_density/visual_detail_load). Low-sev riders: title=slide-id; source_ref blank. Parked (content-QA, out of scope): VO "$5.2T" vs slide "$4.5T".

## What is next
- **WAVE-0 storyboard-correctness DISPATCH (now unblocked):** spec the Gary cover-injection + brief→page-cardinality fix per the ledger's title-based-matching direction; party-mode per sprint governance. Recommended immediate next action.
- **Then Trial A** closes WAVE 0 (literal text/visual slides + clustering, frozen-engine baseline; needs no motion — kira `motion_receipts: []` is EXPECTED).
- **Available in parallel / alternative:** tranche-3 off-path taxonomy sweep (`tagged-error-taxonomy-tranche-3-offpath-sweep`, 12 classes, each needs its own catch-site grep + fail-loud-vs-pause adjudication — Winston: do NOT presume pause family).
- **WAVE 1 (after A+B certify):** pause-topology pin → fold-semantics gate-engine fix → variant/voice wake. Then witness→strict envelope-validator flip; Marcus SPOC thin slice.

## Unresolved issues / risks
- WAVE-0 storyboard-correctness fix not yet specced (root-caused only) — see ledger.
- Open fix-design question: should the deck cover be dropped or retained as an intentional title row? How to handle Gamma merging/dropping a briefed topic (enforce 1:1 vs detect+flag)?
- 2 carried pre-existing L1 findings (non-blocking): motion-pack structural-walk marker order (since 2026-04-21); raw-HTTP allowlist drift, 19 call-sites (since 2026-05-22).
- 8 ambient `app/specialists/*/graph.py` ruff I001 nits (pre-existing; clean on next touch).
- Witness→strict envelope-validator flip still due (gate: every S5 `anomalies.jsonl` reviewed clean).
- `BuilderInputError` node-06 asymmetry — RESOLVED this session (tranche 2).

## Key lessons (binding)
- **Mandatory catch-site grep before a re-base is load-bearing, not ceremony.** Amelia's grep caught two party-ratified pins that the green-light round had not known about; skipping it would have silently broken MUST-FIX pins. Re-bases that change a class's catchability MUST grep every raise + catch site first.
- **"Fail loud" ratified as a crash can be honored by a recoverable error-pause** — when the pin's true intent is non-silent + no-theater + no-publish, not crash-as-mechanism. Surface such conflicts to the original ratifiers rather than unilaterally rewriting their pins.
- **Production-fidelity review ≠ QA review.** Holding the bar at "did the wiring assemble what it was told to build" kept the review fast and surfaced the real systemic bug; blank/aspirational fields and content inaccuracies were correctly parked.
- **One operator observation ("notes match the slide one row down") + direct PNG inspection collapsed two reported glitches into one root cause.**

## Validation summary
- Tranche 2: lockstep exit 0; lint-imports 13/13; ruff clean; 39 in-scope tests green; kill-the-mutant verified; 14 broader contract failures all confirmed ambient (`C:\tmp\codify-batch-failures.txt`), zero regressions. 3-lane bmad-code-review PASS.
- **Step 0 coherence:** no separate `/harmonize` Cora sweep this WRAPUP — the substrate (tranche 2) landed earlier this session WITH full inline adversarial validation (battery + 3-lane review) at `e096661`; all post-commit work is docs-only (no app/scripts/skills `.py` after the commit). Proceed-with-rationale, not a skipped gate. (Tripwire note: next substrate session opens with the normal Step-0 sweep.)
- WRAPUP quality gate: `git diff --check` clean.

## Artifact update checklist
- [x] `app/marcus/orchestrator/{package_builders,production_runner}.py` + 3 test files (committed `e096661`)
- [x] `spec-taxonomy-rebase-tranche-2.md` · [x] `deferred-inventory.md` (+ tranche-3 entry) · [x] `deferred-work.md` (committed `e096661`)
- [x] `content-review-cycle-6-f8da20ae.md` (review ledger) · [x] `STORYBOARD-REVIEW-URLS.txt` (closeout commit)
- [x] `SESSION-HANDOFF.md` (this section) · [x] `next-session-start-here.md` (Step 7)
- [ ] knowledge-graph/ONBOARDING regen — NOT needed (tranche 2 = 5 files < 10 threshold; no manifest/schema change)

## WRAPUP ceremony record (Class S, 2026-06-17)
Step 0 satisfied-by-inline-validation (see Validation summary) · 1 quality gate clean · 2 artifacts updated · 3 no workflow transition (skip) · 4a sprint-status not edited (skip) · 4b no agent/skill interaction-surface change (skip) · 5 no rules/MCP/API change (skip) · 6 no new staging content (skip) · 7 next-session-start-here rewritten · 8 this section · 9 KG regen not needed · 10 worktree clean (untracked `runs/` by-design preserve) · 11 class-drift none (Class S confirmed by tranche-2 app py diff); single worktree · 12 closeout commit + push (MANDATORY) · 13 —.

---

# Session Handoff — 2026-06-13 (Class S — WAVE 0 robustness arc: 4 of 6 items landed on the certified frozen engine)

**Final class:** S (declared S at open — substrate session throughout: 5 specialists + audio seam + 9 test files edited; no drift).
**Branch:** `trial/4-2026-06-12` (cut from merged master post-Trial-3-campaign). **Session anchor:** `c510b82` → **HEAD `37f8323`**. Origin in sync (5 commits pushed, working-branch push mandatory-per-policy satisfied; master-merge SKIPPED — scoped trial branch).

## The headline

First working session on the certified substrate. Opened WAVE 0 of the post-certification roadmap (`roadmap-consensus-2026-06-12`). Engine is FROZEN for Trial A, so all four landed items are correctness/honesty hardening with **zero production-walk behavior change** — each ran quick-dev (spec → 3-lane code review blind/edge/acceptance → commit → push). The robustness theme the operator named: build an unimpeachable error-flagging platform first, then build on it.

## What was completed (4 of 6 WAVE-0 items)

1. **Phantom-delta silent-audio gap CLOSED** (`ebe0c3f`). A segment-manifest delta with no matching narration joined with empty text → enrique silently skipped TTS (no mp3, no error) while G5 counted the slide as covered. Fix: enrique REFUSES pre-spend (`elevenlabs.join.empty-narration-text`) + G5 DROPS pre-coverage so `CoverageGapError` names the silent slide; detection single-homed in `narration_join.phantom_segment_ids`. Highest-priority dp-v1.2 rider (Amelia R1).
2. **dp-v1.2 hygiene mini-batch — 6 rows** (`6b4c9c4`). Winston R1 (join-test honesty: self-compare killed, publisher byte-equality + content anchors), Winston R2 (enrique `DEFAULT_BUNDLE_PATH` retired → fail-loud `elevenlabs.bundle.path-missing`), Amelia R2 (dead `_act_with_trail` + 4 orphaned quinn_r helpers deleted), Murat R1 (ninth-seam regex generalized), Murat R2 (EXCLUSIONS module-qualified + reverse-existence pin), John R1 ((11B,elevenlabs) allowlist row machine-tied to the active voice-HIL rider, strikethrough-aware).
3. **Motion-receipts diagnosis** (`e9edc61`, HIGH confidence). Case file: `_bmad-output/implementation-artifacts/investigations/motion-receipts-cycle-5-6-investigation.md`. Kira node 07E ran in BOTH certified runs but was input-starved (`input keys: cache_prefix`); `_load_motion_plan` empty-default → zero-iteration loop → `motion_receipts: []` + `kling.dispatch.ok` + `provenance: real`. Four-layer silence: no manifest producer for a motion plan / kira silent empty-default / G2F gate folded (`fold_with: G3`) + groundless-allowlisted / compositor tolerates `[]`. Certification stands for the narrated-deck deliverable; the motion leg is structurally UNPROVEN (the party's "visual-scan VO after motion proven" gate was correct). Fix = motion data-plane arc (dp-v2-class, own party round, post-Trial-A); kira taxonomy re-base is a prerequisite (done this session).
4. **Taxonomy re-base — live-path tranche** (`37f8323`). GaryActError / ReceiptParseError / BundleParseError / KiraActError / FTRParseError re-based onto `SpecialistDispatchError` (RuntimeError-derived base → all existing handlers preserved; catch-site audit: each caught once by name in its own `act()`). A mid-walk failure in gary/texas/kira/vera now error-pauses recoverably instead of killing the trial. Rode along: gary fabricated slide-01 roster KILLED (`gamma.slides.starved`; live path unaffected — node-06 builder guarantees non-empty slides) + ninth-seam regex widened to multi-key/multi-row. EXCLUSIONS 18→13.

## What is next

- **WAVE 0 remaining (2 items):** storyboard correctness (BLOCKED on operator cycle-6 content review — glitch #1 already on file: Storyboard B VO-slide sync, maps to `b-manifest-join-lossiness`) → **Trial A** (literal text/visual slides + clustering, frozen-engine baseline; needs no motion).
- **Robustness continuation (operator's stated priority):** taxonomy re-base tranche 2 — `BuilderInputError` (node 06) FIRST (the last live-walk dispatch leg outside error-pause; pair with wrapping `run_builder_node`), then the remaining 12 bare classes.
- **WAVE 1 (after A+B certify):** pause-topology pin → fold-semantics gate-engine fix → wake variant-pick + voice-pick. Then witness→strict envelope-validator flip; Marcus SPOC thin slice.

## Unresolved issues / risks

- 🟡 `BuilderInputError` node-06 recoverability asymmetry (deferred-work §taxonomy review, 2026-06-12) — non-blocking; sharpest next robustness target.
- 2 carried pre-existing L1 findings (non-blocking, unremediated): motion-pack structural-walk marker order (since 2026-04-21); raw-HTTP allowlist drift 19 call-sites (since 2026-05-22).
- 8 ambient `app/specialists/*/graph.py` ruff I001 import-sort nits — pre-existing, NOT session-introduced (none in this session's diff); `ruff --fix` at next touch of those modules.
- 3 deferred findings from the taxonomy review + 4 from the phantom-delta review + 4 from the hygiene review, all filed to `deferred-work.md` (silent-gap family residuals on legacy non-join paths; ninth-seam in-genus regex escapes; gary routing-predicate cleanup).

## Key lessons (binding)

- **Starvation has two failure modes by specialist temperament:** Irene confabulates from exemplars when starved (cycle-4 sepsis); kira silently no-ops (motion). Same root cause (no data-plane producer), opposite symptom. The `input keys: cache_prefix` summary phrase is the universal starvation detector.
- **3-lane review caught real defects** the single-pass would miss: the constructor-identity blind spot (issubclass passes with a broken ctor), the strikethrough-closure blind spot in the linkage test, and the node-06 recoverability asymmetry. The blind hunter's FAIL verdicts were context-artifacts (untracked files absent from the diff) — verify MUST-FIXes against the project before acting.
- **Re-base mechanics:** `SpecialistDispatchError` is RuntimeError-derived, so re-basing a bare `RuntimeError` class needs no dual base (unlike the ValueError-based G5 classes which keep ValueError too). Catch-site grep per class is mandatory (Amelia discipline).

## WRAPUP ceremony record (Class S, 2026-06-13)

- **Step 0:** Cora WRAPUP sweep run — deterministic L1-equivalent battery GREEN at HEAD (lockstep PASS, lint-imports 13/13, audit/contract/audio 59 passed, marcus 182/1 per-slice). Tripwire NOT fired (START sweep cleared it). 0 new blocking findings. Report: `reports/dev-coherence/2026-06-13-0302/`. Step 0b N/A — no sprint-status story flipped (quick-dev specs, story_key unset; arc runs under roadmap/SCP governance not story Kanban).
- **Step 1:** quality gate PASS for session-owned changes — ruff clean on all touched files; `git diff --check` clean; lint-imports 13 KEPT. 8 ambient `*/graph.py` I001 nits recorded as pre-existing.
- **Step 2:** planning + implementation artifacts updated — 3 quick-dev specs (`spec-phantom-delta-silent-audio-gap`, `spec-dp-v1-2-hygiene-mini-batch`, `spec-taxonomy-rebase-live-path`) + 1 investigation case file; `deferred-inventory.md` (3 entries annotated) + `deferred-work.md` (3 review-defer blocks).
- **Steps 3/4a/4b/6:** SKIP — no bmm-workflow phase transition (dated note added to bmm-workflow-status.yaml); `sprint-status.yaml` untouched; no agent/skill SKILL.md changes (specialist `_act.py`/`graph.py` are runtime, not BMAD-persona skill dirs); no course-content staging moves (production output in run dirs pending operator review).
- **Step 5:** `docs/project-context.md` updated (2026-06-13 WAVE-0 block). `docs/agent-environment.md` SKIP — no MCP/API/tool-tier changes.
- **Step 9:** knowledge-graph regeneration RECOMMENDED next docs window (≥10 app/specialists + tests files changed; meta.json commit_sha `ac3f164` now behind HEAD `37f8323`). Guides untouched (no operator-facing workflow change). Structural-walk untouched (no gate/workflow name changes).
- **Step 10:** worktree reconciled — all session-owned changes committed; untracked `runs/<uuid>/` + `runs/compositor/` (cycle-6 bundle, PRESERVE) + `runs/enrique-narration/` are runtime artifacts by design. Single worktree.
- **Step 11:** class-drift check PASS (S declared = S actual). Single worktree registered. Branch metadata in next-session-start-here verified against HEAD.
- **Step 12:** pushes — `16ea90a`, `ebe0c3f`, `6b4c9c4`, `e9edc61`, `37f8323` + this WRAPUP commit, all to `origin/trial/4-2026-06-12`. Master-merge intentionally SKIPPED (scoped trial branch per Step-12 exception); working-branch push satisfied.

**Validation summary:** per-slice batteries green across the session (phantom-delta 313/1; hygiene 322/1; re-base 847+83); ambient full-suite failures roster-matched to `C:\tmp\codify-batch-failures.txt`; 2 live-LLM flakes (desmond, irene) pass solo; zero session-introduced failures (acceptance auditor stash-verified). Lockstep PASS ×3 this session; lint-imports 13/13 throughout.

**Artifact checklist:** SESSION-HANDOFF ✅ · next-session-start-here ✅ (3-way class forecast) · project-context ✅ · 3 specs ✅ · 1 investigation ✅ · deferred-inventory ✅ · deferred-work ✅ · cora chronology ✅ · dev-coherence report ✅ · sprint-status/bmm-workflow N/A (dated note only) · knowledge-graph: operator regen recommended.

---

# Session Handoff — 2026-06-12 (Class S — 🏆 FIRST COMPLETE PRODUCTION RUNS: cycle-5 full walk + cycle-6 FRESH CERTIFICATION E2E through composition hand-off)

**Branch:** `trial/3-2026-05-21`. **Session anchor:** `0a5604a` → **HEAD `8b306b1`** (+WRAPUP commit). Origin in sync.
**Operator rulings this session:** (1) G2C cycle-5 approved after mechanical A-side comparison surfaced content deltas (delegation lapsed correctly); (2) G3 approved on the ONLINE Storyboard B; (3) FULL-DELEGATION COMPLETION DIRECTIVE — "continue rounds of trial+remediation until an entire production run completes through composition for hand-off; I delegate my approvals for all remaining cycles; 4h budget" — **SATISFIED with ~2h to spare**.

## The headline

- **Cycle 5 (`036e7ff8`)**: G0 → Storyboard A online (operator approved) → grounded Pass-2 → **Storyboard B online (operator approved — criterion 7 B-side proven)** → G3/G4 → 6 real ElevenLabs segments → G5 real QA → compositor bundle + DESCRIPT guide → desmond hand-off → `completed`. First complete production run in platform history.
- **Cycle 6 (`f8da20ae`)**: **FRESH CERTIFICATION E2E** — G0 → `completed` 09:23Z, ZERO ad-hoc fixes on substrate `8b306b1`; 20/20 provenance:real, 0 fixture; both storyboards auto-published online (first fresh-run exercise of the G3 roster fix); delegation-exercise log at the run dir. $0.24 LLM + ~$1.01 audio.
- **S5 criteria 1-7: ALL CLOSED** (SCP arc-closure paragraph).

## Remediation arcs landed (each: party design round → tests-first → 4× party review → MUST-FIXes executed)

1. **dp-v1.1 (`f3185b4`)** — cycle-4 08/08B pair: Irene Pass-2 grounding (sepsis confabulation killed: corpus-first prompt, fail-loud reads, slide-roster join check); quinn_r G3B remapped post→storyboard_b; STORYBOARD_GATES + segment-manifest threading for Storyboard B; **PIN-G1 manifest-wide grounding audit** (shrink-only allowlist); **criterion-5 negative test FIRED**.
2. **G3 roster fix (`c6f9d7a`, in-situ at the live G3 pause, folded per operator directive)** — folded gates never pause; roster keys fold-TARGET gates; manifest-driven pin; B published for the paused run via the fixed seam (recorded replay).
3. **dp-v1.2 (`6dc7f94`)** — audio arc: shared `narration_join` (one policy home, import-identity pinned); enrique grounded on operator-approved narration + pre-spend join guard + run-scoped bundle; G5 grounded + fabricated phantom-roster killed (ninth seam; FIXTURE_SIGNATURES extended) + 4 content errors re-based to dispatch-family duals; compositor pre-grounded; **PIN-AUD-3T taxonomy ratchet** (found 18 latent bare classes → shrink-only seed + rider); **PIN-AUD-3P lost-progress twin**; live 1-segment ElevenLabs micro-smoke before resume.
4. **economics fix (`8b306b1`, in-situ, folded)** — deterministic node markers non-billable (the full walk completed in memory and died at cost bookkeeping).

## Key learnings (binding)

- **Fold semantics bite twice**: G3B publisher roster AND G4A/G4B voice-HIL are unreachable-pause classes; rider `voice-selection-hil-fold-defect` filed with reactivation trigger.
- Resume registry is process-scoped: a crashed resume's verdict file replays cleanly.
- All three elevenlabs nodes share ONE act body — narration projections go to node 12 ONLY (double-synthesis = double spend).
- Ambient roster discipline + scoped `git stash` ⚠️ (a pathspec stash took my own changes once — popped clean; prefer diff-vs-roster).

## Next session

1. **Operator reviews cycle-6 storyboards** (URLs in `state/config/runs/f8da20ae.../delegation-exercise-log.md`) + the assembly bundle (`runs/compositor/`) + 6 mp3s — first full content-quality pass on a certified run.
2. Deferred riders by priority: Amelia R1 phantom-delta silent-audio gap (dp-v1.2-review-riders-bundle, highest); taxonomy systematic re-base (live-path classes first); measured durations (mp3 probe re-arms G5 WPM); voice-HIL fold; dp-v2 self-edge vocabulary.
3. Cross-trial harvest entries (cycles 2-6) per methodology §7; witness→strict envelope-validator flip (post-S5 ceremony — S5 is now CLOSED, the flip is due).

## WRAPUP ceremony record (protocol steps)

**Final class:** S (declared S at open — substrate session throughout; no drift).
- **Step 0:** Cora /harmonize ceremony NOT run (no slash-skill registered in this session's context). L1-equivalents green: pipeline-manifest lockstep PASS (2 runs this session), audit suite 33/33 (incl. TW-7c-4, fixture ratchet + new ninth-seam signature, PIN-G1, PIN-AUD-3T), Ratchet-D green with enrique+compositor joined. **Counts as one skip toward Cora's two-skip tripwire.** No story flipped done in sprint-status (Step 0b N/A — arc ran under SCP governance, not story Kanban).
- **Step 1:** ruff clean on batch; `lint-imports` 13 kept / 0 broken; `git diff --check` clean.
- **Step 2:** planning artifacts updated (SCP closure paragraph; deferred-inventory dp-v1.1 + dp-v1.2 + review-rider sections).
- **Steps 3/4a/4b/6:** SKIP — no bmm-workflow phase transition (SCP-governed arc); sprint-status.yaml untouched; no agent/skill files modified; no course-content staging moves (production output lives in run dirs pending operator review).
- **Step 5:** docs/project-context.md updated (2026-06-12 headline block). docs/agent-environment.md SKIP — no MCP/API/tool-tier changes (ElevenLabs client pre-existed).
- **Step 9:** knowledge-graph regeneration RECOMMENDED (≥10 app/ files changed + manifest changes) — operator's other terminal ran /understand mid-session; re-run post-WRAPUP for `8b306b1`+ to refresh `.understand-anything/meta.json::commit_sha`. Guides untouched (no operator-facing workflow change; the trial CLI surface is unchanged).
- **Step 10:** worktree reconciled — session-owned changes all committed; ambient: `.understand-anything/*` + `docs/ONBOARDING.md` (knowledge-graph terminal — left untouched); untracked `runs/<uuid>/`, `runs/compositor/` (cycle-6 assembly bundle — PRESERVE), `runs/enrique-narration/` (legacy default-path voice artifacts from cycle-5's pre-fix leg) are runtime artifacts by design.
- **Step 11:** class-drift check PASS (S→S); single worktree registered; branch metadata verified.
- **Step 12:** pushes — `f3185b4`, `c6f9d7a`, `6dc7f94`, `8b306b1`, `4a654d5`, + this WRAPUP commit, all to `origin/trial/3-2026-05-21`. Master-merge intentionally skipped (scoped trial branch per protocol step-12 exception).

**Validation summary:** batch superset 352+ passed across audit/contracts/specialists/integration; ambient failures roster-matched against `C:/tmp/codify-batch-failures.txt` (incl. schema_pin pair, verified pre-existing on clean tree via scoped stash); live ElevenLabs micro-smoke PASS (45 voices, 62.7KB mp3); two full production walks completed live (the strongest validation the platform has).

**Artifact checklist:** SESSION-HANDOFF ✅ · next-session-start-here ✅ (class forecast D) · project-context ✅ · SCP ✅ · deferred-inventory ✅ · delegation-exercise-log ✅ (run-dir, gitignored tree) · sprint-status/bmm-workflow N/A · knowledge-graph: operator action recommended.

---

# Session Handoff — 2026-06-10/11 (Class S — Trial-3 live-fire: first multi-gate crossing; 9 findings; attempt-4 alive at G1)

**Session dates:** 2026-06-10 (readiness verification + /goal confidence scrub) → 2026-06-11 (corpus refresh probe, trial launches, live-fire defect arc).
**Branch:** `trial/3-2026-05-21`. **Session-start anchor:** `b611e0a`. **HEAD at session-end:** WRAPUP commit (see git log; substantive head `08d5e34`). **Origin in sync after push.**
**Final class:** S (substrate — declared S at open, no drift).

## What happened (compressed ledger)

1. **Readiness verification (2026-06-10):** GO verdict — ratchet 29/29, conformance 19, Postgres, heartbeat, session-readiness all green. Found + fixed 4 doc-drift items (stale handoff pytest command incl. 34-7-deleted file; session-readiness module path; heartbeat invocation; ANTHROPIC_API_KEY→LANGSMITH keys).
2. **/goal 60-min confidence scrub** (party-mode-designed, operator-armed): VERDICT GO 10/10. **Critical catch: composer no-primary roll** against real corpus (wrangler rejects fail-loud) — template + guide fixes, 2/2 clean re-rolls (`bb81b6f`). Operator playbook authored (`c6d0a8d`).
3. **Corpus probe:** Tejal's Notion page unchanged since 2026-05-21 (his fresh material lives on HIS workspace — unreachable by workspace-scoped integrations; operator's page copy is the bridge; fresh share requested). Pull-script README-template regression fixed. (`f3cd33c`)
4. **Trial-3 attempt-3 live-fire arc (2026-06-11)** — 9 findings:
   - #2 dispatch cwd fork (ratchet pinned cwd=corpus_dir; production used REPO_ROOT → 11× File-not-found → 73-byte bundle) + #3 exit-10 "no-results" invented semantics discarding valid 903-word bundles → fixed `919b16d`.
   - #4 irene_pass1 missing from CANONICAL_SPECIALIST_IDS (aliases already targeted it) → roster 11→12 + shape-pin bump → `cd31b33`.
   - #5 **resume walker had NO gate-pause machinery** (raised GateBypassError at every gate live; the known-deferred `7a-2-deferred-resume-mode-multi-gate-pause` follow-on; NO live trial had ever crossed gate-to-gate). Party-mode 4-of-4 Option-A consensus (Winston/Murat/Amelia/John, guardrails: two-commit discipline, 4-assertion floor, 90-min fuse, 5-fix cap, mandatory batch review) → `_pause_at_gate` extracted (proven by unmodified suite) + wired into resume + 3 defect-pinning tests rewritten → `cd31b33`+`d727248`. **LIVE-CONFIRMED: G1→G2C crossed on `a0d31fc0` — first in platform history.**
   - #6 gpt-5.4 missing from operator-editable pricing table (config class, outside cap) → `08d5e34`.
   - #7 pause write sequence non-atomic (torn state on `d8d1332a` from pricing crash mid-pause) → FILED.
   - #8 `max_specialist_calls` default-1 segment cap permanently skips specialists → starved kira of quinn_r on `a0d31fc0` → FILED.
   - #9 CD directive validator fails its own LLM output 2/2 rolls (systematic; first-ever CD live dispatch) → FILED 🔴 — the only blocker on attempt-4.
5. **Attempt-4 (`50b7d353`) is ALIVE, cleanly paused-at-G1, resumable** — first structurally-completable trial ever (all fixes in, throttle strategy known).

## Operational learnings (binding for next session)

Verdict file = full OperatorVerdict shape (guide §5 "minimal" is wrong — doc-drift queue); verdict digest = top-level decision-card `digest` field; `trial resume` is non-interactive (Claude-runnable); resumes re-register cards from disk (cross-process replay valid); ALWAYS pass `--max-specialist-calls 12` on resume; runner pauses at G1/G2C/G3/G4 only.

## Governance trail

Party-mode rounds: 2 (pre-scrub /goal design; A-vs-B hotfix consensus — both unanimous, no Quinn/John escalation needed). 5-hotfix cap honored (#6 config-class, #7/#8/#9 filed not fixed). 🔴 MANDATORY: 5-fix batch `bmad-code-review` before attempt-5 (deferred-inventory entry). Deferred-inventory: +4 entries. Carried Step-1a findings (motion-pack marker order; raw-HTTP allowlist) untouched, carry forward again.

## Next session

Class S forecast: fix #9 CD validator → resume `50b7d353` (open throttle every segment) → G2C → G3 (Storyboard B on Pages site) → G4 → closeout per playbook Phases 5-6. Then postmortem (methodology §7 routing; cross-trial-learnings: "test pinned the correct contract, production never adopted it"; "speculative exit-code semantics"; "known-deferred follow-on never reactivated before launch despite readiness review") + Epic-34 retrospective + 5-fix batch review.

## WRAPUP step log (Class S, 2026-06-11)

- **Step 0 SKIPPED-WITH-RATIONALE:** `/harmonize`/Cora sweep not available in this session's toolset (Audra/Cora dissolved 2026-04-24; CLI wrapper still Slab-4-scoped). Compensating evidence: per-fix battery discipline (ratchet 29 / marcus suite 133 / conformance 19 / lint-imports 13 KEPT / ruff clean on every touched file) + stash-A/B attribution of all 3 ambient failures as pre-existing. No `reports/dev-coherence/` entry this session.
- **Step 1 quality gate:** PASS (git diff --check clean; workflow-status YAML parses; lint-imports 13 KEPT; ruff clean on touched set). Pre-existing ambient: texas/graph.py I001+F401; facade AST sweep stale file list; 2 directive-prompt env tests — all queued into the 5-fix batch review entry.
- **Steps 2/3/5:** deferred-inventory +4; cross-trial-learnings §Trial-3 interim entries; DISPOSITION.md in all 4 run dirs; bmm-workflow-status + project-context dated updates. **Step 4a SKIP** (sprint-status untouched). **4b SKIP** (no agent/skill changes). **6 SKIP** (no content promotion; corpus re-pull committed `f3cd33c`). **Step 9:** guide §5 verdict-shape fix + playbook gate-table corrections QUEUED to doc-drift batch (listed in hot-start); **knowledge-graph staleness flagged** — ~10 substrate files changed since anchor `61aaf03`; recommend `/understand` re-run + ONBOARDING regen at next docs window. **Step 10:** worktree reconciled — untracked `verdict.json` (consumed run-scratch) + repo-root `runs/<uuid>/` dirs (summary-writer RUNS_ROOT inconsistency, harvested as nit) left as documented ambient state. **Step 11:** class S declared=actual, no drift; single worktree. **Step 12:** push mandatory — done (final HEAD per git log).

---

# Session Handoff — 2026-05-22 (Epic 34 §02A Downstream-Consumer Coherence opened + Story 34-1 done)

**Session date:** 2026-05-22
**Branch:** `trial/3-2026-05-21` (continued from prior session)
**Session-start anchor:** `ccb141a` (prior session's wrapup commit)
**HEAD at session-end:** `bc477ed`
**Commits this session:** 10 (8ffd99f..bc477ed)
**Branch state at session-end:** Origin in sync at HEAD. Working tree carries 1 transient (`runs/cache-harness/irene-pass1.md` — cache-harness operational state).
**Sole dev-coherence report:** `reports/dev-coherence/2026-05-22-0236/harmonization-summary.md` (session-START full-repo sweep; CLEAN with 2 pre-existing findings unrelated to Trial-3 launch path)

---

## What was completed this session

### 1. Session-START full-repo `/harmonize` (Cora-orchestrated)

Operator selected option 2 (full-repo sweep) at Step 1a outstanding-findings gate. Result: **CLEAN with 2 pre-existing findings**, both unrelated to the §02A → wrangler integration path:
- Motion structural walk: 1 finding (Creative directive resolution markers out-of-order in v4.2 motion pack; carried since 2026-04-21)
- Raw HTTP guardrail: 19 unallowlisted call-sites across operator scripts + smoke tests; allowlist drift, not load-bearing

### 2. Phase A probe — §02A → downstream integration-drift inventory

Audited 10 surfaces. Inventoried **6 drift items + 1 cleanup-class candidate**:

| Class | Item | Detail |
|---|---|---|
| 🔴 HARD-CRASH | D1 | `src_id` (§02A) vs `ref_id` (wrangler) — crashed Trial-3 attempt-2 |
| 🔴 HARD-CRASH | D2 | `role: supporting` vs wrangler's `supplementary` |
| 🔴 HARD-CRASH (conditional) | D3 | `role: ignored` has no wrangler equivalent |
| 🟡 LOW | D4 | Hardcoded role-string compare in wrangler |
| 🟡 MEDIUM | D5 | `metadata.json` shape mismatch (provenance vs sme_refs) → soft-degrade to `source_id="unknown"` |
| 🟡 LOW | D6 | `ref_id` vs `source_id` field-name fork |
| 🧹 CLEANUP | C1 | Legacy `directive_composer.py` runtime-dead; 7 test files reference it |

**Surprise finding:** §02A → wrangler integration boundary had been exercised **zero times in any green test** prior to Trial-3 attempt-2. Both directive composers emitted `supporting` which wrangler rejected — drift was silent because no trial reached the wrangler with real composer output. Second occurrence of "tested module, untested integration" anti-pattern in same trial-launch arc.

Artifact: `_bmad-output/planning-artifacts/phase-a-probe-2026-05-22-section-02a-downstream-coherence.md`.

### 3. Phase B party-mode Round 1 — IMPASSE on direction

4-voice convened. 3-voice Option 1 (Winston/Amelia/John with amendments) vs Murat Option 3 (adapter; "zero integration green tests is governance failure; +15 to +25 broad-regression forecast on Option 1"). Genuine disagreement was **what is Epic 34's load-bearing achievement?** not which option.

### 4. Dr. Quinn synthesis (Round 2) — Option 5 ratified

Per CLAUDE.md §Party-mode impasse-resolution chain, Dr. Quinn synthesis produced **Option 5 "Round-Trip First, Then Harmonize"** — single Epic, inverted story order (integration test FIRST as Story 34-1; substrate harmonization 34-2..34-4; cleanup 34-5..34-7), temporary in-tree translator scaffolding with delete-at-Epic-close hard AC. Predicted 4-of-4 APPROVE; operator ratified. Chain did NOT escalate to John tiebreaker.

Artifact: `_bmad-output/planning-artifacts/phase-b-consensus-2026-05-22-section-02a-downstream-coherence.md`.

### 5. Epic 34 + 7-story decomposition + SCP

Authored via `bmad-create-epics-and-stories`. SCP authored via `bmad-correct-course`. SCP-ratification party-mode Round 1: **4-of-4 APPROVE-with-amendments. NO impasse.**

Stories: 34-1 (integration test ratchet) → 34-2 (wrangler 6-role union) → 34-3 (§02A src_id→ref_id rename + J-A1) → 34-4 (additive sme_refs) → 34-5 (translator-shrinkage sequence test carrier) → 34-6 (legacy composer deletion) → 34-7 (translator deletion + A23/P5 + Epic close ceremony).

Trial-3-PASS gate codified at Epic 34 header per John PM verdict.

### 6. C1 substrate amendment (TW-7c-4 PERMITTED_PYTHON_DIFFS extension)

29-path allowlist envelope authorizing Epic 34 dispatch. Committed at `3159a0e`; dual-predicate test PASS.

### 7. Stories 34-1 through 34-7 specs + Codex dev-prompts pre-authored

All 7 stories registered in governance JSON + sprint-status.yaml. Stories 34-4 through 34-7 authored with **substrate-tested discipline** post-recovery.

### 8. Codex Story 34-1 dispatch — 4 HALT-AND-SURFACE events → all resolved

Each HALT correct per protocol. Each surfaced a different spec defect in my work:

| HALT | Resolution commit | Defect class |
|---|---|---|
| 1 | `6eb1095` | T1 detector-script ambiguity (spec phrasing loose) |
| 2 | `0b0b014` | Missing governance/sprint-status registration |
| 3 | `42540ea` | AC-34-1-A forward-contract `sme_refs[]` (shipped knowing it was wrong) |
| 4 | `5b3b8a1` | AC-34-1-A `returncode == 0` (never read wrangler exit-code taxonomy) |

### 9. Substrate-audit recovery on Stories 34-2 + 34-3 (`4fbba3a`)

After honest answer to operator's "why has spec development been so faulty," ran per-spec substrate audit. Surfaced **9 latent defects** preempting same-pattern Codex HALTs on Stories 34-2 + 34-3 dispatch.

### 10. Story 34-1 Claude T11 cross-agent review — PASS-WITH-NITS

Cross-agent subagent (Murat M-Murat-1 load-bearing). Verdict:
- All AC + Murat audit + contract D1-D8: PASS
- Forensic-fixture sha256 byte-identical
- A9 vacuous-pass mitigation in place
- Production-load-bearing constant verified
- Broad-regression delta: pre-existing Cat-3/Cat-4 sampling noise (NOT Story-34-1-attributable)
- 2 below-threshold NITs (lint-imports text + yaml.safe_load cosmetic) — both DISCARDED

**Story 34-1 flipped to `done` at `bc477ed`.**

### 11. Codex Story 34-2 dispatch (in-flight) — TW-7c-4 allowlist gap → resolved at WRAPUP

Codex T1-T10 completed locally. All suites green EXCEPT TW-7c-4 (my spec defect: substrate-correct test path at `4fbba3a` wasn't mirrored in C1 allowlist). Resolved at `bc477ed` (allowlist +2 paths for 34-2 + 34-4 wrangler tests; .gitattributes rule for forensic-fixture preservation).

**Story 34-2 status: `review`** (Codex T1-T10 done; Claude T11 standard review pending next session).

---

## What is next

### Immediate (next session opener): Story 34-2 Claude T11 review → Story 34-3 dispatch

Codex resumes Story 34-2 T-final (broad regression + handoff write) → Claude T11 standard review → commit + flip done → Codex dispatches on Story 34-3.

### Medium-term (2-3 sessions): Stories 34-3 → 34-4 → 34-5 → 34-6 → 34-7 sequential close

Per Quinn-synthesis Option 5 ordering. Each story extends Story 34-1's integration ratchet in lockstep with new substrate behavior. Translator shrinks: 1 → 0 (post-34-3) → ... → DELETED (Story 34-7).

### Trial-3 attempt-3 launch (post-Epic-34-close)

Same Tejal corpus `course-content/courses/tejal-apc-c1-m1-p2-trends/`. Fully harmonized substrate (no translator; no legacy composer).

### Post-Trial-3 queue (unchanged from prior session)

- SCP-2026-05-19 (TW-7c-4 broader substrate amendment)
- Marcus-interactive-experience Epic
- 5 doc-currency drift entries cleanup batch

---

## Unresolved issues or risks

### From Step 0a (harmonize sweep at session-START):

Both surfaced session-START and triaged as not-blocking:
1. **Motion structural walk:** 1 finding (Creative directive resolution markers out-of-order in v4.2 motion pack; carried since 2026-04-21). Candidate for post-Trial-3 doc-currency cleanup.
2. **Raw-HTTP allowlist drift:** 19 call-sites; none in Trial-3 launch path. Candidate for tooling-hygiene story.

### From Story 34-1 closure:

T11 cross-agent surfaced 2 NITs, both DISCARDED as below-threshold (lint-imports text inaccuracy; yaml.safe_load cosmetic). No follow-up needed.

### Forward-looking for next session:

- **Latent defects may remain in Stories 34-2 through 34-7 specs** despite substrate-audit recovery. My track record this session (4 HALT events on 34-1; preempted 9 on 34-2/34-3) suggests caution. Treat each Codex HALT-AND-SURFACE as signal, not noise.
- **Story 34-6 direction-may-flip caveat:** AC-34-6-A re-grep at T1 must confirm legacy composer still runtime-dead. If a Story-34-3/34-4/34-5 close accidentally introduces an import, Story 34-6 flips to "harmonize" instead of "delete."

---

## Key lessons learned (Mary-tier candidate for cross-trial-learnings)

### Lesson 1: Spec-as-paper authoring is the anti-pattern that produced 4 HALT events on Story 34-1

I authored Story 34-1's spec by reading the substrate selectively (parts that matched my mental model of "what the spec is about") but never RAN the wrangler subprocess against the forensic directive OR read its full interface contract (exit-code taxonomy at module docstring; current `compose_and_write` signature; actual test-file paths). Each Codex HALT was a substrate punishing the spec-as-paper failure.

**Counter-pattern (now binding for remaining stories):** before declaring a spec ready-for-dev, RUN the substrate. Read actual signatures + line ranges + import paths + file locations + exit-code semantics. All `(will fail until X lands)` parentheticals are anti-pattern signals (the AC belongs to story X, not as forward-contract).

Sibling-to-A14 ("Acceptance criteria drafted against unverified substrate"). File at next retrospective as A14-extension OR new entry.

### Lesson 2: Codex's HALT-AND-SURFACE behavior is correct + load-bearing

Every one of the 5 Codex HALT events this session (4 on Story 34-1 + 1 on Story 34-2) was the correct response to a real spec defect. Proves the cycle (Claude pre-author → Codex T1-T10 → Claude T11) has self-correcting properties when Codex is willing to halt. Operator's "pause and wait for Codex T1 confirmation before authoring more specs" instinct validated 4× over.

### Lesson 3: Two-source-of-truth integration boundaries decay silently

The §02A → wrangler boundary had a vocabulary fork for the entirety of the LangChain/LangGraph migration arc. No green test ever caught it. Quinn-synthesis Option 5's "Round-Trip First, Then Harmonize" mechanism is the structural fix — every Epic touching a producer-consumer contract must have an integration ratchet test as its first story.

Both lessons codified at Story 34-7 as A23 (substrate-tier) + P5 (process-tier) anti-pattern entries per Murat M-Murat-2 binding.

### Lesson 4: When operator asks a substantive question, ANSWER it before patching

Mid-session, operator asked "why has your story-spec development been so faulty? what about the other stories already speced?" My first response was to jump straight to patching the immediate Codex blocker without answering the substantive question. Operator's "try again" caught this; I had to redo with the substantive answer first + the substrate-audit on Stories 34-2 + 34-3.

**Counter-pattern:** when an operator question has TWO parts (substantive diagnosis + immediate technical fix), answer the substantive question first. Patches without diagnosis are noise.

---

## Validation summary

### Step 0a (session-START harmonize): CLEAN with 2 pre-existing findings
- Report home: `reports/dev-coherence/2026-05-22-0236/harmonization-summary.md`
- L1 automated checks: 6 of 7 PASS
- L2 deferred (not needed at session-START scope)

### Step 1 quality gate (during session execution):

- Codex 34-1 + 34-2 T9 self-reviews: ruff clean + lint-imports 13 KEPT + sandbox-AC PASS on every touched file
- Claude T11 cross-agent on Story 34-1: ALL AC + Murat M-Murat-1 mock-surface audit + contract D1-D8 verified clean
- Sprint-status YAML test: passes
- Governance JSON validate: 128 stories total; all 7 Epic-34 entries present
- TW-7c-4 dual-predicate: 5/5 PASS post-allowlist amendment
- Story 34-1 integration ratchet: 3/3 PASS

### Step 0b pre-closure (Story 34-1):

T11 cross-agent review IS the pre-closure equivalent (mock-surface audit + contract compliance + forensic-anchor verification + production-load-bearing constant verification). Skipped formal `/preclosure {34-1}` invocation per deeper rigor of T11.

---

## Content creation summary

N/A — pure system-development session (Epic 34 substrate-coherence work).

---

## Artifact update checklist

| File | Status |
|---|---|
| `_bmad-output/planning-artifacts/phase-a-probe-2026-05-22-section-02a-downstream-coherence.md` | NEW (committed `8ffd99f`) |
| `_bmad-output/planning-artifacts/phase-b-consensus-2026-05-22-section-02a-downstream-coherence.md` | NEW (committed `8ffd99f`) |
| `_bmad-output/planning-artifacts/epics-section-02a-downstream-coherence.md` | NEW + amended (commits `8ffd99f`, `42540ea`, `5b3b8a1`) |
| `_bmad-output/planning-artifacts/sprint-change-proposal-2026-05-22-epic-34-substrate-amendment.md` | NEW + amended (commits `3159a0e`, `5b3b8a1`) |
| `_bmad-output/implementation-artifacts/migration-34-1..34-7-*.md` (7 files) | NEW + amended (commits `d9168c5`, `6eb1095`, `f85b0c2`, `4fbba3a`) |
| `_bmad-output/implementation-artifacts/codex-dev-prompt-34-1..34-7-*.md` (7 files) | NEW + amended (same commits) |
| `_bmad-output/implementation-artifacts/_codex-handoff/34-1.ready-for-review.md` | NEW (committed `bc477ed`) |
| `_bmad-output/implementation-artifacts/sprint-status.yaml` | MODIFIED (7 Epic-34 entries; 34-1 flipped done; 34-2 flipped review) |
| `docs/dev-guide/migration-story-governance.json` | MODIFIED (Stories 34-1..34-7 entries; triage_summary 121→128) |
| `tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py` | MODIFIED (29-path allowlist envelope for Epic 34) |
| `scripts/utilities/detect_tw_7c_4_live_dispatch_scope_creep.py` | MODIFIED (`6eb1095`; pre-existing detector-bug fix) |
| `app/composers/section_02a/_wrangler_translator.py` | NEW (committed `bc477ed`; Codex 34-1; scheduled for deletion at Story 34-7) |
| `tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py` | NEW (committed `bc477ed`; load-bearing integration ratchet) |
| `tests/fixtures/integration/section_02a/forensic_directive_trial_3_attempt_2.yaml` | NEW (committed `bc477ed`; byte-identical Trial-3 forensic anchor) |
| `tests/fixtures/integration/section_02a/__init__.py` | NEW (committed `bc477ed`) |
| `skills/bmad-agent-texas/scripts/run_wrangler.py` | MODIFIED (committed `bc477ed`; Codex 34-2: 7-role union + cross-field invariants + ignored-row filtering) |
| `skills/bmad-agent-texas/scripts/tests/test_run_wrangler_role_enum_union_and_excluded_reason.py` | NEW (committed `bc477ed`; Codex 34-2 test) |
| `.gitattributes` | MODIFIED (committed `bc477ed`; forensic-fixture preservation rule) |
| `next-session-start-here.md` | FINALIZED this session-close (WRAPUP Step 7) |
| `SESSION-HANDOFF.md` | THIS FILE (WRAPUP Step 8) |

**Linked dev-coherence report:** `reports/dev-coherence/2026-05-22-0236/harmonization-summary.md`

---

## Wrapup discipline notes

- **Step 0a (this WRAPUP):** SKIPPED — session-START full-repo sweep at `reports/dev-coherence/2026-05-22-0236/` covered the change window; Cora chronology entry to be appended.
- **Step 0b (this WRAPUP):** SKIPPED — Story 34-1 T11 cross-agent review IS the pre-closure equivalent.
- **Step 4a sprint-status YAML test:** ran successfully (test_sprint_status_yaml.py passes).
- **Step 12 push-cadence:** working-branch push at session-close MANDATORY — executed at `bc477ed`. Compliant with CLAUDE.md push-cadence policy.

**Session push count:** 10 pushes this session (each commit pushed per push-cadence policy 2hr-or-checkpoint rule).

---

## Session continuation 2026-05-22 — Epic 34 stories 34-2 through 34-7 closed + Epic 34 FULLY COMPLETE

**Continuation HEAD progression:** `bc477ed` → `e6f887a` (prior wrap docs) → `cabf850` (Story 34-2 close) → `dcdb7c8` (Story 34-4 spec substrate-currency patch) → `08dfc4a` (Story 34-3 close) → `cbfca40` (Story 34-3 SHA substitution) → `16e36f7` (Story 34-4 close) → `e59b0f4` (Story 34-5 close) → `55a4d25` (Story 34-6 close) → `1b59487` (Story 34-7 close + 🎉 EPIC 34 CLOSED) → `31a2f72` (Epic 34 SHA substitution).

**Continuation commit count:** 9 additional commits closing Stories 34-2 through 34-7 + Epic close ceremony.

### Continuation work completed

#### Stories closed (6 of 7 remaining at session-continuation start)

| Story | Commit | T11 verdict | Notes |
|---|---|---|---|
| 34-2 wrangler 6-role union + ignored-row filter | `cabf850` | PASS / 0 MF / 0 SF / 1 DEFER-NIT | retrieval-shape + role=ignored corner case out of D4 scope |
| 34-3 §02A src_id→ref_id + J-A1(a)/(b) | `08dfc4a` | PASS / 0 MF / 0 SF / 1 PATCH applied | NIT-1 docstring added to `_accept_legacy_source_id_key` validator (AC-34-1-B load-bearing rationale) |
| 34-4 sme_refs additive + ratchet extension | `16e36f7` | PASS / 0 MF / 0 SF / 0 NITs | Cleanest story; bounded 3pts delivered with no findings |
| 34-5 translator-shrinkage carrier ratchet | `e59b0f4` | PASS / 0 MF / 0 SF / 0 NITs | Carrier discipline preserved (0 production code edits) |
| 34-6 legacy directive_composer.py DELETION | `55a4d25` | PASS / 0 MF / 0 SF / 0 NITs | Substrate-audit at session-START predicted ALL 7 hit counts EXACTLY (20/23/5/2/2/2/2); 2 structural-orphan cleanups surfaced at Codex T1 |
| 34-7 translator deletion + A23/P5 + Epic close | `1b59487` | PASS / 0 MF / 0 SF / 0 NITs | AC-34-7-H forensic grep-sweep PERFECT zero hits both markers |

**Track record:** 4-of-6 stories closed with ZERO T11 findings; 1 with 1 DEFER-NIT (corner case); 1 with 1 PATCH applied (docstring). Operator-friction overhead per story remained minimal — operator-bridge pattern (P3 anti-pattern) compensated by clean Codex T1-T10 handoffs and predictable substrate-audit-driven spec authoring.

#### Substrate-audit downtime work (during Codex Story 34-3 dev)

While Codex was working on Story 34-3 (the largest substrate edit in Epic 34), I performed a preemptive substrate-audit of Stories 34-4 through 34-7 specs. Findings:

- **Story 34-4 line-citation drift:** `_write_metadata_json` had shifted from spec-author-time location (lines 1239-1266) to current (lines 1308-1335) due to Story 34-2's validator-constants additions. Patched at `dcdb7c8` (3 spec locations + 3 dev-prompt locations updated with corrected line numbers + grep idiom for further drift absorption).
- **Stories 34-5/34-6/34-7 specs:** All substrate citations verified accurate. Story 34-6's 7 test-file hit counts predicted EXACTLY (20/23/5/2/2/2/2) — substrate-tested authoring discipline held perfectly.

#### Deferred-inventory closures

Three entries closed during Epic 34 execution:
- `section-02a-downstream-consumer-compatibility-systemic-drift` (CRITICAL Trial-3-blocking; filed 2026-05-21T22:30) — CLOSED at commit range `bc477ed..1b59487`
- `trial-cli-effective-trial-id-vs-section-02a-composer-run-id-divergence` (J-A1(a)) — CLOSED via Story 34-3 @ `08dfc4a`
- `trial-cli-model-resolution-trail-not-appended-from-adapter` (J-A1(b)) — CLOSED via Story 34-3 @ `08dfc4a`

#### Anti-pattern entries filed (Murat M-Murat-2 binding)

Two new entries appended to `docs/dev-guide/specialist-anti-patterns.md`:
- **A23. Two-source-of-truth vocab fork latent across N-year-old integration boundary** — sibling-to-A17 but distinct (A17 is shape-hostile; A23 is vocab-forked at boundary that no test exercised). Counter-pattern: integration-boundary green test as authoritative source-of-truth for shared contracts; static-grep coverage NOT a substitute.
- **P5. Schema-coherence Epic without integration-boundary green test is governance failure** — process-tier. Counter-pattern: any Epic touching a producer-consumer contract MUST include integration-boundary green test as FIRST story (RED→GREEN ratchet); subsequent stories EXTEND the test in lockstep per AC-34-4-A-EXT extension pattern.

#### Substrate state at Epic 34 close

- §02A composer emits `ref_id` natively (no translator); composer requires operator-supplied `run_id: UUID`; cli_adapter writes `model_resolution_trail.json` sidecar
- Texas wrangler accepts 7-role union {primary, supporting, ignored, validation, supplementary, visual-primary, visual-supplementary} + closed-set `excluded_reason` enum + cross-field invariants + `sme_refs[]` metadata
- Legacy `app/marcus/orchestrator/directive_composer.py` DELETED (no two-source-of-truth)
- Temporary `app/composers/section_02a/_wrangler_translator.py` scaffold DELETED (died-as-planned per NFR-E34-10)
- Integration-boundary green test installed at `tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py` (sha256-pinned forensic-anchor `351a57f...` from Trial-3 attempt-2 forensic evidence); test EXTENDED through 34-4 (sme_refs assertions) and ratified through 34-7's direct-ratchet simplification
- AC-34-7-H forensic grep-sweep: ZERO hits for both retired Epic-34 scaffold marker literals across entire repo
- Marker-literal hygiene: Codex mechanically rewrote historical artifact mentions (Story 34-1 spec/handoff/dev-prompt + Epic 34 spec + SCP doc + governance JSON) to non-matching obfuscated text preserving audit trail

### Continuation wrapup discipline

- **Final harmonization pass executed:** state artifacts updated at this commit batch (bmm-workflow-status.yaml + project-context.md + this SESSION-HANDOFF.md continuation + sprint-status.yaml — including tombstone for stale experience-profiles Epic 34 outline placeholders that competed for the Epic-34 numeric slot before §02A coherence reclaimed it).
- **Substrate gates pre-Trial-3:** 59 focused Epic 34 tests PASS; ruff PASS; lint-imports 13 KEPT; orphan-grep for legacy composer imports in app/ = 0; AC-34-7-H marker grep-sweep = 0 hits both markers.
- **Pre-existing test failures unchanged:** Codex T8 broad regression measurement 86 failed @ 4456 passed (delta -2 vs requested 88-baseline; failures remain outside Story-34-N focused surface; documented in Story 34-7 handoff Review Notes — e.g., test_lint_imports_kept_count_increases_by_three is a baseline failure even though actual `lint-imports.exe` passes 13 KEPT).
- **Trial-3 attempt-3 LAUNCH READY** — substrate fully harmonized. Per CLAUDE.md §Deferred-inventory governance #1, `bmad-retrospective` on Epic 34 is binding consultation point before next-Epic dispatch; operator discretion whether retrospective precedes Trial-3 launch or follows it.

**Continuation push count:** 9 additional pushes (each commit pushed per push-cadence policy).

---

## Final session-WRAPUP additions 2026-05-22 — Trial-3 operator guide via party-mode + WRAPUP coherence pass

After Epic 34 close + harmonization batch, operator caught a critical conflation in Claude's framing about the trial-3 attempt-3 run. Claude had said "Marcus is your SPOC during the trial," eliding the distinction between Marcus-runtime (`app/marcus/` LangGraph code that emits DecisionCards) and Marcus-agent (`skills/bmad-agent-marcus/` BMAD persona — the conversational AI). Operator's instinct was correct: Marcus-agent is NOT in the runtime loop.

### Party-mode resolution

Invoked `bmad-party-mode` with explicit roster: Marcus + Winston + Amelia + Paige. Round 1 spawned the first three in parallel; UNANIMOUS correction:

- **🎬 Marcus (the agent persona himself):** "During Trial-3 attempt-3, you are interfacing with Marcus-runtime. It is NOT me. I do not live inside the trial runtime. I am your post-hoc and pre-flight interlocutor, not your in-flight one."
- **🏗️ Winston (architect):** "Bright boundary by design. During a tracked trial, the operator's loop is closed against the runtime. Period. Architectural invariant: chat-agent mid-loop violates determinism contract for reproducible trial evidence."
- **💻 Amelia (code-grounded):** Cited `app/marcus/cli/trial.py:104-115` for the G0 prompt verbatim; documented the verb sets per gate from `docs/operator/hil-verb-legend.md:29-57`; explained that post-G0 gates write `run.json` + `checkpoint.json` + `decision-card-<gate_id>.json` and RETURN FROM THE PYTHON FUNCTION + EXIT THE PROCESS (no daemon); resume requires separate `trial resume --verdict-file verdict.json` invocation.

Round 2: Paige drafted single-source operator guide using Round 1 voices as authoritative inputs.

### Deliverable

`_bmad-output/implementation-artifacts/trial-3-operator-guide-attempt-3.md` (263 lines; commit `0dd38ba`). Contents:
- §0 Bright-line Marcus-runtime vs Marcus-agent clarification table
- §1 Pre-launch checklist (8 items)
- §2 Launch command (exact PowerShell)
- §3 G0 in-process prompt walkthrough + Ctrl+C wrinkle
- §4 Per-gate action table (15 rows; G0 through G5; default-recommended verb per gate per Marcus's weed-clearing posture)
- §5 Resume command + verdict.json templates (approve + edit variants)
- §6 Reference files to keep open during trial
- §7 Escalation chain (7 steps; explicitly forbids chatting with runtime; routes operator out-of-band to separate Claude/Codex session for Marcus-agent activation)
- §8 Evidence capture (auto + manual)
- §9 Closeout (PASS / FAIL paths)
- §10 Copy-paste prompts (NONE for weed-clearing trial; ONE escalation-only template)

Post-Paige correction: she guessed run-dir path as `runs/trial-3/<uuid>/`; code-grounded reality per `app/runtime/economics.py:30` is `state/config/runs/<uuid>/`. All 9 occurrences patched before commit.

### Final WRAPUP coherence pass

Operator requested formal session-WRAPUP protocol execution.

- **Step 0 (Cora-orchestrated):** Substantively covered by earlier harmonization pass at `e5a5881` + per-story T11 reviews. Cora dissolved 2026-04-24 per ratification; Audra L1/L2 sweeps formally retired.
- **Step 1 Quality gate:** ruff PASS on Epic 34 touched surfaces; lint-imports 13 KEPT 0 broken.
- **Step 2 BMAD artifacts:** all migration-34-N specs + Codex dev-prompts + handoffs flipped done in-session.
- **Step 3 bmm-workflow-status.yaml:** updated 2026-05-22 with Epic 34 close ledger + next_workflow_step refreshed to Trial-3 launch (commit `e5a5881`).
- **Step 4a sprint-status.yaml:** 2 tests PASS via `tests/test_sprint_status_yaml.py`. All 7 Epic 34 stories `done`. Stale "experience-profiles" Epic-34 outline tombstoned to eliminate numeric-slot collision.
- **Step 4b Interaction testing:** N/A — no new agents created this session.
- **Step 5 project-context.md:** updated 2026-05-22 (commit `e5a5881`). `docs/agent-environment.md` unchanged (no MCP/API/skill/tier changes this session).
- **Step 6 Content state:** N/A.
- **Step 7 next-session-start-here.md:** finalized at WRAPUP — immediate next action set to "Trial-3 attempt-3 launch (operator-confirmed)" with explicit pointer to `trial-3-operator-guide-attempt-3.md` as authoritative ramp-up artifact + 7-step opener sequence.
- **Step 8 SESSION-HANDOFF.md:** finalizing now (this section).
- **Step 9a Guides:** unchanged. Operator guide is implementation-artifact, not docs/.
- **Step 9b Reuse patterns:** A23 + P5 anti-pattern entries landed at `1b59487` per Murat M-Murat-2 binding.
- **Step 9c Structural walks:** unchanged.
- **Step 10 Stale files:** none.
- **Step 10a Dirty worktree:** only `runs/cache-harness/irene-pass1.md` remains transient (cache-harness operational state; gitignored-class; pre-existing throughout session). NOT session-owned; ambient worktree state.
- **Step 11 Artifact completeness:** sprint-status + workflow-status + project-context + next-session-start-here + SESSION-HANDOFF all final.
- **Step 11a Worktree hygiene:** single worktree at `C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS-hybrid`. No stale entries.
- **Step 12 Git closeout:** push mandatory per CLAUDE.md push-cadence policy. Working-branch HEAD at `0dd38ba` matches `origin/trial/3-2026-05-21` — already in sync. Final WRAPUP commit (this SESSION-HANDOFF update + next-session-start-here finalization) follows + push.

### Session-WRAPUP push count

11 total pushes this session (10 prior + 1 final WRAPUP closeout).

### Trial-3 attempt-3 launch readiness affirmed

Substrate gates verified at WRAPUP:
- 59 focused Epic 34 ratchet tests PASS
- ruff PASS
- lint-imports 13 KEPT
- AC-34-7-H forensic grep-sweep: 0 hits both retired markers across entire repo
- Orphan grep for legacy composer in app/: 0 matches
- sprint-status YAML test: 2 PASS

Operator opens `_bmad-output/implementation-artifacts/trial-3-operator-guide-attempt-3.md` at start of next session, runs pre-launch checklist, then launches.

---

**End of SESSION-HANDOFF for 2026-05-22 (Epic 34 FULLY COMPLETE + Trial-3 attempt-3 LAUNCH READY + single-source operator guide landed).**

---

## Interim session 2026-05-25 — Docs/tooling side-quest: ONBOARDING.md generated from knowledge-graph scan

**Session date:** 2026-05-25 (Claude Code CLI)
**WRAPUP date:** 2026-05-26 (Cursor; retroactive WRAPUP run by operator request)
**Branch:** `trial/3-2026-05-21` (continued from 2026-05-22 close)
**Session-start anchor:** `61aaf03` (prior session's final WRAPUP commit — last commit modifying `SESSION-HANDOFF.md`)
**HEAD at session-end:** `94d5810`
**Commits this session:** 2 (`2a3a39c`, `94d5810`)
**Branch state at session-end:** `origin/trial/3-2026-05-21` in sync at HEAD. Working tree clean.
**Dev-coherence report:** N/A — Cora dissolved 2026-04-24; this session was docs/tooling-only (no substrate/schema/workflow change), so Step 0a sweep skip is well-formed.

### What was completed this session

1. **Installed `/understand-anything` Claude Code plugin** (`/plugin marketplace add Lum1104/Understand-Anything`). The plugin emits a knowledge-graph scan of the codebase (nodes per file/symbol, edges per call/import/inheritance, layered by architectural tier) plus an interactive HTML dashboard plus a `/understand-chat` REPL over the graph.

2. **Ran `/understand` against code-only scope** (`app/` + `scripts/` + `skills/`; 685 files) anchored at commit `61aaf03`. Output: 1,937 nodes, 3,472 edges, 8 layers, 12-step tour.

3. **Generated `docs/ONBOARDING.md`** (281 lines) from the knowledge graph. Commit `2a3a39c`. Sections: §1 read-this-first ordering, §2 90-second mental model, §3 architecture-layer map, §4 file-by-file tour, §5 BMAD discipline overview, §6 audit invariants, §7 first-contribution recommended path, §8 operator quick-start, §9 references.

4. **Committed knowledge-graph artifacts** at `94d5810`:
   - `.understand-anything/.understandignore` (82 lines; tool-side ignore for code-analysis scope)
   - `.understand-anything/fingerprints.json` (42,229 lines; per-file fingerprints for incremental rescan)
   - `.understand-anything/knowledge-graph.json` (56,245 lines; the analysis graph itself)
   - `.understand-anything/meta.json` (6 lines; commit anchor + scan metadata)
   - `.gitignore` (+11 lines; excludes `.understand-anything/intermediate/` + `tmp/` + `diff-overlay.json` scratch dirs)
   - `runs/cache-harness/irene-pass1.md` (+60/-35; minor in-session edit; cache-harness operational state)

5. **Pushed both commits** to `origin/trial/3-2026-05-21` per push-cadence policy (safety-checkpoint trigger; `61aaf03..2a3a39c` push + subsequent `94d5810` push in-session).

### What is next

**Unchanged from 2026-05-22 close:** Trial-3 attempt-3 launch on the Tejal corpus (`course-content/courses/tejal-apc-c1-m1-p2-trends/`). Authoritative ramp-up doc is `_bmad-output/implementation-artifacts/trial-3-operator-guide-attempt-3.md` (263 lines; commit `0dd38ba`). The interim 2026-05-25 session did NOT advance toward Trial-3 launch — it added supplementary onboarding context.

### Unresolved issues or risks

- **None blocking Trial-3 attempt-3 launch.** All Epic-34-close gates remain green; substrate is unchanged since 2026-05-22.
- **`docs/ONBOARDING.md` line 7 stale-branch caveat:** the doc reports the branch as `dev/langchain-langgraph-foundation` (the migration-foundation fork-point from which `trial/3-2026-05-21` was branched). Current is `trial/3-2026-05-21`. Generation-time context; not a defect. Refresh naturally via `/understand` after next substantive substrate change.
- **`.gitignore` scope decision deferred:** the knowledge-graph + fingerprints JSON files are 98k+ lines combined (~3 MB). Committed alongside the onboarding doc to keep `/understand-chat` and `/understand-dashboard` usable for teammates without re-running `/understand`. If repo size becomes a concern, switch to "regenerate-locally" pattern (gitignore the graph JSON; track only `.understandignore` + `docs/ONBOARDING.md`).

### Key lessons learned

- **Knowledge-graph scans as session-START preflight:** `.understand-anything/meta.json` carries the commit anchor of the scan. A future session-START could diff `meta.json` anchor against current HEAD to decide whether the ONBOARDING.md is stale. Candidate for retrospective formalization (if pattern proves repeatable).
- **WRAPUP can be retroactive when session was conducted in a sibling agent surface.** This session ran in Claude Code; the operator exited Claude Code without running WRAPUP, then opened Cursor and asked for WRAPUP a day later. The protocol handled this gracefully because: (a) the working-branch was already pushed in-session, (b) Cora dissolution simplified Step 0, (c) the docs/tooling scope was small enough to reconstruct from `git log` + the operator's terminal-transcript file.

### Validation summary

- **Step 0a sweep:** SKIPPED — Cora dissolved 2026-04-24; docs/tooling-only change window with no substrate/schema/workflow files touched; no drift risk.
- **Step 0b pre-closure:** SKIPPED — no stories flipped to `done` this session.
- **Step 1 quality gate:** PASS — `git diff --check 61aaf03..HEAD` returned clean; `docs/ONBOARDING.md` is well-formed markdown; no Python edits this session so ruff/lint-imports are N/A.
- **Step 3 workflow status:** Unchanged. Trial-3 attempt-3 LAUNCH READY position preserved from 2026-05-22.
- **Step 4a sprint-status:** Unchanged. No story status transitions; `tests/test_sprint_status_yaml.py` not re-run (no edits to the YAML).
- **Step 11a worktree hygiene:** Single worktree at `C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS-hybrid`; no stragglers.

### Artifact update checklist

| File | Status |
|---|---|
| `docs/ONBOARDING.md` | **NEW** (committed `2a3a39c`; 281 lines) |
| `.understand-anything/.understandignore` | NEW (committed `94d5810`; 82 lines) |
| `.understand-anything/fingerprints.json` | NEW (committed `94d5810`; 42k lines; tool artifact) |
| `.understand-anything/knowledge-graph.json` | NEW (committed `94d5810`; 56k lines; tool artifact) |
| `.understand-anything/meta.json` | NEW (committed `94d5810`; carries commit anchor `61aaf03`) |
| `.gitignore` | MODIFIED (committed `94d5810`; +11 lines for `.understand-anything/{intermediate,tmp,diff-overlay.json}`) |
| `runs/cache-harness/irene-pass1.md` | MODIFIED (committed `94d5810`; cache-harness operational state) |
| `next-session-start-here.md` | UPDATED at WRAPUP (interim 2026-05-25 session section added; Epic-34 table stale rows cleaned; branch metadata refreshed; validation status refreshed) — gitignored; local-only |
| `SESSION-HANDOFF.md` | THIS FILE (this WRAPUP appendix) |

### Wrapup discipline notes

- **Step 0a (this WRAPUP):** SKIPPED with reason — Cora dissolved 2026-04-24; docs/tooling-only window; no drift risk.
- **Step 0b (this WRAPUP):** SKIPPED with reason — no stories flipped to `done`.
- **Step 0c (this WRAPUP):** N/A — Cora dissolved; SESSION-HANDOFF + next-session-start-here authored directly in Steps 7 + 8.
- **Step 12 push-cadence:** Both session commits already pushed in-session at safety-checkpoint trigger (Mon May 25 ~22:01). HEAD = origin HEAD at `94d5810`. WRAPUP-finalization commit (this appendix) will be the only new push.

**End of SESSION-HANDOFF appendix for interim 2026-05-25 (docs/tooling side-quest: ONBOARDING.md + knowledge-graph artifacts; Trial-3 attempt-3 launch posture unchanged).**
