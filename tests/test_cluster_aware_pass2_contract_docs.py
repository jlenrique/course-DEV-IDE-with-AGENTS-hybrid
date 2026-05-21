"""Contract checks for Story 23.1 cluster-aware Irene Pass 2 guidance."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_irene_skill_documents_cluster_aware_pass2_rules() -> None:
    # Epic 26 Story 26-2 migration: cluster-aware Pass 2 rules moved from SKILL.md
    # to the dedicated pass-2-procedure.md reference.
    content = (
        ROOT
        / "skills"
        / "bmad-agent-content-creator"
        / "references"
        / "pass-2-procedure.md"
    ).read_text(encoding="utf-8")

    assert "process them cluster-by-cluster in manifest order" in content
    assert "must not introduce new concepts outside the head segment's instructional scope" in content
    assert "master_behavioral_intent" in content
    assert "bridge_type: pivot" in content
    assert "bridge_type: cluster_boundary" in content


def test_narration_template_exposes_cluster_role_and_new_bridge_types() -> None:
    content = (
        ROOT
        / "skills"
        / "bmad-agent-content-creator"
        / "references"
        / "template-narration-script.md"
    ).read_text(encoding="utf-8")

    assert "Cluster Role: {none | head | interstitial}" in content
    assert "Cluster Position: {none | establish | develop | tension | resolve}" in content
    assert "Bridge Type: {none | intro | outro | both | pivot | cluster_boundary}" in content
    assert "Do not introduce new concepts in an interstitial" in content


def test_segment_manifest_contract_requires_behavioral_intent_subordination() -> None:
    content = (
        ROOT
        / "skills"
        / "bmad-agent-content-creator"
        / "references"
        / "template-segment-manifest.md"
    ).read_text(encoding="utf-8")

    assert "`behavioral_intent` must serve `master_behavioral_intent`" in content
    assert "must not contradict the cluster's affective direction" in content


def test_operator_ab_loop_uses_cluster_aware_pass2_mode() -> None:
    content = (
        ROOT / "docs" / "workflow" / "operator-script-v4.2-irene-ab-loop.md"
    ).read_text(encoding="utf-8")

    assert "cluster-aware-refinement" in content
    assert "structural-coherence-check" not in content


def test_parameter_directory_and_registry_include_pivot_bridge_type() -> None:
    directory = (ROOT / "docs" / "parameter-directory.md").read_text(encoding="utf-8")
    registry = (
        ROOT / "state" / "config" / "parameter-registry-schema.yaml"
    ).read_text(encoding="utf-8")

    assert "`none`, `intro`, `outro`, `both`, `pivot`, `cluster_boundary`" in directory
    assert "- pivot" in registry
