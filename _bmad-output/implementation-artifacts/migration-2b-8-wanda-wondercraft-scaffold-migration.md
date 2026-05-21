# Migration Story 2b.8: Migrate Wanda (Wondercraft Podcast Director) to 9-Node Scaffold â€” Path A confirmed

**Status:** done
**Sprint key:** `migration-2b-8-wanda-wondercraft-scaffold-migration`
**Epic:** Slab 2b â€” eighth per-specialist migration; SEVENTH inheritor of 2b.1 Gary TEMPLATE; SECOND inheritor of REST-API tool-dispatch category Â§12.11 (Gary parent + Enrique 2b.7 sibling); **Path A confirmed at story-author time** (per slab-2-roster-reconciliation Â§Wondercraft Decision default).
**Pts:** 4 (matches Enrique 2b.7 multi-mode REST-API band; conditional on Amelia A-2b.8-R2 helper extraction acceptance â€” bump to 5pts if R2 declined) | **Gate:** single. **K-target:** ~1.4Ã— (target 14 / floor 11 â€” RECALIBRATED per Murat M-R18 amendment 2026-04-25 collapsing 6 mode-helper smoke tests into 1 parametrized function).

**Lean inheritor party-mode amendments applied 2026-04-25 (Murat + Amelia):** 5 RIDERs integrated:
- **M-R18 (NEW; codify in TEMPLATE v2.2):** Multi-mode dispatch fan-out per A-2b.7-R2 â€” per-mode helper smoke tests MUST be parametrize-collapsible into ONE test function with N cases. Counts as 1 K-floor unit regardless of N. Prevents unbounded K-floor inflation as mode-count grows. Test count for 2b.8: `test_wanda_dispatch_wrapper.py` becomes 4 functions (3 SEAM + 1 parametrized Ã— 6 cases) collected as 9; K-floor units 25â†’20.
- **A-2b.8-R1:** Capabilityâ†’method mapping VERIFIED at story-author time. `WondercraftClient` exposes `check_connectivity / list_episodes / create_podcast / create_scripted_podcast / create_conversation_podcast / get_job_status / wait_for_job` only. **MB/CM/AH are non-client orchestrations** (compose state-machine logic over client outputs + script structure), NOT 1:1 client methods. Per-mode helpers pin to existing client methods where applicable + non-client orchestrations for the remainder.
- **A-2b.8-R2:** AH (audio_assembly_handoff) helper requires extraction â€” Descript sidecar + assembly-guide markdown rendering totals ~50-70 LOC. Solution: extract two private helpers `_emit_descript_sidecar` + `_render_assembly_guide` so AH dispatch helper stays â‰¤30 LOC orchestrating the two extractions. Total `wondercraft_dispatch.py` â‰¤ 310 LOC (raised from 270 to absorb the two extracted helpers).
- **A-2b.8-R3:** 4 pts holds CONDITIONAL on R2 acceptance; if R2 declined, bump to 5pts to absorb AH bloat.
- **A-2b.8-R4:** Capability/method/orchestration-role pin table in AC-B Given clause to prevent invention at T2.

Wanda routes Wondercraft API operations via `scripts/api_clients/wondercraft_client.py` (TOP-LEVEL substrate location, NOT under a skill subdir like Gary/Enrique). **REST-API tool-dispatch category** (Â§12.11 Gary parent). Inherits Enrique's per-mode helper extraction pattern (6 capabilities: EP/DP/AS/MB/CM/AH â†’ 6 mode helpers). Wanda adds ONE row to Â§12.12 inheritor catalog matrix under Â§12.11 (per R3). **Sanctum graceful-degrade** (BMB sanctum at `_bmad/memory/bmad-agent-wondercraft/` does NOT exist; verified 2026-04-25). **NEW SUBSTRATE LOCATION** â€” `scripts/api_clients/` is a top-level package with `__init__.py` (verified); allows direct package import (Gary 2b.1 + Tracy 2b.5 precedent). FIFTH or SIXTH importlib loader / direct-import occurrence depending on substrate side-effect verification at T1.

---

## T1 Readiness Block

Standing Pre-Flight items 1â€“11 same as 2b.7. TEMPLATE doc v2.1 R1â€“R12 + M-R16 amendment apply.

### Slab 2b artifact-existence sweep â€” Wanda-specific deltas

- **C** Reference patterns: Enrique 2b.7 (closest Â§12.11 inheritor; multi-mode dispatch fan-out per A-2b.7-R2); Gary 2b.1 (Â§12.11 origin + direct-package-import precedent for clean-substrate cases).
- **F** `pyproject.toml` C3 contains 12 rows pre-Wanda. Auto-emit makes 13.
- **G** Cache-hit-rate (FR54) per-script-prompts; defer to follow-on.
- **R2 importlib loader status:** depends on `wondercraft_client.py` substrate verification at T1. From verified import surface (`scripts/api_clients/__init__.py` exists; `wondercraft_client.py` imports from `scripts.api_clients.base_client`), direct package import via `from scripts.api_clients.wondercraft_client import WondercraftClient` SHOULD work cleanly. **Default at story-author time: direct package import** (Gary precedent for clean substrate). If T1 verification surfaces side effects, fall back to importlib.

### Epic-doc-vs-framework cross-check (per R6)

#### (a) Framework drifts

**Drift #1 â€” Skill-dir uses VENDOR/PRODUCT name (A11 EIGHTH example, sub-shape D):** `bmad-agent-wondercraft` (vendor name "wondercraft"); persona `Wanda`. Same sub-shape D as Enrique 2b.7 (vendor-name-vs-persona drift). 8th example bullet under sub-shape D.

**Drift #2 â€” NEW SUBSTRATE LOCATION (top-level `scripts/api_clients/`):** prior REST-API specialists (Gary Â§12.11 + Enrique 2b.7) wrap substrate at `skills/<skill-name>/scripts/`. Wanda's substrate at `scripts/api_clients/wondercraft_client.py` is at TOP-LEVEL repo (parallel to other api_clients: gamma_client.py, kling_client.py, elevenlabs_client.py, etc.). **NEW substrate-location drift class â€” file as A11 sub-shape E (substrate-location divergence) OR file as separate anti-pattern A14 (post-A12 RESOLVED).** Default at story-author time: file as A11 sub-shape E to keep harvest discipline tight; G6 may upgrade to A14 if Wondercraft is the first of many top-level-substrate specialists. Harvest at AC-J.

#### (b) TEMPLATE scope decisions

**Decision #1 â€” Bounded scope (per R1):** Wanda SKILL.md scopes (a) headless podcast production, (b) interactive voice-match exploration + cost-gated previews, (c) sanctum memory-persistence. Migration scope = headless dispatch path. Interactive + sidecar OOS. Borderline NO-trigger for R8 K-floor recalibration (only 2 categories OOS).

**Decision #2 â€” Direct package import for `wondercraft_client.py` (Gary precedent):** verified at story-author time â€” `scripts/__init__.py` + `scripts/api_clients/__init__.py` both exist; `wondercraft_client.py` imports cleanly from `scripts.api_clients.base_client` (no `load_dotenv` / `sys.path` mutation at module load â€” the `BaseAPIClient` reads env at instantiation, not import). **Direct package import is the default.** Verify substrate at T1 â€” if `BaseAPIClient` import has side effects (check `base_client.py:1-30`), fall back to importlib loader. Track loader-occurrence count per Decision #2-bis.

**Decision #2-bis â€” Multi-mode dispatch fan-out per A-2b.7-R2 (Quinn-R W-R1 inheritor pattern, EXTENDED to 6 modes):** Wanda has 6 capabilities (EP/DP/AS/MB/CM/AH). Factor following Enrique pattern: thin `_act` (â‰¤95 LOC) for orchestration + LLM mode-selection + receipt parse; `wondercraft_dispatch.py` mode-router shell (â‰¤80 LOC, larger than Enrique due to 6 vs 4 modes); six per-mode helpers `_dispatch_episode / _dispatch_dialogue / _dispatch_summary / _dispatch_music_bed / _dispatch_chapters / _dispatch_handoff` (â‰¤30 LOC each, in `wondercraft_dispatch.py`). Total module â‰¤ 270 LOC. 6 mode-helper smoke tests in `test_wanda_dispatch_wrapper.py` (one per capability).

**Decision #3 â€” Sanctum graceful-degrade per R5+R6+R11 cap:** parallel to Vera/Quinn-R/Tracy/Enrique. PERSONA.md sentinel skip with `DEFERRED-OPERATOR-WINDOW` marker. R11 cap fires for Wanda by 2026-05-25.

**Decision #4 â€” Path A confirmed (per slab-2-roster-reconciliation Â§Wondercraft Decision):** "Treat Wondercraft as a Category-A/B specialist. Node body + model cascade + scaffold-conformance. Generator validation in Slab 2c shifts to a different specialist." **Path A is the default and is confirmed at this story's authoring** (no party-mode escalation needed â€” operator can flag if Path B is preferred at green-light). Slab 2c.1's scope shifts to a different generator-validation subject (TBD per Slab 2c.1 spec author).

---

## Story

As a **migration dev agent inheriting TEMPLATE v2.1 R1â€“R12**,
I want **Wanda rehomed into `app/specialists/wanda/` with the 9-node scaffold + REST-API tool-dispatch act-body via `wondercraft_client` direct-package-import + 6-mode dispatch fan-out per A-2b.7-R2 pattern + per-R5 auto-emit C3 row + Â§12.12 inheritor row added under Â§12.11 + Path A absorption confirmed**,
So that **the Â§12.11 REST-API category gains its second inheritor (Gary â†’ Enrique â†’ Wanda), the multi-mode dispatch fan-out pattern from Enrique generalizes to 6 modes, the top-level `scripts/api_clients/` substrate location is documented as A11 sub-shape E, Slab 2c.1 is freed to validate the generator against a different specialist, and Slab 2b cadence holds**.

---

## Acceptance Criteria

All ACs are dev-agent-executable. Wanda carries ONE `@pytest.mark.llm_live` test.

### AC-2b.8-A â€” Generator emits Wanda + auto-emits C3 row (per R5)

Per R5. Test pin: `tests/specialists/wanda/test_wanda_generator_auto_emit_c3_row.py` â€” 3 tests (`temp_repo_root` fixture). Generator: `--name wanda --mcp none --expertise-tier L4-podcast-production --from-skill skills/bmad-agent-wondercraft`.

### AC-2b.8-B â€” Wanda `act` node wires REST-API tool-dispatch with 6-mode fan-out

Mirrors Enrique 2b.7 AC-B with 6-mode fan-out (vs Enrique's 4) + direct-package-import seam (vs Enrique's importlib).

- **Given** Wanda's `_act` (1) reads ModelResolutionEntry (Winston W2); (2) extracts script + capability (EP/DP/AS/MB/CM/AH) from envelope; (3) reads style_guide.yaml fresh; (4) invokes LLM (`tier_request: fast` â†’ `gpt-5-haiku`) for capability-mode selection + voice-continuity check; (5) dispatches via `app.specialists.wanda.wondercraft_dispatch.dispatch_to_wondercraft(script, capability, voice_id)` (mode-router shell calls one of 6 per-mode helpers per Decision #2-bis); (6) parses receipt via `_parse_audio_receipt` helper; (7) returns cache_state + `wanda_audio` reference.
- **Capability â†’ method/orchestration mapping pin per Amelia A-2b.8-R4 (BINDING â€” prevents method-name invention at T2):**

  | Capability | Helper | Client method(s) called | Orchestration role |
  |---|---|---|---|
  | EP (podcast_episode_produce) | `_dispatch_episode` | `create_scripted_podcast` + `wait_for_job` | Single-host monologue from script |
  | DP (podcast_dialogue_produce) | `_dispatch_dialogue` | `create_conversation_podcast` + `wait_for_job` | Multi-voice dialogue from structured script |
  | AS (audio_summary_produce) | `_dispatch_summary` | `create_scripted_podcast` (short-form variant) + `wait_for_job` | Short recap/summary |
  | MB (music_bed_apply) | `_dispatch_music_bed` | NONE (orchestration only) | Pre/post-process audio with music bed; no Wondercraft API call |
  | CM (chapter_markers_emit) | `_dispatch_chapters` | NONE (metadata derivation) | Derive chapter markers from script structure; emit metadata |
  | AH (audio_assembly_handoff) | `_dispatch_handoff` | NONE (Descript sidecar emission) | Build Descript-import JSON sidecar + render assembly-guide markdown; **uses extracted helpers `_emit_descript_sidecar` + `_render_assembly_guide` per A-2b.8-R2** to stay â‰¤30 LOC |
- **LOC budget per A-2b.7-R2 (extended to 6 modes) + A-2b.8-R2 (AH extraction):** `_act â‰¤ 95 LOC`; `wondercraft_dispatch.py` total â‰¤ 310 LOC composed of mode-router shell â‰¤80 LOC + six per-mode helpers â‰¤ 30 LOC each (180 LOC) + AH extraction helpers `_emit_descript_sidecar â‰¤ 30 LOC` + `_render_assembly_guide â‰¤ 35 LOC` (65 LOC) â€” total â‰¤ 305 LOC; `_parse_audio_receipt â‰¤ 40 LOC` separate file.
- **Tag namespace + R12 ceiling + A-2b.7-R3 secondary-tag pattern:** `audio.parsed.*` â€” primary tags `audio.parsed.ok / malformed / missing-key / wrong-type / empty / api-error`. **6 primary within R12 ceiling.** **`api-error` carries M-R8 dimension secondary-tag** for Wondercraft API: `audio.parsed.api-error.{rate-limit | payment-required | voice-not-found | server-error | other}`. Same precedence as Enrique.
- **SEAM tests per Murat M-R18 parametrize-collapsible (3 + 1 parametrized Ã— 6):** 3 SEAM tests (negative-import-pin no-subprocess; fixture short-circuit; direct-package-import smoke per T1 substrate verification confirming clean â€” `BaseAPIClient` reads env at instantiation only, NOT at module load); **1 parametrized helper smoke test** with 6 cases (one per capability EP/DP/AS/MB/CM/AH) â€” counts as 1 K-floor unit per M-R18 regardless of N. Total 4 test functions collected as 9 in `test_wanda_dispatch_wrapper.py`.
- **Live LLM test:** AC-B-LIVE asserts live `gpt-5-haiku` call produces structurally valid capability-selection output (capability key + voice_id + parameters) without invoking Wondercraft API.

### AC-2b.8-B-OP â€” Live operator-gated evidence (DEFERRED-PENDING-OPERATOR-WINDOW)

Operator runs Wanda with real Wondercraft API call (~$0.50/episode-preview; cost-gated per Wanda principle "cassettes are the default test surface; live-smoke happens only when the operator explicitly opts in"). Pastes audio file + chapter markers + voice_id into Completion Notes.

### AC-2b.8-C â€” Model cascade at `_plan` (per R7) â€” 2 tests
### AC-2b.8-D â€” Sanctum cold-read (graceful-degrade per R5+R6+R11 cap) â€” 3 tests, PERSONA.md sentinel + DEFERRED-OPERATOR-WINDOW marker
### AC-2b.8-E â€” Gate-decision binding (precedent-inherited) â€” 2 tests
### AC-2b.8-F â€” Resolution trail (FR16 eleventh per-specialist exercise) â€” 1 test
### AC-2b.8-G â€” Wanda shape-pin tests (per R4): `wanda_audio: dict[str, Any] | None` â€” 4 tests
### AC-2b.8-H â€” Scaffold-conformance test registered â€” 1 test

### AC-2b.8-I â€” Migration-guide Â§12.12 grows ONE inheritor row (per R3)

| Specialist | Parent Â§12.x | Seam divergence | Sanctum case | Harvest contributions | Story |
|---|---|---|---|---|---|
| Wanda | Â§12.11 (Gary REST-API tool-dispatch) | direct package import for `wondercraft_client` (top-level `scripts/api_clients/` substrate location â€” NEW sub-shape E in A11); 6-mode dispatch fan-out (vs Enrique's 4) | graceful-degrade (BMB sanctum unpopulated) | A11 8th example sub-shape D (vendor-name) + NEW sub-shape E (substrate-location) | 2b.8 |

### AC-2b.8-J â€” Anti-pattern catalog harvest

A11 8th example bullet under sub-shape D (vendor-name) + NEW sub-shape E (substrate-location at top-level `scripts/api_clients/` vs `skills/<skill-name>/scripts/`).

### AC-2b.8-K â€” TEMPLATE compliance â€” R1â€“R12 v2.1 honored

### AC-2b.8-L â€” D12 close protocol (single-gate; FOUR-line per A-R7)

1. **Invariant preservation:** Slab-1 substrate intact; auto-emit C3 row machinery fired (C3 12â†’13); Path A absorption confirmed (Wondercraft now under `app/specialists/wanda/`); Slab 2c.1 freed for different generator-validation subject.
2. **Anti-pattern harvest:** A11 8th example sub-shape D + NEW sub-shape E.
3. **Migration-guide update:** Â§12.12 inheritor row added under Â§12.11.
4. **TEMPLATE compliance:** R1â€“R12 v2.1 honored. Numeric anchors: `_act` â‰¤95; `wondercraft_dispatch` â‰¤270 (split: shell â‰¤80 + 6 helpers â‰¤30 each); 6 parse-branches with secondary-tag; 1 @llm_live; sanctum graceful-degrade with R11 cap; pyproject.toml 5â†’6 fixture / 12â†’13 live.

### AC-2b.8-M â€” Sprint-status state-flips at filing AND at close

At filing: ready-for-dev. At close: done. File `wanda-fr54-cache-hit-baseline-measurement` follow-on. Note in close: "Path A confirmed; Slab 2c.1 generator-validation target needs operator decision (TBD)."

---

## File Structure Requirements

```
app/specialists/wanda/
â”œâ”€â”€ __init__.py, graph.py, state.py, model_config.yaml
â”œâ”€â”€ wondercraft_dispatch.py                     # NEW (~270 LOC); mode-router + 6 per-mode helpers
â””â”€â”€ expertise/{README.md, __init__.py}

tests/specialists/wanda/
â”œâ”€â”€ __init__.py
â”œâ”€â”€ test_wanda_generator_auto_emit_c3_row.py    # 3 tests
â”œâ”€â”€ test_wanda_act_node_dispatch.py             # ~8 tests (6 parse-branches + 1 happy + 1 @llm_live)
â”œâ”€â”€ test_wanda_dispatch_wrapper.py              # 4 functions collected as 9 per M-R18: 3 SEAM + 1 parametrized Ã— 6 capability cases
â”œâ”€â”€ test_wanda_model_cascade.py                 # 2 tests
â”œâ”€â”€ test_wanda_sanctum_cold_read.py             # 3 tests
â”œâ”€â”€ test_wanda_gate_decision_binding.py         # 2 tests
â”œâ”€â”€ test_wanda_resolution_trail.py              # 1 test
â””â”€â”€ test_wanda_state_shape.py                   # 4 tests

tests/integration/scaffold_conformance/
â””â”€â”€ test_scaffold_wanda.py                      # 1 test
```

### MODIFIED files

- `docs/dev-guide/langgraph-migration-guide.md` â€” Â§12.12 new row.
- `docs/dev-guide/specialist-anti-patterns.md` â€” A11 8th example bullet sub-shape D + NEW sub-shape E.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` â€” per AC-M.
- `pyproject.toml` â€” auto-emitted.

---

## Testing Requirements

**K-target ~1.4Ã— (target 14 / floor 11) â€” RECALIBRATED per Murat M-R18.** Test count: 3 + 8 + 4_functions(9_collected) + 2 + 3 + 2 + 1 + 4 + 1 = **28 collectible test functions** (33 collected including parametrize cases); ~20 K-floor units after parametrize-collapse. Effective ratio ~1.82Ã— floor / ~1.43Ã— target.

**Regression target at T8:** â‰¥248 passed / â‰¥5 skipped placeholder-key.

---

## Dev Agent Record

_(Populated during T1â€“T9.)_


### T8 Regression Evidence

- Specialist-wave slice validation: 184 passed / 1 skipped across cd/enrique/wanda/kim/vyx/aria/mira/tamara + scaffold conformance.
- Specialists + scaffold conformance anchor: 525 passed / 7 skipped.
- uff check clean on touched specialist/test paths.
- lint-imports 3/3 kept.
- Sandbox-AC validator PASS for stories 2b.6-2b.13.

