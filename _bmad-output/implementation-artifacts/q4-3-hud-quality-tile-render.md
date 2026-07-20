# Story Q4.3 — HUD quality-tile render

**Epic:** Q4 — Quality Scorecard Live-Wiring (R2) · **Status:** ready-for-dev (after Q4.1) · **Gate mode:** single-gate (additive HUD render of an existing contract section) · **Green-light:** `_bmad-output/planning-artifacts/epic-q4-party-greenlight-2026-07-20.md` (QLW-1…QLW-16).

## Why this story exists (settled during Q4.1)

The Q4.1 survey confirmed the HUD does **NOT** auto-render present optional operator-surface sections — two explicit mechanisms drop an un-enumerated section:
- `app/hud/public.py::build_public_view` is a **positive allowlist** (`_copy_allowed` per section + `ALLOWED_*` tuples) — an un-enumerated `quality` section is silently dropped from the public view.
- `app/hud/render/page.py` renders each optional section via a **dedicated per-section function** (`_run_settings_panel`, `_decision_card`, the deliverables block) — there is no generic optional-section renderer.

So the `quality` tile (shipped in Q4.1 on `operator-surface.json`) needs explicit HUD wiring: an allowlist entry + a render panel.

## ⛔ T1 Readiness (read BEFORE any code — block-mode story)

`app/hud/**` and `tests/hud/**` are **`block_mode_trigger_paths`**. Required T1 readings:

1. [`docs/dev-guide/pipeline-manifest-regime.md`](../../docs/dev-guide/pipeline-manifest-regime.md) — block-mode regime; lockstep exit 0 at closure (orthogonal — passes trivially; the HUD tests are the real arbiters).
2. `app/hud/public.py` — `build_public_view`, `_copy_allowed`, the `ALLOWED_*` tuples. Mirror how an existing optional section (`run_settings` / `decision_card` / `deliverables`) is allowlisted.
3. `app/hud/render/page.py` — the per-section render functions (`_run_settings_panel`, `_decision_card`, the deliverables block). Mirror one for `quality`.
4. The Q4.1 contract: `app/models/runtime/operator_surface.py::QualitySection` (fields: `available`, `band`, `ranked_leak_count`, `top_leaks`, `coverage_gaps`, `trend`, `scorecard_as_of`, `as_of`) — **read-only consumer**; do NOT modify it.
5. `tests/hud/**` — the HUD public-view + render test patterns you extend.

## Story

**As** the operator watching the HUD flight deck, **I want** the `quality` tile rendered (Band + top leaks + trend + how stale the scorecard is), **so that** the honest quality read is visible on the deck, not just in the JSON / the standalone report.

Read-only consumer of the Q4.1 contract — no scoring, no contract change.

## Scope fence (binding)

**IN SCOPE:** (a) allowlist the `quality` section in `app/hud/public.py`; (b) a `_quality_panel` (or equivalent) render function in `app/hud/render/page.py`; (c) HUD tests.

**OUT OF SCOPE / FORBIDDEN:** modifying `QualitySection` / the operator-surface contract / schema (Q4.1); touching `production_runner.py` (Q4.2) or `operator_surface_assembler.py`; recomputing any quality value in the HUD (the HUD renders what is in `operator-surface.json`, it NEVER recomputes — QLW-4); any schema_version/pack bump; a live trial.

## Acceptance Criteria

**AC1 (allowlist passthrough).** `build_public_view` exposes the `quality` section (allowlist entry mirroring `run_settings`/`decision_card`), copying its honest fields. A test asserts the section survives `build_public_view` (previously dropped).

**AC2 (render panel).** A dedicated render function renders the tile on the deck: Band + top-N leaks + trend + `ranked_leak_count`/`coverage_gaps` + the `scorecard_as_of` staleness stamp. Mirrors the existing per-section panels.

**AC3 (QLW-8 zero-lie / fail-soft render).** `available=False` (or the section absent) → the panel renders an explicit honest "quality: unavailable" state, NEVER silent-absence-reads-green and NEVER a fabricated Band. A malformed/None/partial `quality` section must NEVER crash the HUD render (fail-soft, mirror the existing panels' guards). RED-first pin on the unavailable + malformed render.

**AC4 (QLW-4 — HUD never recomputes).** The panel renders ONLY values present on the operator-surface `quality` section; it does NOT import `app.quality` or recompute anything. A test asserts no `app.quality` import on the HUD render path.

**AC5 (QLW-12 — calibration honesty on the deck).** The rendered Band/leaks reflect the tile's honest posture (including the OWED/uncalibrated calibration read); never a fresh-naive number.

**AC6 (block-mode closure).** `check_pipeline_manifest_lockstep.py` exit 0; `tests/hud/**` + public-view tests green (incl. the new allowlist + panel + fail-soft pins); ruff + import-linter clean; no prior-HUD regression.

## RED-first task hints

T1: readings. T2: allowlist the section in public.py (RED: passthrough test fails until added). T3: the render panel in page.py. T4: pins — unavailable/malformed fail-soft render, no-app.quality-import guard, allowlist passthrough. T5: lockstep + full HUD suite + ruff + import-linter.

## Notes for the dev agent

- Read-only consumer of the Q4.1 `QualitySection`. Do NOT touch the contract, the assembler, or production_runner.
- 3-layer adversarial review (Blind/Edge/Acceptance) follows dev (QLW-15).
- The LIVE HUD tile witness rides the operator R2 trial (`q4-2-r2-hud-quality-tile-witness`); do NOT run a live trial.
