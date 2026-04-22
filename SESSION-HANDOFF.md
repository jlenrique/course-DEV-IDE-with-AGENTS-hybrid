# Session Handoff — 2026-04-22 (BMAD WRAPUP: drift remediation + Sprint #1 planning locked)

**WRAPUP Session window (2026-04-22):** Continuation after context summary. Primary objectives: complete motion-walk drift remediation (Tier-1 dev-agent authority), execute full-repo L1/L2 coherence sweep with Cora + Audra, stage deferred remediation briefs for specialist routing, lock Sprint #1 composition + research-capability activation decision.

**Preceding trial session window:** 2026-04-20 21:05 → 2026-04-21 06:03 UTC.
**Branch touched:** `trial/2026-04-19` (WRAPUP), `master` (post-merge verification).
**Operator:** Juanl.

## What Was Completed This Session (2026-04-22 WRAPUP)

### Motion-walk marker drift remediation (Risk 1 closed)

Remediated 6 pre-existing pack-vs-walk-spec marker mismatches (6 findings → 0 criticals on motion workflow structural walk):
- **Pack edits** (`docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`): 6 section headings updated with semantic qualifiers + zero-padding alignment (lines 335, 406, 548, 567, 649, 701)
- **Walk-spec edits** (`state/config/structural-walk/motion.yaml`): 9 needle + sequence entries updated to match pack headings (lines 66-68, 106-107, 112-116, 144, 150, 153, 156, 159, 165)
- **Validation**: Final structural-walk runs confirm motion READY (0 criticals); standard + cluster verified no regression

**Full evidence:** `reports/dev-coherence/2026-04-22-0236/evidence/motion-walk-markers.md` (6-item drift table with pack/walk-spec comparison; remediation trace log)

### Full-repo coherence sweep (L1 deterministic + L2 agentic)

Cora (orchestrator) + Audra (validators) executed Step 0a full-scope harmonization:

**L1 deterministic findings (5 total; exit code 1):**
1. Motion-walk marker drift (6) → REMEDIATED this session
2. Parameter directory ↔ schema lockstep (5 schema-only + ~12 directory-only keys) → STAGED brief for Paige
3. Lane-matrix Coverage Checklist scope (16 of 32 skills lack `## Lane Responsibility` section) → STAGED brief for Winston
4. Handoff stale claim (Epic 33 retrospective marked "required" but already closed 2026-04-19) → FIXED in this session
5. Memory drift (user memory asserted "Both workflows READY" but motion was NEEDS REMEDIATION) → FIXED in this session

**L2 agentic gated off** (per protocol: gated on L1 motion clean; now unblocked for next sweep)

**Staged artifacts for specialist routing next session:**
- `paige-brief-parameter-lockstep.md` — Class A (5 schema-implemented keys missing from directory) + Class B (~12 directory-implemented keys missing from schema); recommends add-to-directory or decompose schema; notes Phase 3 backlog script
- `winston-brief-lane-matrix-coverage.md` — Decision gate: (a) formalize Coverage Checklist as judgment-bearing-skills-only + refine Audra L1-5 check, OR (b) require all 32 skills, OR (c) per-skill decision
- User memory `project_structural_walk_status.md` rewritten — removed stale status snapshot, added reference to live status location

**Evidence trail:** `reports/dev-coherence/2026-04-22-0236/` (trace-report.yaml + 5 evidence files + 2 briefs)

### Strategic decision lockdown (Sprint #1 + Epic 34 + research capability)

User locked three critical decisions for trial #2 onward:

1. **Research capability activation:** Full cross-validation pathway via scite.ai + Consensus with convergence_signal (no aspirational enrichment or gap-filling for trial #2)
2. **§7.1 Irene Pass 2 template placement:** MUST land in Sprint #1 (not deferred); three concrete failure modes documented in reproducibility report §7
3. **Research knob scope for trial #2:** Evidence-bolster only (single control knob; no enrichment, no gap-fill)

**Sprint #1 composition locked (~24–30 pts, 7 stories):**
- 27-2 scite.ai adapter (re-expand from ratified-stub)
- 27-2.5 Consensus adapter (re-expand from ratified-stub)
- 28-1 Tracy reshape charter (post-Round-3 consensus)
- PR-R Marcus dispatch reshaping (new, pull-request standardization)
- Irene retrieval-intake (new, Shape 3 integration)
- Evidence-bolster control surface (new, research knob wiring)
- §7.1 Irene Pass 2 template authoring (from reproducibility §7.1, HIGH priority, ~3pts)

**Epic 34 proposal (Creative-Treatment Experimentation & Profile Curation):** Scoped with 5 stories (34-1 through 34-5); Dan as curator. Deferred to future sprint post-Sprint #1.

### Handoff artifacts finalized

- `next-session-start-here.md` — updated "Immediate Next Action" to Sprint #1 prep (bmad-create-epics-and-stories, bmad-create-story, bmad-party-mode green-light sequence)
- `SESSION-HANDOFF.md` — this file (appended WRAPUP session summary)
- User memory — project_structural_walk_status.md refreshed (stale snapshot removed)

---

### Prior Session Summary (2026-04-21, Trial C1-M1-PRES-20260419B: §09 → §15 closed end-to-end; first complete Marcus-the-APP run)

## What Was Completed

### Trial production run reached pack completion condition

`C1-M1-PRES-20260419B` advanced from `§09 Gate 3 Lock` through `§15 Operator Handoff` in this session. First-ever end-to-end traversal of the v4.2 narrated-lesson-with-video-or-animation pack under Marcus-the-APP orchestration. All gate receipts written; assembly bundle finishing-ready.

| Step | Status | Receipt |
|---|---|---|
| §09 Gate 3 Lock | LOCKED | `gate3-lock-receipt.json` |
| §10 Fidelity + Quality Pre-Spend | GO | `gate10-fidelity-quality-receipt.json` |
| §11 ElevenLabs Voice Selection HIL | APPROVED | `voice-selection.json` (Christina; 2.0s buffer; override reason recorded) |
| §11B Input Package HIL | GO | dials-only amp-up overrides recorded to `voice-selection.json::voice_direction_overrides` |
| §12 ElevenLabs Synthesis | COMPLETE | 14/14 segments; 424.74s total; continuity-stitched via `previous_request_ids` |
| §13 Quinn-R Pre-Composition | PASS_WITH_ADVISORIES | `quinnr-precomposition-receipt.json` (operator GO; Option A for card-01 + slow-WPM accepted on cards 03/06/09) |
| §14 Compositor Assembly | COMPLETE | `prompt14-compositor-receipt.json`; manifest+guide sha256-pinned; Operator Decisions injected into guide |
| §14.5 Desmond Operator Brief | COMPLETE | `prompt14_5-desmond-receipt.json`; mandatory Automation Advisory present; sanctum honesty disclosure recorded |
| §15 Operator Handoff (Descript Ready) | COMPLETE | `prompt15-handoff-receipt.json`; completion_condition_check: COMPLETE |

### Reproducibility report at canonical sequelae location

[`_bmad-output/implementation-artifacts/run-reproducibility-report-c1m1-tejal-20260419b.md`](\_bmad-output/implementation-artifacts/run-reproducibility-report-c1m1-tejal-20260419b.md) — 10 sections capturing every parameter that controlled the creative approach: theme paramset `hil-2026-apc-nejal-A`, Kling v2.6 std K07-clinical-hallway-atmosphere clip (5.04s), ElevenLabs envelope-vs-effective Δ table for Christina dials-only amp-up (stability 0.5→0.25, style 0.0→0.25, emotional_variability 0.5→0.75, pace_variability 0.05→0.15), eleven_multilingual_v2 model with continuity-stitched per-segment requests, 6 fix-on-the-fly events, 8 deferred-remediation items, full reproduction runbook.

### Production-shift wrapup completed in parallel

[`_bmad-output/implementation-artifacts/shift-close-2026-04-21-c1m1-tejal-20260419b.md`](\_bmad-output/implementation-artifacts/shift-close-2026-04-21-c1m1-tejal-20260419b.md) — all 6 production-shift gates evaluated: Run Closure, Baton/Delegation, Evidence/Logging, Risk/Blocker, Next-Shift Handoff all PASS; Workspace Hygiene **controlled** (motion structural-walk 6 pre-existing pack-vs-walk-spec drift findings — Risk 1, NOT introduced this session).

### DB reconciliation

`production_runs` SQLite at `state/runtime/coordination.db`: registered + completed `C1-M1-PRES-20260419B` (status=completed); cancelled stale `C1-M1-PRES-20260415` row (had been lingering in `planning` since 2026-04-17 — was hot-start outstanding item #4). 0 open runs at wrapup.

### Three durable Irene Pass 2 authoring failures captured

Logged with concrete failure modes for the HIGH-priority deferred entry: (a) duplicate `motion_asset` + `motion_asset_path` keys on card-01, (b) `visual_file` missing on cards 02-14, (c) `motion_duration_seconds: null` on card-01 despite Motion Gate having approved the clip. All back-fillable from upstream artifacts but should be authored at Pass 2.

### One new deferred-inventory entry

Theatrical-direction synthesis (Tier 1 + Tier 2) added to `deferred-inventory.md` §Named-But-Not-Filed Follow-Ons (count: 12 → 13). Tier 1 = per-segment `voice_settings` on v2 model; Tier 2 = model swap to tag-capable model + audio-tag authoring. Triggered by operator probing whether dials-only ceiling is sufficient for category-X content.

## What Is Next

1. **Operator-led Descript assembly** of bundle `apc-c1m1-tejal-20260419b-motion` following [`DESMOND-OPERATOR-BRIEF.md`](course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260419b-motion/DESMOND-OPERATOR-BRIEF.md). Out of pack scope; honors Operator Decision A (cross-fade card-01) + B (slow-WPM accept on 03/06/09).
2. After (1), choose: (a) remediate motion structural-walk pack-vs-walk-spec drift (Risk 1; Tier-1 dev-agent path), OR (b) scope/build Irene Pass 2 authoring template before next Pass 2 trial run, OR (c) Epic 33 retrospective.

## Unresolved Issues / Blockers

1. **Motion structural-walk: 6 pre-existing pack-vs-walk-spec drift findings** (Risk 1 in shift-close). Walk-spec at `state/config/structural-walk/motion.yaml` expects markers (`## 4) Ingestion Quality Gate + Irene Packet`, `## 4.75) Creative Directive Resolution (CD)`, `## 6.2)`, `## 6.3)`, `## 7.5)`, `## 7C)`) that don't match v4.2 pack actual section titles. Per CLAUDE.md "Pipeline lockstep regime" — Tier-1 prose alignment is dev-agent authority via Cora's block-mode hook; no party-mode required. NOT a trial blocker; carried forward.
2. **L2 agentic harmonization sweep deferred this session** — gated on L1 motion clean. Rerun once drift remediated.
3. **Irene Pass 2 authoring template (HIGH)** — three concrete failure modes documented in this run's reproducibility report. Must be scoped before next Pass 2 production run. Logged in `deferred-inventory.md`.
4. **Desmond doc-cache never refreshed** — `_bmad/memory/bmad-agent-desmond/MEMORY.md` records Descript version target as **Unknown**. Brief was authored honestly with this disclosure. Next run should ground via `python skills/bmad-agent-desmond/scripts/refresh_descript_reference.py`.
5. **Stray asset (cosmetic)** — `assembly-bundle/audio/apc-c1m1-tejal-20260419b-motion-card-04.zip` is a leftover ElevenLabs alignment-zip experiment, not manifest-referenced. Operator may delete before Descript import or leave (harmless).
6. **Epic 33 retrospective** still `required` in sprint-status.yaml. Not a trial blocker.

## Key Decisions / Observations This Session

1. **Pack §15 completion-condition logic is bundle-shape verification, not subjective approval.** Receipt machine-verifies all 4 media folders + manifest sha256 + downstream-gate identity, then declares COMPLETE. Operator subjective acceptance is implicit in the §13 operator GO captured upstream — no second HIL required at §15.
2. **Compositor `validate_manifest` does NOT accept `motion_asset` (only `motion_asset_path`).** Duplicate keys cause `sync-visuals` to refuse manifest edits with "path appears N times, expected 1" error. Irene Pass 2 emitted both keys with identical values — this is one of the three documented authoring failures.
3. **Compositor `sync-visuals --repo-root` is required** when invoking from the bundle directory; defaults to CWD which is wrong for relative-path resolution.
4. **Christina (BuaKXS4Sv1Mccaw3flfU) on `eleven_multilingual_v2` produces excellent dials-only amp-up output** when running stability-low / style-up envelope per the §11B receipt. Headline parameter that controlled per-segment differentiation is `pace_variability` (0.15) which the runner reads to nudge `speed` per segment; envelope `voice_settings` are uniform across all 14 segments.
5. **Desmond's brief MUST contain a `## Automation Advisory` section** (REST/MCP/CLI/Manual format). The agent has it as an explicit must-include per `references/automation-advisory.md`. Verified `automation_advisory_section_present: true` in receipt.
6. **`production_runs` DB row reconciliation should always go through `manage_run.py`**, never hand-edit the SQLite. `manage_run.py cancel <run-id>` clears stale `planning`-state rows.

## Validation Summary

- **Step 0a harmonization:** FULL-REPO scope (tripwire fired — 3 consecutive prior skips). L1 standard walk READY; L1 motion walk NEEDS REMEDIATION (6 pre-existing findings, NOT introduced this session); sprint-status YAML test 2/2 PASS; fidelity-contract validator 9 contracts / 79 criteria / 0 errors. L2 deferred (gated on L1 motion clean). Tripwire CLEARED for next session. Report: [`reports/dev-coherence/2026-04-21-0603/harmonization-summary.md`](reports/dev-coherence/2026-04-21-0603/harmonization-summary.md).
- **Step 0b pre-closure:** SKIP — no stories flipped to `done` (trial-only session).
- **Step 1 quality gate:** N/A on code (no source code touched). Sprint-status YAML test passed 2/2; fidelity-contract validator passed 9/79/0. Bundle artifacts in gitignored `course-content/staging/`; per-receipt validators all logged in §07F-§15 receipts.
- **Trial run gates:** §09 LOCKED, §10 GO, §11/§11B APPROVED+GO, §12 COMPLETE, §13 PASS_WITH_ADVISORIES, §14/§14.5/§15 COMPLETE.
- **Production-shift wrapup:** 5/6 PASS + Workspace Hygiene **controlled** (Risk 1 documented). Close mode: **controlled**.

## Git Closeout

- **Branch:** `trial/2026-04-19` — anchor `39a014a`. No commits landed during session; all work to commit on this branch.
- **Session-owned changes** (intended for the trial-branch commit; tracked files only):
  - `M SESSION-HANDOFF.md` (this file)
  - `M next-session-start-here.md` (forward-looking; updated for §15 completion + this session-WRAPUP)
  - `M _bmad-output/implementation-artifacts/trial-run-c1m1-tejal-20260419.md` (appended §13/§14/§14.5/§15 closure entries)
  - `M _bmad-output/planning-artifacts/deferred-inventory.md` (HIGH Irene Pass 2 expanded; Tier 1+2 theatrical-direction added; count 12→13)
  - `?? _bmad-output/implementation-artifacts/run-reproducibility-report-c1m1-tejal-20260419b.md` (new — canonical sequelae artifact)
  - `?? _bmad-output/implementation-artifacts/shift-close-2026-04-21-c1m1-tejal-20260419b.md` (new — production-shift wrapup output)
  - `?? scripts/marcus_shims/run_prompt12_narration.py` + `?? scripts/marcus_shims/run_prompt13_quinnr_precomposition.py` (new — Marcus dispatch shims authored during §12 + §13)
- **Gitignored local-only updates** (NOT in commit; preserved as repo audit trail):
  - `_bmad/memory/cora-sidecar/chronology.md` + `index.md` (this wrapup's Cora SW)
  - `reports/dev-coherence/2026-04-21-0603/harmonization-summary.md` (this wrapup's Step 0a report)
  - `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260419b-motion/...` (all bundle artifacts: receipts, manifest, narration, audio, motion clip, guide, brief)
- **Carried-forward ambient state:** none. Prior session's dirty list (CLAUDE.md, docs/workflow/..., etc.) was committed in `39a014a` before this session's anchor.
- **Merge-to-master:** **NOT executed automatically.** Operator approval required per CLAUDE.md before push/merge. Trial-branch commit only on this WRAPUP. Resume state after commit: `trial/2026-04-19` @ <new-commit>.

## Artifact Update Checklist

| Artifact | Updated? | Notes |
|---|---|---|
| `course-content/staging/.../assembly-bundle/segment-manifest.yaml` | ✅ | Gitignored — sync-visuals rewrote paths; removed duplicate motion_asset key |
| `course-content/staging/.../assembly-bundle/DESCRIPT-ASSEMBLY-GUIDE.md` | ✅ | Gitignored — Operator Decisions A/B injected; sha256 `efee4a69…7417` |
| `course-content/staging/.../DESMOND-OPERATOR-BRIEF.md` | ✅ | Gitignored — Automation Advisory present; sha256 `97f20d3e…b0ef` |
| `course-content/staging/.../quinnr-precomposition-receipt.json` | ✅ | Gitignored — pass_with_advisories + operator_acceptance |
| `course-content/staging/.../prompt14-compositor-receipt.json` | ✅ | Gitignored — 3 blocker remediations documented |
| `course-content/staging/.../prompt14_5-desmond-receipt.json` | ✅ | Gitignored — Desmond sanctum state recorded honestly |
| `course-content/staging/.../prompt15-handoff-receipt.json` | ✅ | Gitignored — completion_condition_check: COMPLETE |
| `course-content/staging/.../run-report.md` | ✅ | Gitignored — §13/§14/§14.5/§15 sections added |
| `_bmad-output/implementation-artifacts/run-reproducibility-report-c1m1-tejal-20260419b.md` | ✅ | NEW — canonical sequelae location |
| `_bmad-output/implementation-artifacts/shift-close-2026-04-21-c1m1-tejal-20260419b.md` | ✅ | NEW — production-shift wrapup |
| `_bmad-output/implementation-artifacts/trial-run-c1m1-tejal-20260419.md` | ✅ | §13/§14/§14.5/§15 closure entries appended |
| `_bmad-output/planning-artifacts/deferred-inventory.md` | ✅ | Irene Pass 2 expanded; Tier 1+2 theatrical-direction added; count 12→13 |
| `state/runtime/coordination.db` | ✅ | C1-M1-PRES-20260419B registered+completed; C1-M1-PRES-20260415 cancelled |
| `next-session-start-here.md` | ✅ | Finalized in Step 7 below |
| `SESSION-HANDOFF.md` | ✅ | This file |
| `reports/dev-coherence/2026-04-21-0603/harmonization-summary.md` | ✅ | Step 0a report |
| `_bmad/memory/cora-sidecar/chronology.md` + `index.md` | ✅ | Step 0c append + active-context refresh |
| `sprint-status.yaml` | ⬜ | No sprint-story changes — trial-only session |
| `bmm-workflow-status.yaml` | ⬜ | No workflow phase change |
| `docs/project-context.md` | ⬜ | No architecture/rule change |
| `docs/agent-environment.md` | ⬜ | No tool/MCP change |
| Guides (user/admin/dev) | ⬜ | No content change |
| `state/config/structural-walk/{standard,motion}.yaml` | ⬜ | NOT updated this session — Risk 1 carried forward as unresolved |

---

# Session Handoff — 2026-04-22 (Sprint #1 Authoring + Green-Light, continuation after wrapup)

**Session window (2026-04-22):** Continuation from prior 2026-04-22 wrapup commit `8e58fdf`. Primary objective: author all 5 Sprint #1 stories and run party-mode green-light to lock Sprint #1 composition before dev work opens.

**Branch touched:** `trial/2026-04-19` (same — no new branch cut).
**Operator:** Juanl.

## What Was Completed This Session

### 1. Drift remediation (2 drift surfaces, 6 files)

Discovered during story authoring that the Sprint #1 composition inherited from prior wrapup was partially stale. Tracking artifacts diverged from ground truth:

**Drift 1: Story 27-2 done-drift.** 27-2 was BMAD-closed 2026-04-18 (`883f742` — SciteProvider 620 LOC; regression 1149/2/0/2; 15 PATCH applied), but `bmm-workflow-status.yaml` + `epic-27-texas-intake-expansion.md` + `next-session-start-here.md` still labeled it `ratified-stub / re-expand target`. Sprint-status `development_status` was the only correctly-marked surface.
- Fixed: `bmm-workflow-status.yaml` L107 `epic-27: in-progress`; L123 `27-2: done`; L165 `28-1 blocked_on: [27-2.5]`
- Fixed: `epic-27-texas-intake-expansion.md` L3 status header + L44 roster row

**Drift 2: Epic 28 reshape roster done-drift.** 4-story Tracy reshape (28-1-reshape-charter + 28-2-three-modes + 28-3-irene-tracy-bridge + 28-4-smoke-fixtures) BMAD-closed 2026-04-19, but `bmm-workflow-status.yaml` + `epic-28-tracy-detective.md` still showed the retired pre-reshape `28-1-tracy-pilot-scite-ai` + `28-2-tracy-gate-hardening` roster.
- Fixed: `bmm-workflow-status.yaml` L157 `epic-28: in-progress`; new reshape roster (L164-189) added; retired entries (L192-198) carry `superseded_by` pointers
- Fixed: `epic-28-tracy-detective.md` status header + reshape rationale + active vs retired roster separation
- Fixed: `next-session-start-here.md` Sprint #1 composition revised (removed 27-2 + 28-1-reshape-charter as "to author"; noted both as done)

### 2. Sprint #1 story authoring (5 stories, 1,520 lines)

All 5 Sprint #1 stories authored + registered `ready-for-dev` in sprint-status.yaml:

| Story | File | Lines | Depth |
|---|---|---|---|
| 27-2.5 Consensus adapter | `_bmad-output/implementation-artifacts/27-2.5-consensus-adapter.md` | 596 | FULL dev spec (mirror of 27-2) |
| PR-R Marcus dispatch reshaping | `_bmad-output/implementation-artifacts/PR-R-marcus-dispatch-reshaping.md` | 218 | Spine |
| Irene retrieval-intake | `_bmad-output/implementation-artifacts/irene-retrieval-intake.md` | 228 | Spine |
| Evidence-bolster control surface | `_bmad-output/implementation-artifacts/evidence-bolster-control-surface.md` | 243 | Spine |
| §7.1 Irene Pass 2 authoring template | `_bmad-output/implementation-artifacts/7-1-irene-pass-2-authoring-template.md` | 235 | Spine (HIGH priority, trial-#2 blocker) |

Authoring-depth rationale: 27-2.5 had direct 27-2 precedent (near-mirror), warranting full spec; the other 4 are greenfield, so spine-level per operator direction — party-mode then scoped + ratified with riders.

### 3. Party-mode green-light (4 specialists, 7 tiebreak rulings)

Convened Winston 🏗️ / Amelia 💻 / Murat 🧪 / Paige 📚 via `bmad-party-mode`. Each specialist produced independent green-light verdicts + riders. Operator adjudicated 7 direct disagreements (D1–D7) to ratify a unanimous GREEN Sprint #1:

| # | Decision | Ruling | Resolved-by |
|---|---|---|---|
| **D1** | PR-R retrofit edge count | **3 edges** (Irene Pass 2 + Kira motion + Texas minimal) | Winston |
| **D2** | PR-R registry location | **NEW `skills/bmad-agent-marcus/references/dispatch-registry.yaml`** | Amelia |
| **D3** | PR-R L1 lockstep check | **IN-SCOPE** (+1 pt) | Winston |
| **D4** | Irene intake contract doc | **NEW `skills/bmad-agent-content-creator/references/retrieval-intake-contract.md`** | Paige |
| **D5** | Evidence-bolster missing-credential | **HARD-FAIL at Marcus boot** | Winston |
| **D6** | Intake layer field name | **`evidence_bolster_active`** (`_active` suffix) | Paige |
| **D7** | PR-R sequencing | **Open LAST** (position 5) | Winston |

### 4. Green-light patches applied to all 5 story specs

`§Green-Light Patches Applied (party-mode round 1, 2026-04-22)` section added to each of the 5 story files with:
- Per-specialist verdict (GREEN after riders)
- Applied riders (20+ total across architecture / dev / test / docs)
- Pinned points + regression floors
- Dev sequence position (1–5)
- Vote record (all 4 specialists GREEN after patches)

### 5. Sprint-status.yaml + next-session-start-here.md updated with locked state

- Sprint #1 block header added to `sprint-status.yaml` documenting green-light lock, dev order, canonical naming, roster-level riders
- `next-session-start-here.md` rewritten with Sprint #1 GREEN-LIT section: dev order table, D1-D7 ruling table, canonical 3-layer naming, roster-level riders, drift remediation record, next-steps at session open

## Sprint #1 Final Locked State

**16 pts firm across 5 stories. Dev order ratified via D7:**

1. §7.1 Irene Pass 2 authoring template (3 pts, ≥12 floor) — trial-#2 BLOCKER, open FIRST
2. 27-2.5 Consensus adapter (3 pts, ≥20 floor) — parallel with §7.1; PDG-3 flake gate wired BEFORE T1
3. Evidence-bolster control surface (2 pts, ≥10 floor) — after 27-2.5 T1
4. Irene retrieval-intake (3 pts, ≥14 floor) — after evidence-bolster (consumes `evidence_bolster_active`)
5. PR-R Marcus dispatch reshaping (5 pts, ≥17 floor) — opens LAST per D7

**Cumulative regression floor: ≥1220 passed.**

**Canonical 3-layer naming (sprint-level decision):**
- Layer 1 run-constants: `evidence_bolster: bool = false`
- Layer 2 Irene intake: `evidence_bolster_active: bool`
- Layer 3 Tracy RetrievalIntent: `cross_validate: bool`

**Roster-level riders:**
1. Shared doc-parity test pattern (Murat) — pin before §7.1 / retrieval-intake / evidence-bolster open
2. Module-level constants, no `os.environ.get` at import (Amelia) — 27-2 DEFER trap guard
3. `docs/research-knobs-guide.md` as dedicated file (Paige) — 3-parameter conflation anti-vaccine
4. Fixture hygiene per story (Amelia) — `tests/fixtures/<story-id>/`
5. Flake-gate binding EXTENDED to PR-R (Murat) — 27-2.5 + PR-R both; others get local 3x-run hygiene

## Unresolved Issues / Risks Carried Forward

1. **PDG-3 CI 3x-run flake-detection gate NOT YET WIRED.** Binding blocker: must be wired + zero-flake verified on `pytest -k "cross_validate or retrieval_dispatcher"` BEFORE 27-2.5 dev-story T1 begins. Scope extended to PR-R per Murat roster rider.

2. **Shared doc-parity test pattern NOT YET PINNED.** Murat roster rider: must be designed before positions 3/4 open (evidence-bolster + irene-retrieval-intake both depend on it).

3. **Pre-existing dirty-worktree files (8 files) carried in from session start.** These were present when session opened (per Step 2b dirty-worktree fence at Session START) and not owned by this session's work. Listed below in §Dirty-Worktree Reconciliation — ambient state for next session to triage.

4. **Commit strategy deferred to wrapup.** Per operator direction mid-session, commit deferred to wrapup decision. Session-owned changes total: 10 modified + 5 new files (18 files incl. the 3 drift-remediation edits applied at session start). See §Git Closeout below.

5. **Epic 33 retrospective still flagged `required` in sprint-status.yaml.** Carried forward from prior wrapup; no action taken this session. Update at next session open.

6. **Desmond doc-cache never refreshed.** Carried forward; `_bmad/memory/bmad-agent-desmond/MEMORY.md` still records Descript version target as **Unknown**. Run `python skills/bmad-agent-desmond/scripts/refresh_descript_reference.py` before next narrated-lesson run.

## Key Lessons Learned

1. **Done-drift surface count was 2 (27-2 + Epic 28), not 1.** First drift discovered only during 27-2.5 story authoring's read of context; second discovered only while drafting 28-1 reshape charter. Future session-start protocols benefit from explicit `/harmonize` full-repo sweep before authoring, not after — finding drift mid-authoring forced two pause-remediate-resume cycles. `sprint-status.yaml::development_status` remained the trustworthy source of truth throughout; other tracking surfaces drifted against it.

2. **Authoring depth calibration works: full spec for near-mirror stories; spine spec for greenfield + party-mode ratifies scope.** 27-2.5 at 596 lines (mirror of 27-2) was correctly-sized. The 4 greenfield stories at 218-243 lines each with 8-11 open green-light questions enabled efficient party-mode ratification + rider application rather than sunk-cost spec rewriting. This is the canonical BMAD flow for novel stories.

3. **Party-mode independent subagents produced genuinely divergent expertise.** D1–D7 debates were real architectural decisions — specialists disagreed on substantive grounds (PR-R edge count, registry location, lockstep scope, intake contract doc location, missing-credential policy, naming). Solo-mode roleplay would have converged to a single authorial voice. The subagent approach earned its cost.

4. **Operator tiebreak pattern for party-mode disagreements worked cleanly.** Present each debate in simple terms + pros/cons + per-specialist positions; operator rules one at a time; orchestrator records + sequences. 7 tiebreaks in sequence took ~20 min of focused conversation.

## Validation Summary

- **Step 1 quality gate**: ✅ Ruff clean on `_bmad-output/` + `docs/` (no Python code edited this session)
- **Step 4a sprint-status regression**: ✅ `tests/test_sprint_status_yaml.py` 2 passed
- **Step 0a coherence sweep**: SKIPPED (scope narrow, session-owned only; inline verification during patching confirmed cross-file consistency across drift-remediation + green-light patches). Cora chronology append: `YYYY-MM-DD HH:MM — Step 0a skipped: scope narrow (session-owned docs only); inline verified during patch application`. Next session's 0a auto-promotes to full-repo per tripwire if operator wishes.
- **Step 0b pre-closure audit**: SKIPPED (no stories flipped to `done` this session; all 5 authored stories are `ready-for-dev`)

## Artifact Update Checklist

| Artifact | Status | Notes |
|---|---|---|
| `_bmad-output/implementation-artifacts/27-2.5-consensus-adapter.md` | ✅ NEW + green-light patches | 596 lines; full dev spec |
| `_bmad-output/implementation-artifacts/PR-R-marcus-dispatch-reshaping.md` | ✅ NEW + green-light patches | 218 lines; D1/D2/D3 applied |
| `_bmad-output/implementation-artifacts/irene-retrieval-intake.md` | ✅ NEW + green-light patches | 228 lines; D4 + riders applied |
| `_bmad-output/implementation-artifacts/evidence-bolster-control-surface.md` | ✅ NEW + green-light patches | 243 lines; D5/D6 applied |
| `_bmad-output/implementation-artifacts/7-1-irene-pass-2-authoring-template.md` | ✅ NEW + green-light patches | 235 lines; Murat fixture rider applied |
| `_bmad-output/implementation-artifacts/sprint-status.yaml` | ✅ | 5 story regs + Sprint #1 green-light block header |
| `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml` | ✅ | Epic 27 in-progress + 27-2 done + Epic 28 reshape roster + 28-1 blocked_on |
| `_bmad-output/implementation-artifacts/epic-27-texas-intake-expansion.md` | ✅ | 27-2 roster row + status header + critical path |
| `_bmad-output/implementation-artifacts/epic-28-tracy-detective.md` | ✅ | Status header + reshape rationale + active vs retired roster |
| `next-session-start-here.md` | ✅ | Finalized in Step 7 (Sprint #1 GREEN-LIT section authoritative) |
| `SESSION-HANDOFF.md` | ✅ | This section (appended to prior same-date handoff) |
| `docs/project-context.md` | ⬜ | No architecture/rule change |
| `docs/agent-environment.md` | ⬜ | No tool/MCP change |
| Guides (user/admin/dev) | ⬜ | No content change |
| `state/config/structural-walk/{standard,motion}.yaml` | ⬜ | No control-structure change |
| `reports/dev-coherence/YYYY-MM-DD-HHMM/` | ⬜ | Step 0a skipped per §Validation; skip logged |

## Dirty-Worktree Reconciliation

**Partition per Step 10a:**

### Session-owned (18 files)
- `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml` (M)
- `_bmad-output/implementation-artifacts/epic-27-texas-intake-expansion.md` (M)
- `_bmad-output/implementation-artifacts/epic-28-tracy-detective.md` (M)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (M)
- `_bmad-output/implementation-artifacts/27-2.5-consensus-adapter.md` (??)
- `_bmad-output/implementation-artifacts/7-1-irene-pass-2-authoring-template.md` (??)
- `_bmad-output/implementation-artifacts/PR-R-marcus-dispatch-reshaping.md` (??)
- `_bmad-output/implementation-artifacts/evidence-bolster-control-surface.md` (??)
- `_bmad-output/implementation-artifacts/irene-retrieval-intake.md` (??)
- `next-session-start-here.md` (M)
- `SESSION-HANDOFF.md` (M — this edit)

### Pre-existing unrelated (8 files — ambient state; NOT session-owned)
- `CLAUDE.md` (M)
- `_bmad-output/implementation-artifacts/26-6-marcus-production-readiness-capabilities.md` (M)
- `_bmad-output/implementation-artifacts/prompt-pack-v4-2-run-constants-schema-drift.md` (M)
- `docs/workflow/production-operator-card-v4.md` (M)
- `docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md` (M)
- `skills/bmad-agent-marcus/capabilities/pr-rc.md` (M)
- `state/config/narration-script-parameters.yaml` (M)
- `tests/marcus_capabilities/test_preflight_receipt_contract.py` (M)

**Discipline per protocol:** pre-existing unrelated files NOT staged into session commit. Next session inherits them as ambient state to triage.

## Git Closeout Strategy

Per operator direction mid-session, commits deferred to wrapup. Recommended closeout flow:

1. Stage session-owned files only (explicit `git add` by path — NOT `git add -A`)
2. Single session commit with clear message summarizing: drift remediation (2 surfaces, 4 files) + 5 story specs + Sprint #1 green-light + sprint-status regs + SESSION-HANDOFF
3. Hold on merge-to-master pending: (a) operator review of session commit, (b) decision on 8 pre-existing ambient files

**Exception note**: 8 pre-existing dirty-worktree files remain unrelated to session commit per Step 10a discipline. These are ambient state for next session; not merged into master via this session's commit.

## Links

- Prior session's Step 0a harmonization report: `reports/dev-coherence/2026-04-22-0236/` (still authoritative for motion-walk drift remediation; this session did not re-run)
- Sprint #1 Green-Light record: this section (§Party-mode green-light + §Green-light patches applied in each of 5 story specs)
