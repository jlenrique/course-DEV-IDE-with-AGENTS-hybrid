"""Story 1.2a — Pass-2 delta-id backfill for clustered decks.

RED-first tests. Live trial 52890be7 (first clustered production run) error-paused
at the enrique audio leg: Pass-2 emitted 13 narration segments (ids seg-01..seg-13)
parallel to 13 segment_manifest_deltas with id == None, so the id-keyed join
(party-governed narration_join) dropped all 13 -> elevenlabs.join.dropped-segments.

backfill_delta_ids repairs the id-omission at the Pass-2 output boundary (the
party-governed join policy stays untouched). Green-light amendments folded:
- Winston A1: backfill ONLY when ALL deltas lack ids (partial -> untouched).
- Winston A2: after backfill, the id-keyed _segment_slide_id_from_deltas resolves.
- Murat A1: phantom-text path still catchable.
- Murat A2: length-mismatch -> deltas untouched (guard still fires downstream).
- Murat A3: pin the positional-parallel invariant narr[i].id -> deltas[i].
- Murat A4: AC-4 uses the real 52890be7 shape + the actual join import.
"""
from __future__ import annotations

import json

from app.specialists.irene.graph import _segment_slide_id_from_deltas, backfill_delta_ids
from app.specialists.narration_join import join_narration_segments


def _narr(n: int) -> list[dict]:
    return [
        {"id": f"seg-{i:02d}", "narration_text": f"Narration line {i}."}
        for i in range(1, n + 1)
    ]


def _delta(idval, slide: str) -> dict:
    d = {"visual_references": [{"perception_source": slide}]}
    if idval is not None:
        d["id"] = idval
    return d


# AC-1: all-None deltas, len==narration -> ids backfilled by index ------------
def test_ac1_all_none_deltas_backfilled_by_index() -> None:
    parsed = {
        "narration_script": _narr(3),
        "segment_manifest_deltas": [_delta(None, "s1"), _delta(None, "s2"), _delta(None, "s3")],
    }
    out = backfill_delta_ids(parsed)
    ids = [d.get("id") for d in out["segment_manifest_deltas"]]
    assert ids == ["seg-01", "seg-02", "seg-03"]


# Murat A3: positional-parallel invariant narr[i].id -> deltas[i] -------------
def test_ac_positional_parallel_invariant() -> None:
    # LOAD-BEARING: backfill is only safe because Pass-2 emits the two arrays
    # positionally aligned from one authoring pass. Pin index-for-index pairing.
    parsed = {
        "narration_script": [{"id": "seg-01"}, {"id": "seg-02"}],
        "segment_manifest_deltas": [_delta(None, "sA"), _delta(None, "sB")],
    }
    out = backfill_delta_ids(parsed)
    assert out["segment_manifest_deltas"][0]["id"] == "seg-01"
    assert out["segment_manifest_deltas"][1]["id"] == "seg-02"


# Winston A1: PARTIAL ids -> untouched (out-of-order signal) ------------------
def test_ac_partial_ids_left_untouched() -> None:
    parsed = {
        "narration_script": _narr(3),
        "segment_manifest_deltas": [_delta("seg-01", "s1"), _delta(None, "s2"), _delta(None, "s3")],
    }
    out = backfill_delta_ids(parsed)
    # one delta already had an id -> do NOT backfill; leave for the asserts.
    ids = [d.get("id") for d in out["segment_manifest_deltas"]]
    assert ids == ["seg-01", None, None]


# T11 Edge: a present-but-falsy id (0/"") counts as PRESENT -> untouched ------
def test_ac_falsy_but_present_id_blocks_backfill() -> None:
    # all-None gate must be true "all-None", not "all-falsy": a delta carrying a
    # real-but-falsy id signals the array is NOT all-id-less -> leave untouched.
    parsed = {
        "narration_script": _narr(2),
        "segment_manifest_deltas": [{"id": "", "visual_references": []}, _delta(None, "s2")],
    }
    out = backfill_delta_ids(parsed)
    # second delta NOT backfilled (the first has an explicit, if falsy, id key).
    assert out["segment_manifest_deltas"][1].get("id") is None


# The REAL 52890be7 bug: Pass-2 emits the id under `segment_id`, not `id` -----
def test_ac_segment_id_aliased_to_id() -> None:
    # The party-governed join keys on `id`; Pass-2 emitted it under `segment_id`.
    # Alias is direct + always safe (same value), per-delta (no positional gate).
    parsed = {
        "narration_script": _narr(2),
        "segment_manifest_deltas": [
            {"segment_id": "seg-01", "visual_references": [{"perception_source": "sl1"}]},
            {"segment_id": "seg-02", "visual_references": [{"perception_source": "sl2"}]},
        ],
    }
    out = backfill_delta_ids(parsed)
    assert [d.get("id") for d in out["segment_manifest_deltas"]] == ["seg-01", "seg-02"]


def test_ac_segment_id_alias_is_per_delta_not_positional() -> None:
    # alias works even with a partial array (one already has id) — it is NOT gated
    # on all-None like the positional fallback.
    parsed = {
        "narration_script": _narr(2),
        "segment_manifest_deltas": [
            {"id": "seg-09", "visual_references": []},
            {"segment_id": "seg-02", "visual_references": []},
        ],
    }
    out = backfill_delta_ids(parsed)
    assert out["segment_manifest_deltas"][0]["id"] == "seg-09"  # preserved
    assert out["segment_manifest_deltas"][1]["id"] == "seg-02"  # aliased, NOT positional


def test_ac_real_52890be7_shape_segment_id_zero_dropped() -> None:
    # Exact live shape: 13 deltas with segment_id seg-01..13 + slide_id + refs,
    # id == None. Must alias -> the real join drops ZERO (the audio-leg unblock).
    n = 13
    parsed = {
        "narration_script": _narr(n),
        "segment_manifest_deltas": [
            {"id": None, "segment_id": f"seg-{i:02d}", "slide_id": f"slide-{i:02d}",
             "visual_references": [{"perception_source": f"slide-{i:02d}"}]}
            for i in range(1, n + 1)
        ],
    }
    out = backfill_delta_ids(parsed)
    rows = join_narration_segments(out["narration_script"], out["segment_manifest_deltas"])
    joined = {str(r.get("id") or "") for r in rows}
    dropped = sorted(s["id"] for s in out["narration_script"] if s["id"] not in joined)
    assert dropped == [], f"real clustered shape must join with zero dropped; got {dropped}"
    assert all(str(r.get("narration_text") or "").strip() for r in rows)


# existing ids fully present -> unchanged ------------------------------------
def test_ac_existing_ids_preserved() -> None:
    parsed = {
        "narration_script": _narr(2),
        "segment_manifest_deltas": [_delta("seg-01", "s1"), _delta("seg-02", "s2")],
    }
    out = backfill_delta_ids(parsed)
    assert [d["id"] for d in out["segment_manifest_deltas"]] == ["seg-01", "seg-02"]


# AC-2 / Murat A2: length-mismatch -> untouched + guard still fires -----------
def test_ac2_length_mismatch_untouched_guard_still_fires() -> None:
    parsed = {
        "narration_script": _narr(3),
        "segment_manifest_deltas": [_delta(None, "s1"), _delta(None, "s2")],  # 2 != 3
    }
    out = backfill_delta_ids(parsed)
    assert [d.get("id") for d in out["segment_manifest_deltas"]] == [None, None]
    # downstream guard still fires: id-less deltas drop narration segments.
    rows = join_narration_segments(out["narration_script"], out["segment_manifest_deltas"])
    joined_ids = {str(r.get("id") or "") for r in rows}
    dropped = [s["id"] for s in out["narration_script"] if s["id"] not in joined_ids]
    assert dropped, "length-mismatch must NOT silently repair; guard must still see drops"


# AC-3: pure + idempotent ----------------------------------------------------
def test_ac3_pure_and_idempotent() -> None:
    parsed = {
        "narration_script": _narr(2),
        "segment_manifest_deltas": [_delta(None, "s1"), _delta(None, "s2")],
    }
    snapshot = json.dumps(parsed, sort_keys=True)
    once = backfill_delta_ids(parsed)
    assert json.dumps(parsed, sort_keys=True) == snapshot  # no input mutation
    twice = backfill_delta_ids(once)
    assert once == twice  # idempotent (post-backfill all have ids -> no-op)


# AC-4 / Murat A4: real 52890be7 shape -> ZERO dropped via the actual join ----
def test_ac4_clustered_shape_zero_dropped_via_real_join() -> None:
    n = 13
    parsed = {
        "narration_script": _narr(n),
        "segment_manifest_deltas": [_delta(None, f"slide-{i:02d}") for i in range(1, n + 1)],
    }
    out = backfill_delta_ids(parsed)
    rows = join_narration_segments(out["narration_script"], out["segment_manifest_deltas"])
    joined_ids = {str(r.get("id") or "") for r in rows}
    dropped = sorted(s["id"] for s in out["narration_script"] if s["id"] not in joined_ids)
    assert dropped == [], f"clustered shape must join with zero dropped; got {dropped}"
    # every joined row carries its narration text (no phantom).
    assert all(str(r.get("narration_text") or "").strip() for r in rows)


# Winston A2: after backfill, id-keyed _segment_slide_id_from_deltas resolves -
def test_ac7_id_keyed_lookup_resolves_after_backfill() -> None:
    parsed = {
        "narration_script": _narr(2),
        "segment_manifest_deltas": [_delta(None, "slide-a"), _delta(None, "slide-b")],
    }
    out = backfill_delta_ids(parsed)
    # the id-keyed resolver (line 544) must find a slide_id for each segment.
    for seg in out["narration_script"]:
        slide = _segment_slide_id_from_deltas(seg, out)
        assert slide, f"id-keyed lookup failed for {seg['id']} after backfill"


# Murat A1: phantom-text still detectable (backfill must not paper over) ------
def test_ac_phantom_text_still_detectable() -> None:
    # A delta whose narration text is empty must still surface as a phantom after
    # backfill (the id resolves, but the text is empty -> phantom guard catches it).
    from app.specialists.narration_join import phantom_segment_ids

    parsed = {
        "narration_script": [
            {"id": "seg-01", "narration_text": "real"},
            {"id": "seg-02", "narration_text": "  "},
        ],
        "segment_manifest_deltas": [_delta(None, "s1"), _delta(None, "s2")],
    }
    out = backfill_delta_ids(parsed)
    rows = join_narration_segments(out["narration_script"], out["segment_manifest_deltas"])
    assert "seg-02" in phantom_segment_ids(rows)
