# Story PR-R: Marcus Dispatch Reshaping (Pull-Request Standardization)

**Status:** ready-for-dev (green-lit 2026-04-22 — D1/D2/D3 rulings applied below)
**Created:** 2026-04-22
**Epic:** Sprint #1 standalone story (Marcus infrastructure — likely future Epic 35+ "Marcus Dispatch Discipline")
**Sprint key:** `PR-R-marcus-dispatch-reshaping`
**Sprint:** Sprint #1 (5 of 5 — opens LAST per D7 ruling)
**Points:** **5 pts firm** (ratified at green-light: 3 edges from D1 + L1 check from D3 = 5 pts)
**Depends on:** None hard at T0. Benefits from 27-2.5 + retrieval-intake + evidence-bolster landing first per D7 sequencing (real consumer shapes inform the generalization).
**Blocks:** Cleaner future specialist integrations (post-Sprint #1 stories consume this pattern via the new `dispatch-registry.yaml`).

## TL;DR

- **What:** Define a standard Marcus → specialist dispatch envelope (*pull-request* = input packet + output receipt + error contract + telemetry) and reshape existing specialist dispatch edges to conform. Pattern ratified by 27-0/27-2's `RetrievalIntent` / `ProviderResult` / `ConvergenceSignal` triad; PR-R generalizes that discipline to all Marcus dispatch edges.
- **Why:** Trial run `C1-M1-PRES-20260419B` exposed 8 deferred items and 6 fix-on-the-fly events per the reproducibility report — a material fraction were dispatch-layer contract ambiguities (who produces what shape; who validates; where receipts go). 27-0/27-2 proved contract-first dispatch reduces this. PR-R generalizes it before Sprint #1's new stories (evidence-bolster, Irene retrieval-intake, §7.1 template) compound the ambiguity.
- **Novelty:** NOT a new capability — a **cross-cutting discipline refactor** across the existing dispatch landscape. Touches Marcus's `capabilities/` contract authoring + the specialist-facing sides of each dispatch edge.
- **Size:** 3–5 pts (scope-bounded at green-light). Low floor = "standardize envelope schema + retrofit 2 highest-churn edges (Irene Pass 2, Gary)"; high floor = "standardize + retrofit all 6 edges + add dispatch-audit L1 check."

## Background — Why This Story Exists

**The problem surfaced by the 2026-04-19 trial reproducibility report:** specialist dispatch is currently done via a patchwork — some specialists receive YAML envelopes, some receive inline-dict args, some accept implicit defaults, some require explicit schemas. Output receipts vary: some write `receipt.json`, some append to a log, some return via envelope. Error contracts differ: some specialists exit-30 on validation failure, others pass-through with warnings. Marcus has to special-case each edge.

**The proof pattern** landed in Epic 27: `RetrievalIntent` (input contract) + `RetrievalAdapter.execute` (work) + `ProviderResult` (output contract) + `DispatchError` (error contract). Adding a new provider is now a subclass exercise. Adding a new dispatch edge to Marcus should be similarly disciplined.

**Operator directive (implicit from Sprint #1 framing):** "standardize Marcus's pull-request pattern" — each dispatch is a pull-request with a pinned input + output + error contract.

## Story

As **Marcus (the orchestrator)**,
I want **a standard dispatch envelope (input packet + output receipt + error contract + telemetry) consistent across all specialist edges**,
So that **adding a new specialist OR a new dispatch variant (e.g., evidence-bolster pass on Irene, cross-validated Texas pull) is a subclass-style exercise rather than a bespoke-plumbing exercise, AND trial-run fix-on-the-fly rate drops because contract ambiguity is eliminated upstream**.

## Acceptance Criteria (spine level — expand at green-light)

### Behavioral (AC-B.*)

1. **AC-B.1 — Dispatch envelope schema pinned.** New `state/config/schemas/marcus-dispatch-envelope.schema.json` (name TBD at green-light). Pydantic model `DispatchEnvelope` defines required fields: `run_id`, `specialist_id`, `dispatch_kind` (enum), `input_packet` (specialist-specific payload), `context_refs` (list of artifact paths), `correlation_id`, `timestamp_utc`.
2. **AC-B.2 — Receipt contract pinned.** `DispatchReceipt` schema: `correlation_id`, `specialist_id`, `outcome` (`complete` | `partial` | `failed`), `output_artifacts` (list of paths), `diagnostics` (dict), `duration_ms`, `timestamp_utc`.
3. **AC-B.3 — Error contract pinned.** `DispatchError` taxonomy: `validation_failed`, `specialist_unavailable`, `timeout`, `contract_violation`, `internal_error`. Each error kind carries a human-readable `message` + machine-readable `error_detail` dict.
4. **AC-B.4 — Existing dispatch edges retrofitted to the envelope.** Scope-bounded at green-light. Candidates (in recency-of-drift order per trial report):
   - Irene Pass 2 dispatch
   - Gary dispatch
   - Kira motion dispatch
   - Vera fidelity-check dispatch
   - Quinn-R pre-composition + post-composition dispatch
   - Texas retrieval dispatch (already shape-disciplined via 27-0; minimal retrofit)
5. **AC-B.5 — `_classify_dispatch_kind` helper** — mirrors 27-2's `_classify_directive_shape`. Dispatches without a valid `dispatch_kind` exit with clear error (mirrors 27-2 AC-B.6 pattern).
6. **AC-B.6 — Telemetry log.** Every dispatch emits a structured log line (`logger.info("dispatch.start", extra={...})` + `logger.info("dispatch.end", extra={...})`). Log format standardized for future dashboard / post-mortem extraction.

### Test (AC-T.*)

1. **AC-T.1 — Envelope/receipt/error schema-pin tests.** Pydantic round-trip + frozen-field tests per 31-1 precedent.
2. **AC-T.2 — Retrofit regression tests per edge.** For each edge retrofitted, a contract test asserting input+output+error match the new schemas.
3. **AC-T.3 — Pre-retrofit byte-identical regression.** Similar to 27-2 AC-T.6 golden-file: at least one trial-run-adjacent dispatch exercised end-to-end before + after retrofit; outputs structurally identical (timestamp-scrubbed).
4. **AC-T.4 — No-silent-drop on unknown dispatch_kind.** Exit with clear error, not silent pass-through.
5. **AC-T.5 — Suite regression floor pinned** (TBD collecting count at green-light depending on retrofit scope — estimate ≥15).

### Contract Pinning (AC-C.*)

1. **AC-C.1 — Envelope/receipt schemas live in `state/config/schemas/`** (existing schema home).
2. **AC-C.2 — DispatchError module-prefix contract** — mirrors 27-2 AC-T.10: all dispatch errors' `type(exc).__module__.startswith("marcus.dispatch.")` (or similar). No transport-type leakage.
3. **AC-C.3 — Existing capabilities registry extended** — `registry.yaml` gains dispatch-edge entries alongside capability entries. Or separate `dispatch-registry.yaml` (decide at green-light).
4. **AC-C.4 — Retrofit does NOT change specialist-internal logic.** Only the Marcus-facing boundary moves to envelope/receipt discipline.
5. **AC-C.5 — No LLM-in-the-loop for envelope validation.** Pure Pydantic.

## File Impact (estimated — scope-bounded at green-light)

| File | Change | Lines (est.) |
|------|--------|-------|
| `state/config/schemas/marcus-dispatch-envelope.schema.json` | New — envelope + receipt + error schemas | +120 |
| `scripts/marcus_capabilities/dispatch.py` OR `skills/bmad-agent-marcus/capabilities/dispatch/` | New — Pydantic models + envelope builder + receipt reader + `_classify_dispatch_kind` helper | +250 |
| `skills/bmad-agent-marcus/capabilities/registry.yaml` | Touch — dispatch edge registrations (or separate file) | +50 |
| `skills/bmad-agent-marcus/SKILL.md` + relevant reference docs | Touch — new "Dispatch envelope" reference section | +60 |
| `docs/dev-guide.md` + new sharded `docs/dev-guide/how-to-add-a-dispatch-edge.md` | Touch + New — Recipe-7 (mirrors 27-2's Recipe-6 how-to-add-a-retrieval-provider) | +25 / +180 |
| Retrofit: Irene Pass 2 dispatch | Touch | +50 |
| Retrofit: Gary dispatch | Touch | +50 |
| Retrofit: other edges (scope-bounded at green-light) | Touch | +30 each |
| `tests/marcus_capabilities/test_dispatch_envelope.py` | New — schema-pin + round-trip tests | +150 |
| `tests/marcus_capabilities/test_dispatch_retrofit_<edge>.py` × N | New — per-edge contract tests | +100 each |

**No changes to:** specialist-internal logic (Irene's Pass 1 algorithm, Gary's slide-generation code, Kira's motion-prompt logic, etc.). Retrofit is boundary-only.

## Tasks / Subtasks (spine — expand at green-light)

**Task order TBD at green-light. Proposed:** T1 envelope schema → T2 receipt schema → T3 error taxonomy → T4 `_classify_dispatch_kind` helper → T5 dev-guide Recipe-7 + how-to sharded file → **T6–T(5+N) per-edge retrofit (N = scope-bounded edge count)** → T(N+6) regression suite + pre-commit + lockstep.

- [ ] T1 — Envelope schema Pydantic model + JSON schema + module-level import
- [ ] T2 — Receipt schema Pydantic model + JSON schema
- [ ] T3 — Error taxonomy enum + exception classes + module-prefix contract
- [ ] T4 — `_classify_dispatch_kind` helper + unit tests
- [ ] T5 — Dev-guide Recipe-7 + sharded `how-to-add-a-dispatch-edge.md`
- [ ] T6 — Retrofit dispatch edge #1 (highest-churn — Irene Pass 2 proposed)
- [ ] T7 — Retrofit dispatch edge #2 (Gary proposed)
- [ ] T(N+6) — Retrofit scope bound at green-light (2 edges minimum, 6 edges maximum)
- [ ] T(final) — Regression + pre-commit + review

## Risks (spine)

| Risk | Mitigation |
|------|------------|
| **Retrofit breaks trial-run byte-identical output** — Marcus → specialist → downstream chain fragile | AC-T.3 golden-file regression per retrofitted edge. If byte-identical cannot hold, deviation documented + party-ratified. |
| **Scope creep — all 6 edges at once inflates story to 8+ pts** | Green-light caps retrofit edge count; defer untouched edges to follow-on stories (PR-R-2, PR-R-3 per edge family). |
| **Envelope schema premature — don't know all dispatch shapes yet** | Start with 2 edges retrofitted + Pydantic v2 `model_config={"extra": "allow"}` on `input_packet` sub-object; tighten later. |
| **Registry/schema drift** — envelope schema evolves without lockstep check | AC-C.3 dispatch-registry lockstep L1 check (mirrors 27-2 AC-S6 transform-registry lockstep). Defer to follow-on if green-light cuts scope. |
| **Specialist-internal logic accidentally modified during retrofit** | AC-C.4 contract: retrofit is boundary-only; AC-T.2 per-edge test asserts specialist's output semantics unchanged. |

## Non-goals

- Changing any specialist's internal logic.
- Adding new dispatch kinds (evidence-bolster variant, Irene retrieval-intake, etc.) — those are separate Sprint #1 stories that CONSUME this pattern.
- Replacing the existing `capabilities/` registry (PR-R extends it).
- Dispatch-budget enforcement or throttling — future hardening.
- LLM-mediated dispatch intent translation (manual/direct only).

## Questions for Green-Light Round

1. **Retrofit scope:** which dispatch edges land in this story? Minimum 2 (proposed: Irene Pass 2 + Gary), maximum 6 (all current edges). Each additional edge adds ~1 pt.
2. **Registry choice:** extend `capabilities/registry.yaml` or create separate `dispatch-registry.yaml`? Architectural call for Winston.
3. **Schema location:** `state/config/schemas/marcus-dispatch-envelope.schema.json` vs `skills/bmad-agent-marcus/capabilities/schemas/dispatch-envelope.yaml`? Paige's doc-locality call.
4. **Dispatch-kind enum:** closed set at v1 (which edges?) vs open-string with capability-registry cross-validation? Defaults to closed set with documented extension path.
5. **Telemetry log format:** structured logger.extra + JSON? Or dedicated `dispatch-log.yaml` per run? Mirrors Tracy's `dispatch-log.yaml` pattern (Epic 28 AC-S8).
6. **Lockstep L1 check:** in scope (adds ~0.5 pt) or defer to PR-R-hardening follow-on?
7. **Points estimate:** 3 pts (2 edges retrofitted) / 4 pts (3 edges) / 5 pts (5+ edges + lockstep).
8. **Coordination with Irene retrieval-intake story:** if Irene retrieval-intake lands before PR-R, that edge's dispatch gets built bespoke and retrofitted later. Preferred ordering: PR-R first so Irene retrieval-intake consumes the standard from day 1. Green-light confirms sequencing.

## References

- **27-0 retrieval foundation** ([27-0-retrieval-foundation.md](./27-0-retrieval-foundation.md)) — contract-first dispatch proof pattern; `RetrievalIntent` + `ProviderResult` + `DispatchError` triad is the template.
- **27-2 scite adapter** ([27-2-scite-ai-provider.md](./27-2-scite-ai-provider.md)) — first real consumer of the pattern; writer `code_path` discriminant (AC-C.11) shows how to make dual-path boundaries explicit without silent drift.
- **Marcus capabilities registry** ([skills/bmad-agent-marcus/capabilities/registry.yaml](../../skills/bmad-agent-marcus/capabilities/registry.yaml)) — existing PR-PF / PR-RC / PR-HC / PR-RS pattern; PR-R extends or sits alongside.
- **Trial reproducibility report** ([run-reproducibility-report-c1m1-tejal-20260419b.md](./run-reproducibility-report-c1m1-tejal-20260419b.md)) — 8 deferred items + 6 fix-on-the-fly events; dispatch-layer ambiguity driver.
- **Tracy dispatch-log** ([epic-28-tracy-detective.md §AC-S8](./epic-28-tracy-detective.md)) — per-run dispatch audit trail; template for PR-R's telemetry.

---

## Green-Light Patches Applied (party-mode round 1, 2026-04-22)

Four-panelist roundtable: Winston (Architect) / Amelia (Dev) / Murat (Test) / Paige (Tech Writer). **Unanimous GREEN** after D1/D2/D3 rulings applied + riders honored.

### Verdict

- 🏗️ Winston: YELLOW→GREEN after D1/D2/D3 pinned + registry-choice/dispatch-kind-enum/schema-location/L1-check riders applied
- 💻 Amelia: RED→GREEN after D1 (3 edges) + D2 (new `dispatch-registry.yaml`) + D3 (L1 in-scope) pinned (6 open Qs → 0 open Qs)
- 🧪 Murat: YELLOW→GREEN after D1 edge count pinned (enables regression floor pin) + flake-gate extension
- 📚 Paige: YELLOW→GREEN after D2 registry choice pinned + R-2 audience-layered Marcus SKILL.md + R-3 structured telemetry format

### D1 ruling: Retrofit 3 edges (Winston's position)

**Edges in scope:**
1. **Irene Pass 2** — highest-iteration surface per user memory; biggest win from standardized envelope
2. **Kira motion** — motion-first-before-Irene means Kira's envelope shape gates Irene's; lock it now
3. **Texas (minimal confirmation retrofit)** — already Shape 3-Disciplined per 27-0; retrofitting is confirmation-of-pattern, not invention

**Edges deferred** to follow-on stories (filed in deferred-inventory): Gary, Vera fidelity, Quinn-R (5 edges × ~1pt each = ~5 follow-on pts post-PR-R).

### D2 ruling: New `skills/bmad-agent-marcus/references/dispatch-registry.yaml` (Amelia's position)

Separate file from `capabilities/registry.yaml` — mirrors existing `specialist-registry.yaml` pattern (internal skills vs external connections are semantically different; don't mix). AC-C.3 updated: registry lives at `skills/bmad-agent-marcus/references/dispatch-registry.yaml`; `registry.yaml` unchanged.

### D3 ruling: L1 lockstep check IN-SCOPE (Winston's position, +1pt)

Non-negotiable per CLAUDE.md pipeline lockstep regime. Deliverables added:
- New L1 check script `scripts/validators/check_dispatch_registry_lockstep.py` validating code↔registry alignment (dispatch kinds in code == entries in `dispatch-registry.yaml`)
- Pre-commit hook integration (orphan-detector-equivalent for dispatch edges)
- AC-T.6 (new): L1 check unit test + drift-injection test (sibling code adds edge without registry entry → fails)
- Entry in `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` for dispatch-registry.yaml + dispatch ABC module

### Winston architectural riders applied

- **Dispatch-kind enum: CLOSED** with triple-layer red-rejection per Pydantic-v2 checklist. No open strings. Adding a value requires PR-R-v{N+1} bump + party-mode consensus.
- **Schema location: co-located with ABC at `marcus/dispatch/contract.py`** — NOT in `docs/`. Schema-in-code with Pydantic-v2 enforcement; docs point to code.
- **Registry entries validated** against the Pydantic schema at import time (same pattern as 27-0's `provider_directory` auto-registration).

### Amelia dev-feasibility riders applied

- **Dispatch-kind enum closed-set with triple-layer red-rejection** per pydantic-v2 checklist (aligned with Winston).
- **Module-level constants, no `os.environ.get` at import time** (roster-level rider — 27-2 DEFER recurrence guard).
- **Golden files as `.expected.json` fixtures**, not inline strings (Murat's rider; inline strings encourage drift).
- **Cross-check test enumerating dispatch edges from code** (asserts `len(edges) == len(golden_files)`); protects against edge addition without golden.

### Murat test-discipline riders applied

- **Regression floor pinned ≥17 collecting** (≥15 from 3 edges × 2 golden + 2 × bidirectional envelope/receipt + 1 error-path + ≥2 from L1 check tests per D3).
- **Flake-gate extension BINDING**: PR-R joins 27-2.5 on the 3x-run flake-detection gate (Marcus dispatch has stateful ordering in some paths; byte-identical goldens rely on deterministic upstream).
- **AC-T.6 negative-space coverage**: malformed payload → rejection-with-specific-error atoms (fills "under-covered" gap Murat flagged).
- **AC-T.3 golden files committed as `tests/fixtures/dispatch_retrofit/<edge>.expected.json`** — not regenerated-in-CI.

### Paige docs riders applied

- **Marcus SKILL.md "Dispatch envelope" section audience-layered**: For operators / For dev-agents / For Marcus-at-activation (inherits CLAUDE.md cold-start read path).
- **Telemetry log format: STRUCTURED** (not plain INFO) with field schema documented in how-to. Format matches Epic 28 Tracy's `dispatch-log.yaml` pattern.
- **Recipe-7 sharded how-to** at `docs/dev-guide/how-to-add-a-dispatch-edge.md`; Recipe-7 stub in `docs/dev-guide.md` Extension Guide; ToC entry in main dev-guide.md. Pattern identical to 27-2's Recipe-6.
- **Two minimal worked examples** in how-to (Paige Recipe-7-variation rider): routing condition A vs B, not a single end-to-end walk-through (dispatch edges are routing rules, not components — comparison teaches better).

### Sprint-level canonical naming applied (D6 roster-wide decision)

Dispatch envelope's payload carries the `evidence_bolster` run-constant unchanged to Tracy; Tracy's RetrievalIntent uses `cross_validate: bool` (mechanical). Intake consumer layer uses `evidence_bolster_active: bool`. PR-R's dispatch envelope passes all three through without renaming.

### Regression floor pinned (Murat)

**≥17 collecting additions.** Baseline at PR-R dev-start (cumulative across Sprint #1 prior stories) → cumulative target post-PR-R: ≥1220 passed (roster-level floor).

### Dev sequence

**Open position 5 (LAST)** per D7. Opens after 27-2.5 + evidence-bolster + irene-retrieval-intake land (or are in-flight late-stage). Reason: three real consumer stories inform the generalization; PR-R designed against reality, not speculation.

### Vote record

- 🏗️ Winston: YELLOW → GREEN (after D1/D2/D3 + enum + schema-location + L1 riders applied)
- 💻 Amelia: RED → GREEN (after D1/D2/D3 resolved; 6 open Qs → 0)
- 🧪 Murat: YELLOW → GREEN (after edge count pinned + flake-gate extended + floor pinned)
- 📚 Paige: YELLOW → GREEN (after D2 pinned + audience-layered SKILL.md + Recipe-7 variation)

**Unanimous GREEN → dev-story cleared to start** at position 5, contingent on 27-2.5 flake gate being live + dispatch-registry.yaml schema ratified at T0.

---

**Dev-story expansion triggered at:** green-light ratification (now). Full AC / task / test plan / file impact drilldowns land at T0 readiness check (points 5 firm; scope 3 edges + L1 check firm; registry location firm).
