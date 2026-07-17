# Story 43-7 — Motion-plan + motion-clip renderers

**Epic:** 43 · **Slab:** 3 (sequenced LATE — rider R6, low-frequency gates) · **Status:** ready-for-dev · **Gate mode:** dual-gate.

Follows the **43-3…43-6 pattern**. Two content types on the motion band.

## Story

At **G2.5 (motion-plan status)** and **G2F (motion-clip)**, show the motion plan / clip review as a table instead of the generic dump.

## T1 required readings

- `app/marcus/cli/hil_tabular_projector.py` — registry + bridge + landed renderers (pattern) + `_md_table`/`_truncate_cell` + allowlist.
- `app/gates/section_07d/poll_surface.py::display_motion_plan_status` (:81).
- `app/gates/section_07f/poll_surface.py::display_motion_clip` (:73).
- **43-4 lesson:** verify model binding vs the real paused card (check evidence cards; note G2F folds into `G3` per the manifest — as 43-6 found; target the real card body; file only genuine field-absent mismatches).
- `tests/marcus/cli/test_build_target_renderers_43_6.py` (test pattern); TW-7c-4 Epic-43 block; fixtures README.

## Acceptance criteria

**AC-1 — two renderers**: `render_motion_plan` → `"motion_plan"` (G2.5), `render_motion_clip` → `"motion_clip"` (G2F). Reuse `_md_table`/`_truncate_cell`; tolerate nested-display + bare-payload; name each gate ("G2.5 motion-plan status", "G2F motion-clip") in tests.

**AC-2 — bridge entries** (discover real gate identifiers; G2F folds to `G3` — key by surface_id, leave `G3` unmapped as 43-6 already pinned). Routing tests.

**AC-3 — two synthetic fixtures** from the REAL card/model. README notes.

**AC-4 — ratchet moves.** Remove `motion_plan`, `motion_clip` from `KNOWN_UNRENDERED_ALLOWLIST`; update the ratchet state-pin + the 43-3 bridge exact-map pin, in lockstep. Green.

**AC-5 — invariants.** stdout/stderr split; additive-within-v1; projector stdlib-pure; TW-7c-4 register new test .py file; ruff + import-linter clean; no manifest touch.

## Test / process

- New test file under `tests/marcus/cli/`; routing + shape tests; ratchet green; TW-7c-4 scope test green. Use `-n 0`. Do NOT run the full suite. Do NOT commit or stash.

## Definition of done

Two renderers registered + tabling their fixtures; each routes correctly; both moved allowlist→registry with 43-10 green; any mismatch filed (not fixed); TW-7c-4 registered; ruff/import-linter clean; ready for orchestrator review → `bmad-code-review`.
