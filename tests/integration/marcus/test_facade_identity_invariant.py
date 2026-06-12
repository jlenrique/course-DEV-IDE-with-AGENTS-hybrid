from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.marcus.facade import get_facade


def _write_skill(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "---",
                "name: bmad-agent-marcus",
                "---",
                "",
                "## On Activation",
                "",
                "Rebirth -> Batch-load from sanctum: `INDEX.md`, `PERSONA.md`, `CREED.md`.",
            ]
        ),
        encoding="utf-8",
    )


def _write_manifest(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                'schema_version: "0.1-test"',
                'lane: "run_graph"',
                'entrypoint: "01"',
                'frozen_graph_version: "v-test"',
                "nodes:",
                '  - id: "01"',
                '    specialist_id: "alpha"',
                '  - id: "02"',
                '    specialist_id: "beta"',
                '  - id: "03"',
                '    specialist_id: "gamma"',
                "edges:",
                '  - {from: __start__, to: "01"}',
                '  - {from: "01", to: "02"}',
                '  - {from: "02", to: "03"}',
                '  - {from: "03", to: "01"}',
            ]
        ),
        encoding="utf-8",
    )


def _write_sanctum(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "INDEX.md").write_text("# index\n", encoding="utf-8")
    (root / "PERSONA.md").write_text("# persona\n", encoding="utf-8")
    (root / "CREED.md").write_text("# creed\n", encoding="utf-8")


@pytest.mark.parametrize("preset", ["production", "explore"])
def test_facade_identity_loop_keeps_one_marcus(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, preset: str
) -> None:
    skill_path = tmp_path / "skills" / "bmad-agent-marcus" / "SKILL.md"
    sanctum_root = tmp_path / "_bmad" / "memory" / "bmad-agent-marcus"
    manifest_path = tmp_path / "state" / "config" / "pipeline-manifest.yaml"
    _write_skill(skill_path)
    _write_manifest(manifest_path)
    _write_sanctum(sanctum_root)
    monkeypatch.setattr("app.marcus.facade._MARCUS_SKILL_PATH", skill_path)
    monkeypatch.setattr("app.marcus.facade._MARCUS_SANCTUM_ROOT", sanctum_root)
    monkeypatch.setattr("app.marcus.facade._PIPELINE_MANIFEST_PATH", manifest_path)

    state = SimpleNamespace(current_node=None, events=[])
    facade = get_facade()
    for _ in range(50):
        facade.run_step(state, preset=preset)

    assert len(state.events) == 50
    assert {event["actor"] for event in state.events} == {"Marcus"}


def test_ast_string_sweep_finds_no_operator_leak_tokens() -> None:
    forbidden_tokens = {"Marcus-Intake", "Marcus-Orchestrator"}
    # app/marcus/intake.py was deleted at Story 34-6 structural-orphan
    # cleanup; the sweep list must track live files only.
    paths = [
        Path("app/marcus/facade.py"),
        Path("app/marcus/orchestrator/supervisor.py"),
        Path("app/marcus/orchestrator/routing.py"),
    ]
    for path in paths:
        assert path.is_file(), f"sweep path missing — update the sweep list: {path}"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        string_constants = [
            node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        ]
        assert forbidden_tokens.isdisjoint(string_constants), path


def test_app_namespace_has_no_direct_internal_identity_names() -> None:
    source = Path("app/marcus").read_text if False else None
    del source
    for path in Path("app/marcus").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "intake_module" not in text
        assert "orchestrator_module" not in text
