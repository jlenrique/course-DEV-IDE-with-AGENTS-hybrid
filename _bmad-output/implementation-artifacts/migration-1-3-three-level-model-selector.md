# Migration Story 1.3: Three-Level Model Selector + Registry + Adapter + Selection Policy

**Status:** ready-for-dev
**Sprint key:** 1-3-three-level-model-selector
**Epic:** Slab 1 Substrate (migration Epic 1)
**Milestone anchored:** M1 — model selection cascade for every LLM call.
**Pts:** 3 | **Gate:** dual (schema-shape in PipelineRegistry) | **K-target:** ~1.4×

## Story

As a **dev agent landing the model-selection substrate**,
I want **the full `PipelineRegistry` model + `ModelSelectionPolicy` schema + `app.models.selector` (three-level cascade resolution: per-call → per-specialist → registry default + auto-select policy) + `app.models.adapter` (thin `ChatOpenAI` wrapper with model-resolution-trail span emission)**,
So that **every downstream LLM-invoking node resolves through a uniform cascade, FR17–FR21 are satisfied, model selections + auto-select fallback trail are persistent in `RunState.model_resolution_trail` (NFR-X4 reproducibility), and Marcus's per-specialist override flow has a stable contract from Day 1**.

## Acceptance Criteria

All ACs dev-agent-executable. Schema-shape story for `PipelineRegistry` + `ModelSelectionPolicy` + `ModelResolutionEntry` (latter is the full version of the stub 1.2 left in `RunState`).

### AC-1.3-A — Full `PipelineRegistry` model (replaces 1.1c stub)

- **Given** 1.1c shipped a stub `PipelineRegistry` with `Field(default=None)`-permissive shape
- **When** the dev agent extends it to the full schema per architecture §D2 + Decision §Three-Level Model Cascade: `id: UUID4`, `entries: list[RegistryEntry]`, `default_model_id: str`, `auto_select_enabled: bool`, with `RegistryEntry` carrying `id`, `display_name`, `provider: Literal["openai"]`, `context_window: int`, `cost_per_million_input_tokens: Decimal`, `cost_per_million_output_tokens: Decimal`, `tier: Literal["reasoning", "code", "fast"]`, `available: bool`
- **Then** the model is four-file-lockstep complete (model + validator + tests + golden fixture); `app/models/registry.yaml` extended to a real catalog (≥3 entries: gpt-5.4 reasoning, gpt-5-haiku fast, etc.); `registry_check` from 1.1c now exercises the full validation path.

### AC-1.3-B — `ModelSelectionPolicy` schema

- **Given** auto-select rules need to be data-driven (per architecture D2)
- **When** the dev agent authors `ModelSelectionPolicy` Pydantic model + `app/models/selection_policy.yaml` declaring rules of shape `{when: <predicate>, prefer_tier: <tier>, fallback_chain: [<model_id>, ...]}`
- **Then** the model + YAML round-trip; selection-policy tests assert that conflicting rules surface as named violations (not silent overrides).

### AC-1.3-C — `ModelResolutionEntry` full schema (replaces 1.2 stub)

- **Given** 1.2 shipped a stub `ModelResolutionEntry` placeholder
- **When** the dev agent extends to the full shape: `level: Literal["per_call", "per_specialist", "registry_default", "auto_select_fallback"]`, `requested: str | None`, `resolved: str`, `reason: str`, `timestamp: datetime` (timezone-aware), `cache_prefix_hash: str | None`
- **Then** `RunState.model_resolution_trail: list[ModelResolutionEntry]` carries the full structure; NFR-X4 assertion test in 1.2's `test_reproducibility_invariants.py` is updated to use the real shape (cross-story reference noted in commit body).

### AC-1.3-D — `app.models.selector` three-level cascade

- **Given** the cascade order is per-call override → per-specialist `model_config.yaml` → registry default → auto-select policy fallback
- **When** the dev agent authors `app/models/selector.py` exporting `resolve(specialist_id: str, per_call_override: str | None = None) -> ResolveResult` returning `(model_id, ModelResolutionEntry)`
- **Then** unit tests `tests/unit/models/test_selector.py` cover all four cascade paths + the cache-prefix-stability rule (same input → same `cache_prefix_hash`); auto-select fallback exercises the policy YAML; failures surface as named exceptions, not silent registry-default fallback.

### AC-1.3-E — `app.models.adapter` thin `ChatOpenAI` wrapper

- **Given** PRD Decision 3 ("reject the LangChain cage") mandates direct `ChatOpenAI` adapter use, no high-level agent abstractions
- **When** the dev agent authors `app/models/adapter.py` exporting `make_chat_model(specialist_id, per_call_override=None) -> ChatOpenAI` that:
  - Calls `selector.resolve(...)` → gets `(model_id, resolution_entry)`
  - Constructs `ChatOpenAI(model=model_id, ...)` with appropriate temperature from `RunState`
  - Emits a LangSmith span with the resolution entry as a tag set: `{model_id, level, requested, resolved, reason, cache_prefix_hash}` per NFR-O4
  - Returns the `ChatOpenAI` instance + appends the resolution entry to the active `RunState.model_resolution_trail` (via context-var or explicit return; pick the cleaner pattern at T1)
- **Then** integration test `tests/integration/models/test_adapter_resolution_trail.py` invokes the adapter on a fixture `RunState`; asserts the trail entry was appended; asserts the LangSmith span carries the resolution-trail tag set; skips LangSmith assertion when `LANGSMITH_API_KEY` unset.

### AC-1.3-F — Cache-prefix stability test

- **Given** NFR-I6 + FR23 require cache-prefix stability across cold-read invocations of the same specialist+input
- **When** the dev agent authors `tests/unit/models/test_cache_prefix_stability.py` invoking `selector.resolve(specialist_id="X", per_call_override=None)` twice in a clean process and asserting the two resulting `cache_prefix_hash` values are byte-identical
- **Then** the test passes; if it fails, that's a NFR-I6 violation that must be fixed before the story closes (no waivers).

## Tasks / Subtasks

- [ ] **T1 — Read T1 Bundle** §1 (D2 model cascade, D13 registry-bump), §2 (FR17-FR21, FR22-FR23, FR24, FR25, NFR-O4), §3 (Pydantic + 4-file-lockstep), §6 (anti-patterns).
- [ ] **T2 — Use schema-story scaffold** for `PipelineRegistry`, `ModelSelectionPolicy`, `ModelResolutionEntry` (full version).
- [ ] **T3 — Author the three schemas + four-file-lockstep** per AC-1.3-A through AC-1.3-C.
- [ ] **T4 — Author selector** per AC-1.3-D + unit tests for all four cascade paths.
- [ ] **T5 — Author adapter** per AC-1.3-E + integration test.
- [ ] **T6 — Cache-prefix stability test** per AC-1.3-F.
- [ ] **T7 — Update `RunState`/`ModelResolutionEntry` imports across `app/`** to use the real shape (delete the stub from 1.2; commit message notes the cross-story tightening).
- [ ] **T8 — Run validators + tests.**
- [ ] **T9 — Commit.** `feat(migration): Slab 1 Story 1.3 — three-level model selector + registry + adapter + selection policy`

## Dev Notes

### Cache-prefix stability is load-bearing for NFR-I6

`cache_prefix_hash` must be deterministic across processes. Use `hashlib.sha256(canonical_json_bytes).hexdigest()` over a normalized tuple `(specialist_id, model_id, temperature, system_prompt_hash)`. Do NOT use `hash()` (Python's built-in) — that's process-randomized.

### Per-specialist `model_config.yaml` shape (referenced from selector)

`app/specialists/_scaffold/model_config.yaml` (stub from 1.1c) gets a real schema in this story. Shape: `{specialist_id: str, default_model: str, per_node_overrides: dict[str, str], temperature_default: float}`. Each Slab-2 specialist will carry one of these.

### FR24 cache-invalidation warning is OUT of 1.3 scope

The full FR24 closure (runtime model-override + cache-invalidation warning) lands in Slab 3 Story 3.5. 1.3 does the pre-submission portion only — the resolution trail captures the override so 3.5 can surface the warning at runtime. **Do NOT** implement the warning surface here; mark `# FR24 warning surface deferred to Slab 3 Story 3.5`.

### Registry version-bump procedure (D13)

Adding a new model to `app/models/registry.yaml` is Tier-1 (dev-agent authority) per D13. Removing or version-pinning is Tier-2 (party-mode). Subtract a model = pre-flight party-mode round, not a unilateral commit. 1.3 lands the initial catalog (additive), so no version-bump governance fires.

### Project Structure Notes

**New files:**
- `app/models/{registry,selection_policy,adapter,selector}.py` (selector, adapter new; registry extends 1.1c stub)
- `app/models/state/model_resolution_entry.py` (full shape)
- `app/models/state/validators/{registry,selection_policy,model_resolution_entry}_validators.py`
- `app/specialists/_scaffold/model_config.yaml` (real shape)
- `app/models/selection_policy.yaml`
- Tests + fixtures per four-file-lockstep × 3 schemas

**Modified:**
- `app/models/registry.yaml` (extend to real catalog)
- `app/models/registry_check.py` (use full validation path)
- `app/models/state/run_state.py` (replace stub `ModelResolutionEntry` reference)

## References

- Bundle: [Set-A T1 Context Bundle](../planning-artifacts/slab1-story-set-A-t1-bundle.md)
- Architecture D2 (model cascade), D13 (registry version-bump)
- PRD FR17-FR25, NFR-O4, NFR-I6

## Dev Agent Record

_(placeholder)_
