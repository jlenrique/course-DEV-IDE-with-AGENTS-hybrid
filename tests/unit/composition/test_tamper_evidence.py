"""S2 RED floor (b) — TAMPER-EVIDENCE: replay RAISES (not warns).

Three tamper classes, all must RAISE on replay/verify:
  (i)   mutate persisted selection                       -> refuse
  (ii)  mutate a selected fragment's BYTES (no version   -> refuse  [content-addressing,
        bump)                                                       the non-negotiable]
  (iii) mutate composer_version / model_config           -> refuse
Plus: a record without the current digest_schema_version is NEVER silently compared.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from app.manifest import load
from app.manifest.lanes import DEFAULT_RUN_MANIFEST_PATH
from app.manifest.schema import EdgeSpec, NodeSpec, PipelineManifest
from app.marcus.lesson_plan.composition import (
    COMPOSER_VERSION,
    CompositionReplayError,
    compose_and_digest,
    verify_composition_replay,
)
from app.models.state.component_selection import ComponentSelection


def _live_manifest() -> PipelineManifest:
    return load(DEFAULT_RUN_MANIFEST_PATH)


def _mutate_node_bytes(manifest: PipelineManifest, node_id: str) -> PipelineManifest:
    """Return a copy where one node's BYTES changed but its component version did not."""
    new_nodes = []
    for node in manifest.nodes:
        if node.id == node_id:
            new_nodes.append(node.model_copy(update={"label": (node.label or "") + " TAMPERED"}))
        else:
            new_nodes.append(node)
    return manifest.model_copy(update={"nodes": new_nodes})


def test_replay_passes_when_nothing_tampered() -> None:
    m = _live_manifest()
    sel = ComponentSelection(deck=True, motion=True)
    record = compose_and_digest(sel, manifest=m)
    # No raise.
    verify_composition_replay(record, manifest=m)


def test_tamper_i_mutated_selection_refuses() -> None:
    m = _live_manifest()
    record = compose_and_digest(ComponentSelection(deck=True, motion=True), manifest=m)
    # Attacker flips motion off in the persisted record but keeps the digests.
    tampered = record.model_copy(
        update={"component_selection": {"deck": True, "motion": False, "workbook": False}}
    )
    with pytest.raises(CompositionReplayError):
        verify_composition_replay(tampered, manifest=m)


def test_tamper_ii_fragment_byte_mutation_without_version_bump_refuses() -> None:
    """THE non-negotiable: content-addressing, not label-hashing.

    A selected fragment's bytes change in the manifest while its component
    version label stays put -> replay MUST raise.
    """
    m = _live_manifest()
    record = compose_and_digest(ComponentSelection(deck=True, motion=True), manifest=m)
    mutated = _mutate_node_bytes(m, "07E")  # 07E is the kira motion node
    with pytest.raises(CompositionReplayError):
        verify_composition_replay(record, manifest=mutated)


def test_tamper_iii_composer_version_refuses() -> None:
    m = _live_manifest()
    # Record was produced under an older composer_version.
    record = compose_and_digest(
        ComponentSelection(deck=True, motion=True),
        manifest=m,
        composer_version=COMPOSER_VERSION + "-OLD",
    )
    with pytest.raises(CompositionReplayError):
        verify_composition_replay(record, manifest=m)  # verifies under live COMPOSER_VERSION


def test_digest_schema_version_guard_never_silently_compares_legacy() -> None:
    m = _live_manifest()
    record = compose_and_digest(ComponentSelection(deck=True, motion=True), manifest=m)
    legacy = record.model_copy(update={"digest_schema_version": "1.0"})
    with pytest.raises(CompositionReplayError):
        verify_composition_replay(legacy, manifest=m)


# --- model_config content-addressing (floor b-iii, second half) on a tmp repo ---


def _build_tmp_repo(tmp_path: Path) -> tuple[PipelineManifest, Path]:
    (tmp_path / "runtime" / "graphs" / "v42").mkdir(parents=True)
    cfg_dir = tmp_path / "configs"
    cfg_dir.mkdir()
    (cfg_dir / "model.yaml").write_text(
        yaml.safe_dump({"specialist_id": "x", "default_model": "m-1"}), encoding="utf-8"
    )
    manifest = PipelineManifest(
        schema_version="test",
        lane="run_graph",
        entrypoint="01",
        frozen_graph_version="v42",
        pack_version="v4.2",
        nodes=[
            NodeSpec(id="01", model_config_ref="configs/model.yaml", pack_version="v4.2"),
            NodeSpec(id="02", pack_version="v4.2"),
        ],
        edges=[
            EdgeSpec(**{"from": "__start__", "to": "01"}),
            EdgeSpec(**{"from": "01", "to": "02"}),
            EdgeSpec(**{"from": "02", "to": "__end__"}),
        ],
    )
    return manifest, tmp_path


def test_tamper_iii_model_config_bytes_refuses(tmp_path: Path) -> None:
    manifest, repo_root = _build_tmp_repo(tmp_path)
    sel = ComponentSelection(deck=True, motion=False)
    record = compose_and_digest(
        sel, manifest=manifest, repo_root=repo_root, dispatch_snapshot={}
    )
    # Mutate the referenced model_config file content (no ref change).
    (repo_root / "configs" / "model.yaml").write_text(
        yaml.safe_dump({"specialist_id": "x", "default_model": "m-2-TAMPERED"}),
        encoding="utf-8",
    )
    with pytest.raises(CompositionReplayError):
        verify_composition_replay(
            record, manifest=manifest, repo_root=repo_root, dispatch_snapshot={}
        )
