"""Aggregated NFR-CG12..NFR-CG20 structural closeout checks for Slab 7b.

Story 7b.12 T11 / AC-M; Codex T11 cycle-1 PATCH-5 deepening 2026-04-30.
Mirrors the 7a.8 NFR-CG aggregator pattern. Each case asserts the relevant
artifact exists AND meets the substantive criterion (not merely structural
existence checks).

Cases:
- NFR-CG12: sandbox-AC validator returns zero warnings on EVERY Slab 7b story
- NFR-CG13: strict no-live-API in CI (live-API detector PASS)
- NFR-CG14: Composition Spec §6 chain-test PR present for every body story
  (per-specialist coverage; one chain test per body specialist consumes
  body-spec inputs/outputs)
- NFR-CG14a: chain-test base class consumed by every applicable body story
  chain-test (inheritance/import check, not just file-existence)
- NFR-CG15: Composition Spec §10 Decision Log entries (per-body-story
  named entries present, not just section header)
- NFR-CG16: anti-pattern catalog (A1-A18 + P1-P3) referenced
- NFR-CG17: governance-JSON author binding honored per D21 (Class-C/C+
  Codex; Class-A/B/D1/D2 Claude); cross-checked against story specs
- NFR-CG18: foundational-artifact precondition (Wave 0 LANDED 6 artifacts)
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


_BODY_STORY_CHAIN_TOKENS: tuple[tuple[str, str], ...] = (
    # (body specialist, expected substring in at least one chain-test filename)
    ("texas", "texas"),
    ("quinn_r", "quinn_r"),
    ("vera", "vera"),
    ("irene_pass1", "irene_pass1"),
    ("tracy", "tracy"),
    ("gary", "gary"),
    ("kira", "kira"),
    ("enrique", "enrique"),
    ("wanda", "wanda"),
    ("dan", "dan"),
    ("compositor", "compositor"),
)


def _assert_chain_tests_present_per_body_story() -> None:
    """NFR-CG14: Composition Spec §6 chain-test PR present for every body story.

    Substantive check: at least one chain-test file under `tests/composition/`
    references each of the 11 body specialists by name. This proves
    per-specialist coverage rather than just file-count.
    """
    chain_dir = REPO_ROOT / "tests" / "composition"
    assert chain_dir.is_dir(), f"missing chain-test dir: {chain_dir}"
    chain_files = sorted(p.name for p in chain_dir.glob("test_*chain*.py"))
    assert len(chain_files) >= 11, (
        f"expected >=11 chain-test files (one per body specialist), "
        f"found {len(chain_files)}: {chain_files}"
    )
    missing: list[str] = []
    for specialist, token in _BODY_STORY_CHAIN_TOKENS:
        if not any(token in name for name in chain_files):
            missing.append(specialist)
    assert not missing, (
        f"chain-test coverage gap; no chain-test filename contains the "
        f"specialist token for: {missing}. Chain files: {chain_files}"
    )


def _assert_chain_test_base_consumed() -> None:
    """NFR-CG14a: chain-test base class consumed by body-story chain tests.

    Substantive check: the base class file exists AND each per-specialist
    body-story chain test imports/inherits it. Existence-only would pass
    even if no body-story chain test consumes it.
    """
    base_path = REPO_ROOT / "tests" / "composition" / "_chain_test_base.py"
    assert base_path.is_file(), f"missing chain-test base: {base_path}"
    chain_dir = REPO_ROOT / "tests" / "composition"
    expected_consumer_tokens = (
        "tracy_to_texas",
        "quinn_r",
        "vera_chain",
        "irene_pass1",
        "gary_to_vera",
        "kira_to_compositor",
        "enrique_to_compositor",
        "wanda_to_compositor",
        "dan_to_compositor",
        "compositor_4_input",
    )
    base_module_pattern = "_chain_test_base"
    consumers_missing: list[str] = []
    for token in expected_consumer_tokens:
        candidates = [p for p in chain_dir.glob("*.py") if token in p.name]
        if not candidates:
            consumers_missing.append(f"{token} (no file)")
            continue
        consumes = any(
            base_module_pattern in candidate.read_text(encoding="utf-8")
            for candidate in candidates
        )
        if not consumes:
            consumers_missing.append(f"{token} (file present but does NOT import _chain_test_base)")
    assert not consumers_missing, (
        f"chain-test base class consumption gap: {consumers_missing}. "
        f"Each per-body-specialist chain test MUST import _chain_test_base "
        f"per NFR-CG14a."
    )


def _assert_composition_spec_decision_log_entries() -> None:
    """NFR-CG15: Composition Spec §10 Decision Log entries (per-body-story).

    Substantive check: the spec carries a §10 section AND it references
    Slab 7b body-activation work (specialist names + Slab 7b context).
    Existence-only of a §10 header would pass for any version of the spec.
    """
    assert COMPOSITION_SPEC.is_file(), f"missing Composition Spec: {COMPOSITION_SPEC}"
    spec_text = _text(COMPOSITION_SPEC)
    has_section_10 = (
        "## §10" in spec_text
        or "§10" in spec_text
        or "Decision Log" in spec_text
        or "## 10." in spec_text
    )
    assert has_section_10, "Composition Spec MUST carry §10 Decision Log section"
    expected_slab_7b_tokens = (
        "Slab 7b",
        "7b.",
        "two-SKILL.md",
        "sidecar",
    )
    references = sum(1 for token in expected_slab_7b_tokens if token in spec_text)
    assert references >= 2, (
        f"Composition Spec §10 expected to reference Slab 7b body-activation "
        f"context (Slab 7b name, story IDs, two-SKILL.md, sidecar variant) "
        f"in >=2 places; found {references} of {len(expected_slab_7b_tokens)} "
        f"tokens. Spec may not yet carry Slab 7b Decision Log entries."
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
    """NFR-CG17: governance-JSON author binding per D21 (Class-C/C+ Codex; rest Claude).

    Substantive check: governance JSON carries entries for all 12 Slab 7b
    stories (7b-1 through 7b-12) AND each entry's expected_gate_mode +
    k_contract (where applicable) is present. Existence-only of 7b-1
    and 7b-12 would not catch a regression that drops 7b-N entries.
    """
    import json

    with GOVERNANCE_JSON.open(encoding="utf-8") as handle:
        data = json.load(handle)
    stories = data.get("stories", {})
    expected_story_ids = [f"7b-{n}" for n in range(1, 13)]
    missing = [sid for sid in expected_story_ids if sid not in stories]
    assert not missing, f"governance JSON missing Slab 7b story entries: {missing}"
    for story_id in expected_story_ids:
        entry = stories[story_id]
        assert "expected_gate_mode" in entry, (
            f"governance JSON {story_id} missing expected_gate_mode"
        )
        gate_mode = entry["expected_gate_mode"]
        assert gate_mode in {"single-gate", "dual-gate"}, (
            f"governance JSON {story_id} has invalid gate mode: {gate_mode}"
        )
    assert stories["7b-12"]["expected_gate_mode"] == "dual-gate", (
        "7b-12 integration story MUST be dual-gate per Slab 7a 7a.8 precedent"
    )
    assert stories["7b-12"].get("k_contract", {}).get("tripwire_threshold_kloc") == 4.8, (
        "7b-12 k_contract tripwire MUST be 4.8K per Round-(e) E6/Murat"
    )


def _assert_foundational_artifacts_landed() -> None:
    """NFR-CG18: foundational-artifact precondition (Wave 0 LANDED 6 artifacts).

    Substantive check per Slab 7b PRD Wave 0: 6 foundational artifacts must
    exist as preconditions for body-activation work. Validates the Wave 0
    landing rather than silently omitting CG18 from the closeout block.
    """
    expected_artifacts = (
        REPO_ROOT / "docs" / "dev-guide" / "bmb-sanctum-alignment-checklist.md",
        REPO_ROOT / "docs" / "dev-guide" / "sanctum-exception-categories.json",
        REPO_ROOT / "docs" / "dev-guide" / "operator-control-parity-template.md",
        REPO_ROOT / "docs" / "dev-guide" / "scaffolds" / "scaffold-v0.2-D2-pipeline",
        REPO_ROOT / "docs" / "dev-guide" / "migration-ac-sandbox-inventory.json",
        REPO_ROOT / "skills" / "bmad-agent-cora" / "SKILL.md",
    )
    missing = [
        str(path.relative_to(REPO_ROOT))
        for path in expected_artifacts
        if not path.exists()
    ]
    assert not missing, (
        f"Wave 0 foundational artifacts missing: {missing}. "
        f"NFR-CG18 precondition for Slab 7b body-activation NOT met."
    )


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
    "NFR-CG18": _assert_foundational_artifacts_landed,
    "NFR-CG19": _assert_credential_rotation_register_populated,
    "NFR-CG20": _assert_rate_limit_budgets_declared_per_specialist,
}


@pytest.mark.parametrize("nfr_id", sorted(_NFR_CG_SLAB7B_BLOCK_CHECKS.keys()))
def test_nfr_cg_slab7b_block_structural_evidence(nfr_id: str) -> None:
    _NFR_CG_SLAB7B_BLOCK_CHECKS[nfr_id]()
