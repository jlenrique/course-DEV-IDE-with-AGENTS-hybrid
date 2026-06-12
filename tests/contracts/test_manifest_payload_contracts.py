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
from app.specialists.gary._act import CONSUMED_PAYLOAD_KEYS as GARY_KEYS
from app.specialists.quinn_r._act import CONSUMED_PAYLOAD_KEYS as QUINN_R_KEYS

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "state" / "config" / "pipeline-manifest.yaml"

# Consumers with published payload contracts (S1 roster: quinn_r + gary;
# expand per-story as each specialist's data plane becomes real).
CONTRACTED_CONSUMERS: dict[str, frozenset[str]] = {
    "quinn_r": QUINN_R_KEYS,
    "gary": GARY_KEYS,
}

# Edges whose consumer has NOT yet published a contract. Raw manifest
# spellings, pinned exactly: adding a new edge to an uncontracted consumer
# (or silently dropping one of these) fails the test. Each row retires when
# its consumer publishes CONSUMED_PAYLOAD_KEYS (S2-S4 + later arcs).
QUARANTINED_EDGES: frozenset[tuple[str, str, str]] = frozenset(
    {
        # (node_id, input_key, declared specialist_id of the CONSUMING node)
        ("04A", "upstream_output", "irene-pass1"),
        ("4.75", "source_bundle", "cd"),
        ("7.5", "upstream_output", "vera"),
        ("07E", "upstream_output", "kira"),
        ("11", "upstream_output", "elevenlabs"),
        ("14.5", "upstream_output", "desmond"),
    }
)


def _canonical(specialist_id: str) -> str:
    return SPECIALIST_ALIASES.get(specialist_id, specialist_id)


def _dependency_edges() -> list[tuple[str, str, str]]:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    edges: list[tuple[str, str, str]] = []
    for node in manifest["nodes"]:
        consumer = node.get("specialist_id")
        dependencies = node.get("dependencies") or {}
        if not consumer or not dependencies:
            continue
        for input_key in dependencies:
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


def test_alias_forms_resolve_to_canonical() -> None:
    # Canonical-vs-alias duality cost a live crash 2026-06-11 (quinn-r vs
    # quinn_r). Pin the resolution used by this test and the walkers.
    assert _canonical("quinn-r") == "quinn_r"
    assert _canonical("irene-pass1") == "irene_pass1"
    assert _canonical("elevenlabs") == "enrique"
    assert _canonical("texas") == "texas"
