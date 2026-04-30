# Quinn-R — Quality Reviewer

## OPERATOR

Quinn-R is your **pre-composition + post-composition QA specialist**. He runs validators at the Storyboard-A authorize gate, ensuring lesson-plan + storyboard + narration + audio artifacts are coherent before they reach G2 (Storyboard-A approval) or G5 (final composition QA).

You invoke Quinn-R implicitly through the trial pipeline at G2/G5. You CAN talk to Quinn-R directly when a validator fires and you want to understand why.

**When you'd talk to Quinn-R directly:** debugging G5 mode-mismatch failures, asking "why did `WpmThresholdError` fire?", or reviewing the authorized-storyboard.schema.json contract.

## INPUTS

- **Pre-composition payload:** lesson-plan + storyboard-A + narration draft + Pass-2 manifest.
- **Post-composition payload:** assembly-bundle (audio + captions + visuals + DESCRIPT-ASSEMBLY-GUIDE.md).
- **G5 rubric:** mode-singularity contract; WPM thresholds; VTT monotonicity; coverage gaps; duration coherence.
- **Authorized-storyboard schema:** `state/schemas/authorized-storyboard.schema.json` (Pydantic v2; regenerated via schema-regen utility from 7b.2).

## OUTPUTS

- **Pre-composition QA verdict** (G2C dispatch): `VerdictPayload` with `decision in {confirm, revise, reject, escape, skip-slide, abort-run}` per vocabulary registry.
- **Post-composition QA verdict** (G5 dispatch): structured error reports for `ModeMismatchError` / `WpmThresholdError` / `VttMonotonicityError` / `CoverageGapError` / `DurationCoherenceError` if any G5 dimension fails.
- **Quinn-R summary:** lands at `[bundle]/quinn-r-summary.md` per 7a.5 specialist-summary-writer integration.

## REFERENCE

- Persona SKILL.md: `skills/bmad-agent-quality-reviewer/SKILL.md` (note: `quality-reviewer` is the legacy skill-dir name; persona is named Quinn-R)
- Sanctum: `_bmad/memory/bmad-agent-quinn-r/` (6-file BMB; canonical path landed at 7b.8 retrofit; was `bmad-agent-quality-reviewer/` pre-Slab-7b)
- Story spec: [`migration-7b-2-quinn-r-hardening.md`](../../../_bmad-output/implementation-artifacts/migration-7b-2-quinn-r-hardening.md)
- Code: `app/specialists/quinn_r/` (9-node scaffold; `quality_control_dispatch.py` + `sensory_bridges_dispatch.py` consumed)
- Class: A (option-a sanctum-aligned)
- Specialist alias: `quinn-r` ↔ `quinn_r` per `app/manifest/compiler.py::SPECIALIST_ALIASES`
