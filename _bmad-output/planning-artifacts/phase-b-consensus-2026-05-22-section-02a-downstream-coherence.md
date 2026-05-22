# Phase B consensus — §02A Downstream-Consumer Schema Coherence Epic

**Date:** 2026-05-22
**Anchor:** `ccb141a` (Trial-3 attempt-2 forensic anchor; HEAD on `trial/3-2026-05-21`)
**Phase A probe:** [`phase-a-probe-2026-05-22-section-02a-downstream-coherence.md`](phase-a-probe-2026-05-22-section-02a-downstream-coherence.md)
**Governance authority:** `CLAUDE.md §Party-mode impasse-resolution chain` (ratified 2026-05-19)

## Verdict: Option 5 — "Round-Trip First, Then Harmonize" (Quinn-synthesis ratified)

**Operator-ratified as Phase B direction.** Treated as Round-2 ratified verdict per impasse-chain governance: Dr. Quinn produced a genuine synthesis, predicted 4-of-4 voice APPROVE/APPROVE-with-amendments without steamrollering any voice's load-bearing concern, and the orchestrator (Claude) judged consensus viability sufficient to land without a separate Round-2 voice roll-call.

## How we got here

### Round 1 — 4-voice party-mode (impasse)

| Voice | Verdict | Load-bearing position |
|---|---|---|
| Winston (architect) | APPROVE Option 1 with amendments A1/A2/A3 | Substrate union not rename; §02A taxonomy + wrangler taxonomy both preserved |
| Amelia (dev) | OBJECT — hybrid "Option 1+" | 39 wrangler `ref_id` sites makes pure rename too risky; wrangler-input-accepts-both pattern |
| John (PM) | APPROVE Option 1 with scope amendments + pre-stated tiebreaker | Trial-3 PASS is goalpost; D5/D6 conditional; C1 deferred post-Trial-3 |
| Murat (test architect) | **OBJECT** — APPROVE Option 3 (adapter) with M-Murat-1..4 | §02A→wrangler integration boundary exercised zero times in any green test; A16+A9 stacked; +15 to +25 broad-regression delta on Option 1 |

**Genuine disagreement** (Quinn's diagnosis): not "which option" but "what is Epic 34's load-bearing achievement?" Three voices wanted substrate harmonization first; Murat wanted integration-boundary green test first.

### Quinn synthesis (Option 5)

**Inverts story order so the integration-boundary green test lands FIRST.** Story 34-1 = round-trip test (RED→GREEN via temporary in-tree translator scaffolding). Stories 34-2..34-N harmonize substrate one drift dimension at a time with the round-trip test as continuous green-gate ratchet. Translator shrinks toward zero as each story lands. Epic's FINAL story deletes the translator entirely.

**Critical distinction Quinn names:** the temporary translator is **scaffolding with a sunset-gate AC**, NOT the permanent two-source-of-truth seam Murat feared (Option 3). Trial-3 attempt-3 launches at Epic close on fully harmonized substrate.

### Quinn's predicted 4-voice reactions to Option 5

- **Winston: APPROVE-with-amendments.** A1 (6-role union not rename) + A2 (`src_id` → `ref_id` in §02A; wrangler keeps `ref_id` as 39-site downstream-rooted identifier) + A3 (substrate-before-cosmetic story order) survive intact as story-level constraints inside Option 5. Substrate invariant #7 (integration tests mandatory) is UPGRADED, not satisfied.
- **Amelia: APPROVE-with-amendments.** Her 6-story decomposition (~24-30 pts) maps 1:1 onto Option 5 with Story 34-1 = round-trip test moving from 34-6 → 34-1. Her 39-site ref_id concern absorbed by translator pattern (wrangler stays `ref_id`-internal; §02A renames `src_id` → `ref_id`).
- **John: APPROVE.** Option 5 literally satisfies John's pre-stated tiebreaker clause: *"If Murat flags test-blast >25 files → consider Option 3 as fallback ONLY for D1/D2/D3 (adapter for input shape) with D5/D6 still resolved wrangler-side. That's a hybrid Quinn could synthesize."* Option 5 IS that hybrid, scoped tighter (single Epic, not 2-Epic; temporary translator, not permanent adapter; D5/D6 wrangler-side).
- **Murat: APPROVE-with-amendments.** M-Murat-1 satisfied as Story 34-1 first; M-Murat-2 (A23 + P5 anti-pattern entries) survives to Epic close; M-Murat-3 (`sme_refs` additive alongside `provenance`, no removal) becomes a 34-N AC. **Anticipated M-Murat-5: round-trip test asserts against the actual Trial-3 attempt-2 forensic directive (sha256 `351a57fbe12aff4a49349c4a646618d92ae38a798ec53eee61668f74f8bbd703`) to prove the exact seam crash is closed.** His broad-regression delta forecast under Option 5 should sit closer to his Option 3 range (−2 to +2 per story) because every harmonization story now moves contract with a green integration ratchet underneath it.

## Ratified Phase B verdict (binding for Epic 34 authoring)

### Direction
- **Option 5 (Quinn synthesis).** Single Epic. Integration-test-first sequencing. Temporary in-tree translator scaffolding with delete-at-Epic-close AC. Substrate harmonized one drift dimension at a time with green-gate ratchet between each story.

### Per-drift-item disposition

| Drift item | Disposition | Resolves in |
|---|---|---|
| D1 (`src_id` ↔ `ref_id`) | §02A composer renames `src_id` → `ref_id`. Wrangler keeps `ref_id` (39 downstream sites). | Story 34-2 or 34-3 |
| D2 (`supporting` ↔ `supplementary`) | Wrangler role enum becomes 6-role union: `{primary, supporting, ignored, validation, visual-primary, visual-supplementary}` per Winston A1. | Story 34-2 |
| D3 (`ignored` no equivalent) | Wrangler accepts `ignored` + handles `excluded_reason`. `validation`/`visual-*` preserved per Stories 27-2/27-3 substrate. | Story 34-2 |
| D4 (hardcoded `o.role == "primary"` in wrangler) | Resolved as byproduct of D2 role-vocab expansion (becomes a closed-enum compare, not string compare). | Story 34-2 |
| D5 (`metadata.json` shape `provenance` vs `sme_refs`) | Wrangler emits `sme_refs` **ADDITIVELY alongside** `provenance` (Murat M-Murat-3 binding; do not remove `provenance` — forensic-trail consumers). `sme_refs[].source_id` matches `pre_packet.SourceRef` shape; wrangler computes per-source `content_digest` at extraction time. | Story 34-4 (or merged with D6) |
| D6 (`ref_id` vs `source_id` field-name fork) | Trivial once D5's shape is rewritten — `sme_refs[]` field is `source_id`, matching pre_packet. | Same story as D5 |
| C1 (legacy `app/marcus/orchestrator/directive_composer.py`) | Delete in Epic 34's FINAL story (or second-to-last; placement after Trial-3 attempt-3 GREEN). Rewire 7 test files to §02A composer or delete tests asserting dead-code behavior. **Direction-may-flip caveat:** if Phase B authoring reveals a consumer I missed, keep + harmonize instead of delete. | Story 34-N (final or near-final) |

### Story-ordering invariants (BINDING)

1. **Story 34-1 is the integration round-trip test** — RED-to-GREEN via temporary in-tree translator. Subprocess (NOT in-process) §02A→wrangler→result.yaml. Real Tejal fixture corpus. Real wrangler subprocess via `python -m skills.bmad-agent-texas.scripts.run_wrangler --directive <path> --bundle-dir <path>` (operator's actual launch command pattern). At least one assertion against the Trial-3 attempt-2 forensic directive (sha256 `351a57fbe12aff4a49349c4a646618d92ae38a798ec53eee61668f74f8bbd703`) to prove the exact seam crash is closed (Murat M-Murat-5).
2. **Substrate-change stories land BEFORE field-rename stories** (Winston A3). Role-vocab union before `src_id`→`ref_id`.
3. **Every harmonization story carries an integration-test AC** — Story 34-1's round-trip test must remain GREEN as each story lands (Winston BINDING #7). The translator shrinks story-by-story.
4. **Final story = delete translator.** Hard AC: "temporary translator file removed; round-trip test green without it." This is the C1-deletion-class discipline applied to the scaffold itself.

### Substrate invariants (BINDING regardless of story ordering — Winston's 7)

1. LLM-judged role classification not destroyed (§02A's `ignored` + `excluded_reason` survive Epic).
2. `validation` + `visual-primary` + `visual-supplementary` (Stories 27-2/27-3 substrate) not destroyed.
3. Pydantic-v2 closed-enum discipline preserved both ends (`run_wrangler.py` role validation stays closed list; grows to 6 members).
4. `extra="forbid"` + `validate_assignment=True` on every Pydantic model touched (per `docs/dev-guide/pydantic-v2-schema-checklist.md`).
5. Cross-field invariants survive role expansion (§02A's `role=ignored` ↔ `excluded_reason` MUST/MUST-NOT carries to wrangler).
6. `run_id` UUID4-validated tz-aware at every boundary (folds in J-A1(a) operator-supplied UUID resolution).
7. Integration-coverage tests MANDATORY per story — NOT unit tests with mocks. E2E §02A→wrangler→bundle against fixture corpus.

### Anti-pattern harvest (Murat M-Murat-2)

File at Epic close in `docs/dev-guide/specialist-anti-patterns.md`:
- **A23: "Two-source-of-truth vocab fork latent across N-year-old integration boundary."** *When two modules share a data contract but have never round-tripped through a green test, vocabulary forks accumulate silently and are discovered at first integration attempt; the cost of harmonization grows linearly with the number of downstream consumers minted against either side's vocab.*
- **P5: "Schema-coherence Epic without integration-boundary green test is governance failure."** Process-tier. Triggers a hard requirement at Epic-author time.

### Risks acknowledged at ratification (Quinn-named)

1. **Translator scope creep** → permanent Option-3 adapter by accident. **Mitigation:** delete-translator final-story AC filed AT EPIC AUTHORING time (not deferred). Hard AC.
2. **Trial-3 attempt-3 slip ~0.5-1 session** vs John's 2-session forecast. Acceptable — we've burned more than 0.5 session twice to "tested module, untested integration."
3. **Round-trip test fixture mock-surface vacuity** (Tejal corpus + LLM-mocked composer is itself substrate). **Mitigation:** M-Murat-4-equivalent audit of the mock surface at Story 34-1 code review.

### J-A1 follow-on fold-in

The two J-A1 entries filed at 2026-05-21T22:30 fold into Epic 34 stories:
- **J-A1(a) `trial-cli-effective-trial-id-vs-section-02a-composer-run-id-divergence`** → Story 34-2 or 34-3 (alongside `src_id`→`ref_id` rename); decision: operator-supplied UUID wins, composer accepts `run_id` parameter
- **J-A1(b) `trial-cli-model-resolution-trail-not-appended-from-adapter`** → Story 34-3 or separate story (NFR-X4 audit trail)

### Out of Epic 34 scope (filed-not-dispatched OR deferred)

| Item | Disposition |
|---|---|
| 5 doc-currency drift entries (`g0-directive-composition-doc-stale-post-c2a`, etc.) | DEFERRED — separate post-Trial-3 docs-cleanup batch (~2-3 hrs) |
| SCP-2026-05-19 TW-7c-4 substrate amendment | DEFERRED — post-Trial-3 PASS (queue order preserved) |
| Marcus-interactive-experience Epic | DEFERRED — post-Trial-3 architecture follow-on |
| SIM105 ruff nit in `trial.py` C2b | DEFERRED-OR-FOLD — land alongside any Epic 34 story touching `app/marcus/cli/trial.py` |

## Sprint Change Proposal scope

Epic 34 substrate amendment scope per CLAUDE.md migration-AC sandbox rules:
- TW-7c-4 `PERMITTED_PYTHON_DIFFS` extension for each `app/` Python file touched (Amelia forecast ≥3 paths)
- Non-`app/` Python (wrangler at `skills/bmad-agent-texas/scripts/run_wrangler.py`) extension for line-89 `unexpected` predicate
- New integration test path under `tests/integration/`
- Total forecast 5-6 paths (Amelia's count)

SCP authoring follows Epic decomposition via `bmad-correct-course` skill, NOT this consensus doc.

## Next steps (this session)

1. **Invoke `bmad-create-epics-and-stories`** with this consensus as input → produces `_bmad-output/planning-artifacts/epics-section-02a-downstream-coherence.md` (or registers Epic 34 in existing `epics.md`)
2. Author Story 34-1 spec (`migration-34-1-section-02a-wrangler-integration-roundtrip-test.md`) FIRST per Quinn ordering
3. Codex dev-prompt for Story 34-1 → Codex T1-T10 → Claude T11
4. (Subsequent stories iterate per ordering invariants above)

## Files in scope per drift item (Phase A baseline; updated as stories land)

| Drift | Files |
|---|---|
| D1, D2, D3 | `app/composers/section_02a/directive_model.py`, `skills/bmad-agent-texas/scripts/run_wrangler.py` (lines 280-394 input + 1660-1738 result), wrangler test surface |
| D4 | `skills/bmad-agent-texas/scripts/run_wrangler.py` lines 1281-1288 (resolved as D2 byproduct) |
| D5, D6 | `skills/bmad-agent-texas/scripts/run_wrangler.py` lines 1240-1266 (metadata writer), `app/marcus/intake/pre_packet.py` lines 175-207 |
| C1 | `app/marcus/orchestrator/directive_composer.py` (delete); 7 test files (rewire or delete) |
| Integration test | `tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py` (NEW; Story 34-1) |

---

**Authored by:** orchestrator (Claude) per CLAUDE.md §Party-mode impasse-resolution chain — Round-1 (4-voice) + Quinn synthesis + Round-2 ratification (operator).
**Ratification time:** 2026-05-22 session.
**Cross-reference:** `_bmad-output/planning-artifacts/deferred-inventory.md §CRITICAL Trial-3-blocking — §02A composer downstream-consumer schema-drift` (the Epic-scope finding entry this consensus closes).
