# PRE-T2 Cross-Agent T1 Review — Story 7c.5.G1 (G1 DecisionCard Extend-and-Audit)

**Story key:** `migration-7c-5-g1-decision-card-extend-and-audit`
**Reviewer:** Claude (Opus 4.7) — cross-agent T1 review (NEW pattern per Winston W3 Round-2 party-mode 2026-05-04)
**Review date:** 2026-05-05
**Stage:** PRE-T2 — Codex HALTED at end of T1 awaiting verdict

---

## Verdict: **PASS — Codex MAY proceed to T2**

All three T1 deliverables are present, complete, and structurally sound. Backward-consumer audit surfaced critical scope refinement (2-class-regime validator updates at `app/manifest/compiler.py:328` + `app/gates/resume_api.py:16-79` + `tests/unit/models/decision_cards/test_manifest_dotted_reference_resolver.py:47`) that was NOT pre-enumerated in the spec — this is the cross-agent T1 review pattern doing exactly what Winston W3 designed it to do: catch scope adjacencies before T2 sinks effort into a too-narrow body extension.

No MUST-FIX. No SHOULD-FIX. Codex is unblocked.

---

## Verification battery

| Check | Status | Evidence |
|---|---|---|
| Frozen-hash file authored at `app/models/decision_cards/_frozen_hashes.py` | ✅ PASS | 13 LOC; all 4 gates (g1/g2c/g3/g4) recorded |
| G1 hash matches spec-recorded value | ✅ PASS | `4fe0e985d2285e3219b103424765dec009043564960ec43af1fb5710d2a1a196` matches |
| All 4 hashes verified byte-for-byte against on-disk files | ✅ PASS | Re-computed via `hashlib.sha256(open(...))`: g1/g2c/g3/g4 all match |
| Contract-diff artifact authored at `migration-7c-5-g1-contract-diff.md` | ✅ PASS | 84 LOC; 7 sections covering all spec AC-A bullet 1 requirements |
| Backward-consumer audit at `migration-7c-5-g1-backward-consumer-audit.md` | ✅ PASS | 76 LOC; 24 executable + 3 non-grep + 4 doc references |
| T1 READY notice at `_codex-handoff/7c-5-g1.t1-ready.md` | ✅ PASS | Lists all three deliverable paths + per-deliverable summary |
| Class-conformance baseline | ✅ PASS | 15 (11 activation + 4 decision-card shape-pin per Codex T1 poll) |
| Sandbox-AC validator | ✅ PASS | Codex T1 ran; PASS |
| Legacy `app/models/decision_cards/g1.py` UNMODIFIED at T1 | ✅ PASS | Codex correctly defers body changes to T2 |

---

## Contract-diff artifact verification

§1 (Legacy G1Card field disposition): ✅ All 11 legacy fields enumerated with disposition + rationale. `card_id` / `trial_id` / `created_at` / `verb` / `meta` correctly identified as re-declared (not inherited) since new `DecisionCardBase` is slimmer than legacy `DecisionCard`. Pattern-replication mirrors G2A canonical.

§2 (Legacy DecisionCard base field disposition): ✅ All 9 legacy base behaviors enumerated. `drafted_proposal`, `evidence`, `risks` correctly marked DROP with explicit verdict "no audited consumer reads after construction." `model_config.frozen=False` correctly migrated to `frozen=True` via `DecisionCardBase` (intentional 7c pattern; shape-pin must assert frozen mutation rejection).

§3 (Legacy DecisionCardMeta field disposition): ✅ All 7 legacy meta fields enumerated. `cache_state` / `affected_nodes` / `override_trail` preserved via new `_base.DecisionCardMeta`. `reject_rate` / `party_mode_contributions` / `consolidated_at` / `sanctum_warnings` dropped with explicit consumer-verdict for each.

§4 (New fields added): ✅ `schema_version: Literal["v1"]` (FR-7c-51) + `decision_card_digest: str` (inherited from `DecisionCardBase`). Both correctly identified.

§5 (Closed-enum tightening): ✅ `gate_id` + `gate_focus` retained as Literal; `schema_version` newly added as Literal["v1"]. Triple-layer rejection preserved.

§6 (Pattern-parity ratchets): ✅ All six G2A-canonical idioms enumerated for T2 compliance: UUID4 typing + `enforce_uuid4_version` + `enforce_tz_aware` + strip-then-non-empty validators on `trial_summary`/`opened_by` + Field descriptions + inherited model_config from `DecisionCardBase`.

§7 (Net diff summary): ✅ Added/preserved-by-re-declaration/preserved-via-base/dropped lists complete + required T2 consumer updates explicitly enumerated (constructor sites + manifest validator).

**One ambiguity flagged (NOT MUST-FIX):** §1 row for `meta` says "preserve via `DecisionCardBase.meta`, but migrate to `_base.DecisionCardMeta`." Wording is slightly redundant — `DecisionCardBase` ALREADY types `meta` as the new `_base.DecisionCardMeta`, so G1 just inherits naturally; no re-declaration needed. Intent is clear; T2 implementation should NOT re-declare meta on G1Card.

---

## Backward-consumer audit verification

**Strong:** Audit identified consumers spec did NOT pre-enumerate:

1. **`app/manifest/compiler.py:328`** — `resolve_dotted_ref(..., expected_base_class=DecisionCard)` validates every decision-card schema ref as legacy `DecisionCard` subclass. Under the 2-class regime, this MUST accept BOTH legacy `DecisionCard` (for G2C/G3/G4 still on legacy) AND new `DecisionCardBase` (for migrated G1). **This is a critical scope-adjacency catch.** T2 will need to update the validator's `expected_base_class` parameter to a union/protocol.

2. **`app/gates/resume_api.py:16-79`** — registry/digest API typed to legacy `DecisionCard`. If migrated G1 registers through this API, the type signature needs widening. Codex correctly used conditional language ("if migrated G1 is registered") rather than asserting; T2 verifies whether the registration path is actually exercised for G1.

3. **`tests/unit/models/decision_cards/test_manifest_dotted_reference_resolver.py:47`** — asserts every G1/G2C/G3/G4 dotted ref is subclass of legacy `DecisionCard`. Test must be updated to accept 2-class regime.

These three together constitute the **2-class-regime compatibility surface** that the migration must preserve. Codex's per-site verdict is precise.

**Field-access summary (audit §Field-Access Summary):** No audited site reads `G1Card.drafted_proposal` / `evidence` / `risks` / legacy meta extensions directly. Constructor sites pass these fields (production_runner:411, m3_trial:146, _helpers:12). T2 update surface is therefore narrow: 3 constructor payload updates + 3 2-class-regime validator updates.

**Documentation references:** 4 sites flagged as `requires-deferred-followon` (no executable break). Operator-trial playbook + sources-of-truth doc updates can be a separate documentation-refresh follow-on after all G1-G4 migrations close.

---

## Frozen-hash file verification

```
g1  4fe0e985d2285e3219b103424765dec009043564960ec43af1fb5710d2a1a196  ✅ matches Codex record
g2c 237ce7d1b6c228cea5bc3653027cb40e50e40f316681a736d0692612dc7ba72a  ✅ matches Codex record
g3  bcfe2865df5e7071cf43ada563e29a8b6fc5dfa1cb3abdf99f78fa5d2d0fddf3  ✅ matches Codex record
g4  98536d2ab845972f96e8d374b08bb3929fb8d02024cbc56616c90424061c6b5a  ✅ matches Codex record
```

All four hashes computed independently via `.venv/Scripts/python.exe -c "hashlib.sha256(...)"` and match Codex's recorded values byte-for-byte. AMELIA-P4 frozen-hash baseline is established. The future stories 7c.5.G2C/G3/G4 will consume the same `_frozen_hashes.py` file and verify their own gates' hashes at their respective T2 starts.

---

## T2 scope acknowledgment

Codex MUST address the following at T2 (per the audit):

**Constructor payload updates (drop legacy fields + add `decision_card_digest`):**
- `app/marcus/orchestrator/production_runner.py:411`
- `marcus/orchestrator/m3_trial.py:146`
- `tests/unit/gates/_helpers.py:12`

**2-class-regime compatibility updates (accept BOTH legacy DecisionCard AND DecisionCardBase):**
- `app/manifest/compiler.py:328` — `expected_base_class` parameter
- `tests/unit/models/decision_cards/test_manifest_dotted_reference_resolver.py:47` — assertion update
- `app/gates/resume_api.py:16-79` — IF G1 registers through this API (T2 verifies)

**Documentation:** Defer to documentation-refresh follow-on after all 4 extend-and-audit stories close. Add to `_bmad-output/planning-artifacts/deferred-inventory.md` named-but-not-filed at story close.

---

## Sign-off

PRE-T2 cross-agent T1 review complete. **Codex unblocked. Resume T2.**

T2 scope is broader than initially specified (3 additional 2-class-regime compatibility surfaces) but the spec's K-target=1.4× / pts=2 / R-tier=R3 budget accommodates this. If T2 effort meaningfully exceeds the 1.4× ceiling per `docs/dev-guide/story-cycle-efficiency.md`, surface to Claude at T6 for K-budget extension consideration before T9.

Standard T11 review at end of T9 will verify all backward-consumer audit verdicts honored + frozen-hash AMELIA-P4 delta-AC + Pydantic-v2 14-idiom + the six PARALLEL-DISPATCH GUARDRAILS (#1, #2, #4, #5, #6 universally; #3 informational under serial dispatch).
