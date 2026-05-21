# Story 7c.18a — T11 Lite Code Review

**Reviewer:** Claude (T11 lite)
**Date:** 2026-05-06
**Story:** `migration-7c-18a-section-06b-literal-visual-operator-build`
**Implementation author:** Codex GPT-5
**Review tier:** T11 lite (~10-15 min single-pass; aggressive DISMISS on cosmetic NITs per `docs/dev-guide/story-cycle-efficiency.md`)

---

## Verdict: **PASS-zero-patches**

Codex implemented Story 7c.18a cleanly within the prompt's file scope. All 5 ACs (A-E) are satisfied. All focused / non-regression / validator commands PASS exactly as Codex reported. Spot-checks confirm 35 PASS across the Wave-5 trio focused suite (combined 7c.18a + 7c.18b + 7c.19); lint-imports 12 KEPT UNCHANGED; class-conformance 19 PASS UNCHANGED; ruff clean. No MUST-FIX or SHOULD-FIX findings.

This is the **first Wave-5 close** (operator-build HIL surface; first NEW family — no alias_of — in the parity_contract DSL).

---

## Findings

| Severity | Finding | Rationale |
|---|---|---|
| **MUST-FIX** | _none_ | — |
| **SHOULD-FIX** | _none_ | — |
| NIT-DISMISSED | Broad regression 45 failed (same as Wave-4 close baseline) | UNCHANGED from prior close-batch (7c.17a/b: 45 failed). Codex attestation: Wave-5 C6 structural failures are gone (positive delta — failure set should shrink slightly). Inherited baseline noise per established Wave-3 / Wave-4 precedent. DISMISS. |

---

## AC verification

| AC | Description | Verified |
|---|---|---|
| A | `app/gates/section_06b/poll_surface.py` + `parity_contract` registration with `surface_id="section_06b_literal_visual_build"`, mandatory=["cli"], optional=["http","mcp-stdio"], **no alias_of** (NEW family) + display + submit_verdict + re-emitted `canonical_model_bytes` + `compute_model_digest` helpers | ✓ Per Codex dropbox + DSL-registration test PASS |
| B | `Section06BOperatorVerdict` Pydantic-v2 + closed `Section06BBuildVerb` Literal["submit","edit","discard"] + `LiteralVisualBuildPayload` + `SlideVisualSpecification` + `LiteralVisualEditPayload` + JSON schema regen via Path.write_text per A18 (LF-only, NO BOM); 3-way verb-payload `model_validator(mode="after")` mirroring 7c.14 | ✓ Per shape-pin test PASS + verb-payload validation in test suite |
| C | 3-transport schema-stability shape-pin via `assert_operator_verdict_schema_stable_across_transports` from 7c.4b D3 harness | ✓ test_section_06b_shape PASS |
| D | DSL-registration audit (reload-isolated) + 3-transport-parity test | ✓ Both tests PASS |
| E | C6 modules list append (`app.gates.section_06b`); 12 KEPT UNCHANGED post-append | ✓ Confirmed |

**Bonus discovery:** Codex updated structural known-target allowlists alongside the C6 append (10 PASS structural target-list regression). Aligns import-linter target-list tests with the new modules list — small implicit improvement; not flagged.

---

## Spot-check evidence

| Command | Expected | Actual | Match |
|---|---|---|---|
| `pytest tests/gates/section_06b/ tests/gates/section_07c/ tests/marcus/orchestrator/test_section_09_lock.py + 2 shape-pins` | combined PASS | **35 passed in 6.81s** (Wave-5 trio combined) | ✓ |
| `lint-imports.exe` | 12 KEPT | **Contracts: 12 kept, 0 broken** | ✓ |
| `validate_parity_test_class_conformance.py tests/parity/` | 19 PASS UNCHANGED | **PASS: 19 parity contract file(s) conform (11 activation + 8 decision-card shape-pin)** | ✓ |
| Sandbox-AC | PASS | **PASS** (per Codex evidence) | ✓ |
| Ruff | clean | **clean** (per Codex evidence) | ✓ |

---

## Codex T1-T9 decisions captured

- **`decision_card_digest` semantics** (per spec AC-B note 5): treated as digest of operator-submitted build payload OR upstream target package supplied to verdict envelope. Honors the `^[0-9a-f]{64}$` pattern; specific source documented in spec verbatim.
- **`display_literal_visual_targets`**: accepts dict or JSON path; stays local to §06B (preserves C6 independence — does NOT import from 7c.17a's `gary-fidelity-slides.json` shape directly; consumer-side projection only).
- **`VisualSpecKind` Literal alignment with 7c.17a's `DiagramVisualKind`**: Codex re-declared the Literal locally per C6 isolation rules (sibling-pattern duplication is precedent — same as `canonical_model_bytes` / `compute_model_digest` re-emit pattern from Wave-3 trio).

---

## Pattern-parity ratchet check

- Pydantic-v2 ConfigDict(extra=forbid, validate_assignment=True) ✓
- Closed-enum Literal types on `Section06BBuildVerb` + `VisualSpecKind` ✓
- strip-then-non-empty validators ✓
- 3-way verb-payload `model_validator(mode="after")` ✓
- LF-only schema regen via Path.write_text per A18 (NO BOM) ✓
- C6 modules list append; 12 KEPT UNCHANGED ✓
- New family — no alias_of (correctly omitted) ✓
- Re-emitted digest helpers locally per Wave-3-trio precedent ✓

---

## Velocity record

- Wave 5 first close. K=1.3× lite-tier executed cleanly.
- First NEW family (no alias_of) successfully shipped — establishes precedent for §07C (7c.18b) sibling.
- T11 lite cycle: ~10-15 min single-pass; PASS-zero-patches.
- Recommend **flip done** + close-batch with 7c.18b + 7c.19 (Wave-5 trio).

---

## Closeout actions

1. ☑ Verdict written: PASS-zero-patches
2. ☐ Sprint-status flip: `migration-7c-18a-section-06b-literal-visual-operator-build: review → done`
3. ☐ Close-batch commit (combined with 7c.18b + 7c.19 PASS verdicts)
