"""
Interstitial re-dispatch protocol (Story 21-5).

Implements targeted interstitial repair driven by coherence findings, including:
- perception-informed prompt tightening
- single-interstitial re-dispatch contract
- circuit breaker and operator fallbacks
- full cluster re-dispatch counter reset helper
"""

from __future__ import annotations

import copy
from typing import Any, Callable, Dict, List, Tuple

MAX_REDISPATCH_ATTEMPTS = 2


class InterstitialRedispatchError(ValueError):
    """Structured error type with machine-readable codes."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def extract_head_perception_constraints(
    coherence_report: Dict[str, Any],
) -> Dict[str, Any]:
    """Extract prompt-tightening constraints from head-slide perception results."""
    head = coherence_report.get("head_perception") or {}
    palette = head.get("palette_hex") or []
    fonts = head.get("font_families") or []
    background = head.get("background_treatment") or "unspecified"
    return {
        "palette_hex": [str(v) for v in palette if str(v).strip()],
        "font_families": [str(v) for v in fonts if str(v).strip()],
        "background_treatment": str(background),
    }


def build_tightened_redispatch_prompt(original_prompt: str, constraints: Dict[str, Any]) -> str:
    """Append explicit perception constraints to narrow generative variance."""
    palette = ", ".join(constraints.get("palette_hex") or []) or "none provided"
    fonts = ", ".join(constraints.get("font_families") or []) or "none provided"
    background = constraints.get("background_treatment") or "unspecified"
    additions = (
        "\n\nRe-dispatch constraints from head-slide perception:\n"
        f"- Use explicit palette hex values: {palette}\n"
        f"- Use detected font families: {fonts}\n"
        f"- Match background treatment: {background}\n"
    )
    return f"{original_prompt.rstrip()}{additions}"


def _find_interstitial_index(interstitials: List[Dict[str, Any]], slide_id: str) -> int:
    for idx, item in enumerate(interstitials):
        if str(item.get("slide_id")) == slide_id:
            return idx
    raise InterstitialRedispatchError(
        "missing_required_field",
        f"interstitial not found: {slide_id}",
    )


def _apply_fallback(
    *,
    bundle: Dict[str, Any],
    interstitial_idx: int,
    fallback: str,
) -> Dict[str, Any]:
    interstitial = bundle["interstitials"][interstitial_idx]
    if fallback == "accept-as-is":
        interstitial["fallback_decision"] = "accept-as-is"
        interstitial["accepted_with_warning"] = True
        return bundle
    if fallback == "replace-with-pace-reset":
        interstitial["fallback_decision"] = "replace-with-pace-reset"
        interstitial["asset_path"] = "pace-reset-placeholder.png"
        interstitial["pace_reset_applied"] = True
        return bundle
    if fallback == "drop-from-cluster":
        interstitial["fallback_decision"] = "drop-from-cluster"
        bundle["interstitials"].pop(interstitial_idx)
        bundle["cluster_interstitial_count"] = max(
            0,
            int(bundle.get("cluster_interstitial_count", 0)) - 1,
        )
        return bundle
    raise InterstitialRedispatchError("invalid_fallback", f"unsupported fallback: {fallback}")


def execute_interstitial_redispatch(
    *,
    cluster_bundle: Dict[str, Any],
    interstitial_id: str,
    coherence_report: Dict[str, Any],
    dispatch_single_interstitial: Callable[[Dict[str, Any]], Dict[str, Any]],
    validate_replacement: Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]],
    fallback: str = "accept-as-is",
) -> Dict[str, Any]:
    """Run targeted interstitial re-dispatch and return updated bundle/report."""
    bundle = copy.deepcopy(cluster_bundle)
    interstitials = bundle.get("interstitials")
    if not isinstance(interstitials, list):
        raise InterstitialRedispatchError(
            "missing_required_field",
            "cluster_bundle.interstitials must be a list",
        )
    idx = _find_interstitial_index(interstitials, interstitial_id)
    target = interstitials[idx]
    current_count = int(target.get("re_dispatch_count", 0))
    if current_count >= MAX_REDISPATCH_ATTEMPTS:
        bundle = _apply_fallback(bundle=bundle, interstitial_idx=idx, fallback=fallback)
        return {"status": "circuit_breaker", "bundle": bundle, "validation": None}

    constraints = extract_head_perception_constraints(coherence_report)
    original_prompt = str(target.get("prompt") or "").strip()
    if not original_prompt:
        raise InterstitialRedispatchError(
            "missing_required_field",
            f"prompt is required for interstitial: {interstitial_id}",
        )
    head = bundle.get("head_slide") or {}
    dispatch_payload = {
        "slide_id": interstitial_id,
        "prompt": build_tightened_redispatch_prompt(original_prompt, constraints),
        "theme_id": head.get("theme_id"),
        "style_parameters": head.get("style_parameters") or {},
    }
    dispatch_result = dispatch_single_interstitial(dispatch_payload)
    session_id = dispatch_result.get("session_id")
    png_path = dispatch_result.get("png_path")
    replacement = dispatch_result.get("replacement_output") or {}
    if not session_id or not png_path:
        raise InterstitialRedispatchError(
            "invalid_output_format",
            "dispatch result must include session_id and png_path",
        )

    target["asset_path"] = str(png_path)
    target["re_dispatch_count"] = current_count + 1
    target["last_re_dispatch_session_id"] = str(session_id)

    head_output = {
        "slide_id": str(head.get("slide_id") or ""),
        "text": str(head.get("text") or ""),
    }
    validation = validate_replacement(head_output, replacement)
    if validation.get("decision") == "pass":
        return {"status": "pass", "bundle": bundle, "validation": validation}

    if int(target.get("re_dispatch_count", 0)) >= MAX_REDISPATCH_ATTEMPTS:
        bundle = _apply_fallback(bundle=bundle, interstitial_idx=idx, fallback=fallback)
        return {"status": "circuit_breaker", "bundle": bundle, "validation": validation}
    return {"status": "retry_available", "bundle": bundle, "validation": validation}


def reset_interstitial_counters_for_cluster_redispatch(cluster_bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Reset interstitial re-dispatch counters when operator chooses full cluster re-dispatch."""
    bundle = copy.deepcopy(cluster_bundle)
    interstitials = bundle.get("interstitials")
    if not isinstance(interstitials, list):
        raise InterstitialRedispatchError(
            "missing_required_field",
            "cluster_bundle.interstitials must be a list",
        )
    for item in interstitials:
        item["re_dispatch_count"] = 0
        item.pop("last_re_dispatch_session_id", None)
    return bundle

