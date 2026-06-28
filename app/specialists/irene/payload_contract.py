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
        "perception_artifacts",
        "slide_briefs",
        # P5 directed-voice arc Step 2 (2026-06-27): optional delivery-metadata
        # inputs consumed by the post-freeze voice-direction annotation pass.
        # Both are read ONLY when MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE is set;
        # absent ⇒ conservative built-in default (flag OFF ⇒ not read at all).
        "voice_direction_defaults",
        "voice_direction_overrides",
        # P5-S2 (Step 6, 2026-06-27): the orchestrator-projected per-SLIDE
        # role-derived voice seed table (slide-ordinal → voice_direction). Threaded
        # via runner_supplied_payload (NOT a manifest projection); read ONLY when
        # MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE is set + an enrichment card is
        # present. Aligned to this pass's segment ids by the pinned slide-ordinal
        # join; absent ⇒ conservative built-in default (byte-identical).
        "role_derived_voice_by_slide",
    }
)

__all__ = ["CONSUMED_PAYLOAD_KEYS"]
