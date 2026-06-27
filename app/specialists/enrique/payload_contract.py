"""Enrique (ElevenLabs) consumed-payload contract (audio-arc, 2026-06-12).

Every key Enrique's act body reads from its envelope payload. Ratchet-D
asserts node 12's dependency_projections use ONLY keys declared here. The
defect this pins: cycle-5 nodes 11/11B/12 received ``cache_prefix`` only —
zero audio synthesized, voice selection silently defaulted (fifth/sixth
ungrounded-input instances).
"""

from __future__ import annotations

CONSUMED_PAYLOAD_KEYS: frozenset[str] = frozenset(
    {
        "bundle_path",
        "candidate_voices",
        "cost_per_1k_chars",
        "legacy_dispatch_probe",
        "locked_manifest_path",
        "manifest_path",
        "narration_script",
        "operator_id",
        "rationale",
        "segment_manifest_deltas",
        "segments",
        "selected_voice_id",
        # P5 directed-voice (Step 4): tier-3 default settings consumed from the
        # Pass-2 envelope when the directed-voice flag is ON. Per-segment
        # `voice_direction` rides INSIDE each `segments` row (already declared),
        # so the only NEW top-level key Enrique reads is this defaults block.
        "voice_direction_defaults",
        "voice_preview_candidate_count",
        "voice_selection",
    }
)

__all__ = ["CONSUMED_PAYLOAD_KEYS"]
