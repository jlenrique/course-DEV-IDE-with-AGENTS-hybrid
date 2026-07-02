from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml

from scripts.utilities.fidelity_walk import build_report as legacy_build_report
from scripts.utilities.fidelity_walk import main as legacy_main
from scripts.utilities.file_helpers import project_root
from scripts.utilities.structural_walk import (
    AntiDriftSpec,
    AssetSpec,
    CrossCuttingSpec,
    LiveProbeSpec,
    _build_anti_drift_result,
    _status_for_asset,
    build_report,
    default_output_path,
    get_workflow_specs,
    load_workflow_spec,
    manifest_path,
    render_markdown,
)
from scripts.utilities.structural_walk import (
    main as structural_main,
)


def _valid_contract_yaml(gate: str) -> str:
    secondary = ""
    if gate == "G4":
        secondary = (
            "  schema_ref_secondary: "
            "skills/bmad-agent-content-creator/references/template-segment-manifest.md\n"
        )
    return (
        f"gate: {gate}\n"
        f"gate_name: {gate} Sample\n"
        "producing_agent: sample-agent\n"
        "source_of_truth:\n"
        "  primary: sample\n"
        "  schema_ref: skills/sample/template.md\n"
        f"{secondary}"
        "criteria:\n"
        "  - id: SAMPLE-01\n"
        "    name: Sample\n"
        "    description: Sample criterion\n"
        "    fidelity_class: [creative]\n"
        "    severity: critical\n"
        "    evaluation_type: deterministic\n"
        "    check: sample\n"
        "    requires_perception: false\n"
    )


def _write(root: Path, relative_path: str, content: str = "ok\n") -> None:
    target = root / Path(relative_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def _mkdir(root: Path, relative_path: str) -> None:
    (root / Path(relative_path)).mkdir(parents=True, exist_ok=True)


def _write_asset(root: Path, relative_path: str, *, gate: str | None = None) -> None:
    path = Path(relative_path)
    suffix = path.suffix.lower()
    if relative_path == "skills/bmad-agent-marcus/scripts/generate-production-plan.py":
        _write(
            root,
            relative_path,
            '"""stub"""\n'
            "def load_workflow_templates(workflow_template_path):\n"
            "    return {\n"
            '        "narrated-deck-video-export": {\n'
            '            "label": "Narrated Deck Video Export",\n'
            '            "aliases": [],\n'
            '            "stages": [\n'
            '                {"stage": "source-wrangling"},\n'
            '                {"stage": "lesson-plan-and-slide-brief"},\n'
            '                {"stage": "lesson-plan-coauthoring-04a"},\n'
            '                {"stage": "gate-1"},\n'
            '                {"stage": "slide-generation"},\n'
            '                {"stage": "storyboard"},\n'
            '                {"stage": "gate-2"},\n'
            '                {"stage": "narration-and-manifest"},\n'
            '                {"stage": "gate-3"},\n'
            '                {"stage": "audio-generation"},\n'
            '                {"stage": "composition-guide"},\n'
            '                {"stage": "gate-4"},\n'
            "            ],\n"
            "        },\n"
            '        "narrated-lesson-with-video-or-animation": {\n'
            '            "label": "Narrated Lesson With Video Or Animation",\n'
            '            "aliases": [],\n'
            '            "stages": [\n'
            '                {"stage": "source-wrangling"},\n'
            '                {"stage": "lesson-plan-and-slide-brief"},\n'
            '                {"stage": "lesson-plan-coauthoring-04a"},\n'
            '                {"stage": "creative-directive"},\n'
            '                {"stage": "fidelity-g1"},\n'
            '                {"stage": "fidelity-g2"},\n'
            '                {"stage": "quality-g2"},\n'
            '                {"stage": "gate-1"},\n'
            '                {"stage": "imagine-handoff"},\n'
            '                {"stage": "cluster-prompt-engineering"},\n'
            '                {"stage": "cluster-dispatch-sequencing"},\n'
            '                {"stage": "slide-generation"},\n'
            '                {"stage": "cluster-coherence"},\n'
            '                {"stage": "storyboard"},\n'
            '                {"stage": "fidelity-g3"},\n'
            '                {"stage": "quality-g3"},\n'
            '                {"stage": "gate-2"},\n'
            '                {"stage": "gate-2m"},\n'
            '                {"stage": "motion-generation"},\n'
            '                {"stage": "motion-gate"},\n'
            '                {"stage": "narration-and-manifest"},\n'
            '                {"stage": "fidelity-g4"},\n'
            '                {"stage": "quality-g4"},\n'
            '                {"stage": "gate-3"},\n'
            '                {"stage": "audio-generation"},\n'
            '                {"stage": "fidelity-g5"},\n'
            '                {"stage": "pre-composition-validation"},\n'
            '                {"stage": "composition-guide"},\n'
            '                {"stage": "post-composition-validation"},\n'
            '                {"stage": "gate-4"},\n'
            "            ],\n"
            "        },\n"
            '        "clustered-narrated-deck-video-export": {\n'
            '            "label": "Clustered Narrated Deck Video Export (Interstitial MVP)",\n'
            '            "aliases": ["cluster-presentation"],\n'
            '            "stages": [\n'
            '                {"stage": "source-wrangling"},\n'
            '                {"stage": "lesson-plan-and-slide-brief"},\n'
            '                {"stage": "lesson-plan-coauthoring-04a"},\n'
            '                {"stage": "fidelity-g1"},\n'
            '                {"stage": "cluster-plan"},\n'
            '                {"stage": "fidelity-g2"},\n'
            '                {"stage": "quality-g2"},\n'
            '                {"stage": "gate-1"},\n'
            '                {"stage": "imagine-handoff"},\n'
            '                {"stage": "slide-generation"},\n'
            '                {"stage": "cluster-coherence"},\n'
            '                {"stage": "storyboard"},\n'
            '                {"stage": "fidelity-g3"},\n'
            '                {"stage": "quality-g3"},\n'
            '                {"stage": "gate-2"},\n'
            '                {"stage": "narration-and-manifest"},\n'
            '                {"stage": "fidelity-g4"},\n'
            '                {"stage": "quality-g4"},\n'
            '                {"stage": "gate-3"},\n'
            '                {"stage": "audio-generation"},\n'
            '                {"stage": "fidelity-g5"},\n'
            '                {"stage": "pre-composition-validation"},\n'
            '                {"stage": "composition-guide"},\n'
            '                {"stage": "post-composition-validation"},\n'
            '                {"stage": "gate-4"},\n'
            "            ],\n"
            "        },\n"
            "    }\n"
            "\n"
            "def build_workflow_lookup(workflow_templates):\n"
            "    return {key: key for key in workflow_templates}\n"
            "\n"
            "def select_workflow_variant(content_type, motion_enabled=False):\n"
            '    if content_type == "narrated-lesson-with-video-or-animation" and '
            "not motion_enabled:\n"
            '        return "narrated-deck-video-export"\n'
            '    if content_type == "narrated-deck-video-export" and motion_enabled:\n'
            '        return "narrated-lesson-with-video-or-animation"\n'
            "    return content_type\n"
            "\n"
            "def resolve_workflow(content_type, workflow_templates, workflow_lookup):\n"
            "    template_id = workflow_lookup.get(content_type)\n"
            "    if template_id is None:\n"
            "        return None, None\n"
            "    return template_id, workflow_templates[template_id]\n",
        )
    elif relative_path == "skills/bmad-agent-marcus/references/workflow-templates.yaml":
        _write(
            root,
            relative_path,
            "workflow_templates:\n"
            "  narrated-deck-video-export:\n"
            '    label: "Narrated Deck Video Export"\n'
            "    aliases: []\n"
            "    stages:\n"
            "      - stage: source-wrangling\n"
            "      - stage: lesson-plan-and-slide-brief\n"
            "      - stage: lesson-plan-coauthoring-04a\n"
            "      - stage: gate-1\n"
            "      - stage: slide-generation\n"
            "      - stage: storyboard\n"
            "      - stage: gate-2\n"
            "      - stage: narration-and-manifest\n"
            "      - stage: gate-3\n"
            "      - stage: audio-generation\n"
            "      - stage: composition-guide\n"
            "      - stage: gate-4\n"
            "  narrated-lesson-with-video-or-animation:\n"
            '    label: "Narrated Lesson With Video Or Animation"\n'
            "    aliases: []\n"
            "    stages:\n"
            "      - stage: source-wrangling\n"
            "      - stage: lesson-plan-and-slide-brief\n"
            "      - stage: lesson-plan-coauthoring-04a\n"
            "      - stage: creative-directive\n"
            "      - stage: fidelity-g1\n"
            "      - stage: fidelity-g2\n"
            "      - stage: quality-g2\n"
            "      - stage: gate-1\n"
            "      - stage: imagine-handoff\n"
            "      - stage: cluster-prompt-engineering\n"
            "      - stage: cluster-dispatch-sequencing\n"
            "      - stage: slide-generation\n"
            "      - stage: cluster-coherence\n"
            "      - stage: storyboard\n"
            "      - stage: fidelity-g3\n"
            "      - stage: quality-g3\n"
            "      - stage: gate-2\n"
            "      - stage: gate-2m\n"
            "      - stage: motion-generation\n"
            "      - stage: motion-gate\n"
            "      - stage: narration-and-manifest\n"
            "      - stage: fidelity-g4\n"
            "      - stage: quality-g4\n"
            "      - stage: gate-3\n"
            "      - stage: audio-generation\n"
            "      - stage: fidelity-g5\n"
            "      - stage: pre-composition-validation\n"
            "      - stage: composition-guide\n"
            "      - stage: post-composition-validation\n"
            "      - stage: gate-4\n"
            "  clustered-narrated-deck-video-export:\n"
            '    label: "Clustered Narrated Deck Video Export (Interstitial MVP)"\n'
            "    aliases:\n"
            "      - cluster-presentation\n"
            "    stages:\n"
            "      - stage: source-wrangling\n"
            "      - stage: lesson-plan-and-slide-brief\n"
            "      - stage: lesson-plan-coauthoring-04a\n"
            "      - stage: fidelity-g1\n"
            "      - stage: cluster-plan\n"
            "      - stage: fidelity-g2\n"
            "      - stage: quality-g2\n"
            "      - stage: gate-1\n"
            "      - stage: imagine-handoff\n"
            "      - stage: slide-generation\n"
            "      - stage: cluster-coherence\n"
            "      - stage: storyboard\n"
            "      - stage: fidelity-g3\n"
            "      - stage: quality-g3\n"
            "      - stage: gate-2\n"
            "      - stage: narration-and-manifest\n"
            "      - stage: fidelity-g4\n"
            "      - stage: quality-g4\n"
            "      - stage: gate-3\n"
            "      - stage: audio-generation\n"
            "      - stage: fidelity-g5\n"
            "      - stage: pre-composition-validation\n"
            "      - stage: composition-guide\n"
            "      - stage: post-composition-validation\n"
            "      - stage: gate-4\n",
        )
    elif suffix == ".py":
        _write(root, relative_path, '"""stub"""\nVALUE = 1\n')
    elif suffix in {".yaml", ".yml"}:
        if "state/config/fidelity-contracts/g" in relative_path:
            _write(root, relative_path, _valid_contract_yaml(gate or "G0"))
        else:
            _write(root, relative_path, "key: value\n")
    elif suffix == ".json":
        _write(root, relative_path, '{"ok": true}\n')
    else:
        _write(root, relative_path, "ok\n")


def _create_minimal_repo(root: Path, workflow: str) -> None:
    _write(root, "pyproject.toml", "[project]\nname='structural-walk-test'\n")
    spec = get_workflow_specs()[workflow]
    _write(
        root,
        "skills/sensory-bridges/scripts/bridge_utils.py",
        '"""stub"""\ndef build_response(**kwargs):\n    return kwargs\n',
    )
    _write_workflow_manifests(root)

    for gate in spec.gate_specs:
        for asset in gate.assets:
            _write_asset(root, asset.path, gate=gate.gate)

    for cross_cutting in spec.cross_cutting_specs:
        path = Path(cross_cutting.path)
        if cross_cutting.redirect_contains is not None:
            _write(
                root,
                cross_cutting.path,
                "# Redirect\n\n"
                "**This sidecar is superseded.**\n\n"
                f"{cross_cutting.redirect_contains}\n",
            )
        elif path.suffix:
            _write_asset(root, cross_cutting.path)
        else:
            _mkdir(root, cross_cutting.path)

    anti_drift_docs: dict[str, list[str]] = {}
    for check in spec.anti_drift_specs:
        anti_drift_docs.setdefault(check.path, [])
        anti_drift_docs[check.path].extend(list(check.needles))
    for item in spec.sequence_doc_parity_specs:
        anti_drift_docs.setdefault(item.path, [])
        anti_drift_docs[item.path].append(item.needle)

    for path, needles in anti_drift_docs.items():
        deduped: list[str] = []
        for needle in needles:
            if needle not in deduped:
                deduped.append(needle)
        _write(root, path, "\n".join(deduped) + "\n")


def _write_workflow_manifests(root: Path) -> None:
    for workflow, spec in get_workflow_specs().items():
        payload = {
            "workflow": workflow,
            "title": spec.title,
            "walk_type": spec.walk_type,
            "cross_cutting": [
                {
                    "component": item.component,
                    "path": item.path,
                    **(
                        {"redirect_contains": item.redirect_contains}
                        if item.redirect_contains is not None
                        else {}
                    ),
                    **({"check_mode": item.check_mode} if item.check_mode != "auto" else {}),
                }
                for item in spec.cross_cutting_specs
            ],
            "anti_drift": [
                {
                    "name": item.name,
                    "path": item.path,
                    "needles": list(item.needles),
                    **({"ordered": True} if item.ordered else {}),
                }
                for item in spec.anti_drift_specs
            ],
            "sequence_doc_parity": [
                {
                    "stage": item.stage,
                    "path": item.path,
                    "needle": item.needle,
                }
                for item in spec.sequence_doc_parity_specs
            ],
        }
        if spec.dry_run_steps:
            payload["dry_run"] = {
                "steps": [
                    {
                        "key": item.key,
                        "label": item.label,
                        "scope": item.scope,
                        "input": item.input_ref,
                        "kind": item.kind,
                    }
                    for item in spec.dry_run_steps
                ]
            }
        _write(
            root,
            str(manifest_path(root, workflow).relative_to(root)),
            yaml.safe_dump(payload, sort_keys=False),
        )


def test_standard_workflow_happy_path_is_ready(tmp_path: Path) -> None:
    _create_minimal_repo(tmp_path, "standard")

    report = build_report(
        root=tmp_path,
        workflow="standard",
        generated_at=datetime(2026, 4, 5, 12, 0, 0, tzinfo=UTC),
    )
    markdown = render_markdown(report)

    assert report["workflow"] == "standard"
    assert report["summary"]["overall_status"] == "READY"
    assert report["summary"]["critical_findings"] == 0
    assert "Structural Walk Report" in markdown
    assert "state/config/fidelity-contracts/g5-audio.yaml" in markdown
    assert "state/config/fidelity-contracts/g6-composition.yaml" in markdown


def test_manifest_loader_reads_repo_manifest_contract(tmp_path: Path) -> None:
    _create_minimal_repo(tmp_path, "motion")

    spec = load_workflow_spec(tmp_path, "motion")

    assert spec.key == "motion"
    assert spec.title == "Motion-enabled narrated workflow"
    assert any(item.component == "Motion execution script" for item in spec.cross_cutting_specs)
    assert any(
        item.name == "Motion prompt-pack workflow sequence" for item in spec.anti_drift_specs
    )
    assert len(spec.dry_run_steps) == 3
    assert spec.dry_run_steps[0].kind == "manifest"
    assert spec.dry_run_steps[1].kind == "sequence"
    assert spec.dry_run_steps[2].kind == "sequence_docs"
    # 12 parity specs after v4.2 + 04A lockstep checks:
    # lesson-plan-coauthoring-04a (x2 — prompt-pack + operator-card), storyboard,
    # creative-directive, cluster-prompt-engineering, cluster-dispatch-sequencing,
    # cluster-coherence, gate-2m (x2 — prompt-pack + operator-card), motion-gate
    # (x2), narration-and-manifest.
    assert len(spec.sequence_doc_parity_specs) == 12


def test_manifest_loader_reads_cluster_manifest_contract(tmp_path: Path) -> None:
    _create_minimal_repo(tmp_path, "cluster")

    spec = load_workflow_spec(tmp_path, "cluster")

    assert spec.key == "cluster"
    assert spec.title == "Cluster-enabled narrated workflow"
    assert any(item.component == "Cluster template library" for item in spec.cross_cutting_specs)
    assert any(item.component == "Creative directive contract" for item in spec.cross_cutting_specs)
    assert len(spec.dry_run_steps) == 3
    assert spec.dry_run_steps[1].kind == "sequence"
    assert len(spec.sequence_doc_parity_specs) == 2


def test_manifest_loader_rejects_missing_title(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "state/config/structural-walk/standard.yaml",
        "workflow: standard\nwalk_type: Example\ncross_cutting: []\nanti_drift: []\n",
    )

    try:
        load_workflow_spec(tmp_path, "standard")
    except ValueError as exc:
        assert "missing non-empty title" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected manifest loader to reject missing title")


def test_manifest_loader_rejects_workflow_mismatch(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "state/config/structural-walk/standard.yaml",
        "workflow: motion\ntitle: Wrong\nwalk_type: Example\ncross_cutting: []\nanti_drift: []\n",
    )

    try:
        load_workflow_spec(tmp_path, "standard")
    except ValueError as exc:
        assert "workflow mismatch" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected manifest loader to reject workflow mismatch")


def test_manifest_loader_reads_standard_dry_run_steps(tmp_path: Path) -> None:
    _create_minimal_repo(tmp_path, "standard")

    spec = load_workflow_spec(tmp_path, "standard")

    assert len(spec.dry_run_steps) == 6
    assert spec.dry_run_steps[0].kind == "manifest"
    assert spec.dry_run_steps[2].kind == "sequence_docs"
    assert spec.dry_run_steps[-1].kind == "documents"
    assert len(spec.sequence_doc_parity_specs) == 6


def test_manifest_loader_rejects_empty_dry_run_steps(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "state/config/structural-walk/standard.yaml",
        "workflow: standard\n"
        "title: Standard\n"
        "walk_type: Example\n"
        "cross_cutting: []\n"
        "anti_drift: []\n"
        "dry_run:\n"
        "  steps: []\n",
    )

    try:
        load_workflow_spec(tmp_path, "standard")
    except ValueError as exc:
        assert "dry_run.steps must be a non-empty list" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected manifest loader to reject empty dry_run.steps")


def test_manifest_loader_rejects_unknown_dry_run_kind(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "state/config/structural-walk/standard.yaml",
        "workflow: standard\n"
        "title: Standard\n"
        "walk_type: Example\n"
        "cross_cutting: []\n"
        "anti_drift: []\n"
        "dry_run:\n"
        "  steps:\n"
        "    - key: sample\n"
        "      label: Sample\n"
        "      scope: Example\n"
        "      input: manifest\n"
        "      kind: unsupported\n",
    )

    try:
        load_workflow_spec(tmp_path, "standard")
    except ValueError as exc:
        assert "kind must be one of" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected manifest loader to reject unknown dry_run kind")


def test_motion_workflow_uses_motion_scope_and_output_dir(tmp_path: Path) -> None:
    _create_minimal_repo(tmp_path, "motion")

    report = build_report(root=tmp_path, workflow="motion")
    output_path = default_output_path(
        tmp_path,
        workflow="motion",
        generated_at=datetime(2026, 4, 5, 12, 30, 0, tzinfo=UTC),
    )

    assert report["workflow"] == "motion"
    assert report["summary"]["overall_status"] == "READY"
    assert any(
        component["component"] == "Motion execution script"
        and component["path"] == "skills/kling-video/scripts/kling_operations.py"
        for component in report["cross_cutting"]["components"]
    )
    assert output_path == (
        tmp_path
        / "reports"
        / "structural-walk"
        / "motion"
        / "structural-walk-motion-20260405-123000.md"
    )


def test_import_failure_is_reported_as_real_failure(tmp_path: Path) -> None:
    _create_minimal_repo(tmp_path, "standard")
    _write(
        tmp_path,
        "skills/gamma-api-mastery/scripts/gamma_operations.py",
        "def broken(:\n    pass\n",
    )

    report = build_report(root=tmp_path, workflow="standard")

    assert report["summary"]["overall_status"] == "NEEDS REMEDIATION"
    assert any(
        "Import failed: skills/gamma-api-mastery/scripts/gamma_operations.py" in item
        for item in report["summary"]["remediation_items"]
    )


def test_missing_asset_is_reported_as_missing(tmp_path: Path) -> None:
    _create_minimal_repo(tmp_path, "standard")

    status, findings = _status_for_asset(
        tmp_path,
        AssetSpec("Missing script", "skills/gamma-api-mastery/scripts/missing.py"),
    )

    assert status == "Missing"
    assert findings == ["Missing required asset: skills/gamma-api-mastery/scripts/missing.py"]


def test_invalid_contract_is_reported(tmp_path: Path) -> None:
    _create_minimal_repo(tmp_path, "standard")
    _write(tmp_path, "state/config/fidelity-contracts/g2-slide-brief.yaml", "gate: G2\n")

    report = build_report(root=tmp_path, workflow="standard")

    assert report["summary"]["overall_status"] == "NEEDS REMEDIATION"
    assert any(
        item.startswith("Invalid contract: state/config/fidelity-contracts/g2-slide-brief.yaml")
        for item in report["summary"]["remediation_items"]
    )


def test_yaml_parse_failure_is_reported(tmp_path: Path) -> None:
    broken = tmp_path / "broken.yaml"
    broken.write_text("key: [oops\n", encoding="utf-8")

    status, findings = _status_for_asset(
        tmp_path,
        AssetSpec("Broken YAML", "broken.yaml", check_mode="yaml"),
    )

    assert status == "Invalid YAML"
    assert len(findings) == 1
    assert findings[0].startswith("YAML parse failed: broken.yaml")


def test_json_parse_failure_is_reported(tmp_path: Path) -> None:
    broken = tmp_path / "broken.json"
    broken.write_text('{"oops": }\n', encoding="utf-8")

    status, findings = _status_for_asset(
        tmp_path,
        AssetSpec("Broken JSON", "broken.json", check_mode="json"),
    )

    assert status == "Invalid JSON"
    assert len(findings) == 1
    assert findings[0].startswith("JSON parse failed: broken.json")


def test_redirect_mismatch_is_reported(tmp_path: Path) -> None:
    _write(
        tmp_path, "_bmad/memory/master-orchestrator-sidecar/index.md", "# Redirect\nwrong target\n"
    )

    status, findings = _status_for_asset(
        tmp_path,
        CrossCuttingSpec(
            "Redirect placeholder",
            "_bmad/memory/master-orchestrator-sidecar/index.md",
            redirect_contains="Active sidecar: `_bmad/memory/marcus-sidecar/`",
        ),
    )

    assert status == "Invalid redirect"
    assert findings == [
        "Redirect placeholder missing canonical redirect text: "
        "_bmad/memory/master-orchestrator-sidecar/index.md"
    ]


def test_ordered_anti_drift_failure_is_reported(tmp_path: Path) -> None:
    _write(tmp_path, "docs/workflow/example.md", "SECOND\nFIRST\n")

    checks = _build_anti_drift_result(
        tmp_path,
        (
            AntiDriftSpec(
                "Ordered markers",
                "docs/workflow/example.md",
                ("FIRST", "SECOND"),
                ordered=True,
            ),
        ),
    )

    assert checks == [
        {
            "check": "Ordered markers",
            "status": "Fail",
            "evidence": "docs/workflow/example.md contains required markers out of order",
        }
    ]


def test_live_probe_failure_is_captured(tmp_path: Path) -> None:
    _create_minimal_repo(tmp_path, "standard")
    probe = LiveProbeSpec(
        name="synthetic-failure",
        command=(sys.executable, "-c", "raise SystemExit(3)"),
    )

    report = build_report(root=tmp_path, workflow="standard", live_probes=(probe,))

    assert report["summary"]["overall_status"] == "NEEDS REMEDIATION"
    assert any(
        item.startswith("Live probe failed: synthetic-failure")
        for item in report["summary"]["remediation_items"]
    )


def test_live_probes_are_opt_in_by_default(tmp_path: Path) -> None:
    _create_minimal_repo(tmp_path, "standard")

    report = build_report(root=tmp_path, workflow="standard")
    markdown = render_markdown(report)

    assert report["live_probes"] == []
    assert "## Live Probes" not in markdown


def test_standard_dry_run_preview_adds_plan_and_results(tmp_path: Path) -> None:
    _create_minimal_repo(tmp_path, "standard")

    report = build_report(root=tmp_path, workflow="standard", dry_run=True)
    markdown = render_markdown(report)

    assert report["dry_run"]["summary"] == {"planned": 6, "passed": 6, "blocked": 0}
    assert "## Dry Run Plan" in markdown
    assert "## Dry Run Results" in markdown
    assert "Manifest resolution and shape check" in markdown
    sequence_row = next(
        row
        for row in report["dry_run"]["results"]
        if row["step"] == "Marcus workflow sequence preview"
    )
    assert sequence_row["result"] == "Pass"
    assert "narrated-deck-video-export:" in sequence_row["evidence"]
    assert "source-wrangling -> lesson-plan-and-slide-brief" in sequence_row["evidence"]
    parity_row = next(
        row
        for row in report["dry_run"]["results"]
        if row["step"] == "Marcus sequence-to-document parity"
    )
    assert parity_row["result"] == "Pass"
    assert "Validated 6 sequence-doc checkpoint(s)" in parity_row["evidence"]


def test_standard_dry_run_blocks_on_contract_failure(tmp_path: Path) -> None:
    _create_minimal_repo(tmp_path, "standard")
    _write(tmp_path, "state/config/fidelity-contracts/g1-lesson-plan.yaml", "gate: G1\n")

    report = build_report(root=tmp_path, workflow="standard", dry_run=True)

    assert report["dry_run"]["summary"]["blocked"] >= 1
    contract_row = next(
        row
        for row in report["dry_run"]["results"]
        if row["step"] == "Local fidelity contract validation"
    )
    assert contract_row["result"] == "Blocked"
    assert contract_row["blocker"].startswith("Invalid contract:")
    aggregate_row = next(
        row
        for row in report["dry_run"]["results"]
        if row["step"] == "Local planner and document sanity"
    )
    assert aggregate_row["result"] == "Pass"
    assert aggregate_row["blocker"] == ""


def test_standard_dry_run_blocks_when_marcus_plan_resolution_fails(tmp_path: Path) -> None:
    _create_minimal_repo(tmp_path, "standard")
    (tmp_path / "skills" / "bmad-agent-marcus" / "scripts" / "generate-production-plan.py").unlink()

    report = build_report(root=tmp_path, workflow="standard", dry_run=True)

    sequence_row = next(
        row
        for row in report["dry_run"]["results"]
        if row["step"] == "Marcus workflow sequence preview"
    )
    assert sequence_row["result"] == "Blocked"
    assert sequence_row["blocker"].startswith("Marcus production-plan resolution failed:")
    assert "Missing required asset:" in sequence_row["blocker"]


def test_standard_dry_run_blocks_when_sequence_doc_parity_marker_is_missing(tmp_path: Path) -> None:
    _create_minimal_repo(tmp_path, "standard")
    prompt_pack = (
        tmp_path / "docs" / "workflow" / "production-prompt-pack-v4.1-narrated-deck-video-export.md"
    )
    prompt_pack.write_text("Required HIL review (Storyboard A):\n", encoding="utf-8")

    report = build_report(root=tmp_path, workflow="standard", dry_run=True)

    parity_row = next(
        row
        for row in report["dry_run"]["results"]
        if row["step"] == "Marcus sequence-to-document parity"
    )
    assert parity_row["result"] == "Blocked"
    assert parity_row["blocker"] == (
        "Sequence-doc parity marker missing for stage 'lesson-plan-coauthoring-04a': "
        "docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md"
    )


def test_dry_run_manifest_step_blocks_when_marcus_planning_assets_are_undeclared(
    tmp_path: Path,
) -> None:
    for workflow in ("standard", "motion"):
        case_root = tmp_path / workflow
        _create_minimal_repo(case_root, workflow)
        manifest_file = case_root / manifest_path(case_root, workflow).relative_to(case_root)
        payload = yaml.safe_load(manifest_file.read_text(encoding="utf-8"))
        payload["cross_cutting"] = [
            item
            for item in payload["cross_cutting"]
            if item["path"] != "skills/bmad-agent-marcus/references/workflow-templates.yaml"
        ]
        manifest_file.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

        report = build_report(root=case_root, workflow=workflow, dry_run=True)
        manifest_row = next(
            row
            for row in report["dry_run"]["results"]
            if row["step"] == "Manifest resolution and shape check"
        )
        assert manifest_row["result"] == "Blocked"
        assert manifest_row["blocker"] == (
            "Missing Marcus planning asset declaration: "
            "skills/bmad-agent-marcus/references/workflow-templates.yaml"
        )


def test_motion_dry_run_preview_adds_marcus_motion_sequence(tmp_path: Path) -> None:
    _create_minimal_repo(tmp_path, "motion")

    report = build_report(root=tmp_path, workflow="motion", dry_run=True)
    markdown = render_markdown(report)

    assert report["dry_run"]["summary"] == {"planned": 3, "passed": 3, "blocked": 0}
    assert "## Dry Run Plan" in markdown
    assert "## Dry Run Results" in markdown
    sequence_row = next(
        row
        for row in report["dry_run"]["results"]
        if row["step"] == "Marcus workflow sequence preview"
    )
    assert sequence_row["result"] == "Pass"
    assert "narrated-lesson-with-video-or-animation:" in sequence_row["evidence"]
    assert "gate-2m" in sequence_row["evidence"]
    assert "motion-generation" in sequence_row["evidence"]
    assert "motion-gate" in sequence_row["evidence"]
    parity_row = next(
        row
        for row in report["dry_run"]["results"]
        if row["step"] == "Marcus sequence-to-document parity"
    )
    assert parity_row["result"] == "Pass"
    # 12 parity checkpoints after v4.2 + 04A lockstep enhancements:
    # lesson-plan-coauthoring-04a (x2), storyboard, creative-directive,
    # cluster-prompt-engineering, cluster-dispatch-sequencing, cluster-coherence,
    # gate-2m (x2), motion-gate (x2), narration-and-manifest.
    assert "Validated 12 sequence-doc checkpoint(s)" in parity_row["evidence"]


def test_cluster_dry_run_preview_adds_cluster_sequence(tmp_path: Path) -> None:
    _create_minimal_repo(tmp_path, "cluster")

    report = build_report(root=tmp_path, workflow="cluster", dry_run=True)
    markdown = render_markdown(report)

    assert report["dry_run"]["summary"] == {"planned": 3, "passed": 3, "blocked": 0}
    assert "## Dry Run Plan" in markdown
    assert "## Dry Run Results" in markdown
    sequence_row = next(
        row
        for row in report["dry_run"]["results"]
        if row["step"] == "Marcus workflow sequence preview"
    )
    assert sequence_row["result"] == "Pass"
    assert "clustered-narrated-deck-video-export:" in sequence_row["evidence"]
    assert "cluster-plan" in sequence_row["evidence"]
    assert "cluster-coherence" in sequence_row["evidence"]
    parity_row = next(
        row
        for row in report["dry_run"]["results"]
        if row["step"] == "Marcus sequence-to-document parity"
    )
    assert parity_row["result"] == "Pass"
    assert "Validated 2 sequence-doc checkpoint(s)" in parity_row["evidence"]


def test_motion_dry_run_blocks_when_marcus_plan_resolution_fails(tmp_path: Path) -> None:
    _create_minimal_repo(tmp_path, "motion")
    (tmp_path / "skills" / "bmad-agent-marcus" / "references" / "workflow-templates.yaml").unlink()

    report = build_report(root=tmp_path, workflow="motion", dry_run=True)

    sequence_row = next(
        row
        for row in report["dry_run"]["results"]
        if row["step"] == "Marcus workflow sequence preview"
    )
    assert sequence_row["result"] == "Blocked"
    assert sequence_row["blocker"].startswith("Marcus production-plan resolution failed:")
    assert "Missing required asset:" in sequence_row["blocker"]


def test_motion_dry_run_blocks_when_sequence_doc_parity_marker_is_missing(tmp_path: Path) -> None:
    _create_minimal_repo(tmp_path, "motion")
    operator_card = tmp_path / "docs" / "workflow" / "production-operator-card-v4.md"
    operator_card.write_text(
        "Confirm Storyboard A artifacts and approval:\n"
        "### 7D. Prompt 7D: Gate 2M Motion Designation\n",
        encoding="utf-8",
    )

    report = build_report(root=tmp_path, workflow="motion", dry_run=True)

    parity_row = next(
        row
        for row in report["dry_run"]["results"]
        if row["step"] == "Marcus sequence-to-document parity"
    )
    assert parity_row["result"] == "Blocked"
    assert parity_row["blocker"] == (
        "Sequence-doc parity marker missing for stage 'lesson-plan-coauthoring-04a': "
        "docs/workflow/production-operator-card-v4.md"
    )


def test_cli_rejects_live_probe_in_dry_run_mode(tmp_path: Path, capsys) -> None:
    _create_minimal_repo(tmp_path, "standard")

    exit_code = structural_main(
        [
            "--root",
            str(tmp_path),
            "--workflow",
            "standard",
            "--dry-run",
            "--live-probe",
            "contracts-cli",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "--dry-run cannot be combined with --live-probe" in captured.err


def test_cli_accepts_motion_dry_run_cleanly(tmp_path: Path, capsys) -> None:
    _create_minimal_repo(tmp_path, "motion")

    exit_code = structural_main(["--root", str(tmp_path), "--workflow", "motion", "--dry-run"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Wrote structural walk report to" in captured.out
    assert "Workflow: motion | Overall status: READY" in captured.out


def test_cli_accepts_cluster_dry_run_cleanly(tmp_path: Path, capsys) -> None:
    _create_minimal_repo(tmp_path, "cluster")

    exit_code = structural_main(["--root", str(tmp_path), "--workflow", "cluster", "--dry-run"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Wrote structural walk report to" in captured.out
    assert "Workflow: cluster | Overall status: READY" in captured.out


def test_canonical_cli_default_path_omits_live_probes(tmp_path: Path) -> None:
    _create_minimal_repo(tmp_path, "standard")

    exit_code = structural_main(["--root", str(tmp_path), "--workflow", "standard"])
    report_path = next(
        (tmp_path / "reports" / "structural-walk" / "standard").glob(
            "structural-walk-standard-*.md"
        )
    )
    markdown = report_path.read_text(encoding="utf-8")

    assert exit_code == 0
    assert "## Live Probes" not in markdown


def test_dry_run_output_path_includes_suffix(tmp_path: Path) -> None:
    output_path = default_output_path(
        tmp_path,
        workflow="standard",
        generated_at=datetime(2026, 4, 5, 13, 0, 0, tzinfo=UTC),
        dry_run=True,
    )

    assert output_path == (
        tmp_path
        / "reports"
        / "structural-walk"
        / "standard"
        / "structural-walk-standard-dry-run-20260405-130000.md"
    )


def test_legacy_fidelity_walk_wrapper_routes_to_structural_walk(tmp_path: Path, capsys) -> None:
    _create_minimal_repo(tmp_path, "standard")

    exit_code = legacy_main(["--root", str(tmp_path)])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Legacy alias 'python -m scripts.utilities.fidelity_walk' invoked." in output
    assert "reports" in output
    assert any(
        candidate.name.startswith("structural-walk-standard-")
        for candidate in (tmp_path / "reports" / "structural-walk" / "standard").iterdir()
    )


def test_legacy_fidelity_walk_reexports_structural_helpers(tmp_path: Path) -> None:
    _create_minimal_repo(tmp_path, "standard")

    report = legacy_build_report(root=tmp_path, workflow="standard")

    assert report["workflow"] == "standard"
    assert report["summary"]["overall_status"] == "READY"


def test_historical_reports_are_migrated_out_of_tests() -> None:
    root = project_root()
    history_dir = root / "reports" / "structural-walk" / "standard" / "history"

    assert history_dir.exists()
    assert sorted(path.name for path in history_dir.glob("fidelity-walk-*.md")) == [
        "fidelity-walk-20260403-110000.md",
        "fidelity-walk-20260403-111500.md",
        "fidelity-walk-20260403-153321.md",
        "fidelity-walk-20260403-201006.md",
        "fidelity-walk-20260405-222432.md",
    ]
    assert list((root / "tests").glob("fidelity-walk-*.md")) == []


def test_real_repo_standard_workflow_smoke_has_no_default_live_probes() -> None:
    root = project_root()

    report = build_report(root=root, workflow="standard")

    assert report["summary"]["overall_status"]
