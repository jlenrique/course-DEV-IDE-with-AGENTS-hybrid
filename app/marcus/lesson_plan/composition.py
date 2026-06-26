"""Compile-time component composer + two-part content-addressed digest (S2).

Composition is a COMPILE-TIME act, before the freeze (composition-catalog
ratification 2026-06-25, party GREEN-WITH-AMENDMENTS). A ``ComponentSelection``
names which components are in a run; the composer assembles ONLY the selected
components' manifest nodes into ONE :class:`PipelineManifest`; the runner then
compiles + freezes that assembled composition. Freeze-AFTER-assembly preserves
the proven single-frozen-graph + tamper-evident replay invariant.

Components form a typed producer->consumer DAG (motion consumes deck; workbook
consumes deck). The composer topo-sorts the selection and **FAILS CLOSED** on an
unresolved dependency or a cycle — no partial graph ever reaches freeze.

This module also de-orphans the Lesson-Planner registries
(:mod:`app.marcus.lesson_plan.modality_registry` /
:mod:`app.marcus.lesson_plan.component_type_registry`): the component fragments
bind to registered modalities and the binding is validated at import.

Two-part digest (Murat binding):
  * ``input_closure_digest`` = H(canonical(selection) (+) per-selected-component
    CONTENT-hash (sha256 of the fragment's normalized bytes, NOT a version label)
    (+) composer_version (+) model_config closure (+) frozen/pack version (+)
    digest_schema_version).
  * ``composed_graph_digest`` = canonicalized node_ids + edge_tuples + node
    versions + dispatch_snapshot.
Composition is a PURE function: same ``input_closure_digest`` => same
``composed_graph_digest``.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.manifest import compiler, load
from app.manifest.lanes import DEFAULT_RUN_MANIFEST_PATH
from app.manifest.schema import EdgeSpec, NodeSpec, PipelineManifest, ProjectionSpec
from app.marcus.lesson_plan.component_type_registry import COMPONENT_TYPE_REGISTRY
from app.marcus.lesson_plan.modality_registry import MODALITY_REGISTRY
from app.models.state.component_selection import ComponentSelection
from app.runtime.compiled_graph_digest import (
    DIGEST_SCHEMA_VERSION,
    TwoPartDigest,
    TwoPartDigestMismatchError,
    assert_two_part_digests_match,
    canonical_sha256,
)

COMPOSER_VERSION = "composer-v1"
"""Version of the composition algorithm. Folded into the input closure so a
composer-logic change is tamper-evident (a recorded digest under an old
composer_version refuses replay under a new one)."""

OPTIONAL_PROJECTION_KEYS: frozenset[str] = frozenset({"motion_receipts"})
"""Consumer input keys (on ``dependencies`` / ``dependency_projections``) whose
PRODUCER component may legitimately be DESELECTED — the consumer tolerates the
absent input.

Cross-component contract (MF-1, party composition-catalog 2026-06-25): a KEPT
node can name a producer that lives in an excluded component. The compositor
(node ``14``, deck-base) projects ``motion_receipts`` from ``kira`` (motion); a
deck-only lesson has NO motion, so the compositor runs WITHOUT motion_receipts —
the projection is PRUNED, not frozen as an orphan, and the consumer must tolerate
the absent optional input.

This is the EXPLICIT optional/required declaration the composer consults: any
projection/dependency input key NOT in this set whose producer is absent from the
composition is treated as REQUIRED and FAILS CLOSED (``CompositionError`` before
compile). Widening this set is a governance act, not a runtime convenience."""

WORKBOOK_STUB_NODE_ID = "07W"
"""Stub graph node the workbook fragment contributes until the real producer is
wired as a brick (S3). Lets the composer prove select/exclude-by-registry with a
stub per the S2 scope note."""

_SENTINELS = frozenset({"__start__", "__end__"})

# Motion modality is not yet in MODALITY_REGISTRY (its registry wiring is the S1
# motion-brick's job); the composer carries it as a stub binding so it can still
# select/exclude the real manifest motion nodes by registry-shaped fragment.
_STUB_MODALITIES = frozenset({"motion"})


class CompositionError(RuntimeError):
    """Raised when a selection cannot be composed into a valid frozen graph
    (unresolved dependency, cycle, or a dangling edge endpoint). FAIL CLOSED."""


class CompositionReplayError(CompositionError):
    """Raised when a recorded two-part digest fails to replay (tamper-evidence)."""


@dataclass(frozen=True)
class ComponentFragment:
    """One composable component: its modality binding, owned manifest nodes, and
    producer->consumer dependencies."""

    component: str
    modality_refs: tuple[str, ...]
    manifest_node_ids: frozenset[str]
    depends_on: tuple[str, ...]
    version: str
    is_base: bool = False
    synthetic_nodes: tuple[NodeSpec, ...] = ()
    attach_after: str | None = None


def _workbook_stub_node() -> NodeSpec:
    return NodeSpec(
        id=WORKBOOK_STUB_NODE_ID,
        specialist_id=None,
        gate=False,
        hud_tracked=False,
        pack_version="v4.2",
        rationale=(
            "S2 workbook stub node. The workbook companion is produced by "
            "WorkbookProducer out of band (DOCX); this stub gives the composer a "
            "registry-selectable graph node so deck+motion+workbook is "
            "topologically distinct until the real brick lands (S3)."
        ),
    )


COMPONENT_FRAGMENTS: dict[str, ComponentFragment] = {
    "deck": ComponentFragment(
        component="deck",
        modality_refs=("slides",),
        manifest_node_ids=frozenset(),  # base = remainder (all nodes not owned elsewhere)
        depends_on=(),
        version="deck-v1",
        is_base=True,
    ),
    "motion": ComponentFragment(
        component="motion",
        modality_refs=("motion",),  # stub binding (see _STUB_MODALITIES)
        manifest_node_ids=frozenset({"07D", "07E", "07F"}),
        depends_on=("deck",),
        version="motion-v1",
    ),
    "workbook": ComponentFragment(
        component="workbook",
        modality_refs=("workbook",),
        manifest_node_ids=frozenset(),
        depends_on=("deck",),
        version="workbook-v1",
        synthetic_nodes=(_workbook_stub_node(),),
        attach_after="15",
    ),
}


def _validate_fragment_registry_bindings() -> None:
    """De-orphan + defend: every fragment modality must be registered (or a known
    stub), and the curated component types must exist."""
    for frag in COMPONENT_FRAGMENTS.values():
        for ref in frag.modality_refs:
            if ref not in MODALITY_REGISTRY and ref not in _STUB_MODALITIES:
                raise CompositionError(
                    f"component {frag.component!r} binds unknown modality {ref!r} "
                    f"(not in MODALITY_REGISTRY and not a known stub)"
                )
    # Reference the curated catalog so it is no longer orphaned.
    if "narrated-deck" not in COMPONENT_TYPE_REGISTRY:
        raise CompositionError(
            "component_type_registry missing the 'narrated-deck' curated type"
        )


_validate_fragment_registry_bindings()


def _repo_root(repo_root: Path | None) -> Path:
    return repo_root if repo_root is not None else compiler._repo_root()


def _resolve_order(selection: ComponentSelection) -> tuple[str, ...]:
    """Topo-ordered selected components. FAIL CLOSED on unresolved dep or cycle."""
    selected = list(selection.selected_components())
    sset = set(selected)

    for name in selected:
        frag = COMPONENT_FRAGMENTS.get(name)
        if frag is None:
            raise CompositionError(f"unknown component {name!r}")
        for dep in frag.depends_on:
            if dep not in sset:
                raise CompositionError(
                    f"component {name!r} requires unselected dependency {dep!r} "
                    "(typed producer->consumer DAG fail-closed)"
                )

    deps_map = {
        n: [d for d in COMPONENT_FRAGMENTS[n].depends_on if d in sset] for n in selected
    }
    indeg = {n: len(deps_map[n]) for n in selected}
    ready = sorted(n for n in selected if indeg[n] == 0)
    order: list[str] = []
    while ready:
        node = ready.pop(0)
        order.append(node)
        for other in selected:
            if node in deps_map[other]:
                indeg[other] -= 1
                if indeg[other] == 0:
                    ready.append(other)
                    ready.sort()
    if len(order) != len(selected):
        raise CompositionError(
            "dependency cycle among selected components "
            f"{sorted(set(selected) - set(order))} — no partial graph is frozen"
        )
    return tuple(order)


def _component_owned_ids(component: str, all_ids: set[str]) -> set[str]:
    frag = COMPONENT_FRAGMENTS[component]
    if frag.is_base:
        owned_elsewhere: set[str] = set()
        for other in COMPONENT_FRAGMENTS.values():
            if not other.is_base:
                owned_elsewhere |= other.manifest_node_ids & all_ids
        return all_ids - owned_elsewhere
    return set(frag.manifest_node_ids) & all_ids


def _resolve_excluded_target(
    excluded: str, adj: dict[str, list[str]], kept: set[str], path: frozenset[str]
) -> list[str]:
    """Ordered kept/sentinel nodes reachable from an excluded node via excluded-only hops."""
    results: list[str] = []
    for nxt in adj.get(excluded, []):
        if nxt in kept or nxt in _SENTINELS:
            if nxt not in results:
                results.append(nxt)
        elif nxt not in path:
            for resolved in _resolve_excluded_target(
                nxt, adj, kept, path | {excluded}
            ):
                if resolved not in results:
                    results.append(resolved)
    return results


def _bridge_edges(edges: list[EdgeSpec], included: set[str]) -> list[EdgeSpec]:
    """Drop edges incident to excluded nodes; bridge across them so the surviving
    spine stays connected (a -> [excluded...] -> b becomes a -> b)."""
    adj: dict[str, list[str]] = {}
    for edge in edges:
        adj.setdefault(edge.from_node, []).append(edge.to)

    def kept(node: str) -> bool:
        return node in included or node in _SENTINELS

    new_edges: list[EdgeSpec] = []
    seen: set[tuple[str, str]] = set()
    for edge in edges:
        if not kept(edge.from_node):
            continue
        if kept(edge.to):
            if (edge.from_node, edge.to) not in seen:
                new_edges.append(edge)
                seen.add((edge.from_node, edge.to))
            continue
        for target in _resolve_excluded_target(
            edge.to, adj, included, frozenset({edge.from_node})
        ):
            if (edge.from_node, target) not in seen:
                new_edges.append(EdgeSpec(**{"from": edge.from_node, "to": target}))
                seen.add((edge.from_node, target))
    return new_edges


def _apply_synthetic_attachments(
    edges: list[EdgeSpec], attachments: list[tuple[str, list[NodeSpec]]]
) -> list[EdgeSpec]:
    result = list(edges)
    for attach_after, chain in attachments:
        successors = [e.to for e in result if e.from_node == attach_after]
        result = [e for e in result if e.from_node != attach_after]
        result.append(EdgeSpec(**{"from": attach_after, "to": chain[0].id}))
        for upstream, downstream in zip(chain, chain[1:], strict=False):
            result.append(EdgeSpec(**{"from": upstream.id, "to": downstream.id}))
        for target in successors:
            result.append(EdgeSpec(**{"from": chain[-1].id, "to": target}))
    return result


def _prune_absent_optional_inputs(
    node: NodeSpec, removed_specialists: frozenset[str]
) -> NodeSpec:
    """Resolve a KEPT node's cross-component inputs against the DESELECTED specialists.

    ``removed_specialists`` are the canonical specialist ids that existed as nodes
    in the full manifest but were EXCLUDED by this selection (their owning
    component was deselected). A producer NOT in this set is left untouched — that
    includes implicit/external producers that are never manifest nodes (e.g.
    ``package_builder`` feeding gary), which are selection-independent.

    For each ``dependencies`` value / ``dependency_projections[*]`` producer whose
    component was deselected:
      * input key in :data:`OPTIONAL_PROJECTION_KEYS` -> PRUNE (the consumer
        tolerates the absent optional input — a deck-only compositor runs without
        motion_receipts);
      * otherwise REQUIRED -> raise :class:`CompositionError` (fail closed BEFORE
        compile; no orphaned projection/dependency is ever frozen).

    Returns ``node`` unchanged when nothing is pruned (preserves byte-identity for
    full/default selections where no producer component is deselected)."""
    deps_changed = False
    new_deps: dict[str, str] | None = node.dependencies
    if node.dependencies:
        kept_deps: dict[str, str] = {}
        for key, producer in node.dependencies.items():
            if compiler._canonical_specialist_id(producer) not in removed_specialists:
                kept_deps[key] = producer
            elif key in OPTIONAL_PROJECTION_KEYS:
                deps_changed = True  # prune the optional dependency
            else:
                raise CompositionError(
                    f"node {node.id!r} requires dependency {key!r} from producer "
                    f"{producer!r}, whose component was deselected (absent from the "
                    "composition); not in OPTIONAL_PROJECTION_KEYS so this fails "
                    "closed — no orphaned graph is frozen"
                )
        if deps_changed:
            new_deps = kept_deps or None

    proj_changed = False
    new_proj: dict[str, ProjectionSpec] | None = node.dependency_projections
    if node.dependency_projections:
        kept_proj: dict[str, ProjectionSpec] = {}
        for key, spec in node.dependency_projections.items():
            if compiler._canonical_specialist_id(spec.from_specialist) not in removed_specialists:
                kept_proj[key] = spec
            elif key in OPTIONAL_PROJECTION_KEYS:
                proj_changed = True  # prune the optional projection
            else:
                raise CompositionError(
                    f"node {node.id!r} requires projection {key!r} from producer "
                    f"{spec.from_specialist!r}, whose component was deselected "
                    "(absent from the composition); not in OPTIONAL_PROJECTION_KEYS "
                    "so this fails closed — no orphaned graph is frozen"
                )
        if proj_changed:
            new_proj = kept_proj or None

    if not deps_changed and not proj_changed:
        return node
    return node.model_copy(
        update={"dependencies": new_deps, "dependency_projections": new_proj}
    )


def compose_manifest(
    manifest: PipelineManifest, selection: ComponentSelection
) -> PipelineManifest:
    """Assemble ONLY the selected components' nodes into one PipelineManifest.

    Returns the manifest UNCHANGED (byte-identical) when every present component
    is selected and no synthetic nodes are added — the conditional composer is a
    no-op for the full/default selection.
    """
    order = _resolve_order(selection)
    all_id_set = {node.id for node in manifest.nodes}

    included_ids: set[str] = set()
    synthetic_nodes: list[NodeSpec] = []
    attachments: list[tuple[str, list[NodeSpec]]] = []
    for name in order:
        frag = COMPONENT_FRAGMENTS[name]
        included_ids |= _component_owned_ids(name, all_id_set)
        if frag.synthetic_nodes:
            synthetic_nodes.extend(frag.synthetic_nodes)
            if frag.attach_after is not None:
                attachments.append((frag.attach_after, list(frag.synthetic_nodes)))

    excluded_ids = all_id_set - included_ids
    if not excluded_ids and not synthetic_nodes:
        return manifest  # byte-identical no-op

    included_nodes = [node for node in manifest.nodes if node.id in included_ids]
    # MF-1: a KEPT node may name a producer in an EXCLUDED component. Compute the
    # specialists REMOVED by this selection (present as nodes in the full manifest,
    # absent from the kept set) and resolve each kept node's cross-component inputs
    # against them — prune optional orphans, fail closed on required ones — so no
    # orphaned projection/dependency is ever frozen. Implicit/external producers
    # that are never manifest nodes (e.g. package_builder) are selection-independent
    # and stay untouched.
    full_specialists = frozenset(
        canon
        for node in manifest.nodes
        if (canon := compiler._canonical_specialist_id(node.specialist_id)) is not None
    )
    present_specialists = frozenset(
        canon
        for node in included_nodes
        if (canon := compiler._canonical_specialist_id(node.specialist_id)) is not None
    )
    removed_specialists = full_specialists - present_specialists
    included_nodes = [
        _prune_absent_optional_inputs(node, removed_specialists) for node in included_nodes
    ]
    new_nodes = [*included_nodes, *synthetic_nodes]
    new_edges = _bridge_edges(list(manifest.edges), included_ids)
    new_edges = _apply_synthetic_attachments(new_edges, attachments)

    node_id_set = {node.id for node in new_nodes} | _SENTINELS
    for edge in new_edges:
        if edge.from_node not in node_id_set or edge.to not in node_id_set:
            raise CompositionError(
                f"composed edge {edge.from_node!r}->{edge.to!r} references a node "
                "absent from the composition (fail closed; no partial graph frozen)"
            )
    if manifest.entrypoint not in _SENTINELS and manifest.entrypoint not in {
        node.id for node in new_nodes
    }:
        raise CompositionError(
            f"entrypoint {manifest.entrypoint!r} was excluded by the selection"
        )

    return manifest.model_copy(update={"nodes": new_nodes, "edges": new_edges})


def component_content_hash(
    component: str, manifest: PipelineManifest, repo_root: Path | None = None
) -> str:
    """Content-address a component: sha256 over the NORMALIZED BYTES of the
    manifest material it owns (node specs) + its registry binding + version.

    Content-addressed, NOT label-hashed: editing a node's bytes changes this hash
    even if the component version label is unchanged."""
    del repo_root  # node bytes are repo-root-independent
    frag = COMPONENT_FRAGMENTS[component]
    all_id_set = {node.id for node in manifest.nodes}
    owned = _component_owned_ids(component, all_id_set)
    node_specs = sorted(
        (
            [node.id, node.model_dump(mode="json", by_alias=True)]
            for node in manifest.nodes
            if node.id in owned
        ),
        key=lambda pair: pair[0],
    )
    synthetic = sorted(
        (node.model_dump(mode="json", by_alias=True) for node in frag.synthetic_nodes),
        key=lambda dump: dump["id"],
    )
    payload: dict[str, Any] = {
        "component": frag.component,
        "modality_refs": list(frag.modality_refs),
        "depends_on": list(frag.depends_on),
        "version": frag.version,
        "node_specs": node_specs,
        "synthetic_nodes": synthetic,
    }
    return canonical_sha256(payload)


def _model_config_closure(
    manifest: PipelineManifest, included_ids: set[str], repo_root: Path
) -> list[list[str]]:
    closure: list[list[str]] = []
    for node in manifest.nodes:
        if node.id in included_ids and node.model_config_ref:
            data = (repo_root / node.model_config_ref).read_bytes()
            closure.append([node.id, hashlib.sha256(data).hexdigest()])
    return sorted(closure, key=lambda pair: pair[0])


def _load_dispatch_for_digest(
    repo_root: Path, dispatch_snapshot: dict[str, Any] | None
) -> dict[str, Any]:
    if dispatch_snapshot is not None:
        return dispatch_snapshot
    return dict(compiler._load_dispatch_registry(repo_root))


def compose_and_digest(
    selection: ComponentSelection,
    manifest: PipelineManifest | None = None,
    *,
    dispatch_snapshot: dict[str, Any] | None = None,
    repo_root: Path | None = None,
    composer_version: str = COMPOSER_VERSION,
) -> TwoPartDigest:
    """Compose the selected graph and return its two-part content-addressed digest."""
    manifest = manifest if manifest is not None else load(DEFAULT_RUN_MANIFEST_PATH)
    root = _repo_root(repo_root)

    order = _resolve_order(selection)
    composed = compose_manifest(manifest, selection)
    graph = compiler.compile(composed, repo_root=root)

    node_ids = sorted(str(node_id) for node_id in graph.nodes)
    edge_tuples = sorted([str(src), str(dst)] for src, dst in graph.edges)
    node_versions: dict[str, str | None] = {node.id: node.pack_version for node in composed.nodes}
    included_ids = {node.id for node in composed.nodes}

    content_hashes = {name: component_content_hash(name, manifest, root) for name in order}
    versions = {name: COMPONENT_FRAGMENTS[name].version for name in order}
    mc_closure = _model_config_closure(manifest, included_ids, root)
    dispatch = _load_dispatch_for_digest(root, dispatch_snapshot)

    input_payload: dict[str, Any] = {
        "digest_schema_version": DIGEST_SCHEMA_VERSION,
        "composer_version": composer_version,
        "component_selection": selection.as_map(),
        "component_content_hashes": content_hashes,
        "component_versions": versions,
        "model_config_closure": mc_closure,
        "frozen_graph_version": composed.frozen_graph_version,
        "pack_version": composed.pack_version,
    }
    composed_payload: dict[str, Any] = {
        "digest_schema_version": DIGEST_SCHEMA_VERSION,
        "schema_version": composed.schema_version,
        "frozen_graph_version": composed.frozen_graph_version,
        "node_ids": node_ids,
        "edge_tuples": edge_tuples,
        "node_versions": node_versions,
        "dispatch_snapshot": dispatch,
    }

    return TwoPartDigest(
        composer_version=composer_version,
        component_selection=selection.as_map(),
        component_content_hashes=content_hashes,
        component_versions=versions,
        model_config_closure=mc_closure,
        frozen_graph_version=composed.frozen_graph_version,
        pack_version=composed.pack_version,
        input_closure_digest=canonical_sha256(input_payload),
        composed_graph_digest=canonical_sha256(composed_payload),
        composed_node_ids=node_ids,
        composed_edge_tuples=edge_tuples,
        composed_node_versions=node_versions,
    )


def verify_composition_replay(
    record: TwoPartDigest | dict[str, Any],
    *,
    manifest: PipelineManifest | None = None,
    dispatch_snapshot: dict[str, Any] | None = None,
    repo_root: Path | None = None,
) -> None:
    """Re-resolve -> recompute -> compare a recorded two-part digest. RAISES
    :class:`CompositionReplayError` on any drift (mutated selection, mutated
    fragment bytes without a version bump, mutated composer_version/model_config,
    or a stale digest_schema_version). Tamper-evidence is replay-RAISES, never warn."""
    if isinstance(record, dict):
        record = TwoPartDigest.model_validate(record)

    selection = ComponentSelection(**record.component_selection)
    try:
        recomputed = compose_and_digest(
            selection,
            manifest=manifest,
            dispatch_snapshot=dispatch_snapshot,
            repo_root=repo_root,
            composer_version=COMPOSER_VERSION,
        )
        assert_two_part_digests_match(record, recomputed)
    except TwoPartDigestMismatchError as exc:
        raise CompositionReplayError(str(exc)) from exc


__all__ = [
    "COMPONENT_FRAGMENTS",
    "COMPOSER_VERSION",
    "OPTIONAL_PROJECTION_KEYS",
    "WORKBOOK_STUB_NODE_ID",
    "ComponentFragment",
    "CompositionError",
    "CompositionReplayError",
    "component_content_hash",
    "compose_and_digest",
    "compose_manifest",
    "verify_composition_replay",
]
