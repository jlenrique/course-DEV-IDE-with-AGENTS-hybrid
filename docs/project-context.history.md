# project-context.md — Archived Context Addenda (bootstrapped 2026-07-18T03:00:38+00:00)

> Verbatim addendum stack lifted above the hand-authored base doc when `docs/project-context.md` was demoted to a generated view. This is the archive sibling; it must NOT be named `project-context.md`.

---

# Current Context Addendum - 2026-07-17 (NIGHT) (session WRAPUP: knowledge graph regenerated at bfefcc1b; doc chain deferred to fresh session)

**Session class:** S. Branch `trial/c1m1-p1-2026-07-17` (origin synced).

**Landed:** `.understand-anything/knowledge-graph.json` fully regenerated at HEAD `bfefcc1b` (2699 nodes / 5164 edges / 7 layers / 14-step tour; 894 files; fingerprints baseline rebuilt; validator clean) — Epics 41/42/43 substrate now in-graph. GCM account-picker neutralize fix committed (`b9b5029f`): gh-pages publish can no longer seed the `x-access-token` GCM identity; `ready_for_trial.ps1` purges any seeded identity pre-trial.

**Next (fresh session, operator-directed):** ONBOARDING regen (pairing-completion commit for the graph — do NOT re-run `/understand`), then user/dev/admin/specialist guides + STATE-OF-THE-APP §11 (you-are-here, glyphs, progress table), then the R2 operator-steered live trial. Carried findings unchanged (3 production observations; S-1 party-gated; sandbox env fails).

---

# Current Context Addendum - 2026-07-17 (LATE) (session WRAPUP: EPIC 43 HIL Surface Tabular Coverage COMPLETE + master consolidated)

**Session class:** S. Branches: consolidated `dev/workbook-wave-3940-2026-07-15` → `master` (`12775df6`, pushed); on fresh `trial/c1m1-p1-2026-07-17` (`12775df6`, synced).

**Landed:** **Epic 43 — HIL Surface Tabular Coverage** (green-lit 5/5 SIGN-WITH-RIDERS; CLOSED), surfaced from a live Marcus-SPOC trial (`5169a872`) whose first HIL surface — the G0 directive confirm — dumped raw YAML. Two audits proved the 42-1 tabular projector only covered G0 while 13 more gates emitted identity-only + a JSON blob. 12 stories (each fresh-dev + orchestrator consumer-baseline-diff review): 43-2 registry + generic fallback + paused-gate wiring (systemic fix); 43-10 RED-first coverage ratchet; 43-1 G0 directive table (killed `trial.py:364` raw dump); 43-3 gate→content_type bridge + variant/mode; 43-4 voice; 43-5 plan-unit/estimator/constants; 43-6 target-lists; 43-8 package/handoff; 43-7 motion; 43-9 research/workbook honest de-scope; 43-11 SPOC anti-drift; 43-12 governance close. **14 gate content types → 14 bespoke tabular renderers; ratchet allowlist empty; requirement `hil-operator-surfaces-must-be-tabular` completed (42-1 false-close corrected).** New substrate: `app/marcus/cli/hil_tabular_projector.py` (registry + `GATE_TO_CONTENT_TYPE` bridge + 14 renderers), `app/marcus/cli/trial.py` (`_confirm_or_edit_directive` renders the directive table; `_emit_gate_surface_if_paused` routes per-gate content; recover/resume-batch coverage holes closed). master consolidated (debt cleared).

**Next:** KG/ONBOARDING regen (OWED) + operator-steered R2 live trial on the fresh branch. Do NOT reopen Epic 43. 3 production observations filed (voice G4Card binding; SPOC flagged-axis; fold-gate/pause-set) — fix on own merits only.

---

# Current Context Addendum - 2026-07-17 (session WRAPUP: EPICS 41 + 42 COMPLETE — bc747b51 fixed + ngrok public HUD)

**Session class:** S. Branch `dev/workbook-wave-3940-2026-07-15` (origin `4ca3d19b`; 14 commits, pushed).

**Landed:** Two epics start-to-finish from the parked `bc747b51` diagnosis. **Epic 41 — Resume-Walk Dispatch Integrity** (41-1 resume/recover live-env preflight; 41-2 fail-loud on silent specialist skip both walks; 41-3 REMOVE the `max_specialist_calls` throttle — the ACTUAL bc747b51 cause was `cap=1` starvation, not keyless; 41-4 `MARCUS_TRIAL_BUDGET_USD` dollar-budget enforced-stop). **Epic 42 — Operator Surface Next-Pass** (party-signed 5/5): 42-1 tabular HIL + neutral next-action verb; 42-2 HUD-survives-gate-pause + `CREATE_NO_WINDOW`; 42-3 16-toggle run-settings standing readout (additive-within-v1); 42-4 public read-only HUD non-leak overlay; 42-5 G0S pre-walk settings gate (convention-conforming manifest HEAD gate); 42-6 G0S default-ON wake-sentinel; 42-7 manifest-pin refresh (live 52-node); 42-8 ngrok reserved-domain public HUD. Operator's public HUD wired + live-proven at `https://deplete-courier-blurt.ngrok-free.dev`.

**Next:** operator live steered run (R2 — the only owed witness); KG/ONBOARDING regen + master consolidation (owed); Story 40-2 workbook cover-art trove selection (operator-directed, queued). Do NOT reopen Epic 41/42.

---

# Current Context Addendum - 2026-07-15 (session WRAPUP: Epic 38 CLOSED + first complete workbook + 39/40 wave opened under the Paid-Run Economy Protocol)

**Session class:** S. Branches: `codex/workbook-enhanced-epics-36-40` (consolidated to master `2d5b7493`) then `dev/workbook-wave-3940-2026-07-15`.

**Landed:** First complete runner-verified WORKBOOK (trial `a940c5eb`) + LO-verified follow-up (`8b275e5b`, 6/6 real statements) after two same-day fix cycles (LO-overlay authority-map join `9d4f0593`; Pass-1 head-self-parent normalization `2147ad4d`). Stories 38.1+38.3a CLOSED (party 4/4); Epic-38 retrospective DONE; 38.2 re-homed to the 39-wave; Epic 38 CLOSED. KG+ONBOARDING regenerated at `b24b2aed`; all guides aligned; SOTA §11 refreshed with the Epic-38 close DoD. **Paid-Run Economy Protocol ratified + binding** (witness-replay pre-flight STRICT, probe→freeze→replay→spend, live-shape fixtures, batched governed runs, machine bars with negative pins — `wave-3940-kickoff-party-record-2026-07-15.md`). Wave execution: answer-leak strip (`c0811817`), Story 37-2b (07W.3 deep-dive enrichment; probe attempt 1 froze→normalizer v2→attempt `838524b8` PASS ENRICHED) and Story 39-1 (term-keyed glossary; deterministic probe `fdbed233` PASS 7/7) both `done-awaiting-live-witness`. `tests/live_witness_replay/` FOUNDED (STRICT 19/19, three families witnessed).

**Next:** 39-1b (exercise MERGE, ready-for-dev, strict-serialized) → governed batch run A (witnesses 37-2b+39-1+39-1b; STRICT pre-flight satisfiable) → 38-2 + 39-2 + 40-1 → run B → off-frozen-lesson re-proof finale. HAI cross-SME exploration pre-authorized when AFK at Phase-2 lane 1.

---

# Current Context Addendum - 2026-07-14 (session WRAPUP: Workbook Epics 36–38 advanced; live acceptance next)

**Session class:** S. Branch `codex/workbook-enhanced-epics-36-40`.

**Landed/ready at close:** Epic 36 complete; Stories 37.1/37.2a/37.3/37.4 and 38.0/38.3b complete; Story 38.3a and Story 38.1 remain in progress. Clustered-v2 Pass-1 authority/journal/economics/source-span/slide-authority hardening and Ask-A deterministic wiring are implemented and reviewed. Governed trial `399bcd61` passed ratification, Storyboard A, G2C, and realtime perception before safely stopping at Irene Pass 2 on the shared `$ 5%` token-classification defect. Amendment 8 fixes that production-valid parser defect and is deterministic/review green; the frozen run remains nonpassing and was never retried.

**Next:** the first action of the next working session is one operator-authorized fresh governed paid Marcus-SPOC workbook run: Tejal corpus, deck/workbook/research/realtime perception ON; motion/HUD/batch/detective OFF; fresh identity; delegated HIL; first-run-stands. It must reach `07W.1/07W.2` and produce passing Story 38.3a + 38.1 live evidence. Do not mark either story done before that witness.

**Known debt:** inherited motion structural-walk sequence-document parity remains red but is out of the planned motion-OFF run path; KG/ONBOARDING regeneration is owed after the live-validation arc stabilizes. Full close record: `SESSION-HANDOFF.md` top section; coherence report: `reports/dev-coherence/2026-07-14-1952/`.

---

# Current Context Addendum - 2026-07-11 (session WRAPUP: Operator HUD Epic 35 — full arc + live E2E party verdict)

**Session class:** S. Branch `dev/hud-revival-2026-07-11`.

**Landed:** Operator HUD **Epic 35 — ALL 10 stories (35.0–35.9) authored+closed**. Full chain: bmad-ux (approved spines) → bmad-architecture (19-AD projection-contract spine) → 6-seat party green-light → per-story fresh-dev + adversarial review. New substrate: `app/hud/**` (GET-only server + render), `app/notify/**` (notifier+watchdog, real ntfy L3), `app/models/runtime/operator_surface.py` (projection contract, dual pins + §Projection-Demands parity pin), `app/marcus/orchestrator/operator_surface_assembler.py` (sole-writer emission at `_persist_envelope`), start-path pre-flight/heartbeats + HUD-server launch, legacy `run_hud.py`→deprecation stub (wrong-run fallback deleted).

**Live E2E (35.7):** operator-authorized full paid run reached `completed` ($0.60). Initial 6-seat party verdict = CONDITIONAL/PARTIAL (flagship gate paste-command FAILED F-E2E-1 + ambient instruments empty F-E2E-2).

**Fix arc CLOSED — active goal MET (2026-07-12):** both blockers fixed + re-witnessed on a completed live paid run (trial `31ff847c`, $0.38, all 8 gates→G4A). F-E2E-1 (`ffc97f45`) gate command `gate decide`→`trial resume` inline-verdict — 8/8 gates paste-driven exit 0, zero card_missing + cross-process EXECUTION test. F-E2E-2 (`ed9d1c25`) ambient sections wired into both walks — non-null throughout (roster 1→17, trace 66 events). **Same 6-seat party (incl. contrarians Splinter+Level) UNANIMOUS re-verdict: PERFORMED TO SPEC ON THE WITNESSED SURFACE; HUD authorized for real operator use.** 2 production bugs (NOT HUD) fixed on own merits per SPOC-goal guardrail: vision `prompt_cache_key` (`247cf72d`), research figure-normalizer DOI-x crash (`5ace59f7`). Residual non-blocking DEBT: batch pause-class un-witnessed, workbook cache-only (2-of-3, F-E2E-4), browser DOM/notification, L2-golden gate-snapshot.

**Production fix:** vision realtime `prompt_cache_key` bug (247cf72d) — surfaced by the proofing run at node 07G.

**Next:** HUD arc DONE + operator-usable. Optional: branch consolidation to master (owed); residual non-blocking HUD debt (batch witness, browser witness, L2-golden snapshot); F-E2E-4 workbook (own dev cycle). Do not reopen closed Epic-35 stories.

---

# Current Context Addendum - 2026-07-10 (session WRAPUP: Research foundations + workbook products + TRAIL trio)

**Session class:** S. Branch `dev/agentic-research-foundations-2026-07-10`.

**Landed this session (durable at WRAPUP commit):**
- Agentic Research Foundations **R0–R7 PROMOTED** (detective opt-in, default OFF; Scite/Consensus/Jefferson/credibility/Irene/R7 pause)
- Workbook research products **W0–W4 CLOSED** (shared packet → Research Glossary + Research Trends/hot-topics)
- TRAIL trio **CLOSED under fences** (OpenAlex LIVE; glossary capability-note polish; semantic WARN-only tripwire; full semantic audit still TRAIL)

**Explicit non-claims:** detective not default-ON; glossary not human SME-reviewed; semantic tripwire not production FAIL / not comprehensive claim↔source audit; OpenAlex not PDF/SSO.

**Next:** Workbook artifact customization (interactive). Do not reopen S8 / Batch v1 / foundations claim envelope.

**Close letters:** `agentic-research-foundations-promote-2026-07-10.md`, `workbook-research-products-close-2026-07-10.md`, `trail-trio-close-2026-07-10.md`

---

# Current Context Addendum - 2026-07-10 (session WRAPUP: Batch LLM v1 CLOSED)

**Session class:** S. Branch `dev/batch-mode-2026-07-10`.

**Landed this session (durable at WRAPUP commit):**
- Batch LLM Execution Mode **v1 CLOSED** (party CLOSE 4/4)
- Full spine: A0→A1+A3→B1→B2→B3→B4→B5→B6-land→B6-promote + A2
- Opt-in `--llm-execution-mode batch` (default realtime); vision-only; gpt-5.5 both arms
- `waiting_for_provider_batch` + `trial resume-batch`; cost report; `prompt_cache_key=stable_perception_v1`
- A2 LiteLLM harness hermetic + optional `--run-live`

**Explicit non-claims / deferred:** A1-EXT all-node tiering TRAIL; workbook not batch-eligible; batch not production default.

**Next (operator-chosen):** Workbook artifact customization. Do not reopen S8 or Batch v1.

**Close letter:** `_bmad-output/implementation-artifacts/batch-llm-epic-v1-close-2026-07-10.md`

---

# Current Context Addendum - 2026-07-10 (session WRAPUP: Tejal P4 + trust + next = Batch)


**Session class:** S. Branch `dev/lesson-planning-2026-07-09`.

**Landed this session (durable at WRAPUP commit):**
- Mine-next Track A (N6/N3/N2) + trust Waves 1–2 (T1–T4c) local substrate
- Pass-2 speakable dual-view (narration ⊆ perceived; source provenance ≠ speech license)
- Desmond `HandoffParseError` → `SpecialistDispatchError` + `handoff.parsed.advisory-missing` retryable
- Variant-selection recover noop when Gary dropped (reenter-at-07)
- Tejal P4 fullwalk trial `22b27500-6e67-4dd7-8308-fd89defe3d99` **completed**
  (PASS-WITH-FENCES: motion slide-01 only; node-15 / Desmond brief-file residuals filed)

**Fidelity:** `MARCUS_NARRATION_FIGURE_FIDELITY_ACTIVE` exercised ON for the walk;
**product default remains OFF.**

**Next (operator-chosen):** Batch LLM run-start `realtime|batch` switch
(spec `epic-batch-llm-execution-mode-spec-2026-07-01.md`), then workbook
customization. Do not reopen S8. Do not re-run Tejal fullwalk for fence polish.

**Evidence anchors:**
- `…/evidence/tejal-p4-fullwalk-20260710T005021Z/`
- `…/evidence/irene-figure-contradiction-reenter08-20260710T054100Z/`
- `…/evidence/tejal-p4-continue-desmond-20260710T060700Z/`
- `…/evidence/mine-next-trust-e2e-20260710T043111Z/`
- Close: `mine-next-trust-wave2-e2e-close-2026-07-10.md`

---

# Current Context Addendum - 2026-07-10 (Phase-2 Six Mine-Now + integrated E2E)

**Six Mine-Now program:** CLOSED-all-6 + integrated E2E amendment (party 4/4).
Letters: `phase2-six-mine-now-final-close-2026-07-10.md` +
`phase2-six-mine-integrated-e2e-amendment-2026-07-10.md`.
Greenlight: `phase2-six-mine-now-greenlight-2026-07-09.md`.

**Integrated E2E (durable bar):** `runs/8099669e-e677-4578-9889-a62250c38fb0/`
evidence `mine-integrated-e2e-20260710T024036Z/` — plan-dialogue → live Irene
Pass-1 → auto selection → trial start consumption; SME fail-loud; canonical/
drill/prose as named non-E2E adjuncts. No Gamma. Seam fix: `start_trial`
honors plan-JSON companions.

| # | Aspect | Evidence |
|---|--------|----------|
| 1 | Automatic Lesson_plan | `mine1-auto-selection-20260710T021943Z/` |
| 2 | Interactive SPOC | `mine2a-interactive-planning-20260710T022630Z/` |
| 3 | Per-SME voice | `mine3-per-sme-voice-20260710T023031Z/` |
| 4 | Canonical processed-source | `mine4a-canonical-shape-pin-20260710T022613Z/` |
| 5 | Drill | `mine5-drill-projector-20260710T023034Z/` |
| 6 | Workbook prose uplift | `mine6-prose-uplift-20260710T023242Z/` |

**Fenced residuals:** 2B memory OS; 4B normalize/writeback; HAI/PHS Gamma
variants; drill JSON Schema; in-graph SME revoicer default wire; Gamma full
walk; happy-path coverage JSON write; on-read digest verify.

S8 stays closed. Branch `dev/lesson-planning-2026-07-09`.

---

# Current Context Addendum - 2026-07-09 Session 28 (Claim B live bespoke)

**Marcus plan-ratify Claims A+B:** COMPLETE-with-named-fenced-residuals.
**Claim B:** UNFENCED COMPLETE (**bespoke**) — live OpenAI Irene Pass-1.

Evidence: `marcus-claim-b-live-20260709T234801Z/`  
Runs: `bc8359aa-fdd9-4551-a9a1-e6483941c962` (treatment) vs
`b5cd2bc8-50e5-4d0f-9c60-0dbc79664bde` (control).  
Close: `marcus-claim-b-live-close-2026-07-09.md`.  
Driver: `scripts/utilities/bank_marcus_claim_b_live_irene.py`.

**Holds:** plan-ratify → `runs/<uuid>/` → live Pass-1 → coverage+provenance+
plan≠control; digests match companions; `lo_coverage=present` + LO touch.

**Still fenced (superseded in part by Six Mine-Now 2026-07-10):** Gamma;
lecture ingest; happy-path coverage JSON write in `act()`; on-read digest
verify. (Interactive SPOC / SME / projector / auto-selection MET in Mines 1–5.)

S8 stays closed. Branch `dev/lesson-planning-2026-07-09`.

---

# Current Context Addendum - 2026-07-09 Session 28 (solicitation surface)

**Marcus plan-ratify + Claims A/B (substrate + mocked Claim B):** earlier bank
`marcus-solicitation-success-20260709T230000/` at `318b6b0f`. Live Claim B
supersedes the mock-act fence — see addendum above.

---

# Current Context Addendum - 2026-07-09 Session 28 (continued)

**Step 2→3 DONE:** `planning-context-to-irene-pass1-handoff` =
COMPLETE-with-named-fenced-residuals (party 4/4 CLOSE). Evidence
`irene-planning-context-handoff-20260709T180555/` with per-component live-tests.
Named residuals: ECH-08 / ECH-10 / ECH-12. Claim fence holds.

**Still fenced / next bigger gains:** interactive SPOC planning REPL; W5 compose;
SME/projector/LO UX; full lecture ingestion. Secondary:
`langsmith-start-receipt-offline-stamp`.

S8 stays closed. Branch `dev/lesson-planning-2026-07-09`.

---

# Current Context Addendum - 2026-07-09 Session 28

**Step 1 DONE:** Phase-2 evolutionary bridge
`phase2-evolutionary-planning-to-selection-bridge` =
COMPLETE-with-named-fenced-residuals at `20246475` (pushed). W1–W4 banked;
W5 compose not claimed; §4.1 evolution rule canonicalized.

**Step 2→3:** see addendum above (handoff CLOSED same session).

S8 stays closed. Branch `dev/lesson-planning-2026-07-09`.

---

# Current Context Addendum - 2026-07-09 Session 27

**S8 stays FULLY COMPLETE — do not reopen** (operator). Post-S8 Irene-literal
gate **MET**: Gary preserve-over-condense (`0fb2b2cf`) + Pass-1 fidelity emit
recovery (`6783b54b`) + authentic classic-condense witness `235f2b82…` (no stamp;
`calls_made=2`; creative/literal exports). Pass-2 figure/numeral under
classic-condense = **parked HELR**. Cursor dual-agent-family surfaces landed
(`.cursor/rules/bmad-dual-agent-families.mdc` + `.cursor/agents/` stubs).

**Next frontier (bigger gains):** Phase-2 spine
`lesson-plan-directs-production-collateral-to-selection-edge` (primary candidate),
or operator-picked real HAI/PHS ingestion / LO ratification / course-SME routing.
Secondary hygiene only: `langsmith-start-receipt-offline-stamp`.

---

# Current Context Addendum - 2026-07-09 Session 26

**Class D wrapup** — shadow-monitor lane for S7 Phase-2 A-D closed; session
protocol START/WRAPUP Step 4a hardened so
`_bmad-output/implementation-artifacts/sprint-status.yaml` is the canonical
Kanban ledger (update whenever epic/story status changed; do not skip merely
because the file was untouched mid-session). Product next-gate unchanged from
Session 25: `irene-text-literal-supersedes-styleguide-truncation`. S8 remains
FULLY COMPLETE.

---

# Current Context Addendum - 2026-07-09 Session 25

**S8 FULLY COMPLETE** (Quinn R6 Two-clock synthesis; party A/A/B/B → R6).
Binding letter: `_bmad-output/implementation-artifacts/s8-close-letter-claim-envelope-2026-07-08.md`.

Terminal AFK HIL walk on Tejal Part-4 with guide
`hil-2026-apc-crossroads-classic-preserve`: trial
`1bd08699-614d-4412-ad52-bbe6edb1d6c5`; evidence
`_bmad-output/implementation-artifacts/evidence/s8-tejal-p4-terminal-walk-20260709T004657/`;
`final_status=completed`, workbook.md/.docx present. Product fixes that cleared
the path: title-residue soft-bind (`8f6e861c`); classic-preserve sibling
(`df0229e5`) — **approved classic `condense` left frozen** (operator policy).
Prior classic-condense walk `62308889…` failed Irene figure-contradiction — do
**not** claim that path green.

**Next gate:** `irene-text-literal-supersedes-styleguide-truncation` (filed).
Secondary: `langsmith-start-receipt-offline-stamp`. Do not reopen S8.

---

# Current Context Addendum - 2026-07-08 Session 24

**S8 was CLOSED on claim envelope** (later promoted FULLY COMPLETE 2026-07-09 —
see Session 25). Historical: AFK HIL composed-start proof trial
`9b6dc48b-031a-4b02-870c-ab7f76047c8d` stopped at `gamma.export.brief-unmatched`.

---

# Current Context Addendum - 2026-07-08 Session 23

S8 full-close corpus selection was unblocked; Session 24 closed S8 on the claim
envelope (see above). Historical note: the operator named
`course-content/courses/tejal-c1m1-p4-assessments-bridge` as the proof corpus
with expected bundle `narrated-deck-with-workbook`, HIL operator `juanl`, and an
explicit Tejal exception. BMAD party ratified the exception in
`_bmad-output/implementation-artifacts/s8-tejal-p4-proof-corpus-ratification-2026-07-08.md`.
An earlier no-shortcut trial-start attempt timed out at compose (trail only);
the Session 24 AFK HIL driver cleared that gate with a long wall-clock budget.

---

# Current Context Addendum - 2026-07-08 Session 22

S8 has advanced beyond the first selection-edge slice. Commit `282ea82f` closed the local runtime edge `ratified lesson-plan collateral intent -> BUNDLE_CATALOG -> ComponentSelection -> production runner`; this session adds the ratified planning-input wrapper path in `app/marcus/lesson_plan/collateral_selection.py`, so a wrapper carrying `input_bundle: LessonPlanningInputBundle` resolves `input_bundle.component_selection` only through an exact closed `BUNDLE_CATALOG` match. It fails closed on no-match, duplicate catalog match, or conflicting explicit `bundle_id`, and still does not touch `app/marcus/lesson_plan/composition.py` or `app/models/state/component_selection.py`. Evidence/artifact: `_bmad-output/implementation-artifacts/s8-planning-input-selection-contract-2026-07-08.md`; final validation: focused S8 regression 32 passed, resolver suite 15 passed, ruff clean, and local CLI witnesses `12345678-1234-4234-8234-123456789ac1` / `8ace18c2-df69-49df-990a-e97404090102` resolved the HAI Story D input-bundle wrapper to `narrated-deck-with-motion`. The supplemental full-seat party done-bar discharged the planning-checkpoint F-302 concern, while still ruling that full S8 close requires the remaining prose/workflow lane and an operator-named corpus + HIL composed proof if the close claim is "S8 complete."

Next gate: `_bmad-output/implementation-artifacts/s8-full-close-proof-preflight-2026-07-08.md` records the full-close stop condition. S8 remains open until the operator names the proof corpus, the local Marcus-SPOC runtime runs that corpus with real HIL verdicts, and BMAD party mode concurs that S8 itself is closed. Keep real HAI/PHS ingestion, PHS B-2 renames, LO-ratification UX, course/SME routing, collateral projector families, and Batch LLM/LiteLLM token-efficiency mode deferred unless explicitly selected by a later BMAD/operator decision.

---

# Current Context Addendum - 2026-07-08 Session 21

Phase-2 A-D course-source substrate is complete on `dev/workbook-2026-07-06`; implementation commits are pushed through `03c0db43`. Story A (`7174b366`) added the course-source registry/manifests and broad-root guard, and is now late-backfilled by `_bmad-output/implementation-artifacts/s7-phase2-story-a-close-backfill-2026-07-08.md`; Story C (`8210b90a`) added canonical asset/gap records; Story B (`80cdd68d`) added syllabus-derived metadata proposals; Story D (`03c0db43`) added lesson-planning input bundles with loader/builder, scoped gaps, source-purpose carry-through, and the `ComponentSelection` boundary contract. Story A backfill patched two edge cases: invalid direct `compose_and_write()` inputs fail before default model construction, and ignored source-role files no longer suppress source-availability gaps. Current validation: Story A/course-source slice 60 passed, ruff clean, manifest drift ok/ok.

The operator clarification remains binding: syllabi are reference/example sources, HAI 510 real content is pending lecture videos/slides/readings, and PHS 620 real content is pending authorized Confluence/Canvas access. Next spine: `lesson-plan-directs-production-collateral-to-selection-edge`, with S8 prose work interleaved per operator priority. Keep B-2 PHS renames and any real remote ingestion operator-gated. Historical caveat: F-103 was a real timing/process defect for Story A and is backfilled, not erased; F-104 remains a non-blocking wording polish; F-102 staging hygiene remains binding.

---
