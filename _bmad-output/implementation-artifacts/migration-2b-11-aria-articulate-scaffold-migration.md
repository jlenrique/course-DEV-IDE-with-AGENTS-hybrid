# Migration Story 2b.11: Migrate Aria (Articulate Storyline/Rise) to 9-Node Scaffold â€” operator-instructions Â§12.13 inheritor

**Status:** done
**Sprint key:** `migration-2b-11-aria-articulate-scaffold-migration`
**Epic:** Slab 2b â€” eleventh per-specialist migration; SECOND inheritor of operator-instructions category Â§12.13 (Kim 2b.9 parent + Vyx 2b.10 sibling).
**Pts:** 2 (pure inheritor; mirrors Kim/Vyx pattern verbatim) | **Gate:** single. **K-target:** ~1.4Ã— (target 11 / floor 8 â€” R14 cap from Kim parent).

Aria (Articulate persona) is operator-instructions thin node â€” produces build specifications, branching scenario maps, and SCORM export review steps. **No external dispatch substrate, no LLM at specialist layer at runtime.** Mirrors Kim/Vyx pattern. Adds ONE row to Â§12.12 under Â§12.13 parent (per R3 + R13 + R14).

---

## T1 Readiness Block

Standing Pre-Flight items 1â€“11 same as 2b.10. TEMPLATE doc v2.3 R1â€“R14 apply.

**Slab 2b artifact-existence sweep â€” Aria-specific deltas:**
- **C** Reference patterns: Kim 2b.9 parent + Vyx 2b.10 sibling.
- **F** `pyproject.toml` C3 contains 15 rows pre-Aria. Auto-emit makes 16.
- **G** FR54 N/A.
- **R2 importlib loader status:** UNCHANGED.

**Epic-doc-vs-framework cross-check (per R6):**

(a) **Framework drifts:** Drift #1 â€” Skill-dir `bmad-agent-articulate` (vendor name) vs persona `Aria`. A11 11th example sub-shape D.

(b) **TEMPLATE scope decisions:**
- **R1 bounded scope:** headless deterministic instruction assembly only.
- **R13 single-parent:** classified as Â§12.13 Kim inheritor.
- **R14 K-floor cap:** target 11 / floor 8.
- **Sanctum:** BMB sanctum at `_bmad/memory/bmad-agent-articulate/` does NOT exist; sidecar at `_bmad/memory/aria-sidecar/` (legacy). Graceful-degrade.

---

## Story

As a **migration dev agent inheriting TEMPLATE v2.3 R1â€“R14 + Kim Â§12.13 pattern**,
I want **Aria (Articulate) rehomed into `app/specialists/aria/` mirroring Kim's operator-instructions thin-node pattern + per-R5 auto-emit C3 row + ONE row in Â§12.12 under Â§12.13 parent**,
So that **the operator-instructions category Â§12.13 gains its second inheritor (Kim â†’ Vyx â†’ Aria), and Slab 2b cadence holds**.

---

## Acceptance Criteria

All ACs are dev-agent-executable. Aria does NOT carry any `@pytest.mark.llm_live` test.

### AC-2b.11-A â€” Generator emits Aria + auto-emits C3 row (per R5)
3 tests using `temp_repo_root` fixture. Generator: `--name aria --mcp none --expertise-tier L4-articulate-design --from-skill skills/bmad-agent-articulate`.

### AC-2b.11-B â€” Aria `act` node mirrors Kim Â§12.13 operator-instructions pattern
Per Kim Â§12.13 worked example: deterministic spec assembly via `_assemble_storyline_spec(envelope, registry)` helper. Tag namespace `instructions.parsed.*` per Murat M-R2 + R12 ceiling + M-R19 secondary-tag. **6 primary tags**, R9 precedence same as Kim. M-R21 discriminator pin same.

**LOC budget:** `_act â‰¤ 80 LOC`; `_assemble_storyline_spec â‰¤ 60 LOC`.

### AC-2b.11-C through AC-2b.11-H â€” Mirror Kim pattern (2 + 3 + 2 + 1 + 4 + 1 = 13 tests)

### AC-2b.11-I â€” Â§12.12 inheritor row

| Specialist | Parent Â§12.x | Seam divergence | Sanctum case | Harvest contributions | Story |
|---|---|---|---|---|---|
| Aria (Articulate) | Â§12.13 (operator-instructions) | NO seam divergence (mirrors Kim/Vyx) | graceful-degrade | A11 11th example sub-shape D | 2b.11 |

### AC-2b.11-J â€” A11 11th example bullet sub-shape D
### AC-2b.11-K â€” TEMPLATE compliance R1â€“R14 v2.3
### AC-2b.11-L â€” D12 close protocol â€” auto-emit C3 15â†’16; A11 11th; Â§12.12 row
### AC-2b.11-M â€” Sprint-status flips

---

## File Structure Requirements

```
app/specialists/aria/
â”œâ”€â”€ __init__.py, graph.py, state.py, model_config.yaml
â”œâ”€â”€ storyline_assembly.py                       # NEW (~60 LOC); str.format + named keys
â””â”€â”€ expertise/{README.md, __init__.py, capability_registry.yaml}

tests/specialists/aria/
â”œâ”€â”€ __init__.py + 7 test files mirroring Kim shape (3+7+2+3+2+1+4) = 22 tests
â””â”€â”€ test_aria_state_shape.py = 4 tests

tests/integration/scaffold_conformance/test_scaffold_aria.py = 1 test
```

### MODIFIED files
- `docs/dev-guide/langgraph-migration-guide.md` â€” Â§12.12 NEW row.
- `docs/dev-guide/specialist-anti-patterns.md` â€” A11 11th bullet.
- `_bmad-output/implementation-artifacts/sprint-status.yaml`.
- `pyproject.toml` (auto-emitted).

---

## Testing Requirements

**K-target ~1.4Ã— (target 11 / floor 8) per R14 inheritor cap.** Test count 23 collectible / ~16 K-floor.

**Regression target at T8:** â‰¥269 passed / â‰¥8 skipped placeholder-key.

---

## Dev Agent Record

_(Populated during T1â€“T9.)_


### T8 Regression Evidence

- Specialist-wave slice validation: 184 passed / 1 skipped across cd/enrique/wanda/kim/vyx/aria/mira/tamara + scaffold conformance.
- Specialists + scaffold conformance anchor: 525 passed / 7 skipped.
- uff check clean on touched specialist/test paths.
- lint-imports 3/3 kept.
- Sandbox-AC validator PASS for stories 2b.6-2b.13.

