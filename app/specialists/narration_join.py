"""Shared narration join: Pass-2 narration_script ⋈ deltas ⋈ slide ids.

Audio-segment arc (party consensus 2026-06-12, Winston Q1): the storyboard-B
publisher, Enrique's audio synthesis, and Quinn-R's G5 pre-composition QA
must all agree on the SAME join policy ("slide_id = first non-empty
visual_reference perception_source; narration_text joined by segment id")
or QA validates a different join than the one that paid for audio. This
module is the ONLY home of that policy; an import-identity pin enforces
that all three consumers route through it.

Pure function, no I/O, no raising — starvation semantics belong to callers
(the publisher writes a file; enrique/G5 raise typed dispatch errors).
"""

from __future__ import annotations

from typing import Any


def join_narration_segments(
    narration_script: list[dict[str, Any]] | None,
    segment_manifest_deltas: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    """Return joined segment rows; [] on empty/missing inputs.

    Row shape: {segment_id, slide_id, narration_text, timing_role,
    content_density, visual_detail_load, duration_rationale, bridge_type,
    behavioral_intent}. Deltas with no non-empty perception_source are
    dropped (callers decide whether that is an error).
    """
    text_by_id: dict[str, str] = {}
    for seg in narration_script if isinstance(narration_script, list) else []:
        if isinstance(seg, dict):
            text_by_id[str(seg.get("id") or "")] = str(seg.get("narration_text") or "")
    rows: list[dict[str, Any]] = []
    for delta in segment_manifest_deltas if isinstance(segment_manifest_deltas, list) else []:
        if not isinstance(delta, dict):
            continue
        segment_id = str(delta.get("id") or "")
        slide_id = ""
        for ref in delta.get("visual_references") or []:
            if isinstance(ref, dict):
                slide_id = str(ref.get("perception_source") or "").strip()
                if slide_id:
                    break
        if not slide_id:
            continue
        rows.append(
            {
                "segment_id": segment_id,
                "id": segment_id,
                "slide_id": slide_id,
                "narration_text": text_by_id.get(segment_id, ""),
                "timing_role": delta.get("timing_role"),
                "content_density": delta.get("content_density"),
                "visual_detail_load": delta.get("visual_detail_load"),
                "duration_rationale": delta.get("duration_rationale"),
                "bridge_type": delta.get("bridge_type"),
                "behavioral_intent": delta.get("behavioral_intent"),
            }
        )
    return rows


__all__ = ["join_narration_segments"]
