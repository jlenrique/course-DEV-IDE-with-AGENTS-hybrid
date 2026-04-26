# Migration Story 2b.5: Migrate Tracy (Research Intent Shaper) to 9-Node Scaffold â€” BOUNDED to currently-shipped substrate

**Status:** done
**Sprint key:** `migration-2b-5-tracy-research-intent-shaper-scaffold-migration`
**Epic:** Slab 2b â€” fifth per-specialist migration; FOURTH inheritor of 2b.1 Gary TEMPLATE; **bounded-scope migration of partial Tracy substrate** (Tracy is "Sanctum bundle under construction" per skill README; full SKILL.md persona owned by primary-repo Epic 28 Story 28-1).
**Pts:** 3 | **Gate:** single (per governance JSON `2b-5.expected_gate_mode = "single-gate"`, rationale: "Follows 2b.1 TEMPLATE"). **K-target:** ~1.2Ã— (target 11 / floor 8 â€” RECALIBRATED per Murat M-R11 amendment 2026-04-25: bounded-scope inheritors with â‰¥2 substrate categories OUT OF SCOPE recalibrate K-floor downward one band; Tracy has SKILL.md persona + first-breath + sanctum population OUT OF SCOPE, qualifying for the recalibration).

**3-agent party-mode amendments applied 2026-04-25 (Winston + Murat + Amelia):** 3 BLOCKERs resolved + 9 APPLY RIDERs integrated:
- **BLOCKER-1 (Murat #7 + Amelia BLOCKER-1 convergent):** `skills/bmad_agent_tracy/scripts/posture_dispatcher.py` exposes `PostureDispatcher` class with NotImplementedError stubs (Epic 28-2 owner); NO module-level `dispatch_posture()` function. **Resolution: option (i) â€” wrapper-becomes-no-op-pass-through; LLM at `_act` produces the full manifest; `posture_dispatch.py` records posture-selection trail tag only. AC-B-LIVE asserts vocabulary-conformant intent_class on stub-dispatched fixture results.**
- **BLOCKER-2 (Amelia BLOCKER-2):** cross-cutting extraction story `slab-2a-close-followon-sanctum-lock-cross-cutting` not yet authored as story file. **Resolution: dependency enforced at batch-dev-cycle level â€” 2b.3 close fires the cross-cutting story filing; cross-cutting story MUST close before 2b.5 dev-story opens. Spec authoring is unblocked; dev-story open is gated.**
- **BLOCKER-3 (Winston W-R6):** missing `tracy-skill-persona-authoring-on-hybrid` follow-on. **Resolution: filed at AC-M with named fire-trigger + scope + architectural bound (W-R3 invariant).**
- **RIDERs codifying new TEMPLATE rules (require `specialist-migration-template.md` v2 bump):** M-R11 bounded-scope K-floor recalibration; M-R12 precedence pin convention; M-R13 SSOT invariant test pattern; M-R14 permanent-skip hard cap (3 inheritor stories OR 30 calendar days); M-R15 parse-branch ceiling = 6 unless load-bearing exemption named.
- **Tracy-specific RIDERs:** W-R3 architectural pin against persona-coupling at runtime; W-R4 A11 sub-bullet (no retitle until 6th example with 3rd sub-shape); W-R5 skip-decay marker `"DEFERRED-EPIC-28-1-FORWARD-PORT"` + filing `migration-deferred-skip-decay-monitor` follow-on; Amelia RIDER-2 vocabulary-loader pin (`_VALID_INTENT_CLASSES: frozenset[str]` at module import); Amelia RIDER-3 +1 vocabulary-load test.

Tracy is **LLM+tool-dispatch category** (Â§12.6 Kira parent) â€” LLM at `_act` for query formulation + scoring + editorial-note authoring; dispatches to `posture_dispatcher.py` for posture selection AND atomic manifest writes. Tracy adds ONE row to Â§12.12 inheritor catalog matrix under Â§12.6 parent (per R3). **NOTABLE divergences from prior inheritors:**

1. **Skill-dir snake_case `bmad_agent_tracy/` (NOT kebab-case `bmad-agent-tracy/`)** â€” per slab-2-roster-reconciliation note "Snake-case path (post-Epic-28 sanctum bundle); 3-posture contract." This is **A11 fifth example** but with a NEW sub-shape: snake_case-vs-kebab-case path drift (vs Irene/Gary/Vera/Quinn-R which were skill-dir-vs-persona-name drift). Title may need second broadening â€” defer disposition to G6 review.
2. **NO SKILL.md exists** at story-author time â€” README says SKILL.md "gets built during Story 28-1 implementation." Migration covers ONLY the runtime act-body; SKILL.md persona authoring is OUT OF SCOPE per bounded-scope rule R1 (deferred to Epic 28-1 forward-port from primary OR a separate Tracy-SKILL-authoring story).
3. **Snake_case dirname enables direct package import** â€” `from skills.bmad_agent_tracy.scripts.posture_dispatcher import dispatch_posture` is directly importable (verify at T1 + check `posture_dispatcher.py` for module-level side effects per A-R8/A-R2 verification protocol). If clean, use direct import (NOT importlib loader). R2 third-occurrence loader extraction trigger remains satisfied by Quinn-R 2b.3; Tracy adds a NEW seam-category occurrence (snake_case direct import). Loader extraction follow-on filed at 2b.3 covers Kira+Vera+Quinn-R; Tracy is parallel-but-different seam.
4. **No sanctum, no sidecar at story-author time** â€” no `_bmad/memory/bmad_agent_tracy/` AND no `_bmad/memory/tracy-sidecar/`. Sanctum graceful-degrade case (empty-string digest per R5). NO operator first-breath ceremony scheduled â€” sanctum population deferred to post-Epic-28 forward-port.

---

## T1 Readiness Block

Standing Pre-Flight items 1â€“10 same as 2b.2. Item 11: [`docs/dev-guide/specialist-migration-template.md`](../../docs/dev-guide/specialist-migration-template.md) v1, R1â€“R7 apply.

### Slab 2b artifact-existence sweep â€” Tracy-specific deltas

- **C** Reference patterns: Kira 2a.3 (LLM+tool-dispatch parent at Â§12.6); Vera 2b.2 (closest LLM+tool-dispatch inheritor pattern; uses importlib but Tracy uses direct import).
- **F** `pyproject.toml` C3 contains 9 rows pre-Tracy (5 baseline + Gary + Vera + Quinn-R + Desmond). Tracy auto-emit makes 10. **Generator naming verification at T1:** generator's NAME_PATTERN per `skills/bmad_create_specialist/scripts/generate.py:21` accepts `[a-z][a-z0-9_]*`; `tracy` is the runtime persona name (not `bmad_agent_tracy`). Use `--name tracy --from-skill skills/bmad_agent_tracy`.
- **G** Cache-hit-rate (FR54): Tracy's act invokes LLM with stable provider-mapping prefix (vocabulary.yaml + scite provider reference). FR54 substrate IS applicable. Defer measurement to follow-on (parallel to Desmond `desmond-fr54-cache-hit-baseline-measurement` filing).
- **R2 importlib loader status:** Tracy uses **direct package import** for `posture_dispatcher.py` (snake_case dirname). Loader-occurrences count UNCHANGED at 3 (Kira + Vera + Quinn-R = 3, threshold met at 2b.3). Tracy is a NEW direct-import-via-snake_case-package seam â€” first occurrence of THIS sub-mechanism.

### Epic-doc-vs-framework cross-check (per R6)

#### (a) Framework drifts

**Drift #1 â€” Snake_case skill-dir naming (A11 FIFTH example, possibly second title-broadening trigger):** Tracy's skill-dir is `bmad_agent_tracy/` (snake_case underscore separator), NOT `bmad-agent-tracy/` (kebab-case). All four prior A11 examples (Irene, Gary, Vera, Quinn-R) used kebab-case skill-dir + persona-name divergence. Tracy's shape is **persona-name AS dirname (matching) but with snake_case separator (drifting from kebab-case convention)**. Different sub-shape â€” A11 was titled "sanctum/sidecar contract drift" at 2b.1 broadening; the snake_case shape doesn't fit cleanly. **Disposition options for G6 review:** (a) extend A11 with snake_case-vs-kebab-case sub-bullet, (b) further broaden A11 title to "skill-dir convention drift from hybrid BMB normalization", or (c) file as A12 (post-A12-RESOLVED) or A13 if novel category warrants. **Default at story-author time: option (a) â€” extend A11 with the new sub-shape; G6 review may upgrade to (b) title-broadening per A9 retitle precedent at 2a.4.** Harvest at AC-J.

**Drift #2 â€” Tracy's bounded scope vs roster-reconciliation "Category A migration-ready" label:** slab-2-roster-reconciliation labels Tracy "Category A â€” fully mature, migration-ready" but Tracy's README says "Sanctum bundle under construction; implementation in Epic 28 Story 28-1." Reconciliation predates Story 28-1 ratification on hybrid. **NOT a framework drift in the A9-A12 sense (neither epic-prose vs runtime-reality nor sanctum-path drift); flag as roster-reconciliation document state-drift.** No anti-pattern catalog harvest; instead, file `slab-2-roster-reconciliation-tracy-status-update` follow-on at 2b.5 close to update reconciliation doc with current Tracy state.

#### (b) TEMPLATE scope decisions

**Decision #1 â€” Bounded scope (per R1):** migrate ONLY the currently-shipped runtime substrate (`posture_dispatcher.py`, `irene_bridge.py`, `smoke_fixtures.py`, `vocabulary.yaml`, `postures.md`). SKILL.md persona authoring + first-breath protocol + most reference docs OUT OF SCOPE â€” owned by Epic 28 Story 28-1 on primary; will forward-port to hybrid as a separate story when Epic 28-1 lands on hybrid. Document gating in Dev Agent Record: "Tracy at 2b.5 = runtime act-body + state shape + dispatch wrapper ONLY. Full Tracy migration completes when Epic 28-1 forward-ports from primary."

**Decision #2 â€” Direct package import for `posture_dispatcher.py`:** snake_case dirname `bmad_agent_tracy/` allows `from skills.bmad_agent_tracy.scripts.posture_dispatcher import dispatch_posture`. Verify at T1: (a) `skills/__init__.py` exists (verified â€” present at root); (b) `skills/bmad_agent_tracy/__init__.py` exists (verified per ls 2026-04-25); (c) `skills/bmad_agent_tracy/scripts/__init__.py` exists (verify at T1); (d) `posture_dispatcher.py` has no heavy module-level side effects (verify at T1 â€” if side effects, fall back to importlib loader per A-R8 protocol). Direct import is the FIRST occurrence of this seam sub-mechanism (snake_case package); separate from Kira/Vera/Quinn-R importlib-loader cluster (3 occurrences, extraction filed) AND from Gary direct-package-import cluster (1 occurrence + Tracy = 2 occurrences of direct-import; threshold of 3 unmet).

**Decision #3 â€” Sanctum graceful-degrade with NO scheduled first-breath:** unlike Gary/Vera/Quinn-R where operator first-breath was deferred to operator-window, Tracy's first-breath is owned by Epic 28-1 forward-port (NOT operator-window). PERSONA.md sentinel skip per A-R5 still applies; the test will skip indefinitely on hybrid until Epic 28-1 lands. Document in spec: "Tracy sanctum lock-baseline test will SKIP until Epic 28-1 forward-port lands the BMB sanctum at `_bmad/memory/bmad_agent_tracy/`."

---

## Story

As a **migration dev agent inheriting the 2b.1 TEMPLATE**,
I want **Tracy (Research Intent Shaper) rehomed into `app/specialists/tracy/` with the 9-node scaffold + LLM+tool-dispatch act-body that wraps `posture_dispatcher.py` via direct package import + bounded scope (currently-shipped substrate only) + per-R5 auto-emit C3 row + Â§12.12 inheritor row added under Â§12.6 parent + clear deferral language for SKILL.md persona authoring + first-breath ceremony**,
So that **Tracy's runtime layer lands on the LangGraph stack ahead of Epic 28-1 forward-port (decoupling runtime migration from persona authoring), the first snake_case-dirname-direct-import seam is exercised, and Slab 2b cadence holds even when source skill substrate is partial**.

---

## Acceptance Criteria

All ACs are dev-agent-executable. Tracy carries ONE `@pytest.mark.llm_live` test (AC-B live LLM query formulation against fixture brief).

### AC-2b.5-A â€” Generator emits Tracy + auto-emits C3 row (per R5)

Per R5 + 2b.1 hermetic pattern. Test pin: `tests/specialists/tracy/test_tracy_generator_auto_emit_c3_row.py` â€” 3 tests using `temp_repo_root` fixture. Pre-baseline 5 â†’ post-emit 6 (in fixture); live repo at story close = 10 rows total.

Generator invocation:
```
.venv\Scripts\python.exe -m skills.bmad_create_specialist.scripts.generate \
  --name tracy --mcp none --expertise-tier L4-research-shaping \
  --from-skill skills/bmad_agent_tracy
```

**Note:** `--from-skill` argument points to snake_case dirname; generator must accept this without normalization. Verify at T1.

### AC-2b.5-B â€” Tracy `act` node wires LLM-only manifest authoring + posture-selection trail-tag wrapper

**(BLOCKER-1 resolution: posture_dispatcher.py ships NotImplementedError stubs per Epic 28-2 owner; Tracy's runtime LLM produces the full manifest; the wrapper records posture-selection trail tag only.)**

- **Given** Tracy's `_act` (1) reads ModelResolutionEntry from trail + reject if `cache_prefix_hash is None` (Winston W2); (2) extracts research-brief payload from `state.cache_state.cache_prefix`; (3) invokes LLM (`tier_request: reasoning` â†’ `gpt-5.4` per A10 pattern; "long-context-balanced" framing in epic 2b.1 line 710 maps to `reasoning` per shipped registry; document mapping rationale) for query formulation + intent_class assignment + editorial_note authoring + **full manifest synthesis** (LLM produces complete suggested-resources manifest with vocabulary-conformant intent_class values; the upstream posture-dispatch substrate raises NotImplementedError today, so 2b.5 routes manifest authoring through the LLM directly); (4) records posture-selection via `app.specialists.tracy.posture_dispatch.record_posture_selection(intent_class)` (no-op wrapper that emits a trail-tag entry naming the selected posture; thin direct-package-import shim around `skills.bmad_agent_tracy.scripts.posture_dispatcher` for FR16 contract consistency; `posture_dispatcher.py` ships NotImplementedError stubs per Epic 28-2 owner so the shim does NOT call any of the stub methods); (5) parses LLM-produced manifest via `_parse_manifest` helper into `tracy_manifest` shape; (6) returns cache_state + manifest reference.
- **When** the dev agent implements `_act` per the LLM-only-with-trail-tag-wrapper pattern.
- **Then** invoking `build_tracy_graph()` with fixture brief envelope + monkey-patched LLM returning fixture manifest produces non-empty result containing `tracy_manifest` with vocabulary-conformant entries.
- **LOC budget per A-R3 carry-forward:** `_act â‰¤ 115 LOC`; `posture_dispatch â‰¤ 40 LOC` (downsized from 75 â€” wrapper is no-op trail-tag emitter, not full dispatcher per BLOCKER-1 resolution); `_parse_manifest` helper extracted module-level per Vera A-R9 option-b precedent.
- **Tag namespace per Murat M-R2 + M-R10 + M-R12 + M-R15 conventions:** `manifest.parsed.*` â€” tags `manifest.parsed.ok / malformed / missing-key / wrong-type / empty / no-results / vocabulary-violation`. **M-R15 load-bearing exemption named:** Tracy clears the 6-tag ceiling because (a) `vocabulary-violation` is load-bearing per README rule 4 "Vocabulary SSOT â€” code drift = CI failure"; (b) `no-results` is structurally distinct from `empty` per M-R12 precedence pin (legitimate-zero-results vs LLM-bug). **M-R12 precedence pin (BINDING):** `_parse_manifest` evaluates tags in order `malformed â†’ missing-key â†’ wrong-type â†’ empty â†’ no-results â†’ vocabulary-violation â†’ ok`. Discriminator for `empty` vs `no-results`: `empty` fires when LLM returns null/absent results field; `no-results` fires when LLM returns explicit `{results: [], query_attempted: "..."}` sentinel. Discriminator field MUST be present at parse-helper input or `no-results` cannot fire â€” fall back to `empty`.
- **Vocabulary loader pin per Amelia RIDER-2 (BINDING):** `posture_dispatch.py` loads `intent_class.day_1_values` keys from `skills/bmad_agent_tracy/references/vocabulary.yaml` at MODULE IMPORT time, caches as module-level `_VALID_INTENT_CLASSES: frozenset[str]`. Path resolution: `Path(__file__).resolve().parents[3] / "skills" / "bmad_agent_tracy" / "references" / "vocabulary.yaml"` (parallel to Texas/Kira `REPO_ROOT` pattern). `_parse_manifest` raises `ManifestParseError(tag="manifest.parsed.vocabulary-violation")` on first row whose `intent_class` not in `_VALID_INTENT_CLASSES`. **SSOT invariant test per Murat M-R13:** `test_tracy_vocabulary_loaded_at_import_time` asserts `_VALID_INTENT_CLASSES == frozenset({"narration_citation", "supporting_evidence", "counter_example", "reserved"})` AND that the loader is the ONLY source of truth (no hardcoded enums in `_act` body or graph.py).
- **Live LLM test (`@pytest.mark.llm_live`):** AC-B-LIVE asserts live `gpt-5.4` call produces structurally valid manifest with at least one entry having vocabulary-conformant `intent_class`. Skips on placeholder OPENAI_API_KEY.

### AC-2b.5-B-OP â€” Live operator-gated evidence (DEFERRED-PENDING-OPERATOR-WINDOW)

Operator runs Tracy against a real Marcus-staged research brief; pastes manifest into Completion Notes. Same shape as Vera/Gary precedents.

### AC-2b.5-C â€” Model cascade at `_plan` (per R7)

Trail-entry resolution at `_plan` per R7. Test pin: 2 tests.

### AC-2b.5-D â€” Sanctum cold-read at `_plan` (graceful-degrade per R5+R6; NO scheduled first-breath)

- **Given** Tracy's BMB sanctum at `_bmad/memory/bmad_agent_tracy/` does NOT exist at story-author time (verified: NO entry in `_bmad/memory/`); first-breath ceremony OWNED BY Epic 28-1 forward-port (NOT operator-window).
- **When** Tracy's `plan` node runs `_read_sanctum_digest`.
- **Then** returns empty string; cache-prefix attribution records empty-digest sha256 for FR16 contract consistency.
- **Test pins (3 tests, same as Vera/Quinn-R):**
  1. `test_tracy_sanctum_fingerprint_deterministic_empty_dir`.
  2. `test_tracy_expertise_readme_lists_l4_references`.
  3. `test_tracy_sanctum_lock_baseline_pinned_OR_skip` â€” `if not (SANCTUM_DIR / "PERSONA.md").is_file(): pytest.skip("DEFERRED-EPIC-28-1-FORWARD-PORT: Tracy sanctum awaits Epic 28-1 forward-port â€” see slab-2-roster-reconciliation Tracy status")`. **Skip reason MUST include `"DEFERRED-EPIC-28-1-FORWARD-PORT"` machine-grep marker per Winston W-R5 amendment 2026-04-25** for CI skip-decay monitoring. **Per Murat M-R14 permanent-skip hard cap:** skip allowed THIS story; cap fires at end of Slab 2b OR 2026-05-25, whichever first. After cap: skip becomes BLOCKER; story-author MUST either (a) remove the test, OR (b) replace with structural-shape test that runs without sanctum. Imports `SanctumLockViolation` from `app.specialists.texas.graph` per BLOCKER-2 resolution (FIFTH cross-specialist consumer; depends on `slab-2a-close-followon-sanctum-lock-cross-cutting` extraction story closing BEFORE 2b.5 dev-story opens â€” enforced at batch-dev-cycle level). If extraction story has CLOSED before dev-story open, import shifts to `app.specialists._scaffold.sanctum_exceptions.SanctumLockViolation`.

### AC-2b.5-E â€” Gate-decision binding (precedent-inherited)

2 tests.

### AC-2b.5-F â€” Resolution trail (FR16 eighth per-specialist exercise)

1 test.

### AC-2b.5-G â€” Tracy shape-pin tests (per R4)

Per R4: `tracy_manifest: dict[str, Any] | None` (the suggested-resources manifest per `schemas/suggested-resources.schema.yaml` future schema; loose-typed at 2b.5 per R4). 4 tests.

### AC-2b.5-H â€” Scaffold-conformance test registered

`tests/integration/scaffold_conformance/test_scaffold_tracy.py` â€” 1 test.

### AC-2b.5-I â€” Migration-guide Â§12.12 grows ONE inheritor row (per R3)

Per R3, NEW row in Â§12.12 under Â§12.6 parent:

| Specialist | Parent Â§12.x | Seam divergence | Sanctum case | Harvest contributions | Story |
|---|---|---|---|---|---|
| Tracy | Â§12.6 (Kira LLM+tool-dispatch) | direct package import (snake_case `bmad_agent_tracy/` allows direct import; vs Kira/Vera/Quinn-R kebab-case forcing importlib; vs Gary direct-import for gamma_operations) | graceful-degrade (BMB sanctum awaits Epic 28-1 forward-port; first-breath NOT operator-window-scheduled) | A11 5th example (snake_case-vs-kebab-case skill-dir; possible second title-broadening at G6) + FR54 follow-on filing + bounded-scope substrate gating documentation | 2b.5 |

Update Â§12.5 framing: "eighth specialist proven on 9-node scaffold; LLM+tool-dispatch category now hosts 4 inhabitants (Kira/Vera/Quinn-R/Tracy); first snake_case-skill-dir-direct-import seam exercised at Tracy."

### AC-2b.5-J â€” Anti-pattern catalog harvest (A11 FIFTH example + roster-reconciliation update)

- **A11 fifth example bullet:** Tracy skill-dir `bmad_agent_tracy/` (snake_case), runtime persona `tracy`. Persona name MATCHES dirname (no separator-meta drift like Irene/Gary/Vera/Quinn-R) but uses snake_case separator (NOT kebab-case BMB convention). New sub-shape under A11 broadening. **G6 disposition decides:** title broadening to cover snake_case OR sub-bullet under existing title.
- **`slab-2-roster-reconciliation-tracy-status-update` follow-on filed at 2b.5 close** â€” update reconciliation doc to reflect Tracy's actual partial-substrate state at 2b.5; downgrade or annotate the "Category A â€” fully mature" label.

### AC-2b.5-K â€” TEMPLATE compliance (per R1â€“R7 + new R8â€“R12 from this story's amendments)

R1â€“R7 honored. **Documented deviations + new rules codified at 2b.5 amendments per `specialist-migration-template.md` v2 bump:**
- **R1 bounded-scope aggressive invocation:** SKILL.md persona authoring + first-breath OUT OF SCOPE; deferred to Epic 28-1 forward-port. **W-R3 invariant pin (BINDING):** Tracy's `_act` MUST NOT load `SKILL.md` or first-breath ceremony content at runtime. Test pin: `test_tracy_act_does_not_load_persona` (1 test, NEW) asserts `_act` does not import `SKILL.md` or any sanctum persona file at runtime; static AST scan or import-time grep. This pins the bounded-scope decoupling architecturally.
- **R8 (M-R11 NEW):** Bounded-scope inheritors with â‰¥2 substrate categories OUT OF SCOPE recalibrate K-floor down one band (1.4Ã— â†’ 1.2Ã—). Applied to Tracy: target 11 / floor 8.
- **R9 (M-R12 NEW):** Precedence pin REQUIRED when two parse-branch tags can collide on identical surface shape; discriminator field MUST be named in spec text.
- **R10 (M-R13 NEW):** Load-bearing SSOT contracts require an invariant test alongside the parse-branch test (Texas NFR-I5 retrieval-contract pattern; Tracy vocabulary.yaml pattern).
- **R11 (M-R14 NEW):** Permanent-skip hard cap = 3 inheritor stories OR 30 calendar days, whichever first; after cap, skip becomes BLOCKER.
- **R12 (M-R15 NEW):** Parse-branch ceiling = 6 unless story names load-bearing semantic forcing the +1 (must be NAMED as exemption in spec text, not just listed in tag namespace).

### AC-2b.5-L â€” D12 close protocol (single-gate; FOUR-line per A-R7)

1. **Invariant preservation:** Slab-1 substrate intact; auto-emit C3 row machinery fired (C3 9â†’10 in live repo); FR54 substrate intact + applicable to Tracy (deferred follow-on filed); FIRST snake_case-dirname-direct-import seam lands cleanly.
2. **Anti-pattern harvest:** A11 5th example + roster-reconciliation status-update follow-on filed.
3. **Migration-guide update:** Â§12.12 inheritor row added under Â§12.6 parent; framing sentence updated.
4. **TEMPLATE compliance:** R1â€“R7 honored with R1 bounded-scope aggressive invocation documented. Numeric anchors: `_act` LOC measured (â‰¤115); `posture_dispatch` LOC measured (â‰¤75); 7 parse-branch tests; 1 @llm_live test; sanctum graceful-degrade skip; pyproject.toml C3 row count 5â†’6 fixture / 9â†’10 live.

### AC-2b.5-M â€” Sprint-status state-flips + multiple follow-ons filed at close (per W-R6 BLOCKER + W-R5)

At filing: `migration-2b-5-tracy-research-intent-shaper-scaffold-migration: ready-for-dev`. At close: flip to `done`.

**Follow-ons filed at 2b.5 close (per W-R6 BLOCKER + W-R5 + Decision G + Drift #2):**
1. **`tracy-skill-persona-authoring-on-hybrid` (W-R6 BLOCKER resolution):** Fire-trigger: "Epic 28-1 forward-port story files on hybrid OR operator explicitly requests Tracy first-breath ceremony." Scope: SKILL.md authoring + first-breath protocol + sanctum population at `_bmad/memory/bmad_agent_tracy/`. Architectural bound: scaffold-conformance test for Tracy MUST be re-run at follow-on close to verify `_act` did NOT acquire persona-loading coupling in the interim (ties back to W-R3 invariant). Filed at SAME commit as 2b.5 close per CLAUDE.md Â§Deferred inventory governance Â§3.
2. **`tracy-fr54-cache-hit-baseline-measurement` (Decision G):** Fire-trigger when Marcus orchestration carries Tracy through a real research-brief with stable provider-mapping prefix.
3. **`slab-2-roster-reconciliation-tracy-status-update` (Drift #2):** Update reconciliation doc to reflect Tracy's actual partial-substrate state.
4. **`migration-deferred-skip-decay-monitor` (W-R5):** Lightweight CI check listing all `pytest.skip` with `DEFERRED-EPIC-` markers + their age. ~0.5pt single-gate.
5. **`tracy-strict-vocabulary-llm-live-nightly` (Murat option):** Add `@pytest.mark.llm_live_strict` test asserting full manifest vocabulary conformance, gated behind nightly-only marker. Defer if not useful.

---

## File Structure Requirements

### NEW files

```
app/specialists/tracy/
â”œâ”€â”€ __init__.py                                 # generator-emitted
â”œâ”€â”€ graph.py                                    # generator-emitted; _act body filled at T2
â”œâ”€â”€ state.py                                    # generator-emitted; TracyReturn extended with tracy_manifest
â”œâ”€â”€ model_config.yaml                           # generator-emitted; reasoning/long-context-balanced tier comments
â”œâ”€â”€ posture_dispatch.py                         # NEW (~50-75 LOC); DIRECT package import wrapper around skills.bmad_agent_tracy.scripts.posture_dispatcher.dispatch_posture
â”œâ”€â”€ expertise/
â”‚   â”œâ”€â”€ README.md                               # generator-emitted; dotted reference table for Tracy refs (vocabulary.yaml + postures.md)
â”‚   â””â”€â”€ __init__.py

tests/specialists/tracy/
â”œâ”€â”€ __init__.py                                 # NEW (empty marker per A-R6)
â”œâ”€â”€ test_tracy_generator_auto_emit_c3_row.py    # NEW (3 tests; AC-A)
â”œâ”€â”€ test_tracy_act_node_dispatch.py             # NEW (~11 tests; AC-B with 7 parse-branches per M-R15 exemption + 1 happy-path + 1 @llm_live + 1 vocabulary-loader-import-time test (Amelia RIDER-3 / R10) + 1 W-R3 persona-coupling invariant test)
â”œâ”€â”€ test_tracy_dispatch_wrapper.py              # NEW (3 tests; AC-B SEAM â€” direct package import / no-op pass-through / no-subprocess)
â”œâ”€â”€ test_tracy_model_cascade.py                 # NEW (2 tests; AC-C)
â”œâ”€â”€ test_tracy_sanctum_cold_read.py             # NEW (3 tests; AC-D graceful-degrade with DEFERRED-EPIC-28-1-FORWARD-PORT marker per W-R5)
â”œâ”€â”€ test_tracy_gate_decision_binding.py         # NEW (2 tests; AC-E)
â”œâ”€â”€ test_tracy_resolution_trail.py              # NEW (1 test; AC-F)
â””â”€â”€ test_tracy_state_shape.py                   # NEW (4 tests; AC-G)

tests/integration/scaffold_conformance/
â””â”€â”€ test_scaffold_tracy.py                      # NEW (1 test; AC-H)

tests/fixtures/specialists/tracy/
â”œâ”€â”€ golden_envelope.json                        # NEW (research brief from Irene)
â””â”€â”€ golden_return.json                          # NEW (with tracy_manifest populated; vocabulary-conformant intent_class values)
```

### MODIFIED files

- `docs/dev-guide/langgraph-migration-guide.md` â€” Â§12.12 new row under Â§12.6.
- `docs/dev-guide/specialist-anti-patterns.md` â€” A11 5th example bullet (snake_case sub-shape; G6 may broaden title further).
- `_bmad-output/planning-artifacts/deferred-inventory.md` â€” file two follow-ons per AC-M.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` â€” per AC-M.
- `pyproject.toml` â€” auto-emitted; **NOT manually edited**.

---

## Testing Requirements

**K-target ~1.2Ã— (target 11 / floor 8) â€” RECALIBRATED per Murat M-R11 / R8.** Bounded-scope inheritor (SKILL.md + first-breath + sanctum population OUT OF SCOPE). Test count: 3 + 11 + 3 + 2 + 3 + 2 + 1 + 4 + 1 = **30 collectible test functions** (test_tracy_act_node_dispatch.py = 7 parse-branches per M-R15 exemption + 1 happy-path + 1 @llm_live + 1 vocab-loader-test + 1 W-R3 invariant test = 11 functions); ~16 K-floor units after parametrize-collapse. Effective ratio ~2.0Ã— floor / ~1.5Ã— target. Anti-padding-band-creep guard: dev agent at G6 DISMISSes drift beyond 30.

**Regression target at T8:** â‰¥220 passed / â‰¥3 skipped placeholder-key (was â‰¥210 at 2b.4 close projected; +10 at floor / +12 at target; +1 skip from the W-R5 DEFERRED-EPIC-28-1 sanctum lock test). Import-linter 3/3 KEPT; Ruff clean; Sandbox-AC PASS.

---

## Dev Agent Record

_(Populated during T1â€“T9 execution.)_

### T1 Readiness

- Sandbox AC validator PASS for 2b.5 story file.
- Generator path constraint discovered: `--from-skill` currently enforces `skills/bmad-agent-*`; created compatibility alias `skills/bmad-agent-tracy/SKILL.md` to unblock generation while runtime still sources from `skills/bmad_agent_tracy/`.

### T2-T7 Implementation Notes

- Implemented Tracy runtime at `app/specialists/tracy/`:
  - `graph.py` with reasoning-tier `_plan`, bounded `_act`, `manifest.parsed.*` taxonomy, two-sided trail-tagging, and no-op posture-selection tag emission.
  - `posture_dispatch.py` direct-import seam to `skills.bmad_agent_tracy.scripts.posture_dispatcher` + import-time vocabulary load from `vocabulary.yaml`.
  - `state.py` extended with `tracy_manifest: dict[str, Any] | None`.
- Parse precedence patched to match spec discriminator intent:
  - `empty` when results discriminator absent/empty,
  - `no-results` when explicit `query_attempted` present with empty list.
- Added Tracy specialist test surface (generator/act/wrapper/cascade/sanctum/gate/trail/state + scaffold conformance).
- Updated docs:
  - migration guide §12 framing + §12.12 Tracy row + verification commands.
  - anti-patterns A11 fifth example (snake_case skill-dir sub-shape).
  - deferred inventory follow-ons filed per AC-M.

### T8 Regression Evidence

- Tracy slice:
  - `.venv/Scripts/python.exe -m pytest tests/specialists/tracy tests/integration/scaffold_conformance/test_scaffold_tracy.py -q`
  - Result: **41 passed / 1 skipped**
- Specialists + scaffold conformance anchor:
  - `.venv/Scripts/python.exe -m pytest tests/specialists tests/integration/scaffold_conformance -q`
  - Result: **338 passed / 6 skipped**
- Ruff:
  - `.venv/Scripts/python.exe -m ruff check app/specialists/tracy tests/specialists/tracy tests/integration/scaffold_conformance/test_scaffold_tracy.py docs/dev-guide/langgraph-migration-guide.md docs/dev-guide/specialist-anti-patterns.md _bmad-output/planning-artifacts/deferred-inventory.md`
  - Result: **All checks passed**
- Import-linter:
  - `.venv/Scripts/lint-imports.exe`
  - Result: **3 kept / 0 broken**
- Sandbox AC:
  - `.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-2b-5-tracy-research-intent-shaper-scaffold-migration.md`
  - Result: **PASS**

### Party-Mode Review (3-agent: Winston + Murat + Amelia)

Top-line: GREEN after patch pass.

- PATCH applied
  1. Added direct-import seam pin in wrapper and seam-test coverage.
  2. Strengthened manifest parser with full required-row key/type checks.
  3. Fixed `empty` vs `no-results` discriminator behavior and test matrix alignment.
  4. Expanded two-sided act failure matrix for envelope decode branches.
  5. Filed all AC-M follow-ons in deferred inventory.
- DEFER
  1. Generator snake_case `--from-skill` acceptance remains a tooling gap; tracked via A11 and alias workaround.
- DISMISS
  1. Strict live nightly vocabulary gate deferred by design as a named follow-on, not a 2b.5 blocker.

### G6 Layered Code Review (Blind / Edge / Acceptance)

Top-line: GREEN after remediation.

- PATCH applied
  1. Parser contract hardening for missing-key/wrong-type/empty/no-results discrimination.
  2. Wrapper seam and SSOT validation tightened.
  3. Closure records synchronized (story status + deferred filings + sprint-status update).
- DEFER
  1. `migration-deferred-skip-decay-monitor` and `tracy-strict-vocabulary-llm-live-nightly` intentionally deferred as AC-M follow-ons.
- DISMISS
  1. Non-blocking alias-path ergonomics in generator CLI deferred to cross-cutting generator evolution.

### D12 Close Stub

1. Invariant preservation: Slab-1 substrate intact; C3 auto-emit advanced with Tracy row; bounded no-op wrapper path preserves current partial substrate contract.
2. Anti-pattern harvest: A11 fifth example added (snake_case skill-dir sub-shape); follow-ons filed for roster reconciliation and skip governance.
3. Migration-guide update: §12 framing and §12.12 Tracy inheritor row under §12.6 landed; verification commands expanded.
4. TEMPLATE compliance: R1-R7 upheld with bounded-scope defers explicit. Numeric anchors: Tracy slice 41/1; specialists+conformance 338/6; parser matrix includes malformed/missing-key/wrong-type/empty/no-results/vocabulary-violation + act failure matrix + one `@llm_live` skip-safe test.

### Completion Notes

- AC-B-OP remains **DEFERRED-PENDING-OPERATOR-WINDOW**.
- AC-M follow-ons filed:
  - `tracy-skill-persona-authoring-on-hybrid`
  - `tracy-fr54-cache-hit-baseline-measurement`
  - `slab-2-roster-reconciliation-tracy-status-update`
  - `migration-deferred-skip-decay-monitor`
  - `tracy-strict-vocabulary-llm-live-nightly`
