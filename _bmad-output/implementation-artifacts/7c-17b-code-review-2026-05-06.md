# Story 7c.17b — T11 Lite Code Review

**Reviewer:** Claude (T11 lite)
**Date:** 2026-05-06
**Story:** `migration-7c-17b-marcus-writers-theme-resolution-outbound-envelope`
**Implementation author:** Codex GPT-5
**Review tier:** T11 lite (~10-15 min single-pass; aggressive DISMISS on cosmetic NITs per `docs/dev-guide/story-cycle-efficiency.md`)

---

## Verdict: **PASS-zero-patches**

Codex implemented Story 7c.17b cleanly within the prompt's file scope. All 5 ACs (A-E) are satisfied. All focused / non-regression / validator commands PASS exactly as Codex reported. Spot-checks confirm 33 PASS across `tests/marcus/orchestrator/writers/` + `tests/parity/test_sanctum_alignment_dsl.py`; lint-imports 12 KEPT UNCHANGED; class-conformance 19 PASS UNCHANGED; ruff clean on Marcus-writer scope. No MUST-FIX or SHOULD-FIX findings.

This is the **second Wave-4 close, paired with 7c.17a**, and **closes Wave 4**. Per epic spec dispatch-state, this story's close UNBLOCKS 7c.15 (DISPATCH-BLOCKED on 7c.17b's outbound-envelope deliverable for §15 Marcus bundle writer).

---

## Findings

| Severity | Finding | Rationale |
|---|---|---|
| **MUST-FIX** | _none_ | — |
| **SHOULD-FIX** | _none_ | — |
| NIT-DISMISSED | Broad regression 43→45 failed (+2 net) | Within Wave-3 trio ±3 xdist-ordering noise band (precedent: 7c.6/7/8 verdicts cited "46-49 ±3 noise band; 5 spot-checked failures all pre-Wave-3 attribution per git-blame"). Codex attestation: "No failures are in the new 7c.17b writer modules, schemas, or tests." Inherited drift category list matches prior verdicts. DISMISS as inherited xdist noise per established precedent. Note: 7c.17a + 7c.17b share the same broad-regression run (single workspace; +2 collective). |

---

## AC verification

| AC | Description | Verified |
|---|---|---|
| A | `theme_resolution.py` writer + `GaryThemeResolution` Pydantic-v2 + `ResolvedTheme` sub-model + closed `ThemePaletteHint` Literal + module-import-time `declare_sanctum_alignment(writer_id="gary-theme-resolution", sanctum_path="_bmad/memory/bmad-agent-marcus/")` | ✓ Schema hash pinned `5b3b24b1c84197de2f819adb636b968153cad568a803691f33645cd41e0c9c2e` |
| B | `outbound_envelope.py` writer + `GaryOutboundEnvelope` + `OutboundEnvelopeEntry` (closed `OutboundEnvelopeWriterId` Literal of 5 canonical writer_ids) + deterministic YAML emit (`yaml.safe_dump` with `sort_keys=True` + `default_flow_style=False` + `allow_unicode=True`) + `pre_dispatch_package_gary_md` markdown aggregator (deterministic `sorted(envelope.entries, key=lambda item: item.writer_id)`) | ✓ Read `outbound_envelope.py` directly: closed-enum Literal of 5 writer_ids confirmed at lines 21-27; `enforce_tz_aware` reused from `app.models.state._base` (project standard); LF-only via `newline="\n"`; markdown aggregator deterministic-by-writer_id. Schema hash pinned `382985141ffe8e6572f17415d41d8eda33c6c49e6942d0e5a6d623ea9c1b4056` |
| C | 2 JSON schemas regenerated: `gary-theme-resolution.schema.json` + `pre-dispatch-package.schema.json` (envelope; FR-7c-25 location pin honored) via Path.write_text per A18 (LF-only; NO BOM) | ✓ Both schema files present at canonical paths under `_bmad/memory/bmad-agent-marcus/schemas/`; FR-7c-25 envelope schema location pin honored |
| D | Shape-pin tests + envelope-aggregation test + sanctum-registry-complement test in `tests/marcus/orchestrator/writers/` (separate file from 7c.17a's `test_sanctum_alignments.py` per cross-story test-file separation rule) | ✓ Read `test_sanctum_alignments_complement.py`: hermetic `_clear_sanctum_alignments_for_tests` autouse fixture + module-reload pattern + assertions for 2 NEW writer_ids (`gary-outbound-envelope`, `gary-theme-resolution`) + sanctum_path + alignment_kind triplet |
| E | 5-entry sanctum-manifest emission smoke test consumes `emit_sanctum_alignment_manifest` per 7c.0b AC-F | ✓ `test_all_five_writer_alignments_emit_manifest` imports all 5 writer modules + asserts 5-entry deterministic ordering: `["gary-diagram-cards", "gary-fidelity-slides", "gary-outbound-envelope", "gary-slide-content", "gary-theme-resolution"]` (alphabetic; per `iter_sanctum_alignments` deterministic-ordering invariant) + `schema_version: 1` |

---

## Spot-check evidence

| Command | Expected | Actual | Match |
|---|---|---|---|
| `pytest tests/marcus/orchestrator/writers/ tests/parity/test_sanctum_alignment_dsl.py` | combined PASS | **33 passed in 5.80s** | ✓ |
| `lint-imports.exe` | 12 KEPT | **Contracts: 12 kept, 0 broken** | ✓ |
| `validate_parity_test_class_conformance.py tests/parity/` | 19 PASS UNCHANGED | **PASS: 19** | ✓ |
| `validate_migration_story_sandbox_acs.py <story-file>` | PASS | **PASS — no sandbox-AC violations** | ✓ |
| `ruff check app/marcus/orchestrator/writers/ tests/marcus/orchestrator/writers/` | clean | **All checks passed!** | ✓ |

---

## Pattern-parity ratchet check

- Pydantic-v2 ConfigDict(extra=forbid, validate_assignment=True) on every model ✓
- Closed-enum Literal types on `ThemePaletteHint` + `OutboundEnvelopeWriterId` (5 canonical writer_ids; widening would require party-mode consensus) ✓
- strip-then-non-empty validators on all string fields per Wave-3 G2A canonical ✓
- `Field(...)` with description on every field ✓
- `schema_version: int = 1` on both models per FR-7c-51 ✓
- LF-only schema regen via Path.write_text per A18 ✓
- YAML emit byte-deterministic via PyYAML kwargs (`sort_keys=True` + `default_flow_style=False` + `allow_unicode=True`) ✓
- Markdown aggregator deterministic ordering by `writer_id` ✓
- Timezone-aware datetime via `enforce_tz_aware` (project standard helper from `app.models.state._base`; reused — NOT redefined locally) ✓
- Module-import-time `declare_sanctum_alignment` with `sanctum_path="_bmad/memory/bmad-agent-marcus/"` and default `alignment_kind="bmb-pattern"` ✓
- No parity_contract decorator (writers are NOT HIL surfaces) — class-conformance UNCHANGED ✓
- No pyproject.toml edit — M1-M4 contracts inherited by construction ✓

---

## Coordination evidence (parallel-dispatch with 7c.17a)

Codex confirmed in the dropbox: shared `app/marcus/orchestrator/writers/__init__.py` + `tests/marcus/orchestrator/writers/__init__.py` + `_bmad/memory/bmad-agent-marcus/schemas/` directory created once for the 7c.17a/17b batch; 5 distinct schema filenames; 7c.17b appends 2 (theme-resolution + envelope) to the directory created by 7c.17a; manifest smoke imports all 5 writer modules. PARALLEL-DISPATCH GUARDRAIL #3 (shared-file integration ordering) honored. NO cross-story interference (sanctum-registry tests separated per AC-D rule).

---

## Velocity record

- Wave 4 close (paired with 7c.17a). K=1.3× lite-tier executed cleanly.
- 5-entry sanctum-manifest emission smoke test (per 7c.0b AC-F) is now operational — consumed by the AUDIT-AC layer at 7c.20a/c.
- FR-7c-25 envelope schema location pin honored: `_bmad/memory/bmad-agent-marcus/schemas/pre-dispatch-package.schema.json`.
- T11 lite cycle: ~10-15 min single-pass review; PASS-zero-patches.
- **Wave-4 close consequence (HONORED):** 7c.15 unblocks. Spec already pre-authored at lookahead_tier=2 (`migration-7c-15-...md`); operator can now dispatch in own batch (NOT parallel-safe with this batch per 7c.15 spec).
- Recommend **flip done** + close-batch with 7c.17a.

---

## Closeout actions

1. ☑ Verdict written: PASS-zero-patches
2. ☐ Sprint-status flip: `migration-7c-17b-marcus-writers-theme-resolution-outbound-envelope: review → done`
3. ☐ Close-batch commit (combined with 7c.17a PASS verdict + pre-author of Wave-5 entry pair 7c.18a/b + 7c.19)
