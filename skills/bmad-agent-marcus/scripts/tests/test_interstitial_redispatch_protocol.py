from __future__ import annotations

from importlib import util
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = ROOT / "skills" / "bmad-agent-marcus" / "scripts" / "interstitial_redispatch_protocol.py"


def _load_module():
    spec = util.spec_from_file_location("interstitial_redispatch_protocol", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = _load_module()
execute_interstitial_redispatch = mod.execute_interstitial_redispatch
build_tightened_redispatch_prompt = mod.build_tightened_redispatch_prompt
reset_interstitial_counters_for_cluster_redispatch = mod.reset_interstitial_counters_for_cluster_redispatch
InterstitialRedispatchError = mod.InterstitialRedispatchError


def _bundle() -> dict[str, Any]:
    return {
        "cluster_id": "c1",
        "cluster_interstitial_count": 2,
        "head_slide": {
            "slide_id": "s-head",
            "theme_id": "theme-123",
            "style_parameters": {"tone": "clean"},
            "text": "Head context coherent baseline.",
        },
        "interstitials": [
            {"slide_id": "s-int-1", "prompt": "Original interstitial prompt one.", "asset_path": "old-1.png", "re_dispatch_count": 0},
            {"slide_id": "s-int-2", "prompt": "Original interstitial prompt two.", "asset_path": "old-2.png", "re_dispatch_count": 0},
        ],
    }


def _coherence_report() -> dict[str, Any]:
    return {
        "head_perception": {
            "palette_hex": ["#112233", "#abcdef"],
            "font_families": ["Inter", "Source Sans 3"],
            "background_treatment": "subtle radial gradient",
        }
    }


def test_tightened_prompt_includes_perception_constraints():
    prompt = build_tightened_redispatch_prompt(
        "Base prompt.",
        {
            "palette_hex": ["#112233"],
            "font_families": ["Inter"],
            "background_treatment": "flat dark",
        },
    )
    assert "#112233" in prompt
    assert "Inter" in prompt
    assert "flat dark" in prompt


def test_targeted_redispatch_updates_only_failed_interstitial():
    captured_payload: dict[str, Any] = {}

    def _dispatch(payload: dict[str, Any]) -> dict[str, Any]:
        captured_payload.update(payload)
        return {
            "session_id": "sess-1",
            "png_path": "new-int-2.png",
            "replacement_output": {"slide_id": "s-int-2", "text": "coherent replacement"},
        }

    def _validate(_head: dict[str, Any], _replacement: dict[str, Any]) -> dict[str, Any]:
        return {"decision": "pass", "score": 1.0, "violations": []}

    result = execute_interstitial_redispatch(
        cluster_bundle=_bundle(),
        interstitial_id="s-int-2",
        coherence_report=_coherence_report(),
        dispatch_single_interstitial=_dispatch,
        validate_replacement=_validate,
    )
    updated = result["bundle"]
    assert result["status"] == "pass"
    assert captured_payload["theme_id"] == "theme-123"
    assert captured_payload["style_parameters"]["tone"] == "clean"
    assert "#112233" in captured_payload["prompt"]
    assert "Inter" in captured_payload["prompt"]
    assert "subtle radial gradient" in captured_payload["prompt"]
    assert updated["interstitials"][0]["asset_path"] == "old-1.png"
    assert updated["interstitials"][1]["asset_path"] == "new-int-2.png"
    assert updated["interstitials"][1]["re_dispatch_count"] == 1


def test_circuit_breaker_after_two_attempts_with_accept_fallback():
    bundle = _bundle()
    bundle["interstitials"][1]["re_dispatch_count"] = 2

    def _dispatch(_payload: dict[str, Any]) -> dict[str, Any]:
        raise AssertionError("dispatch should not run when circuit breaker already tripped")

    def _validate(_head: dict[str, Any], _replacement: dict[str, Any]) -> dict[str, Any]:
        raise AssertionError("validate should not run when circuit breaker already tripped")

    result = execute_interstitial_redispatch(
        cluster_bundle=bundle,
        interstitial_id="s-int-2",
        coherence_report=_coherence_report(),
        dispatch_single_interstitial=_dispatch,
        validate_replacement=_validate,
        fallback="accept-as-is",
    )
    target = result["bundle"]["interstitials"][1]
    assert result["status"] == "circuit_breaker"
    assert target["fallback_decision"] == "accept-as-is"
    assert target["accepted_with_warning"] is True


def test_drop_from_cluster_fallback_updates_cluster_count():
    bundle = _bundle()

    def _dispatch(_payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "session_id": "sess-2",
            "png_path": "new-int-2.png",
            "replacement_output": {"slide_id": "s-int-2", "text": "still conflict present"},
        }

    def _validate(_head: dict[str, Any], _replacement: dict[str, Any]) -> dict[str, Any]:
        return {"decision": "fail", "score": 0.2, "violations": ["conflict_detected:s-int-2"]}

    bundle["interstitials"][1]["re_dispatch_count"] = 1
    result = execute_interstitial_redispatch(
        cluster_bundle=bundle,
        interstitial_id="s-int-2",
        coherence_report=_coherence_report(),
        dispatch_single_interstitial=_dispatch,
        validate_replacement=_validate,
        fallback="drop-from-cluster",
    )
    updated = result["bundle"]
    ids = [item["slide_id"] for item in updated["interstitials"]]
    assert result["status"] == "circuit_breaker"
    assert "s-int-2" not in ids
    assert updated["cluster_interstitial_count"] == 1


def test_full_cluster_redispatch_resets_counters():
    bundle = _bundle()
    bundle["interstitials"][0]["re_dispatch_count"] = 2
    bundle["interstitials"][0]["last_re_dispatch_session_id"] = "sess-a"
    bundle["interstitials"][1]["re_dispatch_count"] = 1
    reset = reset_interstitial_counters_for_cluster_redispatch(bundle)
    assert reset["interstitials"][0]["re_dispatch_count"] == 0
    assert "last_re_dispatch_session_id" not in reset["interstitials"][0]
    assert reset["interstitials"][1]["re_dispatch_count"] == 0


def test_invalid_fallback_raises():
    bundle = _bundle()
    bundle["interstitials"][1]["re_dispatch_count"] = 2

    with pytest.raises(InterstitialRedispatchError) as exc:
        execute_interstitial_redispatch(
            cluster_bundle=bundle,
            interstitial_id="s-int-2",
            coherence_report=_coherence_report(),
            dispatch_single_interstitial=lambda _: {},
            validate_replacement=lambda _a, _b: {},
            fallback="not-a-fallback",
        )
    assert exc.value.code == "invalid_fallback"

