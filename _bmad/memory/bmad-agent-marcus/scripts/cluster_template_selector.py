"""
Deterministic content-aware template selector for Story 20c-2.

This module scores templates against content signals and returns an explainable
ranking. Runtime integration with Irene planning is intentionally deferred.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence

SIGNAL_KEYS = {
    "single_core_idea",
    "multi_facet",
    "data_presence",
    "contrast_tension",
    "evidence_density",
    "emotional_weight",
    "visual_decomposability",
}

DEFAULT_SIGNAL_WEIGHTS: dict[str, dict[str, float]] = {
    "deep-dive": {"multi_facet": 1.20, "visual_decomposability": 0.50, "evidence_density": 0.40},
    "contrast-pair": {"contrast_tension": 1.30, "multi_facet": 0.40},
    "evidence-build": {"evidence_density": 1.25, "data_presence": 0.55},
    "quick-punch": {"single_core_idea": 1.25, "contrast_tension": 0.20},
    "cognitive-reset": {"single_core_idea": 0.75, "emotional_weight": 0.40},
    "data-walkthrough": {"data_presence": 1.30, "visual_decomposability": 0.80},
    "narrative-pivot": {"contrast_tension": 1.00, "emotional_weight": 0.55},
    "zoom-and-return": {"visual_decomposability": 1.15, "multi_facet": 0.60},
    "framework-expose": {"multi_facet": 0.95, "visual_decomposability": 0.85},
    "emotional-arc": {"emotional_weight": 1.35, "contrast_tension": 0.45},
}

ARC_BIAS: dict[str, dict[str, float]] = {
    "beginning": {"deep-dive": 0.45, "framework-expose": 0.45},
    "middle": {"contrast-pair": 0.35, "evidence-build": 0.35, "narrative-pivot": 0.25},
    "end": {"emotional-arc": 0.45, "zoom-and-return": 0.35},
}


class ClusterTemplateSelectionError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _template_index(template_library: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    templates = template_library.get("templates")
    if not isinstance(templates, list):
        raise ClusterTemplateSelectionError("invalid_template_library", "templates must be a list")
    index: Dict[str, Dict[str, Any]] = {}
    for template in templates:
        if isinstance(template, dict) and template.get("template_id"):
            index[str(template["template_id"])] = template
    return index


def _normalized_signal_map(content_signals: Mapping[str, float]) -> Dict[str, float]:
    normalized = {key: 0.0 for key in SIGNAL_KEYS}
    for key, value in content_signals.items():
        if key in SIGNAL_KEYS:
            normalized[key] = float(value)
    return normalized


def _top_signal_reasons(weights: Mapping[str, float], signals: Mapping[str, float], limit: int = 3) -> List[str]:
    scored: List[tuple[float, str]] = []
    for key, weight in weights.items():
        signal = float(signals.get(key, 0.0))
        contribution = signal * weight
        if contribution > 0:
            scored.append((contribution, key))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [f"{key}:{score:.2f}" for score, key in scored[:limit]]


def select_cluster_template(
    *,
    template_library: Mapping[str, Any],
    content_signals: Mapping[str, float],
    master_arc_phase: str = "middle",
    previous_template_ids: Sequence[str] = (),
    recent_pacing_profiles: Sequence[str] = (),
    force_template: str | None = None,
    exclude_templates: Sequence[str] = (),
    prefer_templates: Sequence[str] = (),
) -> Dict[str, Any]:
    index = _template_index(template_library)
    excludes = {str(item) for item in exclude_templates}
    prefer = {str(item) for item in prefer_templates}
    phase = str(master_arc_phase or "middle").strip().lower()
    signals = _normalized_signal_map(content_signals)

    if force_template:
        forced = str(force_template)
        if forced in excludes:
            raise ClusterTemplateSelectionError(
                "invalid_override",
                "force_template cannot also be excluded",
            )
        if forced not in index:
            raise ClusterTemplateSelectionError(
                "invalid_override",
                f"force_template not found in template library: {forced}",
            )
        winner = index[forced]
        return {
            "template_id": forced,
            "reasons": ["forced_by_operator"],
            "alternatives": [],
            "ranking": [
                {
                    "template_id": forced,
                    "score_breakdown": {
                        "content_fit": 0.0,
                        "variety_penalty": 0.0,
                        "pacing_penalty": 0.0,
                        "arc_bias": 0.0,
                        "preference_bonus": 0.0,
                        "final_score": 999.0,
                    },
                    "pacing_profile": winner.get("pacing_profile"),
                }
            ],
            "master_arc_phase": phase,
        }

    candidates = [tid for tid in index if tid not in excludes]
    if not candidates:
        raise ClusterTemplateSelectionError("no_candidates", "no selectable templates remain after exclusions")

    last_template = str(previous_template_ids[-1]) if previous_template_ids else None
    recent_pacing = list(recent_pacing_profiles[-2:])

    ranking: List[Dict[str, Any]] = []
    for tid in candidates:
        template = index[tid]
        weights = DEFAULT_SIGNAL_WEIGHTS.get(tid, {})
        content_fit = 0.0
        for signal_name, signal_weight in weights.items():
            content_fit += float(signals.get(signal_name, 0.0)) * float(signal_weight)

        variety_penalty = -0.60 if last_template and tid == last_template else 0.0

        pacing_profile = str(template.get("pacing_profile") or "")
        pacing_penalty = 0.0
        for recent in recent_pacing:
            if pacing_profile and pacing_profile == str(recent):
                pacing_penalty -= 0.35

        arc_bias = float(ARC_BIAS.get(phase, {}).get(tid, 0.0))
        preference_bonus = 0.25 if tid in prefer else 0.0
        final_score = content_fit + variety_penalty + pacing_penalty + arc_bias + preference_bonus

        ranking.append(
            {
                "template_id": tid,
                "score_breakdown": {
                    "content_fit": round(content_fit, 4),
                    "variety_penalty": round(variety_penalty, 4),
                    "pacing_penalty": round(pacing_penalty, 4),
                    "arc_bias": round(arc_bias, 4),
                    "preference_bonus": round(preference_bonus, 4),
                    "final_score": round(final_score, 4),
                },
                "pacing_profile": pacing_profile,
                "reasons": _top_signal_reasons(weights, signals),
            }
        )

    ranking.sort(key=lambda row: (row["score_breakdown"]["final_score"], row["template_id"]), reverse=True)
    winner = ranking[0]
    alternatives = ranking[1:3]
    return {
        "template_id": winner["template_id"],
        "reasons": winner["reasons"],
        "alternatives": [
            {
                "template_id": row["template_id"],
                "final_score": row["score_breakdown"]["final_score"],
                "why_lower": "lower total score",
            }
            for row in alternatives
        ],
        "ranking": ranking,
        "master_arc_phase": phase,
    }

