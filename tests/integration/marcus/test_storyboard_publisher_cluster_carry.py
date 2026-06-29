"""Story 1.3-carry witness: cluster LABELS survive into segment-manifest-storyboard-b.

The delivered ``segment-manifest-storyboard-b.yaml`` carries ``bridge_type`` but
DROPS the four cluster labels (``cluster_id``/``cluster_role``/``cluster_position``/
``narrative_arc``), so cluster structure is not verifiable in what ships.

Drop points (both on the real ``c2c6dcbf`` checkpoint):
1. ``cluster_id``/``cluster_role``/``cluster_position`` ARE on the Pass-2
   ``segment_manifest_deltas`` but ``join_narration_segments`` (the party-governed
   FROZEN neck) omits them from the output row.
2. ``narrative_arc`` is non-null on the Pass-1 plan_units (keyed by ``cluster_id``)
   but absent from the Pass-2 deltas.

Fix lives in the EXPORT projection only (``_write_segment_manifest_for_b``);
``narration_join`` is NOT touched (import-pinned frozen join policy).

Murat amendment A2: the witness MUST be non-vacuous — assert ALL FOUR fields
non-degenerate on a HEAD AND an INTERSTITIAL, the SINGLETON carries its declared
(non-absent) sentinel values, and the degrade path (no arc map) still writes a
valid manifest with the three delta fields carried.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from app.marcus.orchestrator import storyboard_publisher


def _realistic_irene_output() -> dict[str, object]:
    """Mirror the real ``c2c6dcbf`` Pass-2 contribution shape.

    Three segments: a clustered HEAD + clustered INTERSTITIAL (both ``c-u01``)
    and a SINGLETON (``c-u02``). cluster_id/role/position ARE on the deltas;
    narrative_arc is ABSENT from the deltas (it lives on Pass-1 plan_units).
    """
    return {
        "narration_script": [
            {"id": "seg-01", "narration_text": "Head segment narration."},
            {"id": "seg-02", "narration_text": "Interstitial segment narration."},
            {"id": "seg-03", "narration_text": "Singleton segment narration."},
        ],
        "segment_manifest_deltas": [
            {
                "id": "seg-01",
                "timing_role": "concept-build",
                "bridge_type": "intro",
                "visual_references": [{"perception_source": "slide-01"}],
                "cluster_id": "c-u01",
                "cluster_role": "head",
                "cluster_position": "establish",
                # NOTE: no narrative_arc here — it lives on the Pass-1 plan_units.
            },
            {
                "id": "seg-02",
                "timing_role": "concept-build",
                "bridge_type": "cluster_boundary",
                "visual_references": [{"perception_source": "slide-02"}],
                "cluster_id": "c-u01",
                "cluster_role": "interstitial",
                "cluster_position": "tension",
            },
            {
                "id": "seg-03",
                "timing_role": "concept-build",
                "bridge_type": "intro",
                "visual_references": [{"perception_source": "slide-03"}],
                "cluster_id": "c-u02",
                "cluster_role": "head",
                "cluster_position": "establish",
            },
        ],
    }


def _read_segments(manifest_path: Path) -> dict[str, dict[str, object]]:
    loaded = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    return {seg["id"]: seg for seg in loaded["segments"]}


def test_cluster_labels_carry_into_segment_manifest_b(tmp_path: Path) -> None:
    """A2 witness (positive): all four cluster fields survive the export, with
    narrative_arc threaded by cluster_id from the Pass-1 arc map."""
    cluster_arc_by_id = {
        "c-u01": "From X to Y through Z",
        "c-u02": "From A to B through C",
    }
    manifest_path = storyboard_publisher._write_segment_manifest_for_b(
        run_dir=tmp_path,
        irene_output=_realistic_irene_output(),
        cluster_arc_by_id=cluster_arc_by_id,
    )
    segs = _read_segments(manifest_path)

    # (1) HEAD carries ALL FOUR fields non-degenerate.
    head = segs["seg-01"]
    assert head["cluster_id"] == "c-u01"
    assert head["cluster_role"] == "head"
    assert head["cluster_position"] == "establish"
    assert head["narrative_arc"] == "From X to Y through Z"

    # (2) INTERSTITIAL carries all four (arc inherited via shared cluster_id).
    inter = segs["seg-02"]
    assert inter["cluster_id"] == "c-u01"
    assert inter["cluster_role"] == "interstitial"
    assert inter["cluster_position"] == "tension"
    assert inter["narrative_arc"] == "From X to Y through Z"

    # (3) SINGLETON carries its OWN declared sentinel values (not silently absent).
    single = segs["seg-03"]
    assert single["cluster_id"] == "c-u02"
    assert single["cluster_role"] == "head"
    assert single["cluster_position"] == "establish"
    assert single["narrative_arc"] == "From A to B through C"

    # bridge_type (the field that already carried) must still be present — no regress.
    assert head["bridge_type"] == "intro"
    assert inter["bridge_type"] == "cluster_boundary"


def test_cluster_carry_degrades_without_arc_map(tmp_path: Path) -> None:
    """A2 witness (negative/degrade): cluster_arc_by_id=None still writes a valid
    manifest. The three delta-sourced fields carry; narrative_arc is None/absent;
    no crash. (Cluster-absent / non-clustered runs degrade gracefully.)"""
    manifest_path = storyboard_publisher._write_segment_manifest_for_b(
        run_dir=tmp_path,
        irene_output=_realistic_irene_output(),
        cluster_arc_by_id=None,
    )
    segs = _read_segments(manifest_path)

    head = segs["seg-01"]
    # The three delta fields still carry even with no arc map.
    assert head["cluster_id"] == "c-u01"
    assert head["cluster_role"] == "head"
    assert head["cluster_position"] == "establish"
    # narrative_arc degrades to None (declared, not crashing).
    assert head.get("narrative_arc") is None

    # All three segments wrote — manifest is valid.
    assert set(segs) == {"seg-01", "seg-02", "seg-03"}


def test_slide_key_carries_into_segment_manifest_b(tmp_path: Path) -> None:
    """enhanced-vo.1 AC-A5: the directed-voice identity-join key ``slide_key`` rides
    the Pass-2 deltas and survives the EXPORT projection (the frozen join neck drops
    non-core fields). It must NOT silently fall to None in what ships."""
    irene_output = _realistic_irene_output()
    # Stamp slide_key on the deltas the way _attach_voice_direction does on a
    # directed+enriched run (slide-01 head + slide-02 interstitial share source 1).
    slide_key_by_id = {"seg-01": "1", "seg-02": "1", "seg-03": "2"}
    for delta in irene_output["segment_manifest_deltas"]:
        delta["slide_key"] = slide_key_by_id[delta["id"]]
    manifest_path = storyboard_publisher._write_segment_manifest_for_b(
        run_dir=tmp_path,
        irene_output=irene_output,
        cluster_arc_by_id=None,
    )
    segs = _read_segments(manifest_path)
    assert segs["seg-01"]["slide_key"] == "1"
    assert segs["seg-02"]["slide_key"] == "1"  # interstitial inherits source 1
    assert segs["seg-03"]["slide_key"] == "2"


def test_slide_key_absent_stays_byte_identical(tmp_path: Path) -> None:
    """enhanced-vo.1 AC-A6: a non-directed / non-enriched run (deltas carry NO
    slide_key) gains NO slide_key field at export — byte-identical to pre-enhanced."""
    manifest_path = storyboard_publisher._write_segment_manifest_for_b(
        run_dir=tmp_path,
        irene_output=_realistic_irene_output(),
        cluster_arc_by_id=None,
    )
    segs = _read_segments(manifest_path)
    for seg in segs.values():
        assert "slide_key" not in seg


def test_cluster_carry_handles_non_clustered_deltas(tmp_path: Path) -> None:
    """Additive-safety witness: deltas with NO cluster fields (a non-clustered
    run) still write a valid manifest — cluster fields default to None/absent,
    no crash."""
    irene_output = {
        "narration_script": [{"id": "seg-01", "narration_text": "Plain narration."}],
        "segment_manifest_deltas": [
            {
                "id": "seg-01",
                "timing_role": "concept-build",
                "bridge_type": "intro",
                "visual_references": [{"perception_source": "slide-01"}],
            }
        ],
    }
    manifest_path = storyboard_publisher._write_segment_manifest_for_b(
        run_dir=tmp_path,
        irene_output=irene_output,
        cluster_arc_by_id={"c-u01": "unused"},
    )
    segs = _read_segments(manifest_path)
    seg = segs["seg-01"]
    assert seg.get("cluster_id") is None
    assert seg.get("cluster_role") is None
    assert seg.get("cluster_position") is None
    assert seg.get("narrative_arc") is None
