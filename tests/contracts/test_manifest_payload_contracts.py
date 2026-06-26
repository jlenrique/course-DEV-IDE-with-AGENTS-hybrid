"""Ratchet-D — manifest dependency edges must speak their consumer's vocabulary.

S1 of SCP 2026-06-11 segment-data-plane (party-mode 4-of-4; Murat: "this is
the meta-ratchet; A-C are instances of the class it catches"). For every
manifest node with declared dependencies whose consumer has published a
CONSUMED_PAYLOAD_KEYS contract, every input_key must be a key the consumer
actually reads. The fork this pins: node 07B declared ``upstream_output``
while quinn_r read ``slides`` — Quinn-R approved placeholder content it
never received in Trial-3 attempt-4.

Roster is incremental (Amelia): consumers without a published contract sit
in an explicit quarantine list below. The quarantine is itself pinned — a
NEW dependency edge to an uncontracted consumer fails this test, forcing
either a contract declaration or a deliberate quarantine entry. Sixth
A23/P5 instance should be structurally impossible, not just reviewed-against.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from app.manifest.compiler import SPECIALIST_ALIASES

# Amelia a.2 (party review 2026-06-12): contracts resolve THROUGH the act
# module's namespace, pinning that each act imports its own contract — the
# contract must participate in the consumer's import graph, not sit beside it.
from app.specialists.compositor._act import CONSUMED_PAYLOAD_KEYS as COMPOSITOR_KEYS
from app.specialists.enrique._act import CONSUMED_PAYLOAD_KEYS as ENRIQUE_KEYS
from app.specialists.gary._act import CONSUMED_PAYLOAD_KEYS as GARY_KEYS
from app.specialists.irene.graph import CONSUMED_PAYLOAD_KEYS as IRENE_KEYS
from app.specialists.irene_pass1._act import CONSUMED_PAYLOAD_KEYS as IRENE_PASS1_KEYS
from app.specialists.kira._act import CONSUMED_PAYLOAD_KEYS as KIRA_KEYS
from app.specialists.motion_planner._act import CONSUMED_PAYLOAD_KEYS as MOTION_PLANNER_KEYS
from app.specialists.quinn_r._act import CONSUMED_PAYLOAD_KEYS as QUINN_R_KEYS
from app.specialists.vision.graph import CONSUMED_PAYLOAD_KEYS as VISION_KEYS
from app.specialists.workbook_producer._act import (
    CONSUMED_PAYLOAD_KEYS as WORKBOOK_PRODUCER_KEYS,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "state" / "config" / "pipeline-manifest.yaml"

# Consumers with published payload contracts (S1 roster: quinn_r + gary;
# irene_pass1 joined 2026-06-12 when the quarantined 04A edge's bill arrived
# as a confabulated lesson plan in Trial-3 cycle 2; irene joined at dp-v1.1
# when node 08's empty payload produced cycle-4's sepsis narration).
CONTRACTED_CONSUMERS: dict[str, frozenset[str]] = {
    "quinn_r": QUINN_R_KEYS,
    "gary": GARY_KEYS,
    "irene_pass1": IRENE_PASS1_KEYS,
    "irene": IRENE_KEYS,
    # Audio-arc (dp-v1.2, 2026-06-12): enrique + compositor joined when
    # nodes 12/14 gained projections (cycle-5 ungrounded-audio defect).
    "enrique": ENRIQUE_KEYS,
    "compositor": COMPOSITOR_KEYS,
    "vision": VISION_KEYS,
    # 07D.5 motion-plan producer (composition-catalog B2, 2026-06-26): the
    # deterministic producer reads the quinn_r winner deck under upstream_output;
    # kira's 07E edge was rewired from the tolerated quinn_r upstream_output to a
    # single motion_plan projection from the producer (amendment C, fail-closed).
    "motion_planner": MOTION_PLANNER_KEYS,
    "kira": KIRA_KEYS,
    # 07W in-graph companion-workbook producer (composition-catalog B3,
    # 2026-06-26): the terminal-sidecar producer reads the run's segment manifest
    # (irene Pass-2), lesson plan (irene-pass1), and corpus (texas bundle_reference)
    # via dependency_projections; it published CONSUMED_PAYLOAD_KEYS.
    "workbook_producer": WORKBOOK_PRODUCER_KEYS,
}

# Edges whose consumer has NOT yet published a contract. Raw manifest
# spellings, pinned exactly: adding a new edge to an uncontracted consumer
# (or silently dropping one of these) fails the test. Each row retires when
# its consumer publishes CONSUMED_PAYLOAD_KEYS (S2-S4 + later arcs).
QUARANTINED_EDGES: frozenset[tuple[str, str, str]] = frozenset(
    {
        # (node_id, input_key, declared specialist_id of the CONSUMING node)
        # ("04A","upstream_output","irene-pass1") RETIRED 2026-06-12:
        # irene_pass1 published CONSUMED_PAYLOAD_KEYS after the quarantined
        # edge produced cycle-2's confabulated lesson plan.
        ("4.75", "source_bundle", "cd"),
        ("7.5", "upstream_output", "vera"),
        # ("07E","upstream_output","kira") RETIRED 2026-06-26 (composition-catalog
        # B2): the tolerated quinn_r edge was REMOVED; 07E now consumes a single
        # motion_plan projection from the motion_planner producer (07D.5). kira
        # published CONSUMED_PAYLOAD_KEYS and joined CONTRACTED_CONSUMERS.
        # ("11","upstream_output","elevenlabs") RETIRED at dp-v1.2
        # (2026-06-12): the edge delivered kira's whole output dict to the
        # voice-selection leg, which reads none of it — edge deleted from
        # the manifest, enrique published CONSUMED_PAYLOAD_KEYS.
        ("14.5", "upstream_output", "desmond"),
    }
)


def _canonical(specialist_id: str) -> str:
    return SPECIALIST_ALIASES.get(specialist_id, specialist_id)


def _dependency_edges() -> list[tuple[str, str, str]]:
    """All data-plane edges: classic dependencies AND S4 key projections."""
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    edges: list[tuple[str, str, str]] = []
    for node in manifest["nodes"]:
        consumer = node.get("specialist_id")
        if not consumer:
            continue
        for input_key in node.get("dependencies") or {}:
            edges.append((str(node["id"]), str(input_key), str(consumer)))
        for input_key in node.get("dependency_projections") or {}:
            edges.append((str(node["id"]), str(input_key), str(consumer)))
    return edges


def test_contracted_edges_use_consumer_vocabulary() -> None:
    violations: list[str] = []
    for node_id, input_key, consumer in _dependency_edges():
        canonical = _canonical(consumer)
        keys = CONTRACTED_CONSUMERS.get(canonical)
        if keys is None:
            continue
        if input_key not in keys:
            violations.append(
                f"node {node_id}: input_key {input_key!r} is not in "
                f"{canonical}'s CONSUMED_PAYLOAD_KEYS"
            )
    assert violations == [], "\n".join(violations)


def test_uncontracted_edges_are_exactly_the_quarantine_list() -> None:
    uncontracted = {
        (node_id, input_key, consumer)
        for node_id, input_key, consumer in _dependency_edges()
        if _canonical(consumer) not in CONTRACTED_CONSUMERS
    }
    new_edges = uncontracted - QUARANTINED_EDGES
    retired = QUARANTINED_EDGES - uncontracted
    assert new_edges == set(), (
        "New dependency edge(s) to consumers without a published payload "
        f"contract: {sorted(new_edges)} — publish CONSUMED_PAYLOAD_KEYS for "
        "the consumer or add a deliberate quarantine entry."
    )
    assert retired == set(), (
        f"Quarantine entries no longer present in the manifest: {sorted(retired)} "
        "— remove them from QUARANTINED_EDGES."
    )


def test_every_cd_reachable_edge_delivers_a_source_bundle() -> None:
    """Amelia MUST-FIX (party review 2026-06-12): cd's act REQUIRES corpus
    access (read_extracted_source, no fallback). Production safety must be a
    suite property, not an eyeball property: every manifest node consuming
    as cd must declare an edge that delivers bundle access."""
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    bundle_keys = {"source_bundle", "bundle_reference", "upstream_output"}
    violations = []
    for node in manifest["nodes"]:
        if _canonical(str(node.get("specialist_id") or "")) != "cd":
            continue
        delivered = set(node.get("dependencies") or {}) | set(
            node.get("dependency_projections") or {}
        )
        if not (delivered & bundle_keys):
            violations.append(f"node {node['id']}: cd edge without bundle access")
    assert violations == [], violations


def test_alias_forms_resolve_to_canonical() -> None:
    # Canonical-vs-alias duality cost a live crash 2026-06-11 (quinn-r vs
    # quinn_r). Pin the resolution used by this test and the walkers.
    assert _canonical("quinn-r") == "quinn_r"
    assert _canonical("irene-pass1") == "irene_pass1"
    assert _canonical("elevenlabs") == "enrique"
    assert _canonical("texas") == "texas"
