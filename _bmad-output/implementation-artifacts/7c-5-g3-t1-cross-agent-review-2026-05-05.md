# PRE-T2 Cross-Agent T1 Review — Story 7c.5.G3 (G3 DecisionCard Extend-and-Audit, Motion-Clip Approval)

**Story key:** `migration-7c-5-g3-decision-card-extend-and-audit`
**Reviewer:** Claude (Opus 4.7) — cross-agent T1 review (Winston W3 amendment + V6 AMELIA-P5 amendment binding HALT)
**Review date:** 2026-05-05
**Stage:** PRE-T2 — Codex HALTED at end of T1 awaiting verdict
**Parallel-with:** Sibling story 7c.5.G2C reviewed concurrently by separate T1 review subagent (operator (E)-elasticity override of serial-dispatch rule).

---

## Verdict: **PASS — Codex MAY proceed to T2**

All three T1 deliverables are present, complete, structurally sound, and AMELIA-P5 V6-conformant. The G3-specific §1 SEMANTIC ALIGNMENT STATEMENT is explicit, well-placed, and precisely matches the spec's recommended verdict (preserve legacy mid-trial fields verbatim; add `gate_focus="motion_clip_approval"` as the post-Slab-7c family marker; defer operator semantic refinement). All seven DROP rows across §2 + §3 carry `audit_method=heavy` with smoke-pass evidence. No MUST-FIX. No SHOULD-FIX. Codex is unblocked.

---

## Operational baseline note (parallel-dispatch reality)

Per Codex T1-ready notice, the local checkout is at `HEAD=57b92b2` and does not contain a migrated G2C body, G2C shape-pin, or G2C close review artifact, because G2C is being reviewed concurrently. Codex correctly recorded the class-conformance baseline as **16** (11 activation + 5 decision-card shape-pin) rather than the prompt's expected "likely 17". Acknowledged: this is operational reality under operator (E)-elasticity parallel dispatch, **not a defect**. T1 baseline integrity preserved — class-conformance validator still runs PASS at the observed count.

Parallel-with-G2C coordination contract: this verdict is independent of G2C's verdict. Both stories share the `_frozen_hashes.py` substrate established at G1 close (`6a81e66`) and the G1-widened 2-class-regime validators (compiler.py, refs.py, dotted-ref test, resume_api.py). G3 consumes — does not re-edit.

---

## Verification battery

| Check | Status | Evidence |
|---|---|---|
| On-disk `app/models/decision_cards/g3.py` SHA256 | PASS | `bcfe2865df5e7071cf43ada563e29a8b6fc5dfa1cb3abdf99f78fa5d2d0fddf3` (independently re-computed) |
| `FROZEN_AT_SHIP_HASHES["g3"]` recorded | PASS | `bcfe2865df5e7071cf43ada563e29a8b6fc5dfa1cb3abdf99f78fa5d2d0fddf3` (matches byte-for-byte) |
| AMELIA-P4 frozen-hash delta-AC pre-check | PASS | Both equal — pre-check satisfied before T2 |
| Sandbox-AC validator on story spec | PASS | `PASS - no sandbox-AC violations across 1 story file(s)` |
| Class-conformance validator | PASS | `PASS: 16 parity contract file(s) conform (11 activation + 5 decision-card shape-pin)` |
| Contract-diff artifact at `migration-7c-5-g3-contract-diff.md` | PASS | 137 lines; 8 sections (T0 + 7 spec-required) |
| Backward-consumer audit at `migration-7c-5-g3-backward-consumer-audit.md` | PASS | 124 lines; 38 executable + 6 non-grep + 7 required-root smoke + 3 doc references |
| T1 READY notice at `_codex-handoff/7c-5-g3.t1-ready.md` | PASS | All deliverables enumerated; AMELIA-P5 summary + T2 update surface listed |
| Legacy `app/models/decision_cards/g3.py` UNMODIFIED at T1 | PASS | Frozen hash equals on-disk hash; Codex correctly defers body changes to T2 |

---

## CRITICAL ITEM #1: AMELIA-P5 V6 §audit_method compliance — **PASS**

Contract-diff §2 schema is exactly `| field | disposition | audit_method | rationale |` per V6 binding=hard. Every DROP row in §2 + §3 carries `audit_method=heavy` with smoke-pass evidence:

**§2 DROP rows (3):**
- `drafted_proposal` → `audit_method=heavy`. Smoke: `pytest ... -k drafted_proposal --co -q` collected 0 tests in required roots; targeted `card.drafted_proposal` reads exist only in G1-only tests (executed: 4 passed). No required-root G3 direct read exists.
- `evidence` → `audit_method=heavy`. Smoke: collect found 7 tests; execution passed 7. Direct `card.evidence` reads exist only in G1-only adjacent-summary tests (executed: 3 passed).
- `risks` → `audit_method=heavy`. Smoke: 0 tests collected; targeted grep found no `card.risks` or `getattr(..., "risks")` access in required roots.

**§3 DROP rows (4):**
- `reject_rate`, `party_mode_contributions`, `consolidated_at`, `sanctum_warnings` — all `audit_method=heavy`. Smoke per field: 0 tests collected in required roots; targeted grep found no required-root reads. Codex correctly distinguishes that `tests/integration/gates/` reads of `party_mode_contributions` + `consolidated_at` are for `G-PARTY` cards, **not G3** — this is the precise discriminator that V6 demands.

**Light rows correctly bounded:** every `light` audit_method row corresponds to `preserve-via-re-declaration` / `preserve-via-base` / `inherit` / `new-field-add`. Zero light rows on DROP dispositions. V6 audit_method legend respected.

---

## CRITICAL ITEM #2: AMELIA-P4 frozen-hash verification — **PASS**

Independently re-computed both values via the verification commands specified in the prompt:

```
g3 (on-disk)  bcfe2865df5e7071cf43ada563e29a8b6fc5dfa1cb3abdf99f78fa5d2d0fddf3
recorded      bcfe2865df5e7071cf43ada563e29a8b6fc5dfa1cb3abdf99f78fa5d2d0fddf3
```

Match byte-for-byte. AMELIA-P4 delta-AC pre-check satisfied. Codex correctly defers body changes to T2 (legacy `g3.py` UNMODIFIED at T1).

---

## CRITICAL ITEM #3: Contract-diff completeness + G3-SPECIFIC §1 SEMANTIC ALIGNMENT STATEMENT — **PASS**

### §1 SEMANTIC ALIGNMENT STATEMENT verdict: **PASS**

The §1 statement appears as a **dedicated, named, prominent header subsection** at lines 20-22 of the contract-diff:

> ADR 0002 designates G3 as the "motion-clip approval gate", while the legacy `G3Card` field names describe a mid-trial in-flight operator review: `progress_percent`, `active_node_id`, `pending_nodes`, and `operator_prompt`. T1 verdict: preserve these legacy fields verbatim for backward consumers and add `gate_focus: Literal["motion_clip_approval"]` as the post-Slab-7c family marker. This story does not rename operator-facing fields or narrow their meaning. Any operator semantic refinement between "mid-trial review" and "motion-clip approval" should be deferred to a later story after the family contract is migrated.

This statement:
1. **Explicitly names the divergence** (ADR 0002 "motion-clip approval" vs legacy "mid-trial in-flight review").
2. **States an explicit verdict** (preserve verbatim + add gate_focus marker).
3. **Bounds the migration scope** (no field renaming; no semantic narrowing).
4. **Defers the operator-semantic refinement** to a later story (deferred-inventory candidate at G3 close).
5. **Is NOT buried** — it sits at the head of §1 under its own subsection header before the field-disposition table. Per spec mandate "must be explicit, not buried" → satisfied.

This precisely matches the spec's recommended Codex T1 verdict at line 16 of `migration-7c-5-g3-decision-card-extend-and-audit.md`. The statement establishes the semantic-alignment seam Winston W3 designed the cross-agent T1 review to surface before T2 commits to a contract evolution that would otherwise blur ADR-vs-legacy intent.

### §4 NEW field — **PASS**

`gate_focus: Literal["motion_clip_approval"]` listed at line 70 of contract-diff §4, sourced to "ADR 0002 gate-family taxonomy" with disposition "Add as a new closed one-value G3 family marker. Legacy G3Card has no `gate_focus`; this is an explicit contract-evolution ADD." Correctly distinguishes G3 from G2A (which already had gate_focus pre-migration).

### §6 progress_percent bounds preservation — **PASS**

§6 line 89 enumerates: "Preserve `progress_percent` with `Field(..., ge=0.0, le=100.0)`." Bounds are Pydantic-native, load-bearing, and explicitly carried through. §1 disposition row reinforces: "must remain `[0.0, 100.0]`; new shape-pin must cover `0.0`, `100.0`, `-0.1`, and `100.1`." This is the precise boundary-coverage matrix the spec AC-7c.5.G3-C demands. T2 shape-pin compliance gated by this requirement.

### §5 closed-enum tightening — **PASS**

`gate_id` Literal["G3"] retained, `gate_focus` Literal["motion_clip_approval"] added with reject-non-value coverage requirement, `schema_version` Literal["v1"] added, `verb` Literal closed-set retained. Triple-layer rejection preserved per Pydantic-v2 14-idiom checklist.

### Sections §1-§7 + §0 + §8 completeness — **PASS**

All 7 spec-required sections present (§1 field disposition with semantic alignment statement, §2 base disposition with audit_method, §3 meta disposition with audit_method, §4 new fields, §5 closed-enum tightening, §6 pattern-parity ratchets, §7 net diff summary). Plus §0 T0 frozen-hash pre-check + §8 T1 baseline evidence (verification command log). Structure mirrors G1 + G2C canonical contract-diff layout.

---

## CRITICAL ITEM #4: Backward-consumer audit + bounds preservation — **PASS**

Per-call-site enumeration is exhaustive: 38 executable consumer rows across `app/models/decision_cards/`, `app/marcus/orchestrator/`, `marcus/orchestrator/`, `tests/unit/`, `tests/integration/marcus/`, `tests/composition/`. Spot-check of the two production constructor sites:

- **`app/marcus/orchestrator/production_runner.py:441`** — line 35 of audit. Verdict: "requires-update-at-this-story; remove dropped legacy fields, supply `decision_card_digest`, convert meta to `_base.DecisionCardMeta`, add `gate_focus`/`schema_version` through defaults." Matches spec T2 expectations precisely.
- **`marcus/orchestrator/m3_trial.py:177`** — line 39 of audit. Verdict: identical update surface. Correct.

The audit also enumerates the antecedent `common`-dict construction sites (production_runner.py:409, m3_trial.py:152) where `drafted_proposal`, `evidence`, `risks`, and legacy `DecisionCardMeta` are first assembled. T2 must scrub these for the G3 branch; the audit identifies that `m3_trial.py` builds a SHARED `common` dict feeding G1/G2C/G3/G4 branches, so the temporary 2-class regime requires careful per-branch handling (G4 stays legacy; G1/G2C/G3 migrate to `_base.DecisionCardMeta`).

**`progress_percent` bounds preservation requirement** is captured at audit line 28 (per-site verdict on `g3.py:19` source declaration: "preserve/re-declare bounds exactly; shape-pin must cover boundary accept/reject cases") and reinforced in the field-access summary at line 103 ("`progress_percent` remains bounded `[0.0, 100.0]`"). Bounds carry-through is explicit.

**Documentation references (3 sites)** correctly flagged as deferred follow-on per spec (covered by `slab-7c-g1-g4-decision-card-doc-refresh` after all extend-and-audit stories close).

---

## CRITICAL ITEM #5: 2-class-regime validators NOT re-edited — **PASS**

Per the audit "Related Non-Grep Consumers" table (lines 62-68) + Field-Access Summary (lines 109-113), all four 2-class-regime substrate consumers are explicitly tagged `already-updated-by-G1`:

- `app/manifest/compiler.py:324` — already accepts `(DecisionCard, DecisionCardBase)` tuple. ✓
- `app/manifest/refs.py:10` — `resolve_dotted_ref` already supports tuple base classes. ✓
- `tests/unit/models/decision_cards/test_manifest_dotted_reference_resolver.py` — assertion already accepts either base. ✓
- `app/gates/resume_api.py:18, 23, 42, 58` — `StoredDecisionCard.card`, `compute_decision_card_digest`, `register_decision_card` all already typed `DecisionCard | DecisionCardBase`. ✓

Contract-diff §7 confirms (line 111): "No edit is expected for the 2-class-regime substrate unless T2 verification exposes a G3-specific gap." Codex consumes G1's widening; does not re-edit. Scope discipline maintained.

---

## T1 regression baseline acknowledgment

Codex T1-ready notice records `870 passed, 1 failed, 18 skipped`. The sole failure is `tests/parity/test_nfr_cg_block_aggregated.py::test_nfr_cg_block_structural_evidence[NFR-CG6]` — inherited governance-version drift expecting `2026-04-29-slab7b-twelve-stories` while governance JSON ships `2026-05-05-amelia-p5-and-wave-3-lookahead-policy` from V6/V7 amendment commit `57b92b2`. **This is NOT a G3 defect.** It is inherited from the same baseline that affects G2C and any other story authored against `57b92b2`. T11 standard close will track this for resolution at the appropriate parity-test refresh story.

---

## T2 scope acknowledgment

Codex MUST address the following at T2 (per the audit + contract-diff §7):

**G3 four-file lockstep:**
- `app/models/decision_cards/g3.py` — REWRITE to inherit `DecisionCardBase`; preserve `progress_percent` with `Field(..., ge=0.0, le=100.0)`; preserve `active_node_id` + `operator_prompt` with strip-then-non-empty validators; preserve `pending_nodes` default-empty list; ADD `gate_focus: Literal["motion_clip_approval"]` + `schema_version: Literal["v1"]`; UUID4 + enforce_uuid4_version + enforce_tz_aware per G2A canonical.
- `app/models/decision_cards/schema/g3.v1.schema.json` — REGENERATE.
- `tests/parity/test_decision_card_g3_shape.py` — NEW shape-pin (must include progress_percent boundary tests at 0.0 / 100.0 / -0.1 / 100.1; must reject non-`motion_clip_approval` gate_focus; must reject non-v1 schema_version; AMEND-7d-i AST-scan self-grep at T5.2; LOCKSTEP_CHECK import only).
- `tests/fixtures/decision_cards/g3_golden.json` — NEW deterministic golden.

**Constructor payload updates (drop legacy fields + add `decision_card_digest` + convert meta):**
- `app/marcus/orchestrator/production_runner.py:409` (common-dict) + `:441` (G3Card constructor).
- `marcus/orchestrator/m3_trial.py:152` (common-dict; G3 branch only) + `:177` (G3Card constructor).

**No edits expected for 2-class-regime substrate** (G1 handled it; G3 verifies via T6 R3 battery).

**Documentation:** Defer to `slab-7c-g1-g4-decision-card-doc-refresh` follow-on after all 4 extend-and-audit stories close.

---

## Sign-off

PRE-T2 cross-agent T1 review complete. **Codex unblocked. Resume T2.**

T2 effort sits squarely in the spec's K-target=1.4× / pts=2 / R-tier=R3 / lookahead-tier=2 budget. The §1 SEMANTIC ALIGNMENT STATEMENT does its job at T1 (sets the contract-evolution intent before code is written), so T2 should not relitigate ADR-vs-legacy semantics. If T2 effort meaningfully exceeds the 1.4× ceiling per `docs/dev-guide/story-cycle-efficiency.md`, surface to Claude at T6 for K-budget extension consideration before T9.

Standard T11 close at end of T9 will verify: backward-consumer audit verdicts honored + frozen-hash AMELIA-P4 delta-AC at T2 start + Pydantic-v2 14-idiom + progress_percent boundary coverage + AMELIA-P5 V6 §audit_method commitments executed faithfully (no DROP row reversed without re-running heavy smoke) + the inherited NFR-CG6 governance-version baseline drift either resolved or explicitly inherited.
