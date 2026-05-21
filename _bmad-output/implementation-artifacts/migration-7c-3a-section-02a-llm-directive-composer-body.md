# Migration Story 7c.3a: §02A LLM-Driven Directive Composer Body — Trial-2 Finding #2 Structural Retirement

**Status:** done *(spec authored 2026-05-04 with cross-agent contract negotiation per AMEND-V5 pre-flight; predecessor 7c-0b CLOSED `done` commit `9114337`. Codex T1-T10 complete 2026-05-05; operator accepted reviewed/closed 2026-05-05.)*
**Sprint key:** `migration-7c-3a-section-02a-llm-directive-composer-body`
**Epic:** Slab 7c — Marcus Orchestrational Tail (`migration-epic-slab-7c-orchestrational-tail`)
**Pts:** 4
**Gate:** **dual-gate** + **cross-agent code-review MANDATORY** (per `docs/dev-guide/migration-story-governance.json` v2026-05-04-velocity-amendments-bundle, story 7c-3a; rationale: `substrate_shape + invariant_preservation`; cross-agent justified per Murat M6 — closes Trial-2 finding #2 dual-nature claim)
**K-target:** ~1.5× (substrate-shape; ~4 pts; bounded surface = §02A composer module + Pydantic-v2 directive model + Jinja2 prompt template + cache mechanism + Trial-2 forensic regression test + 6 contract-locked sub-decisions verified at T11)
**R-tier (regression scope):** **R3** — full broad regression. Trial-2 finding #2 retirement is invariant-preservation; substrate change risk warrants full coverage.
**T11-tier (review approach):** **cross-agent** — MANDATORY full-fresh-context Blind/Edge/Auditor per governance JSON `cross_agent_review_required: true`. NEVER batched.
**Files touched (declared at spec-author time):**
- `app/composers/section_02a/__init__.py` (NEW; package marker + public exports)
- `app/composers/section_02a/composer.py` (NEW; `compose(corpus_dir, *, llm) -> Directive` body)
- `app/composers/section_02a/directive_model.py` (NEW; `Directive` + `DirectiveSource` Pydantic-v2 models)
- `app/composers/section_02a/_prompt.py` (NEW; Jinja2 prompt-loading helper + cache-key normalization)
- `app/composers/section_02a/_cache.py` (NEW; in-memory cache keyed by SHA256(normalized prompt))
- `docs/conversational-gates/section-02a-composer.j2` (NEW; per-file classification prompt template per 7a precedent)
- `pyproject.toml` (MODIFY; populate C5 `forbidden_modules` per FR-7c-53)
- `tests/composers/section_02a/__init__.py` (NEW; package marker)
- `tests/composers/section_02a/test_composer_directive_model_shape.py` (NEW; Pydantic v2 idiom shape-pin)
- `tests/composers/section_02a/test_composer_classification.py` (NEW; LLM-driven classification with fixture-replay)
- `tests/composers/section_02a/test_composer_trial_2_finding_2_regression.py` (NEW; Trial-2 fixture regression — TW-7c-2 firing trigger)
- `tests/composers/section_02a/test_composer_cache_key_normalization.py` (NEW; cache-key SHA256 stability)
- `tests/composers/section_02a/test_composer_utf8_write.py` (NEW; FR-7c-5 UTF-8 round-trip on directive.yaml write)
- `tests/structural/test_import_linter_c5_target_list_populated.py` (NEW; structural test verifies C5 populated post-7c.3a)
- `tests/composers/fixtures/trial-2/` (NEW; mirror of `state/config/runs/db276994-edf4-47a2-83bc-771cc214c3c1/` content as gitignored-untracked OR carved-down anonymized fixture; surface as `decision_needed` at T1)
**Lookahead tier:** **3 → AUTHORED** — was Tier 3 (held until contract negotiation); spec authored 2026-05-04 per AMEND-V5 cross-agent pre-flight 15-min contract-negotiation pass (decisions locked below in §Contract Negotiation Decisions). Cross-agent T11 review collapses to verification, not negotiation.
**Authored:** 2026-05-04 via `bmad-create-story` workflow + AMEND-V5 cross-agent pre-flight contract negotiation.
**Wave:** 1 — slot 3 (highest-priority Wave 1 story per epic prose; closes Trial-2 finding #2 dual-nature claim).

**FR coverage:**
- **FR-7c-1** Marcus can compose a directive YAML from a corpus directory using LLM reasoning (NOT corpus-scan fallback). The §02A composer is THIS STORY'S DELIVERABLE.
- **FR-7c-2** Marcus can validate composed directive against Trial-2 forensic fixture (`state/config/runs/db276994-edf4-47a2-83bc-771cc214c3c1/`) without reproducing the byte-identical broken directive Trial-2 captured. Regression test owns this assertion.
- **FR-7c-5 (partial)** Marcus preserves UTF-8 round-trip across §02A lifecycle on the WRITE side (compose → write `directive.yaml`). Read-side UTF-8 was retired by 7c.2's structural fix; this story's contribution is the composer's write-side UTF-8-explicit invariant.
- **FR-7c-53 C5** Composer boundary import-linter contract — populate C5 `forbidden_modules` with the corpus-scan fallback paths the composer MUST NOT import.

**NFR coverage:**
- **NFR-7c-P1** §02A LLM-driven composition target ≤60s wall-clock for ≤20-file corpus at gpt-5.4 cache-cold; ≤60s p50 / ≤120s p99 over ≥20 fixture-replay runs; cache-hit ≤2s p99.
- **NFR-7c-P2** Prompt-token count stable across N=10 runs (variance ≤5%); ≥90% cache-hit median[2:]; cache-key normalization rule = `cache_key = SHA256(normalized_prompt)` with `operator_id` + timestamps + `run_id` stripped.
- **NFR-7c-S1** HIL tamper-evidence at writer boundary per D3 (the composer is a writer; output `directive.yaml` carries digest verification at downstream poll surface 7c.3b).
- **NFR-7c-S6** API key handling: `OPENAI_API_KEY` from `.env`; never logged; live-LLM tests `@pytest.mark.llm_live`; auto-skip on placeholder.
- **NFR-7c-X1** Windows-portability — UTF-8-explicit write of `directive.yaml`.
- **NFR-7c-M5** sandbox-AC validator PASS.

**Standing-guardrail enforcement:**
- SG-1 unchanged (composer is orchestration, not specialist).
- SG-2 §02A row in mapping checklist preserved + status improved at retrospective (FR-7c-2 retirement evidence).
- SG-3 Composition Spec §3.1 + §3.5 + §3.6 honored on composer envelope contribution (composer emits to writer-boundary; downstream poll 7c.3b picks it up).
- SG-4 unchanged.

**Tripwire ownership:** **TW-7c-2** detection ownership (cp1252 regression IS retired by 7c.2; this story's TW-7c-2 firing concerns the regression test against Trial-2 forensic fixture — if the test FAILS post-implementation, TW-7c-2 fires high severity; STOP; re-scope §02A; dual-nature claim invalidated).

**Implementation cycle (NEW CYCLE):**
- **Claude (Opus 4.7):** authored this spec with locked contract decisions per AMEND-V5 pre-flight 2026-05-04; sandbox-AC validator PASS; governance JSON entry verified post-velocity-bundle; pre-authored `_bmad-output/implementation-artifacts/codex-dev-prompt-7c-3a-section-02a-llm-directive-composer-body.md` ahead of operator demand.
- **Codex (Sonnet 4.5 or later):** develops §02A composer + Pydantic-v2 directive model + Jinja2 prompt template + cache mechanism + 6 tests + C5 target population per the locked contract decisions below; reaches `review` status; produces a self-conducted T10 layered review at `_bmad-output/implementation-artifacts/_codex-handoff/7c-3a.ready-for-review.md`.
- **Claude T11 cross-agent review:** verifies Codex's implementation matches the locked contract (decisions are NOT relitigated; only verification). Commits + flips `migration-7c-3a-section-02a-llm-directive-composer-body: review → done`.

---

## Contract Negotiation Decisions (LOCKED 2026-05-04 per AMEND-V5 pre-flight)

The following decisions are LOCKED at spec-author time. Cross-agent T11 review verifies Codex's implementation matches; does NOT relitigate the contract. Any Codex deviation surfaces as HALT-AND-SURFACE for operator decision.

**D1. Module path:** `app/composers/section_02a/composer.py` (per FR-7c-1).

**D2. Pydantic-v2 directive model location:** `app/composers/section_02a/directive_model.py` — SEPARATE module from composer (so tests can import the model without triggering composer logic; clean dependency boundary). Public exports via `app/composers/section_02a/__init__.py`.

**D3. Composer signature:**
```python
def compose(
    corpus_dir: Path,
    *,
    llm: BaseChatModel,
    cache: ComposerCache | None = None,
) -> Directive:
    """LLM-driven §02A directive composition; returns validated Directive model."""
```
- `corpus_dir`: pathlib.Path; the directory containing primary content + supporting binaries.
- `llm`: LangChain `BaseChatModel` (consistent with rest of project's LangChain integration). Inject for test fixture-replay determinism.
- `cache`: optional in-memory cache; default constructed if None.
- Returns: validated `Directive` Pydantic model (raises `ValidationError` on invalid).

**D4. Directive Pydantic v2 model fields (frozen at this spec):**

```python
class DirectiveRole(StrEnum):
    PRIMARY = "primary"
    SUPPORTING = "supporting"
    IGNORED = "ignored"


class ExcludedReason(StrEnum):
    GIT_MARKER = "git-marker-file"
    MACOS_METADATA = "macos-metadata"
    WINDOWS_METADATA = "windows-metadata"
    LLM_CLASSIFIED_OUT_OF_SCOPE = "llm-classified-out-of-scope"


class DirectiveSource(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    src_id: str = Field(..., min_length=1)  # e.g., "src-001"
    locator: str = Field(..., min_length=1)  # filename relative to corpus_dir
    provider: str = Field(default="local_file")  # currently always local_file; extensible
    role: DirectiveRole
    description: str | None = Field(default=None)
    expected_min_words: int | None = Field(default=None, ge=0)
    excluded_reason: ExcludedReason | None = Field(default=None)

    @field_validator("role", mode="before")
    @classmethod
    def _reject_unknown_role(cls, value): ...  # triple-layer red-rejection per 7c.0a TripwireLedgerEntry pattern

    @model_validator(mode="after")
    def _enforce_role_field_invariants(self) -> "DirectiveSource":
        # role=ignored REQUIRES excluded_reason populated
        # role in {primary, supporting} + ext in {.docx, .md} REQUIRES expected_min_words populated
        # role=ignored FORBIDS expected_min_words populated
        # binary file extensions (.png, .jpg, .jpeg, .gif, .bmp, .pdf, .pptx, .docx-thumbnails)
        #   when role=supporting MUST NOT have expected_min_words populated (Trial-2 finding #2's
        #   exact bug: PNG/JPG/PPTX/PDF binaries assigned expected_min_words: 200)
        ...


class Directive(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    run_id: UUID  # UUID4 per FR-7c-51 schema_version + uuid4 validation
    corpus_dir: str  # POSIX path-string; pathlib.Path serialization
    sources: list[DirectiveSource] = Field(..., min_length=1)
    composed_at: datetime  # tz-aware enforced via field_validator
    schema_version: int = Field(default=1)  # FR-7c-51 bump-on-change

    @field_validator("composed_at")
    @classmethod
    def _require_tz_aware(cls, value: datetime) -> datetime: ...  # enforce_tz_aware helper from 7c.0a pattern
```

**D5. Excluded-reason canonical pattern matching:**
- `.gitkeep` → `ExcludedReason.GIT_MARKER`
- `.DS_Store` → `ExcludedReason.MACOS_METADATA`
- `Thumbs.db` → `ExcludedReason.WINDOWS_METADATA`
- LLM-classified-as-out-of-scope (e.g., legacy README files irrelevant to lesson) → `ExcludedReason.LLM_CLASSIFIED_OUT_OF_SCOPE`

Pattern matching logic in composer is rule-based for the first 3 (no LLM call needed for `.gitkeep` etc.); LLM call only for ambiguous files. This is an OPTIMIZATION over per-file LLM classification — saves cache misses on known-ignorable patterns.

**D6. Per-file role classification prompt:** Jinja2 template at `docs/conversational-gates/section-02a-composer.j2` (per 7a precedent; consistent with `g1.j2`/`g2c.j2`/etc.). Template inputs:
- `filename` (str)
- `file_size_bytes` (int)
- `file_extension` (str; e.g., `.docx`)
- `binary_sample_hex` (str; first 64 bytes hex-encoded for binary classification)
- `corpus_summary` (str; sibling-files context for relative ranking)

Template output: structured JSON with `{role: str, expected_min_words: int | null, description: str, rationale: str}`. The composer parses this output + validates via `DirectiveSource` model.

**D7. Cache mechanism:**
- `ComposerCache` is a Pydantic-v2 model holding `dict[str, str]` (cache_key → serialized LLM response).
- Cache_key derivation: `SHA256(normalized_prompt)` where `normalized_prompt` = template output with `operator_id`, timestamps (`{{generated_at}}`), and `run_id` STRIPPED via regex replacement before hashing.
- Per NFR-7c-P2: ≥90% cache-hit median[2:] across N=10 runs.
- Cache is in-memory ONLY at this story; persistent cache layer is deferred to a future story (file as deferred-inventory follow-on if operator wants persistence post-7c.21).

**D8. TW-7c-2 firing trigger:** the regression test `test_composer_trial_2_finding_2_regression.py` is THE FIRING TRIGGER. The composer body itself does NOT detect TW-7c-2 — the test does.
- Test asserts: composer runs against `state/config/runs/db276994-edf4-47a2-83bc-771cc214c3c1/` corpus → result has `.gitkeep` excluded with `excluded_reason=GIT_MARKER` (NOT `role: primary`); `APC C1-M1 Tejal 2026-03-29.docx` has `role: primary`; PNG/JPG/PPTX/PDF binaries have `expected_min_words=None` (NOT `expected_min_words: 200`).
- If test FAILS, TW-7c-2 fires high severity → STOP → re-scope §02A → dual-nature claim invalidated. The dispatch fix path: surface to operator; do NOT proceed.

**D9. C5 forbidden_modules canonical list (populate `pyproject.toml::[tool.importlinter]` C5 target):**
```
forbidden_modules = [
    "app.composers._fallback",
    "app.composers.legacy",
    "app.marcus.orchestrator.directive_composer",
]
```
The third entry is the LEGACY directive composer that produced Trial-2 finding #2's broken output. Forbidding `app.composers.section_02a.*` from importing the legacy composer is the structural Trial-2-finding-#2 retirement. C5 KEPT count UNCHANGED at lint-imports level (already KEPT against empty target post-7c.0a; just populating).

**D10. Live-LLM test marker (NFR-7c-S6):** Tests that invoke real OpenAI API are marked `@pytest.mark.llm_live`; auto-skip if `OPENAI_API_KEY` is unset or matches placeholder pattern. Default focused-test run skips them; full broad regression can include them via `--llm-live` flag if operator opts in.

**D11. Test fixture for Trial-2 forensic regression:** the canonical Trial-2 fixture lives at `state/config/runs/db276994-edf4-47a2-83bc-771cc214c3c1/` (gitignored but operator-pinned per NFR-7c-OD6). Decision: regression test reads from THIS path AT-RUNTIME (skips with documented reason if fixture absent). DO NOT mirror the fixture into `tests/composers/fixtures/trial-2/` (would duplicate evidence; spec's mention of that path was speculative). Surface as `decision_needed` if Codex prefers the mirror approach for CI portability.

---

## T1 Readiness Block

**Required readings (cite by reference; do NOT re-derive at T1):**
- `_bmad-output/implementation-artifacts/trial-2-postmortem-2026-05-04.md` — Trial-2 finding #2 forensic detail (run `db276994-edf4-47a2-83bc-771cc214c3c1`; `.gitkeep` promoted to primary; `.docx` demoted to supporting; binaries assigned `expected_min_words: 200`).
- `_bmad-output/planning-artifacts/deferred-inventory.md` — `trial-2-finding-2-directive-composer-corpus-scan-fallback` entry; closed-by-7c.3a verdict at this story's close.
- `state/config/runs/db276994-edf4-47a2-83bc-771cc214c3c1/directive.yaml` — the broken Trial-2 directive output (regression test asserts NON-byte-identicality with this fixture).
- `app/marcus/orchestrator/directive_composer.py` — LEGACY composer that produced Trial-2 finding #2's broken output. READ ONLY at T1 to understand the file-walk pattern + the bug; the legacy composer is FORBIDDEN to import per D9 C5 contract.
- `docs/dev-guide/adr/0001-parity-contract-dsl.md` — informational; the §02A composer surface will register a parity contract via 7c.3b's canonical HIL pattern (NOT this story; this story authors only the composer body).
- `app/models/tripwire_ledger.py` — TripwireLedgerEntry pattern reference for Pydantic-v2 triple-layer red-rejection on closed-enum role.
- `docs/dev-guide/pydantic-v2-schema-checklist.md` — 14 schema idioms; Directive + DirectiveSource MUST conform.
- `docs/dev-guide/dev-agent-anti-patterns.md` — A11 Windows-portability + A-test-1 mocking-the-SUT.
- `docs/dev-guide/story-cycle-efficiency.md` — K-discipline 1.5×.
- `_bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md` — FR-7c-1/2/5/53 + NFR-7c-P1/P2/S1/S6 source spec.
- `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md` (Story 7c.3a section starting at line 480).
- `_bmad-output/planning-artifacts/slab-7c-velocity-amendments-2026-05-04.md` — R-tier + T11-tier conventions; AMEND-V5 cross-agent pre-flight rationale.

**Predecessor state (verified at dispatch time):**
- 7c.0a `done` (commit `f926867`) — TripwireLedgerEntry + ADR + import-linter contracts present.
- 7c.0b `done` (commit `9114337`) — DSL primitives + reference surface + `app/parity/contracts/__init__.py` importable.
- 7c.0c `done` — pytest-xdist + R2 smoke-suite manifest available; the §02A composer's broad regression at T9 benefits from xdist.
- 7c.1 `done` recommended (8-file refactor of transport-parity tests onto DSL); not strictly required but operationally Codex single-thread serializes 7c.3a behind 7c.1.
- Class-conformance: 11 conforming activation contracts.
- lint-imports: 12 KEPT / 0 broken pre-7c.3a; C5 target population in this story keeps count at 12 (no new contract; just target-list population).
- Refresh broad-regression baseline at current HEAD; record total pass/fail/skip counts.

**Live substrate (verified at T1):**
- `app/composers/` directory MAY or MAY NOT exist at T1. If absent, Codex creates `app/composers/__init__.py` + `app/composers/section_02a/` subpackage.
- `app/marcus/orchestrator/directive_composer.py` exists (LEGACY; ~9 KB; READ ONLY).
- Trial-2 forensic fixture at `state/config/runs/db276994-edf4-47a2-83bc-771cc214c3c1/directive.yaml` exists (verified at spec-authoring 2026-05-04). If absent at T1, surface as `decision_needed` (regression test SHALL `pytest.skip` with explicit reason; document operator-recovery path).
- LangChain `BaseChatModel` import path: verify `from langchain_core.language_models import BaseChatModel` resolves cleanly in `.venv`. If absent, surface (LangChain-core SHOULD be installed already given Slab 7a delivered LangGraph integration).
- OpenAI client setup: `OPENAI_API_KEY` env var; live-LLM tests skip if unset.

**Gate-mode rationale (from governance JSON):**
> Slab 7c Wave 1 (highest-priority story within Slab 7c per epic prose; dual-nature feature + Trial-2 finding #2 retirement). Section 02A LLM-driven directive composer body: replaces corpus-scan fallback that produced byte-identical broken directives across 5 successive Trial-2 runs (FR-7c-1 + FR-7c-2 + FR-7c-5 + FR-7c-53 C5 target-list population). Owns TW-7c-2 firing. Cross-agent code-review MANDATORY per Murat M6.

**T1 conclusion:** No unanticipated architectural disagreement. Contract decisions (D1-D11) locked at spec-author per AMEND-V5 pre-flight. Implementation proceeds: §02A composer body + Pydantic-v2 model + Jinja2 prompt template + cache + 6 tests + C5 target population + A11 augmentation. **Hard checkpoints at T1:**
- (a) 7c.0a + 7c.0b + 7c.0c `done`; 7c.1 `done` recommended.
- (b) Trial-2 forensic fixture exists OR documented skip path.
- (c) LangChain `BaseChatModel` importable.
- (d) `app/composers/` package does not exist OR can be safely created.
- (e) Refresh broad-regression baseline.
- (f) Verify D5 excluded-reason pattern matching covers all 4 known cases (.gitkeep, .DS_Store, Thumbs.db, llm-classified) — surface if additional canonical patterns surface during implementation.

---

## Story

As Marcus (and the operator running Trial-3 against a real corpus),
I want the §02A directive composer to compose a directive YAML via LLM reasoning that correctly classifies primary `.docx` lesson content as `role: primary`, ignores `.gitkeep` / `.DS_Store` / `Thumbs.db` with explicit `excluded_reason`, and does NOT assign `expected_min_words` to PNG/JPG/PPTX/PDF binaries (vs Trial-2 finding #2's broken corpus-scan fallback that promoted `.gitkeep` to primary, demoted the actual `.docx` to supporting, and assigned `expected_min_words: 200` to all binaries),
so that Trial-3 G0 ratification surface displays a real LLM-driven directive that the operator can `[a]pprove` / `[e]dit` / `[r]eject` against semantically-correct content classification — closing Trial-2 finding #2's deferred-inventory entry STRUCTURALLY (not via PYTHONIOENCODING-style env workaround; not via legacy fallback; via proper LLM-driven composition).

---

## Acceptance Criteria

### AC-7c.3a-A — `Directive` + `DirectiveSource` Pydantic-v2 model lands at `app/composers/section_02a/directive_model.py` (FR-7c-1 schema portion; D2 + D4)

**Given** the locked contract decision D4 (frozen field set + Literal closed-enum on role + conditional `expected_min_words` / `excluded_reason` invariants)
**When** the dev-agent authors `app/composers/section_02a/directive_model.py`
**Then** the module exposes:
1. `DirectiveRole(StrEnum)` closed enum: `PRIMARY` / `SUPPORTING` / `IGNORED`.
2. `ExcludedReason(StrEnum)` closed enum: `GIT_MARKER` / `MACOS_METADATA` / `WINDOWS_METADATA` / `LLM_CLASSIFIED_OUT_OF_SCOPE`.
3. `DirectiveSource` Pydantic-v2 model conforming to D4 spec. `validate_assignment=True`, `extra="forbid"`. Field validators: triple-layer red-rejection on `role` (Enum + Literal-coercion + before-validator using TypeAdapter, mirroring TripwireLedgerEntry pattern from 7c.0a). `model_validator(mode="after")` enforces conditional invariants (D4 bullet 3-5):
   - `role == IGNORED` REQUIRES `excluded_reason` populated (raises `ValidationError` if missing).
   - `role in {PRIMARY, SUPPORTING}` AND ext in {`.docx`, `.md`} REQUIRES `expected_min_words` populated (raises if missing).
   - `role == IGNORED` FORBIDS `expected_min_words` populated.
   - **Trial-2 finding #2 binary-file invariant (D4 bullet 5):** `role == SUPPORTING` AND ext in `{.png, .jpg, .jpeg, .gif, .bmp, .pdf, .pptx}` FORBIDS `expected_min_words` populated. Raises explicit error referencing Trial-2 finding #2 in the failure message ("binary file extensions cannot have expected_min_words; Trial-2 finding #2 anti-pattern").
4. `Directive` Pydantic-v2 model conforming to D4 spec. `run_id: UUID` (UUID4 enforced via `field_validator`), `composed_at` tz-aware enforced, `schema_version: int = 1` (FR-7c-51 bump-on-change), `sources: list[DirectiveSource]` with `min_length=1`.
5. `app/composers/section_02a/__init__.py` exports `Directive`, `DirectiveSource`, `DirectiveRole`, `ExcludedReason`, and the `compose` function (after AC-B).

**Test pin:** `tests/composers/section_02a/test_composer_directive_model_shape.py` — covers (a) DirectiveRole closed-enum red-rejection (3 valid + 1 invalid); (b) ExcludedReason closed-enum red-rejection; (c) DirectiveSource validate_assignment + extra=forbid + role-conditional invariants (4 cases per D4 bullet 3-5); (d) **Trial-2 finding #2 binary-file invariant** explicit test: `role=SUPPORTING + ext=.png + expected_min_words=200` raises with anti-pattern message; (e) Directive top-level model validates UUID4 + tz-aware composed_at + schema_version default + sources min_length=1; (f) JSON Schema `additionalProperties: false` asserted; (g) round-trip via `model_dump(mode="json")` → `model_validate` for at least 3 sample directives.

> **Notes for 7c.3a-A.** This AC is **dev-agent-executable** (Pydantic v2 + pytest). Codex MUST conform to all 14 idioms in `pydantic-v2-schema-checklist.md`. The triple-layer red-rejection on `role` mirrors 7c.0a's TripwireLedgerEntry pattern (Enum + Literal + before-validator with TypeAdapter).

### AC-7c.3a-B — `compose(corpus_dir, *, llm) -> Directive` body lands at `app/composers/section_02a/composer.py` (FR-7c-1 / D1 + D3 + D5 + D6)

**Given** the locked D1 module path + D3 signature + D5 excluded-reason pattern matching + D6 Jinja2 prompt template
**When** the dev-agent authors `app/composers/section_02a/composer.py`
**Then** the module exposes:
1. `compose(corpus_dir: Path, *, llm: BaseChatModel, cache: ComposerCache | None = None) -> Directive` — the canonical entry-point.
2. Composer flow:
   - Walk `corpus_dir` to enumerate files (reuse pattern from legacy `app/marcus/orchestrator/directive_composer.py` file-walk; do NOT import the legacy module per D9 C5).
   - For each file, apply D5 rule-based excluded-reason matching FIRST (before LLM): `.gitkeep` → `IGNORED + GIT_MARKER`; `.DS_Store` → `IGNORED + MACOS_METADATA`; `Thumbs.db` → `IGNORED + WINDOWS_METADATA`. These files SKIP the LLM call (cache-saving optimization).
   - For non-excluded files, build per-file LLM prompt via Jinja2 template at `docs/conversational-gates/section-02a-composer.j2` (D6 inputs: filename + size + ext + binary_sample_hex + corpus_summary).
   - Cache lookup: SHA256(normalized_prompt) cache_key → cache hit returns recorded LLM response; cache miss invokes `llm.invoke(prompt)`.
   - Parse LLM response (structured JSON per D6) → construct `DirectiveSource`.
   - Aggregate into `Directive(run_id=..., corpus_dir=..., sources=[...], composed_at=..., schema_version=1)`.
   - Validate (Pydantic invokes validators; D4 invariants enforced; raises on Trial-2 anti-pattern attempts).
   - Return.
3. Helper modules: `app/composers/section_02a/_prompt.py` (Jinja2 loader + cache-key normalization regex) + `app/composers/section_02a/_cache.py` (`ComposerCache` Pydantic v2 wrapper around dict[str, str]).

**Test pin:** `tests/composers/section_02a/test_composer_classification.py` — covers (a) compose against synthetic corpus via fixture-replay LLM (no live API call); (b) primary `.docx` correctly classified `role=PRIMARY`; (c) `.gitkeep` excluded with `excluded_reason=GIT_MARKER` (rule-based, no LLM call); (d) `.DS_Store` and `Thumbs.db` similarly rule-based excluded; (e) PNG/JPG binaries classified `role=SUPPORTING + expected_min_words=None` (binary-file invariant honored); (f) `compose` raises `ValidationError` if LLM returns malformed classification (e.g., role=primary + ext=.docx + expected_min_words=None — missing required field per D4).

> **Notes for 7c.3a-B.** This AC is **dev-agent-executable** (no live LLM in focused tests; fixture-replay via stub `BaseChatModel`). The `BaseChatModel` stub returns recorded JSON responses. Live-LLM integration test marked `@pytest.mark.llm_live` per D10.

### AC-7c.3a-C — Trial-2 forensic-fixture regression test owns TW-7c-2 firing (FR-7c-2 / D8 / D11)

**Given** the Trial-2 forensic fixture at `state/config/runs/db276994-edf4-47a2-83bc-771cc214c3c1/directive.yaml` (the BROKEN corpus-scan output) + a fixture-replay LLM stub that returns CORRECT classifications for the same corpus content
**When** the dev-agent runs `tests/composers/section_02a/test_composer_trial_2_finding_2_regression.py`
**Then** the test:
1. Loads the Trial-2 broken `directive.yaml` (skip with explicit reason if fixture absent at runtime).
2. Reconstructs the corpus content list from the broken directive's `sources` field (filenames only).
3. Invokes `compose(corpus_dir, llm=fixture_replay_llm)` against the same filenames.
4. Asserts the COMPOSED directive is NON-byte-identical with the Trial-2 broken directive (`composed_yaml != trial_2_yaml`).
5. Asserts the COMPOSED directive's `sources` list:
   - Includes `.gitkeep` with `role=IGNORED + excluded_reason=GIT_MARKER` (NOT `role=primary` as Trial-2 had).
   - Includes `APC C1-M1 Tejal 2026-03-29.docx` with `role=PRIMARY` (NOT `role=supporting` as Trial-2 had).
   - For each `*.png`, `*.jpg`, `*.pdf`, `*.pptx` entry: `expected_min_words` is `None` (NOT `200` as Trial-2 had).

**And** if AC-7c.3a-C test FAILS (regression detected), TW-7c-2 fires HIGH severity per D8: STOP; do NOT proceed to T11; surface to operator; re-scope §02A; dual-nature claim invalidated. Document the firing in the spec's Completion Notes per NFR-7c-OD2 TripwireLedgerEntry shape if firing occurs (would happen during Codex T9, not at T11).

**Test pin:** the test itself IS the firing trigger (per D8). NO downstream structural test wraps this; it's primary AC.

> **Notes for 7c.3a-C.** This AC is **dev-agent-executable**. The fixture-replay LLM stub is a `BaseChatModel` subclass returning hardcoded classifications matching the corpus content. The test's invariant is "composed directive ≠ Trial-2 broken directive" + per-source-field assertions. If the fixture-replay LLM stub somehow produces the SAME broken classifications, the test fails — that's TW-7c-2 firing (would indicate LLM prompting is wrong, not the composer body).

### AC-7c.3a-D — Cache-key SHA256 normalization stability (NFR-7c-P2 / D7)

**Given** the locked D7 cache-key derivation: `cache_key = SHA256(normalized_prompt)` where `normalized_prompt` strips `operator_id` + `{{generated_at}}` timestamp + `run_id` via regex
**When** the dev-agent runs `tests/composers/section_02a/test_composer_cache_key_normalization.py`
**Then** the test asserts:
1. Two prompts identical EXCEPT for `operator_id` + timestamps + `run_id` produce the SAME cache_key (stripping is idempotent).
2. Two prompts with DIFFERENT corpus content (different filenames) produce DIFFERENT cache_keys.
3. Cache-hit on identical prompt returns the recorded LLM response WITHOUT invoking the LLM (verify via stub LLM with `invoke_count` tracking).
4. Cache-miss on novel prompt invokes the LLM (verify `invoke_count == 1` after first call; `invoke_count == 1` after second call with same cache_key).

**And** the cache-key normalization regex is module-level constant in `_prompt.py`; documented with rationale.

**Test pin:** the test IS the AC pin.

> **Notes for 7c.3a-D.** This AC is **dev-agent-executable**. NFR-7c-P2's ≥90% cache-hit median[2:] target is exercised at the live-LLM integration test (post-7c.3a; deferred to 7c.21 evidence accrual or filed as follow-on). This story's contribution is the cache-key normalization correctness.

### AC-7c.3a-E — UTF-8 round-trip on `directive.yaml` write (FR-7c-5 / NFR-7c-X1)

**Given** the §02A composer writes the validated `Directive` to `state/config/runs/<run-id>/directive.yaml`
**When** the dev-agent runs `tests/composers/section_02a/test_composer_utf8_write.py`
**Then** the test:
1. Composes a directive with macOS-screenshot Unicode content (U+202F NNBSP in a filename's locator field — mirroring 7c.2 regression scenario).
2. Writes the directive to `tmp_path / "directive.yaml"` using the composer's write helper.
3. Reads the written bytes via `Path.read_bytes()`; verifies UTF-8-explicit encoding (decode round-trip + presence of expected NNBSP byte sequence `\xe2\x80\xaf`).
4. `monkeypatch.delenv("PYTHONIOENCODING", raising=False)` — verify structural fix (post-7c.2) is doing the work, NOT the operator-env workaround.

**Test pin:** the test IS the AC pin. ALSO extend the 7c.2 AST-scan structural test (`tests/structural/test_directive_io_uses_utf8_explicit.py`) to include `app/composers/section_02a/composer.py` in `FILES_TO_SCAN` if it isn't already (verify at T1; surface if extension is needed).

> **Notes for 7c.3a-E.** This AC is **dev-agent-executable**. The composer's write helper SHALL use `Path.write_text(yaml.safe_dump(directive_dict), encoding="utf-8")` per A11 + 7c.2 conventions.

### AC-7c.3a-F — C5 import-linter contract populated; legacy composer forbidden (FR-7c-53 / D9)

**Given** the locked D9 C5 forbidden_modules list
**When** the dev-agent populates `pyproject.toml::[tool.importlinter]` C5 contract
**Then** C5 `forbidden_modules` is exactly:
```toml
forbidden_modules = [
    "app.composers._fallback",
    "app.composers.legacy",
    "app.marcus.orchestrator.directive_composer",
]
```
**And** `lint-imports` exits 0 with 12 KEPT (UNCHANGED contract count; just target population on existing C5).

**And** `app/composers/section_02a/composer.py` does NOT import any of the 3 forbidden modules. Verify via grep + lint-imports.

**Test pin:** `tests/structural/test_import_linter_c5_target_list_populated.py` — `tomllib` parse + assert C5 forbidden_modules matches expected set; subprocess `lint-imports` + assert KEPT count = 12.

> **Notes for 7c.3a-F.** This AC is **dev-agent-executable**. NOTE: importing `from app.marcus.orchestrator.directive_composer import _walk_corpus` (or analogous helper) WOULD VIOLATE C5. Codex MUST reuse the file-walk LOGIC (re-author it in `composer.py`) without importing the legacy module. This is the structural Trial-2 finding #2 retirement.

---

## Tasks / Subtasks

- [x] **T1 — Readiness checks**
  - [x] T1.1 Confirm 7c.0a + 7c.0b + 7c.0c all `done`; 7c.1 `done` recommended.
  - [x] T1.2 Verify Trial-2 forensic fixture exists; document skip path if absent.
  - [x] T1.3 Verify LangChain `BaseChatModel` importable.
  - [x] T1.4 Refresh broad-regression baseline.
  - [x] T1.5 Verify D5 excluded-reason patterns cover real-world cases against the Trial-2 corpus.
  - [x] T1.6 Run sandbox-AC validator on this spec; expect PASS.

- [x] **T2 — Author Pydantic-v2 directive model (AC: 7c.3a-A)**
  - [x] T2.1 `app/composers/section_02a/directive_model.py` with `DirectiveRole` + `ExcludedReason` + `DirectiveSource` + `Directive`.
  - [x] T2.2 Triple-layer red-rejection on role + 4 conditional invariants per D4.
  - [x] T2.3 Trial-2 finding #2 binary-file invariant explicit error message.
  - [x] T2.4 `__init__.py` public exports.

- [x] **T3 — Author composer body (AC: 7c.3a-B)**
  - [x] T3.1 `composer.py::compose` per D3 signature.
  - [x] T3.2 D5 rule-based excluded-reason pattern matching (3 cases pre-LLM).
  - [x] T3.3 Per-file LLM call via Jinja2 prompt template (D6).
  - [x] T3.4 Helper modules `_prompt.py` + `_cache.py` (D7 normalization regex + SHA256 derivation).
  - [x] T3.5 File-walk logic re-authored (do NOT import legacy `app/marcus/orchestrator/directive_composer.py`).

- [x] **T4 — Author Jinja2 prompt template (AC: 7c.3a-B / D6)**
  - [x] T4.1 `docs/conversational-gates/section-02a-composer.j2` with D6 inputs + structured-JSON output spec.
  - [x] T4.2 Document prompt design rationale in module docstring of `_prompt.py`.

- [x] **T5 — Author 6 tests (AC: 7c.3a-A through 7c.3a-F test pins)**
  - [x] T5.1 `test_composer_directive_model_shape.py` (model invariants + Trial-2 binary-file anti-pattern explicit test).
  - [x] T5.2 `test_composer_classification.py` (compose + fixture-replay LLM + 6 cases).
  - [x] T5.3 `test_composer_trial_2_finding_2_regression.py` (TW-7c-2 firing trigger).
  - [x] T5.4 `test_composer_cache_key_normalization.py` (SHA256 stability + cache-hit/miss).
  - [x] T5.5 `test_composer_utf8_write.py` (FR-7c-5 / U+202F regression on write).
  - [x] T5.6 `test_import_linter_c5_target_list_populated.py` (C5 + lint-imports KEPT 12).

- [x] **T6 — Populate C5 `forbidden_modules` (AC: 7c.3a-F)**
  - [x] T6.1 Edit `pyproject.toml::[tool.importlinter]` C5 contract per D9.
  - [x] T6.2 Verify lint-imports exits 0 + KEPT 12.
  - [x] T6.3 Verify composer.py does NOT import any of the 3 forbidden modules.

- [x] **T7 — Update 7c.2 AST scan (AC: 7c.3a-E follow-on)**
  - [x] T7.1 If `app/composers/section_02a/composer.py` is NOT in `tests/structural/test_directive_io_uses_utf8_explicit.py::FILES_TO_SCAN`, add it.

- [x] **T8 — Augment A11 anti-pattern catalog (informational; lower priority)**
  - [x] T8.1 Deferred optional `docs/dev-guide/specialist-anti-patterns.md` A11 augmentation to preserve K-target; no implementation dependency.

- [x] **T9 — Verification battery (R-tier R3; cross-agent T11 review)**
  - [x] T9.1 Focused tests: all 6 new test files PASS.
  - [x] T9.2 R3 broad regression `pytest -p no:randomly -q --tb=line` (parallel post-7c.0c) — combined parallel + serial total = T1.4 baseline (delta = 0).
  - [x] T9.3 lint-imports: 12 KEPT (UNCHANGED).
  - [x] T9.4 Class-conformance: 11 (UNCHANGED).
  - [x] T9.5 Sandbox-AC: PASS.
  - [x] T9.6 Ruff: clean on touched files.

- [x] **T10 — Codex self-review (NEW CYCLE T10)**
  - [x] T10.1 Codex authors `_codex-handoff/7c-3a.ready-for-review.md` summarizing: file list (~15 files: 4 NEW package modules + 6 NEW tests + Jinja2 template + pyproject.toml diff + structural test extension) + contract-decision-by-decision compliance table (D1-D11 each: PASS/FAIL/deviation) + TW-7c-2 firing status (PASS = no firing) + broad-regression delta + wall-clock report.

- [x] **T11 — Claude `bmad-code-review` (CROSS-AGENT MANDATORY; standard cross-agent tier)**
  - [x] T11.1 Claude (separate cold context) runs `bmad-code-review` against the diff. **Verifies contract-decision compliance** (D1-D11 each). NOT relitigation. Verdict at `_bmad-output/implementation-artifacts/7c-3a-code-review-2026-05-NN.md`. Commits + flips done.

---

## Dev Notes

**Why this story is the highest-priority Wave 1 story:** Trial-2 paused at G1 with directive content visibly broken (`.gitkeep` promoted to primary; `.docx` demoted; binaries assigned word counts). The dual-nature claim (Marcus orchestrational tail = LLM-driven semantic conversation, NOT corpus-scan automation) is invalidated until 7c.3a closes structurally. Every downstream Trial-3 step depends on a correct §02A directive.

**Why cross-agent MANDATORY at T11:** Murat M6 + the substrate-shape risk surface. The composer's classification logic affects every G0 ratification + every downstream specialist's input contract.

**Why contract decisions LOCKED at spec-author:** AMEND-V5 cross-agent pre-flight rule. T11 review verifies, doesn't negotiate. If Codex deviates from D1-D11 at implementation time, the deviation surfaces as `decision_needed` at T10 self-review (before T11) — operator decides whether to amend the contract or revert the deviation.

**File / module placement summary (post-D1):**
- `app/composers/section_02a/` package (NEW; subpackage of `app/composers/`).
- `docs/conversational-gates/section-02a-composer.j2` (NEW; consistent with 7a precedent).
- `pyproject.toml` C5 target population.
- `tests/composers/section_02a/` package (NEW; 5 test files).
- `tests/structural/test_import_linter_c5_target_list_populated.py` (NEW; sibling of 7c.0b's C4 test).
- 7c.2 AST scan extension (T7).

**Anti-patterns to avoid:**
- **A11 Windows-portability** — UTF-8 explicit on `directive.yaml` write.
- **A-test-1 Mocking the SUT** — fixture-replay LLM is a STUB BaseChatModel (legitimate test injection point per D3); NOT mocking the composer logic itself.
- **A-review-ceremony-1** — at T9.2 broad regression, report ACTUAL delta vs T1 baseline.
- **Importing legacy composer** — D9 C5 forbids this. Re-author file-walk logic in `composer.py`; do NOT `from app.marcus.orchestrator.directive_composer import ...`.
- **Per-file LLM cache misses on known-ignorable patterns** — D5 rule-based pre-LLM filtering is the optimization; don't accidentally route `.gitkeep` through the LLM.

**K-discipline:**
- K-target 1.5× ≈ ~3.75K LOC ceiling. Estimate: 4 package modules ~600-800 LOC + Jinja2 template ~50-150 LOC + 6 test files ~150-300 LOC each = ~900-1800 LOC + pyproject diff ~10 LOC + structural test ~100 LOC + Dev Notes documentation ~300 LOC = ~2.0-3.0K LOC. Comfortable headroom.
- Surface for K-renegotiation if T1.5 surfaces additional excluded-reason canonical patterns or if D5 rule-based matching needs to extend.

**Testing standards:**
- Pytest with `-p no:randomly` (NFR-7c-R2 preservation).
- Live-LLM tests marked `@pytest.mark.llm_live`; skip in focused-test runs.
- Fixture-replay tests use stub `BaseChatModel` returning recorded JSON.

### Project Structure Notes

- **Alignment with unified project structure:** all new file paths conform to existing convention. `app/composers/` may be a NEW top-level subpackage; verify at T1 whether parent `app/composers/__init__.py` exists or needs creation. Sibling pattern: `app/marcus/`, `app/specialists/`, `app/audit/` (post-7c.0b).
- **Detected variances:** none anticipated.

### References

- [Source: docs/dev-guide/migration-story-governance.json#stories.7c-3a]
- [Source: docs/dev-guide/pydantic-v2-schema-checklist.md] (14 idioms; Directive + DirectiveSource conform)
- [Source: docs/dev-guide/dev-agent-anti-patterns.md] (A11 Windows-portability; A-test-1 mocking-SUT)
- [Source: docs/dev-guide/story-cycle-efficiency.md] (K-discipline 1.5×)
- [Source: docs/dev-guide/adr/0001-parity-contract-dsl.md] (informational; §02A surface registers parity contract via 7c.3b — NOT this story)
- [Source: app/models/tripwire_ledger.py] (triple-layer red-rejection pattern reference)
- [Source: app/marcus/orchestrator/directive_composer.py] (LEGACY; READ ONLY at T1; FORBIDDEN to import per D9 C5)
- [Source: state/config/runs/db276994-edf4-47a2-83bc-771cc214c3c1/directive.yaml] (Trial-2 broken fixture; regression target)
- [Source: _bmad-output/implementation-artifacts/trial-2-postmortem-2026-05-04.md] (Trial-2 finding #2 forensic detail)
- [Source: _bmad-output/planning-artifacts/deferred-inventory.md#trial-2-finding-2-directive-composer-corpus-scan-fallback] (closed-by-7c.3a entry)
- [Source: _bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md#FR-7c-1 + #FR-7c-2 + #FR-7c-5 + #FR-7c-53 + #NFR-7c-P1 + #NFR-7c-P2 + #NFR-7c-S6] (FR/NFR sources)
- [Source: _bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md#Story-7c.3a] (Story 7c.3a section starting at line 480)
- [Source: _bmad-output/planning-artifacts/slab-7c-velocity-amendments-2026-05-04.md#AMEND-V5] (cross-agent pre-flight contract negotiation rationale)

---

## Dev Agent Record

### Agent Model Used

Codex Sonnet 4.5 or later (NEW CYCLE T1-T9 + T10 self-review per `feedback_new_cycle_codex_dev_handoff.md`).

### Debug Log References

- 2026-05-05: T1 prerequisites clear: 7c.0a/0b/0c/1 done in local sprint state, Trial-2 fixture present, LangChain `BaseChatModel` importable, sandbox-AC PASS.
- 2026-05-05: T1 broad-regression baseline refreshed immediately before 7c.3a edits: 39 failed, 4063 passed, 27 skipped, 2 xfailed, 11 warnings.
- 2026-05-05: Authored `app/composers/section_02a/` package, Pydantic-v2 directive models, cache, prompt rendering, composer body, and UTF-8 YAML writer.
- 2026-05-05: Populated C5 `forbidden_modules` and updated structural pins that previously expected C5 to remain empty.
- 2026-05-05: Focused/impact test run: 21 passed.
- 2026-05-05: lint-imports: 12 kept, 0 broken.
- 2026-05-05: Class-conformance validator: PASS, 11 activation contract files conform.
- 2026-05-05: Sandbox-AC validator: PASS.
- 2026-05-05: Ruff on touched app/tests/structural files: clean.
- 2026-05-05: R3 broad regression final run: 39 failed, 4077 passed, 27 skipped, 2 xfailed, 11 warnings. Delta vs T1 baseline: +14 passes, same 39 known checkout-level failures, no new 7c.3a failures.

### Completion Notes List

- D1 PASS: composer module path is `app/composers/section_02a/composer.py`.
- D2 PASS: Pydantic-v2 directive models live in `app/composers/section_02a/directive_model.py` and are exported via package `__init__.py`.
- D3 PASS: `compose(corpus_dir: Path, *, llm: BaseChatModel, cache: ComposerCache | None = None) -> Directive` implemented.
- D4 PASS: DirectiveRole, ExcludedReason, DirectiveSource, and Directive conform to Pydantic-v2 idioms with triple-layer role red-rejection, timezone-aware datetime, UUID4 validation, assignment validation, and extra-forbid.
- D5 PASS: `.gitkeep`, `.DS_Store`, and `Thumbs.db` are rule-excluded before LLM invocation.
- D6 PASS: Jinja2 prompt template added at `docs/conversational-gates/section-02a-composer.j2`.
- D7 PASS: `ComposerCache` and SHA256 normalized-prompt cache keys implemented; focused cache tests prove hit/miss behavior. Fixture cache-hit metric: second identical compose call reuses cache with no second LLM invocation.
- D8 PASS: TW-7c-2 firing trigger test passes; no TW-7c-2 fire.
- D9 PASS: C5 forbidden modules populated with the locked three-module list and lint-imports remains 12 KEPT.
- D10 PASS: no live LLM calls are present in default tests; fixture-replay `BaseChatModel` is used.
- D11 PASS: Trial-2 forensic regression reads the canonical fixture path at runtime and has explicit skip behavior if absent.
- Optional T8 A11 anti-pattern catalog augmentation was not performed; documented as deferred to preserve K-target.
- Deferred-inventory entry `trial-2-finding-2-directive-composer-corpus-scan-fallback` still needs final close bookkeeping at T11/story-close.

### File List

- `app/composers/__init__.py` (NEW)
- `app/composers/section_02a/__init__.py` (NEW)
- `app/composers/section_02a/_cache.py` (NEW)
- `app/composers/section_02a/_prompt.py` (NEW)
- `app/composers/section_02a/composer.py` (NEW)
- `app/composers/section_02a/directive_model.py` (NEW)
- `docs/conversational-gates/section-02a-composer.j2` (NEW)
- `tests/composers/__init__.py` (NEW)
- `tests/composers/section_02a/__init__.py` (NEW)
- `tests/composers/section_02a/_helpers.py` (NEW)
- `tests/composers/section_02a/test_composer_cache_key_normalization.py` (NEW)
- `tests/composers/section_02a/test_composer_classification.py` (NEW)
- `tests/composers/section_02a/test_composer_directive_model_shape.py` (NEW)
- `tests/composers/section_02a/test_composer_trial_2_finding_2_regression.py` (NEW)
- `tests/composers/section_02a/test_composer_utf8_write.py` (NEW)
- `tests/structural/test_import_linter_c5_target_list_populated.py` (NEW)
- `pyproject.toml` (MODIFIED)
- `tests/structural/test_directive_io_uses_utf8_explicit.py` (MODIFIED)
- `tests/structural/test_import_linter_contracts_c4_c5_c6_present.py` (MODIFIED)
- `tests/structural/test_import_linter_c4_target_list_populated.py` (MODIFIED)
