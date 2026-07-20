# Story Q4.1 — Operator-surface `quality` tile

**Epic:** Q4 — Quality Scorecard Live-Wiring (R2) · **Status:** ready-for-dev · **Gate mode:** single-gate (additive contract extension on proven precedents) · **Green-light:** `_bmad-output/planning-artifacts/epic-q4-party-greenlight-2026-07-20.md` (QLW-1…QLW-16).

## ⛔ T1 Readiness (read BEFORE any code — block-mode story)

`app/models/runtime/operator_surface.py`, `app/marcus/orchestrator/operator_surface_assembler.py`, and `app/models/schemas/operator-surface.v1.schema.json` are **`block_mode_trigger_paths`** (pipeline-manifest). Required T1 readings:

1. [`docs/dev-guide/pipeline-manifest-regime.md`](../../docs/dev-guide/pipeline-manifest-regime.md) — the block-mode regime. Cora's pre-closure hook runs `check_pipeline_manifest_lockstep.py` (must exit 0 — it is **orthogonal** to operator-surface, so it passes trivially provided you do NOT model the tile as a manifest node/step). The **real arbiters are the shape-pin + parity tests** — both must be green in your completion notes.
2. The precedent optional sections in `operator_surface.py` — **`deliverables`, `run_settings` (42.3), `decision_card` (35.9)** — additive-within-v1 optional sections. Mirror them exactly.
3. `app/quality/report.py` (`render_scorecard_final_report`, `ranked_project_leaks(block)`, `leak_coverage_gaps(block)`), `app/quality/scorecard.py` (`read_scorecard_block()`, `dimension_ref()`, `_EXPECTED_CANONICAL_DIMENSION_KEYS`), `app/quality/history.py` (trend read). These are a GL-3 **clean leaf** (stdlib+yaml at module scope; app.* via deferred imports; a recursive AST guard enforces it).
4. `tests/unit/models/test_operator_surface_shape_pin.py` + `tests/contracts/test_operator_surface_parity.py` — the byte-pin + `extra="forbid"` parity discipline you must extend.
5. `docs/dev-guide/quality-scorecard-dimension-authoring.md` (the scorecard read patterns) + the Q4 greenlight (QLW list).

## Story

**As** the operator steering a paid Marcus-SPOC run, **I want** a compact, honest quality read (Band + top leaks + trend) on the per-run operator surface at run-end, **so that** at the accept/reject/edit decision moment I can see *"is THIS run trustworthy, and where are its load-bearing leaks?"* — without opening the full report.

This story adds the `quality` tile to the operator-surface contract and populates it from the sole-writer assembler. It is **wiring + a typed tile, NOT new scoring logic** (GL-15 no-parallel-plumbing): the readers/projector already exist and are tested (507 green).

## Scope fence (binding)

**IN SCOPE:** (a) a new OPTIONAL `QualitySection` on `OperatorSurfaceProjection` (additive-within-v1); (b) regenerated `operator-surface.v1.schema.json` byte-pin; (c) assembler self-populates the section at the completion choke-point via a deferred `app.quality` import.

**OUT OF SCOPE / FORBIDDEN:** redefining the 8 dimensions / weights / thresholds / scoring math; adding any pipeline step/gate/event_type; editing `pipeline-manifest.yaml` steps, the v4.2 pack, the generator, `PIPELINE_STEPS`, or `frozen-pack-shas.json`; bumping `schema_version` (v1 stays v1); editing `block_mode_trigger_paths` (already registered); the standalone `quality-final-report.md` (that is Q4.2); recomputing dimension levels via `app.quality.signals.*` at emit time (QLW-4). If the additive field cannot land without a breaking change → **33-1 kill-switch: stop, escalate, re-round.** Do NOT silently escalate to v2.

## Acceptance Criteria

**AC1 (QLW-7 — tile shape, NO /100 score).** `QualitySection` (a `_Section` subclass carrying the standard `as_of` read-stamp) declares ONLY these substantive fields, all optional/None-able: `available: bool`; `band: str | None` (the **worst band across all present dimensions** — never paint the best dimension over a redder sibling); `ranked_leak_count: int | None` (`len(ranked_project_leaks(block))`); `top_leaks: list[str]` (default `[]`; top-N ranked leak labels — lane + slug + dimension); `coverage_gaps: int | None` (`len(leak_coverage_gaps(block))`); `trend: str | None`. **No `/100` numeric score** (contradicts `report.py`'s deliberate no-false-precise-headline design). The band-aggregation rule (worst-across-dimensions) is documented in the model docstring.

**AC2 (QLW-4 — reads the COMMITTED doc, deterministic).** The assembler populates the tile from `read_scorecard_block()` / `scorecard.dimension_ref()` (the committed machine-block in `docs/quality/project-quality-scorecard.md`) + `ranked_project_leaks`/`leak_coverage_gaps` + the history trend read. It MUST NOT call `app.quality.signals.*` (live env/import-linter/inventory posture). Substantive per-dimension values carry the doc's committed `as_of`; only the section's own read-stamp uses `now()`. A test asserts no `app.quality.signals` symbol is referenced by the tile path.

**AC3 (QLW-1/QLW-3 — sole-writer assembler, completion choke-point, both walks).** The assembler self-populates `quality` via a **deferred local import** of `app.quality` (mirroring the assembler's existing `next_action`/`TrialEconomicsReport` deferred imports), at the **same verb-conditional completion choke-point `deliverables` uses** — so it rides `emit()` in BOTH node walks with zero duplication and NEVER renders at the G1 start-walk pause. A test exercises both the completion path (tile present) and a non-terminal/pause path (tile absent or `available=False`, never a "completed" posture).

**AC4 (QLW-8 — zero-lie / fail-soft, non-negotiable).** A missing/degraded scorecard block (`read_scorecard_block()` → None/degraded) → the section is STILL emitted with `available=False` and null posture (never silent-absence, never a fabricated band). Any exception in the tile path is swallowed (mirror the assembler's amendment-8 swallow + the `_emit_operator_surface` wrapper) and NEVER perturbs the walk. `unknown == None` at both the section level (`quality: QualitySection | None = None`) and per-field level, so `extra="forbid"` + bidirectional required/optional parity hold (the fields must NOT appear in the schema `required` list). RED-first fail-soft pin: inject absent block + a corrupt read → walk unperturbed, `available=False`, zero fabricated value.

**AC5 (QLW-5/QLW-11 — additive-within-v1 contract lockstep, one commit).** The coupled file set lands in ONE commit: `operator_surface.py` (the `QualitySection` + optional field) · regenerated `operator-surface.v1.schema.json` (byte-pin; **NO `schema_version` bump** — the value literal stays `"v1"`) · `operator_surface_assembler.py` · `tests/contracts/test_operator_surface_parity.py` (add to `_SECTION_DEFS`) · `tests/unit/models/test_operator_surface_shape_pin.py` (new-section-defaults-to-None pin + additionalProperties:false coverage). Add a **lenient-reader back-compat test** (a pre-quality v1 surface still parses — mirror `test_back_compat_pre_42_3_modalities_only_surface_still_parses`). If the tile carries a closed vocabulary (a band enum), re-declare it VERBATIM in model `Literal` + schema `enum` + a set-equality test; else use free `str` (no over-constraint).

**AC6 (QLW-9 — no-Band-better-than-committed adversarial pin).** RED-first: feed a scorecard block with `open_leaks > 0` / a redder dimension → assert the tile's `band` can never render a clean/higher posture than the committed block's worst dimension. A regression that paints the best band over a redder sibling must RED.

**AC7 (QLW-12 — calibration honesty).** The tile renders the calibration dimension's OWED/uncalibrated posture honestly (weak/`None`), and NEVER a fresh-naive number. (Consistency with Q3.4.)

**AC8 (QLW-13 — block-mode closure).** `check_pipeline_manifest_lockstep.py` exits 0 (trivially); the shape-pin + parity + lenient-back-compat + clean-leaf-no-import tests are all green and cited in the completion notes; ruff + import-linter clean; the full `tests/quality/` + operator-surface test suites green with no prior-surface regression.

## RED-first task hints

- T1: readings above. T2: author `QualitySection` in `operator_surface.py` + wire the optional field (RED: shape-pin/parity fail until schema regenerated). T3: regenerate the JSON schema byte-pin. T4: assembler `_quality_dict` (deferred `app.quality` import; band=worst-across-dims; committed-doc read; fail-soft). T5: the pins — fail-soft, no-Band-inflation, both-walks/not-at-pause, no-signals-recompute, lenient back-compat, clean-leaf no-import. T6: ruff + import-linter + full suite; completion notes cite shape-pin/parity green.

## Notes for the dev agent

- **Report back whether Q4.3 (HUD render) is needed:** does the HUD (`app/hud/**`) auto-render present optional operator-surface sections, or does the `quality` tile need explicit per-section render wiring + tests? If it auto-renders, Q4.3 collapses into this story; if not, keep Q4.3 separate.
- Do NOT touch `production_runner.py` here (that is Q4.2) — Q4.1 and Q4.2 are disjoint block-mode surfaces and parallelize.
- 3-layer adversarial review (Blind/Edge/Acceptance) follows dev, per QLW-15.
