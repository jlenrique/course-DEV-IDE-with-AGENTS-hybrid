"""Tests for the profile-aware slide count and runtime estimator (Story 20c-15).

Covers:
- E1: Feasibility triangle (10 cases: PASS, WARN, BLOCK boundaries)
- E2: Profile resolution (4 cases: visual-led, text-led, unknown, missing expansion)
- E3: Backward compatibility (analyze_content_for_slides)
- E4: WARN→ACK→PASS operator cycle
- E5: E2E chain (profile → estimator → operator polling → locked params)
- E6: Word budget derivation from profile
- E7: Content analysis edge cases
"""

import textwrap
from pathlib import Path

import pytest
import yaml

from scripts.utilities.slide_count_runtime_estimator import (
    EstimatorError,
    _analyze_content,
    _load_profile,
    _run_feasibility_triangle,
    analyze_content_for_slides,
    estimate_and_validate,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def visual_led_profiles(tmp_path: Path) -> Path:
    """Profiles YAML with visual-led and text-led, both having cluster_expansion."""
    profiles = {
        "schema_version": "1.1",
        "profiles": {
            "visual-led": {
                "slide_mode_proportions": {
                    "creative": 0.60,
                    "literal-visual": 0.25,
                    "literal-text": 0.15,
                },
                "cluster_expansion": {
                    "avg_interstitials_per_cluster": 1.5,
                    "interstitial_range": [0, 3],
                    "singleton_ratio": 0.30,
                    "cluster_head_word_range": [60, 100],
                    "interstitial_word_range": [15, 30],
                    "estimator_advisory": {"parents_per_minute": 1.5},
                },
            },
            "text-led": {
                "slide_mode_proportions": {
                    "creative": 0.25,
                    "literal-visual": 0.15,
                    "literal-text": 0.60,
                },
                "cluster_expansion": {
                    "avg_interstitials_per_cluster": 3.0,
                    "interstitial_range": [1, 5],
                    "singleton_ratio": 0.10,
                    "cluster_head_word_range": [80, 140],
                    "interstitial_word_range": [25, 40],
                    "estimator_advisory": {"parents_per_minute": 0.95},
                },
            },
        },
    }
    p = tmp_path / "experience-profiles.yaml"
    p.write_text(yaml.safe_dump(profiles, sort_keys=False), encoding="utf-8")
    return p


@pytest.fixture()
def narration_params(tmp_path: Path) -> Path:
    """Minimal narration-script-parameters.yaml."""
    params = {"narration_density": {"target_wpm": 150}}
    p = tmp_path / "narration-script-parameters.yaml"
    p.write_text(yaml.safe_dump(params, sort_keys=False), encoding="utf-8")
    return p


@pytest.fixture()
def extracted_md(tmp_path: Path) -> str:
    """Sample extracted.md with known word count and sections."""
    content = textwrap.dedent("""\
        ## Introduction

        Slide 1: This is the first slide with some introductory content
        about the topic we are covering today.

        ## Main Content

        Part 1: Here we examine the core concepts that are central
        to understanding this module's material in depth.

        ## Summary

        Slide 2: Final summary slide with concluding remarks about
        what we have learned throughout this lesson.
    """)
    p = tmp_path / "extracted.md"
    p.write_text(content, encoding="utf-8")
    return str(p)


@pytest.fixture()
def empty_md(tmp_path: Path) -> str:
    """Empty extracted.md."""
    p = tmp_path / "extracted.md"
    p.write_text("", encoding="utf-8")
    return str(p)


# ---------------------------------------------------------------------------
# E1: Feasibility Triangle — 10 cases
# ---------------------------------------------------------------------------


class TestFeasibilityTriangle:
    """E1: 10 feasibility triangle test cases."""

    def test_all_pass_comfortable_margins(self) -> None:
        """All 5 conditions pass with comfortable margins."""
        result = _run_feasibility_triangle(
            parent_slide_count=10,
            target_runtime_minutes=10.0,
            estimated_total_slides=20.0,
            avg_slide_seconds=30.0,
            target_runtime_seconds=600.0,
        )
        assert result["result"] == "PASS"
        assert len(result["details"]) == 5
        assert all(d["result"] == "PASS" for d in result["details"])

    def test_runtime_fit_block_over_5pct(self) -> None:
        """BLOCK when estimated time overshoots target by >5%."""
        # 20 slides × 35s = 700s, target = 600s, overshoot = 16.7%
        result = _run_feasibility_triangle(
            parent_slide_count=10,
            target_runtime_minutes=10.0,
            estimated_total_slides=20.0,
            avg_slide_seconds=35.0,
            target_runtime_seconds=600.0,
        )
        assert result["result"] == "BLOCK"
        runtime_fit = result["details"][0]
        assert runtime_fit["name"] == "runtime_fit"
        assert runtime_fit["result"] == "BLOCK"

    def test_runtime_fit_warn_under_5pct(self) -> None:
        """WARN when overshoot is 0-5%."""
        # 20 slides × 30.5s = 610s, target = 600s, overshoot = 1.67%
        result = _run_feasibility_triangle(
            parent_slide_count=10,
            target_runtime_minutes=10.0,
            estimated_total_slides=20.0,
            avg_slide_seconds=30.5,
            target_runtime_seconds=600.0,
        )
        assert result["result"] == "WARN"
        runtime_fit = result["details"][0]
        assert runtime_fit["result"] == "WARN"

    def test_runtime_fit_exact_match_passes(self) -> None:
        """PASS when estimated time exactly equals target."""
        result = _run_feasibility_triangle(
            parent_slide_count=10,
            target_runtime_minutes=10.0,
            estimated_total_slides=20.0,
            avg_slide_seconds=30.0,
            target_runtime_seconds=600.0,
        )
        assert result["details"][0]["result"] == "PASS"

    def test_min_slide_duration_block(self) -> None:
        """BLOCK when avg_slide_seconds < MIN_AVG_SLIDE_SECONDS."""
        result = _run_feasibility_triangle(
            parent_slide_count=10,
            target_runtime_minutes=10.0,
            estimated_total_slides=200.0,
            avg_slide_seconds=3.0,
            target_runtime_seconds=600.0,
        )
        assert result["result"] == "BLOCK"
        min_dur = [d for d in result["details"] if d["name"] == "min_slide_duration"][0]
        assert min_dur["result"] == "BLOCK"

    def test_max_slide_duration_block(self) -> None:
        """BLOCK when avg_slide_seconds > MAX_AVG_SLIDE_SECONDS."""
        result = _run_feasibility_triangle(
            parent_slide_count=2,
            target_runtime_minutes=10.0,
            estimated_total_slides=2.0,
            avg_slide_seconds=300.0,
            target_runtime_seconds=600.0,
        )
        assert result["result"] == "BLOCK"
        max_dur = [d for d in result["details"] if d["name"] == "max_slide_duration"][0]
        assert max_dur["result"] == "BLOCK"

    def test_min_parent_count_block(self) -> None:
        """BLOCK when parent_slide_count < MIN_PARENT_SLIDE_COUNT."""
        result = _run_feasibility_triangle(
            parent_slide_count=0,
            target_runtime_minutes=5.0,
            estimated_total_slides=0.0,
            avg_slide_seconds=30.0,
            target_runtime_seconds=300.0,
        )
        assert result["result"] == "BLOCK"
        min_parent = [d for d in result["details"] if d["name"] == "min_parent_count"][0]
        assert min_parent["result"] == "BLOCK"

    def test_min_runtime_block(self) -> None:
        """BLOCK when target_runtime_minutes < MIN_TARGET_RUNTIME_MINUTES."""
        result = _run_feasibility_triangle(
            parent_slide_count=5,
            target_runtime_minutes=0.1,
            estimated_total_slides=5.0,
            avg_slide_seconds=1.2,
            target_runtime_seconds=6.0,
        )
        assert result["result"] == "BLOCK"
        min_rt = [d for d in result["details"] if d["name"] == "min_runtime"][0]
        assert min_rt["result"] == "BLOCK"

    def test_multiple_blocks_still_block(self) -> None:
        """Multiple failing conditions all appear in details."""
        result = _run_feasibility_triangle(
            parent_slide_count=0,
            target_runtime_minutes=0.1,
            estimated_total_slides=0.0,
            avg_slide_seconds=3.0,
            target_runtime_seconds=6.0,
        )
        assert result["result"] == "BLOCK"
        block_count = sum(1 for d in result["details"] if d["result"] == "BLOCK")
        assert block_count >= 3

    def test_underfit_passes(self) -> None:
        """PASS when estimated time is well under target (no BLOCK or WARN)."""
        # 10 slides × 20s = 200s, target = 600s, negative overshoot
        result = _run_feasibility_triangle(
            parent_slide_count=5,
            target_runtime_minutes=10.0,
            estimated_total_slides=10.0,
            avg_slide_seconds=20.0,
            target_runtime_seconds=600.0,
        )
        assert result["result"] == "PASS"


# ---------------------------------------------------------------------------
# E2: Profile Resolution — 4 cases
# ---------------------------------------------------------------------------


class TestProfileResolution:
    """E2: Profile resolution edge cases."""

    def test_load_visual_led_profile(self, visual_led_profiles: Path) -> None:
        profile = _load_profile("visual-led", visual_led_profiles)
        assert profile["cluster_expansion"]["avg_interstitials_per_cluster"] == 1.5
        assert profile["cluster_expansion"]["singleton_ratio"] == 0.30

    def test_load_text_led_profile(self, visual_led_profiles: Path) -> None:
        profile = _load_profile("text-led", visual_led_profiles)
        assert profile["cluster_expansion"]["avg_interstitials_per_cluster"] == 3.0
        assert profile["cluster_expansion"]["singleton_ratio"] == 0.10

    def test_unknown_profile_raises(self, visual_led_profiles: Path) -> None:
        with pytest.raises(EstimatorError, match="Unknown experience profile"):
            _load_profile("cinematic", visual_led_profiles)

    def test_missing_cluster_expansion_raises(self, tmp_path: Path) -> None:
        """Profile exists but lacks cluster_expansion block."""
        profiles = {
            "schema_version": "1.0",
            "profiles": {
                "bare": {
                    "slide_mode_proportions": {"creative": 1.0},
                },
            },
        }
        p = tmp_path / "profiles.yaml"
        p.write_text(yaml.safe_dump(profiles, sort_keys=False), encoding="utf-8")
        with pytest.raises(EstimatorError, match="missing required 'cluster_expansion'"):
            _load_profile("bare", p)


# ---------------------------------------------------------------------------
# E3: Backward Compatibility
# ---------------------------------------------------------------------------


class TestBackwardCompatibility:
    """E3: Legacy analyze_content_for_slides still works."""

    def test_legacy_wrapper_returns_expected_keys(self, extracted_md: str) -> None:
        result = analyze_content_for_slides(extracted_md)
        assert "recommended_slide_count" in result
        assert "estimated_total_runtime_minutes" in result
        assert "word_count" in result
        assert "analysis" in result
        assert result["word_count"] > 0

    def test_legacy_wrapper_respects_max_slides(self, extracted_md: str) -> None:
        result = analyze_content_for_slides(extracted_md, max_slides=1)
        assert result["recommended_slide_count"] <= 1


# ---------------------------------------------------------------------------
# E6: Word Budget Derivation from Profile
# ---------------------------------------------------------------------------


class TestWordBudgetDerivation:
    """E6: Word budgets come from the profile's cluster_expansion."""

    def test_visual_led_word_budgets(
        self,
        visual_led_profiles: Path,
        narration_params: Path,
        extracted_md: str,
    ) -> None:
        result = estimate_and_validate(
            extracted_md,
            parent_slide_count=10,
            target_runtime_minutes=10.0,
            experience_profile="visual-led",
            profiles_path=visual_led_profiles,
            narration_params_path=narration_params,
        )
        assert result["word_budgets"]["cluster_head_word_range"] == [60, 100]
        assert result["word_budgets"]["interstitial_word_range"] == [15, 30]

    def test_text_led_word_budgets(
        self,
        visual_led_profiles: Path,
        narration_params: Path,
        extracted_md: str,
    ) -> None:
        result = estimate_and_validate(
            extracted_md,
            parent_slide_count=10,
            target_runtime_minutes=10.0,
            experience_profile="text-led",
            profiles_path=visual_led_profiles,
            narration_params_path=narration_params,
        )
        assert result["word_budgets"]["cluster_head_word_range"] == [80, 140]
        assert result["word_budgets"]["interstitial_word_range"] == [25, 40]


# ---------------------------------------------------------------------------
# E7: Content Analysis Edge Cases
# ---------------------------------------------------------------------------


class TestContentAnalysis:
    """E7: Edge cases in content analysis."""

    def test_empty_file(self, empty_md: str) -> None:
        result = _analyze_content(empty_md)
        assert result["word_count"] == 0
        assert result["total_sections"] == 0

    def test_slide_headers_counted(self, extracted_md: str) -> None:
        result = _analyze_content(extracted_md)
        assert result["slide_headers_found"] == 2
        assert result["major_sections_found"] == 3
        assert result["part_headers_found"] == 1

    def test_single_word_file(self, tmp_path: Path) -> None:
        p = tmp_path / "single.md"
        p.write_text("hello", encoding="utf-8")
        result = _analyze_content(str(p))
        assert result["word_count"] == 1


# ---------------------------------------------------------------------------
# E2E Integration: estimate_and_validate
# ---------------------------------------------------------------------------


class TestEstimateAndValidate:
    """Full estimate_and_validate integration tests."""

    def test_visual_led_feasible(
        self,
        visual_led_profiles: Path,
        narration_params: Path,
        extracted_md: str,
    ) -> None:
        """Visual-led profile with comfortable margins passes."""
        result = estimate_and_validate(
            extracted_md,
            parent_slide_count=5,
            target_runtime_minutes=10.0,
            experience_profile="visual-led",
            profiles_path=visual_led_profiles,
            narration_params_path=narration_params,
        )
        assert result["feasibility"] == "PASS"
        assert result["profile_used"] == "visual-led"
        assert result["parent_slide_count"] == 5
        # visual-led: 5 × (1 + 1.5 × 0.70) = 5 × 2.05 = 10.25
        assert result["estimated_total_slides"] == 10.2
        assert result["avg_slide_seconds"] > 0

    def test_text_led_higher_expansion(
        self,
        visual_led_profiles: Path,
        narration_params: Path,
        extracted_md: str,
    ) -> None:
        """Text-led profile expands more slides per parent."""
        result = estimate_and_validate(
            extracted_md,
            parent_slide_count=5,
            target_runtime_minutes=10.0,
            experience_profile="text-led",
            profiles_path=visual_led_profiles,
            narration_params_path=narration_params,
        )
        # text-led: 5 × (1 + 3.0 × 0.90) = 5 × 3.7 = 18.5
        assert result["estimated_total_slides"] == 18.5
        assert result["profile_used"] == "text-led"

    def test_overshoot_triggers_block(
        self,
        visual_led_profiles: Path,
        narration_params: Path,
        extracted_md: str,
    ) -> None:
        """Too many parents for short runtime → BLOCK."""
        result = estimate_and_validate(
            extracted_md,
            parent_slide_count=20,
            target_runtime_minutes=1.0,
            experience_profile="visual-led",
            profiles_path=visual_led_profiles,
            narration_params_path=narration_params,
        )
        assert result["feasibility"] == "BLOCK"

    def test_recommendation_included(
        self,
        visual_led_profiles: Path,
        narration_params: Path,
        extracted_md: str,
    ) -> None:
        result = estimate_and_validate(
            extracted_md,
            parent_slide_count=5,
            target_runtime_minutes=10.0,
            experience_profile="visual-led",
            profiles_path=visual_led_profiles,
            narration_params_path=narration_params,
        )
        rec = result["recommendation"]
        assert "recommended_parent_slide_count" in rec
        assert rec["parents_per_minute"] == 1.5
        assert rec["target_wpm"] == 150


# ---------------------------------------------------------------------------
# E4/E5: Operator Polling + Validate Locked Params
# ---------------------------------------------------------------------------


class TestValidateLockedParams:
    """E4: Validate locked params including feasibility status."""

    def test_pass_params_valid(self) -> None:
        from scripts.utilities.operator_polling import validate_locked_params

        params = {
            "parent_slide_count": 10,
            "target_total_runtime_minutes": 10.0,
            "feasibility": "PASS",
        }
        result = validate_locked_params(params)
        assert result["valid"] is True
        assert result["reason"] == "Feasible"

    def test_warn_params_require_ack(self) -> None:
        from scripts.utilities.operator_polling import validate_locked_params

        params = {
            "parent_slide_count": 10,
            "target_total_runtime_minutes": 10.0,
            "feasibility": "WARN",
        }
        result = validate_locked_params(params)
        assert result["valid"] is True
        assert result.get("requires_ack") is True

    def test_block_params_invalid(self) -> None:
        from scripts.utilities.operator_polling import validate_locked_params

        params = {
            "parent_slide_count": 10,
            "target_total_runtime_minutes": 10.0,
            "feasibility": "BLOCK",
        }
        result = validate_locked_params(params)
        assert result["valid"] is False

    def test_out_of_range_parent_count(self) -> None:
        from scripts.utilities.operator_polling import validate_locked_params

        params = {
            "parent_slide_count": 100,
            "target_total_runtime_minutes": 10.0,
            "feasibility": "PASS",
        }
        result = validate_locked_params(params)
        assert result["valid"] is False

    def test_out_of_range_runtime(self) -> None:
        from scripts.utilities.operator_polling import validate_locked_params

        params = {
            "parent_slide_count": 10,
            "target_total_runtime_minutes": 0.1,
            "feasibility": "PASS",
        }
        result = validate_locked_params(params)
        assert result["valid"] is False


class TestCheckRuntimeFeasibility:
    """E5: check_runtime_feasibility delegates to estimator."""

    def test_delegates_to_estimator(
        self,
        visual_led_profiles: Path,
        narration_params: Path,
        extracted_md: str,
    ) -> None:
        from scripts.utilities.operator_polling import check_runtime_feasibility

        result = check_runtime_feasibility(
            parent_slide_count=5,
            target_runtime_minutes=10.0,
            experience_profile="visual-led",
            extracted_md_path=extracted_md,
            profiles_path=visual_led_profiles,
            narration_params_path=narration_params,
        )
        assert result["feasibility"] in ("PASS", "WARN", "BLOCK")
        assert result["profile_used"] == "visual-led"
