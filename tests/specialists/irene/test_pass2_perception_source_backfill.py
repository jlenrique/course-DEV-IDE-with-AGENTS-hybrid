"""Pass-2 perception_source backfill — non-clustered cluster-head gap.

RED-first. Live trial 72ed8fd5 (S5 HIL drive) error-paused at the enrique audio
leg: Pass-2 emitted 13 narration segments + 13 deltas with matching ids, but the
cluster-head delta `seg-10` carried an EMPTY `visual_references` list. The shared
join drops a perception_source-less delta, so its narration is "dropped" and
enrique's pre-spend guard refuses (`elevenlabs.join.dropped-segments`).

`backfill_delta_perception_sources` repairs the gap at the Pass-2 output boundary
from the authoritative roster (positional, alignment-gated) — distinct from
`backfill_delta_ids` (which repairs a missing `id`, not a missing source).
"""
from __future__ import annotations

from app.specialists.irene.graph import backfill_delta_perception_sources
from app.specialists.narration_join import join_narration_segments


def _roster(n: int) -> list[dict]:
    return [{"slide_id": f"slide-{i:02d}"} for i in range(1, n + 1)]


def _delta(slide: str | None) -> dict:
    refs = [{"perception_source": slide}] if slide else []
    return {"visual_references": refs}


# AC-1: the exact 72ed8fd5 shape — one gap (seg-10) backfilled from the roster.
def test_ac1_single_gap_backfilled_from_roster() -> None:
    deltas = [_delta(f"slide-{i:02d}") for i in range(1, 14)]
    deltas[9] = _delta(None)  # seg-10: empty visual_references
    parsed = {"narration_script": [{"id": f"seg-{i:02d}"} for i in range(1, 14)],
              "segment_manifest_deltas": deltas}
    out = backfill_delta_perception_sources(parsed, _roster(13))
    src = out["segment_manifest_deltas"][9]["visual_references"][0]["perception_source"]
    assert src == "slide-10"
    # every delta now carries a perception_source
    assert all(d["visual_references"][0]["perception_source"] for d in out["segment_manifest_deltas"])


# AC-2: end-to-end — the join now covers all 13 (no dropped narration).
def test_ac2_join_covers_all_after_backfill() -> None:
    narr = [{"id": f"seg-{i:02d}", "narration_text": f"line {i}"} for i in range(1, 14)]
    deltas = [{"id": f"seg-{i:02d}", **_delta(f"slide-{i:02d}")} for i in range(1, 14)]
    deltas[9] = {"id": "seg-10", **_delta(None)}
    parsed = {"narration_script": narr, "segment_manifest_deltas": deltas}
    out = backfill_delta_perception_sources(parsed, _roster(13))
    rows = join_narration_segments(out["narration_script"], out["segment_manifest_deltas"])
    joined_ids = {r["id"] for r in rows}
    dropped = [s["id"] for s in narr if s["id"] not in joined_ids]
    assert dropped == []  # seg-10 no longer dropped


# AC-3 (safety): length mismatch → untouched (guard still fires downstream).
def test_ac3_length_mismatch_untouched() -> None:
    deltas = [_delta(None), _delta("slide-02")]
    parsed = {"segment_manifest_deltas": deltas}
    out = backfill_delta_perception_sources(parsed, _roster(3))
    assert out["segment_manifest_deltas"][0]["visual_references"] == []


# AC-4 (safety): MISALIGNED present sources → skip (no mis-attribution).
def test_ac4_misaligned_present_sources_skip() -> None:
    # delta[0] references slide-02 (not slide-01) → positional alignment broken.
    deltas = [_delta("slide-02"), _delta(None), _delta("slide-03")]
    parsed = {"segment_manifest_deltas": deltas}
    out = backfill_delta_perception_sources(parsed, _roster(3))
    assert out["segment_manifest_deltas"][1]["visual_references"] == []  # untouched


# AC-5: no gap → unchanged (idempotent on a complete array).
def test_ac5_no_gap_unchanged() -> None:
    deltas = [_delta(f"slide-{i:02d}") for i in range(1, 4)]
    parsed = {"segment_manifest_deltas": deltas}
    out = backfill_delta_perception_sources(parsed, _roster(3))
    assert out is parsed or out["segment_manifest_deltas"] == deltas
    # second application is a no-op
    assert backfill_delta_perception_sources(out, _roster(3))["segment_manifest_deltas"] == deltas


# AC-6: roster with a blank slide_id → untouched (cannot ground safely).
def test_ac6_blank_roster_id_untouched() -> None:
    roster = [{"slide_id": "slide-01"}, {"slide_id": ""}, {"slide_id": "slide-03"}]
    deltas = [_delta("slide-01"), _delta(None), _delta("slide-03")]
    parsed = {"segment_manifest_deltas": deltas}
    out = backfill_delta_perception_sources(parsed, roster)
    assert out["segment_manifest_deltas"][1]["visual_references"] == []
