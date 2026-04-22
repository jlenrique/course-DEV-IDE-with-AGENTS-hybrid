# Epic 27: Texas Intake Surface Expansion

**Status:** in-progress (27-0 / 27-1 / 27-2 done; 27-2.5 next on critical path; 27-3..27-7 ratified-stubs)
**Created:** 2026-04-17
**Driver:** Close the DOCX contract drift from the 2026-04-17 APC C1-M1 trial AND expand Texas's intake surface to new provider types the HIL operator + Tracy will dispatch against in future runs.

## Why This Is Its Own Epic

Two distinct bodies of work surfaced from the trial converge on one identity: **Texas is the technician, and the technician needs more tools**.

1. **Defect closure** — The trial exposed a contract-vs-code drift: `skills/bmad-agent-texas/references/transform-registry.md` promises `python-docx` as the DOCX extractor, but `skills/bmad-agent-texas/scripts/run_wrangler.py` never wires it. DOCX falls through to `read_text_file()` and produces binary garbage. Severity **High** — documentation lying about capability erodes trust in both layers.
2. **Capability expansion** — The operator has committed (Session 2026-04-17) to growing Texas's intake surface: wire `python-docx`, add image provider (sensory-bridges), add Notion MCP, add Box, add Playwright MCP, add YouTube (video/audio/transcript), and add scite.ai scholarly-citation retrieval. Epic 28 (Tracy the Detective) depends on the scite.ai provider landing first.

Party-mode consensus (Round 3, 2026-04-17 — Winston / John / Amelia / Paige / Murat) confirmed this as a **technician-capability epic** separate from Epic 28 (Tracy the Detective). Different risk profile, different acceptance shape, different epic-burndown semantics. Stapling them would hide Epic 28's probabilistic-agent iteration cost behind Epic 27's mechanical "just wire the library" cadence.

Previously tracked as "texas-visual-source-gap-backlog" stub at [`_bmad-output/implementation-artifacts/texas-visual-source-gap-backlog.md`](./texas-visual-source-gap-backlog.md); that stub is superseded by this epic.

## Scope

**In scope:**

| Provider | Story | Rationale |
|----------|-------|-----------|
| `python-docx` wiring | **27-1** | Contract drift fix. Blocks Tejal trial restart. |
| `scite.ai` (scholarly citations) | **27-2** | Epic 28 Tracy pilot dispatches against this. Hard dependency. |
| Image provider (sensory-bridges) | **27-3** | Closes half of the original visual-source-gap backlog. |
| YouTube (video + audio + transcript) | **27-4** | Three-asset provider; most complex of the batch. |
| Notion MCP | **27-5** | Credentialed read. MCP scaffolding already available in environment. |
| Box | **27-6** | Credentialed read. |
| Playwright MCP | **27-7** | Headless-browser scripted capture. Orthogonal to existing `playwright_html` (local scraper); sibling pattern. |

**Out of scope:**
- Tracy's editorial judgment layer (Epic 28).
- New asset types downstream of Pass 2 (handouts, podcasts, test images, games) — Epic 28 surfaces the intent manifest; actual asset-specialist agents are later epics.
- Replacement of existing `playwright_html` local scraper — 27-7 is additive, sibling provider.
- Rewriting Texas's fidelity manifest schema beyond the `source_origin` tag needed for Tracy-suggested rows (that single field is in 27-2 scope).

## Story Roster

| Story | Title | Points | Order | Status |
|-------|-------|--------|-------|--------|
| **27-0** | **Retrieval Foundation — Shape 3-Disciplined contract + dispatcher + cross-validation merger + Provider Directory (operator amendment)** | 5 | **FOUNDATION — unblocked 27-2, 27-2.5, 27-3, 27-4, 28-1** | **done** (closed BMAD-clean 2026-04-18 after party-mode green-light + bmad-code-review layered pass; +70 collecting tests; 1106/2/0 suite; ruff clean) |
| **27-1** | DOCX provider wiring (contract drift fix) | 2 | done — **locator-shape provider; does NOT depend on 27-0** | **done** (closed 2026-04-17 — python-docx 1.2.0 wired; Tejal cross-val 100% key-term coverage; AC-S6 pilot lockstep test landed) |
| **27-2** | scite.ai adapter (retrieval-shape; first consumer of 27-0) + **deferred 27-0 cascade** (AC-B.7 dispatcher wiring, dev-guide.md "how to add a provider", AC-T.7 log-stream parity tests, dual-emit writer, parametrized schema-compliance) | 5 | 2nd retrieval-shape story; **unblocks Epic 28 Tracy pilot** | **done** (BMAD-closed 2026-04-18, commit `883f742` — SciteProvider shipped; 15 PATCH applied inc. 2 HIGH-confidence correctness bugs; regression 1149/2/0/2; unblocks 28-1 + 27-2.5) |
| **27-2.5** | Consensus adapter (retrieval-shape; cross-validation partner to scite) | 3 | parallel after 27-2 — enables scite+Consensus cross-validation | **ratified-stub — UNBLOCKED 2026-04-18** (soft-blocked on 27-2 for cross-val demo); opened per operator directive ("use one service's findings to confirm or supplement another's") |
| **27-3** | Image provider (retrieval-shape via sensory-bridges) | 3 | parallel after 27-0 + sensory-bridge integration | ratified-stub (reshapes to retrieval-shape per 27-0 contract) |
| **27-4** | YouTube provider (retrieval-shape; video + audio + transcript tri-output) | 5 | parallel after 27-0 | ratified-stub (reshapes to retrieval-shape per 27-0 contract) |
| **27-5** | Notion MCP provider | 3 | parallel after 27-0 | ratified-stub (**locator-shape** — keeps existing directive shape; no foundation dependency at CLI level, but routes through dispatcher internally) |
| **27-6** | Box provider | 2 | parallel after 27-0 | ratified-stub (**locator-shape**) |
| **27-7** | Playwright MCP provider | 3 | parallel after 27-0 | ratified-stub (**locator-shape**) |

**Total: 31 points.** Critical path: **27-1 (done) → 27-0 (done) → 27-2 (done) → 27-2.5 (Consensus, next) → unblocks Epic 28.**

**Shape classification per Round 3 consensus** (see [27-0-retrieval-foundation.md](./27-0-retrieval-foundation.md) for full detail):
- **Retrieval-shape** (intent + acceptance-criteria + provider_hints): 27-2 scite, 27-2.5 Consensus, 27-3 image, 27-4 YouTube.
- **Locator-shape** (operator provides exact locator; Tracy doesn't formulate queries): 27-1 DOCX (done, legacy), 27-5 Notion, 27-6 Box, 27-7 Playwright.

Both shapes internally route through 27-0's dispatcher (Shape 3-Disciplined AC-B.7 — operator-direct becomes degenerate case of the contract). CLI-level UX unchanged for locator-shape providers; retrieval-shape providers are Tracy-dispatched via intent+AC+provider_hints.

## Dependency Graph (post-Round-3 reshape, 2026-04-17)

```
27-1 DOCX (done) ──► unblocks Tejal trial restart (mechanical drift fix; locator-shape; no 27-0 dependency)

27-0 Retrieval Foundation ──┬──► 27-2 scite adapter (DONE) ──► 27-2.5 Consensus adapter ──► UNBLOCKS Epic 28 (28-1 Tracy pilot)
(Shape 3-Disciplined        │                                  (cross-validation partner)
 contract + dispatcher +    │
 cross-validation merger)   ├──► 27-3 image (retrieval-shape; parallel)
                            ├──► 27-4 YouTube (retrieval-shape; parallel)
                            │
                            ├──► 27-5 Notion MCP (locator-shape; routes through dispatcher via degenerate case)
                            ├──► 27-6 Box (locator-shape)
                            └──► 27-7 Playwright MCP (locator-shape)

28-1 Tracy pilot ──► reshapes to emit intent + AC + provider_hints (not scite-specific queries)
                     per 27-0's Shape 3-Disciplined contract
```

**Critical path for Epic 28 unblock**: 27-1 (done) → **27-0 (done)** → **27-2 (done)** → **27-2.5 (Consensus — next)** → 28-1.

## AC Spine — Cross-Cutting Acceptance Criteria

Every 27-N story must satisfy:

- **AC-S1: Provider contract compliance.** The new provider is registered in `skills/bmad-agent-texas/references/transform-registry.md` AND implemented in `skills/bmad-agent-texas/scripts/run_wrangler.py` provider dispatch. Registry-vs-code drift check (see AC-S6) must pass.
- **AC-S2: Fidelity-manifest compatibility.** Provider emits rows conforming to the existing Texas manifest schema. New optional fields are added as explicit schema extensions with migration notes (not silent additions).
- **AC-S3: Structured return, not blob dump.** Per John's Round-1 Epic 28 pre-anticipation: every provider returns a structured manifest (resource + provenance + access-path), not a blob dump. This is the only Tracy-anticipation Epic 27 owes.
- **AC-S4: Failure-mode coverage.** Provider handles: network failure, auth failure, empty-result, malformed-response, rate-limit. Each failure path produces a FAILED `SourceOutcome` with `error_kind`, `error_detail`, `known_losses`, `recommendations` — never a traceback.
- **AC-S5: Test coverage per provider.** Minimum: happy-path integration test (cassette-backed where network is involved), one failure-mode test, one schema-conformance test. Per `feedback_regression_proof_tests` hard-preference: no `xfail` / `skip` on default suite at closure.
- **AC-S6: Transform-registry lockstep check.** A new `format-capability-lockstep` check (companion to Audra L1-W, stubbed in `a944189`) asserts: every format advertised in `transform-registry.md` has a working extractor in code. Fails commit otherwise. Would have caught the DOCX drift pre-trial.
- **AC-S7: CP1252 guard sanity.** Windows CLI invocation of provider dev commands does not crash with `UnicodeEncodeError`. Story 26-7 introduced the `sys.stdout.reconfigure` pattern; each new provider CLI surface inherits it.
- **AC-S8: Documentation currency.** `transform-registry.md` section for the new provider matches implementation exactly: advertised formats, known-losses, auth requirements, failure modes.

## Non-Functional Requirements

- **Logging:** per-provider structured log lines matching the existing Texas logging pattern (`setup_logging(name='texas', ...)`).
- **Test coverage target:** ≥90% line coverage per new provider module. Measured, not intuited (per `feedback_regression_proof_tests`).
- **Backward compatibility:** existing provider contracts (`local_file`, `pdf`, `url`, `notion`, `playwright_html`) remain unchanged. New providers are additive.
- **Auth handling:** credentials read from environment variables or `.env` (never committed). Provider README documents the required env vars.
- **Offline-first tests:** cassette-backed (`vcr.py`) per Murat's Round-2 flakiness doctrine. `tests/cassettes/texas/<provider>/` holds canonical responses. Real-network tests quarantined to `tests/live/` with `@pytest.mark.live`, excluded from default run.

## Risk Register

| Risk | Owner | Mitigation |
|------|-------|-----------|
| scite.ai API schema drift between cassette record and live production | Murat | Schema-canary test in 27-2; cassette refresh cadence quarterly; stale cassette >6 months = CI warning. |
| Notion MCP / Box / Playwright MCP availability in local dev + CI | Winston | Provider stories start with MCP-availability preflight; if MCP not installed, provider scaffolds but test marks `xfail` until environment gate lands. |
| YouTube three-asset (video + audio + transcript) contract complexity | Amelia | 27-4 split internally into three AC groups — each asset extractable independently; transcript-only path is the fallback when video download fails. |
| Lockstep check (AC-S6) proving too strict and blocking minor drift | Paige | Check emits `warn` for format-only drift, `error` for capability drift (promise-vs-code divergence). First pilot with current Texas before enforcing on Epic 27 stories. |
| Operator re-scaffolds Texas sanctum during Epic 27 work | Winston | Scaffold v0.2 preservation semantics (Epic 26-5) gates this; if 26-5 hasn't landed when a 27-N story rescaffolds, it uses `--force` with pre-backup discipline documented in the story. |
| Audra L1 check not yet expanded to this lockstep class | Paige | 27-2 lands AC-S6's initial lockstep implementation; promotion to full Audra L1 class = separate post-Epic-27 story (not in this epic's scope). |

## Definition of Done (Epic Level)

- All 7 stories `done` per `sprint-status.yaml`.
- All 7 providers registered in `transform-registry.md` AND implemented in `run_wrangler.py`.
- Lockstep check (AC-S6) passing on full registry.
- Zero regressions against the current `tests/` baseline (622 passing as of 2026-04-17 progress-map hardening).
- One clean end-to-end trial run exercising at least the DOCX + scite.ai providers (Tejal restart trial satisfies this).
- Documentation: `transform-registry.md` updated for every provider; one per-provider quick-reference page under `skills/bmad-agent-texas/references/providers/` (or similar — exact path per Paige's doc organization at story time).

## Party-Mode Consensus Record

- **Round 1 (2026-04-17)** — Winston, John, Sally, Mary: Tracy is a standalone specialist; Epic 27 and Epic 28 are separate epics; structured manifest output is the only Tracy-anticipation Epic 27 owes (John).
- **Round 2 (2026-04-17)** — Amelia, Murat, Paige, Dr. Quinn: hard pre-Pass-2 gate confirmed; asset-intent vocabulary two-field pattern (intent_class + intent_detail + reserved); `editorial_note` field name (not `tracy_note`); Murat's cassette + xfail-alongside-artifact doctrine; Dr. Quinn's coherence-gate + pre-indexed-domain-map deferred to Epic 28 v2 backlog.
- **Round 3 (2026-04-17)** — John, Amelia, Paige, Murat: Epic 27 story breakdown (7 stories, 23 points); critical path 27-1 → 27-2; Epic 28 compresses to 2 stories (28-1 + 28-2); branch hygiene (ratification on current branch, implementation on per-epic branches).
- **Dispatch-vs-artifact ratification (2026-04-17)** — Winston: specialists never call specialists at runtime; filesystem-mediated artifact handoff is not a rule violation; Marcus owns all dispatch edges. **Governing principle for all future specialist-to-specialist data exchange.**

## Appendix: Supersedes / Supersedes-by

- **Supersedes:** [`texas-visual-source-gap-backlog.md`](./texas-visual-source-gap-backlog.md) (2026-04-17 severity-High stub). That stub's Option A is adopted as the architecture; Option B and Option C are closed.
- **Sits alongside:** [`epic-28-tracy-detective.md`](./epic-28-tracy-detective.md) — Epic 28 depends on 27-2 (scite.ai provider) landing first.
- **Related charter:** [`run-charters/pretrial-prep-charter-20260417.md`](./run-charters/pretrial-prep-charter-20260417.md) — 26-9 (Texas wrangler intake-surface expansion) was deferred in that charter; this epic is its successor with expanded scope.

## Links

- [Story 27-1: DOCX provider wiring](./27-1-docx-provider-wiring.md)
- [Story 27-2: scite.ai provider](./27-2-scite-ai-provider.md)
- [Story 27-3: Image provider](./27-3-image-provider.md) (stub)
- [Story 27-4: YouTube provider](./27-4-youtube-provider.md) (stub)
- [Story 27-5: Notion MCP provider](./27-5-notion-mcp-provider.md) (stub)
- [Story 27-6: Box provider](./27-6-box-provider.md) (stub)
- [Story 27-7: Playwright MCP provider](./27-7-playwright-mcp-provider.md) (stub)
