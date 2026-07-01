# Digest note — corrupted-vs-clean (BAR 6)

Digest scheme: **canonical_sha256** (`recompute_digest_from_disk(..., DigestAlgo.CANONICAL_SHA256)`), the same scheme the RAI pins.

- **Golden baseline (untouched, run 8d819b8d-...):** `c23a37c5e56f764f9b42b40a396535b51a9af99650c4d68215af1bb4933667ce`
  - Re-verified AFTER both live arms: still `c23a37c5` — golden never mutated.
- **HALT trial (08b5ff0f) g0-enrichment.json:**
  - clean/ratified digest pinned in RAI: `c23a37c5e56f...`
  - on-disk digest AFTER corruption: `a8fd457155aed77d8f147f5fbccdf981d5fd86a5b4302e011923bb49fbf47bab`
  - corruption method: added benign top-level key `_leg4_udac_corruption_marker` → **still valid JSON, still present on disk**; only the canonical digest diverged → `TAG_STALE` on digest mismatch (NOT a parse/missing-file failure).
- **CONTROL trial (938e1680) g0-enrichment.json:** left clean; on-disk digest == RAI digest `c23a37c5e56f...` → guard PASSES.

This is the BAR-6 point: the halt is triggered by a **content/digest mutation of a still-present, still-valid-JSON asset**, not by file absence.
