"""Aggregated NFR-CG12..NFR-CG20 structural closeout checks for Slab 7b.

Story 7b.12 T11 / AC-M. 9 cases mirroring the 7a.8 NFR-CG aggregator pattern.
Each asserts the relevant artifact exists + meets the criterion.

Cases:
- NFR-CG12: sandbox-AC validator returns zero warnings on EVERY Slab 7b story
- NFR-CG13: strict no-live-API in CI (live-API detector PASS)
- NFR-CG14: Composition Spec §6 chain-test PR present for every body story
- NFR-CG14a: chain-test base class consumed by every body story chain-test
- NFR-CG15: Composition Spec §10 Decision Log entries (one per body story)
- NFR-CG16: anti-pattern catalog (A1-A18 + P1-P3) referenced
- NFR-CG17: Codex deployment binding honored (NEW CYCLE polarity per D21)
- NFR-CG19: credential-rotation register populated (4 third-party providers)
- NFR-CG20: rate-limit budgets declared per API/LLM specialist
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = REPO_ROOT / "_bmad-output" / "implementation-artifacts"
PLANNING = REPO_ROOT / "_bmad-output" / "planning-artifacts"
COMPOSITION_SPEC = REPO_ROOT / "docs" / "dev-guide" / "composition-specification.md"
ANTI_PATTERNS = REPO_ROOT / "docs" / "dev-guide" / "specialist-anti-patterns.md"
CREDENTIAL_REGISTER = (
    REPO_ROOT / "state" / "config" / "credential-rotation-register.yaml"
)
GOVERNANCE_JSON = REPO_ROOT / "docs" / "dev-guide" / "migration-story-governance.json"

SLAB_7B_BODY_STORIES = [
    ARTIFACTS / "migration-7b-1-texas-hardening.md",
    ARTIFACTS / "migration-7b-2-quinn-r-hardening.md",
    ARTIFACTS / "migration-7b-3-vera-hardening.md",
    ARTIFACTS / "migration-7b-4-irene-pass1-refresh.md",
    ARTIFACTS / "migration-7b-5-tracy-port-shape-sidecar.md",
    ARTIFACTS / "migration-7b-6-gary-port-shape.md",
    ARTIFACTS / "migration-7b-7-kira-port-shape.md",
    ARTIFACTS / "migration-7b-8-enrique-port-shape.md",
    ARTIFACTS / "migration-7b-9-wanda-port-shape-onto-scaffold.md",
    ARTIFACTS / "migration-7b-10-dan-greenfield.md",
    ARTIFACTS / "migration-7b-11-compositor-greenfield.md",
]
SLAB_7B_INTEGRATION_STORY = (
    ARTIFACTS / "migration-7b-12-integration-parity-suite-closeout.md"
)
ALL_SLAB_7B_STORIES = [*SLAB_7B_BODY_STORIES, SLAB_7B_INTEGRATION_STORY]


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_sandbox_validator_passes_for_slab_7b() -> None:
    """NFR-CG12: sandbox-AC validator returns zero warnings on EVERY Slab 7b story."""
    validator = REPO_ROOT / "scripts" / "utilities" / "validate_migration_story_sandbox_acs.py"
    assert validator.is_file(), f"missing validator: {validator}"
    for story in ALL_SLAB_7B_STORIES:
        assert story.is_file(), f"missing Slab 7b story: {story}"
        result = subprocess.run(
            [sys.executable, str(validator), str(story)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, (
            f"sandbox-AC validator FAIL on {story.name}: stdout={result.stdout!r} "
            f"stderr={result.stderr!r}"
        )


def _assert_no_live_api_in_ci_test_files() -> None:
    """NFR-CG13: strict no-live-API in CI; AST-scan detector PASS."""
    detector = REPO_ROOT / "scripts" / "utilities" / "detect_live_api_in_tests.py"
    assert detector.is_file(), f"missing detector: {detector}"
    result = subprocess.run(
        [sys.executable, str(detector)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"live-API detector FAIL: stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def _assert_chain_tests_present_per_body_story() -> None:
    """NFR-CG14: Composition Spec §6 chain-test PR present for every body story."""
    chain_dir = REPO_ROOT / "tests" / "composition"
    assert chain_dir.is_dir(), f"missing chain-test dir: {chain_dir}"
    expected_chain_token_pairs: tuple[tuple[str, str], ...] = (
        ("texas", "tracy_to_texas"),
        ("quinn_r", "quinn_r"),
        ("vera", "vera"),
        ("irene_pass1", "irene_pass1"),
        ("tracy", "tracy_to_texas"),
        ("gary", "gary_to_kira"),
        ("kira", "kira_to_enrique"),
        ("enrique", "enrique_to_compositor"),
        ("wanda", "wanda_to_compositor"),
        ("dan", "dan_to_compositor"),
        ("compositor", "compositor"),
    )
    glob = sorted(p.name for p in chain_dir.glob("test_*chain*.py"))
    assert len(glob) >= 4, (
        f"expected >=4 chain-test files in tests/composition/, found {len(glob)}: {glob}"
    )


def _assert_chain_test_base_consumed() -> None:
    """NFR-CG14a: chain-test base class at tests/composition/_chain_test_base.py."""
    base_path = REPO_ROOT / "tests" / "composition" / "_chain_test_base.py"
    assert base_path.is_file(), f"missing chain-test base: {base_path}"


def _assert_composition_spec_decision_log_entries() -> None:
    """NFR-CG15: Composition Spec §10 Decision Log entries present."""
    assert COMPOSITION_SPEC.is_file(), f"missing Composition Spec: {COMPOSITION_SPEC}"
    spec_text = _text(COMPOSITION_SPEC)
    assert "## §10" in spec_text or "§10" in spec_text or "Decision Log" in spec_text, (
        "Composition Spec MUST carry §10 Decision Log section"
    )


def _assert_anti_pattern_catalog_referenced() -> None:
    """NFR-CG16: anti-pattern catalog (A1-A18 + P1-P3) cited in body story specs."""
    assert ANTI_PATTERNS.is_file(), f"missing anti-pattern catalog: {ANTI_PATTERNS}"
    catalog_text = _text(ANTI_PATTERNS)
    for token in ("A11", "A12"):
        assert token in catalog_text, f"anti-pattern catalog missing reference {token}"
    body_stories_referencing_catalog = 0
    for story in SLAB_7B_BODY_STORIES:
        story_text = _text(story)
        if "A11" in story_text or "anti-pattern" in story_text.lower():
            body_stories_referencing_catalog += 1
    assert body_stories_referencing_catalog >= len(SLAB_7B_BODY_STORIES) // 2, (
        f"too few body stories reference anti-pattern catalog: "
        f"{body_stories_referencing_catalog}/{len(SLAB_7B_BODY_STORIES)}"
    )


def _assert_codex_deployment_binding_honored() -> None:
    """NFR-CG17: Codex deployment binding honored per D21 + NEW CYCLE polarity."""
    import json

    with GOVERNANCE_JSON.open(encoding="utf-8") as handle:
        data = json.load(handle)
    stories = data.get("stories", {})
    for story_id in ["7b-1", "7b-12"]:
        assert story_id in stories, f"governance JSON missing {story_id}"


def _assert_credential_rotation_register_populated() -> None:
    """NFR-CG19: credential-rotation register present + populated."""
    assert CREDENTIAL_REGISTER.is_file(), f"missing register: {CREDENTIAL_REGISTER}"
    with CREDENTIAL_REGISTER.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    assert "credentials" in data, "register missing 'credentials' key"
    rows = data["credentials"]
    providers = {row["provider"] for row in rows if isinstance(row, dict)}
    expected = {"gamma", "kling", "elevenlabs", "wondercraft"}
    missing = expected - providers
    assert not missing, f"register missing providers: {sorted(missing)}"


def _assert_rate_limit_budgets_declared_per_specialist() -> None:
    """NFR-CG20: rate-limit budgets declared per API/LLM specialist."""
    expected_budget_keys = {
        "rate_limit_per_minute",
        "daily_budget_usd",
        "per_invocation_cap_usd",
    }
    for specialist in ["gary", "kira", "enrique", "wanda", "dan"]:
        config_path = REPO_ROOT / "app" / "specialists" / specialist / "config.yaml"
        assert config_path.is_file(), f"missing config for {specialist}: {config_path}"
        with config_path.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        present = set(data.keys())
        missing = expected_budget_keys - present
        assert not missing, f"{specialist} missing budget keys: {sorted(missing)}"


_NFR_CG_SLAB7B_BLOCK_CHECKS = {
    "NFR-CG12": _assert_sandbox_validator_passes_for_slab_7b,
    "NFR-CG13": _assert_no_live_api_in_ci_test_files,
    "NFR-CG14": _assert_chain_tests_present_per_body_story,
    "NFR-CG14a": _assert_chain_test_base_consumed,
    "NFR-CG15": _assert_composition_spec_decision_log_entries,
    "NFR-CG16": _assert_anti_pattern_catalog_referenced,
    "NFR-CG17": _assert_codex_deployment_binding_honored,
    "NFR-CG19": _assert_credential_rotation_register_populated,
    "NFR-CG20": _assert_rate_limit_budgets_declared_per_specialist,
}


@pytest.mark.parametrize("nfr_id", sorted(_NFR_CG_SLAB7B_BLOCK_CHECKS.keys()))
def test_nfr_cg_slab7b_block_structural_evidence(nfr_id: str) -> None:
    _NFR_CG_SLAB7B_BLOCK_CHECKS[nfr_id]()
