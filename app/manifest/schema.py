"""`PipelineManifest` + `NodeSpec` + `EdgeSpec` — the manifest-as-graph-config contract.

Story 1.4 (Slab 1) — realizes architecture decision **D6** (Manifest-as-Graph-Config
Loader). The shape is the union of:

- **Architecture-canonical set** (AC-1.4-A): `schema_version`, `lane`, `entrypoint`,
  `frozen_graph_version`, `nodes`, `edges`
- **v4.2 inventory deltas** from the primary-repo 379-line `pipeline-manifest.yaml`
  performed at T1 per the Winston/Amelia 2026-04-22 amendment (NOT deferred to 1.6):
  top-level `pack_version`, `generator_ref`, `learning_events`, `block_mode_trigger_paths`;
  per-node `label`, `gate`, `gate_code`, `sub_phase_of`, `insertion_after`,
  `hud_tracked`, `pack_section_anchor`, `pack_version`, `rationale`,
  `learning_events`, `dependencies`.

Story 1.6 will migrate the real v4.2 manifest into this schema (synthesizing
`edges` from per-node `insertion_after`, injecting `lane`/`entrypoint`/
`frozen_graph_version`, adding `specialist_id`/`scaffold_node`/`model_config_ref`
per node). At Slab 1 close, the 1.1c stub manifest conforms to the same shape.

Pydantic-v2 idioms per `docs/dev-guide/pydantic-v2-schema-checklist.md`:
- `extra="forbid"` on every model (unknown keys raise, do NOT drift silently)
- `validate_assignment=True` (mutations re-validate; closes G6 MF-1/2/3 from 31-1)
- Closed enums via `Literal[...]`
- No `min_length` on free-text `rationale`
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ManifestLane = Literal["run_graph", "dev_graph"]
"""D4 lane separation — Marcus runtime lane vs Cora dev lane.

The compiler instantiates a separate `StateGraph` per lane; nodes from one lane
never land in the other graph. Enforced via unit test in
`tests/unit/manifest/test_lane_separation.py` (AC-1.4-D).
"""


class LearningEventsConfig(BaseModel):
    """Top-level learning-event wiring (Epic 33 substrate).

    Carries the `schema_ref` pointer the primary-repo v4.2 manifest uses at its
    top level. Per-step emissions live on `NodeSpec.learning_events` via
    `StepLearningEventsConfig`.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    schema_ref: str | None = Field(
        default=None,
        description="Path (repo-relative) to the learning-event schema YAML.",
    )


class StepLearningEventsConfig(BaseModel):
    """Per-node learning-event emission metadata (v4.2 inventory delta)."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    emits: bool = Field(
        default=False,
        description="Whether this node emits learning events at runtime.",
    )
    event_types: list[str] = Field(
        default_factory=list,
        description="Event-type strings this node may emit (open-set; validated by capture layer).",
    )
    schema_ref: str | None = Field(
        default=None,
        description="Optional per-node override of the top-level learning-event schema_ref.",
    )


class NodeSpec(BaseModel):
    """One node in the compiled `StateGraph`.

    Architecture-canonical fields: `id`, `specialist_id`, `scaffold_node`,
    `model_config_ref`. v4.2 inventory deltas ride under the explicit
    extensibility trailing from AC-1.4-A: `label`, `gate`, `gate_code`,
    `sub_phase_of`, `insertion_after`, `hud_tracked`, `pack_section_anchor`,
    `pack_version`, `rationale`, `learning_events`.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    id: str = Field(
        ...,
        min_length=1,
        description="Node identifier (unique within the manifest).",
    )
    specialist_id: str | None = Field(
        default=None,
        description=(
            "Specialist identifier the compiler resolves to a callable. Slab 1 uses a "
            "passthrough stub; full resolution is Slab 2 Story 2a.1 scope."
        ),
    )
    scaffold_node: str | None = Field(
        default=None,
        description=(
            "Which scaffold-node slot (of the 9-node specialist scaffold) this node "
            "represents. Slab 2 concept; optional in Slab 1."
        ),
    )
    model_config_ref: str | None = Field(
        default=None,
        description=(
            "Repo-relative path to a `model_config.yaml` file. Compiler validates "
            "presence at compile time (NFR-M2 / FR25). `None` skips the lint pass."
        ),
    )
    dependencies: dict[str, str] | None = Field(
        default=None,
        description=(
            "Manifest-declared dependency map for production composition. Keys are "
            "downstream specialist input keys; values are upstream specialist ids. "
            "Missing or empty maps use the runner's permanent fallback resolution. "
            "Delivers the WHOLE upstream output dict under the input key — for "
            "granular consumers use dependency_projections instead."
        ),
    )
    dependency_projections: dict[str, ProjectionSpec] | None = Field(
        default=None,
        description=(
            "Edge-level key projection (party review 2026-06-12, Winston "
            "Deviation-2 ruling: projection, not spread). Keys are downstream "
            "consumer input keys; values name the producer specialist and the "
            "producer OUTPUT key to project. Projected input keys are validated "
            "against the consumer's CONSUMED_PAYLOAD_KEYS by the Ratchet-D "
            "contract test; governed by data_plane_vocabulary_version."
        ),
    )
    fold_with: str | None = Field(
        default=None,
        description=(
            "Gate code for an upstream/surfaced pause point this node folds into. "
            "Mutually exclusive with fold_target."
        ),
    )
    fold_target: str | None = Field(
        default=None,
        description=(
            "Named subgraph target for compile-time folding. Mutually exclusive "
            "with fold_with."
        ),
    )

    # v4.2 inventory deltas (per-step metadata)
    label: str | None = Field(
        default=None,
        description="Human-readable step label (v4.2 manifest).",
    )
    gate: bool | None = Field(
        default=None,
        description="Whether this step is a HIL gate (v4.2 manifest).",
    )
    gate_code: str | None = Field(
        default=None,
        description="HIL gate identifier (e.g., 'G0', 'G2C'); v4.2 manifest.",
    )
    sub_phase_of: str | None = Field(
        default=None,
        description="Parent step id for nested sub-phases (v4.2 manifest).",
    )
    insertion_after: str | None = Field(
        default=None,
        description=(
            "Prior step id for linear-chain ordering (v4.2 manifest). Story 1.6 "
            "synthesizes `EdgeSpec` entries from this field when migrating the "
            "real v4.2 manifest."
        ),
    )
    hud_tracked: bool | None = Field(
        default=None,
        description="Whether `run_hud` surfaces this step (v4.2 manifest).",
    )
    pack_section_anchor: str | None = Field(
        default=None,
        description="Prompt-pack section anchor (v4.2 manifest cross-ref).",
    )
    pack_version: str | None = Field(
        default=None,
        description="Per-step prompt-pack version identifier (v4.2 manifest).",
    )
    rationale: str = Field(
        default="",
        description="Free-text rationale (stored verbatim; NO min_length per checklist §6).",
    )
    learning_events: StepLearningEventsConfig | None = Field(
        default=None,
        description="Per-step learning-event emission config (v4.2 manifest).",
    )

    @model_validator(mode="after")
    def _enforce_fold_fields_mutually_exclusive(self) -> NodeSpec:
        if self.fold_with is not None and self.fold_target is not None:
            raise ValueError(
                f"node {self.id}: fold_with and fold_target are mutually exclusive"
            )
        return self

    @model_validator(mode="after")
    def _enforce_projection_keys_disjoint_from_dependencies(self) -> NodeSpec:
        # A key delivered by both mechanisms would reintroduce the silent-
        # precedence genus the adapter collision guard retired.
        if self.dependencies and self.dependency_projections:
            overlap = sorted(set(self.dependencies) & set(self.dependency_projections))
            if overlap:
                raise ValueError(
                    f"node {self.id}: input key(s) {overlap} declared in BOTH "
                    "dependencies and dependency_projections"
                )
        return self


class ProjectionSpec(BaseModel):
    """One projected key on a dependency edge: producer output key -> consumer input key."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        populate_by_name=True,
    )

    from_specialist: str = Field(
        ...,
        min_length=1,
        alias="from",
        description="Producer specialist id (canonical or manifest spelling).",
    )
    key: str = Field(
        ...,
        min_length=1,
        description="Key inside the producer's contribution output to project.",
    )


class EdgeSpec(BaseModel):
    """One edge in the compiled `StateGraph`.

    `condition` (optional) names a callable in the condition-function registry
    (`app.manifest.conditions`). Slab 1 stub registry exposes only
    `"always_true"` and `"always_false"`; full dispatch registry is Slab 3.

    `dispatch_envelope` is the Slab 3 dispatch-shape pointer (trailing `...` from
    AC-1.4-A). Slab 1 accepts any dict payload; Slab 3 narrows to `SpecialistEnvelope`.

    `decision_card_schema` is an additive Slab 3 pointer to the Pydantic model
    that an interrupting gate emits. It uses `<module>:<ClassName>` dotted-ref
    syntax and is compile-time validated by `app.manifest.refs.resolve_dotted_ref`.

    `from_node` is aliased to the YAML/JSON key `"from"` because `from` is a
    Python reserved word and cannot be a field name directly.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        populate_by_name=True,
    )

    from_node: str = Field(
        ...,
        alias="from",
        min_length=1,
        description="Source node id (LangGraph convention: `__start__` marks graph entry).",
    )
    to: str = Field(
        ...,
        min_length=1,
        description="Target node id (LangGraph convention: `__end__` marks graph exit).",
    )
    condition: str | None = Field(
        default=None,
        description=(
            "Optional condition-function name. Presence triggers "
            "`add_conditional_edges`; absence triggers `add_edge`. Resolved at "
            "compile time against the condition registry."
        ),
    )
    dispatch_envelope: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Slab 3 dispatch envelope payload. Slab 1 accepts arbitrary dicts; "
            "Slab 3 narrows the shape to `SpecialistEnvelope`."
        ),
    )
    decision_card_schema: str | None = Field(
        default=None,
        description=(
            "Optional `<module>:<ClassName>` dotted reference naming the "
            "DecisionCard subclass emitted at this edge's gate boundary."
        ),
    )


class PipelineManifest(BaseModel):
    """The manifest-as-graph-config root shape.

    Loaded by `app.manifest.loader.load()` from YAML; compiled by
    `app.manifest.compiler.compile()` into a LangGraph `StateGraph` (one per
    `lane`). Architecture-canonical fields + v4.2 inventory deltas are unified
    here per the Winston/Amelia 2026-04-22 amendment.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    # Architecture-canonical top-level
    schema_version: str = Field(
        ...,
        min_length=1,
        description="Manifest schema version (e.g., '0.1-stub', '1.0').",
    )
    lane: ManifestLane = Field(
        ...,
        description="D4 lane identity (`run_graph` for Marcus runtime; `dev_graph` for Cora).",
    )
    entrypoint: str = Field(
        ...,
        min_length=1,
        description=(
            "Node id that starts the graph. Must match a `nodes[].id` OR the "
            "LangGraph sentinel `__start__` (edges from `__start__` then name the "
            "real entry node)."
        ),
    )
    frozen_graph_version: str = Field(
        ...,
        min_length=1,
        description=(
            "Frozen-graph version identifier (e.g., 'v0.1-stub', 'v42'). "
            "Compiler asserts `runtime/graphs/v{version}/` exists at compile time. "
            "Full ceremony (Slab 4 Story 4.5)."
        ),
    )
    data_plane_vocabulary_version: str | None = Field(
        default=None,
        description=(
            "Versioned home for the manifest's data-plane vocabulary "
            "(dependencies + dependency_projections) — Winston S1-B, party "
            "review 2026-06-12: pack_version provably does not govern the "
            "data plane (regime doc, determination 2026-06-12). Tier-2 "
            "governance for vocabulary changes attaches HERE: bump requires "
            "party-mode consensus, like a pack bump but for edges."
        ),
    )
    nodes: list[NodeSpec] = Field(
        ...,
        description="All graph nodes. Must be non-empty; node ids must be unique.",
    )
    edges: list[EdgeSpec] = Field(
        default_factory=list,
        description=(
            "Explicit edges. For the v4.2 migration, Story 1.6 synthesizes these "
            "from per-node `insertion_after`. Empty is legal (graph with just an "
            "entrypoint and no transitions)."
        ),
    )

    # v4.2 inventory deltas (top-level)
    pack_version: str | None = Field(
        default=None,
        description=(
            "Prompt-pack version identifier (e.g., 'v4.2'). Distinct from "
            "`frozen_graph_version` (LangGraph compiled-graph identity)."
        ),
    )
    generator_ref: str | None = Field(
        default=None,
        description="Repo-relative path to the generator script (pipeline-manifest regime).",
    )
    learning_events: LearningEventsConfig | None = Field(
        default=None,
        description="Top-level learning-event wiring (Epic 33 substrate).",
    )
    block_mode_trigger_paths: list[str] = Field(
        default_factory=list,
        description="Paths whose modification triggers pipeline-manifest regime block-mode review.",
    )

    @field_validator("nodes")
    @classmethod
    def _enforce_nodes_non_empty(cls, value: list[NodeSpec]) -> list[NodeSpec]:
        if not value:
            raise ValueError("PipelineManifest.nodes must be non-empty")
        return value

    @model_validator(mode="after")
    def _enforce_unique_node_ids(self) -> PipelineManifest:
        seen: set[str] = set()
        for node in self.nodes:
            if node.id in seen:
                raise ValueError(f"duplicate node id in manifest: {node.id!r}")
            seen.add(node.id)
        return self

    @model_validator(mode="after")
    def _enforce_entrypoint_resolves(self) -> PipelineManifest:
        if self.entrypoint == "__start__":
            return self
        node_ids = {node.id for node in self.nodes}
        if self.entrypoint not in node_ids:
            raise ValueError(
                f"entrypoint {self.entrypoint!r} does not resolve to a node id "
                f"(known ids: {sorted(node_ids)}; or use the LangGraph sentinel '__start__')"
            )
        return self

    @model_validator(mode="after")
    def _enforce_edge_endpoints_resolve(self) -> PipelineManifest:
        node_ids = {node.id for node in self.nodes}
        sentinels = {"__start__", "__end__"}
        for edge in self.edges:
            if edge.from_node not in node_ids and edge.from_node not in sentinels:
                raise ValueError(
                    f"edge from {edge.from_node!r} does not resolve to a node id "
                    f"(known ids: {sorted(node_ids)}; sentinels: {sorted(sentinels)})"
                )
            if edge.to not in node_ids and edge.to not in sentinels:
                raise ValueError(
                    f"edge to {edge.to!r} does not resolve to a node id "
                    f"(known ids: {sorted(node_ids)}; sentinels: {sorted(sentinels)})"
                )
        return self


__all__ = [
    "EdgeSpec",
    "LearningEventsConfig",
    "ManifestLane",
    "NodeSpec",
    "PipelineManifest",
    "StepLearningEventsConfig",
]
