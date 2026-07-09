"""Irene Pass-1 consumed-payload contract (Ratchet-D vocabulary).

Published 2026-06-12 (Trial-3 cycle-3 error-pause follow-through): the 04A
edge sat in Ratchet-D's quarantine and its bill arrived as a confabulated
lesson plan. Keys the act actually reads:

- ``mode`` / ``pass_phase`` / ``irene_mode`` — pass-1 mode enforcement
- ``run_id`` / ``runs_root`` — artifact placement
- ``upstream_output`` — whole-dict upstream delivery (texas bundle metadata
  at §04A plan creation; the latest irene-pass1 plan at §05/§05B refinement)
- ``bundle_reference`` — S4 key projection from texas (corpus access for
  the fidelity passes; resolved by app.specialists.source_bundle)
- ``min_cluster_floor`` — Leg-C R3 scripted floor (RUNNER CONTEXT, threaded by
  ``_runner_payload_for_specialist``); consumed POST-HOC by
  ``app.specialists.irene_pass1.cluster_floor`` and STRIPPED from the
  LLM-visible prompt (D-0)
- ``planning_context`` — optional purpose/audience/LOs/source assessment
  (RUNNER CONTEXT from run_dir artifacts); advisory framing only — corpus
  remains the ONLY topic basis. Surfaced in a labeled prompt section; also
  remains in the envelope JSON for receipt/audit.
"""

from __future__ import annotations

CONSUMED_PAYLOAD_KEYS: frozenset[str] = frozenset(
    {
        "bundle_reference",
        "irene_mode",
        "min_cluster_floor",
        "mode",
        "pass_phase",
        "planning_context",
        "run_id",
        "runs_root",
        "upstream_output",
    }
)

__all__ = ["CONSUMED_PAYLOAD_KEYS"]
