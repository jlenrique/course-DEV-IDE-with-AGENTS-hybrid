# Story 43-3 — Variant / per-slide-mode selection renderers (+ the gate→renderer bridge)

**Epic:** 43 · **Slab:** 2 · **Status:** ready-for-dev
**Gate mode:** dual-gate (touches the paused-at-gate emit wiring + projector registry).
**Load-bearing note:** this is the FIRST bespoke renderer that must fire on the *paused-at-gate* path, so it also establishes the **gate→content_type bridge** that every later bespoke renderer (43-4…43-9) reuses.

## Story

As the **operator**, at **G2B (per-slide presentation-mode)** and **G2M (A/B variant selection)**, I want each choice shown as a purpose-built table (the modes/variants and what distinguishes them) rather than the generic Field|Value dump, so I can actually compare options before selecting.

## The bridge problem (resolve this first)

43-2's `_emit_gate_surface_if_paused` sets `content_type = card.get("gate_id") or gate`. 43-10's canonical keys (`per_slide_mode`, `variant_ab`, …) are SEMANTIC, not gate_ids. So a renderer registered under `"variant_ab"` will NOT be dispatched by the wiring. **Establish a clean bridge** so a paused gate routes to its registered bespoke renderer:

- **AC-0 (bridge):** add a `GATE_TO_CONTENT_TYPE` mapping (in `hil_tabular_projector.py` or a small sibling) from the gate identifier the wiring sees (the decision-card `gate_id` / gate string) → the canonical content-type key. Update `_emit_gate_surface_if_paused` to resolve `content_type = GATE_TO_CONTENT_TYPE.get(gate_key)` (None → generic fallback, unchanged behavior). A test MUST prove a paused-gate fixture routes to the BESPOKE renderer (not the generic fallback). Additive-within-v1 (rider R7); generic fallback still covers every unmapped gate.

## T1 required readings

- `_bmad-output/planning-artifacts/epic-43-hil-surface-tabular-coverage.md` §2/§4b.
- `app/marcus/cli/hil_tabular_projector.py` — registry, `render_gate_content`, `GATE_CONTENT_TYPES`, `KNOWN_UNRENDERED_ALLOWLIST`, `_md_table`, `_truncate_cell`, `render_generic_gate_content` (pattern).
- `app/marcus/cli/trial.py` — `_emit_gate_surface_if_paused` (the `content_type` derivation to bridge).
- `app/gates/section_05_5/poll_surface.py` (`display_per_slide_mode`, :88) and `app/gates/section_07b/poll_surface.py` (`display_per_slide_variant`, :90) — the exact dict shapes to render + to synthesize fixtures from.
- `tests/fixtures/hil_projector/README.md` — confirms NO real run reached these gates → **synthesize** schema-faithful fixtures.
- `tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py` — register new test/fixture .py paths in `PERMITTED_PYTHON_DIFFS` (see the Epic-43 block).

## Acceptance criteria

**AC-0 — the gate→content_type bridge** (above). Proven by a routing test.

**AC-1 — `per_slide_mode` renderer (G2B).** `render_per_slide_mode(content, ...)` registered under `content_type="per_slide_mode"`; tables the available modes (per the section_05_5 poll-surface shape) with their distinguishing fields. Reuse `_md_table` + `_truncate_cell`. Names "G2B per-slide-mode selection" in an AC/test.

**AC-2 — `variant_ab` renderer (G2M).** `render_variant_ab(content, ...)` registered under `content_type="variant_ab"`; tables the A/B variants side-by-side (per section_07b). Names "G2M A/B variant selection".

**AC-3 — Fixtures (synthesized, zero spend).** Add schema-faithful fixtures under `tests/fixtures/hil_projector/` (e.g. `poll-per-slide-mode-synthetic.json`, `poll-variant-ab-synthetic.json`) built to the poll-surface `display_*` return shapes. Document in the fixtures README that they are SYNTHETIC (no real run reached G2B/G2M) with the source poll_surface named.

**AC-4 — Ratchet moves (43-10).** Remove `per_slide_mode` and `variant_ab` from `KNOWN_UNRENDERED_ALLOWLIST`; both are now registered. Run `tests/marcus/cli/test_projector_coverage_ratchet_43_10.py` — the disjoint/coverage invariants stay green with 2 more registered, 2 fewer waived.

**AC-5 — No raw dump / stdout-stderr / additive.** Human tables to stderr; stdout machine JSON untouched (rider R4). Additive-within-v1 (rider R7). Projector stays stdlib-pure.

## Test requirements

- New test file(s) under `tests/marcus/cli/`; replay against the synthetic fixtures; the AC-0 routing test; ratchet green.
- Register EVERY new `.py` test file in `PERMITTED_PYTHON_DIFFS` (TW-7c-4) — the orchestrator will otherwise catch it in the consumer baseline-diff.
- Run ONLY touched test files + the ratchet + TW-7c-4 scope test. Do NOT run the full suite. Do NOT commit or stash.

## Definition of done

Bridge established (paused gate → bespoke renderer, proven); per_slide_mode + variant_ab renderers registered + tabling their synthetic fixtures; both moved allowlist→registry with 43-10 green; TW-7c-4 test files registered; ruff/import-linter clean; ready for orchestrator review (consumer baseline-diff) → `bmad-code-review`.
