# Spec — Variant Arc: 2 genuinely-distinct variants via operator-specified per-variant Gamma settings

**Status:** DRAFT for party green-light (NEW CYCLE; substrate). **Date:** 2026-06-23. **Authority:** operator directive (forward-requirements-2026-06-23.md Q2/Q3) + goal v9 ARC step 3.
**Closes:** the distinctness half of [[trial-4-binding-variant-voice-picker]] / [[beta-genuine-variant-distinctness]] (mechanics exist; genuine N-different renders are the gap).

## Problem
Today the operator can choose a variant **count** at G2B and pick per-slide at Storyboard A (G2C), but the "variants" are **single-dispatch** — not reliably *different* renders. The operator wants **2 variants per slide that are genuinely distinct by design**, by **specifying the Gamma settings for each variant** (e.g. variant A = theme X + photographic; variant B = theme Y + diagrammatic), and picking the favored one per slide at Storyboard A.

## What exists (reuse, do not rebuild)
- Gary already has Gamma parameter mastery: theme/template preview, double-dispatch, PNG export normalization (`app/specialists/gary/gamma_dispatch.py`, `_act.py`, `payload_contract.py`; project-context.md "Gamma API Mastery").
- G2B decision card surfaces variant treatment (`app/marcus/cli/gate_shims/g2b_shim.py`, `production_runner.py`); G2C Storyboard A renders + selects per slide.
- Creative-Director directive schema (`state/config/schemas/creative-directive.schema.json` + `.yaml`; contract `skills/bmad-agent-cd/references/creative-directive-contract.md`).

## The change (NEW CYCLE)
1. **CD directive schema** — add an additive, OPTIONAL per-variant `gamma_settings` array (one entry per variant: theme/template, image-style, density/numCards, tone). Backward-compatible: absent → current behavior (auto/default variants). Additive bump + `-gen` regen if the directive participates in the determinism witness; confirm at T1 whether this touches the pack/manifest lockstep (it should NOT — directive is data-plane, not the v4.2 pack).
2. **G2B decision card** — surface the per-variant `gamma_settings` so the operator can set/override each variant's Gamma params at the gate (default = a sensible distinct pair, e.g. A=photographic/themeX, B=diagrammatic/themeY, operator-overridable). Carry the operator's choices into the CD directive.
3. **Gary `gamma_dispatch`** — for each of the N variants, dispatch a Gamma generation with **that variant's declared settings** (not a single shared dispatch). Each variant is a distinct render keyed by `variant_id`. Reuse the existing double-dispatch/export-normalization path; the new bit is per-variant param binding.
4. **Storyboard A (G2C)** — already renders + selects per slide; confirm it shows the 2 distinct renders and binds the per-slide pick (the selected_variant_id seam already exists per the `select` verb / `_SELECTABLE_KEYS_BY_GATE` G2B).

## Acceptance (lightweight — proof, not ceremony)
- A production smoke on the frozen corpus generates **2 variants per slide that are visibly/parametrically distinct** (different theme/image-style per declared settings), renders both in Storyboard A, and binds a per-slide selection at G2C — end-to-end, no hard-blocks.
- Backward-compat: a run WITHOUT per-variant settings still works (default behavior).
- Operator SUPPLIES the actual settings at runtime; this cycle builds the MECHANISM + the default distinct-pair + the smoke.
- ruff + focused tests green; no 4-file-lockstep / v4.2-pack / manifest edit (confirm at T1); CD-directive schema change is additive (round-trip test).

## Governance / fences
Party-mode green-light THIS scope before Codex opens (per goal). Codex T1–T10 → Claude T11. No mocks (live Gamma); additive non-regression; never leave the lockstep/manifest half-modified. Honesty: every "distinct" claim backed by the actual 2 renders in the smoke.

## Party-mode green-light disposition (2026-06-23) — 3/3 GREEN-WITH-AMENDMENTS (no impasse)
Winston (architect) / John (PM) / Amelia (dev). Binding amendments (folded into `codex-dev-prompt-variant-arc.md`):
- **A3 VERIFIED (Winston, load-bearing):** `creative-directive.schema.json` is NOT in `pipeline-manifest.yaml::block_mode_trigger_paths` → confirmed **data-plane-only** (no pack/manifest lockstep). The spec's compat claim holds.
- **Additive-only + open-enum (Winston A1/A2):** `gamma_settings` OPTIONAL; absent → byte-identical legacy path (pin test); theme/image_style = open string + documented known-values (NOT closed enum); density/tone may be closed.
- **Keying is the real risk (Amelia A2/A3 + Winston A4):** artifact/run-dir keys MUST incorporate `variant_id` when settings present, byte-identical when absent (load-bearing backward-compat gate). T1 read-and-report on whether Gary keys on slide-id alone vs (slide-id, variant_id) BEFORE coding; per-variant fallback (A set, B default works).
- **N fixed at 2 (Amelia A1):** no general N fan-out (follow-on).
- **Default pair (Winston A5 / John C):** `DEFAULT_VARIANT_PAIR` = photographic(A) vs diagrammatic(B) on the **image-style axis** (highest perceptual distance, lowest layout/normalization perturbation); a SMOKE FIXTURE, not a product default.
- **Distinctness assertion (John A / Amelia):** mechanical (different settings → different artifacts) in tests; "distinct ENOUGH" = operator-gated eye-check at G2C.
- **Backward-compat explicit test (John B):** absent settings → today's behavior.
- **John Q4 (key):** the variant arc is critical-path-**PREFERRED, NOT trial-blocking** — single-variant is an acceptable trial-1 fallback. Do not let it become a false trial blocker.
- **Named dissent:** none. Codex T1–T10 → Claude T11. Operator supplies real settings at runtime; this cycle = mechanism + default pair + smoke.

## Open question for party (RESOLVED above)
- **Default distinct-pair policy:** what should the 2 default variants be when the operator doesn't specify (so distinctness is non-vacuous out of the box)? Proposal: A = photographic/literal-visual-leaning; B = diagrammatic/structured — operator-overridable. Party to ratify the default axis.
