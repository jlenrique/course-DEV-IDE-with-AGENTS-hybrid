"""Kira consumed-payload contract (Ratchet-D vocabulary).

Published 2026-06-25 (S1 motion-restore): kira 07E sat in Ratchet-D's
quarantine (``("07E","upstream_output","kira")``) with no published contract,
which is the consumer-side half of why the motion data plane went unaudited —
a starved 07E could not be caught by the manifest-vocabulary ratchet because
kira declared no vocabulary to check edges against. Keys kira's act actually
reads from the dispatched payload (``decode_envelope_payload`` ->
``generate_motion_from_plan``):

- ``motion_plan`` — the explicit per-slide plan dict ({slides: [...]}); the
  primary motion-producer-edge input key (projected from the motion-plan
  producer once it lands — see deferred motion data-plane arc).
- ``motion_plan_path`` — filesystem path to a motion_plan.yaml (operator /
  replay path).
- ``slides`` — top-level slide list (legacy/alt plan delivery).
- ``bundle_path`` — run bundle root for motion/ receipt + inspection artifacts.
- ``upstream_output`` — whole-dict upstream delivery (the pre-S1 dependency
  edge from quinn_r; tolerated but not a motion plan).
"""

from __future__ import annotations

CONSUMED_PAYLOAD_KEYS: frozenset[str] = frozenset(
    {
        "bundle_path",
        "motion_plan",
        "motion_plan_path",
        "slides",
        "upstream_output",
    }
)

__all__ = ["CONSUMED_PAYLOAD_KEYS"]
