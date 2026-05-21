# Migration Story 2b.4: Migrate Desmond (Descript Assembly Specialist) to 9-Node Scaffold

**Status:** done
**Sprint key:** `migration-2b-4-desmond-descript-scaffold-migration`
**Epic:** Slab 2b â€” fourth per-specialist migration; THIRD inheritor of 2b.1 Gary TEMPLATE; **SECOND populated-and-locked sanctum case** (after Texas 2a.4); narration category inheritor (Â§12.5 Irene parent).
**Pts:** 3 | **Gate:** single (per governance JSON `2b-4.expected_gate_mode = "single-gate"`, rationale: "Follows 2b.1 TEMPLATE"). **K-target:** ~1.4Ã— (target 13 / floor 10; pure inheritor â€” no new category, no R2 trigger, no novel dispatch surface).

**Lean inheritor party-mode amendments applied 2026-04-25 (Murat + Amelia, 2-agent for clean inheritor):** 3 RIDERs integrated â€” M-R10 (narration parse-helper precedence convention: structural-presence tags evaluated BEFORE content-validation tags; `empty` precedes `advisory-missing`; carries forward to all narration inheritors), A-DESMOND-R1 (sanctum baseline capture command pinned in T1 Readiness with CRLFâ†’LF normalization matching `_read_sanctum_digest`), A-DESMOND-R2 (`advisory-missing` detection mechanism pinned: exact heading-line detection in `_parse_handoff` using `re.search(r"^## Automation Advisory[ \t]*$", parsed_text, re.MULTILINE)`). All mechanical T1 pins â€” no scope change.

Desmond produces Descript assembly-handoff instructions for human editors. Act-body is **narration category** (Â§12.5 Irene parent) â€” LLM authoring with NO external dispatch substrate (the `init_desmond_sanctum.py` + `refresh_descript_reference.py` scripts are operator/session-side CLI tools, NOT runtime dispatch substrates invoked from `_act`). Desmond adds ONE row to Â§12.12 inheritor catalog matrix under Â§12.5 parent (per R3). **NO A11 drift** (skill-dir `bmad-agent-desmond` matches runtime persona `desmond`). **POPULATED-and-LOCKED sanctum** at `_bmad/memory/bmad-agent-desmond/` (BOND/CAPABILITIES/CLONE-FORK-NOTICE/CREED/INDEX/MEMORY/PERSONA + sessions/ â€” verified at story-author time 2026-04-25).

---

## T1 Readiness Block

Standing Pre-Flight items 1â€“10 same as 2b.2. Item 11: [`docs/dev-guide/specialist-migration-template.md`](../../docs/dev-guide/specialist-migration-template.md) v1, R1â€“R7 apply.

### Slab 2b artifact-existence sweep â€” Desmond-specific deltas

- **C** Reference patterns: Irene 2a.2 (narration category at Â§12.5 â€” closest precedent; pure LLM authoring). NOT Vera/Quinn-R (those are LLM+tool-dispatch); NOT Texas/Gary (tool-dispatch).
- **F** `pyproject.toml` C3 contains 8 rows pre-Desmond (5 baseline + Gary + Vera + Quinn-R). Desmond auto-emit makes 9.
- **G** Cache-hit-rate (FR54): Desmond's act invokes LLM with stable Descript-doc-cache prefix (per principle: "refresh a local doc cache so guidance stays aligned"). **FR54 substrate IS applicable** at the Desmond layer â€” the cached Descript doc reference + team conventions form a stable prefix. Defer FR54 measurement to a 2b-mid-slab follow-on (NOT 2b.4 scope) since this is the FIRST narration-category inheritor and the FR54 harness baseline at Irene is the comparison point. File `desmond-fr54-cache-hit-baseline-measurement` follow-on at 2b.4 close.
- **R2 importlib loader status:** Desmond has NO dispatch wrapper (no LLM+tool-dispatch substrate; act-body is pure LLM narration). Loader-occurrences count UNCHANGED at 3 (Kira + Vera + Quinn-R). R2 extraction follow-on filed at 2b.3 still owed pre-2b.5 per Winston hard reactivation gate.

### Epic-doc-vs-framework cross-check (per R6)

#### (a) Framework drifts

**NONE at 2b.4.** Skill-dir `bmad-agent-desmond` matches runtime persona `desmond` (no A11 drift); model tier "fast and current Descript-aware" maps cleanly to `tier_request: fast` â†’ `gpt-5-haiku` per epic prose intent (no A10 drift â€” though the "fast and current" framing is approximate). **First Slab 2b story with NO framework drifts** â€” confirms the harvest-gate continues to find drift only when present.

#### (b) TEMPLATE scope decisions

**Decision #1 â€” Bounded scope (per R1):** Desmond SKILL.md describes (a) headless `--headless` doc-refresh mode, (b) interactive rebirth mode for editor consultation, (c) session-close memory-persistence ritual. **Migration scope:** the headless dispatch path Marcus invokes for assembly-handoff authoring. Doc-refresh is a CLI script (`refresh_descript_reference.py`) â€” operator-side, OUT OF SCOPE. Interactive rebirth + memory-persistence are sidecar concerns, OUT OF SCOPE.

**Decision #2 â€” NO dispatch wrapper:** Desmond's `_act` invokes LLM directly via `make_chat_model(specialist_id="desmond", tier_request="fast")` and returns the assembly-handoff text. No external substrate. R2 sub-mechanism rule does NOT apply (no loader needed; no third-occurrence trigger advanced). Same shape as Irene Â§12.5.

**Decision #3 â€” POPULATED-and-LOCKED sanctum:** Desmond's BMB sanctum at `_bmad/memory/bmad-agent-desmond/` IS populated (verified 2026-04-25). AC-2b.4-D applies the populated-and-locked case (parallel to Texas 2a.4) â€” sha256 manifest pinned with hard equality test. **NO graceful-degrade applies.** Sanctum lock baseline captured at T1 + inlined as module-level constant in test file per Amelia A3 carry-forward.

**Sanctum baseline capture command (per Amelia A-DESMOND-R1 amendment 2026-04-25 â€” BINDING; CRLFâ†’LF normalization matches `_read_sanctum_digest`):**
```bash
.venv\Scripts\python.exe -c "import hashlib, pathlib; root=pathlib.Path('_bmad/memory/bmad-agent-desmond'); [print(f'{p.relative_to(root).as_posix()!r}: {hashlib.sha256(p.read_bytes().replace(chr(13).encode()+chr(10).encode(), chr(10).encode())).hexdigest()!r},') for p in sorted(root.rglob('*'), key=lambda x: x.relative_to(root).as_posix()) if p.is_file()]"
```
Emits dict-literal-ready lines for `DESMOND_SANCTUM_LOCK_BASELINE` constant in `app/specialists/desmond/graph.py`. **Without CRLF normalization, baseline mismatches `assert_sanctum_lock` at first run** â€” single most likely T2 trip. The deferred `slab-2a-close-followon-sanctum-lock-regen` script is NOT yet shipped; use the inline command.

---

## Story

As a **migration dev agent inheriting the 2b.1 TEMPLATE**,
I want **Desmond (Descript Assembly Specialist) rehomed into `app/specialists/desmond/` with the 9-node scaffold + narration-category act-body (LLM-only, NO dispatch substrate) + populated-and-locked sanctum cold-read (second occurrence after Texas) + per-R5 auto-emit C3 row positive regression test + Â§12.12 inheritor row added under Â§12.5 parent**,
So that **the narration category gains its first inheritor (Irene â†’ Desmond), the populated-and-locked sanctum case is exercised a second time (proving the pattern from Texas generalizes), the 2b cadence proves out for pure-LLM specialists with no novel surface, and Slab 2b inheritor velocity continues**.

---

## Acceptance Criteria

All ACs are dev-agent-executable. Desmond carries ONE `@pytest.mark.llm_live` test (AC-B live LLM authoring against fixture envelope).

### AC-2b.4-A â€” Generator emits Desmond + auto-emits C3 row (per R5)

Per R5 + 2b.1 hermetic pattern. Test pin: `tests/specialists/desmond/test_desmond_generator_auto_emit_c3_row.py` â€” 3 tests using `temp_repo_root` fixture. Pre-baseline 5 â†’ post-emit 6 (in fixture); live repo at story close = 9 rows total.

Generator invocation:
```
.venv\Scripts\python.exe -m skills.bmad_create_specialist.scripts.generate \
  --name desmond --mcp none --expertise-tier L4-descript-assembly \
  --from-skill skills/bmad-agent-desmond
```

### AC-2b.4-B â€” Desmond `act` node wires NARRATION (LLM-only; no dispatch substrate)

- **Given** Desmond is a Descript assembly specialist; her `_act` (1) reads the latest `ModelResolutionEntry` from `state.model_resolution_trail` + reject if `cache_prefix_hash is None` (Winston W2 discriminator-check); (2) extracts the assembly-context payload from `state.cache_state.cache_prefix` (envelope-carrier-hack); (3) assembles the LLM prompt from sanctum-cached Descript doc references + team-convention memory; (4) invokes LLM (`tier_request: fast` â†’ `gpt-5-haiku`) to author the assembly handoff text + mandatory `## Automation Advisory` block; (5) parses the LLM response into the handoff envelope shape; (6) returns `{cache_state: {cache_prefix: <output_blob>, entries_count: ...}}` with handoff encoded as sorted-keys canonical JSON.
- **When** the dev agent implements `_act` per the narration pattern (Irene precedent at `app/specialists/irene/graph.py`).
- **Then** invoking `build_desmond_graph()` with a fixture envelope produces a non-empty result containing `desmond_handoff` (the assembly-handoff package) + provenance metadata.
- **LOC budget per A-R3 carry-forward:** `_act â‰¤ 115 LOC`; `_parse_handoff` helper extracted module-level (per Vera A-R9 option-b precedent) so 5-branch parametrize matrix targets the helper, not `_act`.
- **Tag namespace per Murat M-R2 convention + M-R10 narration precedence convention:** `handoff.parsed.*` â€” tags `handoff.parsed.ok / malformed / missing-key / wrong-type / empty / advisory-missing` (advisory-missing fires when LLM omits the mandatory `## Automation Advisory` block â€” Desmond's load-bearing principle). Six parametrized parse-branch cases. **`_parse_handoff` MUST evaluate `empty` BEFORE `advisory-missing` per Murat M-R10 amendment 2026-04-25** â€” structural-presence tags (`empty`, `malformed`) evaluated BEFORE content-validation tags (`advisory-missing`). Rationale: `empty` is strictly broader (no content at all); `advisory-missing` presupposes content exists but lacks required block. Test pin: parametrize case input `""` â†’ tag = `empty`, NOT `advisory-missing`. **Convention generalizes** to any future narration inheritor with mandatory content blocks (e.g., future specialist requiring `## Risk Statement`).
- **`advisory-missing` detection per Amelia A-DESMOND-R2 (BINDING regex pin):** `_parse_handoff` uses `re.search(r"^## Automation Advisory[ \t]*$", parsed_text, re.MULTILINE)` to detect the mandatory header. Case-sensitive, exact `## ` prefix, and exact heading line (trailing whitespace allowed only). Case/spacing variants flag as advisory-missing (correct â€” bug-as-feature; the parser enforces the SKILL.md contract verbatim). Detection lives in `_parse_handoff` (extracted helper per A-R9), tag emitted to resolution-trail.
- **Live LLM test (`@pytest.mark.llm_live`):** AC-B-LIVE asserts the live `gpt-5-haiku` call produces a structurally valid handoff shape AND the response includes the mandatory `## Automation Advisory` markdown header. Skips on placeholder OPENAI_API_KEY.

### AC-2b.4-B-OP â€” Live operator-gated evidence (DEFERRED-PENDING-OPERATOR-WINDOW)

Operator runs Desmond against a real Marcus-staged assembly-handoff request (one handoff authoring; ~1500 tokens). Pastes handoff + Automation Advisory into Completion Notes. Same shape as Vera/Gary operator-gated evidence.

### AC-2b.4-C â€” Model cascade at `_plan` (per R7)

Trail-entry resolution at `_plan` per R7. Desmond DOES invoke LLM at `_act` (narration category). Test pin: 2 tests (default + override).

### AC-2b.4-D â€” Sanctum cold-read at `_plan` (POPULATED-and-LOCKED â€” second real occurrence after Texas)

- **Given** Desmond's BMB sanctum at `_bmad/memory/bmad-agent-desmond/` IS populated at story-author time (verified: BOND/CAPABILITIES/CLONE-FORK-NOTICE/CREED/INDEX/MEMORY/PERSONA + sessions/ all present). **Second populated-and-locked case after Texas 2a.4** â€” proving the pattern generalizes beyond Texas's pure-tool-dispatch.
- **When** Desmond's `plan` node runs `_read_sanctum_digest` (modeled on Texas's helper post-2a.3-P6 â€” bytes-level CRLFâ†’LF normalization).
- **Then** `_read_sanctum_digest(SANCTUM_DIR)` returns a non-empty deterministic sorted-by-as_posix sha256 listing of the BMB persona files (7 files at story-author time).
- **Test pins (4 tests â€” UPGRADE from pure-graceful-degrade pattern; matches Texas 2a.4 populated-and-locked shape):**
  1. `test_desmond_sanctum_fingerprint_deterministic_populated` â€” fingerprint deterministic across two reads against real `_bmad/memory/bmad-agent-desmond/`.
  2. `test_desmond_expertise_readme_lists_l4_references` â€” reference-name shape matches `expertise/README.md`.
  3. `test_desmond_sanctum_lock_baseline_pinned` â€” pre-run sha256 manifest matches recorded baseline (operator-curated baseline captured at T1 + inlined as `DESMOND_SANCTUM_LOCK_BASELINE` module-level constant per Texas precedent). **Hard sha256 equality** â€” no softening, no file-count-only fallback. Per-file.
  4. `test_desmond_sanctum_lock_violation_raises_named_exception` â€” synthetic mutation triggers `SanctumLockViolation` (imported `from app.specialists.texas.graph` per pending cross-cutting refactor â€” same import as Vera/Quinn-R; threshold met for Slab-2 cross-cutting `slab-2a-close-followon-sanctum-lock-cross-cutting` extraction filed at 2b.3 close, scheduled before 2b.5).

### AC-2b.4-E â€” Gate-decision binding (precedent-inherited)

2 tests.

### AC-2b.4-F â€” Resolution trail (FR16 seventh per-specialist exercise)

1 test.

### AC-2b.4-G â€” Desmond shape-pin tests (per R4)

Per R4 (one new field, loose-typed): `desmond_handoff: dict[str, Any] | None` (the assembly-handoff package + Automation Advisory text). Strict-typing deferred to 2b.15. Test pin: 4 tests.

### AC-2b.4-H â€” Scaffold-conformance test registered

`tests/integration/scaffold_conformance/test_scaffold_desmond.py` â€” 1 test.

### AC-2b.4-I â€” Migration-guide Â§12.12 grows ONE inheritor row (per R3)

Per R3, NEW row in Â§12.12 under Â§12.5 (Irene narration) parent:

| Specialist | Parent Â§12.x | Seam divergence | Sanctum case | Harvest contributions | Story |
|---|---|---|---|---|---|
| Desmond | Â§12.5 (Irene narration) | NO dispatch substrate (pure LLM authoring); Automation Advisory mandatory output block per Desmond principle | populated-and-locked (BMB sanctum present; 7 locked files; sha256 baseline pinned) | NONE (no framework drifts; first 2b story with empty harvest) | 2b.4 |

Update Â§12.5 framing sentence to reflect "seventh specialist proven on 9-node scaffold; second populated-and-locked sanctum case (Desmond after Texas); narration category now has 2 inhabitants (Irene + Desmond)."

### AC-2b.4-J â€” Anti-pattern catalog harvest (NONE at 2b.4)

**No new bullets.** First 2b story with no framework drifts to harvest. Document explicitly in Dev Agent Record + D12 stub: "harvest empty â€” confirms standing protocol surfaces drift only when present."

### AC-2b.4-K â€” TEMPLATE compliance (per R1â€“R7)

R1â€“R7 honored without deviation. Numeric anchors at D12.

### AC-2b.4-L â€” D12 close protocol (single-gate; FOUR-line per A-R7)

1. **Invariant preservation:** Slab-1 substrate intact; auto-emit C3 row machinery fired correctly (C3 list grows 8â†’9 rows in live repo); FR54 substrate intact + applicable to Desmond (cache-hit-rate measurement deferred to follow-on per Decision G); SECOND populated-and-locked sanctum case lands cleanly (Texas pattern generalizes).
2. **Anti-pattern harvest:** NONE â€” first 2b story with empty harvest. Standing protocol confirmed working.
3. **Migration-guide update:** Â§12.12 inheritor row added under Â§12.5 parent per AC-I; framing sentence updated.
4. **TEMPLATE compliance:** R1â€“R7 honored without deviation. Numeric anchors: `_act` LOC measured (â‰¤115); 5 parse-branch tests; 1 @llm_live test; sanctum populated-and-locked case (4 tests including lock-baseline + lock-violation); pyproject.toml C3 row count 5â†’6 in temp fixture / 8â†’9 in live repo.

### AC-2b.4-M â€” Sprint-status state-flips at filing AND at close

At filing: `migration-2b-4-desmond-descript-scaffold-migration: ready-for-dev`. At close: flip to `done`. Also at close: file `desmond-fr54-cache-hit-baseline-measurement` follow-on per Decision G.

---

## File Structure Requirements

### NEW files

```
app/specialists/desmond/
â”œâ”€â”€ __init__.py                                 # generator-emitted
â”œâ”€â”€ graph.py                                    # generator-emitted; _act body filled at T2 (narration-only, NO dispatch wrapper)
â”œâ”€â”€ state.py                                    # generator-emitted; DesmondReturn extended with desmond_handoff
â”œâ”€â”€ model_config.yaml                           # generator-emitted; fast-tier comments
â”œâ”€â”€ expertise/
â”‚   â”œâ”€â”€ README.md                               # generator-emitted; dotted reference table for Desmond's references
â”‚   â””â”€â”€ __init__.py

# NO dispatch wrapper module â€” Desmond is narration-only

tests/specialists/desmond/
â”œâ”€â”€ __init__.py                                 # NEW (empty marker per A-R6)
â”œâ”€â”€ test_desmond_generator_auto_emit_c3_row.py  # NEW (3 tests; AC-A)
â”œâ”€â”€ test_desmond_act_node_authoring.py          # NEW (~7 tests; AC-B with 5 parse-branches + 1 happy-path + 1 @llm_live)
â”œâ”€â”€ test_desmond_model_cascade.py               # NEW (2 tests; AC-C)
â”œâ”€â”€ test_desmond_sanctum_cold_read.py           # NEW (4 tests; AC-D POPULATED â€” upgrade from graceful-degrade pattern)
â”œâ”€â”€ test_desmond_gate_decision_binding.py       # NEW (2 tests; AC-E)
â”œâ”€â”€ test_desmond_resolution_trail.py            # NEW (1 test; AC-F)
â””â”€â”€ test_desmond_state_shape.py                 # NEW (4 tests; AC-G)

tests/integration/scaffold_conformance/
â””â”€â”€ test_scaffold_desmond.py                    # NEW (1 test; AC-H)

tests/fixtures/specialists/desmond/
â”œâ”€â”€ golden_envelope.json                        # NEW
â””â”€â”€ golden_return.json                          # NEW (with desmond_handoff populated including Automation Advisory)
```

### MODIFIED files

- `docs/dev-guide/langgraph-migration-guide.md` â€” Â§12.12 new row under Â§12.5; Â§12.5 framing updated.
- `docs/dev-guide/specialist-anti-patterns.md` â€” NO changes (empty harvest).
- `_bmad-output/planning-artifacts/deferred-inventory.md` â€” file `desmond-fr54-cache-hit-baseline-measurement` follow-on per AC-M.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` â€” per AC-M.
- `pyproject.toml` â€” auto-emitted; **NOT manually edited**.

---

## Testing Requirements

**K-target ~1.4Ã— (target 13 / floor 10).** Pure narration inheritor â€” no dispatch surface. Test count: 3 + 7 + 2 + 4 + 2 + 1 + 4 + 1 = **24 collectible test functions** (test_desmond_act_node_authoring.py = 6 parse-branches with M-R10 precedence case + 1 happy-path + 1 @llm_live = 7 functions; `empty` case asserts precedence over `advisory-missing`); ~18 K-floor units after parametrize-collapse. Effective ratio ~1.8Ã— floor / ~1.4Ã— target. Anti-padding-band-creep guard: dev agent at G6 DISMISSes drift beyond 24.

**Regression target at T8:** â‰¥210 passed / â‰¥2 skipped placeholder-key (was â‰¥202 at 2b.3 close projected; +8 at floor / +10 at target). Import-linter 3/3 KEPT; Ruff clean; Sandbox-AC PASS.

---

## Dev Agent Record

_(Populated during T1â€“T9 execution.)_

### T1 Readiness

- Readiness references consumed in required order; TEMPLATE R1-R7 applied.
- Sandbox-AC validator PASS:
  - `.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-2b-4-desmond-descript-scaffold-migration.md`
- Sanctum baseline captured at T1 using the pinned CRLF->LF normalization command and inlined into `DESMOND_SANCTUM_LOCK_BASELINE`.

### T2-T7 Implementation Notes

- Implemented Desmond runtime in `app/specialists/desmond/graph.py`:
  - `_plan` resolves model cascade and enforces populated-and-locked sanctum via `assert_sanctum_lock`.
  - `_act` is narration-only (no dispatch wrapper), with prompt assembly from sanctum digest + Desmond references.
  - Added extracted `_parse_handoff` helper with `handoff.parsed.*` tags:
    - `ok`, `malformed`, `missing-key`, `wrong-type`, `empty`, `advisory-missing`.
    - M-R10 precedence enforced (`empty` before `advisory-missing`).
    - A-DESMOND-R2 regex hardened to exact heading line: `re.search(r"^## Automation Advisory[ \\t]*$", parsed_text, re.MULTILINE)`.
  - Added two-sided trail-tagging on `_act` failure paths.
- Extended `DesmondReturn` with loose-typed `desmond_handoff: dict[str, Any] | None` per R4.
- Added full Desmond test surface and updated fixture `golden_return.json` with `desmond_handoff`.
- Updated migration guide framing + §12.12 row; anti-pattern catalog unchanged (empty harvest).

### T8 Regression Evidence

- Desmond slice:
  - `.venv/Scripts/python.exe -m pytest tests/specialists/desmond tests/integration/scaffold_conformance/test_scaffold_desmond.py -q`
  - Result: **40 passed / 1 skipped**
- Specialists + scaffold conformance anchor:
  - `.venv/Scripts/python.exe -m pytest tests/specialists tests/integration/scaffold_conformance -q`
  - Result: **300 passed / 5 skipped**
- Ruff:
  - `.venv/Scripts/python.exe -m ruff check app/specialists/desmond tests/specialists/desmond tests/integration/scaffold_conformance/test_scaffold_desmond.py docs/dev-guide/langgraph-migration-guide.md _bmad-output/planning-artifacts/deferred-inventory.md _bmad-output/implementation-artifacts/sprint-status.yaml`
  - Result: **All checks passed**
- Import-linter:
  - `.venv/Scripts/lint-imports.exe`
  - Result: **3 kept / 0 broken**
- Sandbox AC:
  - `.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-2b-4-desmond-descript-scaffold-migration.md`
  - Result: **PASS**

### Party-Mode Review (lean 2-agent: Murat + Amelia)

Top-line: GREEN after patch pass.

- PATCH applied
  1. Parse precedence contract pin (`empty` beats `advisory-missing`) strengthened in dedicated test.
  2. Sanctum lock test hardened to assert named exception on synthetic mutation.
  3. Added explicit two-sided trail-tag assertion for malformed-envelope `_act` path.
- DEFER
  1. FR54 Desmond-vs-Irene comparative baseline remains deferred to follow-on (`desmond-fr54-cache-hit-baseline-measurement`).
- DISMISS
  1. Requests to introduce new anti-pattern bullets were dismissed (no framework drift evidence in this story).

### G6 Layered Code Review (Blind / Edge / Acceptance)

Top-line: GREEN.

- PATCH applied
  1. Ensured `assert_sanctum_lock` compares per-file manifest equality (not aggregate hash fallback).
  2. Added explicit migration-guide verification commands for Desmond.
  3. Recorded follow-on filing and sprint-status close flip anchors.
- DEFER
  1. Strict-typed handoff schema extraction deferred to 2b.15 dispatch-contract hardening wave.
- DISMISS
  1. Optional prompt wording/style nits (non-behavioral) dismissed.

### D12 Close Stub

1. Invariant preservation: Slab-1 substrate intact; C3 auto-emit remains active and regression-tested; FR54 substrate remains applicable to Desmond but baseline measurement deferred by follow-on; second populated-and-locked sanctum case landed and lock baseline pinned.
2. Anti-pattern harvest: NONE (empty harvest confirms drift harvesting is conditional, not forced).
3. Migration-guide update: §12 framing updated and §12.12 Desmond inheritor row added under §12.5.
4. TEMPLATE compliance: R1-R7 honored. Numeric anchors: `_act` <= 115 LOC; parse matrix includes six branches with precedence pin; one `@llm_live` test (skip-safe when live model unavailable); sanctum lock suite includes deterministic fingerprint + baseline equality + violation exception; Desmond slice 40/1; specialists+conformance 300/5.

### Completion Notes

- AC-B-OP remains **DEFERRED-PENDING-OPERATOR-WINDOW**.
- Follow-on filed in deferred inventory:
  - `desmond-fr54-cache-hit-baseline-measurement`.

