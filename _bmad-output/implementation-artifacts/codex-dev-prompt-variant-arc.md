# Codex Dev Prompt — Variant Arc: per-variant Gamma settings (NEW CYCLE)

**You are Codex (T1–T10).** Claude T11. Party green-light: **3/3 GREEN-WITH-AMENDMENTS** (Winston/John/Amelia, no impasse). Spec: `spec-variant-arc-per-variant-gamma-settings.md` (§Party disposition). **Do NOT relitigate scope.**

## Goal
Let the operator specify **per-variant Gamma settings** so each of **2 variants/slide** is a genuinely-distinct render, chosen at Storyboard A (G2C). Closes the `trial-4-binding-variant-voice-picker` distinctness gap. Build the **mechanism + a default distinct-pair + a smoke**; the operator supplies real settings at runtime (do NOT build a settings UI).

## T1 PRECONDITION (Amelia A3 / Winston A4 — required FIRST, report in Dev Notes)
Read `app/specialists/gary/gamma_dispatch.py`, `_act.py`, `payload_contract.py`, and the G2C Storyboard-A binding. **Report whether export-normalization + artifact/run-dir keys on slide-id ALONE or on (slide-id, variant_id).** If slide-id alone → weaving variant_id into the keys IS the real work of this story (still one cycle, but it's rework not a loop — flag before proceeding). Also confirm Gary's dispatch accepts a settings dict vs reading a single global theme field.

## The change
1. **CD directive schema** (`state/config/schemas/creative-directive.schema.json` + `.yaml`, KEPT IN PARITY) — add an **additive, OPTIONAL** per-variant `gamma_settings` array (one entry/variant: theme/template, image_style, density, tone). **Absent → byte-identical to today's single-dispatch** (Winston A1). Do NOT touch `required`, do NOT narrow existing types. **theme + image_style = open string with documented known-values (NOT closed enum)** so new Gamma themes don't force a schema bump (Winston A2); density/tone may be closed enums.
2. **G2B decision card** (`app/marcus/cli/gate_shims/g2b_shim.py` + `production_runner.py`) — surface per-variant `gamma_settings` for operator set/override; tolerate absent/null without rejecting; carry choices into the CD directive.
3. **Gary `gamma_dispatch`** — for N=2 variants, dispatch each with its declared settings (reuse the existing double-dispatch + PNG export-normalization). **Per-variant fallback** (Winston A4): a directive may set settings for A and leave B default; both must work. **Artifact/run-dir keys MUST incorporate `variant_id` when gamma_settings present, byte-identical when absent** (Amelia A2 — the load-bearing backward-compat gate).
4. **Storyboard A (G2C)** — confirm it renders the 2 distinct variants + binds the per-slide pick (`selected_variant_id` seam exists). "Renders a choice of 2" vs "binds one" are different — verify at T1.

## N FIXED AT 2 (Amelia A1) — no general N-variant fan-out (follow-on).

## Default distinct-pair (Winston A5 / John C)
A named constant `DEFAULT_VARIANT_PAIR` in Gary's module: **A = photographic image_style, B = diagrammatic/illustrative image_style**, holding theme/template/density/tone constant (image-style is the highest perceptual-distance / lowest layout-perturbation axis). **Label it a SMOKE FIXTURE / sensible default the operator overrides at runtime — NOT a product default.**

## Tests (RED-first; Amelia — all four non-negotiable)
1. **Additive-schema round-trip:** directive with/without `gamma_settings` round-trips; absent → omitted (not null-injected); `.json`/`.yaml` parity.
2. **Per-variant dispatch:** N settings → N dispatch calls each carrying its own settings → N distinct variant-keyed PNG artifacts. Real Gary code/payload assembly; stub only the HTTP edge.
3. **Backward-compat-no-settings (LOAD-BEARING):** no `gamma_settings` → exactly ONE dispatch, current artifact key, byte-identical run-dir layout vs baseline. The regression gate.
4. **Smoke (live Gamma):** 2 distinct renders/slide, selectable at G2C, no hard-blocks. Distinctness asserted **mechanically** (different settings → different output hashes); "distinct ENOUGH" is an **operator-gated** eye-check at G2C (not a dev-agent assertion).

## Fences / governance
No mocks (live Gamma); additive non-regression (existing single-variant runs unchanged); **no v4.2-pack / manifest / 4-file-lockstep edit** (A3 verified data-plane-only — confirm untouched at T1); ruff + focused tests green. Codex T1–T10 → Claude T11.

## Handoff → Claude T11
`_codex-handoff/variant-arc-ready-for-review.md`: the T1 keying-report finding, before/after, the 4 test results, the smoke's 2-distinct-render evidence (artifact hashes + paths), backward-compat attestation, baseline-diff attestation.

## NOTE (John Q4): this is critical-path-PREFERRED, NOT trial-blocking. Single-variant remains an acceptable trial-1 fallback if this slips.
