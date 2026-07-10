# Mine 4A CLOSE — Canonical processed-source (2026-07-10 UTC)

**Status:** CLOSED by party (John / Winston / Amelia / Murat) — CLOSE-with-named-fenced-residuals  
**Live run:** `runs/09e01f7f-39aa-4179-be34-980a7fbe01ae/`  
**Evidence:** `_bmad-output/implementation-artifacts/evidence/mine4a-canonical-shape-pin-20260710T022613Z/canonical-processed-source/verdict.json`

## Claim MET

Documented canonical layout; automated validators for lesson leaf + run dir; reader digests; `kind` (AssetKind) shape-pin on enrichment nodes (gates Mine 5).

## Delivered

| Piece | Path |
|---|---|
| Validator | `app/marcus/course_source/canonical_processed_source.py` |
| TypedComponent.kind | `app/marcus/lesson_plan/source_type.py` (optional; required by run_dir validator) |
| Contract doc | `docs/dev-guide/canonical-processed-source-structure.md` |
| Unit | `tests/marcus/course_source/test_canonical_processed_source.py` (7 passed) |
| Liveproof | `scripts/utilities/bank_mine4a_canonical_shape_pin_liveproof.py` → pass |

## Fenced residuals (4B)

- Manifest/checksum emission at write time + reader validate-on-load (party-named seam)
- Automated normalize writeback to typed folders; historical backfill; cloud storage
- Output projectors (Mine 5/6)

## Next

Mine 5 Drill projector (unblocked).
