# Migration Story 7c.5.G3: G3 DecisionCard Extend-and-Audit (Motion-Clip Approval)

**Status:** ready-for-dev *(spec authored 2026-05-05 lookahead_tier=2 author-skeleton-ahead; predecessor 7c.4b CLOSED at `8b12970`; siblings G0+G2A CLOSED at `e2aa599`; G5+G6 CLOSED at `f059e84`; G1 in-progress 2026-05-05; G2C also pre-authored at lookahead_tier=2. **DISPATCH HELD until G2C closes** — extend-and-audit chain is SERIAL only; G3 dispatches third in the chain.)*
**Sprint key:** `migration-7c-5-g3-decision-card-extend-and-audit`
**Epic:** Slab 7c — Marcus Orchestrational Tail (`migration-epic-slab-7c-orchestrational-tail`)
**Pts:** 2
**K-target:** 1.4×
**Estimated LOC:** ~350 (g3.py rewrite ~80 + schema regen ~50 + new shape-pin ~120 + new golden ~40 + contract-diff artifact ~80 + backward-consumer-audit artifact ~50 + __init__.py)
**Gate-mode:** **`dual-gate-cross-agent-CONTRACT-EVOLUTION`** (NAMED gate-mode per Winston W3)
**Cross-agent review:** false — T11 standard tier (the "cross-agent" component refers to T1 PRE-T2 cross-agent review)
**R-tier:** R3
**T11-tier:** standard
**Lookahead-tier:** 2
**files_touched:** 3 modified (`g3.py`, `schema/g3.v1.schema.json`, `__init__.py`) + 4 new (`tests/parity/test_decision_card_g3_shape.py`, `tests/fixtures/decision_cards/g3_golden.json`, `_bmad-output/implementation-artifacts/migration-7c-5-g3-contract-diff.md`, `_bmad-output/implementation-artifacts/migration-7c-5-g3-backward-consumer-audit.md`)

**Semantic alignment note (REQUIRED at T1 contract-diff §1):** ADR 0002 §1 designates G3 as "motion-clip approval gate" but the legacy G3Card fields (`progress_percent`, `active_node_id`, `pending_nodes`, `operator_prompt`) describe mid-trial in-flight operator review. T1 contract-diff §1 MUST address this semantic divergence: are the legacy fields preserved verbatim (under the broader "motion-clip approval" umbrella the operator decides on at-the-moment of motion-clip review) OR is the legacy semantic preserved with `gate_focus="motion_clip_approval"` reflecting the family-contract authoring intent. **Recommended Codex T1 verdict:** preserve legacy fields verbatim (no operator-facing field renames; backward consumers continue to function); add `gate_focus="motion_clip_approval"` per ADR 0002 to align with the post-Slab-7c family taxonomy. Operator semantic alignment refinements deferred to a future story (filed as a deferred-inventory follow-on at G3 close if needed).

---

## Story

As the dev-agent,
I want the legacy G3Card (Slab 7a substrate; mid-trial in-flight review fields) extended-and-migrated to inherit from `DecisionCardBase` AND add `gate_focus: Literal["motion_clip_approval"]` per ADR 0002 family-contract authoring target AND FR-7c-51 `schema_version` AND complete the four-file lockstep co-commit,
So that G3 motion-clip approval gate conforms to the post-Slab-7c contract while preserving every backward-consumer access pattern AND establishes the semantic alignment seam (legacy mid-trial fields preserved; family-contract focus marker added).

---

## Predecessor / Dependency Context

- **7c.4b** (CLOSED 2026-05-05): provides `DecisionCardBase`.
- **7c.5.G1** (in-progress; CLOSE before G2C; G2C closes before G3): provides canonical extend-and-audit pattern + 2-class-regime compatibility substrate already in place.
- **7c.5.G2C** (pre-authored at lookahead_tier=2; CLOSE before this story): provides the canonical extend-and-audit pattern for stories where the legacy gate has NO `gate_focus` field and the post-Slab-7c migration ADDS one. G3 follows the same pattern.
- **`app/models/decision_cards/_frozen_hashes.py`**: G3 pre-extension SHA256 = `bcfe2865df5e7071cf43ada563e29a8b6fc5dfa1cb3abdf99f78fa5d2d0fddf3`. T2 verifies on-disk match.
- **Existing G3Card legacy substrate:** `app/models/decision_cards/g3.py` (41 LOC; gate_id=Literal["G3"], progress_percent=float [0.0, 100.0], active_node_id=str (min_length=1), pending_nodes=list[str], operator_prompt=str; NO gate_focus field).
- **ADR 0002 §1 G3 row:** "Motion-clip approval gate. Already shipped; extend-and-audit in 7c.5.G3."

---

## Acceptance Criteria

### AC-7c.5.G3-A — Pre-T2 contract-diff + backward-consumer audit artifacts

**Then** before T2 begins:

1. **`migration-7c-5-g3-contract-diff.md`** authored with 7 sections mirroring G1 + G2C (+ AMELIA-P5 V6 amendment 2026-05-05):
   - §1 Legacy G3Card field disposition (preserved-via-re-declaration: gate_id, progress_percent with bounds [0.0, 100.0], active_node_id non-empty, pending_nodes default empty list, operator_prompt strip-then-non-empty per G2A pattern). **PLUS the semantic alignment statement per spec metadata above** — explicit verdict that legacy mid-trial fields are preserved verbatim under the broader "motion-clip approval" gate_focus marker, with operator semantic refinement deferred.
   - §2 Legacy DecisionCard base field disposition. **AMELIA-P5 binding=hard:** every row MUST carry `audit_method: heavy|light` qualifier per `docs/dev-guide/migration-story-governance.json::extend_and_audit_t1_audit_method`. DROP rows REQUIRE `audit_method=heavy` with smoke-pass evidence against `tests/composition/` + `tests/integration/marcus/` + `tests/integration/replay/`. Schema: `| field | disposition | audit_method | rationale |`. Per G1 precedent, drafted_proposal + evidence + risks are candidate DROP rows — but per AMELIA-P5 each row's verdict requires smoke-pass evidence (G1 saw drafted_proposal + evidence reversed at T6; G3 verifies for itself).
   - §3 Legacy DecisionCardMeta field disposition (mirror G1/G2C)
   - §4 New fields added: `schema_version: Literal["v1"]` + `decision_card_digest` (inherited) + **`gate_focus: Literal["motion_clip_approval"]`** (NEW per ADR 0002)
   - §5 Closed-enum tightening (gate_id Literal["G3"] retained; new gate_focus + schema_version Literals)
   - §6 Pattern-parity ratchets (UUID4 + enforce_uuid4_version + enforce_tz_aware + strip-then-non-empty on `operator_prompt` + `active_node_id` + Field descriptions)
   - §7 Net diff summary
2. **`migration-7c-5-g3-backward-consumer-audit.md`** authored — per-call-site verdict for every G3Card consumer (grep `G3Card` exhaustively).
3. **AMELIA-P4 frozen-hash delta-AC pre-check:** verify G3 hash in `_frozen_hashes.py` matches `bcfe2865df5e7071cf43ada563e29a8b6fc5dfa1cb3abdf99f78fa5d2d0fddf3`.

**Cross-agent T1 review checkpoint:** Drop T1 READY notice at `_codex-handoff/7c-5-g3.t1-ready.md`. HALT-AND-WAIT.

### AC-7c.5.G3-B — AMELIA-P4 frozen-hash delta-AC

At T2 start, observed `g3.py` SHA256 == `FROZEN_AT_SHIP_HASHES["g3"]`. Mismatch → HALT.

### AC-7c.5.G3-C — Four-file lockstep co-commit

Co-commit:
1. `app/models/decision_cards/g3.py` — REWRITTEN: `class G3Card(DecisionCardBase)`; preserved fields (progress_percent with `Field(..., ge=0.0, le=100.0)`; active_node_id with strip-then-non-empty validator; pending_nodes with default empty list; operator_prompt with strip-then-non-empty); ADDED `gate_focus: Literal["motion_clip_approval"]`; ADDED `schema_version: Literal["v1"]`; re-declared base fields per G2A canonical.
2. `app/models/decision_cards/schema/g3.v1.schema.json` — REGENERATED.
3. `tests/parity/test_decision_card_g3_shape.py` — NEW shape-pin (10-11 tests; field-presence + closed-enum on gate_id + gate_focus + JSON-Schema byte-match + golden round-trip + progress_percent boundary tests [0.0, 100.0, -0.1, 100.1] + non-empty active_node_id + strip-then-non-empty operator_prompt + frozen mutation rejection). MUST import LOCKSTEP_CHECK only (AMEND-7d-i).
4. `tests/fixtures/decision_cards/g3_golden.json` — NEW deterministic golden (`gate_id: "G3"`, `gate_focus: "motion_clip_approval"`, `progress_percent: 50.0`, etc.).

### AC-7c.5.G3-D — Backward-consumer non-regression

Mirror G1/G2C. Constructor sites updated; 2-class-regime substrate already accepts G3Card via DecisionCardBase post-G1.

### AC-7c.5.G3-E — Class-conformance + Pydantic-v2 14-idiom + bounds validators

T1-baseline + 1. 14-idiom + bounds preservation: `Field(..., ge=0.0, le=100.0)` on `progress_percent` (Pydantic-native validation; preserve from legacy).

---

## Tasks / Subtasks (compact; mirror G1+G2C)

- [ ] **T0 — Frozen-hash pre-check** (verify g3 hash matches recorded)
- [ ] **T1 — Contract-diff (with §1 semantic alignment statement) + backward-consumer audit + T1-ready dropbox**
- [ ] **CROSS-AGENT T1 REVIEW CHECKPOINT** (binding HALT)
- [ ] **T2 — AMELIA-P4 verification + G3Card rewrite** (preserve progress_percent bounds; add gate_focus + schema_version; pattern-parity ratchets)
- [ ] **T3 — Schema regeneration**
- [ ] **T4 — Golden fixture authoring**
- [ ] **T5 — Shape-pin authoring (mandatory AMEND-7d-i AST-scan self-grep at T5.2; INCLUDE progress_percent boundary tests at 0.0 / 100.0 / -0.1 / 100.1)**
- [ ] **T6 — R-tier R3 verification battery**
- [ ] **T10 — Codex self-review dropbox**

---

## Required Readings (T1)

1. This story spec (note semantic alignment requirement).
2. `_bmad-output/implementation-artifacts/migration-7c-5-g1-decision-card-extend-and-audit.md` (canonical extend-and-audit spec).
3. `_bmad-output/implementation-artifacts/migration-7c-5-g2c-decision-card-extend-and-audit.md` (predecessor extend-and-audit; canonical pattern for ADD-gate_focus migration).
4. `_bmad-output/implementation-artifacts/migration-7c-5-g1-contract-diff.md` AND `migration-7c-5-g2c-contract-diff.md` (canonical contract-diff structures).
5. `_bmad-output/implementation-artifacts/migration-7c-5-g1-backward-consumer-audit.md` AND `migration-7c-5-g2c-backward-consumer-audit.md`.
6. `_bmad-output/implementation-artifacts/7c-5-g1-code-review-2026-05-NN.md` AND `7c-5-g2c-code-review-2026-05-NN.md` (predecessor T11 verdicts; document any patches affecting G3).
7. `app/models/decision_cards/_base.py` + `g3.py` (LEGACY) + `g2a.py` (canonical fresh-author) + `g1.py` (canonical extend-and-audit migrated body — post-G1).
8. `app/parity/contracts/tw_7c_3_firing.py` + `tests/structural/test_tw_7c_3_firing_spec_single_source.py`.
9. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (G3 = motion-clip approval gate; semantic alignment).
10. `docs/dev-guide/pydantic-v2-schema-checklist.md`.
11. Governance JSON `7c-5-g3` (extend_and_audit_t1_deliverables binding=hard).

## Sandbox-AC validator status

Spec contains zero forbidden CLIs in dev-agent AC blocks. Sandbox-AC: PASS (verified at T0).

---

## Dispatch Hold

**HELD until G2C closes** (serial dispatch only; G3 is third in the extend-and-audit chain after G1 → G2C → G3).

At dispatch-time, Claude verifies AMELIA-P2 freshness.

## Cross-agent T1 review checkpoint (same as G1/G2C)

Two Claude review checkpoints: PRE-T2 + POST-T9. Both must PASS before commit + flip done.
