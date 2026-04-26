# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Agent-level ElevenLabs operations wrapper.

Bridges the Voice Director's decisions and the ElevenLabs API client layer.
Handles style-guide loading, VTT generation, pronunciation dictionary authoring,
and structured result formatting for Marcus-mediated workflows.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import xml.sax.saxutils as xml_utils
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.api_clients.elevenlabs_client import ElevenLabsClient
from scripts.utilities.ffmpeg import resolve_ffmpeg_binary

load_dotenv(PROJECT_ROOT / ".env")

try:
    FFMPEG_BINARY = resolve_ffmpeg_binary()
except Exception as e:
    raise RuntimeError(f"ffmpeg not available: {e}")

STYLE_GUIDE_PATH = PROJECT_ROOT / "state" / "config" / "style_guide.yaml"
VOICE_PROFILES_PATH = (
    PROJECT_ROOT / "state" / "config" / "elevenlabs-voice-profiles.yaml"
)
STAGING_DIR = PROJECT_ROOT / "course-content" / "staging"
VOICE_PREVIEW_MODES = {
    "continuity_preview",
    "default_plus_alternatives",
    "description_driven_search",
}
VOICE_STOPWORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "by",
    "for",
    "from",
    "in",
    "into",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}
VOICE_PENALTY_TERMS = {
    "anime",
    "cartoon",
    "character",
    "child",
    "comedy",
    "extreme",
    "fantasy",
    "game",
    "gaming",
    "parody",
    "silly",
}
VOICE_CLARITY_HINTS = {
    "articulate",
    "authoritative",
    "calm",
    "clear",
    "clinical",
    "conversational",
    "credible",
    "deliberate",
    "educational",
    "measured",
    "natural",
    "narration",
    "narrator",
    "professional",
    "warm",
}
DEFAULT_AUDIO_BUFFER_SECONDS = 1.5
DEFAULT_PACE_VARIABILITY = 0.05
MIN_ELEVENLABS_SPEED = 0.7
MAX_ELEVENLABS_SPEED = 1.2


def load_style_guide_elevenlabs() -> dict[str, Any]:
    """Load ElevenLabs defaults from the mutable style guide."""
    if not STYLE_GUIDE_PATH.exists():
        return {}
    data = yaml.safe_load(STYLE_GUIDE_PATH.read_text(encoding="utf-8")) or {}
    return data.get("tool_parameters", {}).get("elevenlabs", {})


def load_voice_preview_profiles() -> dict[str, Any]:
    """Load governed voice preview profiles and keyword overrides."""
    if not VOICE_PROFILES_PATH.exists():
        return {}
    return yaml.safe_load(VOICE_PROFILES_PATH.read_text(encoding="utf-8")) or {}


def merge_parameters(
    style_defaults: dict[str, Any],
    overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Merge style-guide defaults with per-request overrides."""
    merged: dict[str, Any] = {}
    for source in [style_defaults, overrides or {}]:
        for key, value in source.items():
            if value is not None and value != "":
                merged[key] = value
    return merged


def _coerce_float(
    value: Any | None,
    *,
    field_name: str,
) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a number.") from exc


def _coerce_bool(value: Any | None, *, field_name: str) -> bool | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes", "on"}:
        return True
    if normalized in {"false", "0", "no", "off"}:
        return False
    raise ValueError(f"{field_name} must be a boolean.")


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _resolve_voice_direction(
    merged: dict[str, Any],
) -> dict[str, Any]:
    """Resolve raw ElevenLabs settings plus pipeline-level abstractions.

    `emotional_variability` is a pipeline abstraction that maps inversely to
    ElevenLabs stability when stability is not explicitly set.
    """

    stability = _coerce_float(merged.get("stability"), field_name="stability")
    similarity_boost = _coerce_float(
        merged.get("similarity_boost"),
        field_name="similarity_boost",
    )
    style = _coerce_float(merged.get("style"), field_name="style")
    speed = _coerce_float(merged.get("speed"), field_name="speed")
    use_speaker_boost = _coerce_bool(
        merged.get("use_speaker_boost"),
        field_name="use_speaker_boost",
    )
    emotional_variability = _coerce_float(
        merged.get("emotional_variability"),
        field_name="emotional_variability",
    )
    pace_variability = _coerce_float(
        merged.get("pace_variability"),
        field_name="pace_variability",
    )

    if emotional_variability is not None:
        emotional_variability = _clamp(emotional_variability, 0.0, 1.0)
    if stability is None and emotional_variability is not None:
        stability = 1.0 - emotional_variability
    if speed is not None:
        speed = _clamp(speed, MIN_ELEVENLABS_SPEED, MAX_ELEVENLABS_SPEED)
    if pace_variability is None:
        pace_variability = DEFAULT_PACE_VARIABILITY
    pace_variability = _clamp(pace_variability, 0.0, 0.25)

    return {
        "stability": stability,
        "similarity_boost": similarity_boost,
        "style": style,
        "speed": speed,
        "use_speaker_boost": use_speaker_boost,
        "emotional_variability": emotional_variability,
        "pace_variability": pace_variability,
    }


def _coerce_audio_buffer_seconds(value: Any | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        resolved = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("audio_buffer_seconds must be a number.") from exc
    if resolved < 0:
        raise ValueError("audio_buffer_seconds must be non-negative.")
    return resolved


def _resolve_audio_buffer_seconds(
    value: Any | None,
    *,
    style_defaults: dict[str, Any] | None = None,
    fallback: float = DEFAULT_AUDIO_BUFFER_SECONDS,
) -> float:
    resolved = _coerce_audio_buffer_seconds(value)
    if resolved is not None:
        return resolved
    style_defaults = style_defaults or {}
    resolved = _coerce_audio_buffer_seconds(style_defaults.get("audio_buffer_seconds"))
    if resolved is not None:
        return resolved
    return fallback


def _merge_unique_terms(*groups: list[str] | tuple[str, ...] | set[str] | None) -> list[str]:
    """Merge string terms while preserving first-seen order."""
    merged: list[str] = []
    seen: set[str] = set()
    for group in groups:
        if not group:
            continue
        for item in group:
            normalized = str(item or "").strip().lower()
            if not normalized or normalized in seen:
                continue
            merged.append(normalized)
            seen.add(normalized)
    return merged


def _resolve_voice_preview_profile(
    *,
    style_defaults: dict[str, Any],
    presentation_attributes: dict[str, Any] | None,
    ideal_voice_description: str | None,
) -> tuple[str, dict[str, Any]]:
    """Resolve the active profile and apply description keyword overrides."""
    profiles_data = load_voice_preview_profiles()
    profiles = profiles_data.get("profiles", {})
    if not isinstance(profiles, dict) or not profiles:
        return "inline-fallback", {}

    content_type = str(
        (presentation_attributes or {}).get("content_type") or ""
    ).strip()
    selected_name = (
        str(style_defaults.get("voice_selection_profile") or "").strip()
        or str(
            (profiles_data.get("content_type_profiles") or {}).get(content_type) or ""
        ).strip()
        or str(profiles_data.get("default_profile") or "").strip()
    )
    if selected_name not in profiles:
        selected_name = str(profiles_data.get("default_profile") or "").strip()
    if selected_name not in profiles:
        selected_name = next(iter(profiles.keys()))

    resolved = {
        key: list(value) if isinstance(value, list) else value
        for key, value in dict(profiles.get(selected_name) or {}).items()
    }

    description = str(ideal_voice_description or "").strip().lower()
    overrides = profiles_data.get("description_keyword_overrides") or {}
    for keyword, patch in overrides.items():
        if not isinstance(patch, dict):
            continue
        if not re.search(rf"\b{re.escape(str(keyword).lower())}\b", description):
            continue
        for key, value in patch.items():
            if isinstance(value, list):
                resolved[key] = _merge_unique_terms(resolved.get(key), value)
            elif value is not None:
                resolved[key] = value

    return selected_name, resolved


def _sha256_file(path: str | Path) -> str:
    """Return a stable SHA-256 hex digest for a file."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json_file(path: str | Path) -> dict[str, Any]:
    """Read a JSON file from disk."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _flatten_voice_context(value: Any) -> list[str]:
    """Flatten nested voice-selection context into human-readable snippets."""
    if value is None:
        return []
    if isinstance(value, str):
        cleaned = value.strip()
        return [cleaned] if cleaned else []
    if isinstance(value, dict):
        parts: list[str] = []
        for key, nested in value.items():
            for item in _flatten_voice_context(nested):
                parts.append(f"{key} {item}")
        return parts
    if isinstance(value, (list, tuple, set)):
        parts: list[str] = []
        for nested in value:
            parts.extend(_flatten_voice_context(nested))
        return parts
    return [str(value)]


def _tokenize_voice_terms(*chunks: str) -> list[str]:
    """Tokenize voice-search text into normalized terms."""
    tokens: list[str] = []
    for chunk in chunks:
        for token in re.findall(r"[a-z0-9]+", chunk.lower()):
            if len(token) < 3 or token in VOICE_STOPWORDS:
                continue
            tokens.append(token)
    # Preserve first-seen order to keep rationales stable.
    return list(dict.fromkeys(tokens))


def _voice_preview_url(
    voice: dict[str, Any],
    *,
    preferred_language: str | None = None,
    preferred_locale: str | None = None,
) -> str:
    """Return the best catalog preview/sample URL when available."""
    verified_languages = (
        voice.get("verified_languages")
        if isinstance(voice.get("verified_languages"), list)
        else []
    )
    if preferred_locale:
        for entry in verified_languages:
            if (
                str(entry.get("locale") or "").strip().lower()
                == preferred_locale.strip().lower()
                and str(entry.get("preview_url") or "").strip()
            ):
                return str(entry["preview_url"]).strip()
    if preferred_language:
        for entry in verified_languages:
            if (
                str(entry.get("language") or "").strip().lower()
                == preferred_language.strip().lower()
                and str(entry.get("preview_url") or "").strip()
            ):
                return str(entry["preview_url"]).strip()
    for key in ("preview_url", "sample_url"):
        value = str(voice.get(key) or "").strip()
        if value:
            return value
    return ""


def _voice_labels_blob(labels: Any) -> str:
    """Flatten ElevenLabs voice labels for scoring and display."""
    if isinstance(labels, dict):
        return " ".join(str(value) for value in labels.values() if value)
    if isinstance(labels, list):
        return " ".join(str(value) for value in labels if value)
    if labels:
        return str(labels)
    return ""


def _voice_search_blob(voice: dict[str, Any]) -> str:
    """Combine voice metadata fields into a single scoring/search string."""
    fields = [
        str(voice.get("name") or ""),
        str(voice.get("description") or ""),
        str(voice.get("category") or ""),
        _voice_labels_blob(voice.get("labels")),
    ]
    return " ".join(field for field in fields if field).strip().lower()


def _build_voice_candidate(
    voice: dict[str, Any],
    *,
    desired_terms: list[str],
    context_terms: list[str],
    clarity_hints: set[str],
    penalty_terms: set[str],
    preferred_language: str | None,
    preferred_locale: str | None,
    source: str,
    source_label: str,
) -> dict[str, Any] | None:
    """Normalize a raw ElevenLabs voice into a scored preview candidate."""
    preview_url = _voice_preview_url(
        voice,
        preferred_language=preferred_language,
        preferred_locale=preferred_locale,
    )
    if not preview_url:
        return None

    voice_id = str(voice.get("voice_id") or "").strip()
    if not voice_id:
        return None

    blob = _voice_search_blob(voice)
    category = str(voice.get("category") or "").strip()
    labels = voice.get("labels") if isinstance(voice.get("labels"), dict) else {}
    matched_desired = [term for term in desired_terms if term in blob]
    matched_context = [term for term in context_terms if term in blob and term not in matched_desired]
    penalties = [term for term in penalty_terms if term in blob]
    clarity_hits = [term for term in clarity_hints if term in blob]

    score = 30
    if category.lower() in {"premade", "professional", "generated"}:
        score += 6
    score += len(matched_desired) * 8
    score += len(matched_context) * 4
    score += len(clarity_hits) * 3
    score -= len(penalties) * 7

    rationale_bits: list[str] = []
    if source_label:
        rationale_bits.append(source_label)
    if matched_desired:
        rationale_bits.append(
            "matches requested voice cues: " + ", ".join(matched_desired[:4])
        )
    elif matched_context:
        rationale_bits.append(
            "aligns with presentation context: " + ", ".join(matched_context[:4])
        )
    if clarity_hits:
        rationale_bits.append(
            "supports intelligible narration: " + ", ".join(clarity_hits[:3])
        )
    if not rationale_bits:
        rationale_bits.append(
            "kept as a conservative narration candidate with catalog preview availability"
        )

    return {
        "voice_id": voice_id,
        "name": str(voice.get("name") or voice_id),
        "preview_url": preview_url,
        "category": category or None,
        "description": str(voice.get("description") or "").strip() or None,
        "labels": labels,
        "source": source,
        "score": score,
        "matched_terms": matched_desired or matched_context,
        "rationale": "; ".join(rationale_bits),
    }


def _rank_voice_candidates(
    voices: list[dict[str, Any]],
    *,
    desired_terms: list[str],
    context_terms: list[str],
    clarity_hints: set[str],
    penalty_terms: set[str],
    preferred_language: str | None,
    preferred_locale: str | None,
    limit: int,
    exclude_voice_ids: set[str] | None = None,
    source: str,
    source_label: str,
) -> list[dict[str, Any]]:
    """Rank catalog voices for preview by metadata fit and preview availability."""
    exclude_voice_ids = exclude_voice_ids or set()
    candidates: list[dict[str, Any]] = []
    for voice in voices:
        voice_id = str(voice.get("voice_id") or "").strip()
        if not voice_id or voice_id in exclude_voice_ids:
            continue
        candidate = _build_voice_candidate(
            voice,
            desired_terms=desired_terms,
            context_terms=context_terms,
            clarity_hints=clarity_hints,
            penalty_terms=penalty_terms,
            preferred_language=preferred_language,
            preferred_locale=preferred_locale,
            source=source,
            source_label=source_label,
        )
        if candidate is not None:
            candidates.append(candidate)
    candidates.sort(key=lambda item: (-item["score"], item["name"].lower(), item["voice_id"]))
    return candidates[:limit]


def preview_voice_options(
    *,
    mode: str = "default_plus_alternatives",
    presentation_attributes: dict[str, Any] | None = None,
    previous_voice_id: str | None = None,
    previous_voice_receipt_path: str | Path | None = None,
    ideal_voice_description: str | None = None,
    style_defaults: dict[str, Any] | None = None,
    audio_buffer_seconds: float | None = None,
    locked_manifest_path: str | Path | None = None,
    locked_script_path: str | Path | None = None,
    output_path: str | Path | None = None,
    client: ElevenLabsClient | None = None,
) -> dict[str, Any]:
    """Build HIL-ready ElevenLabs catalog voice previews without generating audio."""
    if mode not in VOICE_PREVIEW_MODES:
        raise ValueError(
            f"Unsupported voice preview mode: {mode}. Expected one of {sorted(VOICE_PREVIEW_MODES)}."
        )
    if client is None:
        client = ElevenLabsClient()
    style_defaults = style_defaults or load_style_guide_elevenlabs()
    resolved_audio_buffer_seconds = _resolve_audio_buffer_seconds(
        audio_buffer_seconds, style_defaults=style_defaults
    )
    voices = client.list_voices()
    voice_map = {
        str(voice.get("voice_id") or "").strip(): voice
        for voice in voices
        if str(voice.get("voice_id") or "").strip()
    }
    profile_name, profile = _resolve_voice_preview_profile(
        style_defaults=style_defaults,
        presentation_attributes=presentation_attributes,
        ideal_voice_description=ideal_voice_description,
    )
    preview_candidate_count = max(3, int(style_defaults.get("preview_candidate_count") or 3))
    preferred_language = str(
        profile.get("preferred_languages", [style_defaults.get("preferred_language", "en")])[0]
        if profile.get("preferred_languages")
        else style_defaults.get("preferred_language", "en")
    ).strip()
    preferred_locale = str(
        profile.get("preferred_locales", ["en-US"])[0]
        if profile.get("preferred_locales")
        else "en-US"
    ).strip()
    preferred_terms = _merge_unique_terms(
        [
            "professional",
            "clear",
            "calm",
            "warm",
            "credible",
            "educational",
        ],
        profile.get("preferred_tokens"),
    )
    penalty_terms = set(
        _merge_unique_terms(list(VOICE_PENALTY_TERMS), profile.get("avoided_tokens"))
    )
    clarity_hints = set(
        _merge_unique_terms(list(VOICE_CLARITY_HINTS), profile.get("preferred_tokens"))
    )
    profile_context_terms = _merge_unique_terms(
        profile.get("preferred_use_cases"),
        profile.get("preferred_accents"),
        profile.get("preferred_ages"),
        profile.get("preferred_genders"),
    )

    default_voice_id = str(style_defaults.get("default_voice_id") or "").strip() or None
    resolved_previous_voice_id = str(previous_voice_id or "").strip() or None
    prior_voice_source = {
        "type": "none",
        "voice_id": None,
        "voice_name": None,
        "fallback_reason": None,
    }
    if previous_voice_receipt_path:
        receipt_path = Path(previous_voice_receipt_path)
        if receipt_path.exists():
            previous_receipt = _load_json_file(receipt_path)
            resolved_previous_voice_id = (
                str(previous_receipt.get("selected_voice_id") or "").strip()
                or str(
                    (previous_receipt.get("presentation_voice_source") or {}).get("voice_id")
                    or ""
                ).strip()
                or None
            )
            if resolved_previous_voice_id:
                prior_voice_source.update(
                    {
                        "type": "previous_receipt",
                        "voice_id": resolved_previous_voice_id,
                        "source_path": str(receipt_path),
                    }
                )
        else:
            prior_voice_source["fallback_reason"] = "previous voice receipt path not found"
    context_chunks = _flatten_voice_context(presentation_attributes or {})
    context_terms = _tokenize_voice_terms(*context_chunks)
    baseline_terms = preferred_terms
    enriched_context_terms = _merge_unique_terms(context_terms, profile_context_terms)

    if mode == "description_driven_search":
        if not ideal_voice_description:
            raise ValueError(
                "ideal_voice_description is required for description_driven_search mode."
            )
        desired_terms = _tokenize_voice_terms(ideal_voice_description, *context_chunks)
        if not desired_terms:
            desired_terms = baseline_terms
        recommendations = _rank_voice_candidates(
            voices,
            desired_terms=desired_terms,
            context_terms=enriched_context_terms or baseline_terms,
            clarity_hints=clarity_hints,
            penalty_terms=penalty_terms,
            preferred_language=preferred_language,
            preferred_locale=preferred_locale,
            limit=preview_candidate_count,
            source="description_recommendation",
            source_label="recommended from operator voice description",
        )
        if len(recommendations) < preview_candidate_count:
            raise ValueError(
                f"Need {preview_candidate_count} previewable catalog voices for description-driven recommendations."
            )
        result = {
            "status": "selection_required",
            "selection_mode": "description_recommendation",
            "mode": mode,
            "profile_name": profile_name,
            "default_voice_id": default_voice_id,
            "previous_voice_id": resolved_previous_voice_id,
            "ideal_voice_description": ideal_voice_description,
            "presentation_context": context_chunks,
            "candidate_voices": recommendations,
            "catalog_voice_count": len(voices),
            "audio_buffer_seconds": resolved_audio_buffer_seconds,
            "selected_voice_id": None,
            "selected_voice_name": None,
            "selected_from_rank": None,
            "operator_notes": None,
            "override_reason": None,
            "presentation_voice_source": prior_voice_source,
        }
        if locked_manifest_path:
            result["locked_manifest_path"] = str(Path(locked_manifest_path))
            result["locked_manifest_hash"] = _sha256_file(locked_manifest_path)
        if locked_script_path:
            result["locked_script_path"] = str(Path(locked_script_path))
            result["locked_script_hash"] = _sha256_file(locked_script_path)
        if output_path:
            write_json_output(result, output_path)
            write_voice_selection_review(result, output_path)
            result["output_path"] = str(Path(output_path))
        return result

    anchor_source = ""
    anchor_source_label = ""
    anchor_voice_id = None
    if mode == "continuity_preview":
        anchor_voice_id = resolved_previous_voice_id
        if resolved_previous_voice_id:
            anchor_source = "previous_presentation_voice"
            anchor_source_label = "carry-forward voice from this presentation"
        elif default_voice_id:
            anchor_voice_id = default_voice_id
            anchor_source = "style_guide_default"
            anchor_source_label = "fallback default voice because no prior receipt resolved"
            prior_voice_source["fallback_reason"] = (
                prior_voice_source.get("fallback_reason")
                or "no trusted previous presentation voice resolved"
            )
    elif default_voice_id:
        anchor_voice_id = default_voice_id
        anchor_source = "style_guide_default"
        anchor_source_label = "style-guide default voice for a new presentation"

    if mode == "continuity_preview" and resolved_previous_voice_id:
        anchor_source = "previous_presentation_voice"
        anchor_source_label = "carry-forward voice from this presentation"

    candidate_voices: list[dict[str, Any]] = []
    if anchor_voice_id and anchor_voice_id in voice_map:
        anchor_candidate = _build_voice_candidate(
            voice_map[anchor_voice_id],
            desired_terms=baseline_terms,
            context_terms=enriched_context_terms,
            clarity_hints=clarity_hints,
            penalty_terms=penalty_terms,
            preferred_language=preferred_language,
            preferred_locale=preferred_locale,
            source=anchor_source,
            source_label=anchor_source_label,
        )
        if anchor_candidate is not None:
            candidate_voices.append(anchor_candidate)
            prior_voice_source.update(
                {
                    "type": anchor_source,
                    "voice_id": anchor_candidate["voice_id"],
                    "voice_name": anchor_candidate["name"],
                }
            )
        elif anchor_source == "previous_presentation_voice":
            prior_voice_source["fallback_reason"] = (
                prior_voice_source.get("fallback_reason")
                or "prior voice lacks a current preview URL"
            )
    elif anchor_voice_id and anchor_source == "previous_presentation_voice":
        prior_voice_source["fallback_reason"] = (
            prior_voice_source.get("fallback_reason")
            or "previous presentation voice not available in the current catalog"
        )

    alternative_terms = enriched_context_terms or baseline_terms
    exclude = {candidate["voice_id"] for candidate in candidate_voices}
    alternatives = _rank_voice_candidates(
        voices,
        desired_terms=baseline_terms,
        context_terms=alternative_terms,
        clarity_hints=clarity_hints,
        penalty_terms=penalty_terms,
        preferred_language=preferred_language,
        preferred_locale=preferred_locale,
        limit=max(0, preview_candidate_count - len(candidate_voices)),
        exclude_voice_ids=exclude,
        source="presentation_attribute_alternative",
        source_label="APP-selected alternative based on presentation attributes",
    )
    candidate_voices.extend(alternatives)

    if len(candidate_voices) < preview_candidate_count:
        filler = _rank_voice_candidates(
            voices,
            desired_terms=baseline_terms,
            context_terms=baseline_terms,
            clarity_hints=clarity_hints,
            penalty_terms=penalty_terms,
            preferred_language=preferred_language,
            preferred_locale=preferred_locale,
            limit=preview_candidate_count - len(candidate_voices),
            exclude_voice_ids={candidate["voice_id"] for candidate in candidate_voices},
            source="fallback_alternative",
            source_label="fallback narration candidate with catalog preview",
        )
        candidate_voices.extend(filler)

    candidate_voices = candidate_voices[:preview_candidate_count]
    if len(candidate_voices) < preview_candidate_count:
        raise ValueError(
            f"Need {preview_candidate_count} previewable catalog voices for governed voice preview."
        )

    for index, candidate in enumerate(candidate_voices, start=1):
        candidate["rank"] = index
        candidate["selection_basis"] = (
            "primary continuity/default preview" if index == 1 else "APP-selected alternative"
        )

    result = {
        "status": "selection_required",
        "selection_mode": "default_and_alternatives",
        "mode": mode,
        "profile_name": profile_name,
        "default_voice_id": default_voice_id,
        "previous_voice_id": resolved_previous_voice_id,
        "presentation_context": context_chunks,
        "candidate_voices": candidate_voices,
        "catalog_voice_count": len(voices),
        "audio_buffer_seconds": resolved_audio_buffer_seconds,
        "selected_voice_id": None,
        "selected_voice_name": None,
        "selected_from_rank": None,
        "operator_notes": None,
        "override_reason": None,
        "presentation_voice_source": prior_voice_source,
    }
    if locked_manifest_path:
        result["locked_manifest_path"] = str(Path(locked_manifest_path))
        result["locked_manifest_hash"] = _sha256_file(locked_manifest_path)
    if locked_script_path:
        result["locked_script_path"] = str(Path(locked_script_path))
        result["locked_script_hash"] = _sha256_file(locked_script_path)
    if output_path:
        write_json_output(result, output_path)
        write_voice_selection_review(result, output_path)
        result["output_path"] = str(Path(output_path))
    return result


def finalize_voice_selection(
    preview_receipt_path: str | Path,
    *,
    selected_voice_id: str,
    output_path: str | Path | None = None,
    operator_notes: str | None = None,
    override_reason: str | None = None,
    audio_buffer_seconds: float | None = None,
) -> dict[str, Any]:
    """Persist the operator's selected voice from a preview receipt."""
    receipt = _load_json_file(preview_receipt_path)
    candidates = (
        receipt.get("candidate_voices")
        if isinstance(receipt.get("candidate_voices"), list)
        else []
    )
    selected_candidate = next(
        (candidate for candidate in candidates if candidate.get("voice_id") == selected_voice_id),
        None,
    )
    if selected_candidate is None:
        raise ValueError("Selected voice_id is not present in the preview candidate set.")

    selected_rank = int(selected_candidate.get("rank") or 0)
    if selected_rank != 1 and not str(override_reason or "").strip():
        raise ValueError(
            "override_reason is required when selecting a non-primary preview candidate."
        )

    resolved_audio_buffer_seconds = _resolve_audio_buffer_seconds(
        audio_buffer_seconds if audio_buffer_seconds is not None else receipt.get("audio_buffer_seconds"),
        style_defaults=load_style_guide_elevenlabs(),
    )

    decision = dict(receipt)
    decision.update(
        {
            "status": "approved",
            "selected_voice_id": selected_candidate.get("voice_id"),
            "selected_voice_name": selected_candidate.get("name"),
            "selected_from": selected_candidate.get("source"),
            "selected_from_rank": selected_rank,
            "preview_url": selected_candidate.get("preview_url"),
            "selection_rationale": selected_candidate.get("rationale"),
            "audio_buffer_seconds": resolved_audio_buffer_seconds,
            "operator_notes": operator_notes,
            "override_reason": override_reason,
            "voice_preview_receipt_path": str(Path(preview_receipt_path)),
            "approved_at_utc": datetime.now(UTC).isoformat(),
        }
    )
    target_path = Path(output_path) if output_path else Path(preview_receipt_path)
    write_json_output(decision, target_path)
    decision["output_path"] = str(target_path)
    return decision


def build_pronunciation_pls(
    terms: dict[str, str],
    *,
    alphabet: str = "ipa",
    locale: str = "en-US",
) -> str:
    """Build a minimal PLS document from grapheme -> pronunciation mappings."""
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<lexicon version="1.0"',
        '    xmlns="http://www.w3.org/2005/01/pronunciation-lexicon"',
        '    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
        '    xsi:schemaLocation="http://www.w3.org/2005/01/pronunciation-lexicon',
        '        http://www.w3.org/TR/2007/CR-pronunciation-lexicon-20071212/pls.xsd"',
        f'    alphabet="{alphabet}" xml:lang="{locale}">',
    ]
    for term, pronunciation in terms.items():
        lines.extend(
            [
                "<lexeme>",
                f"    <grapheme>{xml_utils.escape(term)}</grapheme>",
                f"    <phoneme>{xml_utils.escape(pronunciation)}</phoneme>",
                "</lexeme>",
            ]
        )
    lines.append("</lexicon>")
    return "\n".join(lines) + "\n"


def _format_vtt_timestamp(value: float) -> str:
    """Format seconds as a WebVTT timestamp."""
    total_ms = max(0, round(value * 1000))
    hours, remainder = divmod(total_ms, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"


def _parse_vtt_timestamp(value: str) -> float:
    match = re.match(r"^(\d{2}):(\d{2}):(\d{2})\.(\d{3})$", value.strip())
    if not match:
        raise ValueError(f"Invalid VTT timestamp: {value}")
    hours, minutes, seconds, milliseconds = (int(part) for part in match.groups())
    return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0


def alignment_to_vtt(alignment: dict[str, Any] | None) -> str:
    """Convert ElevenLabs character alignment to a word-level WebVTT track."""
    if not alignment:
        return "WEBVTT\n\n"

    characters = alignment.get("characters", [])
    starts = alignment.get("character_start_times_seconds", [])
    ends = alignment.get("character_end_times_seconds", [])
    cues: list[tuple[float, float, str]] = []
    current_chars: list[str] = []
    current_start: float | None = None
    current_end: float | None = None

    for char, start, end in zip(characters, starts, ends):
        if char.isspace():
            if current_chars and current_start is not None and current_end is not None:
                cues.append((current_start, current_end, "".join(current_chars)))
                current_chars = []
                current_start = None
                current_end = None
            continue

        if current_start is None:
            current_start = start
        current_end = end
        current_chars.append(char)

    if current_chars and current_start is not None and current_end is not None:
        cues.append((current_start, current_end, "".join(current_chars)))

    lines = ["WEBVTT", ""]
    for index, (start, end, text) in enumerate(cues, start=1):
        lines.append(str(index))
        lines.append(f"{_format_vtt_timestamp(start)} --> {_format_vtt_timestamp(end)}")
        lines.append(text)
        lines.append("")
    return "\n".join(lines)


def offset_vtt_timestamps(vtt_text: str, offset_seconds: float) -> str:
    if offset_seconds <= 0:
        return vtt_text
    lines = vtt_text.splitlines()
    updated: list[str] = []
    for line in lines:
        if "-->" not in line:
            updated.append(line)
            continue
        start_text, end_text = (part.strip() for part in line.split("-->", 1))
        try:
            start = _parse_vtt_timestamp(start_text) + offset_seconds
            end = _parse_vtt_timestamp(end_text) + offset_seconds
        except ValueError as e:
            raise ValueError(f"Invalid VTT timestamp in line: {line}") from e
        updated.append(f"{_format_vtt_timestamp(start)} --> {_format_vtt_timestamp(end)}")
    suffix = "\n" if vtt_text.endswith("\n") else ""
    return "\n".join(updated) + suffix


def _apply_audio_buffer(
    audio_path: Path,
    *,
    lead_seconds: float,
    tail_seconds: float,
    base_duration: float,
    ffmpeg_path: str | None = None,
) -> None:
    if lead_seconds <= 0 and tail_seconds <= 0:
        return
    if lead_seconds < 0 or tail_seconds < 0:
        raise ValueError("audio_buffer_seconds must be non-negative.")
    ffmpeg = ffmpeg_path or FFMPEG_BINARY
    temp_path = audio_path.with_name(f"{audio_path.stem}-buffered{audio_path.suffix}")
    silence_inputs: list[tuple[str, float]] = []
    if lead_seconds > 0:
        silence_inputs.append(("lead", lead_seconds))
    if tail_seconds > 0:
        silence_inputs.append(("tail", tail_seconds))

    command = [ffmpeg, "-y"]
    input_count = 0
    for _, duration in silence_inputs:
        command.extend(
            [
                "-f",
                "lavfi",
                "-t",
                f"{duration:.3f}",
                "-i",
                "anullsrc=r=44100:cl=stereo",
            ]
        )
        input_count += 1
    command.extend(["-i", str(audio_path)])
    audio_input_index = input_count
    input_count += 1
    filter_inputs = [f"[{idx}:a]" for idx in range(input_count)]
    filter_str = "".join(filter_inputs) + f"concat=n={input_count}:v=0:a=1[out]"
    command.extend(
        [
            "-filter_complex",
            filter_str,
            "-map",
            "[out]",
            str(temp_path),
        ]
    )
    subprocess.run(command, capture_output=True, text=True, check=True)
    temp_path.replace(audio_path)


def load_manifest(manifest_path: str | Path) -> dict[str, Any]:
    """Load a YAML segment manifest from disk."""
    manifest_path = Path(manifest_path)
    return yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}


def save_manifest(manifest: dict[str, Any], manifest_path: str | Path) -> Path:
    """Save a YAML segment manifest back to disk."""
    manifest_path = Path(manifest_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        yaml.safe_dump(manifest, sort_keys=False, allow_unicode=False),
        encoding="utf-8",
    )
    return manifest_path


def generate_narration(
    text: str,
    *,
    output_dir: str | Path | None = None,
    filename_stem: str = "narration",
    voice_id: str | None = None,
    parameter_overrides: dict[str, Any] | None = None,
    pronunciation_dictionary_locators: list[dict[str, str]] | None = None,
    previous_request_ids: list[str] | None = None,
    next_request_ids: list[str] | None = None,
    audio_buffer_seconds: float = 0.0,
    client: ElevenLabsClient | None = None,
) -> dict[str, Any]:
    """Generate narration audio + VTT using style-guide defaults and overrides."""
    if client is None:
        client = ElevenLabsClient()
    if output_dir is None:
        output_dir = STAGING_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    merged = merge_parameters(load_style_guide_elevenlabs(), parameter_overrides)
    voice_direction = _resolve_voice_direction(merged)
    resolved_voice_id = voice_id or merged.get("default_voice_id")
    if not resolved_voice_id:
        raise ValueError("No ElevenLabs voice_id available from args or style guide.")

    audio_path = output_dir / f"{filename_stem}.mp3"
    vtt_path = output_dir / f"{filename_stem}.vtt"
    result = client.text_to_speech_with_timestamps_file(
        text,
        resolved_voice_id,
        audio_path,
        model_id=merged.get("model_id", "eleven_multilingual_v2"),
        stability=voice_direction["stability"] if voice_direction["stability"] is not None else 0.5,
        similarity_boost=voice_direction["similarity_boost"]
        if voice_direction["similarity_boost"] is not None
        else 0.75,
        style=voice_direction["style"] if voice_direction["style"] is not None else 0.0,
        speed=voice_direction["speed"],
        use_speaker_boost=voice_direction["use_speaker_boost"],
        output_format=merged.get("output_format", "mp3_44100_128"),
        pronunciation_dictionary_locators=pronunciation_dictionary_locators,
        previous_request_ids=previous_request_ids,
        next_request_ids=next_request_ids,
    )
    vtt = alignment_to_vtt(result.get("normalized_alignment") or result.get("alignment"))
    vtt_path.write_text(vtt, encoding="utf-8")
    alignment = result.get("normalized_alignment") or result.get("alignment") or {}
    ends = alignment.get("character_end_times_seconds", [])
    duration_seconds = ends[-1] if ends else 0.0

    if audio_buffer_seconds > 0:
        _apply_audio_buffer(
            audio_path,
            lead_seconds=audio_buffer_seconds,
            tail_seconds=0,
            base_duration=duration_seconds,
        )
        vtt = offset_vtt_timestamps(vtt, audio_buffer_seconds)
        vtt_path.write_text(vtt, encoding="utf-8")
        duration_seconds += audio_buffer_seconds

    return {
        "status": "success",
        "voice_id": resolved_voice_id,
        "audio_path": str(audio_path),
        "vtt_path": str(vtt_path),
        "request_id": result.get("request_id"),
        "narration_duration": duration_seconds,
        "output_format": result.get("output_format"),
        "voice_direction": voice_direction,
    }


def _verify_voice_selection_hashes(
    voice_selection_path: str | Path,
    manifest_path: str | Path,
) -> dict[str, Any]:
    """Verify voice-selection.json hashes match the locked manifest and script.

    Returns the parsed voice-selection data on success.
    Raises ``ValueError`` if hashes diverge.
    """
    vs = _load_json_file(voice_selection_path)
    expected_manifest_hash = vs.get("locked_manifest_hash", "")
    expected_script_hash = vs.get("locked_script_hash", "")
    if not expected_manifest_hash or not expected_script_hash:
        raise ValueError(
            "voice-selection.json missing locked_manifest_hash or locked_script_hash"
        )
    actual_manifest_hash = _sha256_file(manifest_path)
    if actual_manifest_hash != expected_manifest_hash:
        raise ValueError(
            f"Manifest hash mismatch: voice-selection expects "
            f"{expected_manifest_hash[:16]}... but locked manifest is "
            f"{actual_manifest_hash[:16]}..."
        )
    # Script hash requires finding the script next to the manifest.
    manifest_dir = Path(manifest_path).resolve().parent
    script_candidates = [
        manifest_dir / "narration-script.md",
        manifest_dir.parent / "narration-script.md",
    ]
    script_path = next((p for p in script_candidates if p.exists()), None)
    if script_path:
        actual_script_hash = _sha256_file(script_path)
    if actual_script_hash != expected_script_hash:
        raise ValueError(
            f"Script hash mismatch: voice-selection expects "
            f"{expected_script_hash[:16]}... but locked script is "
            f"{actual_script_hash[:16]}..."
        )
    return vs


def _load_pass2_envelope_voice_direction_defaults(manifest_path: str | Path) -> dict[str, Any]:
    manifest_dir = Path(manifest_path).resolve().parent
    bundle_dir = manifest_dir.parent if manifest_dir.name == "assembly-bundle" else manifest_dir
    envelope_path = bundle_dir / "pass2-envelope.json"
    if not envelope_path.is_file():
        return {}
    try:
        envelope = _load_json_file(envelope_path)
    except Exception:
        return {}
    defaults = envelope.get("voice_direction_defaults", {})
    return defaults if isinstance(defaults, dict) else {}


def generate_manifest_narration(
    manifest_path: str | Path,
    *,
    output_dir: str | Path | None = None,
    parameter_overrides: dict[str, Any] | None = None,
    default_voice_id: str | None = None,
    voice_selection_path: str | Path | None = None,
    audio_buffer_seconds: float | None = None,
    progress_callback: Any | None = None,
    client: ElevenLabsClient | None = None,
) -> dict[str, Any]:
    """Generate narration for each manifest segment and write results back.

    This is the pipeline bridge used by Marcus:
    Irene manifest -> ElevenLabs narration assets -> updated manifest.

    Parameters
    ----------
    voice_selection_path:
        Optional path to ``voice-selection.json``.  When provided the function
        verifies ``locked_manifest_hash`` and ``locked_script_hash`` match the
        Gate 3 locked artifacts *before* any ElevenLabs spend.  The
        ``selected_voice_id`` from the file also serves as the default voice
        (unless *default_voice_id* is explicitly provided).
    progress_callback:
        Optional ``callable(segment_id, index, total)`` invoked after each
        segment is synthesized so the caller can report progress.
    """
    # ── Voice-selection hash gate ────────────────────────────────────────
    vs_data: dict[str, Any] | None = None
    if voice_selection_path:
        # Resolve the locked root manifest for hash comparison.  When the
        # manifest_path lives under assembly-bundle/, the locked original
        # sits one directory up.
        locked_root = Path(manifest_path).resolve().parent.parent / "segment-manifest.yaml"
        hash_target = locked_root if locked_root.exists() else Path(manifest_path)
        vs_data = _verify_voice_selection_hashes(voice_selection_path, hash_target)
        if not default_voice_id:
            default_voice_id = vs_data.get("selected_voice_id")

    if client is None:
        client = ElevenLabsClient()
    manifest = load_manifest(manifest_path)
    lesson_id = manifest.get("lesson_id", "lesson")
    base_output_dir = Path(output_dir) if output_dir else STAGING_DIR / lesson_id
    audio_dir = base_output_dir / "audio"
    captions_dir = base_output_dir / "captions"
    audio_dir.mkdir(parents=True, exist_ok=True)
    captions_dir.mkdir(parents=True, exist_ok=True)

    merged = merge_parameters(
        merge_parameters(
            load_style_guide_elevenlabs(),
            _load_pass2_envelope_voice_direction_defaults(manifest_path),
        ),
        parameter_overrides,
    )
    voice_direction = _resolve_voice_direction(merged)
    resolved_default_voice_id = default_voice_id or merged.get("default_voice_id")
    if not resolved_default_voice_id:
        raise ValueError("No ElevenLabs default voice available for manifest processing.")

    resolved_audio_buffer_seconds = _resolve_audio_buffer_seconds(
        audio_buffer_seconds
        if audio_buffer_seconds is not None
        else (vs_data or {}).get("audio_buffer_seconds"),
        style_defaults=merged,
    )
    ffmpeg_path = None
    if resolved_audio_buffer_seconds > 0:
        ffmpeg_path = resolve_ffmpeg_binary()

    segments = manifest.get("segments", [])
    total_segments = len(segments)
    estimated_durations = [
        float(segment["duration_estimate_seconds"])
        for segment in segments
        if segment.get("duration_estimate_seconds") not in (None, "")
    ]
    mean_estimated_duration = (
        sum(estimated_durations) / len(estimated_durations) if estimated_durations else None
    )
    max_estimated_delta = (
        max(abs(duration - mean_estimated_duration) for duration in estimated_durations)
        if estimated_durations and mean_estimated_duration is not None
        else 0.0
    )
    previous_request_ids: list[str] = []
    outputs: list[dict[str, Any]] = []
    for seg_index, segment in enumerate(segments, start=1):
        segment_id = segment.get("id", "segment")
        narration_text = (segment.get("narration_text") or "").strip()
        if not narration_text:
            segment["narration_duration"] = 0.0
            segment["narration_file"] = None
            segment["narration_vtt"] = None
            segment["audio_buffer_seconds"] = 0.0
            segment.setdefault("sfx_file", None)
            if progress_callback:
                progress_callback(segment_id, seg_index, total_segments)
            continue

        voice_id = segment.get("voice_id") or resolved_default_voice_id
        segment_speed = voice_direction["speed"]
        duration_estimate = _coerce_float(
            segment.get("duration_estimate_seconds"),
            field_name=f"{segment_id}.duration_estimate_seconds",
        )
        if (
            segment_speed is not None
            and duration_estimate is not None
            and mean_estimated_duration is not None
            and max_estimated_delta > 0
            and voice_direction["pace_variability"] > 0
        ):
            relative_delta = (duration_estimate - mean_estimated_duration) / max_estimated_delta
            segment_speed = _clamp(
                segment_speed - (relative_delta * voice_direction["pace_variability"]),
                MIN_ELEVENLABS_SPEED,
                MAX_ELEVENLABS_SPEED,
            )
        segment_overrides = dict(parameter_overrides or {})
        if segment_speed is not None:
            segment_overrides["speed"] = segment_speed
        result = generate_narration(
            narration_text,
            output_dir=audio_dir,
            filename_stem=segment_id,
            voice_id=voice_id,
            parameter_overrides=segment_overrides,
            previous_request_ids=previous_request_ids or None,
            client=client,
        )

        # Move the generated VTT into the captions folder while keeping the API of
        # generate_narration simple for single-file usage.
        audio_path = Path(result["audio_path"])
        generated_vtt_path = Path(result["vtt_path"])
        final_vtt_path = captions_dir / f"{segment_id}.vtt"
        if generated_vtt_path != final_vtt_path:
            final_vtt_path.write_text(
                generated_vtt_path.read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            generated_vtt_path.unlink()

        buffer_seconds = resolved_audio_buffer_seconds
        narration_duration = result["narration_duration"]
        if buffer_seconds > 0:
            _apply_audio_buffer(
                audio_path,
                lead_seconds=buffer_seconds,
                tail_seconds=0,
                base_duration=narration_duration,
                ffmpeg_path=ffmpeg_path,
            )
            updated_vtt = offset_vtt_timestamps(
                final_vtt_path.read_text(encoding="utf-8"),
                buffer_seconds,
            )
            final_vtt_path.write_text(updated_vtt, encoding="utf-8")
            narration_duration += buffer_seconds

        segment["narration_duration"] = narration_duration
        segment["narration_file"] = str(audio_path)
        segment["narration_vtt"] = str(final_vtt_path)
        segment["audio_buffer_seconds"] = buffer_seconds
        segment.setdefault("sfx_file", None)

        sfx_cue = segment.get("sfx")
        if sfx_cue:
            sfx_result = generate_sound_effect(
                sfx_cue,
                output_dir=audio_dir,
                filename=f"{segment_id}-sfx.mp3",
                client=client,
            )
            segment["sfx_file"] = sfx_result["sfx_path"]

        if result.get("request_id"):
            previous_request_ids = [result["request_id"]]

        outputs.append(
            {
                "segment_id": segment_id,
                "voice_id": voice_id,
                "request_id": result.get("request_id"),
                "narration_duration": narration_duration,
                "narration_file": segment["narration_file"],
                "narration_vtt": segment["narration_vtt"],
                "audio_buffer_seconds": buffer_seconds,
                "sfx_file": segment.get("sfx_file"),
                "duration_estimate_seconds": duration_estimate,
                "speed": segment_speed,
            }
        )

        if progress_callback:
            progress_callback(segment_id, seg_index, total_segments)

    saved_path = save_manifest(manifest, manifest_path)
    return {
        "status": "success",
        "manifest_path": str(saved_path),
        "narration_outputs": outputs,
        "voice_direction": voice_direction,
    }


def create_pronunciation_dictionary(
    name: str,
    terms: dict[str, str],
    *,
    output_dir: str | Path | None = None,
    description: str | None = None,
    client: ElevenLabsClient | None = None,
) -> dict[str, Any]:
    """Create a PLS file locally and upload it to ElevenLabs."""
    if client is None:
        client = ElevenLabsClient()
    if output_dir is None:
        output_dir = STAGING_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    pls_path = output_dir / f"{name}.pls"
    pls_path.write_text(build_pronunciation_pls(terms), encoding="utf-8")
    created = client.create_pronunciation_dictionary_from_file(
        name,
        pls_path,
        description=description,
    )
    created["local_pls_path"] = str(pls_path)
    return created


def generate_sound_effect(
    text: str,
    *,
    output_dir: str | Path | None = None,
    filename: str = "sfx.mp3",
    client: ElevenLabsClient | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Generate a sound effect and save it locally."""
    if client is None:
        client = ElevenLabsClient()
    if output_dir is None:
        output_dir = STAGING_DIR
    output_path = Path(output_dir) / filename
    client.text_to_sound_effect_file(text, output_path, **kwargs)
    return {"status": "success", "sfx_path": str(output_path)}


def generate_dialogue(
    inputs: list[dict[str, str]],
    *,
    output_dir: str | Path | None = None,
    filename: str = "dialogue.mp3",
    client: ElevenLabsClient | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Generate multi-speaker dialogue and save it locally."""
    if client is None:
        client = ElevenLabsClient()
    if output_dir is None:
        output_dir = STAGING_DIR
    output_path = Path(output_dir) / filename
    client.text_to_dialogue_file(inputs, output_path, **kwargs)
    return {"status": "success", "dialogue_path": str(output_path)}


def generate_music(
    *,
    output_dir: str | Path | None = None,
    filename: str = "music.mp3",
    client: ElevenLabsClient | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Generate background music and save it locally."""
    if client is None:
        client = ElevenLabsClient()
    if output_dir is None:
        output_dir = STAGING_DIR
    output_path = Path(output_dir) / filename
    client.generate_music_file(output_path, **kwargs)
    return {"status": "success", "music_path": str(output_path)}


def write_json_output(payload: dict[str, Any], output_path: str | Path) -> Path:
    """Persist structured JSON output for Marcus-managed receipts."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return output_path


def _voice_review_markdown_path(output_path: str | Path) -> Path:
    """Resolve the sibling review markdown path for a preview receipt."""
    output_path = Path(output_path)
    return output_path.with_name("voice-selection-review.md")


def write_voice_selection_review(
    preview_receipt: dict[str, Any], output_path: str | Path
) -> Path:
    """Persist a human-readable review surface for Prompt 11 voice selection."""
    review_path = _voice_review_markdown_path(output_path)
    review_path.parent.mkdir(parents=True, exist_ok=True)

    mode = str(preview_receipt.get("mode") or "unknown")
    profile_name = str(preview_receipt.get("profile_name") or "unknown")
    audio_buffer_seconds = preview_receipt.get("audio_buffer_seconds")
    presentation_voice_source = preview_receipt.get("presentation_voice_source") or {}
    source_type = str(presentation_voice_source.get("type") or "none")
    source_voice_name = str(presentation_voice_source.get("voice_name") or "").strip()
    source_voice_id = str(presentation_voice_source.get("voice_id") or "").strip()
    source_fallback = str(
        presentation_voice_source.get("fallback_reason") or ""
    ).strip()

    lines = [
        "# Voice Selection Review",
        "",
        f"- Status: `{preview_receipt.get('status', 'unknown')}`",
        f"- Review path: `{mode}`",
        f"- Profile: `{profile_name}`",
        f"- Audio buffer seconds: `{audio_buffer_seconds}`",
        "",
        "## Locked Gate 3 Package",
        f"- Narration script: `{preview_receipt.get('locked_script_path', 'missing')}`",
        f"- Narration script SHA-256: `{preview_receipt.get('locked_script_hash', 'missing')}`",
        f"- Segment manifest: `{preview_receipt.get('locked_manifest_path', 'missing')}`",
        f"- Segment manifest SHA-256: `{preview_receipt.get('locked_manifest_hash', 'missing')}`",
        "",
        "## Continuity Context",
        f"- Presentation voice source: `{source_type}`",
    ]
    if source_voice_name or source_voice_id:
        lines.append(
            f"- Source voice: `{source_voice_name or 'unknown'}` (`{source_voice_id or 'unknown'}`)"
        )
    if source_fallback:
        lines.append(f"- Fallback reason: {source_fallback}")

    presentation_context = _flatten_voice_context(
        preview_receipt.get("presentation_context")
    )
    if presentation_context:
        lines.extend(["", "## Presentation Context"])
        for item in presentation_context:
            lines.append(f"- {item}")

    lines.extend(["", "## Candidates"])
    for candidate in preview_receipt.get("candidate_voices", []):
        rank = candidate.get("rank", "?")
        name = candidate.get("name") or candidate.get("voice_id") or "Unknown voice"
        voice_id = candidate.get("voice_id") or "unknown"
        source = candidate.get("source") or "unknown"
        basis = candidate.get("selection_basis") or "candidate"
        lines.extend(
            [
                f"### Rank {rank}: {name}",
                f"- Voice ID: `{voice_id}`",
                f"- Source: `{source}`",
                f"- Basis: {basis}",
                f"- Preview URL: {candidate.get('preview_url') or 'missing'}",
                f"- Rationale: {candidate.get('rationale') or 'No rationale provided.'}",
            ]
        )
        description = candidate.get("description")
        if description:
            lines.append(f"- Description: {description}")

    lines.extend(
        [
            "",
            "## Operator Decision",
            "- Select the carry-forward voice or one alternative.",
            "- If selecting a non-primary candidate, record an override reason.",
            "- Do not proceed to synthesis until `voice-selection.json` is written and hashes still match the locked script and manifest.",
            "",
        ]
    )
    review_path.write_text("\n".join(lines), encoding="utf-8")
    return review_path


def build_parser() -> argparse.ArgumentParser:
    """Build a CLI for agent-driven execution and smoke checks."""
    parser = argparse.ArgumentParser(
        description="Run ElevenLabs operations and return structured JSON."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    narration = subparsers.add_parser("narration", help="Generate narration + VTT")
    narration.add_argument("text")
    narration.add_argument("--voice-id")
    narration.add_argument("--output-dir")
    narration.add_argument("--filename-stem", default="narration")

    dictionary = subparsers.add_parser(
        "dictionary", help="Create pronunciation dictionary from JSON terms"
    )
    dictionary.add_argument("name")
    dictionary.add_argument("terms_json")
    dictionary.add_argument("--output-dir")
    dictionary.add_argument("--description")

    sfx = subparsers.add_parser("sfx", help="Generate sound effect")
    sfx.add_argument("text")
    sfx.add_argument("--output-dir")
    sfx.add_argument("--filename", default="sfx.mp3")

    manifest = subparsers.add_parser(
        "manifest", help="Generate narration for all manifest segments"
    )
    manifest.add_argument("manifest_path")
    manifest.add_argument("--output-dir")
    manifest.add_argument("--default-voice-id")
    manifest.add_argument(
        "--voice-selection",
        help="Path to voice-selection.json; verifies hashes before synthesis",
    )
    manifest.add_argument("--audio-buffer-seconds", type=float)

    voice_preview = subparsers.add_parser(
        "voice-preview",
        help="Return HIL-ready ElevenLabs catalog preview options without synthesis",
    )
    voice_preview.add_argument(
        "--mode",
        choices=sorted(VOICE_PREVIEW_MODES),
        default="default_plus_alternatives",
    )
    voice_preview.add_argument("--presentation-attributes-json")
    voice_preview.add_argument("--previous-voice-id")
    voice_preview.add_argument("--previous-voice-receipt")
    voice_preview.add_argument("--ideal-voice-description")
    voice_preview.add_argument("--audio-buffer-seconds", type=float)
    voice_preview.add_argument("--locked-manifest")
    voice_preview.add_argument("--locked-script")
    voice_preview.add_argument("--output-path")

    voice_select = subparsers.add_parser(
        "voice-select",
        help="Persist the operator's selected voice from preview candidates",
    )
    voice_select.add_argument("--preview-receipt", required=True)
    voice_select.add_argument("--selected-voice-id", required=True)
    voice_select.add_argument("--output-path")
    voice_select.add_argument("--operator-notes")
    voice_select.add_argument("--override-reason")
    voice_select.add_argument("--audio-buffer-seconds", type=float)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "narration":
            result = generate_narration(
                args.text,
                output_dir=args.output_dir,
                filename_stem=args.filename_stem,
                voice_id=args.voice_id,
            )
        elif args.command == "dictionary":
            result = create_pronunciation_dictionary(
                args.name,
                json.loads(args.terms_json),
                output_dir=args.output_dir,
                description=args.description,
            )
        elif args.command == "manifest":
            def _cli_progress(seg_id: str, index: int, total: int) -> None:
                print(
                    f"[{index}/{total}] {seg_id} synthesized",
                    file=sys.stderr,
                    flush=True,
                )

            result = generate_manifest_narration(
                args.manifest_path,
                output_dir=args.output_dir,
                default_voice_id=args.default_voice_id,
                voice_selection_path=getattr(args, "voice_selection", None),
                audio_buffer_seconds=getattr(args, "audio_buffer_seconds", None),
                progress_callback=_cli_progress,
            )
        elif args.command == "voice-preview":
            attributes = (
                json.loads(args.presentation_attributes_json)
                if args.presentation_attributes_json
                else None
            )
            result = preview_voice_options(
                mode=args.mode,
                presentation_attributes=attributes,
                previous_voice_id=args.previous_voice_id,
                previous_voice_receipt_path=args.previous_voice_receipt,
                ideal_voice_description=args.ideal_voice_description,
                audio_buffer_seconds=args.audio_buffer_seconds,
                locked_manifest_path=args.locked_manifest,
                locked_script_path=args.locked_script,
                output_path=args.output_path,
            )
        elif args.command == "voice-select":
            result = finalize_voice_selection(
                args.preview_receipt,
                selected_voice_id=args.selected_voice_id,
                output_path=args.output_path,
                operator_notes=args.operator_notes,
                override_reason=args.override_reason,
                audio_buffer_seconds=args.audio_buffer_seconds,
            )
        else:
            result = generate_sound_effect(
                args.text,
                output_dir=args.output_dir,
                filename=args.filename,
            )
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:  # pragma: no cover - CLI path
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
