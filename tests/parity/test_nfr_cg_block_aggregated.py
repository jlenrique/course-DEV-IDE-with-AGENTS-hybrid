"""Aggregated NFR-CG1..NFR-CG11 structural closeout checks."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = REPO_ROOT / "_bmad-output" / "implementation-artifacts"
PLANNING = REPO_ROOT / "_bmad-output" / "planning-artifacts"
GOVERNANCE_JSON = REPO_ROOT / "docs" / "dev-guide" / "migration-story-governance.json"
DEFERRED_INVENTORY = PLANNING / "deferred-inventory.md"

SLAB_7A_STORIES = [
    ARTIFACTS / "migration-7a-1-directive-composer.md",
    ARTIFACTS / "migration-7a-2-manifest-fold-flags-compiler-extension.md",
    ARTIFACTS / "migration-7a-3-pre-gate-marcus-shared-llm-node.md",
    ARTIFACTS / "migration-7a-4-per-slide-subgraph-html-review-pack-skeleton.md",
    ARTIFACTS / "migration-7a-5-conversation-persistence-specialist-summary-writer.md",
    ARTIFACTS / "migration-7a-6-vocabulary-registry-parity-table.md",
    ARTIFACTS / "migration-7a-7-a2-single-decision-shims-terminal-gates.md",
    ARTIFACTS / "migration-7a-8-integration-parity-test-suite-slab-7a-closeout.md",
]


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@pytest.mark.parametrize("nfr_id", [f"NFR-CG{index}" for index in range(1, 12)])
def test_nfr_cg_block_structural_evidence(nfr_id: str) -> None:
    checks = {
        "NFR-CG1": _assert_sandbox_validator_passes_for_slab_7a,
        "NFR-CG2": _assert_composition_smoke_evidence,
        "NFR-CG3": _assert_n_item_trace_per_story,
        "NFR-CG4": _assert_four_file_lockstep_evidence,
        "NFR-CG5": _assert_k_floor_and_tripwire_governance,
        "NFR-CG6": _assert_gate_mode_governance,
        "NFR-CG7": _assert_pre_commit_stack_surfaces,
        "NFR-CG8": _assert_anti_pattern_catalog_citations,
        "NFR-CG9": _assert_marcus_duality_boundary_evidence,
        "NFR-CG10": _assert_bmad_sprint_governance_cycle,
        "NFR-CG11": _assert_deferred_inventory_governance,
    }

    checks[nfr_id]()


def _assert_sandbox_validator_passes_for_slab_7a() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/utilities/validate_migration_story_sandbox_acs.py",
            *[path.as_posix() for path in SLAB_7A_STORIES],
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def _assert_composition_smoke_evidence() -> None:
    assert (ARTIFACTS / "migration-7-1-directive-composer-composition-smoke.py").is_file()
    assert (ARTIFACTS / "migration-7-7-a2-shims-composition-smoke.py").is_file()
    assert "Composition Smoke" in _text(SLAB_7A_STORIES[0])


def _assert_n_item_trace_per_story() -> None:
    for story in SLAB_7A_STORIES:
        text = _text(story)
        assert "N-item" in text or "N1" in text or "substrate" in text, story


def _assert_four_file_lockstep_evidence() -> None:
    required = [
        REPO_ROOT / "schema" / "production_envelope.v1.schema.json",
        REPO_ROOT / "app" / "models" / "schemas" / "decision_cards.schema.json",
        REPO_ROOT / "app" / "models" / "schemas" / "specialist_state.schema.json",
        REPO_ROOT / "tests" / "fixtures" / "runtime" / "production_envelope_golden.json",
        REPO_ROOT / "tests" / "fixtures" / "models" / "state" / "golden_operator_verdict.json",
        REPO_ROOT / "tests" / "fixtures" / "specialist_state" / "specialist_state_golden.json",
    ]

    assert all(path.is_file() for path in required)
    assert "four-file" in _text(SLAB_7A_STORIES[3]).lower()
    assert "four-file" in _text(SLAB_7A_STORIES[4]).lower()


def _assert_k_floor_and_tripwire_governance() -> None:
    governance = json.loads(GOVERNANCE_JSON.read_text(encoding="utf-8"))

    assert governance["stories"]["7a-8"]["expected_k_target"] == 1.6
    assert governance["stories"]["7a-4"]["k_contract"]["tripwire_threshold_kloc"] == 4.08
    assert "K-tripwire" in _text(SLAB_7A_STORIES[7])


def _assert_gate_mode_governance() -> None:
    governance = json.loads(GOVERNANCE_JSON.read_text(encoding="utf-8"))

    assert governance["version"] == "2026-04-28-slab7a-eight-stories"
    assert governance["stories"]["7a-8"]["expected_gate_mode"] == "dual-gate"
    assert governance["stories"]["7a-8"]["rationale"] == (
        "operator_acceptance_gate + invariant_preservation"
    )


def _assert_pre_commit_stack_surfaces() -> None:
    pyproject = _text(REPO_ROOT / "pyproject.toml")

    assert "[tool.ruff]" in pyproject
    assert "[tool.importlinter]" in pyproject
    assert "co-commit-invariant" in _text(SLAB_7A_STORIES[7])


def _assert_anti_pattern_catalog_citations() -> None:
    catalog = _text(REPO_ROOT / "docs" / "dev-guide" / "specialist-anti-patterns.md")
    slab_reviews = "\n".join(
        _text(path)
        for path in ARTIFACTS.glob("7a-*-code-review-2026-04-29.md")
        if path.is_file()
    )
    story = _text(SLAB_7A_STORIES[7])

    assert "### A12." in catalog
    assert "### A17." in catalog
    assert "### P3." in catalog
    assert all(token in story + slab_reviews for token in ["A12", "A17", "P3"])


def _assert_marcus_duality_boundary_evidence() -> None:
    assert (REPO_ROOT / "app" / "marcus" / "orchestrator" / "gate_runner.py").is_file()
    assert (
        REPO_ROOT
        / "tests"
        / "integration"
        / "marcus"
        / "test_marcus_duality_boundary.py"
    ).is_file()


def _assert_bmad_sprint_governance_cycle() -> None:
    sprint_status = yaml.safe_load((ARTIFACTS / "sprint-status.yaml").read_text(encoding="utf-8"))
    statuses = sprint_status["development_status"]

    assert all(
        statuses[f"migration-7a-{index}-{slug}"] == "done"
        for index, slug in [
            (1, "directive-composer"),
            (2, "manifest-fold-flags-compiler-extension"),
            (3, "pre-gate-marcus-shared-llm-node"),
            (4, "per-slide-subgraph-html-review-pack-skeleton"),
            (5, "conversation-persistence-specialist-summary-writer"),
            (6, "vocabulary-registry-parity-table"),
            (7, "a2-single-decision-shims-terminal-gates"),
        ]
    )
    assert statuses["migration-7a-8-integration-parity-test-suite-slab-7a-closeout"] in {
        "in-progress",
        "review",
        "done",
    }
    assert "Claude spec" in _text(SLAB_7A_STORIES[7])
    assert "Codex dev" in _text(SLAB_7A_STORIES[7])


def _assert_deferred_inventory_governance() -> None:
    text = _text(DEFERRED_INVENTORY)

    assert "Slab 7a-Filed Named-But-Not-Filed Follow-Ons" in text
    assert "Slab 7a-8 golden-trace fixtures from trial-2" in text
    assert "Slab 7a-4 HTML review-pack full styling" in text
    assert "Slab 7a-7 + Doc-7-D documentation-completion follow-on" in text
