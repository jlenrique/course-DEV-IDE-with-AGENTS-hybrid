# Next Session Start Here

> Scope note: this file is the hot-start for the next repo session.
> **Current objective:** Trial production run `C1-M1-PRES-20260419B` reached pack completion condition (§01 → §15 closed end-to-end). First-ever end-to-end Marcus-the-APP run.
>
> **Trial branch:** `trial/2026-04-19` @ `5533145` (wrapup commit; merged into `master` @ `6fe40fd`, both pushed). Working tree clean apart from gitignored paths.
>
> **Deferred inventory status (2026-04-21):** 4 backlog epics (15, 16, 17, 18) / 4 deferred stories in active epics (20c-4, 20c-5, 20c-6, 20a-5) / **13 named-but-not-filed follow-ons** (added: theatrical-direction synthesis Tier 1 + Tier 2). See [`_bmad-output/planning-artifacts/deferred-inventory.md`](\_bmad-output/planning-artifacts/deferred-inventory.md). Binding consultation per [CLAUDE.md §Deferred inventory governance](CLAUDE.md).

## Immediate Next Action

**Wire PDG-3 CI 3x-run flake-detection gate, then open §7.1 + 27-2.5 in parallel via `bmad-dev-story`** (2026-04-23 session start).

Sprint #1 is GREEN-LIT — all 5 stories `ready-for-dev` with unanimous party-mode verdicts and riders applied. Dev order ratified. First concrete action: wire the flake-detection gate (binding PDG-3; blocks 27-2.5 T1). Second: open §7.1 (trial-#2 blocker) concurrent with 27-2.5.

Prior session-level context (Sprint #1 preparation → authoring → green-light, completed 2026-04-22):

1. **Research capability activation (locked):** Full cross-validation via scite.ai + Consensus with convergence_signal
2. **§7.1 Irene Pass 2 template placement (locked):** Lands in Sprint #1, not deferred backlog; position 1 dev order; trial-#2 blocker
3. **Research knob scope (locked):** Evidence-bolster only (no aspirational enrichment or gap-filling for trial #2)
4. **Sprint #1 composition (locked 2026-04-22 party-mode):** 5 stories, 16 pts firm, dev order + D1-D7 rulings + canonical naming recorded below

## Sprint #1 GREEN-LIT 2026-04-22 — 16 pts firm across 5 stories

### Dev Order (party-mode ratified per D7)

| Pos | Story | Pts | Floor | Open when |
|---|---|---|---|---|
| **1** | **§7.1 Irene Pass 2 authoring template** ([spec](_bmad-output/implementation-artifacts/7-1-irene-pass-2-authoring-template.md)) | 3 | ≥12 | **Trial-#2 BLOCKER — open FIRST** |
| **2** | **27-2.5 Consensus adapter** ([spec](_bmad-output/implementation-artifacts/27-2.5-consensus-adapter.md)) | 3 | ≥20 | Parallel with §7.1; **PDG-3 flake gate wired + zero-flake verified BEFORE T1** |
| **3** | **evidence-bolster control surface** ([spec](_bmad-output/implementation-artifacts/evidence-bolster-control-surface.md)) | 2 | ≥10 | After 27-2.5 T1 |
| **4** | **irene-retrieval-intake** ([spec](_bmad-output/implementation-artifacts/irene-retrieval-intake.md)) | 3 | ≥14 | After evidence-bolster (consumes `evidence_bolster_active`) |
| **5** | **PR-R Marcus dispatch reshaping** ([spec](_bmad-output/implementation-artifacts/PR-R-marcus-dispatch-reshaping.md)) | 5 | ≥17 | **Open LAST** — 3 consumers inform the generalization |

**Total: 16 pts firm. Cumulative regression floor: ≥1220 passed.**

### D1-D7 Green-Light Rulings (2026-04-22 party-mode round 1)

| # | Decision | Ruling |
|---|---|---|
| **D1** | PR-R retrofit edge count | **3 edges**: Irene Pass 2 + Kira motion + Texas (minimal confirmation); Gary/Vera/Quinn-R deferred |
| **D2** | PR-R registry location | **NEW** `skills/bmad-agent-marcus/references/dispatch-registry.yaml` (mirrors specialist-registry pattern) |
| **D3** | PR-R L1 lockstep check | **IN-SCOPE** (+1 pt; non-negotiable per CLAUDE.md pipeline lockstep regime) |
| **D4** | Irene intake contract doc | **NEW** `skills/bmad-agent-content-creator/references/retrieval-intake-contract.md` (skill-folder proximity) |
| **D5** | Evidence-bolster missing-credential | **HARD-FAIL at Marcus boot** (contract integrity > first-run friction) |
| **D6** | Intake layer field name | **`evidence_bolster_active`** (`_active` suffix for layer-2 runtime state projection) |
| **D7** | PR-R sequencing | **Open LAST** (three consumers inform the generalization) |

### Canonical 3-Layer Naming (sprint-level, authoritative for all 5 stories)

- **Layer 1 (run-constants YAML)**: `evidence_bolster: bool = false`
- **Layer 2 (Irene intake Pydantic)**: `evidence_bolster_active: bool`
- **Layer 3 (Tracy RetrievalIntent)**: `cross_validate: bool` (unchanged from 27-2)

### Roster-Level Riders

1. **Shared doc-parity test pattern** — pin shared helper before §7.1 / retrieval-intake / evidence-bolster open dev (Murat)
2. **Module-level constants, no `os.environ.get` at import** — inherits 27-2 DEFER trap guard (Amelia)
3. **Cumulative regression floor ≥1220 passed** (Murat)
4. **Fixture hygiene**: `tests/fixtures/<story-id>/`; no cross-story reference (Amelia)
5. **`docs/research-knobs-guide.md`** as dedicated file (NOT appended to operations-context.md) with 3-concept comparison table + 'what it does NOT do' anti-conflation column (Paige)
6. **Flake-gate binding EXTENDED to PR-R** (Murat); other stories get "local 3x-run before PR" hygiene

### Drift Remediation (this session, 2026-04-22)

1. **27-2 done-drift**: 27-2 BMAD-closed 2026-04-18 (SciteProvider 620 LOC; 1149/2/0/2; 15 PATCH), but `bmm-workflow-status.yaml` / `epic-27-texas-intake-expansion.md` / this file labeled it `ratified-stub`. All 4 surfaces aligned.
2. **Epic 28 done-drift**: 4-story Tracy reshape (28-1-reshape-charter + 28-2-three-modes + 28-3-irene-tracy-bridge + 28-4-smoke-fixtures) BMAD-closed 2026-04-19, but `bmm-workflow-status.yaml` + `epic-28-tracy-detective.md` showed retired pre-reshape roster. All surfaces aligned.
3. `sprint-status.yaml` `development_status` was the authoritative Kanban throughout; all other surfaces re-sync'd to match.

### Next Steps at Session Open

1. **Wire PDG-3 CI 3x-run flake-detection gate** on `pytest -k "cross_validate or retrieval_dispatcher"`; zero-flake verified BEFORE 27-2.5 dev-story T1 (binding; extends to PR-R per Murat roster rider).
2. **Open §7.1 + 27-2.5 in parallel** (positions 1 + 2) via `bmad-dev-story`. §7.1 is trial-#2 blocker.
3. **Pin shared doc-parity test pattern** before positions 3/4 open.
4. **Commit drift remediation + authored story specs + green-light patches + sprint-status updates** (DEFERRED from this session per operator at D-time; commit at session start or batch at wrapup).

**Epic 34 (Creative-Treatment Experimentation & Profile Curation) proposed for future sprint.** Scoped in this session: 5 stories (34-1 through 34-5) with Dan as curator. Deferred pending Sprint #1 completion.

## Trial Run Status — C1-M1-PRES-20260419B (FINAL)

| Step | Status | Notes |
|---|---|---|
| §01 → §08B | ✅ COMPLETE | Closed in prior sessions (storyboard B published 2026-04-20) |
| **§09 Gate 3 Lock** | ✅ LOCKED | sha256 pins on script/manifest/envelope/motion_plan |
| **§10 Fidelity + Quality** | ✅ PASS | GO; `gate10-fidelity-quality-receipt.json` |
| **§11 Voice Selection** | ✅ APPROVED | Christina (`BuaKXS4Sv1Mccaw3flfU`); 2.0s buffer; override reason recorded |
| **§11B Input Package HIL** | ✅ GO | dials-only amp-up overrides recorded |
| **§12 ElevenLabs Synthesis** | ✅ COMPLETE | 14/14 segments; 424.74s total; continuity-stitched |
| **§13 Quinn-R Pre-Composition** | ✅ PASS_WITH_ADVISORIES | Operator GO; Option A for card-01 + slow-WPM accepted on cards 03/06/09 |
| **§14 Compositor Assembly** | ✅ COMPLETE | sync-visuals + guide generated + Operator Decisions injected |
| **§14.5 Desmond Operator Brief** | ✅ COMPLETE | Automation Advisory present; sanctum honesty disclosure recorded |
| **§15 Operator Handoff** | ✅ COMPLETE | completion_condition_check: COMPLETE; gate_decision: GO |
| Operator-led Descript assembly | ⏳ READY | Out of pack scope — operator opens `DESMOND-OPERATOR-BRIEF.md` |

**Receipts (bundle root, gitignored):**
- §13: `quinnr-precomposition-receipt.json`
- §14: `prompt14-compositor-receipt.json` (manifest sha256 `8e35c387…7d04`; guide sha256 `efee4a69…7417`)
- §14.5: `prompt14_5-desmond-receipt.json` (brief sha256 `97f20d3e…b0ef`)
- §15: `prompt15-handoff-receipt.json`

**Reproducibility report:** [`_bmad-output/implementation-artifacts/run-reproducibility-report-c1m1-tejal-20260419b.md`](\_bmad-output/implementation-artifacts/run-reproducibility-report-c1m1-tejal-20260419b.md) — capture of all principal settings, parameter values, 6 fix-on-the-fly events, 8 deferred items, full reproduction runbook.

**Production-shift close record:** [`_bmad-output/implementation-artifacts/shift-close-2026-04-21-c1m1-tejal-20260419b.md`](\_bmad-output/implementation-artifacts/shift-close-2026-04-21-c1m1-tejal-20260419b.md) — close mode **controlled** (Risk 1 motion structural-walk pack-vs-walk-spec drift; 6 pre-existing findings).

## Outstanding Items (Completed This Session — See § Drift Remediation Summary Below)

1. **✅ Motion structural-walk: 6 pre-existing pack-vs-walk-spec drift findings REMEDIATED** (2026-04-22). All three structural walks (standard, motion, cluster) now READY. Edits applied to: (a) `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` (6 section-heading updates: 04A, 4.75, 6.2, 6.3, 7.5, 07C — added semantic qualifiers + adopted zero-padding), (b) `state/config/structural-walk/motion.yaml` (9 anti_drift + sequence_doc_parity needle updates matching pack). Validation: motion-walk final READY with 0 criticals. Standard/cluster verified no regression. Complete evidence in `reports/dev-coherence/2026-04-22-0236/evidence/`.

2. **✅ L2 agentic harmonization sweep completed** (2026-04-22). Full-repo drift sweep (L1 deterministic + L2 agentic) discovered 5 findings (motion-walk drift REMEDIATED, parameter lockstep Class A/B drift STAGED for Paige, lane-matrix coverage STAGED for Winston, handoff stale claim FIXED, memory drift FIXED). Trace report + 5 evidence files staged in `reports/dev-coherence/2026-04-22-0236/`. Three staged briefs (Paige + Winston + memory-update) for routing next session.

3. **Irene Pass 2 authoring template (HIGH priority)** — NOW IN SPRINT #1 scope. Three concrete failure modes from reproducibility report §7 (duplicate motion_asset key, missing visual_file on cards 02-14, null motion_duration_seconds) will be authored as Story: §7.1 Irene Template Authoring (new story, ~3pts, scoped for Sprint #1).

4. **Theatrical-direction synthesis (Tier 1 + Tier 2)** — deferred-inventory entry 12 → 13. Now in Epic 34 proposed backlog (stories 34-1 through 34-5). Decision pending user review of trial B audio output.

5. **Desmond doc-cache never refreshed** — carries forward as pre-condition check before next narrated-lesson run. `_bmad/memory/bmad-agent-desmond/MEMORY.md` still records Descript version target as **Unknown**. Run `python skills/bmad-agent-desmond/scripts/refresh_descript_reference.py` when preparing next lesson.

6. **Stray asset (cosmetic)** — `assembly-bundle/audio/apc-c1m1-tejal-20260419b-motion-card-04.zip` carries forward. Operator may delete or leave (harmless).

7. **Epic 33 retrospective** — still `required` in `sprint-status.yaml`. Action: update `sprint-status.yaml` to reflect **Epic 33 already closed (2026-04-19)** and remove "required" status; update `next-session-start-here.md` accordingly.

8. **Tripwire CLEARED for next session.** This session ran Step 0a full-repo drift sweep (motion walk remediation blocked L2 completion). L2 now unblocked (motion READY). Next `/harmonize` defaults to since-handoff scope.

9. **Carried-forward ambient state:** none. This session's WRAPUP commit completes motion-walk remediation + drift-sweep artifacts. Working tree clean apart from gitignored paths after commit.

## Drift Remediation Summary (This Session — 2026-04-22)

**Motion-walk marker drift remediation: 6 → 0 findings (COMPLETE)**

| File | Changes | Result |
|---|---|---|
| `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` | 6 section-heading updates (lines 335, 406, 548, 567, 649, 701) | Pack sections now carry semantic qualifiers; zero-padding aligned |
| `state/config/structural-walk/motion.yaml` | 9 needle/sequence entries updated (lines 66-68, 106-107, 112-116, 144, 150, 153, 156, 159, 165) | Walk-spec markers match pack headings; zero-padding convention adopted |
| Structural walk validation | All three workflows re-validated | **motion READY (0 criticals), standard READY, cluster READY** |
| Drift-sweep artifacts | Trace + 5 evidence files staged | `reports/dev-coherence/2026-04-22-0236/{trace-report.yaml, evidence/*.md, briefs}` |
| User memory refresh | project_structural_walk_status.md rewritten | Removed stale snapshot; added note: live status in `reports/structural-walk/` |

**Research capability activation locked (trial #2 planning):**
- Full cross-validation: scite.ai + Consensus with convergence_signal
- Evidence-bolster knob only (no enrichment / no gap-fill for trial #2)
- §7.1 Irene Pass 2 template lands in Sprint #1

**Sprint #1 locked: ~24–30 pts, 7 stories**
- 27-2, 27-2.5, 28-1 (retrieval + Tracy reshape)
- PR-R (Marcus dispatch), Irene retrieval-intake, evidence-bolster control (new stories)
- §7.1 Irene template (from reproducibility §7.1, HIGH priority)

## Repo State

- **`trial/2026-04-19`** @ `5533145` — pushed to origin.
- **`master`** @ `6fe40fd` — merge of `trial/2026-04-19`; pushed to origin.
- **Working tree:** clean apart from gitignored paths (sidecars, dev-coherence reports, `course-content/staging/`).
- **No new test regressions** — `tests/test_marcus_shims_importable.py` smoke test 2/2 PASS guards the two new dispatch shims.
- **Next working branch:** not pre-cut. Next session opens on `trial/2026-04-19`. Operator cuts a fresh branch from `master` when picking a repo-work direction (motion-walk drift remediation, Irene Pass 2 template, or new lesson trial).

## Startup Commands

```bash
# Verify baseline before starting
git branch --show-current          # trial/2026-04-19 (or operator-cut new branch)
git status --short                  # expect: clean apart from gitignored paths
git log --oneline -3                # expect: 5533145 trial(wrapup)... ; 6fe40fd merge ... reachable from master

# OPTIONAL: harmonization sweep (tripwire CLEARED — defaults to since-handoff scope)
# Recommend running it if intent is to start motion-walk drift remediation,
# since that touches state/config/structural-walk/motion.yaml and the v4.2 pack.
```

## Notes

- `course-content/staging/` is gitignored — all bundle artifacts live locally only, not committed to git.
- Bundle path: `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260419b-motion/`
- Desmond brief: [`DESMOND-OPERATOR-BRIEF.md`](course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260419b-motion/DESMOND-OPERATOR-BRIEF.md)
- Assembly guide: [`assembly-bundle/DESCRIPT-ASSEMBLY-GUIDE.md`](course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260419b-motion/assembly-bundle/DESCRIPT-ASSEMBLY-GUIDE.md)
- Trial run log: [`_bmad-output/implementation-artifacts/trial-run-c1m1-tejal-20260419.md`](\_bmad-output/implementation-artifacts/trial-run-c1m1-tejal-20260419.md)
- Reproducibility report: [`_bmad-output/implementation-artifacts/run-reproducibility-report-c1m1-tejal-20260419b.md`](\_bmad-output/implementation-artifacts/run-reproducibility-report-c1m1-tejal-20260419b.md)
- Shift close record: [`_bmad-output/implementation-artifacts/shift-close-2026-04-21-c1m1-tejal-20260419b.md`](\_bmad-output/implementation-artifacts/shift-close-2026-04-21-c1m1-tejal-20260419b.md)
- Step 0a harmonization report: [`reports/dev-coherence/2026-04-21-0603/harmonization-summary.md`](reports/dev-coherence/2026-04-21-0603/harmonization-summary.md)
- Pipeline lockstep regime: [`docs/dev-guide/pipeline-manifest-regime.md`](docs/dev-guide/pipeline-manifest-regime.md)
