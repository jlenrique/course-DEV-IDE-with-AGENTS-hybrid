"""Contract for pipeline-manifest top-level key uniqueness."""

from __future__ import annotations

from pathlib import Path

import yaml


# Files that are, by design, a SECOND manifest and therefore legitimately
# share manifest-shaped keys. pipeline-manifest-substrate-stub.yaml is the
# Slab-1 Story 1.6 single-node smoke stub (eb2adb01); its header
# self-identifies as the deliberate stub for app.smoke_test.run_smoke() and
# the 1.1d transport-parity tests, and every consumer references it by
# explicit filename. Exempting the deliberate second manifest preserves the
# contract's intent: no ACCIDENTAL shadowing of manifest SSOT keys.
# See contracts-triage-ledger-2026-07-02 row 13.
_DELIBERATE_SECOND_MANIFESTS = {"pipeline-manifest-substrate-stub.yaml"}

# Narrow per-file, per-key allowances for governed shape overlaps.
# capability-overlay.yaml carries a `generator_ref` provenance key naming its
# generator script; the key is explicitly specified in the ratified overlay
# shape (spec-braid-s4-marcus-capability-overlay.md line 60; landed cce6df19).
# All other files/keys keep full teeth.
_ALLOWED_FILE_KEY_OVERLAPS: dict[str, set[str]] = {
    "capability-overlay.yaml": {"generator_ref"},
}


def _collect_collisions(state_config: Path) -> dict[str, list[str]]:
    manifest_path = state_config / "pipeline-manifest.yaml"
    manifest_data = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    manifest_keys = set(manifest_data.keys())

    allowed_shared = {"schema_version"}
    collisions: dict[str, list[str]] = {}
    for candidate in state_config.glob("*.yaml"):
        if candidate.name == "pipeline-manifest.yaml":
            continue
        if candidate.name in _DELIBERATE_SECOND_MANIFESTS:
            continue
        other_data = yaml.safe_load(candidate.read_text(encoding="utf-8")) or {}
        if not isinstance(other_data, dict):
            continue
        shared = (
            manifest_keys.intersection(other_data.keys())
            - allowed_shared
            - _ALLOWED_FILE_KEY_OVERLAPS.get(candidate.name, set())
        )
        if shared:
            collisions[candidate.name] = sorted(shared)
    return collisions


def test_pipeline_manifest_keys_do_not_shadow_other_state_configs() -> None:
    state_config = Path(__file__).resolve().parents[2] / "state" / "config"
    collisions = _collect_collisions(state_config)
    assert not collisions, f"pipeline-manifest top-level key collisions: {collisions}"


def test_disjoint_keys_detector_flags_synthesized_collision(tmp_path: Path) -> None:
    (tmp_path / "pipeline-manifest.yaml").write_text(
        "schema_version: '1.0'\npack_version: 'v4.2'\nsteps: []\n",
        encoding="utf-8",
    )
    (tmp_path / "other.yaml").write_text(
        "pack_version: 'shadow'\n",
        encoding="utf-8",
    )
    collisions = _collect_collisions(tmp_path)
    assert collisions == {"other.yaml": ["pack_version"]}

