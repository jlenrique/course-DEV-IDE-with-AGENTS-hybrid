# T11 Standard Code Review — Story 7c.3b (Section 02A G0 Poll-Surface Canonical HIL Pattern)

**Story key:** `migration-7c-3b-section-02a-g0-poll-surface-canonical-hil-pattern`
**Reviewer:** Claude (Opus 4.7)
**T11 tier:** standard (per AMEND-V3; AC count = 4; first canonical HIL surface; pattern-replicability target for 7+ downstream gates)
**Diff size:** ~1,150 LOC (12 new files: 1 surface + 1 transports + 1 gate verdict model + 9 test files; 0 modified outside artifact-tracking)
**Review date:** 2026-05-05

---

## Verdict: **PASS** (zero patches; 2 known inherited issues confirmed non-regressing; 1 informational CLI-discovery-root follow-on)

Story 7c.3b delivers the canonical Section 02A G0 poll-surface as the **byte-equivalent three-transport HIL pattern** that 7+ downstream gates (G1/G2A/G2C/G3/G4/G5/G6) will replicate. The implementation cleanly separates **domain-agnostic substrate** (`canonical_model_bytes` + `compute_model_digest` + `submit_verdict` neutral path) from **Section 02A-specific behavior** (`apply_directive_edit` field-level Directive re-validation), satisfying the pattern-replicability ask without over-coupling to per-gate domain models.

The 4 ACs A-D are all covered with focused tests (15 passed). Codex's 3 T1 decisions are well-reasoned and explicitly documented: (1) sibling `Section02AOperatorVerdict` model at `app/models/operator_verdict_section_02a.py` rather than extending the live global `app/models/state/operator_verdict.py` (avoids unrelated four-file lockstep churn outside this story's scope); (2) sha256 over canonical JSON bytes via `model_dump(mode="json")` + sorted_keys + compact_separators + UTF-8 (transport-neutral); (3) `DirectiveEditPayload(edits: dict[str, dict[str, Any]])` field-level edit schema (preserves FR-7c-49 nested visibility while allowing downstream gates to copy + adapt).

---

## Verification Battery

| Check | Status | Evidence |
|---|---|---|
| Sandbox-AC validator | ✅ PASS | Codex T10 |
| Class-conformance | ✅ PASS | 11 contracts (UNCHANGED) |
| `lint-imports` | ✅ PASS | 12 KEPT / 0 broken (UNCHANGED; no contract change) |
| Focused tests | ✅ PASS | 15 passed (3 transport parity + 4 edit-path + tamper + AST registration + schema-shape + cardinality floor) |
| Smoke suite | ✅ PASS | 181 passed / 18 skipped |
| R2 broad regression | ✅ PASS | 39 failed / 4077 passed (T1 baseline preserved; checkout-level red unchanged from 7c.3a) |
| Self-registration audit (explicit roots) | ✅ PASS | `surface_cardinality=10`, `audit_status=PASS` |
| Ruff hygiene | ✅ PASS | clean |

---

## AC Coverage Verification

### AC-7c.3b-A — Three-transport byte-equivalence + tamper-detection (PASS)

`tests/gates/section_02a/test_g0_poll_surface_three_transport_parity.py` asserts CLI / HTTP / MCP-stdio handlers emit identical `operator_verdict` payloads for the same directive + operator action. The deterministic parity timestamp design (default = `directive.composed_at`; callers may pass `submitted_at` explicitly for real submissions) is the right tradeoff for the byte-equivalence assertion — flagged by Codex's Blind Hunter self-review and confirmed by T11. Tamper test exercises `GateError("digest_mismatch", ...)` on resume with mutated digest. **Module-level `@parity_contract(surface_id="section_02a_g0_poll", mandatory_transports=["cli", "http", "mcp-stdio"], optional_transports=["mcp-subprocess"])`** confirmed at `app/gates/section_02a/poll_surface.py:38-42`.

### AC-7c.3b-B — Field-level edit application + full re-validation (PASS)

`tests/gates/section_02a/test_g0_poll_surface_field_level_edit.py` covers 4 edit paths: (1) approved directive returns unchanged; (2) edit verdict applies field updates, re-validates via `Directive.model_validate(...)`, and emits new digest; (3) role reclassification clears/sets dependent fields per Trial-2 finding #2 binary-file invariant; (4) unknown `src_id` raises `GateError("directive_edit_invalid", ...)`. The `_EDITABLE_SOURCE_FIELDS` frozenset (`description`, `excluded_reason`, `expected_min_words`, `locator`, `provider`, `role`) at `poll_surface.py:26-35` is the explicit safelist; non-editable field rejection is unit-tested.

### AC-7c.3b-C — DSL registration + audit cardinality (PASS)

`tests/gates/section_02a/test_g0_poll_surface_dsl_registration.py` asserts: (1) AST-level `@parity_contract` decorator at module scope with closed transport keywords; (2) registry membership via `app/parity/contracts/_registry.py`; (3) explicit-root self-registration audit floor=10 PASS via the discovery roots `app.gates.section_02a` + `tests.integration.transport_parity` + `tests.integration.transports` (matching 7c.1's expected registration locations). The 10-surface floor is consistent with the 7c.1 substrate.

### AC-7c.3b-D — Per-surface OperatorVerdict schema-shape pin (PASS)

`tests/schemas/operator_verdict/test_section_02a_shape.py` asserts: (1) JSON Schema hash matches frozen value; (2) `surface_id` const = `"section_02a_g0_poll"`; (3) `verb` Literal closed-set `{"approve", "edit", "reject"}`; (4) `decision_card_digest` sha256-hex pattern; (5) nested `DirectiveEditPayload` schema visibility; (6) frozen=True / extra=forbid / validate_assignment=True triple; (7) UUID4 enforcement on `run_id`. **Pattern-replicability confirmed:** this shape-pin is structurally identical to the harness 7c.4b will produce, so 7c.3b's standalone shape test will reshape into the parametrized harness call at 7c.4b close (per AMEND-V5 D3 contract decision; documented as optional T1 decision in the 7c.4b spec).

---

## Pydantic-v2 14-Idiom Conformance (per `docs/dev-guide/pydantic-v2-schema-checklist.md`)

`app/models/operator_verdict_section_02a.py` confirmed conforming on all applicable idioms:

| Idiom | Evidence |
|---|---|
| `extra="forbid"` | both models, ConfigDict |
| `validate_assignment=True` | both models, ConfigDict |
| `frozen=True` | both models, ConfigDict |
| Timezone-aware datetimes | `_require_tz_aware` field_validator at line 87-90 |
| UUID4 enforcement | `_require_uuid4` field_validator at line 82-85 |
| Closed Literals (no string fallback) | `Section02AVerdictVerb`, `Section02ASurfaceId` |
| Triple-layer red-rejection on closed enums | Literal + ConfigDict.extra=forbid + model_validator verb-payload consistency check |
| Field-level descriptions | all fields |
| sha256-hex pattern validation | `_require_sha256` field_validator |
| `default_factory=lambda: datetime.now(tz=UTC)` | `submitted_at` |
| `pattern=` on operator_id | `^[a-zA-Z][a-zA-Z0-9_-]+$` |
| `min_length=1` on edits | DirectiveEditPayload.edits |
| `model_validator(mode="after")` for cross-field invariants | `_enforce_verb_payload_consistency` (4 cases: edit-requires-payload + edit-forbids-reject_reason + reject-requires-reason + approve-forbids-both) |
| Non-empty edit-block enforcement | `_reject_empty_update_blocks` field_validator |

---

## Pattern Replicability Assessment (T11 critical lens)

The reusable substrate at `app/gates/section_02a/poll_surface.py` cleanly factors into:

- **Domain-agnostic helpers** (downstream gates inherit verbatim): `canonical_model_bytes(model: BaseModel)` → bytes, `compute_model_digest(model: BaseModel)` → sha256-hex, `submit_verdict(...)` neutral path that builds OperatorVerdict + handles digest computation, `resume_from_verdict(...)` neutral path that re-derives expected digest + raises `digest_mismatch`.
- **Section 02A-specific edit behavior** (downstream gates replace only this seam): `apply_directive_edit(directive, edit_payload) -> Directive` with `_EDITABLE_SOURCE_FIELDS` frozenset.
- **Per-surface verdict model** (downstream gates author their own; harness'd from 7c.4b onward): `Section02AOperatorVerdict` with verb-payload consistency invariants tailored to this gate's allowed verbs.

The boundary is correctly drawn: domain-agnostic substrate at `compute_model_digest` and `submit_verdict`; per-gate replacement only at `apply_directive_edit` (the only gate-specific edit-validation seam). 7+ downstream gates can each contribute one ~50 LOC apply-edit function + one ~120 LOC OperatorVerdict model and inherit everything else. **Pattern replicability target met.**

---

## Two Known Inherited Failures (confirmed non-regressing)

Codex flagged 2 failures in the broad-regression delta as inherited from prior story baseline:

1. **`tests/parity/test_nfr_cg_block_aggregated.py::test_nfr_cg_block_structural_evidence[NFR-CG6]`** — pre-existing in 7c.3a's broad-regression baseline (39-failure checkout-level class). Verified by inspection: NFR-CG6 evidence aggregation depends on substrate downstream of 7c.3b's scope; **no causal link to 7c.3b's diff.**
2. **`tests/structural/test_tw_7c_4_5_6_detection_scaffolds_present.py::test_tw_7c_4_detector_exists_and_passes`** — TW-7c-4 detector script self-trip on its own filename containing the literal `"live_dispatch"` substring (the detector greps for this token across the repo and matches itself). Pre-existing in 7c.0b's broad-regression baseline. Deferred to a future hardening pass (script needs `git_ls_files` + path-exclusion for the detector's own location). **No causal link to 7c.3b's diff.**

Both are confirmed inherited (T1 broad baseline = T9 broad baseline = 39 failures); **broad-regression delta = 0**.

---

## Informational Follow-On (not a patch)

**Audit CLI default-roots discovery shortfall:** Codex correctly identified that the prompt's standalone command `.venv/Scripts/python.exe -m app.parity.contracts._audit --declared-floor 10` defaults to app-only discovery roots and returns `surface_cardinality=2` (finds only section_02a's registration), failing the floor=10. The **story-level audit** with explicit roots `app.gates.section_02a`, `tests.integration.transport_parity`, `tests.integration.transports` correctly returns `surface_cardinality=10` PASS. This matches 7c.1's expected registration locations.

**T11 adjudication:** This is a **prompt-side / CLI-discovery-roots issue**, not a 7c.3b regression. The DSL package internals (`app/parity/contracts/_audit.py`) were correctly NOT modified per the prompt's "DO NOT touch 7c.0b DSL package" boundary. The fix belongs in **either** (a) the audit CLI's default-discovery-root expansion in a future 7c.0b-hardening story, **or** (b) the prompt template's standalone-command example updating to use the explicit-roots flag. **No patch required for 7c.3b close.** Filed as informational follow-on; will surface at 7c.5.G* spec authoring as a transport-tests-discovery convention to lock in.

---

## Findings (zero MUST-FIX; zero NIT)

- All 4 ACs covered with focused tests + smoke + broad regression baselines preserved.
- Pydantic-v2 14-idiom conformance verified for both `Section02AOperatorVerdict` and `DirectiveEditPayload`.
- Triple-layer red-rejection pattern (Literal + ConfigDict.extra=forbid + model_validator) correctly applied for closed enums.
- Module-level `@parity_contract` registration with all 4 transport keywords (3 mandatory + 1 optional) confirmed.
- Pattern-replicability boundary cleanly drawn between domain-agnostic substrate (digest helpers + neutral submit/resume paths) and gate-specific edit behavior.
- T1 decisions explicitly documented and reasonable (sibling model location avoids unrelated lockstep churn; deterministic parity timestamp enables byte-equivalence; nested edit-payload schema preserves FR-7c-49 visibility).
- No cross-§section imports introduced (gates section_02a's `app/gates/section_02a/` package contains only Section 02A-specific imports + the domain-agnostic helpers consumed via direct module body — confirms 7c.4b's C6 contract will populate cleanly with empty source-side breakage risk).
- TW-7c-4 detector self-trip + NFR-CG6 confirmed inherited (broad-regression delta = 0).
- Informational follow-on flagged for audit-CLI discovery-roots (no 7c.3b patch).

---

## Sign-Off

**Verdict:** PASS (zero patches; zero deferred items in 7c.3b scope; 1 informational follow-on for downstream).

The Section 02A G0 poll surface is the **canonical pattern target** for Slab 7c HIL gates. 7+ downstream stories (7c.5.G* + alias gates) inherit the substrate via direct module imports; per-gate replacement is contained to ~50 LOC of edit-behavior + ~120 LOC of per-gate OperatorVerdict. Pattern-replicability ask satisfied.

**Next action:** Stage and commit 7c.3b deliverables; flip `migration-7c-3b-section-02a-g0-poll-surface-canonical-hil-pattern: review → done` in sprint-status.yaml.

**Unblocks at 7c.3b close:**
- 7c.4b Gate-Family Foundation Implementation now has its OperatorVerdict-pattern-precedent confirmed (D3 parametrized harness can target this shape); 7c.4b is currently `ready-for-dev` with cross-agent MANDATORY pre-flight contracts D1-D8 LOCKED.
- 8 per-gate four-file-lockstep stories 7c.5.G0..G6 (4 fresh-author + 4 extend-and-audit) will replicate this canonical pattern post-7c.4b-close.
