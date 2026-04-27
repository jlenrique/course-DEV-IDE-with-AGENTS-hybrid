# Specialist Migration TEMPLATE â€” Decisions for Slab 2b inheritor stories

**Version:** 2.4 (2026-04-25 - slab-close governance bump: codified M-R22 advisory, M-R24 advisory, and Paige section 12.10 retrospective-container restructure; consensus ratified in slab-close party-mode.)
**Authority:** This document is the canonical reference for **how a Slab-2b per-specialist migration story is shaped**. It exists so that 2b.2â€“2b.14 inheritor stories do not have to re-derive the per-specialist migration pattern from the 2b.1 spec body. **Updates to the rules require party-mode consensus + a version bump in the header table** (mirrors `specialist-anti-patterns.md` format-freeze pattern).
**Origin story:** `_bmad-output/implementation-artifacts/migration-2b-1-gary-scaffold-migration.md` (rules first written + validated against Gary's migration). The numeric anchors below are the post-execution evidence Gary's run produces; inheritor stories cite these as concrete benchmarks, not just rules.

**Migration-complete note:** Slab 1-5a complete 2026-04-26 per M5
`SHIP-CONDITIONAL` verdict; v2.4 R1-R14 carried through ship; future migration
extensions follow this TEMPLATE per PRD Â§Future Work.

> **You-are-here** (Slab 2b dev-agent reading order at T1):
> 1. [`scaffold-conformance-framework.md`](scaffold-conformance-framework.md) â€” 9-node canonical contract + T1 pre-flight
> 2. [`langgraph-state-idioms.md`](langgraph-state-idioms.md) â€” state-shape idioms (interrupt, Command, Send, reducers)
> 3. [`model-selection-guide.md`](model-selection-guide.md) â€” three-level cascade
> 4. [`sanctum-reference-conventions.md`](sanctum-reference-conventions.md) â€” sanctum / sidecar conventions (BMB direct-dir vs SKILL.md sidecar)
> 5. [`specialist-anti-patterns.md`](specialist-anti-patterns.md) â€” known traps (read before writing ACs)
> 6. **This document** â€” TEMPLATE rules for per-specialist migrations (read before authoring 2b.x story spec)

## Format

Each rule below carries: **Rule**, **Why**, **How to apply**, and (where applicable) **Evidence anchor from 2b.1 Gary run** so inheritor stories have concrete numeric / file-path benchmarks rather than abstract guidance.

---

## R1. Bounded scope: migrate the headless dispatch path; defer LLM-at-plan to per-specialist enhancement stories

**Rule.** A per-specialist 2b.x migration covers ONLY the headless dispatch path (the runtime act-body category Marcus invokes). LLM-mediated parameter recommendation, quality assessment, exemplar study, or any other LLM-using SKILL.md capabilities are OUT OF SCOPE for the migration story unless the specialist materially needs them at the runtime layer. Filed as separate per-specialist enhancement stories only when a concrete need surfaces.

**Why.** Bolting LLM-at-plan onto the headless dispatch path conflates two seams (runtime dispatch + plan-time intelligence) and forces every inheritor to make the same scope-decision case-by-case. The trail-entry-at-`_plan`-with-no-invocation pattern (mirroring Texas) keeps FR16 contract-shape uniform across all four categories. Architectural property worth preserving is **category-shape consistency across the 9-node scaffold**, not feature parity with each specialist's full SKILL.md.

**How to apply.** At T1, list the specialist's SKILL.md capabilities (PR/QA/ES/etc.). Identify the runtime dispatch path (what does Marcus actually call when delegating). Migrate only that. Document any deferred capability in the spec's "TEMPLATE scope decisions" sub-subsection of T1 Readiness (NOT in the framework-drift subsection â€” see R6).

**Evidence anchor from 2b.1 Gary run.** Gary's SKILL.md lists 10 capabilities (PR / SG / QA / ES / CT / VC / TP / SP / SM / ENV); the 2b.1 migration covers only the headless dispatch path (pure REST-API tool-dispatch via `gamma_operations.execute_generation`). The other 9 capabilities are preserved as the SKILL.md's interactive surface, deferred to per-specialist enhancement stories filed only when materially needed.

---

## R2. Dispatch-wrapper seam-category divergence â€” extraction at "third occurrence of SAME seam category"

**Rule.** Specialists that dispatch to external tools fall into one of these seam categories: subprocess (Kira/Texas), REST-API (Gary), or future MCP-tool (Slab-3 forward-looking). Each seam category has its own dispatch-wrapper shape. **A wrapper template is extracted from the per-specialist code only at the THIRD occurrence of the SAME seam category** â€” not earlier, even when the second occurrence "looks like" it would benefit from extraction.

**Why.** Premature factoring on a 2-instance pattern is the exact mistake Slab 2a was right to defer (see slab-2a-retrospective Â§"Dispatch-wrapper extraction candidate"). Two instances may share surface structure but diverge under load when the third specialist surfaces (e.g., timeout-policy, retry-policy, session-management semantics differ between subprocess + REST-API + MCP-tool). Wait for the third occurrence to extract; the third instance is the evidence threshold that the pattern actually generalizes.

**How to apply.** At T1 of each 2b.x spec, identify the dispatch seam category. If it's the third occurrence of an existing category, file a cross-cutting wrapper-extraction story (NOT scope creep into the per-specialist migration). If it's the first or second of any category, inline-author the wrapper modeled on the closest precedent.

**Evidence anchor from 2b.1 Gary run.** Gary is the FIRST REST-API category occurrence. Subprocess category has Kira (1st) + Texas (2nd) â€” extraction owed at the third subprocess occurrence (e.g., another video/audio specialist later in 2b). REST-API category has Gary (1st) â€” extraction owed at the third REST-API occurrence (which may be many specialists away, given REST-API is uncommon in the current roster).

---

## R3. Â§12 cascade rule: category-novel adds Â§12.x; pure inheritors catalog at Â§12.12

**Rule.** Subsequent 2b.x specialists that fall into one of the FOUR established act-body categories (narration / LLM+tool-dispatch / pure-tool-dispatch / REST-API-tool-dispatch) DO NOT add their own Â§12.x worked-example subsection in `langgraph-migration-guide.md`. Instead they get a one-line entry in **Â§12.12 Inheritor catalog matrix** (single table: `Specialist | Parent Â§12.x | Seam divergence | Sanctum case | Harvest contributions`). Only category-novel specialists (a fifth or further shape) add new Â§12.x.

**Why.** Without this rule, Â§12 grows to 14+ near-identical worked examples â€” unreadable. The matrix gives readers a single-section lookup ("who inherits what") while keeping worked-example bodies clean. Forward-pointers from each Â§12.x to Â§12.12 preserve locality.

**How to apply.** At T1, identify the parent Â§12.x. Add one row to Â§12.12 (NOT a new Â§12.x section). At each Â§12.x worked example bottom, add or update the forward-pointer "Inheritors of this category catalogued at Â§12.12."

**Evidence anchor from 2b.1 Gary run.** Â§12.11 Gary REST-API category added (category-novel; fourth shape after Slab 2a's three). Â§12.12 inheritor-catalog matrix structure established. Future 2b.2-2b.14 specialists add ONE row to Â§12.12, not a new Â§12.x.

---

## R4. State-shape extension: at most one new field per specialist, loose-typed

**Rule.** Each per-specialist `XxxReturn` shape adds AT MOST ONE new field. The field is loose-typed (`list[dict[str, Any]] | None` or `str | None` or similar). Strict-typing of the per-domain payload schema is owed at Story 2b.15 dispatch-contract-hardening, NOT in the per-specialist migration story.

**Why.** Strict-typing during per-specialist migrations forces each specialist to invent a schema that 2b.15 will then have to reconcile across all 17 specialists. Better to land all 14 loose-typed extensions, then tighten in one consolidated story where cross-specialist patterns are visible. `extra="forbid"` on parent classes still red-rejects unknown keys, so loose-typing is bounded to known-named fields.

**How to apply.** Identify the one field the specialist's SKILL.md outbound contract names (per Marcus delegation surface). Add it to `XxxReturn` as `field_name: <loose_type> | None = None` with `Field(default=None, description="...")`. Document Resolution-B rationale in the state.py docstring.

**Risk worth naming in the spec.** If 2b.15 slips, the loose-typing accumulates and 2b.x â†’ 2c migration carries 14 untyped fields into production. 2b.15 must be named in deferred-inventory with hard reactivation gating ("opens immediately on 2b.14 close") to convert soft-defer into hard sequencing constraint.

**Evidence anchor from 2b.1 Gary run.** `gary_slide_output: list[dict[str, Any]] | None = None` added to `GaryReturn`. Pydantic v2 with `validate_assignment=True` + `extra="forbid"` accepts cleanly.

---

## R5. Auto-emit C3 verification: positive regression test in every 2b.x story

**Rule.** Every 2b.x story includes a positive regression test that proves the Story-2a.5 generator auto-emit machinery fired correctly for the specialist (no manual `pyproject.toml` edits anywhere). The test runs against a synthetic temp-repo fixture (NOT live `pyproject.toml`) for hermetic order-independence across all inheritor stories.

**Why.** A 2a.5 silent regression that breaks auto-emit would go undetected for 13 specialists if not caught at every story. Live-repo `pyproject.toml` reads are order-sensitive and create vacuous-skip risk across inheritors (e.g., Story 2b.2's test, copy-pasted from 2b.1, would skip if Gary's row is already present pre-run).

**How to apply.** Use the `temp_repo_root` fixture pattern at `tests/specialists/generator/conftest.py` (synthetic `pyproject.toml` with known 5-row C3 baseline). Run the generator against the temp repo root; assert pre/post counts against the fixture's baseline. The live-repo check, if needed, becomes a one-time T1 sanity assertion in the workflow (recorded in Dev Agent Record), NOT a `pytest`-collected test.

**Evidence anchor from 2b.1 Gary run.** `tests/specialists/gary/test_gary_generator_auto_emit_c3_row.py` uses `temp_repo_root` fixture; pre-baseline = 5, post-emit = 6, with `app.specialists.gary.graph -> app.gates.resume_api` row + comment marker.

---

## R6. Anti-pattern harvest-gate continues: at every 2b.x T1, run epic-doc-vs-framework cross-check

**Rule.** At every 2b.x T1, run the epic-doc-vs-framework cross-check (the standing protocol from Slab 2a). Flag any drifts. Harvest as augmented bullets under the existing A9/A10/A11/A12 entries unless party-mode-ratified novel pattern surfaces (then file a new entry per `specialist-anti-patterns.md` "How to add an entry"). T1 Readiness section MUST split drift-vs-scope discipline into two sub-subsections:

- **Sub-subsection (a) Framework drifts (harvest as anti-pattern bullets)** â€” drifts where epic prose drifted from runtime reality; framework wins; harvest into anti-pattern catalog.
- **Sub-subsection (b) TEMPLATE scope decisions (codify in this document)** â€” deliberate scope choices the story author makes (e.g., bounded-scope per R1); NOT drifts; NOT harvested into anti-pattern catalog.

**Why.** Conflating framework drifts with deliberate scope decisions in the same "drifts" section muddies the harvest discipline. A future 2b.x dev agent following the standing protocol will see "N drifts flagged" and try to harvest all of them â€” but scope decisions don't belong in the catalog.

**How to apply.** When authoring T1 Readiness for a 2b.x spec, identify each drift / decision and slot it into (a) or (b) based on whether epic prose drifted from runtime reality (a) or the author chose to scope something differently than the epic suggests (b).

**Evidence anchor from 2b.1 Gary run.** Three items flagged at T1: Drift #1 (sanctum/sidecar contract duality â€” bucket (a), augments A11) + Drift #2 (model-ID `gpt-4.1-mini` not in registry â€” bucket (a), augments A10) + Drift #3 (bounded scope â€” bucket (b), codified in R1 of this document).

---

## R7. Trail-entry resolution at `_plan` is mandatory even when `_act` does not invoke the chat handle

**Rule.** For any tool-dispatch category specialist (subprocess, REST-API, future MCP-tool), the `_plan` node MUST resolve and append the `ModelResolutionEntry` to `RunState.model_resolution_trail` even when `_act` will not invoke the resolved chat handle.

**Why.** Without this rule, an inheritor dev agent may shortcut and skip resolution at `_plan` ("why resolve a model I never call?"). That breaks: (a) cache-prefix attribution per NFR-I6 (the entry's `cache_prefix_hash` is consumed by Slab-3 middleware); (b) FR16 trail-entry contract uniformity across all four specialist categories; (c) Winston W2 discriminator-check pattern at `_act` (which reads `state.model_resolution_trail[-1].cache_prefix_hash` and rejects on `None`); (d) any future Slab-3 middleware that walks the trail and expects every specialist to have a `_plan`-time entry.

**How to apply.** In every 2b.x `_plan` node body: call `make_chat_model(specialist_id=..., temperature=state.temperature, tier_request=...)` and append `handle.entry` to `state.model_resolution_trail`. Document in `model_config.yaml` inline comments that the chat handle is NOT invoked at `_act` for tool-dispatch categories. Test pin: AC-C verifies the trail entry exists post-`_plan` even though no LLM call fires at `_act`.

**Evidence anchor from 2b.1 Gary run + 2a.4 Texas precedent.** Gary's `_plan` calls `make_chat_model(specialist_id="gary", tier_request="fast")` â†’ resolves to `gpt-5-haiku`; appends `handle.entry` to trail. `_act` discriminator-check reads trail and rejects if last entry's `cache_prefix_hash` is None. Chat handle never invoked.

---

---

## R8. Bounded-scope inheritors recalibrate K-floor downward (M-R11)

**Rule.** When R1 bounded-scope is invoked aggressively (â‰¥2 substrate categories OUT OF SCOPE per the migration story â€” e.g., SKILL.md persona + first-breath ceremony + sanctum population), K-floor recalibrates down one band: `1.4Ã— â†’ 1.2Ã—` target. Surplus tests above the recalibrated floor become G6 DISMISS-eligible.

**Why.** Bounded-scope migrations have smaller surface than full-substrate inheritors (fewer files migrated, fewer ceremony tests, simpler test discipline). Holding K-floor at full-substrate band invites either (a) test-padding to clear the floor or (b) drift toward longer parametrize matrices. Recalibration rewards the bounded-scope discipline.

**How to apply.** When authoring a bounded-scope inheritor spec: count substrate categories OUT OF SCOPE per R1. If â‰¥2, declare K-target ~1.2Ã— (target-N+1 / floor-N) and recompute test count budget against the lower floor. Document the recalibration in spec text as a NAMED amendment (M-R11 reference).

**Evidence anchor from 2b.5 Tracy run.** Tracy has SKILL.md persona + first-breath + sanctum population OUT OF SCOPE â€” 3 substrate categories. K recalibrated 1.4Ã—â†’1.2Ã— (target 11 / floor 8 vs full-substrate 13/10). Documented at AC-2b.5-K + Testing Requirements.

**W-R8 amendment (2b.9 close, codified in v2.3):** R8 has TWO independent trigger conditions: **(a) â‰¥2 substrate categories OOS** (Tracy precedent); **(b) category-novel + structurally lighter act-body than prior categories** (Kim precedent â€” Kim has no LLM, no dispatch substrate; act-body is structurally lighter than narration / LLM+tool-dispatch / pure-tool-dispatch / REST-API). Either condition alone is sufficient to trigger R8 recalibration. Stories may hit both (Kim hits both); document in spec text. (a) is the bounded-scope-aggressive case; (b) is the category-establishing-thin-node case.

---

## R13. Inheritor-parent matrix invariant: one inheritor â†’ one parent Â§12.x (W-R9)

**Rule.** The Â§12.12 inheritor catalog matrix maintains a **one-row-per-inheritor â†’ one-parent-Â§12.x** invariant. Each inheritor row in Â§12.12 names exactly ONE parent Â§12.x (the category whose worked example the inheritor follows). Multi-parent / hybrid-classification inheritors are NOT permitted; they require structural matrix change (column for "primary parent / secondary parent") which is OUT OF SCOPE for any per-specialist migration story.

**Why.** The matrix's reading-flow invariant is "scan Â§12.12 â†’ find your inheritor â†’ follow the single-parent Â§12.x worked example for the implementation pattern." Multi-parent rows break this invariant; the reader doesn't know which parent's pattern to follow. Hybrid specialists exist (Midjourney has limited-API surface + dominant operator-instructions surface) but the matrix cannot represent them without architectural change.

**How to apply.** When authoring an inheritor spec, classify the specialist into ONE of the established categories. If the substrate has multiple surfaces (e.g., REST-API stub + operator-instructions), pick the DOMINANT surface as the parent and file the secondary surface as a DEFERRED follow-on (Slab-3 or a future per-specialist enhancement story). Pre-classification of ambiguous cases must happen at the slab-establishing TEMPLATE story, NOT at the per-inheritor authoring time (prevents per-story relitigation).

**Evidence anchor from 2b.9 Kim run.** Midjourney (2b.12) pre-classified as Option A (Category C operator-instructions inheritor with API-stub OOS to Slab-3 follow-on `midjourney-api-stub-slab-3-followon` filed at 2b.9 close). Hybrid Option B rejected per R13 invariant.

---

## R14. Inheritor K-floor cap (M-R20)

**Rule.** Inheritors of an established category Â§12.x (rows in Â§12.12 inheritor catalog matrix) target **K-floor â‰¤ parent-target** (NOT parent-floor + N). Parent-target serves as the inheritor cap; substrate-specific tests beyond parent-target migrate to follow-on stories. Document the cap in the Â§12.12 inheritor catalog row header.

**Why.** Without this cap, inheritor stories drift case-by-case as each adds its own niche tag/branch. By the Nth inheritor, K-floor has crept upward and cannot be argued down at G6 review. The cap forces inheritor stories to either (a) match the established pattern within budget, or (b) escalate "this isn't a clean inheritor" to party-mode for re-categorization.

**How to apply.** When authoring an inheritor spec for Â§12.x, look up the parent's K-target. Set inheritor K-target = parent-target; inheritor K-floor = parent-floor + â‰¤5 substrate-specific tests. If substrate forces beyond +5, escalate at story-author time to party-mode; the inheritor is not a clean inheritor.

**Evidence anchor from 2b.9 Kim run.** Kim's K-floor 8 / target 11 sets the Â§12.13 ceiling. Inheritors of Â§12.13 (Vyond 2b.10 / Articulate 2b.11 / Midjourney 2b.12 / Canva 2b.13) target K-floor â‰¤ 13 (Kim's floor 8 + â‰¤5 substrate-specific tests). Documented in Â§12.12 row header at 2b.9 close.

---

---

## R9. Precedence pin REQUIRED when two parse-branch tags collide on identical surface shape (M-R12)

**Rule.** When a parse-helper has two tags that can both match the same input shape (e.g., `empty` vs `no-results`; `malformed` vs `wrong-type` for nested structures), the spec MUST pin precedence ordering AND name the discriminator field. Without precedence pin + discriminator, parametrize cases collapse into undecidable tests and one case is vacuous.

**Why.** Without precedence ordering, the parse-helper's behavior at runtime is non-deterministic for ambiguous inputs. Test parametrize matrix cannot reliably assert "input X â†’ tag Y" if both Xâ†’Y and Xâ†’Z are valid by the helper's logic.

**How to apply.** In AC-B (or whichever AC names the parse-helper), state the precedence as ordered narration: `tag-1 â†’ tag-2 â†’ ... â†’ ok`. Name the discriminator field that distinguishes overlapping tags. Add parametrize case asserting precedence (input that COULD match the lower-precedence tag â†’ asserts higher-precedence tag fires).

**Evidence anchor from 2b.4 Desmond + 2b.5 Tracy runs.** Desmond pinned `empty` BEFORE `advisory-missing` (M-R10 narration precedence convention â€” special case of R9 for narration category). Tracy pinned `malformed â†’ missing-key â†’ wrong-type â†’ empty â†’ no-results â†’ vocabulary-violation â†’ ok` with discriminator field `query_attempted` distinguishing `empty` (LLM bug) from `no-results` (legitimate-zero-results sentinel).

---

## R10. Load-bearing SSOT contracts require an invariant test alongside the parse-branch test (M-R13)

**Rule.** When a specialist has a load-bearing single-source-of-truth (SSOT) contract (e.g., a controlled vocabulary file, a schema reference, a tier-mapping table), the spec MUST require TWO distinct tests: (a) parse-branch test exercising the violation tag (one parametrize case); (b) invariant test asserting the SSOT loader is the ONLY source (no hardcoded enums in `_act` body; emitted golden fixtures conform to SSOT; loader runs at module import with cached frozenset/typed-set).

**Why.** Parse-branch test alone exercises the violation case but does NOT prevent code drift where a future dev agent introduces a hardcoded enum that bypasses the SSOT loader. Texas's NFR-I5 retrieval-contract preservation pattern is the reference implementation: hard sha256 baseline test + grep-style assertion that the contract file is the ONLY source.

**How to apply.** In AC-G (or AC-Invariant), name the SSOT loader pin: module-level `_VALID_<NAME>: frozenset[str]` cached at module import; parse-helper raises with structured tag on violation; ONE invariant test asserts loader == known set AND grep-style asserts no other source.

**Evidence anchor from 2b.5 Tracy run.** `_VALID_INTENT_CLASSES: frozenset[str]` loaded from `vocabulary.yaml` at module import in `posture_dispatch.py`; `_parse_manifest` raises `ManifestParseError(tag="manifest.parsed.vocabulary-violation")` on violation; `test_tracy_vocabulary_loaded_at_import_time` invariant test pins both load + uniqueness.

---

## R11. Permanent-skip hard cap = 3 inheritor stories OR 30 calendar days, whichever first (M-R14)

**Rule.** When a test uses `pytest.skip(...)` with a deferred-reactivation marker (e.g., `DEFERRED-OPERATOR-WINDOW`, `DEFERRED-EPIC-XX-FORWARD-PORT`, `DEFERRED-SLAB-3`), the skip is allowed for at most **3 inheritor stories OR 30 calendar days, whichever first**. After the cap, the skip becomes a BLOCKER and the story author MUST either (a) remove the test (no contract pretense), or (b) replace with a structural-shape test that runs without the deferred substrate.

**Why.** `pytest.skip` with named gate is the right shape for short-term decoupling from operator-window or upstream-forward-port dependencies. But "indefinitely" is the erosion vector â€” vacuous-pass becomes the default; sanctum-conformance / SSOT-conformance discipline degrades when skips outnumber executed assertions across slabs.

**How to apply.** Skip reason MUST include a machine-grep marker (`DEFERRED-<GATE>`). At spec-author time, declare the cap in Dev Agent Record. At each subsequent inheritor story T1, the dev agent counts elapsed inheritor-stories + calendar-days; if cap fired, escalate. CI follow-on `migration-deferred-skip-decay-monitor` lists all `DEFERRED-*` markers + their age for operator visibility.

**Evidence anchor from 2b.5 Tracy run.** AC-D test #3 skips with `"DEFERRED-EPIC-28-1-FORWARD-PORT"` marker; cap fires at end of Slab 2b OR 2026-05-25, whichever first. After cap: skip becomes BLOCKER per R11.

---

## R12. Parse-branch ceiling = 6 unless story names load-bearing semantic forcing the +1 (M-R15)

**Rule.** Default parse-branch parametrize matrix is bounded at **6 cases** (the `bundle.parsed.* / receipt.parsed.* / ftr.parsed.* / qrr.parsed.* / handoff.parsed.*` precedents at Texas/Gary/Vera/Quinn-R/Desmond all sit at 6). To exceed 6, the spec MUST NAME the load-bearing semantic forcing the +1 as an exemption in spec text â€” NOT just listed in the tag namespace.

**Why.** Parse-branch counts have a monotone-drift tendency across inheritor stories (Vera 6 â†’ Quinn-R 6 â†’ Desmond 6 â†’ Tracy 7+). Without an explicit exemption rule, the matrix grows un-budgeted; G6 reviewers cannot judge "is this novel surface or pad-band-creep?" Naming the exemption forces the spec author to argue for the +1 explicitly.

**How to apply.** In AC-B, list the parse-branch tags. If count > 6, add a sentence in spec text: "**M-R15 load-bearing exemption named:** `<tag-N+1>` is load-bearing because <specific-rationale>." If the rationale is "completeness" or "symmetry with Texas/Gary/etc." that's NOT load-bearing â€” DROP back to 6.

**Evidence anchor from 2b.5 Tracy run.** Tracy clears the 6-tag ceiling (7 tags) because (a) `vocabulary-violation` is load-bearing per Tracy README rule 4 "Vocabulary SSOT â€” code drift = CI failure"; (b) `no-results` is structurally distinct from `empty` per R9 precedence pin (legitimate-zero-results vs LLM-bug). Both rationales are story-specific.

**M-R18 amendment (2b.8 close, codified in v2.2):** When a multi-mode dispatch specialist (per A-2b.7-R2 pattern) emits per-mode helper smoke tests, those tests MUST be parametrize-collapsible into ONE test function with N cases. Counts as 1 K-floor unit regardless of N. Prevents unbounded K-floor inflation as mode-count grows (Enrique 4 modes â†’ Wanda 6 modes â†’ future N modes). The function may live in `test_<specialist>_dispatch_wrapper.py` alongside the 3 SEAM tests; total test functions in that file = 3 SEAM + 1 parametrized = 4 (regardless of mode count).

---

## How to apply this template at a 2b.x story spec

1. At T1 Readiness Standing Pre-Flight items list: **add this document (`docs/dev-guide/specialist-migration-template.md`) as item 11, sibling to `scaffold-conformance-framework.md` and `sanctum-reference-conventions.md`.** The 2b.x story spec includes a one-line citation in the form: "TEMPLATE rules from `docs/dev-guide/specialist-migration-template.md` v1 apply per R1â€“R7."

2. Each spec's "TEMPLATE-establishing decisions" AC (the equivalent of 2b.1's AC-2b.1-K) is replaced with: **"AC-2b.x-K: TEMPLATE rules R1â€“R7 from `docs/dev-guide/specialist-migration-template.md` apply. Document any deviation + rationale in Dev Agent Record."** Inheritor specs do NOT re-state the rules; they cite them.

3. Each spec's T1 Readiness `Epic-doc-vs-framework cross-check` section is split per R6 into (a) Framework drifts + (b) TEMPLATE scope decisions sub-subsections.

4. At story close, the D12 close stub includes a 4th line for TEMPLATE-validated stories: **"TEMPLATE compliance: R1â€“R7 honored without deviation"** OR **"TEMPLATE deviation: R<n> deviated for <reason> with party-mode ratification"**.

---

## Changelog

| Version | Date | Changes | Origin |
|---|---|---|---|
| v1 | 2026-04-25 | Initial freeze. Seven rules R1â€“R7 ratified at Story 2b.1 close per AC-2b.1-K + party-mode P-R4 (Paige) + W-R1 (Winston seventh-rule rider). | Story 2b.1 close |
| v2 | 2026-04-25 | Added R8â€“R12 codifying party-mode amendments at Story 2b.5 close: R8 (M-R11 bounded-scope K-floor recalibration), R9 (M-R12 precedence pin convention), R10 (M-R13 SSOT invariant test pattern), R11 (M-R14 permanent-skip hard cap 3 stories / 30 days), R12 (M-R15 parse-branch ceiling 6 unless named exemption). M-R10 narration precedence convention from Story 2b.4 Desmond is special case of R9 for narration category. | Story 2b.5 close |

| v2.4 | 2026-04-25 | Slab-close amendment: codified M-R22 (tag namespace root tracks category), M-R24 (wave-close framing), and Paige section 12.10 retrospective-container restructure. | Story 2b.17 close |

