# Claude Code Brief: Topic Coverage Assurance Interlock Before Leg-1b

Date: 2026-06-29
Branch: `dev/concierge-production-substrate-2026-06-29`
Current substrate: Leg-1a is party-CLOSED, committed, and pushed at `faf1fbbe`.
Audience: Claude Code / BMAD dev session lead

## Executive Recommendation

Insert a narrow design/governance interlock **now**, before Leg-1b opens for development.

Do **not** proceed directly from Leg-1a into `warm_callback` authoring until the party explicitly decides how topic/source-note coverage is represented and checked. Leg-1b is the first concierge leg that authors new learner-facing lexical content, so this is the optimal point to add quality-control structure rather than discovering coverage drift after scripts, audio, or Descript assembly.

This should be a focused interlock, not a full Leg-4 provenance-ledger buildout. The right move is a thin, LLM-backed **topic coverage assurance layer** that gives Leg-1b a source-point anchor substrate and gives later Legs 3/4 something real to harden.

## Why This Belongs Before Leg-1b

Leg-1a was tonal and text-preserving: `contrast_emphasis -> [slow]` authors zero new words, so Vera-R7 was not required.

Leg-1b is different:
- `warm_callback` authors new spoken language.
- The callback must be anchored to source-backed prior teaching, not merely stylistically plausible.
- Vera-R7/source containment is already ratified as a hard gate.
- The operator's production intent is that Gamma carries the visible gist while narration carries the details and source-note nuance.

Without an atomic source-topic ledger, Leg-1b can prove "the callback is contained" while still failing the bigger production question: did the source notes' important points get carried somewhere, either on screen or in narration?

## Proposed Insertion Point

Before `concierge-leg1b` party GREEN-LIGHT / create-story.

Recommended workflow:
1. Party amendment round: John + Winston + Murat + Irene + Vera, with Marcus/Dr. Quinn synthesizing.
2. Produce a short design record and, if accepted, a small story before or bundled into Leg-1b.
3. Only then create the Leg-1b implementation story.

Suggested label:
`concierge-coverage-assurance-interlock-before-leg1b`

## Minimal Target Shape

Add a thin, LLM-backed source-topic coverage contract with four concepts:

1. `source_point_id`
   - Atomic source-note point.
   - Carries `source_ref`, source text/span, topic label, and risk flags.

2. Coverage intent
   - `gist_required_on_slide`
   - `detail_required_in_narration`
   - `verbatim_required`
   - `workbook_candidate`
   - `excluded_or_context_only`

3. Planned surface mapping
   - Which slide, narration segment, workbook section, motion beat, or deliberate exclusion will carry the point.

4. Receipt status
   - `covered_on_slide`
   - `covered_in_narration`
   - `covered_in_workbook`
   - `verbatim_preserved`
   - `missing`
   - `altered_or_risky`

The intended division of labor should be explicit:
- Gamma/slides carry the **gist** and visible learning surface.
- Narration carries detail, nuance, examples, callbacks, clinical terms, numbers, negations, and exemplary language where needed.

## Scope Boundary

This interlock should not attempt to fully solve deterministic semantic coverage across the whole app.

In scope now:
- Define the coverage assurance contract.
- Decide where it enters Leg-1b.
- Require Leg-1b callback authoring to cite source-point anchors.
- Require at least one LLM-backed coverage receipt for the Leg-1b live slice.
- Add fail-loud behavior for `must-cover` source points that have no planned slide/narration/workbook surface.

Out of scope now:
- Full UI.
- Full corpus-wide deterministic semantic matcher.
- Large refactor of G2/G3/G4.
- Replacing existing Vera/G4 contracts.
- Full Leg-4 UDAC run-asset-index work.

## Recommended Leg-1b Acceptance Bar Amendment

Add these to the existing Leg-1b bar:

1. Every authored `warm_callback` must cite one or more `source_point_id` anchors.
2. The callback text must pass Vera-R7/source-containment against those anchors.
3. The callback must not introduce a new clinical claim, numeric claim, comparator, negation, or term absent from its anchors.
4. The Leg-1b live slice must include a coverage receipt showing whether each relevant source point is handled on screen, in narration, both, or intentionally deferred.
5. A source point marked `detail_required_in_narration` cannot be considered satisfied merely because Gamma produced a visually plausible slide.

## Suggested Party Questions

Ask the party to decide:

1. Does Leg-1b require a source-point anchor substrate before callback authoring?
2. Should the first version be LLM-backed and receipt-driven rather than deterministic-only?
3. What is the minimum schema needed for `source_point_id` and coverage intent?
4. Does a missing `must-cover` point block before audio spend?
5. Does this become a Leg-1b pre-story, or is it folded into Leg-1b as T0/T1?

## Marcus Recommendation

Yes: insert this interlock now.

Best path: make it a short pre-story/design spike that produces an agreed contract and one thin live/real slice receipt, then open Leg-1b against that contract. This preserves momentum while preventing Leg-1b from hard-coding callback behavior before the system knows what source-note point the callback is supposed to serve.

The risk of not doing this now is small in code terms but large in production terms: `warm_callback` may become technically live while remaining pedagogically ungrounded. The true-production concierge run needs the stronger guarantee: each important source-note point is accounted for somewhere, with details preferentially carried by narration and gist preferentially carried by slides.

## Proposed Handoff Sentence to Claude

Pause before creating/devving Leg-1b. Run a brief party amendment on topic/source-note coverage assurance, then either create a narrow `coverage-assurance-interlock` story or add a binding T0/T1 to Leg-1b. Leg-1b must not author `warm_callback` text until source-point anchors and coverage receipts are ratified.
