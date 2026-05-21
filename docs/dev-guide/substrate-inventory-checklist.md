# Substrate Inventory Checklist — pre-MVP-vote / pre-slab-opener gate

**Status:** authored 2026-04-27 in operator session post-Slab-6.0-close + post-A17/P3 anti-pattern filings.
**Audience:** anyone authoring an architecture document, a slab-opener spec, or a substantive substrate story for any BMAD-managed system. Mandatory reading before voting any composition-shape MVP / SHIP-CONDITIONAL / slab-opener.
**Status of this document itself:** living checklist. Each new project that finds a substrate gap not in this list adds an item. Numbered N1+ to distinguish from anti-patterns A1+ and process-anti-patterns P1+ in `specialist-anti-patterns.md`.

---

## Why this checklist exists

The LangChain/LangGraph migration (2026-04 → 2026-04-27) discovered 6 substrate gaps post-vote:

- A15 — Plausible-Token Substrate Contamination (fictitious OpenAI model IDs across ~25 surfaces)
- A16 #1-#4 — Composition-vs-Component Audit Gap (4 instances: smoke max_completion_tokens; Wondercraft payload; SciteProvider auth+tools; Slab 6.1 first-attempt compose-without-invoke)
- A17 — Substrate Designed for Isolation, Composition Assumed (specialists + cache_prefix overwrite + per-specialist gates fire before production gate)
- P3 — Composition-Shape Vote Without End-to-End Exercise (M5 voted on unexercised composition)

Each was an "unknown unknown" at vote time and became "known" only after expensive integration discovery. This checklist exists so future projects discover these patterns at architecture-authoring time (cheap), not at strict-AC implementation time (expensive).

The checklist is derived from observed failure modes, not speculation. Each item has a concrete verification step + a clear PASS/FAIL gate. Each item maps to one or more anti-patterns it would have caught.

---

## How to use this checklist

**At architecture-authoring time:** the architect reads each item + ensures the architecture document has a corresponding section / contract / specification. Items without an answer in the doc are gaps to be addressed before the vote.

**At slab-opener time:** the story author reads each item + ensures the slab opener has corresponding ACs. Items without an AC are vote-evidence-base requirements per P3 counter-discipline.

**At MVP-vote / SHIP-CONDITIONAL-vote time:** the party-mode round reads each item + verifies the vote evidence base actually addresses each one. Items not addressed become explicit conditional-window items or vote-blockers per operator decision.

**At code-review time (bmad-code-review):** the Acceptance Auditor layer reads each item + traces the implementation against it. Items missing become `patch` or `decision_needed` triage candidates.

Failing the checklist isn't a project-blocker. It's a vote-evidence-base requirement. Either (a) close the gap, (b) RE-SCOPE the vote to exclude the unaddressed claim, OR (c) explicitly name the gap as a conditional-window item.

---

## The checklist (12 items as of 2026-04-27; living)

### N1 — External-provider resource ID validity (catches A15)

**Item:** Every external-provider resource ID (model_id, capability slug, endpoint URL, region code, account namespace, project key) appearing in shipped config is verified against a vendored snapshot of the provider's catalog.

**Verification:**
- Lint guard test (denylist) excluding production code paths from containing known-fictitious or unverified IDs
- Catalog membership test (allowlist) asserting every config-surface ID appears in `tests/fixtures/<provider>_catalog_snapshot.json`
- Catalog snapshot has `_provenance` block: `snapshot_source_url`, `snapshot_date`, `next_refresh_due_by`, `refresh_cadence`, `refresh_owner`
- At least one live-provider smoke test gated `pytest -m live` (tier-coverage if cascade exists)

**PASS criteria:** all four sub-checks present + green. Catalog snapshot freshness within stated cadence.

**Anti-patterns this catches:** A15 (Plausible-Token Substrate Contamination)

---

### N2 — Composition exercise before any composition-shape vote (catches A16 + A17 + P3)

**Item:** Before any MVP / SHIP-CONDITIONAL / composition-shape vote, ≥1 real upstream→downstream component pair runs end-to-end through the proposed substrate. Real components, not stubs. Output joins the vote-evidence base.

**Verification:**
- "Composition Smoke" gate in slab-opener template (per Quinn-R Q3 amendment); 30-line throwaway script wires components together end-to-end before slab spec ratifies
- For systems with N>2 components: at least one chain test under `tests/composition/` with `ComposedSpecialistChainHarness`-equivalent fixture
- Chain test asserts envelope-state propagation (not just output equality)
- Failing smoke triggers explicit operator decision: re-scope OR defer OR explicit-composition-shape-vote with named gap

**PASS criteria:** Composition Smoke gate present in slab opener; chain test exists for ≥1 pair; chain test passes against real components.

**Anti-patterns this catches:** A16 (Composition-vs-Component Audit Gap) + A17 (Substrate Designed for Isolation) + P3 (Composition-Shape Vote Without End-to-End Exercise)

---

### N3 — Live-API smoke before MVP close (catches A15 + A16)

**Item:** ≥1 live-API smoke test exists for every external provider the system integrates with. Smoke is gated `pytest -m live` (excluded from default collection); skips cleanly when keys absent; runs successfully when keys present.

**Verification:**
- `tests/live/test_<provider>_smoke.py` files for each provider in the integration set
- Each smoke test makes ONE cheap call (no retries, no multi-step, no state mutation)
- Each smoke test asserts response shape (not content) + non-zero behavior + latency cap
- Pre-MVP-close: operator runs `pytest tests/live/ -m live` with keys set; output captured for close-record

**PASS criteria:** smoke tests exist for ALL providers; default collection excludes them; operator-witnessed run for MVP close.

**Anti-patterns this catches:** A15 (referent validity) + A16 (composition validation at the integration layer)

---

### N4 — Per-component isolation invariant preserved post-composition (catches A17)

**Item:** When composition layer ships, all per-component isolated-execution tests remain GREEN. Components may run in isolation OR in composition; both modes must work.

**Verification:**
- Per-component test suites (`tests/specialists/<name>/test_*.py` or equivalent) all PASS post-composition
- A test specifically asserting per-component isolated execution still works (e.g., `tests/composition/test_specialist_isolation_preserved.py`)
- M3-style deterministic harness (or equivalent isolated-execution path) remains UNCHANGED + functional

**PASS criteria:** isolated tests + composition tests both green; harness unchanged.

**Anti-patterns this catches:** A17 (Substrate Designed for Isolation, Composition Assumed) — counter-pattern: composition adds modes, doesn't replace them

---

### N5 — Cross-component state-flow contract (catches A17)

**Item:** Cross-component state-flow paths (state keys, envelopes, accumulators) are explicitly contracted: which fields are per-component scratch, which fields accumulate cross-component, which are read-only. Documented; tested; immutability-where-appropriate enforced.

**Verification:**
- State schema (Pydantic v2 strict; four-file-lockstep per checklist) explicitly distinguishes per-component fields from accumulators
- For accumulators: `add_contribution`-style methods with immutability invariants (raise on duplicate-add)
- Composition fixture asserts accumulation semantics (NOT overwrite; NOT silent loss)
- Tests cover negative cases (e.g., specialist tries to add contribution twice → raises; specialist tries to read pre-itself contribution that doesn't exist → returns None or raises with clear error)

**PASS criteria:** state schema documents the distinction; composition fixture asserts accumulation; negative tests present.

**Anti-patterns this catches:** A17 (cache_prefix overwrite was the smoking gun for the original A17 instance)

---

### N6 — Gate boundary scope hierarchy (catches A17 finding)

**Item:** Per-component gates and system-level gates have explicit hierarchy + non-overlap. Specifically: per-component gates do NOT block composition execution unintentionally.

**Verification:**
- Architecture document has explicit "Gate Hierarchy" section listing system-level gates (e.g., G1/G2C/G3/G4 in this migration) + per-component gates (e.g., specialist scaffold's `gate_decision`)
- Composition adapter explicitly handles or bypasses per-component gates appropriately
- Test asserts: composition execution reaches system-level gate (not halted at per-component gate)

**PASS criteria:** hierarchy documented; composition adapter handles per-component gates; test asserts system-gate-reachable.

**Anti-patterns this catches:** A17 finding #1 (per-specialist `gate_decision` interrupts fire before production-level G1)

---

### N7 — Replay regression verifies execution path (catches A16 + 5a.1 lesson)

**Item:** Replay regression tests verify the EXECUTION PATH (which components fired, in what order, with what state-flow), not just artifact OUTPUTS (final hashes match).

**Verification:**
- Replay test reads trace metadata + asserts node-execution sequence
- Test asserts cross-component state-flow occurred (not just outputs hash-match)
- Replay against frozen baseline + against live-execution both green

**PASS criteria:** replay test surface includes execution-path assertions, not just output-hash-match.

**Anti-patterns this catches:** A16 (the 5a.1 + 5a.2 work passed because outputs matched; execution path was never verified)

---

### N8 — Cost machinery integration with real trace data (catches A16 + 5a.3 lesson)

**Item:** Cost reports / per-component cost attribution / cascade machinery are verified against REAL trace data, not synthetic fixtures. At least one trace from a real-API run feeds into cost report end-to-end.

**Verification:**
- At least one cost-engineering test consumes a real LangSmith (or equivalent) trace
- Real-trace test exists alongside synthetic-fixture tests (both required; not either/or)
- Cost report's per-component attribution + total accuracy verified against the real trace

**PASS criteria:** real-trace cost test exists + green + attribution verified.

**Anti-patterns this catches:** A16 (5a.3 cost-engineering machinery was tested against synthetic LangSmith trace fixtures only; never validated against real trace data until operator ran live smoke)

---

### N9 — Operator-witnessed evidence at M-gate vote (catches P3)

**Item:** M-gate / SHIP-CONDITIONAL / MVP-vote evidence base includes ≥1 operator-witnessed end-to-end exercise from operator's machine, not just dev-side test runs.

**Verification:**
- Spec defines what "operator-witnessed" means for the vote (e.g., `pytest <slice> -m live` from operator's machine; output pasted into close-record)
- Operator-witnessed evidence is REQUIRED for vote, not optional
- Output captured + stored as close-record artifact

**PASS criteria:** operator-witnessed evidence captured + stored for the vote.

**Anti-patterns this catches:** P3 (Composition-Shape Vote Without End-to-End Exercise)

---

### N10 — Anti-pattern catalog read at architecture-authoring time (catches BMAD template gap)

**Item:** Architecture document explicitly cross-references the anti-pattern catalog. Each prior A* / P* / N* entry is read; for each, the architect derives a corresponding architecture-document section / contract / specification (or explicitly notes "not applicable to this system, because...").

**Verification:**
- Architecture document has §"Anti-Pattern Mitigation" section listing each prior A* / P* / N* + the architecture-doc surface that addresses it
- Items without addressing surface are filed as deferred-inventory follow-ons or explicitly marked out-of-scope
- Pre-vote review confirms the cross-reference is current (catalog hasn't gained new entries since)

**PASS criteria:** §"Anti-Pattern Mitigation" present + complete + current.

**Anti-patterns this catches:** the BMAD template gap that allowed A15-A17 + P3 to ride into the migration's M5 vote unaddressed

---

### N11 — Composition mode declared alongside isolated mode (catches A17 directly)

**Item:** Every multi-component contract that COULD be composed at runtime declares a "composition mode" alongside its "isolated mode" at design time. Both modes are spec'd; both modes have tests; both modes' invariants documented.

**Verification:**
- Component scaffold spec has explicit §"Isolated Execution" + §"Composed Execution" sections
- Both sections have ≥1 test exercising the mode
- Mode-specific invariants documented (what's true in isolation may not be true in composition + vice versa)

**PASS criteria:** scaffold spec has both sections + both tests + invariants documented.

**Anti-patterns this catches:** A17 (Substrate Designed for Isolation, Composition Assumed) — the structural fix at the contract design level

---

### N12 — Auth model verified via probe (catches A16 Wondercraft + Scite instances)

**Item:** External provider auth contracts are verified via PROBE before code is written that depends on the auth shape. Auth-model assumptions from documentation patterns are NOT trusted without verification.

**Verification:**
- Operator-runnable probe script exists for each external provider's auth (e.g., `scripts/operator/probe_<provider>_auth.py`)
- Probe attempts the auth flow + reports success/failure + identifies actual auth scheme (HTTP Basic / Bearer / OAuth 2.x / API key header / etc.)
- Provider client code is written AFTER probe verifies actual auth model

**PASS criteria:** probe script exists; ran successfully against real provider; client code matches probe-discovered auth model.

**Anti-patterns this catches:** A16 (Wondercraft assumed HTTP X-API-KEY but payload-shape was wrong; SciteProvider assumed HTTP Basic but real MCP requires OAuth 2.1 Bearer)

---

## Living checklist — extension protocol

**When to add a new N-item:**
- A new substrate gap is discovered post-vote that no existing N-item would have caught
- The new gap is structural (not a one-off oversight)
- Mary harvest-gate ratification (or equivalent for non-BMAD-managed systems) approves the new item

**When to remove an N-item:**
- Never. Even items that feel obvious-in-hindsight stay; future architects without this migration's context need them spelled out.

**When to revise an N-item:**
- The verification step needs updating (e.g., a new tool exists that performs the verification more cheaply)
- A new anti-pattern instance reveals the existing item's verification was incomplete

**Format-freeze:** four-section item shape (Item / Verification / PASS criteria / Anti-patterns this catches). Preserved for stability + readability across revisions.

---

## Application to current migration's Slab 6.0 + 6.1

**Slab 6.0 (production envelope substrate; status `review` per Codex 2026-04-27):**
- N1: not directly relevant (no new external provider IDs introduced by Slab 6.0)
- N2: ✅ AC-C composition fixture + Composition Smoke gate amendment (AC-D)
- N3: not directly relevant (Slab 6.0 uses synthetic specialist outputs; live API is Slab 6.1's responsibility)
- N4: ✅ AC-E specialist isolation invariant preserved
- N5: ✅ ProductionEnvelope schema explicitly distinguishes per-component (cache_prefix) from cross-component (envelope contributions); immutability enforced
- N6: ✅/partial Slab 6.0 dispatch adapter invokes compiled specialist graphs through the per-specialist `gate_decision` boundary and records interrupts; Slab 6.1 owns the production system-gate reachability proof.
- N7: not directly relevant (replay regression is 5a.1's responsibility; Slab 6.0 doesn't touch it)
- N8: partial (contract-ready) — Slab 6.0 requires explicit per-contribution `cost_usd` and makes envelope rollup a direct sum; real trace cost attribution remains Slab 6.1 / 5a.3 cost machinery responsibility.
- N9: pending — operator-side dual-gate (per AC-I) is the operator-witnessed evidence; runs after Slab 6.0 implementation
- N10: ✅ Slab 6.0 spec includes an explicit "Anti-Pattern Mitigation Trace" cross-reference to A15/A16/A17/P3 and the N1-N12 review trace requirement.
- N11: ✅ Spec explicitly preserves specialists' isolated-mode contracts + adds composed-mode contract via dispatch adapter
- N12: not directly relevant (no new external provider auth introduced)

**Slab 6.1 (runner consumes substrate; will be re-scoped):**
- N1: re-verify after Slab 6.0 close (any new external-IDs introduced in runner code)
- N2: ✅ runner exercises full Texas → cd → ... chain via real LangGraph composition with envelope+adapter from 6.0
- N3: ✅ AC-G live-OpenAI production trial smoke gates the close
- N4: ✅ specialists still pass isolated-execution tests post-runner-build
- N5: ✅ envelope contract from 6.0 enforces accumulation semantics
- N6: ✅ runner respects Slab-6.0 adapter's gate-hierarchy handling
- N7: pending — should add execution-path assertion to replay-regression suite (post-runner)
- N8: ✅ AC-G live trial feeds real trace into cost report
- N9: ✅ operator-witnessed live trial gates the close
- N10: pending — should add §"Anti-Pattern Mitigation" to Slab 6.1 spec
- N11: not directly relevant (runner doesn't introduce new multi-component contracts)
- N12: not directly relevant (no new external provider auth)

## Operator-presence loop integration

For any future operator-presence ceremony (M-gate ceremonies, live-smoke verification, MVP-close witness):

1. Run the checklist against the slab/MVP that's voting
2. Items with ✅ proceed to vote evidence
3. Items with pending become explicit conditional-window items
4. Items with ❌ either re-scope, defer, or block

This integrates the checklist into the operator-witness pattern that already worked for M2/M3 + Slab 5a + Slab 6.0 dual-gates.

---

## See also

- `docs/dev-guide/specialist-anti-patterns.md` — A1-A17 codebase anti-patterns + P3 process anti-pattern
- `docs/dev-guide/migration-story-governance.json` — gate-mode designations + amendment log
- `docs/dev-guide/pydantic-v2-schema-checklist.md` — companion checklist for Pydantic v2 schema discipline
- `docs/dev-guide/story-cycle-efficiency.md` — companion governance rules for K-floor + gate-mode + dismiss rubric
- BMAD architecture template (when amended per N10 to require Anti-Pattern Mitigation cross-reference)

---

**Living document.** Each future project that finds a substrate gap not in this list adds an item.
