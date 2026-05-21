# Codex dev-story prompt — Story 7c.3a (§02A LLM-Driven Directive Composer Body; Trial-2 finding #2 structural retirement; cross-agent MANDATORY)

**Cycle:** Claude spec (with locked contract decisions D1-D11 per AMEND-V5 pre-flight) → Codex T1-T9 + T10 self-review → Codex drops `_bmad-output/implementation-artifacts/_codex-handoff/7c-3a.ready-for-review.md` → **Claude T11 cross-agent MANDATORY `bmad-code-review`** → Claude commit + flip done.
**Wave:** 1 — slot 3 (highest-priority Wave 1 story; closes Trial-2 finding #2).
**Pre-authored:** 2026-05-04 ahead of operator dispatch with cross-agent pre-flight contract negotiation per AMEND-V5.
**Dispatch ordering:** **DISPATCH AFTER 7c.1 CLOSES** (Codex single-thread serializes 7c.3a behind 7c.0c → 7c.1). Predecessor chain technically clean post-7c.0b but operationally serial.
**AMELIA-P2 freshness check at dispatch.**

---

```
Run bmad-dev-story on Story 7c.3a (Slab 7c Wave 1; dual-gate; cross-agent code-review MANDATORY; §02A LLM-driven directive composer body — Trial-2 finding #2 structural retirement).

## ⚠️ CONTRACT-LOCKED STORY — D1-D11 ARE LOCKED AT SPEC-AUTHOR; DO NOT RELITIGATE.

The spec at `_bmad-output/implementation-artifacts/migration-7c-3a-section-02a-llm-directive-composer-body.md` carries 11 LOCKED contract decisions (D1-D11) per AMEND-V5 cross-agent pre-flight protocol. Your job: implement per the contract. If you disagree with a decision OR find an implementation-time obstacle, surface as `decision_needed` at T10 BEFORE completing — do NOT silently deviate. T11 cross-agent review verifies contract compliance, NOT contract negotiation.

## Required reading (read in order)

1. Story spec: `_bmad-output/implementation-artifacts/migration-7c-3a-section-02a-llm-directive-composer-body.md` (status: ready-for-dev; **§Contract Negotiation Decisions D1-D11 are LOCKED**; 6 ACs A-F; 11 task groups T1-T11).
2. **Trial-2 forensic fixture** (the broken corpus-scan output):
   - `state/config/runs/db276994-edf4-47a2-83bc-771cc214c3c1/directive.yaml` — broken Trial-2 directive; regression target.
   - `_bmad-output/implementation-artifacts/trial-2-postmortem-2026-05-04.md` — finding #2 forensic detail.
   - `_bmad-output/planning-artifacts/deferred-inventory.md` — `trial-2-finding-2-directive-composer-corpus-scan-fallback` entry; closed-by-7c.3a verdict at this story's close.
3. **Predecessor 7c.0a's frozen TripwireLedgerEntry pattern**: `app/models/tripwire_ledger.py` — triple-layer red-rejection on closed-enum reference (Enum + Literal + before-validator using TypeAdapter). Mirror this pattern for `DirectiveRole`.
4. **Predecessor 7c.0b's frozen DSL package**: `app/parity/contracts/__init__.py` — informational; §02A composer surface will register parity contract via 7c.3b's HIL pattern (NOT this story).
5. Slab 7c PRD: `_bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md` — FR-7c-1 + FR-7c-2 + FR-7c-5 + FR-7c-53 + NFR-7c-P1/P2/S6.
6. Slab 7c epics: `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md` (Story 7c.3a section starting at line 480).
7. Velocity-amendments artifact: `_bmad-output/planning-artifacts/slab-7c-velocity-amendments-2026-05-04.md` — AMEND-V5 cross-agent pre-flight rationale.
8. Required readings:
   - `docs/dev-guide/pydantic-v2-schema-checklist.md` — 14 idioms; Directive + DirectiveSource MUST conform.
   - `docs/dev-guide/dev-agent-anti-patterns.md` — A11 Windows-portability + A-test-1 mocking-SUT.
   - `docs/dev-guide/story-cycle-efficiency.md` — K-discipline 1.5×.
9. Governance JSON: `docs/dev-guide/migration-story-governance.json` story `7c-3a` (dual-gate; cross_agent_review_required=true; expected_pts=4; expected_k_target=1.5; r_tier=R3; t11_tier=cross-agent; lookahead_tier=3-AUTHORED; prerequisite_stories=[7c-0b]).
10. Sandbox-AC inventory: `docs/dev-guide/migration-ac-sandbox-inventory.json`.
11. **LEGACY composer (READ ONLY; FORBIDDEN to import per D9 C5):** `app/marcus/orchestrator/directive_composer.py` — produced Trial-2 finding #2's broken output. Inspect to understand the file-walk pattern + the bug; re-author the file-walk in `app/composers/section_02a/composer.py` WITHOUT importing the legacy module.
12. **§02A composer prompt-template precedent (7a Jinja2 patterns):** `docs/conversational-gates/g1.j2`, `g2c.j2`, etc. Your `section-02a-composer.j2` follows the same shape.

## T1 hard checkpoints (HALT-AND-SURFACE if violated)

- 7c.0a + 7c.0b + 7c.0c all `done`; 7c.1 `done` recommended (operationally serial via Codex single-thread).
- Trial-2 forensic fixture exists at `state/config/runs/db276994-edf4-47a2-83bc-771cc214c3c1/directive.yaml`. If absent, regression test `test_composer_trial_2_finding_2_regression.py` must `pytest.skip` with explicit reason (NOT silent skip; document in test).
- LangChain `BaseChatModel` importable: `.venv/Scripts/python.exe -c "from langchain_core.language_models import BaseChatModel; print('OK')"` resolves cleanly.
- `app/composers/` package may need creation (parent + `__init__.py`).
- D5 excluded-reason patterns cover real-world cases against Trial-2 corpus (filenames `.gitkeep`, `.DS_Store`, `Thumbs.db`); surface if additional canonical patterns emerge during implementation.
- pyproject.toml C5 contract exists with empty `forbidden_modules` (post-7c.0a state); refresh expected post-7c.3a state to D9 list.
- Class-conformance: 11 contracts; lint-imports: 12 KEPT.

## Files in scope

**New (~15 files):**
- `app/composers/__init__.py` (NEW package marker if parent doesn't exist).
- `app/composers/section_02a/__init__.py` (NEW; public exports of `Directive`, `DirectiveSource`, `DirectiveRole`, `ExcludedReason`, `compose`, `ComposerCache`).
- `app/composers/section_02a/composer.py` (NEW; D3 signature: `compose(corpus_dir: Path, *, llm: BaseChatModel, cache: ComposerCache | None = None) -> Directive`).
- `app/composers/section_02a/directive_model.py` (NEW; D4 Pydantic-v2 models with triple-layer red-rejection + 4 conditional invariants + Trial-2 binary-file invariant).
- `app/composers/section_02a/_prompt.py` (NEW; D6 Jinja2 loader + D7 cache-key normalization regex).
- `app/composers/section_02a/_cache.py` (NEW; D7 `ComposerCache` Pydantic-v2 wrapper + SHA256 derivation).
- `docs/conversational-gates/section-02a-composer.j2` (NEW; D6 Jinja2 prompt template).
- `tests/composers/__init__.py` (NEW package marker if parent doesn't exist).
- `tests/composers/section_02a/__init__.py` (NEW package marker).
- `tests/composers/section_02a/test_composer_directive_model_shape.py` (NEW; AC-A test pin).
- `tests/composers/section_02a/test_composer_classification.py` (NEW; AC-B test pin).
- `tests/composers/section_02a/test_composer_trial_2_finding_2_regression.py` (NEW; AC-C TW-7c-2 firing trigger).
- `tests/composers/section_02a/test_composer_cache_key_normalization.py` (NEW; AC-D test pin).
- `tests/composers/section_02a/test_composer_utf8_write.py` (NEW; AC-E test pin).
- `tests/structural/test_import_linter_c5_target_list_populated.py` (NEW; AC-F test pin).

**Modified:**
- `pyproject.toml` (D9 C5 `forbidden_modules` populated with 3 entries; KEPT count UNCHANGED at 12).
- `tests/structural/test_directive_io_uses_utf8_explicit.py` (T7 extension to include `app/composers/section_02a/composer.py` in `FILES_TO_SCAN`).

**Optionally modified (T8; surface as decision_needed if K-budget tight):**
- `docs/dev-guide/specialist-anti-patterns.md` — A11 seventh-instance reference to Trial-2 finding #2 retirement (cross-reference to 7c.3a). LOWER PRIORITY; skip if K-budget tight.

**Do NOT modify:**
- 7c.0a's ADR (`docs/dev-guide/adr/0001-parity-contract-dsl.md` — read only).
- 7c.0a's TripwireLedgerEntry (`app/models/tripwire_ledger.py` — read only; mirror its pattern, don't import).
- 7c.0b's DSL package (`app/parity/contracts/**` — read only).
- 7c.1's refactored test files (`tests/integration/transport_parity/**` + `tests/integration/transports/**` — read only).
- LEGACY directive composer (`app/marcus/orchestrator/directive_composer.py` — READ ONLY at T1 to understand the bug; DO NOT IMPORT per D9 C5).
- C4 + C6 forbidden_modules (only C5 is yours).
- Existing test BUSINESS LOGIC outside of T7 extension to AST scan.

**Do NOT introduce:**
- New third-party deps. LangChain + Pydantic v2 + Jinja2 + UUID + hashlib (stdlib) are sufficient.
- Imports of legacy `app.marcus.orchestrator.directive_composer` (FORBIDDEN per D9 C5).
- Imports of `app.composers._fallback` or `app.composers.legacy` (don't exist; FORBIDDEN per D9 C5 as a forward-looking guard).
- Live-LLM calls in non-`@pytest.mark.llm_live`-marked tests (NFR-7c-S6 + D10).
- Custom YAML parser (use `yaml.safe_dump` + `yaml.safe_load`).
- Per-test-function classification (composer is a single function called once per `compose` invocation).
- Mock the `compose` function in any of the 6 tests (use real composer + fixture-replay LLM stub).
- Defensive `serial` markers (post-7c.0c xdist defaults applied; if a 7c.3a test empirically fails under xdist, add the marker AS PART OF the fix).

## Critical implementation notes

- **Contract decisions D1-D11 are LOCKED.** If implementation surfaces a need to deviate, surface as `decision_needed` at T10 self-review BEFORE completing. Do NOT silently deviate.
- **K-target 1.5× ≈ ~3.75K LOC ceiling.** Estimate ~2.0-3.0K LOC. Comfortable headroom. Surface for K-renegotiation if T1.5 surfaces additional excluded-reason patterns or if D5 rule-based matching needs to extend significantly.
- **Cross-agent MANDATORY at T11** — Claude reviews FULL diff in fresh context. T10 self-review is supplemental.
- **Triple-layer red-rejection on `DirectiveRole`** — mirror 7c.0a's TripwireLedgerEntry pattern exactly. Layer 1 = Enum subclass; Layer 2 = Literal type with TypeAdapter at module level; Layer 3 = `field_validator(mode="before")` invoking the TypeAdapter on raw input.
- **Trial-2 finding #2 binary-file invariant (D4 bullet 5)** is the structural retirement core — `role=SUPPORTING + ext in {.png,.jpg,.jpeg,.gif,.bmp,.pdf,.pptx} + expected_min_words IS_NOT None` MUST raise `ValidationError` with the explicit anti-pattern message. Codex SHALL include the test for this exact case.
- **D5 rule-based excluded-reason matching is the optimization** — `.gitkeep` + `.DS_Store` + `Thumbs.db` SKIP the LLM call; only ambiguous files invoke the LLM. Each rule-based skip is 1 cache-hit-saving + 1 cache-miss-avoiding.
- **D8 TW-7c-2 firing trigger lives in the regression test, NOT the composer body.** If `test_composer_trial_2_finding_2_regression.py` fails at T9, surface as HALT-AND-SURFACE (NOT proceed to T10).
- **D9 C5 forbidden_modules is structural Trial-2 finding #2 retirement.** The legacy composer at `app/marcus/orchestrator/directive_composer.py` is ALIVE in the repo (do NOT delete; other migration code may reference it during transition); but the §02A composer is FORBIDDEN to import it. Re-author the file-walk logic; do NOT shortcut via legacy import.
- **D11 fixture path:** the regression test reads from `state/config/runs/db276994-edf4-47a2-83bc-771cc214c3c1/directive.yaml` AT-RUNTIME. If the fixture is absent (e.g., on a fresh checkout where the run dir was pruned), the test SHALL `pytest.skip` with explicit reason. NOT a HALT — the fixture is gitignored-but-operator-pinned per NFR-7c-OD6.
- **Cache-key normalization regex (D7)**: strip `operator_id` (likely value pattern), `{{generated_at}}` ISO-8601 timestamps (regex pattern), `run_id` UUID4 (regex pattern). Document the regex pattern in `_prompt.py` module docstring with each strip's rationale.
- **NFR-7c-S6 API key handling**: `OPENAI_API_KEY` from `.env`; tests `@pytest.mark.llm_live` auto-skip on placeholder. Document the placeholder pattern in test fixture (e.g., `if os.environ.get("OPENAI_API_KEY", "").startswith("placeholder-"): pytest.skip(...)`).
- **Windows portability per NFR-7c-X1**: `Path.write_text(yaml.safe_dump(directive.model_dump()), encoding="utf-8")`. Never default-encoding; never `PYTHONIOENCODING` workarounds.
- **No live API in focused tests.** Fixture-replay LLM stub returns hardcoded JSON.

## Verification battery (T9; R-tier R3; cross-agent T11 review)

```bash
# Focused tests (6 new test files):
.venv/Scripts/python.exe -m pytest tests/composers/section_02a/ tests/structural/test_import_linter_c5_target_list_populated.py -p no:randomly -q --tb=short

# T7 extended AST scan (post-extension):
.venv/Scripts/python.exe -m pytest tests/structural/test_directive_io_uses_utf8_explicit.py -p no:randomly -q --tb=short

# R3 broad regression (parallel default post-7c.0c; combined parallel + serial):
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line

# Class-conformance (11 contracts; no regression):
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/

# Lint-imports (12 KEPT; C5 target population doesn't add a new contract):
.venv/Scripts/lint-imports.exe

# Sandbox-AC validator:
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-3a-section-02a-llm-directive-composer-body.md

# Ruff hygiene on touched files (full app/composers + new tests + structural):
.venv/Scripts/python.exe -m ruff check app/composers/ tests/composers/ tests/structural/test_import_linter_c5_target_list_populated.py docs/conversational-gates/section-02a-composer.j2
```

Expected post-7c.3a outcomes:
- All 6 new focused tests PASS (no TW-7c-2 firing).
- T7 AST scan PASS (composer.py uses UTF-8 explicit).
- Combined parallel + serial pass total = T1.4 baseline (delta = 0; no broad-regression introduced).
- Class-conformance: 11 contracts (UNCHANGED).
- Lint-imports: 12 KEPT (UNCHANGED).
- Sandbox-AC: PASS.
- Ruff: clean.
- C5 target list populated with 3 forbidden_modules per D9.

## T10 + T11

**T10:** Codex G6 self-review at `_bmad-output/implementation-artifacts/_codex-handoff/7c-3a.ready-for-review.md`. Per dropbox protocol — drop the completion notice. Flip story status `in-progress` → `review` in spec file.

**Critical T10 content (cross-agent MANDATORY review at T11 needs this evidence):**
- **Contract-decision compliance table**: D1-D11 each, with PASS/DEVIATION/SURFACE-FOR-OPERATOR verdict. If ANY decision shows DEVIATION, surface as `decision_needed` for operator BEFORE completing T10.
- File list (~15 NEW + 2 modified).
- TW-7c-2 firing status: PASS (no firing) — explicitly verified.
- Trial-2 finding #2 deferred-inventory entry status: closed-by-7c.3a (verify in deferred-inventory.md update at T8 if undertaken; or surface as TODO for next session).
- Wall-clock report: focused-test time + R3 broad regression time (parallel + serial combined).
- Broad-regression delta vs T1.4 baseline (numbers).
- Cache-hit metric on fixture-replay tests (NFR-7c-P2 informational).
- Live-LLM test skip count (`@pytest.mark.llm_live` count + skip-reason).
- Layered self-review (Blind + Edge + Auditor) per current convention.

**T11:** Claude (separate cold context from Codex dev) does FINAL `bmad-code-review` (**CROSS-AGENT MANDATORY** per governance JSON cross_agent_review_required=true). T11 is a **VERIFICATION pass** of the locked contract; NOT relitigation. Review verdict at `_bmad-output/implementation-artifacts/7c-3a-code-review-2026-05-NN.md`. Claude verifies:
- Contract-decision compliance D1-D11 each (matches Codex T10's table).
- Triple-layer red-rejection on DirectiveRole correctly mirrors TripwireLedgerEntry pattern.
- Trial-2 finding #2 binary-file invariant test explicitly present + asserts the exact anti-pattern (`role=SUPPORTING + ext=.png + expected_min_words=200` raises).
- D5 rule-based excluded-reason patterns applied correctly (3 cases pre-LLM).
- D6 Jinja2 prompt template structure + cache-key normalization regex (D7) is auditable + documented.
- D8 TW-7c-2 firing test PASSES (composed directive ≠ Trial-2 broken directive).
- D9 C5 target list = 3 forbidden_modules; lint-imports KEPT 12.
- D11 fixture-skip path documented if absent.
- NFR-7c-S6 API key handling + `@pytest.mark.llm_live` markers correct.
- Combined-pass invariant: NFR-7c-R2 ≥1403 deterministic baseline preserved.

Claude applies remediation cycles per HALT-AND-REMEDIATE; commits the diff; flips `migration-7c-3a-section-02a-llm-directive-composer-body: review → done` in sprint-status.yaml.

## Boundary

- **HALT and surface to operator on:**
  (a) 7c.0a OR 7c.0b OR 7c.0c status NOT `done`.
  (b) Trial-2 forensic fixture absent AND no documented skip path.
  (c) LangChain `BaseChatModel` not importable.
  (d) **Contract-decision deviation** (D1-D11): silent deviation is forbidden; surface at T10 BEFORE completing.
  (e) AC-7c.3a-C TW-7c-2 firing test FAILS (composer reproduces Trial-2 broken classifications): TW-7c-2 fires HIGH severity → STOP → re-scope §02A → dual-nature claim invalidated → operator decision.
  (f) D5 excluded-reason pattern matching surfaces a real-world file the rules don't cover (e.g., a corpus contains `.thumbs/` directory or `.~lock.docx#` LibreOffice marker): surface for D5 extension.
  (g) Cache-key normalization regex (D7) cannot deterministically strip `operator_id`/timestamps/`run_id` because their formats are ambiguous: surface for D7 refinement.
  (h) Any focused test fails at T9.
  (i) Combined parallel + serial pass total ≠ T1.4 baseline (NFR-7c-R2 invariant violation).
  (j) Lint-imports KEPT count ≠ 12 (contract introduced or demoted; C5 target population MUST keep count = 12).
  (k) Class-conformance regression.
  (l) ANY sandbox-AC violation.

- **Do NOT touch:**
  - 7c.0a's TripwireLedgerEntry (mirror its pattern; do NOT import).
  - 7c.0b's DSL package (informational only).
  - LEGACY composer (READ ONLY at T1; DO NOT IMPORT per D9 C5).
  - 7c.1's refactored test files.
  - C4 or C6 forbidden_modules.

- **Do NOT introduce:**
  - New third-party deps.
  - Imports of legacy `app.marcus.orchestrator.directive_composer`.
  - Live-LLM calls in non-marked tests.
  - Custom YAML parser.
  - Mock the `compose` function (use real + stub LLM).
  - Defensive `serial` markers without empirical xdist failure.
  - Per-test-function `@parity_contract` decoration (this story doesn't register a parity contract; that's 7c.3b's territory).
```

---

## Operator dispatch checklist (before sending this prompt to Codex)

1. ☐ Verify `migration-7c-0a-decision-foundation: done` AND `migration-7c-0b-scaffold-foundation: done` AND `migration-7c-0c-pytest-xdist-classification: done` in BOTH spec files AND sprint-status.yaml. 7c.1 `done` recommended (operationally serial).
2. ☐ Run `.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-3a-section-02a-llm-directive-composer-body.md` → expect PASS.
3. ☐ AMELIA-P2 freshness check: Claude re-diffs `migration-7c-3a-section-02a-llm-directive-composer-body.md` against this prompt; if spec hash changed since 2026-05-04 authoring, regenerate this prompt before dispatch.
4. ☐ Verify governance JSON entry for 7c-3a is current (dual-gate; cross_agent_review_required=true; r_tier=R3; t11_tier=cross-agent; lookahead_tier=3-AUTHORED; pts=4; K=1.5; prerequisite_stories=[7c-0b]) — locked at v2026-05-04-velocity-amendments-bundle.
5. ☐ Confirm sprint-status.yaml shows `migration-7c-3a-section-02a-llm-directive-composer-body: ready-for-dev`.
6. ☐ Verify Trial-2 forensic fixture exists at `state/config/runs/db276994-edf4-47a2-83bc-771cc214c3c1/directive.yaml`.
7. ☐ Verify LangChain `BaseChatModel` importable: `.venv/Scripts/python.exe -c "from langchain_core.language_models import BaseChatModel; print('OK')"`.
8. ☐ Dispatch this prompt to Codex; Codex flips status `ready-for-dev → in-progress` at T1 start.

## Post-Codex-T10 dropbox-watch protocol

1. ☐ Codex drops `_bmad-output/implementation-artifacts/_codex-handoff/7c-3a.ready-for-review.md` upon T10 completion.
2. ☐ Claude (separate cold context) reads the dropbox notice + the ~15-file diff + contract-decision compliance table; runs `bmad-code-review` (T11; **CROSS-AGENT MANDATORY**).
3. ☐ Claude verifies D1-D11 compliance + Trial-2 invariants + TW-7c-2 firing PASS + cache-key stability + UTF-8 write + C5 population + combined-pass invariant.
4. ☐ Claude applies remediation cycles per HALT-AND-REMEDIATE if any.
5. ☐ Claude commits + flips `migration-7c-3a-section-02a-llm-directive-composer-body: review → done` in sprint-status.yaml.
6. ☐ At 7c.3a close, Trial-2 finding #2 deferred-inventory entry status flips to `closed-by-7c.3a`. Trial-3 G0 ratification surface (7c.3b's HIL pattern) inherits a working LLM-driven directive.
