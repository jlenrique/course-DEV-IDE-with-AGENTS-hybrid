# Migration Story 2b.10: Migrate Vyx (Vyond Animation) to 9-Node Scaffold â€” operator-instructions Â§12.13 inheritor

**Status:** done
**Sprint key:** `migration-2b-10-vyx-vyond-scaffold-migration`
**Epic:** Slab 2b â€” tenth per-specialist migration; FIRST inheritor of operator-instructions category Â§12.13 (Kim 2b.9 parent).
**Pts:** 2 (pure inheritor; no novel architectural surface; matches Â§12.13 pattern from Kim) | **Gate:** single. **K-target:** ~1.4Ã— (target 11 / floor 8 â€” inherited from Kim per R14 cap).

Vyx (Vyond persona) is operator-instructions thin node â€” produces storyboards, scene plans, timing maps, and Studio build instructions. **No external dispatch substrate, no LLM at specialist layer at runtime** (deterministic instruction assembly from envelope + capability templates, mirroring Kim 2b.9 pattern). Adds ONE row to Â§12.12 inheritor catalog matrix under Â§12.13 parent (per R3 + R13 single-parent invariant + R14 K-floor cap).

---

## T1 Readiness Block

Standing Pre-Flight items 1â€“11 same as 2b.9. TEMPLATE doc v2.3 R1â€“R14 apply. **R14 inheritor K-floor cap binding**: target â‰¤13 (Kim's parent target).

**Slab 2b artifact-existence sweep â€” Vyx-specific deltas:**
- **C** Reference patterns: Kim 2b.9 (parent Â§12.13 â€” operator-instructions thin node). Vyx mirrors verbatim.
- **F** `pyproject.toml` C3 contains 14 rows pre-Vyx. Auto-emit makes 15.
- **G** FR54 N/A (no LLM at specialist layer).
- **R2 importlib loader status:** UNCHANGED (no dispatch wrapper).

**Epic-doc-vs-framework cross-check (per R6):**

(a) **Framework drifts:** Drift #1 â€” Skill-dir `bmad-agent-vyond` (vendor name) vs persona `Vyx`. A11 10th example sub-shape D (vendor-name).

(b) **TEMPLATE scope decisions:**
- **Decision #1 (R1 bounded scope):** headless deterministic instruction assembly only. Interactive + sidecar OOS. R8 trigger: same as Kim â€” both conditions stack (â‰¥2 OOS + category-novel-thin-node-inheritor).
- **Decision #2 (R13 single-parent):** classified as Category C operator-instructions inheritor of Â§12.13 Kim. Single parent. PASS R13.
- **Decision #3 (R14 K-floor cap):** target 11 / floor 8 â€” inherited from Kim parent. Substrate-specific tests budget â‰¤5.
- **Decision #4 (sanctum):** BMB sanctum at `_bmad/memory/bmad-agent-vyond/` does NOT exist; sidecar at `_bmad/memory/vyx-sidecar/` (legacy). Graceful-degrade per R5+R6+R11.

---

## Story

As a **migration dev agent inheriting TEMPLATE v2.3 R1â€“R14 + Kim Â§12.13 pattern**,
I want **Vyx (Vyond) rehomed into `app/specialists/vyx/` mirroring Kim's operator-instructions thin-node pattern + per-R5 auto-emit C3 row + ONE row in Â§12.12 under Â§12.13 parent**,
So that **the operator-instructions category Â§12.13 gains its first inheritor (Kim â†’ Vyx), validates the Â§12.13 pattern's reusability, and Slab 2b cadence holds**.

---

## Acceptance Criteria

All ACs are dev-agent-executable. Vyx does NOT carry any `@pytest.mark.llm_live` test (no LLM invocation at specialist layer).

### AC-2b.10-A â€” Generator emits Vyx + auto-emits C3 row (per R5)

3 tests using `temp_repo_root` fixture. Generator: `--name vyx --mcp none --expertise-tier L4-vyond-animation --from-skill skills/bmad-agent-vyond`.

### AC-2b.10-B â€” Vyx `act` node mirrors Kim Â§12.13 operator-instructions pattern

Per Kim Â§12.13 worked example: deterministic checklist assembly via `_assemble_storyboard(envelope, registry)` helper using `str.format` + named keys per A-2b.9-R1. Tag namespace `instructions.parsed.*` per Murat M-R2 + R12 ceiling + M-R19 secondary-tag on `template-resolution-failed`. **6 primary tags**, R9 precedence: `malformed-envelope â†’ missing-key â†’ wrong-type â†’ empty â†’ template-resolution-failed â†’ ok`. M-R21 discriminator pin same as Kim.

**LOC budget:** `_act â‰¤ 80 LOC` (Kim parity); `_assemble_storyboard â‰¤ 60 LOC`.

**NO @pytest.mark.llm_live** (no LLM at Vyx layer).

### AC-2b.10-C â€” Model cascade at `_plan` per R7 (trail entry only) â€” 2 tests
### AC-2b.10-D â€” Sanctum graceful-degrade per R5+R6+R11 â€” 3 tests, PERSONA.md sentinel + DEFERRED-OPERATOR-WINDOW marker
### AC-2b.10-E â€” Gate-decision binding (precedent-inherited) â€” 2 tests
### AC-2b.10-F â€” Resolution trail (FR16 thirteenth per-specialist exercise) â€” 1 test
### AC-2b.10-G â€” Vyx shape-pin tests (per R4): `vyx_storyboard: dict[str, Any] | None` â€” 4 tests
### AC-2b.10-H â€” Scaffold-conformance test registered â€” 1 test

### AC-2b.10-I â€” Migration-guide Â§12.12 grows ONE inheritor row (per R3 + R14)

| Specialist | Parent Â§12.x | Seam divergence | Sanctum case | Harvest contributions | Story |
|---|---|---|---|---|---|
| Vyx (Vyond) | Â§12.13 (operator-instructions) | NO seam divergence (mirrors Kim verbatim) | graceful-degrade | A11 10th example sub-shape D | 2b.10 |

### AC-2b.10-J â€” A11 10th example bullet sub-shape D â€” NO new top-level entries
### AC-2b.10-K â€” TEMPLATE compliance (per R1â€“R14 v2.3) â€” R14 cap honored
### AC-2b.10-L â€” D12 close protocol (single-gate; FOUR-line) â€” auto-emit C3 14â†’15; A11 10th; Â§12.12 row; R14 cap honored
### AC-2b.10-M â€” Sprint-status flips at filing AND close

---

## File Structure Requirements

```
app/specialists/vyx/
â”œâ”€â”€ __init__.py, graph.py, state.py, model_config.yaml
â”œâ”€â”€ storyboard_assembly.py                      # NEW (~60 LOC); str.format + named keys; KeyError â†’ template-resolution-failed
â””â”€â”€ expertise/
    â”œâ”€â”€ README.md, __init__.py
    â””â”€â”€ capability_registry.yaml                # NEW; baseline registry per A-2b.9-R2 pattern (Vyond storyboard / scene-plan / Studio-build templates)

tests/specialists/vyx/
â”œâ”€â”€ __init__.py
â”œâ”€â”€ test_vyx_generator_auto_emit_c3_row.py      # 3 tests
â”œâ”€â”€ test_vyx_act_node_assembly.py               # 7 tests (6 parse-branches + 1 happy-path; NO @llm_live)
â”œâ”€â”€ test_vyx_model_cascade.py                   # 2 tests
â”œâ”€â”€ test_vyx_sanctum_cold_read.py               # 3 tests
â”œâ”€â”€ test_vyx_gate_decision_binding.py           # 2 tests
â”œâ”€â”€ test_vyx_resolution_trail.py                # 1 test
â””â”€â”€ test_vyx_state_shape.py                     # 4 tests

tests/integration/scaffold_conformance/
â””â”€â”€ test_scaffold_vyx.py                        # 1 test
```

### MODIFIED files
- `docs/dev-guide/langgraph-migration-guide.md` â€” Â§12.12 NEW row; Â§12.5 framing updated.
- `docs/dev-guide/specialist-anti-patterns.md` â€” A11 10th bullet.
- `_bmad-output/implementation-artifacts/sprint-status.yaml`.
- `pyproject.toml` (auto-emitted).

---

## Testing Requirements

**K-target ~1.4Ã— (target 11 / floor 8) per R14 inheritor cap.** Test count: 3+7+2+3+2+1+4+1 = **23 collectible**; ~16 K-floor units. Effective ratio ~2.0Ã— floor / ~1.45Ã— target.

**Regression target at T8:** â‰¥262 passed / â‰¥7 skipped placeholder-key.

---

## Dev Agent Record

_(Populated during T1â€“T9.)_


### T8 Regression Evidence

- Specialist-wave slice validation: 184 passed / 1 skipped across cd/enrique/wanda/kim/vyx/aria/mira/tamara + scaffold conformance.
- Specialists + scaffold conformance anchor: 525 passed / 7 skipped.
- uff check clean on touched specialist/test paths.
- lint-imports 3/3 kept.
- Sandbox-AC validator PASS for stories 2b.6-2b.13.

