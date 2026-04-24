"""FR54 cache hit rate baseline scaffold (AC-1.6-E).

M1 acceptance requires ≥60% cache hit rate on the second invocation of the
pipeline. In Slab 1, all specialists are passthroughs (no LLM calls), so there
is nothing to cache. This test lands the measurement fixture + plumbing so
Slab 2's first specialist migration has an existing harness to re-enable; the
actual ≥60% assertion is skipped until real LLM-invoking specialists land.

Re-enable trigger: when the first Slab 2 specialist story lands a real LLM
call in a passthrough slot, flip the `pytest.skip` in this file to an active
assertion parsing LangSmith span metadata for cache-hit status.
"""

from __future__ import annotations

import pytest

from app.smoke_test import run_full_smoke


@pytest.mark.skip(
    reason=(
        "FR54 cache-hit baseline deferred: Slab 1 specialists are passthroughs (no LLM "
        "calls). Re-enable when the first Slab 2 specialist lands a real LLM call — "
        "parse LangSmith span metadata for cache-hit status and assert ≥60% on the "
        "second run across LLM-invoking nodes."
    )
)
def test_cache_hit_rate_at_least_sixty_percent_on_second_run() -> None:
    # Scaffold — runs the pipeline twice for when the real specialists land.
    first = run_full_smoke()
    second = run_full_smoke()
    # Placeholder assertion; real implementation parses span-level cache metadata.
    assert first.keys() == second.keys()
