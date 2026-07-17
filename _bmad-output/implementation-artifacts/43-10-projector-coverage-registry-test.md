# Story 43-10 — Projector coverage registry test (RED-first ratchet)

**Epic:** 43 · **Slab:** 4 (but lands EARLY — rider R3, the acceptance ratchet) · **Status:** ready-for-dev
**Dispatch position:** after 43-2 (needs its registry), before the bespoke renderers.
**Gate mode:** single-gate (test + a small canonical data addition; no behavior change).

## Story

As the **team**, I want a structural test that **fails if any gate content type lacks a renderer** and can only be satisfied by either registering a bespoke renderer or explicitly waiving the type on a **shrink-only allowlist** — so "closed on a subset" (the exact 42-1 failure) becomes mechanically impossible. This generalizes operator pin 3 across every gate, permanently.

## T1 required readings

- `_bmad-output/planning-artifacts/epic-43-hil-surface-tabular-coverage.md` — §2 (the full gate content-type inventory), §4b rider R3.
- `app/marcus/cli/hil_tabular_projector.py` — the 43-2 registry: `registered_content_types()` (frozenset), `register_renderer`, `get_renderer`, `render_gate_content`.
- The audit inventory in the epic spec §2 for the canonical content-type list.

## The canonical gate content-type universe (from the audit, §2)

Every gate content type the operator reviews. Two are already rendered by the pre-43 projector (enrichment/LOs); the rest need bespoke renderers (or the generic fallback until then):

`directive` (G0) · `estimator` (G1.5) · `run_constants` (G1.5) · `plan_unit` (G1A) · `per_slide_mode` (G2B) · `variant_ab` (G2M) · `literal_visual` (06B) · `storyboard_targets` (07C) · `motion_plan` (G2.5) · `motion_clip` (G2F) · `storyboard_b` (G3B) · `voice_candidates` (G4A) · `input_package` (G4B) · `final_handoff` (G5) · `research_packet` · `workbook`

(Exact key spellings are the dev's to finalize, but they MUST be a single canonical set consumed by both the test and the renderers.)

## Acceptance criteria

**AC-1 — Canonical content-type set.** A single canonical enumeration of gate content types lives in one place (e.g. `GATE_CONTENT_TYPES` in `hil_tabular_projector.py` or a small sibling) — the SSOT both the coverage test and every bespoke `register_renderer` call reference. Additive data, no behavior change (rider R7).

**AC-2 — Coverage test (RED-first).** A test asserts: for every canonical content type, EITHER a bespoke renderer is registered (`in registered_content_types()`) OR the type is in `KNOWN_UNRENDERED_ALLOWLIST`. At 43-2 (no bespoke renderers yet) the allowlist = the full canonical set. The test is GREEN now (all types allowlisted) and stays green as each bespoke story moves a type from allowlist → registry.

**AC-3 — Shrink-only + disjoint invariants.** Two guard assertions: (a) `KNOWN_UNRENDERED_ALLOWLIST ⊆ GATE_CONTENT_TYPES` (no stray/typo entries); (b) `registered_content_types() ∩ KNOWN_UNRENDERED_ALLOWLIST == ∅` (a type that has a bespoke renderer MUST be removed from the allowlist — you cannot both register and waive). This forces each bespoke story to delete its allowlist row when it registers.

**AC-4 — Anti-regression for new gates.** The test also asserts there is no canonical type that is neither registered nor allowlisted — so a future new gate content type cannot be silently added without a renderer or an explicit waiver. Name this behavior in the AC ("names G0 directive composition and every gate surface by canonical key") so a G0E-only replay can never re-close it (pin 3, mechanical).

**AC-5 — 43-12 hook.** Document that 43-12 (governance close) asserts `KNOWN_UNRENDERED_ALLOWLIST == ∅`. Leave a clear comment on the allowlist that it is shrink-only and empty-at-epic-close.

## Test requirements

- Pure test + a small canonical-data addition. No renderer behavior change.
- New test file (e.g. `tests/marcus/cli/test_projector_coverage_ratchet_43_10.py`).
- Run ONLY the new/touched test files. Do NOT run the full suite. Do NOT commit or stash.

## Constraints

- Additive-within-v1 (rider R7). ruff + import-linter clean. Keep the projector stdlib-pure (no import from trigger paths).
- Leave the tree uncommitted for orchestrator review.

## Definition of done

Canonical content-type SSOT + coverage ratchet test green (all types allowlisted at 43-2) with the shrink-only + disjoint + no-orphan invariants; each future bespoke story now MUST move its type allowlist→registry; ready for `bmad-code-review` (single-gate).
