"""Regression checks for sprint-status YAML health."""

from __future__ import annotations

import re
from pathlib import Path

import yaml


def _contains_key(node: object, target: str) -> bool:
    if isinstance(node, dict):
        if target in node:
            return True
        return any(_contains_key(value, target) for value in node.values())
    if isinstance(node, list):
        return any(_contains_key(value, target) for value in node)
    return False


def _extract_story_status(path: Path) -> str:
    match = re.search(
        r"^\*\*Status:\*\*\s+([A-Za-z0-9-]+)\s*$",
        path.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    assert match, f"Missing status marker in {path}"
    return match.group(1)


def test_sprint_status_yaml_parses_and_contains_current_cluster_epic_keys() -> None:
    sprint_status = (
        Path(__file__).resolve().parents[1]
        / "_bmad-output"
        / "implementation-artifacts"
        / "sprint-status.yaml"
    )

    parsed = yaml.safe_load(sprint_status.read_text(encoding="utf-8"))

    assert isinstance(parsed, dict)
    assert _contains_key(parsed, "epic-20a")
    assert _contains_key(parsed, "20a-2-interstitial-brief-specification-standard")
    assert _contains_key(parsed, "20a-3-cluster-narrative-arc-schema")
    assert _contains_key(parsed, "20a-4-operator-cluster-density-controls")


def test_cluster_story_statuses_match_sprint_status() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    sprint_status = (
        repo_root
        / "_bmad-output"
        / "implementation-artifacts"
        / "sprint-status.yaml"
    )
    parsed = yaml.safe_load(sprint_status.read_text(encoding="utf-8"))
    development_status = parsed["development_status"]

    expected_statuses = {
        "19-2-gary-dispatch-contract-extensions": "done",
        "19-3-fidelity-gate-contract-updates": "done",
        "20a-2-interstitial-brief-specification-standard": "done",
        "20a-3-cluster-narrative-arc-schema": "done",
        "20a-4-operator-cluster-density-controls": "done",
        "20a-5-retrofit-exemplar-library": "ready-for-dev",
        "20b-1-irene-pass1-cluster-planning-implementation": "done",
    }
    story_paths = {
        "19-2-gary-dispatch-contract-extensions": repo_root
        / "_bmad-output"
        / "implementation-artifacts"
        / "19-2-gary-dispatch-contract-extensions.md",
        "19-3-fidelity-gate-contract-updates": repo_root
        / "_bmad-output"
        / "implementation-artifacts"
        / "19-3-fidelity-gate-contract-updates.md",
        "20a-2-interstitial-brief-specification-standard": repo_root
        / "_bmad-output"
        / "implementation-artifacts"
        / "20a-2-interstitial-brief-specification-standard.md",
        "20a-3-cluster-narrative-arc-schema": repo_root
        / "_bmad-output"
        / "implementation-artifacts"
        / "20a-3-cluster-narrative-arc-schema.md",
        "20a-4-operator-cluster-density-controls": repo_root
        / "_bmad-output"
        / "implementation-artifacts"
        / "20a-4-operator-cluster-density-controls.md",
        "20a-5-retrofit-exemplar-library": repo_root
        / "_bmad-output"
        / "implementation-artifacts"
        / "20a-5-retrofit-exemplar-library.md",
        "20b-1-irene-pass1-cluster-planning-implementation": repo_root
        / "_bmad-output"
        / "implementation-artifacts"
        / "20b-1-irene-pass1-cluster-planning-implementation.md",
    }

    for sprint_key, expected_status in expected_statuses.items():
        assert development_status[sprint_key] == expected_status
        assert _extract_story_status(story_paths[sprint_key]) == expected_status
