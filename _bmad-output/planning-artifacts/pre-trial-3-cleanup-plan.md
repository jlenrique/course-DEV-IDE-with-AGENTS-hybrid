---
title: Pre-Trial-3 Cleanup Plan — Multi-Agent-Ratified (Operator-Revised)
authoredAt: 2026-05-07
revisedAt: 2026-05-07 (operator directives Q1-Q5 folded in)
status: ratified-by-bmad-party-mode-2026-05-07; operator-revised; pending pre-S1 party-mode re-review
authority: party-mode roundtable (Paige, Mary, John, Winston, Murat, Amelia, Sally) + operator directives 2026-05-07
operatorMandate: "above all, make sure the production prompt packet is correct, complete, current, and not littered with left-over content"
trigger: post-Slab-7c retrospective close (commit 0ef8594, 2026-05-07); Trial-3 fresh-corpus launch is next strategic move
governance: every session (S1-S5) gated by party-mode pre-review (approach) + post-review (implementation outcome); 10 review gates total
---

# Pre-Trial-3 Cleanup Plan

## REVISIONS — 2026-05-07 (operator directives Q1-Q5)

After party-mode roundtable delivered the original plan, operator (Juanl) issued five directives that reshape scope. The original plan body below is preserved as the multi-agent-ratified baseline; these revisions take precedence where they conflict.

**Q1 directive — "preflight must be addressable + verifiable":** PP-3 is reshaped from a "restore preamble vs correct changelog" binary to a substantive deliverable. The v4.2 pack's preamble must explicitly cover four operator-launchpad concerns, each verifiable:
1. **Environment** — paths, credentials, state-of-disk; verifiable via a checklist that fails closed if any precondition is absent.
2. **System health** — substrate responsiveness; verifiable via the existing health-check probe surface (`scripts/health/`, etc.).
3. **Production run-constants** — defaults visible; verifiable via a diff between operator-supplied overrides and the documented defaults.
4. **Preflight check** — a pass/fail gate before the operator commits to launching. Failure surfaces actionable next-steps; PASS records evidence.

Effort: ~3-4 hr (was 15 min for "correct changelog" or 2-3 hr for naive "restore"). Scope: PP-3 expands to PP-3a through PP-3d covering each of the four concerns.

**Q2 directive — "generate v5 as new canonical pack":** Major scope expansion. The fully-corrected v4.2 (post-PP-1 through PP-8 cleanup) becomes the SOURCE for a new v5 canonical pack. v4.2 stays frozen-as-legacy-axis for the mapping checklist; v5 becomes the production-runs canonical authority going forward. v5 carries:
- All §01-§15 from corrected v4.2
- The Q1 four-concern preamble
- Post-Slab-7c specialist roster (11 activated specialists; Enrique not Audra)
- Migrated runtime path references (NOT legacy primary-repo paths)
- YAML frontmatter (`version: 5.0.0 / status: canonical-for-production-runs / last-updated: <date>`)
- Per-§section migrated-runtime gate-pause disclosure
- Party-mode ratification BEFORE "canonical" status confers

Effort: ~6-12 hr authoring + 1 party-mode round. **Promoted to its own session (S2).** v4.3 sibling pack disposition: superseded-by-v5 (operator confirmation pending at S2 ratification).

**Q3 directive — "every run is a trial; we need a robust reflection mechanism":** Drop the one-off Trial-3 PRD framing entirely (P0-12 retired). Replace with a recurring trial-run methodology pattern. Deliverables:
- `docs/trials/methodology.md` — what we test, evidence we collect, success/partial-pass/fail framing, reflection cadence (the role John originally wanted a PRD to play)
- Per-run trio: `docs/trials/trial-N/launch.md` (pre-flight) + `docs/trials/trial-N/log.md` (during) + `docs/trials/trial-N/postmortem.md` (after)
- `docs/trials/cross-trial-learnings.md` — harvest doc that rolls up patterns over time (Mary's harvest-discipline applied to trials)
- First instance: `docs/trials/trial-3/` skeleton populated as the canonical example

Closer in shape to incident-postmortem ops than to product-PRD. Lighter weight. Naturally recurring. Aligns with operator framing. Effort: ~3-4 hr. **Promoted to its own session (S3).**

**Q4 directive — "clean up marcus/ namespace anomaly now":** ESCALATED to P0. The legacy top-level `marcus/` package was preserved as a migration-shim during Slab 1-7c; with Slab 7c done its purpose is complete. Recommended action: **collapse** (delete legacy `marcus/`, update all imports to `app.marcus.*`), NOT formalize-the-shim. Cleaner long-term substrate. Effort: ~2-4 hr disciplined import sweep + test runs; Codex single-gate dev-story. **Added to S1 P0 set.**

**Q5 directive — "take as many sessions as necessary":** No compression. Five-session sequence below; thoroughness over speed. Total ~35-46 hr cleanup work. Trial-3 launches when all 5 sessions complete + party-mode final ratification.

**Governance amendment (operator-mandated):** every session in the sequence is gated by party-mode review BEFORE (review the approach) AND AFTER (review the implementation). Ten review gates total. Plan-file revisions (this document) are themselves subject to a pre-S1 party-mode re-review before any implementation begins.

---

## AMENDMENTS — pre-S1 review 2026-05-07 (party-mode ratified)

Four reviewers (Paige, Amelia, Murat, Mary) returned GO-WITH-AMENDMENTS. All 13 amendments accepted. Operator directive 2026-05-07 post-review: **NO MORE DEFERRALS — full clean substrate; take time/tokens as needed.**

### Major scope reshapes from pre-S1 review

1. **marcus/ namespace = dedicated session (NEW S2).** Amelia surveyed the actual import surface: 464 occurrences across 176 files; 98 test files import `marcus.*` directly; **`app/marcus/lesson_plan/` and `app/marcus/intake/` DO NOT EXIST** — legacy `marcus/` is a partial migration, NOT a shim. Realistic effort: **8-14 hr, dual-gate, 5pt Codex story, R2/lookahead-2.** Operator selected Option (i) full collapse. Carved into its own session for dedicated branch + dual-gate ceremony + rollback isolation.

2. **S2 ↔ S3 swap (Mary).** Methodology BEFORE v5 authoring — v5's preflight pass/fail gate IS a methodology question. Authoring v5 first means re-aligning when methodology lands later.

3. **No deferrals (operator).** All P2 + P3 items previously deferred to "post-Trial-3" lifted into the cleanup arc. New S6 absorbs them. Total cleanup grows from ~40-50 hr to ~75-105 hr.

### Tactical amendments folded in

| # | Amendment | Source | Effort impact |
|---|---|---|---|
| AM-1 | PP-3b + PP-3d collapse to single deliverable (same preflight gate); rename PP-3a/b/c (env / health-gate / run-constants) | Murat | -30 min |
| AM-2 | PP-3 cites `skills/pre-flight-check/` paths; strike phantom `scripts/health/` reference | Murat | neutral |
| AM-3 | `state/config/run-constants.yaml` existence-spike (10 min) BEFORE P0-6 — file confirmed absent at top level; PP-3c documents the gap, references P1-25 spike | Murat | +10 min pre-S1 |
| AM-4 | P0-4 surgical precision: delete zombie heading at line 323 + delete 2 zombie placeholders + renumber line 335 P3→P4 + verify A1-A20 count in line 299 preamble | Mary | neutral |
| AM-5 | Inventory archive moved S4 → S1 as P0-IH (1 hr; hot-start hygiene for S2-S6) | Mary | +1 hr S1; -1 hr S5 |
| AM-6 | Harvest-log artifact at `_bmad-output/planning-artifacts/pre-trial-3-harvest-log.md`; each post-review captures session harvest items; S6 close rolls up | Mary | +15 min/session |
| AM-7 | PP-3a / P1-27 scope fence: PP-3a verifies env-var presence + naming; P1-27 verifies validity via API smoke | Paige | neutral |
| AM-8 | PP-2 disposition vote (15 min mid-S1 party-mode round): banner-only declaration that v4.2 Marcus-module column = legacy-frozen reference. Recommended outcome: banner. Frees S4 v5 authoring to use migrated paths exclusively | Paige | +15 min S1 |
| AM-9 | Trim original §6 "Recommended sequence" from preserved baseline (superseded; bloat). Keep §5 + §8 audit value | Paige | neutral |
| AM-10 | P0-9 effort 1 hr → 1.5 hr (47-failure baseline catalog realism per Murat) | Murat | +30 min S1 |
| AM-11 | Final-launch gate token (codified): `pytest tests/trial/test_trial3_readiness.py tests/test_preflight_check.py tests/marcus_capabilities/test_preflight_receipt_contract.py -v` + `python -m skills.pre-flight-check.scripts.preflight_runner` (live; zero RESOLUTION-NEEDED for production-required tools) | Murat | neutral; binding gate |
| AM-12 | S1 dispatch order: P0-1 → P0-2 → P0-3 → P0-4 → P0-5 → P0-7 → P0-8 → P0-IH → P0-6 → P0-9 → P0-10 → P0-11 (Murat risk-stack-rank; marcus/ moved to dedicated S2) | Murat | neutral |
| AM-13 | Asymmetric review weighting: pre-review ~15 min / 2-3 voices (approach-confirmation); post-review ~30 min / 4 voices (implementation-scrutiny). Respects operator mandate without burning party-mode capacity | Mary | -50% pre-review cost |

---

## REVISED 6-SESSION SEQUENCE (operator-ratified 2026-05-07)

| Session | Focus | Hours | Pre-review agents | Post-review agents |
|---|---|---|---|---|
| **S1** | Foundation cleanup + Q1 preamble + structural fixes. P0-1 through P0-11 + P0-IH (inventory archive) + PP-2 disposition vote. **NO marcus/ namespace surgery** (carved to S2). **NO Trial-3 PRD** (Q3 retired; replaced by S3 methodology). | ~12-15 hr | (DONE 2026-05-07) Paige + Amelia + Murat + Mary | Paige + Amelia + Murat + Mary |
| **S2** | **marcus/ namespace full collapse (operator Option i; NO DEFERRAL).** Codex 5pt dual-gate cross-agent T11 dev story. Physical move of 40 files (incl. entire Lesson Planner / 4A subgraph). Update 98 test imports + 7 app imports + ~30 fixture/script imports. Import-linter contract surgery (rewrite C1, C2; add `forbidden` contract on top-level `marcus`). Refactor shim-identity test. Full test-suite × 3 iterations. Dedicated branch + PR + dual-gate ceremony for rollback isolation. | ~10-14 hr | Amelia + Winston + Murat | Amelia + Winston + Murat + Paige |
| **S3** | Trial-run methodology (per Q3; sequence-corrected per Mary). Author `docs/trials/methodology.md` (success/partial-pass/fail framing, evidence collection, reflection cadence) + per-run trio templates (`launch.md`, `log.md`, `postmortem.md`) + `docs/trials/cross-trial-learnings.md` skeleton + Trial-3 instance skeleton at `docs/trials/trial-3/`. | ~3-4 hr | John + Mary + Sally | John + Mary + Murat + Sally |
| **S4** | v5 canonical pack authoring (per Q2). Source = corrected v4.2 (post-S1) + S3 methodology preflight framing. Carries: §01-§15 corrected, Q1 four-concern preamble, post-Slab-7c specialist roster (11 + Enrique not Audra), migrated runtime path references, YAML frontmatter (version 5.0.0; status canonical-for-production-runs), per-§section gate-pause disclosure footnotes. Party-mode ratification BEFORE "canonical" status confers. Update all repo references: v4.2 = legacy-frozen authority for mapping checklist; v5 = canonical for production runs. v4.3 sibling pack disposition: superseded-by-v5. | ~8-10 hr | Paige + Sally + John | Paige + Sally + John + Murat |
| **S5** | P1 risk-reduction batch (full). PRD frontmatter executionClosedAt stamps × 3; Slab 7c PRD story_count 26→36; prd.md forwarder; §Epic 3 Stories 3.1-3.6 collapse; 4 housekeeping stories filed in deferred-inventory.md; governance JSON housekeeping-1/2/3/4 entries; sprint-status epic-7c flip; **land housekeeping-2** (scanner-staleness AST rewrite; 2-3 hr Codex); Composition Spec §10 — 5 Slab 7c entries; Migration architecture doc D14-D20; Marcus checkpoint-coord.md refresh (14 §section HIL); 11 §section operator-reference doc stubs; README status table; migration banners (user-guide / admin-guide / dev-guide); v4.3 disposition execution; sources-of-truth.md `### Legacy production prompt-pack authority` extension; state/config spikes (G2A presence; structural-walk needles v4.1→v4.2; frozen-graph digest refresh); test_all_five → test_all_six rename; cred-readiness sweep; CI green confirmation; `.tmp/` sweep; CLAUDE.md governance amendment (4th trigger: multi-slab retrospective hygiene); Epic 15 PRD skeleton. | ~14-18 hr | Mary + Murat + Winston | Mary + Murat + Winston + Paige |
| **S6** | P2 + P3 housekeeping (full clean — NO DEFERRALS). Skill-dir archives (Audra, Cora → `skills/_archive/`); 10+ legacy sidecar archives → `_bmad/memory/_archive/sidecars-pre-trial-3/`; 8 legacy script archives → `scripts/_archive/`; 3 underscore-named Python module relocations out of `skills/`; `skills/reports/` → `_bmad-output/reports/skill-conformance/`; anti-pattern harvest backfill (5 high-density file DISMISS-thread audit); 2 new harvest entries (A21 AUDIT-not-BUILD; A22 AMEND-7c percentage threshold); refresh `specialist-anti-patterns.md` cross-references; v4.1 sibling pack audit for Audra→Enrique; `test_bmb_scaffold.py` 26-skip audit; **land housekeeping-1** (digest-helpers extract); **land housekeeping-3** (specialist-side producer models); **land housekeeping-4** (vera+dan sidecar cleanup); ADR 0003 (NEW family precedent §06B+§07C); ADR 0004 (lane-independence canonical form); **retire ENVELOPE-CARRIER-HACK** (`app/specialists/irene/graph.py:30-38`; Slab 3 `RunState.specialist_envelope` migration); resolve placeholder specialists `app/specialists/{kim,vyx,aria,mira,tamara}/` (operator decides delete vs body); rename `app/cora/ → app/dev_workflow/`; port `heartbeat_check.mjs` + `smoke_*.mjs` → Python (sandbox-AC alignment); retire `app/specialists/_stub/passthrough_specialist.py`; standalone `docs/SOURCE-OF-TRUTH-INDEX.md` operator-facing flat index. | ~25-35 hr | Amelia + Mary + Winston + Paige | All 4 + Sally for UX archive review |
| **(Trial-3 launches)** | Final all-7 party-mode rite-of-passage ratification: substrate clean + maps current + methodology in place + final-gate token green. | — | All 7 agents | n/a |

**Total cleanup arc:** ~75-105 hours across 6 implementation sessions + 12 party-mode review rounds (1 pre-S1 done; 11 remaining).

**Operator capacity assumption:** Sessions are not calendar-bound. Operator paces the sequence; orchestrator (Claude) executes within each session.

---

## S1 P0 SET — final (post pre-S1 review amendments)

Session 1 dispatch order per AM-12 (Murat risk-stack-rank). marcus/ collapse REMOVED from S1 (carved to dedicated S2 per Amelia A1 finding); inventory archive ADDED as P0-IH (Mary AM-5).

| # | Action | Owner | Effort | Notes |
|---|---|---|---|---|
| **P0-1** | Move `SCAFFOLD_NODE_IDS` → `app/specialists/_scaffold/contract.py`; update 20 specialist `graph.py` imports + tests | Codex (1pt single-gate, lite T11) | 1.5 hr | unchanged |
| **P0-2** | De-Trial-2 the gate_runner default path (`app/marcus/orchestrator/gate_runner.py:11`) | Codex (1pt single-gate, lite T11) | 30 min | unchanged |
| **P0-3** | Rewrite Marcus specialist-registry.yaml to list 11 Slab-7-activated specialists | Claude manual edit | 1 hr | unchanged |
| **P0-4** | Anti-pattern catalog dedup (Mary AM-4 surgical precision): delete zombie `## Process Anti-Patterns` heading at line 323 + delete 2 zombie "Reserved for future" placeholders + renumber line 335 P3→P4 (Composition-Shape Vote) + verify A1-A20 count in line 299 preamble | Claude manual edit | 30 min | precision-tightened |
| **P0-5** | v4.2 quick fixes: PP-1 Audra→Enrique crosswalk; PP-4 delete §3.g legacy fallback; PP-5 fix broken `docs/human-in-the-loop.md` cross-ref | Claude manual edits | 30 min | unchanged |
| **P0-6 (per Q1, AM-1, AM-2, AM-7)** | v4.2 substantive preamble — three sub-deliverables, each verifiable: **PP-3a** env-var presence + naming checklist (validity check is P1-27 separate scope) + **PP-3b** system-health & preflight gate documenting existing `skills/pre-flight-check/scripts/preflight_runner.py` invocation + actionable FAIL classes + **PP-3c** production run-constants visible + diffable (documents the gap: `state/config/run-constants.yaml` confirmed absent; references P1-25 spike resolution). Cite `skills/pre-flight-check/` paths (real); strike phantom `scripts/health/` reference. | Claude authoring + Murat verification-pass | 3-4 hr | PP-3b + PP-3d collapsed (same gate) |
| **P0-7** | sources-of-truth.md lines 76-77: `PRODUCTION_GATE_IDS` → `production_gate_ids(manifest)`; expand DecisionCard list to G0/G2A/G5/G6 | Claude manual edit | 30 min | unchanged |
| **P0-8** | mapping-checklist line 7: remove `PRODUCTION_GATE_IDS = frozenset(...)` literal; replace with manifest-derived citation | Claude manual edit | 5 min | unchanged |
| **P0-IH (NEW per AM-5)** | Inventory archive: move 23 closed entries (13 strikethrough + 10 RESOLVED-not-struck) to `## Closed Entries — Archived` section bottom; refresh count summary; close `mapping-checklist-deferred-row-detection-strengthening` (Slab 7c retro decision) | Claude manual edit | 1 hr | hot-start hygiene for S2-S6 |
| **P0-9 (per AM-10)** | 47-failure broad-regression baseline catalog at `_bmad-output/implementation-artifacts/broad-regression-baseline-2026-05-07.md`; one-line attribution per failing nodeid | Claude | 1.5 hr | bumped from 1 hr |
| **P0-10** | `docs/operator/hil-verb-legend.md` — one-page table mapping each §section to verb-set | Claude (Sally + Paige voices) | 1 hr | unchanged |
| **P0-11** | `docs/operator/corpus-preparation-guide.md` — FRESH-corpus shape rules + `course-content/courses/<lesson_slug>/` convention | Claude (Sally + Paige voices) | 1 hr | unchanged |
| **PP-2 disposition (per AM-8)** | Mid-S1 party-mode round (15 min) ratifying v4.2 Marcus-module column = legacy-frozen reference (banner-only declaration, NOT runtime-path-replace). Frees S4 v5 authoring to use migrated paths exclusively. | 3-agent party-mode | 15 min | new mid-session gate |
| ~~**P0-NEW marcus/ collapse**~~ | **CARVED TO S2** — Amelia A1: actual scope is 8-14 hr dual-gate Codex 5pt cross-agent T11 with dedicated branch + PR + rollback isolation. Cannot live in S1. | (S2) | (S2) | promoted to dedicated session |
| ~~**P0-12 Trial-3 PRD**~~ | RETIRED per Q3 — replaced by S3 trial-run methodology | — | — | — |

**Pre-S1 prerequisites (10-25 min total):**
- **PRE-1 (per AM-3):** Verify `state/config/run-constants.yaml` absence at top level (Murat verified during pre-S1; result CONFIRMED ABSENT). Document in PP-3c body.
- **PRE-2:** Tighten P0-4 spec wording in plan file (Mary AM-4 sub-steps embedded in P0-4 row above; complete).

**Final S1 P0 total:** 12 items + 1 mid-session disposition gate, **~13-15 hr** (was 12-15; +1 hr P0-IH; -2-4 hr removed marcus/; +30 min P0-9 bump; +15 min PP-2 vote).

**S1 launch token:** all 12 P0 items closed + PP-2 disposition recorded + harvest log instantiated + post-S1 party-mode review GO verdict.

---

## ORIGINAL PLAN BODY (preserved as multi-agent baseline)

> The sections below are the original 2026-05-07 party-mode-ratified plan. Where they conflict with the REVISIONS section above, revisions take precedence. Preserved here as audit trail of the multi-agent baseline before operator directives folded in.

> **Ratification:** seven BMAD party-mode agents independently crawled distinct slices of the repo on 2026-05-07. This plan consolidates their findings into a single prioritized roadmap. Each agent's full report is preserved verbatim in this session's transcript; this artifact is the synthesis.

> **Single highest-leverage finding (consensus across Paige, Sally, Amelia):** the production prompt pack v4.2 names `skills/bmad-agent-audra` as owner of §11/§11B/§12 voice/audio surfaces — a stale citation since Slab 7b 7b.8 activated `bmad-agent-enrique` as the canonical specialist. AND Marcus's own `skills/bmad-agent-marcus/references/specialist-registry.yaml` does not list any of the 11 Slab-7-activated specialists by their canonical names. **Trial-3 cannot launch with these two artifacts misaligned** — the operator-facing legacy authority and the orchestrator-facing routing registry diverge on who exists.

---

## 1. Executive summary

**Substrate is materially Trial-3-ready.** Murat's risk audit confirms 1.7× class-conformance headroom + 6.4× shape-pin headroom + 4/4 NFR-7c-R7a/R7b predicates green. Tripwire ledger queryable. Schema-pins on Trial3Transcript honored. Broad-regression delta = 0 vs 47-failure baseline.

**Documentation, governance, and operator-experience surfaces have NOT kept pace with the substrate.** Seven distinct drift categories surfaced — none alone are blockers, but their cumulative effect is "operator launches Trial-3 against a substrate whose map is 25 days old."

**Verdict:** Trial-3 should NOT launch until the **P0 (12 items, ~6–8 hours)** is cleared. P1 (~10–14 hours) is strongly recommended but can defer if operator capacity is constrained. P2/P3 are post-Trial-3 housekeeping.

**The cleanup is map-and-doc work, not new-substrate work.** This is the right inversion — substrate over-engineered (Murat's words) ; documentation under-engineered.

---

## 2. Production prompt pack v4.2 audit (operator's TOP PRIORITY)

Per Paige's audit: the pack at `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` is **structurally complete (§01–§15 all present, internally consistent on gate names, all referenced scripts exist on disk)** but carries **7 substantive correctness gaps + 4 cosmetic gaps**. Trial-3 should NOT launch against the pack until the substantive gaps are remediated.

| # | Finding | Severity | Recommended remediation | Effort |
|---|---|---|---|---|
| **PP-1** | TL;DR Crosswalk lines 33–35 cite `skills/bmad-agent-audra` as owner of §11/§11B/§12 — Audra was dissolved 2026-04-24; canonical owner is `bmad-agent-enrique` post-7b.8 | **HIGH (operator misdirection)** | Replace `skills/bmad-agent-audra` → `skills/bmad-agent-enrique` in rows 11, 11B, 12 | 5 min |
| **PP-2** | Marcus-module column throughout TL;DR Crosswalk references legacy primary-repo paths (`marcus/orchestrator/loop.py`, `scripts/utilities/run_hud.py`) — migrated runtime invokes `app/marcus/orchestrator/production_runner.py` + `app/marcus/cli/trial.py` | **HIGH (path drift)** | Add a banner declaring the column legacy-reference status, OR replace paths with migrated counterparts (party-mode disposition required — see action H6) | 15 min – 1 hr depending on choice |
| **PP-3** | Changelog at lines 1486/1488 promises "Pre-Run Checklist", "Run Constants" section, "Initialization Instructions", "Execution Rules", "audience tags" preamble — **none of these sections exist in the file** | **HIGH (trust + readability)** | Either restore preamble using v4.3 sibling pack lines 11-40 as template, OR correct the changelog to remove false claims | 2-3 hr (restore) or 15 min (correct changelog) |
| **PP-4** | §3.g Legacy prose-only fallback (lines 276-287) — its self-deletion clause ("delete after two clean runner runs") was met at Slab 7b 7b.1 close (2026-05-01) | MEDIUM (leftover; operator-confusion) | Delete §3.g entirely OR move to `archive/` sibling | 5 min |
| **PP-5** | Cross-ref `docs/human-in-the-loop.md` at line 1052 — actual file is `docs/workflow/human-in-the-loop.md` | LOW (broken link) | One-line edit | 30 sec |
| **PP-6** | Provenance Appendix lines 1493-1527 — 33 rows of identical boilerplate ("Section X maintains manifest-driven pipeline contract") | LOW (zero-information) | Delete OR rewrite with real per-section provenance citations | 2-3 hr (rewrite) or 5 min (delete) |
| **PP-7** | No YAML front-matter; reader must scroll to line 1483 to discover sub-revision is v4.2i | MEDIUM (governance) | Add `version: 4.2i / status: legacy-authority-for-mapping-checklist / last-updated: 2026-04-19` front-matter | 10 min |
| **PP-8** | Body uses gate names G1/G2/G2.5/G2M/G2F/G3/G3B/G4/G4A/G4B/G5 etc. but the migrated runtime's `production_gate_ids(manifest)` only invokes runner-pause for G1/G2C/G3/G4 (see ADR 0002) — pack does not disclose this asymmetry | MEDIUM (operator-experience) | Add bracketed footnote in §05/§05B/§07B/§07C/§07D/§07F/§08B/§11/§11B/§13/§14.5 noting "migrated-runtime: only G1/G2C/G3/G4 are runner-pauses; other gates body-validated; see ADR 0002" | 30-45 min |

**Assessment:** PP-1 + PP-2 + PP-3 + PP-8 + PP-5 are pre-Trial-3 mandatory (5 items, ~3-5 hr aggregate; PP-2 and PP-3 carry party-mode-disposition cost). PP-4 + PP-6 + PP-7 are MEDIUM and can ride P1.

---

## 3. Source-of-truth registry — recommended structure

Per Paige + Winston consensus: `docs/dev-guide/sources-of-truth.md` exists and is well-structured but (a) lines 76-77 are stale (cite removed `PRODUCTION_GATE_IDS` frozenset; understate runtime by 14 gate IDs); (b) does not register the legacy-authority prompt-pack docs.

**Action SOT-1 (P0):** Update lines 76-77 to reference `production_gate_ids(manifest)` per 7a-2 retirement; expand Slab 7c DecisionCard family-contract additions (G0/G2A/G5/G6).

**Action SOT-2 (P1):** Append a new `### Legacy production prompt-pack authority` section registering: v4.2 motion-enabled pack, v4.1 non-motion pack, v4.3 cluster pack (with status disposition), legacy mapping checklist, operator Irene A/B loop, production checkpoints. Schema per Paige's table proposal.

**Action SOT-3 (P2):** Author standalone `docs/SOURCE-OF-TRUTH-INDEX.md` as one-page operator-facing flat list (distinct from dev-tier registry; different audience).

---

## 4. Findings by domain (consolidated)

### 4.1 Documentation (Paige's slice)

Beyond the prompt pack: `README.md` status table line 71 cites "M5 SHIP-CONDITIONAL through 2026-05-03" (window expired); `docs/user-guide.md`, `docs/admin-guide.md`, `docs/dev-guide.md` migration banners pre-date Slab 7b/7c; `docs/workflow/production-prompt-pack-v4.3-*.md` is in limbo (paused without status disposition); `docs/dev-guide/specialist-anti-patterns.md` carries A19+A20+P1/P2/P3 from Slab 7c session not yet visible to readers as distinct entries (see Mary's slice for catalog-shape problem).

### 4.2 Deferred-inventory + harvest (Mary's slice)

**HEADLINE FINDING (URGENT):** `docs/dev-guide/specialist-anti-patterns.md` has **two `## Process Anti-Patterns` headings** (lines 299 and 323) with **conflicting P1/P2/P3 numbering**. Slab 7c entries (P1 facilitator-skill, P2 DISMISS-thread, P3 NEW-CYCLE-bridge) collide with the original 2026-04-27 P3 (Composition-Shape Vote). The 2026-04-27 P3 is **shadowed**. This MUST be resolved before P5 is filed.

**Inventory hygiene:** 13 strikethrough closed + 10 RESOLVED-but-not-strikethrough = **23 closed entries living in the active table** (62% noise). Plus stale "reactivate at Slab 7c" triggers that have silently expired. Plus duplicate framings (`5a-1` ↔ `m5-fr-trace-partial-FR51`; same for FR52; `2c-2-ac-d` + `2c-2-ac-e`).

**Latent harvest candidates from Slab 7c not yet filed:** AUDIT-not-BUILD framing; AMEND-7c percentage-threshold pattern; positive NEW-CYCLE precedent (T11 PASS-zero × 47).

**Maintenance-trigger gap:** CLAUDE.md §"Deferred inventory governance" fires at (a) Epic retro / (b) story closure / (c) session-wrapup. Multi-slab retrospectives accumulate hygiene debt these triggers don't catch. **Propose new trigger (d):** "at the close of every multi-slab retrospective, archive closed entries + refresh stale triggers."

### 4.3 PRDs + Epics (John's slice)

**Trial-3 PRD does NOT exist.** Only `_bmad-output/implementation-artifacts/trial-3-readiness-checklist.md` (operator-facing playbook, implementation-tier — NOT requirements-tier). FRESH-corpus signal is product-shape decision; partial-PASS likely first-attempt outcome — **needs PRD-tier success criteria bracketing**. Highest-leverage pre-Trial-3 deliverable.

**`prd.md` (30-line stub) actively misleads.** Cold-start cites "Epic 20c (Wave 2B)"; pre-dates entire LangChain/LangGraph migration. Replace with forwarder OR archive.

**Slab 7a/7b/7c PRD frontmatter all read as "PRD-authoring complete" not "execution complete."** Add `executionClosedAt` + `supersededBy: <retrospective>` stamps.

**Slab 7c PRD frontmatter `story_count_final: 26` is off by ~38%** (actual: 36). AMEND-6 explicit note "fix at next edit" — not yet honored.

**§Epic 3 retirement banner landed correctly at lines 892-901, but original Story 3.1-3.6 entries still appear in full below it.** Collapse to "RETIRED — see banner above" stub.

**Epic 15 (Learning & Compound Intelligence) has only seed-level treatment in `epics.md`** — no slab-style PRD. Required before reactivation. Author skeleton pre-Trial-3 so post-PASS dispatch is <1 session.

### 4.4 Architecture + state/config (Winston's slice)

**`docs/dev-guide/sources-of-truth.md` lines 76-77 staleness** is highest single-leverage doc fix (covered above as SOT-1).

**Migration architecture doc frozen at D13 (2026-04-22).** All Slab 7-series decisions (W1 fold-flags, W2 parity-DSL, W3 extend-and-audit gate-mode, W4 alias-DSL inheritance, W5 Marcus-writer partition, W6 transport-DSL completeness) live ONLY in slab PRDs/party-mode notes/ADRs. **The migration architecture doc is no longer the architecture-of-record.** Append D14-D20 as P1 work.

**Composition Spec §10 Decision Log silent on Slab 7c.** §02A directive composer, W5 partition, eight-family taxonomy LOCK, C6 `independence` pivot, A20 cross-package helper duplication — all missing.

**ADR 0003 candidate:** "NEW family precedent for §06B + §07C with no `alias_of` parent" — should be opened to ratify the precedent for future per-section HIL fanouts.

**State/config verification needed (Codex spike candidates):**
- `state/config/run-constants.yaml` — does §04.55 lock semantics expect a top-level template file? (verify; may surface "expected file not present" on fresh-corpus first §04.55 invocation)
- `state/config/fidelity-contracts/` — confirm G2A presence (ADR 0002 names "fresh-author in 7c.5.G2A"; no `g2a-*.yaml` visible)
- `state/config/structural-walk/standard.yaml` — references v4.1 prompt pack; pipeline-manifest is v4.2 (verify needles match v4.2 anchors)
- `runtime/graphs/v42/compiled-graph-digest.txt` — refresh per frozen-graph-version-ceremony post-Slab-7c

### 4.5 Tests + governance (Murat's slice)

**Highest-risk gap: 47-failure broad-regression baseline is NOT cataloged.** No canonical inventory document enumerating which tests are in the failing set with attribution. Trial-3 forensic comparison "is failing test X new?" becomes a manual git-blame exercise instead of a diff. **Recommend: 1-page `_bmad-output/implementation-artifacts/broad-regression-baseline-2026-05-07.md` enumerating ~47 failing nodeids with one-line attribution per failure.**

**Sprint-status.yaml line 1619: `migration-epic-slab-7c-orchestrational-tail: in-progress`** — should be `done` (all 36 stories closed; retrospective closed). 1-line flip.

**Governance JSON gap:** 4 housekeeping-1/2/3/4 stories live in sprint-status.yaml but lack governance-JSON entries with r_tier/t11_tier/lookahead_tier/files_touched annotations. Required before Codex picks up housekeeping-2.

**Test naming:** `test_all_five_writer_alignments_emit_manifest` — 5 → 6 writers post-7c.15 (assertion correct; name stale). 1-line rename.

**Trial-2 corpus path coupling:** `tests/agents/bmad-agent-texas/test_cross_validator.py:195` hard-codes `course-content/courses/tejal-APC-C1/C1M1Part01.md`. **If FRESH corpus replaces Tejal directory, this test fails.** Recommend: keep Tejal corpus on disk during Trial-3 (cheap), document in checklist §3 prerequisites.

**Audit suite verdict:** 7/7 audit/ tests are KEEP — permanent regression guards. Trial-3 surface in tests/trial/ is decoupled from corpus (good).

**Land housekeeping-2 (scanner-staleness AST rewrite) pre-Trial-3** — closes -1 from broad-regression count (47→46), simplifies forensic baseline.

### 4.6 Code-side (Amelia's slice)

**P0 BLOCKER (production imports from tests):** All 20 specialist `graph.py` files import `SCAFFOLD_NODE_IDS` from `tests.integration.scaffold_conformance.scaffold_contract`. Any non-pytest entry point (production runner, MCP server, container) `ImportError`s at boot. **Move `SCAFFOLD_NODE_IDS` to `app/specialists/_scaffold/contract.py`** + update 20 imports.

**P0 BLOCKER (Trial-2 hardcoded in production orchestrator):** `app/marcus/orchestrator/gate_runner.py:11` — `DEFAULT_TRIAL_2_ARTIFACT_DIR = Path("_artifacts") / "trial-2"`. Trial-3 calibration evidence will land in trial-2/ unless every caller overrides. Parameterize OR rename to trial-neutral path.

**P0 BLOCKER (stale Marcus specialist-registry):** `skills/bmad-agent-marcus/references/specialist-registry.yaml` does not list the 11 Slab-7-activated specialists by canonical names. Lists API/skill-names instead. Marcus cannot delegate. Rewrite to mirror `docs/dev-guide/specialist-sanctum-alignment-matrix.md`.

**HIGH (Marcus duality):** Top-level `marcus/` (legacy) coexists with `app/marcus/` (Slab 7 home). `app/marcus/facade.py:3` shims to legacy. Decision needed pre-Trial-3: collapse OR formalize shim with import-linter contracts.

**Dissolved-specialist skill dirs:** `skills/bmad-agent-audra/` + `skills/bmad-agent-cora/` should move to `skills/_archive/`. Cold-start agent could otherwise invoke dissolved persona.

**Placeholder specialists** (`app/specialists/{kim,vyx,aria,mira,tamara}/`): scaffold-only; no `_act.py`. Either delete pre-Trial-3 OR add STATUS line.

**`app/cora/` exists** but is the dev-graph workflow runner (NOT the dissolved Cora persona). Name confusion. Clarifying comment OR rename to `app/dev_workflow/`.

**Sidecar inventory:** ~20 `*-sidecar/` directories under `_bmad/memory/`. Operator-gated `vera-sidecar/` + `dan-sidecar/` per housekeeping-4. The dissolved (`audra`, `cora`, `mike`) + placeholder (`aria`, `kim`, `mira`, `tamara`, `vyx`, `canvas-specialist`) + superseded (`tracy`, `gary`, `kira`, `enrique`, `quinn-r`, `irene`, `marcus`) can move to `_bmad/memory/_archive/sidecars-pre-trial-3/`.

### 4.7 Operator-facing UX (Sally's slice)

**`skills/bmad-agent-marcus/references/checkpoint-coord.md` is STALE** — describes legacy 4-gate model, not the 14-§section HIL surfaces shipped in Slab 7c. Marcus's mental model contradicts the surfaces he presents. Refresh pre-Trial-3.

**Verb-set diversity is operator-attention risk:** approve/edit/reject (most), select/edit/reject (7c.14), submit/edit/discard (7c.18a/b), complete/edit/reject (7c.15), lock/edit (7c.8), acknowledged (7c.7). **Without a one-page legend the operator pattern-matches by feel; attention degrades by §08B.**

**Operator-reference docs gap:** `docs/conversational-gates/` has G0/G1/G2C/G3/G4 (5 references). Slab 7c shipped 14 surfaces. **11 surfaces have no operator-reference doc** (§04.5, §04.55, §05.5, §06B, §07C, §07D, §07F, §08B, §11, §11B, §15).

**Corpus-prep guide gap:** FRESH-corpus Trial-3 means operator must shape the corpus from zero. No `docs/operator/corpus-preparation-guide.md` exists. Without it, corpus-prep mistakes risk on §02A directive composition (the surface that closes Trial-2 finding #2).

**`docs/workflow/human-in-the-loop.md` is STALE** — pre-Slab-2 vocabulary; references gates that no longer exist as runner-pauses.

**DESCRIPT-ASSEMBLY-GUIDE.md** (output of `section_15_bundle.py`): structurally correct (writer-id → payload → embedded text in code fences) but not narrative. Acceptable for Trial-3 (Juanl IS the experienced operator); flag for post-Trial-3 polish.

**Trial3Transcript JSON serialization:** auditable but not narrative. Operator post-trial sees event_types + sha256 digests but no human-readable "what was decided." Schema is shape-pinned to FR-7c-51 — change is governance, not editorial. Defer to post-Trial-3.

---

## 5. Prioritized cleanup roadmap

### P0 — Trial-3 launch blockers (must clear before launch)

| # | Action | Owner | Effort | Source |
|---|---|---|---|---|
| **P0-1** | Move `SCAFFOLD_NODE_IDS` from `tests.integration.scaffold_conformance.scaffold_contract` → `app/specialists/_scaffold/contract.py`; update 20 specialist `graph.py` imports + tests | Codex (1pt single-gate) | 1.5 hr | Amelia A1 |
| **P0-2** | Parameterize `app/marcus/orchestrator/gate_runner.py:11` — remove `DEFAULT_TRIAL_2_ARTIFACT_DIR`; thread `trial_id` through (or rename default to trial-neutral) | Codex (1pt single-gate) | 30 min | Amelia A2 |
| **P0-3** | Rewrite `skills/bmad-agent-marcus/references/specialist-registry.yaml` to list 11 Slab-7-activated specialists by canonical name + role + sanctum path; mirror sanctum-alignment-matrix | Claude (manual edit) | 1 hr | Amelia B3 + Sally HIGH-1 |
| **P0-4** | Anti-pattern catalog: collapse duplicate `## Process Anti-Patterns` headings; renumber rescued entry to **P4. Composition-Shape Vote Without End-to-End Exercise**; preserve all bodies verbatim | Claude (manual edit) | 30 min | Mary B.1 |
| **P0-5** | Production prompt pack v4.2: fix Audra→Enrique crosswalk lines 33-35; fix `docs/human-in-the-loop.md` cross-ref at line 1052; delete or archive §3.g legacy fallback | Paige (Claude) | 30 min | Paige PP-1, PP-4, PP-5 |
| **P0-6** | Production prompt pack v4.2: resolve missing preamble (changelog v4.2d/f promise sections that don't exist) — restore from v4.3 sibling pack OR correct changelog | Paige (Claude); party-mode disposition vote | 2-3 hr (restore) or 15 min (correct) | Paige PP-3 |
| **P0-7** | Update `docs/dev-guide/sources-of-truth.md` lines 76-77: replace `PRODUCTION_GATE_IDS` frozenset reference with `production_gate_ids(manifest)`; expand DecisionCard list to include G0/G2A/G5/G6 | Paige (Claude) | 30 min | Paige A.9 + Winston D.1 |
| **P0-8** | Update `_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md` line 7 — remove stale `PRODUCTION_GATE_IDS = frozenset({"G1","G2C","G3","G4"})` literal; replace with manifest-derived citation | Paige (Claude) | 5 min | Winston A.5 |
| **P0-9** | Catalog 47-failure broad-regression baseline as `_bmad-output/implementation-artifacts/broad-regression-baseline-2026-05-07.md` — 1-line attribution per failing nodeid | Murat (Claude or Codex) | 1 hr | Murat E.1 |
| **P0-10** | Author `docs/operator/hil-verb-legend.md` — one-page table mapping each §section to verb-set + meaning of each verb at that surface + what `edit` permits | Sally + Paige (Claude) | 1 hr | Sally HIGH-2 |
| **P0-11** | Author `docs/operator/corpus-preparation-guide.md` — FRESH-corpus shape rules, `course-content/courses/<lesson_slug>/` convention, what goes in / what stays out, §02A composer expectations | Sally + Paige (Claude) | 1 hr | Sally HIGH-5 |
| **P0-12** | Author Trial-3 PRD at `_bmad-output/planning-artifacts/prd-trial-3.md` — FRESH-corpus product shape; PASS / partial-PASS / FAIL success criteria; pre-conditions; gate-by-gate evidence acceptance; reactivation triggers | John + party-mode (1 session) | 2-3 hr | John H1 |

**P0 aggregate:** ~12-16 hours of focused work; can be split into two operator sessions OR partially parallelized between Claude (manual edits) and Codex (P0-1, P0-2 dev-stories).

### P1 — Strongly recommended before Trial-3 (risk-reduction)

| # | Action | Effort |
|---|---|---|
| **P1-1** | Production prompt pack v4.2: Marcus-module column rewrite (banner-only OR runtime-path-replace; party-mode disposition) | 15 min – 1 hr |
| **P1-2** | Production prompt pack v4.2: per-§section migrated-runtime gate-pause disclosure footnotes | 30-45 min |
| **P1-3** | Production prompt pack v4.2: YAML front-matter (version 4.2i; status legacy-authority; last-updated) | 10 min |
| **P1-4** | Inventory archive: move 23 closed entries (13 strikethrough + 10 RESOLVED-not-struck) to bottom-of-file `## Closed Entries — Archived` OR sibling `deferred-inventory-archive.md`; refresh count summary | 1 hr |
| **P1-5** | Inventory: close `mapping-checklist-deferred-row-detection-strengthening` (already closed by Slab 7c retro decision; not yet reflected) | 5 min |
| **P1-6** | Inventory: merge duplicate framings (5a-1↔FR51; 5a-2↔FR52; 2c-2-ac-d↔2c-2-ac-e) | 30 min |
| **P1-7** | Inventory: refresh stale "reactivate at Slab 7c" triggers (class-c-validator-method-name-rename, slab-7b-scaffold-conformance-update, slab-7b-pre-existing-full-ruff-debt) | 20 min |
| **P1-8** | Slab 7a/7b/7c PRD frontmatter: add `executionClosedAt` + `supersededBy: <retrospective>` stamps | 30 min |
| **P1-9** | Slab 7c PRD: fix `story_count_final: 26 → 36` per AMEND-6 | 5 min |
| **P1-10** | Replace `prd.md` (30-line stub) with forwarder pointing to migration PRD + Slab sub-PRDs + retrospectives | 30 min |
| **P1-11** | Collapse §Epic 3 Stories 3.1-3.6 in `epics-langchain-langgraph-migration.md` to "RETIRED — see banner above" stub | 15 min |
| **P1-12** | Move 4 Slab-7c housekeeping stories from retrospective Action-Items into deferred-inventory.md per CLAUDE.md governance | 15 min |
| **P1-13** | Add 4 housekeeping-1/2/3/4 entries to `migration-story-governance.json` with r_tier/t11_tier/lookahead_tier/files_touched; bump version to `2026-05-07-slab7c-housekeeping-quartet-added` | 1-2 hr |
| **P1-14** | Sprint-status.yaml: flip `migration-epic-slab-7c-orchestrational-tail: in-progress → done` | 1 min |
| **P1-15** | Land housekeeping-2 scanner-staleness AST rewrite (1pt single-gate lite; spec already `ready-for-dev`) — closes -1 from regression count | 2-3 hr Codex |
| **P1-16** | Composition Spec §10: append 5 Slab 7c entries (§02A composer, W5 partition, eight-family LOCK, C6 independence pivot, A20 helper duplication) | 1-1.5 hr |
| **P1-17** | Migration architecture doc: append D14-D20 (W1-W6 + ADR 0003 candidate) — OR open `D14+` appendix file referenced from main doc | 2-3 hr |
| **P1-18** | Refresh `skills/bmad-agent-marcus/references/checkpoint-coord.md` to describe 14 §section HIL surfaces (NOT legacy 4-gate model) | 1 hr |
| **P1-19** | Author 11 per-§section operator-reference doc stubs at `docs/conversational-gates/section-{02a,04a,04.5,04.55,05.5,06b,07b,07c,07d,07f,08b,11,11b,15}-operator-reference.md` (mirror G0/G1/G2C/G3/G4 pattern) | 2-3 hr |
| **P1-20** | Refresh OR retire `docs/workflow/human-in-the-loop.md` (pre-Slab-2 vocabulary) | 30 min |
| **P1-21** | Refresh `README.md` status table — Slab 7b/7c not reflected; M5 SHIP-CONDITIONAL window expired | 30 min |
| **P1-22** | Refresh migration banners in `docs/user-guide.md`, `docs/admin-guide.md`, `docs/dev-guide.md` | 45 min |
| **P1-23** | Resolve `docs/workflow/production-prompt-pack-v4.3-*.md` status (supersede-by-v4.2 OR update for cluster-only-active) | 15-30 min |
| **P1-24** | Extend `docs/dev-guide/sources-of-truth.md` with `### Legacy production prompt-pack authority` section (per Paige Section C proposal) | 30-45 min |
| **P1-25** | State/config verification spikes: `run-constants.yaml` semantics, G2A fidelity contract, `structural-walk/standard.yaml` v4.1→v4.2 needles, `runtime/graphs/v42/compiled-graph-digest.txt` refresh | 1-2 hr Codex |
| **P1-26** | Rename `test_all_five_writer_alignments_emit_manifest` → `test_all_six_*` | 5 min |
| **P1-27** | Cred-readiness sweep: confirm operator `.env` has required keys for Trial-3 smoke surface (OPENAI_API_KEY required; LANGSMITH_API_KEY + DATABASE_URL recommended; per-API smoke keys per `--live` opt-ins) | 30 min |
| **P1-28** | Run `.github/workflows/specialist-parity.yml` + `activation-contract.yml` locally; confirm green pre-Trial-3 | 30 min |
| **P1-29** | Sweep `.tmp/` directories (commit-split/, pytest-fixtures/, probes); confirm `.gitignore` covers; remove stale fixtures | 15 min |
| **P1-30** | Decide marcus/ vs app/marcus/ namespace strategy (collapse OR formalize shim with import-linter); minimal call: pin a comment header making the precedence explicit | 30 min – 4 hr depending on choice |
| **P1-31** | Author Epic 15 PRD skeleton at `_bmad-output/planning-artifacts/prd-epic-15-learning-compound-intelligence.md` so post-Trial-3 PASS reactivation is <1 session | 1-2 hr |
| **P1-32** | CLAUDE.md amendment: add fourth deferred-inventory governance trigger "(d) at the close of every multi-slab retrospective, archive closed entries + refresh stale triggers" | 10 min |

**P1 aggregate:** ~18-25 hours; one focused session-day if uninterrupted.

### P2 — Trial-3 +1 housekeeping (post-launch cleanup)

- Archive `skills/bmad-agent-{audra,cora}/` → `skills/_archive/`
- Archive non-Vera/non-Dan superseded sidecars to `_bmad/memory/_archive/sidecars-pre-trial-3/`
- Archive legacy `scripts/utilities/{fix_slide_content, fix_test_file, repair_validator, restore_validator_clean, m5_pre_vote_audit, cluster_dispatch_trial, inspect_gary_output, fidelity_walk}` → `scripts/_archive/`
- Decide `skills/{gamma_api_mastery, bmad_create_specialist, bmad_agent_tracy}/` Python module relocation (out of `skills/` namespace)
- Move `skills/reports/` → `_bmad-output/reports/skill-conformance/`
- Author standalone `docs/SOURCE-OF-TRUTH-INDEX.md` operator-facing flat index
- Anti-pattern harvest backfill: scan 5 high-DISMISS-count files (30-1, 32-4, 32-2a, 29-1, 30-2b) for cross-story DISMISS-thread accumulations ≥3 per P2 ratchet rule
- File two new harvest candidates: AUDIT-not-BUILD framing + AMEND-7c percentage-threshold pattern (A21/A22 or P5/P6)
- Refresh `docs/dev-guide/specialist-anti-patterns.md` + `specialist-migration-template.md` for Slab 7b/7c learnings
- Audit v4.1 sibling pack for same Audra→Enrique correctness issues
- Audit `tests/migration/test_bmb_scaffold.py`'s 26 skip occurrences during housekeeping
- Land housekeeping-1/3/4 (digest-helpers extract / specialist-side producer models / vera+dan sidecar cleanup)

### P3 — Technical debt (Trial-3 +N)

- Open ADR 0003 for §06B + §07C NEW family precedent
- Fold M2+C2 import-linter contract redundancy + open ADR 0004 for symmetric-lane-independence canonical form
- Retire ENVELOPE-CARRIER-HACK in `app/specialists/irene/graph.py:30-38`
- Resolve placeholder specialists `app/specialists/{kim,vyx,aria,mira,tamara}/` — body or delete
- Rename `app/cora/ → app/dev_workflow/` (or pin clarifying comment header)
- Port `scripts/heartbeat_check.mjs` + `smoke_*.mjs` to Python (sandbox-AC alignment)
- Confirm `app/specialists/_stub/passthrough_specialist.py` retirement plan
- Author Trial-3 postmortem PRD-amendment (lessons → roadmap shape for Trial-4/5 cadence)
- Reassess `test_audit_ac_slab_7c_close_d12_protocol.py` archive candidacy at Slab 8 opener

---

## 6. Recommended sequence

### Session-1 (P0 sprint, ~6-8 hr)

**Phase A (parallel; ~2 hr):**
- P0-1, P0-2 → Codex dev-stories (1pt each, single-gate, lite T11)
- P0-3 (Marcus registry rewrite) → Claude manual edit
- P0-4 (anti-pattern duplicate-section consolidation) → Claude manual edit
- P0-5 (prompt pack quick fixes: Audra→Enrique, broken xref, §3.g delete) → Claude manual edit
- P0-7 (sources-of-truth.md lines 76-77) → Claude manual edit
- P0-8 (mapping-checklist line 7) → Claude manual edit

**Phase B (~3-4 hr):**
- P0-6 disposition vote (party-mode: restore preamble OR correct changelog) — 30 min
- Execute chosen path (either restore from v4.3 OR correct changelog)
- P0-9 (broad-regression baseline catalog) — Claude or Codex spike
- P0-10 (operator HIL verb legend)
- P0-11 (corpus-preparation guide)

**Phase C (~2-3 hr; party-mode):**
- P0-12 (Trial-3 PRD authoring) — convene party-mode for product-shape ratification

**End of Session-1:** P0 cleared. Push to `origin/dev/langchain-langgraph-foundation` per push-cadence policy.

### Session-2 (P1 sprint, optional, ~6-8 hr selective)

Operator selects which P1 items ship pre-Trial-3 vs ride post-Trial-3. **Recommended P1 minimum-viable set for risk-reduction:** P1-4, P1-5, P1-13, P1-14, P1-15, P1-16, P1-18, P1-21, P1-25, P1-27, P1-28, P1-29, P1-32 (~10-12 hr). The remaining P1 can ship post-Trial-3 without significant risk.

### Trial-3 launch decision criteria

Trial-3 launches when:
- **All P0 items closed** (12/12)
- **Critical P1 items closed** (P1-13 governance JSON; P1-14 sprint-status flip; P1-25 state/config spikes; P1-27 cred-readiness; P1-28 CI green; P1-29 .tmp/ swept)
- **Operator reads `docs/operator/hil-verb-legend.md` once + tapes to second monitor** per Sally's Version-B story
- **Operator reads `docs/operator/corpus-preparation-guide.md` + has FRESH corpus prepared** per convention
- **Trial-3 PRD ratified at party-mode** with PASS/partial-PASS/FAIL criteria explicit

---

## 7. Risk register (cross-domain consensus)

| Risk | Severity | Mitigation |
|---|---|---|
| Operator follows v4.2 prompt pack crosswalk and looks for `skills/bmad-agent-audra/` | HIGH | P0-5 (5-min editorial) |
| Production runner / MCP server boots and `ImportError`s on `tests.integration.scaffold_conformance` | HIGH | P0-1 (1.5 hr Codex) |
| Trial-3 calibration evidence lands in `_artifacts/trial-2/` | HIGH | P0-2 (30 min Codex) |
| Marcus tries to delegate to a Slab-7-activated specialist, fails to find it in registry | HIGH | P0-3 (1 hr Claude) |
| P5 anti-pattern filing compounds the duplicate-`## Process Anti-Patterns` shadowing | HIGH | P0-4 (30 min Claude) |
| Trial-3 surfaces unexpected behavior; operator/agent reads `sources-of-truth.md` and is misled by stale `PRODUCTION_GATE_IDS` citation | MEDIUM-HIGH | P0-7 (30 min Claude) |
| Trial-3 forensic comparison "is this failing test new?" requires manual git-blame per failure | MEDIUM-HIGH | P0-9 (1 hr) |
| Operator hits §04.55 "lock or edit" with no reference doc; pattern-matches by feel; attention degrades | MEDIUM | P0-10 + P1-19 |
| FRESH corpus prep mistakes trigger the §02A directive composer silent-bypass class (closed by 7c.3a but operator-prep discipline remains operator-side) | MEDIUM | P0-11 |
| Trial-3 PASS/FAIL judgment is ambiguous; partial-PASS bracketing not formalized | MEDIUM | P0-12 |
| Codex picks up housekeeping-2 and finds no governance-JSON entry | LOW-MEDIUM | P1-13 |
| `state/config/run-constants.yaml` lock target absent on first §04.55 invocation | LOW | P1-25 |
| `tests/agents/bmad-agent-texas/test_cross_validator.py:195` fails if Tejal corpus dir replaced by FRESH corpus | LOW | Document in checklist §3 to keep Tejal corpus on disk during Trial-3 |

---

## 8. Multi-agent ratification record

| Agent | Slice | P0 contributions | P1 contributions |
|---|---|---|---|
| 📚 Paige (Tech Writer) | Documentation | PP-1, PP-3, PP-5, PP-7 (sources-of-truth.md), PP-8 (broken xref) | PP-2, PP-4, PP-6, PP-9-15 (banners + v4.3 disposition + SOT extension) |
| 📊 Mary (BA) | Deferred-inventory + harvest | E1 anti-pattern duplicate consolidation (URGENT) | E2-E10 (archive 23 closed; merge duplicates; refresh triggers; CLAUDE.md amendment) |
| 📋 John (PM) | PRDs + epics | H1 Trial-3 PRD | H2-H6 (forwarder, frontmatter stamps, 7c story_count fix, §Epic 3 collapse, housekeeping inventory entry) + Epic 15 skeleton |
| 🏗️ Winston (Architect) | Architecture + state/config | Tier-1 #1-3 (sources-of-truth + mapping-checklist citation) | Tier-2 (Composition §10; D14-D20; state/config spikes; ADR 0003) |
| 🧪 Murat (Test Architect) | Tests + governance | TIER-1 #1-3 (47-failure baseline; epic-7c flip; housekeeping-2 land) | TIER-2 (governance JSON quartet; test rename) |
| 💻 Amelia (Developer) | Code-side | P0 #1-3 (SCAFFOLD_NODE_IDS move; gate_runner Trial-2 hardcoding; Marcus registry) | P1-P3 (marcus duality; cred sweep; archives) |
| 🎨 Sally (UX Designer) | Operator-facing | HIGH-1, HIGH-2, HIGH-5 (checkpoint-coord refresh; verb legend; corpus-prep guide) | HIGH-3, HIGH-4 (HIL doc retire; 11 operator-reference stubs); MED-6-13 |

**Consensus convergence points (3+ agents same finding):**
- Audra→Enrique stale citation: Paige + Sally + Amelia
- `production_gate_ids(manifest)` staleness in sources-of-truth.md: Paige + Winston + Murat (implicit)
- Marcus specialist-registry stale: Sally + Amelia + (Mary harvest-discipline implicit)
- 14-surface operator-reference docs gap: Sally + Paige
- Trial-3 PRD missing: John + Sally (corpus-prep) + Murat (success-criteria implicit)
- Inventory hygiene + governance refresh trigger: Mary + John

**Disagreements (none material):** all seven agents converged on "substrate ready; documentation behind." No agent argued for delaying Trial-3 beyond P0 closure.

---

## 9. Closing posture

The cleanup pass codified here is **a documentation-and-governance pass, not a substrate pass.** The dev-agent side delivered 36/36 with broad-regression delta = 0 and over-engineered shape-pin headroom. What's left is the map catching up to the territory.

**Single-sentence summary for the operator:** *Twelve P0 items (~6-8 hours of focused work, mix of Claude manual edits + 2 Codex single-gate dev-stories + 1 party-mode Trial-3 PRD ceremony) clear all Trial-3 launch blockers. P1 (~18-25 hr) is risk-reduction; recommend selective adoption based on session capacity. P2/P3 are post-Trial-3 housekeeping.*

**Production prompt pack v4.2 verdict (per operator's TOP PRIORITY):** *Body is structurally complete and internally consistent (§01-§15 all present; gate-name-internally-coherent; all referenced scripts exist on disk). The perimeter (TL;DR Crosswalk + preamble + cross-refs + version stamping) carries leftover content + stale citations. Five HIGH-tier prompt-pack items (PP-1, PP-3, PP-5, PP-7, PP-8) are part of the P0 set. The pack is fundamentally sound — it just needs a tech-writer's pass to reconcile the perimeter with the substrate the body describes.*

**Trial-3 confidence after P0 closure:** GREEN. Substrate is ready; Map will be ready; Operator's first-encounter ergonomics will be supported by verb legend + corpus-prep guide + Trial-3 PRD success criteria. The trial that produces validation evidence + leaves the operator energized rather than depleted is within reach.

— Ratified 2026-05-07 by BMAD party-mode roundtable: Paige 📚, Mary 📊, John 📋, Winston 🏗️, Murat 🧪, Amelia 💻, Sally 🎨.
