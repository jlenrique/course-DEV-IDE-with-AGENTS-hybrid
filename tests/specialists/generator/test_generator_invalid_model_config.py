from __future__ import annotations

from pathlib import Path

import pytest

from app.manifest.compiler import compile
from app.manifest.exceptions import CompileError
from app.manifest.schema import NodeSpec, PipelineManifest


def test_compile_raises_on_unknown_model_id_in_model_config_ref(tmp_path: Path) -> None:
    repo_root = Path(".").resolve()
    config_rel = Path("tests") / "fixtures" / "specialists" / "_tmp_invalid_model_config.yaml"
    config_abs = repo_root / config_rel
    config_abs.parent.mkdir(parents=True, exist_ok=True)
    config_abs.write_text(
        "\n".join(
            [
                "specialist_id: \"toytest\"",
                "default_model: \"gpt-4.9-imaginary\"",
                "per_node_overrides: {}",
                "temperature_default: 0.0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    manifest = PipelineManifest(
        schema_version="1.0",
        lane="run_graph",
        entrypoint="toytest_step",
        frozen_graph_version="v0.1-stub",
        nodes=[
            NodeSpec(
                id="toytest_step",
                specialist_id="toytest",
                model_config_ref=str(config_rel).replace("\\", "/"),
            )
        ],
        edges=[],
    )

    try:
        with pytest.raises(CompileError, match="toytest"):
            compile(manifest, repo_root=repo_root)
    finally:
        if config_abs.exists():
            config_abs.unlink()
