# Migration Story 34-3: §02A `src_id` → `ref_id` Rename + J-A1(a)/(b) cli_adapter Completion (Winston A2 binding)

**Status:** ready-for-dev *(spec authored 2026-05-22 with locked contract decisions D1-D7; predecessor Stories 34-1 + 34-2 expected `done` at dispatch.)*
**Sprint key:** `migration-34-3-section-02a-src-id-rename-and-cli-adapter-completion`
**Epic:** Epic 34 — §02A Downstream-Consumer Schema Coherence
**Pts:** 5
**Gate:** **dual-gate** (§02A substrate edit across multiple files + cli_adapter behavior change)
**K-target:** ~1.5× (5 pts; bounded surface = 1 Pydantic model field rename + 4 §02A composer files + cli_adapter J-A1(a)/(b) logic + 8 test files migrated + 1 sidecar JSON test)
**R-tier:** **R2**
**T11-tier:** standard
**Files touched:**

**Modified (~13 files):**
- `app/composers/section_02a/directive_model.py` (D1: rename `src_id` → `ref_id` in DirectiveSource)
- `app/composers/section_02a/composer.py` (D2: consume renamed field; accept `run_id` parameter per J-A1(a))
- `app/composers/section_02a/_prompt.py` (D2: LLM prompt template + cache-key normalization referencing field name)
- `app/composers/section_02a/_cache.py` (D2: cache-key regex if it includes field name)
- `app/composers/section_02a/cli_adapter.py` (D3 + D4: thread `effective_trial_id`; persist ModelResolutionEntry)
- `app/composers/section_02a/__init__.py` (re-export surface; preserve API per W-SCP-A1)
- `docs/conversational-gates/section-02a-composer.j2` (D2: if it references `src_id` field name — verify at T1)
- `tests/composers/section_02a/_helpers.py` (test surface migration)
- `tests/composers/section_02a/test_composer_cache_key_normalization.py`
- `tests/composers/section_02a/test_composer_classification.py`
- `tests/composers/section_02a/test_composer_directive_model_shape.py`
- `tests/composers/section_02a/test_composer_trial_2_finding_2_regression.py`
- `tests/composers/section_02a/test_composer_utf8_write.py`
- `tests/gates/section_02a/_helpers.py`
- `tests/gates/section_02a/test_g0_poll_surface_field_level_edit.py`
- `tests/marcus_cli/test_compose_section_02a_directive_adapter.py` (M-A1 wiring contract; ref_id update + new J-A1 assertions)

**New:**
- `tests/marcus_cli/test_cli_adapter_run_id_thread_through.py` (J-A1(a) regression)
- `tests/marcus_cli/test_cli_adapter_model_resolution_trail.py` (J-A1(b) regression + sidecar JSON path)
- Translator-shrinkage update at `app/composers/section_02a/_wrangler_translator.py`: remove `src-id-to-ref-id` from `TRANSLATOR_ACTIVE_MAPPINGS` (`TRANSLATOR_ACTIVE_MAPPINGS` reaches empty frozenset at this story's close)

**Lookahead tier:** **2** (multi-file substrate; field rename + behavior change in cli_adapter).
**Wave:** 1 — slot 3 (lands AFTER Stories 34-1 + 34-2 per Winston A3).

**FR coverage:** FR-E34-1 (`src_id` → `ref_id`), FR-E34-8 (J-A1(a) run_id thread-through), FR-E34-9 (J-A1(b) trail append).
**NFR coverage:** NFR-E34-1 (Story-34-1 ratchet), NFR-E34-2 (Pydantic-v2 closed-enum), NFR-E34-3 (Pydantic hygiene), NFR-E34-6 (UUID4-tz-aware preserved), NFR-E34-8 (TW-7c-4), NFR-E34-11..13.

**Contract Decisions (LOCKED 2026-05-22):**

**D1. §02A Pydantic model field rename (Winston A2 BINDING):** In `app/composers/section_02a/directive_model.py`:
- Rename `DirectiveSource.src_id: str` → `DirectiveSource.ref_id: str`
- All field constraints preserved (`min_length=1`)
- Pydantic-v2 hygiene preserved (`extra="forbid"`, `validate_assignment=True`)
- `__all__` exports unchanged (field name is on the model, not at module level)

**D2. Cascading rename across §02A package (SUBSTRATE-AUDIT-CORRECTED 2026-05-22):**

**Verified via per-file grep at substrate-audit time** (2026-05-22):
- `docs/conversational-gates/section-02a-composer.j2` — **0 matches for `src_id` or `ref_id`**. j2 template does NOT reference the field name. **NO-OP for Story 34-3.** Remove from scope.
- `app/composers/section_02a/{composer.py, _prompt.py, _cache.py, cli_adapter.py, __init__.py}` — Codex T1 MUST grep each file individually. Expected hits per source-of-truth (`directive_model.py:58` is the only declaration; consumers reference via `DirectiveSource.src_id` attribute access). Likely small per-file count (≤5 hits each).

Codex T1 SHALL run `grep -rn "src_id" app/composers/section_02a/` to enumerate EXACT hits before authoring. If a file shows 0 hits, REMOVE from the modify list. Do NOT touch files with no field references.

**D3. J-A1(a) — operator-supplied run_id wins (FR-E34-8 BINDING — SUBSTRATE-AUDIT-CORRECTED 2026-05-22):**

**Current substrate** (verified via Read of `app/composers/section_02a/cli_adapter.py` and `app/marcus/cli/trial.py:241-244`):

```python
# cli_adapter.py CURRENT signature (lines 29-34):
def compose_and_write(
    corpus_dir: Path,         # positional
    run_dir: Path,            # positional
    *,
    llm: BaseChatModel | None = None,  # keyword-only, optional
) -> tuple[Path, str]:
```

```python
# trial.py CURRENT call site (lines 241-244):
directive_path, directive_digest = compose_and_write(
    corpus_dir=input_path,
    run_dir=run_dir,
)
```

`effective_trial_id` is in scope at trial.py line 220 (`effective_trial_id = trial_id or uuid4()`).

**Story 34-3 changes (preserving the positional+kwarg structure):**

```python
# cli_adapter.py NEW signature — ADD `run_id` as keyword-only required:
def compose_and_write(
    corpus_dir: Path,
    run_dir: Path,
    *,
    run_id: UUID,                       # NEW keyword-only REQUIRED
    llm: BaseChatModel | None = None,   # existing kwarg unchanged
) -> tuple[Path, str]:
    """Bridge trial CLI's effective_trial_id to §02A composer's run_id."""
    if llm is None:
        from app.models.adapter import make_chat_model
        handle = make_chat_model("marcus")
        llm = handle.chat
        # ... J-A1(b) trail-write happens here per D4 (handle.entry usage)
    else:
        handle = None  # no audit-trail to write when caller injects llm (test path)

    directive = compose(
        corpus_dir,
        llm=llm,
        cache=ComposerCache(),
        run_id=run_id,                  # threaded through; NOT internally generated
    )
    directive_path = run_dir / "directive.yaml"
    write_directive_yaml(directive, directive_path)
    digest = hashlib.sha256(directive_path.read_bytes()).hexdigest()
    return directive_path, digest
```

```python
# composer.py — ADD `run_id: UUID` REQUIRED kwarg:
def compose(
    corpus_dir: Path,
    *,
    llm: BaseChatModel,
    cache: ComposerCache | None = None,
    run_id: UUID,                       # NEW required parameter
) -> Directive:
    """LLM-driven §02A directive composition; uses caller-supplied run_id."""
    # ... (existing body unchanged)
    return Directive(
        run_id=run_id,                  # threaded through
        corpus_dir=str(corpus_dir),
        sources=tuple(...),
        composed_at=datetime.now(tz=UTC),
    )
```

```python
# trial.py NEW call site (replaces lines 241-244):
directive_path, directive_digest = compose_and_write(
    corpus_dir=input_path,
    run_dir=run_dir,
    run_id=effective_trial_id,           # NEW threaded param
)
```

**TODO(post-trial-3-retro) block REMOVAL (BINDING):** cli_adapter.py:50-63 docstring contains a `Known seams (TODO(post-trial-3-retro)):` block documenting J-A1(a) + J-A1(b) deferral. Story 34-3 MUST EXCISE this entire docstring block in lockstep with the code fix. Replace with a single line: `Threads operator-supplied run_id (J-A1(a)) and writes model_resolution_trail sidecar (J-A1(b)).`

**D4. J-A1(b) — model_resolution_trail sidecar (FR-E34-9 BINDING — SUBSTRATE-AUDIT-CORRECTED 2026-05-22):**

`cli_adapter.compose_and_write` currently discards `ChatModelHandle.entry` (TODO block at lines 56-63 documents this). Story 34-3 persists it as a sidecar JSON in `run_dir`.

**Verified imports** (Read of `app/models/adapter.py:31-52`):
- `ModelResolutionEntry` is at `app.models.state.model_resolution_entry` (NOT `app.models.adapter` — adapter re-imports it).
- `ChatModelHandle = NamedTuple` with fields `(chat: ChatOpenAI, entry: ModelResolutionEntry)`.

```python
# cli_adapter.py — add imports:
import json
from datetime import UTC, datetime

# Inside compose_and_write, after `handle = make_chat_model("marcus")` (only the
# default branch where caller did NOT inject llm; if caller injected, skip the
# trail write since there's no handle.entry available):
if handle is not None:
    trail_sidecar_path = run_dir / "model_resolution_trail.json"
    trail_data = {
        "specialist_id": "marcus",
        "resolved": handle.entry.resolved,
        "level": handle.entry.level,
        "cache_prefix_hash": handle.entry.cache_prefix_hash,
        "captured_at": datetime.now(tz=UTC).isoformat(),
        # Codex T1: verify ModelResolutionEntry actual field shape via
        # `Read app/models/state/model_resolution_entry.py`; include any
        # additional fields needed for audit-trail reproducibility.
    }
    trail_sidecar_path.write_text(
        json.dumps(trail_data, indent=2, sort_keys=True),
        encoding="utf-8",
    )
```

The sidecar path is **deterministic** (`run_dir / "model_resolution_trail.json"`); downstream consumers OR Marcus run state can pick it up later.

**Codex T1 readiness:** verify `ModelResolutionEntry` actual field shape at `app/models/state/model_resolution_entry.py` before authoring. If the model has more fields than `{resolved, level, cache_prefix_hash}`, include all relevant ones in the sidecar JSON for NFR-X4 audit-trail completeness.

(This is the simpler-of-two-options per J-A1(b) entry; threading through `RunState.model_resolution_trail` is a deeper refactor that Story 34-3 does NOT undertake — surface as decision_needed if Codex believes the sidecar is wrong direction.)

**D5. §02A test surface migration (Amelia A-A1 BINDING — SUBSTRATE-AUDIT-CORRECTED 2026-05-22):**

**Verified per-file grep at substrate-audit time** (2026-05-22 via `Grep "src_id|ref_id" tests/composers/section_02a/` + `tests/gates/section_02a/`):

**Files with ACTUAL `src_id|ref_id` matches (4 files):**
- `tests/composers/section_02a/test_composer_directive_model_shape.py` — 2 matches
- `tests/composers/section_02a/test_composer_utf8_write.py` — 1 match
- `tests/gates/section_02a/_helpers.py` — 3 matches
- `tests/gates/section_02a/test_g0_poll_surface_field_level_edit.py` — 1 match

**Total: 7 matches across 4 files** (NOT 8 files as my prior spec said; Amelia's Round-1 list named the right SCOPE but I overstated the per-file count without verifying).

**Files allowlisted at C1 but with ZERO grep hits at audit time** (Codex T1 verify):
- `tests/composers/section_02a/_helpers.py` — 0 (may need touches if it imports `DirectiveSource` and uses attribute access via `.src_id`)
- `tests/composers/section_02a/__init__.py` — 0 (package marker)
- `tests/composers/section_02a/test_composer_cache_key_normalization.py` — 0
- `tests/composers/section_02a/test_composer_classification.py` — 0
- `tests/composers/section_02a/test_composer_trial_2_finding_2_regression.py` — 0

These files are PRE-ALLOWLISTED but Codex SHALL NOT modify them unless T1 grep surfaces actual `src_id` references (e.g., attribute access patterns my literal-string grep missed: `directive.sources[0].src_id` would be hits). Codex T1 SHALL run a wider grep: `grep -rn "src_id\|\.src_id\|.*src_id.*=" tests/composers/section_02a/ tests/gates/section_02a/` to catch attribute access. If wider grep surfaces more hits, expand the modify list. Otherwise, restrict to the 4 files above.

**T2 final-grep verification:** post-rename, `grep -rn "src_id" tests/composers/section_02a/ tests/gates/section_02a/` MUST return 0 matches. Any residual hit = halt + investigate.

**D6. M-A1 wiring-contract tests migration:**

`tests/marcus_cli/test_compose_section_02a_directive_adapter.py` (4 tests) reference `compose_directive` mock + return shape. Update to:
- Mock `compose` (not `compose_directive`) signature with new `run_id` parameter
- Assert cli_adapter threads `effective_trial_id` through to `compose(run_id=...)` per J-A1(a)
- Assert sidecar `model_resolution_trail.json` is written per J-A1(b)

**D7. Translator shrinkage (Story 34-1 ratchet preservation):**

After D1+D2 land, the translator's `src-id-to-ref-id` mapping is no longer needed. Story 34-3 removes it from `TRANSLATOR_ACTIVE_MAPPINGS`. At this story's close, `TRANSLATOR_ACTIVE_MAPPINGS = frozenset()` (empty). Story 34-5's sequence test verifies monotonic shrinkage; Story 34-7 deletes the translator file entirely.

---

## Task chain T1-T11

**T1 readiness check:** C1 + Stories 34-1 + 34-2 = `done`. Verify `TRANSLATOR_ACTIVE_MAPPINGS` currently contains 1 element (`src-id-to-ref-id`).

**T2 §02A package + j2 template rename:** D1 + D2 sweep across §02A package files + Jinja2 template.

**T3 cli_adapter J-A1(a) + (b):** D3 + D4 implementation.

**T4 trial.py call-site update:** thread `effective_trial_id` through `compose_and_write` call.

**T5 §02A test surface migration:** D5 sweep across 8 test-surface paths.

**T6 M-A1 wiring tests update + 2 new J-A1 tests:** D6 + new test files.

**T7 translator shrinkage:** D7.

**T8 ruff + lint-imports + focused suite.**

**T9 broad regression + Story-34-1 ratchet check.**

**T10 self-G6 + ready-for-review handoff.**

**T11 Claude review + commit + flip done.**

---

## Acceptance Criteria (carryforward from Epic 34 spec)

- **AC-34-3-A** §02A field rename (D1 BINDING).
- **AC-34-3-B** §02A test suite migration (D5 BINDING).
- **AC-34-3-C** J-A1(a) operator-supplied run_id (D3 BINDING).
- **AC-34-3-D** J-A1(b) model_resolution_trail sidecar (D4 BINDING).
- **AC-34-3-E** Translator shrinkage (D7 BINDING).
- **AC-34-3-F** Closes deferred-inventory entries J-A1(a) + J-A1(b).

## Cross-references

Epic 34 §"Story 34-3"; Story 34-1 spec (translator); Story 34-2 spec (predecessor); deferred-inventory.md J-A1(a)/J-A1(b) entries.
