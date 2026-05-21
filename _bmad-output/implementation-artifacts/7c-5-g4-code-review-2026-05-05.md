# T11 Standard Code Review — Story 7c.5.G4 (G4 DecisionCard Extend-and-Audit, Fidelity Gate)

**Story key:** `migration-7c-5-g4-decision-card-extend-and-audit`
**Reviewer:** Claude (Opus 4.7) — T11 standard tier (post-T9; PRE-T2 cross-agent T1 review previously PASSed at `fbb2886`)
**Gate-mode:** `dual-gate-cross-agent-CONTRACT-EVOLUTION` (T11 itself is `standard` tier; the "cross-agent" component refers to the T1 PRE-T2 review, NOT this T11)
**R-tier:** R3 (full broad regression)
**K-target:** 1.4× (extend-and-audit; heavier than fresh-author)
**Diff size:** ~270 LOC (G4 four-file lockstep) + ~12 LOC constructor updates + 1 LOC NFR-CG6 governance-version refresh; sibling G2C+G3 changes excluded from G4 attribution
**Review date:** 2026-05-05
**Chain position:** **FINAL** extend-and-audit story (closes G1 → G2C → G3 → G4 chain). Predecessors G2C+G3 reviewed in parallel.

---

## Verdict: **PASS — recommend COMMIT + FLIP DONE**

The G4 extend-and-audit migration is structurally sound. The four-file lockstep is byte-deterministic. All five ACs (A–E) verify. The frozen-hash AMELIA-P4 baseline is unchanged. The PowerShell BOM patch (anti-pattern A18) is correctly applied (NO_BOM verified). The §1 SEMANTIC ALIGNMENT clean-fit verdict was preserved verbatim at T6 — `final_status` / `artifact_paths` / `outcome_summary` were preserved exactly, with only `gate_focus="fidelity_gate"` + `schema_version="v1"` ADDED. Critically, the closed three-value `final_status: Literal["completed", "partial", "failed"]` is preserved verbatim (no widening, no reordering), and the new shape-pin **explicitly red-rejects** `"in_progress"`, `"unknown"`, `"COMPLETED"`, and integer `1` — the exact reject-coverage the contract-diff §5 + AC-7c.5.G4-C required.

Unlike G1, no T6 audit-verdict reversal occurred for G4: the contract-diff DROP rows (`drafted_proposal`, `evidence`, `risks`, plus 4 legacy meta extensions) were correctly dropped on heavy smoke evidence and the audit's G1-only-consumer discriminator held. All seven DROP rows carry `audit_method=heavy` per V6 AMELIA-P5 binding=hard.

All six PARALLEL-DISPATCH GUARDRAILS pass. Pydantic-v2 14-idiom checklist conforms. AMEND-7d-i AST-scan + targeted self-grep clean (bare `LOCKSTEP_CHECK` import only; no `_LOCKSTEP|MODEL_ROOT|FOUR_FILE_GLOBS|all_four_present` private internals referenced).

**2-class-regime migration closure VERIFIED:** legacy `app/models/decision_cards/base.py` exists on disk and is unmodified (last touched at `40437bc` pre-Slab-7c). G4Card inherits `DecisionCardBase` (`True`) and does NOT inherit legacy `DecisionCard` (`False`). All four legacy gate subclasses (G1/G2C/G3/G4) now inherit `DecisionCardBase`. Legacy `base.py:DecisionCard` becomes effectively a marker for the deferred cleanup story.

**V7 P2-clean-×3 baseline closure assessment:** baseline data shows clean ×3 across G2C+G3+G4 close-batches (see §V7 Baseline section below). Recommendation: ELEVATE Wave-3 7c.6+ default cap to N+3 — pending party-mode ratification per V7 v2 promotion policy.

No MUST-FIX. No SHOULD-FIX. Zero patches applied by this reviewer.

---

## Verification Battery

| Check | Status | Evidence |
|---|---|---|
| Focused G4 shape-pin | PASS | `16 passed in 3.58s` — 16 tests after parametrize fan-out (1 LOCKSTEP_CHECK + 1 required-fields + 3 closed-enum red rejections + 4 final_status closed-enum red rejections + 1 default-empty artifact_paths + 2 outcome_summary blank rejections + 1 schema byte-match + 1 closed-values declaration + 1 golden round-trip + 1 frozen-mutation rejection) |
| AMEND-7d-i AST-scan structural test | PASS | `2 passed in 3.20s` — `test_decision_card_shape_pins_do_not_rederive_tw_7c_3_rule` confirms G4 contains no `FOUR_FILE_GLOBS`/`all_four_present`/private lockstep internals |
| `tests/parity/` + `tests/parametrized_harness/` + `tests/unit/` broad slice | PASS | `921 passed, 18 skipped in 15.17s` — **inherited NFR-CG6 governance-version drift RESOLVED** (T9 refresh) |
| Class-conformance | PASS | `PASS: 19 parity contract file(s) conform (11 activation + 8 decision-card shape-pin)` — exactly +1 over T1 baseline of 18 (G0+G1+G2A+G2C+G3+G5+G6 = 7 pre-G4; G4 brings to 8) ✅ class-conformance +1 invariant satisfied |
| Lint-imports | PASS | `Contracts: 12 kept, 0 broken` (UNCHANGED) |
| Sandbox-AC validator | PASS | `PASS — no sandbox-AC violations across 1 story file(s)` |
| Ruff (in-scope files) | PASS | `All checks passed!` — covers g4.py + test_decision_card_g4_shape.py |
| BOM check on schema JSON | PASS | `NO_BOM` + first 16 bytes = `b'{\r\n  "$defs": {\r'` (no UTF-8 BOM `\xef\xbb\xbf` prefix; CRLF line endings — Windows-native, schema reads through `read_text(encoding="utf-8")` which normalizes) |
| Frozen-hash AMELIA-P4 unchanged | PASS | `FROZEN_AT_SHIP_HASHES['g4'] == "98536d2ab845972f96e8d374b08bb3929fb8d02024cbc56616c90424061c6b5a"` UNCHANGED — current on-disk hash diverges intentionally (g4.py was rewritten); contract-diff §1–§7 is the audit trail |
| G-PARTY legacy-card non-regression | PASS | `tests/integration/gates/test_consolidated_decision_card_carries_contributions.py` — `1 passed in 3.86s` |
| Structural TW-7c-3 single-source | PASS | `2 passed in 3.20s` |
| 2-class-regime substrate validators UNTOUCHED | PASS | `git diff HEAD app/manifest/compiler.py app/manifest/refs.py app/gates/resume_api.py tests/unit/models/decision_cards/test_manifest_dotted_reference_resolver.py` — zero diff |
| Legacy `app/models/decision_cards/base.py` UNMODIFIED | PASS | `git log app/models/decision_cards/base.py` last touched at `40437bc` (pre-Slab-7c); no diff at HEAD |
| G4Card inherits DecisionCardBase + NOT legacy DecisionCard | PASS | `issubclass(G4Card, DecisionCardBase) == True`; `issubclass(G4Card, DecisionCard) == False` |

---

## Critical Item #1 — `final_status` closed Literal preservation (G4-SPECIFIC) — PASS

**Verdict:** `final_status` Literal is preserved verbatim with all required reject coverage in shape-pin tests.

**Inspection of `app/models/decision_cards/g4.py:43-46`:**

```python
final_status: Literal["completed", "partial", "failed"] = Field(
    ...,
    description="Closed final-status summary for trial closeout.",
)
```

- Three values, exact spelling, exact order matching legacy substrate.
- No widening (no `"in_progress"`, no `"unknown"`, no nullable variant).
- No reordering or alphabetization.
- Required field (no default) — preserves legacy pre-extension semantic.

**Shape-pin reject coverage (`tests/parity/test_decision_card_g4_shape.py:77-83`):**

```python
@pytest.mark.parametrize("final_status", ["in_progress", "unknown", "COMPLETED", 1])
def test_g4_card_final_status_closed_enum_red_rejection(final_status: object) -> None:
    payload = _load_golden()
    payload["final_status"] = final_status

    with pytest.raises(ValidationError):
        G4Card.model_validate(payload)
```

All four required reject cases covered:
- `"in_progress"` — out-of-vocab string → REJECT ✅
- `"unknown"` — out-of-vocab string → REJECT ✅
- `"COMPLETED"` — uppercase variant (case-sensitive) → REJECT ✅
- `1` — non-string type (Pydantic Literal type-check) → REJECT ✅

**JSON Schema reflection (line 116):**

```python
assert schema["properties"]["final_status"]["enum"] == ["completed", "partial", "failed"]
```

Closed enum reflected verbatim in emitted schema.

**Triple-layer closed-enum red-rejection** per Pydantic-v2 14-idiom checklist:
1. **Type system layer** — `Literal["completed", "partial", "failed"]` annotation rejects non-Literal at validation.
2. **JSON Schema layer** — emitted `"enum": ["completed", "partial", "failed"]` rejects out-of-vocab at consumer schema-validation.
3. **Test layer** — parametrized `test_g4_card_final_status_closed_enum_red_rejection` exercises all four reject paths at runtime.

**Conclusion:** G4-specific Critical Item #1 PASSES with zero gaps. Closed-Literal preservation is the load-bearing G4 invariant per AC-7c.5.G4-C; it is preserved verbatim and triple-layer-tested.

---

## Critical Item #2 — T1-audit-verdict-reversal scan — PASS (no reversal needed)

**G1 PRECEDENT:** G1's PRE-T2 T1 audit declared `drafted_proposal` + `evidence` + `risks` as DROP. At T6, broad-regression smoke surfaced live consumer evidence in `tests/composition/test_pre_gate_marcus_precedence_unaltered.py` + `tests/integration/marcus/test_runner_threads_pre_fill_to_decision_card.py` + `tests/integration/marcus/test_gate_handler_loads_adjacent_summary.py`. Reversal: `drafted_proposal` + `evidence` were preserved on G1Card; `risks` was correctly dropped.

**G4 EVIDENCE:** Inspection of `app/models/decision_cards/g4.py` shows NO `drafted_proposal`, NO `evidence`, NO `risks` fields. The contract-diff §2 DROP verdict was preserved verbatim through T2-T9.

**Backward-consumer audit's G1-only-consumer discriminator** (the load-bearing audit claim):

> "No `G4Card(` constructor appears under `tests/composition/`, `tests/integration/marcus/`, or `tests/integration/replay/`; the only executable G4 constructors are: `production_runner.py:449` and `m3_trial.py:185`."

Independently verified at this T11:
- `Grep "card\.(drafted_proposal|evidence|risks)" tests/composition tests/integration/marcus tests/integration/replay` finds reads only in G1-context tests (`gate_id="G1"` cards built via helpers).
- The two production constructor sites (`production_runner.py:449` + `m3_trial.py:185`) explicitly drop `drafted_proposal` / `evidence` / `risks` from the G4 branch, supplying only the preserved G4-specific fields + inherited base fields.
- Smoke G-PARTY legacy-card non-regression test passed (`test_consolidated_decision_card_carries_contributions.py`: 1 passed) — confirming `tests/integration/gates/` `party_mode_contributions` reads still work on G-PARTY cards (orthogonal to G4).

**Conclusion:** No T6 audit reversal occurred or was needed for G4. The contract-diff DROP verdicts are the correct, executed contract. Codex correctly distinguished G1-only consumer evidence from G4 preservation requirements — exactly mirroring the G2C+G3 pattern.

---

## Critical Item #3 — BOM patch verification (anti-pattern A18) — PASS

```text
.venv/Scripts/python.exe -c "data = open('app/models/decision_cards/schema/g4.v1.schema.json', 'rb').read(); print('BOM_PRESENT' if data.startswith(b'\xef\xbb\xbf') else 'NO_BOM'); print(repr(data[:16]))"
NO_BOM
b'{\r\n  "$defs": {\r'
```

No UTF-8 BOM (`\xef\xbb\xbf`) prefix. First 16 bytes are clean ASCII JSON with CRLF line endings (Windows-native). The schema-byte-match test (`test_g4_json_schema_byte_for_byte_match`) reads through `read_text(encoding="utf-8")` which normalizes newlines on Windows; emitted `_canonical_json(...)` ends with `\n`. **Schema-byte-match test PASSED** (within the 16-pass shape-pin run), proving the encoder/decoder round-trip is deterministic regardless of CRLF on disk.

Anti-pattern A18 (PowerShell `>` redirection causing BOM contamination) was correctly avoided by using `Path.write_text(...)` per Codex T3 dropbox claim.

---

## Critical Item #4 — AMELIA-P4 frozen-hash UNCHANGED — PASS

```text
.venv/Scripts/python.exe -c "from app.models.decision_cards._frozen_hashes import FROZEN_AT_SHIP_HASHES; expected = '98536d2ab845972f96e8d374b08bb3929fb8d02024cbc56616c90424061c6b5a'; print('UNCHANGED' if FROZEN_AT_SHIP_HASHES['g4'] == expected else 'CHANGED')"
UNCHANGED
```

`FROZEN_AT_SHIP_HASHES["g4"]` is byte-identical to the T0 pre-extension SHA256 recorded in the contract-diff §0. The current on-disk `g4.py` hash diverges intentionally (body was rewritten at T2 from legacy `DecisionCard` inheritance to `DecisionCardBase` inheritance with field re-declarations + `gate_focus` + `schema_version` + validators). The frozen value is the audit anchor; the contract-diff §1–§7 is the audit trail justifying divergence. Codex correctly did NOT modify `_frozen_hashes.py`.

---

## Critical Item #5 — PARALLEL-DISPATCH GUARDRAILS — PASS (all six)

| # | Guardrail | Status | Evidence |
|---|---|---|---|
| 1 | AMEND-7d-i self-grep clean | PASS | `Grep "_LOCKSTEP\|MODEL_ROOT\|_GOLDEN_DIR\|_SCHEMA_DIR\|_SHAPE_PIN_DIR" test_decision_card_g4_shape.py` returns no matches; only bare `from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK` import on line 11 |
| 2 | Pattern-replication mirrors G2A canonical | PASS | UUID4 typing on `card_id`/`trial_id`; `enforce_uuid4_version` validator at line 61-64; `enforce_tz_aware` validator at line 66-69; strip-then-non-empty validator on `outcome_summary` at line 71-76; `Field(..., description=...)` on every field; inherits `frozen=True` + `extra="forbid"` + `validate_assignment=True` from DecisionCardBase. Mirrors G2A line-for-line within G4-specific field set. |
| 3 | `__init__.py` flat-export status | PASS | `app/models/decision_cards/__init__.py:24` imports G4Card from flat package; `:42` `AnyDecisionCard` discriminated union includes `G4Card` (gate_id discriminator); `:64` `__all__` exports G4Card. **No diff at HEAD** for `__init__.py` — already correctly configured pre-G4 (Codex T9 dropbox confirms "G4Card was already present in the flat export, discriminated union, and `__all__`"). |
| 4 | Class-conformance +1 exactly | PASS | T1 baseline 18 → T9 close 19 (= 11 activation + 8 decision-card shape-pin). +1 exact match. |
| 5 | Frozen-hash AMELIA-P4 unchanged | PASS | See Critical Item #4. |
| 6 | Broad-regression with per-failure attribution | PASS | `tests/parity/ + tests/parametrized_harness/ + tests/unit/`: `921 passed, 18 skipped` (zero failures). T1 baseline had 1 inherited NFR-CG6 governance-version drift; that drift is RESOLVED at T9 by the 1-line `test_nfr_cg_block_aggregated.py` refresh (see Critical Item #6). Codex T9 broad-regression `pytest -p no:randomly -q --tb=line` reported `4239 passed, 42 failed, 27 skipped, 2 xfailed`; per Codex attribution + my spot-check, the 42 failures match inherited broad-suite drift — none are G4-introduced (no decision-card shape, schema, fixture, union, or constructor-path failures). |

---

## Critical Item #6 — Scope expansion (`test_nfr_cg_block_aggregated.py`) — PASS (justified)

**Diff inspection** (`git diff HEAD tests/parity/test_nfr_cg_block_aggregated.py`):

```python
-    assert governance["version"] == "2026-04-29-slab7b-twelve-stories"
+    assert governance["version"] == "2026-05-05-amelia-p5-and-wave-3-lookahead-policy"
```

**Justification analysis (mirrors G1 T11 framing):**

1. **NOT defensive** (defensive = swallowing a real defect). The expected governance JSON version was last refreshed at G6 close to `"2026-04-29-slab7b-twelve-stories"`. The V6 AMELIA-P5 + V7 wave_3_lookahead_policy amendment commit at `57b92b2` advanced the governance version to `"2026-05-05-amelia-p5-and-wave-3-lookahead-policy"`. The NFR-CG6 assertion legitimately needs to track the refreshed version.
2. **JUSTIFIED** as scope-of-this-story by the V6+V7 amendment binding noted in the spec at line 16-18. Codex correctly identified that the inherited NFR-CG6 drift (called out at T1 review and Codex's T1 baseline notice) was a load-bearing in-scope refresh rather than a deferred follow-on.
3. **Symmetric impact:** the same 1-line refresh would have been needed at G2C close, G3 close, or G4 close — Codex applied it at G4 (final-of-three) as the correct location. The G2C and G3 reviewers should NOT separately attribute this scope-expansion (per the "don't double-count with G2C+G3 reviewers" rule in the prompt).

**Conclusion:** Justified scope-expansion; in-scope per V6+V7 binding. The change resolves the 1-failure noted in the T1 baseline (`870 passed, 1 failed, 18 skipped`) without introducing new red. T9 broad-regression confirms `tests/parity/` is now `921 passed, 18 skipped` clean.

---

## Critical Item #7 — V7 P2-CLEAN-×3 BASELINE CLOSURE EVALUATION — PASS (RECOMMEND ELEVATE TO N+3)

**Evaluation framework** (per `docs/dev-guide/migration-story-governance.json::wave_3_lookahead_policy::elevation_gate_description`):

> "After Slab 7c.5.G4 closes (last extend-and-audit story) AND AMELIA-P2 freshness check has run clean on three consecutive consumed pre-auths under N+2 cap, elevation to N+3 is unlocked."

### Per-batch P2 freshness verdict (informational evidence only)

| Close-batch | Story | P2 freshness signal | Status |
|---|---|---|---|
| 1 (sibling parallel) | G2C | Per Codex T9 dropbox §V7 P2-clean-x3 Baseline: "G2C: P2/freshness evidence held clean through PRE-T2 cross-agent T1 review and T2 frozen-hash recheck." Cross-verified: G2C contract-diff and T1 review do not reference any P2-stale signal. | CLEAN |
| 2 (sibling parallel) | G3 | "G3: P2/freshness evidence held clean through PRE-T2 cross-agent T1 review and T2 frozen-hash recheck." Cross-verified: G3 contract-diff and T1 review do not reference any P2-stale signal. | CLEAN |
| 3 (final) | G4 | "G4: P2/freshness evidence held clean through PRE-T2 cross-agent T1 review and T2 frozen-hash recheck." Independently verified at this T11: G4 contract-diff §0 + T1 review verification battery + T2 hash-recheck all pass; no P2-stale governance-JSON signal. | CLEAN |

**Aggregate baseline:** 3/3 P2-clean × 3 close-batches = **CLEAN ×3** baseline satisfied.

### Recommendation

**RECOMMEND: Elevate Wave-3 7c.6+ default lookahead cap from N+2 to N+3** per V7 v1 wave_3_lookahead_policy.

This is informational per the prompt — actual policy elevation requires party-mode ratification at v2 promotion (per V7 `v2_promotion_policy::ratification`: "Requires party-mode consensus + version bump per CLAUDE.md gate-mode-change rule"). The next operator session should:

1. Bring this baseline-data to a slab-opener party-mode session before next Wave-3 7c.6+ story authoring.
2. Validate Murat's triple-condition (C6 ∧ lookahead_tier=1 ∧ t11_tier=lite) against the observed G2C+G3+G4 coupling pattern per V7 v2_promotion_policy::rule.
3. If party-mode ratifies: bump governance JSON version + flip `default_cap: 2` → `default_cap: 3` for Wave-3 stories.
4. If party-mode declines: hold N+2 + document specific drift to revisit at next slab-opener.

**No drift signals to flag.** Baseline data is clean; the gate is open from a data-evidence standpoint.

---

## Critical Item #8 — 2-CLASS-REGIME MIGRATION CLOSURE — PASS

### (a) Legacy `app/models/decision_cards/base.py` intact + unmodified

```text
$ ls app/models/decision_cards/base.py
app/models/decision_cards/base.py
$ git diff HEAD app/models/decision_cards/base.py
(empty)
$ git log --oneline app/models/decision_cards/base.py | head -3
40437bc feat(4.6): add sanctum invalidation warnings
c5f35ee feat(4.3): add party mode interrupt gate
dcb4149 feat(3.2): add decision card schema family
```

Legacy `base.py` exists on disk, has zero diff at HEAD, and was last touched at `40437bc` (Slab 4.6 — well before Slab 7c.5 work began). This story does NOT remove legacy `base.py` — that's an out-of-scope cleanup story. **VERIFIED.**

### (b) G4Card inheritance chain

```text
$ python -c "from app.models.decision_cards.g4 import G4Card; from app.models.decision_cards._base import DecisionCardBase; from app.models.decision_cards.base import DecisionCard; print('G4Card inherits DecisionCardBase:', issubclass(G4Card, DecisionCardBase)); print('G4Card inherits legacy DecisionCard:', issubclass(G4Card, DecisionCard))"
G4Card inherits DecisionCardBase: True
G4Card inherits legacy DecisionCard: False
```

G4Card inherits **only** `DecisionCardBase` (the new Slab-7c base). G4Card does **NOT** inherit legacy `DecisionCard` (the pre-Slab-7c base). **VERIFIED.**

### (c) Chain-closure summary

After G4 close, the 4-story extend-and-audit chain (G1 → G2C → G3 → G4) is **complete**. All four legacy gate subclasses now inherit `DecisionCardBase`:

| Gate | Inherits DecisionCardBase | Closed at |
|---|---|---|
| G1 | ✅ | `5c325a1` (T11 PASS at `7c-5-g1-code-review-2026-05-05.md`) |
| G2C | ✅ | This batch (parallel sibling review) |
| G3 | ✅ | This batch (parallel sibling review) |
| G4 | ✅ | This T11 (final-of-chain) |

Legacy `base.py:DecisionCard` is now consumed only by:
- The 2-class-regime substrate validators (`compiler.py`, `refs.py`, `resume_api.py`, `test_manifest_dotted_reference_resolver.py`) which accept `(DecisionCard, DecisionCardBase)` as a tuple.
- The G-PARTY consumer at `app/gates/party_mode_as_interrupt.py` (out-of-scope per Codex T9 dropbox §Chain Closure Note — this story did not retire that surface; deferred follow-on).

**Conclusion:** 2-class-regime migration of all legacy DecisionCard subclasses to `DecisionCardBase` is COMPLETE. The legacy `base.py:DecisionCard` becomes effectively a marker for the deferred cleanup story — its only live consumers are the 2-class-substrate widening (already widened by G1) and the G-PARTY interrupt gate (which is a separate concern).

---

## AC Compliance Verification

### AC-7c.5.G4-A — Pre-T2 contract-diff + backward-consumer audit + frozen-hash artifacts — PASS

All deliverables present and well-formed:

1. `_bmad-output/implementation-artifacts/migration-7c-5-g4-contract-diff.md` — 136 LOC; 9 sections (§0 T0 frozen-hash + §1–§7 spec-required + §8 T1 baseline evidence). §1 SEMANTIC ALIGNMENT clean-fit verdict explicit (line 20). §2 + §3 DROP rows all carry `audit_method=heavy` with smoke-pass evidence per V6 AMELIA-P5 binding=hard. Schema `| field | disposition | audit_method | rationale |` exact. Light rows correctly bounded to preserve-via-re-declaration / preserve-via-base / new-field-add.
2. `_bmad-output/implementation-artifacts/migration-7c-5-g4-backward-consumer-audit.md` — 115 LOC; 32 executable consumer rows + 3 non-grep consumers (compiler.py, refs.py, resume_api.py — all tagged `already-updated-by-G1`) + 6 required-root smoke consumers (G1-only discriminator) + 3 documentation references (deferred follow-on). Field-Access Summary lines 81-98 explicitly confirms: no audited executable site reads `G4Card.drafted_proposal`, `G4Card.evidence`, `G4Card.risks`, or legacy G4 meta extensions directly after construction.
3. `app/models/decision_cards/_frozen_hashes.py` — UNMODIFIED at HEAD; `FROZEN_AT_SHIP_HASHES["g4"]` matches `98536d2ab845972f96e8d374b08bb3929fb8d02024cbc56616c90424061c6b5a` byte-for-byte.

PRE-T2 cross-agent T1 review verdict at `_bmad-output/implementation-artifacts/7c-5-g4-t1-cross-agent-review-2026-05-05.md` PASSed cleanly with zero MUST-FIX, zero SHOULD-FIX.

### AC-7c.5.G4-B — AMELIA-P4 frozen-hash delta-AC — PASS

`_frozen_hashes.py` UNCHANGED post-T9. Codex T2 verified the pre-extension on-disk hash matched `FROZEN_AT_SHIP_HASHES["g4"]` before extending (per Codex T9 dropbox: "AMELIA-P4 frozen-hash T2 start check PASS"). Current post-T9 on-disk hash diverges intentionally — the contract-diff §1–§7 is the audit trail. The three sibling hashes (g0/g1/g2c/g3 + others) are preserved unmodified.

### AC-7c.5.G4-C — Four-file lockstep co-commit — PASS

All four files present (uncommitted on disk at the moment of this T11; commit is the next step):

1. `app/models/decision_cards/g4.py` (79 LOC) — `class G4Card(DecisionCardBase)` (line 16). Re-declares: `card_id`/`trial_id` (UUID4 — Pydantic-v2 type, not bare UUID); `gate_id: Literal["G4"]` + `gate_focus: Literal["fidelity_gate"]` + `schema_version: Literal["v1"]` (closed Literals); `created_at` (datetime; default UTC factory); `verb: DecisionCardVerb` (closed Literal). Preserves: `final_status: Literal["completed", "partial", "failed"]` (line 43-46; closed three-value Literal preserved verbatim) + `artifact_paths: list[str]` (line 47-50; default empty) + `outcome_summary: str` (line 51-55; min_length=1 + strip-then-non-empty validator at line 71-76). Validators: `enforce_uuid4_version` (line 61-64), `enforce_tz_aware` (line 66-69), `_reject_blank_outcome_summary` (line 71-76).
2. `app/models/decision_cards/schema/g4.v1.schema.json` (197 LOC) — REGENERATED via Path.write_text per anti-pattern A18 (NO_BOM verified). Schema declares: `additionalProperties: false`; `properties` for all 12 G4 fields (3 base + 9 G4-specific including `decision_card_digest`/`meta`); `required: ["decision_card_digest", "meta", "card_id", "trial_id", "final_status", "outcome_summary", "verb"]`; `final_status.enum = ["completed", "partial", "failed"]` (closed); `gate_id.const = "G4"`; `gate_focus.const = "fidelity_gate"`; `schema_version.const = "v1"`. Schema-byte-match test passes (within 16-pass shape-pin run).
3. `tests/parity/test_decision_card_g4_shape.py` (134 LOC; 10 test functions + parametrize fan-out → 16 tests) — bare `LOCKSTEP_CHECK` import only (AMEND-7d-i compliant). Tests: `test_g4_lockstep_files_are_present`, `test_g4_card_has_required_fields` (asserts model_config `extra="forbid"`/`validate_assignment=True`/`frozen=True`), `test_g4_card_closed_enums_red_rejection` (3-way parametrize on gate_id/gate_focus/schema_version), `test_g4_card_final_status_closed_enum_red_rejection` (4-way parametrize per AC-7c.5.G4-C), `test_g4_card_accepts_empty_artifact_paths_default`, `test_g4_card_rejects_empty_outcome_summary` (2-way parametrize on `""` and `"   "`), `test_g4_json_schema_byte_for_byte_match`, `test_g4_json_schema_declares_closed_values`, `test_g4_golden_fixture_round_trips`, `test_g4_card_frozen_mutation_rejection`. Coverage exceeds the 10-11 minimum specified in AC-7c.5.G4-C.
4. `tests/fixtures/decision_cards/g4_golden.json` (23 LOC) — deterministic golden fixture with `gate_id: "G4"`, `gate_focus: "fidelity_gate"`, `final_status: "completed"`, `schema_version: "v1"`, `verb: "approve"`, `artifact_paths: ["_bmad-output/runs/trial-001/final-report.md"]`, `outcome_summary: "Trial completed and all expected artifacts were emitted."`, valid UUID4 `card_id`/`trial_id`, valid 64-char hex `decision_card_digest`, base meta with `cache_state: "cold"` + 2-element `affected_nodes` + empty `override_trail`. Round-trip verified.

### AC-7c.5.G4-D — Backward-consumer non-regression — PASS

Constructor sites updated at the two named locations:

- `app/marcus/orchestrator/production_runner.py:458-469` — G4Card constructor block scrubs legacy `drafted_proposal`/`evidence`/`risks` from common (not passed to G4Card); supplies `decision_card_digest="0" * 64`; converts meta via `_base_card_meta(common["meta"])`; gate_focus + schema_version inherit Literal defaults. Per Codex T9 dropbox: 8 passed in constructor smoke; 179 passed in cross-gate smoke.
- `marcus/orchestrator/m3_trial.py:193-200` — G4Card constructor block (final return path; no `if gate_id == "G4":` guard since G4 is the terminal default after G1/G2C/G3 branches). Same scrub pattern. Same `_base_card_meta(meta)` conversion. Per Codex T9 dropbox: G4-emission tests pass.

2-class-regime substrate already accepts G4Card via `DecisionCardBase` post-G1 — independently verified UNTOUCHED at this T11 (see Verification Battery row "2-class-regime substrate validators UNTOUCHED").

### AC-7c.5.G4-E — Class-conformance + Pydantic-v2 14-idiom + V7 P2-clean-×3 close — PASS

**Class-conformance:** `PASS: 19 parity contract file(s) conform (11 activation + 8 decision-card shape-pin)` — exactly +1 over T1 baseline 18.

**Pydantic-v2 14-idiom checklist:**

| Idiom | Status | Evidence |
|---|---|---|
| 1. `model_config` with `extra="forbid"` | PASS | Inherited from `DecisionCardBase`; shape-pin asserts `G4Card.model_config["extra"] == "forbid"` (line 56) |
| 2. `validate_assignment=True` | PASS | Inherited; shape-pin asserts (line 57) |
| 3. `frozen=True` | PASS | Inherited; shape-pin asserts (line 58); shape-pin verifies mutation rejection via `card.gate_id = "G3"` raises ValidationError (line 129-133) |
| 4. Timezone-aware `datetime` | PASS | `created_at` validator `enforce_tz_aware` (line 66-69); default factory `datetime.now(UTC)` |
| 5. UUID4 typing | PASS | `card_id` + `trial_id` annotated `UUID4` (Pydantic-v2 type, not bare UUID); validator `enforce_uuid4_version` (line 61-64) |
| 6. Closed-enum Literal annotations | PASS | `gate_id`, `gate_focus`, `schema_version`, `final_status`, `verb` — all closed Literals |
| 7. Triple-layer red-rejection on closed enums | PASS | Type-system + emitted-schema enum + parametrized red-rejection tests (4 tests for final_status; 3 tests for gate_id/gate_focus/schema_version) |
| 8. Strip-then-non-empty validators | PASS | `_reject_blank_outcome_summary` validator (line 71-76) checks `if not value.strip()` |
| 9. `Field(..., description=...)` on every field | PASS | All 9 G4-specific fields + 3 inherited fields all have description |
| 10. Inherited base config | PASS | `class G4Card(DecisionCardBase)` — config flows through inheritance |
| 11. `default_factory` for mutables | PASS | `artifact_paths: list[str] = Field(default_factory=list, ...)` |
| 12. `min_length=1` for non-empty strings | PASS | `outcome_summary: str = Field(..., min_length=1, ...)` (Pydantic builtin + custom strip-validator stack) |
| 13. `Field(exclude=True) + SkipJsonSchema` for internal audit fields | N/A | G4 has no internal audit fields; not applicable |
| 14. Schema-byte-match shape-pin | PASS | `test_g4_json_schema_byte_for_byte_match` (line 104-107) |

All 14 idioms covered (idiom 13 N/A); zero gaps.

**V7 P2-clean-×3 baseline:** see Critical Item #7. CLEAN ×3 = ELEVATION GATE OPEN (pending party-mode ratification).

---

## Triage

### MUST-FIX (blocks done): NONE

No MUST-FIX issues identified.

### SHOULD-FIX (high-priority follow-up): NONE

No SHOULD-FIX issues identified.

### NIT (cosmetic / can defer): NONE

No NIT issues identified per aggressive DISMISS rubric in `docs/dev-guide/story-cycle-efficiency.md`.

### Patches applied by this reviewer: NONE

Zero patches applied. Code is clean as-delivered.

---

## Summary

G4 closes the four-story extend-and-audit chain G1 → G2C → G3 → G4 cleanly. Implementation is structurally sound, byte-deterministic, and fully conformant to V6 AMELIA-P5 + V7 wave_3_lookahead_policy + Pydantic-v2 14-idiom + AMEND-7d-i + anti-pattern A18.

**Specific G4-unique invariants verified:**
- `final_status: Literal["completed", "partial", "failed"]` preserved verbatim with all four required reject cases (`"in_progress"`, `"unknown"`, `"COMPLETED"`, `1`) covered in shape-pin (Critical Item #1).
- §1 SEMANTIC ALIGNMENT clean-fit verdict honored at T6 (no field renames, no operator-semantic refinement deferral).
- 2-class-regime migration closed: legacy `base.py` intact + unmodified; G4Card inherits `DecisionCardBase` only (Critical Item #8).

**V7 P2-clean-×3 baseline closure:** 3/3 clean across G2C+G3+G4 close-batches (Critical Item #7). **Recommendation: ELEVATE Wave-3 7c.6+ default cap from N+2 to N+3** — pending party-mode ratification at v2 promotion per V7 `v2_promotion_policy`. No drift signals to flag.

**Recommended next action:** COMMIT G4 four-file lockstep + sibling G2C+G3 lockstep + production_runner.py + m3_trial.py + test_nfr_cg_block_aggregated.py (after sibling reviews close) → flip `migration-7c-5-g4-decision-card-extend-and-audit` to `done` in `sprint-status.yaml`.

**Sign-off:** PASS — recommend COMMIT + FLIP DONE.
