# Migration Story 34-4: Wrangler `metadata.json` `sme_refs[]` Additive Emission (Murat M-Murat-3 binding)

**Status:** ready-for-dev *(spec authored 2026-05-22 with locked contract decisions D1-D5; predecessor Stories 34-1 + 34-2 + 34-3 expected `done` at dispatch.)*
**Sprint key:** `migration-34-4-wrangler-metadata-sme-refs-additive-emission`
**Epic:** Epic 34 — §02A Downstream-Consumer Schema Coherence
**Pts:** 3
**Gate:** **single-gate** (focused metadata-writer edit; same wrangler file as Story 34-2; bounded scope)
**K-target:** ~1.5× (3 pts; bounded surface = 1 metadata writer function + integration test extension per AC-34-4-A-EXT + targeted test)
**R-tier:** **R1**
**T11-tier:** standard
**Files touched (substrate-verified 2026-05-22):**

**Modified (~2 files):**
- `skills/bmad-agent-texas/scripts/run_wrangler.py` (lines 1239-1266 metadata writer; D1 implementation — add `sme_refs` key to meta dict)
- `tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py` (Story 34-1's test extended per AC-34-4-A-EXT — adds sme_refs assertion block)

**New (~1-2 files):**
- `skills/bmad-agent-texas/scripts/tests/test_run_wrangler_sme_refs_emission.py` (NEW; co-located with `test_run_wrangler.py`; D3 test pin)

**Conditionally modified (1 file; surface decision_needed if needed):**
- `app/marcus/intake/pre_packet.py` — likely UNCHANGED (pre_packet's existing `_build_sme_refs` at lines 175-197 ALREADY reads `metadata["sme_refs"]` in the preferred branch; Story 34-4 makes that branch fire. No pre_packet changes expected. Verify at T1.)

**Lookahead tier:** **1** (focused; small surface; substrate verified).
**Wave:** 1 — slot 4 (downstream of substrate harmonization Stories 34-2 + 34-3; closes D5/D6 soft-degrade).

**FR coverage:** FR-E34-4 (additive sme_refs), FR-E34-5 (`SourceRef` shape match).
**NFR coverage:** NFR-E34-1 (Story-34-1 ratchet stays GREEN + EXTENDS per AC-34-4-A-EXT), NFR-E34-2 (Pydantic-v2 closed-enum preserved — n/a no enum changes), NFR-E34-3 (no Pydantic models touched in wrangler; n/a), NFR-E34-8 (TW-7c-4 dual-predicate; run_wrangler.py pre-allowlisted), NFR-E34-11..13.

**Contract Decisions (LOCKED 2026-05-22 — SUBSTRATE-VERIFIED):**

**D1. `_write_metadata_json` additive sme_refs (AC-34-4-A BINDING):**

**Current substrate** (verified via Read of `run_wrangler.py:1239-1266`):
```python
def _write_metadata_json(
    bundle_dir: Path,
    run_id: str,
    outcomes: list[SourceOutcome],
    run_timestamp: str,
) -> Path:
    """Write metadata.json with the provenance chain preserved."""
    provenance = [
        {
            "ref_id": o.ref_id,
            "kind": o.provider,
            "ref": o.locator,
            "role": o.role,
            "description": o.description,
            "extractor_used": o.extractor_used,
            "fetched_at": o.fetched_at,
        }
        for o in outcomes
    ]
    meta = {
        "run_id": run_id,
        "generated_at": run_timestamp,
        "provenance": provenance,
        "primary_consumption_path": "extracted.md",
    }
    path = bundle_dir / "metadata.json"
    path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return path
```

**Story 34-4 change: ADD `sme_refs` key alongside `provenance` (additive — `provenance` PRESERVED per Murat M-Murat-3 binding):**

```python
def _write_metadata_json(
    bundle_dir: Path,
    run_id: str,
    outcomes: list[SourceOutcome],
    run_timestamp: str,
) -> Path:
    """Write metadata.json with the provenance chain preserved + sme_refs additive."""
    provenance = [
        {
            "ref_id": o.ref_id,
            "kind": o.provider,
            "ref": o.locator,
            "role": o.role,
            "description": o.description,
            "extractor_used": o.extractor_used,
            "fetched_at": o.fetched_at,
        }
        for o in outcomes
    ]
    # Story 34-4: additive sme_refs[] emission matching pre_packet.SourceRef shape
    # (`{source_id, path, content_digest}`). source_id mirrors ref_id (D6 field-name
    # fork closure). content_digest computed per-source from outcome.content_text
    # bytes — NOT whole-bundle sha256 of extracted.md (pre_packet fallback was
    # whole-bundle which is wrong digest semantically).
    sme_refs = [
        {
            "source_id": o.ref_id,
            "path": o.locator if o.provider == "local_file" else None,
            "content_digest": hashlib.sha256(
                o.content_text.encode("utf-8")
            ).hexdigest(),
        }
        for o in outcomes
    ]
    meta = {
        "run_id": run_id,
        "generated_at": run_timestamp,
        "provenance": provenance,        # PRESERVED per Murat M-Murat-3
        "sme_refs": sme_refs,            # NEW additive emission per FR-E34-4/5
        "primary_consumption_path": "extracted.md",
    }
    path = bundle_dir / "metadata.json"
    path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return path
```

**D2. Per-source content_digest derivation (FR-E34-5 BINDING):**

`content_digest` is `sha256(outcome.content_text.encode("utf-8"))` — per-source. This is DIFFERENT from pre_packet's existing fallback at `pre_packet.py:200-206` which computes sha256 over whole `extracted.md` bytes. The Story 34-4 emission is semantically correct (per-source digest); pre_packet's fallback was a wrong-shape stopgap.

`hashlib` is already imported at `run_wrangler.py` top — verify at T1, but Phase A probe confirmed it.

**D3. `path` field semantics (substrate-verified — pre_packet.SourceRef constraint):**

Per `app/marcus/lesson_plan/log.py:329-335`, `SourceRef.path` has a validator that REJECTS absolute paths + `..` traversal segments (`_validate_repo_relative_path`). The wrangler's `o.locator` for `provider == "local_file"` is the corpus-relative path (passed in via the directive). This MUST be repo-relative; if it's not (e.g., an operator passes an absolute path), pre_packet will reject.

**Conditional handling:** if `o.provider != "local_file"` (e.g., `notion_mcp`, `url`, `playwright_html`, `box`), `path` MUST be `null`. pre_packet's SourceRef.path allows `None`.

**T1 verification:** test that the wrangler outputs `path=null` for non-local providers (use an existing wrangler test fixture with a `url` source if one exists; otherwise skip this assertion).

**D4. Ignored-row exclusion (downstream of Story 34-2 D4):**

Story 34-2's `_load_directive` filtering removes `role=ignored` rows from `outcomes` before they reach materialization. Therefore `sme_refs[]` naturally inherits the filtering — Story 34-4 SHALL NOT add a separate filter for `ignored`. The list comprehension on `outcomes` is the right boundary.

**D5. Story 34-1 ratchet extension (AC-34-4-A-EXT BINDING):**

Per Epic 34 AC-34-4-A-EXT, Story 34-4 MUST EXTEND `tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py` to add the following assertion block AFTER the existing materials-non-empty-then-row-shape assertions:

```python
# NEW Story 34-4 extension: sme_refs[] additive emission verification
import json
metadata_path = bundle_dir / "metadata.json"
metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

# AC-34-4-A: sme_refs key present + non-empty BEFORE per-entry shape (A9 mitigation)
assert "sme_refs" in metadata, f"metadata.json missing 'sme_refs' key: {metadata.keys()}"
assert len(metadata["sme_refs"]) >= 1, (
    f"metadata.json.sme_refs is empty: {metadata['sme_refs']!r}"
)

# AC-34-4-A: per-entry shape match
for i, entry in enumerate(metadata["sme_refs"]):
    assert set(entry.keys()) == {"source_id", "path", "content_digest"}, (
        f"sme_refs[{i}] keys drift: expected {{source_id, path, content_digest}}, "
        f"got {set(entry.keys())}"
    )
    assert isinstance(entry["source_id"], str) and entry["source_id"], (
        f"sme_refs[{i}].source_id must be non-empty string: {entry['source_id']!r}"
    )
    assert entry["path"] is None or isinstance(entry["path"], str), (
        f"sme_refs[{i}].path must be str or None: {entry['path']!r}"
    )
    assert isinstance(entry["content_digest"], str) and len(entry["content_digest"]) == 64, (
        f"sme_refs[{i}].content_digest must be 64-char sha256 hex: {entry['content_digest']!r}"
    )

# AC-34-4-A: provenance PRESERVED unchanged (Murat M-Murat-3 binding)
assert "provenance" in metadata, "Story 34-4 MUST preserve provenance key"
assert len(metadata["provenance"]) == len(metadata["sme_refs"]), (
    "sme_refs and provenance must have same cardinality (one entry per outcome)"
)

# AC-34-4-A: sme_refs[i].source_id matches materials[i].ref_id (FR-E34-5 one-to-one)
materials_ref_ids = {m["ref_id"] for m in result_yaml["materials"]}
sme_refs_source_ids = {e["source_id"] for e in metadata["sme_refs"]}
assert materials_ref_ids == sme_refs_source_ids, (
    f"materials.ref_id set != sme_refs.source_id set: "
    f"materials={materials_ref_ids} sme_refs={sme_refs_source_ids}"
)
```

This is the "ratchet extension" pattern per Quinn-synthesis Option 5 — Story 34-1's test grows in lockstep with new substrate behavior.

---

## Task chain T1-T11

**T1 readiness check:** C1 + Stories 34-1 + 34-2 + 34-3 = `done` in sprint-status.yaml. Story 34-1 round-trip test PASS on clean tree. Verify `SourceOutcome.content_text` field exists (substrate at `run_wrangler.py:183`). Verify `hashlib` import at wrangler top (Phase A confirmed).

**T2 wrangler metadata writer extension:** D1 implementation at lines 1239-1266.

**T3 Story-34-1 ratchet extension:** D5 implementation — extend `tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py` with sme_refs assertion block.

**T4 wrangler-side test:** author `skills/bmad-agent-texas/scripts/tests/test_run_wrangler_sme_refs_emission.py` with unit tests:
- sme_refs present in metadata.json
- per-entry shape matches `{source_id, path, content_digest}`
- source_id == ref_id (one-to-one)
- path is None for non-local providers (use synthetic fixture)
- content_digest is per-source sha256 (NOT whole-bundle)
- ignored rows excluded (inherited from Story 34-2; verify)

**T5 pre_packet verification (likely NO-OP):** verify `_build_sme_refs` at `pre_packet.py:175-197` consumes the new sme_refs without modification. Existing branch at line 188-197 should fire on the new wrangler output. If T5 surfaces a mismatch, pre_packet may need a minor adjustment — surface decision_needed.

**T6 ruff + lint-imports + focused suite.**

**T7 Story-34-1 integration ratchet:** stays GREEN with new sme_refs assertions; broad regression delta within abort tripwire.

**T8 self-G6 + T9 ready-for-review + T10 Claude T11 review + commit + flip done.**

---

## Acceptance Criteria (carryforward from Epic 34 spec)

- **AC-34-4-A** (additive sme_refs): D1 BINDING.
- **AC-34-4-A-EXT** (integration-test extension): D5 BINDING — Story 34-1 test extended per Epic-34 AC-34-4-A-EXT spec.
- **AC-34-4-B** (pre_packet contract satisfaction): T5 verification.
- **AC-34-4-C** (translator shrinkage): n/a — translator unchanged at this story (D5/D6 are wrangler-output, not translator-input).
- **AC-34-4-D** (ignored-row metadata exclusion): inherited from Story 34-2 D4; verified at T4.

## Cross-references

- Epic 34 spec §"Story 34-4" + AC-34-4-A-EXT
- Story 34-1 spec (D5 ratchet-extension target)
- Story 34-2 spec (D4 ignored-row filter; inherited)
- `app/marcus/intake/pre_packet.py:175-207` (consumer contract)
- `app/marcus/lesson_plan/log.py:311-336` (SourceRef Pydantic model)
- `skills/bmad-agent-texas/scripts/run_wrangler.py:171-187` (SourceOutcome dataclass with content_text field)
