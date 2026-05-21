---
name: checkpoint-coord
code: HC
description: Human checkpoint coordination and review-gate transitions
---

# Human Checkpoint Coordination

## Purpose

Marcus manages human review gates throughout production workflows. These are non-negotiable quality control points where the user — as creative director and domain expert — reviews, approves, rejects, or requests revision of specialist output. Human judgment is front-loaded at the points where revision is cheapest — before expensive audio and video generation.

---

## Four Formalized HIL Gates

The production pipeline has four mandatory human checkpoints. Each gate has defined inputs, review criteria, and downstream consequences.

### HIL Gate 1 — Lesson Plan Review
**Timing:** After Irene Pass 1; before Gary generates slides
**What to review:** Lesson plan (learning objectives, content outline, concept sequence, visual suggestions), slide brief (pedagogical intent per slide)
**Review criteria:** Content accuracy, objectives coverage, appropriate Bloom's level, logical sequencing, scope (is this one lesson or should it split?), and whether the proposed behavioral/affective goals fit the teaching need
**Approve → next step:** Gary generates slide deck from the slide brief
**Revision → back to:** Irene Pass 1 with specific feedback

### HIL Gate 2 — Slides Review
**Timing:** After Gary generates slides; before Irene Pass 2
**Pre-approval technical gate:**
- Run `.\.venv\Scripts\python.exe skills/bmad-agent-marcus/scripts/validate-gary-dispatch-ready.py --payload <gary-dispatch-result.json>`
- Require `status: pass` before presenting approval decision options
**Dispatch checks enforced:** non-empty `file_path`, non-empty `source_ref`, non-empty slide set, contiguous `card_number` sequence `1..N`
**What to review:** Gary's Gamma slide PNGs (visual quality, brand compliance, content accuracy, layout clarity)
**Review criteria:** Brand consistency (JCPH Navy, Medical Teal, Montserrat), visual hierarchy, content fidelity to slide brief, accessibility contrast, professional medical aesthetic, and fit to the approved `behavioral_intent`
**Approve → next step:** Gary's PNG paths passed to Irene for Pass 2 (narration + manifest). This is the most important gate — narration cannot be written until slides are approved.
**Revision → back to:** Gary with specific visual feedback

### HIL Gate 3 — Script & Manifest Review
**Timing:** After Irene Pass 2; before ElevenLabs runs and before Kira can be queued
**What to review:** Narration script (prose quality, pedagogical accuracy, slide complementarity) + segment manifest (segment structure, SFX/music cues, visual assignments)
**Review criteria:** Narration complements visuals (doesn't duplicate), appropriate tone and pacing, accurate medical content, logical segment structure, manifest field completeness, whether runtime variance is justified (`timing_role`, `content_density`, `visual_detail_load`, `duration_rationale`), whether bridge cadence is intentional (`bridge_type`), and whether narration + manifest preserve the intended behavioral/affective effect
**Approve → next step:** Marcus sends the approved script + manifest to ElevenLabs first. Once ElevenLabs returns `narration_duration` and audio artifacts to Marcus, Marcus can then delegate duration-targeted video work to Kira and route the completed manifest onward.
**Revision → back to:** Irene Pass 2 with specific feedback on script or manifest

### HIL Gate 4 — Final Video Review
**Timing:** After human assembles in Descript and exports final MP4; after Quinn-R post-composition validation
**What to review:** Final composed video (visual-audio sync, caption accuracy, overall instructional quality, pacing, music levels)
**Review criteria:** Audio-visual complementarity (Mayer's multimedia principle), learner engagement, professional production quality, accessibility (captions readable, audio description present), Quinn-R's post-composition report
**Approve → next step:** Asset staged for Canvas deployment
**Revision → back to:** Descript for targeted edits (no need to regenerate unless narration or visuals are wrong)

---

## Review Gate Protocol

At each checkpoint, Marcus:

1. **Presents the artifact** — Show the work product clearly, with enough context for informed review
2. **States quality criteria** — Reference the specific HIL gate criteria above and style bible standards
3. **Shows specialist self-assessment** — Share the specialist's own evaluation of the artifact
4. **Shows Quinn-R pre-validation** — For gates 3 and 4, include Quinn-R's automated check results
5. **Requests explicit decision** — Ask for one of: approve, reject with reason, or request specific revisions

Example (Gate 2): "Here's the cardiac physiology slide deck — 14 frames covering all four learning objectives. Intended effect: credible with an attention-reset on the complication slide. Style bible: JCPH Navy headers, Medical Teal highlights. Gary's self-assessment: all objectives covered, visual hierarchy consistent, one accessibility note on contrast ratio for Figure 3. This is the critical gate — once you approve, I'll send these to Irene for narration. What's your call?"

Gate 2 validation presentation order:
1. Show dispatch-readiness validation result (`pass`/`fail`) and key checks.
2. If `fail`, show blocking errors and stop for remediation.
3. If `pass`, present slide review package and request explicit user decision.

---

## Decision Handling

- **Approved** — Record approval in state, advance production plan to next stage, save parameter decisions to patterns (default mode only)
- **Revision requested** — Capture specific feedback, route back to specialist with revision context, re-present at the same gate after revision
- **Rejected** — Record rejection with reason, discuss alternatives with user, adjust production plan

---

## Quality Criteria Sources

Quality criteria come from two sources, both re-read fresh for each review gate:

- **Style bible** (`resources/style-bible/`) — brand identity, visual standards, accessibility, content voice/tone
- **Medical education standards** — Bloom's alignment, clinical case integration quality, assessment-objective tracing, backward design adherence
- **HIL gate criteria** — specific criteria per gate defined above

---

## Outcome Tracking

In default mode, record checkpoint outcomes in state:
- Artifact identifier and version
- HIL gate number (1-4)
- Decision (approved / revision / rejected)
- Revision count for this artifact
- User feedback notes (condensed)
- Time from first presentation to final approval

This data feeds expertise crystallization in `patterns.md` and production history in `chronology.md`.

---

## Script Integration

Use the `production-coordination` skill to persist checkpoint outcomes:

- **Before presenting**: call `manage_run.py checkpoint {run_id}` to mark the stage `awaiting-review` and create a `quality_gates` record.
- **On approval**: call `manage_run.py approve {run_id} --score {0.0-1.0}` to record the decision and update the gate record.
- **On revision**: note the feedback in the conversation context. The stage remains at `awaiting-review` until approved or the user redirects.

---

## Quinn-R Validation Integration

Quinn-R runs **automated quality checks between gates**, so artifacts presented for human review have already passed deterministic checks:

| Before Gate | Quinn-R Pre-Check |
|-------------|------------------|
| Gate 1 | Lesson plan structure, objective completeness |
| Gate 2 | Brand validation (automated), accessibility scan |
| Gate 3 | Manifest schema completeness, narration coverage |
| Gate 4 (post-composition) | Audio levels, caption sync, composition integrity |

Quinn-R's pre-composition pass (before Gate 4 — before the user opens Descript) validates: narration WPM with script-aware advisory downgrade when appropriate, VTT monotonicity, segment coverage, video duration vs narration duration (±0.5s), and missing asset paths. If pre-composition fails on blocking findings, route failing assets back to the producing agent before presenting the Descript Assembly Guide to the user. Advisory findings such as runtime-band drift or bridge-cadence gaps should be shown to the operator rather than silently escalated.
