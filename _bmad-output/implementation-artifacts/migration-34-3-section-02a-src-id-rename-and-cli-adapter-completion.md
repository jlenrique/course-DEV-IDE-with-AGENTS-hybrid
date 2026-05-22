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

**D2. Cascading rename across §02A package:** Search `app/composers/section_02a/` and `docs/conversational-gates/section-02a-composer.j2` for ALL references to `src_id` and replace with `ref_id`. Files affected (Codex T1 grep-verify):
- `composer.py` — likely consumes the field name in payload construction
- `_prompt.py` — if the LLM prompt template names the field (likely yes per 7c.3a precedent)
- `_cache.py` — if cache-key derivation includes field name (unlikely; cache key is SHA256 of normalized prompt)
- `cli_adapter.py` — likely consumes via `Directive.sources[i].src_id` access patterns
- `__init__.py` — re-exports unchanged (field name is internal to Pydantic model)
- `section-02a-composer.j2` — if it tells the LLM to emit `src_id: ...` per source

**D3. J-A1(a) — operator-supplied run_id wins (FR-E34-8 BINDING):**

Per `app/composers/section_02a/composer.py` current behavior, `Directive.run_id` is generated internally as `uuid4()` (per `directive_model.py:114`). Story 34-3 changes this:

```python
# composer.py — new signature
def compose(
    corpus_dir: Path,
    *,
    llm: BaseChatModel,
    cache: ComposerCache | None = None,
    run_id: UUID,  # NEW required parameter; uuid4-validated by Pydantic at Directive instantiation
) -> Directive:
    """LLM-driven §02A directive composition; uses caller-supplied run_id."""
    # ... (existing body)
    return Directive(
        run_id=run_id,  # threaded through; NOT internally generated
        corpus_dir=str(corpus_dir),
        sources=tuple(...),
        composed_at=datetime.now(tz=UTC),
    )
```

And in `cli_adapter.py::compose_and_write`:

```python
def compose_and_write(
    *,
    corpus_dir: Path,
    run_dir: Path,
    effective_trial_id: UUID,  # NEW required parameter (was probably absent before)
) -> tuple[Path, str]:
    """Bridge trial CLI's effective_trial_id to §02A composer's run_id."""
    chat_handle = make_chat_model("marcus")
    directive = compose(
        corpus_dir,
        llm=chat_handle.chat,
        cache=ComposerCache(),
        run_id=effective_trial_id,  # NEW threaded param
    )
    directive_path = run_dir / "directive.yaml"
    write_directive_yaml(directive, directive_path)
    digest = hashlib.sha256(directive_path.read_bytes()).hexdigest()
    # ... J-A1(b) trail-append happens here per D4
    return directive_path, digest
```

And in `app/marcus/cli/trial.py` (carries the `effective_trial_id` already):

```python
# At call site, update from:
#   directive_path, directive_digest = compose_and_write(corpus_dir=input_path, run_dir=run_dir)
# To:
directive_path, directive_digest = compose_and_write(
    corpus_dir=input_path,
    run_dir=run_dir,
    effective_trial_id=effective_trial_id,  # NEW
)
```

**D4. J-A1(b) — model_resolution_trail sidecar (FR-E34-9 BINDING):**

`cli_adapter.compose_and_write` currently discards `ChatModelHandle.entry`. Story 34-3 persists it as a sidecar JSON in `run_dir`:

```python
# cli_adapter.py — inside compose_and_write, after chat_handle obtained:
import json
from app.models.adapter import ModelResolutionEntry  # or equivalent path

# ... after `chat_handle = make_chat_model("marcus")`:
trail_sidecar_path = run_dir / "model_resolution_trail.json"
trail_data = {
    "specialist_id": "marcus",
    "resolved": chat_handle.entry.resolved,  # access via NamedTuple field names per current adapter
    "level": chat_handle.entry.level,
    "cache_prefix_hash": chat_handle.entry.cache_prefix_hash,
    # ... any other ModelResolutionEntry fields per current schema
    "captured_at": datetime.now(tz=UTC).isoformat(),
}
trail_sidecar_path.write_text(
    json.dumps(trail_data, indent=2, sort_keys=True),
    encoding="utf-8",
)
```

The sidecar path is **deterministic** (`run_dir / "model_resolution_trail.json"`); downstream consumers OR Marcus run state can pick it up later. (This is the simpler-of-two-options per J-A1(b) entry; threading through `RunState.model_resolution_trail` is a deeper refactor that Story 34-3 does NOT undertake — surface as decision_needed if Codex believes the sidecar is wrong direction.)

**D5. §02A test surface migration (Amelia A-A1 BINDING):**

Codex T2 sweeps the 8 §02A test-surface paths (all pre-allowlisted at C1) and replaces ALL occurrences of `src_id` → `ref_id`. Grep-verify count per Amelia's pre-Round-1 inventory:
- `tests/composers/section_02a/test_composer_directive_model_shape.py` — 2 hits
- `tests/composers/section_02a/_helpers.py` — N hits
- `tests/composers/section_02a/test_composer_classification.py` — N hits
- `tests/composers/section_02a/test_composer_cache_key_normalization.py` — N hits
- `tests/composers/section_02a/test_composer_trial_2_finding_2_regression.py` — N hits
- `tests/composers/section_02a/test_composer_utf8_write.py` — N hits
- `tests/gates/section_02a/_helpers.py` — 3 hits
- `tests/gates/section_02a/test_g0_poll_surface_field_level_edit.py` — 1 hit

Total ≥ 7 hits (Amelia grep) + however many in the _helpers files. Codex T2 final-grep MUST confirm zero residual `src_id` references in §02A test surface.

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
