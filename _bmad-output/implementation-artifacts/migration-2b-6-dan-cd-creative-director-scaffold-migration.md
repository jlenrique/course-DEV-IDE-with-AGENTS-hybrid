# Migration Story 2b.6: Migrate Dan/CD (Creative Director) to 9-Node Scaffold

**Status:** done
**Sprint key:** `migration-2b-6-dan-cd-creative-director-scaffold-migration`
**Epic:** Slab 2b â€” sixth per-specialist migration; FIFTH inheritor of 2b.1 Gary TEMPLATE; THIRD populated-and-locked sanctum case (after Texas 2a.4 + Desmond 2b.4); narration category inheritor (Â§12.5 Irene parent + Desmond Â§12.12 peer).
**Pts:** 3 | **Gate:** single (per governance JSON `2b-6.expected_gate_mode = "single-gate"`, rationale: "Follows 2b.1 TEMPLATE"). **K-target:** ~1.4Ã— (target 13 / floor 10; clean inheritor, no R8 bounded-scope recalibration).

**Lean inheritor party-mode amendments applied 2026-04-25 (Murat + Amelia):** 4 RIDERs integrated:
- **M-R16 (NEW; codify in TEMPLATE v2.1):** R10 SSOT invariant test pattern is **two-test minimum** â€” (a) import-uniqueness grep + (b) live validator-rejection negative case (feed `_parse_directive` known-bad directive WITHOUT live LLM; assert `validator-failed` tag emitted AND validator-error-list non-empty; proves validator is wired, not stubbed). Test count for 2b.6: `test_cd_validator_ssot_invariant.py` becomes 2 tests; total collectible 26â†’27.
- **M-R17 (NEW):** Live LLM AC-B-LIVE asserts STRUCTURAL pass only (4 top-level keys + structurally-typed slide_mode_proportions/narration_profile_controls dicts), NOT full validator-PASS (sum-to-1.0 + 11 keys + experience_profile enum + profile-parity). Full validator semantics deferred to operator-gated AC-B-OP. Avoids flake from LLM nondeterminism + validator coupling.
- **A-CD-RIDER-1:** Pin validator entry-function contract in AC-B â€” `from scripts.utilities.creative_directive_validator import validate_creative_directive`; signature `validate_creative_directive(directive) -> list[str]`; empty list = valid; non-empty = tag `validator-failed` with `errors[0]` as discriminator detail. Hard-deps on `state/config/schemas/creative-directive.schema.json` + `state/config/experience-profiles.yaml` + `pyyaml` at call time.
- **A-CD-RIDER-2:** Pin R10 SSOT invariant test mechanism as AST-walk + regex-on-string-literals â€” `ast.parse` walk of `app/specialists/cd/` Python files; assert (a) exactly ONE `Import`/`ImportFrom` of `creative_directive_validator` in `graph.py` at module scope; (b) NO string literal in any module body matches `r'(slide_mode_proportions|narration_profile_controls|experience_profile)\s*[=:]'` outside test fixture paths.

Dan (CD lane) produces validator-clean creative directives for Marcus's resolver + Irene's narration. Act-body is **narration category** (Â§12.5 Irene parent) â€” LLM at `_act` for structured directive synthesis + creative_rationale authoring; NO external dispatch substrate. CD adds ONE row to Â§12.12 inheritor catalog matrix under Â§12.5 parent (per R3). **POPULATED-and-LOCKED sanctum** at `_bmad/memory/bmad-agent-cd/` (BOND/CAPABILITIES/CLONE-FORK-NOTICE/CREED/INDEX/MEMORY/PERSONA all present â€” verified 2026-04-25). **NEW A11 sub-shape** â€” skill-dir `bmad-agent-cd` uses LANE name (`cd`), not persona name (`dan`); first occurrence of lane-vs-persona drift class; harvest at AC-J (G6 reviews title-broadening per Winston W-R4 from 2b.5 â€” defaults to sub-bullet under existing A11 unless 6th example with 3rd sub-shape forces retitle, which Tracy 5th example was; CD is 6th but its sub-shape is novel â€” disposition decided at G6).

---

## T1 Readiness Block

Standing Pre-Flight items 1â€“10 same as 2b.2. Item 11: [`docs/dev-guide/specialist-migration-template.md`](../../docs/dev-guide/specialist-migration-template.md) v2 (R1â€“R12 apply).

### Slab 2b artifact-existence sweep â€” CD-specific deltas

- **C** Reference patterns: Desmond 2b.4 (closest narration inheritor; populated-and-locked sanctum precedent) + Irene 2a.2 (narration category origin).
- **F** `pyproject.toml` C3 contains 10 rows pre-CD (5 baseline + Gary + Vera + Quinn-R + Desmond + Tracy). CD auto-emit makes 11.
- **G** Cache-hit-rate (FR54) applicable (CD's directives have stable experience-profile prefix + per-run varying envelope). Defer to follow-on.
- **R2 importlib loader status:** CD has NO dispatch wrapper; loader-occurrences UNCHANGED at 3 (Kira + Vera + Quinn-R).
- **R10 SSOT trigger:** `scripts/utilities/creative_directive_validator.py` is the load-bearing SSOT for directive shape per CD SKILL.md "Every directive MUST follow `./references/creative-directive-contract.md` AND MUST pass `scripts/utilities/creative_directive_validator.py`." Triggers R10 invariant test pattern at AC-G.

### Epic-doc-vs-framework cross-check (per R6)

#### (a) Framework drifts

**Drift #1 â€” Skill-dir uses LANE name not persona name (A11 SIXTH example, NEW sub-shape):** CD's skill-dir is `bmad-agent-cd/` (lane name `cd`); runtime persona is `Dan`. Per CD SKILL.md "CD = lane (contracts, lane-matrix); Dan = persona." This is the **third A11 sub-shape**:
1. Sub-shape A (Irene/Gary/Vera/Quinn-R): persona-name vs descriptive-skill-name divergence (kebab-case)
2. Sub-shape B (Tracy 2b.5): snake_case-vs-kebab-case separator divergence
3. Sub-shape C (CD 2b.6): lane-vs-persona divergence (NEW)

**Per Winston W-R4 disposition rule from 2b.5: "G6 disposition default = sub-bullet under A11 unless a SIXTH example with a third sub-shape lands by 2b.5 close."** CD IS the 6th example AND introduces a 3rd sub-shape â€” **W-R4 condition triggers retitle consideration at G6**. Disposition options: (a) extend A11 with the lane-vs-persona sub-bullet only, (b) retitle A11 to "Persona/skill-dir naming convention drift from hybrid BMB normalization" (covering all three sub-shapes), (c) further title-broaden following A9 2a.4 precedent. **Default at story-author time: option (b) â€” retitle.** G6 may upgrade to (c) if a 4th sub-shape surfaces by close. Harvest at AC-J.

**Drift #2 â€” Model tier "long-context-balanced" not in selection_policy (A10 SIXTH example):** CD SKILL.md describes structured directive synthesis + experience-profile reasoning. Epic 2b.1 line 710 names CD as "long-context-balanced" tier. Maps to `tier_request: reasoning` â†’ `gpt-5.4`. A10 sixth example.

#### (b) TEMPLATE scope decisions

**Decision #1 â€” Bounded scope (per R1):** CD SKILL.md scopes (a) directive generation via Marcus envelope, (b) sanctum-bound rebirth + memory-persistence ritual. Migration scope = headless dispatch path (envelope-in â†’ directive-out). Memory-persistence sidecar concerns OUT OF SCOPE. NOT a bounded-scope-aggressive invocation â€” 1 substrate category OUT OF SCOPE only; R8 K-floor recalibration does NOT trigger.

**Decision #2 â€” NO dispatch wrapper (narration-only):** parallel to Desmond 2b.4 + Irene 2a.2. R2 sub-mechanism rule does NOT apply.

**Decision #3 â€” POPULATED-and-LOCKED sanctum (3rd occurrence after Texas 2a.4 + Desmond 2b.4):** CD's BMB sanctum at `_bmad/memory/bmad-agent-cd/` IS populated. AC-D applies populated-and-locked case + sha256 manifest pin. Sanctum baseline capture command per Amelia A-DESMOND-R1 (CRLFâ†’LF normalized).

**Decision #4 â€” `creative_directive_validator.py` as SSOT (R10 trigger):** the validator script IS the load-bearing contract for directive shape. Per R10, requires invariant test alongside parse-branch test: (a) parse-branch test exercises violation tag `directive.parsed.validator-failed`; (b) invariant test pins that the validator import-path is the only source-of-truth for directive shape (no hardcoded shape checks in `_act` body or graph.py).

---

## Story

As a **migration dev agent inheriting the 2b.1 TEMPLATE v2 (R1â€“R12)**,
I want **Dan/CD rehomed into `app/specialists/cd/` with the 9-node scaffold + narration-category act-body (LLM-only directive synthesis + creative_rationale authoring) + populated-and-locked sanctum cold-read (3rd occurrence) + per-R5 auto-emit C3 row + per-R10 SSOT invariant test for `creative_directive_validator.py` + Â§12.12 inheritor row added under Â§12.5 parent + A11 6th-example with potential title broadening at G6**,
So that **the narration category gains its second inheritor (Desmond + CD = 3 narration specialists with Irene), the populated-and-locked sanctum case is exercised a third time (proving the pattern generalizes across narration + tool-dispatch categories), the new R10 SSOT invariant test pattern lands its first inheritor exercise, and Slab 2b inheritor velocity continues**.

---

## Acceptance Criteria

All ACs are dev-agent-executable. CD carries ONE `@pytest.mark.llm_live` test (AC-B live LLM directive authoring against fixture envelope).

### AC-2b.6-A â€” Generator emits CD + auto-emits C3 row (per R5)

Per R5 + 2b.1 hermetic pattern. Test pin: `tests/specialists/cd/test_cd_generator_auto_emit_c3_row.py` â€” 3 tests using `temp_repo_root` fixture. Pre-baseline 5 â†’ post-emit 6 (in fixture); live repo at story close = 11 rows total.

Generator invocation:
```
.venv\Scripts\python.exe -m skills.bmad_create_specialist.scripts.generate \
  --name cd --mcp none --expertise-tier L4-creative-direction \
  --from-skill skills/bmad-agent-cd
```

**Naming note:** `--name cd` uses lane name (per skill-dir convention) NOT persona name `dan`. Generator NAME_PATTERN accepts `cd` (alphanumeric + lowercase per `generate.py:21`). Document `app/specialists/cd/` package name in Dev Agent Record + spec.

### AC-2b.6-B â€” CD `act` node wires NARRATION (LLM-only directive synthesis + validator-clean output)

- **Given** CD's `_act` (1) reads ModelResolutionEntry + reject if `cache_prefix_hash is None` (Winston W2); (2) extracts envelope payload from `state.cache_state.cache_prefix` (research brief + experience-profile request); (3) reads sanctum-cached directives from `_bmad/memory/bmad-agent-cd/MEMORY.md` for tuning patterns; (4) invokes LLM (`tier_request: reasoning` â†’ `gpt-5.4` per A10 6th example) for directive synthesis (`experience_profile`, `slide_mode_proportions`, 11 `narration_profile_controls`, `creative_rationale`); (5) parses + validates LLM output via `_parse_directive` helper that calls `creative_directive_validator.py` import (NOT subprocess) on the directive shape; (6) returns cache_state with `cd_directive` encoded as sorted-keys canonical JSON.
- **When** the dev agent implements `_act` per narration pattern (Desmond + Irene precedents).
- **Then** invoking `build_cd_graph()` with fixture envelope produces non-empty result containing `cd_directive` with all 4 required fields populated.
- **LOC budget per A-R3 carry-forward:** `_act â‰¤ 115 LOC`; `_parse_directive` helper extracted module-level (per Vera A-R9 / R10 SSOT pattern).
- **Tag namespace per Murat M-R2 + R9 (M-R12) precedence convention + R12 (M-R15) ceiling:** `directive.parsed.*` â€” tags `directive.parsed.ok / malformed / missing-key / wrong-type / empty / validator-failed`. Six parametrized cases. Within R12 default ceiling â€” no exemption needed. **R9 precedence pin:** `_parse_directive` evaluates tags in order `malformed â†’ missing-key â†’ wrong-type â†’ empty â†’ validator-failed â†’ ok`. Discriminator: `validator-failed` requires the directive to be structurally valid (passes `missing-key` + `wrong-type` checks) but fails `creative_directive_validator.py` semantic checks (e.g., `slide_mode_proportions` doesn't sum to 1.0 Â±0.001).
- **Validator entry-function contract pinned per A-CD-RIDER-1 (BINDING):** `from scripts.utilities.creative_directive_validator import validate_creative_directive`; signature `validate_creative_directive(directive) -> list[str]` â€” returns list of error messages (NOT bool, NOT raise). **Empty list = valid; non-empty = tag `validator-failed` with `errors[0]` as discriminator detail.** Validator hard-depends on `state/config/schemas/creative-directive.schema.json` + `state/config/experience-profiles.yaml` + `pyyaml` at call time. **Common-trap warning:** `if not validate_creative_directive(directive):` truthiness inverts logic (empty list is falsy â†’ "no errors" path); use `errors = validate_creative_directive(directive); if errors:` instead.
- **R10 SSOT invariant test (per M-R16 two-test minimum + A-CD-RIDER-2 AST mechanism, BINDING):** Two tests in `test_cd_validator_ssot_invariant.py`:
  1. **Import-uniqueness AST walk:** `ast.parse` walk of `app/specialists/cd/` Python files; assert (a) exactly ONE `Import`/`ImportFrom` of `creative_directive_validator` in `graph.py` at module scope; (b) NO string literal in any module body matches `r'(slide_mode_proportions|narration_profile_controls|experience_profile)\s*[=:]'` outside test fixture paths (no shape-key checks reimplemented in production code).
  2. **Live validator-rejection negative case (M-R16 sufficiency requirement):** feed `_parse_directive` a known-bad directive WITHOUT live LLM (e.g., `slide_mode_proportions = {"literal-text": 0.5, "literal-visual": 0.5, "creative": 0.5}` summing to 1.5); assert (a) returned tag is `directive.parsed.validator-failed` AND (b) validator-error-list is non-empty (proves validator is actually wired, not stubbed). Without this, future refactor replacing validator with `[]` always-pass stub would still PASS test #1 â€” false-green eliminated.
- **Live LLM test (`@pytest.mark.llm_live`) per M-R17 STRUCTURAL-PASS scope:** AC-B-LIVE asserts live `gpt-5.4` call produces structurally-shaped directive â€” (a) is a dict; (b) has all 4 top-level keys (`experience_profile`, `slide_mode_proportions`, `narration_profile_controls`, `creative_rationale`); (c) `slide_mode_proportions` is a dict with 3 mode keys; (d) `narration_profile_controls` is a dict. **Does NOT assert** sum-to-1.0, all-11-controls present, experience_profile enum match, profile-parity. Full validator-PASS deferred to operator-gated AC-B-OP. Avoids flake from LLM nondeterminism Ã— validator coupling per Murat M-R17 amendment.

### AC-2b.6-B-OP â€” Live operator-gated evidence (DEFERRED-PENDING-OPERATOR-WINDOW)

Operator runs CD against a real Marcus-staged experience-profile request; pastes directive into Completion Notes.

### AC-2b.6-C â€” Model cascade at `_plan` (per R7)

Trail-entry resolution at `_plan` per R7. Test pin: 2 tests.

### AC-2b.6-D â€” Sanctum cold-read at `_plan` (POPULATED-and-LOCKED â€” 3rd occurrence)

- **Given** CD's BMB sanctum at `_bmad/memory/bmad-agent-cd/` IS populated (verified 2026-04-25: BOND/CAPABILITIES/CLONE-FORK-NOTICE/CREED/INDEX/MEMORY/PERSONA â€” 7 files at story-author time).
- **Test pins (4 tests, mirroring Texas + Desmond pattern):**
  1. `test_cd_sanctum_fingerprint_deterministic_populated`.
  2. `test_cd_expertise_readme_lists_l4_references`.
  3. `test_cd_sanctum_lock_baseline_pinned` â€” hard sha256 equality; `CD_SANCTUM_LOCK_BASELINE` module-level constant. **Sanctum baseline capture command per Amelia A-DESMOND-R1** (CRLFâ†’LF normalized; substitute `bmad-agent-cd` for `bmad-agent-desmond` in the inline Python command).
  4. `test_cd_sanctum_lock_violation_raises_named_exception` â€” imports `SanctumLockViolation` from extracted shared module per Slab-2 cross-cutting refactor (depends on `slab-2a-close-followon-sanctum-lock-cross-cutting` having closed before 2b.6 dev-story open per Winston hard reactivation gate from 2b.3 + 2b.5 BLOCKER-2 batch-dev-cycle enforcement; if extraction story has CLOSED, import from `app.specialists._scaffold.sanctum_exceptions`; if PENDING, import from `app.specialists.texas.graph`).

### AC-2b.6-E â€” Gate-decision binding (precedent-inherited)

2 tests.

### AC-2b.6-F â€” Resolution trail (FR16 ninth per-specialist exercise)

1 test.

### AC-2b.6-G â€” CD shape-pin tests (per R4 + R10 SSOT invariant)

Per R4: `cd_directive: dict[str, Any] | None` (the creative directive package). 4 four-file-lockstep tests + 1 R10 SSOT invariant test (per AC-B). Total 5.

### AC-2b.6-H â€” Scaffold-conformance test registered

`tests/integration/scaffold_conformance/test_scaffold_cd.py` â€” 1 test.

### AC-2b.6-I â€” Migration-guide Â§12.12 grows ONE inheritor row (per R3)

Per R3, NEW row in Â§12.12 under Â§12.5 (Irene narration) parent:

| Specialist | Parent Â§12.x | Seam divergence | Sanctum case | Harvest contributions | Story |
|---|---|---|---|---|---|
| CD (Dan) | Â§12.5 (Irene narration) | NO dispatch substrate; SSOT validator import at module load (`creative_directive_validator.py`) | populated-and-locked (3rd occurrence after Texas + Desmond) | A10 6th example + A11 6th example with NEW lane-vs-persona sub-shape (W-R4 retitle trigger â†’ G6 disposition) | 2b.6 |

Update Â§12.5 framing: "ninth specialist proven on 9-node scaffold; narration category now hosts 3 inhabitants (Irene + Desmond + CD); 3 populated-and-locked sanctum cases proves the pattern generalizes."

### AC-2b.6-J â€” Anti-pattern catalog harvest (A10 6th + A11 6th with W-R4 retitle trigger)

- **A10 sixth example bullet:** CD `tier_request` "long-context-balanced" not in selection_policy; maps to `reasoning` â†’ `gpt-5.4`.
- **A11 sixth example + W-R4 RETITLE TRIGGER:** CD skill-dir `bmad-agent-cd` uses LANE name; persona is Dan. NEW sub-shape (third under A11, after persona-name divergence + snake_case divergence). **G6 disposition decides retitle.** Default per W-R4 (if 6th example with 3rd sub-shape lands by 2b.5 close â€” CD lands at 2b.6, slightly past the named cap, but within the disposition window): retitle A11 to "Persona/skill-dir naming convention drift from hybrid BMB normalization."

### AC-2b.6-K â€” TEMPLATE compliance (per R1â€“R12)

R1â€“R12 honored without deviation. R8 K-floor recalibration does NOT trigger (only 1 substrate category OOO). R10 SSOT invariant test pattern lands first inheritor exercise.

### AC-2b.6-L â€” D12 close protocol (single-gate; FOUR-line per A-R7)

1. **Invariant preservation:** Slab-1 substrate intact; auto-emit C3 row machinery fired (C3 10â†’11 in live repo); 3rd populated-and-locked sanctum case lands cleanly; R10 SSOT invariant test pattern lands first inheritor exercise.
2. **Anti-pattern harvest:** A10 6th + A11 6th example with W-R4 retitle trigger (G6 disposition).
3. **Migration-guide update:** Â§12.12 inheritor row added under Â§12.5; framing updated.
4. **TEMPLATE compliance:** R1â€“R12 v2 honored. Numeric anchors: `_act` LOC measured (â‰¤115); 6 parse-branch tests; 1 @llm_live; sanctum populated-and-locked (4 tests); 1 R10 SSOT invariant test; pyproject.toml C3 row count 5â†’6 fixture / 10â†’11 live.

### AC-2b.6-M â€” Sprint-status state-flips at filing AND at close

At filing: ready-for-dev. At close: done. File `cd-fr54-cache-hit-baseline-measurement` follow-on.

---

## File Structure Requirements

### NEW files

```
app/specialists/cd/
â”œâ”€â”€ __init__.py                                 # generator-emitted
â”œâ”€â”€ graph.py                                    # generator-emitted; _act body filled at T2 (narration-only)
â”œâ”€â”€ state.py                                    # generator-emitted; CdReturn extended with cd_directive
â”œâ”€â”€ model_config.yaml                           # generator-emitted; reasoning-tier comments
â”œâ”€â”€ expertise/
â”‚   â”œâ”€â”€ README.md                               # generator-emitted; dotted reference table for CD references (creative-directive-contract + profile-targets + capability-authoring)
â”‚   â””â”€â”€ __init__.py

# NO dispatch wrapper module

tests/specialists/cd/
â”œâ”€â”€ __init__.py                                 # NEW (per A-R6)
â”œâ”€â”€ test_cd_generator_auto_emit_c3_row.py       # NEW (3 tests; AC-A)
â”œâ”€â”€ test_cd_act_node_authoring.py               # NEW (~8 tests; AC-B with 6 parse-branches + 1 happy-path + 1 @llm_live)
â”œâ”€â”€ test_cd_validator_ssot_invariant.py         # NEW (2 tests per M-R16 two-test minimum; AC-B R10 SSOT invariant â€” import-uniqueness AST walk + live validator-rejection negative case)
â”œâ”€â”€ test_cd_model_cascade.py                    # NEW (2 tests; AC-C)
â”œâ”€â”€ test_cd_sanctum_cold_read.py                # NEW (4 tests; AC-D POPULATED)
â”œâ”€â”€ test_cd_gate_decision_binding.py            # NEW (2 tests; AC-E)
â”œâ”€â”€ test_cd_resolution_trail.py                 # NEW (1 test; AC-F)
â””â”€â”€ test_cd_state_shape.py                      # NEW (4 tests; AC-G)

tests/integration/scaffold_conformance/
â””â”€â”€ test_scaffold_cd.py                         # NEW (1 test; AC-H)

tests/fixtures/specialists/cd/
â”œâ”€â”€ golden_envelope.json                        # NEW (experience-profile request)
â””â”€â”€ golden_return.json                          # NEW (with cd_directive populated; validator-clean shape)
```

### MODIFIED files

- `docs/dev-guide/langgraph-migration-guide.md` â€” Â§12.12 new row under Â§12.5; Â§12.5 framing updated.
- `docs/dev-guide/specialist-anti-patterns.md` â€” A10 6th + A11 6th example with W-R4 retitle trigger.
- `_bmad-output/planning-artifacts/deferred-inventory.md` â€” file `cd-fr54-cache-hit-baseline-measurement` per AC-M.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` â€” per AC-M.
- `pyproject.toml` â€” auto-emitted; **NOT manually edited**.

---

## Testing Requirements

**K-target ~1.4Ã— (target 13 / floor 10).** Clean inheritor â€” no R8 recalibration. Test count: 3 + 8 + 2 + 2 + 4 + 2 + 1 + 4 + 1 = **27 collectible test functions** (test_cd_validator_ssot_invariant.py = 2 tests per M-R16); ~20 K-floor units after parametrize-collapse. Effective ratio ~2.0Ã— floor / ~1.5Ã— target.

**Regression target at T8:** â‰¥230 passed / â‰¥3 skipped placeholder-key. Import-linter 3/3 KEPT; Ruff clean; Sandbox-AC PASS.

---

## Dev Agent Record

_(Populated during T1â€“T9 execution.)_


### T8 Regression Evidence

- Specialist-wave slice validation: 184 passed / 1 skipped across cd/enrique/wanda/kim/vyx/aria/mira/tamara + scaffold conformance.
- Specialists + scaffold conformance anchor: 525 passed / 7 skipped.
- uff check clean on touched specialist/test paths.
- lint-imports 3/3 kept.
- Sandbox-AC validator PASS for stories 2b.6-2b.13.

