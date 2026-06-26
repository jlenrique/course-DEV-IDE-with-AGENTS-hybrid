"""motion_planner consumed-payload contract (Ratchet-D vocabulary).

Published 07D.5 (composition-catalog B2, 2026-06-26): the deterministic
motion-plan producer reads the authorized winner deck (quinn_r) and projects a
per-slide ``motion_plan`` into kira's consumed shape. Declaring this vocabulary
lets the manifest-edge Ratchet-D test (``tests/contracts/
test_manifest_payload_contracts.py``) validate the 07D.5 dependency edge against
the keys this producer actually reads:

- ``upstream_output`` — the quinn_r authorized winner deck delivered whole under
  the manifest ``dependencies: {upstream_output: quinn_r}`` edge; the producer
  extracts ``authorized_storyboard`` / ``authorized_slides`` from it.
- ``authorized_storyboard`` — an explicit authorized-storyboard dict
  (dev/replay path), if delivered directly instead of nested under
  ``upstream_output``.
- ``motion_designations`` — optional Gate-2M designation override; when absent
  the producer auto-designates from the Epic-14 recommendation engine.
- ``perception_artifacts`` — optional per-slide perception (vision) the producer
  may consult when present.
- ``bundle_path`` — run bundle root (slide-image resolution, replay parity).
"""

from __future__ import annotations

CONSUMED_PAYLOAD_KEYS: frozenset[str] = frozenset(
    {
        "authorized_storyboard",
        "bundle_path",
        "motion_designations",
        "perception_artifacts",
        "upstream_output",
    }
)

__all__ = ["CONSUMED_PAYLOAD_KEYS"]
