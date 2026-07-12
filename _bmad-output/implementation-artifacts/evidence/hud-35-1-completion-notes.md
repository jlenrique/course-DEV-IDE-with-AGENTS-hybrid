# Story 35.1 — Operator-surface contract package — Completion Notes

**Date:** 2026-07-11 · **Dev agent:** fresh Claude dev agent (formal `bmad-dev-story`) · **Branch:** `dev/hud-revival-2026-07-11` · **No commits made** (working tree only, per dispatch; orchestrator commits post-review).

## Files created (all new — story owns all four)

| File | Role |
|---|---|
| `app/models/runtime/operator_surface.py` | Contract package: strict `OperatorSurfaceProjection` v1, `read_operator_surface_lenient` + `Unrecognized`, `derive_event_transitions` + `stall_condition`, `HudConfig` + `load_hud_config` + `HUD_CONFIG_DEFAULTS`, `operator_surface_schema_text()` / `emit_operator_surface_schema()` (AD-1/3/4/5/16/18/19) |
| `app/models/schemas/operator-surface.v1.schema.json` | Committed emitted schema — AD-4a byte-pin source (23,705 bytes) |
| `tests/unit/models/test_operator_surface_shape_pin.py` | Byte-identical pin + structural asserts + strict-model rejections + witness/strict lifecycle tests (decision-card pattern) |
| `tests/contracts/test_operator_surface_parity.py` | Field presence, enum parity incl. AD-5 L1 set-equality, round-trip per status, bidirectional required/optional, lenient-reader fixtures, event goldens, caps, size tripwire, HudConfig loader (lesson-plan pattern) |

No existing files were modified (deliberately did NOT touch `app/models/runtime/__init__.py` — consumers import `app.models.runtime.operator_surface` directly; keeps the diff inside story ownership).

## T1 readings completed (in dispatch order)

pipeline-manifest-regime.md · epic-35-stories §35.1 · epics-operator-hud Story 35.1 AC · ARCHITECTURE-SPINE AD-1/3/4/5/10/15/16/17/18/19 · pydantic-v2-schema-checklist (14 idioms) · `test_decision_card_shape_pin.py` + `decision_card_schema_text` emitter (`app/models/decision_cards/vocabulary.py:76`) · `test_lesson_plan_json_schema_parity.py` · `production_trial_envelope.py` (status vocabulary + `_lifecycle_invariants` witness pattern) · EXPERIENCE.md §Projection Demands + §Notifications · brief addendum §E config sketch.

## Field inventory (v1, strict `extra="forbid"` + `validate_assignment=True` throughout)

**Top level:** `schema_version: Literal["v1"]` · `seq: int ≥0` (write counter, feeds ETag) · `progress_seq: int ≥0` + `last_progress_at` (AD-10 watchdog pair) · `envelope_digest: str` (AD-17) · `as_of` (all datetimes tz-aware via shared `enforce_tz_aware`).

| Section | Presence | Fields |
|---|---|---|
| `identity` | always | `trial_id` (UUID4-enforced), `lesson`, `preset` (`production\|explore`), `operator_id`, `as_of` |
| `envelope` | always | `status` (seven verbatim literals), `paused_gate`, `paused_error_tag`, `waiting_batch_id`, `completed_at`, `as_of` |
| `notifications_echo` | always | `config: HudConfig`, `parse_status`, `as_of` (AD-9/19 echo) |
| `next_action` | paused statuses | `command` (exact CLI string, verbatim), `pause_class` (3-literal subset of status vocab), `as_of` |
| `steps` | post-registered | `manifest_digest`, `node_count`, `walk_index`, `walk_generation`, `reentered_from`, `entries[]` (step_id/label/`stage-1\|stage-2`/status/conditions/blockers/locked_artifact_summary), `as_of` |
| `preflight` | optional | `items[]`: name, `state` (`pending\|running\|pass\|fail\|missed` — **`missed` ≠ `fail`**), output, latency_ms, quota_reading, `quota_confidence` (`direct\|proxy\|unknown`), `as_of` |
| `health` | post-registered | `tiles[]`: label, value (`float\|str`), unit, confidence, `threshold_state` (`nominal\|warning\|breached\|unknown`), per-tile `as_of`, `history[]` ≤50 (trim-not-raise), `as_of` |
| `specialists` | optional | `roster[]`: name, status, current_node, model, last_artifact, cost_usd, `as_of` |
| `modalities` | optional | `llm_execution_mode`, `detective_disposition`, `styleguide`, `styleguide_provenance`, `as_of` |
| `trace` | optional | `events[]` ≤200 ring (trim-not-raise): at/event/detail, `as_of` |

## Key design decisions

1. **Status literal re-declared verbatim, not imported.** The AD-5 L1 set-equality test against `ProductionTrialStatus` would be a tautology if the contract imported the envelope's Literal. Re-declaration + `get_args` set-equality makes the parity test a real tripwire (plus the 35.0 reverse trigger-path tripwire on the envelope file).
2. **Envelope section is structurally required at `registered` (documented deviation from a literal reading of the §35.1 inventory).** The stories file says "at registered only identity+notifications_echo mandatory," but `envelope.status` IS the lifecycle discriminator, and greenlight amendment 12 pins pre-envelope exits as "projection at `registered`" — an unrenderable status-less projection would violate zero-lie. The envelope section simply reads `status="registered"` with all pause fields None before the runtime envelope exists. Rationale in the model docstring.
3. **Lifecycle presence rules: witness-by-default, strict-via-context** — exact mirror of `production_trial_envelope._lifecycle_invariants` (Dr. Quinn "witness, don't gate"). Violations checked: non-registered requires steps+health; paused statuses require next_action; pause-metadata coupling (paused_gate / paused_error_tag / waiting_batch_id / completed_at) mirrors the envelope's own invariants. `context={"invariant_mode": "strict"}` raises; default logs.
4. **Lenient reader = strip-then-validate.** Recursive annotation-driven strip (`Union`/`list`/`dict`/nested-model aware) removes unknown ADDED keys at any depth, then validates with the strict model (witness mode → presence violations never raise on the consumer path). Unknown `schema_version` and unknown `envelope.status` are checked BEFORE strip/validate so `Unrecognized` carries the typed reason. Whole body wrapped in a catch-all: no input of any type raises (fixtures cover garbage bytes, truncated JSON, non-object JSON, empty bytes/str, BOM'd input).
5. **`run_stalled` is in the vocabulary, never in derivation.** `EVENT_CLASSES` carries all five classes; `derive_event_transitions` derives the four transition-derivable ones; a stall is the *absence* of writes — invisible to a `(prev, cur)` pair — so the watchdog (35.6) evaluates the companion pure predicate `stall_condition(cur, now, budget_seconds)` (in-flight only; `waiting_for_provider_batch` exempt by status; naive `now` rejected).
6. **Derivation edge semantics (documented in docstring, pinned by goldens):** `prev=None` + paused status fires (first observation of a paused run is alert-worthy; the notifier's AD-9 ack state file dedupes across restarts); `batch_pause_resumed` is transition-only (`prev=None` cannot fire it, per AD-9); `health_threshold` needs a baseline (prev tile by label; fires on entering `warning`/`breached` from a different state; at most once per call); repeated same-status snapshots never refire; output order deterministic.
7. **`HudConfig` frozen value-object; defaults defined exactly once** (`HUD_CONFIG_DEFAULTS`). Notification matrix defaults follow the EXPERIENCE.md §Notifications table (which supersedes the brief-addendum §E sketch's `health_threshold: enabled=false` — EXPERIENCE says on-HUD only ⇒ `enabled=True, sound=False, push=False`); `staleness_budget_seconds=5`, `stall_budget_seconds=600`, `hud_port=8791` (AD-6 [ASSUMPTION]). Loader never raises: missing/unparseable/non-mapping/invalid → `(HUD_CONFIG_DEFAULTS, reason-string)`; partial notification matrices **merge over defaults** (a one-class override never silently disables the rest); `hud: {port: N}` nesting normalized onto `hud_port`.
8. **Ring caps trim, never raise** (`field_validator` keeps newest N; re-trims on assignment via `validate_assignment`). `TRACE_RING_CAP=200`, `HEALTH_HISTORY_CAP=50` per AD-16.
9. **Schema emitter mirrors the decision-card pattern byte-for-byte** (`json.dumps(model_json_schema(), indent=2, sort_keys=True) + "\n"`, written `newline="\n"`).
10. **Import purity:** direct imports are `pydantic`, stdlib, `yaml` (config loader), and `app.models.state._base` (the shared tz/UUID4 validator helpers — pure stdlib). Runtime check confirmed importing the module loads zero `app.marcus`/`app.hud`/`app.notify` modules.

## Pydantic-v2 checklist conformance (the 14 idioms)

#1 `extra="forbid"` + `validate_assignment=True` on every model (frozen for the two config value-objects) · #2 tz-aware validators on every datetime field (shared `enforce_tz_aware`) · #3 UUID4 pin on `trial_id` (shared `enforce_uuid4_version`) · #4 closed enums rejected at three surfaces (Literal construction test, schema `enum` assert, lenient-reader/TypeAdapter path via `model_validate`) · #5 n/a (no internal audit fields in v1) · #6 verbatim free-text fields carry no min_length/regex/normalization (`status`, `lesson`, `quota_reading`, step `status`, trace `detail`) · #7 n/a (no revision field; monotonic counters are producer-owned per AD-10) · #8 own pin file for this family · #9 bidirectional required/optional parity (root + all 18 defs, parametrized) · #10 n/a (`envelope_digest` is carried, not computed here — digest computation is 35.2 assembler scope) · #11 n/a (Lesson-Planner-specific rule; no intake/orchestrator vocabulary present regardless) · #12 n/a (no warn-path validators) · #13 state-machine guard = the lifecycle `model_validator(mode="after")` · #14 `additionalProperties: false` verified at root AND every `$def`.

## Verification evidence

**Target suites — all green (first run green; re-run post-ruff-fix):**
```
.venv/Scripts/python.exe -m pytest tests/unit/models/test_operator_surface_shape_pin.py tests/contracts/test_operator_surface_parity.py -q
........................................................................ [ 69%]
................................                                         [100%]
104 passed in 4.12s
```

**Ruff:** `All checks passed!` on all three new Python files (one E501 fixed during dev).

**lint-imports:** `Contracts: 16 kept, 0 broken.`

**Import purity (runtime + AST):** `forbidden modules loaded: NONE`; direct imports = `__future__, app.models.state._base, dataclasses, datetime, json, logging, pathlib, pydantic, types, typing, uuid, yaml`.

**L1 lockstep (trigger-path regime, 35.0 rows):** `check_pipeline_manifest_lockstep.py` → **exit 0**, trace `reports/dev-coherence/2026-07-11-2116/check-pipeline-manifest-lockstep.PASS.yaml`.

**Size tripwire:** representative max fixture (200 trace events, 8 tiles × 50 history, 80 steps, 20 preflight items, 12 specialists) serializes to **88,605 bytes (86.5 KB)** — under the 128KB target and 256KB limit; test fails loud above the limit and fails-with-warning-text above the target.

**Epic-AC L1 witness set:** byte-pin ✅ · parity ✅ · enum set-equality vs `ProductionTrialStatus` (all seven) ✅ · lenient reader: future-fields fixture → parses, unknown-status → `Unrecognized`, unknown-schema_version → `Unrecognized`, garbage → never raises ✅ · event goldens all five classes incl. resume-that-repauses (waiting→in-flight→paused-at-gate) and recover-reenter (paused-at-error→in-flight ⇒ no event) ✅ · caps (201st trace event drops oldest; 51st history reading drops oldest; re-trim on assignment) ✅ · 256KB tripwire ✅.

## Ambient failures observed (NOT 35.1 breakage — dispositioned)

Wider `tests/unit/models + tests/contracts` sweep: **680 passed, 2 failed, 1 skipped**. Both failures are pre-existing on the branch and read only tracked content untouched by this story (working tree delta = the four new untracked files only):

1. `tests/contracts/test_transform_registry_lockstep.py::test_every_format_covered_or_exempted` — `transform-registry.md` sections `Box (fetch layer)` and `Image (intake via sensory-bridges)` are neither covered nor exempted. Registry-doc drift from an earlier arc.
2. `tests/contracts/test_30_1_zero_test_edits.py::test_no_preexisting_test_files_modified_in_30_1` — compares `git diff d7fd520..HEAD -- tests/` (commit-to-commit; cannot see untracked files). Pre-existing on the branch after the 35.0 merge commit `0f3fee72`.

Recommend routing both to the story-35.0-style disposition lane (or deferred-inventory) — out of 35.1 ownership.

## Deviations from dispatch

- **Envelope section required at `registered`** (decision #2 above) — structural necessity; documented in the model docstring.
- **`health_threshold` default `enabled=True` (on-HUD only)** — EXPERIENCE.md table over brief-addendum §E sketch (decision #7).
- None otherwise: all specified functions, models, constants, and test classes delivered as dispatched.

## Handoff notes for 35.2 (assembler)

- `assembler.emit` should serialize via `model_dump_json()`; the lenient reader accepts str/bytes/dict.
- The assembler owns `seq`/`progress_seq` bumps and `envelope_digest` computation (AD-17) — the contract only carries them.
- `NotificationsEchoSection.parse_status` takes `load_hud_config`'s second tuple element verbatim.
- Strict-context validation (`context={"invariant_mode": "strict"}`) is available for assembler-side CI tests; production writes go witness-mode.
