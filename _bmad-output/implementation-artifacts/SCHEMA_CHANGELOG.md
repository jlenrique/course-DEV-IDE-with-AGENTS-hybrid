# Schema Changelog

Authoritative record of extraction-report schema versions and the contracts pinned by `skills/bmad-agent-texas/scripts/retrieval/contracts.py`. Every non-patch bump requires a new entry here â€” the schema-pin contract test (`tests/contracts/test_acceptance_criteria_schema_stable.py`) enforces this gate.

Per semver-for-schemas:
- **Major (X.0)** â€” breaking: renamed field, changed type, removed field, changed requiredâ†”optional for an existing field.
- **Minor (1.X)** â€” additive only: new optional fields with v1.0-compatible defaults, new enum values that don't break old consumers.
- **Patch (1.0.X)** â€” docs / clarifications / typo fixes; no machine-readable change.

## DecisionCard Family v1.0 - 2026-04-26 - Story 3.2 DecisionCard Schema Family

**Type:** Initial shape (no predecessor family).

**Reason for introduction:** Story 3.2 established the Marcus gate payload
family so every Slab 3 gate emits a typed DecisionCard with a stable,
per-gate schema and a shared D2 meta surface.

**Shapes and contracts pinned:**

- `app/models/decision_cards/base.py`:
  `DecisionCard`, `DecisionCardMeta`, `DecisionCardVerb`.
- `app/models/decision_cards/{g1,g2c,g3,g4}.py`:
  `G1Card`, `G2CCard`, `G3Card`, `G4Card`.
- `app/models/decision_cards/override_event.py`:
  `OverrideEvent`.
- Manifest additive field:
  `app.manifest.schema.EdgeSpec.decision_card_schema`.
- Dotted-ref resolver:
  `app.manifest.refs.resolve_dotted_ref(...)`.

**Semantics pinned:**

- Discriminated-union routing is keyed by `gate_id`.
- `DecisionCardMeta` carries `cache_state`, `affected_nodes`,
  `override_trail`, and `reject_rate`.
- `decision_card_schema` uses `<module>:<ClassName>` dotted refs and is
  compile-time validated against DecisionCard subclasses.

**Migration:** N/A (initial family).

## OperatorVerdict Gate Surface v2.0 - 2026-04-26 - Story 3.3 Verdict + Resume API

**Type:** Breaking change to the verdict receipt shape.

**Reason for introduction:** Story 3.3 upgraded the Slab 1 verdict substrate
into a trial-bound tamper-evident receipt that can safely drive gate resume.

**Shapes and contracts pinned:**

- `app/models/state/operator_verdict.py`:
  `OperatorVerdict`, `OperatorVerdictVerb`.
- `app/gates/schema/operator_verdict.v1.schema.json`:
  gate-surface schema pin.
- `app/gates/resume_api.py`:
  `register_decision_card(...)`,
  `compute_decision_card_digest(...)`,
  `resume_from_verdict(...)`.

**Semantics pinned:**

- Verdict identity now binds `verdict_id`, `trial_id`, `card_id`, and
  `decision_card_digest`.
- `decision_card_digest` is sha256 over DecisionCard canonical JSON plus
  `trial_run_id`, `issuance_timestamp_iso`, and `server_nonce`.
- Replay of a consumed nonce is rejected.
- Legacy input name `decision_card_id` remains accepted as a compatibility alias
  for `card_id`, but the canonical serialized field is now `card_id`.

**Migration:** Existing callers must provide `trial_id` and
`decision_card_digest`. Serialized fixtures and downstream schemas move from
`decision_card_id` to `card_id`.

## ModelOverrideWarning v1.0 - 2026-04-26 - Story 3.5 Runtime Override Warning

**Type:** Initial shape (strict FR24 warning contract for runtime model
override confirmation).

**Reason for introduction:** Story 3.5 closes FR24 by making every runtime
model override two-phase and operator-confirmed. Before state mutation, the
operator must see a pinned warning that carries projected cache impact,
affected nodes, cost delta, and a short-lived `confirm_token`.

**Shapes and contracts pinned:**

- `app/runtime/override_warning.py`:
  `ModelOverrideWarning`.
- `app/runtime/schema/override_warning.v1.schema.json`:
  runtime warning schema pin.
- `app/runtime/override_api.py`:
  `submit_override(...)`, `apply_override(...)`,
  `compute_cache_impact(...)`.
- `app/models/state/run_state.py` additive field:
  `model_overrides: dict[str, str]`.

**Semantics pinned:**

- `confirm_token` is lowercase sha256 hex.
- `issued_at` and `expires_at` must be timezone-aware.
- `expires_at` must be after `issued_at`.
- `submit_override(...)` is idempotent for the same
  `(trial_id, node_id, new_model)` tuple while the warning is still live.
- `apply_override(...)` consumes the pending token, updates
  `RunState.model_overrides`, appends an `OverrideEvent`, and emits
  a proto ledger event with `kind="override"`.

**Migration:** `RunState` gains an additive `model_overrides` field with a
default-empty mapping, so pre-3.5 serialized fixtures remain parseable.

## Epic 33 Pipeline Lockstep Substrate v1.0 - 2026-04-19 - Story 33-2 Pipeline Manifest SSOT

**Type:** Initial shape (no predecessor manifest contract).

**Reason for introduction:** Story 33-2 landed the canonical pipeline-manifest substrate so pack/hud/orchestrator projections share one declarative source of truth and deterministic lockstep enforcement.

**Shapes and contracts pinned:**

- `state/config/pipeline-manifest.yaml` schema surface, including top-level fields:
  `schema_version`, `pack_version`, `generator_ref`, `learning_events`, `steps`.
- `scripts/utilities/pipeline_manifest.py` loader contract:
  parse/validate manifest shape, expose deterministic typed projection, enforce invariant checks.
- `scripts/utilities/check_pipeline_manifest_lockstep.py` L1 contract:
  deterministic lockstep checks, strict exit-code discipline, trace artifact emission.

**Semantics pinned:**

- Manifest is the canonical pipeline topology authority; downstream projections are derived.
- Lockstep checks classify failures deterministically and are CI-automatable.
- Story 33-2 closed with AC-B.15 rewire deferred to 33-1a because 33-1 Case C found no in-repo generator of record.

**Migration:** N/A (initial shape).

## Epic 33 Generator Substrate v1.1 - 2026-04-19 - Story 33-1a Build v4.2 Generator

**Type:** Additive extension to Epic 33 substrate contracts.

**Reason for introduction:** Story 33-1a closed Case-C escalation by introducing the in-repo deterministic v4.2 generator and extending manifest step entries with rationale metadata for generated provenance.

**Shapes and contracts pinned:**

- `scripts/generators/v42/` package with deterministic Jinja2 rendering (`render.py`, `env.py`, `manifest.py`, template tree).
- Manifest step additive field in `scripts/utilities/pipeline_manifest.py`:
  `StepEntry.rationale: str | None`.
- Fixture ratification pair for downstream regeneration gate:
  `tests/generators/v42/fixtures/manifest_fixture.yaml`,
  `tests/generators/v42/fixtures/expected_pack/fixture_pack.md`,
  `tests/generators/v42/fixtures/pack_sha_fixture.txt`.

**Semantics pinned:**

- Generator path-of-record: `scripts/generators/v42/render.py` (wired in `state/config/pipeline-manifest.yaml` `generator_ref`).
- Deterministic render contract validated by hash round-trip + 5x repeatability tests.
- No LLM in critical path (`test_33_1a_no_llm_imports.py` contract guard).

**Migration:** Additive only; existing manifests without `rationale` remain valid (`rationale=None` default).

## Epic 15 Learning Events Lite v1.0 - 2026-04-19 - Story 15-1-lite-marcus

**Type:** Additive extension across manifest + new learning-event schema/check surfaces.

**Reason for introduction:** Story 15-1-lite-marcus introduced the minimal learning-event contract (schema + capture + Marcus gate wiring + L1 lockstep) used as Epic 33's load-bearing meta-test.

**Shapes and contracts pinned:**

- New schema config: `state/config/learning-event-schema.yaml` (`schema_version`, closed `event_type_enum`, required-field contract).
- New capture surface: `scripts/utilities/learning_event_capture.py` (`LearningEvent`, `create_event`, `validate_event`, `append_to_ledger`).
- New L1 checker: `scripts/utilities/check_learning_event_lockstep.py` with deterministic checks A/B/C/D and 0/1/2 exit-code discipline.
- Manifest extensions in `state/config/pipeline-manifest.yaml`:
  - top-level `learning_events.schema_ref` populated,
  - Gate 2/3/4 emitter declarations (`G2C`, `G3`, `G4`) with event types `[approval, revision, waiver]`,
  - `block_mode_trigger_paths` entries for learning-event files.

**Semantics pinned:**

- Closed event type set for lite scope: `approval`, `revision`, `waiver`.
- Append-only learning ledger contract at `{run_dir}/learning-events.yaml`.
- Marcus gate wiring emits exactly three statically-resolvable call-sites (G2C/G3/G4).

**Migration:** Additive only; existing non-learning-event flows remain valid with empty/non-emitting declarations.

## Lesson Plan v1.0 additive extension â€” 2026-04-18 â€” Story 29-3 Irene Blueprint Co-author

**Type:** Additive optional-field extension to the existing Lesson Plan v1.0 shape family.

**Reason for introduction:** 31-4 proved the blueprint branch can emit a real
draft artifact, but it intentionally did not invent the final typed sign-off
pointer. Story 29-3 adds the minimal machine-readable bridge so downstream
stories can distinguish "draft exists" from "Irene + writer approved the
blueprint branch."

**Shapes pinned (live in marcus/lesson_plan/schema.py):**

- BlueprintSignoff: lueprint_asset_path, signoff_artifact_path,
  irene_review_complete, writer_signoff_complete, signed_at.
- PlanUnit.blueprint_signoff: new OPTIONAL field (BlueprintSignoff | None).

**Semantics pinned:**

- Both stored paths are repo-relative strings; absolute paths and upward
  traversal are rejected by validator logic.
- signed_at is timezone-aware.
- The pointer is additive and optional: pre-29-3 plans remain valid with
  lueprint_signoff = null.
- 29-3 records approval state in a deterministic sidecar artifact plus the
  typed pointer; it does not emit directly to the Lesson Plan log and does not
  implement 31-5's pass/fail branch.

**Migration:** N/A. Existing v1.0 lesson plans remain valid because the new
field is optional.
## Coverage Manifest v1.0 â€” 2026-04-18 â€” Story 32-2 Plan-Ref Envelope Coverage Manifest

**Type:** Initial shape (no predecessor).

**Reason for introduction:** 32-2 ships the explicit audit artifact that 32-3
will consume directly. It does not invent downstream emitters; it enumerates
the expected 05â†’13 plan-ref surfaces, records whether each one preserves
`lesson_plan_revision` + `lesson_plan_digest`, and verifies whether the live
consumer path proves canonical `assert_plan_fresh(...)` usage.

**Shapes pinned (live in `marcus/lesson_plan/coverage_manifest.py`):**

- `CoverageSurface`: `step_id`, `surface_name`, `owner_story_key`,
  `module_path`, `artifact_kind`, `plan_ref_mode`,
  `has_lesson_plan_revision`, `has_lesson_plan_digest`,
  `assert_plan_fresh_required`, `assert_plan_fresh_verified`, `status`,
  `notes`.
- `CoverageSummary`: `total_surfaces`, `implemented_surfaces`,
  `pending_surfaces`, `deferred_surfaces`,
  `surfaces_with_full_plan_ref_coverage`,
  `surfaces_missing_one_or_both_fields`,
  `surfaces_missing_freshness_gate_verification`, `trial_ready`.
- `CoverageManifest`: `schema_version`, `generated_at`, `source_story_key`,
  `surfaces`, `summary`.
- `CoverageInventoryEntry`: story-owned inventory row used to materialize the
  emitted manifest and gate stale pending/implemented transitions.

**Semantics pinned:**

- Canonical emitted artifact path:
  `_bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json`.
- Deterministic ordering: `step_id`, then `owner_story_key`, then
  `surface_name`.
- `trial_ready` is true only when there are no pending/deferred rows and every
  implemented row has full plan-ref coverage plus verified freshness gating.
- `assert_plan_fresh` proof is AST-based and import-path-aware. Accepted proofs
  are limited to direct canonical calls from `marcus.lesson_plan.log` or a
  same-module wrapper that itself calls that canonical symbol on the live
  surface before downstream processing.

**Anti-patterns locked down:**

- No abstract family placeholder standing in for multiple concrete boundaries.
- No grep-only freshness verification.
- No silent omission of future surfaces; they remain visible as `pending` until
  the owning story lands and the module path exists.

**Migration:** N/A (initial shape).

## Modality Registry v1.0 â€” 2026-04-18 â€” Story 31-3 Registries

**Type:** Initial shape (no predecessor).

**Reason for introduction:** 31-3 ships the TARGETING SURFACE â€” the frozen
closed-set catalog of atomic producer targets. Marcus-Orchestrator reads the
registry at plan-lock to route `scope_decision.delegated-to-modality-X` entries
to concrete producers; Irene references `modality_ref` validity; Tracy dispatches
based on composite composition.

**Shapes pinned (live in `marcus/lesson_plan/modality_registry.py`):**

- `ModalityRef`: `Literal["slides", "blueprint", "leader-guide", "handout",
  "classroom-exercise"]` â€” closed set of 5 entries at MVP. Widening requires
  ruling amendment + schema-version bump (minor if additive, major if
  renaming or status-semantics change) + SCHEMA_CHANGELOG entry (AC-C.4).
- `ModalityEntry`: `modality_ref` (ModalityRef) / `status`
  (`Literal["ready", "pending"]`) / `producer_class_path` (`str | None`) /
  `description` (free-text). `ConfigDict(extra="forbid", frozen=True,
  validate_assignment=True)`. AC-C.6 invariant via
  `@model_validator(mode="after")`: `status == "pending"` implies
  `producer_class_path is None`.
- `MODALITY_REGISTRY`: `types.MappingProxyType` wrapping the seeded dict.
  `isinstance(MODALITY_REGISTRY, MappingProxyType)` is the pinned type.
  Any mutation attempt raises (`TypeError` from MappingProxyType or
  `AttributeError` from missing methods).
- Query API: `get_modality_entry(modality_ref) -> ModalityEntry | None`
  (no warn / no raise on unknown â€” closed-set discipline);
  `list_ready_modalities() -> frozenset[str]` (returns `{"slides",
  "blueprint"}` at MVP); `list_pending_modalities() -> frozenset[str]`
  (returns `{"leader-guide", "handout", "classroom-exercise"}` at MVP).

**Semantics pinned:**

- CLOSED SET at MVP. Unlike `event_type_registry` (which WARNs on unknown for
  GagnÃ©-seam extensibility), `modality_registry` rejects silently via `None`
  return â€” widening is not an extensibility surface; it's a governed change.
- At 31-3 MVP every entry has `producer_class_path=None`. Gary/slides
  backfills via separate amendment; 31-4 backfills `blueprint` via minor
  schema bump; `pending` modalities stay `None`.
- R2 rider S-2 carry-forward: `description` is free-text, no `min_length`.

**Anti-patterns locked down:**

- No runtime registry extension, no plugin discovery hooks, no per-tenant
  variation (AC-C.7).
- `MODALITY_REGISTRY["slides"] = ...` / `del` / `clear` / `update` / `pop` /
  `popitem` / `setdefault` / attribute set all raise. AC-T.2 parametrized
  matrix enforces at CI.
- `intake` / `orchestrator` tokens forbidden in user-facing strings (AC-T.8 /
  R1 amendment 17 / R2 rider S-3 carry-forward).

**Migration:** N/A (initial shape).

**Consumer compatibility:** 30-3 / 29-2 / 28-2 / 31-4 / 30-4 consume via the
public query API. Direct `MODALITY_REGISTRY[key]` access is PERMITTED
(public Mapping) but the query helpers are preferred because they return
`None` on miss.

## Component Type Registry v1.0 â€” 2026-04-18 â€” Story 31-3 Registries

**Type:** Initial shape (no predecessor).

**Reason for introduction:** Names the N=2 composite-package shapes at MVP â€”
the minimum needed to prove both single-modality and multi-modality composite
shapes using only `ready` modalities. Prompt-pack authors compose packages
against these entries; Tracy dispatches enrichment per composite.

**Shapes pinned (live in `marcus/lesson_plan/component_type_registry.py`):**

- `ComponentTypeEntry`: `component_type_ref` (str, min_length=1) /
  `modality_refs` (`tuple[ModalityRef, ...]`, every element must be a key in
  MODALITY_REGISTRY) / `description` (free-text) / `prompt_pack_version`
  (`str | None`). `ConfigDict(extra="forbid", frozen=True,
  validate_assignment=True)`. Composition-validity enforced at TWO layers:
  (a) `ModalityRef` Literal closed-set check at field-validation time,
  (b) `@model_validator(mode="after")` explicit lookup against
  `MODALITY_REGISTRY` (defense in depth against `ModalityRef` widening
  without registry update).
- `COMPONENT_TYPE_REGISTRY`: `types.MappingProxyType` with 2 entries:
  `narrated-deck` composes `("slides",)`;
  `motion-enabled-narrated-lesson` composes `("slides", "blueprint")`.
  Both `prompt_pack_version=None` at MVP.
- Query API: `get_component_type_entry(component_type_ref) ->
  ComponentTypeEntry | None`.

**Semantics pinned:**

- N=2 ENTRIES FROZEN at MVP. Widening requires ruling amendment +
  schema-version bump + SCHEMA_CHANGELOG entry (AC-C.5).
- Composites compose ONLY `ready` modalities at MVP (cross-status coupling
  out-of-scope).
- Recursive composites (a composite of composites) are out-of-scope
  (AC-C.7 (f)).
- Import-time assertion in the module: every seeded
  `component_type_ref.modality_refs` element is a key in
  `MODALITY_REGISTRY` (belt-and-suspenders against typos in the seed dict).

**Anti-patterns locked down:**

- Same immutability + no-runtime-extension discipline as Modality Registry.
- `modality_refs` is a `tuple` (frozen-by-value); not a `list`.

**Migration:** N/A (initial shape).

**Consumer compatibility:** 28-2 / prompt-pack authors consume via
`get_component_type_entry` or direct registry iteration.

## ModalityProducer ABC v1.0 â€” 2026-04-18 â€” Story 31-3 Registries

**Type:** Initial shape (no predecessor).

**Reason for introduction:** Names the producer contract every modality
producer subclasses. 31-4 (blueprint-producer, 5pt single story) implements
this ABC first; Gary/Gamma slides adopts via separate amendment. R1 ruling
amendment 7 binding: ABC MUST be complete-enough that 31-4 lands without
splitting.

**Shapes pinned (live in `marcus/lesson_plan/modality_producer.py` and
`marcus/lesson_plan/produced_asset.py`):**

- `ModalityProducer` (ABC):
  - `modality_ref: ClassVar[str]` â€” pinned by subclass.
  - `status: ClassVar[Literal["ready", "pending"]]` â€” pinned by subclass.
  - `@abstractmethod produce(self, plan_unit, context) -> ProducedAsset`.
  - **M-AM-2 (Murat R2 BINDING) `__init_subclass__` hook:** CPython does NOT
    check `ClassVar[...]` type hints at class-definition or instantiation
    time; the hook raises `TypeError` at class-definition time on missing /
    wrong-type `modality_ref`, missing `status`, or status outside the
    closed set. This is the actual enforcement â€” the annotations are
    documentation-only without this hook.
  - ABC membership enforced separately via `abc.ABC` + abstract method:
    subclass missing `produce()` â†’ `TypeError` at instantiation.
- `ProductionContext` (Pydantic):
  - `lesson_plan_revision: int ge=0` / `lesson_plan_digest: str min_length=1`.
  - `ConfigDict(extra="forbid", frozen=True, validate_assignment=True)`.
  - **W-2 (Winston R2) extensibility seam:** 31-4 MAY subclass for
    blueprint-specific fields WITHOUT a schema version bump; subclasses MUST
    preserve `lesson_plan_revision` + `lesson_plan_digest` as the
    staleness-gate primitives. Subclass stories document extensions in their
    own SCHEMA_CHANGELOG entry.
- `ProducedAsset` (Pydantic):
  - `asset_ref` / `modality_ref` / `source_plan_unit_id` / `created_at`
    (tz-aware UTC) / `asset_path` / `fulfills`.
  - `fulfills` regex: `^[a-z0-9._-]+@(?:0|[1-9]\d*)$`. Accepts zero revision
    (`unit@0`); rejects leading-zero (`unit@007` â€” M-AM-3 strict-monotonic
    integer discipline), negative, non-integer, uppercase, unicode, multi-@,
    whitespace.
  - **Q-R2-A (Quinn R2) cross-field validator:** `source_plan_unit_id ==
    fulfills.split("@", 1)[0]` â€” rejects counterfeit-fulfillment with the
    explicit `"counterfeit-fulfillment seam; tri-phasic contract violation"`
    error message.

**Semantics pinned:**

- Every `ProducedAsset` carries `fulfills: {plan_unit_id}@{plan_revision}` â€”
  Quinn's Tri-Phasic Contract execution-phase artifact.
- The ABC does NOT enforce registry membership at instantiation
  (`modality_ref="unknown-but-a-str"` is still instantiable at the ABC
  layer). That's a consumer-site check â€” see
  `tests/fixtures/consumers/fixture_30_3_marcus_consumer.py`
  staleness-gate-at-consumer-boundary pattern (Q-R2-B).

**Anti-patterns locked down:**

- No hooks beyond `produce()` on the ABC (no `setup()` / `teardown()` /
  `validate()`). If 31-4 needs more, widen here, not there (R1 amendment 7
  binding).
- `ProducedAsset.fulfills` must pass regex AND cross-field validator â€”
  either failure rejects.

**Migration:** N/A (initial shape).

**Consumer compatibility:** 31-4 subclasses `ModalityProducer`; 30-4 + 31-5
read `ProducedAsset.fulfills` for fanout tracking + Quinn-R gate.

## Lesson Plan Log v1.0 â€” 2026-04-18 â€” Story 31-2 Lesson Plan Log

**Type:** Initial shape (no predecessor log file exists).

**Reason for introduction:** 31-2 ships the write-path on top of the 31-1
shape foundation. Surfaces the append-only JSONL log + single-writer
enforcement + monotonic-revision gate (plan.locked only, per R2 M-2) +
staleness detector + `pre_packet_snapshot` payload shape (Winston R1
amendment on 30-4).

**Shapes pinned (live in `marcus/lesson_plan/log.py`):**

- `LessonPlanLog`: write API (`append_event(envelope, writer_identity)`),
  read API (`read_events(since_revision, event_types)`), helpers
  (`latest_plan_revision`, `latest_plan_digest`), property (`path`).
- `WriterIdentity`: `Literal["marcus-orchestrator", "marcus-intake"]`
  (closed set per AC-C.5; widening requires ruling amendment + major
  schema bump).
- `WRITER_EVENT_MATRIX`: `dict[str, frozenset[WriterIdentity]]` â€” AC-B.3
  single-writer enforcement matrix. Only the `pre_packet_snapshot` row
  permits `marcus-intake`; the other five rows are
  Marcus-Orchestrator-only per R1 ruling amendment 13.
- `NAMED_MANDATORY_EVENTS`: alias of
  `event_type_registry.RESERVED_LOG_EVENT_TYPES` (single source of truth,
  two naming surfaces). Frozenset â€” M-3 immutability asserted via
  `.add()` raising `AttributeError`.
- `SourceRef`: `source_id`, `path` (Optional), `content_digest`.
- `PrePacketSnapshotPayload`: `sme_refs` (list[SourceRef]),
  `ingestion_digest`, `pre_packet_artifact_path`,
  `step_03_extraction_checksum` â€” the four fields 30-4 needs to
  reconstruct Intake-era context from the log alone (Winston R1).
- `PlanLockedPayload`: `lesson_plan_digest` â€” the digest field
  `latest_plan_digest()` reads.
- `StalePlanRefError`: new exception (subclass of `ValueError`) raised by
  `assert_plan_fresh` when envelope revision and/or digest mismatches
  log. R2 M-1 axis-named message format: `"StalePlanRefError: revision
  mismatch (envelope=N, log=M); digest mismatch (envelope='x', log='y')"`.
- `UnauthorizedWriterError`: new exception (subclass of
  `PermissionError`) raised by `append_event` on writer/event-type mismatch.
- `assert_plan_fresh`: module-level staleness detector; duck-typed on
  `lesson_plan_revision` + `lesson_plan_digest` attributes. Called by
  every envelope 05â†’13 before downstream processing; 32-2 coverage
  manifest audits call-site coverage.
- `LOG_PATH`: `Path("state/runtime/lesson_plan_log.jsonl")` â€” module
  constant; tests override via fixture or explicit `path=` kwarg.

**Semantics pinned:**

- Append-only JSONL â€” one canonical-JSON line per event + newline.
  `open("a") + write + flush + fsync`. Atomic on POSIX for writes <
  `PIPE_BUF`; single-process single-writer assumption bridges the
  Windows NTFS gap (see W-R1 future-hardening note below).
- Monotonic revision on `plan.locked` ONLY (R2 M-2). Non-`plan.locked`
  events at stale revision are LEGAL (interleave semantics).
- Re-read-after-write consistency (R2 M-5 / AC-T.11): immediate
  `read_events()` after `append_event()` MUST yield the just-appended
  event.
- No dedup on `event_id`; no compaction; no rotation; no multi-process
  writer coordination (all explicitly out-of-scope per AC-C.7).

**Anti-patterns locked down:**

- No direct `open(LOG_PATH, "a")` in downstream code; `bmad-code-review`
  Blind Hunter layer scans for bypasses (AC-C.8).
- No writer_identity spoofing (Q-R2-R1 R2 rider): modules pass only
  their own writer identity; grep-detectable in code review.
- `NAMED_MANDATORY_EVENTS.add()` raises `AttributeError` (M-3 frozenset
  immutability).
- Unknown event_types are REJECTED at write time (governance artifact,
  not extensibility surface) â€” AC-B.2 (b) / AC-T.7.

**R2 party-mode GREEN with 7 riders (2026-04-18):**

- W-R1 â€” Windows atomic-write future-hardening caveat (docstring only).
- Q-R2-R1 â€” writer_identity anti-pattern discipline (Dev Notes +
  code-review grep).
- M-1 â€” AC-T.4 2Ã—2 staleness matrix + axis-named error message.
- M-2 â€” Monotonic gate ONLY on plan.locked (non-plan.locked stale
  ACCEPTED).
- M-3 â€” `NAMED_MANDATORY_EVENTS` frozenset immutability test.
- M-4 â€” Baseline rebase to commit `15f68b1` HEAD (1023 `--run-live` /
  1001 default).
- M-5 â€” AC-T.11 re-read-after-write consistency + K floor 15 â†’ 17.

**Migration:** N/A (initial shape; no predecessor log file exists â€”
`state/runtime/lesson_plan_log.jsonl` is created by first `append_event`
call).

**Consumer compatibility:** 30-1 / 30-4 / 32-2 consume via the public
`LessonPlanLog.read_events` API. Direct `open(LOG_PATH)` reads in
consumer code are a code-review block (AC-C.8).

## Lesson Plan v1.0 â€” 2026-04-18 â€” Story 31-1 Lesson Plan Schema Foundation

**Type:** Initial shape (no predecessor).

**Reason for introduction:** Lesson Planner MVP foundation (R1 orchestrator
ruling amendment 5). Ships the `LessonPlan` / `PlanUnit` / `Dials` /
`IdentifiedGap` primitives + the `schema_version: "1.0"` root field + the
`weather_band` abundance-framed enum (gold / green / amber / gray; no red).

**Shapes pinned:**

- `LessonPlan`: `schema_version`, `learning_model`, `structure`, `plan_units`,
  `revision`, `updated_at`, `digest`.
- `PlanUnit`: `unit_id`, `event_type`, `source_fitness_diagnosis`,
  `scope_decision`, `weather_band`, `modality_ref`, `rationale`, `gaps`,
  `dials`.
- `Dials`: `enrichment`, `corroboration` (both `float | None` in `[0.0, 1.0]`).
- `IdentifiedGap`: `gap_id`, `description`, `suggested_posture`
  (`embellish | corroborate | gap_fill`).

**Anti-patterns locked down:** `rationale` is free text verbatim (no trimming,
no coercion, no enum); `weather_band` rejects `"red"` at three validation
layers.

**Migration**: N/A (initial shape; no predecessor artifacts exist).

## Fit Report v1.0 â€” 2026-04-18 â€” Story 31-1 Lesson Plan Schema Foundation

**Type:** Initial shape (absorbed from original 29-1 per R1 ruling amendment 5).

**Reason for introduction:** Irene's diagnostic output carrier. 31-1 ships
the shape only; 29-1 ships the validator + serializer + emission wiring on
top of the shape.

**Shapes pinned:**

- `FitReport`: `schema_version`, `source_ref`, `plan_ref`, `diagnoses`,
  `generated_at`, `irene_budget_ms`.
- `FitDiagnosis`: `unit_id`, `fitness` (`sufficient | partial | absent`),
  `commentary`, `recommended_scope_decision`, `recommended_weather_band`.

**Migration**: N/A (initial shape; no predecessor artifacts exist).

## Scope Decision v1.0 â€” 2026-04-18 â€” Story 31-1 Lesson Plan Schema Foundation

**Type:** Initial shape (absorbed from 30-3a / implicit 31-1 per R1 ruling
amendment 5; R2 rider S-4 adds the two-level actor surface; R2 rider W-1
adds the generic event envelope; R2 rider Q-5 adds the locked-bypass guard).

**Reason for introduction:** Jurisdictional primitive for the Lesson
Planner bilateral typed contract. Maya is the sole signatory; internal
audit tooling receives a separate private actor surface.

**Shapes pinned:**

- `ScopeDecision`: `state` (`proposed | ratified | locked`), `scope`
  (`in-scope | out-of-scope | delegated | blueprint`), `proposed_by`
  (`system | operator` â€” public), `internal_proposed_by` (five-valued
  internal Marcus-duality taxonomy; `Field(exclude=True)` +
  `SkipJsonSchema`), `ratified_by` (`"maya" | None`), `locked_at`.
- `ScopeDecisionTransition`: `event_type` (Literal
  `"scope_decision_transition"`), `unit_id`, `plan_revision`, `from_state`,
  `to_state`, `from_scope`, `to_scope`, `actor` (`system | operator` â€”
  public), `internal_actor` (private + `SkipJsonSchema`), `timestamp`,
  `rationale_snapshot`.
- `EventEnvelope`: `event_id`, `timestamp`, `plan_revision`, `event_type`,
  `payload`. Generic envelope every future log event in 31-2 conforms to.

**Anti-patterns locked down:** direct `state="locked", ratified_by=None`
construction is rejected by a `model_validator(mode="after")` bypass guard
(Q-5); `_internal_proposed_by` and `_internal_actor` never leak into
default `model_dump` or the published JSON Schema.

**Migration**: N/A (initial shape; no predecessor artifacts exist).

## v1.1 â€” 2026-04-18 â€” Story 27-0 Retrieval Foundation

**Type:** Minor (additive, backwards-compatible)

**Reason for bump:** Shape 3-Disciplined retrieval architecture (Epic 27) adds retrieval-shape provenance to the per-source entry in `extraction-report.yaml`. Every new field is optional with a v1.0-compatible default so pre-Shape-3 consumers remain correct. See `skills/bmad-agent-texas/references/extraction-report-schema.md#changelog` for the full migration note.

**Additive fields (all optional, default to null / false / []):**

- `sources[].retrieval_intent: string | null`
- `sources[].provider_hints: list[{provider, params}]`
- `sources[].cross_validate: boolean`
- `sources[].convergence_signal: {providers_agreeing, providers_disagreeing, single_source_only} | null`
- `sources[].source_origin: "operator-named" | "tracy-suggested"` (default `operator-named`)
- `sources[].tracy_row_ref: string | null`

**Contracts pinned (`retrieval/contracts.py`):**

- `RetrievalIntent` â€” `intent`, `provider_hints: list[ProviderHint]`, `kind`, `acceptance_criteria`, `iteration_budget`, `convergence_required`, `cross_validate`
- `ProviderHint` â€” `provider`, `params` (AC-C.10, Winston MUST-FIX #2)
- `AcceptanceCriteria` â€” `mechanical`, `provider_scored`, `semantic_deferred`
- `TexasRow` â€” `source_id`, `title`, `body`, `authors`, `date`, `provider`, `provider_metadata`, `source_origin`, `tracy_row_ref`, `convergence_signal`, `authority_tier`, `completeness_ratio`, `structural_fidelity`
- `ConvergenceSignal` â€” `providers_agreeing`, `providers_disagreeing`, `single_source_only` (structural per AC-C.11 dumbness clause)
- `ProviderInfo` â€” `id`, `shape`, `status`, `capabilities`, `auth_env_vars`, `spec_ref`, `notes` (AC-B.8 operator amendment 2026-04-18)

**Consumer compatibility matrix:**

| Consumer reads | Writer emits v1.0 | Writer emits v1.1 |
|---|---|---|
| v1.0 | âœ“ native | âœ“ new fields invisible (ignored) |
| v1.1 | âœ“ new fields default | âœ“ native |

**Rollback:** N/A â€” no breaking change. Revert via `schema_version: "1.0"` on writer side; consumers continue to work.

## v1.0 â€” pre-2026-04-18 â€” baseline

Original extraction-report schema shipped with Epic 25 (Story 25-1, Texas runtime wrangling runner). See `skills/bmad-agent-texas/references/extraction-report-schema.md` (v1.0 block) for the baseline field set.

