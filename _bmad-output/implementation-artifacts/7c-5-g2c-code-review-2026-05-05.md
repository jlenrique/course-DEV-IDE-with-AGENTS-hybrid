# T11 Standard Code Review — Story 7c.5.G2C (G2C DecisionCard Extend-and-Audit, Pre-Composition QA)

**Story key:** `migration-7c-5-g2c-decision-card-extend-and-audit`
**Reviewer:** Claude (Opus 4.7) — T11 standard tier (post-T9 standard review; PRE-T2 cross-agent T1 review previously PASSed at `aa9c040`)
**Gate-mode:** `dual-gate-cross-agent-CONTRACT-EVOLUTION` (T11 itself is `standard` tier; the "cross-agent" component refers to the T1 PRE-T2 review, NOT this T11)
**R-tier:** R3 (full broad regression)
**K-target:** 1.4× (extend-and-audit)
**Diff size (G2C-only scope):** 4 lockstep files (modified `g2c.py` + regenerated schema + new shape-pin + new golden) + 2 constructor sites (`production_runner.py:434`, `m3_trial.py:169`) + 1 governance-version tracker (`tests/parity/test_nfr_cg_block_aggregated.py`)
**Review date:** 2026-05-05

---

## Verdict: **PASS — recommend COMMIT + FLIP DONE**

The G2C extend-and-audit migration is structurally sound. The four-file lockstep is now byte-deterministic after one mechanical patch (see Critical Item #2 below). All five ACs (A–E) verify. The frozen-hash AMELIA-P4 baseline `237ce7d1...` is unchanged. The `__init__.py` flat-export and discriminated union were already complete from a prior commit and require no edit (Pydantic discriminates on `gate_id` field value, not on parent class — migrating G2CCard from `DecisionCard` → `DecisionCardBase` does not break `AnyDecisionCardAdapter`). The two constructor sites (`production_runner.py:434` + `m3_trial.py:169`) correctly drop `drafted_proposal`/`evidence`/`risks`, supply `decision_card_digest`, and convert legacy meta to `_base_card_meta(...)`. The `test_nfr_cg_block_aggregated.py` modification is a JUSTIFIED governance-version tracker bump (`2026-04-29-slab7b-twelve-stories` → `2026-05-05-amelia-p5-and-wave-3-lookahead-policy`), tracking the V6+V7 codification at `57b92b2`; it is NOT defensive silencing. PARALLEL-DISPATCH GUARDRAILS all green. Pydantic-v2 14-idiom checklist conforms.

T1-audit verdict on `drafted_proposal` / `evidence` / `risks` was DROP for G2C (with `audit_method=heavy` smoke-pass evidence). NO T6 reversal occurred for G2C — the smoke-pass evidence in the T1 audit (executed against `tests/composition/` + `tests/integration/marcus/` + `tests/integration/replay/` with `-k <field>` collection + execution) confirmed all live consumers in those required roots construct `gate_id="G1"` cards, not G2C. The contract-diff §2 captures this correctly with smoke-pass commands and `audit_method=heavy` rationale. The G1-precedent reversal pathway was correctly avoided.

**MUST-FIX:** 0
**SHOULD-FIX:** 1 (mechanical patch applied by reviewer — schema CRLF→LF byte-determinism)
**NIT/DISMISS:** 0

---

## Verification Battery

| Check | Status | Evidence |
|---|---|---|
| Focused G2C shape-pin | PASS | `18 passed in 3.60s` — 18 tests (1 LOCKSTEP_CHECK + 1 required-fields + 3+3+3+3 closed-enum red rejections on gate_id/gate_focus/schema_version/readiness_status + 1 dropped-legacy-fields rejection + 1 schema byte-match + 1 golden round-trip + 1 frozen-mutation rejection) |
| AMEND-7d-i AST-scan structural test | PASS | `2 passed` — `test_decision_card_shape_pins_do_not_rederive_tw_7c_3_rule` confirms G2C does not contain `FOUR_FILE_GLOBS` or `all_four_present` literals; bare `LOCKSTEP_CHECK` import only |
| `tests/parity/` + `tests/parametrized_harness/` + `tests/unit/` broad slice | PASS | `921 passed, 18 skipped in 11.99s` — clean. NFR-CG6 governance-tracker test now PASSES (was the sole T1-baseline failure; resolved by V6+V7 version bump in test) |
| Composition + integration-marcus smoke | PASS | `132 passed, 1 skipped in 16.35s` — drafted_proposal/evidence live consumers (G1-only) + cross-gate handler loaders all green |
| Discriminated union + manifest dotted ref slice | PASS | `35 passed in 5.89s` — `test_per_gate_strict` + `test_discriminated_union_routing` + `test_manifest_dotted_reference_resolver` (2-class regime) + `test_routing_manifest_driven` + `test_nfr_cg_block_aggregated` |
| Class-conformance | PASS | `PASS: 19 parity contract file(s) conform (11 activation + 8 decision-card shape-pin)` — Codex T9 reported 19 (G0+G2A+G5+G6+G1+G2C+G3+G4 = 8 shape-pins; G3/G4 land in sibling reviews concurrently) |
| Lint-imports | PASS | `Contracts: 12 kept, 0 broken` (UNCHANGED) |
| Sandbox-AC validator | PASS | `PASS — no sandbox-AC violations across 1 story file(s)` |
| Ruff (in-scope files) | PASS | `All checks passed!` — covers `g2c.py` + `test_decision_card_g2c_shape.py` + `__init__.py` |
| Schema-emission determinism (post-patch) | PASS | In-Python byte comparison: emitted (5529 bytes) == on-disk (5529 bytes), MATCH; LF + no BOM |
| BOM check on schema JSON | PASS | `NO_BOM`; first 16 bytes = `b'{\n  "$defs": {\n '` post-patch |
| Frozen-hash AMELIA-P4 unchanged | PASS | `FROZEN_AT_SHIP_HASHES['g2c'] == "237ce7d1b6c228cea5bc3653027cb40e50e40f316681a736d0692612dc7ba72a"` UNCHANGED post-T9 |

---

## Critical Items Disposition

### Critical Item #1 — T1-audit-verdict-reversal scan: NO REVERSAL OCCURRED — PASS

For G2C, the T1 audit declared DROP for `drafted_proposal` + `evidence` + `risks` with **AMELIA-P5 V6 `audit_method=heavy` smoke-pass evidence** (mandated by V6 amendment at `57b92b2`). The smoke-pass evidence is documented in contract-diff §2 with concrete pytest invocations:

- `pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k drafted_proposal --co -q` → 0 tests collected
- `pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k evidence --co -q` → 7 tests collected; `-k evidence -q --tb=short` → 7 passed (all G1-only constructors)
- `pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k risks --co -q` → 0 tests collected
- Targeted `card.drafted_proposal` / `card.evidence` / `card.risks` greps across required roots: all reads bind to `_build_decision_card(gate_id="G1", ...)` helpers; no `G2CCard(` constructor under those roots

Verified in `g2c.py` (lines 16–58): the three fields are NOT declared on `G2CCard`. The `model_config["extra"] = "forbid"` (inherited from `DecisionCardBase`) ensures any consumer attempting to pass them at construction would raise `ValidationError`. The shape-pin's `test_g2c_card_rejects_dropped_legacy_fields` covers this with parametrized payloads injecting `drafted_proposal` / `evidence` / `risks` / `meta.reject_rate` and asserting `pytest.raises(ValidationError)`.

The G1 T6-reversal precedent **does not apply to G2C** — G1's reversal was justified because live composition/integration tests read `card.drafted_proposal` / `card.evidence` from G1-typed cards. G2C has no such live readers, and the V6 `audit_method=heavy` protocol caught this distinction correctly at T1 (not just static-grep). The PRE-T2 T1 cross-agent review at `aa9c040` already validated this DROP verdict; T11 confirms post-T9 implementation honored it.

### Critical Item #2 — BOM patch verification + byte-determinism: SHOULD-FIX PATCHED — PASS

**Initial state (Codex T3 output):** `NO_BOM` (correctly avoided PowerShell `>` redirection per A18). However, the schema file was written with **CRLF line endings** (5726 bytes; `b'{\r\n  "$defs": {\r\n...'`), while the canonical Python regen `Path.write_text(canonical, encoding="utf-8")` on Windows produces CRLF by default (text-mode universal newline translation). The canonical re-emit produces 5529 bytes (`b'{\n  "$defs": {\n...'`).

This breaks **byte-for-byte regen determinism** per A18 spirit, even though the shape-pin test (`test_g2c_json_schema_byte_for_byte_match`) passes because it uses `read_text(encoding='utf-8')` which itself does universal newline translation, masking the CRLF/LF mismatch.

**Sibling-schema convention check:** all five predecessor schemas use LF (`g0.v1` 5581b LF, `g1.v1` 5900b LF, `g2a.v1` 5887b LF, `g5.v1` 5575b LF, `g6.v1` 5977b LF). G2C's CRLF is the outlier. This is a **latent A18 prescription gap** (the documented incantation doesn't pin `newline="\n"`); follow-on policy refinement may want to update A18 to specify `Path.write_bytes(canonical.encode("utf-8"))` or `open(..., "w", encoding="utf-8", newline="\n")` for cross-platform determinism.

**Patch applied (mechanical, this reviewer):** rewrote schema via `Path.write_bytes(canonical.encode('utf-8'))`. Result: 5529 bytes, LF, no BOM, matches sibling convention, byte-deterministic across platforms. Post-patch shape-pin still PASSes (18/18). Patch documented in §Reviewer Patches below.

### Critical Item #3 — Scope expansion justification (`test_nfr_cg_block_aggregated.py`): JUSTIFIED — PASS

`git diff HEAD -- tests/parity/test_nfr_cg_block_aggregated.py` shows a **single-line version-string change**:

```diff
-    assert governance["version"] == "2026-04-29-slab7b-twelve-stories"
+    assert governance["version"] == "2026-05-05-amelia-p5-and-wave-3-lookahead-policy"
```

This is **(a) governance-tracker maintenance — JUSTIFIED scope expansion**, NOT (b) defensive silencing. The change updates the assertion to match the actual `governance["version"]` field that was set in `docs/dev-guide/migration-story-governance.json` at commit `57b92b2` ("docs(slab-7c-velocity-amendments): codify V6 (AMELIA-P5 DROP-row Heavy gate) + V7 (Wave-3 lookahead-cap policy)"). The version bump landed in governance JSON BEFORE G2C dispatch and the corresponding test-side update is the trailing edge of that V6+V7 codification. T1 baseline (`870 passed, 1 failed, 18 skipped`) had this as the sole inherited failure attributed to "governance JSON version is `2026-05-05-amelia-p5-and-wave-3-lookahead-policy` from commit `57b92b2`."

The remainder of the test (other assertions on K-floor governance, story-specific gate-modes, etc.) is UNCHANGED — no relaxation of behavior, no `pytest.skip`, no try/except wrapper, no commented-out assertion. Scope expansion is the minimum-viable fix.

**Discriminated union investigation (`__init__.py`):** UNMODIFIED. Inspection confirms (lines 22, 42, 62) that `G2CCard` was already in the flat import, `AnyDecisionCard` discriminated union, and `__all__` from a prior commit (the package was already structured for the future migration). The `AnyDecisionCardAdapter = TypeAdapter(AnyDecisionCard)` discriminates on `gate_id` value via the `Field(discriminator="gate_id")` annotation — discrimination is by **field value**, not by **parent class hierarchy**. Migrating `G2CCard` from inheriting `DecisionCard` to inheriting `DecisionCardBase` does NOT break the discriminator. Verified: `tests/unit/models/decision_cards/test_discriminated_union_routing.py` passes 35 tests in the union+routing slice.

### Critical Item #4 — AMELIA-P4 frozen-hash UNCHANGED post-T9: PASS

```text
FROZEN_AT_SHIP_HASHES['g2c'] == "237ce7d1b6c228cea5bc3653027cb40e50e40f316681a736d0692612dc7ba72a"
```

Output: `UNCHANGED`. The pre-extension hash is preserved as the audit-trail anchor for the original G2C contract; the current on-disk `g2c.py` hash (post-rewrite to inherit `DecisionCardBase`) differs intentionally and is justified by the contract-diff artifact. The three sibling hashes (g1/g3/g4 — note G1's was already updated post-G1-close per AMEND) are preserved unmodified for current and future extend-and-audit story audits.

### Critical Item #5 — PARALLEL-DISPATCH GUARDRAILS: ALL PASS

1. **AMEND-7d-i AST-scan compliance — PASS.** Grep on `test_decision_card_g2c_shape.py` for `FOUR_FILE_GLOBS|all_four_present` returned **No matches found**. The only lockstep-related import is the bare `from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK` (line 11), used at line 42 only. Structural test `tests/structural/test_tw_7c_3_firing_spec_single_source.py` PASSES (2 tests).

2. **Pattern-replication discipline — PASS.** `g2c.py` mirrors G2A canonical:
   - Inherits `DecisionCardBase` (line 16) — NOT legacy `DecisionCard`
   - `card_id` / `trial_id` typed as Pydantic `UUID4` (lines 23, 27) — not bare `UUID`
   - `enforce_uuid4_version` validator (lines 60–63)
   - `enforce_tz_aware` validator on `created_at` (lines 65–68)
   - `Field(..., description="...")` on every field
   - Closed Literals on `gate_id` ("G2C"), `gate_focus` ("pre_composition_qa"), `schema_version` ("v1"), `readiness_status` ("ready"|"blocked"), `verb` ("approve"|"edit"|"reject")
   - Inherited `extra="forbid"`, `validate_assignment=True`, `frozen=True` from `DecisionCardBase`

3. **Shared-file integration ordering — PASS.** `__init__.py` UNMODIFIED; `G2CCard` was already in flat-export, `AnyDecisionCard` union, and `__all__`. Discriminated union routes by `gate_id` field-value, not by parent class — migration to `DecisionCardBase` does not break it. `tests/unit/models/decision_cards/test_discriminated_union_routing.py` passes.

4. **Pattern-parity ratchet — PASS-with-clarification.** G2C has NO free-text scalar fields requiring strip-then-non-empty validation. `blocking_issues` and `ready_nodes` are `list[str]` with `default_factory=list` — they are valid as empty lists (the empty-blocked-issues case is the canonical "ready" state per the readiness_status taxonomy). The contract-diff §6 explicitly documents this: "G2C has no free-text scalar field requiring strip-then-non-empty validation." Spot-check vs `g2a.py` confirms this is a structural difference between G2A (which has `outcome_summary: str`) and G2C (which has list fields only) — G2C correctly omits the validator that G2A applies.

5. **Class-conformance arithmetic — PASS.** Validator reports `19 parity contract file(s) conform (11 activation + 8 decision-card shape-pin)`. T1 baseline was 16 (11+5: G0+G2A+G5+G6+G1). Increment to 19 reflects G2C+G3+G4 shape-pins all landing concurrently in this working-tree (G3/G4 reviewed by sibling T11s). G2C alone increments by +1; combined with G3+G4 sibling-additions = 16+3=19. Story-scoped expectation +1 SATISFIED.

6. **Broad-regression baseline shift — PASS.** Codex T9 reported `4239 passed, 42 failed, 27 skipped, 2 xfailed` from full-suite `pytest -p no:randomly -q --tb=line`. Failure attribution: "no decision-card shape, schema, fixture, union, or constructor-path failures surfaced. The 42 failures match the inherited broad-suite drift count already documented on adjacent Slab 7c closes." Local broad-slice (`tests/parity/ tests/parametrized_harness/ tests/unit/`) is `921 passed, 18 skipped` — fully clean (no inherited failures in the canonical extend-and-audit verification battery). The full-suite 42 failures are inherited drift in dispatch registry / run HUD / replay pack hash / sanctum cache state / generated v42 template / ProactorEventLoop+psycopg incompatibility / catalog model-id drift — none are G2C-introduced.

---

## AC Compliance Verification

### AC-7c.5.G2C-A — Pre-T2 contract-diff + backward-consumer audit + frozen-hash artifacts — PASS

All three deliverables present, structurally sound (PRE-T2 reviewed at `aa9c040`):

1. `_bmad-output/implementation-artifacts/migration-7c-5-g2c-contract-diff.md` — 132 LOC; 8 sections covering frozen-hash pre-check (§0), legacy G2C fields disposition (§1), legacy DecisionCard base disposition with **AMELIA-P5 V6 `audit_method=heavy|light` qualifier per row** (§2: drafted_proposal+evidence+risks DROP-with-heavy-smoke-pass-evidence), legacy DecisionCardMeta disposition (§3 — also carries `audit_method` per V6), new fields (§4: `schema_version` + `decision_card_digest` + `gate_focus`), closed-enum tightening (§5), pattern-parity ratchets (§6), net diff (§7), T1 baseline evidence (§8 with concrete pytest commands).
2. `_bmad-output/implementation-artifacts/migration-7c-5-g2c-backward-consumer-audit.md` — 110 LOC; per-call-site verdicts for ~30 sites covering `__init__.py` (3 sites), `g2c.py` (6 sites self-references), `production_runner.py` (3 sites), `m3_trial.py` (4 sites), unit-tests (~10 sites), 6 already-G1-updated 2-class-regime substrate sites, 7 required-root smoke consumers (all G1-only), 3 documentation references. Field-Access Summary §confirms no executable G2C site reads dropped fields.
3. `_frozen_hashes.py` already landed at G1 close — G2C key `237ce7d1...` UNCHANGED post-T9.

### AC-7c.5.G2C-B — AMELIA-P4 frozen-hash delta-AC — PASS

T0/T2 frozen-hash pre-check: PASS. Recorded and on-disk pre-extension hashes matched (`237ce7d1...`); current post-T9 on-disk hash differs intentionally per the contract-diff audit trail. The three sibling hashes (g1/g3/g4) are preserved unmodified for current/future extend-and-audit stories.

### AC-7c.5.G2C-C — Four-file lockstep co-commit — PASS (post-patch)

All four files present:

1. `app/models/decision_cards/g2c.py` (71 LOC) — `class G2CCard(DecisionCardBase)` (line 16); inheritance migration complete. Re-declares: `card_id` / `trial_id` (UUID4; lines 23, 27), `gate_id: Literal["G2C"]` + `gate_focus: Literal["pre_composition_qa"]` + `schema_version: Literal["v1"]` + `readiness_status: Literal["ready", "blocked"]` (closed Literals; lines 31, 35, 19, 43), `created_at` (datetime; default UTC factory; line 39), `verb: DecisionCardVerb` (closed Literal; line 55), `blocking_issues` + `ready_nodes` (list[str] with empty default; lines 47, 51). Validators: `_enforce_uuid4` + `_enforce_created_at_tz` (lines 60–68). `__all__ = ["G2CCard"]` (line 71).
2. `app/models/decision_cards/schema/g2c.v1.schema.json` (5529 bytes post-patch) — REGENERATED; emits `additionalProperties: false`, `const: "G2C"` for gate_id, `const: "pre_composition_qa"` for gate_focus, `const: "v1"` for schema_version, `enum: ["ready", "blocked"]` for readiness_status. Required array correctly excludes defaulted-Literal fields (gate_id, gate_focus, schema_version) and includes `decision_card_digest`, `meta`, `card_id`, `trial_id`, `readiness_status`, `verb`. UTF-8, LF, no BOM (post-patch).
3. `tests/parity/test_decision_card_g2c_shape.py` (132 LOC; 18 tests after parametrize fan-out) — covers LOCKSTEP_CHECK lockstep-files-present, contract-fields presence + model_config inheritance, gate_id+gate_focus+schema_version+readiness_status closed-enum red-rejection (4 enums × 3 invalid values each = 12 parametrized cases), dropped-legacy-fields rejection, schema byte-match, golden round-trip, and frozen mutation rejection. AMEND-7d-i compliant: bare `from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK` (line 11), used at line 42 only.
4. `tests/fixtures/decision_cards/g2c_golden.json` (38 LOC) — UUID4-shape `card_id` (`12121212-1212-4212-8212-121212121212`) / `trial_id` (`bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb`), tz-aware `created_at: "2026-05-05T12:05:00Z"`, `meta.cache_state: "mixed"`, `meta.affected_nodes: ["06", "07"]`, populated `override_trail` with one event, `gate_id: "G2C"`, `gate_focus: "pre_composition_qa"`, `schema_version: "v1"`, `readiness_status: "ready"`, `blocking_issues: []`, `ready_nodes: ["06", "06B"]`, `verb: "approve"`, valid 64-char `decision_card_digest`.

Schema byte-for-byte match verified post-patch (5529 bytes both sides).

### AC-7c.5.G2C-D — Backward-consumer non-regression — PASS

The `tests/parity/ tests/parametrized_harness/ tests/unit/` slice reports `921 passed, 18 skipped` — fully clean (NFR-CG6 governance-tracker now green per Critical Item #3). G2C-critical consumer slices verified green:

- `tests/unit/marcus/test_routing_manifest_driven.py` — PASS (manifest dotted ref string preserved)
- `tests/unit/models/decision_cards/test_per_gate_strict.py` — PASS (rejection of naive datetimes / invalid gate_id / invalid verb continues to hold for migrated G2C)
- `tests/unit/models/decision_cards/test_discriminated_union_routing.py` — PASS (discriminator routes G2C correctly post-DecisionCardBase migration)
- `tests/unit/models/decision_cards/test_manifest_dotted_reference_resolver.py` — PASS (2-class-regime assertion accepts both `DecisionCard` and `DecisionCardBase`; G1 already established this pathway)
- `tests/unit/manifest/test_schema.py` — PASS (manifest schema test dotted-ref preserved)
- Constructor-site updates: `production_runner.py:434` and `m3_trial.py:169` correctly drop `drafted_proposal`/`evidence`/`risks`, supply `decision_card_digest="0" * 64`, convert legacy meta to `_base_card_meta(...)`, default `gate_focus`/`schema_version` to inherited values
- Documentation references (`docs/conversational-gates/g2c-operator-reference.md` + `docs/operator/production-trial-playbook.md` + `docs/dev-guide/sources-of-truth.md`) deferred to follow-on `slab-7c-g1-g4-decision-card-doc-refresh` (filed in `deferred-inventory.md`; reactivates after all extend-and-audit stories close)

### AC-7c.5.G2C-E — Class-conformance + Pydantic-v2 14-idiom — PASS

Class-conformance: T1 baseline 16 → post-T9 19 (+3 = G2C + G3 + G4 sibling additions in working tree). G2C alone increments by +1.

Pydantic-v2 14-idiom checklist (per `docs/dev-guide/pydantic-v2-schema-checklist.md`):

| Idiom | Status | Evidence |
|---|---|---|
| 1. `extra="forbid"` | PASS | Inherited from `DecisionCardBase` |
| 2. `validate_assignment=True` | PASS | Inherited |
| 3. `frozen=True` | PASS | Inherited |
| 4. Tz-aware datetimes | PASS | `enforce_tz_aware` validator at lines 65–68 |
| 5. UUID4 typing | PASS | `card_id: UUID4` + `trial_id: UUID4` (Pydantic-v2 type) |
| 6. UUID4-version enforcement | PASS | `enforce_uuid4_version` validator at lines 60–63 |
| 7. Closed Literals on enums | PASS | `gate_id`, `gate_focus`, `schema_version`, `readiness_status`, `verb` all `Literal[...]` |
| 8. `Field(...)` with `description` | PASS | Every field |
| 9. Default-factory for mutable defaults | PASS | `blocking_issues` + `ready_nodes` use `default_factory=list`; `created_at` uses `default_factory=lambda: datetime.now(UTC)` |
| 10. Explicit required vs defaulted | PASS | Required: `card_id`, `trial_id`, `readiness_status`, `verb`. Defaulted via Literal: `gate_id`, `gate_focus`, `schema_version`. Defaulted via factory: `created_at`, `blocking_issues`, `ready_nodes` |
| 11. Triple-layer red-rejection on closed enums | PASS | Shape-pin parametrizes `["G1", "G3", 42]` for gate_id, `["trial_open", "motion_clip_approval", None]` for gate_focus, `["v0", "v2", None]` for schema_version, `["pending", "READY", None]` for readiness_status (case-mismatch + adjacent-vocab + null) |
| 12. JSON-schema byte-determinism | PASS-post-patch | Patched to LF; re-emits identically; shape-pin `test_g2c_json_schema_byte_for_byte_match` PASSES |
| 13. Strip-then-non-empty | N/A | G2C has no free-text scalar field; list fields use empty default (correct per readiness_status taxonomy) |
| 14. Internal audit fields excluded from schema | N/A | No internal audit fields on G2C |

---

## Reviewer Patches Applied

### Patch #1 (mechanical, ~1 LOC equivalent): Schema CRLF→LF byte-determinism

**Location:** `app/models/decision_cards/schema/g2c.v1.schema.json`
**Issue:** Codex's T3 schema regen used `Path.write_text(canonical, encoding="utf-8")` per A18, but on Windows this defaults to CRLF line endings. Result: 5726 bytes with CRLF, vs canonical 5529 bytes with LF (the predecessor convention used by G0/G1/G2A/G5/G6).
**Action taken:** Rewrote the schema in-place via:
```python
from pathlib import Path
import json
from app.models.decision_cards.g2c import G2CCard
canonical = json.dumps(G2CCard.model_json_schema(), indent=2, sort_keys=True) + "\n"
Path("app/models/decision_cards/schema/g2c.v1.schema.json").write_bytes(canonical.encode("utf-8"))
```
**Post-patch verification:**
- `read_bytes()` length: 5529 (matches canonical)
- `b"\r\n" in data`: False
- `data.startswith(b"\xef\xbb\xbf")`: False
- Shape-pin: 18/18 PASS
- Sibling-convention parity: matches G0/G1/G2A/G5/G6 LF format

**Follow-on (NOT for this story; for governance refresh):** `docs/dev-guide/specialist-anti-patterns.md::A18` should be updated to specify `Path.write_bytes(canonical.encode("utf-8"))` or `open(..., "w", encoding="utf-8", newline="\n")` rather than the platform-dependent `Path.write_text(..., encoding="utf-8")`. This is filed as a future doc-refresh follow-on (NIT-tier; tracked separately). The patch closes the immediate G2C byte-determinism gap.

---

## Downstream Impact

After 7c.5.G2C close + commit + flip-done, **AMELIA-P3 staggering** unblocks for 4 Wave-3 G2C-aliased HIL surface stories: **7c.9 / 7c.10 / 7c.11 / 7c.12**. Per governance JSON `downstream_dispatch_staggering_keyed`, those 4 MUST dispatch ≥30 minutes apart. Plan dispatch sequence ahead of close (per `feedback_velocity_amendments_slab_7c.md`).

**V7 wave_3_lookahead_policy first baseline:** G2C close is the first P2-clean-×3 baseline cycle for Wave-3 lookahead-cap elevation (default_cap=2 → elevated_cap=3 at G4 close; threshold P2_clean_x3). G2C close is P2-clean (this T11 verdict + sibling G3 + sibling G4 reviews).

---

## Sign-Off

**Reviewer:** Claude (Opus 4.7, T11 standard tier, 2026-05-05)
**Verdict:** PASS — recommend COMMIT + FLIP DONE
**Patches:** 1 mechanical (schema CRLF→LF byte-determinism)
**Sibling-review note:** G3 + G4 reviewed in parallel by separate T11 subagents; the constructor-site shared-file modifications (`production_runner.py`, `m3_trial.py`) and the governance-tracker test (`test_nfr_cg_block_aggregated.py`) span all three; this verdict scopes to G2C-only attribution.

Next steps: commit (G2C four-file lockstep + constructor-site G2C-branch updates + governance-tracker bump + this verdict + Codex dropbox), update `sprint-status.yaml`, update `next-session-start-here.md`, plan AMELIA-P3 staggered dispatch for 7c.9/10/11/12.
