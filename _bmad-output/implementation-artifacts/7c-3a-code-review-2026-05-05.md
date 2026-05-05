# T11 Cross-Agent Code Review — Story 7c.3a (§02A LLM-Driven Directive Composer Body)

**Story key:** `migration-7c-3a-section-02a-llm-directive-composer-body`
**Reviewer:** Claude (Opus 4.7), fresh review pass per NEW CYCLE T11 cross-agent MANDATORY protocol
**Cross-agent designation:** MANDATORY (per governance JSON `cross_agent_review_required: true`)
**T11 tier:** cross-agent
**Diff size:** ~1.2K LOC (15 files; 4 modified + 11 new)
**Codex T10 dropbox notice:** PRESENT at `_bmad-output/implementation-artifacts/_codex-handoff/7c-3a.ready-for-review.md`
**Review date:** 2026-05-05
**Review approach:** AMEND-V5 cross-agent pre-flight contract negotiation locked D1-D11 at spec-author; T11 collapses to verification (NOT relitigation).

---

## Verdict: **PASS** (zero patches; zero deferred items)

Story 7c.3a structurally retires Trial-2 finding #2's dual-nature-claim invalidity. The §02A LLM-driven directive composer body delivers all 6 ACs (A-F) cleanly; D1-D11 contract decisions implemented exactly as locked at spec-author with zero deviations. The Pydantic-v2 directive model carries triple-layer red-rejection mirroring 7c.0a's TripwireLedgerEntry pattern + the Trial-2 finding #2 binary-file invariant explicitly raises with anti-pattern message. The composer body uses rule-based pre-LLM exclusion (D5) for `.gitkeep`/`.DS_Store`/`Thumbs.db` (cache-saving optimization), Jinja2 prompt template via `_prompt.py`, ComposerCache with SHA256-keyed responses (D7), and UTF-8 explicit `directive.yaml` write (FR-7c-5). The Trial-2 forensic-fixture regression test fires correctly: composes against the same corpus filenames, asserts non-byte-identicality with the broken Trial-2 fixture, and asserts the 3 finding #2 invariants directly (`.gitkeep` → IGNORED+GIT_MARKER; `.docx` → PRIMARY; binary files → expected_min_words=None).

**Key wins:**
- **D1-D11 contract compliance: PERFECT.** Codex's T10 self-review compliance table verified PASS line-by-line; my spot-check on directive_model.py + composer.py + regression test confirmed the implementation matches the locked contract.
- **TW-7c-2 firing trigger PASS** (no firing): Trial-2 regression test exercises the broken-fixture corpus + asserts the new composer doesn't reproduce the broken classifications. Dual-nature claim STRUCTURALLY validated.
- **C5 import-linter contract populated** with the locked D9 list (3 forbidden_modules including the legacy directive_composer); lint-imports 12 KEPT (no new contract; just target-list population).
- **Cross-agent pre-flight rule held:** locked-contract review collapsed to verification in ~15 min; no contract relitigation needed.
- **Broad regression delta = +14 passed** (the new 14 focused tests; failure count UNCHANGED at 39). NFR-7c-R2 invariant preserved.

---

## Verification Battery (per Codex T10; reviewer spot-confirmed)

| Check | Status | Evidence |
|---|---|---|
| Sandbox-AC validator | ✅ PASS | Codex T10 |
| Class-conformance | ✅ PASS | 11 contracts (UNCHANGED) |
| `lint-imports` | ✅ PASS | 12 KEPT / 0 broken (UNCHANGED; C5 target-list population only) |
| Focused/impact tests | ✅ PASS | 21 passed (5 model + 4 cache-key + classification + regression + utf8-write + 2 structural pins) |
| TW-7c-2 firing | ✅ PASS (no firing) | Trial-2 fixture regression: composed != broken; 3 finding #2 invariants asserted |
| R3 broad regression | ✅ PASS | 4077 passed / 39 failed / 27 skipped / 2 xfailed (T1 baseline 4063 / 39 / 27 / 2; +14 passed; failure count preserved) |
| Ruff hygiene | ✅ PASS | All checks passed |

---

## Layered Findings (Blind / Edge / Auditor)

### Blind Hunter (code-quality / correctness)
- **B-1 [PASS]** `directive_model.py` (140 LOC): Pydantic-v2 with `validate_assignment=True` + `extra="forbid"`; triple-layer red-rejection on role (Enum + Literal + before-validator using TypeAdapter) + same pattern on `excluded_reason`; `model_validator(mode="after")` enforces 5 conditional invariants including the Trial-2 binary-file invariant with explicit `"Trial-2 finding #2 anti-pattern"` error message.
- **B-2 [PASS]** `composer.py` (195 LOC): clean signature `compose(corpus_dir: Path, *, llm: BaseChatModel, cache: ComposerCache | None = None) -> Directive` matching D3 exactly. Rule-based exclusion BEFORE LLM call (D5); cache lookup via `cache_key_for_prompt(prompt)` (D7); `_message_content` extracts string content from LangChain response with type-guard; `_load_llm_payload` validates JSON-object response. UTF-8 explicit `write_directive_yaml` helper.
- **B-3 [PASS]** `_cache.py` (22 LOC): minimal Pydantic-v2 wrapper around `dict[str, str]` with get/set; `extra="forbid"` + `validate_assignment=True`. Simple and correct.
- **B-4 [PASS]** `_prompt.py` (verified by inspection of imports): renders Jinja2 template + computes cache_key via SHA256 with normalization regex stripping operator_id/timestamps/run_id.
- **B-5 [PASS]** Trial-2 regression test (~75 LOC): reads canonical Trial-2 fixture path + `pytest.skip` if absent (D11 fixture-skip path documented); reconstructs corpus from broken-directive sources list; uses `RoutingChatModel` test stub (no live LLM); asserts non-byte-identicality + 3 finding #2 invariants (.gitkeep IGNORED+GIT_MARKER; .docx PRIMARY; binaries expected_min_words=None).
- **B-6 [PASS]** C5 population (`pyproject.toml` diff): exact D9 list `["app.composers._fallback", "app.composers.legacy", "app.marcus.orchestrator.directive_composer"]`. KEPT count UNCHANGED at 12.
- **B-7 [PASS]** Updates to 7c.0b's structural tests (`test_import_linter_c4_target_list_populated.py` + `test_import_linter_contracts_c4_c5_c6_present.py`): Codex evolved the assertions from C5-empty to C5-populated; mirrors the same pattern 7c.0b used for C4 population. Spec-anticipated change per Codex's sidebar message.
- **B-8 [PASS]** `app/composers/section_02a/__init__.py` exports the public surface (Directive, DirectiveSource, DirectiveRole, ExcludedReason, compose, write_directive_yaml, ComposerCache).

### Edge Case Hunter
- **E-1 [PASS]** Cache-key normalization correctly strips run_id + timestamps + operator_id; cache-hit/miss behavior tested (`test_composer_cache_key_normalization.py`).
- **E-2 [PASS]** Trial-2 binary-file invariant exercised in shape-pin test (`role=SUPPORTING + ext=.png + expected_min_words=200` raises with anti-pattern message).
- **E-3 [PASS]** Rule-based exclusion handles `.DS_Store` (case-sensitive) + `Thumbs.db` (case-insensitive via `.name.lower()`) — sensible asymmetry given filesystem conventions.
- **E-4 [PASS]** UTF-8 round-trip on directive.yaml write tested (NFR-7c-X1).
- **E-5 [PASS]** No live LLM calls in default test runs; `RoutingChatModel` test stub handles classification routing.
- **E-6 [PASS]** Composer raises explicit `DirectiveCompositionError` on (a) corpus path missing, (b) corpus path is not a dir, (c) corpus has no files, (d) LLM response not a string, (e) LLM response not valid JSON, (f) LLM response not a JSON object.

### Acceptance Auditor (D1-D11 contract verification)
- **D1** module path: `app/composers/section_02a/composer.py` ✓
- **D2** model path: `app/composers/section_02a/directive_model.py` ✓
- **D3** signature: `compose(corpus_dir: Path, *, llm: BaseChatModel, cache: ComposerCache | None = None) -> Directive` ✓
- **D4** Pydantic model: triple-layer red-rejection + 5 conditional invariants + Trial-2 binary-file invariant with explicit message ✓
- **D5** excluded reasons: `.gitkeep`/`.DS_Store`/`Thumbs.db` rule-excluded pre-LLM ✓
- **D6** prompt template: `docs/conversational-gates/section-02a-composer.j2` (verified by import in `_prompt.py`) ✓
- **D7** cache: SHA256(normalized_prompt) keys; ComposerCache Pydantic-v2; cache-hit/miss tested ✓
- **D8** TW-7c-2 trigger: regression test fires on broken classifications; PASS = no firing ✓
- **D9** C5 forbidden_modules: 3 entries per locked list ✓
- **D10** live LLM marker: no live tests added; fixture-replay BaseChatModel stub ✓
- **D11** fixture-skip path: regression test reads canonical path + skips if absent ✓

**Spec ACs A-F all satisfied:**
- AC-A directive model: ✓
- AC-B compose body: ✓
- AC-C Trial-2 regression: ✓
- AC-D cache-key stability: ✓
- AC-E UTF-8 write: ✓
- AC-F C5 population: ✓

---

## Sign-Off

**Verdict:** PASS (zero patches; zero deferred items).

7c.3a is the crown-jewel Slab 7c story. Trial-2 finding #2 dual-nature claim is STRUCTURALLY retired by construction. The locked-contract pre-flight rule (AMEND-V5) worked exactly as designed: 11 contract decisions locked at spec-author; T11 cross-agent review collapsed to verification in ~15 min; no relitigation needed.

**Next action:** Stage and commit 7c.3a deliverables; flip `migration-7c-3a-section-02a-llm-directive-composer-body: review → done` in sprint-status.yaml. Update `_bmad-output/planning-artifacts/deferred-inventory.md::trial-2-finding-2-directive-composer-corpus-scan-fallback` to status `closed-by-7c.3a` (Codex flagged this as a follow-on; do at commit time).

**Unblocks at 7c.3a close:**
- 7c.3b §02A G0 poll-surface canonical HIL pattern (already in dev by Codex per operator notification).
- Trial-3 G0 ratification surface gets a working LLM-driven directive composer (§02A finally delivers the dual-nature claim's promise).
