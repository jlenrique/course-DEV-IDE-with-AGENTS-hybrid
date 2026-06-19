# Interaction Test Guide — Quinn-R (Quality Reviewer, Quality Guardian 🛡️)

## Purpose
Verify Quinn-R activates correctly, reviews artifacts across 5 quality dimensions, provides structured feedback with severity and fixes, handles mode-aware logging, and escalates medical accuracy concerns.

## Prerequisites
- Quinn-R's SKILL.md loaded in Cursor agent chat
- `resources/style-bible/master-style-bible.md` present
- `state/config/course_context.yaml` with learning objectives
- `state/config/tool_policies.yaml` present (or defaults used)

---

## Scenario 1: Interactive Activation
**Trigger:** "Talk to Quinn-R" or "I need the Quality Guardian"
**Expected:**
- [ ] Greets with quality state (last review cycle summary or "no reviews yet")
- [ ] Reports recurring patterns if any
- [ ] Offers to review artifacts
- [ ] Does NOT dump capability list

## Scenario 2: First Run (No Sidecar)
**Trigger:** Activate with empty `_bmad/memory/quinn-r-sidecar/`
**Expected:**
- [ ] Runs init.md first-run setup
- [ ] Creates sidecar structure (4 files)
- [ ] Verifies style-bible, course_context, tool_policies exist
- [ ] Notes any missing references as partial-review capability

## Scenario 3: Headless Review from Marcus
**Trigger:** Provide review request: `{production_run_id: "test-001", artifact_paths: ["course-content/staging/story-3.2-samples/NS-C1M1L1-02-narration-script.md"], content_type: "narration_script", producing_specialist: "content-creator"}`
**Expected:**
- [ ] Reads artifact and style bible
- [ ] Reviews across all 5 dimensions
- [ ] Returns structured quality report with dimension scores
- [ ] Includes findings with severity, location, description, fix suggestion
- [ ] Returns overall verdict (pass/fail)

## Scenario 4: Accessibility Violation Detection
**Trigger:** Provide artifact with heading skip (H2 → H4)
**Expected:**
- [ ] Flags as Critical severity (non-negotiable per Principle 1)
- [ ] Specifies exact location (line, heading text)
- [ ] Provides fix: "Add H3 heading or promote to H3"
- [ ] Overall verdict: FAIL (accessibility below threshold)

## Scenario 5: Brand Consistency Check
**Trigger:** Provide artifact referencing non-palette color (#ff0000)
**Expected:**
- [ ] Flags as Medium or High severity
- [ ] References style bible palette colors
- [ ] Suggests replacement with nearest brand color

## Scenario 6: Learning Objective Alignment
**Trigger:** Provide artifact content that doesn't trace to any learning objective
**Expected:**
- [ ] Flags orphaned content
- [ ] Identifies which learning objectives have NO corresponding content
- [ ] Severity: High

## Scenario 7: Medical Accuracy Escalation
**Trigger:** Provide artifact mentioning "administer 500mg aspirin for pediatric fever"
**Expected:**
- [ ] Flags as Critical-escalation
- [ ] Does NOT adjudicate correctness
- [ ] Notes: "Unusual pediatric aspirin dosage — aspirin is generally contraindicated in children (Reye's syndrome risk)"
- [ ] Routes through Marcus to human review

## Scenario 8: Mode-Aware Logging
**Trigger:** Run review in ad-hoc mode (run_mode: "ad-hoc")
**Expected:**
- [ ] Quality review EXECUTES fully (QA runs in both modes)
- [ ] Returns structured quality report
- [ ] Logging status: "suppressed" (no SQLite write)
- [ ] Sidecar writes suppressed (except transient index section)

## Scenario 9: Multi-Artifact Pairing Check
**Trigger:** Provide narration script + slide brief that reference each other
**Expected:**
- [ ] Checks cross-artifact consistency (pairing references match)
- [ ] Verifies content alignment between paired artifacts
- [ ] Verifies terminology consistency
- [ ] Checks asset-lesson pairing invariant (both reference LP)

## Scenario 10: Redirect (Wrong Agent)
**Trigger:** "Design a lesson plan for Module 3" or "Create slides"
**Expected:**
- [ ] Redirects: "I'm Quinn-R — I handle quality validation only. For content design talk to Irene, for slides talk to Gary, or ask Marcus."
- [ ] Does NOT attempt the task

## Scenario 11: Calibration Transparency
**Trigger:** After multiple reviews where user has adjusted severity preferences
**Expected:**
- [ ] Notes calibration adjustments in quality report
- [ ] "Flagging as medium (was low — user escalated heading hierarchy issues)"
- [ ] Calibration limits respected: accessibility cannot be demoted below Critical

## Scenario 12: Partial Review (Missing References)
**Trigger:** Review artifact when `resources/style-bible/` is missing
**Expected:**
- [ ] Brand consistency dimension: SKIPPED
- [ ] Other dimensions reviewed normally
- [ ] Overall verdict: PARTIAL REVIEW
- [ ] Clear note about what was skipped and why

---

## Scenarios Added: Story 3.3.1 (Two-Pass Validation + Audio/Composition Dimensions)

## Scenario 13: Pre-Composition Pass
**Trigger:** Marcus invokes review with `review_pass: "pre-composition"` + `segment_manifest_path`
**Expected:**
- [ ] Quinn-R runs pre-composition checks (AQ + CI dimensions) against assets
- [ ] Validates narration WPM against the voice-agnostic intelligibility band [110, 200] (P1 2026-06-19; beta-phase-1-closure-ratification §5) from duration/word-count ratio
- [ ] Validates VTT timestamp monotonicity
- [ ] Validates segment narration coverage (>95% of script words)
- [ ] Validates video duration vs narration duration (±0.5s tolerance)
- [ ] Returns `review_pass: "pre-composition"` in report
- [ ] Does NOT run post-composition checks (brand, full accessibility) — those are post-composition
- [ ] If pass: Marcus provides Descript Assembly Guide to user; if fail: routes back to producing agent

## Scenario 14: Post-Composition Pass
**Trigger:** Marcus invokes review with `review_pass: "post-composition"` + final MP4 + VTT paths
**Expected:**
- [ ] Quinn-R runs full 7-dimension review (CC, BV, LA, IS, AQ, CI, CA)
- [ ] AQ checks: narration at -16 LUFS, music ducked -30 LUFS under speech, SFX -20 LUFS
- [ ] CI checks: caption synchronization, transition consistency
- [ ] Returns `review_pass: "post-composition"` in report
- [ ] `dimension_scores` includes all 7 dimensions

## Scenario 15: Audio Quality Dimension (AQ)
**Trigger:** Provide narration MP3 with WPM outside the intelligibility band [110, 200] (e.g., runaway-fast at 240 WPM; note 200 is now in-band/inclusive)
**Expected:**
- [ ] AQ dimension FAIL
- [ ] Finding: severity High — "Narration pace: 240 WPM (intelligibility band: 110-200). Recommend regenerating with lower stability or adjusted pacing."
- [ ] Location: specific segment ID from manifest
- [ ] Actionable fix suggestion included
