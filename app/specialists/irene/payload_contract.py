"""Irene (Pass 2) consumed-payload contract (dp-v1.1, party consensus 2026-06-12).

Declares every key Irene's Pass-2 act body reads from its envelope payload.
The manifest contract lockstep test (Ratchet-D) asserts that node 08's
dependency_projections use ONLY keys declared here. The defect this pins:
Trial-3 cycle-4 node 08 received ``input keys: cache_prefix`` only, so
Pass 2 authored a sepsis narration from her bundled L5 exemplars — the
fourth ungrounded-prompt instance (cycle-2 irene_pass1/cd were the second
and third).

Lives in its own module per the established pattern (irene_pass1, quinn_r):
the contract is import-surface, re-exported through the consumer's graph
module so it participates in the import graph (Amelia a.2).
"""

from __future__ import annotations

CONSUMED_PAYLOAD_KEYS: frozenset[str] = frozenset(
    {
        "bundle_reference",
        "gary_slide_output",
        "lesson_plan",
        "pass_phase",
        "slide_briefs",
    }
)

__all__ = ["CONSUMED_PAYLOAD_KEYS"]
