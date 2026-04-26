from __future__ import annotations

from pathlib import Path

from app.runtime.compiled_graph_digest import compute_compiled_graph_digest

V42_DIR = Path(__file__).resolve().parents[2] / "runtime" / "graphs" / "v42"


def test_compiled_graph_digest_is_stable_for_same_inputs() -> None:
    first = compute_compiled_graph_digest(
        V42_DIR / "manifest-snapshot.yaml",
        dispatch_registry_snapshot=V42_DIR / "dispatch-registry-snapshot.yaml",
    )
    second = compute_compiled_graph_digest(
        V42_DIR / "manifest-snapshot.yaml",
        dispatch_registry_snapshot=V42_DIR / "dispatch-registry-snapshot.yaml",
    )

    assert first == second
    assert len(first) == 64


def test_compiled_graph_digest_changes_when_pack_version_changes() -> None:
    baseline = compute_compiled_graph_digest(
        V42_DIR / "manifest-snapshot.yaml",
        dispatch_registry_snapshot=V42_DIR / "dispatch-registry-snapshot.yaml",
    )
    changed = compute_compiled_graph_digest(
        V42_DIR / "manifest-snapshot.yaml",
        pack_version="v4.2.1",
        dispatch_registry_snapshot=V42_DIR / "dispatch-registry-snapshot.yaml",
    )

    assert baseline != changed
