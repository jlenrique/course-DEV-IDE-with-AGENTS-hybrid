# Irene — Lesson Plan Coauthor (Pass-1) + Narration Architect (Pass-2)

## OPERATOR

Irene runs in two distinct passes. She is your **lesson-plan coauthoring specialist** at Pass-1 (G1A) and your **Pass-2 narration architect** at G3 narration-script generation. Pass-1 + Pass-2 share the same persona-continuity sanctum but live in separate `app/specialists/` directories with separate scaffolds.

**Pass-1 (Irene Pass-1; this doc's primary scope):** lesson-plan coauthoring + scope-lock contract + per-plan-unit ratification surface for G1A. Mode-singularity hard-constraint enforcement (`ModeMismatchError`).

**Pass-2 (Irene Pass-2; pre-Slab-7b):** narration-script + storyboard manifest emission at G3.

You invoke Irene implicitly through the trial pipeline at G1A (Pass-1) or G3 (Pass-2). You talk to Irene directly when authoring or reviewing lesson plans, or debugging narration-shape questions.

**When you'd talk to Irene directly:** asking "what's the lesson-plan contract?", reviewing a Pass-2 narration script for behavioral-intent shape, or debugging a `ModeMismatchError` from G5.

## INPUTS

- **Pass-1:** Texas Pass-1 retrieval bundle + operator directive + lesson-plan template.
- **Pass-2:** locked Pass-1 lesson plan + Tracy RetrievalIntent enrichments + storyboard cluster boundaries.
- **Mode contract**: mode-singularity rule (one-mode-at-a-time per segment).
- **Cache-hit-rate harness**: `tests/end_to_end/test_cache_hit_rate_baseline.py` (median[2:] ≥ 85% post-warm-up per Slab 2a.2 MF1+MF2+MF5 discipline).

## OUTPUTS

- **Pass-1**: `[bundle]/lesson-plan-pass1.md` + per-plan-unit G1A ratification artifacts.
- **Pass-2**: `[bundle]/08-pass2-narration-script.md` + `pass2-envelope.json` + `segment-manifest.yaml`.
- **Irene summary**: lands at `[bundle]/irene-summary.md` per 7a.5 specialist-summary-writer integration.

## REFERENCE

- Persona SKILL.md: `skills/bmad-agent-content-creator/SKILL.md` (Irene is the content-creator persona; Pass-1 + Pass-2 share)
- Sanctum: `_bmad/memory/bmad-agent-content-creator/` (6-file BMB; SHARED between Pass-1 + Pass-2 per Slab 2a.2 era convention)
- Pass-1 story spec: [`migration-7b-4-irene-pass1-refresh.md`](../../../_bmad-output/implementation-artifacts/migration-7b-4-irene-pass1-refresh.md)
- Pass-1 code: `app/specialists/irene_pass1/` (NEW directory at 7b.4; separate from Pass-2 `irene/`)
- Pass-2 code: `app/specialists/irene/` (pre-Slab-7b)
- Class: B (refresh after Vera G4 inheritance; cache-hit-rate harness ≥85%)
