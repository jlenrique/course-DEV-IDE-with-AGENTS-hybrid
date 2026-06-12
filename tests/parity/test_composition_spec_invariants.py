"""SG-3 aggregated Composition Spec invariant checks for Slab 7a closeout."""

from __future__ import annotations

import inspect
import re
from pathlib import Path

import yaml

from app.manifest.loader import load
from app.marcus.orchestrator import production_runner
from app.models.runtime.production_envelope import ProductionEnvelope

REPO_ROOT = Path(__file__).resolve().parents[2]
COMPOSITION_SPEC = REPO_ROOT / "docs" / "dev-guide" / "composition-specification.md"
MANIFEST = REPO_ROOT / "state" / "config" / "pipeline-manifest.yaml"


def _composition_spec_text() -> str:
    return COMPOSITION_SPEC.read_text(encoding="utf-8")


def test_section_3_1_envelope_append_only_and_sha256_invariant() -> None:
    # Doc-phrase pins follow the v2 as-built rewrite (drift micro-batch
    # 2026-06-12): per-node keying replaced the v1 append-only-per-specialist
    # invariant; the SHA256 digest invariant is unchanged.
    text = _composition_spec_text()

    assert "### 3.1 The accumulator: `ProductionEnvelope`" in text
    assert "per (specialist_id, node_id)" in text
    assert "retry-overwrite" in text
    assert "SHA256 of canonical-JSON-serialized output" in text
    assert "add_contribution" in ProductionEnvelope.__dict__
    assert (
        REPO_ROOT / "tests" / "unit" / "runtime" / "test_production_envelope_strict.py"
    ).is_file()


def test_section_3_5_gate_precedence_is_non_blocking_by_default() -> None:
    text = _composition_spec_text()
    signature = inspect.signature(production_runner.run_production_trial)

    assert "### 3.5 Gate precedence rule" in text
    assert "Per-specialist gates auto-resolve under production composition" in text
    assert "gate_overrides" not in signature.parameters
    assert production_runner._build_decision_card is not None


def test_section_3_6_manifest_declared_dependencies_are_present() -> None:
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    manifest_model = load(MANIFEST)
    dependency_nodes = [
        node for node in manifest["nodes"] if node.get("dependencies")
    ]

    assert "### 3.6 Dependency_map sourcing" in _composition_spec_text()
    assert dependency_nodes
    assert any(node.dependencies for node in manifest_model.nodes)


def test_section_6_chain_test_per_pr_contract_exists() -> None:
    text = _composition_spec_text()

    assert "## 6. The composition-test discipline" in text
    assert "chain-test-per-PR rule" in text
    assert (
        REPO_ROOT
        / "tests"
        / "composition"
        / "test_texas_to_cd_chain.py"
    ).is_file()
    assert (
        REPO_ROOT
        / "tests"
        / "composition"
        / "composed_specialist_chain_harness.py"
    ).is_file()


def test_section_9_composition_smoke_gate_evidence_exists() -> None:
    text = _composition_spec_text()

    assert "## 9. Composition Smoke gate" in text
    assert (
        REPO_ROOT
        / "_bmad-output"
        / "implementation-artifacts"
        / "migration-7-1-directive-composer-composition-smoke.py"
    ).is_file()
    assert (
        REPO_ROOT
        / "_bmad-output"
        / "implementation-artifacts"
        / "migration-7-7-a2-shims-composition-smoke.py"
    ).is_file()


def test_section_10_decision_log_tracks_runner_supplied_payload() -> None:
    text = _composition_spec_text()

    assert "## 10. Decision Log" in text
    assert "2026-04-29" in text
    assert "runner-supplied directive carrier" in text
    assert "runner_supplied_payload" in text


def test_section_11_migration_triggers_are_tracked_without_new_7a8_trigger() -> None:
    text = _composition_spec_text()
    triggers = re.findall(r"^\*\*Trigger \d", text, flags=re.MULTILINE)

    assert "## 11. Migration triggers" in text
    assert len(triggers) == 6
    assert "Gate precedence complexity grows" in text
    assert "Adapter LOC exceeds" in text
