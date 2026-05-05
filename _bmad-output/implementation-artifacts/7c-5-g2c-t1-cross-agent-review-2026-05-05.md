# PRE-T2 Cross-Agent T1 Review — Story 7c.5.G2C (G2C DecisionCard Extend-and-Audit — Pre-Composition QA)

**Story key:** `migration-7c-5-g2c-decision-card-extend-and-audit`
**Reviewer:** Claude (Opus 4.7) — cross-agent T1 review (V6 AMELIA-P5 amendment 2026-05-05)
**Review date:** 2026-05-05
**Stage:** PRE-T2 — Codex HALTED at end of T1 awaiting verdict
**Predecessor:** G1 T1 review PASSed at commit `5c325a1`; G1 closed at `6a81e66` widening 2-class-regime substrate

---

## Verdict: **PASS — Codex MAY proceed to T2**

All three T1 deliverables are present, complete, and structurally sound. AMELIA-P5 V6 binding rule (`audit_method` qualifier on every contract-diff §2 + §3 row, with DROP rows requiring `audit_method=heavy` + smoke-pass evidence) is fully honored. Backward-consumer audit correctly identifies the narrow T2 update surface (two G2C constructor sites) and confirms G1's 2-class-regime widenings are consumed (not re-edited). Frozen-hash AMELIA-P4 baseline matches byte-for-byte.

No MUST-FIX. No SHOULD-FIX. Codex is unblocked.

---

## Verification battery

| Check | Status | Evidence |
|---|---|---|
| Frozen-hash file authored at `app/models/decision_cards/_frozen_hashes.py` | PASS | All 4 gates present (g1/g2c/g3/g4) |
| G2C on-disk hash matches recorded hash | PASS | Both = `237ce7d1b6c228cea5bc3653027cb40e50e40f316681a736d0692612dc7ba72a` |
| Contract-diff artifact authored at `migration-7c-5-g2c-contract-diff.md` | PASS | 132 LOC; 8 sections (incl. §0 T0 pre-check + §8 T1 baseline evidence) |
| Backward-consumer audit at `migration-7c-5-g2c-backward-consumer-audit.md` | PASS | 110 LOC; per-call-site verdicts for executable + non-grep + smoke + doc consumers |
| T1 READY notice at `_codex-handoff/7c-5-g2c.t1-ready.md` | PASS | Lists deliverables + AMELIA-P5 Summary + T2 update surface |
| Class-conformance baseline | PASS | `16 parity contract file(s) conform (11 activation + 5 decision-card shape-pin)` |
| Sandbox-AC validator | PASS | `no sandbox-AC violations across 1 story file(s)` |
| Governance JSON V6 + V7 present | PASS | `extend_and_audit_t1_audit_method` + `wave_3_lookahead_policy` both in `migration-story-governance.json` |
| Legacy `app/models/decision_cards/g2c.py` UNMODIFIED at T1 | PASS | Hash matches recorded pre-extension value; body changes correctly deferred to T2 |
| 2-class-regime substrate UNMODIFIED at T1 | PASS | `git status` shows no modifications to `compiler.py`/`refs.py`/dotted-ref-test/`resume_api.py` |
| T1 regression baseline | PASS-modulo-inherited | 870 passed, 1 failed (NFR-CG6 governance-version drift from `57b92b2`, not G2C body work), 18 skipped |

---

## Critical Item #1: AMELIA-P5 §audit_method compliance (V6 binding=hard)

**Verdict: PASS**

§2 schema verified as `| field | disposition | audit_method | rationale |`. §3 (Legacy DecisionCardMeta) also carries `audit_method` per governance JSON `extend_and_audit_t1_audit_method` (correct — §3 contains DROP rows so the qualifier applies).

**§2 DROP rows (all `audit_method=heavy` with smoke-pass evidence):**

- `drafted_proposal` — heavy: `pytest -k drafted_proposal --co -q` collected 0 tests in required roots. Targeted grep found direct reads only in G1-only tests; `pytest tests/composition/test_pre_gate_marcus_precedence_unaltered.py tests/integration/marcus/test_runner_threads_pre_fill_to_decision_card.py -q` passed 4 tests.
- `evidence` — heavy: collected 7 tests; execution passed 7 tests; targeted grep confirmed direct reads only in G1-only adjacent-summary tests; `pytest tests/integration/marcus/test_gate_handler_loads_adjacent_summary.py -q` passed 3 tests.
- `risks` — heavy: collected 0 tests; targeted grep found no `card.risks` access in required roots.

**§3 DROP rows (all `audit_method=heavy`):**

- `reject_rate`, `party_mode_contributions`, `consolidated_at`, `sanctum_warnings` — heavy: `--co` runs collected 0 tests in required roots; targeted grep found no required-root reads. Audit explicitly notes that `tests/integration/gates/` reads `party_mode_contributions`/`consolidated_at` on `G-PARTY` cards, not G2C — surgical scope discipline.

**ADD-only / preserve / inherit rows correctly use `audit_method=light`:** `card_id`, `trial_id`, `created_at`, `verb`, `meta`, `model_config.*` rows — all 8 light-marked rows are non-DROP. No light-marked DROP appears anywhere.

**Codex T1-ready notice AMELIA-P5 Summary:** Section "AMELIA-P5 Summary" enumerates DROP rows + smoke-pass evidence per row, including the §3 metadata DROP rows. Compliance is full and explicit.

---

## Critical Item #2: Frozen-hash AMELIA-P4 verification

**Verdict: PASS**

Independently re-computed:

```text
on_disk_g2c  = 237ce7d1b6c228cea5bc3653027cb40e50e40f316681a736d0692612dc7ba72a
recorded_g2c = 237ce7d1b6c228cea5bc3653027cb40e50e40f316681a736d0692612dc7ba72a
```

Both match the spec-recorded value byte-for-byte. AMELIA-P4 frozen-at-ship baseline is intact. T2 will consume this hash for the delta-AC check before body extension begins.

---

## Critical Item #3: Contract-diff completeness (mirror G1 7-section structure)

**Verdict: PASS — exceeds template (8 sections including §0 T0 pre-check + §8 T1 baseline evidence)**

- §1 Legacy G2CCard field disposition — 4 fields (`gate_id`/`readiness_status`/`blocking_issues`/`ready_nodes`) all marked preserve-via-re-declaration with rationale. Discriminator routing + readiness payload + list-shape constructor coverage all addressed.
- §2 Legacy DecisionCard base disposition — 11 rows total with `audit_method` qualifier. DROP rows: `drafted_proposal`/`evidence`/`risks`. preserve-via-re-declaration: `card_id`/`trial_id`/`created_at`/`verb`. preserve-via-base: `meta`/`extra="forbid"`/`validate_assignment=True`. `frozen=False -> True` change called out as intentional 7c pattern.
- §3 Legacy DecisionCardMeta disposition — 7 rows with `audit_method` qualifier. preserve-via-base: `cache_state`/`affected_nodes`/`override_trail`. DROP+heavy: `reject_rate`/`party_mode_contributions`/`consolidated_at`/`sanctum_warnings`.
- §4 New fields — 3 rows: `schema_version: Literal["v1"]` (FR-7c-51), `decision_card_digest: str` (inherited from `DecisionCardBase`), and **`gate_focus: Literal["pre_composition_qa"]` correctly identified as a NEW field with explicit note "Legacy G2CCard has no `gate_focus`; this is an explicit contract-evolution ADD."** This addresses the review-framework caveat exactly.
- §5 Closed-enum tightening — `gate_id` Literal["G2C"], `readiness_status` Literal["ready","blocked"], `gate_focus` Literal["pre_composition_qa"], `schema_version` Literal["v1"], `verb` Literal["approve","edit","reject"]. All five closed enums called out for triple-layer rejection.
- §6 Pattern-parity ratchets — six G2A-canonical idioms enumerated: UUID4 typing + `enforce_uuid4_version` + `enforce_tz_aware` + closed Literals + `Field(..., description=...)` + inherited `DecisionCardBase` config. Audit correctly notes "G2C has no free-text scalar field requiring strip-then-non-empty validation" — accurate (G2C has no `trial_summary`/`opened_by` analog; only list fields and Literals).
- §7 Net diff summary — Added/preserved-by-re-declaration/preserved-via-base/dropped lists complete. T2 consumer-update list explicitly enumerates the two constructor sites + four-file lockstep + the negative assertion that 2-class-regime substrate needs NO new edit.

Mirrors G1 structure faithfully and improves on it (§0 + §8 add T0/T1 evidence inline rather than scattering across separate notices).

---

## Critical Item #4: Backward-consumer audit completeness

**Verdict: PASS — both spec-named constructor sites correctly identified at the exact line numbers**

Spot-check confirmed:

- `app/marcus/orchestrator/production_runner.py:434` — verified live; constructs `G2CCard(**common, readiness_status="ready", blocking_issues=[], ready_nodes=pending_nodes[:3])`. Audit verdict: `requires-update-at-this-story; remove dropped legacy fields, supply decision_card_digest, convert meta to _base.DecisionCardMeta, add gate_focus/schema_version through defaults`. Accurate.
- `marcus/orchestrator/m3_trial.py:169` — verified live; constructs `G2CCard(**common, verb="edit", readiness_status="ready", blocking_issues=[], ready_nodes=["07C", "09"])`. Audit verdict: same as above. Accurate.

Audit also enumerates:

- 5 sites under `app/models/decision_cards/` (the file itself + flat-export + discriminated-union + `__all__`)
- 2 sites under `app/marcus/orchestrator/production_runner.py` (import + line 409 `common` build + line 434 constructor)
- 3 sites under `marcus/orchestrator/m3_trial.py` (import + line 152 `common` build + line 169 constructor)
- 6 sites in `tests/unit/models/decision_cards/` (helpers + per-gate-strict + dotted-ref + discriminated-union)
- 4 sites in `tests/unit/marcus/` and `tests/unit/manifest/` (manifest dotted-ref string stability)
- 6 G1-only smoke consumers under `tests/composition/` + `tests/integration/marcus/` (correctly classified — direct reads of `drafted_proposal`/`evidence` all construct `gate_id="G1"` cards, NOT G2C)
- 6 already-updated-by-G1 sites under `app/manifest/` + `app/gates/resume_api.py` (correctly marked as accepted, not re-edited)
- 3 deferred-followon documentation sites

Per-site verdict format mirrors G1 audit (preserved-via-re-declaration / preserved-via-base / preserved-via-flat-export / requires-update-at-this-story / already-updated-by-G1 / requires-deferred-followon). Field-Access Summary accurately concludes "the only executable G2C constructors are production_runner.py:434 and m3_trial.py:169" — matches the live grep evidence.

---

## Critical Item #5: 2-class-regime validators NOT re-edited

**Verdict: PASS**

`git status --short` confirms NO modifications to:

- `app/manifest/compiler.py`
- `app/manifest/refs.py`
- `tests/unit/models/decision_cards/test_manifest_dotted_reference_resolver.py`
- `app/gates/resume_api.py`

Audit's "Related Non-Grep Consumers" section correctly marks all six rows under these files as `already-updated-by-G1; no G2C-specific edit expected`. §7 Net Diff Summary closes with the explicit negative assertion: "No edit is expected for the 2-class-regime substrate unless T2 verification exposes a G2C-specific gap." This is precisely the consume-not-re-edit discipline the review framework requires. Codex's T1-ready notice "T2 Update Surface Identified" section reaffirms: "2-class-regime substrate already accepts both `DecisionCard` and `DecisionCardBase` after G1."

If T2 verification surfaces a G2C-specific compatibility gap that G1 did not exercise (e.g., a discriminated-union path that exclusively walks G2C dotted refs), Codex should surface it at T6 K-budget review rather than silently widen substrate.

---

## T2 scope acknowledgment

Codex MUST address the following at T2 (per the audit + V6 binding rule):

**Constructor payload updates (drop legacy fields + supply `decision_card_digest` + convert meta + add `gate_focus`/`schema_version`):**

- `app/marcus/orchestrator/production_runner.py:434` (G2C branch only — G1 branch already handled by predecessor story)
- `marcus/orchestrator/m3_trial.py:169` (G2C branch only)

**G2C four-file lockstep:**

- `app/models/decision_cards/g2c.py` — migrate inheritance from legacy `DecisionCard` to `DecisionCardBase`, re-declare 4 G2C-specific fields, add `gate_focus`/`schema_version`, drop legacy common fields
- `schema/g2c.v1.schema.json` — regenerate
- `tests/fixtures/decision_cards/g2c_golden.json` — refresh
- `tests/parity/test_decision_card_g2c_shape.py` — author new shape-pin (will become parity contract file #17 after T2)

**Documentation:** Defer to existing follow-on `slab-7c-g1-g4-decision-card-doc-refresh` after all 4 extend-and-audit stories close (already named-but-not-filed).

**Inherited NFR-CG6 governance-version drift:** Not a G2C body issue; the test expects `2026-04-29-slab7b-twelve-stories` but the JSON now reads `2026-05-05-amelia-p5-and-wave-3-lookahead-policy` from commit `57b92b2`. Either (a) update the test expectation to track the V6/V7 amendment version (cleanest), or (b) leave as-is and document in Completion Notes that the failure is inherited and will be cleared by a separate governance-version-bump cleanup. Codex should pick (a) at T9 if doing so does not exceed K-budget.

If T2 effort meaningfully exceeds K-target=1.4× per `docs/dev-guide/story-cycle-efficiency.md` (e.g., T2 surfaces a G2C-specific 2-class-regime gap requiring substrate widening), surface to Claude at T6 for K-budget extension consideration before T9. Standard T11 review at end of T9 will verify all backward-consumer audit verdicts honored + frozen-hash AMELIA-P4 delta-AC + Pydantic-v2 14-idiom + the six PARALLEL-DISPATCH GUARDRAILS.

---

## Sign-off

PRE-T2 cross-agent T1 review complete. **Codex unblocked. Resume T2.**

This is the SECOND end-to-end exercise of the cross-agent T1 review checkpoint (G1 was first at `5c325a1`). G1's 3-class-regime scope adjacency catch is NOT mirrored here because G1 already widened the substrate; G2C inherits clean. The pattern is functioning as designed: G1 paid the substrate-widening cost once, G2C/G3/G4 should consume it for free unless their specific union/dotted-ref paths expose a gap G1 did not exercise.

V6 AMELIA-P5 amendment (`audit_method` qualifier) is functioning as designed: every DROP row carries explicit smoke-pass evidence inline in the contract-diff, eliminating the prior risk of light-audit DROP rows slipping through with insufficient justification. G2C is the first extend-and-audit story to operate fully under V6 from T0; compliance is full.

Codex MAY proceed to T2.
