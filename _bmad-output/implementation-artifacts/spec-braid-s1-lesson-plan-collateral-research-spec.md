---
story_key: braid-s1-lesson-plan-collateral-research-spec
epic: Braid — Marcus-interlocutor + research-foundations + lesson-planning-with-workbook-companion (2026-06-24)
slice: Slice 1 — CLIENT VALUE (the workbook the client asked for)
status: ready-for-dev
gate_mode: dual
tier: Tier-2 (schema-shape; party green-light secured via braid ratification 2026-06-24)
authority: _bmad-output/planning-artifacts/braid-green-light-ratification-2026-06-24.md (DP4 + G1–G6); braid-strawman-2026-06-24.md §3 DP4/DP5
baseline_commit: c7ed16d
cycle: NEW CYCLE (dev T1–T10 RED-first → Claude T11 bmad-code-review + party close)
r_tier: R2
t11_tier: standard
lookahead_tier: 2
schema_shape: true
scaffold: docs/dev-guide/scaffolds/schema-story/
files_touched:
  - app/marcus/lesson_plan/collateral_spec.py            # NEW — the content-model schema family
  - app/marcus/lesson_plan/schema/collateral_spec.v1.schema.json  # NEW — emitted JSON Schema witness
  - app/specialists/irene_pass1/_act.py                  # additive: collateral emission instructions + pure post-parse normalize + artifact lines
  - app/specialists/irene_pass1/payload_contract.py      # (no change expected; emission is additive on output, not new consumed keys)
  - tests/specialists/irene_pass1/test_irene_pass1_collateral_emission.py  # NEW
  - tests/marcus/lesson_plan/test_collateral_spec_shape_stable.py          # NEW
  - tests/marcus/lesson_plan/test_collateral_spec_json_schema_parity.py    # NEW
  - tests/marcus/lesson_plan/test_no_intake_orchestrator_leak_collateral_spec.py  # NEW
  - _bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md             # new family entry
---

# S1: Lesson-plan collateral + research spec — Irene Pass-1 additive emission (DP4)

## Frozen Intent

Extend Irene **Pass-1** to **additively** emit, alongside the existing slide brief / plan-units, a **WORKBOOK CONTENT MODEL** plus a **research-enrichment goals block** — the DP4 deliverable of the braid. This is the *spec* the client's workbook is built from (S2 builds the producer; S3 wires research). It is a **schema-shape story**: the deliverable is a Pydantic-v2 model family (`CollateralSpec` + children), an emitted JSON Schema witness, shape-pin tests, and the Pass-1 emission + pure post-parse normalization that produces a well-formed instance on the real artifact.

**The content-model discipline (not a shopping list) — binding from DP4:**
- Every workbook **section binds a `learning_objective_id`** — the asset-lesson pairing invariant extended to collateral. A section with no objective is a contract violation, not a soft warning.
- Every section carries a **depth-delta contract**: an explicit declaration of *what depth is deferred OFF the glance-slide INTO the workbook*. This is the load-bearing field — it is what legitimizes the deck's tight VO (the glance-deck and the read-in-depth workbook are dual-coding partners; the VO can stay tight precisely because the workbook carries the deferred depth).
- **Exercises** carry a **Bloom level** (closed enum) + a **source-grounded answer-key reference** (`source_ref`-bearing; authored backward from sourced content per G3).
- **Research-enrichment goals** are expressed as **pedagogical intent** (e.g. "learner needs the primary-source basis for the 23% figure"), NOT raw fetch queries. S3 (Texas/Tracy) translates intent → fetch; S1 must not pre-empt that boundary.

**Additive / no-regression invariant.** The empty case is an **explicit `collateral: none` declaration** — a decision on record, NOT an absent key. Degenerate-empty round-trips to today's deck-only behavior with zero regression to the existing plan-unit / cluster emission.

## Scope fence — v1 vs v-next (read this before writing any field)

**IN SCOPE (v1, this story):**
1. The `CollateralSpec` content-model schema family (Pydantic v2) under `app/marcus/lesson_plan/`.
2. Emitted JSON Schema witness + shape-pin / parity / no-leak tests (schema-shape discipline).
3. Pass-1 **additive emission**: collateral-emission prompt instructions + a **pure post-parse normalize backstop** (mirror `normalize_clusters`) + additive artifact lines in `irene-pass1.md`. The emitted `lesson_plan` dict gains a `collateral` key.
4. The explicit `collateral: none` empty-declaration path.

**OUT OF SCOPE (v-next / other braid stories — name them, do not build them):**
- **The workbook producer / render / DOCX** → **S2** (`ModalityProducer` subclass; `"workbook"` added to `MODALITY_REGISTRY`). **S1 does NOT touch `MODALITY_REGISTRY`** and does NOT add `"workbook"` to the closed `ModalityRef` set. (That is S2's schema-version bump under the registry's AC-C.4 amendment rule.)
- **Live research fetch / citation injection** → **S3** (pass the existing Irene→Tracy→Texas bridge through `production_runner.py`). S1 emits research *intent*; no retrieval, no `source_ref` resolution, no Texas call.
- **Marcus elicitation / conversational authoring of the spec** → S4/S5. v1 collateral is **predefined** for the frozen tejal deck (DP5); Pass-1 emits the content model from the corpus-grounded plan, not from an interactive operator dialogue.
- **Answer-key *content* generation, exercise *prose*** → S2 producer. S1's exercise carries the Bloom level + an answer-key `source_ref` reference + intent, not the worked solution.

## Substrate grounding (verified against `c7ed16d`)

- **Where Pass-1 emits the plan.** `app/specialists/irene_pass1/_act.py`:
  - `parse_pass1_response(raw_text)` (`:342`) parses the model JSON, runs `normalize_clusters`, then guarantees ≥1 plan_unit (fallback branch). **This is the integration seam for a `normalize_collateral` backstop** (call it after `normalize_clusters`, before/after the fallback-unit branch, mirroring how clusters are normalized on both LLM output and the fallback unit).
  - `_cluster_emission_instructions()` (`:156`) is the additive prompt block requesting the cluster fields. **The collateral-emission instructions are a sibling block** appended in `assemble_pass1_prompt` (`:122`).
  - `write_lesson_plan(plan, ...)` (`:376`) writes `runs/<run_id>/irene-pass1.md`. **Additive collateral lines** append here (the Story-1.1 cluster lines are the exact precedent — flat lines unchanged, new lines appended).
  - `act(...)` (`:447`) returns `output["lesson_plan"] = plan`; the plan dict carrying the new `collateral` key rides in `cache_state.cache_prefix` (canonical `_json_dumps`, sorted-keys). **No new consumed payload key** — emission is additive on the *output* plan dict, so `payload_contract.CONSUMED_PAYLOAD_KEYS` is unchanged.
- **The producer/registry precedent the content model must compose with.** `app/marcus/lesson_plan/`:
  - `produced_asset.py::ProducedAsset` pins `source_plan_unit_id` (open-id regex `OPEN_ID_REGEX_PATTERN`) + `fulfills: {plan_unit_id}@{plan_revision}` + the Q-R2-A cross-field invariant. **`CollateralSpec` sections must use the same `OPEN_ID_REGEX_PATTERN` for `learning_objective_id`** so S2's producer can bind asset→objective without a regex fork.
  - `modality_registry.py` (`SCHEMA_VERSION="1.0"`, `MappingProxyType`, AC-C.4 closed-set rule) — **S1 reads but does NOT modify it.** `"workbook"` is S2's add.
  - `modality_producer.py::ModalityProducer` ABC — the `produce(plan_unit, context) -> ProducedAsset` contract S2 will implement consuming this spec. S1's job is to make the spec *complete enough to produce from*.
  - `schema.py` (`PlanUnit`, `ScopeDecision`, `LearningModel`) — the existing pydantic-v2 family; `CollateralSpec` is a new sibling module in the same package, same idioms.
- **🟢 No lockstep / pipeline-manifest touch required (verified).** `block_mode_trigger_paths` (`state/config/pipeline-manifest.yaml:60-71`) lists the manifest, L1 script, run_hud, progress_map, workflow_runner, the v4.2 pack, and the learning-event schema/capture. **Neither `app/specialists/irene_pass1/` nor `app/marcus/lesson_plan/` is a trigger path.** S1 adds **no pipeline node, no manifest projection, no pack section** (it is additive *within* node 04A/05's existing Pass-1 emission, not a new data-plane edge). Therefore: **no `dp-vN` bump, no `-gen` witness regen, no pipeline-lockstep regime.** A SCHEMA_CHANGELOG entry for the new `collateral_spec` family **is** required (schema-shape discipline). If dev discovers any need to project `collateral` onto a downstream node's `dependency_projections`, **STOP** — that is a manifest touch, escalate it as a Tier-2 governance bump per `docs/dev-guide/pipeline-manifest-regime.md`, do not silently edit the manifest.

## T1 Readiness (required readings — dev reads ALL before any code)

1. `_bmad-output/planning-artifacts/braid-green-light-ratification-2026-06-24.md` — DP4 (content model) + G1–G6 (honesty gates). **The binding contract.**
2. `docs/dev-guide/pydantic-v2-schema-checklist.md` — the 14 idioms. Mandatory for this schema-shape story.
3. `docs/dev-guide/scaffolds/schema-story/` (`src/schema.py.tmpl`, `src/digest.py.tmpl`, the three test templates) — **instantiate from the scaffold; do not re-derive from the 31-1 precedent.**
4. `docs/dev-guide/dev-agent-anti-patterns.md` — traps (schema, test-authoring, believed-green).
5. `app/marcus/lesson_plan/produced_asset.py` + `modality_registry.py` + `modality_producer.py` — the producer/registry/`ProducedAsset` contract the spec must compose with (and the `OPEN_ID_REGEX_PATTERN` to reuse).
6. `app/specialists/irene_pass1/_act.py` — the emission seams (`parse_pass1_response`, `_cluster_emission_instructions`, `normalize_clusters`, `write_lesson_plan`, `act`). `normalize_clusters` is the **pattern to mirror** for `normalize_collateral` (pure, idempotent, never-crash backstop).
7. `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` — entry format for the new family.

## The content model (the contract dev must encode)

A normative sketch — dev pins exact field names against the scaffold + checklist. **All models:** `ConfigDict(extra="forbid", validate_assignment=True)`; value-objects `frozen=True`; tz-aware datetime validators on any timestamp; closed enums get the three red-rejection surfaces (validator + JSON-Schema `enum` + TypeAdapter round-trip); free-text fields carry NO `min_length`.

- **`CollateralSpec`** (top-level, carried on the emitted `lesson_plan["collateral"]`):
  - `schema_version: str` (default `SCHEMA_VERSION`, pinned; AC-C.2-style version field).
  - `declaration: Literal["present", "none"]` — **the explicit empty-case discriminant.** `"none"` = the on-record decision that this lesson ships deck-only (degenerate-empty); `"present"` requires ≥1 workbook section.
  - `workbook: WorkbookSpec | None` — present iff `declaration == "present"`; a `model_validator(mode="after")` enforces the discriminant↔payload invariant (bypass-guard idiom, checklist §13).
  - `research_goals: list[ResearchEnrichmentGoal]` (MAY be empty even when `declaration == "present"` — research is enrichment, not mandatory for a workbook section).
- **`WorkbookSpec`**:
  - `sections: list[WorkbookSection]` — non-empty when present.
- **`WorkbookSection`** (the content-model heart):
  - `section_id: str` (open-id regex).
  - `learning_objective_id: str` (`OPEN_ID_REGEX_PATTERN` — **the asset-lesson pairing invariant**; required, never empty).
  - `title: str`.
  - `depth_delta: DepthDeltaContract` — **required, the load-bearing field.**
  - `exercises: list[Exercise]` (MAY be empty for a pure-narrative section; but the artifact-level acceptance gate requires ≥1 exercise *somewhere* in the present-case witness).
  - `narrative_intent: str` (free-text, verbatim, no min_length) — the "fuller narrative" brief (prose is composed by S2 under G1, not here).
- **`DepthDeltaContract`** (frozen value-object):
  - `deferred_from_slide: str` — the glance-slide / plan-unit id whose depth is being deferred (open-id regex; the dual-coding anchor).
  - `deferred_depth: str` (free-text, verbatim) — *what* depth moves off the glance-slide into the workbook (the legitimization of the tight VO).
  - optionally `retained_on_slide: str` (free-text) — what stays at glance altitude (helps S2 avoid re-stating).
- **`Exercise`**:
  - `exercise_id: str` (open-id regex).
  - `bloom_level: BloomLevel` — **closed enum** `Literal["remember","understand","apply","analyze","evaluate","create"]` (the six revised-Bloom levels); three red-rejection surfaces.
  - `prompt_intent: str` (free-text verbatim) — the exercise's pedagogical intent (worked prose is S2).
  - `answer_key_source_ref: str` — a **source-grounded** answer-key reference (G3: authored backward from sourced content; in v1 this is the *intent-level reference / `source_ref` placeholder slot* the S3 retrieval set resolves — it must be a structurally-valid `source_ref`-shaped field, not a fabricated citation).
- **`ResearchEnrichmentGoal`** (pedagogical-intent, NOT a fetch query):
  - `goal_id: str` (open-id regex).
  - `pedagogical_intent: str` (free-text verbatim) — e.g. "learner needs the primary-source basis for the 23% figure". **A `field_validator` (warn-or-reject, dev calls it with party-mode default = reject) that rejects obvious raw-query shapes** (e.g. a string that is purely a search-engine query / URL / boolean-operator soup) — the boundary that keeps S1 from pre-empting S3's fetch translation. Document the heuristic; keep it conservative (false-positive-averse, per the verbatim-field discipline).
  - `binds_to_objective_id: str | None` (open-id regex when present) — optional linkage to a workbook section's objective.

> **Digest determinism (checklist §10):** if dev adds a `digest` to `CollateralSpec` (recommended for S2/S3 staleness-gating, mirroring `lesson_plan_digest`), it ships the four §10 edge-case tests. If dev defers the digest to S2, file it as a named follow-on and say so in the CHANGELOG (do not silently omit).

## Acceptance Criteria

Acceptance is the **ARTIFACT WITNESS** (G6), never a green unit suite. Numbered; dev-agent legs are hard-blocking offline; the one live leg is operator-gated per the sandbox-AC split.

- **AC-1 (schema family — dev-agent).** `app/marcus/lesson_plan/collateral_spec.py` defines `CollateralSpec`, `WorkbookSpec`, `WorkbookSection`, `DepthDeltaContract`, `Exercise`, `ResearchEnrichmentGoal`, `BloomLevel` with every checklist idiom: `extra="forbid"` + `validate_assignment=True` on all; `frozen=True` on value-objects; closed `BloomLevel` enum with the **three red-rejection surfaces** (`test_*` for direct-construction, JSON-Schema `enum` array, TypeAdapter round-trip); free-text fields with no `min_length` (tested with the adversarial-string battery: empty/space/tab/`\r\n`/emoji/single-char).
- **AC-2 (objective-binding invariant — dev-agent).** A `WorkbookSection` constructed without a `learning_objective_id` (or with one failing `OPEN_ID_REGEX_PATTERN`) **rejects at construction AND on assignment** (`validate_assignment` proof). Test pins both surfaces.
- **AC-3 (depth-delta required — dev-agent).** A present-case `WorkbookSection` without a `depth_delta` rejects. `DepthDeltaContract` round-trips `deferred_from_slide` (regex-valid) + `deferred_depth` (verbatim). Test asserts the contract is non-optional on a present section.
- **AC-4 (exercise fidelity shape — dev-agent, G3).** `Exercise` requires a valid `bloom_level` (red value rejected on all three surfaces) and an `answer_key_source_ref` of `source_ref` shape. Test pins a red Bloom value RED and a malformed `answer_key_source_ref` RED.
- **AC-5 (research = intent not query — dev-agent).** `ResearchEnrichmentGoal.pedagogical_intent` accepts a pedagogical-intent string and **rejects (default) an obvious raw fetch-query / URL** via the documented heuristic. Test carries ≥1 accepted intent + ≥1 rejected raw-query, plus a near-boundary case documented as accepted (false-positive-averse).
- **AC-6 (explicit empty declaration — dev-agent, no-regression).** `CollateralSpec(declaration="none")` constructs with `workbook=None` and round-trips through `model_validate_json(model_dump_json())` byte-faithfully. `declaration="present"` with `workbook=None` (or zero sections) **rejects** via the discriminant↔payload `model_validator`. `declaration="none"` with a non-null `workbook` **rejects**. (The `collateral: none` decision is on record, never an absent key.)
- **AC-7 (JSON-Schema parity + no-leak — dev-agent).** `collateral_spec.v1.schema.json` is emitted; bidirectional required-vs-optional parity test (checklist §9) passes; `additionalProperties: false` propagates (checklist §14); `test_no_intake_orchestrator_leak_collateral_spec.py` (checklist §11) passes over all `Field(description=...)`, `model_dump_json()`, and the CHANGELOG entry; per-family shape-pin test `test_collateral_spec_shape_stable.py` (checklist §8) passes.
- **AC-8 (Pass-1 additive emission — dev-agent).** `_cluster_emission_instructions`-sibling collateral instructions are appended in `assemble_pass1_prompt`; a pure `normalize_collateral(plan)` backstop (mirroring `normalize_clusters`: pure, idempotent, never-crash, returns a new dict) guarantees `plan["collateral"]` is a well-formed `CollateralSpec`-shaped dict on **both** LLM output and the fallback-unit path; `write_lesson_plan` appends additive collateral lines to `irene-pass1.md`. Offline test: feed `parse_pass1_response` a model response (a) with a present collateral block and (b) with none → both yield a valid `CollateralSpec` (present / `none` respectively); existing plan-unit + cluster lines are **byte-unchanged** (no-regression assertion against a frozen `irene-pass1.md` cluster-section fixture).
- **AC-9 (no-regression to existing Pass-1 — dev-agent).** The full existing `tests/specialists/irene_pass1/` suite stays green (cluster emission, learning events, ratification, scope-lock, mode-singularity). `CONSUMED_PAYLOAD_KEYS` is unchanged (emission is additive on output; no new consumed key). `ruff` clean; `lint-imports` 0-broken; the new schema module is reachable in the import graph (mirror the Amelia-a.2 import-anchor discipline so the module can't rot).
- **AC-10 (artifact-witness, present-case — OPERATOR-GATED live leg / Murat).** **Given** the frozen `tejal-apc-c1-m1-p2-trends` corpus and the predefined v1 collateral intent, **When** a real Pass-1 LLM run completes, **Then** the produced `runs/<id>/irene-pass1.md` + emitted `lesson_plan["collateral"]` validate as a `CollateralSpec(declaration="present")` carrying **≥1 workbook section bound to a real plan-unit `learning_objective_id`**, **a depth-delta naming depth deferred off a real glance-slide**, and **≥1 exercise with a valid Bloom level + answer-key `source_ref` slot**. No mocks; live API; first-run-stands; no retry-to-green. Evidence (the artifact + a structural validation transcript) pasted into Completion Notes.
- **AC-11 (artifact-witness, degenerate-empty round-trip — OPERATOR-GATED live leg).** A Pass-1 run on a deck-only configuration emits `collateral: {declaration: "none", ...}` and the deck pipeline is **byte-unchanged** vs the pre-S1 baseline (the `collateral: none` declaration is the only delta). Confirms the additive/no-regression invariant on a real artifact.
- **AC-12 (honesty gates G3/G4 — governance).** G3 (exercise fidelity): exercises in the witness reference a `source_ref` slot, not a fabricated citation (S3 resolves them; S1 emits the structurally-valid reference + intent). **G4 (no reading-path halo):** Completion Notes state **explicitly** that S1 advances **no** reading-path / fresh-naive-holdout generalization claim — collateral emission is orthogonal to the perception/reading-path arc. SCHEMA_CHANGELOG entry filed for the `collateral_spec` v1 family; **no `dp-vN` bump, no manifest/pack touch** (and if dev found one necessary, it is escalated, not silently taken).

> **Sandbox-AC note.** No forbidden operator-CLI appears in any dev-agent AC block. AC-1..AC-9 are verified via shipped Python deps (pydantic, pytest, ruff, lint-imports) entirely offline. The only live legs (AC-10/AC-11) are **operator-gated** with evidence in Completion Notes — the live LLM Pass-1 run is the artifact-witness, consistent with the no-mocks / first-run-stands discipline. Per the cost-is-not-a-constraint memory, Claude MAY execute the operator-gated live legs itself via a fresh independent subagent under the V1–V4 validity protocol (deterministic structural validator as sole judge; first-run-stands; no edits to the schema/normalizer to chase green).

## Build contract

- **Cycle:** NEW CYCLE. Dev (Codex) runs **T1–T10 RED-first** (write the failing schema/shape/parity/no-leak/emission tests first, then implement to green). Driver prompt: `codex-dev-prompt-braid-s1-lesson-plan-collateral-research-spec.md` (authored after this spec hits ready-for-dev, per the NEW-CYCLE memory). Claude runs **T11**: independent battery + 3-layer adversarial `bmad-code-review` (Blind Hunter / Edge Case Hunter / Acceptance Auditor) + party close + commit + flip `done`.
- **RED-first proof (T10 self-review must show):** at least the empty/present discriminant invariant (AC-6), the objective-binding rejection (AC-2), and the additive-emission no-regression (AC-8) are demonstrated RED before the implementation lands, GREEN after.
- **Scaffold adoption (enforced):** instantiate `collateral_spec.py` + the three test files from `docs/dev-guide/scaffolds/schema-story/`. A from-scratch re-derivation is a review finding.
- **K-floor discipline:** target 1.2–1.5× K. This is one schema module + one emission seam + four test files; do not balloon it.
- **No-leak / single-voice:** `collateral_spec.py` descriptions and the CHANGELOG entry must pass the §11 forbidden-token grep (Marcus is one voice).
- **First-run-stands on the live legs:** AC-10/AC-11 are judged by a deterministic structural validator (a committed function that loads the artifact and asserts the `CollateralSpec` shape); no retry-to-green, no tuning the normalizer to the tejal artifact.

## Named follow-ons (file to deferred-inventory per CLAUDE.md §"Deferred inventory governance")

- `braid-s2-workbook-producer` — `"workbook"` → `MODALITY_REGISTRY` (AC-C.4 schema-version bump) + `WorkbookProducer(ModalityProducer)` consuming this `CollateralSpec`; Markdown→DOCX; prose under G1.
- `braid-s3-thin-research-wiring` — Irene→Tracy→Texas bridge through `production_runner.py`; resolves the `answer_key_source_ref` / research-goal slots to real `source_ref`s; L2 citation fail-mode (G2).
- `collateral-spec-digest` (conditional) — if the `CollateralSpec.digest` is deferred out of S1, file it here with the §10 determinism test surface as the reactivation contract.

## Concurrence

Per the braid ratification §5 spec-authoring contract, after S0–S3 specs are authored to the amendments a **light party concurrence pass** confirms ready-to-implement → launch dev. This spec is authored to DP4 + G1–G6; it asserts the no-manifest-touch finding for that pass to confirm.
