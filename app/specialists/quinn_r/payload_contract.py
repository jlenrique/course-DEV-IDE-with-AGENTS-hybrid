"""Quinn-R consumed-payload contract (S1, SCP 2026-06-11 segment-data-plane).

Declares every key Quinn-R's act body reads from its envelope payload.
The manifest contract lockstep test (Ratchet-D) asserts that any manifest
dependency edge targeting quinn-r uses ONLY keys declared here — the
vocabulary fork this pins: node 07B declared ``upstream_output`` while the
act body read ``slides``, so Quinn-R approved placeholder slides it never
received in Trial-3 attempt-4.

Lives in its own module (not _act.py) because the act body carries a
LOC-budget guard; the contract is import-surface, not act logic.
"""

from __future__ import annotations

CONSUMED_PAYLOAD_KEYS: frozenset[str] = frozenset(
    {
        "artifact_path",
        "gate_id",
        "gate_phase",
        "modality",
        "motion_assets",
        "narration_profile_controls",
        "narration_segments",
        "runs_root",
        "slides",
        "storyboard",
        "vtt_text",
        "wpm_tolerance",
    }
)

__all__ = ["CONSUMED_PAYLOAD_KEYS"]
