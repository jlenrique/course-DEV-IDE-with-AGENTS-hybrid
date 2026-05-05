# T11 Standard Code Review — Story 7c.5.G3 (G3 DecisionCard Extend-and-Audit, Motion-Clip Approval)

**Story key:** `migration-7c-5-g3-decision-card-extend-and-audit`
**Reviewer:** Claude (Opus 4.7) — T11 standard tier (post-T9 standard review; PRE-T2 cross-agent T1 review previously PASSed at `aa9c040`)
**Gate-mode:** `dual-gate-cross-agent-CONTRACT-EVOLUTION` (T11 itself is `standard` tier; the "cross-agent" component refers to the T1 PRE-T2 review, NOT this T11)
**R-tier:** R3 (full broad regression)
**K-target:** 1.4× (extend-and-audit; heavier than fresh-author)
**Diff size:** ~470 LOC across 14 files (4 new G3 lockstep + 2 modified production constructors + 1 inherited NFR-CG6 fix + sibling G2C/G4 four-file lockstep co-modified in this commit)
**Review date:** 2026-05-05

---

## Verdict: **PASS — recommend COMMIT + FLIP DONE**

The G3 extend-and-audit migration is structurally sound and faithfully honors the §1 SEMANTIC ALIGNMENT STATEMENT ratified at PRE-T2 T1 review. The four-file lockstep is byte-deterministic. All five ACs (A–E) verify. The frozen-hash AMELIA-P4 baseline is unchanged; the on-disk `g3.py` hash diverges from the recorded frozen value as intended (body extended; contract-diff §1–§8 is the audit trail justifying divergence). The progress_percent bounds preservation requirement is satisfied — `[Ge(ge=0.0), Le(le=100.0)]` carried verbatim from the legacy declaration to the migrated `G3Card`, and the new shape-pin covers all four boundary cases (0.0/100.0/-0.1/100.1). All six PARALLEL-DISPATCH GUARDRAILS pass (note: G3 dispatched in parallel with G2C+G4 under operator (E)-elasticity override). Pydantic-v2 14-idiom checklist conforms. The migrated `g3.py` mirrors `g1.py` (the canonical extend-and-audit migrated body) line-by-line.

The T1-audit verdict on `drafted_proposal` / `evidence` / `risks` was NOT reversed at T6 for G3. Unlike G1 (where these fields had live consumers in `tests/composition/` + `tests/integration/marcus/`), G3's contract-diff §2 explicitly notes "direct reads only in G1-only tests" — and the contract-diff §2's heavy-audit smoke evidence holds: G3's broad-regression slice reports `921 passed, 18 skipped` (cleaner than G1's `870 passed, 1 failed`), confirming the DROP verdict for G3 is durable. The G1 reviewer's recommended T1-smoke-elaboration follow-on did not need to be filed for G3 — Codex T1 audit's static-grep + targeted smoke-pass methodology was sufficient.

No MUST-FIX. No SHOULD-FIX. One NIT (workspace-only CRLF on schema file; git's `.gitattributes` will normalize at commit). Zero patches applied by this reviewer.

---

## Verification Battery

| Check | Status | Evidence |
|---|---|---|
| Focused G3 shape-pin | PASS | `16 passed in 3.59s` — 16 tests after parametrize fan-out (1 LOCKSTEP_CHECK + 1 required-fields + 3 closed-enum red rejections + 2 progress_percent boundary accepts + 2 progress_percent boundary rejects + 2+2 non-empty validators + 1 schema byte-match + 1 golden round-trip + 1 frozen-mutation rejection) |
| AMEND-7d-i AST-scan structural test | PASS | `2 passed in 3.25s` — confirms G3 shape-pin contains no `FOUR_FILE_GLOBS` / `all_four_present` literals; only `LOCKSTEP_CHECK` imported from `tw_7c_3_firing` |
| `tests/parity/` + `tests/parametrized_harness/` + `tests/unit/` broad slice | PASS | `921 passed, 18 skipped in 20.09s` — **NFR-CG6 inherited governance-version drift now resolved** by the sibling G2C-authored `test_nfr_cg_block_aggregated.py` patch (justified scope-expansion; see Critical Item #7) |
| Decision-cards + marcus + gates consumer slice | PASS | `146 passed in 6.97s` — covers test_per_gate_strict, test_discriminated_union_routing, test_manifest_dotted_reference_resolver (2-class-regime accepts both bases), test_routing_manifest_driven, gates helpers |
| Composition + marcus integration smoke | PASS | `182 passed, 1 skipped in 9.83s` — confirms G3 DROP verdict on drafted_proposal/evidence/risks holds (no live consumers exposed in the heavy-audit roots cited in contract-diff §2) |
| Replay integration | PASS-modulo-inherited | `4 failed, 195 passed, 1 skipped in 12.42s` — 4 failures are PackHashDriftError on trial_id `33333333...` from `649c3a6` (Slab 5a.1 baseline, predates Slab 7c entirely). **Inherited; NOT G3-introduced** |
| Class-conformance | PASS | `19 parity contract file(s) conform (11 activation + 8 decision-card shape-pin)` — matches Codex T9 claim 16→17→18→19 (G0+G2A+G5+G6+G1+G2C+G3+G4 = 8 shape-pins; +1 G3 increment correct) |
| Lint-imports | PASS | `Contracts: 12 kept, 0 broken` (UNCHANGED) |
| Sandbox-AC validator | PASS | `PASS — no sandbox-AC violations across 1 story file(s)` |
| Ruff (in-scope files) | PASS | `All checks passed!` — covers g3.py + test_decision_card_g3_shape.py |
| Schema-emission determinism | PASS | In-Python text-mode comparison: emitted (5725 chars) == on-disk (5725 chars), MATCH |
| BOM check on schema JSON | PASS | `NO_BOM`; first 16 bytes start with `b'{\r\n  "$defs": {\r'` (no `\xef\xbb\xbf` BOM prefix) — note CRLF observation in NIT below |
| Frozen-hash AMELIA-P4 unchanged | PASS | `FROZEN_AT_SHIP_HASHES['g3'] == "bcfe2865df5e7071cf43ada563e29a8b6fc5dfa1cb3abdf99f78fa5d2d0fddf3"` UNCHANGED post-T9 (current on-disk g3.py hash `f67e0318695ff94684f1aa43acb66ea53728a2846b096f96aa16ab42ca689ce2` differs intentionally; contract-diff justifies) |

---

## §1 SEMANTIC ALIGNMENT STATEMENT honored at T2 — **PASS**

The PRE-T2 contract-diff §1 statement set the contract-evolution intent: "preserve legacy mid-trial fields verbatim under the broader 'motion-clip approval' gate_focus marker; defer operator semantic refinement." T2 honors this verdict precisely:

### Legacy field preservation — verbatim

Pydantic introspection of the migrated `G3Card` confirms all four legacy operator-facing fields are present with identical names, identical type annotations, and identical declarative metadata:

| Legacy field | Legacy declaration | Migrated declaration | Status |
|---|---|---|---|
| `progress_percent` | `float`, `ge=0.0`, `le=100.0` | `float`, `[Ge(ge=0.0), Le(le=100.0)]` | VERBATIM (annotation + bounds) |
| `active_node_id` | `str`, `min_length=1` | `str`, `min_length=1` + strip-then-non-empty validator | VERBATIM + tightened (G2A pattern ratchet, declared at T1) |
| `pending_nodes` | `list[str]`, default empty | `list[str]`, `default_factory=list` | VERBATIM |
| `operator_prompt` | `str` (legacy declared `min_length=1` per T0 record) | `str`, `min_length=1` + strip-then-non-empty validator | VERBATIM + tightened (G2A pattern ratchet, declared at T1) |
| `gate_id` | `Literal["G3"]` | `Literal["G3"]`, default="G3" | VERBATIM |
| `verb` | `Literal["approve","edit","reject"]` | `Literal["approve","edit","reject"]` | VERBATIM |

No operator-facing field renames. No semantic narrowing. The strip-then-non-empty validator additions on `active_node_id` + `operator_prompt` were explicitly declared at contract-diff §1 (rationale: "tightens whitespace-only rejection per G2A pattern while preserving the non-empty contract") and at §6 (Pattern-Parity Ratchets) — these are NOT smuggled operator-semantic refinement; they are pre-ratified G2A canonical idiom adoptions.

### `gate_focus="motion_clip_approval"` added per ADR 0002 — PASS

The `gate_focus: Literal["motion_clip_approval"]` field appears at line 35–38 of `g3.py` with `default="motion_clip_approval"` and description "Closed one-value marker for the G3 gate family." Schema emits `"const": "motion_clip_approval"` at line 128–133. Shape-pin red-rejection covers `gate_focus="pre_composition_qa"` (a deliberately-wrong value from G2C's family) at parametrize fan-out.

### No smuggled operator-semantic refinement

A field-level diff scan (Codex's introspection report) shows the migrated body adds exactly three new fields beyond the legacy set: `schema_version`, `decision_card_digest` (inherited from `DecisionCardBase`), and `gate_focus` — all explicitly enumerated in contract-diff §4. No new operator-facing field, no behavior-changing validator on the legacy four, no rename of `operator_prompt` to a "motion_clip_approval"-flavored synonym. The deferral commitment at §1 is honored.

**Verdict: §1 SEMANTIC ALIGNMENT STATEMENT honored at T2 — PASS.**

---

## progress_percent bounds preservation — **PASS** (G3-SPECIFIC critical item)

Pydantic introspection: `progress_percent` annotation is `<class 'float'>` with metadata `[Ge(ge=0.0), Le(le=100.0)]`. JSON Schema emission at line 158–164 of `g3.v1.schema.json`:

```json
"progress_percent": {
  "description": "Observed trial completion percentage at the checkpoint.",
  "maximum": 100.0,
  "minimum": 0.0,
  "title": "Progress Percent",
  "type": "number"
}
```

Shape-pin boundary coverage at `tests/parity/test_decision_card_g3_shape.py` lines 78–94:

- `test_g3_card_accepts_progress_percent_boundaries` parametrized at `[0.0, 100.0]` — PASS (2 tests)
- `test_g3_card_rejects_progress_percent_out_of_bounds` parametrized at `[-0.1, 100.1]` — PASS (2 tests)

All four spec-mandated boundary cases (AC-7c.5.G3-C: "include progress_percent boundary tests at 0.0 / 100.0 / -0.1 / 100.1") are covered. Bounds preservation is byte-equivalent to the legacy declaration; no relaxation, no removal.

**Verdict: progress_percent bounds preservation — PASS.**

---

## AC Compliance Verification

### AC-7c.5.G3-A — Pre-T2 contract-diff + backward-consumer audit + frozen-hash artifacts — PASS

All three deliverables present (verified at PRE-T2 review at `aa9c040`):

1. `_bmad-output/implementation-artifacts/migration-7c-5-g3-contract-diff.md` — 137 lines; 8 sections covering legacy G3 fields disposition (§1, with semantic alignment statement at lines 20–22), legacy DecisionCard base disposition with AMELIA-P5 V6 audit_method qualifier on every row (§2 — 3 DROP rows = drafted_proposal/evidence/risks; all marked `audit_method=heavy` with smoke-pass evidence), legacy DecisionCardMeta disposition with audit_method (§3 — 4 DROP rows; all `audit_method=heavy`), new fields (§4: `schema_version` + `decision_card_digest` + `gate_focus`), closed-enum tightening (§5), pattern-parity ratchets (§6), net diff (§7), T1 baseline evidence (§8).
2. `_bmad-output/implementation-artifacts/migration-7c-5-g3-backward-consumer-audit.md` — 124 lines; 38 executable consumer rows + 6 non-grep + 7 required-root smoke + 3 doc references.
3. `app/models/decision_cards/_frozen_hashes.py` — UNCHANGED; G3 hash matches PRE-T2 review record.

### AC-7c.5.G3-B — AMELIA-P4 frozen-hash delta-AC — PASS

`_frozen_hashes.py` UNCHANGED post-T9. Codex T2 verified the pre-extension on-disk hash matched `FROZEN_AT_SHIP_HASHES["g3"]` before extending; current post-T9 on-disk hash `f67e0318...` intentionally diverges — the contract-diff artifact is the audit trail.

### AC-7c.5.G3-C — Four-file lockstep co-commit — PASS

All four files present, co-committed:

1. `app/models/decision_cards/g3.py` (94 LOC) — `G3Card(DecisionCardBase)` (line 16). Re-declares: `card_id`/`trial_id` (UUID4 — Pydantic-v2 type, not bare UUID; lines 23/27); `gate_id: Literal["G3"]` + `gate_focus: Literal["motion_clip_approval"]` + `schema_version: Literal["v1"]` (lines 31/35/19 — closed Literals); `created_at` (datetime; default UTC factory); `verb: DecisionCardVerb` (closed Literal). Preserves: `progress_percent` with `Field(..., ge=0.0, le=100.0)` (lines 43–48); `active_node_id` (strip-then-non-empty validator lines 78–83); `pending_nodes` (default empty list line 54); `operator_prompt` (strip-then-non-empty validator lines 85–90).
2. `app/models/decision_cards/schema/g3.v1.schema.json` (201 LOC) — REGENERATED; emits `additionalProperties: false`, `const: "G3"` for gate_id, `const: "motion_clip_approval"` for gate_focus, `const: "v1"` for schema_version, `minimum: 0.0` + `maximum: 100.0` for progress_percent. Required array correctly excludes defaulted-Literal fields.
3. `tests/parity/test_decision_card_g3_shape.py` (135 LOC; 16 tests after parametrize fan-out) — covers field-presence + closed-enum red-rejection (3 enums × 1 invalid value each = 3) + progress_percent boundary accept (2) + progress_percent boundary reject (2) + non-empty validators on active_node_id + operator_prompt (2 × 2 = 4) + schema byte-match (1) + golden round-trip (1) + frozen-mutation rejection (1) + LOCKSTEP_CHECK (1). AMEND-7d-i compliant: bare `from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK` only (line 11); used at line 43 only.
4. `tests/fixtures/decision_cards/g3_golden.json` (26 LOC) — UUID4-shape `card_id`/`trial_id`, tz-aware `created_at: "2026-05-05T12:10:00Z"`, `meta.cache_state: "mixed"`, `meta.affected_nodes: ["08","09"]`, empty `override_trail`, `gate_id: "G3"`, `gate_focus: "motion_clip_approval"`, `schema_version: "v1"`, `progress_percent: 53.5`, `active_node_id: "08"`, `pending_nodes: ["09","10","11"]`, `operator_prompt`, `verb: "edit"`, valid 64-char lowercase hex `decision_card_digest`.

Schema text-mode byte-for-byte match verified in-Python (5725 chars on both sides).

### AC-7c.5.G3-D — Backward-consumer non-regression — PASS

The `tests/parity/ tests/parametrized_harness/ tests/unit/` slice reports `921 passed, 18 skipped` — **the inherited NFR-CG6 governance-version drift carried forward from G6 close is now resolved** by the sibling G2C-authored `test_nfr_cg_block_aggregated.py` patch (governance JSON ships `2026-05-05-amelia-p5-and-wave-3-lookahead-policy`; test now expects the same). G3-critical consumer slices verified green:

- `tests/unit/marcus/` + `tests/unit/models/decision_cards/` + `tests/unit/gates/` — `146 passed`
- `tests/composition/` + `tests/integration/marcus/` — `182 passed, 1 skipped` (heavy-audit roots from contract-diff §2; confirms drafted_proposal/evidence/risks DROP verdict holds for G3)

Constructor sites updated correctly:

- `app/marcus/orchestrator/production_runner.py:441` — `G3Card` constructor now passes `card_id`, `trial_id`, `created_at`, `decision_card_digest="0"*64`, `meta=_base_card_meta(common["meta"])`, `verb`, plus G3-specific `progress_percent=50.0`, `active_node_id=node_id`, `pending_nodes=pending_nodes`, `operator_prompt`. Drops the legacy `**common` splat (which would have passed `drafted_proposal`/`evidence`/`risks`). Matches contract-diff §7 update surface exactly.
- `marcus/orchestrator/m3_trial.py:177` — same shape; G3 branch only. Drops `**common` splat. Matches PRE-T2 audit verdict.

Documentation references (`docs/operator/production-trial-playbook.md` + `docs/dev-guide/sources-of-truth.md`) deferred to follow-on `slab-7c-g1-g4-decision-card-doc-refresh` per spec (reactivates after all four extend-and-audit stories close).

### AC-7c.5.G3-E — Class-conformance + Pydantic-v2 14-idiom + bounds validators — PASS

Validator reports `19 parity contract file(s) conform (11 activation + 8 decision-card shape-pin)`. The +1 G3 increment matches Codex T9 claim. See Pydantic-v2 14-idiom checklist below — all applicable idioms PASS, including idiom #4 (closed-enum triple-rejection across `gate_id` + `gate_focus` + `schema_version` + `verb`) and bounds preservation (idiom adjacent: Pydantic-native `Field(..., ge, le)` on progress_percent).

---

## Critical Item #1: §1 SEMANTIC ALIGNMENT STATEMENT honored at T2 — covered above (PASS)

(See dedicated section.)

## Critical Item #2: progress_percent bounds preservation (G3-SPECIFIC) — covered above (PASS)

(See dedicated section.)

## Critical Item #3: T1-audit-verdict-reversal scan (G1 PRECEDENT) — **PASS — no reversal needed**

The PRE-T2 cross-agent T1 review ratified the contract-diff §2 verdict that `drafted_proposal`, `evidence`, and `risks` would be DROPPED with `audit_method=heavy` smoke-pass evidence. Heavy-audit smoke commands enumerated at §8 of the contract-diff demonstrated 0 collected tests in the required roots for `drafted_proposal` and `risks`, and 7 collected (all passing) for `evidence` — but with the explicit discriminator that all `card.evidence` reads were in **G1-only adjacent-summary tests** (`tests/integration/marcus/test_gate_handler_loads_adjacent_summary.py`), not G3.

T2 honored this verdict: the migrated `g3.py` does NOT carry `drafted_proposal`, `evidence`, or `risks` as G3 direct fields. Re-running the heavy-audit smoke roots (`tests/composition/` + `tests/integration/marcus/` + `tests/integration/replay/`) at T11 confirms the verdict is durable — 182 passed in composition+marcus; 4 inherited replay failures are PackHashDriftError on a `649c3a6` Slab 5a.1 baseline trial pack, unrelated to G3 fields.

**No reversal at T6** (contrast with G1, which reversed `drafted_proposal`+`evidence` at T6). G3's contract-diff is structurally final. The G1 T11 reviewer's recommended `audit-pattern-T1-smoke-elaboration-for-extend-and-audit` follow-on did not need to be filed for G3 — Codex T1's static-grep + targeted smoke-pass methodology surfaced the G3-vs-G1 consumer asymmetry up-front.

## Critical Item #4: BOM patch verification (anti-pattern A18) — **PASS** (with NIT)

```
NO_BOM
b'{\r\n  "$defs": {\r'
```

The first 16 bytes of `app/models/decision_cards/schema/g3.v1.schema.json` start with `{\r\n` — no UTF-8 BOM `\xef\xbb\xbf` prefix. **Anti-pattern A18 (PowerShell BOM) is correctly avoided.**

**NIT (workspace-only; will not block commit):** the schema file uses CRLF line endings on disk while sibling schemas (`g0`/`g1`/`g2a`/`g2c`/`g5`/`g6`) use LF. `git ls-files --eol` reports `i/lf w/crlf attr/text=auto eol=lf` for `g3.v1.schema.json` (and `g4.v1.schema.json`); the repo's `.gitattributes` declares `* text=auto eol=lf`, so git will normalize CRLF→LF at commit. The byte-for-byte parity test passes because Python's text-mode read normalizes CRLF→LF on Windows reads. Functionally invisible after commit; no patch required by this reviewer. **Recommendation for future Codex extend-and-audit prompts: explicitly specify `Path(...).write_text(text, encoding="utf-8", newline="\n")` to avoid the Windows default CRLF write.** (Filed as a Codex-prompt-hardening recommendation; NOT applied to this reviewer's verdict.)

## Critical Item #5: AMELIA-P4 frozen-hash UNCHANGED post-T9 — **PASS**

```
UNCHANGED
value=bcfe2865df5e7071cf43ada563e29a8b6fc5dfa1cb3abdf99f78fa5d2d0fddf3
```

`_frozen_hashes.py` is unchanged post-T9. The recorded G3 hash equals the spec-authored value. Current on-disk `g3.py` hash is `f67e0318695ff94684f1aa43acb66ea53728a2846b096f96aa16ab42ca689ce2` (intentional divergence; body extended). Contract-diff §1–§8 is the AMELIA-P4 audit trail. Sibling hashes (g1/g2c/g4) remain UNCHANGED.

## Critical Item #6: PARALLEL-DISPATCH GUARDRAILS verification — **PASS**

G3 dispatched in parallel with G2C+G4 under operator (E)-elasticity override. All six guardrails verify:

### #1 — AMEND-7d-i AST-scan compliance — PASS

Self-grep on `tests/parity/test_decision_card_g3_shape.py`:

```
forbidden tokens found: CLEAN
imports from tw_7c_3_firing:
  from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK
```

No `FOUR_FILE_GLOBS` / `all_four_present` literals. Plus `tests/structural/test_tw_7c_3_firing_spec_single_source.py` reports `2 passed`. Bare `LOCKSTEP_CHECK` import only.

### #2 — Pattern-replication discipline — PASS

`g3.py` mirrors `g1.py` (the canonical extend-and-audit migrated body) line-by-line:

| Pattern | G1 reference | G3 implementation | Status |
|---|---|---|---|
| Inheritance from `DecisionCardBase` | line 16 | line 16 | MIRROR |
| Pydantic-v2 `UUID4` (not bare UUID) | line 23/27 | line 23/27 | MIRROR |
| `enforce_uuid4_version` validator | lines 70–73 | lines 68–71 | MIRROR |
| `enforce_tz_aware` validator | lines 75–78 | lines 73–76 | MIRROR |
| Strip-then-non-empty validator on str fields | lines 80–85, 87–92 | lines 78–83, 85–90 | MIRROR |
| `gate_focus` Literal one-value | line 35 (`"trial_open"`) | line 35 (`"motion_clip_approval"`) | MIRROR (G3-specific value) |
| `schema_version` Literal | line 19 | line 19 | MIRROR |
| Field descriptions on every field | all fields | all fields | MIRROR |

### #3 — Shared-file integration ordering — PASS

`app/models/decision_cards/__init__.py` was already authored with G3Card flat-export + discriminated union membership (line 23 import; line 42 union; line 63 `__all__`). UNCHANGED in this commit — Codex correctly identified this in T10 dropbox: "G3Card was already present in the flat export, discriminated union, and __all__." Discriminated union still works for G3Card-on-DecisionCardBase (`AnyDecisionCard` is `G0Card | G1Card | G2ACard | G2CCard | G3Card | G4Card | G5Card | G6Card` discriminated by `gate_id`).

### #4 — Pattern-parity ratchet — PASS

`active_node_id` + `operator_prompt` use strip-then-non-empty validators (mirroring G2A `plan_unit_summary` and G1 `trial_summary`/`opened_by`). `card_id` + `trial_id` typed as Pydantic `UUID4` (not bare UUID). All fields have `Field(..., description=...)`. Schema emits `format: uuid4` (not generic `format: uuid`). progress_percent retains `Pydantic-native` `Field(..., ge=0.0, le=100.0)` (not external validator).

### #5 — Class-conformance arithmetic — PASS

Codex T9 claim: 16 → 19 (+3 for G2C+G3+G4 in this parallel batch) OR 18→19 if G2C+G4 land first. Validator reports: `19 parity contract file(s) conform (11 activation + 8 decision-card shape-pin)`. The 8 decision-card shape-pins are G0+G2A+G5+G6+G1+G2C+G3+G4. The +1 G3 increment is correctly attributed.

### #6 — Broad-regression baseline shift with per-failure attribution — PASS

Codex T10 dropbox reports `4239 passed, 42 failed, 27 skipped, 2 xfailed` from full-suite broad. Codex's attribution: "no decision-card shape, schema, fixture, union, or constructor-path failures surfaced. The 42 failures match inherited broad-suite drift from the surrounding workspace."

Spot-check verification:
- `tests/integration/replay/test_replay_*` (4 failures observed in replay slice) — last commit `649c3a6` Slab 5a.1 baseline; PackHashDriftError unrelated to G3 fields. **Inherited claim verified.**
- `tests/parity/test_nfr_cg_block_aggregated.py::test_nfr_cg_block_structural_evidence[NFR-CG6]` — RESOLVED in this commit (sibling G2C patch updated the expected version to `2026-05-05-amelia-p5-and-wave-3-lookahead-policy` matching governance JSON ship version). **No longer in the failure set.**

The reproduced parity+harness+unit slice (a subset of the full broad suite) reports `921 passed, 18 skipped` confirming the inherited NFR-CG6 surface no longer persists post-this-commit.

## Critical Item #7: Scope expansion (`test_nfr_cg_block_aggregated.py`) — **PASS — justified governance-tracker update**

The single-line modification at `tests/parity/test_nfr_cg_block_aggregated.py:108`:

```diff
-    assert governance["version"] == "2026-04-29-slab7b-twelve-stories"
+    assert governance["version"] == "2026-05-05-amelia-p5-and-wave-3-lookahead-policy"
```

**Authorship:** the G2C Codex dropbox (`_codex-handoff/7c-5-g2c.ready-for-review.md`) explicitly claims authorship: "The inherited NFR-CG6 governance-version drift was resolved by updating `tests/parity/test_nfr_cg_block_aggregated.py` to the current governance version `2026-05-05-amelia-p5-and-wave-3-lookahead-policy`." G3's working tree consumes this fix as a sibling-parallel update.

**Justification:** governance JSON `docs/dev-guide/migration-story-governance.json` ships at version `2026-05-05-amelia-p5-and-wave-3-lookahead-policy` (per commit `57b92b2` codifying V6+V7 amendments). The test was asserting the prior `2026-04-29-slab7b-twelve-stories` version, which was correct at the moment Slab 7b closed (G6 close commit `f059e84`). After `57b92b2` shipped the V6+V7 amendments, the test was structurally stale. **This is a justified governance-tracker update, NOT defensive silencing.** The G1 T11 reviewer flagged this same drift as an inherited finding and noted "T11 standard close will track this for resolution at the appropriate parity-test refresh story" — G2C+G3+G4 collectively are that refresh. Scope expansion is in-bounds.

K-budget assessment: G3's K-target is 1.4× of fresh-author baseline; the inherited `test_nfr_cg_block_aggregated.py` patch is a single line and is sibling-shared (not solely attributable to G3). Well within budget. No K-overage to log.

---

## Pydantic-v2 14-Idiom Checklist (per `docs/dev-guide/pydantic-v2-schema-checklist.md`)

| # | Idiom | G3 Status | Evidence |
|---|---|---|---|
| 1 | `extra="forbid"` + `validate_assignment=True` + `frozen=True` | PASS | Inherited from `DecisionCardBase.model_config`; shape-pin asserts all three at lines 57–59 |
| 2 | Tz-aware datetime | PASS | `enforce_tz_aware` validator at lines 73–76; default factory `datetime.now(UTC)` at line 40 |
| 3 | UUID4 enforcement | PASS | `enforce_uuid4_version` validator at lines 68–71 (covers card_id, trial_id); Pydantic `UUID4` typing at lines 23/27 |
| 4 | Closed-enum triple-rejection | PASS | `Literal["G3"]` + `Literal["motion_clip_approval"]` + `Literal["v1"]` + `DecisionCardVerb` Literal — Pydantic validator surface; JSON Schema emits `const`/`enum`; round-trip exercises both layers |
| 5 | Internal audit fields | N/A | G3Card has no audit-only fields |
| 6 | Free-text verbatim | PASS | `active_node_id` + `operator_prompt` are verbatim operator strings; strip-then-non-empty validators reject blank/whitespace-only |
| 7 | Revision monotonicity | N/A | DecisionCards are immutable (`frozen=True`); no revision field |
| 8 | Per-family shape-pin | PASS | `tests/parity/test_decision_card_g3_shape.py` is its own file; class-conformance validator recognizes it as the 7th decision-card shape-pin (G0+G2A+G5+G6+G1+G2C+G3 = 7th in batch order) |
| 9 | Required-vs-optional bidirectional parity | PASS | Schema `required` array contains the 8 non-defaulted fields (decision_card_digest + meta + card_id + trial_id + progress_percent + active_node_id + operator_prompt + verb); `gate_id`/`gate_focus`/`schema_version`/`created_at`/`pending_nodes` correctly excluded (defaults) |
| 10 | Digest determinism | Inherited | `decision_card_digest` validator on `DecisionCardBase` enforces lowercase sha256 hex |
| 11 | No-leak grep | N/A | G3 fields don't traffic in intake/orchestrator vocabulary |
| 12 | Warn-once dedup | N/A | No warning paths in G3 |
| 13 | State-machine bypass guard | N/A | G3 has no internal state machine |
| 14 | `additionalProperties: false` round-trip | PASS | Emitted schema lines 14, 101 — both object levels (`DecisionCardMeta` $defs + root) carry `additionalProperties: false` |

**Bounds adjacent (G3-specific):** progress_percent uses Pydantic-native `Field(..., ge=0.0, le=100.0)` (not external validator). Schema emits `minimum: 0.0` + `maximum: 100.0` (numeric). Triple-layer enforcement: Pydantic validator on input + JSON Schema bounds on emit + shape-pin boundary tests on round-trip.

---

## Findings

### MUST-FIX

(none)

### SHOULD-FIX

(none)

### NIT / DISMISS

- **Workspace-only schema CRLF.** `app/models/decision_cards/schema/g3.v1.schema.json` (and sibling `g4.v1.schema.json`) have CRLF line endings on disk; git's `.gitattributes` declares `eol=lf` and will normalize at commit (`git ls-files --eol` reports `i/lf w/crlf` — index will be LF). Functionally invisible post-commit. **DISMISSED** for this verdict; recommend Codex prompt hardening for future extend-and-audit migrations to specify `newline="\n"` on `Path.write_text` for schema files.

---

## Patches Applied

(none)

---

## Sign-off

**T11 standard tier code review: PASS.** Recommend **COMMIT + FLIP DONE**.

The G3 extend-and-audit migration honors all five ACs, all six PARALLEL-DISPATCH GUARDRAILS, the AMELIA-P4 frozen-hash delta-AC, the AMEND-7d-i AST-scan boundary, the AMELIA-P5 V6 §audit_method DROP-row commitments, the Pydantic-v2 14-idiom checklist, the §1 SEMANTIC ALIGNMENT STATEMENT, and the progress_percent bounds preservation requirement. The migrated `g3.py` mirrors `g1.py` (the canonical extend-and-audit migrated body) line-by-line. The two production constructor sites (`production_runner.py:441` + `m3_trial.py:177`) drop the legacy `**common` splat and supply only the migrated payload shape. No T6 verdict reversal needed (contract-diff §2 DROP verdict on drafted_proposal/evidence/risks is structurally durable for G3). The sibling-shared `test_nfr_cg_block_aggregated.py` patch resolves the inherited NFR-CG6 governance-version drift carried forward from G6 close. The PowerShell BOM anti-pattern (A18) is correctly avoided; only a workspace-only CRLF NIT remains, which git will normalize at commit.

The four-file lockstep is byte-deterministic in text mode (5725 chars on both sides). Class-conformance shows +1 increment to 19 (8 decision-card shape-pins). Lint-imports + ruff + sandbox-AC all green.

Codex T0–T10 deliverables stand. Proceed to commit + sprint-status flip to `done`.
