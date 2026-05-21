# Migration Story 2b.9: Migrate Kim (CourseArc Specialist) to 9-Node Scaffold â€” establishes NEW operator-instructions thin-node category Â§12.13

**Status:** done
**Sprint key:** `migration-2b-9-kim-coursearc-scaffold-migration`
**Epic:** Slab 2b â€” ninth per-specialist migration; **establishes NEW FIFTH specialist-shape category: operator-instructions thin node** (after narration Â§12.5 / LLM+tool-dispatch Â§12.6 / pure-tool-dispatch Â§12.7 / REST-API-tool-dispatch Â§12.11 / **operator-instructions Â§12.13 NEW**). Inherits R3 cascade rule: category-novel specialist adds new Â§12.x worked example; subsequent Category-C inheritors (Vyond/Articulate/Midjourney/Canva at 2b.10-2b.13) add ONE row each to Â§12.12 inheritor catalog matrix under Â§12.13 parent.
**Pts:** 3 (TEMPLATE-establishing for new category + modest implementation surface; NO dispatch wrapper, NO LLM call at runtime, NO sanctum first-breath needed) | **Gate:** single. **K-target:** ~1.4Ã— (target 11 / floor 8 â€” RECALIBRATED per Murat M-R11/R8 because category-novel BUT also has 2 substrate categories OOS â€” interactive + sidecar â€” borderline; declared YES-trigger for R8 since the category-establishing surface isn't test-heavy).

**3-agent party-mode amendments applied 2026-04-25 (Winston + Murat + Amelia):** 8 RIDERs integrated:
- **W-R7:** Architectural pin against Marcus-helper extraction â€” added to AC-K. Kim's residency in `app/specialists/kim/` is load-bearing for FR16 trail uniformity + Slab-2 scaffold-survivability claim.
- **W-R8 (codify in TEMPLATE v2.3):** R8 trigger taxonomy â€” TWO independent conditions: (a) â‰¥2 substrate categories OOS (Tracy precedent); (b) category-novel + structurally lighter act-body than prior categories (Kim precedent). Either alone sufficient.
- **W-R9 (codify in TEMPLATE v2.3 + slab-2-roster-reconciliation):** Midjourney pre-classification at 2b.12 â€” default Option A (Category C operator-instructions inheritor with API-stub OOS to Slab-3 follow-on) to preserve "one inheritor â†’ one parent" matrix invariant. Hybrid Option B requires structural matrix change.
- **M-R19:** `template-resolution-failed` carries M-R8 dimension secondary-tag â€” `instructions.parsed.template-resolution-failed.{unknown-workflow | template-malformed | registry-empty | other}`. Primary stays at 6 (R12-clean).
- **M-R20 (codify in TEMPLATE v2.3):** Inheritor K-floor cap â€” inheritors of Â§12.13 target K-floor â‰¤ 13 (Kim's floor 8 + â‰¤5 substrate-specific tests per inheritor). Document in Â§12.12 inheritor catalog row header. Prevents pad-creep across 2b.10-2b.13.
- **M-R21:** `template-resolution-failed` vs `missing-key` discriminator pin â€” `missing-key` = key absent from envelope dict; `template-resolution-failed` = key present + structurally-typed-correct + value non-empty BUT `registry.lookup(target_workflow)` returns None/KeyError. Add parametrize precedence case.
- **A-2b.9-R1:** Pin template format = `str.format` + named keys; map `KeyError` â†’ `instructions.parsed.template-resolution-failed`.
- **A-2b.9-R2:** Pin capability registry baseline at `app/specialists/kim/expertise/capability_registry.yaml` (module-shipped); sanctum override at `_bmad/memory/bmad-agent-kim/references/capability-registry.yaml` when populated.

Kim produces deterministic CourseArc deployment checklists for human execution. **No external dispatch substrate**, **no LLM call at the specialist layer at runtime** (envelope-in carries course/module/scope; instructions assembled from template + envelope values; deterministic per Kim SKILL.md "Manual-tool only: CourseArc is treated as LTI/SCORM workflow guidance, not API runtime"). Trail-entry at `_plan` per R7 still mandatory (FR16 contract uniformity). Kim adds NEW Â§12.13 worked example AND opens the operator-instructions inheritor catalog row in Â§12.12 for Vyond/Articulate/Midjourney/Canva downstream.

---

## T1 Readiness Block

Standing Pre-Flight items 1â€“11 same as 2b.8. TEMPLATE doc v2.2 R1â€“R12 + M-R16/M-R18 amendments apply.

### Slab 2b artifact-existence sweep â€” Kim-specific deltas

- **C** Reference patterns: Texas 2a.4 (closest precedent for "no LLM at specialist layer" â€” Texas trail-entry at `_plan` without invoking; Kim follows same R7 pattern). NO direct precedent for operator-instructions (Kim establishes the category at Â§12.13).
- **F** `pyproject.toml` C3 contains 13 rows pre-Kim. Auto-emit makes 14.
- **G** Cache-hit-rate (FR54) NOT applicable at Kim layer â€” no LLM prefix to cache. Same disposition as Texas/Gary/Enrique pure-tool-dispatch.
- **R2 importlib loader status:** UNCHANGED â€” Kim has NO dispatch wrapper.

### Epic-doc-vs-framework cross-check (per R6)

#### (a) Framework drifts

**Drift #1 â€” Skill-dir uses VENDOR name + persona divergence (A11 NINTH example, sub-shape D):** `bmad-agent-coursearc` (vendor name); persona `Kim`. Same sub-shape D as Enrique/Wanda. 9th example bullet under sub-shape D. NO retitle trigger (sub-shape already present in catalog).

#### (b) TEMPLATE scope decisions

**Decision #1 â€” Bounded scope (per R1):** Kim SKILL.md scopes (a) headless deterministic-checklist generation, (b) interactive guidance/consultation, (c) sidecar memory persistence. Migration scope = headless deterministic dispatch. Interactive + sidecar OOS. **R8 K-floor recalibration TRIGGERED** (â‰¥2 categories OOS) â€” target 11/floor 8 vs default 13/10.

**Decision #2 â€” NEW CATEGORY: operator-instructions thin node (Â§12.13):** Kim is the FIRST operator-instructions thin node â€” no external dispatch substrate, no LLM call at the specialist layer at runtime, deterministic instruction assembly from envelope + template. Distinct from prior four categories:
- vs Â§12.5 narration (Irene/Desmond/CD): no LLM call at `_act`
- vs Â§12.6 LLM+tool-dispatch (Kira/Vera/Quinn-R/Tracy): no LLM, no dispatch
- vs Â§12.7 pure-tool-dispatch (Texas): no dispatch substrate
- vs Â§12.11 REST-API tool-dispatch (Gary/Enrique/Wanda): no API call

**Â§12.13 worked example structure** mirrors Â§12.5/Â§12.6/Â§12.7/Â§12.11 shape: before-state in skill / after-state in app/specialists/kim/ / divergences-from-Texas table (closest precedent â€” both NO-LLM-at-specialist-layer, but Texas dispatches subprocess where Kim does NOT). Inheritor pattern: Vyond (2b.10), Articulate (2b.11), Midjourney (2b.12), Canva (2b.13) add ONE row each to Â§12.12 under Â§12.13 parent.

**Decision #3 â€” NO LLM at `_act` per Kim "deterministic" principle:** instruction template assembly from envelope `{course, module, scope, target_workflow}` values + capability registry per Kim references. Trail-entry at `_plan` per R7 still mandatory (FR16) â€” `make_chat_model(specialist_id="kim", tier_request="fast")` resolves trail entry; chat handle never invoked at `_act`. Documented in `model_config.yaml` inline comments per Texas precedent.

**Decision #4 â€” Sanctum graceful-degrade (BMB sanctum absent at story-author time):** standard graceful-degrade per R5+R6+R11 cap.

---

## Story

As a **migration dev agent inheriting TEMPLATE v2.2 R1â€“R12**,
I want **Kim (CourseArc specialist) rehomed into `app/specialists/kim/` with the 9-node scaffold + operator-instructions thin-node act-body (NO dispatch substrate, NO LLM at `_act`, deterministic checklist assembly) + per-R5 auto-emit C3 row + NEW Â§12.13 worked example establishing operator-instructions category for Vyond/Articulate/Midjourney/Canva inheritors**,
So that **the FIFTH specialist-shape category lands cleanly on the same 9-node scaffold (proving cross-category survivability extends from four to five), the Â§12.13 inheritor pattern is set for 4 inheritor stories at 2b.10-2b.13, and Slab 2b cadence absorbs operator-instructions specialists**.

---

## Acceptance Criteria

All ACs are dev-agent-executable. Kim does NOT carry any `@pytest.mark.llm_live` test (no LLM invocation at the specialist layer).

### AC-2b.9-A â€” Generator emits Kim + auto-emits C3 row (per R5)

Per R5. Test pin: 3 tests using `temp_repo_root` fixture. Generator: `--name kim --mcp none --expertise-tier L4-coursearc-deployment --from-skill skills/bmad-agent-coursearc`.

### AC-2b.9-B â€” Kim `act` node wires DETERMINISTIC operator-instructions assembly (NEW category Â§12.13)

- **Given** Kim's `_act` (1) reads ModelResolutionEntry (Winston W2 â€” applies even though no LLM invoked at `_act`, per R7); (2) extracts envelope `{course, module, scope, target_workflow}` from `state.cache_state.cache_prefix`; (3) reads CourseArc capability registry from sanctum (or graceful-degrade to baseline templates if sanctum absent); (4) assembles deterministic checklist via `_assemble_checklist(envelope, registry)` helper (string-template formatting â€” no LLM call); (5) returns cache_state with `kim_checklist` encoded as sorted-keys canonical JSON.
- **When** the dev agent implements `_act` per the operator-instructions deterministic pattern.
- **Then** invoking `build_kim_graph()` with fixture envelope produces non-empty result containing `kim_checklist` (status + recommended_workflow + steps array).
- **NO `@pytest.mark.llm_live` marker** (no LLM call at Kim layer); test runs unconditionally on placeholder OPENAI_API_KEY.
- **LOC budget:** `_act â‰¤ 80 LOC` (lower than narration ceiling of 115 â€” no LLM call simplifies orchestration); `_assemble_checklist â‰¤ 60 LOC` (string-template assembly).
- **Tag namespace per Murat M-R2 + R12 ceiling + M-R19 secondary-tag + M-R21 discriminator pin:** `instructions.parsed.*` â€” primary tags `instructions.parsed.ok / malformed-envelope / missing-key / wrong-type / empty / template-resolution-failed`. **6 primary tags within R12 ceiling.** **`template-resolution-failed` carries M-R19 dimension secondary-tag:** `instructions.parsed.template-resolution-failed.{unknown-workflow | template-malformed | registry-empty | other}` (operator triage axis). R9 precedence: `malformed-envelope â†’ missing-key â†’ wrong-type â†’ empty â†’ template-resolution-failed â†’ ok`. **M-R21 discriminator pin (BINDING):** `missing-key` = required key (`course / module / scope / target_workflow`) absent from envelope dict (`key in envelope` â†’ False); `template-resolution-failed` = envelope structurally complete (all keys present, types correct, values non-empty) BUT `registry.lookup(envelope["target_workflow"])` returns None/KeyError. Add parametrize precedence case: envelope with `target_workflow="nonexistent_workflow"` â†’ MUST fire `template-resolution-failed`, NOT `missing-key`. Without pin, dev agent will conflate "missing template for present key" with "missing key" â†’ R9 violation.
- **Template format pin per Amelia A-2b.9-R1 (BINDING):** `_assemble_checklist` uses **`str.format(**envelope_safe_keys)`** + named keys (stdlib only â€” Jinja2 adds runtime dep + import-linter surface; f-string requires `eval` for dynamic templates which is rejected; `string.Template` is too thin for nested keys). **`KeyError` mapped to `instructions.parsed.template-resolution-failed.{unknown-workflow|template-malformed|other}` tag** per M-R19 secondary-tag axis. Document in `_assemble_checklist` docstring.
- **NO live LLM test** â€” Kim's deterministic-output property is proven by happy-path + parse-branch tests alone.

### AC-2b.9-C â€” Model cascade at `_plan` per R7 (trail entry only; no LLM invocation at `_act`)

Trail-entry resolution at `_plan` MANDATORY per R7 even though Kim does NOT invoke LLM at `_act`. Documented in `model_config.yaml` inline comments per Texas precedent: "Kim is operator-instructions thin node â€” no LLM invoked at the specialist layer. Resolution-trail entry recorded at `_plan` per FR16; chat handle never invoked at `_act`. Tier maps to `fast`/`gpt-5-haiku` for trail-entry shape consistency across the specialist roster."

Test pins (2 tests): default + override.

### AC-2b.9-D â€” Sanctum cold-read (graceful-degrade per R5+R6+R11 cap)

3 tests. PERSONA.md sentinel skip with `DEFERRED-OPERATOR-WINDOW` marker. R11 cap fires by 2026-05-25.

### AC-2b.9-E â€” Gate-decision binding (precedent-inherited)

2 tests.

### AC-2b.9-F â€” Resolution trail (FR16 twelfth per-specialist exercise; first NO-LLM-at-act-since-Texas)

1 test.

### AC-2b.9-G â€” Kim shape-pin tests (per R4)

`kim_checklist: dict[str, Any] | None` (status + recommended_workflow + steps array per Kim Return Contract). 4 tests.

### AC-2b.9-H â€” Scaffold-conformance test registered

1 test.

### AC-2b.9-I â€” Migration-guide Â§12 grows Â§12.13 NEW operator-instructions worked example + cascade-renumber + Â§12.12 inheritor catalog row

Per R3, Kim is **category-novel** (FIFTH category) â†’ adds NEW Â§12.x. Cascade-renumber: Verification commands (current Â§12.13) â†’ Â§12.14; Governance notes (current Â§12.14) â†’ Â§12.15; (any subsequent slab-retrospectives shift). NEW order:
- Â§12.5 Irene narration
- Â§12.6 Kira LLM+tool-dispatch
- Â§12.7 Texas pure-tool-dispatch
- Â§12.10 Slab 2a retrospective (unchanged)
- Â§12.11 Gary REST-API tool-dispatch
- Â§12.12 Inheritor catalog matrix (NEW row added: Kim under Â§12.13)
- **Â§12.13 Kim operator-instructions thin node (NEW)**
- Â§12.14 Verification commands (was Â§12.13)
- Â§12.15 Governance notes (was Â§12.14)

Â§12.13 structure mirrors Â§12.7 Texas (closest precedent â€” both NO-LLM-at-specialist-layer; Texas section template is the cleanest reference). Divergences-from-Texas table cells: dispatch substrate (NONE vs subprocess); LLM-at-`_act` (NO vs NO â€” same); operator-instruction artifact (checklist+steps vs retrieval-bundle); no parse-branch parity since Kim parses envelope (5 cases) where Texas parses bundle (8 cases).

Â§12.5 framing sentence updated: "twelfth specialist proven on 9-node scaffold; FIVE established categories â€” narration / LLM+tool-dispatch / pure-tool-dispatch / REST-API-tool-dispatch / operator-instructions; inheritors of the new operator-instructions category are catalogued at Â§12.12 (Vyond/Articulate/Midjourney/Canva at 2b.10-2b.13)."

Â§12.12 NEW row added at Kim landing:

| Specialist | Parent Â§12.x | Seam divergence | Sanctum case | Harvest contributions | Story |
|---|---|---|---|---|---|
| Kim (CourseArc) | Â§12.13 (operator-instructions) | NO dispatch substrate; deterministic checklist assembly via string-template formatting | graceful-degrade (BMB sanctum unpopulated) | A11 9th example sub-shape D | 2b.9 |

### AC-2b.9-J â€” Anti-pattern catalog harvest

A11 9th example bullet under sub-shape D. NO new top-level entries.

### AC-2b.9-K â€” TEMPLATE compliance (per R1â€“R12 v2.2 + W-R7 architectural pin)

R1â€“R12 v2.2 honored. **Documented decision (R8 trigger â€” both Winston W-R8 conditions stack on Kim):** (a) Kim has 2 substrate categories OOS (interactive + sidecar) qualifying for R8 K-floor recalibration per Tracy precedent; (b) Kim is category-novel + structurally lighter act-body than prior categories (no LLM, no dispatch â€” Kim precedent for W-R8 condition (b)). Either condition alone sufficient; Kim hits both. **NEW category Â§12.13 lands** per R3 cascade rule.

**Winston W-R7 architectural pin (BINDING):** *"Kim's residency in `app/specialists/kim/` as a 9-node specialist (rather than a Marcus-side template helper) is architecturally load-bearing for FR16 trail uniformity and the Slab-2 scaffold-survivability claim. Future refactor proposals to extract Kim to a Marcus helper require Slab-3 architect consensus and a counter-proof against the trail-uniformity invariant."*

**Winston W-R9 Midjourney pre-classification (BINDING for downstream 2b.12):** Midjourney is pre-classified as **Option A** â€” Category C operator-instructions inheritor with API-stub OOS to Slab-3 follow-on. Preserves "one inheritor â†’ one parent" matrix invariant in Â§12.12. Hybrid Option B (operator-instructions PRIMARY + REST-API SECONDARY) requires structural matrix change (column for "primary parent / secondary parent") and is NOT in 2b.12-author authority. File `midjourney-api-stub-slab-3-followon` in deferred-inventory at 2b.9 close (not 2b.12 â€” gate ahead of inheritor authoring).

### AC-2b.9-L â€” D12 close protocol (single-gate; FOUR-line per A-R7)

1. **Invariant preservation:** Slab-1 substrate intact; auto-emit C3 row machinery fired (C3 13â†’14); FIFTH specialist-shape category lands cleanly; FR54 substrate intact (Kim doesn't generalize FR54 â€” no LLM at specialist layer).
2. **Anti-pattern harvest:** A11 9th example sub-shape D.
3. **Migration-guide update:** Â§12.13 NEW worked example added per AC-I; cascade-renumber applied; Â§12.12 inheritor row added; Â§12.5 framing updated.
4. **TEMPLATE compliance:** R1â€“R12 v2.2 honored; R3 cascade rule fires (NEW Â§12.13). Numeric anchors: `_act` LOC â‰¤80 (lower than narration ceiling); `_assemble_checklist` LOC â‰¤60; 6 parse-branches; ZERO @llm_live tests; sanctum graceful-degrade with R11 cap; pyproject.toml 5â†’6 fixture / 13â†’14 live.

### AC-2b.9-M â€” Sprint-status state-flips + follow-on filings at close

At filing: ready-for-dev. At close: done. Follow-ons filed at close:
1. **`midjourney-api-stub-slab-3-followon`** per Winston W-R9 â€” pre-classification of Midjourney's API-stub as Slab-3 deferred work; ahead of 2b.12 author. Fire-trigger: Slab-3 architectural opens.
2. **Â§12.12 inheritor catalog header annotation** per Murat M-R20 â€” document inheritor K-floor cap (â‰¤13 for Â§12.13 inheritors) at the matrix row header so Vyond/Articulate/Midjourney/Canva spec-authors at 2b.10-2b.13 inherit the cap automatically.

Close note: "FIFTH specialist-shape category established; Vyond/Articulate/Midjourney/Canva at 2b.10-2b.13 inherit pattern with K-floor cap â‰¤13 per M-R20; Midjourney pre-classified as Option A per W-R9."

---

## File Structure Requirements

```
app/specialists/kim/
â”œâ”€â”€ __init__.py, graph.py, state.py, model_config.yaml
â”œâ”€â”€ checklist_assembly.py                       # NEW (~60 LOC); str.format + named keys per A-2b.9-R1; KeyError â†’ template-resolution-failed tag
â”œâ”€â”€ expertise/
â”‚   â”œâ”€â”€ README.md
â”‚   â”œâ”€â”€ __init__.py
â”‚   â””â”€â”€ capability_registry.yaml                # NEW per A-2b.9-R2; baseline registry keyed by target_workflow â†’ {recommended_workflow, steps_template[], compliance_template[], evidence_template[]}; sanctum override at _bmad/memory/bmad-agent-kim/references/capability-registry.yaml when populated

# NO dispatch wrapper module â€” Kim is deterministic-thin-node

tests/specialists/kim/
â”œâ”€â”€ __init__.py
â”œâ”€â”€ test_kim_generator_auto_emit_c3_row.py      # 3 tests
â”œâ”€â”€ test_kim_act_node_assembly.py               # ~7 tests (6 parse-branches + 1 happy-path; NO @llm_live)
â”œâ”€â”€ test_kim_model_cascade.py                   # 2 tests
â”œâ”€â”€ test_kim_sanctum_cold_read.py               # 3 tests
â”œâ”€â”€ test_kim_gate_decision_binding.py           # 2 tests
â”œâ”€â”€ test_kim_resolution_trail.py                # 1 test
â””â”€â”€ test_kim_state_shape.py                     # 4 tests

tests/integration/scaffold_conformance/
â””â”€â”€ test_scaffold_kim.py                        # 1 test
```

### MODIFIED files

- `docs/dev-guide/langgraph-migration-guide.md` â€” Â§12.13 NEW + cascade-renumber + Â§12.5 framing + Â§12.12 row.
- `docs/dev-guide/specialist-anti-patterns.md` â€” A11 9th example bullet sub-shape D.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` â€” per AC-M.
- `pyproject.toml` â€” auto-emitted.

---

## Testing Requirements

**K-target ~1.4Ã— (target 11 / floor 8) â€” RECALIBRATED per R8.** Test count: 3 + 7 + 2 + 3 + 2 + 1 + 4 + 1 = **23 collectible**; ~16 K-floor units. Effective ratio ~2.0Ã— floor / ~1.45Ã— target.

**Regression target at T8:** â‰¥255 passed / â‰¥6 skipped placeholder-key. Import-linter 3/3 KEPT; Ruff clean; Sandbox-AC PASS.

---

## Dev Agent Record

_(Populated during T1â€“T9.)_


### T8 Regression Evidence

- Specialist-wave slice validation: 184 passed / 1 skipped across cd/enrique/wanda/kim/vyx/aria/mira/tamara + scaffold conformance.
- Specialists + scaffold conformance anchor: 525 passed / 7 skipped.
- uff check clean on touched specialist/test paths.
- lint-imports 3/3 kept.
- Sandbox-AC validator PASS for stories 2b.6-2b.13.

