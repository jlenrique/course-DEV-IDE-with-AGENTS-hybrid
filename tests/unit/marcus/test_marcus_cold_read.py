from __future__ import annotations

from pathlib import Path

import pytest

from marcus.facade import get_facade


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
                "edges:",
                '  - {from: __start__, to: "01"}',
            ]
        ),
        encoding="utf-8",
    )


def _write_sanctum(root: Path, *, persona: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "INDEX.md").write_text("# index\n", encoding="utf-8")
    (root / "PERSONA.md").write_text(persona, encoding="utf-8")
    (root / "CREED.md").write_text("# creed\n", encoding="utf-8")


def test_marcus_fingerprint_changes_when_sanctum_changes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    skill_path = tmp_path / "skills" / "bmad-agent-marcus" / "SKILL.md"
    sanctum_root = tmp_path / "_bmad" / "memory" / "bmad-agent-marcus"
    manifest_path = tmp_path / "state" / "config" / "pipeline-manifest.yaml"
    _write_skill(skill_path)
    _write_manifest(manifest_path)
    _write_sanctum(sanctum_root, persona="# persona a\n")
    (sanctum_root / "ignored").mkdir(exist_ok=True)
    (sanctum_root / "ignored" / "noise.md").write_text("ignored", encoding="utf-8")

    monkeypatch.setattr("marcus.facade._MARCUS_SKILL_PATH", skill_path)
    monkeypatch.setattr("marcus.facade._MARCUS_SANCTUM_ROOT", sanctum_root)
    monkeypatch.setattr("marcus.facade._PIPELINE_MANIFEST_PATH", manifest_path)

    facade_a = get_facade()
    _write_sanctum(sanctum_root, persona="# persona b\n")
    facade_b = get_facade()

    assert facade_a.sanctum_digest != facade_b.sanctum_digest
    assert facade_a.session_id != facade_b.session_id


def test_marcus_fingerprint_populated_on_init(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    skill_path = tmp_path / "skills" / "bmad-agent-marcus" / "SKILL.md"
    sanctum_root = tmp_path / "_bmad" / "memory" / "bmad-agent-marcus"
    manifest_path = tmp_path / "state" / "config" / "pipeline-manifest.yaml"
    _write_skill(skill_path)
    _write_manifest(manifest_path)
    _write_sanctum(sanctum_root, persona="# persona a\n")

    monkeypatch.setattr("marcus.facade._MARCUS_SKILL_PATH", skill_path)
    monkeypatch.setattr("marcus.facade._MARCUS_SANCTUM_ROOT", sanctum_root)
    monkeypatch.setattr("marcus.facade._PIPELINE_MANIFEST_PATH", manifest_path)

    facade = get_facade()

    assert len(facade.sanctum_digest) == 64
    assert facade.state is not None
    assert facade.state.marcus_fingerprint is not None
    assert facade.state.marcus_fingerprint[0] == facade.sanctum_digest


def test_no_singleton_short_circuit_across_calls(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    skill_path = tmp_path / "skills" / "bmad-agent-marcus" / "SKILL.md"
    sanctum_root = tmp_path / "_bmad" / "memory" / "bmad-agent-marcus"
    manifest_path = tmp_path / "state" / "config" / "pipeline-manifest.yaml"
    _write_skill(skill_path)
    _write_manifest(manifest_path)
    _write_sanctum(sanctum_root, persona="# persona a\n")

    monkeypatch.setattr("marcus.facade._MARCUS_SKILL_PATH", skill_path)
    monkeypatch.setattr("marcus.facade._MARCUS_SANCTUM_ROOT", sanctum_root)
    monkeypatch.setattr("marcus.facade._PIPELINE_MANIFEST_PATH", manifest_path)

    facade_a = get_facade()
    facade_b = get_facade()

    assert facade_a is not facade_b
    assert facade_a.session_id != facade_b.session_id
