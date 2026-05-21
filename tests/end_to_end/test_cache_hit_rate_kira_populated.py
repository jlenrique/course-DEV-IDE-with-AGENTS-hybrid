from __future__ import annotations

import hashlib
import json
import statistics
from pathlib import Path
from typing import Any

import openai
import pytest

from app.models.state.cache_state import CacheState
from app.models.state.run_state import RunState
from app.specialists.kira.graph import SANCTUM_DIR, _act, _plan

BASELINE_TOKENS_2A2_EMPTY_SANCTUM = 9399

_KIRA_ENVELOPE: dict[str, Any] = {
    "slide_id": "fr54-kira-001",
    "visual_file": "artifacts/segment-001.png",
    "motion_goal": "Slow cinematic push-in over annotated diagram with subtle depth.",
}


def _sanctum_hash_lines(sanctum_dir: Path = SANCTUM_DIR) -> list[str]:
    if not sanctum_dir.exists() or not sanctum_dir.is_dir():
        return []
    lines: list[str] = []
    files = sorted(
        (p for p in sanctum_dir.rglob("*") if p.is_file()),
        key=lambda p: p.relative_to(sanctum_dir).as_posix(),
    )
    for file_path in files:
        rel = file_path.relative_to(sanctum_dir).as_posix()
        digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
        lines.append(f"{rel}\t{digest}")
    return lines


@pytest.mark.llm_live
def test_kira_populated_sanctum_cache_hit_rate_and_cost() -> None:
    baseline_manifest = _sanctum_hash_lines()
    # EH-15 pre-condition: this test is the populated-and-locked steady-state
    # epoch exercise per docs/dev-guide/sanctum-reference-conventions.md §3.
    # If the sanctum dir is absent or empty, the drift assertion would pass
    # vacuously ([] == []) and the test would silently report empty-sanctum
    # behavior under a "populated" name. Skip explicitly so the operator sees
    # that ceremony has not yet fired; AC-D Completion Notes annotates the
    # graceful-degrade case separately.
    if not baseline_manifest:
        pytest.skip(
            "AC-D: _bmad/memory/bmad-agent-kling/ is empty or absent; "
            "operator has not run first-breath ceremony for the populated-and-locked "
            "epoch. Populated-sanctum exercise deferred until ceremony fires."
        )
    payload_blob = json.dumps(
        _KIRA_ENVELOPE, sort_keys=True, ensure_ascii=True, separators=(",", ":")
    )
    cache_hit_rates: list[float] = []
    prompt_tokens_seen: list[int] = []

    for idx in range(10):
        current_manifest = _sanctum_hash_lines()
        assert current_manifest == baseline_manifest, (
            f"AC-D: sanctum drift detected before invocation {idx + 1}; "
            "run invalidated"
        )
        state = RunState(
            graph_version="v0.1-stub",
            temperature=0.0,
            cache_state=CacheState(cache_prefix=payload_blob, entries_count=0),
        )
        state = state.model_copy(update=_plan(state))
        try:
            output = json.loads(_act(state)["cache_state"]["cache_prefix"])
        except openai.NotFoundError as exc:
            pytest.skip(f"Model not available in this environment: {exc}")
        usage = output.get("usage") or {}
        prompt_tokens = usage.get("input_tokens") or usage.get("prompt_tokens") or 0
        cached_tokens = (
            (usage.get("input_token_details") or {}).get("cache_read")
            or (usage.get("input_tokens_details") or {}).get("cached_tokens")
            or (usage.get("prompt_tokens_details") or {}).get("cached_tokens")
            or usage.get("cache_read_input_tokens")
            or 0
        )
        prompt_tokens_seen.append(prompt_tokens)
        cache_hit_rates.append(cached_tokens / prompt_tokens if prompt_tokens > 0 else 0.0)

    assert _sanctum_hash_lines() == baseline_manifest, "AC-D: sanctum drift post-run"
    if not prompt_tokens_seen or max(prompt_tokens_seen) < 1024:
        pytest.fail(
            "AC-D: prefix below 1024 OpenAI threshold; Kira envelope + sanctum + "
            "system message too short for provider prefix cache"
        )

    median_post_warmup = statistics.median(cache_hit_rates[1:])
    steady_state_tokens = prompt_tokens_seen[0]
    sanctum_context_cost = steady_state_tokens - BASELINE_TOKENS_2A2_EMPTY_SANCTUM
    print("\n=== AC-D / FR54 KIRA POPULATED-SANCTUM EVIDENCE ===")
    print(f"sanctum_files={len(baseline_manifest)}")
    print(f"prompt_tokens={prompt_tokens_seen}")
    print(f"median_hit_rate_inv2_10={median_post_warmup * 100:.2f}%")
    print(f"steady_state_tokens={steady_state_tokens}")
    print(f"baseline_tokens={BASELINE_TOKENS_2A2_EMPTY_SANCTUM}")
    print(f"sanctum_context_cost={sanctum_context_cost}")
    print("=== END EVIDENCE ===\n")
    assert median_post_warmup >= 0.60, (
        f"AC-D: median cache-hit-rate invocations 2-10 = {median_post_warmup * 100:.2f}% "
        "below 60% threshold"
    )
