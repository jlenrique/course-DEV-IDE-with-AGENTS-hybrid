from __future__ import annotations

from pathlib import Path

BASELINE_ROOT = (
    Path("tests")
    / "fixtures"
    / "generator_validation"
    / "wanda_baseline"
    / "2026-04-25"
)


def test_wanda_validation_baseline_fixture_present() -> None:
    required = {
        "__init__.py",
        "graph.py",
        "state.py",
        "model_config.yaml",
        "expertise/README.md",
    }
    for rel_path in required:
        assert (BASELINE_ROOT / rel_path).is_file(), rel_path

    metadata = BASELINE_ROOT / "BASELINE_METADATA.md"
    assert metadata.is_file()
    text = metadata.read_text(encoding="utf-8")
    for key in (
        "generator_commit_sha",
        "wondercraft_skill_commit_sha",
        "emit_date",
        "operator",
        "purpose",
    ):
        assert f"- {key}:" in text
