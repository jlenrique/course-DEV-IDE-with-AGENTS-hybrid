# Codex dev-story prompt — Story 7c.3b (§02A G0 Poll-Surface Canonical HIL Pattern; pattern-author for 10 Wave-3 surfaces)

**Cycle:** Claude spec → Codex T1-T5 + T10 self-review → Codex drops `_bmad-output/implementation-artifacts/_codex-handoff/7c-3b.ready-for-review.md` → Claude T11 standard `bmad-code-review` → Claude commit + flip done.
**Wave:** 1 — slot 4 (pattern-author for 10 Wave-3 HIL surfaces 7c.6..15).
**Authored:** 2026-05-05 to immediately unblock Codex post-7c.3a-close.
**Dispatch ordering:** **DISPATCHABLE NOW.** Predecessor 7c.3a operator-marked-done; Directive + DirectiveSource models frozen at `app/composers/section_02a/directive_model.py`.

---

```
Run bmad-dev-story on Story 7c.3b (Slab 7c Wave 1 slot 4; dual-gate; pattern-author for 10 Wave-3 HIL surfaces).

## Required reading (read in order)

1. Story spec: `_bmad-output/implementation-artifacts/migration-7c-3b-section-02a-g0-poll-surface-canonical-hil-pattern.md` (status: ready-for-dev; 4 ACs A-D; 5 task groups T1-T5 + T10/T11).
2. **Predecessor 7c.3a's frozen models**: `app/composers/section_02a/directive_model.py` — `Directive` + `DirectiveSource` + `DirectiveRole` + `ExcludedReason` Pydantic v2 models. The poll surface displays `Directive` + accepts edits that produce new validated `Directive`.
3. **DSL primitives (post-7c.0b/7c.1)**: `app/parity/contracts/__init__.py` — `@parity_contract` decorator + `SurfaceTransportDeclaration` + `iter_registered_surfaces`.
4. **Pattern-precedent for parity-contract registration**: `tests/integration/transport_parity/test_fastapi_mcp_parity.py` (post-7c.1) — module-level `@parity_contract` + sentinel function pattern.
5. **OperatorVerdict canonical model** (verify location at T1): `app/models/operator_verdict.py` — discriminated-union root. §02A variant either extends OR sibling-files; surface as `decision_needed` at T1.3.
6. Slab 7c PRD: `_bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md` — FR-7c-3 + FR-7c-4 + FR-7c-20 + FR-7c-49 + NFR-7c-P4 + NFR-7c-S1 + NFR-7c-X2.
7. Slab 7c epics: `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md` (Story 7c.3b section starting at line 516).
8. Velocity-amendments: `_bmad-output/planning-artifacts/slab-7c-velocity-amendments-2026-05-04.md` — R-tier R2 + t11_tier=standard.
9. Required readings:
   - `docs/dev-guide/pydantic-v2-schema-checklist.md` (14 idioms; OperatorVerdict §02A variant conforms).
   - `docs/dev-guide/dev-agent-anti-patterns.md` (A11 + A-test-1).
   - `docs/dev-guide/story-cycle-efficiency.md` (K-discipline 1.4×).
   - `docs/dev-guide/pytest-xdist-classification.md` (R-tier R2 smoke convention).
10. Governance JSON: `docs/dev-guide/migration-story-governance.json` story `7c-3b` (dual-gate; expected_pts=2; expected_k_target=1.4; r_tier=R2; t11_tier=standard; lookahead_tier=2-AUTHORED; prerequisite_stories=[7c-3a]).

## T1 hard checkpoints (HALT-AND-SURFACE if violated)

- 7c.3a deliverables present: `app/composers/section_02a/directive_model.py` importable; Directive + DirectiveSource models work via `Directive.model_validate({...})`.
- DSL `@parity_contract` importable: `.venv/Scripts/python.exe -c "from app.parity.contracts import parity_contract; print('OK')"`.
- `app/models/operator_verdict.py` location: confirm existence + decide extend-vs-sibling for §02A variant. Document the choice + rationale.
- `tests/_helpers/runtime_subprocess.py` (or analogous transport-test helper) available for HTTP/MCP-stdio testing.
- `app/gates/__init__.py` parent package exists OR can be created cleanly (verify; create if absent).
- Class-conformance: 11; lint-imports: 12 KEPT.
- Refresh broad-regression baseline; 7c.3b is R-tier R2, so smoke-pass + focused-pass + impact-zone is the verification battery.

## Files in scope

**New (~9 files):**
- `app/gates/section_02a/__init__.py` (NEW package marker; public exports).
- `app/gates/section_02a/poll_surface.py` (NEW; G0 poll-surface module — display_directive + submit_verdict + canonicalized digest computation + module-level @parity_contract decorator with surface_id="section_02a_g0_poll" + 3-transport mandatory).
- `app/gates/section_02a/_transports.py` (NEW; CLI + HTTP + MCP-stdio handlers OR delegate to existing transport scaffolding — pick at T1).
- `app/models/operator_verdict_section_02a.py` (NEW IF extending feels risky) OR extend `app/models/operator_verdict.py` (preferred) — T1.3 decision.
- `app/models/directive_edit_payload.py` (NEW; `DirectiveEditPayload` Pydantic-v2 model for field-level edits) OR colocate with OperatorVerdict variant.
- `tests/gates/section_02a/__init__.py` (NEW package marker).
- `tests/gates/section_02a/test_g0_poll_surface_three_transport_parity.py` (NEW; AC-A test pin; 3 parametrized cases + tamper-detection).
- `tests/gates/section_02a/test_g0_poll_surface_field_level_edit.py` (NEW; AC-B test pin; 4 cases incl. binary-file invariant violation re-validation).
- `tests/gates/section_02a/test_g0_poll_surface_dsl_registration.py` (NEW; AC-C test pin; AST + iter_registered + audit floor=10).
- `tests/schemas/operator_verdict/test_section_02a_shape.py` (NEW; AC-D test pin; JSON-Schema hash stability + discriminated-union variant + edit_payload nested schema).

**Optionally new (T1-decision):**
- `tests/schemas/operator_verdict/__init__.py` if directory doesn't exist.
- `tests/gates/__init__.py` if test directory doesn't exist.

**Modified (1 file):**
- `app/models/operator_verdict.py` — IF the §02A variant extends the existing discriminated-union root (preferred per T1.3 default). Spec: add §02A variant + DirectiveEditPayload import.

**Do NOT modify:**
- 7c.3a deliverables (`app/composers/section_02a/**` — read only).
- 7c.0a's TripwireLedgerEntry, 7c.0b's DSL package, 7c.1's refactored test files (all read-only).
- pyproject.toml (no import-linter changes; no addopts changes).
- Any other production code outside `app/gates/section_02a/` + the OperatorVerdict variant.

**Do NOT introduce:**
- New third-party deps. Pydantic v2 + LangChain + httpx + MCP transport infrastructure (already shipped via prior Slabs).
- Per-test-function `@parity_contract` decoration (module-level only).
- §02A-specific assumptions baked into reusable helpers (canonicalize digest computation as a parameterized helper that 10 downstream HIL surfaces can copy).
- Mocking of OperatorVerdict in 3-transport parity test.
- Live-LLM calls (this story doesn't invoke LLMs; it operates on pre-composed directives).

## Critical implementation notes

- **Pattern-replicability is the load-bearing concern.** Every helper introduced here gets COPIED into 10 downstream Wave-3 stories. If §02A-specific assumptions leak into the helpers (e.g., hardcoded `Directive` type), 10 downstream stories duplicate code. Parameterize aggressively: the digest-computation helper takes a `model: BaseModel` arg, not `directive: Directive`.
- **K-target 1.4× ≈ ~3.5K LOC ceiling.** Estimate ~800-1500 LOC. Comfortable.
- **R-tier R2** = focused + impact-zone + smoke. NOT broad regression. The `pytest --smoke -p no:randomly` flag (post-7c.0c) is canonical for R2 verification.
- **3-transport byte-equivalence** is the NFR-7c-X2 invariant. The CLI + HTTP + MCP-stdio handlers MUST produce IDENTICAL `OperatorVerdict` payloads (modulo transport-frame metadata). Test asserts byte-identicality (or canonicalized-identicality if framing differs by transport).
- **Verdict-digest match enforced on resume** is the NFR-7c-S1 D3 invariant. `resume_from_verdict()` raises `GateError` if digest mismatches. Test asserts both PASS-on-match AND FAIL-on-tamper.
- **Field-level edit re-validation** is the FR-7c-4 safety net. The poll surface CANNOT submit an edited directive that fails Directive.model_validate (e.g., D4 binary-file invariant from 7c.3a). Test exercises the binary-file violation case explicitly.
- **DSL self-registration via @parity_contract** is the FR-7c-20 contract. Module-level decorator on a sentinel function (consume 7c.1 pattern-precedent). Surface_id="section_02a_g0_poll".
- **OperatorVerdict canonicalization conventions:** lock at T1 + document in Dev Notes. Pick (a) digest = SHA256(YAML | JSON serialize) (b) edit_payload schema (typed dict[str, dict] OR DirectiveEditPayload model). Whichever Codex picks becomes the canonical pattern for 10 downstream HIL surfaces.

## Verification battery (T5; R-tier R2)

```bash
# Focused tests:
.venv/Scripts/python.exe -m pytest tests/gates/section_02a/ tests/schemas/operator_verdict/test_section_02a_shape.py -p no:randomly -q --tb=short

# Impact-zone (post-7c.3a's tests stay green; post-7c.1's transport-parity stays green):
.venv/Scripts/python.exe -m pytest tests/composers/section_02a tests/integration/transport_parity tests/integration/transports tests/parity tests/structural -p no:randomly -q --tb=short

# Smoke pass (R2 sufficient — NOT broad R3):
.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short

# Class-conformance (11 contracts; UNCHANGED):
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/

# Lint-imports (12 KEPT; UNCHANGED — no contract change):
.venv/Scripts/lint-imports.exe

# Sandbox-AC validator:
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-3b-section-02a-g0-poll-surface-canonical-hil-pattern.md

# Self-registration audit at floor=10 (post-7c.1's 9 + this story's 1):
.venv/Scripts/python.exe -m app.parity.contracts._audit --declared-floor 10

# Ruff hygiene:
.venv/Scripts/python.exe -m ruff check app/gates/section_02a/ app/models/operator_verdict*.py tests/gates/section_02a/ tests/schemas/operator_verdict/test_section_02a_shape.py
```

Expected post-7c.3b outcomes:
- 4 new focused tests PASS.
- Impact-zone tests UNCHANGED (no regression).
- R2 smoke pass UNCHANGED (200 nodeids PASS; new 7c.3b tests not in smoke manifest yet — re-curate at next wave-close).
- Class-conformance: 11 (UNCHANGED).
- Lint-imports: 12 KEPT (UNCHANGED).
- Sandbox-AC: PASS.
- Self-registration audit at floor=10: PASS.
- Ruff: clean.

## T10 + T11

**T10:** Codex G6 self-review at `_bmad-output/implementation-artifacts/_codex-handoff/7c-3b.ready-for-review.md`. Per dropbox protocol — drop the completion notice. Flip story status `in-progress` → `review` in spec file.

**Critical T10 content:**
- File list (~9 files NEW + 1 modified).
- T1 decisions: OperatorVerdict location (extend vs sibling); digest canonicalization rule (YAML vs JSON); edit_payload schema (typed-dict vs DirectiveEditPayload model). Document each + rationale.
- 3-transport byte-equivalence wall-clock + verification.
- Verdict-digest tamper-detection test result.
- Field-level edit re-validation: 4 cases coverage incl. binary-file invariant.
- Self-registration audit at floor=10 PASS.
- Pattern-replicability self-assessment: are the helpers parameterizable? (List each helper + parameterization choice + suitability for 10 downstream replications.)

**T11:** Claude (separate cold context from Codex dev) does FINAL `bmad-code-review` (single-gate; **standard tier**). Review verdict at `_bmad-output/implementation-artifacts/7c-3b-code-review-2026-05-NN.md`. Claude verifies:
- Canonical pattern is replicable (10 Wave-3 stories will copy with minimal adaptation).
- 3-transport byte-equivalence holds (NFR-7c-X2).
- Verdict-digest match enforced on resume (NFR-7c-S1 D3 invariant).
- Field-level edit re-validation correctly catches D4 invariants from 7c.3a's Directive model.
- @parity_contract module-level registration with correct surface_id + transport set.
- Combined-pass invariant: NFR-7c-R2 baseline preserved.

Claude applies remediation cycles per HALT-AND-REMEDIATE; commits the diff; flips `migration-7c-3b-section-02a-g0-poll-surface-canonical-hil-pattern: review → done` in sprint-status.yaml.

## Boundary

- **HALT and surface to operator on:**
  (a) 7c.3a's Directive model not importable.
  (b) DSL `@parity_contract` not importable.
  (c) OperatorVerdict location decision ambiguous AND extending breaks existing tests.
  (d) `tests/_helpers/runtime_subprocess.py` (or analogous transport helper) not available — without 3-transport infrastructure, AC-A can't be exercised.
  (e) 3-transport byte-equivalence FAILS (CLI + HTTP + MCP-stdio produce DIFFERENT OperatorVerdict payloads for same input) — investigate; surface for design discussion.
  (f) Verdict-digest tamper-detection test FAILS — D3 invariant violation; HALT-AND-SURFACE.
  (g) Field-level edit re-validation does NOT catch D4 binary-file invariant — Pydantic invariants from 7c.3a not propagating; HALT.
  (h) Self-registration audit at floor=10 FAILS — `surface_id="section_02a_g0_poll"` not registering correctly.
  (i) Combined parallel + serial pass total ≠ T1 baseline (NFR-7c-R2 invariant violation).
  (j) Lint-imports KEPT count ≠ 12.
  (k) Class-conformance regression.

- **Do NOT touch:**
  - 7c.3a deliverables (composer body + Directive model — read only).
  - 7c.0b's DSL package.
  - 7c.1's refactored transport-parity test files.
  - pyproject.toml.

- **Do NOT introduce:**
  - New third-party deps.
  - Per-test-function `@parity_contract` decoration.
  - §02A-specific assumptions baked into reusable helpers.
  - Mocking of OperatorVerdict.
  - Live-LLM calls.
  - Defensive `serial` markers.
```

---

## Operator dispatch checklist (before sending this prompt to Codex)

1. ☐ Verify 7c.3a operator-marked-done OR sprint-status reflects done (7c.3a's deliverables in tree are sufficient even if T11 commit not yet landed).
2. ☐ Run `.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-3b-section-02a-g0-poll-surface-canonical-hil-pattern.md` → expect PASS.
3. ☐ AMELIA-P2 freshness check: Claude re-diffs `migration-7c-3b-section-02a-g0-poll-surface-canonical-hil-pattern.md` against this prompt; if spec hash changed since 2026-05-05 authoring, regenerate.
4. ☐ Verify governance JSON entry for 7c-3b is current — locked at v2026-05-04-velocity-amendments-bundle.
5. ☐ Confirm sprint-status.yaml shows `migration-7c-3b-section-02a-g0-poll-surface-canonical-hil-pattern: ready-for-dev`.
6. ☐ Dispatch this prompt to Codex; Codex flips status `ready-for-dev → in-progress` at T1 start.

## Post-Codex-T10 dropbox-watch protocol

1. ☐ Codex drops `_bmad-output/implementation-artifacts/_codex-handoff/7c-3b.ready-for-review.md` upon T10 completion.
2. ☐ Claude (separate cold context) reads the dropbox notice + the ~10-file diff + canonicalization-decisions table; runs `bmad-code-review` (T11; standard tier).
3. ☐ Claude verifies pattern-replicability + 3-transport byte-equivalence + digest-match + edit re-validation + DSL registration + audit floor=10 + combined-pass invariant.
4. ☐ Claude applies remediation cycles per HALT-AND-REMEDIATE if any.
5. ☐ Claude commits + flips `migration-7c-3b-section-02a-g0-poll-surface-canonical-hil-pattern: review → done`.
6. ☐ At 7c.3b close, **the 10 Wave-3 HIL surface stories (7c.6..15) inherit the canonical pattern** + can dispatch as their G* predecessor closes per per-surface-overlap rule.
