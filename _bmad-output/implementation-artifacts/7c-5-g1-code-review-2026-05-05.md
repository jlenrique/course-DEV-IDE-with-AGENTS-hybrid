# T11 Standard Code Review — Story 7c.5.G1 (G1 DecisionCard Extend-and-Audit)

**Story key:** `migration-7c-5-g1-decision-card-extend-and-audit`
**Reviewer:** Claude (Opus 4.7) — T11 standard tier (post-T9 standard review; PRE-T2 cross-agent T1 review previously PASSed at `5c325a1`)
**Gate-mode:** `dual-gate-cross-agent-CONTRACT-EVOLUTION` (T11 itself is `standard` tier; the "cross-agent" component refers to the T1 PRE-T2 review, NOT this T11)
**R-tier:** R3 (full broad regression)
**K-target:** 1.4× (extend-and-audit; heavier than fresh-author)
**Diff size:** ~660 LOC across 17 files (4 new G1 lockstep + 6 modified 2-class-regime substrate + 2 unexpected scope-expansion + 5 artifacts)
**Review date:** 2026-05-05

---

## Verdict: **PASS — recommend COMMIT + FLIP DONE**

The G1 extend-and-audit migration is structurally sound. The four-file lockstep is byte-deterministic. All five ACs (A–E) verify. The frozen-hash AMELIA-P4 baseline is unchanged; the on-disk `g1.py` hash diverges from the recorded frozen value as intended (body extended; contract-diff §1–§8 is the audit trail justifying divergence). The PowerShell BOM patch (anti-pattern A18) is correctly applied. The two unexpected scope-expansion files (`app/manifest/refs.py` + `app/replay/regression.py`) are defensible: `refs.py` widens `expected_base_class` to accept `tuple[type, ...]` (clean parameter-type extension consumed by `compiler.py`), and `regression.py` swaps `meta["reject_rate"]` to `meta.get("reject_rate", 0.0)` (defensive backward-compat fix surfaced by T6 broad-regression run). All six PARALLEL-DISPATCH GUARDRAILS pass. Pydantic-v2 14-idiom checklist conforms.

The PRE-T2 T1 audit's verdict reversal on `drafted_proposal` / `evidence` (originally marked DROP based on static grep; reversed at T6 when smoke/integration tests exposed live consumers in `tests/composition/test_pre_gate_marcus_precedence_unaltered.py` + `tests/integration/marcus/test_runner_threads_pre_fill_to_decision_card.py` + `tests/integration/marcus/test_gate_handler_loads_adjacent_summary.py`) is correctly documented in BOTH the contract-diff and the backward-consumer audit artifacts. **This is a meaningful audit-defect class** — see Critical Item #1 below for the recommended process-level follow-on for G2C/G3/G4.

No MUST-FIX. No SHOULD-FIX. Zero patches applied by this reviewer.

---

## Verification Battery

| Check | Status | Evidence |
|---|---|---|
| Focused G1 shape-pin | PASS | `18 passed in 3.45s` — 18 tests after parametrize fan-out (1 LOCKSTEP_CHECK + 1 required-fields + 3+3+3 closed-enum red rejections + 1 schema byte-match + 1 golden round-trip + 2+2 non-empty validators + 1 frozen-mutation rejection) |
| AMEND-7d-i AST-scan structural test | PASS | `2 passed in 3.19s` — `test_decision_card_shape_pins_do_not_rederive_tw_7c_3_rule` confirms G1 does not contain `FOUR_FILE_GLOBS` or `all_four_present` literals |
| Decision-cards + gates + routing slice | PASS | `57 passed in 6.57s` — covers test_per_gate_strict, test_discriminated_union_routing, test_manifest_dotted_reference_resolver (2-class-regime assertion), test_routing_manifest_driven, gates helpers |
| Live drafted_proposal/evidence consumer tests | PASS | `7 passed in 6.19s` — composition/test_pre_gate_marcus_precedence_unaltered + 2 integration/marcus tests; T6 audit-reversal evidence holds |
| `tests/parity/` + `tests/parametrized_harness/` + `tests/unit/` broad slice | PASS-modulo-inherited | `870 passed, 1 failed, 18 skipped in 11.73s` — sole failure is `test_nfr_cg_block_aggregated.py::test_nfr_cg_block_structural_evidence[NFR-CG6]` (governance JSON version drift `2026-04-29-slab7b-twelve-stories` vs `2026-05-04-velocity-amendments-bundle`); **inherited from G6 close, NOT G1-introduced** |
| Class-conformance | PASS | `PASS: 16 parity contract file(s) conform (11 activation + 5 decision-card shape-pin)` — matches Codex T9 claim 15→16 (G0+G2A+G5+G6+G1 = 5 shape-pins) |
| Lint-imports | PASS | `Contracts: 12 kept, 0 broken` (UNCHANGED) |
| Sandbox-AC validator | PASS | `PASS — no sandbox-AC violations across 1 story file(s)` |
| Ruff (in-scope files) | PASS | `All checks passed!` — covers g1.py + test_decision_card_g1_shape.py + compiler.py + refs.py + resume_api.py + regression.py |
| Schema-emission determinism | PASS | In-Python byte comparison: emitted (5900 chars) == on-disk (5900 chars), MATCH |
| BOM check on schema JSON | PASS | `NO_BOM` + first 16 bytes = `b'{\n  "$defs": {\n '` (no UTF-8 BOM `\xef\xbb\xbf` prefix) |
| Frozen-hash AMELIA-P4 unchanged | PASS | `FROZEN_AT_SHIP_HASHES['g1'] == "4fe0e985d2285e3219b103424765dec009043564960ec43af1fb5710d2a1a196"` UNCHANGED post-T9 (current on-disk hash `7aa6897b3e4989e073f2db3215e7d2aaf7e9c09dc5ea2bf2bd31f3c5793df9f0` differs intentionally; contract-diff justifies) |

---

## AC Compliance Verification

### AC-7c.5.G1-A — Pre-T2 contract-diff + backward-consumer audit + frozen-hash artifacts — PASS

All three deliverables present, structurally sound, and post-T6 corrections applied:

1. `_bmad-output/implementation-artifacts/migration-7c-5-g1-contract-diff.md` — 95 LOC; 8 sections covering legacy G1 fields disposition (§1), legacy DecisionCard base disposition (§2 — UPDATED at T6 to reflect `drafted_proposal`/`evidence` reversal from DROP → preserve-via-re-declaration), legacy DecisionCardMeta disposition (§3), new fields (§4: `schema_version` + `decision_card_digest`), closed-enum tightening (§5), pattern-parity ratchets (§6), net diff (§7), schema-emission changes (§8 NEW post-T6 documenting the regenerated schema).
2. `_bmad-output/implementation-artifacts/migration-7c-5-g1-backward-consumer-audit.md` — 82 LOC; per-call-site verdicts for 24 executable sites + 3 non-grep consumers (compiler.py:328 + test_manifest_dotted_reference_resolver.py:47 + resume_api.py:16-79) + 4 doc references. Field-Access Summary §UPDATED to reflect T6-discovered live consumers in `tests/composition/` + `tests/integration/marcus/` reading `card.drafted_proposal` / `card.evidence` directly.
3. `app/models/decision_cards/_frozen_hashes.py` — 13 LOC; all 4 gates (g1/g2c/g3/g4) recorded; G1 hash matches PRE-T2 review record; UNCHANGED post-T9.

### AC-7c.5.G1-B — AMELIA-P4 frozen-hash delta-AC — PASS

`_frozen_hashes.py` UNCHANGED post-T9. Codex T2 verified the pre-extension on-disk hash matched `FROZEN_AT_SHIP_HASHES["g1"]` before extending; current post-T9 on-disk hash (`7aa6897b...`) intentionally diverges — the contract-diff artifact (AC-A) is the audit trail. The three sibling hashes (g2c/g3/g4) are preserved unmodified for future extend-and-audit stories.

### AC-7c.5.G1-C — Four-file lockstep co-commit — PASS

All four files present, co-committed:

1. `app/models/decision_cards/g1.py` (96 LOC) — `G1Card(DecisionCardBase)` (line 16); inheritance migration from legacy `DecisionCard` complete. Re-declares: `card_id` / `trial_id` (UUID4 — Pydantic-v2 type, not bare UUID; line 23/27); `gate_id: Literal["G1"]` + `gate_focus: Literal["trial_open"]` + `schema_version: Literal["v1"]` (lines 31/35/19 — closed Literals); `created_at` (datetime; default UTC factory); `verb: DecisionCardVerb` (closed Literal). Preserves: `drafted_proposal` (line 43) + `evidence` (line 47) as DIRECT G1 fields per T6 reversal; `trial_summary` (strip-then-non-empty validator line 80–85); `opened_by` (strip-then-non-empty validator line 87–92); `next_nodes` (default empty list).
2. `app/models/decision_cards/schema/g1.v1.schema.json` (208 LOC) — REGENERATED; emits `additionalProperties: false`, `const: "G1"` for gate_id, `const: "trial_open"` for gate_focus, `const: "v1"` for schema_version. Required array correctly excludes defaulted-Literal fields. UTF-8 without BOM (anti-pattern A18 patch verified).
3. `tests/parity/test_decision_card_g1_shape.py` (130 LOC; 18 tests after parametrize fan-out) — covers field-presence, gate_id+gate_focus+schema_version closed-enum red-rejection (3 enums × 3 invalid values each = 9), schema byte-match, golden round-trip, trial_summary+opened_by non-empty (2 × 2 = 4), and frozen mutation rejection. AMEND-7d-i compliant: bare `from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK` only (line 11); used at line 44 only.
4. `tests/fixtures/decision_cards/g1_golden.json` (53 LOC) — UUID4-shape `card_id`/`trial_id`, tz-aware `created_at: "2026-04-26T12:00:00Z"`, `meta.cache_state: "healthy"`, `meta.affected_nodes: ["04","05"]`, populated `override_trail` with one event, `gate_id: "G1"`, `gate_focus: "trial_open"`, `schema_version: "v1"`, `verb: "approve"`, valid 64-char lowercase hex `decision_card_digest`.

Schema byte-for-byte match verified in-Python (5900 chars on both sides).

### AC-7c.5.G1-D — Backward-consumer non-regression — PASS

The `tests/parity/ tests/parametrized_harness/ tests/unit/` slice reports `870 passed, 1 failed, 18 skipped` — sole failure is the inherited `NFR-CG6` governance JSON version drift carried forward from G6 close. G1-critical consumer slices verified green:

- `tests/unit/marcus/test_routing_manifest_driven.py` — PASS
- `tests/unit/models/decision_cards/test_per_gate_strict.py` — PASS
- `tests/unit/models/decision_cards/test_discriminated_union_routing.py` — PASS
- `tests/unit/models/decision_cards/test_manifest_dotted_reference_resolver.py` — PASS (2-class-regime assertion accepts BOTH `DecisionCard` and `DecisionCardBase`)
- `tests/unit/gates/_helpers.py` consumers — PASS
- T6-reversal evidence: `tests/composition/test_pre_gate_marcus_precedence_unaltered.py` (drafted_proposal direct read) + `tests/integration/marcus/test_runner_threads_pre_fill_to_decision_card.py` (drafted_proposal default shape) + `tests/integration/marcus/test_gate_handler_loads_adjacent_summary.py` (evidence direct read) — `7 passed in 6.19s`

Documentation references (`docs/operator/production-trial-playbook.md` + `docs/dev-guide/sources-of-truth.md`) deferred to follow-on `slab-7c-g1-g4-decision-card-doc-refresh` filed in `deferred-inventory.md` — reactivates after all four extend-and-audit stories close.

### AC-7c.5.G1-E — Class-conformance + Pydantic-v2 14-idiom — PASS

Validator reports `16 parity contract file(s) conform (11 activation + 5 decision-card shape-pin)`. The +1 G1 increment (15→16) matches Codex T9 claim. See Pydantic-v2 14-idiom checklist below — all applicable idioms PASS.

---

## Critical Item #1: T1 Audit Verdict Reversal on `drafted_proposal` / `evidence`

The PRE-T2 cross-agent T1 review (committed `5c325a1`) ratified the contract-diff §2 verdict that `drafted_proposal` and `evidence` would be DROPPED with "no audited consumer reads after construction." Codex's T6 broad-regression run uncovered live consumers in three test files that read these fields DIRECTLY off the constructed G1Card:

1. `tests/composition/test_pre_gate_marcus_precedence_unaltered.py:28` — `card.drafted_proposal["decision"]`
2. `tests/integration/marcus/test_runner_threads_pre_fill_to_decision_card.py:45,66` — `_build_decision_card(...).drafted_proposal`
3. `tests/integration/marcus/test_gate_handler_loads_adjacent_summary.py:35,42,63` — `card.evidence[-1]` and length assertions

Codex correctly remediated by reversing the verdict — both fields preserved as DIRECT G1Card fields (g1.py:43,47), schema regenerated to include them, golden fixture populated with non-empty payloads, and BOTH artifacts (contract-diff §2 + backward-consumer audit Field-Access Summary) updated to reflect the reversal.

**Process-level finding (not blocking; recommend a deferred-inventory follow-on for G2C/G3/G4):**

The T1 audit pattern as ratified in spec AC-A is **static-grep-only**: it identifies field-access patterns through `rg G1Card` + dotted-import enumeration. This misses runtime consumers exercised only at smoke/integration test time. For G1 the cost was minor (1 round-trip; T6 caught it cleanly), but for G2C/G3/G4 — gates with denser specialist-summary / specialist-contribution / mid-trial-progress payloads — the static grep is more likely to miss live consumers because consumers reach into nested dict/list payloads the way `card.evidence[-1]` does.

**Recommendation:** Add a follow-on `audit-pattern-T1-smoke-elaboration-for-extend-and-audit` to `deferred-inventory.md` proposing that G2C/G3/G4 T1 deliverables explicitly run a smoke-test pass at T1 before declaring a field DROP — i.e., grep is necessary but not sufficient; T1 should also exercise `tests/composition/`, `tests/integration/marcus/`, and `tests/integration/replay/` slices against the legacy gate to enumerate runtime field reads. This pivots the T1 audit from "static-only" to "static + smoke-elaboration."

This recommendation is filed at the end of the verdict body for the operator's discretion (filing the follow-on requires party-mode consensus per CLAUDE.md governance for new follow-ons that affect cross-story workflow).

---

## Critical Item #2: PowerShell BOM Patch Verification (Anti-Pattern A18)

```
NO_BOM
b'{\n  "$defs": {\n '
```

The first 16 bytes of `app/models/decision_cards/schema/g1.v1.schema.json` start with `{\n` directly (no `\xef\xbb\xbf` BOM prefix). Codex's T3 manual rewrite to UTF-8-without-BOM is correctly applied. The schema byte-for-byte match assertion `test_g1_json_schema_byte_for_byte_match` passes (focused G1 shape-pin reports 18 passed including this assertion). Anti-pattern A18 in `docs/dev-guide/specialist-anti-patterns.md` is observed and remediated.

---

## Critical Item #3: Scope Expansion (`app/manifest/refs.py` + `app/replay/regression.py`)

Both files were NOT in the spec's pre-enumerated audit list. Diffs verified:

### `app/manifest/refs.py`

```python
- expected_base_class: type[Any] | None = None,
+ expected_base_class: type[Any] | tuple[type[Any], ...] | None = None,
```

Plus a corresponding error-message branch that joins tuple class names with " or " when `expected_base_class` is a tuple. **Justification: clean parameter-type widening required by the 2-class-regime change in `compiler.py`** (which now passes `(DecisionCard, DecisionCardBase)` to `resolve_dotted_ref`). Without this widening, `compiler.py:328`'s tuple argument would fail isinstance/issubclass checks at the boundary. This is structurally inseparable from the 2-class-regime work that PRE-T2 review explicitly approved at `app/manifest/compiler.py:328`. **In-scope; not a defect.**

### `app/replay/regression.py`

```python
- "reject_rate": meta["reject_rate"],
+ "reject_rate": meta.get("reject_rate", 0.0),
```

**Justification: defensive backward-compat fix surfaced at T6 broad-regression run.** The legacy `DecisionCardMeta` had `reject_rate` as a required field; the new `_base.DecisionCardMeta` drops it (per contract-diff §3). Replay projection unconditionally read `meta["reject_rate"]` — under the 2-class regime, replay payloads sourced from migrated G1 cards lack this key, causing `KeyError` mid-broad-regression. The `meta.get(..., 0.0)` patch is the minimal intervention preserving replay-projection correctness for both legacy and migrated metadata shapes. The `0.0` fallback matches the field's pre-existing default in legacy meta. **In-scope; defensive correctness fix; not a defect.**

K-budget assessment: G1's K-target is 1.4× of fresh-author baseline; the 2 unexpected files add ~10 LOC total, well within budget. No K-overage to log.

---

## Critical Item #4: AMELIA-P4 Frozen-Hash Unchanged

```
UNCHANGED
Recorded: 4fe0e985d2285e3219b103424765dec009043564960ec43af1fb5710d2a1a196
```

`_frozen_hashes.py` is unchanged post-T9. The recorded G1 hash equals the spec-authored value. Current on-disk `g1.py` hash is `7aa6897b3e4989e073f2db3215e7d2aaf7e9c09dc5ea2bf2bd31f3c5793df9f0` (intentional divergence; body extended). Contract-diff §1–§8 is the AMELIA-P4 audit trail. The three sibling hashes (g2c/g3/g4) remain UNCHANGED for future extend-and-audit stories to consume.

---

## PARALLEL-DISPATCH GUARDRAILS Verification

Even though G1 is serial-dispatch, all six guardrails apply and verify:

### #1 — AMEND-7d-i AST-scan compliance — PASS

```
$ python -c "lines = [l for l in open('tests/parity/test_decision_card_g1_shape.py').read().splitlines() if 'FOUR_FILE_GLOBS' in l or 'all_four_present' in l]; print(lines or 'CLEAN')"
CLEAN
```

Plus `tests/structural/test_tw_7c_3_firing_spec_single_source.py` reports `2 passed`. The shape-pin imports `LOCKSTEP_CHECK` only (line 11) and uses it at line 44 — no rederivation of `FOUR_FILE_GLOBS` or `all_four_present` constants.

### #2 — Pattern-replication discipline — PASS

`g1.py` mirrors `g2a.py` line-by-line where applicable:

| Pattern | G2A reference | G1 implementation | Status |
|---|---|---|---|
| Inheritance from `DecisionCardBase` | line 16 | line 16 | MIRROR |
| Pydantic-v2 `UUID4` (not bare UUID) | line 23/27 | line 23/27 | MIRROR |
| `enforce_uuid4_version` validator | lines 66-69 | lines 70-73 | MIRROR |
| `enforce_tz_aware` validator | lines 78-81 | lines 75-78 | MIRROR |
| Strip-then-non-empty validator on str fields | lines 83-88 | lines 80-85, 87-92 | MIRROR |
| Field descriptions on every field | all fields | all fields | MIRROR |

### #3 — Shared-file integration ordering — PASS (informational under serial dispatch)

`app/models/decision_cards/__init__.py` flat-export includes G1Card alongside G0/G2A/G2C/G3/G4/G5/G6 (line 41 discriminated union; line 60 `__all__`). No conflict with sibling extend-and-audit work because G2C/G3/G4 are HELD until G1 closes (per spec Dispatch Hold).

### #4 — Pattern-parity ratchet — PASS

`trial_summary` + `opened_by` use strip-then-non-empty validators (mirroring G2A `plan_unit_summary`). `card_id` + `trial_id` typed as Pydantic `UUID4` (not bare UUID). All fields have `Field(..., description=...)`. Schema emits `format: uuid4` (not generic `format: uuid`).

### #5 — Class-conformance arithmetic — PASS

Codex T9 claim: 15 → 16 (+1). Validator reports: `16 parity contract file(s) conform (11 activation + 5 decision-card shape-pin)`. The +1 G1 increment is correctly attributed; the 5 decision-card shape-pins are G0+G2A+G5+G6+G1.

### #6 — Broad-regression baseline shift with per-failure attribution — PASS

Codex T9 claims `44 failed / 4187 passed / 27 skipped / 2 xfailed` from full-suite broad. Codex's dropbox §Broad-Regression Attribution lists 45 inherited failure categories (one G1-specific failure was the `reject_rate` KeyError, REMEDIATED at T6 in `regression.py`; the remaining 44 are inherited from prior-session checkout debt).

Spot-check of 3 inherited-claim tests:
- `tests/parity/test_nfr_cg_block_aggregated.py` — last commit `1f81965` (Slab 7b Stories 7b.1-7b.11 close 2026-04-29) — pre-this-session, **inherited claim verified**
- `tests/test_run_hud.py` — last commit `1f81965` (Slab 7b 2026-04-29) — pre-this-session, **inherited claim verified**
- `tests/end_to_end/test_irene_pass1_cache_hit_rate.py` — last commit `1f81965` (Slab 7b 2026-04-29) — pre-this-session, **inherited claim verified**

The reproduced parity+harness+unit slice (a subset of the full broad suite) reports `870 passed, 1 failed (NFR-CG6 inherited), 18 skipped` confirming the inherited NFR-CG6 surface persists from G6 close.

---

## Pydantic-v2 14-Idiom Checklist (per `docs/dev-guide/pydantic-v2-schema-checklist.md`)

| # | Idiom | G1 Status | Evidence |
|---|---|---|---|
| 1 | `extra="forbid"` + `validate_assignment=True` + `frozen=True` | PASS | Inherited from `DecisionCardBase.model_config`; shape-pin asserts all three at lines 58-60 |
| 2 | Tz-aware datetime | PASS | `enforce_tz_aware` validator at lines 75-78; default factory `datetime.now(UTC)` at line 40 |
| 3 | UUID4 enforcement | PASS | `enforce_uuid4_version` validator at lines 70-73 (covers card_id, trial_id); Pydantic `UUID4` typing at lines 23/27 |
| 4 | Closed-enum triple-rejection | PASS | `Literal["G1"]` + `Literal["trial_open"]` + `Literal["v1"]` + `DecisionCardVerb` Literal — Pydantic validator surface; JSON Schema emits `const`/`enum`; round-trip exercises both layers |
| 5 | Internal audit fields | N/A | G1Card has no audit-only fields |
| 6 | Free-text verbatim | PASS | `trial_summary` + `opened_by` are verbatim operator strings; strip-then-non-empty validators reject blank/whitespace-only |
| 7 | Revision monotonicity | N/A | DecisionCards are immutable (`frozen=True`); no revision field |
| 8 | Per-family shape-pin | PASS | `tests/parity/test_decision_card_g1_shape.py` is its own file; class-conformance validator recognizes it as the 5th decision-card shape-pin |
| 9 | Required-vs-optional bidirectional parity | PASS | Schema `required` array contains the 7 non-defaulted fields (decision_card_digest + meta + card_id + trial_id + trial_summary + opened_by + verb); `gate_id`/`gate_focus`/`schema_version`/`created_at`/`drafted_proposal`/`evidence`/`next_nodes` correctly excluded (defaults) |
| 10 | Digest determinism | Inherited | `decision_card_digest` validator on `DecisionCardBase` enforces lowercase sha256 hex |
| 11 | No-leak grep | N/A | G1 fields don't traffic in intake/orchestrator vocabulary |
| 12 | Warn-once dedup | N/A | No warning paths in G1 |
| 13 | State-machine bypass guard | N/A | G1 has no internal state machine |
| 14 | `additionalProperties: false` round-trip | PASS | Emitted schema lines 14, 101 — both object levels (`DecisionCardMeta` $defs + root) carry `additionalProperties: false` |

---

## Findings

### MUST-FIX

(none)

### SHOULD-FIX

(none)

### NIT / DISMISS

(none — all preconditions for COMMIT + FLIP DONE are met)

### Process-level recommendation (NOT a finding; informational)

**T1-audit-incomplete pattern for extend-and-audit stories.** As discussed in Critical Item #1, the static-grep-only T1 audit pattern declared `drafted_proposal` and `evidence` DROP at PRE-T2 cross-agent review, but T6 smoke uncovered live consumers and Codex correctly reversed the verdict. For G2C/G3/G4 (denser payloads; more nested specialist-summary reads), recommend filing a follow-on `audit-pattern-T1-smoke-elaboration-for-extend-and-audit` to `deferred-inventory.md` proposing T1 deliverables explicitly elaborate the field-access enumeration with smoke-test runs against `tests/composition/` + `tests/integration/marcus/` + `tests/integration/replay/` before declaring DROP. The operator should weigh the cost (T1 takes longer) vs. benefit (fewer T6 reversals) at G2C dispatch.

(Filed as a recommendation, NOT applied to deferred-inventory.md by this verdict — adding cross-story workflow follow-ons requires party-mode consensus per CLAUDE.md.)

---

## Patches Applied

(none)

---

## Sign-off

**T11 standard tier code review: PASS.** Recommend **COMMIT + FLIP DONE**.

The G1 extend-and-audit migration honors all five ACs, all six PARALLEL-DISPATCH GUARDRAILS, the AMELIA-P4 frozen-hash delta-AC, the AMEND-7d-i AST-scan boundary, and the Pydantic-v2 14-idiom checklist. The T6 audit-reversal on `drafted_proposal` / `evidence` is correctly reflected in both contract-diff and backward-consumer audit artifacts. The 2-class-regime substrate updates (`app/gates/resume_api.py` + `app/manifest/compiler.py` + `app/manifest/refs.py` + the test assertion) are minimal and structurally consistent. The defensive `regression.py` patch resolves one G1-specific broad-regression KeyError. The remaining 44 broad-regression failures are inherited from prior sessions (3-of-3 spot-checks confirmed via `git log`). The PowerShell BOM patch (anti-pattern A18) is correctly applied; schema is byte-for-byte deterministic.

A process-level recommendation for G2C/G3/G4 is filed in this verdict body for operator consideration.

Codex T0-T10 deliverables stand. Proceed to commit + sprint-status flip to `done`.
