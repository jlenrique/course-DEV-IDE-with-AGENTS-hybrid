# /// script
# requires-python = ">=3.10"
# ///
"""Validate Irene Pass 2 completeness - post-Pass-2 check.

Story 11.3 gate (extended for stricter Pass 2 semantics):
- Require both gary_slide_output and perception_artifacts.
- Fail closed with explicit missing-field diagnostics.
- Preserve Gary card ordering as the source of truth for downstream narration.
- When bundle-root Pass 2 outputs are present, also validate:
  - every authorized slide has at least one manifest segment
  - every manifest segment has non-empty narration_text
  - every manifest segment has at least one non-empty visual narration cue
    traceable to perception and present in narration_text
  - every non-static motion segment is tied to the approved motion asset and
    has matching motion perception confirmation

Timing: Run AFTER Irene Pass 2 completes, not before delegation.
Perception artifacts are generated inline during Pass 2
(the LLM reads each slide PNG and emits a perception artifact as a
side-effect of writing narration). This validator confirms completeness.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
import re

try:
    import yaml
except ImportError:  # pragma: no cover - optional for yaml input
    yaml = None  # type: ignore[assignment]


REQUIRED_PASS2_FIELDS = ("gary_slide_output", "perception_artifacts")
NARRATION_SCRIPT_FILENAME = "narration-script.md"
SEGMENT_MANIFEST_FILENAME = "segment-manifest.yaml"
PERCEPTION_ARTIFACTS_FILENAME = "perception-artifacts.json"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
NARRATION_PARAMS_PATH = PROJECT_ROOT / "state" / "config" / "narration-script-parameters.yaml"
WORD_RE = re.compile(r"\b\w+(?:[-']\w+)?\b")
_FALLBACK_INTRO_PATTERNS = [
    "in this section",
    "let's turn to",
    "we'll begin",
    "welcome",
    "to start",
]
_FALLBACK_OUTRO_PATTERNS = [
    "next, we'll",
    "to wrap up",
    "moving forward",
    "in summary",
    "that brings us",
]
_FALLBACK_PIVOT_PATTERNS = [
    "but",
    "however",
    "yet",
]
_BEHAVIORAL_INTENT_COMPATIBILITY: dict[str, set[str]] = {
    "credible": {"credible", "clear-guidance", "reflective"},
    "alarming": {"credible", "alarming", "clear-guidance"},
    "provocative": {"credible", "provocative", "reflective"},
    "reflective": {"credible", "reflective", "moving", "clear-guidance"},
    "moving": {"credible", "moving", "reflective"},
    "clear-guidance": {"credible", "alarming", "clear-guidance", "attention-reset", "reflective"},
    "attention-reset": {"credible", "clear-guidance", "attention-reset"},
}
_CLUSTER_ARC_POSITION_ORDER = {
    "establish": 0,
    "tension": 1,
    "develop": 2,
    "resolve": 3,
}
_GENERIC_CONCEPT_STOPWORDS = {
    "about",
    "after",
    "again",
    "along",
    "also",
    "although",
    "because",
    "before",
    "being",
    "between",
    "brief",
    "closure",
    "compare",
    "comparison",
    "concept",
    "detail",
    "details",
    "during",
    "evidence",
    "explain",
    "explains",
    "explore",
    "explains",
    "focus",
    "focused",
    "guidance",
    "guide",
    "guided",
    "headword",
    "however",
    "insight",
    "intro",
    "itself",
    "learner",
    "main",
    "moving",
    "next",
    "notice",
    "outro",
    "pivotword",
    "recap",
    "resolve",
    "section",
    "slide",
    "slides",
    "story",
    "summary",
    "through",
    "toward",
    "using",
    "via",
    "while",
}


def _is_remote_http_ref(value: str) -> bool:
    parsed = urlparse(str(value).strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _resolve_existing_local_path(path_value: str, *, bundle_dir: Path | None) -> Path | None:
    candidate = Path(path_value)
    if candidate.is_absolute():
        return candidate if candidate.is_file() else None

    if bundle_dir is not None:
        bundle_candidate = (bundle_dir / candidate).resolve()
        if bundle_candidate.is_file():
            return bundle_candidate

    project_candidate = (PROJECT_ROOT / candidate).resolve()
    if project_candidate.is_file():
        return project_candidate

    return None


def _resolve_local_path(path_value: str, *, bundle_dir: Path | None) -> Path:
    candidate = Path(path_value)
    if candidate.is_absolute():
        return candidate.resolve(strict=False)
    if bundle_dir is not None:
        return (bundle_dir / candidate).resolve(strict=False)
    return (PROJECT_ROOT / candidate).resolve(strict=False)


def _normalize_path_string(path_value: str, *, bundle_dir: Path | None) -> str:
    return str(_resolve_local_path(path_value, bundle_dir=bundle_dir))


def _load_payload(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8-sig")
    suffix = path.suffix.lower()

    if suffix in {".yml", ".yaml"}:
        if yaml is None:
            raise RuntimeError("PyYAML is required for YAML input payloads")
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)

    if not isinstance(data, dict):
        raise ValueError("Pass 2 envelope payload must be an object at the top level")
    return data


def _bundle_dir_from_inputs(
    payload: dict[str, Any],
    *,
    envelope_path: Path | None,
) -> Path | None:
    if envelope_path is not None:
        return envelope_path.parent
    bundle_path = payload.get("bundle_path")
    if isinstance(bundle_path, str) and bundle_path.strip():
        return _resolve_local_path(bundle_path.strip(), bundle_dir=None)
    return None


def _resolve_bundle_output_path(
    payload: dict[str, Any],
    *,
    bundle_dir: Path | None,
    filename: str,
) -> Path | None:
    expected_outputs = payload.get("expected_outputs", [])
    if isinstance(expected_outputs, list):
        for entry in expected_outputs:
            if not isinstance(entry, str):
                continue
            candidate = Path(entry)
            if candidate.name.lower() == filename.lower():
                return _resolve_local_path(entry, bundle_dir=bundle_dir)

    if bundle_dir is None:
        return None
    return bundle_dir / filename


def _load_json_object(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain a JSON object at the top level")
    return data


def _load_yaml_object(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required for segment-manifest validation")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain a YAML mapping at the top level")
    return data


def _load_json_array(path: Path) -> list[Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, list):
        raise ValueError(f"{path.name} must contain a JSON array at the top level")
    return data


def _load_meta_slide_language_guardrails() -> dict[str, Any]:
    """Load narration anti-meta guardrails from narration-script-parameters.yaml."""
    if yaml is None or not NARRATION_PARAMS_PATH.is_file():
        return {"policy": "allowed", "forbidden_phrases": []}

    try:
        data = yaml.safe_load(NARRATION_PARAMS_PATH.read_text(encoding="utf-8")) or {}
    except Exception:
        return {"policy": "allowed", "forbidden_phrases": []}

    visual = data.get("visual_narration", {})
    if not isinstance(visual, dict):
        return {"policy": "allowed", "forbidden_phrases": []}

    policy = str(visual.get("meta_slide_language") or "allowed").strip().lower()
    phrases_raw = visual.get("forbidden_meta_phrases", [])
    if not isinstance(phrases_raw, list):
        phrases_raw = []

    forbidden_phrases = [
        str(item).strip().lower()
        for item in phrases_raw
        if isinstance(item, str) and str(item).strip()
    ]
    return {"policy": policy, "forbidden_phrases": forbidden_phrases}


def _load_narration_density() -> dict[str, Any]:
    if yaml is None or not NARRATION_PARAMS_PATH.is_file():
        return {}
    try:
        data = yaml.safe_load(NARRATION_PARAMS_PATH.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    density = data.get("narration_density", {})
    return density if isinstance(density, dict) else {}


def _load_cluster_narration() -> dict[str, Any]:
    density = _load_narration_density()
    cluster_narration = density.get("cluster_narration", {})
    return cluster_narration if isinstance(cluster_narration, dict) else {}


def _load_runtime_variability() -> dict[str, Any]:
    if yaml is None or not NARRATION_PARAMS_PATH.is_file():
        return {}
    try:
        data = yaml.safe_load(NARRATION_PARAMS_PATH.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    runtime_variability = data.get("runtime_variability", {})
    return runtime_variability if isinstance(runtime_variability, dict) else {}


def _load_pedagogical_bridging() -> dict[str, Any]:
    if yaml is None or not NARRATION_PARAMS_PATH.is_file():
        return {}
    try:
        data = yaml.safe_load(NARRATION_PARAMS_PATH.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    bridging = data.get("pedagogical_bridging", {})
    return bridging if isinstance(bridging, dict) else {}


def _load_narration_profile_controls() -> dict[str, Any]:
    if yaml is None or not NARRATION_PARAMS_PATH.is_file():
        return {}
    try:
        data = yaml.safe_load(NARRATION_PARAMS_PATH.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    controls = data.get("narration_profile_controls", {})
    return controls if isinstance(controls, dict) else {}


def _active_narration_profile_controls(payload: dict[str, Any]) -> dict[str, Any]:
    envelope_controls = payload.get("narration_profile_controls")
    if isinstance(envelope_controls, dict):
        return dict(envelope_controls)
    return _load_narration_profile_controls()


def _normalize_phrase_patterns(raw: Any) -> list[str]:
    if not isinstance(raw, list):
        return []
    return [str(item).strip() for item in raw if isinstance(item, str) and str(item).strip()]


def _text_matches_any_phrase_pattern(text: str, patterns: list[str]) -> bool:
    if not patterns:
        return False
    lowered = text.lower()
    return any(pattern.lower() in lowered for pattern in patterns)


def _spoken_bridge_issue_message(
    bridge_type: str,
    narration_text: str,
    *,
    intro_patterns: list[str],
    outro_patterns: list[str],
    pivot_patterns: list[str],
) -> str | None:
    """Return a short machine reason if narration_text lacks required spoken cues."""
    bt = str(bridge_type or "none").strip().lower() or "none"
    if bt == "cluster_boundary":
        bt = "both"
    if bt == "none":
        return None
    if not str(narration_text or "").strip():
        return "is empty"
    if bt == "intro":
        if not _text_matches_any_phrase_pattern(narration_text, intro_patterns):
            return f"lacks intro-class cue (expected substring from {len(intro_patterns)} pattern(s))"
        return None
    if bt == "outro":
        if not _text_matches_any_phrase_pattern(narration_text, outro_patterns):
            return f"lacks outro-class cue (expected substring from {len(outro_patterns)} pattern(s))"
        return None
    if bt == "pivot":
        if not _text_matches_any_phrase_pattern(narration_text, pivot_patterns):
            return f"lacks pivot-class cue (expected substring from {len(pivot_patterns)} pattern(s))"
        return None
    if bt == "both":
        if not _text_matches_any_phrase_pattern(narration_text, intro_patterns):
            return f"lacks intro-class cue for bridge_type both (expected substring from {len(intro_patterns)} pattern(s))"
        if not _text_matches_any_phrase_pattern(narration_text, outro_patterns):
            return f"lacks outro-class cue for bridge_type both (expected substring from {len(outro_patterns)} pattern(s))"
        return None
    return None


def _behavioral_intent_serves_master(
    master_behavioral_intent: str | None,
    segment_behavioral_intent: str | None,
) -> bool:
    master = str(master_behavioral_intent or "").strip().lower()
    segment = str(segment_behavioral_intent or "").strip().lower()
    if not master or not segment:
        return True
    if master == segment:
        return True
    return segment in _BEHAVIORAL_INTENT_COMPATIBILITY.get(master, set())


def _word_count(text: str) -> int:
    return len(WORD_RE.findall(text or ""))


def _extract_concept_tokens(text: str) -> set[str]:
    tokens: set[str] = set()
    for raw_token in WORD_RE.findall(text or ""):
        token = raw_token.lower()
        normalized = token.replace("-", "").replace("'", "")
        if len(normalized) < 4:
            continue
        if normalized in _GENERIC_CONCEPT_STOPWORDS:
            continue
        if not any(ch.isalpha() for ch in normalized):
            continue
        tokens.add(normalized)
    return tokens


def _normalize_anchor_text(value: str) -> str:
    normalized = str(value or "").strip().lstrip("#").strip().lower()
    return re.sub(r"\s+", " ", normalized)


def _extract_markdown_section(text: str, anchor: str) -> str:
    normalized_anchor = _normalize_anchor_text(anchor)
    if not normalized_anchor:
        return text
    lines = text.splitlines()
    collecting = False
    collected: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            heading_text = stripped.lstrip("#").strip()
            if collecting:
                break
            if _normalize_anchor_text(heading_text) == normalized_anchor:
                collecting = True
                collected.append(line)
                continue
        elif collecting:
            collected.append(line)
    return "\n".join(collected).strip() if collected else text


def _load_source_ref_excerpt(source_ref: str, *, bundle_dir: Path | None) -> str:
    raw = str(source_ref or "").strip()
    if not raw:
        return ""
    if "#" in raw:
        path_part, anchor = raw.split("#", 1)
    else:
        path_part, anchor = raw, ""
    candidate = _resolve_existing_local_path(path_part.strip(), bundle_dir=bundle_dir)
    if candidate is None:
        return ""
    try:
        text = candidate.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = candidate.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""
    return _extract_markdown_section(text, anchor)


def _normalize_word_range(raw: Any) -> tuple[int, int] | None:
    if not isinstance(raw, (list, tuple)) or len(raw) != 2:
        return None
    try:
        lower = int(raw[0])
        upper = int(raw[1])
    except (TypeError, ValueError):
        return None
    if lower <= 0 or upper < lower:
        return None
    return lower, upper


def _is_cluster_boundary_transition(
    previous_record: dict[str, Any] | None,
    current_record: dict[str, Any],
) -> bool:
    if previous_record is None:
        return False
    previous_cluster_id = str(previous_record.get("cluster_id") or "").strip() or None
    current_cluster_id = str(current_record.get("cluster_id") or "").strip() or None
    if not previous_cluster_id or not current_cluster_id:
        return False
    if previous_cluster_id == current_cluster_id:
        return False
    return True


def _bridge_satisfies_cadence(
    bridge_type: str,
    *,
    accepted_bridge_types: set[str],
    cluster_bridge_cadence_override: bool,
    record_is_clustered: bool,
    is_cluster_boundary: bool,
    cluster_role: str | None,
    fallback_due: bool,
) -> bool:
    bt = str(bridge_type or "none").strip().lower() or "none"
    if bt == "none":
        return False
    if accepted_bridge_types and bt not in accepted_bridge_types:
        return False
    if not cluster_bridge_cadence_override or not record_is_clustered:
        return True
    if is_cluster_boundary:
        return bt == "cluster_boundary"
    if str(cluster_role or "").strip().lower() == "interstitial":
        return False
    return fallback_due and bt in {"intro", "outro", "both"}


def _should_check_spoken_bridge_cues(
    bridge_type: str,
    *,
    cluster_bridge_cadence_override: bool,
    cluster_id: str | None,
) -> bool:
    bt = str(bridge_type or "none").strip().lower() or "none"
    if bt in ("", "none"):
        return False
    if cluster_bridge_cadence_override and cluster_id:
        return bt == "cluster_boundary"
    return True


def _rationale_dimension_hits(
    rationale: str,
    *,
    dimension_keywords: dict[str, list[str]],
) -> set[str]:
    lowered = rationale.lower()
    hits: set[str] = set()
    for dimension, keywords in dimension_keywords.items():
        if any(keyword.lower() in lowered for keyword in keywords):
            hits.add(dimension)
    return hits


def _find_forbidden_meta_segments_in_script(
    narration_path: Path,
    *,
    forbidden_phrases: list[str],
) -> list[str]:
    """Return segment IDs in narration-script.md containing forbidden phrases."""
    if not forbidden_phrases:
        return []

    text = narration_path.read_text(encoding="utf-8")
    flagged: list[str] = []
    current_segment: str | None = None
    current_lines: list[str] = []

    def flush_segment() -> None:
        if current_segment is None:
            return
        lowered = "\n".join(current_lines).lower()
        if any(phrase in lowered for phrase in forbidden_phrases):
            flagged.append(current_segment)

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("[SEGMENT:") and line.endswith("]"):
            flush_segment()
            current_segment = line[len("[SEGMENT:") : -1].strip()
            current_lines = []
            continue
        if current_segment is not None:
            current_lines.append(raw_line)

    flush_segment()
    return sorted(set(flagged))


def _extract_behavioral_intents_from_script(narration_path: Path) -> dict[str, str]:
    """Parse `[SEGMENT: ...]` blocks and extract stage-direction behavioral intents."""
    intents: dict[str, str] = {}
    current_segment: str | None = None

    for raw_line in narration_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("[SEGMENT:") and line.endswith("]"):
            current_segment = line[len("[SEGMENT:") : -1].strip()
            continue
        if current_segment is None:
            continue
        if line.lower().startswith("- behavioral intent:"):
            intent = line.split(":", 1)[1].strip()
            if intent:
                intents[current_segment] = intent
    return intents


def _artifact_identity_key(artifact: dict[str, Any]) -> str:
    slide_id = str(artifact.get("slide_id") or "").strip()
    if slide_id:
        return slide_id
    artifact_path = str(artifact.get("artifact_path") or "").strip()
    if artifact_path:
        return artifact_path
    return json.dumps(artifact, sort_keys=True)


def _normalize_artifact_for_compare(artifact: dict[str, Any]) -> str:
    return json.dumps(artifact, sort_keys=True)


def _load_authorized_slide_ids(
    payload: dict[str, Any],
    *,
    bundle_dir: Path | None,
    gary_slide_ids: list[str],
) -> list[str]:
    authorized_path_value = payload.get("authorized_storyboard_path")
    if isinstance(authorized_path_value, str) and authorized_path_value.strip():
        authorized_path = _resolve_existing_local_path(authorized_path_value, bundle_dir=bundle_dir)
        if authorized_path is not None:
            data = _load_json_object(authorized_path)
            slide_ids = data.get("slide_ids", [])
            if isinstance(slide_ids, list):
                normalized = [str(item).strip() for item in slide_ids if str(item).strip()]
                if normalized:
                    return normalized
    return gary_slide_ids


def _load_motion_plan_assignments(
    payload: dict[str, Any],
    *,
    bundle_dir: Path | None,
) -> dict[str, dict[str, Any]]:
    motion_path_value = payload.get("motion_plan_path")
    if not isinstance(motion_path_value, str) or not motion_path_value.strip():
        return {}

    motion_plan_path = _resolve_existing_local_path(motion_path_value, bundle_dir=bundle_dir)
    if motion_plan_path is None:
        return {}

    motion_plan = _load_yaml_object(motion_plan_path)
    slides = motion_plan.get("slides", [])
    if not isinstance(slides, list):
        return {}

    by_slide_id: dict[str, dict[str, Any]] = {}
    for row in slides:
        if not isinstance(row, dict):
            continue
        slide_id = str(row.get("slide_id") or "").strip()
        if slide_id:
            by_slide_id[slide_id] = row
    return by_slide_id


def _build_perception_element_lookup(
    perception_artifacts: list[dict[str, Any]],
) -> dict[str, set[str]]:
    lookup: dict[str, set[str]] = {}
    for artifact in perception_artifacts:
        if not isinstance(artifact, dict):
            continue
        slide_id = str(artifact.get("slide_id") or "").strip()
        if not slide_id:
            continue
        elements = artifact.get("visual_elements", [])
        descriptions: set[str] = set()
        if isinstance(elements, list):
            for element in elements:
                if not isinstance(element, dict):
                    continue
                description = str(element.get("description") or "").strip()
                if description:
                    descriptions.add(description)
        if slide_id in lookup:
            lookup[slide_id].update(descriptions)
        else:
            lookup[slide_id] = descriptions
    return lookup


def _validate_bundle_pass2_outputs(
    payload: dict[str, Any],
    *,
    bundle_dir: Path | None,
    gary_slide_ids: list[str],
    gary_slide_path_by_id: dict[str, str],
    gary_slide_source_ref_by_id: dict[str, str],
    perception_artifacts: list[dict[str, Any]],
    runtime_policy_strict: bool,
) -> dict[str, Any]:
    details: dict[str, Any] = {
        "narration_script_path": None,
        "segment_manifest_path": None,
        "perception_artifacts_path": None,
        "authorized_slide_count": 0,
        "manifest_segment_count": 0,
        "narration_script_missing": False,
        "narration_script_empty": False,
        "segment_manifest_missing": False,
        "segment_manifest_invalid": False,
        "perception_artifacts_missing": False,
        "perception_artifacts_invalid": False,
        "missing_manifest_for_slide_ids": [],
        "unknown_manifest_slide_ids": [],
        "segments_missing_narration_text": [],
        "segments_missing_visual_narration_cue": [],
        "segments_with_untraceable_visual_cues": [],
        "segments_with_forbidden_meta_slide_language": [],
        "script_segments_with_forbidden_meta_slide_language": [],
        "segments_with_behavioral_intent_mismatch": [],
        "segments_with_master_behavioral_intent_violation": [],
        "cluster_behavioral_intent_violations_by_cluster": {},
        "segments_missing_behavioral_intent": [],
        "cluster_new_concept_violations": [],
        "cluster_arc_integrity_violations": [],
        "motion_segments_with_static_narration_hint": [],
        "perception_artifact_mismatches": [],
        "motion_segments_missing_perception_confirmation": [],
        "motion_segments_with_unapproved_asset_binding": [],
        "runtime_budget_warnings": [],
        "cluster_word_range_warnings": [],
        "missing_runtime_rationale_fields": [],
        "weak_runtime_rationales": [],
        "bridge_cadence_warnings": [],
        "within_cluster_bridge_warnings": [],
        "cluster_boundary_warnings": [],
        "spoken_bridge_warnings": [],
        "active_narration_profile_controls": {},
    }

    if bundle_dir is None:
        return {"errors": [], "details": details}

    errors: list[str] = []
    warnings: list[str] = []
    meta_guardrails = _load_meta_slide_language_guardrails()
    narration_density = _load_narration_density()
    cluster_narration = _load_cluster_narration()
    runtime_variability = _load_runtime_variability()
    pedagogical_bridging = _load_pedagogical_bridging()
    spoken_policy_raw = pedagogical_bridging.get("spoken_bridge_policy", {})
    spoken_policy = spoken_policy_raw if isinstance(spoken_policy_raw, dict) else {}
    spoken_enforcement = str(spoken_policy.get("enforcement") or "warn").strip().lower()
    if spoken_enforcement not in {"off", "warn", "error"}:
        spoken_enforcement = "warn"
    intro_patterns = _normalize_phrase_patterns(spoken_policy.get("intro_phrase_patterns"))
    outro_patterns = _normalize_phrase_patterns(spoken_policy.get("outro_phrase_patterns"))
    if not intro_patterns:
        intro_patterns = list(_FALLBACK_INTRO_PATTERNS)
    if not outro_patterns:
        outro_patterns = list(_FALLBACK_OUTRO_PATTERNS)
    pivot_patterns = list(_FALLBACK_PIVOT_PATTERNS)
    details["active_narration_profile_controls"] = _active_narration_profile_controls(payload)

    narration_path = _resolve_bundle_output_path(
        payload,
        bundle_dir=bundle_dir,
        filename=NARRATION_SCRIPT_FILENAME,
    )
    manifest_path = _resolve_bundle_output_path(
        payload,
        bundle_dir=bundle_dir,
        filename=SEGMENT_MANIFEST_FILENAME,
    )
    perception_path = _resolve_bundle_output_path(
        payload,
        bundle_dir=bundle_dir,
        filename=PERCEPTION_ARTIFACTS_FILENAME,
    )

    if narration_path is not None:
        details["narration_script_path"] = str(narration_path)
    if manifest_path is not None:
        details["segment_manifest_path"] = str(manifest_path)
    if perception_path is not None:
        details["perception_artifacts_path"] = str(perception_path)

    if narration_path is None or not narration_path.is_file():
        details["narration_script_missing"] = True
        errors.append(f"Missing required Pass 2 artifact: {NARRATION_SCRIPT_FILENAME}")
    else:
        narration_text = narration_path.read_text(encoding="utf-8").strip()
        if not narration_text:
            details["narration_script_empty"] = True
            errors.append(f"{NARRATION_SCRIPT_FILENAME} exists but is empty")
        elif meta_guardrails["policy"] == "forbidden":
            details["script_segments_with_forbidden_meta_slide_language"] = (
                _find_forbidden_meta_segments_in_script(
                    narration_path,
                    forbidden_phrases=meta_guardrails["forbidden_phrases"],
                )
            )
    script_behavioral_intents = (
        _extract_behavioral_intents_from_script(narration_path)
        if narration_path is not None and narration_path.is_file()
        else {}
    )

    if perception_path is None or not perception_path.is_file():
        details["perception_artifacts_missing"] = True
        errors.append(f"Missing required Pass 2 artifact: {PERCEPTION_ARTIFACTS_FILENAME}")
        standalone_perception_artifacts: list[dict[str, Any]] = []
    else:
        try:
            standalone_raw = _load_json_array(perception_path)
            standalone_perception_artifacts = [
                item for item in standalone_raw if isinstance(item, dict)
            ]
        except Exception as exc:
            details["perception_artifacts_invalid"] = True
            errors.append(f"{PERCEPTION_ARTIFACTS_FILENAME} is invalid: {type(exc).__name__}: {exc}")
            standalone_perception_artifacts = []

    if manifest_path is None or not manifest_path.is_file():
        details["segment_manifest_missing"] = True
        errors.append(f"Missing required Pass 2 artifact: {SEGMENT_MANIFEST_FILENAME}")
        return {"errors": errors, "details": details}

    try:
        manifest = _load_yaml_object(manifest_path)
    except Exception as exc:
        details["segment_manifest_invalid"] = True
        errors.append(f"{SEGMENT_MANIFEST_FILENAME} is invalid: {type(exc).__name__}: {exc}")
        return {"errors": errors, "details": details}

    segments = manifest.get("segments", [])
    if not isinstance(segments, list):
        details["segment_manifest_invalid"] = True
        errors.append(f"{SEGMENT_MANIFEST_FILENAME} segments must be a list")
        return {"errors": errors, "details": details}

    details["manifest_segment_count"] = len(segments)

    authorized_slide_ids = _load_authorized_slide_ids(
        payload,
        bundle_dir=bundle_dir,
        gary_slide_ids=gary_slide_ids,
    )
    details["authorized_slide_count"] = len(authorized_slide_ids)

    manifest_slide_ids: list[str] = []
    manifest_slide_id_set: set[str] = set()
    interstitial_slide_ids: set[str] = set()
    interstitials_missing_cluster_id: list[str] = []
    interstitials_missing_timing_role: list[str] = []
    motion_segments: list[dict[str, Any]] = []
    spoken_bridge_warnings: list[str] = []
    perception_elements_by_slide = _build_perception_element_lookup(perception_artifacts)
    perception_slide_ids = {
        str(item.get("slide_id") or "").strip()
        for item in perception_artifacts
        if isinstance(item, dict)
    }
    motion_plan_by_slide_id = _load_motion_plan_assignments(payload, bundle_dir=bundle_dir)
    motion_perception_artifacts = payload.get("motion_perception_artifacts", [])
    if motion_perception_artifacts is not None and not isinstance(motion_perception_artifacts, list):
        motion_perception_artifacts = []

    motion_confirmations: dict[str, set[str]] = {}
    if isinstance(motion_perception_artifacts, list):
        for artifact in motion_perception_artifacts:
            if not isinstance(artifact, dict):
                continue
            slide_id = str(artifact.get("slide_id") or "").strip()
            if not slide_id:
                continue
            source_motion_path = str(
                artifact.get("source_motion_path")
                or artifact.get("artifact_path")
                or ""
            ).strip()
            if not source_motion_path:
                continue
            motion_confirmations.setdefault(slide_id, set()).add(
                _normalize_path_string(source_motion_path, bundle_dir=bundle_dir)
            )

    segments_missing_narration_text: list[str] = []
    segments_missing_visual_narration_cue: list[str] = []
    segments_with_untraceable_visual_cues: list[str] = []
    motion_segments_missing_perception_confirmation: list[str] = []
    motion_segments_with_unapproved_asset_binding: list[str] = []
    motion_segments_with_noncanonical_visual_file: list[str] = []
    segments_with_forbidden_meta_slide_language: list[str] = []
    segments_with_behavioral_intent_mismatch: list[str] = []
    segments_missing_behavioral_intent: list[str] = []
    motion_segments_with_static_narration_hint: list[str] = []
    runtime_budget_warnings: list[str] = []
    cluster_word_range_warnings: list[str] = []
    missing_runtime_rationale_fields: list[str] = []
    weak_runtime_rationales: list[str] = []
    within_cluster_bridge_warnings: list[str] = []
    cluster_records_by_id: dict[str, list[dict[str, Any]]] = {}
    runtime_targets_by_card = {
        int(entry.get("card_number")): float(entry.get("target_runtime_seconds"))
        for entry in payload.get("runtime_plan", {}).get("per_slide_targets", [])
        if isinstance(entry, dict)
        and entry.get("card_number") not in (None, "")
        and entry.get("target_runtime_seconds") not in (None, "")
    }
    target_wpm = narration_density.get("target_wpm")
    try:
        target_wpm = float(target_wpm) if target_wpm not in (None, "") else None
    except (TypeError, ValueError):
        target_wpm = None
    required_runtime_fields = {
        str(item).strip()
        for item in runtime_variability.get("required_manifest_fields", [])
        if isinstance(item, str) and str(item).strip()
    }
    allowed_timing_roles = {
        str(item).strip()
        for item in runtime_variability.get("allowed_timing_roles", [])
        if isinstance(item, str) and str(item).strip()
    }
    allowed_density_levels = {
        str(item).strip()
        for item in runtime_variability.get("allowed_density_levels", [])
        if isinstance(item, str) and str(item).strip()
    }
    raw_dimension_keywords = runtime_variability.get("rationale_dimensions", {})
    dimension_keywords = {
        str(key).strip(): [
            str(value).strip()
            for value in values
            if isinstance(value, str) and str(value).strip()
        ]
        for key, values in raw_dimension_keywords.items()
        if isinstance(key, str) and isinstance(values, list)
    }
    bridge_cadence = runtime_variability.get("bridge_cadence", {})
    bridge_cadence_enabled = bool(bridge_cadence.get("enabled"))
    try:
        bridge_minutes = float(bridge_cadence.get("require_intro_or_outro_every_minutes"))
    except (TypeError, ValueError):
        bridge_minutes = 0.0
    try:
        bridge_slides = int(bridge_cadence.get("require_intro_or_outro_every_slides"))
    except (TypeError, ValueError):
        bridge_slides = 0
    accepted_bridge_types = {
        str(item).strip().lower()
        for item in bridge_cadence.get("accepted_bridge_types", [])
        if isinstance(item, str) and str(item).strip()
    }
    allowed_bridge_types = set(accepted_bridge_types) | {"none"}
    cluster_head_word_range = _normalize_word_range(
        cluster_narration.get("cluster_head_word_range")
    )
    interstitial_word_range = _normalize_word_range(
        cluster_narration.get("interstitial_word_range")
    )
    within_cluster_policy_raw = pedagogical_bridging.get("within_cluster_bridge_policy", {})
    within_cluster_policy = (
        within_cluster_policy_raw if isinstance(within_cluster_policy_raw, dict) else {}
    )
    within_cluster_default = str(within_cluster_policy.get("default") or "none").strip().lower()
    tension_override = str(
        within_cluster_policy.get("tension_position_override") or ""
    ).strip().lower()
    cluster_bridge_cadence_override = bool(
        bridge_cadence.get("cluster_bridge_cadence_override")
    )
    ordered_slide_records: list[dict[str, Any]] = []
    ordered_slide_index: dict[str, dict[str, Any]] = {}
    for segment in segments:
        if not isinstance(segment, dict):
            continue
        seg_id = str(segment.get("id") or "<missing-id>").strip() or "<missing-id>"
        slide_id = str(segment.get("gary_slide_id") or segment.get("slide_id") or "").strip()
        card_number = segment.get("gary_card_number")
        cluster_role = str(segment.get("cluster_role") or "").strip().lower() or None
        cluster_id = str(segment.get("cluster_id") or "").strip() or None
        cluster_position = str(segment.get("cluster_position") or "").strip().lower() or None
        if slide_id:
            manifest_slide_ids.append(slide_id)
            manifest_slide_id_set.add(slide_id)
            if cluster_role == "interstitial":
                interstitial_slide_ids.add(slide_id)
        # Validate interstitial cluster metadata
        if cluster_role == "interstitial":
            if not cluster_id:
                interstitials_missing_cluster_id.append(seg_id)
            timing_role = str(segment.get("timing_role") or "").strip()
            if not timing_role:
                interstitials_missing_timing_role.append(seg_id)
        slide_key = slide_id or (str(card_number) if card_number not in (None, "") else seg_id)
        bridge_type = str(segment.get("bridge_type") or "none").strip().lower() or "none"
        duration_estimate_raw = segment.get("duration_estimate_seconds")
        try:
            duration_estimate = (
                float(duration_estimate_raw)
                if duration_estimate_raw not in (None, "")
                else float(runtime_targets_by_card.get(card_number))
                if isinstance(card_number, int) and card_number in runtime_targets_by_card
                else 0.0
            )
        except (TypeError, ValueError):
            duration_estimate = 0.0
        slide_record = ordered_slide_index.get(slide_key)
        if slide_record is None:
            slide_record = {
                "seg_id": seg_id,
                "slide_id": slide_id,
                "card_number": card_number,
                "bridge_type": bridge_type,
                "duration_estimate_seconds": duration_estimate,
                "cluster_id": cluster_id,
                "cluster_role": cluster_role,
            }
            ordered_slide_index[slide_key] = slide_record
            ordered_slide_records.append(slide_record)
        else:
            if slide_record.get("bridge_type") in (None, "", "none") and bridge_type != "none":
                slide_record["bridge_type"] = bridge_type
            if not slide_record.get("duration_estimate_seconds") and duration_estimate:
                slide_record["duration_estimate_seconds"] = duration_estimate
            if not slide_record.get("cluster_id") and cluster_id:
                slide_record["cluster_id"] = cluster_id
            if not slide_record.get("cluster_role") and cluster_role:
                slide_record["cluster_role"] = cluster_role

        narration_text = str(segment.get("narration_text") or "").strip()
        words = _word_count(narration_text)
        if not narration_text:
            segments_missing_narration_text.append(seg_id)
        elif meta_guardrails["policy"] == "forbidden":
            lowered = narration_text.lower()
            if any(phrase in lowered for phrase in meta_guardrails["forbidden_phrases"]):
                segments_with_forbidden_meta_slide_language.append(seg_id)
        if narration_text and cluster_role == "head" and cluster_head_word_range is not None:
            lower, upper = cluster_head_word_range
            tolerated_lower = lower - 5
            tolerated_upper = upper + 5
            if words < tolerated_lower or words > tolerated_upper:
                cluster_word_range_warnings.append(
                    f"{seg_id}: cluster head narration word count {words} falls outside "
                    f"cluster_head_word_range {lower}-{upper} with ±5 tolerance "
                    f"({tolerated_lower}-{tolerated_upper})."
                )
        if narration_text and cluster_role == "interstitial" and interstitial_word_range is not None:
            lower, upper = interstitial_word_range
            tolerated_lower = lower - 5
            tolerated_upper = upper + 5
            if words < tolerated_lower or words > tolerated_upper:
                cluster_word_range_warnings.append(
                    f"{seg_id}: interstitial narration word count {words} falls outside "
                    f"interstitial_word_range {lower}-{upper} with ±5 tolerance "
                    f"({tolerated_lower}-{tolerated_upper})."
                )
        if bridge_type != "none" and within_cluster_default == "none":
            tension_pivot_allowed = (
                cluster_role == "interstitial"
                and cluster_position == "tension"
                and tension_override == "pivot"
                and bridge_type == "pivot"
            )
            if not tension_pivot_allowed:
                if cluster_role != "interstitial" and bridge_type == "pivot":
                    within_cluster_bridge_warnings.append(
                        f"{seg_id}: only tension interstitials may use bridge_type pivot; "
                        f"cluster role {cluster_role or 'unknown'} is not eligible."
                    )
                elif cluster_role == "interstitial" and cluster_position == "tension" and tension_override == "pivot":
                    within_cluster_bridge_warnings.append(
                        f"{seg_id}: tension interstitials may only use bridge_type pivot; got {bridge_type}."
                    )
                elif cluster_role == "interstitial":
                    within_cluster_bridge_warnings.append(
                        f"{seg_id}: clustered interstitial at position {cluster_position or 'unknown'} "
                        "must use bridge_type none; non-none within-cluster bridges are reserved for "
                        "tension pivots."
                    )
        if (
            spoken_enforcement != "off"
            and narration_text
            and _should_check_spoken_bridge_cues(
                bridge_type,
                cluster_bridge_cadence_override=cluster_bridge_cadence_override,
                cluster_id=cluster_id,
            )
        ):
            cue_issue = _spoken_bridge_issue_message(
                bridge_type,
                narration_text,
                intro_patterns=intro_patterns,
                outro_patterns=outro_patterns,
                pivot_patterns=pivot_patterns,
            )
            if cue_issue:
                msg = (
                    f"{seg_id}: bridge_type is {bridge_type} but narration_text {cue_issue} "
                    f"(spoken_bridge_policy enforcement={spoken_enforcement})."
                )
                if spoken_enforcement == "error":
                    errors.append(msg)
                else:
                    spoken_bridge_warnings.append(msg)
        script_intent = str(script_behavioral_intents.get(seg_id) or "").strip()
        manifest_intent = str(segment.get("behavioral_intent") or "").strip()
        if script_intent and manifest_intent and script_intent != manifest_intent:
            segments_with_behavioral_intent_mismatch.append(seg_id)
        if not script_intent and not manifest_intent:
            segments_missing_behavioral_intent.append(seg_id)
        effective_intent = manifest_intent or script_intent
        master_behavioral_intent = str(segment.get("master_behavioral_intent") or "").strip()
        if cluster_id:
            cluster_records_by_id.setdefault(cluster_id, []).append(
                {
                    "seg_id": seg_id,
                    "slide_id": slide_id,
                    "card_number": card_number,
                    "cluster_role": cluster_role,
                    "cluster_position": cluster_position,
                    "narration_text": narration_text,
                    "effective_intent": effective_intent,
                    "master_behavioral_intent": master_behavioral_intent,
                    "source_ref": gary_slide_source_ref_by_id.get(slide_id, ""),
                }
            )

        if (
            isinstance(card_number, int)
            and card_number in runtime_targets_by_card
            and target_wpm
            and narration_text
        ):
            target_seconds = runtime_targets_by_card[card_number]
            expected_words = target_seconds * target_wpm / 60.0
            lower_bound = expected_words * 0.8
            upper_bound = expected_words * 1.2
            if words < lower_bound or words > upper_bound:
                runtime_budget_warnings.append(
                    f"{seg_id}: narration word count {words} falls outside the soft runtime band "
                    f"for slide {card_number} ({target_seconds:.1f}s at {target_wpm:.0f} WPM -> "
                    f"{lower_bound:.0f}-{upper_bound:.0f} words)."
                )

        should_validate_runtime_fields = bool(required_runtime_fields) and (
            (isinstance(card_number, int) and card_number in runtime_targets_by_card)
            or any(
                segment.get(field_name) not in (None, "")
                for field_name in (
                    "timing_role",
                    "content_density",
                    "visual_detail_load",
                    "duration_rationale",
                    "bridge_type",
                    "onset_delay",
                    "dwell",
                    "cluster_gap",
                    "transition_buffer",
                )
            )
        )
        if should_validate_runtime_fields:
            field_values = {
                "timing_role": str(segment.get("timing_role") or "").strip(),
                "content_density": str(segment.get("content_density") or "").strip(),
                "visual_detail_load": str(segment.get("visual_detail_load") or "").strip(),
                "duration_rationale": str(segment.get("duration_rationale") or "").strip(),
                "bridge_type": str(segment.get("bridge_type") or "").strip().lower(),
                "onset_delay": segment.get("onset_delay"),
                "dwell": segment.get("dwell"),
                "cluster_gap": segment.get("cluster_gap"),
                "transition_buffer": segment.get("transition_buffer"),
            }
            missing_fields: list[str] = []
            for field_name in required_runtime_fields:
                raw_value = field_values.get(field_name)
                if field_name in {"onset_delay", "dwell", "cluster_gap", "transition_buffer"}:
                    # Backward-compat default: absent timing buffers behave as 0.0.
                    # We only enforce validity when an explicit value is provided.
                    continue
                elif not raw_value:
                    missing_fields.append(field_name)
            for float_field in ("onset_delay", "dwell", "cluster_gap", "transition_buffer"):
                if float_field not in required_runtime_fields:
                    continue
                raw_value = field_values.get(float_field)
                if raw_value in (None, ""):
                    continue
                try:
                    parsed_value = float(raw_value)
                except (TypeError, ValueError):
                    missing_fields.append(f"{float_field}(float)")
                    continue
                if parsed_value < 0:
                    missing_fields.append(f"{float_field}(>=0)")
            if (
                field_values["timing_role"]
                and allowed_timing_roles
                and field_values["timing_role"] not in allowed_timing_roles
            ):
                missing_fields.append("timing_role(valid)")
            if (
                field_values["content_density"]
                and allowed_density_levels
                and field_values["content_density"] not in allowed_density_levels
            ):
                missing_fields.append("content_density(valid)")
            if (
                field_values["visual_detail_load"]
                and allowed_density_levels
                and field_values["visual_detail_load"] not in allowed_density_levels
            ):
                missing_fields.append("visual_detail_load(valid)")
            if (
                field_values["bridge_type"]
                and allowed_bridge_types
                and field_values["bridge_type"] not in allowed_bridge_types
            ):
                missing_fields.append("bridge_type(valid)")
            if missing_fields:
                missing_runtime_rationale_fields.append(
                    f"{seg_id}: missing or invalid runtime rationale fields: {', '.join(missing_fields)}."
                )

            rationale = field_values["duration_rationale"]
            if rationale and dimension_keywords:
                dimension_hits = _rationale_dimension_hits(
                    rationale,
                    dimension_keywords=dimension_keywords,
                )
                if len(dimension_hits) < 2:
                    weak_runtime_rationales.append(
                        f"{seg_id}: duration_rationale should reference at least two runtime dimensions "
                        f"(purpose, density, visual burden); detected {', '.join(sorted(dimension_hits)) or 'none'}."
                    )

        refs = segment.get("visual_references", [])
        valid_visual_cue_found = False
        if isinstance(refs, list):
            for ref in refs:
                if not isinstance(ref, dict):
                    continue
                cue = str(ref.get("narration_cue") or "").strip()
                source = str(ref.get("perception_source") or "").strip()
                element = str(ref.get("element") or "").strip()
                if not cue:
                    continue
                if cue not in narration_text:
                    continue
                if not source or source not in perception_slide_ids:
                    continue
                available_elements = perception_elements_by_slide.get(source, set())
                if available_elements and element and element not in available_elements:
                    continue
                valid_visual_cue_found = True
                break
        if not isinstance(refs, list) or not refs or not valid_visual_cue_found:
            segments_missing_visual_narration_cue.append(seg_id)
        elif slide_id:
            # Only classify as traceable once a cue exists and the slide identity is known.
            trace_sources = {
                str(ref.get("perception_source") or "").strip()
                for ref in refs
                if isinstance(ref, dict) and str(ref.get("narration_cue") or "").strip()
            }
            if not trace_sources or slide_id not in trace_sources:
                segments_with_untraceable_visual_cues.append(seg_id)

        motion_type = str(segment.get("motion_type") or "static").strip().lower() or "static"
        if motion_type != "static":
            motion_segments.append(segment)

            # Heuristic: motion-first narration check for video segments.
            # Video segments should reference dynamic/temporal visual content,
            # not just describe the static slide layout.
            visual_mode = str(segment.get("visual_mode") or "").strip().lower()
            if visual_mode == "video" and narration_text:
                _motion_keywords = (
                    "motion", "movement", "moves", "moving", "animation", "animated",
                    "transition", "change", "changes", "changing", "process",
                    "progresses", "progression", "sequence", "flow", "flows",
                    "shifts", "transforms", "evolves", "unfolds", "action",
                    "plays", "clip", "video", "dynamic",
                )
                narration_lower = narration_text.lower()
                if not any(kw in narration_lower for kw in _motion_keywords):
                    motion_segments_with_static_narration_hint.append(seg_id)

            approved_assignment = motion_plan_by_slide_id.get(slide_id, {})
            approved_asset = str(approved_assignment.get("motion_asset_path") or "").strip()
            segment_asset = str(segment.get("motion_asset_path") or "").strip()
            segment_status = str(segment.get("motion_status") or "").strip().lower()
            approved_status = str(approved_assignment.get("motion_status") or "").strip().lower()
            segment_visual_file = str(segment.get("visual_file") or "").strip()
            approved_slide_png = str(gary_slide_path_by_id.get(slide_id) or "").strip()

            canonical_visual_ok = bool(
                approved_slide_png
                and segment_visual_file
                and _normalize_path_string(segment_visual_file, bundle_dir=bundle_dir)
                == _normalize_path_string(approved_slide_png, bundle_dir=bundle_dir)
            )
            if not canonical_visual_ok:
                motion_segments_with_noncanonical_visual_file.append(seg_id)

            approved_ok = bool(
                approved_asset
                and segment_asset
                and segment_status == "approved"
                and approved_status == "approved"
                and _normalize_path_string(segment_asset, bundle_dir=bundle_dir)
                == _normalize_path_string(approved_asset, bundle_dir=bundle_dir)
            )
            if not approved_ok:
                motion_segments_with_unapproved_asset_binding.append(seg_id)
                continue

            confirmed_paths = motion_confirmations.get(slide_id, set())
            expected_path = _normalize_path_string(approved_asset, bundle_dir=bundle_dir)
            if expected_path not in confirmed_paths:
                motion_segments_missing_perception_confirmation.append(seg_id)

    missing_manifest_for_slide_ids = [
        slide_id for slide_id in authorized_slide_ids if slide_id not in manifest_slide_id_set
    ]
    # Interstitial slide_ids are valid but not in the authorized storyboard — exclude from unknown check
    unknown_manifest_slide_ids = sorted(
        manifest_slide_id_set - set(authorized_slide_ids) - interstitial_slide_ids
    )

    details["missing_manifest_for_slide_ids"] = missing_manifest_for_slide_ids
    details["unknown_manifest_slide_ids"] = unknown_manifest_slide_ids
    details["segments_missing_narration_text"] = sorted(set(segments_missing_narration_text))
    details["segments_missing_visual_narration_cue"] = sorted(set(segments_missing_visual_narration_cue))
    details["segments_with_untraceable_visual_cues"] = sorted(set(segments_with_untraceable_visual_cues))
    details["segments_with_forbidden_meta_slide_language"] = sorted(
        set(segments_with_forbidden_meta_slide_language)
    )
    details["segments_with_behavioral_intent_mismatch"] = sorted(
        set(segments_with_behavioral_intent_mismatch)
    )
    segments_with_master_behavioral_intent_violation: list[str] = []
    cluster_behavioral_intent_violations_by_cluster: dict[str, list[str]] = {}
    for cluster_id, records in cluster_records_by_id.items():
        head_record = next(
            (record for record in records if record["cluster_role"] == "head"),
            None,
        )
        cluster_master_behavioral_intent = ""
        if head_record is not None:
            cluster_master_behavioral_intent = str(
                head_record["master_behavioral_intent"] or ""
            ).strip()
        if not cluster_master_behavioral_intent:
            cluster_master_behavioral_intent = next(
                (
                    str(record["master_behavioral_intent"] or "").strip()
                    for record in records
                    if str(record["master_behavioral_intent"] or "").strip()
                ),
                "",
            )
        violations = sorted(
            {
                f"{record['seg_id']}({record['effective_intent']}->{cluster_master_behavioral_intent})"
                for record in records
                if record["cluster_role"] == "interstitial"
                and record["effective_intent"]
                and cluster_master_behavioral_intent
                and not _behavioral_intent_serves_master(
                    cluster_master_behavioral_intent,
                    record["effective_intent"],
                )
            }
        )
        if any(record["cluster_role"] == "interstitial" for record in records) and not cluster_master_behavioral_intent:
            violations.append(f"{cluster_id}(missing master_behavioral_intent)")
        if violations:
            cluster_behavioral_intent_violations_by_cluster[cluster_id] = violations
            segments_with_master_behavioral_intent_violation.extend(violations)
    details["segments_with_master_behavioral_intent_violation"] = sorted(
        set(segments_with_master_behavioral_intent_violation)
    )
    details["cluster_behavioral_intent_violations_by_cluster"] = cluster_behavioral_intent_violations_by_cluster
    details["segments_missing_behavioral_intent"] = sorted(
        set(segments_missing_behavioral_intent)
    )
    details["motion_segments_with_static_narration_hint"] = sorted(
        set(motion_segments_with_static_narration_hint)
    )
    details["motion_segments_missing_perception_confirmation"] = sorted(
        set(motion_segments_missing_perception_confirmation)
    )
    details["motion_segments_with_unapproved_asset_binding"] = sorted(
        set(motion_segments_with_unapproved_asset_binding)
    )
    details["motion_segments_with_noncanonical_visual_file"] = sorted(
        set(motion_segments_with_noncanonical_visual_file)
    )
    details["runtime_budget_warnings"] = sorted(set(runtime_budget_warnings))
    details["cluster_word_range_warnings"] = sorted(set(cluster_word_range_warnings))
    details["missing_runtime_rationale_fields"] = sorted(set(missing_runtime_rationale_fields))
    details["weak_runtime_rationales"] = sorted(set(weak_runtime_rationales))
    bridge_cadence_warnings: list[str] = []
    cluster_boundary_warnings: list[str] = []
    if bridge_cadence_enabled and ordered_slide_records and (bridge_minutes > 0 or bridge_slides > 0):
        slides_since_bridge = 0
        seconds_since_bridge = 0.0
        previous_record: dict[str, Any] | None = None
        for index, record in enumerate(ordered_slide_records, start=1):
            bridge_type = str(record.get("bridge_type") or "none").strip().lower() or "none"
            is_cluster_boundary = _is_cluster_boundary_transition(previous_record, record)
            record_is_clustered = bool(str(record.get("cluster_id") or "").strip())
            if (
                cluster_bridge_cadence_override
                and is_cluster_boundary
                and bridge_type != "cluster_boundary"
            ):
                cluster_boundary_warnings.append(
                    f"{record.get('seg_id')}: cluster boundary transition should use bridge_type "
                    "cluster_boundary when cluster_bridge_cadence_override=true."
                )
            if index > 1:
                slides_since_bridge += 1
                seconds_since_bridge += float(record.get("duration_estimate_seconds") or 0.0)
            slides_exceeded = bool(bridge_slides > 0 and slides_since_bridge >= bridge_slides)
            minutes_exceeded = bool(bridge_minutes > 0 and seconds_since_bridge >= bridge_minutes * 60.0)
            if _bridge_satisfies_cadence(
                bridge_type,
                accepted_bridge_types=accepted_bridge_types,
                cluster_bridge_cadence_override=cluster_bridge_cadence_override,
                record_is_clustered=record_is_clustered,
                is_cluster_boundary=is_cluster_boundary,
                cluster_role=str(record.get("cluster_role") or "").strip().lower() or None,
                fallback_due=slides_exceeded or minutes_exceeded,
            ):
                slides_since_bridge = 0
                seconds_since_bridge = 0.0
            else:
                if slides_exceeded or minutes_exceeded:
                    bridge_cadence_warnings.append(
                        f"{record.get('seg_id')}: explicit intro/outro bridge cadence exceeded before this slide "
                        f"({slides_since_bridge} slides, {seconds_since_bridge/60.0:.1f} estimated minutes without a marked bridge; "
                        f"target <= {bridge_slides} slides or <= {bridge_minutes:.1f} minutes)."
                    )
                    slides_since_bridge = 0
                    seconds_since_bridge = 0.0
            previous_record = record
    details["bridge_cadence_warnings"] = sorted(set(bridge_cadence_warnings))
    details["within_cluster_bridge_warnings"] = sorted(set(within_cluster_bridge_warnings))
    details["cluster_boundary_warnings"] = sorted(set(cluster_boundary_warnings))
    details["spoken_bridge_warnings"] = sorted(set(spoken_bridge_warnings))

    cluster_new_concept_violations: list[str] = []
    cluster_arc_integrity_violations: list[str] = []
    for cluster_id, records in cluster_records_by_id.items():
        ordered_records = sorted(
            records,
            key=lambda record: (
                record["card_number"] if isinstance(record["card_number"], int) else 10**9,
                record["seg_id"],
            ),
        )
        head_record = next(
            (record for record in ordered_records if record["cluster_role"] == "head"),
            None,
        )
        if head_record is None:
            cluster_arc_integrity_violations.append(
                f"{cluster_id}: cluster is missing a head segment."
            )
            continue

        head_concepts = _extract_concept_tokens(head_record["narration_text"])
        head_concepts.update(
            _extract_concept_tokens(
                _load_source_ref_excerpt(head_record["source_ref"], bundle_dir=bundle_dir)
            )
        )
        for record in ordered_records:
            if record["cluster_role"] != "interstitial":
                continue
            introduced = sorted(
                token
                for token in _extract_concept_tokens(record["narration_text"])
                if token not in head_concepts
            )
            if introduced:
                cluster_new_concept_violations.append(
                    f"{record['seg_id']}: new concept(s) outside head scope: {', '.join(introduced[:6])}"
                )

        positions = [
            str(record["cluster_position"] or "").strip().lower()
            for record in ordered_records
            if str(record["cluster_position"] or "").strip()
        ]
        if positions:
            if positions[0] != "establish":
                cluster_arc_integrity_violations.append(
                    f"{cluster_id}: arc integrity failure - first cluster position must be establish, got {positions[0]}."
                )
            for previous, current in zip(positions, positions[1:], strict=False):
                if _CLUSTER_ARC_POSITION_ORDER.get(current, -1) < _CLUSTER_ARC_POSITION_ORDER.get(previous, -1):
                    cluster_arc_integrity_violations.append(
                        f"{cluster_id}: arc integrity failure - disordered cluster positions {previous} -> {current}."
                    )
                    break
            resolve_index = next(
                (index for index, position in enumerate(positions) if position == "resolve"),
                None,
            )
            if resolve_index is not None:
                prior_positions = positions[:resolve_index]
                if not any(position in {"tension", "develop"} for position in prior_positions):
                    cluster_arc_integrity_violations.append(
                        f"{cluster_id}: arc integrity failure - resolve appears without a middle beat before it."
                    )
            resolve_record = next(
                (record for record in reversed(ordered_records) if record["cluster_position"] == "resolve"),
                None,
            )
            if resolve_record is not None:
                establish_concepts = _extract_concept_tokens(head_record["narration_text"])
                resolve_concepts = _extract_concept_tokens(resolve_record["narration_text"])
                if establish_concepts and resolve_concepts and not (establish_concepts & resolve_concepts):
                    cluster_arc_integrity_violations.append(
                        f"{cluster_id}: arc integrity failure - resolve segment {resolve_record['seg_id']} lacks a callback to establish concepts."
                    )
    details["cluster_new_concept_violations"] = sorted(set(cluster_new_concept_violations))
    details["cluster_arc_integrity_violations"] = sorted(set(cluster_arc_integrity_violations))
    envelope_artifacts_by_key = {
        _artifact_identity_key(item): _normalize_artifact_for_compare(item)
        for item in perception_artifacts
        if isinstance(item, dict)
    }
    standalone_artifacts_by_key = {
        _artifact_identity_key(item): _normalize_artifact_for_compare(item)
        for item in standalone_perception_artifacts
        if isinstance(item, dict)
    }
    mismatch_keys = sorted(
        key
        for key in set(envelope_artifacts_by_key) | set(standalone_artifacts_by_key)
        if envelope_artifacts_by_key.get(key) != standalone_artifacts_by_key.get(key)
    )
    details["perception_artifact_mismatches"] = mismatch_keys

    if interstitials_missing_cluster_id:
        errors.append(
            "interstitial segment(s) missing required cluster_id: "
            + ", ".join(sorted(set(interstitials_missing_cluster_id)))
        )
    if interstitials_missing_timing_role:
        errors.append(
            "interstitial segment(s) missing required timing_role: "
            + ", ".join(sorted(set(interstitials_missing_timing_role)))
        )

    if missing_manifest_for_slide_ids:
        errors.append(
            "segment-manifest.yaml missing at least one segment for slide_id(s): "
            + ", ".join(missing_manifest_for_slide_ids)
        )
    if unknown_manifest_slide_ids:
        errors.append(
            "segment-manifest.yaml references unknown slide_id(s): "
            + ", ".join(unknown_manifest_slide_ids)
        )
    if segments_missing_narration_text:
        errors.append(
            "segment-manifest.yaml has segment(s) with empty narration_text: "
            + ", ".join(sorted(set(segments_missing_narration_text)))
        )
    if segments_missing_visual_narration_cue:
        errors.append(
            "segment-manifest.yaml has segment(s) without a non-empty visual narration_cue tied to perception and present in narration_text: "
            + ", ".join(sorted(set(segments_missing_visual_narration_cue)))
        )
    if segments_with_untraceable_visual_cues:
        errors.append(
            "segment-manifest.yaml has segment(s) with visual narration cues that do not trace to the segment's own slide_id perception lineage: "
            + ", ".join(sorted(set(segments_with_untraceable_visual_cues)))
        )
    if segments_with_forbidden_meta_slide_language:
        errors.append(
            "segment-manifest.yaml has segment(s) using forbidden meta slide-language while audience-directed narration is required: "
            + ", ".join(sorted(set(segments_with_forbidden_meta_slide_language)))
        )
    if details["script_segments_with_forbidden_meta_slide_language"]:
        errors.append(
            "narration-script.md has segment(s) using forbidden meta slide-language while audience-directed narration is required: "
            + ", ".join(details["script_segments_with_forbidden_meta_slide_language"])
        )
    if details["segments_with_behavioral_intent_mismatch"]:
        errors.append(
            "narration-script.md and segment-manifest.yaml disagree on behavioral_intent for segment(s): "
            + ", ".join(details["segments_with_behavioral_intent_mismatch"])
        )
    if details["segments_with_master_behavioral_intent_violation"]:
        errors.append(
            "clustered interstitial behavioral_intent validation failed against master_behavioral_intent: "
            + ", ".join(details["segments_with_master_behavioral_intent_violation"])
        )
    if details["cluster_new_concept_violations"]:
        errors.append(
            "clustered interstitial narration introduces new concept(s) outside head scope: "
            + ", ".join(details["cluster_new_concept_violations"])
        )
    if details["cluster_arc_integrity_violations"]:
        errors.append(
            "cluster arc integrity failures detected: "
            + ", ".join(details["cluster_arc_integrity_violations"])
        )
    if details["segments_missing_behavioral_intent"]:
        warnings.append(
            "segment(s) have no behavioral_intent in either narration-script.md or segment-manifest.yaml: "
            + ", ".join(details["segments_missing_behavioral_intent"])
        )
    if details["motion_segments_with_static_narration_hint"]:
        warnings.append(
            "video segment(s) may lack motion-first narration — narration does not reference dynamic/temporal visual content: "
            + ", ".join(details["motion_segments_with_static_narration_hint"])
        )
    if mismatch_keys:
        errors.append(
            "perception-artifacts.json must match the envelope perception_artifacts for artifact key(s): "
            + ", ".join(mismatch_keys)
        )
    if motion_segments and not isinstance(payload.get("motion_perception_artifacts"), list):
        errors.append(
            "motion-enabled Pass 2 requires motion_perception_artifacts aligned to non-static segments"
        )
    if motion_segments_with_unapproved_asset_binding:
        errors.append(
            "motion segment(s) are not bound to the approved motion asset from motion_plan.yaml: "
            + ", ".join(sorted(set(motion_segments_with_unapproved_asset_binding)))
        )
    if motion_segments_with_noncanonical_visual_file:
        errors.append(
            "motion segment(s) must keep visual_file bound to the approved Gary/Gamma still instead of the motion clip: "
            + ", ".join(sorted(set(motion_segments_with_noncanonical_visual_file)))
        )
    if motion_segments_missing_perception_confirmation:
        errors.append(
            "motion segment(s) are missing motion perception confirmation for the approved asset: "
            + ", ".join(sorted(set(motion_segments_missing_perception_confirmation)))
        )

    warnings.extend(details["runtime_budget_warnings"])
    warnings.extend(details["cluster_word_range_warnings"])
    warnings.extend(details["missing_runtime_rationale_fields"])
    warnings.extend(details["weak_runtime_rationales"])
    warnings.extend(details["bridge_cadence_warnings"])
    warnings.extend(details["within_cluster_bridge_warnings"])
    warnings.extend(details["cluster_boundary_warnings"])
    warnings.extend(details["spoken_bridge_warnings"])

    if runtime_policy_strict:
        runtime_policy_violations = (
            details["runtime_budget_warnings"]
            + details["cluster_word_range_warnings"]
            + details["missing_runtime_rationale_fields"]
            + details["weak_runtime_rationales"]
            + details["bridge_cadence_warnings"]
            + details["within_cluster_bridge_warnings"]
            + details["cluster_boundary_warnings"]
        )
        if spoken_enforcement == "warn":
            runtime_policy_violations += details["spoken_bridge_warnings"]
        errors.extend(
            [
                f"runtime_policy_violation: {violation}"
                for violation in runtime_policy_violations
            ]
        )

    return {"errors": errors, "warnings": warnings, "details": details}


def validate_irene_pass2_handoff(
    payload: dict[str, Any],
    *,
    expected_artifact_hint: str | None = None,
    envelope_path: Path | None = None,
    runtime_policy_strict: bool = True,
) -> dict[str, Any]:
    """Validate required Pass 2 inputs and sequencing integrity."""
    missing_fields = [key for key in REQUIRED_PASS2_FIELDS if key not in payload]
    errors: list[str] = []

    if missing_fields:
        errors.append(
            "Missing required Pass 2 field(s): " + ", ".join(missing_fields)
        )

    gary = payload.get("gary_slide_output", [])
    perception = payload.get("perception_artifacts", [])

    if gary is not None and not isinstance(gary, list):
        errors.append("gary_slide_output must be an array")
        gary = []
    if perception is not None and not isinstance(perception, list):
        errors.append("perception_artifacts must be an array")
        perception = []

    card_sequence = [item.get("card_number") for item in gary if isinstance(item, dict)]
    strictly_ascending = all(
        isinstance(n, int) and isinstance(m, int) and n < m
        for n, m in zip(card_sequence, card_sequence[1:], strict=False)
    )
    contiguous_from_one = (
        bool(card_sequence)
        and all(isinstance(n, int) for n in card_sequence)
        and card_sequence == list(range(1, len(card_sequence) + 1))
    )

    missing_file_path_for: list[str] = []
    missing_source_ref_for: list[str] = []
    non_png_file_path_for: list[str] = []
    remote_file_path_for: list[str] = []
    missing_local_png_for: list[str] = []
    png_card_mismatch_for: list[str] = []
    gary_slide_path_by_id: dict[str, str] = {}
    gary_slide_source_ref_by_id: dict[str, str] = {}
    bundle_dir = _bundle_dir_from_inputs(payload, envelope_path=envelope_path)
    for item in gary:
        if not isinstance(item, dict):
            continue
        slide_label = str(item.get("slide_id") or item.get("card_number") or "unknown")
        file_path = item.get("file_path")
        source_ref = item.get("source_ref")
        card_number = item.get("card_number")
        if not isinstance(file_path, str) or not file_path.strip():
            missing_file_path_for.append(slide_label)
        else:
            normalized_path = file_path.strip()
            if _is_remote_http_ref(normalized_path):
                remote_file_path_for.append(slide_label)
            if Path(normalized_path).suffix.lower() != ".png":
                non_png_file_path_for.append(slide_label)
            if envelope_path is not None and _resolve_existing_local_path(
                normalized_path,
                bundle_dir=bundle_dir,
            ) is None:
                missing_local_png_for.append(slide_label)

            # Check PNG filename number matches card_number
            if isinstance(card_number, int) and card_number > 0:
                filename = Path(normalized_path).name
                if filename.startswith("slide_") and filename.endswith(".png"):
                    num_str = filename[6:-4]  # Remove "slide_" and ".png"
                    try:
                        filename_number = int(num_str)
                        if filename_number != card_number:
                            png_card_mismatch_for.append(slide_label)
                    except ValueError:
                        pass  # Non-numeric, skip check

            slide_id = item.get("slide_id")
            if isinstance(slide_id, str) and slide_id.strip():
                gary_slide_path_by_id[slide_id.strip()] = normalized_path
                if isinstance(source_ref, str) and source_ref.strip():
                    gary_slide_source_ref_by_id[slide_id.strip()] = source_ref.strip()
        if not isinstance(source_ref, str) or not source_ref.strip():
            missing_source_ref_for.append(slide_label)

    if not contiguous_from_one:
        errors.append(
            "gary_slide_output card_number sequence must be contiguous and start at 1 (1..N)"
        )
    if missing_file_path_for:
        errors.append(
            "gary_slide_output missing non-empty file_path for: " + ", ".join(missing_file_path_for)
        )
    if remote_file_path_for:
        errors.append(
            "gary_slide_output file_path must reference local downloaded PNGs; remote path found for: "
            + ", ".join(remote_file_path_for)
        )
    if non_png_file_path_for:
        errors.append(
            "gary_slide_output file_path must end with .png for: "
            + ", ".join(non_png_file_path_for)
        )
    if missing_local_png_for:
        errors.append(
            "gary_slide_output file_path does not exist on disk for: "
            + ", ".join(missing_local_png_for)
        )
    if png_card_mismatch_for:
        errors.append(
            "gary_slide_output card_number does not match slide_XX.png filename for: "
            + ", ".join(png_card_mismatch_for)
        )
    if missing_source_ref_for:
        errors.append(
            "gary_slide_output missing non-empty source_ref for: "
            + ", ".join(missing_source_ref_for)
        )

    gary_slide_ids = [
        str(item.get("slide_id")).strip()
        for item in gary
        if isinstance(item, dict) and item.get("slide_id")
    ]
    perception_slide_ids = {
        str(item.get("slide_id"))
        for item in perception
        if isinstance(item, dict) and item.get("slide_id")
    }

    missing_perception_for = sorted(set(gary_slide_ids) - perception_slide_ids)
    if missing_perception_for:
        errors.append(
            "perception_artifacts missing slide_id(s): " + ", ".join(missing_perception_for)
        )

    missing_source_image_path_for: list[str] = []
    mismatched_source_image_path_for: list[str] = []
    for item in perception:
        if not isinstance(item, dict):
            continue
        slide_id = str(item.get("slide_id") or "").strip()
        if not slide_id:
            continue
        source_image_path = item.get("source_image_path")
        if not isinstance(source_image_path, str) or not source_image_path.strip():
            missing_source_image_path_for.append(slide_id)
            continue
        normalized_source_path = source_image_path.strip()
        expected_path = gary_slide_path_by_id.get(slide_id)
        if expected_path is not None and normalized_source_path != expected_path:
            mismatched_source_image_path_for.append(slide_id)

    if missing_source_image_path_for:
        errors.append(
            "perception_artifacts missing non-empty source_image_path for slide_id(s): "
            + ", ".join(sorted(set(missing_source_image_path_for)))
        )
    if mismatched_source_image_path_for:
        errors.append(
            "perception_artifacts source_image_path must match gary_slide_output.file_path for slide_id(s): "
            + ", ".join(sorted(set(mismatched_source_image_path_for)))
        )

    bundle_checks = _validate_bundle_pass2_outputs(
        payload,
        bundle_dir=bundle_dir,
        gary_slide_ids=gary_slide_ids,
        gary_slide_path_by_id=gary_slide_path_by_id,
        gary_slide_source_ref_by_id=gary_slide_source_ref_by_id,
        perception_artifacts=[item for item in perception if isinstance(item, dict)],
        runtime_policy_strict=runtime_policy_strict,
    )
    errors.extend(bundle_checks["errors"])
    warnings = bundle_checks.get("warnings", [])

    remediation_hint = (
        "Perception artifacts are emitted inline during Pass 2. "
        "If missing, re-run Irene on the affected slides to regenerate perception side-effects. "
        "Narration grounding must use local post-integration downloaded PNGs from gary_slide_output. "
        "Pass 2 must also produce a complete segment-manifest.yaml with non-empty narration_text "
        "and traceable visual narration cues for every authorized slide."
    )
    if expected_artifact_hint:
        remediation_hint += f" (expected location hint: {expected_artifact_hint})"

    status = "pass" if not errors else "fail"
    return {
        "status": status,
        "runtime_policy_mode": "strict" if runtime_policy_strict else "advisory",
        "required_fields": list(REQUIRED_PASS2_FIELDS),
        "missing_fields": missing_fields,
        "errors": errors,
        "warnings": warnings,
        "card_sequence": card_sequence,
        "order_check": {
            "strictly_ascending": strictly_ascending,
            "contiguous_from_one": contiguous_from_one,
        },
        "consistency": {
            "gary_slide_count": len(gary),
            "perception_count": len(perception),
            "missing_perception_for": missing_perception_for,
            "missing_file_path_for": missing_file_path_for,
            "missing_source_ref_for": missing_source_ref_for,
            "missing_source_image_path_for": sorted(set(missing_source_image_path_for)),
            "mismatched_source_image_path_for": sorted(set(mismatched_source_image_path_for)),
            "non_png_file_path_for": non_png_file_path_for,
            "remote_file_path_for": remote_file_path_for,
            "missing_local_png_for": missing_local_png_for,
        },
        "pass2_outputs": bundle_checks["details"],
        "remediation_hint": remediation_hint,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Irene Pass 2 handoff envelope")
    parser.add_argument(
        "--envelope",
        type=Path,
        required=True,
        help="Path to pass2 envelope JSON/YAML",
    )
    parser.add_argument(
        "--expected-artifact-hint",
        type=str,
        default=None,
        help="Optional path hint shown in remediation guidance",
    )
    parser.add_argument(
        "--runtime-policy-advisory",
        action="store_true",
        help="Keep runtime/script-policy findings as warnings instead of hard failures.",
    )
    args = parser.parse_args()

    try:
        payload = _load_payload(args.envelope)
        result = validate_irene_pass2_handoff(
            payload,
            expected_artifact_hint=args.expected_artifact_hint,
            envelope_path=args.envelope,
            runtime_policy_strict=not args.runtime_policy_advisory,
        )
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "pass" else 1
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "fail",
                    "errors": [f"validator_exception: {type(exc).__name__}: {exc}"],
                },
                indent=2,
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
