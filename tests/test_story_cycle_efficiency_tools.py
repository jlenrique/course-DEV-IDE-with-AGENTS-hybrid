from __future__ import annotations

import shutil
from pathlib import Path

import scripts.utilities.capture_marcus_golden_trace as golden_trace
import scripts.utilities.instantiate_schema_story_scaffold as scaffold
import scripts.utilities.validate_marcus_golden_trace_fixture as golden_trace_validator


def _prepare_scaffold_repo(tmp_path: Path, monkeypatch) -> Path:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    scaffold_root = repo_root / "docs" / "dev-guide" / "scaffolds" / "schema-story"
    scaffold_root.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(scaffold.SCAFFOLD_ROOT, scaffold_root, dirs_exist_ok=True)

    monkeypatch.setattr(scaffold, "REPO_ROOT", repo_root)
    monkeypatch.setattr(scaffold, "SCAFFOLD_ROOT", scaffold_root)
    return repo_root


def test_instantiate_skip_story_spec_preserves_existing_preseed(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo_root = _prepare_scaffold_repo(tmp_path, monkeypatch)

    existing_preseed = (
        repo_root
        / "_bmad-output"
        / "specs"
        / "pre-seed-drafts"
        / "31-3-registries-PRE-SEED.md"
    )
    existing_preseed.parent.mkdir(parents=True, exist_ok=True)
    existing_preseed.write_text("pre-existing pre-seed", encoding="utf-8")

    exit_code = scaffold.main(
        [
            "--story-key",
            "31-3-registries",
            "--schema-name",
            "Registries",
            "--module-path",
            "marcus.lesson_plan.registries",
            "--points",
            "2",
            "--predecessors",
            "31-1",
            "--k-floor",
            "8",
            "--no-digest",
            "--skip-story-spec",
        ]
    )

    assert exit_code == 0
    assert existing_preseed.read_text(encoding="utf-8") == "pre-existing pre-seed"
    assert (repo_root / "app" / "marcus" / "lesson_plan" / "registries.py").exists()
    assert (repo_root / "tests" / "contracts" / "test_registries_shape_stable.py").exists()
    assert (
        repo_root / "tests" / "contracts" / "test_registries_json_schema_parity.py"
    ).exists()
    assert (
        repo_root
        / "tests"
        / "contracts"
        / "test_no_intake_orchestrator_leak_registries.py"
    ).exists()


def test_instantiate_collision_without_force_returns_nonzero(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo_root = _prepare_scaffold_repo(tmp_path, monkeypatch)

    collision = repo_root / "app" / "marcus" / "lesson_plan" / "registries.py"
    collision.parent.mkdir(parents=True, exist_ok=True)
    collision.write_text("occupied", encoding="utf-8")

    exit_code = scaffold.main(
        [
            "--story-key",
            "31-3-registries",
            "--schema-name",
            "Registries",
            "--module-path",
            "marcus.lesson_plan.registries",
            "--no-digest",
            "--skip-story-spec",
        ]
    )

    assert exit_code == 3
    assert collision.read_text(encoding="utf-8") == "occupied"


def test_instantiate_generates_dormant_contract_tests_and_clean_schema_stub(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo_root = _prepare_scaffold_repo(tmp_path, monkeypatch)

    exit_code = scaffold.main(
        [
            "--story-key",
            "31-3-registries",
            "--schema-name",
            "Registries",
            "--module-path",
            "marcus.lesson_plan.registries",
            "--no-digest",
            "--skip-story-spec",
        ]
    )

    assert exit_code == 0

    generated_schema = (
        repo_root / "app" / "marcus" / "lesson_plan" / "registries.py"
    ).read_text(encoding="utf-8").lower()
    assert "intake" not in generated_schema
    assert "orchestrator" not in generated_schema

    for relative_path in (
        repo_root / "tests" / "contracts" / "test_registries_shape_stable.py",
        repo_root / "tests" / "contracts" / "test_registries_json_schema_parity.py",
        repo_root
        / "tests"
        / "contracts"
        / "test_no_intake_orchestrator_leak_registries.py",
    ):
        generated_test = relative_path.read_text(encoding="utf-8")
        assert "pytest.mark.skip" in generated_test


def test_normalize_trace_replaces_locked_tokens_idempotently(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    payload = (
        "2026-04-18T12:34:56Z "
        "123e4567-e89b-42d3-a456-426614174000 "
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa "
        f"{repo_root}\\foo\\bar"
    )

    once = golden_trace.normalize_trace(payload, repo_root)
    twice = golden_trace.normalize_trace(once, repo_root)

    assert golden_trace.TIMESTAMP_TOKEN in once
    assert golden_trace.UUID4_TOKEN in once
    assert golden_trace.SHA256_TOKEN in once
    assert "{{REPO_ROOT}}" in once
    assert once == twice


def test_normalize_trace_does_not_touch_uuid3_or_short_hex(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    uuid3 = "123e4567-e89b-32d3-a456-426614174000"
    short_hex = "a" * 63

    assert golden_trace.normalize_trace(uuid3, repo_root) == uuid3
    assert golden_trace.normalize_trace(short_hex, repo_root) == short_hex


def test_validate_golden_trace_fixture_dir_passes_with_complete_bundle(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    fixture_dir = repo_root / "tests" / "fixtures" / "golden_trace" / "marcus_pre_30-1"
    fixture_dir.mkdir(parents=True)

    manifest_lines = [
        "captured_at: 2026-04-18T12:34:56+00:00",
        "source_path: tests/fixtures/trial_corpus/docx-tejal-case-study-2026-04-17.docx",
        "source_sha256: " + ("a" * 64),
        "repo_commit_sha: deadbeef",
        "module_versions:",
        "  python: 3.13.5",
        "  pydantic: 2.11.0",
        "capture_points:",
    ]
    for point in golden_trace.CAPTURE_POINTS:
        manifest_lines.extend(
            [
                f'  - step: "{point["step"]}"',
                f'    name: {point["name"]}',
                f'    filename: {point["filename"]}',
                f'    description: {point["description"]}',
            ]
        )
    (fixture_dir / "golden-trace-manifest.yaml").write_text(
        "\n".join(manifest_lines) + "\n",
        encoding="utf-8",
    )

    for point in golden_trace.CAPTURE_POINTS:
        (fixture_dir / point["filename"]).write_text(
            '{\n  "_internal_emitter": "marcus-intake",\n  "step": "'
            + point["step"]
            + '"\n}\n',
            encoding="utf-8",
        )

    issues = golden_trace_validator.validate_fixture_dir(fixture_dir, repo_root)
    assert issues == []


def test_validate_golden_trace_fixture_dir_flags_missing_files_and_paths(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    fixture_dir = repo_root / "tests" / "fixtures" / "golden_trace" / "marcus_pre_30-1"
    fixture_dir.mkdir(parents=True)

    (fixture_dir / "golden-trace-manifest.yaml").write_text(
        "captured_at: 2026-04-18T12:34:56+00:00\n"
        "source_path: tests/fixtures/trial_corpus/docx-tejal-case-study-2026-04-17.docx\n"
        "source_sha256: " + ("a" * 64) + "\n"
        "repo_commit_sha: deadbeef\n"
        "module_versions:\n"
        "  python: 3.13.5\n"
        "capture_points:\n"
        '  - step: "01"\n'
        "    name: ingestion\n"
        "    filename: step-01-ingestion-envelope.json\n"
        "    description: Ingestion envelope emitted after source intake.\n",
        encoding="utf-8",
    )
    (fixture_dir / "step-01-ingestion-envelope.json").write_text(
        '{\n  "_internal_emitter": "marcus-intake",\n'
        f'  "path": "{repo_root.as_posix()}/danger"\n'
        "}\n",
        encoding="utf-8",
    )

    issues = golden_trace_validator.validate_fixture_dir(fixture_dir, repo_root)
    assert any("capture_points length" in issue for issue in issues)
    assert any("absolute repo-root path" in issue for issue in issues)
    assert any("missing capture point file" in issue for issue in issues)


def test_capture_golden_trace_from_tracked_bundle_synthesis(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    source = repo_root / "course-content" / "courses" / "tejal-APC-C1" / "sample.pdf"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("real-ish source", encoding="utf-8")

    bundle_dir = (
        repo_root
        / "course-content"
        / "staging"
        / "tracked"
        / "source-bundles"
        / "sample-run"
    )
    bundle_dir.mkdir(parents=True, exist_ok=True)
    output_dir = repo_root / "tests" / "fixtures" / "golden_trace" / "marcus_pre_30-1"

    (bundle_dir / "run-constants.yaml").write_text(
        "requested_content_type: narrated-lesson-with-video-or-animation\n"
        "execution_mode: tracked/default\n"
        "quality_preset: production\n"
        "motion_enabled: true\n"
        "double_dispatch: false\n"
        "theme_selection: theme-a\n",
        encoding="utf-8",
    )
    (bundle_dir / "preflight-results.json").write_text(
        '{\n  "bundle_path": "C:/abs/repo/path",\n  "timestamp": "2026-04-18T12:34:56Z"\n}\n',
        encoding="utf-8",
    )
    (bundle_dir / "operator-directives.md").write_text(
        "# Operator Directives\nfocus: keep it\n",
        encoding="utf-8",
    )
    (bundle_dir / "metadata.json").write_text(
        '{\n  "source_authority_scope": {"primary": "part-1"}\n}\n',
        encoding="utf-8",
    )
    (bundle_dir / "ingestion-evidence.md").write_text(
        "# Ingestion Evidence\n- ok\n",
        encoding="utf-8",
    )
    (bundle_dir / "manifest.json").write_text(
        '{\n  "bundle_dir": "C:/abs/repo/path/bundle"\n}\n',
        encoding="utf-8",
    )
    (bundle_dir / "result.yaml").write_text(
        "status: complete\nartifacts:\n  - extracted.md\n",
        encoding="utf-8",
    )
    (bundle_dir / "ingestion-quality-gate-receipt.md").write_text(
        "# Gate Receipt\n- gate_decision: proceed\n",
        encoding="utf-8",
    )
    (bundle_dir / "irene-packet.md").write_text(
        "# Irene Packet\n- ready\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(golden_trace, "project_root", lambda: repo_root)

    exit_code = golden_trace.main(
        [
            "--source",
            str(source),
            "--bundle-dir",
            str(bundle_dir),
            "--output",
            str(output_dir),
        ]
    )

    assert exit_code == 0
    issues = golden_trace_validator.validate_fixture_dir(output_dir, repo_root)
    assert issues == []
    step_01 = (output_dir / "step-01-ingestion-envelope.json").read_text(encoding="utf-8")
    assert "{{TIMESTAMP}}" in step_01
    assert "{{REPO_ROOT}}" not in step_01 or "C:/abs/repo/path" not in step_01
