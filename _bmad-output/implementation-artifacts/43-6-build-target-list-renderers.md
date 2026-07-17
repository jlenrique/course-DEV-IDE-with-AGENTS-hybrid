# Story 43-6 — Build-target list renderers (literal-visual, storyboard, G3B)

**Epic:** 43 · **Slab:** 3 · **Status:** ready-for-dev · **Gate mode:** dual-gate.

Follows the **43-3/43-4 pattern**. Three content types (build-target lists the operator reviews mid-deck).

## Story

At **06B (literal-visual build targets)**, **07C (storyboard build targets)**, and **G3B (storyboard-B / live-URL review)**, show each target list as a table instead of the generic dump.

## T1 required readings

- `app/marcus/cli/hil_tabular_projector.py` — registry + bridge (`GATE_TO_CONTENT_TYPE`/`resolve_content_type`) + the 43-3/43-4 bespoke renderers (pattern) + `_md_table`/`_truncate_cell` + allowlist.
- `app/gates/section_06b/poll_surface.py::display_literal_visual_targets` (:90).
- `app/gates/section_07c/poll_surface.py::display_storyboard_targets` (:92).
- `app/gates/section_08b/poll_surface.py::display_storyboard_b` (:73).
- **Per 43-4's lesson:** confirm each poll_surface's model binding matches the card that actually flows at the paused gate — check any on-disk evidence card (`state/config/runs/**/decision-card-*.json` or `_bmad-output/**/evidence/**`) and target the renderer at the REAL paused-card body. If a poll_surface binds a different model than the paused card, target the real card body and FILE the mismatch (as 43-4 did) — do not fix it here.
- `tests/marcus/cli/test_voice_candidates_renderer_43_4.py` (test pattern); TW-7c-4 Epic-43 block; fixtures README.

## Acceptance criteria

**AC-1 — three renderers**, registered under canonical keys:
- `render_literal_visual` → `"literal_visual"` (06B): one row per slide target.
- `render_storyboard_targets` → `"storyboard_targets"` (07C): one row per storyboard slide.
- `render_storyboard_b` → `"storyboard_b"` (G3B): the G3 card review (storyboard/live-URL fields).
Reuse `_md_table`/`_truncate_cell`; tolerate nested-display + bare-payload; name each gate in tests.

**AC-2 — bridge entries** for the three gates in `GATE_TO_CONTENT_TYPE` (discover the real gate identifiers from the poll_surfaces / evidence cards). Routing tests prove each fixture reaches its renderer.

**AC-3 — three synthetic fixtures**, generated from the REAL card/model that flows at each paused gate (not necessarily the poll_surface's declared type — see 43-4's lesson). README notes.

**AC-4 — ratchet moves.** Remove `literal_visual`, `storyboard_targets`, `storyboard_b` from `KNOWN_UNRENDERED_ALLOWLIST`; update the ratchet state-pin (and the 43-3 bridge exact-map pin, in lockstep). Green.

**AC-5 — invariants.** stdout/stderr split; additive-within-v1; projector stdlib-pure; TW-7c-4 register new test .py file(s); ruff + import-linter clean; no manifest touch.

## Test / process

- New test file(s) under `tests/marcus/cli/`; routing + shape tests; ratchet green; TW-7c-4 scope test green. Use `-n 0`. Do NOT run the full suite. Do NOT commit or stash.

## Definition of done

Three renderers registered + tabling their fixtures; each gate routes correctly; all three moved allowlist→registry with 43-10 green; any model-binding mismatch filed (not fixed); TW-7c-4 registered; ruff/import-linter clean; ready for orchestrator review → `bmad-code-review`.
