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

**New (SUBSTRATE-AUDIT-CORRECTED 2026-05-22 — existing wrangler-validator tests live at `skills/bmad-agent-texas/scripts/tests/`, NOT `tests/specialists/texas/`; verified via Glob):**
- `skills/bmad-agent-texas/scripts/tests/test_run_wrangler_role_enum_union_and_excluded_reason.py` (NEW; co-located with existing `test_run_wrangler.py`)

Note: `tests/specialists/texas/` contains tests for the LangGraph specialist node (Story 7b.1 surface), NOT wrangler validator unit tests. Story 34-2's wrangler-validator changes are tested at the script-level via the wrangler subprocess, not via the specialist node.
- Translator-shrinkage update at `app/composers/section_02a/_wrangler_translator.py`: remove `role-supporting-to-supplementary` AND `filter-ignored-rows` mappings from `TRANSLATOR_ACTIVE_MAPPINGS` (Story 34-1's frozenset shrinks)

**Lookahead tier:** **1** (focused; small surface).
**Wave:** 1 — slot 2 (substrate change; lands BEFORE Story 34-3 per Winston A3 substrate-before-cosmetic ordering).

**FR coverage:** FR-E34-2 (6-role union), FR-E34-3 (excluded_reason), FR-E34-6 (cross-field invariants migrate).
**NFR coverage:** NFR-E34-1 (integration test mandatory — Story 34-1's ratchet), NFR-E34-2 (Pydantic-v2 closed-enum preserved), NFR-E34-4 (LLM-judged taxonomy not destroyed), NFR-E34-5 (27-2/27-3 substrate preserved), NFR-E34-8 (TW-7c-4 dual-predicate), NFR-E34-11..13 (NEW CYCLE + sandbox-AC + governance validator).

**Contract Decisions (LOCKED 2026-05-22):**

**D1. Role enum extension (Winston A1 BINDING — SUBSTRATE-AUDIT-CORRECTED 2026-05-22):**

**Current substrate** (verified via Read of `run_wrangler.py:328-338`):
```python
if src["role"] not in (
    "primary",
    "validation",
    "supplementary",
    "visual-primary",
    "visual-supplementary",
):
    raise DirectiveError(
        f"sources[{i}].role must be primary|validation|supplementary"
        f"|visual-primary|visual-supplementary, got {src['role']!r}"
    )
```

**Story 34-2 deliverable: extract to module-level constant AND extend the 5-element tuple to 7-element frozenset.** The wrangler currently uses an INLINE tuple (no named constant). Story 34-2 introduces:

```python
# At module top (alongside _SUPPORTED_PROVIDERS at line 228):
_ALLOWED_ROLES: frozenset[str] = frozenset({
    "primary",
    "supporting",        # NEW — §02A taxonomy
    "ignored",           # NEW — §02A taxonomy (filtered before materialization per D4)
    "validation",        # PRESERVED — Stories 27-2/27-3 substrate
    "supplementary",     # PRESERVED — original wrangler vocab
    "visual-primary",    # PRESERVED — Stories 27-2/27-3 substrate
    "visual-supplementary",  # PRESERVED — Stories 27-2/27-3 substrate
})

# At lines 328-338 (REPLACE inline tuple with constant reference):
if src["role"] not in _ALLOWED_ROLES:
    raise DirectiveError(
        f"sources[{i}].role must be one of "
        f"{sorted(_ALLOWED_ROLES)}, got {src['role']!r}"
    )
```

Refactor-to-constant is INTENTIONAL story scope (improves testability + downstream consumers like the ignored-row filter in D4 can reuse the same set). The §"6-role union" naming in Winston A1 is shorthand for the union itself — 7 elements once written out (one preserved + two new + four 27-2/27-3 visual+validation+supplementary).

**D2. `excluded_reason` handling (FR-E34-3 — SUBSTRATE-AUDIT-CORRECTED 2026-05-22):**

Insert new validation block at the boundary between role-check (currently line 338, post-D1 refactor) and ref_id-check (currently line 339):

```python
# After D1's `if src["role"] not in _ALLOWED_ROLES:` raise block at ~line 338:
# NEW excluded_reason cross-field invariants (D2):
_ALLOWED_EXCLUDED_REASONS: frozenset[str] = frozenset({
    "git-marker-file",
    "macos-metadata",
    "windows-metadata",
    "llm-classified-out-of-scope",
})

if src["role"] == "ignored":
    excluded_reason = src.get("excluded_reason")
    if not isinstance(excluded_reason, str) or not excluded_reason.strip():
        raise DirectiveError(
            f"sources[{i}].excluded_reason MUST be a non-empty string "
            f"when role=ignored; got {excluded_reason!r}"
        )
    if excluded_reason not in _ALLOWED_EXCLUDED_REASONS:
        raise DirectiveError(
            f"sources[{i}].excluded_reason must be one of "
            f"{sorted(_ALLOWED_EXCLUDED_REASONS)}, got {excluded_reason!r}"
        )
else:
    # role in {primary, supporting, validation, supplementary, visual-primary, visual-supplementary}
    if "excluded_reason" in src and src["excluded_reason"] is not None:
        raise DirectiveError(
            f"sources[{i}].excluded_reason forbidden on non-ignored sources; "
            f"role={src['role']!r} got excluded_reason={src['excluded_reason']!r}"
        )
```

`_ALLOWED_EXCLUDED_REASONS` constant lives at module level (alongside `_ALLOWED_ROLES` per D1) and mirrors §02A's `ExcludedReason` enum at `app/composers/section_02a/directive_model.py:44-50`.

**D3. Cross-field invariants from §02A (FR-E34-6 BINDING):**

Per `app/composers/section_02a/directive_model.py:80-106`, migrate these invariants to wrangler validator:

a) `role=ignored` → MUST have `excluded_reason` (covered by D2)
b) `role=ignored` → MUST NOT have `expected_min_words` (NEW invariant for wrangler)
c) `role=primary|supporting|supplementary|visual-*` → MUST NOT have `excluded_reason` (covered by D2)
d) Text extensions (`.docx`, `.md`) + role=primary|supporting|supplementary → MUST have `expected_min_words` (NEW invariant for wrangler — currently the wrangler doesn't check this)
e) Binary extensions (`.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.pdf`, `.pptx`) + role=supporting → MUST NOT have `expected_min_words` (Trial-2 anti-pattern guard; from §02A directive_model.py:97-105)

The validator MAY use a helper function (`_enforce_cross_field_invariants(src: dict, src_idx: int) -> None`) to keep validator readable. Each invariant violation raises `DirectiveError` with the specific clause cited.

**D4. Ignored-row filtering (downstream behavior — AC-34-2-B; SUBSTRATE-AUDIT-CORRECTED 2026-05-22):**

After validation, before materialization, the wrangler MUST filter out `role=ignored` rows. **Verified substrate control flow** (Read of `run_wrangler.py:1771-1820`):

```python
# Current locator-shape path at lines 1774-1778:
outcomes: list[SourceOutcome] = []
for src in directive["sources"]:
    outcomes.append(_wrangle_source(src, run_timestamp))
```

**Story 34-2 deliverable: insert ignored-row filter at line 1776 (immediately before the materialization for-loop). Filter ignored rows from `directive["sources"]` + emit audit log line per filtered row.**

```python
# At line 1776, REPLACE the for-loop start:
ignored_sources = [src for src in directive["sources"] if src["role"] == "ignored"]
non_ignored_sources = [src for src in directive["sources"] if src["role"] != "ignored"]

for ignored_src in ignored_sources:
    print(  # or wrangler's existing log mechanism — verify at T1
        f"[run_wrangler] filtered ignored source: "
        f"ref_id={ignored_src['ref_id']} "
        f"excluded_reason={ignored_src.get('excluded_reason', 'unknown')} "
        f"locator={ignored_src.get('locator', '<no-locator>')}",
        file=sys.stderr,  # audit log to stderr; preserves stdout for --json
    )

outcomes: list[SourceOutcome] = []
for src in non_ignored_sources:
    outcomes.append(_wrangle_source(src, run_timestamp))
```

Result: `outcomes`, `extracted.md`, `metadata.json::provenance`, `result.yaml::materials` ALL exclude ignored rows. Audit log emitted to stderr (does not pollute --json stdout).

**Codex T1 verification:** confirm wrangler's existing log mechanism (print to stderr vs Python `logging`). The file uses `print(..., file=sys.stderr)` pattern at multiple sites (verify; if `logging`, use that instead).

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
