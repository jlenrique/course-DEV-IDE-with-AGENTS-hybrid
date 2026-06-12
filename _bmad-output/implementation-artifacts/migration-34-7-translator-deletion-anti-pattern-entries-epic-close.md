# Migration Story 34-7: Translator Deletion + A23/P5 Anti-Pattern Entries + Epic 34 Close (FINAL STORY)

**Status:** done *(Codex T1-T10 + Claude T11 standard `bmad-code-review` PASS 2026-05-22; **EPIC 34 CLOSED**. T11 verdict: 0 MUST-FIX, 0 SHOULD-FIX, 0 functional NITs. All 8 ACs (AC-34-7-A through H) PASS. Forensic grep-sweep verified zero hits both markers across entire repo.)*
**Sprint key:** `migration-34-7-translator-deletion-anti-pattern-entries-epic-close`
**Epic:** Epic 34 — §02A Downstream-Consumer Schema Coherence (this is the FINAL closing story)
**Pts:** 3
**Gate:** **dual-gate** (production code deletion + doctrine surface edit + deferred-inventory closure + Epic-close ceremony)
**K-target:** ~1.5×
**R-tier:** **R2**
**T11-tier:** standard
**Files touched (substrate-verified 2026-05-22):**

**Deleted (1 file):**
- `app/composers/section_02a/_wrangler_translator.py` (temporary in-tree scaffold from Story 34-1; carries `Epic-34 scaffold marker constant = True` + `Epic-34 delete-at-close marker` markers per Story 34-1 D2)

**Modified (3 files):**
- `tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py` (REMOVE translator import + translator invocation; test runs §02A → wrangler subprocess DIRECTLY post-substrate-harmonization)
- `tests/integration/test_section_02a_translator_shrinkage_sequence.py` (DELETE — test asserted properties of a now-deleted module; nothing left to assert)
- `docs/dev-guide/specialist-anti-patterns.md` (APPEND A23 + P5 entries per Murat M-Murat-2 binding; format-frozen 4-field per Paige 2026-04-22; substrate-verified next ordinals: A23, P5)
- `_bmad-output/planning-artifacts/deferred-inventory.md` (CLOSURE MARKERS on `section-02a-downstream-consumer-compatibility-systemic-drift` + J-A1(a) + J-A1(b) entries)

**Lookahead tier:** **1** (focused; final cleanup; substrate verified).
**Wave:** 1 — slot 7 (FINAL).

**FR coverage:** Closure of FR-E34-* via Epic-close ceremony.
**NFR coverage:** NFR-E34-9 (A23 + P5 anti-pattern entries filed at Epic close); NFR-E34-10 (delete-at-Epic-close hard AC for translator); NFR-E34-1 (Story-34-1 ratchet stays GREEN without translator).

**Contract Decisions (LOCKED 2026-05-22 — SUBSTRATE-VERIFIED):**

**D1. Translator file deletion (AC-34-7-A BINDING):**

`app/composers/section_02a/_wrangler_translator.py` is DELETED entirely. Pre-conditions verified at T1:
- `TRANSLATOR_ACTIVE_MAPPINGS == frozenset()` at dispatch (Stories 34-2 + 34-3 retired all 3 mappings)
- Story 34-5's `test_translator_active_mappings_is_empty_at_story_34_5_close` PASSES at dispatch

No other modules in `app/` import the translator (Story 34-1 D1 spec restricts imports to test surface only). Only consumer is `tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py`.

**D2. Story 34-1 round-trip test simplification (AC-34-7-B BINDING):**

Edit `tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py`:
- REMOVE the import `from app.composers.section_02a._wrangler_translator import ...`
- REMOVE the `translate_directive_for_wrangler(directive)` call
- REPLACE with direct write of §02A's `Directive.model_dump(mode="json")` to YAML (no translation layer)
- REMOVE `test_translator_active_mappings_is_load_bearing_in_production` and `test_translator_module_carries_deletion_markers` (translator no longer exists)
- KEEP `test_forensic_directive_round_trips_through_wrangler_subprocess_via_translator` (rename to drop "via_translator" suffix) — verify it still PASSES against post-substrate-harmonized §02A + wrangler

Post-edit: the test runs §02A → wrangler subprocess DIRECTLY. Forensic-anchor assertion + materials assertion + exit-code assertion + sme_refs assertion (per Story 34-4 extension) all stay green.

**D3. Story 34-5 sequence-test deletion:**

`tests/integration/test_section_02a_translator_shrinkage_sequence.py` is DELETED entirely. The translator module it was testing no longer exists; tests would fail at import.

**D4. A23 + P5 anti-pattern entries (AC-34-7-D BINDING; Murat M-Murat-2):**

Append to `docs/dev-guide/specialist-anti-patterns.md` per format-frozen 4-field shape (verified at substrate-audit time: 4-field format `name / example / counter-pattern / slab-of-discovery`; current ordinals end at A22 and P4; next are A23 + P5):

```markdown
### A23. Two-source-of-truth vocab fork latent across N-year-old integration boundary

- **Example:** Epic 34 §02A composer ↔ Texas wrangler schema-drift surfaced at Trial-3 attempt-2 (2026-05-21; run-id `6a3393f8-...`; sha256 `351a57f...`). Both directive composers (legacy `app/marcus/orchestrator/directive_composer.py` from Story 7a.1 + new §02A `app/composers/section_02a/` from Story 7c.3a) emitted `role: supporting` which the Texas wrangler at `skills/bmad-agent-texas/scripts/run_wrangler.py:328-338` rejected (wanted `supplementary`). The drift had been silently present in the codebase across multiple Slab arcs but never triggered because no trial-run reached the wrangler with a real composer-output directive — Trial-2 attempts halted before specialist dispatch. Cost to harmonize: Epic 34 (7 stories ~29 pts) + 27-path TW-7c-4 substrate-freeze allowlist amendment.
- **Counter-pattern:** When two modules share a data contract, REQUIRE an integration-boundary green test as the contract's authoritative source-of-truth. Story 34-1 establishes the §02A → wrangler subprocess round-trip test at `tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py` as the canonical example. Static-grep coverage of the substrate is NOT a substitute; only a round-trip green test catches vocab forks. Sibling-to-A17 (substrate hostile to composition) but distinct: A17 is shape-hostile; A23 is vocab-forked at a boundary that no test exercised.
- **Slab of discovery:** Epic 34 (post-Slab-7c §02A downstream-consumer coherence; ratified Phase B 2026-05-22 via Quinn-synthesis Option 5; closed via this story)

### P5. Schema-coherence Epic without integration-boundary green test is governance failure

- **Example:** Epic 34 Phase A probe + Phase B party-mode (2026-05-22) discovered that the §02A composer ↔ Texas wrangler integration boundary had been exercised exactly ZERO times in any green test prior to Trial-3 attempt-2. Murat dissented at Phase B Round 1 with broad-regression forecast of +15 to +25 failures on the harmonize-down-substrate option vs −2 to +2 on adapter-with-test option. Dr. Quinn synthesis ratified Option 5 ("Round-Trip First, Then Harmonize") which inverted story order so the integration ratchet (Story 34-1) lands BEFORE substrate harmonization (Stories 34-2 through 34-7). The Epic SHIPPED on Murat's dissent posture, not against it.
- **Counter-pattern:** Any Epic touching a producer-consumer contract MUST include an integration-boundary green test as its FIRST story (RED→GREEN ratchet). Subsequent stories EXTEND the test in lockstep with new substrate behavior (per AC-34-4-A-EXT extension pattern). Process-tier: triggers a hard requirement at Epic-author time per `bmad-create-epics-and-stories` workflow Step-3 readiness — ANY Epic spec touching a producer-consumer seam SHALL declare which story IS the integration ratchet and which subsequent stories extend it.
- **Slab of discovery:** Epic 34 (post-Slab-7c §02A downstream-consumer coherence; Murat M-Murat-2 binding from Phase B SCP-ratification Round 1 2026-05-22)
```

**D5. Deferred-inventory closure markers (AC-34-7-E BINDING):**

Edit `_bmad-output/planning-artifacts/deferred-inventory.md`:

1. Move `section-02a-downstream-consumer-compatibility-systemic-drift` (current location ~lines 405-453; CRITICAL Trial-3-blocking section) to `§Closed Entries — Archived` with strikethrough + closure marker:

```markdown
| ~~**`section-02a-downstream-consumer-compatibility-systemic-drift`**~~ | ~~Trial-3 attempt-2 forensic crash 2026-05-21; Epic-scope finding~~ | **CLOSED 2026-05-22 via Epic 34 (sprint-change-proposal-2026-05-22-epic-34-substrate-amendment.md; Stories 34-1..34-7 at commit range <C1-sha>..<this-commit-sha>).** Phase B Quinn-synthesis Option 5 ratified; 7-story integration-ratchet-first harmonization. Trial-3 attempt-3 launches on fully harmonized substrate (no temporary translator). |
```

2. Same closure for `trial-cli-effective-trial-id-vs-section-02a-composer-run-id-divergence` (J-A1(a)) → strikethrough + `CLOSED 2026-05-2N via Story 34-3 (commit <sha>)`.

3. Same closure for `trial-cli-model-resolution-trail-not-appended-from-adapter` (J-A1(b)) → strikethrough + `CLOSED 2026-05-2N via Story 34-3 (commit <sha>)`.

**D6. Forensic grep-sweep (AC-34-7-H BINDING — Murat new-A23-adjacent-surface mitigation):**

Post-D1 deletion + D2/D3 edits, Codex SHALL run two repo-wide greps:

```bash
grep -rn "Epic-34 scaffold marker constant" .
grep -rn "Epic-34 delete-at-close marker" .
```

**BOTH MUST return ZERO matches.** If either returns >0 hits, Codex SHALL NOT proceed to T10; investigate residue + complete deletion + re-run grep until 0.

Codex T9 self-review handoff MUST include grep evidence (`zero hits across N files searched`) as forensic proof of complete scaffold deletion.

**D7. Trial-3 attempt-3 launch readiness check (AC-34-7-F BINDING):**

At Story 34-7 close, operator can fire the launch command:
```
.\.venv\Scripts\python.exe -m app.marcus.cli trial start --preset production --input course-content/courses/tejal-apc-c1-m1-p2-trends/
```

with NO substrate work remaining (no translator; no legacy composer; harmonized vocabulary; integration ratchet green). The Trial-3-PASS gate per Epic 34 header is SATISFIED.

---

## Task chain T1-T11

**T1 readiness check:**
- C1 + Stories 34-1..34-6 = `done` in sprint-status.yaml.
- Story 34-1 round-trip test PASS.
- `TRANSLATOR_ACTIVE_MAPPINGS == frozenset()` (verify via grep + Read).
- Story 34-5's sequence test PASSES at dispatch.
- Anti-pattern catalog at `docs/dev-guide/specialist-anti-patterns.md` confirmed at A22 + P4 (next: A23 + P5).

**T2 translator deletion:** D1 implementation.

**T3 Story-34-1 test simplification:** D2 implementation.

**T4 Story-34-5 sequence-test deletion:** D3 implementation.

**T5 anti-pattern entries:** D4 implementation; APPEND A23 + P5 per format-frozen 4-field shape.

**T6 deferred-inventory closures:** D5 implementation.

**T7 forensic grep-sweep:** D6 implementation; verify ZERO hits both greps.

**T8 ruff + lint-imports + focused suite + broad regression sweep.**

**T9 self-G6** (standard) + grep evidence in T9 handoff.

**T10 ready-for-review handoff.**

**T11 Claude T11 standard review + commit + flip done + Epic 34 close ceremony.**

---

## Acceptance Criteria

- **AC-34-7-A** (translator deletion): D1 BINDING.
- **AC-34-7-B** (round-trip test stays GREEN without translator): D2 BINDING.
- **AC-34-7-C** (Trial-3 forensic-anchor assertion stays GREEN): inherited from AC-34-1-B; Story-34-1 test still asserts sha256 byte-identical match post-translator-removal.
- **AC-34-7-D** (A23 + P5 entries filed): D4 BINDING.
- **AC-34-7-E** (deferred-inventory closure markers): D5 BINDING.
- **AC-34-7-F** (Trial-3 attempt-3 launch readiness): D7 BINDING.
- **AC-34-7-G** (anti-pattern audit — M-Murat-4 reframe): repo-wide audit of every test mocking `run_wrangler` subprocess; document findings + file follow-on if any vacuous-test surface persists.
- **AC-34-7-H** (forensic-sweep for translator-scaffold residue): D6 BINDING.

## Epic 34 closure ceremony at Story 34-7 close

After Claude T11 PASSes:
1. Story 34-7 flipped `done` in sprint-status.yaml.
2. Sprint-status.yaml entry: "**🎉 Epic 34 §02A Downstream-Consumer Schema Coherence FULLY COMPLETE: 7/7 stories DONE.**"
3. Deferred-inventory closure markers applied per D5.
4. `next-session-start-here.md` updated to reflect Trial-3 attempt-3 launch readiness.
5. SESSION-HANDOFF.md entry for Epic 34 closure (if at session-wrap).
6. Operator can dispatch Trial-3 attempt-3.

## Cross-references

- Epic 34 §"Story 34-7" + NFR-E34-9 + NFR-E34-10
- Story 34-1 spec D2 (scaffold marker source-of-truth)
- Phase B consensus (Quinn-synthesis Option 5 ratification record)
- Murat M-Murat-2 binding (A23 + P5 anti-pattern filing)
- `docs/dev-guide/specialist-anti-patterns.md` (format-frozen 4-field shape)
- `_bmad-output/planning-artifacts/deferred-inventory.md` (closure target)
