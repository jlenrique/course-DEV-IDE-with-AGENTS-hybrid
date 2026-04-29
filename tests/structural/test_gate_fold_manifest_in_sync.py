from __future__ import annotations

from app.manifest.gate_fold_manifest_emit import (
    DEFAULT_MANIFEST_PATH,
    DEFAULT_OUTPUT_PATH,
    emit_gate_fold_manifest,
)


def test_gate_fold_manifest_is_in_sync(tmp_path) -> None:
    candidate = tmp_path / "gate_fold_manifest.yaml"

    emit_gate_fold_manifest(DEFAULT_MANIFEST_PATH, candidate)

    assert candidate.read_bytes() == DEFAULT_OUTPUT_PATH.read_bytes()
