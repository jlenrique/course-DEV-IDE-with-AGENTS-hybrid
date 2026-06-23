"""Validation helpers for Creative Director directives."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.utilities.file_helpers import project_root as default_project_root

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]


PROJECT_ROOT = default_project_root()
CREATIVE_DIRECTIVE_SCHEMA_PATH = (
    PROJECT_ROOT / "state" / "config" / "schemas" / "creative-directive.schema.json"
)
EXPERIENCE_PROFILES_PATH = PROJECT_ROOT / "state" / "config" / "experience-profiles.yaml"
SUM_TOLERANCE = 0.001


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return payload


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise ValueError("pyyaml is required to validate creative directives")
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected YAML mapping at {path}")
    return payload


def load_experience_profile_targets(
    *,
    profiles_path: Path | None = None,
) -> dict[str, Any]:
    """Return the configured profile target blocks keyed by profile name.

    Single source of truth for directive emitters (e.g., the CD specialist's
    deterministic canonicalization): the parity rule below forbids any
    deviation from these targets, so emitters must bind values from here
    rather than asking an LLM to reproduce them.
    """
    profiles_path = profiles_path or EXPERIENCE_PROFILES_PATH
    payload = _load_yaml(profiles_path)
    profiles = payload.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        raise ValueError(f"no profiles mapping in {profiles_path}")
    return profiles


def validate_creative_directive(
    directive: dict[str, Any],
    *,
    schema_path: Path | None = None,
    profiles_path: Path | None = None,
) -> list[str]:
    """Return a list of validation errors for a creative directive payload."""
    schema_path = schema_path or CREATIVE_DIRECTIVE_SCHEMA_PATH
    profiles_path = profiles_path or EXPERIENCE_PROFILES_PATH
    schema = _load_json(schema_path)
    profiles_data = _load_yaml(profiles_path)

    errors: list[str] = []
    required = schema.get("required", [])
    if isinstance(required, list):
        for field in required:
            if field not in directive:
                errors.append(f"missing required field: {field}")

    # JSON Schema const — required key presence alone is insufficient (AC3).
    if "schema_version" in directive:
        sv = directive["schema_version"]
        if not isinstance(sv, str) or sv != "1.0":
            errors.append('schema_version must be the string "1.0"')

    allowed_top_level = set((schema.get("properties") or {}).keys())
    extra_top_level = sorted(set(directive.keys()) - allowed_top_level)
    if extra_top_level:
        errors.append(f"unknown top-level fields: {extra_top_level}")

    profile = directive.get("experience_profile")
    profile_schema = ((schema.get("properties") or {}).get("experience_profile") or {})
    allowed_profiles = set(profile_schema.get("enum", []))
    if profile not in allowed_profiles:
        errors.append(
            f"experience_profile must be one of {sorted(allowed_profiles)}; got {profile!r}"
        )

    modes = directive.get("slide_mode_proportions")
    mode_schema = ((schema.get("properties") or {}).get("slide_mode_proportions") or {})
    required_mode_keys = mode_schema.get("required", [])
    if not isinstance(modes, dict):
        errors.append("slide_mode_proportions must be an object")
    else:
        keys = set(modes.keys())
        expected_keys = set(required_mode_keys) if isinstance(required_mode_keys, list) else set()
        if keys != expected_keys:
            errors.append(
                "slide_mode_proportions must include exactly "
                f"{sorted(expected_keys)}; got {sorted(keys)}"
            )
        total = 0.0
        for key in sorted(expected_keys):
            value = modes.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                errors.append(f"slide_mode_proportions.{key} must be numeric")
                continue
            numeric = float(value)
            if numeric < 0 or numeric > 1:
                errors.append(f"slide_mode_proportions.{key} must be within [0, 1]")
            total += numeric
        if expected_keys and abs(total - 1.0) > SUM_TOLERANCE:
            errors.append(
                "slide_mode_proportions must sum to 1.0 within "
                f"±{SUM_TOLERANCE}; got {total:.6f}"
            )

    controls = directive.get("narration_profile_controls")
    controls_schema = ((schema.get("properties") or {}).get("narration_profile_controls") or {})
    control_props = controls_schema.get("properties", {})
    required_controls = controls_schema.get("required", [])
    if not isinstance(controls, dict):
        errors.append("narration_profile_controls must be an object")
    else:
        allowed_control_keys = (
            set(control_props.keys()) if isinstance(control_props, dict) else set()
        )
        unknown_control_keys = sorted(set(controls.keys()) - allowed_control_keys)
        if unknown_control_keys:
            errors.append(
                f"narration_profile_controls contains unknown keys: {unknown_control_keys}"
            )
        for field in required_controls:
            if field not in controls:
                errors.append(f"narration_profile_controls missing required key: {field}")
        for field, value in controls.items():
            allowed = (
                (control_props.get(field) or {}).get("enum")
                if isinstance(control_props, dict)
                else None
            )
            if allowed and value not in allowed:
                errors.append(
                    f"narration_profile_controls.{field} must be one of {allowed}; got {value!r}"
                )

    rationale = directive.get("creative_rationale")
    if not isinstance(rationale, str) or not rationale.strip():
        errors.append("creative_rationale must be a non-empty string")

    gamma_settings = directive.get("gamma_settings")
    gamma_schema = ((schema.get("properties") or {}).get("gamma_settings") or {})
    if "gamma_settings" in directive and gamma_settings is not None:
        if not isinstance(gamma_settings, list):
            errors.append("gamma_settings must be a list or null when present")
        else:
            item_schema = gamma_schema.get("items") if isinstance(gamma_schema, dict) else {}
            item_props = item_schema.get("properties", {}) if isinstance(item_schema, dict) else {}
            allowed_keys = set(item_props.keys()) if isinstance(item_props, dict) else set()
            required_item_keys = (
                item_schema.get("required", []) if isinstance(item_schema, dict) else []
            )
            seen_variants: set[str] = set()
            for index, item in enumerate(gamma_settings):
                if not isinstance(item, dict):
                    errors.append(f"gamma_settings[{index}] must be an object")
                    continue
                unknown = sorted(set(item) - allowed_keys)
                if unknown:
                    errors.append(f"gamma_settings[{index}] contains unknown keys: {unknown}")
                for field in required_item_keys:
                    if field not in item:
                        errors.append(f"gamma_settings[{index}] missing required key: {field}")
                variant_id = item.get("variant_id")
                allowed_variants = (
                    (item_props.get("variant_id") or {}).get("enum")
                    if isinstance(item_props, dict)
                    else None
                )
                if allowed_variants and variant_id not in allowed_variants:
                    errors.append(
                        f"gamma_settings[{index}].variant_id must be one of "
                        f"{allowed_variants}; got {variant_id!r}"
                    )
                elif isinstance(variant_id, str):
                    if variant_id in seen_variants:
                        errors.append(f"gamma_settings duplicate variant_id: {variant_id}")
                    seen_variants.add(variant_id)
                for field in ("theme", "template", "image_style"):
                    if field in item and not isinstance(item[field], str):
                        errors.append(f"gamma_settings[{index}].{field} must be a string")
                for field in ("density", "tone"):
                    allowed = (
                        (item_props.get(field) or {}).get("enum")
                        if isinstance(item_props, dict)
                        else None
                    )
                    if allowed and field in item and item[field] not in allowed:
                        errors.append(
                            f"gamma_settings[{index}].{field} must be one of "
                            f"{allowed}; got {item[field]!r}"
                        )

    # Enforce profile parity with configured targets.
    configured_profiles = profiles_data.get("profiles", {})
    if (
        isinstance(profile, str)
        and isinstance(configured_profiles, dict)
        and profile in configured_profiles
    ):
        target = configured_profiles[profile]
        if isinstance(target, dict):
            target_modes = target.get("slide_mode_proportions")
            if (
                isinstance(target_modes, dict)
                and isinstance(modes, dict)
                and target_modes != modes
            ):
                errors.append(
                    "slide_mode_proportions must match profile target values "
                    "in experience-profiles.yaml"
                )
            target_controls = target.get("narration_profile_controls")
            if (
                isinstance(target_controls, dict)
                and isinstance(controls, dict)
                and target_controls != controls
            ):
                errors.append(
                    "narration_profile_controls must match profile target values "
                    "in experience-profiles.yaml"
                )

    return errors
