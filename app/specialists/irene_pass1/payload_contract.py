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
"""

from __future__ import annotations

CONSUMED_PAYLOAD_KEYS: frozenset[str] = frozenset(
    {
        "bundle_reference",
        "irene_mode",
        "mode",
        "pass_phase",
        "run_id",
        "runs_root",
        "upstream_output",
    }
)

__all__ = ["CONSUMED_PAYLOAD_KEYS"]
