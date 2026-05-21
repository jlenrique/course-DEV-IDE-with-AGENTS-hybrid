"""Validation tests for experience profile definitions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from scripts.utilities import run_constants as rc

PROFILES_PATH = Path("state/config/experience-profiles.yaml")
NARRATION_PARAMS_PATH = Path("state/config/narration-script-parameters.yaml")
EXPECTED_MODE_KEYS = {"literal-text", "literal-visual", "creative"}


def _load_profiles() -> dict[str, Any]:
    data = yaml.safe_load(PROFILES_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _load_narration_params() -> dict[str, Any]:
    data = yaml.safe_load(NARRATION_PARAMS_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_profiles_file_has_required_top_level_shape() -> None:
    data = _load_profiles()
    assert data["schema_version"] == "1.1"
    assert isinstance(data.get("profiles"), dict)
    assert {"visual-led", "text-led"}.issubset(data["profiles"].keys())


def test_profile_mode_proportions_are_canonical_and_normalized() -> None:
    profiles = _load_profiles()["profiles"]
    for profile_name, profile_data in profiles.items():
        assert isinstance(profile_data, dict)
        modes = profile_data.get("slide_mode_proportions")
        assert isinstance(modes, dict), f"{profile_name} missing slide_mode_proportions"
        assert set(modes.keys()) == EXPECTED_MODE_KEYS
        total = 0.0
        for key, value in modes.items():
            assert isinstance(value, (int, float)) and not isinstance(value, bool)
            numeric = float(value)
            assert 0.0 <= numeric <= 1.0
            total += numeric
        assert abs(total - 1.0) <= 0.001


def test_profile_narration_controls_have_required_keys() -> None:
    profiles = _load_profiles()["profiles"]
    required_controls = set(_load_narration_params()["narration_profile_controls"].keys())
    for profile_name, profile_data in profiles.items():
        controls = profile_data.get("narration_profile_controls")
        assert isinstance(controls, dict), f"{profile_name} missing narration_profile_controls"
        assert set(controls.keys()) == required_controls


def test_profile_cluster_density_is_present_and_valid() -> None:
    profiles = _load_profiles()["profiles"]
    allowed = rc.ALLOWED_CLUSTER_DENSITIES
    for profile_name, profile_data in profiles.items():
        cluster_density = profile_data.get("cluster_density")
        assert isinstance(cluster_density, str), f"{profile_name} missing cluster_density"
        assert cluster_density in allowed


def test_every_profile_name_is_accepted_by_parse_run_constants() -> None:
    profiles = _load_profiles()["profiles"]
    base = {
        "run_id": "profile-contract",
        "lesson_slug": "lesson",
        "bundle_path": "bundle",
        "primary_source_file": "primary.pdf",
        "optional_context_assets": [],
        "theme_selection": "theme",
        "theme_paramset_key": "preset",
        "execution_mode": "tracked/default",
        "quality_preset": "draft",
    }

    for profile_name, profile_data in profiles.items():
        parsed = rc.parse_run_constants(
            {
                **base,
                "experience_profile": profile_name,
            }
        )
        assert parsed.experience_profile == profile_name
        assert parsed.cluster_density == rc.resolve_experience_profile(profile_name)["cluster_density"]
        assert parsed.slide_mode_proportions == profile_data["slide_mode_proportions"]


def test_downstream_skills_do_not_reference_experience_profiles_directly() -> None:
    allowed_upstream_dirs = {"bmad-agent-cd", "bmad-agent-marcus"}
    offenders: list[str] = []

    for skill_dir in Path("skills").iterdir():
        if not skill_dir.is_dir() or skill_dir.name in allowed_upstream_dirs:
            continue
        for path in skill_dir.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".mp3", ".mp4", ".db"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if "experience-profiles" in text:
                offenders.append(str(path).replace("\\", "/"))

    assert offenders == []
