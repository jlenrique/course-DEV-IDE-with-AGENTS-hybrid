# Carried-Findings (b) — Witness Record (D-B)

Date: 2026-07-02 UTC. Branch: dev/carried-findings-enum-refresh-2026-07-02.

1. byte-test-RED-at-HEAD.txt — test_publisher_segment_manifest_byte_stable_through_shared_join RED at HEAD (oracle = bare join; writer applies post-join projection since 1.3-carry). Premise confirmed.
2. pre-extraction-golden.yaml — characterization golden: _write_segment_manifest_for_b over the test module's NARRATION+DELTAS, cluster_arc_by_id=None, captured BEFORE the lift (649 bytes).
3. post-extraction-capture.yaml + diff-clean-note.txt — same invocation AFTER the mechanical lift of the projection into module-level enrich_segments_for_export(segments, deltas, arc_map): BYTE-IDENTICAL (649 bytes). Lift was byte-neutral; no escalation needed.
4. Oracle repaired: expected = yaml.safe_dump({"segments": enrich_segments_for_export(join_narration_segments(...), DELTAS, {})}, sort_keys=False, allow_unicode=True) — kwargs pinned identical to the writer — plus mandatory literal anchors (cluster_id/cluster_role/cluster_position/narrative_arc as explicit nulls; voice_direction/slide_key ABSENT for this fixture).
5. Projection unit test added: tests/integration/marcus/test_storyboard_export_projection.py — hand-written literals for delta-value-wins, voice_direction/slide_key both branches, ambiguous-duplicate-id (Edge-#4), pre-era pin (exact dicts).
6. red-witness-cluster-role-mutation.txt — cluster_role copy line commented out: ALL 5 projection unit tests RED AND the byte test RED specifically on the literal anchor 'cluster_role: null' (byte-equality clause alone stayed satisfied — the anchors are the independent oracle, exactly as designed). Restored; all green.

Frozen neck app/specialists/_shared/narration_join.py + app/specialists/narration_join UNTOUCHED (read-only honored; publisher-side only).
