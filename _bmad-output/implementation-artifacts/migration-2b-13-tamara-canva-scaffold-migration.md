# Migration Story 2b.13: Migrate Tamara (Canva Visual Designer) to 9-Node Scaffold â€” operator-instructions Â§12.13 inheritor

**Status:** done
**Sprint key:** `migration-2b-13-tamara-canva-scaffold-migration`
**Epic:** Slab 2b â€” thirteenth per-specialist migration; FOURTH (LAST) inheritor of operator-instructions category Â§12.13 (Kim/Vyx/Aria/Mira siblings).
**Pts:** 2 (pure inheritor; pure-shell per slab-2-roster-reconciliation; lightest specialist of Slab 2b) | **Gate:** single. **K-target:** ~1.4Ã— (target 11 / floor 8 â€” R14 cap).

Tamara (Canva persona) is operator-instructions thin node â€” produces design specifications, template recommendations, brand-safe visual direction, and Canva editor instructions. Per slab-2-roster-reconciliation: "Pure shell per 2026-03-26 capability audit (Canva API cannot edit elements). Migration is an envelope + 'guidance only' return." **No external dispatch substrate, no LLM at specialist layer at runtime.** Mirrors Kim/Vyx/Aria/Mira pattern. Adds ONE row to Â§12.12 under Â§12.13 parent. **CLOSES the operator-instructions inheritor wave** (Kim parent + 4 inheritors total).

---

## T1 Readiness Block

Standing Pre-Flight items 1â€“11 same as 2b.10. TEMPLATE doc v2.3 R1â€“R14 apply.

**Slab 2b artifact-existence sweep â€” Tamara-specific deltas:**
- **C** Reference patterns: Kim 2b.9 parent + Vyx/Aria/Mira siblings.
- **F** `pyproject.toml` C3 contains 17 rows pre-Tamara. Auto-emit makes 18.
- **G** FR54 N/A.
- **R2 importlib loader status:** UNCHANGED.

**Epic-doc-vs-framework cross-check (per R6):**

(a) **Framework drifts:** Drift #1 â€” Skill-dir `bmad-agent-canva` (vendor name) vs persona `Tamara`. A11 13th example sub-shape D. **By 2b.13, A11 sub-shape D has 5+ examples (Enrique/Wanda/CourseArc/Vyond/Articulate/Midjourney/Canva); G6 may consider sub-shape consolidation pattern (no further harvest needed beyond 5th example per harvest-gate "after 5 examples, pattern is established").**

(b) **TEMPLATE scope decisions:**
- **R1 bounded scope:** headless deterministic instruction assembly only.
- **R13 single-parent:** Â§12.13 Kim inheritor.
- **R14 K-floor cap:** target 11 / floor 8.
- **Sanctum:** BMB sanctum at `_bmad/memory/bmad-agent-canva/` does NOT exist; sidecar at `_bmad/memory/tamara-sidecar/` (legacy). Graceful-degrade.

---

## Story

As a **migration dev agent inheriting TEMPLATE v2.3 R1â€“R14 + Kim Â§12.13 pattern**,
I want **Tamara (Canva) rehomed into `app/specialists/tamara/` mirroring Kim's operator-instructions thin-node pattern + per-R5 auto-emit C3 row + ONE row in Â§12.12 under Â§12.13 parent + closes the operator-instructions inheritor wave**,
So that **the operator-instructions category Â§12.13 reaches its full inheritor count (Kim + 4 inheritors), Slab 2b's per-specialist migration cadence completes ahead of cross-cutting stories 2b.15-2b.17**.

---

## Acceptance Criteria

All ACs are dev-agent-executable. Tamara does NOT carry any `@pytest.mark.llm_live` test.

### AC-2b.13-A â€” Generator emits Tamara + auto-emits C3 row (per R5)
3 tests using `temp_repo_root` fixture. Generator: `--name tamara --mcp none --expertise-tier L4-canva-design --from-skill skills/bmad-agent-canva`.

### AC-2b.13-B â€” Tamara `act` node mirrors Kim Â§12.13 operator-instructions pattern
Per Kim Â§12.13: deterministic spec assembly via `_assemble_design_spec(envelope, registry)` helper. Tag namespace `instructions.parsed.*` (parameters: design_specifications, template_recommendations, brand_visual_direction, editor_instructions). 6 primary tags + M-R19 secondary-tag.

**LOC budget per Amelia A-BATCH-R1 amendment 2026-04-25 (soft RIDER for Tamara 4-template assembly):** `_act â‰¤ 80 LOC`; `_assemble_design_spec â‰¤ 75 LOC` (Tamara has 4 templates: design-spec / template-recommendation / brand-direction / editor-instruction â€” vs Kim's 3-template; +15 LOC headroom over Kim baseline). G6 reviewer treats overrun â‰¤75 LOC as advisory, NOT MUST-FIX.

### AC-2b.13-C through AC-2b.13-H â€” Mirror Kim pattern (2+3+2+1+4+1 = 13 tests)

### AC-2b.13-I â€” Â§12.12 inheritor row

| Specialist | Parent Â§12.x | Seam divergence | Sanctum case | Harvest contributions | Story |
|---|---|---|---|---|---|
| Tamara (Canva) | Â§12.13 (operator-instructions) | NO seam divergence (pure-shell; Canva API cannot edit elements) | graceful-degrade | A11 13th example sub-shape D (sub-shape D pattern established at 5+ examples; consolidation candidate) | 2b.13 |

### AC-2b.13-J â€” A11 sub-shape D recurrence (FROZEN at 5 per Murat M-R23) â€” last operator-instructions inheritor

**Per Murat M-R23 amendment 2026-04-25:** A11 sub-shape D harvest FROZEN at 5 examples. Tamara 2b.13 records "sub-shape D recurrence noted in Â§12.12 inheritor catalog row only â€” NO new A11 top-level bullet."
### AC-2b.13-K â€” TEMPLATE compliance R1â€“R14 v2.3
### AC-2b.13-L â€” D12 close protocol â€” auto-emit C3 17â†’18; A11 13th; Â§12.12 row; **closes operator-instructions inheritor wave**
### AC-2b.13-M â€” Sprint-status flips. Close note: "Operator-instructions inheritor wave complete (Kim parent + 4 inheritors at 2b.10-2b.13)."

---

## File Structure Requirements

```
app/specialists/tamara/
â”œâ”€â”€ __init__.py, graph.py, state.py, model_config.yaml
â”œâ”€â”€ design_spec_assembly.py                     # NEW (~60 LOC); str.format + named keys
â””â”€â”€ expertise/{README.md, __init__.py, capability_registry.yaml}

tests/specialists/tamara/ â€” 23 tests mirroring Kim shape

tests/integration/scaffold_conformance/test_scaffold_tamara.py â€” 1 test
```

### MODIFIED files
- `docs/dev-guide/langgraph-migration-guide.md` â€” Â§12.12 NEW row + framing-sentence updated for "operator-instructions wave complete."
- `docs/dev-guide/specialist-anti-patterns.md` â€” A11 13th bullet.
- `_bmad-output/implementation-artifacts/sprint-status.yaml`.
- `pyproject.toml` (auto-emitted).

---

## Testing Requirements

**K-target ~1.4Ã— (target 11 / floor 8) per R14 inheritor cap.** Test count 23 collectible / ~16 K-floor.

**Regression target at T8:** â‰¥283 passed / â‰¥10 skipped placeholder-key.

---

## Dev Agent Record

_(Populated during T1â€“T9.)_


### T8 Regression Evidence

- Specialist-wave slice validation: 184 passed / 1 skipped across cd/enrique/wanda/kim/vyx/aria/mira/tamara + scaffold conformance.
- Specialists + scaffold conformance anchor: 525 passed / 7 skipped.
- uff check clean on touched specialist/test paths.
- lint-imports 3/3 kept.
- Sandbox-AC validator PASS for stories 2b.6-2b.13.

