"""Compositor consumed-payload contract (audio-arc, 2026-06-12).

Every key the Compositor's deterministic assembly reads from its envelope
payload. Ratchet-D asserts node 14's dependency_projections use ONLY keys
declared here. Pre-grounded by party consensus (John: "convicted by
construction" — the compositor was written before dp-v1 projections
existed, so its inputs were KNOWN absent).
"""

from __future__ import annotations

CONSUMED_PAYLOAD_KEYS: frozenset[str] = frozenset(
    {
        "BUNDLE_PATH",
        "assembly_guide_path",
        "audio_bed_paths",
        "audio_paths",
        "bundle_path",
        "compositor_invocation",
        "gary_slide_output",
        "motion_asset_paths",
        "motion_receipts",
        "run_id",
        "visuals",
    }
)

__all__ = ["CONSUMED_PAYLOAD_KEYS"]
