# Slab 7a Retrospective - Inter-Gate Conversational Orchestration

**Closed draft:** 2026-04-29  
**Slab:** 7a - Inter-Gate Conversational Orchestration  
**Stories:** 7a.1, 7a.2, 7a.6, 7a.3, 7a.4, 7a.5, 7a.7, 7a.8  
**Author:** Codex via `bmad-retrospective`-shaped closeout draft during Story 7a.8  
**Authority:** Draft retrospective for Claude/operator finalization at Story 7a.8 T12.

---

## If you're reading this at Slab 7b T1, here's what you need

Five things:

1. **Trial-2 evidence is still the acceptance ceremony.** Slab 7a built the substrate and parity checks; operator-witnessed trial-2 or trial-2 dry-run evidence remains the Gate-2 close proof.
2. **SG-2 is 33 rows, not 34.** The operator-ratified 2026-04-29 amendment corrected bookkeeping while preserving the no-row-dropped invariant. The row-count CI guard now enforces exactly 33.
3. **The NEW cycle worked repeatedly.** Claude specification, Codex development, and Claude review/commit closed six Codex-developed Slab 7a stories cleanly; 7a.7 was the documented exception where Claude developed directly.
4. **The 7a.5 M3 contract fix is the import-boundary precedent.** Implementation belongs under `app.models.state.specialist_summary_artifacts`; `app.marcus.orchestrator.specialist_summary_writer` remains a facade.
5. **Slab 7b inherits deferred trial artifacts.** If trial-2 has not run before final close, activate `slab-7a-trial-2-golden-trace-fixtures-deferred-to-slab-7b` as the precise golden-trace follow-on.

---

## Commitments Landed Across Slab 7a

| Commitment | Closure Evidence |
|---|---|
| Directive composition closes trial-475 Gap 2 | 7a.1 + 7a.2 orchestration-only manifest registration |
| Manifest-derived active terminal gates | 7a.2 `production_gate_ids(manifest)` returns `{G1, G2C, G3, G4}` |
| 11-specialist vocabulary roster | 7a.6 `SpecialistId` import-time floor |
| 33-row operator-control parity floor | 7a.6 scaffold + 7a.8 metadata coverage and row-count checks |
| Pre-gate Marcus proposals | 7a.3 single shared call site and template suite |
| Per-slide review substrate | 7a.4 subgraph, HTML skeleton, max-3 revise invariant |
| Conversation persistence and summaries | 7a.5 SHA256 chain + specialist-summary writer facade convention |
| A2 terminal gate shims | 7a.7 G1/G2C/G3/G4 shims and Composition Smoke |
| Closeout tripwires and invariant suite | 7a.8 calibration tripwire, engagement report, duality boundary, NFR-CG block |

---

## Cycle Lessons

**PATCH-cycle frequency was healthy but real.** 7a.1 and 7a.2 needed remediation; 7a.4 needed a golden-fixture patch. 7a.3, 7a.5, 7a.6, and 7a.7 closed with no blocking patches. The pattern is useful: integration and schema-adjacent stories are where review effort pays off most.

**Halt-and-adapt worked best when tied to a named invariant.** Examples: PyYAML rather than ruamel, 33-row SG-2 correction, and the 7a.5 import-boundary violation. Each was resolved by naming the invariant, not by broad refactoring.

**Facade modules are now an established repair pattern.** The 7a.5 specialist-summary writer fix preserved both call directions: specialists import models; orchestration imports the facade. Use this pattern when a future implementation needs both runtime convenience and import-linter compliance.

**Composition Spec testing must stay structural and cheap.** The 7a.8 invariant suite proves the seven required sections are still represented by live artifacts without re-running every underlying test in duplicate.

---

## Deferred-Inventory Consultation

Consulted: `_bmad-output/planning-artifacts/deferred-inventory.md` on 2026-04-29.

| Entry | Slab 7a Verdict |
|---|---|
| Slab 7b sandbox-AC inventory PR | Reactivate at Slab 7b PRD authoring before any Slab 7b story opens. |
| Slab 7a-8 golden-trace fixtures from trial-2 | Keep active; if trial-2 has not run at close, rename or alias to `slab-7a-trial-2-golden-trace-fixtures-deferred-to-slab-7b`. |
| Slab 7a-4 HTML review-pack full styling | Keep deferred; trial-2 should inform actual styling needs. |
| Slab 7a-7 + Doc-7-D documentation-completion follow-on | Keep deferred until post-trial evidence exists. |
| Polish-pass deferred items | Keep deferred to Doc-7-D or reader-friction-driven doc pass. |
| Slab 7a impact assessment update for fold flags | Keep deferred to Doc-7-D; not a code blocker. |
| 7a-2 deferred resume-mode multi-gate pause | Keep deferred; current tests intentionally assert the interim GateBypassError behavior. |
| 7a-1 resume-mode directive rederive | Keep deferred; safe under current Path Z first-contribution-wins. |
| 7a-1 trial-start guide augment | Keep deferred as operator-doc polish after trial-2 evidence. |

No entry is ready to implement inside 7a.8 except the trial-2 golden-trace naming cleanup, which belongs to Claude/operator closeout if trial-2 evidence is absent.

---

## Slab 7b Kickoff Readiness

Hard gates:

- [ ] Operator Gate-2 evidence ceremony pasted into Story 7a.8 Completion Notes.
- [ ] `silent_bypass_events: 0` confirmed in trial-2 or trial-2 dry-run `run_summary.yaml`.
- [ ] Slab 7b sandbox-AC inventory PR scoped before live API stories open.
- [ ] Golden-trace fixture disposition recorded: committed from trial-2, or explicitly deferred to Slab 7b.

Soft gates:

- [ ] Review whether multi-gate resume remains acceptable as GateBypassError or now needs true pause-and-resume.
- [ ] Harvest trial-2 operator-friction evidence before Doc-7-D documentation cleanup.
- [ ] Re-check Composition Spec Section 11 triggers after trial-2 evidence, not just code substrate.

---

## Closing Note

Slab 7a moved the migrated runtime from a terminal-gate-only skeleton toward explicit inter-gate orchestration substrate. The largest remaining risk is not code absence inside 7a.8; it is evidence absence until the operator-witnessed trial-2 ceremony runs. Slab 7b should start from evidence, not assumptions.
