# PRE-T2 Cross-Agent T1 Review — Story 7c.5.G4 (G4 DecisionCard Extend-and-Audit, Fidelity Gate)

**Story key:** `migration-7c-5-g4-decision-card-extend-and-audit`
**Reviewer:** Claude (Opus 4.7) — cross-agent T1 review (Winston W3 amendment + V6 AMELIA-P5 amendment + V7 wave_3_lookahead_policy binding HALT)
**Review date:** 2026-05-05
**Stage:** PRE-T2 — Codex HALTED at end of T1 awaiting verdict
**Chain position:** FINAL extend-and-audit (closes G1 → G2C → G3 → G4 chain). Predecessor G1 PASS at `5c325a1`; siblings G2C+G3 parallel PASS at `aa9c040`. Operator (E)-elasticity override authorized G4 dispatch ahead of G3 body close.

---

## Verdict: **PASS — Codex MAY proceed to T2**

All three T1 deliverables are present, complete, structurally sound, and AMELIA-P5 V6-conformant. The G4 §1 SEMANTIC ALIGNMENT STATEMENT is the **clean-fit** case (not a divergence statement): legacy `final_status / artifact_paths / outcome_summary` describe trial-closeout posture, which fits ADR 0002 "fidelity gate" framing without operator-semantic refinement deferral — explicitly the inverse of G3's mid-trial-vs-motion-clip-approval divergence. All seven DROP rows across §2 + §3 carry `audit_method=heavy` with smoke-pass evidence. No MUST-FIX. No SHOULD-FIX. Codex is unblocked.

---

## Operational baseline note (parallel-dispatch + (E)-elasticity reality)

Per Codex T1-ready notice, the operator instructed Codex to dispatch G4 even though local sprint status records G2C and G3 as `in-progress` (their bodies not yet migrated). This is the operator (E)-elasticity override path explicitly contemplated in the G4 spec at line 3 ("DISPATCH HELD until G3 closes OR operator (E)-elasticity override authorizes earlier"). Codex correctly recorded the local class-conformance baseline as **16** (11 activation + 5 decision-card shape-pin) rather than the prompt's expected "likely 18", because G2C+G3 shape-pins are not yet on disk. **This is operational reality, not a defect.** T1 baseline integrity preserved — class-conformance validator still runs PASS at the observed count.

G4 consumes — does not re-edit — the `_frozen_hashes.py` substrate (G1-established) and the G1-widened 2-class-regime validators (compiler.py, refs.py, dotted-ref test, resume_api.py). Cross-verified via `git diff --name-only HEAD` over those six paths: zero modifications.

---

## Verification battery

| Check | Status | Evidence |
|---|---|---|
| On-disk `app/models/decision_cards/g4.py` SHA256 | PASS | `98536d2ab845972f96e8d374b08bb3929fb8d02024cbc56616c90424061c6b5a` (independently re-computed) |
| `FROZEN_AT_SHIP_HASHES["g4"]` recorded | PASS | `98536d2ab845972f96e8d374b08bb3929fb8d02024cbc56616c90424061c6b5a` (matches byte-for-byte) |
| AMELIA-P4 frozen-hash delta-AC pre-check | PASS | Both equal — pre-check satisfied before T2 |
| Sandbox-AC validator on story spec | PASS | `PASS - no sandbox-AC violations across 1 story file(s)` |
| Class-conformance validator | PASS | `PASS: 16 parity contract file(s) conform (11 activation + 5 decision-card shape-pin)` |
| Contract-diff artifact at `migration-7c-5-g4-contract-diff.md` | PASS | 136 lines; 9 sections (T0 + 7 spec-required + T1 baseline evidence) |
| Backward-consumer audit at `migration-7c-5-g4-backward-consumer-audit.md` | PASS | 115 lines; 32 executable + 3 non-grep + 6 required-root smoke + 3 doc references |
| T1 READY notice at `_codex-handoff/7c-5-g4.t1-ready.md` | PASS | All deliverables enumerated; AMELIA-P5 summary + T2 update surface listed; (E)-elasticity dispatch caveat recorded |
| Legacy `app/models/decision_cards/g4.py` UNMODIFIED at T1 | PASS | Frozen hash equals on-disk hash; Codex correctly defers body changes to T2 |
| 2-class-regime validators UNMODIFIED at T1 | PASS | `git diff --name-only HEAD` over compiler.py + refs.py + dotted-ref-test + resume_api.py — zero modifications |

---

## CRITICAL ITEM #1: AMELIA-P5 V6 §audit_method compliance — **PASS**

Contract-diff §2 schema is exactly `| field | disposition | audit_method | rationale |` per V6 binding=hard. Every DROP row in §2 + §3 carries `audit_method=heavy` with smoke-pass evidence:

**§2 DROP rows (3):**
- `drafted_proposal` → `audit_method=heavy`. Smoke: `pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k drafted_proposal --co -q` collected 0 tests in required roots; targeted `card.drafted_proposal` reads exist only in G1-only tests; `pytest tests/composition/test_pre_gate_marcus_precedence_unaltered.py tests/integration/marcus/test_runner_threads_pre_fill_to_decision_card.py -q` passed 4 tests. No required-root G4 direct read exists.
- `evidence` → `audit_method=heavy`. Smoke: collect found 7 tests; execution passed 7. Direct `card.evidence` reads exist only in G1-only adjacent-summary tests; `pytest tests/integration/marcus/test_gate_handler_loads_adjacent_summary.py -q` passed 3 tests.
- `risks` → `audit_method=heavy`. Smoke: 0 tests collected; targeted grep found no `card.risks` or `getattr(..., "risks")` access in required roots.

**§3 DROP rows (4):**
- `reject_rate`, `party_mode_contributions`, `consolidated_at`, `sanctum_warnings` — all `audit_method=heavy`. Smoke per field: 0 tests collected in required roots; targeted grep found no required-root reads. Codex correctly distinguishes that `tests/integration/gates/` reads of `party_mode_contributions` + `consolidated_at` are for `G-PARTY` cards, **not G4** — same precise discriminator as G2C+G3 verdicts.

**Light rows correctly bounded:** every `light` audit_method row corresponds to `preserve-via-re-declaration` / `preserve-via-base` / new-field-add. Zero light rows on DROP dispositions. V6 audit_method legend respected. Validator predicate (DROP+light → REJECT) holds.

---

## CRITICAL ITEM #2: AMELIA-P4 frozen-hash verification — **PASS**

Independently re-computed both values via the verification commands specified in the prompt:

```
g4 (on-disk)  98536d2ab845972f96e8d374b08bb3929fb8d02024cbc56616c90424061c6b5a
recorded      98536d2ab845972f96e8d374b08bb3929fb8d02024cbc56616c90424061c6b5a
```

Match byte-for-byte. AMELIA-P4 delta-AC pre-check satisfied. Codex correctly defers body changes to T2 (legacy `g4.py` UNMODIFIED at T1).

---

## CRITICAL ITEM #3: Contract-diff completeness + G4 SEMANTIC ALIGNMENT (CLEAN-FIT) — **PASS**

### §1 SEMANTIC ALIGNMENT VERDICT — clean-fit case (no divergence statement required)

The §1 statement appears at lines 18-20 of the contract-diff:

> Semantic alignment verdict: the legacy G4 closeout fields fit ADR 0002's "fidelity gate" framing cleanly. `final_status`, `artifact_paths`, and `outcome_summary` describe the trial output posture at closeout, which is the point where fidelity standards are confirmed before final handoff. Unlike G3, no semantic-divergence statement or field-name compromise is required. T2 should preserve the legacy fields verbatim and add `gate_focus: Literal["fidelity_gate"]` as the post-Slab-7c family marker.

This statement:
1. **Explicitly compares with the G3 precedent** (which DID require a divergence statement) and articulates why G4 does not.
2. **States an explicit verdict** (preserve verbatim + add gate_focus marker; no field renaming).
3. **Bounds the migration scope** (no operator-semantic refinement deferred to follow-on; clean ADR↔legacy alignment).
4. **Matches the spec's "Special semantic note" at line 39** of the story spec ("G4Card's existing `final_status` semantic ('trial closeout completed/partial/failed') fits cleanly with ADR 0002's 'fidelity gate' framing... No semantic-divergence statement needed").

The clean-fit verdict is the correct verdict here. Winston W3 designed the cross-agent T1 review precisely so that semantic alignment seams are surfaced BEFORE T2 commits to a contract evolution; in G4's case, no seam exists and the audit confirms it explicitly. Verifying the absence of divergence is as load-bearing as documenting one.

### §4 NEW field — **PASS**

`gate_focus: Literal["fidelity_gate"]` listed at line 67 of contract-diff §4, sourced to "ADR 0002 gate-family taxonomy" with disposition "Add as a new closed one-value G4 family marker. Legacy G4Card has no `gate_focus`; this is an explicit contract-evolution ADD." Correctly distinguishes G4 from G2A (which already had gate_focus pre-migration) and aligns with G1/G2C/G3 ADD pattern.

### §5 closed-enum tightening — **PASS**

`gate_id` Literal["G4"] retained, `final_status` Literal["completed","partial","failed"] retained with explicit shape-pin coverage requirement (must reject `"in_progress"`, `"unknown"`, `"COMPLETED"`, and non-string values), `gate_focus` Literal["fidelity_gate"] added with reject-non-value coverage requirement, `schema_version` Literal["v1"] added, `verb` Literal["approve","edit","reject"] retained. Triple-layer rejection preserved per Pydantic-v2 14-idiom checklist. The `final_status` closed three-value set is load-bearing closeout state per the AC-7c.5.G4-C requirement; T2 shape-pin must not widen.

### §6 pattern-parity ratchets — **PASS**

§6 enumerates the canonical G2A ratchets: UUID4 typing on `card_id`/`trial_id`, `enforce_uuid4_version` validator, `enforce_tz_aware` for `created_at`, strip-then-non-empty validator for `outcome_summary`, every field with `Field(..., description=...)`, and inheritance of `extra="forbid"` + `validate_assignment=True` + `frozen=True` from `DecisionCardBase`. Mirrors G2A canonical and post-G1/G2C/G3 patterns.

### Sections §1–§7 + §0 + §8 completeness — **PASS**

All 7 spec-required sections present (§1 field disposition with semantic alignment statement, §2 base disposition with audit_method, §3 meta disposition with audit_method, §4 new fields, §5 closed-enum tightening, §6 pattern-parity ratchets, §7 net diff summary). Plus §0 T0 frozen-hash pre-check + §8 T1 baseline evidence (verification command log). Structure mirrors G1 + G2C + G3 canonical contract-diff layouts.

---

## CRITICAL ITEM #4: Backward-consumer audit completeness — **PASS**

Per-call-site enumeration is exhaustive: 32 executable consumer rows across `app/models/decision_cards/`, `app/marcus/orchestrator/`, `marcus/orchestrator/`, `tests/unit/`, `tests/integration/marcus/`, `tests/composition/`. Spot-check of the two production constructor sites (the prompt's named verification targets):

- **`app/marcus/orchestrator/production_runner.py:449`** — line 33 of audit. Verdict: "requires-update-at-this-story; remove dropped legacy fields, supply `decision_card_digest`, convert meta to `_base.DecisionCardMeta`, add `gate_focus`/`schema_version` through defaults." Matches spec T2 expectations precisely.
- **`marcus/orchestrator/m3_trial.py:185`** — line 37 of audit. Verdict: identical update surface. Correct.

The audit also enumerates the antecedent `common`-dict construction sites (production_runner.py:409, m3_trial.py:152) where `drafted_proposal`, `evidence`, `risks`, and legacy `DecisionCardMeta` are first assembled. T2 must scrub these for the G4 branch; the audit identifies that `m3_trial.py` builds a SHARED `common` dict feeding G1/G2C/G3/G4 branches. Per audit, after T2 G4 close, all four legacy gate branches will be on `DecisionCardBase` — which closes the 2-class regime for the migrated subclasses (legacy `base.py` separately retired in a later cleanup story).

**Field-Access Summary** (audit lines 81-98) explicitly confirms: no audited executable site reads `G4Card.drafted_proposal`, `G4Card.evidence`, `G4Card.risks`, or legacy G4 meta extensions directly after construction. No `G4Card(` constructor exists under the required-root smoke trees; the only executable G4 constructors are the two production sites named above. Direct reads of `drafted_proposal` and `evidence` exist but are bound to `gate_id="G1"` cards, not G4.

**Documentation references (3 sites)** correctly flagged as deferred follow-on (covered by `slab-7c-g1-g4-decision-card-doc-refresh` after all extend-and-audit stories close). ADR 0002's G4 fidelity-gate row noted as "Cleanly aligns with legacy closeout fields; contract diff records this semantic fit" — reinforces §1 clean-fit verdict.

---

## CRITICAL ITEM #5: 2-class-regime validators NOT re-edited — **PASS**

Per the audit "Related Non-Grep Consumers" table (lines 56-60) + Field-Access Summary (lines 98-103), all four 2-class-regime substrate consumers are explicitly tagged `already-updated-by-G1`:

- `app/manifest/compiler.py` — already accepts `(DecisionCard, DecisionCardBase)` tuple.
- `app/manifest/refs.py` — `resolve_dotted_ref` already supports tuple base classes.
- `tests/unit/models/decision_cards/test_manifest_dotted_reference_resolver.py` — assertion already accepts either base.
- `app/gates/resume_api.py` — `StoredDecisionCard.card`, `compute_decision_card_digest`, `register_decision_card` all already typed `DecisionCard | DecisionCardBase`.

Independently verified via `git diff --name-only HEAD` over those four paths: zero modifications. Plus `app/models/decision_cards/g4.py` and `app/models/decision_cards/_frozen_hashes.py` unmodified. Contract-diff §7 confirms (line 110): "No edit is expected for the 2-class-regime substrate unless T2 verification exposes a G4-specific gap." Codex consumes G1's widening; does not re-edit. Scope discipline maintained.

---

## V7 P2-clean-×3 baseline note (informational — for T11 not T1)

Per V7 `wave_3_lookahead_policy` (codified at `57b92b2`), G4 close completes the 3-cycle baseline for AMELIA-P2 freshness elevation gate. After G4 closes, if AMELIA-P2 freshness check across the consumed pre-auths under N+2 cap (G2C + G3 + G4 close-batches) held clean, Wave-3 7c.6+ stories elevate to N+3 cap.

This T1 review acknowledges the baseline-closure expectation but does NOT evaluate P2 freshness: that evaluation is T11's job at T9 close, not T1's. Codex correctly noted this in the T1-ready dropbox §V7 Note ("T10 must report whether G2C, G3, and G4 freshness remained clean enough to unlock Wave-3 N+3"). The contract-diff and backward-consumer audit do not introduce any P2-stale signal — the G4 spec was authored against `57b92b2` which carries V6+V7, and all governance-JSON references resolve to current schema.

---

## T1 regression baseline acknowledgment

Codex T1-ready notice records `870 passed, 1 failed, 18 skipped`. The sole failure is `tests/parity/test_nfr_cg_block_aggregated.py::test_nfr_cg_block_structural_evidence[NFR-CG6]` — inherited governance-version drift expecting `2026-04-29-slab7b-twelve-stories` while governance JSON ships `2026-05-05-amelia-p5-and-wave-3-lookahead-policy` from V6/V7 amendment commit `57b92b2`. **This is NOT a G4 defect.** It is the same inherited drift seen in G2C and G3 T1 baselines. T11 standard close will track this for resolution at the appropriate parity-test refresh story.

---

## T2 scope acknowledgment

Codex MUST address the following at T2 (per the audit + contract-diff §7):

**G4 four-file lockstep:**
- `app/models/decision_cards/g4.py` — REWRITE to inherit `DecisionCardBase`; preserve `final_status` as closed `Literal["completed", "partial", "failed"]`; preserve `artifact_paths: list[str]` with default empty; preserve `outcome_summary: str` with strip-then-non-empty validator; ADD `gate_focus: Literal["fidelity_gate"]` + `schema_version: Literal["v1"]`; UUID4 + `enforce_uuid4_version` + `enforce_tz_aware` per G2A canonical.
- `app/models/decision_cards/schema/g4.v1.schema.json` — REGENERATE via `Path.write_text` per anti-pattern A18 (no PowerShell `>` redirection).
- `tests/parity/test_decision_card_g4_shape.py` — NEW shape-pin (10-11 tests; field-presence + closed-enum on `gate_id` + `gate_focus` + `final_status` boundary tests including non-three-value rejections + JSON-Schema byte-match + golden round-trip + non-empty `outcome_summary` + `artifact_paths` default-empty acceptance + frozen mutation rejection; AMEND-7d-i AST-scan self-grep at T5.2; LOCKSTEP_CHECK bare import only).
- `tests/fixtures/decision_cards/g4_golden.json` — NEW deterministic golden.

**Constructor payload updates (drop legacy fields + add `decision_card_digest` + convert meta):**
- `app/marcus/orchestrator/production_runner.py:409` (common-dict; G4 branch only) + `:449` (G4Card constructor).
- `marcus/orchestrator/m3_trial.py:152` (common-dict; G4 branch only) + `:185` (G4Card constructor).

**No edits expected for 2-class-regime substrate** (G1 handled it; G4 verifies via T6 R3 battery).

**Documentation:** Defer to `slab-7c-g1-g4-decision-card-doc-refresh` follow-on after all 4 extend-and-audit stories close — which is **G4 itself closing the chain**.

**T10 dropbox V7 reporting:** Codex MUST document P2-clean count for G2C+G3+G4 baseline at T10 dropbox per AC-7c.5.G4-E.

---

## Sign-off

PRE-T2 cross-agent T1 review complete. **Codex unblocked. Resume T2.**

T2 effort sits squarely in the spec's K-target=1.4× / pts=2 / R-tier=R3 / lookahead-tier=2 budget. The §1 SEMANTIC ALIGNMENT clean-fit verdict means T2 should NOT relitigate ADR-vs-legacy semantics — preserve `final_status`/`artifact_paths`/`outcome_summary` verbatim, add `gate_focus="fidelity_gate"`, and apply the G2A canonical pattern-parity ratchets. If T2 effort meaningfully exceeds the 1.4× ceiling per `docs/dev-guide/story-cycle-efficiency.md`, surface to Claude at T6 for K-budget extension consideration before T9.

**Chain-closure note:** G4 close completes the 4-story extend-and-audit chain G1→G2C→G3→G4 — completing the 2-class-regime migration of all legacy DecisionCard subclasses to DecisionCardBase. Standard T11 close at end of T9 will verify: backward-consumer audit verdicts honored + frozen-hash AMELIA-P4 delta-AC at T2 start + Pydantic-v2 14-idiom + AMELIA-P5 V6 §audit_method commitments executed faithfully (no DROP row reversed without re-running heavy smoke) + V7 P2-clean-×3 baseline status documented in T10 dropbox + the inherited NFR-CG6 governance-version baseline drift either resolved or explicitly inherited.
