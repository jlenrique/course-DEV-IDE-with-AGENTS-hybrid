# Codex dispatch: Slab 6.0 production envelope substrate (Path A-prime per 5-agent ratification)

**Session:** 2026-04-27 (operator-authorized post-5-agent-party-mode-ratification)
**Branch:** `dev/langchain-langgraph-foundation`
**Predecessor state:**
- 5 commits landed in operator session: `ad98640` (A15+A16 substrate remediation), `1c4ebd3` (Wondercraft fix), `a7f6d72` (Slab 5a + Slab 6.1 opener), `c2065e9` (M2+M3 ceremonies), `56f408b` (operator docs + dispatches), `bf9aae5` (Slab 6.0 opener + A17+P3 + verdict annotation)
- Codex's Slab 6.1 strict-AC exploratory patch REVERTED honestly per decision_needed disposition (working tree on `app/manifest/compiler.py` etc. is in Codex's own state from c7d6447 / 7421f66 + the REVERTED state)
- 5-agent party-mode round 2026-04-27 ratified Path A-prime + scope-split
- Slab 6.0 spec: `_bmad-output/implementation-artifacts/migration-6-0-production-envelope-substrate.md` (~8pt dual-gate; party-mode greenlit)
- A17 + P3 anti-pattern entries filed at `docs/dev-guide/specialist-anti-patterns.md`
- Slab 6.1 spec WILL BE re-scoped to "runner consumes substrate" by you in lockstep with this Slab 6.0 implementation (per AC-J)

**Mission:** implement Slab 6.0 production envelope substrate per Path A-prime. The substrate this story ships is the missing piece that A17 (Substrate Designed for Isolation, Composition Assumed) named — composition contract + dispatch adapter + composition fixture proving end-to-end specialist chain works. With this substrate in place, Slab 6.1 (runner consumes substrate) becomes straightforward.

## Why this dispatch exists

Codex's Slab 6.1 strict-AC HALT (2026-04-27) revealed that the migration's specialist substrate doesn't admit composition. 14 specialists were built for ISOLATED execution (M3 deterministic harness pattern); composing them into a single executing LangGraph fails because:
1. Per-specialist `gate_decision` interrupts fire before production-level G1
2. Two-phase scaffold (`_plan` calls `make_chat_model`; `_act` does tool work) doesn't map to single-node execution
3. Shared `cache_state.cache_prefix` carrier overwritten per-specialist; downstream specialists fail because upstream output isn't visible

Per A17 counter-pattern: every multi-component contract must declare composition mode alongside isolated mode. Per P3 counter-discipline: before any composition-shape vote, run real upstream→downstream pair end-to-end.

This dispatch operationalizes the A17 counter-pattern AND the P3 counter-discipline as concrete substrate.

**Operator preference (binding, unchanged):** "do it right, no band-aids, only rational trade-offs that get named in writing." Halt-and-surface if substrate disagrees with spec. Same pattern as 3.1 + 5a.3 + A15 + A16 + A17 instances.

## Path A-prime decision (binding; ratified by 5-agent party-mode 2026-04-27)

- **Production envelope state-key** lives **alongside** `cache_state.cache_prefix`, NOT replacing or wrapping it
- **Specialists STAY UNCHANGED.** No specialist contract modifications. All 14 specialists' isolated-execution paths remain valid (M3 harness path remains the canonical isolated-execution path)
- **Dispatch adapter** at runner layer marshals specialist outputs into envelope and reads downstream specialist inputs from envelope
- **Composition fixture** (`ComposedSpecialistChainHarness` + `tests/composition/test_texas_to_cd_chain.py`) proves the channel works end-to-end on the EXACT pair that failed in Codex's strict-AC HALT (Texas → cd)
- **Specialist contracts that genuinely need a composition mode are deferred to Slab 8 consolidation** (Amelia A3 rider; tracked separately if needed)

This is Path A-prime per Winston's modification of Codex's original Path A. Eliminates "is this an adapter bug or a scaffold bug" ambiguity by separating per-specialist scratch (cache_prefix; specialist's own scratch) from cross-specialist accumulator (envelope; production composition's own).

## Scope per spec (8 ACs A through J; see `migration-6-0-production-envelope-substrate.md` for detail)

- **AC-A:** ProductionEnvelope Pydantic v2 strict (four-file-lockstep): model + JSON Schema + 5 shape-pin tests + golden fixture
- **AC-B:** ProductionDispatchAdapter core invocation contract: 3 integration tests
- **AC-C:** tests/composition/ tree + ComposedSpecialistChainHarness + test_texas_to_cd_chain.py (the load-bearing test; THE strict-AC HALT scenario succeeds here)
- **AC-D:** Composition Smoke gate amendment to slab-opener template
- **AC-E:** Specialist isolation invariant preserved (1 parametrized test across 14 specialists)
- **AC-F:** A17 + P3 entries-present test
- **AC-G:** Anti-pattern catalog harvest (no new entries expected)
- **AC-H:** TEMPLATE compliance (R1, R6, R8)
- **AC-I:** D12 close protocol (FIVE-line dual-gate)
- **AC-J:** Sprint-status + upstream-state state-flips at filing AND close (also re-scopes Slab 6.1 spec to "runner consumes substrate")

K-floor: 16 honest. K-target ~1.4× (target ~22).

## Key implementation guidance

**Decision #2 binding (A-prime variant):** envelope state-key is NEW alongside `cache_prefix`. Extend `app/models/state/run_state.py::RunState` to include `production_envelope: ProductionEnvelope | None = None` field. Specialists never read or write to this field directly; only the adapter does.

**Decision #3 binding (envelope schema; Pydantic v2 strict):** see spec for full schema. Critical invariants: `add_contribution` raises if specialist_id already present (immutability); each contribution carries `output_digest` (SHA256 for replay-regression); tz-aware datetime on `contributed_at`; cost_usd ≥ 0.0.

**Decision #4 binding (adapter contract):** see spec. Adapter is the ONLY surface that knows about envelope-vs-cache_prefix shape differences. Specialists unchanged; envelope unchanged; adapter bridges. New file: `app/marcus/orchestrator/dispatch_adapter.py`.

**Decision #5 binding (tests/composition/ tree):** new directory. Contains harness + chain test for Texas → cd. Use synthetic specialist outputs at the LLM-call boundary (mock `app.models.adapter.make_chat_model` for the chain test) so cost stays trivial (~$0). Real-OpenAI exercise is Slab 6.1's responsibility.

**Decision #6 binding (Composition Smoke gate amendment):** locate the slab-opener template (likely under `skills/bmad-create-story/` or `_bmad/`), add Composition Smoke step + disposition rules. The amendment is governance-shaped not code-shaped; one focused Markdown edit + 1 test asserting the amendment is present.

## What this dispatch does NOT do

- Does NOT modify any specialist code (`app/specialists/<name>/graph.py`)
- Does NOT modify the M3 deterministic harness (`marcus/orchestrator/m3_trial.py`)
- Does NOT touch `app/manifest/compiler.py` (preserved-state from Codex's c7d6447; envelope work is runner-layer)
- Does NOT touch FR34 gate machinery (`app/gates/resume_api.py`)
- Does NOT build the production runner itself (Slab 6.1's responsibility; consumes this substrate)
- Does NOT exercise live OpenAI (Slab 6.1's responsibility; this story uses synthetic specialist outputs in chain tests)

## Sequencing (per spec phasing)

- **Day 1:** ProductionEnvelope schema (AC-A) + four-file-lockstep + ProductionDispatchAdapter scaffold (AC-B core)
- **Day 2:** Composition fixture + Texas → cd chain test (AC-C; THE load-bearing test) + specialist isolation preservation test (AC-E)
- **Day 3:** Composition Smoke gate template amendment (AC-D) + A17+P3 entries-present test (AC-F) + RunState extension
- **Day 4-5:** Integration verification + buffer for halt-and-adapt cycles + docs update + close artifacts

## Halt-and-adapt expectations

Per spec: at least one halt-and-ratify cycle expected, probably around the Texas → cd chain test surfacing a real specialist contract that needs careful adapter handling. The chain test is the load-bearing AC; if cd's `_act` reads from `cache_state.cache_prefix` directly (vs from envelope), the adapter must construct cache_prefix appropriately for cd to consume — that's the surface where substrate-vs-spec disagreement is most likely.

If you discover that any specialist's `_act` REQUIRES cache_state mutations that don't map cleanly through the envelope-then-construct-cache_prefix pattern, HALT and surface. Operator decides whether to (a) extend the adapter contract, (b) restrict the chain pair to specialists where the pattern works, or (c) escalate scope.

## Disposition rules (unchanged)

- **`patch` items in your own work mid-implementation:** address in commits as you go
- **`defer` items:** file as deferred-inventory entries with explicit reactivation gates
- **`decision_needed` items:** HALT and surface. Do not silently choose. Same pattern as Slab 6.1 strict-AC HALT today

## Verification gates at dispatch close

- All 8 ACs (A through J) per `migration-6-0-production-envelope-substrate.md`
- `pytest tests/composition/ -q --tb=short` — all PASS (this is the load-bearing gate; AC-C + AC-E)
- `pytest tests/unit/runtime/test_production_envelope_strict.py tests/integration/marcus/test_dispatch_adapter.py tests/migration/test_composition_smoke_template_present.py tests/migration/test_a17_p3_entries_present.py -q --tb=short` — all PASS
- `pytest tests/specialists/ -q --tb=short` (or focused per-specialist slice) — all PASS (proves specialist isolation invariant intact per AC-E)
- `pytest tests/test_no_fictitious_model_ids.py tests/integration/runtime/test_cascade_ids_in_openai_published_catalog.py` — both PASS (no new fictitious IDs introduced)
- `ruff check app/models/runtime app/marcus/orchestrator tests/unit/runtime tests/integration/marcus tests/composition tests/migration` — clean
- `lint-imports --config pyproject.toml` — 9 KEPT (or higher if new contract added; if Slab 6.0 introduces new boundary, file as governance update)
- Sandbox-AC validator on this story spec — PASS

## What this dispatch unlocks

Slab 6.1 (runner consumes substrate; ~5pt; reduced from prior ~13pt) becomes straightforward after this lands:
- Production runner imports `ProductionDispatchAdapter`
- Composes manifest into LangGraph
- For each specialist node: invokes via adapter (which marshals envelope ↔ cache_prefix)
- HIL gates per FR34 unchanged
- Live-OpenAI smoke per AC-G of the (re-scoped) Slab 6.1 spec
- ~1-2 days Codex time for Slab 6.1 after Slab 6.0 lands

After Slab 6.0 + 6.1 both close + operator-witnessed live-OpenAI production trial:
- M5 condition #3 promotes from REFRAMED-AS-SLAB-6.0-+-SLAB-6.1 to RESOLVED
- The migration's actual product capability (real production-graph runner against live OpenAI) ships
- Bounded-MVP SHIP becomes "MVP SHIP + Slab 6.0/6.1 substantive product capability"
- Slab 6.2 (SciteProvider OAuth migration; `5a-2-scite-mcp-oauth-integration`) becomes operator-decision priority

## Effort estimate

~3-5 days focused Codex time. Likely 1-2 substrate-aware halts (most likely around Texas → cd chain test; possibly around RunState extension if there are downstream consumers I'm not aware of).

## Carry-forward notes

- Codex's preserved-state commits `c7d6447` + `7421f66` from yesterday remain on HEAD; build on top
- The Slab 6.1 spec at `_bmad-output/implementation-artifacts/migration-6-1-production-graph-runner.md` will be RE-SCOPED in lockstep per AC-J — when Slab 6.0 closes, edit the 6.1 spec to reflect "runner consumes substrate" scope (~5pt; remove the substrate-building ACs that are now in 6.0's responsibility; keep the runner-composition + HIL + trace-binding + live-smoke + evidence-discipline ACs)
- Repo-wide pytest remains environment-tainted on operator's Windows machine; story-owned slices + composition tests are the trustworthy gates
- Per the Composition Smoke gate amendment (AC-D), Slab 6.0 itself must operationalize the smoke as evidence — the Texas → cd chain test IS the Composition Smoke for this slab

## Final notes

This is the substrate-aware adaptation that A17 named. Done well, the migration's actual production capability becomes a clean 2-story sequence (6.0 substrate + 6.1 runner). Done poorly (substrate that recreates the composition-vs-isolation tension), the next iteration of A17 will surface — same as A15 + A16 + A17 cycle.

The party-mode discipline + bmad-code-review's substantive catches + halt-and-surface protocol have all worked today. Slab 6.0 is the next integration of those findings into real substrate. Build it carefully; the migration's product value depends on it.
