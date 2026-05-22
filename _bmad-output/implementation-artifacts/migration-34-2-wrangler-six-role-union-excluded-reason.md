# Migration Story 34-2: Texas Wrangler 6-Role Union + excluded_reason + Cross-Field Invariants (Winston A1 binding)

**Status:** ready-for-dev *(spec authored 2026-05-22 with locked contract decisions D1-D5; predecessor Story 34-1 expected `done` at dispatch time.)*
**Sprint key:** `migration-34-2-wrangler-six-role-union-excluded-reason`
**Epic:** Epic 34 — §02A Downstream-Consumer Schema Coherence
**Pts:** 5
**Gate:** **single-gate** (focused wrangler-validator edit; same-file boundary as Story 34-4; Story 34-1's ratchet stays green per Quinn-synthesis Option 5)
**K-target:** ~1.5× (5 pts; bounded surface = 1 wrangler input-validator function + helper for `excluded_reason` cross-field invariant + targeted tests)
**R-tier:** **R2**
**T11-tier:** standard (Claude T11; cross-agent NOT mandatory for single-gate substrate edits with Story-34-1 ratchet underneath)
**Files touched:**

**Modified:**
- `skills/bmad-agent-texas/scripts/run_wrangler.py` (lines 280-394 input validator; expand role enum; add `excluded_reason` handling; migrate §02A cross-field invariants)

**New:**
- `skills/bmad-agent-texas/scripts/tests/test_wrangler_role_enum_union_and_excluded_reason.py` (OR equivalent path under `tests/specialists/texas/` per existing pattern — verify at T1)
- Translator-shrinkage update at `app/composers/section_02a/_wrangler_translator.py`: remove `role-supporting-to-supplementary` AND `filter-ignored-rows` mappings from `TRANSLATOR_ACTIVE_MAPPINGS` (Story 34-1's frozenset shrinks)

**Lookahead tier:** **1** (focused; small surface).
**Wave:** 1 — slot 2 (substrate change; lands BEFORE Story 34-3 per Winston A3 substrate-before-cosmetic ordering).

**FR coverage:** FR-E34-2 (6-role union), FR-E34-3 (excluded_reason), FR-E34-6 (cross-field invariants migrate).
**NFR coverage:** NFR-E34-1 (integration test mandatory — Story 34-1's ratchet), NFR-E34-2 (Pydantic-v2 closed-enum preserved), NFR-E34-4 (LLM-judged taxonomy not destroyed), NFR-E34-5 (27-2/27-3 substrate preserved), NFR-E34-8 (TW-7c-4 dual-predicate), NFR-E34-11..13 (NEW CYCLE + sandbox-AC + governance validator).

**Contract Decisions (LOCKED 2026-05-22):**

**D1. Role enum extension (Winston A1 BINDING):** Wrangler's `run_wrangler.py:328-338` role-check MUST extend from current 5-element set to **6-element union**:

```python
ALLOWED_ROLES: frozenset[str] = frozenset({
    "primary",
    "supporting",        # NEW — §02A taxonomy (was not in pre-Epic-34 wrangler set)
    "ignored",           # NEW — §02A taxonomy (was not in pre-Epic-34 wrangler set)
    "validation",        # PRESERVED — Stories 27-2/27-3 substrate (NFR-E34-5)
    "supplementary",     # PRESERVED — original wrangler vocab (NFR-E34-5)
    "visual-primary",    # PRESERVED — Stories 27-2/27-3 substrate (NFR-E34-5)
    "visual-supplementary",  # PRESERVED — Stories 27-2/27-3 substrate (NFR-E34-5)
})
```

(That's actually 7 elements once written out; the §"6-role union" naming is shorthand from Winston A1 referring to the union itself, not the cardinality. Codex MUST extend to ALL members listed, not lose any.)

**D2. `excluded_reason` handling (FR-E34-3):** For sources with `role=ignored`:
- `excluded_reason` field MUST be present + non-empty
- Value MUST be in §02A's `ExcludedReason` enum: `{git-marker-file, macos-metadata, windows-metadata, llm-classified-out-of-scope}`
- If absent OR not in enum → `DirectiveError` with explicit error message naming the enum members

For sources with `role` in `{primary, supporting, validation, supplementary, visual-primary, visual-supplementary}`:
- `excluded_reason` MUST be absent (or None)
- If present + non-None → `DirectiveError` with explicit "excluded_reason forbidden on non-ignored sources"

**D3. Cross-field invariants from §02A (FR-E34-6 BINDING):**

Per `app/composers/section_02a/directive_model.py:80-106`, migrate these invariants to wrangler validator:

a) `role=ignored` → MUST have `excluded_reason` (covered by D2)
b) `role=ignored` → MUST NOT have `expected_min_words` (NEW invariant for wrangler)
c) `role=primary|supporting|supplementary|visual-*` → MUST NOT have `excluded_reason` (covered by D2)
d) Text extensions (`.docx`, `.md`) + role=primary|supporting|supplementary → MUST have `expected_min_words` (NEW invariant for wrangler — currently the wrangler doesn't check this)
e) Binary extensions (`.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.pdf`, `.pptx`) + role=supporting → MUST NOT have `expected_min_words` (Trial-2 anti-pattern guard; from §02A directive_model.py:97-105)

The validator MAY use a helper function (`_enforce_cross_field_invariants(src: dict, src_idx: int) -> None`) to keep validator readable. Each invariant violation raises `DirectiveError` with the specific clause cited.

**D4. Ignored-row filtering (downstream behavior — AC-34-2-B):**

After validation, before materialization, the wrangler MUST filter out `role=ignored` rows from materialization:
- Removed from `materials[]` in `result.yaml`
- Removed from `provenance[]` in `metadata.json`
- Removed from `extracted.md` content
- Audit-log line emitted per filtered-out row: `[run_wrangler] filtered ignored source: ref_id={ref_id} excluded_reason={excluded_reason} locator={locator}`

Implementation hint: at the boundary between `_load_directive` (validation) and materialization (extraction pipeline), insert a filter step. Per-row, if `role == "ignored"`, log + skip.

**D5. Primary-presence invariant preserved (AC-34-2-C):**

The existing rule at `run_wrangler.py:389-394` (at least one `role in {primary, visual-primary}`) is UNCHANGED in behavior. `ignored` rows do NOT count toward primary-presence. After D4 filtering, the primary-presence check operates on the post-filter `sources[]` list.

---

## Task chain T1-T11

**T1 readiness check:**
- C1 substrate amendment at commit `3159a0e` is HEAD or ancestor.
- Story 34-1 is `done` (verify `migration-34-1-section-02a-wrangler-integration-roundtrip-test: done` in `sprint-status.yaml`).
- §02A baseline at `app/composers/section_02a/directive_model.py:80-106` is read for cross-field invariant migration reference.
- Translator file `app/composers/section_02a/_wrangler_translator.py` exists post Story 34-1.

**T2 wrangler validator extension:**
- Open `skills/bmad-agent-texas/scripts/run_wrangler.py`.
- Locate the role-check block (currently lines 328-338).
- Replace with D1 7-element frozenset + D2 `excluded_reason` handling + D3 cross-field invariants.
- Wrangler-style invariants — fail-loud with `DirectiveError`; preserve closed-list shape (no string-comparison drift; NFR-E34-2).

**T3 ignored-row filter step:**
- After `_load_directive` returns, before per-source extraction, insert filter per D4.
- Audit-log via the wrangler's existing stdout/stderr printf pattern (or `logger.info` if a logger exists).

**T4 translator shrinkage:**
- Open `app/composers/section_02a/_wrangler_translator.py`.
- Remove `role-supporting-to-supplementary` from `TRANSLATOR_ACTIVE_MAPPINGS`.
- Remove `filter-ignored-rows` from `TRANSLATOR_ACTIVE_MAPPINGS`.
- Remove the corresponding mapping functions from `translate_directive_for_wrangler` body.
- POST: `TRANSLATOR_ACTIVE_MAPPINGS` should contain ONLY `{"src-id-to-ref-id"}` at this story close (Story 34-3 retires that last one).

**T5 tests author:**
- Author `tests/specialists/texas/test_wrangler_role_enum_union_and_excluded_reason.py` (or wrangler's adjacent test path):
  - Test role-acceptance for all 7 enum members
  - Test rejection of unknown role (e.g., `role=foo`)
  - Test `excluded_reason` required iff `role=ignored`
  - Test `excluded_reason` enum members
  - Test cross-field invariants (4 cases: text-needs-words; binary-forbids-words; ignored-forbids-words; ignored-requires-excluded-reason)
  - Test ignored-row filtering (verify NOT in materials, provenance, extracted.md after wrangler run)
  - Test primary-presence with ignored rows (must still fail-loud if ONLY ignored sources)

**T6 ruff + lint-imports:**
- `.venv/Scripts/python.exe -m ruff check skills/bmad-agent-texas/scripts/run_wrangler.py tests/specialists/texas/test_wrangler_role_enum_union_and_excluded_reason.py`
- `.venv/Scripts/python.exe -m lint_imports` — expect KEPT count unchanged.

**T7 focused suite run:**
- `.venv/Scripts/python.exe -m pytest skills/bmad-agent-texas/scripts/tests/ tests/specialists/texas/ tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py -v`
- Story 34-1 round-trip test MUST stay GREEN (with TRANSLATOR_ACTIVE_MAPPINGS now reduced to 1 element).

**T8 broad regression sweep:**
- Compare against 88-baseline per SCP §5 abort tripwire.
- Story 34-1 ratchet stay-green is BINDING abort trigger.

**T9 self-conducted G6 layered review** (standard layered; not cross-agent).

**T10 ready-for-review handoff:**
- Flip to `review` in `sprint-status.yaml`; write handoff at `_codex-handoff/34-2.ready-for-review.md`.

**T11 Claude review:**
- Verify D1-D5 contract compliance.
- Verify Story 34-1 ratchet stays green.
- Commit + flip done.

---

## Acceptance Criteria (carryforward from Epic 34 spec)

**AC-34-2-A** (role enum union): D1 BINDING; wrangler accepts all 7 enum members; cross-field invariants D2/D3 enforced.

**AC-34-2-B** (ignored-row filtering): D4 BINDING.

**AC-34-2-C** (primary-presence invariant preserved): D5 BINDING.

**AC-34-2-D** (translator shrinkage): T4 BINDING.

**AC-34-2-E** (regression sentinel): T7 BINDING — all 16 §02A upstream tests + Story-34-1 round-trip stay GREEN.

**AC-34-2-F** (Story-34-1 ratchet preserved): T8 BINDING — round-trip test PASS at close.

## Cross-references

- Epic 34 spec §"Story 34-2"
- Story 34-1 spec (translator scaffold contract)
- C1 SCP allowlist (run_wrangler.py + translator + test paths pre-allowlisted)
