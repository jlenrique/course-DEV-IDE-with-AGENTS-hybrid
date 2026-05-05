# Migration Story 7c.5.G2C: G2C DecisionCard Extend-and-Audit (Pre-Composition QA)

**Status:** ready-for-dev *(spec authored 2026-05-05 lookahead_tier=2 author-skeleton-ahead; predecessor 7c.4b CLOSED at `8b12970`; siblings G0+G2A CLOSED at `e2aa599`; G5+G6 CLOSED at `f059e84`; G1 in-progress 2026-05-05 (HALTED at PRE-T2 cross-agent T1 review). **DISPATCH HELD until G1 closes** — extend-and-audit chain is SERIAL only; all 4 stories share the legacy DecisionCard migration surface + the 2-class-regime compatibility validators.)*
**Sprint key:** `migration-7c-5-g2c-decision-card-extend-and-audit`
**Epic:** Slab 7c — Marcus Orchestrational Tail (`migration-epic-slab-7c-orchestrational-tail`)
**Pts:** 2
**K-target:** 1.4× (heavier than fresh-author due to backward-consumer audit + contract-diff artifact + 2-class-regime migration)
**Estimated LOC:** ~350 (g2c.py rewrite ~70 + schema regen ~50 + new shape-pin ~115 + new golden ~40 + contract-diff artifact ~70 + backward-consumer-audit artifact ~50 + __init__.py + minimal validator updates if G1 already absorbed them)
**Gate-mode:** **`dual-gate-cross-agent-CONTRACT-EVOLUTION`** (NAMED gate-mode per Winston W3)
**Cross-agent review:** false — T11 standard tier (the "cross-agent" component refers to the **T1 PRE-T2 cross-agent review** of contract-diff + backward-consumer audit; NOT T11)
**R-tier:** R3 (full broad regression)
**T11-tier:** standard
**Lookahead-tier:** 2 (author-skeleton-ahead; substrate fully landed; G1 contract-diff + backward-consumer audit pattern is the canonical reference once G1 closes)
**files_touched:** 3 modified (`g2c.py`, `schema/g2c.v1.schema.json`, `__init__.py`) + 4 new (`tests/parity/test_decision_card_g2c_shape.py`, `tests/fixtures/decision_cards/g2c_golden.json`, `_bmad-output/implementation-artifacts/migration-7c-5-g2c-contract-diff.md`, `_bmad-output/implementation-artifacts/migration-7c-5-g2c-backward-consumer-audit.md`)

**Special downstream constraint (per governance JSON `downstream_dispatch_staggering_keyed`):** This story's close is the trigger for AMELIA-P3 staggering on 4 Wave-3 stories — `7c.9` / `7c.10` / `7c.11` / `7c.12` — all aliased to G2C. Those 4 must dispatch ≥30 min apart per AMELIA-P3.

---

## Story

As the dev-agent,
I want the legacy G2CCard (Slab 7a substrate; inherits from legacy `DecisionCard`) extended-and-migrated to inherit from `DecisionCardBase` AND add `gate_focus: Literal["pre_composition_qa"]` AND FR-7c-51 `schema_version` AND complete the four-file lockstep co-commit (regenerated schema + new shape-pin + new golden fixture),
So that G2C pre-composition QA gate conforms to the post-Slab-7c contract while preserving every backward-consumer access pattern AND unblocking AMELIA-P3 staggering for 4 Wave-3 G2C-aliased HIL surface stories.

---

## Predecessor / Dependency Context

- **7c.4b** (CLOSED 2026-05-05): provides `DecisionCardBase` substrate.
- **7c.5.G1** (in-progress as of 2026-05-05; CLOSE before this story dispatches): provides the canonical extend-and-audit pattern for body migration + the 2-class-regime compatibility surfaces. After G1 closes, `app/manifest/compiler.py:328` + `tests/unit/models/decision_cards/test_manifest_dotted_reference_resolver.py:47` + (possibly) `app/gates/resume_api.py:16-79` will already accept BOTH legacy `DecisionCard` AND new `DecisionCardBase`. **G2C T1 backward-consumer audit verifies the substrate accepts G2C specifically; T2 body extension is narrower than G1 because the 2-class-regime substrate is already in place.**
- **`app/models/decision_cards/_frozen_hashes.py`** (LANDED at G1 close): G2C pre-extension SHA256 = `237ce7d1b6c228cea5bc3653027cb40e50e40f316681a736d0692612dc7ba72a`. T2 verifies on-disk match.
- **Existing G2CCard legacy substrate:** `app/models/decision_cards/g2c.py` (33 LOC; gate_id=Literal["G2C"], readiness_status=Literal["ready","blocked"], blocking_issues=list[str], ready_nodes=list[str]; NO gate_focus field).
- **G2A canonical pattern:** `app/models/decision_cards/g2a.py` for fresh-author UUID4-typed + strip-then-non-empty validators.

---

## Acceptance Criteria

### AC-7c.5.G2C-A — Pre-T2 contract-diff + backward-consumer audit artifacts

**Given** the prior G2C contract is shipped at `app/models/decision_cards/g2c.py` with frozen-at-ship SHA256 already recorded in `_frozen_hashes.py`
**When** Codex executes T0/T1 deliverables
**Then** before T2 (extension) begins:

1. **`_bmad-output/implementation-artifacts/migration-7c-5-g2c-contract-diff.md`** is authored — diff-against-prior-contract artifact with sections (mirror G1's structure + AMELIA-P5 V6 amendment 2026-05-05):
   - §1 Legacy G2CCard field disposition matrix (gate_id / readiness_status / blocking_issues / ready_nodes — preserved-via-re-declaration)
   - §2 Legacy DecisionCard base field disposition. **AMELIA-P5 binding=hard:** every row MUST carry `audit_method: heavy|light` qualifier per `docs/dev-guide/migration-story-governance.json::extend_and_audit_t1_audit_method`. DROP rows REQUIRE `audit_method=heavy` with smoke-pass evidence against `tests/composition/` + `tests/integration/marcus/` + `tests/integration/replay/`. Schema: `| field | disposition | audit_method | rationale |`. Per G1 precedent, drafted_proposal + evidence + risks are candidate DROP rows — but per AMELIA-P5 each row's verdict requires smoke-pass evidence (G1's T6 reversal showed drafted_proposal + evidence had live consumers; G2C verifies these for itself).
   - §3 Legacy DecisionCardMeta field disposition (cache_state / affected_nodes / override_trail preserved; reject_rate / party_mode_contributions / consolidated_at / sanctum_warnings dropped per G1 precedent)
   - §4 New fields added: `schema_version: Literal["v1"]` (FR-7c-51) + `decision_card_digest` (inherited from `DecisionCardBase`) + **`gate_focus: Literal["pre_composition_qa"]`** (NEW; legacy G2CCard has NO gate_focus field — this is a contract-evolution add per ADR 0002 family-contract authoring target)
   - §5 Closed-enum tightening (gate_id remains `Literal["G2C"]`; readiness_status remains `Literal["ready", "blocked"]`; new `gate_focus` and `schema_version` Literals)
   - §6 Pattern-parity ratchets per G2A canonical (UUID4 typing on card_id/trial_id; `enforce_uuid4_version`; `enforce_tz_aware`; Field descriptions; inherited `frozen=True`)
   - §7 Net diff summary
2. **`_bmad-output/implementation-artifacts/migration-7c-5-g2c-backward-consumer-audit.md`** authored — per-call-site verdict for every G2CCard consumer (grep `G2CCard` exhaustively; expect ~20+ sites paralleling G1's 24 — `production_runner.py`, `m3_trial.py`, multiple unit tests, manifest validator, possibly `resume_api.py`).
3. **AMELIA-P4 frozen-hash delta-AC pre-check:** verify `_frozen_hashes.py` exists + contains G2C key = `237ce7d1b6c228cea5bc3653027cb40e50e40f316681a736d0692612dc7ba72a`. The file should already be present (landed at G1 T1). If missing or hash mismatch, HALT-AND-SURFACE.

**Cross-agent T1 review checkpoint:** Drop T1 READY notice at `_bmad-output/implementation-artifacts/_codex-handoff/7c-5-g2c.t1-ready.md`. HALT-AND-WAIT for cross-agent T1 review verdict at `_bmad-output/implementation-artifacts/7c-5-g2c-t1-cross-agent-review-2026-05-NN.md`. PASS unblocks T2.

### AC-7c.5.G2C-B — AMELIA-P4 frozen-hash delta-AC

**Given** `_frozen_hashes.py` records G2C SHA256 = `237ce7d1b6c228cea5bc3653027cb40e50e40f316681a736d0692612dc7ba72a`
**When** Codex begins T2
**Then** verify: `hashlib.sha256(open("app/models/decision_cards/g2c.py", "rb").read()).hexdigest() == FROZEN_AT_SHIP_HASHES["g2c"]`. Mismatch → HALT.

### AC-7c.5.G2C-C — Four-file lockstep co-commit (FR-7c-6 + FR-7c-7 + FR-7c-49)

Co-commit:
1. `app/models/decision_cards/g2c.py` — REWRITTEN: `class G2CCard(DecisionCardBase)`; preserved fields (readiness_status / blocking_issues / ready_nodes); ADDED `gate_focus: Literal["pre_composition_qa"]`; ADDED `schema_version: Literal["v1"]`; re-declared base fields per G2A canonical (card_id: UUID4, trial_id: UUID4, gate_id: Literal["G2C"], created_at, verb).
2. `app/models/decision_cards/schema/g2c.v1.schema.json` — REGENERATED.
3. `tests/parity/test_decision_card_g2c_shape.py` — NEW shape-pin (9-10 tests mirroring G2A pattern; closed-enum red-rejection on gate_id + gate_focus + readiness_status; JSON-Schema byte-match; golden round-trip; non-empty blocking_issues/ready_nodes if applicable; frozen mutation rejection). MUST `from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK` (AMEND-7d-i; bare import only).
4. `tests/fixtures/decision_cards/g2c_golden.json` — NEW deterministic golden fixture (`gate_id: "G2C"`, `gate_focus: "pre_composition_qa"`, `readiness_status: "ready"`, etc.).

### AC-7c.5.G2C-D — Backward-consumer non-regression

`pytest tests/parity/ tests/parametrized_harness/ tests/unit/ -p no:randomly -q` PASSES. Constructor sites (`production_runner.py`, `m3_trial.py`, `tests/unit/gates/_helpers.py` etc.) updated per audit verdicts. 2-class-regime substrate (compiler.py + dotted-ref-test + resume_api) already accepts both regimes post-G1 close — verify G2C is recognized.

### AC-7c.5.G2C-E — Class-conformance + Pydantic-v2 14-idiom conformance

Class-conformance count = T1-baseline + 1. 14-idiom checklist: same as G1 (inherited model_config + closed Literals + UUID4 typing + tz-aware + Field descriptions).

---

## Tasks / Subtasks (compact; mirror G1 structure)

- [ ] **T0 — Frozen-hash pre-check** (no file authoring; just verify g2c hash matches recorded value; G1 already authored `_frozen_hashes.py`)
- [ ] **T1 — Contract-diff + backward-consumer audit + T1-ready dropbox** (mirror G1 §T1 structure; ~50% the time of G1's T1 because `_frozen_hashes.py` already exists and 2-class-regime compatibility surfaces are already updated)
- [ ] **CROSS-AGENT T1 REVIEW CHECKPOINT** (binding HALT)
- [ ] **T2 — AMELIA-P4 frozen-hash verification + G2CCard rewrite** (inheritance migration to `DecisionCardBase`; preserve gate-specific fields; add gate_focus + schema_version; pattern-parity ratchets per G2A canonical)
- [ ] **T3 — Schema regeneration**
- [ ] **T4 — Golden fixture authoring**
- [ ] **T5 — Shape-pin authoring (with mandatory AMEND-7d-i AST-scan self-grep at T5.2)**
- [ ] **T6 — R-tier R3 verification battery (focused + AC-D backward-consumer + AMEND-7d-i AST-scan + smoke + R3 broad + class-conformance + lint-imports + sandbox-AC + ruff)**
- [ ] **T10 — Codex self-review dropbox**

---

## Required Readings (T1)

1. This story spec.
2. `_bmad-output/implementation-artifacts/migration-7c-4b-gate-family-foundation-implementation.md` (D1-D8).
3. **`_bmad-output/implementation-artifacts/migration-7c-5-g1-decision-card-extend-and-audit.md`** (canonical extend-and-audit predecessor; T1 deliverable patterns).
4. **`_bmad-output/implementation-artifacts/migration-7c-5-g1-contract-diff.md`** (canonical contract-diff structure to mirror).
5. **`_bmad-output/implementation-artifacts/migration-7c-5-g1-backward-consumer-audit.md`** (canonical backward-consumer audit structure; per-call-site verdict shape).
6. `_bmad-output/implementation-artifacts/7c-5-g1-code-review-2026-05-NN.md` (G1 T11 verdict — once landed; document any post-G1 patches that affect G2C).
7. `app/models/decision_cards/_base.py`.
8. `app/models/decision_cards/g2c.py` (LEGACY pre-extension; pre-extension SHA256 = `237ce7d1b6c228cea5bc3653027cb40e50e40f316681a736d0692612dc7ba72a`).
9. `app/models/decision_cards/g2a.py` (G2A canonical fresh-author pattern; UUID4 typing + strip-then-non-empty validators).
10. `app/models/decision_cards/g1.py` (POST-G1-close MIGRATED pattern; canonical extend-and-audit body shape).
11. `app/parity/contracts/tw_7c_3_firing.py` + `tests/structural/test_tw_7c_3_firing_spec_single_source.py`.
12. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (G2C = pre-composition QA gate).
13. `docs/dev-guide/pydantic-v2-schema-checklist.md`.
14. Governance JSON `7c-5-g2c` (extend_and_audit_t1_deliverables binding=hard; downstream_dispatch_staggering_keyed for 7c.9/10/11/12).

## Sandbox-AC validator status

Spec contains zero forbidden CLIs in dev-agent AC blocks. Sandbox-AC: PASS (verified at T0).

---

## Dispatch Hold

**HELD until G1 closes** (serial dispatch only; NOT concurrent with G3/G4 — all extend-and-audit stories share the legacy migration surface). After G1 closes, dispatch G2C alone.

At dispatch-time, Claude verifies AMELIA-P2 freshness + re-runs sandbox-AC.

## Cross-agent T1 review checkpoint (NEW pattern for extend-and-audit; same as G1)

Two Claude review checkpoints:
1. **Pre-T2 cross-agent T1 review** — Claude reads contract-diff + backward-consumer audit + frozen-hash artifacts BEFORE T2.
2. **Post-T9 standard T11 review** — Claude reads body extension + verification battery results.

Both must PASS before commit + flip done.

## Downstream impact

After 7c.5.G2C closes, four Wave-3 HIL stories unblock simultaneously: **7c.9 / 7c.10 / 7c.11 / 7c.12** (G2C-aliased per ADR 0002 §2). AMELIA-P3 staggering applies — those four MUST dispatch ≥30 min apart per governance JSON. Plan dispatch sequence ahead of G2C close.
