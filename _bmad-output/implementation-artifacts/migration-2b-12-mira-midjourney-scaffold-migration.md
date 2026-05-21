# Migration Story 2b.12: Migrate Mira (Midjourney) to 9-Node Scaffold â€” operator-instructions Â§12.13 inheritor (Option A per W-R9 pre-classification)

**Status:** done
**Sprint key:** `migration-2b-12-mira-midjourney-scaffold-migration`
**Epic:** Slab 2b â€” twelfth per-specialist migration; THIRD inheritor of operator-instructions category Â§12.13 (Kim/Vyx/Aria siblings); **Option A pre-classified at 2b.9 close per Winston W-R9** (Category C operator-instructions inheritor with API-stub OOS to Slab-3 follow-on `midjourney-api-stub-slab-3-followon`).
**Pts:** 2 (pure inheritor; mirrors Kim pattern; API-stub OOS) | **Gate:** single. **K-target:** ~1.4Ã— (target 11 / floor 8 â€” R14 cap).

Mira (Midjourney persona) is operator-instructions thin node per W-R9 pre-classification â€” produces ready-to-paste prompt sets, parameter recommendations, and iteration plans for Discord/web workflows. **API-stub surface OUT OF SCOPE** per W-R9 (deferred to `midjourney-api-stub-slab-3-followon` filed at 2b.9 close); migration covers ONLY operator-instructions surface. **No external dispatch substrate at the migrated layer, no LLM at specialist layer at runtime.** Adds ONE row to Â§12.12 under Â§12.13 parent.

---

## T1 Readiness Block

Standing Pre-Flight items 1â€“11 same as 2b.10. TEMPLATE doc v2.3 R1â€“R14 apply.

**Slab 2b artifact-existence sweep â€” Mira-specific deltas:**
- **C** Reference patterns: Kim 2b.9 parent + Vyx/Aria siblings.
- **F** `pyproject.toml` C3 contains 16 rows pre-Mira. Auto-emit makes 17.
- **G** FR54 N/A.
- **R2 importlib loader status:** UNCHANGED at the migrated layer (API-stub OOS).
- **W-R9 pre-classification verified:** Mira filed as Option A at 2b.9 close per `midjourney-api-stub-slab-3-followon` deferred-inventory entry. R13 single-parent invariant honored. NO hybrid classification.

**Epic-doc-vs-framework cross-check (per R6):**

(a) **Framework drifts:** Drift #1 â€” Skill-dir `bmad-agent-midjourney` (vendor name) vs persona `Mira`. A11 12th example sub-shape D.

(b) **TEMPLATE scope decisions:**
- **R1 bounded scope:** headless deterministic instruction assembly only; API-stub deferred to Slab-3.
- **R13 single-parent:** Option A (Category C Â§12.13 inheritor); R13 invariant preserved.
- **R14 K-floor cap:** target 11 / floor 8.
- **Sanctum:** BMB sanctum at `_bmad/memory/bmad-agent-midjourney/` does NOT exist; sidecar at `_bmad/memory/mira-sidecar/` (legacy). Graceful-degrade.

---

## Story

As a **migration dev agent inheriting TEMPLATE v2.3 R1â€“R14 + Kim Â§12.13 pattern + W-R9 Option A pre-classification**,
I want **Mira (Midjourney) rehomed into `app/specialists/mira/` mirroring Kim's operator-instructions thin-node pattern + per-R5 auto-emit C3 row + ONE row in Â§12.12 under Â§12.13 parent + Midjourney API-stub deferred to Slab-3 per W-R9**,
So that **the operator-instructions category Â§12.13 gains its third inheritor, R13 single-parent invariant is preserved (no hybrid), and Midjourney API-stub work is properly queued at Slab-3**.

---

## Acceptance Criteria

All ACs are dev-agent-executable. Mira does NOT carry any `@pytest.mark.llm_live` test.

### AC-2b.12-A â€” Generator emits Mira + auto-emits C3 row (per R5)
3 tests using `temp_repo_root` fixture. Generator: `--name mira --mcp none --expertise-tier L4-midjourney-prompts --from-skill skills/bmad-agent-midjourney`.

### AC-2b.12-B â€” Mira `act` node mirrors Kim Â§12.13 operator-instructions pattern
Per Kim Â§12.13: deterministic prompt-set assembly via `_assemble_prompt_set(envelope, registry)` helper. Tag namespace `instructions.parsed.*` (parameters: prompt_text, parameter_recommendations, iteration_plan). 6 primary tags + M-R19 secondary-tag on `template-resolution-failed`. R9 precedence same as Kim.

**LOC budget:** `_act â‰¤ 80 LOC`; `_assemble_prompt_set â‰¤ 60 LOC`.

### AC-2b.12-C through AC-2b.12-H â€” Mirror Kim pattern (2+3+2+1+4+1 = 13 tests)

### AC-2b.12-I â€” Â§12.12 inheritor row

| Specialist | Parent Â§12.x | Seam divergence | Sanctum case | Harvest contributions | Story |
|---|---|---|---|---|---|
| Mira (Midjourney) | Â§12.13 (operator-instructions per W-R9 Option A) | NO seam divergence; API-stub OOS to Slab-3 follow-on | graceful-degrade | A11 12th example sub-shape D | 2b.12 |

### AC-2b.12-J â€” A11 sub-shape D recurrence (FROZEN at 5 per Murat M-R23) + W-R9 Option A confirmation

**Per Murat M-R23 amendment 2026-04-25:** A11 sub-shape D harvest FROZEN at 5 examples (Enrique/Wanda/Kim/Vyx/Aria). Mira 2b.12 records "sub-shape D recurrence noted in Â§12.12 inheritor catalog row only â€” NO new A11 top-level bullet" per harvest-gate "after 5 examples, pattern is established." Save catalog from accumulating 9+ redundant bullets across Slab 2b. W-R9 Option A confirmation IS recorded (deferred-inventory entry referenced).
### AC-2b.12-K â€” TEMPLATE compliance R1â€“R14 v2.3 (R13 + W-R9 honored)
### AC-2b.12-L â€” D12 close protocol â€” auto-emit C3 16â†’17; A11 12th; Â§12.12 row; R13 invariant preserved
### AC-2b.12-M â€” Sprint-status flips

---

## File Structure Requirements

```
app/specialists/mira/
â”œâ”€â”€ __init__.py, graph.py, state.py, model_config.yaml
â”œâ”€â”€ prompt_set_assembly.py                      # NEW (~60 LOC); str.format + named keys
â””â”€â”€ expertise/{README.md, __init__.py, capability_registry.yaml}

tests/specialists/mira/ â€” 23 tests mirroring Kim shape

tests/integration/scaffold_conformance/test_scaffold_mira.py â€” 1 test
```

### MODIFIED files
- `docs/dev-guide/langgraph-migration-guide.md` â€” Â§12.12 NEW row.
- `docs/dev-guide/specialist-anti-patterns.md` â€” A11 12th bullet.
- `_bmad-output/implementation-artifacts/sprint-status.yaml`.
- `pyproject.toml` (auto-emitted).

---

## Testing Requirements

**K-target ~1.4Ã— (target 11 / floor 8) per R14 inheritor cap.** Test count 23 collectible / ~16 K-floor.

**Regression target at T8:** â‰¥276 passed / â‰¥9 skipped placeholder-key.

---

## Dev Agent Record

_(Populated during T1â€“T9.)_


### T8 Regression Evidence

- Specialist-wave slice validation: 184 passed / 1 skipped across cd/enrique/wanda/kim/vyx/aria/mira/tamara + scaffold conformance.
- Specialists + scaffold conformance anchor: 525 passed / 7 skipped.
- uff check clean on touched specialist/test paths.
- lint-imports 3/3 kept.
- Sandbox-AC validator PASS for stories 2b.6-2b.13.

