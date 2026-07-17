# Story 43-8 — Input-package + final-handoff renderers

**Epic:** 43 · **Slab:** 3 · **Status:** ready-for-dev · **Gate mode:** dual-gate.

Follows the **43-3/43-4/43-5/43-6 pattern**. Two content types (the audio-package + final-handoff review surfaces).

## Story

At **G4B (input-package preview)** and **G5 (final handoff)**, show the package / handoff artifacts as a table instead of the generic dump.

## T1 required readings

- `app/marcus/cli/hil_tabular_projector.py` — registry + bridge + the landed bespoke renderers (pattern) + `_md_table`/`_truncate_cell` + allowlist.
- `app/gates/section_11b/poll_surface.py::display_input_package` (:77).
- `app/gates/section_15/poll_surface.py::display_final_handoff` (:79).
- **Per 43-4's lesson:** verify each poll_surface's model binding vs the real paused card (check on-disk evidence cards; woken pause set = G0E/G0R/G0S/G1/G2B/G2C/G3/G4/G4A — G4B/G5 may not be woken). Target the real card body; file any genuine field-absent mismatch (don't fix).
- `tests/marcus/cli/test_plan_unit_estimator_constants_renderers_43_5.py` (test pattern); TW-7c-4 Epic-43 block; fixtures README.

## Acceptance criteria

**AC-1 — two renderers**, registered under canonical keys:
- `render_input_package` → `"input_package"` (G4B): table the input-package artifact paths / fields (per section_11b).
- `render_final_handoff` → `"final_handoff"` (G5): table the handoff artifacts + summary (per section_15).
Reuse `_md_table`/`_truncate_cell`; tolerate nested-display + bare-payload; name each gate ("G4B input-package preview", "G5 final handoff") in tests.

**AC-2 — bridge entries** for G4B, G5 in `GATE_TO_CONTENT_TYPE` (discover real gate identifiers). Routing tests prove each fixture reaches its renderer.

**AC-3 — two synthetic fixtures** built from the REAL card model/body. README notes.

**AC-4 — ratchet moves.** Remove `input_package`, `final_handoff` from `KNOWN_UNRENDERED_ALLOWLIST`; update the ratchet state-pin + the 43-3 bridge exact-map pin, in lockstep. Green.

**AC-5 — invariants.** stdout/stderr split; additive-within-v1; projector stdlib-pure; TW-7c-4 register new test .py file; ruff + import-linter clean; no manifest touch.

## Test / process

- New test file under `tests/marcus/cli/`; routing + shape tests; ratchet green; TW-7c-4 scope test green. Use `-n 0`. Do NOT run the full suite. Do NOT commit or stash.

## Definition of done

Two renderers registered + tabling their fixtures; each gate routes correctly; both moved allowlist→registry with 43-10 green; any model-binding mismatch filed (not fixed); TW-7c-4 registered; ruff/import-linter clean; ready for orchestrator review → `bmad-code-review`.
