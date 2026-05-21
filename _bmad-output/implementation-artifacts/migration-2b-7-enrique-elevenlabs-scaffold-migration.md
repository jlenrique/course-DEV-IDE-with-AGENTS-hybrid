# Migration Story 2b.7: Migrate Enrique (ElevenLabs Voice Director) to 9-Node Scaffold

**Status:** done
**Sprint key:** `migration-2b-7-enrique-elevenlabs-scaffold-migration`
**Epic:** Slab 2b â€” seventh per-specialist migration; SIXTH inheritor of 2b.1 Gary TEMPLATE; FIRST inheritor of REST-API tool-dispatch category Â§12.11 (Gary parent).
**Pts:** 4 (BUMPED 3â†’4 per Amelia A-2b.7-R4 â€” substrate complexity higher than initially scoped: 1712-LOC `elevenlabs_operations.py` + 4 distinct mode entry points + composite manifest-narration function + pronunciation-dictionary authoring + VTT generation; matches Quinn-R 4pts heavy-inheritor band) | **Gate:** single (per governance JSON `2b-7.expected_gate_mode = "single-gate"`). **K-target:** ~1.4Ã— (target 17 / floor 13 â€” adjusted for per-mode helper test surface per A-2b.7-R2).

**Lean inheritor party-mode amendments applied 2026-04-25 (Murat + Amelia):** Murat GREEN; Amelia 4 RIDERs (substrate-driven):
- **A-2b.7-R1:** Strike conditional "OR direct package import" language; **importlib loader is MANDATORY** (substrate verified at story-author time: `elevenlabs_operations.py:26-46` runs `load_dotenv` + `sys.path.insert` Ã— 2 + cross-package imports + `raise RuntimeError` at module load if ffmpeg missing; PLUS `skills/elevenlabs-audio/scripts/__init__.py` is MISSING â€” direct package import structurally blocked).
- **A-2b.7-R2:** Multi-mode dispatch (narration / dialogue / SFX / music) requires per-mode helper extraction following Quinn-R W-R1 dispatcher pattern. Refactor LOC budget: `_act â‰¤ 95 LOC` (orchestration); `elevenlabs_dispatch â‰¤ 60 LOC` (mode-router shell); per-mode helpers `_dispatch_narration / _dispatch_dialogue / _dispatch_sfx / _dispatch_music` â‰¤ 35 LOC each; `_parse_audio_receipt â‰¤ 40 LOC`. Adds 4 mode-helper smoke tests.
- **A-2b.7-R3:** `audio.parsed.api-error` secondary-tag per HTTP status (M-R8 dimension pattern): `audio.parsed.api-error.{rate-limit | payment-required | voice-not-found | server-error | other}`. Operator triage value (429 retry-with-backoff vs 402 billing-escalation vs 404 voice-config-drift vs 5xx transient). Tag count stays 6 primary; secondary is dimension axis under `api-error`. R9 precedence appended: `payment-required â†’ voice-not-found â†’ rate-limit â†’ server-error â†’ other`.
- **A-2b.7-R4:** Pts 3â†’4; K-target 1.4Ã— target 13â†’17 / floor 10â†’13; collectible 27â†’31 / K-floor 20â†’24.

Enrique routes ElevenLabs API operations via the `elevenlabs-audio` substrate skill â€” **REST-API tool-dispatch category** (Â§12.11 Gary parent). Mirrors Gary's pattern: importlib loader OR direct package import (verify at T1) wraps `elevenlabs_operations.py` runner; LLM at `_act` for voice/mode selection + pronunciation handling + manifest write-back. **NEW A11 sub-shape #4** â€” skill-dir `bmad-agent-elevenlabs/` uses VENDOR/PRODUCT name (`elevenlabs`), persona is `Enrique`, lane is "Voice Director." Distinct from prior sub-shapes (persona-divergence A/snake-case B/lane-name C). Harvest at AC-J. **Sanctum graceful-degrade** (BMB sanctum at `_bmad/memory/bmad-agent-elevenlabs/` does NOT exist; verified 2026-04-25).

---

## T1 Readiness Block

Standing Pre-Flight items 1â€“11 same as 2b.6. Item 11: TEMPLATE doc v2.1 R1â€“R12 + M-R16 amendment apply.

### Slab 2b artifact-existence sweep â€” Enrique-specific deltas

- **C** Reference patterns: Gary 2b.1 (REST-API category Â§12.11 origin; importlib OR direct-package-import depending on substrate side-effects).
- **F** `pyproject.toml` C3 contains 11 rows pre-Enrique. Auto-emit makes 12.
- **G** Cache-hit-rate (FR54) per-script-prompts; defer FR54 to Slab-3 follow-on.
- **R2 importlib loader status:** depends on `elevenlabs_operations.py` substrate verification at T1. If side effects â†’ importlib (FOURTH occurrence; extends post-extraction state of `slab-2b-mid-cross-cutting-importlib-loader-extraction`); if clean â†’ direct package import (THIRD occurrence after Gary + Tracy; per Winston W-R2-2b.5 "extract when ceremony emerges, not on count alone" â€” defer extraction).

### Epic-doc-vs-framework cross-check (per R6)

#### (a) Framework drifts

**Drift #1 â€” Skill-dir uses VENDOR name (A11 SEVENTH example, NEW sub-shape D):** `bmad-agent-elevenlabs` (vendor name); persona `Enrique`. Sub-shapes now: A (persona-divergence), B (snake-case-divergence), C (lane-divergence), **D (vendor-name-divergence â€” NEW)**. CD 2b.6 W-R4 trigger likely retitled A11 to "Persona/skill-dir naming convention drift from hybrid BMB normalization" (G6 disposition); Enrique fits cleanly under that broader title. Harvest at AC-J as 7th example bullet under sub-shape D.

**Drift #2 â€” Model tier inferred from SKILL.md ("audio production specialist"; not in epic 2b.1 explicit tier table):** maps to `tier_request: fast` â†’ `gpt-5-haiku` (audio-direction is structurally simple â€” voice/mode selection from constrained options). NO A10 harvest (epic doesn't name a tier; spec author makes the binding decision).

#### (b) TEMPLATE scope decisions

**Decision #1 â€” Bounded scope (per R1):** Enrique SKILL.md scopes (a) headless audio synthesis, (b) interactive catalog audition + voice exploration, (c) sidecar memory-persistence. Migration scope = headless dispatch. Interactive + sidecar OUT OF SCOPE. NOT R8 bounded-scope-aggressive (only 2 categories OOS; threshold â‰¥2 â€” borderline, but interactive is small surface; declare R8 trigger as "borderline NO-trigger" per Murat M-R11 read).

**Decision #2 â€” REST-API dispatch wrapper with importlib loader MANDATORY (per Amelia A-2b.7-R1):** Enrique uses `app/specialists/enrique/elevenlabs_dispatch.py` wrapping `elevenlabs_operations.py` from `skills/elevenlabs-audio/scripts/`. **Substrate verified 2026-04-25:** `elevenlabs_operations.py:26-46` runs at module load â€” `from dotenv import load_dotenv` + `load_dotenv(PROJECT_ROOT / ".env")` + `sys.path.insert(0, str(PROJECT_ROOT))` Ã— 2 + `from scripts.api_clients.elevenlabs_client import ElevenLabsClient` + `raise RuntimeError` if ffmpeg missing. PLUS `skills/elevenlabs-audio/scripts/__init__.py` is MISSING â€” direct package import structurally blocked even without side-effect concerns. **Importlib loader is MANDATORY; direct-import fallback is N/A.** FOURTH importlib loader occurrence â€” extends post-extraction state of `slab-2b-mid-cross-cutting-importlib-loader-extraction` cross-cutting story.

**Decision #2-bis â€” Multi-mode dispatch fan-out per Amelia A-2b.7-R2 (Quinn-R W-R1 pattern):** ElevenLabs substrate exposes 4 distinct mode entry functions (`generate_narration` line 1050 / `generate_dialogue` line 1434 / `generate_sound_effect` line 1416 / `generate_music` line 1452) plus composite `generate_manifest_narration` line 1180 (~200 LOC). One `_act` cannot fan-out to 4 modes + LLM mode-selection + manifest write-back at the standard 115 LOC ceiling. **Factor following Quinn-R W-R1 dispatcher pattern:** thin `_act` (â‰¤95 LOC) for orchestration + LLM-driven mode selection + receipt parse; `elevenlabs_dispatch.py` mode-router shell (â‰¤60 LOC); four per-mode helpers `_dispatch_narration / _dispatch_dialogue / _dispatch_sfx / _dispatch_music` (â‰¤35 LOC each, in `elevenlabs_dispatch.py`). Total module â‰¤ 200 LOC. 4 mode-helper smoke tests in `test_enrique_dispatch_wrapper.py`.

**Decision #3 â€” Sanctum graceful-degrade:** parallel to Vera/Quinn-R/Tracy. PERSONA.md sentinel skip with `DEFERRED-OPERATOR-WINDOW` marker per W-R5 + R11 hard cap.

---

## Story

As a **migration dev agent inheriting TEMPLATE v2.1 R1â€“R12**,
I want **Enrique rehomed into `app/specialists/enrique/` with the 9-node scaffold + REST-API tool-dispatch act-body via `elevenlabs_operations.py` importlib loader + per-R5 auto-emit C3 row + Â§12.12 inheritor row added under Â§12.11 Gary parent**,
So that **the REST-API category (Â§12.11) gains its first inheritor (Gary â†’ Enrique), the importlib loader pattern gains its fourth occurrence (extending post-extraction state of the cross-cutting story), and Slab 2b cadence holds**.

---

## Acceptance Criteria

All ACs are dev-agent-executable. Enrique carries ONE `@pytest.mark.llm_live` test.

### AC-2b.7-A â€” Generator emits Enrique + auto-emits C3 row (per R5)

Per R5. Test pin: `tests/specialists/enrique/test_enrique_generator_auto_emit_c3_row.py` â€” 3 tests (`temp_repo_root` fixture). Generator: `--name enrique --mcp none --expertise-tier L4-audio-production --from-skill skills/bmad-agent-elevenlabs`.

### AC-2b.7-B â€” Enrique `act` node wires REST-API tool-dispatch via importlib loader

- **Given** Enrique's `_act` (1) reads ModelResolutionEntry (Winston W2); (2) extracts script + segment manifest from envelope; (3) reads style_guide.yaml fresh per Enrique principle 4; (4) invokes LLM (`tier_request: fast` â†’ `gpt-5-haiku`) for voice/mode selection + pronunciation-dictionary decisions; (5) dispatches via `app.specialists.enrique.elevenlabs_dispatch.dispatch_to_elevenlabs(script, segment_manifest, voice_id, mode)` (importlib-loader wrapper around `skills/elevenlabs-audio/scripts/elevenlabs_operations.py` per Decision #2); (6) parses receipt (audio file paths + timing metadata + voice_id used) via `_parse_audio_receipt` helper; (7) returns cache_state + `enrique_audio` reference.
- **LOC budget per A-2b.7-R2 (multi-mode helper extraction):** `_act â‰¤ 95 LOC` (orchestration + LLM mode-selection + receipt parse); `elevenlabs_dispatch.py` total â‰¤ 200 LOC composed of mode-router shell â‰¤60 LOC + four per-mode helpers (`_dispatch_narration / _dispatch_dialogue / _dispatch_sfx / _dispatch_music`) â‰¤ 35 LOC each; `_parse_audio_receipt` extracted helper â‰¤ 40 LOC.
- **Tag namespace + R12 ceiling + A-2b.7-R3 secondary-tag pattern:** `audio.parsed.*` â€” primary tags `audio.parsed.ok / malformed / missing-key / wrong-type / empty / api-error`. **6 primary tags within R12 ceiling.** **`api-error` carries M-R8 dimension secondary-tag** for operator triage: `audio.parsed.api-error.{rate-limit | payment-required | voice-not-found | server-error | other}`. R9 precedence: `malformed â†’ missing-key â†’ wrong-type â†’ empty â†’ api-error â†’ ok`. Within `api-error` secondary-tag precedence: `payment-required â†’ voice-not-found â†’ rate-limit â†’ server-error â†’ other` (most-actionable first).
- **SEAM tests (3 tests parallel to Gary + 4 mode-helper smoke tests per A-2b.7-R2):** negative-import-pin (no subprocess); fixture short-circuit on missing voice_id/script; importlib-loader smoke; **per-mode helper smoke (4 tests, one per mode):** assert each `_dispatch_<mode>` calls correct entry function from substrate. Total 7 tests in `test_enrique_dispatch_wrapper.py`.
- **Live LLM test:** AC-B-LIVE asserts live `gpt-5-haiku` call produces structurally valid voice-selection output (mode key + voice_id + settings) without invoking ElevenLabs API.

### AC-2b.7-B-OP â€” Live operator-gated evidence (DEFERRED-PENDING-OPERATOR-WINDOW)

Operator runs Enrique with real ElevenLabs API call (~$0.30/short-segment). Pastes audio file + timing metadata + voice_id into Completion Notes.

### AC-2b.7-C â€” Model cascade at `_plan` (per R7)

2 tests.

### AC-2b.7-D â€” Sanctum cold-read (graceful-degrade per R5+R6+R11 cap)

3 tests. PERSONA.md sentinel skip with `"DEFERRED-OPERATOR-WINDOW"` marker per W-R5. R11 hard cap: 3 inheritor stories OR 30 days; Enrique skip allowed; cap fires for Enrique by 2026-05-25.

### AC-2b.7-E â€” Gate-decision binding (precedent-inherited)

2 tests.

### AC-2b.7-F â€” Resolution trail (FR16 tenth per-specialist exercise)

1 test.

### AC-2b.7-G â€” Enrique shape-pin tests (per R4)

`enrique_audio: dict[str, Any] | None` (audio assets + timing metadata + voice_id used). 4 tests.

### AC-2b.7-H â€” Scaffold-conformance test registered

1 test.

### AC-2b.7-I â€” Migration-guide Â§12.12 grows ONE inheritor row (per R3)

| Specialist | Parent Â§12.x | Seam divergence | Sanctum case | Harvest contributions | Story |
|---|---|---|---|---|---|
| Enrique | Â§12.11 (Gary REST-API tool-dispatch) | importlib loader for `elevenlabs_operations.py` (hyphenated dirname `elevenlabs-audio/` forces it; 4th importlib occurrence) | graceful-degrade (BMB sanctum unpopulated) | A11 7th example sub-shape D (vendor-name) | 2b.7 |

### AC-2b.7-J â€” Anti-pattern catalog harvest

A11 7th example bullet under sub-shape D (vendor-name-vs-persona divergence). NO new top-level entries.

### AC-2b.7-K â€” TEMPLATE compliance (per R1â€“R12)

R1â€“R12 v2.1 honored without deviation.

### AC-2b.7-L â€” D12 close protocol (single-gate; FOUR-line per A-R7)

1. **Invariant preservation:** Slab-1 substrate intact; auto-emit C3 row machinery fired (C3 11â†’12 in live repo); FIRST Â§12.11 REST-API category inheritor lands cleanly.
2. **Anti-pattern harvest:** A11 7th example sub-shape D.
3. **Migration-guide update:** Â§12.12 inheritor row added under Â§12.11; framing updated.
4. **TEMPLATE compliance:** R1â€“R12 v2.1 honored. Numeric anchors: `_act` LOC â‰¤115; `elevenlabs_dispatch` LOC â‰¤75; 6 parse-branch tests; 1 @llm_live; sanctum graceful-degrade with R11 cap; pyproject.toml 5â†’6 fixture / 11â†’12 live.

### AC-2b.7-M â€” Sprint-status state-flips at filing AND at close

At filing: ready-for-dev. At close: done. File `enrique-fr54-cache-hit-baseline-measurement` follow-on.

---

## File Structure Requirements

```
app/specialists/enrique/
â”œâ”€â”€ __init__.py, graph.py, state.py, model_config.yaml
â”œâ”€â”€ elevenlabs_dispatch.py                      # NEW (~50-75 LOC); importlib loader
â””â”€â”€ expertise/{README.md, __init__.py}

tests/specialists/enrique/
â”œâ”€â”€ __init__.py
â”œâ”€â”€ test_enrique_generator_auto_emit_c3_row.py  # 3 tests
â”œâ”€â”€ test_enrique_act_node_dispatch.py           # ~8 tests (6 parse-branches + 1 happy + 1 @llm_live)
â”œâ”€â”€ test_enrique_dispatch_wrapper.py            # 7 tests per A-2b.7-R2 (3 SEAM + 4 per-mode helper smoke)
â”œâ”€â”€ test_enrique_model_cascade.py               # 2 tests
â”œâ”€â”€ test_enrique_sanctum_cold_read.py           # 3 tests
â”œâ”€â”€ test_enrique_gate_decision_binding.py       # 2 tests
â”œâ”€â”€ test_enrique_resolution_trail.py            # 1 test
â””â”€â”€ test_enrique_state_shape.py                 # 4 tests

tests/integration/scaffold_conformance/
â””â”€â”€ test_scaffold_enrique.py                    # 1 test

tests/fixtures/specialists/enrique/
â”œâ”€â”€ golden_envelope.json
â””â”€â”€ golden_return.json
```

### MODIFIED files

- `docs/dev-guide/langgraph-migration-guide.md` â€” Â§12.12 new row; framing.
- `docs/dev-guide/specialist-anti-patterns.md` â€” A11 7th example bullet.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` â€” per AC-M.
- `pyproject.toml` â€” auto-emitted.

---

## Testing Requirements

**K-target ~1.4Ã— (target 17 / floor 13) â€” bumped per A-2b.7-R4.** Test count: 3 + 8 + 7 + 2 + 3 + 2 + 1 + 4 + 1 = **31 collectible**; ~24 K-floor units. Effective ratio ~1.85Ã— floor / ~1.4Ã— target.

**Regression target at T8:** â‰¥244 passed / â‰¥4 skipped placeholder-key (Tracy + Enrique sanctum DEFERRED-* skips). Import-linter 3/3 KEPT; Ruff clean; Sandbox-AC PASS.

---

## Dev Agent Record

_(Populated during T1â€“T9.)_


### T8 Regression Evidence

- Specialist-wave slice validation: 184 passed / 1 skipped across cd/enrique/wanda/kim/vyx/aria/mira/tamara + scaffold conformance.
- Specialists + scaffold conformance anchor: 525 passed / 7 skipped.
- uff check clean on touched specialist/test paths.
- lint-imports 3/3 kept.
- Sandbox-AC validator PASS for stories 2b.6-2b.13.

