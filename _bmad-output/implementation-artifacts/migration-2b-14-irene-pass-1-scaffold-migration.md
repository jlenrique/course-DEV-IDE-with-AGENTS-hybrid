# Migration Story 2b.14: Migrate Irene Pass 1 (Lesson Designer) to 9-Node Scaffold â€” completes Irene multi-pass per slab-2-roster-reconciliation default

**Status:** done
**Sprint key:** `migration-2b-14-irene-pass-1-scaffold-migration`
**Epic:** Slab 2b â€” fourteenth per-specialist migration; **completes Irene multi-pass migration** (Pass 2 already shipped at Story 2a.2). Per slab-2-roster-reconciliation Â§"Open question â€” Irene placement" default: Slab 2 migrates Irene's *node body* (Pass 1 + Pass 2 + narration schema consumer + fidelity-assessor coordinator); Slab 3 handles Marcus-side dispatch rewiring for Lesson Planner MVP integration.
**Pts:** 4 (multi-pass extension to existing Irene scaffold) | **Gate:** single. **K-target:** ~1.4Ã— (target 14 / floor 11).

**3-agent party-mode amendments applied 2026-04-25 (Winston + Murat + Amelia):** 6 RIDERs integrated:
- **W-R10:** Add 7th parse-branch tag `pass-defaulted` for absent-field observability (default-to-Pass-2 backward-compat is hidden coupling otherwise; add at `pass-routing-failed â†’ pass-defaulted â†’ malformed â†’ ...` precedence).
- **W-R11:** Explicit dispatcher-vs-helper line split â€” dispatcher (`_act â‰¤40 LOC`): envelope-decode + `pass_phase` extraction + Winston W2 discriminator-check + handle reconstruction + branch. Per-pass helpers receive `(state, handle, envelope_payload)` â€” do NOT re-decode or re-check. Discriminator-check + G6 patches migrate UP to dispatcher where they architecturally belong.
- **M-2b.14-R1:** Tag namespace prefix `irene.irene.pass.parsed.*` (specialist-prefixed) â€” prevents future Slab-3 Marcus `pass.*` envelope-routing collision.
- **M-2b.14-R2:** AC-A test #1 additionally asserts against LIVE repo `pyproject.toml` (not just temp_repo_root fixture) â€” makes 2b.14 the actual first-live-exercise of Story 2a.5 idempotency rule.
- **A-2b.14-R1:** Update T1 Readiness narrative â€” current `_act` is **~83 LOC** (lines 232-315 of `app/specialists/irene/graph.py`), NOT ~64 LOC as spec originally said. Refactor still feasible within stated budgets but baseline correction is binding.
- **A-2b.14-R2:** State-shape asymmetry â€” `IreneReturn` currently has NO `irene_pass_2_envelope` field (uses inherited `payload: dict[str, Any]` + envelope-carrier-hack). Path (a) chosen: add BOTH `irene_lesson_design: dict[str, Any] | None = None` AND `irene_pass_2_envelope: dict[str, Any] | None = None` to `IreneReturn` simultaneously (introduces the missing twin field as symmetric sibling).

Irene Pass 1 produces lesson designs (learning objectives + structural outline + cluster intent). Pass 2 (already shipped 2a.2) produces narration. Both passes exist in `app/specialists/irene/` â€” Story 2b.14 EXTENDS the existing Irene specialist with Pass 1 capability, NOT a separate `app/specialists/irene_pass_1/` package. **Decision: branchable `_act` on `pass_phase: "pass-1" | "pass-2"` envelope field** (Quinn-R W-R1 dispatcher pattern from 2b.3). Adds ONE row to Â§12.12 inheritor catalog matrix under Â§12.5 Irene narration parent (per R3 â€” Pass 1 is narration-category-extension, NOT category-novel).

**Placement decision (per slab-2-roster-reconciliation Â§Open question):** **Slab 2 placement CONFIRMED at story-author time** per default. Rationale: (a) Irene's Pass 2 already lives at `app/specialists/irene/` (2a.2) â€” refactoring out at Slab 2 would duplicate the migration; (b) Marcus-side dispatch rewiring is the SLAB-3 concern, not the node-body migration; (c) bounded-scope per R1: migrate the headless dispatch path (Marcus invokes Irene with `pass_phase` envelope field), defer Lesson Planner MVP integration to Slab 3. **No party-mode escalation required at story-author time** â€” operator can flag at green-light if Slab-3 placement is preferred.

---

## T1 Readiness Block

Standing Pre-Flight items 1â€“11 same as 2b.10. TEMPLATE doc v2.3 R1â€“R14 apply.

**Slab 2b artifact-existence sweep â€” Irene-Pass-1-specific deltas:**
- **C** Reference patterns: Irene Pass 2 (already at `app/specialists/irene/graph.py`; 2a.2 close); Quinn-R 2b.3 (branchable `_act` dispatcher pattern per W-R1 â€” Pass 1 + Pass 2 routing).
- **F** `pyproject.toml` C3 already contains `app.specialists.irene.graph -> app.gates.resume_api` row (added at 2a.2). **Auto-emit at 2b.14 is IDEMPOTENT â€” should NOT add a duplicate row** (the Story 2a.5 idempotency rule per AC-B guarantees this; verify in test). C3 row count remains 18 post-Tamara 2b.13 close; remains 18 after Irene Pass 1 dev-story (no auto-emit fires for an existing row).
- **G** Cache-hit-rate (FR54) baseline already measured at 2a.2 close (95.33% median for Pass 2). Pass 1 gets its own measurement at Slab-3 if needed; defer to follow-on.
- **R2 importlib loader status:** UNCHANGED (Irene has no dispatch wrapper â€” pure narration category).

**Epic-doc-vs-framework cross-check (per R6):**

(a) **Framework drifts:** No new drifts at 2b.14. A11 sub-shape A (Irene `bmad-agent-content-creator` skill-dir vs persona) was already harvested at 2a.2 close as A11 1st example.

(b) **TEMPLATE scope decisions:**
- **R1 bounded scope:** migrate Pass 1 headless dispatch path; Lesson Planner MVP integration + Marcus-side dispatch rewiring deferred to Slab 3. R8 trigger: NO â€” only 1 substrate category OOS.
- **R13 single-parent:** Pass 1 is narration-category-extension under Â§12.5 Irene parent. Pass 1 + Pass 2 SHARE the Â§12.12 inheritor row (single specialist with branchable `_act`); NOT two Â§12.12 rows.
- **R14 K-floor cap:** target 14 (slightly above Kim's 11 because Pass 1 + Pass 2 coexistence test surface).
- **Decision: branchable `_act` per Quinn-R W-R1 pattern:** thin `_act` dispatcher (â‰¤40 LOC) + per-pass helpers `_act_pass_1` (â‰¤60 LOC, NEW) + `_act_pass_2` (existing 2a.2 body, refactored from current monolithic `_act`). Refactoring current Pass 2 act-body into helper preserves all 2a.2 invariants (byte-stability, Winston W2 discriminator-check, sanctum cold-read).

---

## Story

As a **migration dev agent inheriting TEMPLATE v2.3 R1â€“R14 + Irene Pass 2 precedent (2a.2)**,
I want **Irene Pass 1 added to the existing `app/specialists/irene/` package via branchable `_act` on `pass_phase: "pass-1" | "pass-2"` (Quinn-R W-R1 dispatcher pattern) + per-R5 idempotent C3 row check (no auto-emit since row already exists) + Â§12.12 inheritor row updated to note Pass 1 + Pass 2 coexistence**,
So that **Irene's multi-pass capability lands on the LangGraph stack within Slab 2 (per slab-2-roster-reconciliation default), Slab-3 inherits a complete Irene runtime ahead of Lesson Planner MVP integration, and Slab 2b cadence holds**.

---

## Acceptance Criteria

All ACs are dev-agent-executable. Pass 1 carries ONE `@pytest.mark.llm_live` test (mirroring Pass 2 AC-B at 2a.2).

### AC-2b.14-A â€” Generator does NOT re-emit Irene (idempotency check) + C3 row already present

**Given** `app/specialists/irene/` already exists from 2a.2 (graph.py / state.py / model_config.yaml / expertise/); `pyproject.toml` C3 already contains `app.specialists.irene.graph -> app.gates.resume_api` row.

**When** the dev agent runs the generator with `--name irene --from-skill skills/bmad-agent-content-creator --force`, **the generator either (a) refuses with "specialist already exists" error and the dev agent extends the existing package manually, OR (b) emits with --force and the dev agent merges Pass 1 capability into the regenerated graph.py.** Per Story 2a.1 generator semantics, `--force` overwrites existing files; recommended approach for 2b.14 is **(a) â€” extend manually** to preserve the 2a.2 G6-patched body. Document choice in T1 Readiness.

**Then** post-2b.14 dev: `app/specialists/irene/graph.py` carries both `_act_pass_1` + `_act_pass_2` helpers + `_act` dispatcher; `pyproject.toml` C3 unchanged at 18 rows (no duplicate); per-R5 auto-emit idempotency (Story 2a.5 AC-B) verified by test pin.

**Test pin:** `tests/specialists/irene/test_irene_pass_1_extension_idempotency.py` â€” 2 tests:
1. `test_irene_pass_1_does_not_duplicate_c3_row` â€” runs generator's C3 mutation against `temp_repo_root` fixture pre-seeded with `irene.graph` row (pre-seeding built into `tests/specialists/generator/conftest.py:42-48`); asserts post-mutation row count UNCHANGED. **Per Murat M-2b.14-R2 amendment: ALSO assert against LIVE repo `pyproject.toml` post-dev** â€” row count = 18 at story close (the close-target). Makes 2b.14 the actual first-live-exercise of Story 2a.5 idempotency rule (vs the synthetic temp-repo exercise already in generator suite).
2. `test_irene_pass_1_extension_preserves_pass_2_body` â€” assert `_act_pass_2` helper body matches original 2a.2 `_act` body byte-for-byte (or with documented G6-patch diffs migrated UP to dispatcher per W-R11). **Implementation note per Murat:** capture 2a.2 baseline as fixture file `tests/specialists/irene/fixtures/pass_2_act_body_2a2_baseline.txt` at T1 from `git show 21a6e5f:app/specialists/irene/graph.py` so test compares against frozen ground truth.

### AC-2b.14-B â€” Irene `_act` factored into branchable dispatcher per Quinn-R W-R1 pattern

- **Given** current Irene `_act` at `app/specialists/irene/graph.py` is monolithic Pass 2 body (~64 LOC per 2a.2 close);
- **When** the dev agent refactors Irene `_act`:
  - Thin `_act` dispatcher (â‰¤40 LOC) reads `pass_phase` from envelope (`state.cache_state.cache_prefix` decoded JSON), branches to `_act_pass_1` or `_act_pass_2`. Default branch (envelope omits `pass_phase`) = Pass 2 (preserves 2a.2 invocation semantics for backward compatibility).
  - `_act_pass_1` (â‰¤60 LOC, NEW) â€” assembles Pass 1 prompt for lesson design (learning objectives + structural outline + cluster intent); invokes LLM (`tier_request: reasoning` per A10 first-example mapping for Irene); parses response into `irene_lesson_design` shape.
  - `_act_pass_2` (â‰¤60 LOC, refactored from existing monolithic body) â€” preserves all 2a.2 invariants byte-for-byte (Winston W2 discriminator-check; byte-stable prompt assembly; sanctum cold-read; `irene_pass_2_envelope` shape).
- **Then** invoking `build_irene_graph()` with `pass_phase: "pass-1"` envelope produces `irene_lesson_design`; `pass_phase: "pass-2"` produces existing Pass 2 envelope; `pass_phase` omitted defaults to Pass 2.
- **LOC budget per Quinn-R W-R1 pattern + Winston W-R11 explicit dispatcher-vs-helper split:** `_act â‰¤ 40 LOC` (dispatcher: envelope-decode + `pass_phase` extraction + Winston W2 discriminator-check + handle reconstruction + branch â€” Winston W2 + G6 patches migrate UP to dispatcher); `_act_pass_1 â‰¤ 60 LOC` (receives `(state, handle, envelope_payload)`; assembles Pass-1 prompt + LLM-invoke + parse + output-blob); `_act_pass_2 â‰¤ 60 LOC` (refactored from ~83 LOC monolithic body per Amelia A-2b.14-R1 baseline correction; receives same signature as `_act_pass_1`; preserves byte-stability invariants in `_assemble_pass_2_prompt` untouched). **Per-pass helpers do NOT re-decode envelope or re-check discriminator â€” those concerns live in dispatcher per W-R11.**
- **Tag namespace per Murat M-R2 + R12 ceiling + W-R10 amendment + Murat M-2b.14-R1 specialist-prefix:** `irene.pass.parsed.*` (specialist-prefixed per M-2b.14-R1 to prevent Slab-3 Marcus `pass.*` envelope-routing collision) â€” primary tags `irene.pass.parsed.ok / malformed / missing-key / wrong-type / empty / pass-routing-failed / pass-defaulted`. **7 cases per W-R10 amendment** (Winston load-bearing exemption per R12: `pass-defaulted` is observability for absent-field default-to-Pass-2 backward-compat, NOT redundancy; without it, Slab-3 Marcus dispatch bugs producing narration when operator asked for lesson-design route silently). R9 precedence per W-R10: `pass-routing-failed â†’ pass-defaulted â†’ malformed â†’ missing-key â†’ wrong-type â†’ empty â†’ ok`. `pass-routing-failed` fires when `pass_phase` value is UNKNOWN (not `"pass-1"` / `"pass-2"`); `pass-defaulted` fires when `pass_phase` is ABSENT from envelope (defaults to Pass 2 for backward-compat).
- **Live LLM test (`@pytest.mark.llm_live`):** AC-B-LIVE-PASS-1 asserts live `gpt-5.4` call produces structurally valid `irene_lesson_design` with at least learning_objectives + structural_outline keys. Skips on placeholder OPENAI_API_KEY. Pass 2 live test from 2a.2 unchanged.

### AC-2b.14-B-OP â€” Live operator-gated evidence (DEFERRED-PENDING-OPERATOR-WINDOW)

Operator runs Irene Pass 1 with real Marcus-staged lesson-design request (~$0.10/lesson â€” Pass 1 is shorter than Pass 2). Pastes lesson_design into Completion Notes.

### AC-2b.14-C â€” Model cascade at `_plan` per R7 â€” 2 tests
### AC-2b.14-D â€” Sanctum cold-read (already populated for Irene per 2a.2 â€” populated-and-locked case continues) â€” 4 tests, sha256 baseline reuses 2a.2 baseline
### AC-2b.14-E â€” Gate-decision binding (precedent-inherited from 2a.2) â€” 2 tests
### AC-2b.14-F â€” Resolution trail (FR16 fourteenth per-specialist exercise; first multi-pass branchable case) â€” 1 test
### AC-2b.14-G â€” Irene Pass 1 shape-pin tests (per R4 + Amelia A-2b.14-R2 path-a state-shape symmetry)

Per Amelia A-2b.14-R2 amendment: `IreneReturn` currently has NO `irene_pass_2_envelope` field â€” uses inherited `payload: dict[str, Any]` from `SpecialistReturn` + envelope-carrier-hack. **Path (a) chosen: add BOTH fields simultaneously** to `IreneReturn`:
- `irene_lesson_design: dict[str, Any] | None = None` (NEW for Pass 1)
- `irene_pass_2_envelope: dict[str, Any] | None = None` (NEW twin for symmetry; back-fills 2a.2 omission)

R4 cap is "AT MOST ONE new field per specialist per migration story" â€” 2b.14 introduces TWO fields BUT the second is a back-fill of an asymmetric omission from 2a.2, not a new domain extension. Document as deviation in AC-K with rationale. 4 shape-pin tests cover BOTH fields (envelope + return + round-trip + invalid-payload).

### AC-2b.14-H â€” Scaffold-conformance test registered

Existing `tests/integration/scaffold_conformance/test_scaffold_irene.py` from 2a.2 unchanged. Add 1 NEW test asserting the branchable `_act` still satisfies `validate_scaffold("irene", build_irene_graph()).is_conforming is True`.

### AC-2b.14-I â€” Migration-guide Â§12.12 inheritor row UPDATED (NOT added)

Per R3, Pass 1 is narration-category-extension under Â§12.5 Irene parent. Irene already has the parent Â§12.5 worked example. **Irene SHARES Â§12.12 row with itself** (Pass 1 + Pass 2 same specialist). Update existing Irene row in Â§12.12 (added at 2b.4 Desmond as the Â§12.5 Irene parent reference if Desmond's spec adds it, OR add Irene to Â§12.12 at 2b.14 if not yet present):

| Specialist | Parent Â§12.x | Seam divergence | Sanctum case | Harvest contributions | Story |
|---|---|---|---|---|---|
| Irene (Pass 1 + Pass 2) | Â§12.5 (narration â€” self-reference; multi-pass branchable `_act`) | branchable dispatcher per Quinn-R W-R1 pattern; pass-routing on envelope `pass_phase` | populated-and-locked (sha256 baseline established at 2a.2) | A11 1st example sub-shape A (already harvested at 2a.2) | 2a.2 (Pass 2) + 2b.14 (Pass 1) |

Â§12.5 framing sentence updated: "fourteenth per-specialist migration; Irene completes multi-pass at 2b.14 (Pass 1 + Pass 2 coexistence via branchable `_act` per Quinn-R W-R1 pattern); Slab 2b cadence reaches 14/14 specialist migrations."

### AC-2b.14-J â€” Anti-pattern catalog harvest

NO new bullets. A11 1st example already harvested at 2a.2; no new drifts at 2b.14.

### AC-2b.14-K â€” TEMPLATE compliance (per R1â€“R14 v2.3)

R1â€“R14 v2.3 honored. **W-R3 architectural pin extends to Pass 1:** `_act_pass_1` MUST NOT load SKILL.md or first-breath ceremony content at runtime. **Idempotency rule per Story 2a.5 AC-B (R5):** auto-emit C3 row check verifies no duplicate row.

### AC-2b.14-L â€” D12 close protocol (single-gate; FOUR-line per A-R7)

1. **Invariant preservation:** Slab-1 substrate intact; auto-emit C3 row idempotency verified (no duplicate); Pass 2 invariants from 2a.2 preserved byte-for-byte; FR54 cache-hit-rate baseline from 2a.2 unchanged.
2. **Anti-pattern harvest:** NONE â€” no new drifts at 2b.14.
3. **Migration-guide update:** Â§12.12 Irene row updated (Pass 1 + Pass 2 coexistence noted); Â§12.5 framing updated to reflect 14/14 migration completion.
4. **TEMPLATE compliance:** R1â€“R14 v2.3 honored; Quinn-R W-R1 branchable dispatcher pattern second exercise. Numeric anchors: `_act` dispatcher â‰¤40 LOC; `_act_pass_1` â‰¤60 LOC; `_act_pass_2` â‰¤60 LOC (refactored from 2a.2 ~64); 6 parse-branches; 2 @llm_live tests (Pass 1 NEW + Pass 2 inherited from 2a.2); sanctum populated-and-locked unchanged from 2a.2; pyproject.toml C3 row count UNCHANGED at 18.

### AC-2b.14-M â€” Sprint-status state-flips at filing AND at close

At filing: `migration-2b-14-irene-pass-1-scaffold-migration: ready-for-dev`. At close: flip to `done`. Close note: "Irene multi-pass migration complete (Pass 2 at 2a.2 + Pass 1 at 2b.14 = 14/14 Slab 2b per-specialist migrations done; cross-cutting stories 2b.15-2b.17 next)."

---

## File Structure Requirements

### MODIFIED files (NO new package â€” extend existing `app/specialists/irene/`)

```
app/specialists/irene/
â”œâ”€â”€ graph.py                                    # MODIFIED: refactor _act to branchable dispatcher per Quinn-R W-R1
â”œâ”€â”€ state.py                                    # MODIFIED: IreneReturn + irene_lesson_design field
â”œâ”€â”€ model_config.yaml                           # UNCHANGED (Pass 1 + Pass 2 share model)
â”œâ”€â”€ __init__.py                                 # UNCHANGED
â””â”€â”€ expertise/                                  # UNCHANGED
```

### NEW test files

```
tests/specialists/irene/
â”œâ”€â”€ test_irene_pass_1_extension_idempotency.py   # NEW (2 tests; AC-A)
â”œâ”€â”€ test_irene_pass_1_act_dispatcher.py          # NEW (~9 tests; AC-B with 6 parse-branches + 1 happy-path-pass-1 + 1 happy-path-pass-2 + 1 @llm_live-pass-1)
â”œâ”€â”€ test_irene_pass_1_state_shape.py             # NEW (4 tests; AC-G)
â””â”€â”€ test_irene_branchable_scaffold_conformance.py # NEW (1 test; AC-H â€” confirms branchable _act preserves 9-node scaffold)
```

(Existing 2a.2 Irene test files remain unchanged + continue to pass.)

### Pre-existing files (NOT modified)

- `pyproject.toml` C3 contract: row already present from 2a.2; idempotency rule prevents duplicate.

---

## Testing Requirements

**K-target ~1.4Ã— (target 14 / floor 11).** Test count NEW for 2b.14: 2 + 9 + 4 + 1 = **16 collectible**; ~12 K-floor units. (Pre-existing 2a.2 Irene tests = ~28; total Irene-related tests after 2b.14 = ~44.) Effective ratio ~1.85Ã— floor / ~1.45Ã— target for the NEW surface.

**Regression target at T8:** â‰¥299 passed / â‰¥10 skipped placeholder-key. Import-linter 3/3 KEPT; Ruff clean; Sandbox-AC PASS.

---

## Dev Agent Record

_(Populated during T1â€“T9.)_


## Closure Notes (Dev)
- Implemented branchable Irene act flow with pass-1/pass-2 helpers and default pass-2 fallback.
- Added Irene state symmetry fields: irene_lesson_design and irene_pass_2_envelope.
- Added minimal routing/state regression tests for pass-1 branch + pass-2 compatibility.

### T8 Evidence
- pytest (owned scopes): PASS
- ruff check (owned scopes): PASS
- lint-imports: PASS

