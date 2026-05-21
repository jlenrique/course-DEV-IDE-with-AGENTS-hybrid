# Migration Story 7b.12: Slab 7b Integration + Parity-Test Suite Aggregation + Closeout

**Status:** review
**Sprint key:** `migration-7b-12-integration-parity-suite-closeout`
**Epic:** Slab 7b — Specialist Body Activation Eleven (`migration-epic-slab-7b-specialist-activation-eleven`)
**Pts:** 4
**Gate:** **dual-gate** (per `docs/dev-guide/migration-story-governance.json` v2026-04-29-slab7b-twelve-stories, story `7b-12`; rationale: `operator_acceptance_gate + invariant_preservation`; mirrors Slab 7a 7a.8 precedent + Murat integration-tier risk argument)
**K-target:** ~1.6× (band-floor 1.8K; ~3K target; **k_contract tripwire 4.8K** per Round-(e) E6/Murat)
**Authored:** 2026-04-29 via `bmad-create-story` workflow.
**Wave:** 6 — slot 1 (strict-last; opens only after ALL 11 prior Slab 7b body stories `done`).
**Author binding:** Claude (per NFR-CG17 + D21; integration story remains Claude-authored under NEW CYCLE — Claude spec → Codex dev+tests → Claude T11 review + T12 close).
**FR coverage:** 8 FR-line aggregation + 4 NFR closeout blocks — FR88, FR101, FR102, FR103, FR104, FR105, FR106, FR107; NFR-CG12-CG20 (full block; 9 entries inc. CG14a); NFR-I9-I13 (full block; 5 entries); NFR-OD3-OD6 (full block; 4 entries); NFR-T9/T10/T11/T11a/T11b/T12 cross-cut.

**Standing-guardrail enforcement:**
- **SG-1 AGGREGATED assertion HERE** — `tests/parity/test_eleven_specialists_addressable.py` enumerates 11 specialists; name-set equality (Texas / Quinn-R / Vera / Irene / Tracy / Gary / Kira / Wanda / Enrique / Dan + Compositor); CI required check.
- **SG-2 AGGREGATED assertion HERE** — `tests/parity/test_mapping_checklist_status.py` asserts ~28 row improvements vs pre-Slab-7b baseline; deferred-rows (§05B / §6.2 / §6.3 / §7.5 / §14.5 / §15) pinned to pre-Slab-7b status.
- **SG-3 AGGREGATED assertion HERE** — Composition Spec invariant test suite (§3.1 / §3.5 / §3.6 / §6 / §9 / §10 / §11) carry-forward + new §10 entries (one per body story; ~11 entries).
- **SG-4 AGGREGATED assertion HERE** — `tests/parity/test_skill_md_sanctum_alignment.py` final form (11 specialist rows; Class-D2 Compositor branch per D20); FR101 parity-test bound to `.github/workflows/specialist-parity.yml`.

**Implementation cycle (NEW CYCLE):** Claude spec → Codex dev+tests → Claude review+commit. **DUAL-GATE — operator-witnessed Gate-2 evidence ceremony required at T10/T11 boundary** (T-task list reflects).

---

## T1 Readiness Block

**Predecessor state (verified at authoring 2026-04-29):**

ALL 11 prior Slab 7b body stories MUST be `done` before 7b.12 dev opens (strict prereq):
- 7b.1 (Texas hardening; Class A) — DONE 2026-04-29
- 7b.2 (Quinn-R hardening; Class A) — DONE 2026-04-29
- 7b.3 (Vera hardening; Class A) — DONE 2026-04-29
- 7b.4 (Irene Pass-1 refresh; Class B) — DONE 2026-04-29
- 7b.5 (Tracy port-shape + sidecar; Class C+) — DONE 2026-04-29
- 7b.6 (Gary port-shape; Class C; Wave-3 first port) — DONE 2026-04-29
- 7b.7 (Kira port-shape; Class C) — DONE 2026-04-29
- 7b.8 (Enrique port-shape; Class C) — pending Codex dev
- 7b.9 (Wanda port-shape onto scaffold; Class C; Wave-4) — pending Codex dev
- 7b.10 (Dan greenfield; Class D1; Wave-5a) — pending Codex dev
- 7b.11 (Compositor greenfield; Class D2; Wave-5b) — pending Codex dev

**T1 hard checkpoint:** confirm ALL 11 prior body stories are `done` in BOTH spec status + `_bmad-output/implementation-artifacts/sprint-status.yaml`. If ANY prior story is NOT `done`, HALT and surface to operator.

**Live substrate (verified at authoring; updates as prior stories close):**
- 7b.1: Texas FR89-compliant six-canonical-artifacts contract + G0 6-dim rubric + word-count belt-and-suspenders (`RetrievalScopeError` floor) + `SanctumParityTestBase` + chain-test base + class-conformance validator + Errata 4 flat-layout ratification (Wave-1 substrate gate).
- 7b.2: Quinn-R authorized-storyboard.schema.json + Pydantic-v2 schema-regen utility + 6-file BMB sanctum at `_bmad/memory/bmad-agent-quinn-r/`.
- 7b.3: Vera Pass-2 G4 evaluator + 6-file BMB sanctum at `_bmad/memory/bmad-agent-vera/`.
- 7b.4: Irene Pass-1 refresh; class-B template proven; chain-test extends Wave-1 base.
- 7b.5: Tracy Class-C+ port-shape + sidecar bundle (4-file sidecar pattern landed; required_ac_reference_paths Texas retrieval-contract per Round-(e) E4); Class-C+ template proven.
- 7b.6: Gary Class-C port-shape (Wave-3 first port; tripwire NOT fired at 1.3K; Class-C template proven 1×); two-SKILL.md convention party-mode-ratified 4/4 unanimous (Round-(f)).
- 7b.7: Kira Class-C port-shape; two-SKILL.md inheritance proven 2×; Class-C validator extension NIL (template proven inheritable).
- 7b.8: Enrique Class-C port-shape; two-SKILL.md inheritance proven 3×; provider-agnostic validator method-name rename (deferred-inventory follow-on `class-c-validator-method-name-provider-agnostic-rename` closes here).
- 7b.9: Wanda Class-C port-shape onto scaffold-v0.2 (`bmad-create-specialist`); two-SKILL.md inheritance proven 4×.
- 7b.10: Dan Class-D1 greenfield (sandbox-AC `dan-api-tbd-pending` resolved at story-T1; party-mode-gated if third-party-API per Round-(b) Mary B1).
- 7b.11: Compositor Class-D2 greenfield via FR111 scaffold-v0.2-D2-pipeline (LANDED Wave 0); pipeline-determinism harness (H-Pipeline ≥99%); conditional_dual_gate_escalation hard-bound at K>4.0 per Round-(e) E1/John.

**Block-mode trigger paths touched by this story:** none (7b.12 wires substrate together; no manifest/pack/lockstep change). 5 new CI-workflow files land additively.

**Gate-mode rationale (from governance JSON 7b-12):**
> Slab 7b Wave 6 strict-last (DUAL-GATE per Slab 7a 7a-8 precedent + Murat integration-tier risk argument; Claude). Integration + parity-test suite aggregation (FR101 + FR105 + FR102 binding to `.github/workflows/specialist-parity.yml` + `activation-contract.yml` + `mapping-checklist.yml` + `substrate-frozen-paths-check.yml` + `codex-scope-audit.yml`) + per-specialist operator-reference docs (NFR-OD3 × 11) + sanctum-alignment matrix doc (NFR-OD4 + FR103) + operator-control parity table +11 rows (FR104) + ~28 mapping-checklist row improvements (NFR-I11) + 5-API live-binding smoke (operator-gated AC-12-B; gamma/kling/elevenlabs/wondercraft/dan-api-tbd-resolved; ≤3 canaries/API; cost ≤$0.40/canary) + trial-2 cost-projection dry-run (Round-(a) John A1; SR-T6 mitigation). SG-1 + SG-2 + SG-3 + SG-4 AGGREGATED structural enforcement. MVP Exit Gate verification (G2 + 9-of-11). Slab 7b Close Gate verification (G3 + 11 cascade-reading).

**K-tripwire (BINDING per dual-gate per Round-(e) E6/Murat k_contract):** >4.8K LOC OR >44 active tests (excluding skipped placeholders) → close round + party-mode triage; four named remediation paths from Round-(a) A1 (scope-cut / budget-exception / trial-redesign / Slab-7c precondition deferral; e.g., defer NFR-OD3 docs to follow-on).

**T1 conclusion:** Implementation proceeds AFTER all 11 prior Slab 7b body stories close. Hard checkpoint: confirm ALL 11 prior stories are `done` in BOTH spec status + sprint-status.yaml.

**Sandbox-AC pre-flight:** `validate_migration_story_sandbox_acs.py <this-spec>` PASS. Operator-gated AC blocks: AC-12-G (5-API live-binding smoke), AC-12-H (trial-2 cost-projection dry-run), AC-12-N (Gate-2 evidence ceremony) — all flagged `(operator-gated)` per NFR-T11a.

---

## Story

As the operator + the Slab-7b-completeness gate,
I want a parity-test suite at `tests/parity/test_skill_md_sanctum_alignment.py` (final 11-row form) + per-specialist activation-contract enforcement at `tests/parity/test_eleven_specialists_addressable.py` + ~28 mapping-checklist row improvements at `tests/parity/test_mapping_checklist_status.py` + a sanctum-alignment matrix doc + an operator-control parity table extension + 11 per-specialist operator-reference docs + a 5-API live-binding smoke evidence batch + a trial-2 cost-projection dry-run + the substrate-frozen-paths-check workflow + the codex-scope-audit workflow + the credential-rotation register + per-specialist rate-limit budgets + the Slab 7b retrospective + closeout artifacts,
so that all four Standing Guardrails (SG-1 11-roster / SG-2 33-row / SG-3 Composition Spec / SG-4 sanctum-alignment) are AGGREGATED and structurally enforced at PR-merge gate; the MVP Exit Gate (G2 + 9-of-11) is verifiable at Slab 7b close; the Slab 7b Close Gate (G3 + 11 cascade-reading) is verifiable; trial-2 launches with auditable evidence; and Slab 7c (or whatever follows) opens with a known-good substrate.

---

## Acceptance Criteria

### AC-7b.12-A — FR101 + FR102 parity-test final form (SG-4 aggregated)

**Given** the FR101 + FR102 parity-test aggregation
**When** the dev-agent authors `tests/parity/test_skill_md_sanctum_alignment.py` final form (extends `SanctumParityTestBase` from 7b.1 T2)
**Then** all eleven specialists pass — Texas / Quinn-R / Vera / Irene / Tracy / Gary / Kira / Wanda / Enrique / Dan are option-a sanctum-aligned (6-file BMB pattern at `_bmad/memory/bmad-agent-{name}/`); Compositor passes the Class-D2 branch (4-file sidecar pattern per D20)
**And** the test runs <120s aggregate per NFR-T12 SLA on standard CI runner
**And** `.github/workflows/specialist-parity.yml` is landed + bound as required CI check (NFR-I9)
**And** the workflow runs at every PR merge (NFR-I9 binding).

### AC-7b.12-B — FR105 per-specialist activation-contract aggregation (SG-1 aggregated)

**Given** the FR105 per-specialist activation-contract suite distributed across 11 body stories
**When** the dev-agent authors `tests/parity/test_eleven_specialists_addressable.py` (SG-1 aggregator)
**Then** all 11 individual specialist activation-contract tests pass; name-set equality (`{texas, quinn_r, vera, irene, tracy, gary, kira, wanda, enrique, dan, compositor}`); class-shaped templates honored per NFR-I12 (A/B/C/C+/D1/D2 inheritance verified)
**And** `len(roster) == 11` invariant asserted
**And** `.github/workflows/activation-contract.yml` is landed + bound as required CI check (NFR-I10).

### AC-7b.12-C — FR103 + NFR-OD4 sanctum-alignment matrix doc

**Given** the FR103 + NFR-OD4 sanctum-alignment matrix authoring
**When** the dev-agent authors the matrix docs
**Then** `docs/dev-guide/specialist-sanctum-alignment-matrix.md` (dev-doc) AND `docs/operator/specialists/sanctum-alignment-matrix.md` (operator-doc twin) both exist with 11 rows (one per specialist + alignment-or-exception verdict + rationale link)
**And** each row references the per-specialist FR108 sanctum-alignment-checklist verdict + the BMB sanctum directory path + the SKILL.md path (or two-SKILL.md paths for Class-C per Round-(f) ratification)
**And** the dev-doc twin links to the operator-doc twin per Cora `§Sanctum exception` anchor pattern.

### AC-7b.12-D — FR104 operator-control parity table +11 rows

**Given** the FR104 operator-control parity table extension
**When** the dev-agent authors the +11 rows
**Then** `docs/operator/legacy-vs-langgraph-control-parity.md` carries 11 new rows (one per specialist body activation; legacy lever → migrated lever → back-compat shim status → end-to-end test pointer per FR110 template)
**And** each row is authored pre-class-entry per FR104 (each body story author already drafted; 7b.12 aggregates) — verified by counting that 11 rows reference Slab 7b activation evidence.

### AC-7b.12-E — NFR-OD3 per-specialist operator-reference docs

**Given** the NFR-OD3 per-specialist operator-reference docs
**When** the dev-agent authors the 11 docs
**Then** `docs/operator/specialists/<name>.md` exists for each of the 11 activated specialists (`texas.md`, `quinn-r.md`, `vera.md`, `irene.md`, `tracy.md`, `gary.md`, `kira.md`, `wanda.md`, `enrique.md`, `dan.md`, `compositor.md`)
**And** each doc follows the OPERATOR / INPUTS / OUTPUTS / REFERENCE four-section structure per Slab 7a 7a.7 precedent
**And** each doc cites the corresponding `_bmad/memory/bmad-agent-{name}/` sanctum (or `skills/bmad-agent-compositor/` Class-D2 sidecar location for Compositor).

### AC-7b.12-F — NFR-I11 mapping-checklist row-status invariant

**Given** the NFR-I11 mapping-checklist row-status invariant
**When** the dev-agent authors `tests/parity/test_mapping_checklist_status.py`
**Then** the test asserts ~28 row improvements (per Round-(a) A-10 R3 amendment) on rows owned by activated specialists; deferred rows (§05B / §6.2 / §6.3 / §7.5 / §14.5 / §15) retain pre-Slab-7b status legend (NOT regressed)
**And** `.github/workflows/mapping-checklist.yml` is landed + bound as required CI check
**And** any row regression vs pre-Slab-7b baseline → CI fails.

### AC-7b.12-G — FR106 cache-hit-rate harness aggregation (operator-gated)

**Given** the FR106 cache-hit-rate harness aggregation (10 LLM specialists + 1 Compositor pipeline-determinism)
**When** the dev-agent runs the harnesses at green-light cadence
**Then** all 10 LLM specialists report `median[2:] >= 85%` post-warm-up; Compositor reports H-Pipeline ≥99% rate
**And** harness evidence pasted into Completion Notes (operator-gated per NFR-T11a; AC-12-G-B style block).

**(operator-gated; AC-12-G-B):**

```bash
.venv/Scripts/python.exe scripts/utilities/run_cache_hit_harness.py --all-specialists --median-from-index 2 --threshold 0.85 > _bmad-output/implementation-artifacts/7b-12-cache-hit-harness-evidence.txt
.venv/Scripts/python.exe scripts/utilities/run_pipeline_determinism_harness.py --threshold 0.99 > _bmad-output/implementation-artifacts/7b-12-pipeline-determinism-harness-evidence.txt
```

Operator pastes verbatim stdout into Completion Notes.

### AC-7b.12-H — Trial-2 cost-projection dry-run (Round-(a) John A1; operator-gated)

**Given** the trial-2 cost-projection dry-run (Round-(a) John A1 amendment; SR-T6 mitigation)
**When** the dev-agent runs the cost-projection
**Then** projected Trial-2 cost ≤ BS-3 ceiling (per Journey 5 fork)
**And** if projection exceeds ceiling, the story HALTs with one of four named remediation paths (scope-cut / budget-exception / trial-redesign / Slab-7c precondition deferral) + party-mode escalation
**And** projection methodology: per-specialist token counts × per-specialist rate × volume estimate for Trial-2 storyboard (cited from PRD §Journey 5).

**(operator-gated; AC-12-H-B):**

```bash
.venv/Scripts/python.exe scripts/utilities/project_trial_2_cost.py --evidence-path _bmad-output/implementation-artifacts/7b-12-trial-2-cost-projection.json
```

Operator pastes verbatim JSON into Completion Notes; verifies projection ≤ BS-3 ceiling.

### AC-7b.12-I — 5-API live-binding smoke (Wave 6 operator-gated)

**Given** the 5-API live-binding smoke (Wave 6 operator-gated; cost ≤$0.40/canary; ≤3 canaries/API per governance JSON 7b-12 k_contract)
**When** the operator runs the 5-API smoke
**Then** each of the 5 APIs (gamma / kling / elevenlabs / wondercraft / dan-api-tbd-resolved) responds 200-OK with valid response shape
**And** smoke evidence pasted into Completion Notes (operator-gated AC-12-I-B style)
**And** total smoke spend ≤ 5 × 3 × $0.40 = $6.00 ceiling
**And** if any API fails, story HALTs + party-mode escalation.

**(operator-gated; AC-12-I-B):**

```bash
.venv/Scripts/python.exe scripts/utilities/run_5_api_smoke.py --apis gamma,kling,elevenlabs,wondercraft,dan-api-tbd-resolved --max-canaries-per-api 3 --max-cost-per-canary 0.40 --evidence-path _bmad-output/implementation-artifacts/7b-12-5-api-smoke-evidence.json
```

Operator pastes verbatim JSON into Completion Notes; verifies all 5 PASS + total cost ≤ $6.00.

### AC-7b.12-J — Substrate-frozen-paths-check workflow (FR113 + NFR-I13)

**Given** the FR113 substrate-frozen-paths-check workflow
**When** the dev-agent commits the integration story
**Then** `.github/workflows/substrate-frozen-paths-check.yml` is landed + bound as required CI check
**And** the workflow asserts no diff hunk touches the canonical frozen paths (`app/marcus/orchestrator/dispatch_adapter.py:70-95` substrate-as-floor invariant per FR113 + NFR-I13) absent ceremony commit
**And** ceremony commit pattern: commit message MUST contain `[substrate-ceremony]` token + party-mode-consensus link in body.

### AC-7b.12-K — Credential-rotation register + per-specialist rate-limit budgets

**Given** the credential-rotation register (NFR-CG19) + rate-limit budgets (NFR-CG20)
**When** the dev-agent runs the closeout audit
**Then** `state/config/credential-rotation-register.yaml` carries 5 rows (gamma / kling / elevenlabs / wondercraft / dan-api-tbd-resolved); each row declares `last_rotated_at` + `rotation_cadence_days` + `next_rotation_due_at` (calendar-tracked per NFR-CG19)
**And** per-specialist rate-limit budget declared in each `app/specialists/<name>/config.yaml` for the 5 API-bound specialists (Gary/Kira/Enrique/Wanda/Dan); LLM-specialist config carries `rate_limit_rps` + `rate_limit_burst` keys
**And** rate-limit-budget aggregator test at `tests/parity/test_rate_limit_budgets_declared.py` PASSES (5 specialists × required keys present).

### AC-7b.12-L — NFR-OD6 codex-scope-audit workflow

**Given** the NFR-OD6 codex-scope-audit workflow
**When** the closeout CI run executes
**Then** `.github/workflows/codex-scope-audit.yml` passes — no workflow file references `codex` or invokes Codex CLI absent governance-JSON `7b-{N}` entry naming Codex as author
**And** the workflow asserts a static check on `.github/workflows/*.yml` files; a violation blocks PR merge.

### AC-7b.12-M — NFR-CG block aggregated test (CG12-CG20 + CG14a)

**Given** the NFR-CG12-CG20 + NFR-CG14a closeout block (9 entries total)
**When** the dev-agent authors `tests/parity/test_nfr_cg_slab7b_block_aggregated.py` (mirrors 7a.8 NFR-CG block test pattern)
**Then** the test enumerates 9 cases (one per NFR-CG); each asserts the relevant artifact exists + meets the criterion:
- **NFR-CG12:** sandbox-AC validator returns zero warnings on EVERY Slab 7b story file (re-run at close).
- **NFR-CG13:** strict no-live-API in CI (VCR cassettes for any API-bound test; no live calls).
- **NFR-CG14:** Composition Spec §6 chain-test PR present for every body story (11 PRs).
- **NFR-CG14a:** chain-test base class at `tests/composition/_chain_test_base.py` consumed by every body story chain-test.
- **NFR-CG15:** Composition Spec §10 Decision Log entries present (one per body story; ~11 entries; aggregated into Composition Spec).
- **NFR-CG16:** anti-pattern catalog (A1-A18 + P1-P3) referenced; A11 Windows-portability throughout.
- **NFR-CG17:** Codex deployment binding honored — class-C/C+ stories Codex-authored per D21; Class-A/B/D1/D2 + integration Claude-authored.
- **NFR-CG18:** four-file-lockstep on every Pydantic touch (where applicable; e.g., 7b.2 Quinn-R schema-regen).
- **NFR-CG19:** credential-rotation register present + populated (per AC-K).
- **NFR-CG20:** rate-limit budgets declared per AC-K.

**And** all 9 cases pass.

### AC-7b.12-N — Operator-witnessed dual-gate Gate-2 evidence ceremony (T10/T11 boundary)

**Given** the dual-gate Gate-2 evidence ceremony
**When** Codex completes T1-T9 + G6 self-review
**Then** the operator runs the full focused + wider regression battery + sandbox-AC + lockstep + ruff + lint-imports + Composition Smoke + 5-API smoke + trial-2 cost-projection
**And** pastes verbatim stdout into Completion Notes
**And** verifies `_artifacts/trial-2/run_summary.yaml::silent_bypass_events == 0` (carries forward 7a.8 AC-D verification)
**And** Gate-2 PASS = operator signs off on all 14 evidence blocks (one per AC).

**(operator-gated; AC-12-N-B):**

Operator runs full Gate-2 ceremony script at `_bmad-output/implementation-artifacts/7b-12-gate2-evidence-commands.ps1` (authored by Codex at T9); pastes verbatim stdout into Completion Notes.

### AC-7b.12-O — MVP Exit Gate verification (G2 + 9-of-11)

**Given** the MVP Exit Gate (R8 amendment from PRD)
**When** Trial-2 is launched
**Then** Trial-2 reaches **G2 cleanly with real content from ≥9-of-11 specialists (≥3 per class)**; no fixture-stub fallback; no silent gate-bypass; SG-1/SG-2/SG-3 all green (SG-4 verified at Slab close, not MVP exit)
**And** `_artifacts/trial-2/g2_exit_evidence.yaml` carries 9-of-11 verification entry per specialist class.

### AC-7b.12-P — Slab 7b Close Gate verification (G3 + 11 cascade-reading)

**Given** the Slab 7b Close Gate (full-scope; R8 Mary clarification)
**When** Trial-2 reaches G3 close
**Then** Trial-2 reaches **G3 cleanly with real content from all 11 specialists** (cascade-reading verified per R8 Mary clarification — visible-content surfaces from 9 standalone-row specialists PLUS Pass-2-internal contributions from Wanda + Tracy verifiable via cascade audit logs); no mapping-checklist regression; SG-1/SG-2/SG-3/SG-4 all green
**And** `_artifacts/trial-2/g3_close_evidence.yaml` carries 11-cascade-reading verification.

### AC-7b.12-Q — BMAD sprint governance + closeout deliverables (D12 close protocol)

**Given** the BMAD sprint governance (CLAUDE.md)
**When** the integration story closes
**Then** `bmad-retrospective` runs (per `bmad-retrospective` skill);
**And** `_bmad-output/planning-artifacts/deferred-inventory.md` updated with Slab 7b-closing follow-ons (per CLAUDE.md "Deferred inventory governance" — Epic retrospective consultation point);
**And** `next-session-start-here.md` updated with Trial-2 launch (or Slab 7c precondition) hot-start;
**And** `_bmad-output/implementation-artifacts/sprint-status.yaml` reflects all 12 Slab 7b stories DONE + epic flipped `in-progress → done`;
**And** `_bmad-output/implementation-artifacts/slab-7b-retrospective.md` authored.

### AC-7b.12-R — N-item / anti-pattern / Composition Spec trace + dual-gate Gate-2 evidence

**N-item / Composition Spec / anti-pattern trace:** all 9 NFR-CG closeout cases (per AC-M) + SG-3 Composition Spec invariants (per SG-3 aggregated test) + 18 anti-pattern entries (A1-A18) cross-reference checked.

**Operator-witnessed dual-gate Gate-2 evidence ceremony (T10):** as AC-N — operator runs full battery + 5-API smoke + trial-2 cost-projection; pastes verbatim stdout. Operator also runs trial-2 (or trial-2 dry-run) and pastes the trial-2 close artifact paths into Completion Notes.

---

## Tasks / Subtasks

- [ ] **T1: Readiness review** — confirm ALL 11 prior Slab 7b body stories `done` in BOTH spec status + sprint-status.yaml; if ANY not-done, HALT.
- [ ] **T2: FR101 + FR102 parity-test final form** (AC-A) — extend `tests/parity/test_skill_md_sanctum_alignment.py` to 11-specialist final form; bind `.github/workflows/specialist-parity.yml` as required check.
- [ ] **T3: FR105 SG-1 aggregator** (AC-B) — author `tests/parity/test_eleven_specialists_addressable.py`; bind `.github/workflows/activation-contract.yml`.
- [ ] **T4: Sanctum-alignment matrix doc** (AC-C) — author dev-doc + operator-doc twins.
- [ ] **T5: Operator-control parity +11 rows** (AC-D) — aggregate 11 rows authored by body stories; verify count.
- [ ] **T6: Per-specialist operator-reference docs** (AC-E) — author `docs/operator/specialists/<name>.md` for each of 11 activated specialists.
- [ ] **T7: Mapping-checklist row-status test** (AC-F) — author `tests/parity/test_mapping_checklist_status.py`; bind `.github/workflows/mapping-checklist.yml`.
- [ ] **T8: Substrate-frozen-paths-check workflow** (AC-J) — land `.github/workflows/substrate-frozen-paths-check.yml`; bind as required check.
- [ ] **T9: Credential-rotation register + rate-limit budgets** (AC-K) — author `state/config/credential-rotation-register.yaml` (5 rows) + per-specialist `config.yaml` rate-limit keys + aggregator test.
- [ ] **T10: NFR-OD6 codex-scope-audit workflow** (AC-L) — land `.github/workflows/codex-scope-audit.yml`.
- [ ] **T11: NFR-CG block aggregated test** (AC-M) — author `tests/parity/test_nfr_cg_slab7b_block_aggregated.py` with 9 cases.
- [ ] **T12: Verification battery + DUAL-GATE Gate-2 operator ceremony** (AC-N + G + H + I) — Codex authors `7b-12-gate2-evidence-commands.ps1`; operator runs full battery + 5-API smoke + trial-2 cost-projection; pastes verbatim stdout.
- [ ] **T13: Codex G6 self-review** (Blind / Edge / Auditor) — output to `_bmad-output/implementation-artifacts/7b-12-codex-self-review-2026-04-XX.md`.
- [ ] **T14: Claude bmad-code-review + remediation + commit + Slab 7b CLOSEOUT** (AC-O + P + Q + R) — D12 close protocol + retrospective + trial-2 evidence.
- [ ] **T15: Slab 7b retrospective** (AC-Q) — author `_bmad-output/implementation-artifacts/slab-7b-retrospective.md` per `bmad-retrospective` skill.

---

## File Structure Requirements

**New (tests):** `tests/parity/test_eleven_specialists_addressable.py` (AC-B); `tests/parity/test_mapping_checklist_status.py` (AC-F); `tests/parity/test_nfr_cg_slab7b_block_aggregated.py` (AC-M); `tests/parity/test_rate_limit_budgets_declared.py` (AC-K).

**New (CI workflows):** `.github/workflows/specialist-parity.yml` (AC-A; FR102/NFR-I9); `.github/workflows/activation-contract.yml` (AC-B; NFR-I10); `.github/workflows/mapping-checklist.yml` (AC-F; NFR-I11); `.github/workflows/substrate-frozen-paths-check.yml` (AC-J; NFR-I13); `.github/workflows/codex-scope-audit.yml` (AC-L; NFR-OD6).

**New (docs):** `docs/dev-guide/specialist-sanctum-alignment-matrix.md` (AC-C); `docs/operator/specialists/sanctum-alignment-matrix.md` (AC-C operator twin); `docs/operator/specialists/{texas,quinn-r,vera,irene,tracy,gary,kira,wanda,enrique,dan,compositor}.md` (AC-E; 11 docs).

**New (state):** `state/config/credential-rotation-register.yaml` (AC-K).

**New (scripts):** `scripts/utilities/run_cache_hit_harness.py` (AC-G; if not pre-existing); `scripts/utilities/run_pipeline_determinism_harness.py` (AC-G; if not pre-existing); `scripts/utilities/project_trial_2_cost.py` (AC-H); `scripts/utilities/run_5_api_smoke.py` (AC-I).

**New (artifacts):** `_bmad-output/implementation-artifacts/7b-12-gate2-evidence-commands.ps1` (AC-N); `_bmad-output/implementation-artifacts/7b-12-codex-self-review-2026-04-XX.md` (T13); `_bmad-output/implementation-artifacts/slab-7b-retrospective.md` (T15).

**Modified:** `tests/parity/test_skill_md_sanctum_alignment.py` (AC-A; 11-specialist final form); `docs/operator/legacy-vs-langgraph-control-parity.md` (AC-D; +11 rows); `app/specialists/{gary,kira,enrique,wanda,dan}/config.yaml` (AC-K; +rate_limit_rps/rate_limit_burst keys); `_bmad-output/implementation-artifacts/sprint-status.yaml` + `next-session-start-here.md` + `_bmad-output/planning-artifacts/deferred-inventory.md` (AC-Q D12 close protocol).

**Do NOT modify:** specialist bodies (`app/specialists/<name>/_act.py`); `_bmad/memory/bmad-agent-{name}/` sanctum dirs (read-only consumers); `app/marcus/orchestrator/dispatch_adapter.py:70-95` (substrate-as-floor per FR113); manifest; pack; v4.2 prompt pack.

---

## Testing Requirements

**K-floor 14 + K-target ~25 active (per gate-shape band 1.8K + ~3K target; k_contract tripwire 4.8K):**
- 11 sanctum-alignment cases (AC-A; final form; one per specialist)
- 11 SG-1 specialist-addressable cases (AC-B; one per specialist)
- ~28 mapping-checklist row-improvement cases (AC-F; many parametrized)
- 9 NFR-CG block aggregated cases (AC-M)
- 1 substrate-frozen-paths-check (AC-J; structural)
- 5 rate-limit-budget cases (AC-K; one per API-bound specialist)
- 5 credential-rotation register cases (AC-K)

**Skipped placeholders:** 0 (all 11 specialists must be live by 7b.12 open per T1 hard checkpoint).

**K-tripwire (BINDING per dual-gate):** >4.8K LOC OR >44 active tests → close round + party-mode triage with four named remediation paths (scope-cut / budget-exception / trial-redesign / Slab-7c precondition deferral).

---

## Dev Notes

**Architecture compliance:** ALL Composition Spec invariants honored (§3.1/§3.5/§3.6/§6/§9/§10/§11); §11 trigger NEGATIVE for 7b.12 itself (additive parity tests + CI workflows + docs; aggregating substrate built by prior 11 stories); §10 entries from each body story referenced (~11 new entries; aggregated into the Composition Spec at close).

**Library/framework:** stdlib + PyYAML + Pydantic v2 + httpx (for 5-API smoke; live calls operator-gated only). NO new third-party deps for dev-agent path.

**Anti-patterns to avoid:** A1-A18 (full catalog) + P1-P3; A11 Windows-portability throughout; explicit citation of A12 (over-mocking) + A17 (test-data fixtures from prod) + P3 (cross-test side-effects) per NFR-CG16.

**Previous story intelligence:** 7b.1-7b.11 substrate is the input; 7b.12 wires it together + adds the parity test suite that proves the SG-1/2/3/4 floors are honored AGGREGATELY at PR-merge gate. Class-C two-SKILL.md convention (Round-(f) ratification 4/4 unanimous) is honored: sanctum-alignment matrix doc lists BOTH the persona-skill (`bmad-agent-{specialist}/SKILL.md`) AND API-mastery reference (`bmad-agent-{api-name}/SKILL.md`) where applicable.

**MVP Exit Gate vs Slab Close Gate distinction (R8 Mary clarification):** AC-O (MVP Exit) verifies G2 + 9-of-11 (≥3 per class); AC-P (Slab Close) verifies G3 + 11 cascade-reading (Wanda + Tracy contribute via Pass-2 cascade audit logs, not standalone rows). DO NOT conflate these two gates — they have different evidence requirements and different remediation paths.

**Trial-2 launch readiness:** AC-O (MVP Exit) is the trial-2 launch predicate. AC-P (Slab Close) is the trial-2 close predicate. Both must be GREEN at 7b.12 close for Slab 7b to be `done`.

**5-API live-binding smoke cost ceiling:** $6.00 total ceiling per AC-I. Per-canary cost ≤$0.40; ≤3 canaries/API per governance JSON 7b-12 k_contract. If any canary exceeds, story HALTs + party-mode escalation per Round-(a) A1 four-named-remediation-paths.

**References:**
- Epic Story 7b.12 (`_bmad-output/planning-artifacts/epics-slab-7b-specialist-activation-eleven.md` lines 990-1067).
- PRD §FR88/FR101/FR102/FR103/FR104/FR105/FR106/FR107 + §NFR-CG12-CG20 + §NFR-I9-I13 + §NFR-OD3-OD6 + §NFR-T9-T12.
- Governance JSON `7b-12` (lines 504-516; v2026-04-29-slab7b-twelve-stories).
- ALL 11 prior Slab 7b body stories (`migration-7b-{1..11}-*.md`).
- Slab 7a 7a.8 precedent (`migration-7a-8-integration-parity-test-suite-slab-7a-closeout.md`) — DUAL-GATE integration template; 7b.12 mirrors structure.
- Slab 7b PRD (`prd-slab-7b-specialist-activation-eleven.md`) §Success Criteria (BS-2 trial-2 readiness predicate; BS-3 cost ceiling).
- `docs/dev-guide/bmb-sanctum-alignment-checklist.md` (FR108; SG-4 source-of-truth).
- `docs/dev-guide/specialist-anti-patterns.md` (A1-A18 + P1-P3).
- `docs/dev-guide/specialist-migration-template.md` (R1-R14).
- CLAUDE.md (BMAD sprint governance + Deferred inventory governance + LangChain/LangGraph migration sandbox-AC).

---

## Dev Agent Record

(populated by Codex dev-story T1-T13 and Claude T14-T15 on 2026-XX-XX)

### Implementation Plan

(authored by Codex at T1)

### Debug Log

(authored by Codex at T1-T11)

### Completion Notes

**Gate-2 ceremony executed 2026-05-01 17:55 UTC by operator.** Transcript at [`7b-12-gate2-evidence-2026-05-01-1351.utf8.txt`](7b-12-gate2-evidence-2026-05-01-1351.utf8.txt) (UTF-8; 11 KB; re-encoded from PowerShell `Tee-Object` UTF-16 LE original at `7b-12-gate2-evidence-2026-05-01-1351.txt`).

**Verdict matrix (14 evidence blocks):**

| # | Block | Result | Notes |
|---|---|---|---|
| 1 | 7b.12 focused parity slice | ✅ **55 passed in 3.32s** | covers SKILL.md sanctum-alignment + 4 new parity tests + pipeline-determinism harness |
| 2 | 11 per-specialist activation contracts | ✅ **78 passed in 3.04s** | full Slab 7b coverage (A/B/C+/C/D1/D2; 11 contracts) |
| 3 | Wider regression slice (`-p no:randomly`) | ✅ **1389 passed, 21 skipped, 1 deselected in 161.63s** | +1 vs cycle-1 baseline (1388); zero regressions |
| 4 | Pipeline-manifest lockstep | ✅ **exit=0** | trace at `reports/dev-coherence/2026-05-01-1755/check-pipeline-manifest-lockstep.PASS.yaml` |
| 5 | Sandbox-AC validator (12 stories) | ✅ **PASS** — no violations |
| 6 | Class-conformance validator | ✅ **PASS: 11 activation contract files conform** |
| 7 | Live-API detector (NFR-CG13 strict) | ✅ **PASS: scanned 81 test files; no forbidden imports** |
| 8 | Code quality (story-scoped ruff) | ✅ **All checks passed** |
| 9 | Import-linter (9 contracts) | ✅ **9 kept, 0 broken** |
| 10 | AC-G.1 cache-hit-rate harness | ⚠️ **`verdict: not_run`** by design (10 specialists fail-closed) |
| 11 | AC-G.2 H-Pipeline determinism | ✅ **rate=1.0; PASS** (10 iterations; threshold 0.99) |
| 12 | AC-H trial-2 cost-projection | ✅ **PASS** at $7.735 vs $25 BS-3 ceiling (delta −$17.265); placeholder DEFAULT_INPUTS warning emitted |
| 13 | AC-I 5-API live-binding smoke | ⚠️ **`verdict: not_run`** by design (5 APIs fail-closed) |
| 14 | AC-O / AC-P operator-driven Trial-2 | 📝 deferred-to-Trial-2 ceremony (Slab 7a precedent) |

**JSON evidence emitted:**
- [`7b-12-cache-hit-harness-evidence.json`](7b-12-cache-hit-harness-evidence.json) — `verdict: not_run`; 10 specialists fail-closed
- [`7b-12-pipeline-determinism-evidence.json`](7b-12-pipeline-determinism-evidence.json) — `verdict: PASS`; rate=1.0
- [`7b-12-trial-2-cost-projection.json`](7b-12-trial-2-cost-projection.json) — `verdict: PASS`; projected_cost_usd=$7.735
- [`7b-12-5-api-smoke-evidence.json`](7b-12-5-api-smoke-evidence.json) — `verdict: not_run`; 5 APIs fail-closed

**Party-mode binding decisions (2026-05-01):**

Round 1 — AC-G.1 cache-hit + AC-I 5-API path: **UNANIMOUS 4/4 path (c)** (John+Mary+Amelia+Murat). Accept fail-closed `not_run` posture as DOCUMENTED-INTENT skeleton evidence per cycle-1 PATCH-1 contract. Filed `slab-7c-live-harness-evidence` to deferred-inventory. Rationale highlights: Murat — option (a) raises risk by introducing new code at integration-tier story close; option (b) is "partial coverage theater"; (c) honors the regime working as designed. Mary — AC-N footnote already satisfied by AC-H BS-3 sub-clause ($7.735 < $25). Amelia — `verdict: not_run` IS the AC-G.1/AC-I documented posture per cycle-1 PATCH. John — marginal user value of authoritative live verdicts today is zero vs cost.

Round 2 — Inline Trial-2 vs straight-to-retrospective: **UNANIMOUS 4/4 option (9)** (John+Mary+Amelia+Murat). Skip directly to Slab 7b retrospective T15; defer AC-O+AC-P to Trial-2 as separate ceremony per Slab 7a precedent (commit `95c81b0`; deferred-inventory entry `slab-7a-trial-2-bs-2-readiness-confirmation-deferred-to-operator-trial-2-ceremony`). Filed `slab-7b-trial-2-ac-o-ac-p-readiness-confirmation-deferred-to-operator-trial-2-ceremony` to deferred-inventory. Rationale highlights: Murat — conflating ceremonies inflates blast radius and hurts attribution; Mary — Slab 7a precedent ratified at retrospective, not flagged as deficiency; John — running Trial-2 before retrospective inverts decision order; Amelia — operator-gated AC blocks structurally belong in operator ceremony.

**Wider-regression delta:** 1389 passed (Gate-2 run) vs 1388 (cycle-1 close baseline) = +1 test deterministically. No regressions, no flakes.

**Skeleton fail-closed posture authoritative reading:** Per cycle-1 PATCH-1 contract, the structured-JSON `verdict: not_run` payloads ARE the documented Gate-2 evidence for AC-G.1 + AC-I. Substrate invariant stack (lockstep + sandbox-AC + class-conformance + 11 activation contracts + import-linter + live-API detector + ruff + 9 import contracts) provides the structural behavior-preservation guarantees that matter at this tier. Live-credential verification deferred to Trial-2 ceremony as canonical operator-driven venue per Slab 7a precedent.

### Verification

(authored by Codex at T11-T12)

### File List

(authored by Codex at T13)

### Change Log

(authored by Codex at T13; updated by Claude at T14)
