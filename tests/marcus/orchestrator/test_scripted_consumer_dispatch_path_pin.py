"""Leg-C AC#14 (M-3/J-4, non-waivable) + D-2 — production-dispatch-path pin.

The D1 adjudication root cause: the floor honoring lived in a module PRODUCTION
NEVER DISPATCHES (``app.specialists.irene.graph::_act_pass_1`` behind a
``pass_phase`` no manifest/runner ever sets), while nodes 04A/05/05B dispatch
the SEPARATE ``app.specialists.irene_pass1`` module. These tests pin the whole
resolution chain so a registered scripted class whose consumer is not reachable
from the production dispatch graph FAILS CI (D-2):

manifest ``specialist_id`` (``irene-pass1`` at nodes 04A/05/05B — the ONLY
specialist the runner threads the scripted floor to, see
``production_runner._runner_payload_for_specialist``'s ``irene-pass1`` branch,
``app/marcus/orchestrator/production_runner.py:1488``)
  -> canonical id via ``SPECIALIST_ALIASES`` (``app/manifest/compiler.py:42-46``:
     ``"irene-pass1" -> "irene_pass1"``; the walker passes the canonical id)
  -> dispatch registry ``state/config/dispatch-registry.yaml``
     (``irene_pass1: app.specialists.irene_pass1.graph:build_irene_pass1_graph``,
     loaded by ``ProductionDispatchAdapter._load_graph_builders``,
     ``app/marcus/orchestrator/dispatch_adapter.py:230-238``)
  -> the resolved module must import/bind the floor consumer
     (``app.specialists.irene_pass1.cluster_floor.consume_min_cluster_floor``).
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest
import yaml

from app.manifest.compiler import SPECIALIST_ALIASES, _canonical_specialist_id

REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = REPO_ROOT / "state" / "config" / "pipeline-manifest.yaml"
DISPATCH_REGISTRY_PATH = REPO_ROOT / "state" / "config" / "dispatch-registry.yaml"

# The manifest spelling of the specialist the runner's scripted-floor threading
# targets (the ``if specialist_id == "irene-pass1"`` branch at
# production_runner.py:1488).
FLOOR_RECEIVING_SPECIALIST_ID = "irene-pass1"

# D-2 consumer registry: every registered scripted class names the module that
# consumes it at the real dispatched surface. Grows in lockstep with
# SCRIPTED_ENUM_CLASSES (asserted below).
SCRIPTED_CONSUMER_MODULES = {
    "min_cluster_floor": "app.specialists.irene_pass1.cluster_floor",
}


def _floor_receiving_nodes() -> list[dict]:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    return [
        node
        for node in manifest["nodes"]
        if node.get("specialist_id") == FLOOR_RECEIVING_SPECIALIST_ID
    ]


def _registry_builder_ref(canonical_id: str) -> str:
    registry = yaml.safe_load(DISPATCH_REGISTRY_PATH.read_text(encoding="utf-8"))
    return str(registry["specialists"][canonical_id])


def test_manifest_floor_receiving_nodes_are_the_pass1_trio() -> None:
    """The scripted floor's receiving nodes exist and are exactly 04A/05/05B."""
    nodes = _floor_receiving_nodes()
    assert {node["id"] for node in nodes} == {"04A", "05", "05B"}, (
        "the runner threads the scripted floor to specialist_id "
        f"{FLOOR_RECEIVING_SPECIALIST_ID!r}; expected manifest nodes 04A/05/05B, "
        f"got {[node['id'] for node in nodes]!r}"
    )


def test_dispatch_path_resolves_to_irene_pass1_module() -> None:
    """manifest specialist_id -> canonical alias -> registry -> real module."""
    canonical = _canonical_specialist_id(FLOOR_RECEIVING_SPECIALIST_ID)
    assert canonical == "irene_pass1"
    assert SPECIALIST_ALIASES[FLOOR_RECEIVING_SPECIALIST_ID] == canonical
    builder_ref = _registry_builder_ref(canonical)
    assert builder_ref == "app.specialists.irene_pass1.graph:build_irene_pass1_graph"
    module_name, function_name = builder_ref.split(":", 1)
    module = importlib.import_module(module_name)
    assert callable(getattr(module, function_name))


def test_floor_consumer_reachable_from_production_dispatch_module() -> None:
    """AC#14 pin + D-2 import-reachability (RED pre-port; xfail flipped at port).

    Importing the registry-resolved dispatch module must pull the scripted
    class's consumer into the import graph, and the act module the graph
    dispatches must bind the consuming function. A registered scripted class
    whose consumer is NOT reachable from the resolved dispatch module = FAIL
    (the exact fully-closed-loop-of-tautology the D1 adjudication found).
    """
    canonical = _canonical_specialist_id(FLOOR_RECEIVING_SPECIALIST_ID)
    builder_ref = _registry_builder_ref(canonical)
    dispatch_module_name = builder_ref.split(":", 1)[0]

    from app.specialists.gary.styleguide_library import SCRIPTED_ENUM_CLASSES

    # Every registered scripted class must have a declared consumer module.
    assert set(SCRIPTED_CONSUMER_MODULES) == set(SCRIPTED_ENUM_CLASSES), (
        "SCRIPTED_CONSUMER_MODULES must track the sealed scripted registry "
        "1:1 — a registered class with no declared consumer is dead config"
    )

    dispatch_module = importlib.import_module(dispatch_module_name)
    assert dispatch_module is not None

    for scripted_class, consumer_module_name in SCRIPTED_CONSUMER_MODULES.items():
        # (a) importing the DISPATCH module must have made the consumer module
        # import-reachable (it is in sys.modules without a direct import here).
        assert consumer_module_name in sys.modules, (
            f"scripted class {scripted_class!r}: consumer module "
            f"{consumer_module_name!r} is not reachable from the production "
            f"dispatch module {dispatch_module_name!r} (D-2 dead-consumer)"
        )
        consumer_module = sys.modules[consumer_module_name]
        assert callable(consumer_module.consume_min_cluster_floor)
        assert callable(consumer_module.assert_floor_consulted)

    # (b) the act module the dispatched graph invokes binds the consumer, so the
    # consumption seam sits ON the dispatched path, not beside it.
    act_module = importlib.import_module("app.specialists.irene_pass1._act")
    assert (
        act_module.consume_min_cluster_floor
        is sys.modules["app.specialists.irene_pass1.cluster_floor"].consume_min_cluster_floor
    )


def test_floor_threading_branch_accepts_canonical_specialist_id(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC#14 gap closure (live-diagnosed F1, 2026-07-01).

    The original pin proved module REACHABILITY along the dispatch chain but never
    exercised the PAYLOAD BRANCH with the id form the walk actually passes: the
    compiler stamps ``handler.__production_specialist_id__ =
    _canonical_specialist_id(node.specialist_id)`` (``app/manifest/compiler.py:163``),
    both walks read that attribute (``production_runner.py:2550``/``:3276``) and
    thread it to ``_runner_payload_for_specialist`` (``:1978``) — so the branch sees
    ``"irene_pass1"`` (underscore), never the manifest spelling. A live instrumented
    walk proved the hyphen-only branch returned None on every real dispatch. This
    test pins that the CANONICAL id (derived here from the same alias table, so an
    alias-table change re-fails loudly) actually threads the floor.
    """
    from app.marcus.orchestrator import production_runner

    canonical = _canonical_specialist_id(FLOOR_RECEIVING_SPECIALIST_ID)
    assert canonical is not None
    ssot = tmp_path / "gamma-style-guides.yaml"
    ssot.write_text(
        yaml.safe_dump(
            {
                "style_guides": {
                    "pinned": {
                        "production_mode": "api",
                        "scripted": [
                            {
                                "class": "min_cluster_floor",
                                "value": 4,
                                "rationale": "AC#14 payload-branch pin",
                                "provenance": {
                                    "authoring_styleguide": "x",
                                    "envelope_write_stamp": "z",
                                },
                            }
                        ],
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(production_runner, "GAMMA_STYLE_GUIDES_SSOT_PATH", ssot)
    directive = tmp_path / "directive.yaml"
    directive.write_text(
        yaml.safe_dump({"gamma_settings": [{"variant_id": "A", "styleguide": "pinned"}]}),
        encoding="utf-8",
    )

    payload = production_runner._runner_payload_for_specialist(
        specialist_id=canonical, directive_path=directive, bundle_dir=None
    )
    assert payload == {"min_cluster_floor": 4}, (
        "the floor-threading branch must accept the CANONICALIZED specialist id "
        f"{canonical!r} — the id form the walk passes at the dispatch call site"
    )
