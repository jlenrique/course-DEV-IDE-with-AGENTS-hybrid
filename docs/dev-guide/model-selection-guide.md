# Model Selection Guide (Slab 1)

Three-level model cascade + registry governance per architecture decisions **D2**
(three-level model-cascade code location + override flow) and **D13** (model-registry
mid-migration bump procedure). Slab 1 landed the selector + registry + adapter; this
guide documents the resolution order + override flow for specialist authors.

## Cascade order (Level 1 → Level 3)

The `app.models.selector.resolve_model(call_context)` function walks these three
levels in order. The first level that returns a concrete model identifier wins;
no fallback to the next level on a concrete miss — only on absence.

### Level 1 — Per-call override

The highest-priority override. A specialist (or the operator via runtime CLI at
Slab 3+) passes an explicit `model_id` into the call context. Bypasses all downstream
resolution; the selector emits a `per_call_override` breadcrumb into the resolution
trail so the LangSmith span records the caller-supplied choice.

Shape: `{"model_id": "gpt-4.1-mini", "source": "per_call_override"}`.

When to use: rare — reserved for cost-cap overrides, A/B experiments, and debug
probes. Specialists should almost never need this at Slab 2+; the per-specialist
level is the right home for steady-state choices.

### Level 2 — Per-specialist `model_config.yaml`

Each specialist ships `app/specialists/{specialist_id}/model_config.yaml` naming the
model tier this specialist uses by default. Slab 2 stories populate these files as
part of each specialist's scaffold; Slab 1 ships the schema + selector (no specialist
configs shipped — every node's `model_config_ref` in the migrated v4.2 manifest is
currently `null`, letting Level 3 serve).

Shape (per-specialist):

```yaml
# app/specialists/{specialist_id}/model_config.yaml
specialist_id: "irene"           # must match directory name
tier: "s"                        # "f" (fast) | "m" (mid) | "s" (smart) — auto-select cascade input
default_model: "gpt-4.1"         # resolved against registry; overridden only by Level 1
temperature: 0.7                 # documented variance per NFR-X5
rationale: "Irene's cluster-aware narration needs the s-tier."
```

The `tier` field drives auto-select policy (Level 3). A specialist can pin
`default_model` to a specific registry entry OR leave it blank and inherit the tier's
default.

### Level 3 — Registry default (auto-select policy)

`state/config/model-registry.yaml` enumerates the known OpenAI models (Slab 1 locks
OpenAI per PRD) with a `tier` assignment each. `state/config/model-selection-policy.yaml`
maps tier names → preferred model per tier.

The auto-select policy walks the tier's preferred-model list top-down, returning
the first available entry. A registry bump per D13 adds new models to the pool
(Tier-1 patch) or shifts tier assignments (Tier-2 minor) or introduces a new tier
(Tier-3 major).

Shape (registry):

```yaml
# state/config/model-registry.yaml
version: "1.0"
models:
  - id: "gpt-4.1"
    tier: "s"
    max_tokens: 128000
    supports_cache_prefix: true
  - id: "gpt-4.1-mini"
    tier: "m"
    max_tokens: 128000
    supports_cache_prefix: true
  - id: "gpt-4.1-nano"
    tier: "f"
    max_tokens: 128000
    supports_cache_prefix: true
```

Shape (policy):

```yaml
# state/config/model-selection-policy.yaml
version: "1.0"
tiers:
  s:
    preferred: ["gpt-4.1"]
    fallback: []
  m:
    preferred: ["gpt-4.1-mini"]
    fallback: ["gpt-4.1"]
  f:
    preferred: ["gpt-4.1-nano"]
    fallback: ["gpt-4.1-mini"]
```

## Model-resolution trail (NFR-O4)

Every cascade resolution appends a `ModelResolutionEntry` to `RunState.model_resolution_trail`
(schema from Story 1.2; full cascade shape from Story 1.3). Each entry carries:

- `specialist_id` — who asked
- `call_id` — UUID4 per LLM call
- `requested_tier` — the tier the specialist asked for
- `resolved_model` — the model id the cascade picked
- `source` — `per_call_override` / `per_specialist` / `registry_default`
- `timestamp` — UTC
- `cache_prefix_hash` — stable cache-key prefix per NFR-I6

The trail is emitted as a LangSmith span tag + persisted in `RunState` so any
resumed graph can inspect past model selections without re-running the selector.

## Version-bump procedure (D13)

The registry + policy files are versioned via the top-level `version: "<major>.<minor>"`
field. D13 distinguishes three tiers of change:

- **Tier-1 (patch)** — additive; new model added to an existing tier, or a
  documentation-only change. Dev-agent authority; single-gate story.
- **Tier-2 (minor)** — non-breaking shift; tier reassignment, new tier introduced
  but existing specialists keep their current tier. Party-mode consensus required
  BEFORE the dev story opens; version bump in the file.
- **Tier-3 (major)** — breaking; tier removed, cascade semantics changed,
  reproducibility contract affected (NFR-X4 trail shape changes). Party-mode +
  operator sign-off; major version bump.

At each bump, the frozen-graph-version ceremony (architecture §D8, Slab 4 Story 4.5)
snapshots the registry alongside the compiled graph so byte-for-byte replay against
an earlier run picks the exact same model.

## Related

- Architecture decisions: D2 (cascade), D13 (registry bump)
- PRD requirements: FR17–FR21 (cascade), FR22 (resolution trail), FR23 (cache
  stability), NFR-O4 (trail spans), NFR-I6 (cache-prefix stability), NFR-X4
  (reproducibility — model selection trail)
- Code: `app/models/selector.py`, `app/models/selection_policy.py`,
  `app/models/registry.py`, `app/models/adapter.py`
- State shape: `app/models/state/model_resolution_entry.py`
- Pipeline manifest reference: [`langgraph-migration-guide.md §7`](langgraph-migration-guide.md)
