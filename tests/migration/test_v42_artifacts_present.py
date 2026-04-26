from __future__ import annotations

from pathlib import Path

V42_DIR = Path(__file__).resolve().parents[2] / "runtime" / "graphs" / "v42"


def test_v42_artifacts_present_and_non_empty() -> None:
    expected = (
        "README.md",
        "manifest-snapshot.yaml",
        "dev-graph-manifest-snapshot.yaml",
        "dispatch-registry-snapshot.yaml",
        "pack-version.txt",
        "compiled-graph-digest.txt",
    )

    for name in expected:
        path = V42_DIR / name
        assert path.is_file(), f"missing v42 artifact: {name}"
        assert path.read_text(encoding="utf-8").strip(), f"empty v42 artifact: {name}"


def test_pack_version_text_format() -> None:
    value = (V42_DIR / "pack-version.txt").read_text(encoding="utf-8").strip()

    assert value == "v4.2"
