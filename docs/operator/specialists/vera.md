# Vera — Pass-2 Fidelity Assessor

## OPERATOR

Vera is your **Pass-2 fidelity-assessment specialist**. She runs the G4 fidelity rubric on Pass-2 narration script + storyboard manifest before they progress to motion / audio / compositor stages. Quinn-R consumes Vera's G4 verdicts at G5 final QA.

You invoke Vera implicitly through the trial pipeline at G4. You CAN talk to Vera directly to inspect a fidelity rubric or understand why a Pass-2 artifact failed G4.

**When you'd talk to Vera directly:** asking "why did this storyboard fail G4 fidelity?", "what does the rubric look for in `[bundle]/08-pass2-narration-script.md`?", or "is the cluster-arc integrity rule honored here?".

## INPUTS

- **Pass-2 narration script** (`[bundle]/08-pass2-narration-script.md`): per-segment narration text + timing + visual_detail_load values.
- **Pass-2 envelope** (`pass2-envelope.json`): structured Pass-2 contract emission.
- **Storyboard manifest** (`segment-manifest.yaml`): cluster boundaries + bridge cadence + visual continuity.
- **G4 rubric**: fidelity dimensions (token-coverage, behavioral-intent shape, bridge-cadence mechanics, cluster-arc integrity).

## OUTPUTS

- **G4 fidelity verdict**: structured rubric scoring + pass/fail per dimension + per-segment annotations.
- **Vera summary**: lands at `[bundle]/vera-summary.md` per 7a.5 specialist-summary-writer integration.
- **Pass-2 G4 dispatch payload**: consumed by Quinn-R at G5 mode-mismatch / coverage-gap checks.

## REFERENCE

- Persona SKILL.md: `skills/bmad-agent-fidelity-assessor/SKILL.md` (note: `fidelity-assessor` is the legacy skill-dir name; persona is Vera)
- Sanctum: `_bmad/memory/bmad-agent-vera/` (6-file BMB; canonical path landed at 7b.3 / refreshed at 7b.8 retrofit; legacy `vera-sidecar/` preserved out-of-band per `vera-sidecar-cleanup-post-trial-2-validation` follow-on)
- Story spec: [`migration-7b-3-vera-hardening.md`](../../../_bmad-output/implementation-artifacts/migration-7b-3-vera-hardening.md)
- Code: `app/specialists/vera/` (9-node scaffold; `sensory_bridges_dispatch.py` consumed)
- Class: A (option-a sanctum-aligned)
