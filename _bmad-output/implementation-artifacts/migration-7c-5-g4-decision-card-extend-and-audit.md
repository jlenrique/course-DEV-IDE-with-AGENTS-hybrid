# Migration Story 7c.5.G4: G4 DecisionCard Extend-and-Audit (Fidelity Gate)

**Status:** ready-for-dev *(spec authored 2026-05-05 lookahead_tier=2 author-skeleton-ahead; predecessor 7c.4b CLOSED at `8b12970`; siblings G0+G2A CLOSED at `e2aa599`; G5+G6 CLOSED at `f059e84`; G1 CLOSED at `6a81e66`; G2C+G3 in-progress at T1-PASS post `aa9c040`. **DISPATCH HELD until G3 closes** OR operator (E)-elasticity override authorizes earlier — final extend-and-audit story; closes the 4-story chain.)*
**Sprint key:** `migration-7c-5-g4-decision-card-extend-and-audit`
**Epic:** Slab 7c — Marcus Orchestrational Tail (`migration-epic-slab-7c-orchestrational-tail`)
**Pts:** 2
**K-target:** 1.4×
**Estimated LOC:** ~350 (g4.py rewrite ~75 + schema regen ~50 + new shape-pin ~115 + new golden ~40 + contract-diff artifact ~75 + backward-consumer-audit artifact ~50 + __init__.py)
**Gate-mode:** **`dual-gate-cross-agent-CONTRACT-EVOLUTION`** (NAMED gate-mode per Winston W3)
**Cross-agent review:** false — T11 standard tier (the "cross-agent" component refers to T1 PRE-T2 cross-agent review)
**R-tier:** R3
**T11-tier:** standard
**Lookahead-tier:** 2
**files_touched:** 3 modified (`g4.py`, `schema/g4.v1.schema.json`, `__init__.py`) + 4 new (`tests/parity/test_decision_card_g4_shape.py`, `tests/fixtures/decision_cards/g4_golden.json`, `_bmad-output/implementation-artifacts/migration-7c-5-g4-contract-diff.md`, `_bmad-output/implementation-artifacts/migration-7c-5-g4-backward-consumer-audit.md`)

**V6 + V7 amendments inherit (codified at `57b92b2`):**
- AMELIA-P5 DROP-row Heavy gate binding=hard. Contract-diff §2 MUST carry per-row `audit_method=heavy|light`; DROP rows REQUIRE `audit_method=heavy` with smoke-pass evidence.
- V7 wave_3_lookahead_policy: G4 close completes the 3-story baseline (G2C + G3 + G4) for AMELIA-P2 P2-clean-×3 promotion gate. After G4 close, Wave-3 7c.6+ can elevate to N+3 cap if all 3 P2 freshness checks held clean.

---

## Story

As the dev-agent,
I want the legacy G4Card (Slab 7a substrate; closeout gate fields) extended-and-migrated to inherit from `DecisionCardBase` AND add `gate_focus: Literal["fidelity_gate"]` per ADR 0002 family taxonomy AND FR-7c-51 `schema_version` AND complete the four-file lockstep co-commit,
So that G4 fidelity gate conforms to the post-Slab-7c contract while preserving every backward-consumer access pattern AND closes the 4-story extend-and-audit chain (G1 → G2C → G3 → G4) that completes the 2-class-regime migration of all legacy DecisionCard subclasses to DecisionCardBase.

---

## Predecessor / Dependency Context

- **7c.4b** (CLOSED 2026-05-05): provides `DecisionCardBase`.
- **7c.5.G1** (CLOSED at `6a81e66`): canonical extend-and-audit migration pattern + 2-class-regime substrate widening (compiler.py + refs.py + dotted-ref-test + resume_api.py accept BOTH legacy DecisionCard AND new DecisionCardBase).
- **7c.5.G2C + 7c.5.G3** (in-progress at T1-PASS post `aa9c040`; CLOSE before this story dispatches in serial chain): canonical extend-and-audit T0/T1/T2 pattern reference.
- **`app/models/decision_cards/_frozen_hashes.py`**: G4 pre-extension SHA256 = `98536d2ab845972f96e8d374b08bb3929fb8d02024cbc56616c90424061c6b5a`. T2 verifies on-disk match.
- **Existing G4Card legacy substrate:** `app/models/decision_cards/g4.py` (33 LOC; gate_id=Literal["G4"], final_status=Literal["completed","partial","failed"], artifact_paths=list[str], outcome_summary=str; NO gate_focus field).
- **ADR 0002 §1 G4 row:** "Fidelity gate. Already shipped; extend-and-audit in 7c.5.G4."

**Special semantic note:** G4Card's existing `final_status` semantic ("trial closeout completed/partial/failed") fits cleanly with ADR 0002's "fidelity gate" framing (G4 evaluates whether the trial outputs meet fidelity standards before final closeout). No semantic-divergence statement needed (unlike G3 which had legacy mid-trial-review fields vs ADR-designated motion-clip-approval semantics). Confirm at T1.

---

## Acceptance Criteria

### AC-7c.5.G4-A — Pre-T2 contract-diff + backward-consumer audit artifacts (Winston W3 + V6 AMELIA-P5)

**Then** before T2 begins:

1. **`migration-7c-5-g4-contract-diff.md`** authored with 7 sections mirroring G1 + G2C + G3 (+ V6 AMELIA-P5 `audit_method` qualifiers per row):
   - §1 Legacy G4Card field disposition (preserved-via-re-declaration: gate_id Literal["G4"]; final_status Literal["completed","partial","failed"]; artifact_paths list[str] default empty; outcome_summary str strip-then-non-empty per G2A pattern). Confirm semantic fit with ADR 0002 "fidelity gate" framing — no divergence statement required if alignment is clean.
   - §2 Legacy DecisionCard base field disposition. **AMELIA-P5 binding=hard:** every row MUST carry `audit_method: heavy|light` qualifier per `docs/dev-guide/migration-story-governance.json::extend_and_audit_t1_audit_method`. DROP rows REQUIRE `audit_method=heavy` with smoke-pass evidence against `tests/composition/` + `tests/integration/marcus/` + `tests/integration/replay/`. Schema: `| field | disposition | audit_method | rationale |`. Per G1+G2C+G3 precedent, drafted_proposal + evidence + risks are candidate DROP rows — but per AMELIA-P5 each row's verdict requires smoke-pass evidence (G1's T6 reversal showed drafted_proposal + evidence had live consumers; G2C+G3 confirmed via smoke; G4 verifies for itself).
   - §3 Legacy DecisionCardMeta field disposition (mirror G1/G2C/G3 with `audit_method` per row).
   - §4 New fields added: `schema_version: Literal["v1"]` (FR-7c-51) + `decision_card_digest` (inherited from `DecisionCardBase`) + **`gate_focus: Literal["fidelity_gate"]`** (NEW; legacy G4Card has NO gate_focus field).
   - §5 Closed-enum tightening (gate_id remains `Literal["G4"]`; final_status remains 3-value Literal; new gate_focus + schema_version Literals).
   - §6 Pattern-parity ratchets per G2A canonical (UUID4 typing on card_id/trial_id; enforce_uuid4_version; enforce_tz_aware; strip-then-non-empty validators on outcome_summary; Field descriptions; inherited frozen=True).
   - §7 Net diff summary.

2. **`migration-7c-5-g4-backward-consumer-audit.md`** authored — per-call-site verdict for every G4Card consumer (grep `G4Card` exhaustively).

3. **AMELIA-P4 frozen-hash delta-AC pre-check:** verify `_frozen_hashes.py::FROZEN_AT_SHIP_HASHES["g4"] == "98536d2ab845972f96e8d374b08bb3929fb8d02024cbc56616c90424061c6b5a"` matches on-disk g4.py SHA256.

**Cross-agent T1 review checkpoint:** Drop T1 READY notice at `_codex-handoff/7c-5-g4.t1-ready.md`. HALT-AND-WAIT for cross-agent T1 review verdict at `_bmad-output/implementation-artifacts/7c-5-g4-t1-cross-agent-review-2026-05-NN.md`. PASS unblocks T2.

### AC-7c.5.G4-B — AMELIA-P4 frozen-hash delta-AC

At T2 start, observed `g4.py` SHA256 == `FROZEN_AT_SHIP_HASHES["g4"]`. Mismatch → HALT.

### AC-7c.5.G4-C — Four-file lockstep co-commit

Co-commit:
1. `app/models/decision_cards/g4.py` — REWRITTEN: `class G4Card(DecisionCardBase)`; preserved fields (final_status with closed Literal["completed","partial","failed"]; artifact_paths list[str] default empty; outcome_summary with strip-then-non-empty validator); ADDED `gate_focus: Literal["fidelity_gate"]`; ADDED `schema_version: Literal["v1"]`; re-declared base fields per G2A canonical (card_id: UUID4, trial_id: UUID4, gate_id: Literal["G4"], created_at, verb).
2. `app/models/decision_cards/schema/g4.v1.schema.json` — REGENERATED via Path.write_text per anti-pattern A18 (no PowerShell `>` redirection).
3. `tests/parity/test_decision_card_g4_shape.py` — NEW shape-pin (10-11 tests; field-presence + closed-enum on gate_id + gate_focus + final_status + JSON-Schema byte-match + golden round-trip + non-empty outcome_summary + artifact_paths default-empty acceptance + frozen mutation rejection). MUST `from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK` (AMEND-7d-i; bare import only).
4. `tests/fixtures/decision_cards/g4_golden.json` — NEW deterministic golden (`gate_id: "G4"`, `gate_focus: "fidelity_gate"`, `final_status: "completed"`, etc.).

### AC-7c.5.G4-D — Backward-consumer non-regression

Mirror G1/G2C/G3. Constructor sites updated. 2-class-regime substrate already accepts G4Card via DecisionCardBase post-G1.

### AC-7c.5.G4-E — Class-conformance + Pydantic-v2 14-idiom + V7 P2-clean-×3 close

Class-conformance count = T1-baseline + 1.

**V7 wave_3_lookahead_policy gate close:** G4 is the third (and final) extend-and-audit story. After G4 close, AMELIA-P2 freshness check across the consumed pre-auths under N+2 cap (G5+G6+G1+G2C+G3 close-batches) provides empirical baseline for promotion to N+3 cap on Wave-3 7c.6+ stories. Document P2-clean count at T10 dropbox.

---

## Tasks / Subtasks (compact; mirror G1+G2C+G3)

- [ ] **T0 — Frozen-hash pre-check** (file already populated; just verify g4 hash matches)
- [ ] **T1 — Contract-diff (with V6 AMELIA-P5 audit_method qualifiers per row) + backward-consumer audit + T1-ready dropbox**
- [ ] **CROSS-AGENT T1 REVIEW CHECKPOINT** (binding HALT)
- [ ] **T2 — AMELIA-P4 verification + G4Card rewrite** (preserve final_status closed Literal; add gate_focus + schema_version; pattern-parity ratchets per G2A canonical)
- [ ] **T3 — Schema regeneration** (Path.write_text per anti-pattern A18; canonical command embedded in Codex prompt)
- [ ] **T4 — Golden fixture authoring**
- [ ] **T5 — Shape-pin authoring** (mandatory AMEND-7d-i AST-scan self-grep at T5.2; INCLUDE final_status closed-enum boundary tests)
- [ ] **T6 — R-tier R3 verification battery**
- [ ] **T10 — Codex self-review dropbox** (include V7 P2-clean-×3 baseline summary for wave_3_lookahead_policy v1 gate)

---

## Required Readings (T1)

1. This story spec.
2. `_bmad-output/implementation-artifacts/migration-7c-5-g1-decision-card-extend-and-audit.md` (canonical extend-and-audit predecessor).
3. `_bmad-output/implementation-artifacts/migration-7c-5-g2c-decision-card-extend-and-audit.md` AND `migration-7c-5-g3-decision-card-extend-and-audit.md` (immediate predecessors; canonical V6 AMELIA-P5 application patterns).
4. `_bmad-output/implementation-artifacts/migration-7c-5-{g1,g2c,g3}-contract-diff.md` (canonical contract-diff structures with audit_method qualifiers).
5. `_bmad-output/implementation-artifacts/migration-7c-5-{g1,g2c,g3}-backward-consumer-audit.md`.
6. `_bmad-output/implementation-artifacts/7c-5-{g1,g2c,g3}-t1-cross-agent-review-2026-05-05.md` (T1 review precedents).
7. `_bmad-output/implementation-artifacts/7c-5-{g1,g2c,g3}-code-review-2026-05-NN.md` (T11 verdicts; document any patches affecting G4).
8. `app/models/decision_cards/_base.py` + `g4.py` (LEGACY) + `g2a.py` (canonical fresh-author) + `g1.py`/`g2c.py`/`g3.py` (canonical extend-and-audit migrated bodies — post-close).
9. `app/parity/contracts/tw_7c_3_firing.py` + `tests/structural/test_tw_7c_3_firing_spec_single_source.py`.
10. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (G4 = fidelity gate per §1).
11. `docs/dev-guide/specialist-anti-patterns.md::A18` (PowerShell BOM hardening).
12. `docs/dev-guide/pydantic-v2-schema-checklist.md`.
13. Governance JSON `7c-5-g4` + `extend_and_audit_t1_audit_method` (V6) + `wave_3_lookahead_policy` (V7).

## Sandbox-AC validator status

Spec contains zero forbidden CLIs in dev-agent AC blocks. Sandbox-AC: PASS (verified at T0).

---

## Dispatch Hold

**HELD until G3 closes** (serial dispatch chain G1→G2C→G3→G4) OR operator (E)-elasticity override authorizes earlier. G4 is the fourth and final extend-and-audit story; closes the 2-class-regime migration of all legacy DecisionCard subclasses to DecisionCardBase. After G4 close, V7 wave_3_lookahead_policy v1 P2-clean-×3 promotion gate fires (if all 3 P2 freshness checks held clean across G2C+G3+G4 close-batches), elevating Wave-3 7c.6+ default cap to N+3.

At dispatch-time, Claude verifies AMELIA-P2 freshness.

## Cross-agent T1 review checkpoint (same as G1/G2C/G3 pattern)

Two Claude review checkpoints: PRE-T2 + POST-T9. Both must PASS before commit + flip done.
