"""FR54 cache-hit-rate baseline measurement against Irene Pass 2 (Story 2a.2).

**This is the M1 ACCEPT-WITH-GAP closure test.** Activated 2026-04-24 by Story
2a.2 — the first real LLM-invoking specialist migration. Per the deferred-
inventory trigger, the un-skip happened when Irene's `_act` body replaced the
generator's passthrough with a real `chat.invoke(...)` call.

## Measurement protocol (per AC-D + MF1 + MF2 + MF5 + MF6)

1. **MF6 sanctum-lock pre-check** — assert sanctum dir is empty (count == 0)
   before any invocation. Empty-sanctum is the activation-baseline epoch
   per `docs/dev-guide/sanctum-reference-conventions.md §3`.
2. **MF2 prompt-token floor** — assert assembled prompt has `prompt_tokens >= 1024`
   in OpenAI usage metadata; named pytest.fail on sub-threshold (NOT a silent
   0% report).
3. **MF5 in-process N≥10** — invoke Irene's `_plan → _act` 10 times in-process
   (NOT subprocess) with byte-identical envelope input + identical
   `OPENAI_API_KEY` within a single test session.
4. **MF5 cache-metric source** — read `response.usage_metadata` from the
   OpenAI API response directly (NOT LangSmith trace parsing — that's AC-G's
   concern, not AC-D's).
5. **MF1 disposition rule** — report `median(cache_hit_rate[2:])` — median of
   invocations 2 through 10 (first invocation is always 0% — no prefix exists
   yet). Closure rule: median ≥ 60% → PASS. If median < 60% → story does NOT
   close; party-mode reconvenes before retry.
6. **MF6 sanctum-lock post-check** — re-assert sanctum count == 0. Drift
   invalidates the run.

## Auto-skip behavior

Tagged `@pytest.mark.llm_live`. Per `tests/conftest.py` Pass 2:
- `OPENAI_API_KEY` unset OR placeholder sentinel `sk-substrate-no-real-key-do-not-invoke`
  → test auto-skips with the "no real key" reason. Murat SF3 binding: the
  placeholder/skip path is exercised at T8 dual-path regression separately.
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any

import pytest

from app.models.state.cache_state import CacheState
from app.models.state.run_state import RunState
from app.specialists.irene.graph import SANCTUM_DIR, _act, _plan

# Synthetic Pass-2 envelope — fixed across all 10 invocations for
# byte-identical prompt-prefix delivery to OpenAI's prefix cache.
_PASS_2_ENVELOPE: dict[str, Any] = {
    "lesson_slug": "fr54-baseline-c1m1",
    "gary_slide_output": [
        {"slide_id": "s1", "slide_purpose": "intro", "title": "Welcome"},
        {"slide_id": "s2", "slide_purpose": "concept", "title": "Cell Membrane"},
        {"slide_id": "s3", "slide_purpose": "synthesis", "title": "Summary"},
    ],
    "perception_artifacts": [
        {"slide_id": "s1", "confidence": "HIGH", "elements": ["title-banner"]},
        {"slide_id": "s2", "confidence": "HIGH", "elements": ["diagram", "labels"]},
        {"slide_id": "s3", "confidence": "HIGH", "elements": ["bullet-list"]},
    ],
    "narration_profile_controls": {
        "bridge_cadence_minutes": 2,
        "visual_references_per_slide": 2,
    },
}


def _sanctum_file_count(sanctum_dir: Path = SANCTUM_DIR) -> int:
    """Count files in sanctum dir for MF6 lock-and-verify protocol."""
    if not sanctum_dir.exists():
        return 0
    return sum(1 for _ in sanctum_dir.rglob("*") if _.is_file())


@pytest.mark.llm_live
def test_irene_pass_2_cache_hit_rate_meets_60_percent_median(tmp_path: Path) -> None:
    """FR54 cache-hit-rate baseline — closes M1 ACCEPT-WITH-GAP at story 2a.2 done flip."""
    # MF6 sanctum-lock pre-check
    pre_count = _sanctum_file_count()
    assert pre_count == 0, (
        f"AC-D / MF6: sanctum dir {SANCTUM_DIR} must be empty (count == 0) before "
        f"the 10-invocation cache window. Found {pre_count} files. Per D2 SYNTHESIS "
        f"verdict, 2a.2 is the activation-baseline epoch. Archive any populated "
        f"content to `_bmad/memory/_archive/` before re-running."
    )

    # dp-v1.1 grounding: Pass 2 is fail-loud on corpus + lesson plan; the
    # bundle is fixed for the whole 10-invocation window so the prompt
    # prefix stays byte-identical (the corpus TEXT is embedded, not the path).
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    (bundle_dir / "extracted.md").write_text(
        "# Source corpus\n\nCell membrane structure and transport.\n",
        encoding="utf-8",
    )
    payload_blob = json.dumps(
        {
            **_PASS_2_ENVELOPE,
            "bundle_reference": str(bundle_dir),
            "lesson_plan": {"title": "Cell Membrane", "objectives": ["obj-1"]},
        },
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
    )
    cache_hit_rates: list[float] = []
    prompt_tokens_seen: list[int] = []

    for invocation_idx in range(10):
        # MF6 per-invocation guard
        mid_count = _sanctum_file_count()
        assert mid_count == 0, (
            f"AC-D / MF6: sanctum drift detected during cache window "
            f"(invocation {invocation_idx + 1}); count == {mid_count} "
            f"(expected 0). Run invalidated."
        )

        state = RunState(
            graph_version="v0.1-stub",
            temperature=0.0,
            cache_state=CacheState(cache_prefix=payload_blob, entries_count=0),
        )
        plan_update = _plan(state)
        state = state.model_copy(update=plan_update)
        act_update = _act(state)
        output = json.loads(act_update["cache_state"]["cache_prefix"])
        usage = output.get("usage") or {}
        prompt_tokens = usage.get("input_tokens") or usage.get("prompt_tokens") or 0
        # G6 EH-SF4 fix: usage_metadata cached-token shape varies across the OpenAI
        # SDK surfaces. Extract from all four documented forms; first non-zero wins:
        #   1. LangChain UsageMetadata: usage["input_token_details"]["cache_read"]
        #   2. Responses API: usage["input_tokens_details"]["cached_tokens"]
        #   3. Chat Completions raw: usage["prompt_tokens_details"]["cached_tokens"]
        #   4. Legacy chat completions flat: usage["cache_read_input_tokens"]
        cached_tokens = (
            (usage.get("input_token_details") or {}).get("cache_read")
            or (usage.get("input_tokens_details") or {}).get("cached_tokens")
            or (usage.get("prompt_tokens_details") or {}).get("cached_tokens")
            or usage.get("cache_read_input_tokens")
            or 0
        )

        prompt_tokens_seen.append(prompt_tokens)
        hit_rate = cached_tokens / prompt_tokens if prompt_tokens > 0 else 0.0
        cache_hit_rates.append(hit_rate)

    # MF6 post-run check
    post_count = _sanctum_file_count()
    assert post_count == 0, (
        f"AC-D / MF6: sanctum drift detected post-run (count == {post_count}; "
        f"expected 0). Run invalidated."
    )

    # MF2 prompt-token floor pre-check (assert AFTER all 10 invocations land)
    if not prompt_tokens_seen or max(prompt_tokens_seen) < 1024:
        pytest.fail(
            f"AC-D / MF2: max prompt_tokens across 10 invocations = "
            f"{max(prompt_tokens_seen) if prompt_tokens_seen else 0} below 1024 "
            f"floor. The Pass-2 reference bundle is too short to qualify for "
            f"OpenAI prefix cache. Cannot close M1 ACCEPT-WITH-GAP at current "
            f"envelope size; investigate prompt assembly."
        )

    # MF1 disposition rule: median of invocations 2 through 10 (slice [1:])
    median_post_warmup = statistics.median(cache_hit_rates[1:])

    # Diagnostic output — surfaced even on PASS so operator can paste into
    # Completion Notes per AC-D evidence template.
    print("\n=== AC-D / FR54 CACHE-HIT-RATE BASELINE (Story 2a.2) ===")
    print(f"Sanctum count: pre={pre_count} post={post_count} (MF6 OK)")
    print(f"Prompt tokens per invocation: {prompt_tokens_seen}")
    print("Cache hit rate per invocation (0..9):")
    for idx, rate in enumerate(cache_hit_rates):
        marker = "  (cold)" if idx == 0 else ""
        print(f"  inv[{idx + 1:2d}] = {rate * 100:6.2f}%{marker}")
    print(f"Median of inv 2-10 (post-warmup): {median_post_warmup * 100:.2f}%")
    print(f"MF1 disposition rule: median >= 60% --> PASS. Got {median_post_warmup * 100:.2f}%.")
    print("=== END AC-D EVIDENCE BLOCK ===\n")

    assert median_post_warmup >= 0.60, (
        f"AC-D / MF1: median cache-hit-rate across invocations 2-10 = "
        f"{median_post_warmup * 100:.2f}% below the 60% closure threshold. "
        f"Story does NOT close. Party-mode reconvenes before retry. "
        f"Per-invocation rates: {[round(r * 100, 2) for r in cache_hit_rates]}"
    )
