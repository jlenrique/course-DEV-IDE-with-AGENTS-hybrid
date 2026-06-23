# Forward Requirements — queued (2026-06-23, operator-stated)

Captured during the LLM-first ship arc so they are not lost. None of these are dispatched yet; they queue behind the in-flight **image_role decorative-vs-illustrative Codex iteration** and its T11.

## Q1 — Cadence-token cleanup (Pass-2 narration voice, DEEPER fix)
**Queued AFTER the image_role T11** (operator-directed). The overarching "Narrate content, not geography" principle is already live in `pass-2-grammar-riders-examples.md` (`5147e0f`). The deeper root cause remains: the per-pattern **cadence tokens** the runtime lint requires include spatial phrases ("the column to the right", "the text side", "top-left", "returning to the center"), which actively pull narration back toward spatial meta-commentary.
**Scope:** soften the spatial cadence tokens to conceptual ones across the patterns, **in lockstep** with `scripts/validators/pass_2_emission_lint.py` (`_check_reading_path_pattern`) + the three-way parity (`reading-path-patterns.yaml` ↔ `segment-manifest.schema.json` ↔ this riders file). Touches the parity-locked set → run the lockstep tests; likely a small NEW CYCLE or careful Claude-direct after the tree is free. Follow-on key: **`pass2-cadence-tokens-spatial-to-conceptual`**.

## Q2 — Two variants per slide, choose at Storyboard A
Operator wants **2 versions of each slide generated**, and to **pick the favored one of each pair at the Storyboard A juncture (G2C)**.
- The variant **count** is already an operator decision at G2B ("how many variants per slide"); setting it to **2** is supported today.
- The real gap (known): **genuine variant distinctness** — current dispatch is single-dispatch, so the "variants" are not reliably *different* renders. This is the existing inventory item [[`trial-4-binding-variant-voice-picker`]] / [[`beta-genuine-variant-distinctness`]]. Q3 below is the mechanism that makes the 2 variants genuinely distinct.
- Storyboard A (G2C) already renders + lets the operator select per-slide; the per-pair pick is the existing G2C selection at N=2.

## Q3 — Operator-specified Gamma settings PER variant (the distinctness mechanism)
Operator wants to **specify the Gamma settings Gary uses to create each variant** — i.e., declare, per variant, the Gamma generation parameters (theme/template, tone, image style, layout/density, etc.) so the two renders are *deliberately* different rather than randomly varied.
**Implementation shape (for the variant NEW CYCLE):**
- The **G2B decision card** (Creative-Director treatment / capability e) carries a per-variant **Gamma parameter set** the operator can set/override (e.g. variant A = theme X + photographic; variant B = theme Y + illustrative/diagrammatic).
- The **Creative Director directive** schema carries those per-variant param sets downstream.
- **Gary** (`gamma_operations.py` / the Gamma dispatch) generates each variant with its declared settings (the Gamma API exposes theme/template/numCards/image-style knobs — real, controllable).
- Result: genuine 2-up distinctness by **design**, selectable at G2C. This directly closes [[`trial-4-binding-variant-voice-picker`]] distinctness gap.
**Reuse note:** Gary's Gamma parameter mastery already exists (theme/template preview, double-dispatch, PNG export normalization per project-context.md); this surfaces those knobs to the operator per variant rather than auto-choosing.

## Sequencing
1. (in-flight) image_role decorative-vs-illustrative Codex iteration → Claude T11 (combined with the LLM-primary close).
2. Q1 cadence-token cleanup.
3. Q2+Q3 variant arc (2 distinct variants via operator-specified per-variant Gamma settings) — a NEW CYCLE (substrate: G2B card + CD directive + Gary dispatch); party green-light first per governance.
Honesty/governance unchanged: no mocks; live gpt-5.5/Gamma; metric-citation; party green-light precedes substrate dev.
