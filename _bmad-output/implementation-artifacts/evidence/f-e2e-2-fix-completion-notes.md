# F-E2E-2 fix — completion notes

**Defect (from epic-35 story-35.7 party review + evidence/hud-35-7-e2e-witness/FINDINGS.md F-E2E-2):**
during the production walk the operator-surface assembler emitted
identity/envelope/next_action/steps/decision_card but NEVER `health`,
`specialists`, `modalities`, or `trace`. Result: the HUD's health strip (FR9),
specialist chips (FR7), modality chips (FR10), and state-trace well (FR8) were
EMPTY mid-run, and the witness-mode lifecycle invariant
("status=in-flight requires the health section") fired on every in-flight emit.
Root cause: the assembler had section-update APIs but the production runner
never CALLED them during the walk (and had no API for specialists/modalities).

## Files changed

1. `app/marcus/orchestrator/operator_surface_assembler.py`
   - New import of `ModalitiesSection`, `SpecialistEntry`, `SpecialistsSection`.
   - New public method **`update_ambient(*, health_tiles, specialist_roster, modalities, trace_event)`** —
     refreshes the health strip / specialist roster / modality readings and
     appends one trace event in **ONE** non-progress `_merge_write`
     (`progress=lambda prev: False`, `require_prev=True`). A `None` argument
     leaves that section untouched (prev preserved); a present-but-empty list
     still writes the (empty) section so an early run renders present-but-empty,
     never null. All-`None` is a no-op. Wrapped so no exception escapes into the
     walk (greenlight amendment 8). `update_health`/`append_trace` were left
     intact (still used by the 35.2 tests).

2. `app/marcus/orchestrator/production_runner.py`
   - New ambient builders (all guarded, zero-lie, never raise into the walk):
     - `_operator_surface_cost_reading` — cost for the health tile: prefers
       persisted `cost-report.json` total, else the **live accumulated
       per-contribution spend** off `run_state.production_envelope.contributions`
       (a real known partial mid-walk). confidence=`proxy`.
     - `_operator_surface_health_tiles` (FR9) — a `run cost` tile (USD) plus
       `openai quota` / `gamma quota` tiles set `value="unknown"`,
       `confidence="unknown"`, `threshold_state="unknown"` (never-false-green:
       platform quota is not cheaply known mid-walk).
     - `_operator_surface_specialist_roster` (FR7) — one `SpecialistEntry` per
       specialist aggregated from envelope contributions (name, status
       `contributed`, current_node + model from the most recent contribution,
       summed cost). Empty until the first contribution; a bounded display
       projection (AD-16).
     - `_operator_surface_styleguide` + `_operator_surface_modalities` (FR10) —
       `llm_execution_mode` from `run_state`; detective disposition from
       `research_detective_gate.load_disposition` / `landing_path` sidecars;
       styleguide name(s) + provenance from the run's `directive.yaml`
       (`gamma_settings[].styleguide`, `styleguide_picker_provenance`).
     - `_refresh_operator_surface_ambient(...)` — the wrapper that constructs an
       assembler and calls `update_ambient` with the three built sections + an
       optional trace event. Double-guarded.

## Where each section is wired (walk points)

Start walk (`run_production_trial`):
- **Pre-persist ambient refresh** — inserted immediately BEFORE the
  `registered -> in-flight` `model_copy` + `_persist_envelope`, right after
  `run_state` is constructed. This is the key ordering: it establishes `health`
  (and specialists/modalities/trace) while the projection is still `registered`
  (lifecycle-exempt), so the in-flight emit's read-merge-write INHERITS a present
  health section and the "requires the health section" invariant never fires.
- **Per-node refresh** — inside the walk loop, right after the existing
  `_emit_operator_surface_steps(...)`, with `trace_event=("node-enter", node.id)`,
  so the cost tile / specialist chips / trace well grow as the walk progresses.

Continuation walk (`_run_continuation_walk`, resume/recover body):
- **Pre-loop refresh** — before the `_continue_assembler` freshness-tick block,
  with `trace_event=("walk-continue", "resuming at index N")` (run_state was
  rehydrated from the checkpoint, so its contributions/modes are known).
- **Per-node refresh** — inside the continuation loop after the steps emit
  (two-walk parity; the HUD must not go empty after a resume/recover).

Ambient refreshes bump `seq` but never `progress_seq` (AD-10) — the per-node
`_emit_operator_surface_steps` retains sole ownership of progress advance.

## Data sourcing summary

| Section | Source | Missing-data behavior |
|---|---|---|
| health (FR9) | `cost-report.json` else live `contributions` cost sum; platform tiles | cost tile present (0.0 floor); platform tiles `unknown` (never green) |
| specialists (FR7) | `run_state.production_envelope.contributions` | empty roster until first contribution |
| modalities (FR10) | `run_state.llm_execution_mode`; detective sidecars; `directive.yaml` styleguide | omit field; whole section `None` if nothing resolvable |
| trace (FR8) | node-enter / walk-start / walk-continue boundaries | ring-buffer bounded by the contract (cap 200) |

## In-flight lifecycle warning — cleared

Yes. Because the pre-persist refresh sets `health` while `status="registered"`
(exempt), the in-flight transition emit reads a prior projection that already
carries health and re-serializes an in-flight projection with health present —
so the witness-mode `"status=in-flight requires the health section"` violation no
longer fires for in-flight/paused steady state (`steps` is likewise already set
by the existing index-0 steps emit). On resume/recover the on-disk projection
still carries health from the start walk, so re-emits preserve it. Confirmed by
`test_ambient_health_at_registered_clears_in_flight_witness_warning` and
`test_refresh_wrapper_populates_projection_and_clears_warning`.

## Test approach + results

Full-walk fixtures are too heavy for a unit test, so (per the task's sanctioned
fallback) the new tests drive `update_ambient` and the `production_runner`
ambient builders + `_refresh_operator_surface_ambient` wrapper directly with a
STUB run state (`SimpleNamespace` envelope + contributions), which exercises
exactly the emission wiring F-E2E-2 changed.

New file: `tests/unit/marcus/orchestrator/test_operator_surface_ambient_f_e2e_2.py` (17 tests):
- assembler `update_ambient`: all-four-sections populate; not-a-progress-event
  (seq bumps, progress_seq flat); None-arg preserves prior section;
  empty-roster writes present-but-empty; all-None no-op; never-raises on bad tile.
- witness warning: baseline in-flight-without-health fires it; ambient health at
  registered clears it across the in-flight transition; health preserved across a
  paused-at-gate emit (no re-warn).
- production_runner builders: roster aggregation; empty roster; live-cost +
  unknown platform tiles; persisted-cost-report preference; modalities from
  run_state + directive + detective receipt; modalities None when nothing
  resolvable.
- wrapper: populates projection + clears warning (production order);
  no-prior-projection is a safe no-op (require_prev skip).

Results (all green, `.venv/Scripts/python.exe`):
- `tests/unit/marcus/orchestrator` — **231 passed** (17 new + existing 35.2 suite intact).
- `tests/unit/models/test_operator_surface_shape_pin.py` + `tests/contracts/test_operator_surface_parity.py` + `tests/hud` + `tests/notify` — **220 passed** (no regression on the broader operator-surface / HUD / notify contract surface).
- `ruff check` (both source files + new test) — clean.
- `lint-imports` (import-linter) — **18 kept, 0 broken** (HUD1/HUD2 layer contracts intact).
- `check_pipeline_manifest_lockstep.py` — **exit 0** (both owned files are block_mode trigger paths; no manifest/pack/step-list change, so lockstep stays green).

## Tests created/modified (for zero-test-edits guard allowlisting)

- CREATED: `tests/unit/marcus/orchestrator/test_operator_surface_ambient_f_e2e_2.py`
- (no existing test files modified)

## Deviations / notes

- Added a single combined `update_ambient` method rather than separate
  `update_specialists` / `update_modalities` methods (the task allowed a section
  API tweak). Rationale: one merge-write per refresh instead of three+ minimizes
  os.replace contention on Windows and keeps the four ambient sections cohesive;
  existing `update_health`/`append_trace` are untouched.
- Platform (OpenAI/Gamma) quota tiles are rendered as explicit `unknown` rather
  than omitted, so the health strip is visibly populated AND honestly signals
  "no quota telemetry wired" — consistent with the never-false-green invariant.
  Straightforward to swap for real quota readings later without touching the walk.
- `tests/contracts/test_30_1_zero_test_edits.py` intentionally NOT touched (owned
  by the orchestrator to reconcile the allowlist with the new test file above).
