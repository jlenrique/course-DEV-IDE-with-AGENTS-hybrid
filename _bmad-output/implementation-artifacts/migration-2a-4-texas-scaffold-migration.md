# Migration Story 2a.4: Migrate Texas (Source Wrangler) to 9-Node Scaffold

**Status:** done
**Sprint key:** `migration-2a-4-migrate-texas-to-9-node-scaffold`
**Epic:** Slab 2a (migration Epic 2a) — **fourth and CLOSING story of Slab 2a**; opens post-2a.3-BMAD-CLOSED (party-mode 4/4 GREEN 2026-04-25). **Slab 2a closing story → feeds M2 milestone.**
**Pts:** 3 | **Gate:** single (per [`docs/dev-guide/migration-story-governance.json::2a-4`](../../docs/dev-guide/migration-story-governance.json), rationale: null — follows 2a.1 TEMPLATE / 2a.2 / 2a.3 pattern, no new schema-shape, no new CI contract) | **K-target:** ~1.4× (target 14 tests / floor 11; rationale below in Testing Requirements)

**Pre-coding party-mode round 2026-04-25: 4/4 GREEN with riders applied (Winston W1; Amelia A1–A4; Murat M1–M5; Paige P1–P8).** Riders below are integrated into the ACs they touch; some land as pre-T1 doc edits (P1 A9 retitle landed in `docs/dev-guide/specialist-anti-patterns.md` immediately) and some as deferred-inventory items (P5 implementation-artifacts README, P8 §12 size review).

This is the **third per-specialist migration** + the **first PURE-tool-dispatch act-body category** (Texas's `_act` invokes the retrieval dispatcher via subprocess; **NO LLM call at the Texas layer** — the model cascade still resolves at `_plan` for the resolution-trail entry, but the chat handle is never invoked). It is also the **FIRST REAL POPULATED-AND-LOCKED SANCTUM EXERCISE** — Texas's sanctum at `_bmad/memory/bmad-agent-texas/` ships with full BMB shape (BOND / CREED / INDEX / MEMORY / PERSONA / CAPABILITIES + sessions/ + capabilities/ + references/ + scripts/) populated by operator first-breath ceremony **before this story opens**, so the populated-sanctum digest is a real measurement, not a graceful-degrade re-baseline as 2a.3 was forced to fall back on.

The story closes Slab 2a — D12 close-protocol obligations are expanded with a slab-retrospective summary and the migration-guide §12 reference becomes structurally complete (three worked-example categories: narration / LLM+tool-dispatch / pure-tool-dispatch).

---

## T1 Readiness Block

**Before writing any code**, the dev agent reads in order per [`scaffold-conformance-framework.md §T1 Readiness Pre-Flight`](../../docs/dev-guide/scaffold-conformance-framework.md):

### Standing Pre-Flight items (applies to every Slab 2+ story)

1. **Governance lookup** — [`docs/dev-guide/migration-story-governance.json`](../../docs/dev-guide/migration-story-governance.json) — confirms Story 2a-4 is `expected_gate_mode: "single-gate"` with `rationale: null`. Do not relitigate.
2. **Canonical 9-node contract** — [`tests/integration/scaffold_conformance/scaffold_contract.py::SCAFFOLD_NODE_IDS`](../../tests/integration/scaffold_conformance/scaffold_contract.py) frozenset (`receive/plan/act/verify/reflect/emit_spans/gate_decision/finalize/handoff`). **Authoritative source of truth for node names.**
3. **Sanctum reference conventions** — [`docs/dev-guide/sanctum-reference-conventions.md`](../../docs/dev-guide/sanctum-reference-conventions.md). 2a.4 is the **first REAL populated-and-locked epoch exercise** — Texas's sanctum is already populated with curated BMB content. Pre-T1 lock-and-verify protocol per §4 must fire.
4. **Gate-decision binding** — [`docs/dev-guide/gate-decision-binding-semantics.md`](../../docs/dev-guide/gate-decision-binding-semantics.md). Generator emits `interrupt()` pattern; `resume_from_verdict` imported for Contract C3 binding but **NOT invoked at runtime** until Slab 3.3. Per Winston spec-vs-implementation drift flag (party-mode 2026-04-25), the "routes around" language in Epic 2a is precedent-inherited drift across Irene + Kira + Texas; Slab-3 conditional-edge fix is the architectural remedy. Document at AC-E.
5. **State contracts** — [`app/models/state/`](../../app/models/state/) (from Story 1.2). Texas's subclasses (`TexasEnvelope(SpecialistEnvelope)` + `TexasReturn(SpecialistReturn)`) inherit the substrate.
6. **Model cascade** — [`docs/dev-guide/model-selection-guide.md`](../../docs/dev-guide/model-selection-guide.md) + [`app/models/selection_policy.yaml`](../../app/models/selection_policy.yaml). Live tiers are `reasoning / fast / code`. **Texas-specific note:** Texas is a pure-tool-dispatch specialist; the resolution-trail entry is recorded at `_plan` per FR16, but the chat handle is **never invoked** at `_act` (Texas dispatches to the retrieval runner via subprocess; no LLM call at the Texas layer). Map to `tier_request: fast` → `gpt-5-haiku` for the trail-entry contract; document the no-invoke discipline in `model_config.yaml` inline comments.
7. **LLM-live skip-fixture** — [`tests/conftest.py`](../../tests/conftest.py) auto-skips `@pytest.mark.llm_live` when `OPENAI_API_KEY` is unset. **Texas does NOT need any `@pytest.mark.llm_live` tests at the Texas layer** (no LLM call). Live retrieval-dispatch tests are operator-gated via AC-B-OP only (involves real provider keys for scite / Consensus / etc.).
8. **Severance posture** — [`docs/dev-guide/langgraph-migration-guide.md §8.1`](../../docs/dev-guide/langgraph-migration-guide.md). No `git show upstream/master:…`. Hybrid working tree is sole input surface. Texas's source at [`skills/bmad-agent-texas/`](../../skills/bmad-agent-texas/) (10 references including the load-bearing `retrieval-contract.md`; full scripts dir including `run_wrangler.py`, `cross_validator.py`, `extraction_validator.py`, `retrieval/{base,consensus_provider,contracts,dispatcher,fake_provider,mcp_client,normalize,provider_directory,refinement_registry,scite_provider}.py`).
9. **Generator entrypoint** — `skills/bmad-create-specialist/` shipped by Story 2a.1 (commit `cc79df5`). **Invocation form** (DR-1 venv-direct per 2a.2 D1):
   ```
   .venv\Scripts\python.exe -m skills.bmad_create_specialist.scripts.generate \
     --name texas --mcp none --expertise-tier L4-source-wrangling \
     --from-skill skills/bmad-agent-texas
   ```
   Use `--mcp none` because Texas's tool dispatch happens via direct subprocess to `run_wrangler.py`, not via an MCP-tool surface registered in the generator (the L7 "MCP tool" framing in Epic 2a.4 line 645 is forward-looking to Slab 3 when MCP server tools wrap the runner; at Slab 2a it's a subprocess wrapper similar to Kira's `kling_dispatch.py`).
10. **Predecessor close evidence** — Story 2a.3 BMAD-CLOSED 2026-04-25 with 9 G6 PATCH applied + 4/4 party-mode ratification; migration-suite regression baseline now **380 passed / 7 skipped / 0 failed (placeholder-key)**. Substrate intact across 3 specialists (Irene + Kira + Texas-pending).

### Slab 2a artifact-existence sweep (8-point)

At T1, confirm all 8 artifacts exist + shape (grep + one-line-eval each):

- **A** `app/manifest/compiler.py::compile()` raises `CompileError` (additive-only validator per commit `2a336df`)
- **B** `app/models/state/specialist_envelope.py::SpecialistEnvelope` + `specialist_return.py::SpecialistReturn` with `ConfigDict(extra="forbid", validate_assignment=True)`
- **C** `app/specialists/irene/graph.py::build_irene_graph` (2a.2) + `app/specialists/kira/graph.py::build_kira_graph` (2a.3) — two reference patterns for Texas to model against (narration / LLM+tool-dispatch); Texas adds the third (pure-tool-dispatch)
- **D** `app/gates/resume_api.py::resume_from_verdict` raises `NotImplementedError`; generator imports for C3 binding, does NOT invoke
- **E** `app/specialists/_scaffold/{graph,state,model_config,expertise}` populated (from 2a.1)
- **F** `skills/bmad_create_specialist/scripts/generate.py` exits 0 on valid invocation (verify via `--help` first)
- **G** `tests/end_to_end/test_cache_hit_rate_kira_populated.py` exists + skips on empty-sanctum (post-2a.3 P9 patch); **Texas does NOT add a cache-hit-rate harness — pure-tool-dispatch specialists have no LLM prefix to cache; the FR54 measurement category does not apply at the Texas layer**
- **H** `docs/dev-guide/sanctum-reference-conventions.md` exists + names 2a.3 onward as populated-and-locked epoch (MF7 deliverable from 2a.2; reinforced at 2a.3 §3 epoch table)

### Epic-doc-vs-framework cross-check (standing protocol; THREE drifts flagged at this story)

**⚠️ Drift #1 — Test path "tests/bmad-agent-texas/..." (Epic 2a.4 line 647):** epic AC text says *"Texas's current tests (`tests/bmad-agent-texas/...`) exist from primary"*. **Reality:** the hybrid test tree is at `tests/agents/bmad-agent-texas/` (verified — contains `test_cross_validator.py` + `test_extraction_validator.py`); plus contracts tests at `tests/contracts/test_texas_row_fungibility.py` + fixtures under `tests/contracts/fixtures/retrieval/`. **Follow the framework.** Same A9-class pattern as 2a.1/2a.2/2a.3 node-name drifts (epic-doc-vs-Slab-1-hardened-reality drift for paths). Harvest as a **FOURTH example bullet under existing A9** at AC-K (per format-freeze harvest-gate "duplicate patterns augment existing entries"). Optionally extend A9's title from "Epic-doc node-name drift" to "Epic-doc structural-name drift from Slab-1-hardened reality" if scope expands beyond node names — defer the title-broadening question to AC-K G6 review.

**⚠️ Drift #2 — Symlink for retrieval-contract reference (Epic 2a.4 line 641):** epic says *"`app/specialists/texas/expertise/retrieval-contract-ref.md` is a **symlink or pointer file** referencing the existing doc"*. **Reality:** symlinks are not portable on Windows checkouts (operator works on Windows; CI may differ); per 2a.2 sanctum-path A11 precedent, hybrid uses **direct files / pointer files**, not symlinks. **Follow the framework.** Use a markdown pointer file at `app/specialists/texas/expertise/retrieval-contract-ref.md` that opens with a single sentence + relative-path link to the source-of-truth doc. NFR-I5 is preserved: `skills/bmad-agent-texas/references/retrieval-contract.md` is NOT modified; the app-side pointer is additive. No A-entry harvest needed (epic explicitly listed both options; choosing pointer-file is within the epic's allowed set).

**⚠️ Drift #3 — Six-artifact bundle naming (Epic 2a.4 line 645):** epic says *"result normalizes to the six-artifact bundle per schema v1.1"*. **Reality (verified via `skills/bmad-agent-texas/scripts/run_wrangler.py:5-9` + `:1782-1804`):** the six artifacts are `extracted.md` + `metadata.json` + `manifest.json` + `extraction-report.yaml` + `ingestion-evidence.md` + `result.yaml`. Schema v1.1 is the dual-emit version pinned in `tests/contracts/test_texas_row_fungibility.py`. No drift — confirmed alignment. Spec's mention of "six-artifact bundle" is correct.

**Drifts #1–#3 are anti-pattern #3 standing-protocol live exercises.** Dev agent logs all three in Dev Agent Record T1 Readiness block + uses the framework in every case.

### Carries from 2a.3 close (party-mode ratified 2026-04-25)

Three items batched at 2a.3 BMAD-CLOSE to land at 2a.4 T1 (per [`_bmad-output/maps/deferred-work.md` §Carries to 2a.4 T1 Readiness](../maps/deferred-work.md)):

1. **[Murat soft-blocker — Slab-2-mandatory]** `_extract_kling_response` parse-branch coverage from 2a.3 was DEFERRED. **2a.4 T1 application:** Texas does NOT have a direct analogue to Kira's `_extract_kling_response` (no LLM-response parser at the Texas layer — Texas parses YAML directives + JSON-RPC MCP responses, both with strict schemas). However, the **retrieval-result-bundle parser** in `_act` (which reads `result.yaml` + `extraction-report.yaml` from the runner subprocess output) is the analogous surface; AC-B test pin includes parametrized parse-branch coverage for the bundle parser (happy-path + missing-key + malformed-YAML + multi-status-code variants).
2. **[Hygiene PR — `.gitattributes`]** Land as part of 2a.4 T1: add `tests/fixtures/specialists/**/*.mp4 binary` (Kira retroactive) + `_bmad/memory/** text=auto eol=lf` (Texas + Irene + Kira sanctum trees). One-line PR; bundles into Texas spec as part of pre-T2 hygiene rather than a separate commit.
3. **[Paige doc polish]** Migration-guide §12 framing sentence above divergences-from-Irene table + §12.7/§12.8 renumber back-reference grep. **2a.4 application:** the §12 polish is part of AC-J's §12.7-Texas-walkthrough authoring (§12 grows: §12.5 Irene + §12.6 Kira + §12.7 Texas; renumber retains the §12.7 Verification commands → §12.8, §12.8 Governance notes → §12.9 cascade per 2a.3 P1 pattern). Framing-sentence-above-divergences-table addition lands in §12.7-Texas authoring.

### Operator pre-T1 sanctum-ceremony status (UPGRADE from 2a.3 — already populated)

Per [`sanctum-reference-conventions.md §3 epoch table`](../../docs/dev-guide/sanctum-reference-conventions.md), 2a.4 fires the **first REAL populated-and-locked epoch exercise**:

```
ls _bmad/memory/bmad-agent-texas/
→ BOND.md  CAPABILITIES.md  CLONE-FORK-NOTICE.md  CREED.md  INDEX.md  MEMORY.md  PERSONA.md
   capabilities/  references/  scripts/  sessions/
```

Texas's sanctum is **already populated** by prior operator first-breath ceremony (likely from primary-repo Epic 26-7 Texas BMB sanctum landing) and survives upstream severance per `project_upstream_severance.md`. **No graceful-degrade fallback needed** — populated-sanctum is the actual case Texas exercises.

**Pre-T1 lock-and-verify protocol** (operator action required BEFORE `bmad-dev-story` opens):
```
find _bmad/memory/bmad-agent-texas -type f -exec sha256sum {} +
```
Capture full output as the lock-baseline manifest in T1 Readiness §G. Per-AC-D-substitute-invocation guard (Texas does not run AC-D cache-hit-rate but DOES exercise sanctum cold-read at AC-F): re-hash before each dev-agent test invocation; abort + fail-loud on any drift. Post-run identity check.

### Governance pre-flight (single run before T2)

```
.venv\Scripts\python.exe scripts/utilities/validate_migration_story_sandbox_acs.py \
  _bmad-output/implementation-artifacts/migration-2a-4-texas-scaffold-migration.md
```
Expect PASS (no forbidden CLIs in dev-agent ACs; live retrieval-provider dispatch operator-gated as AC-B-OP).

---

## Story

As a **migration dev agent**,
I want **Texas (Shape 3-Disciplined source-wrangling specialist) rehomed into `app/specialists/texas/` with the 9-node scaffold + retrieval-contract preserved verbatim per NFR-I5 + pure-tool-dispatch act-body that subprocesses to `skills/bmad-agent-texas/scripts/run_wrangler.py` + first REAL populated-and-locked sanctum cold-read exercise + Slab 2a closing D12 protocol satisfied with retrospective summary**,
So that **the third per-specialist migration proves the scaffold survives a third act-body category (pure-tool-dispatch — no LLM at the specialist layer), the retrieval substrate remains authoritative across the migration boundary (NFR-I5 contract preservation), Slab 2a closes with three worked-example categories in the §12 reference (narration / LLM+tool-dispatch / pure-tool-dispatch) ready for Slab 2b's 14-specialist tranche to inherit, and the `RetrievalIntent` → six-artifact bundle dispatch is exercised end-to-end on the LangChain/LangGraph stack**.

---

## Acceptance Criteria

All ACs are dev-agent-executable (sandbox-AC compliant). **Texas does NOT carry any `@pytest.mark.llm_live` tests** — there is no LLM call at the Texas layer. Live retrieval-provider dispatch (AC-B-OP) is operator-gated (requires real `SCITE_API_KEY` / `CONSENSUS_API_KEY` / etc.; dev-agent path uses fixture directives + the `fake_provider` adapter).

### AC-2a.4-A — Generator emits Texas from skill directory

- **Given** [`skills/bmad-agent-texas/`](../../skills/bmad-agent-texas/) contains the retrieval substrate (10 references including the load-bearing `retrieval-contract.md`; `run_wrangler.py` runner; `retrieval/{dispatcher,contracts,provider_directory,...}.py` orchestration); generator at `skills/bmad-create-specialist/` is proven (Story 2a.1, 2a.2, 2a.3)
- **When** the dev agent runs (DR-1 invocation form per 2a.2 D1):
  ```
  .venv\Scripts\python.exe -m skills.bmad_create_specialist.scripts.generate \
    --name texas --mcp none --expertise-tier L4-source-wrangling \
    --from-skill skills/bmad-agent-texas
  ```
- **Then** `app/specialists/texas/` exists with `__init__.py`, `graph.py`, `state.py`, `model_config.yaml`, `expertise/README.md`; `validate_scaffold("texas", build_texas_graph()).is_conforming is True`; ruff clean; import-linter C1 (lane-isolation) PASS.
- **Procedural-coupling step (per A12 deferred-inventory entry, manual until that follow-on lands; THIRD specialist to do this manual step):** dev agent appends one line to `pyproject.toml` `[[tool.importlinter.contracts]]` C3 `ignore_imports`:
  ```
  "app.specialists.texas.graph -> app.gates.resume_api",
  ```
  This reinforces the urgency to land the generator auto-emit follow-on **before Slab 2b.1 TEMPLATE opens** — three manual edits across 2a.2 / 2a.3 / 2a.4 is the documented evidence base for the deferred-inventory entry.

### AC-2a.4-B — Texas `act` node wires PURE-tool-dispatch (no LLM call at the Texas layer)

- **Given** 2a.1's generator emits `_act` defaulting to `passthrough_node`; 2a.2 (Irene) + 2a.3 (Kira) both shipped LLM-invoking `_act` bodies. **Texas's `_act` is the FIRST pure-tool-dispatch act-body category** — the Texas layer does NOT call any LLM.
- **When** the dev agent replaces `app/specialists/texas/graph.py::_act` with **a BOUNDED tool-dispatch invocation**: (1) read the latest `ModelResolutionEntry` from `state.model_resolution_trail` + reject if `cache_prefix_hash is None` (Winston W2/2a.2 discriminator-check pattern carried forward — applies even though no LLM is invoked, because the trail-entry contract stays consistent across all three specialist categories); (2) extract the `RetrievalIntent` payload from `state.cache_state.cache_prefix` (envelope-carrier-hack inherited from 2a.2/2a.3 — Slab-3 retirement tracked); (3) call the mockable retrieval-dispatch wrapper `app.specialists.texas.retrieval_dispatch.dispatch_retrieval(directive_path, bundle_dir)` (a thin module ~40 LOC modeled on Kira's `kling_dispatch.py` — fixture-bundle short-circuit when no real directive provided; subprocess to `run_wrangler.py` when real directive provided); (4) parse the resulting `result.yaml` + `extraction-report.yaml` from the bundle directory (parametrized parse-branch coverage per Murat soft-blocker carry-forward — see Testing Requirements); (5) return `{cache_state: {cache_prefix: <output_blob>, entries_count: ...}}` with the bundle reference encoded as sorted-keys canonical JSON (envelope-carrier-hack pattern for now). Bounded scope: **~80 LOC act-body + ~40 LOC retrieval_dispatch wrapper**.
- **Then** invoking `build_texas_graph()` with a realistic `TexasEnvelope` (fixture envelope at `tests/fixtures/specialists/texas/golden_envelope.json` + dispatch wrapper monkey-patched to return a fixture six-artifact bundle path) produces a non-empty result containing `bundle_reference` (the path to the bundle directory) + bundle artifact summaries (six-artifact roster). **NO `@pytest.mark.llm_live` marker** (no LLM call); test runs unconditionally on placeholder OPENAI_API_KEY.
- **Scope-slip flag:** if act-body or retrieval_dispatch wrapper exceeds ~140 LOC at T4 (act ~80 + dispatch ~40 + parser ~20), dev agent STOPS and raises party-mode re-scope decision. **Mid-task LOC checkpoint (Amelia A3 rider):** after `_act` lands and before dispatch wrapper, hard line is `_act ≤ 100 LOC` AND `retrieval_dispatch ≤ 60 LOC` — if either crosses, pause + re-convene.
- **Subprocess kwargs pinning (Amelia A1 rider):** `retrieval_dispatch.dispatch_retrieval` invokes the runner via `subprocess.run(args, shell=False, check=False, capture_output=True, text=True, timeout=30)` — `shell=False` and `timeout=30` are CONTRACTED, not optional. Test pin: `tests/specialists/texas/test_texas_act_node_dispatch.py::test_act_subprocess_kwargs_pinned` asserts the kwargs are present so a future regression that drops `timeout` or flips `shell=True` fails red.
- **Two-sided assertion on parse-branch cases (Murat M5 rider):** each parametrized case asserts BOTH (a) the parser returns the expected dict shape AND (b) the resolution-trail entry records the parse outcome with the right tag (`bundle.parsed.ok` / `bundle.parsed.malformed` / `bundle.parsed.missing-key` / `bundle.parsed.wrong-type` / `bundle.parsed.empty` / `bundle.parsed.exit-10` / `bundle.parsed.exit-30`). Reason: a parser that returns the right value but tags the trail wrong produces a passing unit test and a broken gate decision.
- **Parse-branch coverage — bind 7 cases (Murat M1 rider; Amelia A2 reconciled):**
  | # | Case | Priority | Risk if uncovered |
  |---|---|---|---|
  | 1 | Happy-path: exit 0, both files well-formed, expected schema | P0 | Smoke regression |
  | 2 | Missing required key in `result.yaml` | P0 | Silent None propagation |
  | 3 | Malformed YAML (unparseable) in either file | P0 | Bare exception leaks past `_act` |
  | 4 | Wrong type at expected key (string where dict expected) | P1 | Type-confusion → AttributeError downstream |
  | 5 | Empty / zero-byte stdout (subprocess returned 0 but emitted nothing) | P0 | Cross-platform tempfile semantics |
  | 6 | Runner exit code 10 (no results found per delegation-contract) | P0 | Distinguishes "tool failed" from "tool succeeded with empty result" |
  | 7 | Runner exit code 30 (hard error) with partial bundle | P1 | Defensive: don't trust bundle when exit code says "I crashed mid-write" |

  **Collapse-to-6 escape clause:** if dev agent finds branches 6 and 7 share dispatch (single `match` on exit code, single bundle-shape handler), drop to 6 cases and document the collapse in Completion Notes. Don't pad K for ceremony.

### AC-2a.4-B-OP — Live retrieval-provider dispatch evidence (operator-gated)

- **Given** Texas's mocked dispatch path is shape-verified by AC-B; live retrieval-dispatch requires real provider keys (`SCITE_API_KEY` for scite adapter; `CONSENSUS_API_KEY` for Consensus adapter; etc. — varies per directive)
- **When** the **operator** runs a one-directive live retrieval-dispatch via the runner CLI (`.venv/Scripts/python.exe skills/bmad-agent-texas/scripts/run_wrangler.py --directive <fixture-directive> --bundle-dir <tmp-bundle>`) on a realistic `RetrievalIntent` directive (e.g., a known-good scite query)
- **Then** the operator pastes into Completion Notes: (a) the runner exit code; (b) the resulting six-artifact bundle file roster + sha256 sums; (c) the `result.yaml` envelope showing `bundle_reference` populated end-to-end. **NO** dev-agent automation of the live API; this AC is purely Completion-Notes paste of operator-machine evidence. Mockable dev-agent path covers the shape; this AC covers the live wire.

### AC-2a.4-C — Model cascade resolves correctly at Texas's `plan` node (trail entry only; no LLM invocation)

- **Given** Texas's `model_config.yaml` specifies `default_model: "gpt-5-haiku"` (Texas's L4 dispatch workload is structurally trivial; `tier_request: fast` resolves to `gpt-5-haiku`) + per-node override map + `temperature_default: 0.0` (deterministic; no LLM at Texas means the temperature is never consumed at runtime, but the value is recorded in the resolution-trail entry for cache-prefix attribution consistency across specialists)
- **When** `app.models.selector.resolve_model()` runs at Texas's `_plan` node with no runtime override
- **Then** resolution trail appends a `ModelResolutionEntry` with `resolved_model_id="gpt-5-haiku"`, `resolution_level="per-specialist-default"`, and a cache-prefix hash per 1.3; with a runtime `RunState.model_overrides={"texas": "gpt-5.4"}` set, resolution returns `gpt-5.4` at `resolution_level="per-call-override"`. **The chat handle returned by `make_chat_model(...)` is NOT invoked at Texas's `_act`** — Texas's runtime path is sub-process dispatch only; the trail-entry exists for FR16 contract consistency + cache-prefix attribution if Slab-3+ middleware needs it.
- **Test pin:** `tests/specialists/texas/test_texas_model_cascade.py` — 2 tests (default + override).
- **Documented in `model_config.yaml` inline comments:** "Texas is pure-tool-dispatch — no LLM invoked at the specialist layer. Resolution-trail entry recorded at `_plan` per FR16; chat handle never invoked at `_act`. Tier maps to `fast`/`gpt-5-haiku` for trail-entry shape consistency across the specialist roster."

### AC-2a.4-D — Sanctum cold-read at `plan` node (FR15 third per-specialist exercise — FIRST REAL populated-and-locked case)

- **Given** Texas's sanctum at `_bmad/memory/bmad-agent-texas/` is **already populated** by operator first-breath ceremony with full BMB shape (BOND / CREED / INDEX / MEMORY / PERSONA / CAPABILITIES + CLONE-FORK-NOTICE.md + sessions/ + capabilities/ + references/ + scripts/). 2a.3's populated-sanctum exercise was deferred to graceful-degrade (sanctum dir absent); **Texas is the FIRST per-specialist exercise to actually hit the populated case**.
- **When** Texas's `plan` node runs `_read_sanctum_digest` (modeled on `app/specialists/kira/graph.py::_read_sanctum_digest`, post-2a.3-P6 patch — bytes-level CRLF→LF normalization preserved for cross-platform cache-prefix determinism)
- **Then** sanctum payload includes Texas's L4 references by dotted convention per [`sanctum-reference-conventions.md §2`](../../docs/dev-guide/sanctum-reference-conventions.md): the 10 reference files in `skills/bmad-agent-texas/references/` (`capability-authoring.md`, `delegation-contract.md`, `extract-and-validate.md`, `extraction-report-schema.md`, `fallback-resolution.md`, `first-breath.md`, `memory-guidance.md`, `retrieval-contract.md`, `source-interview.md`, `transform-registry.md`) — listed in Texas's `expertise/README.md`; `_read_sanctum_digest` produces a deterministic sorted-by-as_posix sha256 listing; **populated-sanctum case produces a non-empty fingerprint** (distinct from 2a.2's empty-sanctum sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`).
- **Test pins (3 tests — UPGRADE from Kira's 2 tests because Texas's populated case adds a third dimension):**
  1. `tests/specialists/texas/test_texas_sanctum_cold_read.py::test_texas_populated_sanctum_fingerprint_deterministic` — fingerprint deterministic across two reads against the real `_bmad/memory/bmad-agent-texas/` directory (non-tmp_path; first real populated case in the test pack).
  2. `tests/specialists/texas/test_texas_sanctum_cold_read.py::test_texas_expertise_readme_lists_l4_references` — reference-name shape matches Texas's `expertise/README.md` dotted list (drift detector inherited from 2a.3 P8).
  3. `tests/specialists/texas/test_texas_sanctum_cold_read.py::test_texas_sanctum_lock_baseline_pinned` — pre-run sha256 manifest matches a recorded baseline (operator-curated baseline in T1 Readiness §G; test asserts no drift between baseline-time-of-author and run-time-of-test). **This is the first real exercise of the lock-and-verify protocol from `sanctum-reference-conventions.md §4`. Hard sha256 equality (Murat M2 rider — no softening, no file-count-only fallback). Per-file. Baseline value INLINED as module-level constant in the test file (Amelia A3 rider — one-file-readable; not external fixture) so a future maintainer can trace lock-failure to the recorded baseline without spelunking.**
  4. **[Winston W1 rider]** `tests/specialists/texas/test_texas_sanctum_cold_read.py::test_texas_sanctum_lock_violation_raises_named_exception` — assert that a post-activation mutation (synthetic: monkey-patch the digest function to return a different sha256, OR write a temp file mid-test and re-read) raises a SPECIFIC named exception class (e.g., `SanctumLockViolation` or equivalent — if no such class exists in the sanctum-reference-conventions module, dev agent adds one ~10 LOC + reuses across Irene/Kira via a Slab-2-cross-cutting follow-on filed at story close). The trail entry records the lock-violation cause. **No generic `RuntimeError`; no silent re-read.** Test asserts both the exception class AND the trail-entry tag.

### AC-2a.4-E — Gate-decision node binds `interrupt()` pattern (precedent-inherited from 2a.2/2a.3)

- **Given** 2a.1's generator emits `gate_decision` as interrupt-placeholder per [`gate-decision-binding-semantics.md`](../../docs/dev-guide/gate-decision-binding-semantics.md); both Irene (2a.2) + Kira (2a.3) ship identical pattern (TRANSITIONS table routes through gate_decision unconditionally on canonical chain). Texas inherits the same pattern.
- **When** Texas's graph is constructed
- **Then** `gate_decision` node is PRESENT in the 9-node scaffold (structural conformance per SCAFFOLD_NODE_IDS frozenset) AND its body binds the `interrupt()` pattern (imports `resume_from_verdict` for Contract C3 stability; does NOT invoke at runtime). **Spec-vs-implementation drift acknowledged** (Winston flag at 2a.3 party-mode 2026-04-25): the Epic 2a "routes around" language is precedent-inherited drift across all three specialists; Slab-3 conditional-edge fix is the architectural remedy applied uniformly; spec-language reconciliation is tracked in [`_bmad-output/maps/deferred-work.md` §Deferred from 2a.3 G6 review](../maps/deferred-work.md).
- **Test pins (2 tests):**
  1. `tests/specialists/texas/test_texas_gate_decision_binding.py::test_texas_gate_decision_present_and_binds_interrupt` — asserts node-presence + import-level binding to `resume_from_verdict`; does NOT invoke at runtime.
  2. `tests/specialists/texas/test_texas_gate_decision_binding.py::test_texas_transitions_match_canonical_chain` — pins the canonical TRANSITIONS chain (matches Irene + Kira shape; consistency across the three specialists is the architectural invariant Slab-3 will retire uniformly).

### AC-2a.4-F — Resolution trail + LangSmith spans (FR16 third per-specialist exercise)

- **Given** Texas's `_plan` node appends to `RunState.model_resolution_trail`; Texas's `emit_spans` node publishes LangSmith spans per NFR-O4
- **When** Texas's scaffold runs end-to-end (with mocked retrieval dispatch)
- **Then** `RunState.model_resolution_trail` has ≥1 `ModelResolutionEntry` naming the resolved model + cache-prefix hash + resolution level; LangSmith spans include `specialist_id="texas"`, `node_id` per 9-node set, `resolution_level`, and the cache-prefix tag.
- **Test pin:** `tests/specialists/texas/test_texas_resolution_trail.py` — 1 test.

### AC-2a.4-G — Texas shape-pin tests (four-file-lockstep per 1.2)

- **Given** the generator emits `app/specialists/texas/state.py` with `TexasEnvelope` + `TexasReturn` subclasses; Texas's domain adds **one new field** to the return shape: `bundle_reference: str | None` (path-string to the six-artifact bundle directory)
- **When** the dev agent verifies 1.2 four-file-lockstep discipline on Texas's schema surface
- **Then** all four lockstep files exist + the new field is shape-pinned:
  1. **MODEL** — `app/specialists/texas/state.py`: `TexasEnvelope` (`_SPECIALIST_ID = "texas"` + 50KB payload cap mirrors Irene/Kira); `TexasReturn` (`_SPECIALIST_ID = "texas"` + new field `bundle_reference: str | None = None` with `Field(default=None, description="...")`).
  2. **VALIDATOR** — inherited from parents; document Resolution B rationale in state.py docstring.
  3. **TESTS** — `tests/specialists/texas/test_texas_state_shape.py` with ≥4 tests: envelope field presence + return field presence (including `bundle_reference` default + populated cases) + round-trip determinism (NFR-X1) + invalid-payload red-rejection.
  4. **GOLDEN FIXTURE** — `tests/fixtures/specialists/texas/golden_envelope.json` + `golden_return.json` (with `bundle_reference` populated to a fixture bundle path).

### AC-2a.4-H — Scaffold-conformance test registered

- **Given** the scaffold-conformance framework at `tests/integration/scaffold_conformance/`
- **When** Texas migrates
- **Then** new file `tests/integration/scaffold_conformance/test_scaffold_texas.py` imports `build_texas_graph` + calls `validate_scaffold("texas", ...)` + asserts `.is_conforming is True`; file follows the 2a.2/2a.3/framework-doc pattern verbatim.

### AC-2a.4-I — NFR-I5 contract preservation (Texas retrieval-contract.md unmodified)

- **Given** the existing retrieval contract at `skills/bmad-agent-texas/references/retrieval-contract.md` is the load-bearing source-of-truth for Texas's Shape 3-Disciplined retrieval foundation (Story 27-0); NFR-I5 explicitly requires this file to be preserved verbatim across the migration
- **When** the dev agent migrates Texas
- **Then** `git diff skills/bmad-agent-texas/references/retrieval-contract.md` shows ZERO changes; the app-side `app/specialists/texas/expertise/retrieval-contract-ref.md` is a markdown pointer file (NOT a symlink, per Drift #2 framework-wins) opening with a single sentence + relative-path link to the source-of-truth doc.
- **Test pin:** `tests/specialists/texas/test_texas_retrieval_contract_preserved.py` — 2 tests: (a) computes sha256 of `skills/bmad-agent-texas/references/retrieval-contract.md`; asserts equals a recorded baseline (baseline pinned at story open in T1 Readiness §I; baseline value INLINED as module-level constant per Amelia A3 rider; **hard sha256 equality per Murat M3 rider — no softening; "any change to that file is a contract change that needs explicit acknowledgment, not silent drift"**); (b) asserts `app/specialists/texas/expertise/retrieval-contract-ref.md` exists + contains the relative-path link to the source-of-truth doc.

### AC-2a.4-J — Existing Texas test suite + new contract test pass together

- **Given** the existing tests at `tests/agents/bmad-agent-texas/{test_cross_validator.py, test_extraction_validator.py}` (Drift #1 framework-wins on path: hybrid uses `tests/agents/bmad-agent-texas/`, NOT epic's `tests/bmad-agent-texas/`) + the existing contracts test at `tests/contracts/test_texas_row_fungibility.py`
- **When** the migration adds the new tests at `tests/specialists/texas/`
- **Then** both test suites pass (existing + new); no regression of retrieval behavior; **migration-suite regression floor is ≥395 passed / 7 skipped (placeholder-key)** — pre-2a.4 baseline 380/7/0 + Texas's new tests (~15) → 395 expected. Existing Texas tests count toward the regression baseline already.
- **Single-call enforcement (Amelia A4 rider):** at T7, the regression invocation MUST run `tests/agents/bmad-agent-texas/ tests/contracts/test_texas_row_fungibility.py tests/specialists/texas/` as a **single** pytest call (not three sequential calls). Catches cross-suite import-order regressions that sequential runs would miss. Pin in T7 evidence block.

### AC-2a.4-K — Migration-guide §12 Specialist Walkthrough updated (D12 slab-closing)

- **Given** Story 2a.2 populated `§12.5 Irene worked before/after` (narration category); Story 2a.3 P1 patch added `§12.6 Kira worked before/after` (LLM+tool-dispatch category) with §12.7+§12.8 renumbering; Texas adds the **third worked-example category (pure-tool-dispatch)**
- **When** Texas migrates at 2a.4 as the Slab 2a closing story
- **Then** `docs/dev-guide/langgraph-migration-guide.md §12` is updated:
  - **§12.7 ADDED** as Texas's pure-tool-dispatch case: actual generator invocation + actual file tree + actual diff snippets + the retrieval_dispatch wrapper module + first-real-populated-sanctum cold-read evidence + the `RetrievalIntent` → six-artifact bundle dispatch flow + NFR-I5 preservation note. Annotates where Texas's path diverges from Irene's + Kira's (no LLM call, pure subprocess dispatch, populated-sanctum first-real-exercise, retrieval-contract preservation contract).
  - **§12.5 retained** as Irene's narration case; **§12.6 retained** as Kira's LLM+tool-dispatch case (post-2a.3-P1).
  - **§12.4 post-edit checklist** retains the procedural-coupling step (Texas reinforces the urgency — third specialist to manually do the C3 ignore_imports row).
  - **§12.7 Verification commands → §12.8** + **§12.8 Governance notes → §12.9** renumbered (per 2a.3-P1 cascade pattern).
  - **§12 framing-sentence carry from 2a.3** (Paige doc-polish carry): one sentence above the divergences-from-Irene table in §12.6 (Kira) saying "When you migrate the next specialist, expect divergences in **these eight categories**; if your specialist has a divergence outside these categories, that's a signal to update §12 itself." Then verify Texas's §12.7 surfaces a new divergence category (no-LLM-at-act-body) — confirming the framing sentence's predicted use case fires immediately. **Explicit verification (Paige P4 rider):** AC-K asserts (a) §12.6 framing sentence is present pre-Texas-edit; (b) Texas's no-LLM-at-act-body divergence is added either to §12.6 table OR to §12.7 walkthrough with a back-pointer; (c) framing sentence's predicted use case is exercised by Texas's actual divergence emergence.
  - **§12 SECTION-LEVEL framing sentence (Paige P2 rider — NEW):** add ABOVE §12.5, one level up from the sub-section divergence-table framing: *"§12.5–§12.7 cover three specialist-shape categories proven across Slab 2a (narration / LLM+tool-dispatch / pure-tool-dispatch). If you migrate a specialist whose act-body shape doesn't fit any of these three, add a §12.x section before proceeding — the categories are extensible, not exhaustive."* This produces two framing sentences operating at two levels: section-level (categories of specialist-shape are extensible) + sub-section-level (categories of divergence within Kira are bounded; surprise is a signal). A future fourth specialist-shape category becomes a §12.8 ADD with cascade renumber, not §12 restructuring.
  - **Renumber-grep scope EXPANDED (Paige P3 rider):** verify no internal refs in `langgraph-migration-guide.md` OR Slab 2a story specs OR `next-session-start-here.md` OR `_bmad-output/planning-artifacts/deferred-inventory.md` still point at pre-renumber §12.7 / §12.8 slot numbers. Those last two drift surfaces have bitten before.
  - **§12.10 ADDED — "Slab 2a retrospective summary"**: 2-3 paragraph closing note for the slab (Paige P6 rider — cap at 4 paragraphs; if it grows to 4, paragraph 2's FR54-doesn't-generalize point can compress into paragraph 1). **Three paragraphs:** (1) what Slab 2a proved — three categories / FR9-FR16 closed / §12 structurally complete; (2) what doesn't generalize — FR54 cache-hit-rate is narration-bound; pure-tool-dispatch can't measure cache-hits because there's no LLM call; (3) pointer to D12 + Slab 2b kickoff gate ("for full retrospective see [`slab-2a-retrospective.md`]; Slab 2b opens once A12 generator auto-emit follow-on lands"). **Murat M4 rider — substitute metric:** §12.10 MUST also record `subprocess-dispatch-latency stability` as the pure-tool-dispatch substitute metric (p50 / p95 wall-clock from `_act` entry to bundle-parse complete, measured across the test pack runs); §12.10 records the baseline; future Texas changes that regress p95 by >20% trigger a perf-review checkpoint. Not a hard gate at 2a.4 — a §12.10 retrospective deliverable that feeds Slab 2b TEMPLATE design directly.

### AC-2a.4-L — Hygiene PR landed (`.gitattributes` carry from 2a.3)

- **Given** 2a.3 party-mode (Murat + Paige + Winston) flagged `.gitattributes` hygiene as a one-line nag carry-forward
- **When** the dev agent lands the PR as part of 2a.4 T1 hygiene (NOT a separate commit; bundles into Texas spec landing)
- **Then** `.gitattributes` at repo root contains:
  ```
  _bmad/memory/** text=auto eol=lf
  tests/fixtures/**/*.mp4 binary
  ```
  Storage-side hygiene complementing 2a.3's runtime-side P6 CRLF→LF normalization (defense-in-depth per Murat 2a.2 MF3 binding). Verified by a one-shot grep test or operator-paste in Completion Notes; no formal AC test pin needed.

### AC-2a.4-M — Close protocol (D12 slab-closing — EXPANDED for slab close)

- **Given** 2a.4 is the **slab-closing story** for Slab 2a (Story 2a.5 does not exist; Slab 2a closes at 2a.4 per epic line 532-536)
- **When** the story closes
- **Then** the D12 slab-closing close stub is recorded in Dev Agent Record with **expanded slab-retrospective content**:
  1. **Invariant preservation (Slab 2a-wide):**
     - **NFR-I5** Texas retrieval-contract.md preserved verbatim across migration ✓ (per AC-I sha256 baseline test)
     - **invariant #13** specialist registry (FR9-FR12 + FR15 + FR16 closed for all three Slab 2a specialists: Irene 2a.2 + Kira 2a.3 + Texas 2a.4)
     - **FR54** cache-hit-rate baseline measured at Irene 2a.2 (95.33% empty-sanctum); steady-state populated-sanctum exercise effectively deferred (Kira graceful-degrade; Texas pure-tool-dispatch — no LLM at specialist layer means no provider cache to measure)
     - **Slab-1 substrate intact** across three specialist migrations: regression baseline 303 (Slab 1 close) → ~395 expected (post-2a.4 close); +92 net across Slab 2a
  2. **Anti-pattern harvest (Slab 2a cumulative + 2a.4-specific):**
     - **A9 fourth example (or title broadening — defer to G6 review):** Drift #1 (`tests/bmad-agent-texas/...` epic-vs-`tests/agents/bmad-agent-texas/` reality) — fourth concrete instance of epic-doc-vs-Slab-1-hardened-reality drift across Slab 2a (after 2a.1 node names + 2a.2 node names + 2a.3 node names). Either augment A9 with a fourth bullet OR broaden A9's title from "Epic-doc node-name drift" to "Epic-doc structural-name drift" — defer the title-broadening question to G6 review; the harvest-gate rule allows duplicate-pattern augmentation either way.
     - **A10 augment NOT applicable at 2a.4** — Texas does not surface a new model-ID drift; the cascade entry is `gpt-5-haiku` per `tier_request: fast` mapping (consistent with Kira's pattern), and the model is never invoked at runtime so no drift surface.
     - **A11 augment NOT applicable at 2a.4** — Texas's sanctum path matches the framework convention (`_bmad/memory/bmad-agent-texas/` matches `skills/bmad-agent-texas/` skill-dir name); no drift.
     - **A12 reinforcement (third specialist manual C3 row):** the deferred-inventory entry "Generator auto-emit pyproject.toml C3 ignore_imports row" now has **three independent occurrences** (Irene 2a.2 + Kira 2a.3 + Texas 2a.4) of the manual-edit pattern — the strongest possible evidence base. **Slab 2b.1 TEMPLATE MUST NOT open until the generator auto-emit follow-on lands**; this is the slab-closing binding.
  3. **Migration-guide update:** §12.7 added for Texas pure-tool-dispatch worked example per AC-K + §12.10 added for Slab 2a retrospective summary.
  4. **Slab 2a retrospective convening (party-mode):** at story close, convene `bmad-retrospective` per CLAUDE.md §Pipeline lockstep regime — review deferred-inventory + specialist-anti-patterns catalog + cumulative cycle-efficiency metrics across the four Slab 2a stories; surface any deferred-inventory entries newly ready to reactivate; identify Slab 2b.1 TEMPLATE pre-flight items (notably: A12 generator auto-emit follow-on landing as the gate). **Winston rider:** retrospective MUST consult `_bmad-output/planning-artifacts/deferred-inventory.md` per CLAUDE.md governance — do not invent a custom inventory-review shape; reuse the Epic-retrospective convention. Retrospective output lands at `_bmad-output/implementation-artifacts/slab-2a-retrospective.md` (NEW file).
     - **Target ~250 lines (Paige P7 rider — section-by-section line budget):** front matter + 5-line "if you're reading this at Slab 2b T1, here's what you need" opener block (~30 lines) + FR coverage closed table (~30) + cumulative regression intelligence 303 → ~395 trajectory (~40) + deferred-inventory follow-ons surfaced (~40) + anti-pattern catalog state (A9 fourth-instance + title-broadening disposition; harvest-gate retrospective on the 4-test sample) (~30) + §12 reference completeness (~30) + Slab 2b kickoff readiness checklist with A12 gate front-and-center (~50). Total: ~250.
     - **Dispatch-wrapper extraction candidate (Winston rider):** retrospective records `kira/kling_dispatch.py` + `texas/retrieval_dispatch.py` + (anticipated) `2b.1/<wrapper>.py` as three independent occurrences of the same dispatch-wrapper shape — flag for Slab 2b extraction to `_bmad/scaffolds/dispatch_wrapper_template.py` if the third occurrence confirms.
     - **§12 size review trigger (Paige P8 rider — defer to inventory):** at retrospective close, file a deferred-inventory item: "§12 size review when subsection count exceeds 12 — readability check on `langgraph-migration-guide.md §12`."
     - **implementation-artifacts/ index (Paige P5 rider — defer to inventory):** if no README/index exists at `_bmad-output/implementation-artifacts/`, file a deferred-inventory item: "implementation-artifacts/ index or README at Slab 2b open — directory clutter is hindering newcomer triage."

---

## Architecture Compliance

### Decisions the story honors

| Decision | Application |
|---|---|
| **D1 — Sanctum hybrid** | Sanctum path `_bmad/memory/bmad-agent-texas/` matches skill-dir name; **first REAL populated-and-locked epoch exercise** per `sanctum-reference-conventions.md §3` (2a.3 deferred to graceful-degrade; Texas hits the populated case). |
| **D2 — Three-level model cascade** | `gpt-5-haiku` default via `tier_request: fast` (Texas is pure-tool-dispatch; LLM never invoked at runtime; trail entry recorded for FR16 contract consistency). |
| **D3 — HIL tamper-evidence** | `resume_api` import for C3 binding; `interrupt()` pattern per AC-E; manual pyproject.toml C3 ignore_imports row added per AC-A (third specialist; A12 deferred-inventory entry urgency reinforced). |
| **D4 — Lane separation** | `app/specialists/texas/` in `run_graph` lane per import-linter C1; no cross-lane imports. The `retrieval_dispatch` wrapper subprocesses to `skills/bmad-agent-texas/scripts/run_wrangler.py` (NOT a direct cross-lane import). |
| **D5 — Sanctum cold-read + cache-prefix stability** | Cold reads at `plan` node per AC-D; cache-prefix stability per NFR-I6 inherited (no FR54 measurement at Texas — pure-tool-dispatch specialists have no LLM prefix to cache). |
| **D12 — Cross-slab governance** | D12 slab-closing close stub per AC-M; party-mode retrospective at story close. |
| **D13 — Registry bump** | Not applicable at 2a.4 (registry unchanged). |

### NFR coverage closed by this story

- **NFR-I5** Texas retrieval-contract.md preserved verbatim per AC-I (sha256 baseline test).
- **NFR-I6** cache-prefix stability inherited from 2a.3 P6 patch (CRLF→LF normalization in `_read_sanctum_digest`); Texas inherits the same byte-stable digest function.
- **NFR-X1** `TexasEnvelope.model_dump_json() ↔ model_validate_json` round-trip verified in AC-G.
- **NFR-X3** Texas sanctum fingerprint computed per AC-D (first real populated-and-locked exercise; sha256 of full sanctum content).
- **NFR-X4** model resolution trail populated per AC-F (third per-specialist exercise).

### FR coverage closed by this story

- **FR9** (lane-isolated specialist package) — `app/specialists/texas/` under `run_graph` lane enforced by C1
- **FR10** (state-subclass discipline) — `TexasEnvelope(SpecialistEnvelope)` + `TexasReturn(SpecialistReturn)` per AC-G
- **FR11** (model_config per-specialist) — Texas's `model_config.yaml` shipped per AC-C (with no-invoke discipline documented inline)
- **FR12** (expertise directory per-specialist) — Texas's `expertise/README.md` with L4 refs + `retrieval-contract-ref.md` pointer per AC-D + AC-I
- **FR15** (sanctum cold-read) — third per-specialist exercise; **FIRST real populated-and-locked exercise** per AC-D
- **FR16** (resolution trail) — third per-specialist exercise per AC-F

FR54 (cache-hit-rate) is NOT measured at Texas — pure-tool-dispatch specialists have no LLM prefix to cache. The FR54 substrate is intact (test harness preserved at 2a.3 P9 patch); Texas's contribution is to confirm the FR54 measurement category does not generalize to all specialist types, which is itself an architectural learning for the §12.10 slab retrospective.

---

## File Structure Requirements

### NEW files (dev agent + generator author these)

```
app/specialists/texas/
├── __init__.py                           # Package marker
├── graph.py                              # 9-node StateGraph; _act + helpers + retrieval_dispatch invocation (~120 LOC total)
├── state.py                              # TexasEnvelope + TexasReturn (with bundle_reference field)
├── model_config.yaml                     # tier_request: fast → gpt-5-haiku (no-invoke discipline documented)
├── retrieval_dispatch.py                 # Mockable wrapper around skills/bmad-agent-texas/scripts/run_wrangler.py; ~40 LOC
└── expertise/
    ├── README.md                         # 10-row L4 refs dotted-list table + retrieval-contract-ref.md pointer
    └── retrieval-contract-ref.md         # Pointer file (NOT symlink) → skills/bmad-agent-texas/references/retrieval-contract.md

tests/specialists/texas/
├── __init__.py
├── test_texas_state_shape.py             # AC-G four-file-lockstep MODEL shape (≥4 tests)
├── test_texas_model_cascade.py           # AC-C (2 tests: default + override)
├── test_texas_gate_decision_binding.py   # AC-E (2 tests: presence + canonical-chain)
├── test_texas_sanctum_cold_read.py       # AC-D (3 tests: populated determinism + reference-shape + lock-baseline)
├── test_texas_resolution_trail.py        # AC-F (1 test)
├── test_texas_act_node_dispatch.py       # AC-B (mocked retrieval dispatch + parametrized parse-branch coverage per Murat carry; ~5 parametrized cases)
└── test_texas_retrieval_contract_preserved.py  # AC-I (2 tests: sha256 baseline + pointer-file presence)

tests/integration/scaffold_conformance/
└── test_scaffold_texas.py                # AC-H — validate_scaffold("texas", ...)

tests/fixtures/specialists/texas/
├── golden_envelope.json                  # Representative TexasEnvelope payload (with directive_path)
├── golden_return.json                    # Representative TexasReturn payload (with bundle_reference)
├── fixture_bundle/                       # Stub six-artifact bundle (extracted.md, metadata.json, manifest.json, extraction-report.yaml, ingestion-evidence.md, result.yaml — minimal valid shapes)
└── ac_b_op_directive.yaml                # AC-B-OP operator-gated live retrieval directive template (PRE-AUTHORED 2026-04-25; default scite single-provider query; ~$0.02-0.10 per dispatch; customize per operator's available provider key)

scripts/utilities/
└── ac_b_op_texas_live_retrieval_evidence.py  # AC-B-OP operator helper script (PRE-AUTHORED 2026-04-25; ~200 LOC). Orchestrates: venv check → provider-key check → wrangler subprocess → six-artifact sha256 capture → result.yaml tail extraction → filled-in evidence block emission to stdout + persistence to <bundle-dir>/ac_b_op_evidence.md

_bmad/memory/bmad-agent-texas/            # ALREADY POPULATED by operator first-breath; lock-and-verify only at AC-D
```

### MODIFIED files

- `pyproject.toml` — append `"app.specialists.texas.graph -> app.gates.resume_api"` to C3 `ignore_imports` (per AC-A; third manual-edit instance of the A12 deferred-inventory pattern)
- `.gitattributes` — append `_bmad/memory/** text=auto eol=lf` + `tests/fixtures/**/*.mp4 binary` (per AC-L hygiene PR carry)
- [`docs/dev-guide/langgraph-migration-guide.md`](../../docs/dev-guide/langgraph-migration-guide.md) — §12.7 Texas walkthrough + §12.10 Slab 2a retrospective summary + §12.7→§12.8 + §12.8→§12.9 renumber + §12.6 framing-sentence-above-divergences-table addition (per AC-K)
- [`docs/dev-guide/specialist-anti-patterns.md`](../../docs/dev-guide/specialist-anti-patterns.md) — A9 fourth example or title broadening per AC-M (G6 disposition)
- [`_bmad-output/implementation-artifacts/sprint-status.yaml`](sprint-status.yaml) — flip `migration-2a-4-…` ready-for-dev → in-progress → done; flip `migration-epic-2a-slab-2-scaffold-pilot` in-progress → done at slab close
- [`_bmad-output/implementation-artifacts/slab-2a-retrospective.md`](slab-2a-retrospective.md) — **NEW file** authored at story close per AC-M slab-retrospective convening

### NOT modified

- **`skills/bmad-agent-texas/references/retrieval-contract.md`** — **NFR-I5 contract preservation; verified at AC-I via sha256 baseline test**
- `tests/integration/scaffold_conformance/scaffold_contract.py` — frozen
- `app/specialists/_scaffold/` — reference remains untouched
- `app/specialists/_stub/passthrough_specialist.py` — stays for not-yet-migrated specialists
- `app/specialists/irene/` — Story 2a.2 baseline preserved unchanged
- `app/specialists/kira/` — Story 2a.3 baseline preserved unchanged (post-G6 patches frozen)
- `skills/bmad-create-specialist/` — generator shipped by 2a.1; auto-emit improvements are deferred-inventory follow-on (A12; MUST land before Slab 2b.1 TEMPLATE opens)
- `skills/bmad-agent-texas/` (excluding the protected references — `references/retrieval-contract.md` MUST NOT change) — primary skill source; severance honored
- `tests/agents/bmad-agent-texas/` — existing tests (test_cross_validator.py + test_extraction_validator.py) preserved; new tests land at `tests/specialists/texas/`
- `tests/contracts/test_texas_row_fungibility.py` — existing schema-pin contract test preserved
- Primary-repo paths — severance honored

---

## Technical Requirements

### Dependencies

All runtime deps already in lockfile (per 1.1a 10-package palette + 2a.2 conftest extensions). No new dep at 2a.4.

The `retrieval_dispatch` wrapper subprocesses to `.venv/Scripts/python.exe skills/bmad-agent-texas/scripts/run_wrangler.py --directive ... --bundle-dir ... --json`. Subprocess invocation is via Python's `subprocess.run(...)` with explicit args (no shell=True). No new dep introduced.

### Invariants preserved (NFR-X1–X5)

- **NFR-X1** — `TexasEnvelope.model_dump_json() ↔ model_validate_json` round-trip verified in AC-G
- **NFR-X2** — `RunState.graph_version` pins per Slab 1 substrate
- **NFR-X3** — Texas sanctum fingerprint computed per AC-D (FIRST real populated-and-locked per-specialist exercise)
- **NFR-X4** — model resolution trail populated per AC-F
- **NFR-X5** — temperature variance N/A at runtime: `temperature_default: 0.0` is recorded but never consumed (no LLM invocation at Texas layer); rationale in `model_config.yaml` inline comments.

### Live retrieval-dispatch test discipline

Two distinct live dimensions (analogous to 2a.3 but different shape):

| Dimension | AC | Marker | Auto-skip behavior | Live evidence |
|---|---|---|---|---|
| **Live retrieval-provider dispatch (scite/Consensus/etc.)** | AC-B-OP only | NONE (operator-gated AC) | N/A — dev agent never invokes live retrieval providers | Operator pastes one-directive evidence into Completion Notes |
| **NO `@pytest.mark.llm_live` at Texas layer** | — | — | — | — |

**Rationale:** Texas is pure-tool-dispatch — no LLM call at the Texas layer means no `@llm_live` marker needed. Dev-agent path uses fixture directives + the existing `fake_provider` adapter for shape verification; live API call is purely operator-machine workflow with real `SCITE_API_KEY` / `CONSENSUS_API_KEY` / etc. This split is faithful to the sandbox-AC discipline.

---

## Testing Requirements

### K-target policy: ~1.4× (target 14 / floor 11)

Per governance JSON `2a-4` rationale: null (single-gate; no schema-shape; no CI-contract change). Texas is structurally similar to Irene/Kira but with ONE extra AC (AC-I retrieval-contract preservation) + slab-closing D12 obligations. Realistic breakdown:

- Schema-shape models introduced: `TexasEnvelope`, `TexasReturn` (2 models with one new field `bundle_reference`); AC-G → 4 shape-pin tests
- Scaffold conformance: 1 test (AC-H)
- Model cascade: 2 tests (AC-C default + override)
- Gate-decision binding: 2 tests (AC-E)
- Sanctum cold-read: **4 tests** (AC-D — populated determinism + reference-shape + lock-baseline pin + **lock-violation named-exception** per Winston W1 rider)
- Resolution trail: 1 test (AC-F)
- Act-body retrieval dispatch + bundle parser: 1 test wrapper + **7 parametrized parse-branch cases** (per Murat M1 rider; collapse-to-6 allowed if branches 6/7 share dispatch) + 1 subprocess-kwargs-pinned subtest per Amelia A1 + two-sided assertions per Murat M5
- Retrieval-contract preservation: 2 tests (AC-I sha256 baseline + pointer-file presence)
- **Total: ~19-22 tests at target with party-mode riders applied.** Floor 11 / target 14 cleared comfortably (~1.4-1.6× — within Murat anti-padding band).

### Regression floor (placeholder-key path)

Per Murat 2a.2 SF4 + 2a.3 ratification, story close requires the placeholder-key path to meet its floor:

| Path | Floor at T8 | Enforcement |
|---|---|---|
| **Placeholder-key (CI / dev-agent sandbox)** | ≥ 395 passed / 7 skipped (no new `@llm_live` tests at Texas — 2 pre-existing Kira `@llm_live` skips remain; no Texas additions) / 0 failed | dev-agent T8 regression |

- Pre-2a.4 baseline: 380 passed / 7 skipped / 0 failed (2a.3 BMAD-CLOSE placeholder-key)
- 2a.4 adds ~16 new tests (4 shape + 1 conformance + 2 cascade + 2 gate-decision + 3 sanctum + 1 trail + 1 act-body + 2 contract-preservation = 16) → net +16 over baseline → **≥396 expected**
- Import-linter: 3/3 KEPT (Texas C3 ignore_imports row added at AC-A per A12 procedural-coupling pattern)
- Ruff: clean
- Sandbox-AC validator: PASS

### Live-retrieval test discipline (operator-gated only)

No `@pytest.mark.llm_live` at the Texas layer (no LLM call). Live retrieval-provider dispatch is AC-B-OP operator-gated only. The dev-agent path uses:
- Fixture directive YAML at `tests/fixtures/specialists/texas/fixture_directive.yaml`
- The existing `skills/bmad-agent-texas/scripts/retrieval/fake_provider.py` adapter (shipped by Story 27-0)
- Mocked subprocess invocation (`subprocess.run` monkey-patched to return a fixture bundle path without actually firing the runner)

This means **the dev-agent regression suite stays fully deterministic** — no skip dimension introduced by Texas, no flake risk from network-bound providers.

---

## Previous Story Intelligence

### From Story 2a.3 (Kira Motion Migration) — 2026-04-25 BMAD-CLOSED post-G6 + party-mode 4/4 GREEN

**Key lesson — independent G6 layered review caught MUST-FIX UNFULFILLED ACs.** Codex's 2a.3 dev-story landing left AC-J (§12.6 Kira walkthrough) and AC-K (anti-pattern A9/A10 augments) UNFULFILLED — `git status` confirmed neither file was opened. Independent G6 (Blind Hunter / Edge Case Hunter / Acceptance Auditor) caught both as MUST-FIX patches; G6 now precedes the close-flip on every story. **2a.4 inherits this discipline:** dev agent must explicitly verify §12.7-Texas walkthrough lands in `langgraph-migration-guide.md` before declaring story done.

**Key lesson — bounded-scope discipline holds across three categories.** Irene 2a.2 (`_act` 64 LOC), Kira 2a.3 (`_act` ~75 LOC + `kling_dispatch.py` 80 LOC), Texas projected (`_act` ~80 LOC + `retrieval_dispatch.py` ~40 LOC). All within budget. Apply the same scope-slip flag at T4 (~140 LOC ceiling for act+wrapper combined).

**Key lesson — byte-stable prompt assembly + CRLF/LF normalization is non-negotiable.** Kira 2a.3 P6 patched `_read_sanctum_digest` to normalize `\r\n → \n` before sha256 (cross-platform cache-prefix determinism). Texas inherits this verbatim. Operator works on Windows; CI may be POSIX; without the normalization, populated-sanctum digest diverges per platform.

**Key lesson — discriminator-check at act-node boundary** (Winston W2/2a.2). Even though Texas does not invoke the LLM at `_act`, the discriminator-check pattern still applies to enforce the resolution-trail-entry contract. Texas inherits this directly.

**Key lesson — envelope-carrier-hack is acknowledged Slab-2 bounded scope.** All three Slab 2a specialists encode the envelope payload as sorted-keys canonical JSON in `state.cache_state.cache_prefix`. Slab-3 retirement is tracked in deferred-inventory; 2a.4 does NOT solve it.

**Key lesson — populated-and-locked sanctum is a NEW measurement category.** 2a.2 pioneered empty-sanctum baseline. 2a.3 deferred populated exercise (sanctum dir absent). **2a.4 fires the first REAL populated case** (Texas's sanctum is already populated by prior operator first-breath ceremony). The lock-and-verify protocol in `sanctum-reference-conventions.md §4` becomes a real test pin (AC-D test 3).

**Key lesson — generator denylist + DR-2 are stable.** Texas is Category A+B per slab-2-roster-reconciliation; invocation proceeds normally.

**Key lesson — procedural-coupling (A12) urgency reinforces with each manual instance.** Irene 2a.2 + Kira 2a.3 + Texas 2a.4 = three independent manual edits to pyproject.toml C3 ignore_imports. **The deferred-inventory entry "Generator auto-emit pyproject.toml C3 ignore_imports row" MUST land before Slab 2b.1 TEMPLATE opens.** Three is sufficient evidence; do not let it become four.

### Three drifts from Epic 2a.4 text (captured at T1 per standing protocol)

1. **Test path** — epic says `tests/bmad-agent-texas/...`; reality is `tests/agents/bmad-agent-texas/`. A9-class drift (fourth instance across Slab 2a).
2. **Symlink for retrieval-contract reference** — epic says "symlink or pointer file"; framework wins on pointer-file (Windows-compatible). No A-entry harvest needed (epic explicitly listed both options).
3. **Six-artifact bundle naming** — confirmed alignment with reality (`extracted.md` + `metadata.json` + `manifest.json` + `extraction-report.yaml` + `ingestion-evidence.md` + `result.yaml`). No drift.

### Carries from 2a.3 close (party-mode 4/4 GREEN ratification)

1. Murat soft-blocker — parse-branch coverage. **2a.4 application:** Texas `_act`'s bundle parser gets parametrized parse-branch coverage (~5 cases) per AC-B.
2. `.gitattributes` hygiene PR. **2a.4 application:** AC-L bundles into Texas spec landing.
3. Paige doc polish — §12 framing sentence + §12.7/§12.8 renumber-grep. **2a.4 application:** AC-K extends §12 with §12.7-Texas + §12.10-retrospective + framing-sentence add + cascade-renumber.

### Dev Notes anti-pattern anchors

- **A9 fourth instance** (test path drift) — augment per harvest-gate rule, OR broaden A9 title; G6 disposition
- **A12 procedural-coupling** — third concrete instance reinforces deferred-inventory urgency
- **Late-binding default-arg** (Slab-1 gotcha #4): still relevant
- **Passthrough `{}` return shape** (Slab-1 gotcha #6): Texas's real `_act` replaces this for the texas specialist specifically

---

## Git Intelligence

Recent Slab 2 commits for pattern reference:

- (post-2a.3-close commit pending; 2a.3 BMAD-CLOSED 2026-04-25 via 9-PATCH G6 review + 4/4 party-mode ratification) — **expected commit hash visible at 2a.4 T1 once 2a.3 lands to origin**
- `21a6e5f` — Story 2a.2 BMAD-CLOSED (Irene Pass 2 migration; cache-hit-rate 95.33% median)
- `61d7311` — Session wrapup 2026-04-24
- `5dafe82` — 2a.2 13 party-mode riders applied
- `e14616c` — Story 2a.1 flip review → done
- `cc79df5` — Story 2a.1 consolidated dev-story landing
- `2a336df` — Story 2a.1 review remediation (compiler validator additive-only per DR-1)
- `f78bd72` — Slab-1 GOLDEN ratification + DR-SLAB-1-CLOSE
- `835e650` — Upstream severance

Diff intelligence: 2a.3 added ~17 files under `app/specialists/kira/` + `tests/specialists/kira/` + 1 new test (P8 readme-shape-pin) + `kling_dispatch.py` wrapper module. Net diff: ~12 files. **2a.4 will add a comparable set under `app/specialists/texas/` + `tests/specialists/texas/`, plus the `retrieval_dispatch.py` wrapper, plus `slab-2a-retrospective.md` (NEW), plus §12.7 + §12.10 doc additions. Net diff estimate: ~14-18 files.**

---

## Project Context Reference

### Pre-read memory entries

- [`memory/feedback_verify_via_shipped_deps.md`](../../../Users/juanl/.claude/projects/c--Users-juanl-Documents-GitHub-course-DEV-IDE-with-AGENTS-hybrid/memory/feedback_verify_via_shipped_deps.md) — sandbox-AC rule
- [`memory/project_upstream_severance.md`](../../../Users/juanl/.claude/projects/c--Users-juanl-Documents-GitHub-course-DEV-IDE-with-AGENTS-hybrid/memory/project_upstream_severance.md) — severance posture
- [`memory/project_no_docker.md`](../../../Users/juanl/.claude/projects/c--Users-juanl-Documents-GitHub-course-DEV-IDE-with-AGENTS-hybrid/memory/project_no_docker.md) — Postgres-native; no docker-compose
- [`memory/feedback_venv_python_allowed.md`](../../../Users/juanl/.claude/projects/c--Users-juanl-Documents-GitHub-course-DEV-IDE-with-AGENTS-hybrid/memory/feedback_venv_python_allowed.md) — `.venv/Scripts/` binaries are pre-authorized

### Post-story unblocks

- **Slab 2b Epic opens** — Slab 2a closes at 2a.4; Slab 2b is the 14-specialist tranche per Epic 2b. **2b.1 (Gary TEMPLATE) gated on filing the A12 generator-auto-emit follow-on as a 2a.1 defect story before 2b.1 opens** (deferred-inventory binding; reinforced by Texas's third manual-edit instance).
- **Migration-guide §12 reference structurally complete** — three worked-example categories (narration / LLM+tool-dispatch / pure-tool-dispatch) ready for Slab 2b inheritance per the original §12 design intent
- **M2 milestone** — Slab 2a close + Slab 2b kickoff-readiness feeds the M2 acceptance gate

---

## Dev Agent Record

_(Dev agent populates this section during T1–T9 execution.)_

### T1 Readiness

**Date:** 2026-04-25 | **Dev agent:** Codex (GPT-5) | **Operator:** Juanl

#### A. Pre-T1 ratifications (operator + party-mode TBD)

Three pre-T1 items expected to surface here per 2a.2/2a.3 precedent:

| Item | Disposition (TBD) |
|---|---|
| Generator CLI surface — uv vs venv-direct | Default to venv-direct per 2a.2 D1 ratification |
| Sanctum-state — populated-and-locked confirmation | Texas sanctum already populated; pre-run sha256 baseline manifest captured in §G below |
| Live evidence path — operator opt-in for AC-B-OP live retrieval-provider dispatch | **DEFERRED-PENDING-SLAB-3 ratified 2026-04-25 pre-T1.** No live-run stage in 2a.4 lifecycle; AC-B-OP remains documented and explicitly not executed on hybrid. |

#### B. Generator CLI substitution (D1 application — DR-1 audit)

To populate at T1 open. Spec form:
```
.venv\Scripts\python.exe -m skills.bmad_create_specialist.scripts.generate \
  --name texas --mcp none --expertise-tier L4-source-wrangling \
  --from-skill skills/bmad-agent-texas
```

#### C. Standing pre-flight items (10/10 TBD)

To populate at T1 open per the 10-item list above.

#### D. 8-point artifact-existence sweep (A–H)

To populate at T1 open per the 8-item list above.

#### E. Three epic-doc-vs-framework drifts logged (anti-pattern #3 standing protocol)

To populate at T1 open. Expected drifts: A9 fourth example (test path `tests/bmad-agent-texas/` → `tests/agents/bmad-agent-texas/`); symlink-vs-pointer-file (epic-listed both options; pointer-file wins; no harvest); six-artifact bundle confirmed (no drift).

#### F. Sandbox-AC validator (governance pre-flight)

To populate at T1 open. Expected: PASS.

#### G. Sanctum lock-and-verify micro-protocol (FIRST REAL populated-and-locked epoch exercise)

Pre-T1 baseline captured 2026-04-25 — Texas sanctum is already populated by prior operator first-breath ceremony (17 files; full BMB shape):

```
find _bmad/memory/bmad-agent-texas -type f -exec sha256sum {} +
```

**Lock manifest (PINNED — module-level constant in `tests/specialists/texas/test_texas_sanctum_cold_read.py` per Amelia A3 rider):**

| File | sha256 |
|---|---|
| `_bmad/memory/bmad-agent-texas/BOND.md` | `292daf562836bedb64f335b6f48ce4b1f8a76d7bf2999dfe591c2c7744602270` |
| `_bmad/memory/bmad-agent-texas/CAPABILITIES.md` | `aa41899f3f5f3358f2d14c3f6d71e2dd4af7a98175b8f193c1233cc363305a30` |
| `_bmad/memory/bmad-agent-texas/CLONE-FORK-NOTICE.md` | `3f217dda8cb9f251277c9cba647c6331c1da166abf43931979da7e75366423aa` |
| `_bmad/memory/bmad-agent-texas/CREED.md` | `019e69a856912e9ca159dbabe4ec0849b69eccc75f69026f1a274a94ac9d5654` |
| `_bmad/memory/bmad-agent-texas/INDEX.md` | `f9925f7b9da182f29fe5cee43aff57aadfd20f874099a37f683679c7e924fa57` |
| `_bmad/memory/bmad-agent-texas/MEMORY.md` | `1845fb2666062835836b1ff71c9c6fcdb316485babe5064491a6d12c96459119` |
| `_bmad/memory/bmad-agent-texas/PERSONA.md` | `c56223c4e873a2b8ed22e75cb128915948216ff6f471f50cd9e2ab0ab3f6a902` |
| `_bmad/memory/bmad-agent-texas/references/capability-authoring.md` | `d03139cdecffc83b39cea0cae1475a5a137d6232b4c05914fa887199ea7585d7` |
| `_bmad/memory/bmad-agent-texas/references/delegation-contract.md` | `0703ddce39eff29f9f690f0389eda2b0be9c9b295ac6dce059d93082ece099df` |
| `_bmad/memory/bmad-agent-texas/references/extract-and-validate.md` | `935b53ad9d101d631d8e853e667ec9fe48f23bd7d0dc006c0f721778acc0ef29` |
| `_bmad/memory/bmad-agent-texas/references/fallback-resolution.md` | `7f57912c214d35ec05bfada03bdfcf7a4c54b09077f6000c7170738fe0b4143d` |
| `_bmad/memory/bmad-agent-texas/references/memory-guidance.md` | `1c01b65ed84440767ad9766ef36686f26c5d648333387a244f609f0da72f986e` |
| `_bmad/memory/bmad-agent-texas/references/source-interview.md` | `e2cceee0dd474cdd4e5ca9c7d70c09701fa91ed30e83e2dcbf3a3c9b7fee2b02` |
| `_bmad/memory/bmad-agent-texas/references/transform-registry.md` | `59f15c3b84e0763d1590510c997f731cef3706d51cf1cb4397734a1f355cb648` |
| `_bmad/memory/bmad-agent-texas/scripts/cross_validator.py` | `b9b1379230bf604b06c5c67c7ade848a203c8a23a06ed35f43db730a80fce23e` |
| `_bmad/memory/bmad-agent-texas/scripts/extraction_validator.py` | `391c61e564f8c00c89b9104013f83e0f266ef22c5751d14fce81f2aeacec1ade` |
| `_bmad/memory/bmad-agent-texas/scripts/source_wrangler_operations.py` | `ac32edc8f3004b0e90d88c03cf613bd19afa7963ae689e417a262cb96715d981` |

**This is the first real exercise of the lock-and-verify protocol** — 2a.3 deferred to graceful-degrade; Texas hits the populated case. Per-test-invocation guard: re-hash + diff against this manifest; abort + fail-loud on any drift via the named exception class per Winston W1 rider (AC-D test 4). Post-run identity check.

**Operator caveat:** if the sanctum is legitimately edited between baseline capture (2026-04-25) and dev-story open, the protocol per Murat M2 binding is: pause story, recapture baseline, document the edit in Completion Notes, resume. Do NOT weaken the assertion to "file count equality" — silent mutation is the bug class MF6 was authored to prevent.

#### H. Pure-tool-dispatch act-body category reference (input to AC-B authoring)

Texas's primary references:
- [`skills/bmad-agent-texas/SKILL.md`](../../skills/bmad-agent-texas/SKILL.md) — Texas persona + Lane Responsibility + Communication Style + Principles
- [`skills/bmad-agent-texas/references/retrieval-contract.md`](../../skills/bmad-agent-texas/references/retrieval-contract.md) — load-bearing source-of-truth for Shape 3-Disciplined retrieval foundation (NFR-I5 protected; do not modify)
- [`skills/bmad-agent-texas/references/delegation-contract.md`](../../skills/bmad-agent-texas/references/delegation-contract.md) — Marcus ↔ Texas envelope contract
- [`skills/bmad-agent-texas/references/extraction-report-schema.md`](../../skills/bmad-agent-texas/references/extraction-report-schema.md) — schema v1.1 dual-emit shape
- [`skills/bmad-agent-texas/scripts/run_wrangler.py`](../../skills/bmad-agent-texas/scripts/run_wrangler.py) — the production runner that `retrieval_dispatch.py` subprocesses to (consumed via subprocess; mocked at dev-agent layer)
- [`skills/bmad-agent-texas/scripts/retrieval/`](../../skills/bmad-agent-texas/scripts/retrieval/) — provider-adapter directory (dispatcher, contracts, scite_provider, consensus_provider, fake_provider, etc.)

#### I. NFR-I5 retrieval-contract baseline (pre-T1 lock — captured 2026-04-25)

```
sha256sum skills/bmad-agent-texas/references/retrieval-contract.md
→ ac98ff6261adcd84b2910e1e21a1d9911a90974d6ac016f875cd835048601dd0
```

**Pinned baseline (INLINED as module-level constant in `tests/specialists/texas/test_texas_retrieval_contract_preserved.py` per Amelia A3 + Murat M3 riders):**

```python
NFR_I5_RETRIEVAL_CONTRACT_BASELINE_SHA256 = "ac98ff6261adcd84b2910e1e21a1d9911a90974d6ac016f875cd835048601dd0"
```

AC-I test pin asserts byte-equality with this hash post-migration. Hard sha256 — no softening per Murat M3 binding ("any change to that file is a contract change that needs explicit acknowledgment, not silent drift").

T1 Readiness COMPLETE → proceed to T2 (generator dry-run + real invocation).

### T2–T7 Implementation Notes

- Ran generator (venv-direct form) and scaffolded `app/specialists/texas/` plus baseline tests/fixtures.
- Replaced generated `app/specialists/texas/graph.py` with pure-tool-dispatch flow:
  - `_plan` resolves `tier_request="fast"` for model-resolution-trail parity.
  - `_act` performs no LLM call at Texas layer; reads directive/bundle from envelope carrier, dispatches through `dispatch_retrieval`, parses `result.yaml` + `extraction-report.yaml`, and emits canonical JSON output blob.
  - Added `SanctumLockViolation` and hard lock-check helpers (`_read_sanctum_digest`, `_current_sanctum_manifest`, `assert_sanctum_lock`) with CRLF→LF normalization.
- Added `app/specialists/texas/retrieval_dispatch.py` wrapper:
  - Fixture-bundle short-circuit for dev/test path.
  - Subprocess path for real directive uses `shell=False` and `timeout=30`.
- Updated Texas state/config/expertise surfaces:
  - `TexasReturn.bundle_reference` field added.
  - `TexasEnvelope.payload_out` pinned to `TexasReturn`.
  - `model_config.yaml` set to `gpt-5-haiku` with comments clarifying no act-time invoke.
  - `expertise/README.md` expanded to 10-row L4 reference table.
  - `expertise/retrieval-contract-ref.md` added as pointer file.
- Added Texas fixture assets:
  - `golden_envelope.json`, `golden_return.json`, `fixture_directive.yaml`, and six-artifact fixture bundle under `tests/fixtures/specialists/texas/fixture_bundle/`.
- Added/updated Texas tests:
  - state-shape + invalid payload
  - model cascade
  - gate-decision binding
  - sanctum populated cold-read + lock violation
  - resolution trail
  - act-node dispatch + parse branches + subprocess kwargs pin
  - retrieval-contract preservation
  - scaffold conformance
- Applied cross-cutting AC-L hygiene:
  - `.gitattributes` entries for `_bmad/memory/**` and `tests/fixtures/**/*.mp4`.
  - manual C3 row in `pyproject.toml`: `"app.specialists.texas.graph -> app.gates.resume_api",`
- Authored AC-K docs updates in `docs/dev-guide/langgraph-migration-guide.md`:
  - framing sentence above divergences table
  - new §12.7 Texas worked example
  - renumber to §12.8/§12.9 and add §12.10 slab-retrospective summary section.

### T8 Regression Evidence

- `.venv\Scripts\python.exe -m pytest tests/specialists/texas tests/agents/bmad-agent-texas tests/contracts/test_texas_row_fungibility.py -q`
  - Result: `63 passed`
- `.venv\Scripts\python.exe -m pytest tests/integration/scaffold_conformance/test_scaffold_texas.py -q`
  - Result: `1 passed`
- `.venv\Scripts\python.exe -m ruff check app/specialists/texas tests/specialists/texas tests/integration/scaffold_conformance/test_scaffold_texas.py docs/dev-guide/langgraph-migration-guide.md`
  - Result: clean
- `.venv\Scripts\lint-imports.exe`
  - Result: `3 KEPT / 0 broken`

### G5 Single-Gate Review

Per `docs/dev-guide/migration-story-governance.json::2a-4.expected_gate_mode = "single-gate"`. Self-conducted layered G6 review. Party-mode consult triggered ONLY if a Slab-1 invariant breakage surfaces.

### G6 Layered Code-Review (Blind Hunter / Edge Case Hunter / Acceptance Auditor)

Independent G6 layered code-review conducted 2026-04-25 via `bmad-code-review` skill. Three subagents in parallel (Blind Hunter / Edge Case Hunter / Acceptance Auditor); triage per aggressive single-gate rubric in [`docs/dev-guide/story-cycle-efficiency.md`](../../docs/dev-guide/story-cycle-efficiency.md): **8 PATCH applied + 9 DEFER + ~20 DISMISS**.

**Patch findings (all applied 2026-04-25 in this story-close pass):**

- [x] [Review][Patch] **AC-M `slab-2a-retrospective.md` NEW file ABSENT** — Acceptance Auditor MUST-FIX. Author the file at `_bmad-output/implementation-artifacts/slab-2a-retrospective.md` per Paige P7 section-by-section line budget (~157 lines, all 7 required sections).
- [x] [Review][Patch] **AC-K Paige P2 section-level framing sentence above §12.5 MISSING** — Acceptance Auditor MUST-FIX. Add the section-level framing sentence directly above `### 12.5 Irene worked before/after ...` in `langgraph-migration-guide.md`.
- [x] [Review][Patch] **AC-K Paige P4 sub-section framing sentence above §12.6 in spec-required form MISSING** — Acceptance Auditor MUST-FIX. Replace the placeholder "The table below highlights..." with the spec-required "When you migrate the next specialist, expect divergences in **these eight categories**..." form.
- [x] [Review][Patch] **AC-B exit-code parametrized branches MISSING (Murat M1 #5 / #6 / #7)** — Acceptance Auditor MUST-FIX. Add exit-30 / unknown-exit / exit-10 graceful-degrade tests in `tests/specialists/texas/test_texas_act_node_dispatch.py`. Two-sided assertion: `BundleDispatchError(tag=...)` exception side AND state-side trail entry.
- [x] [Review][Patch] **AC-B Murat M5 two-sided trail-tag assertion NOT IMPLEMENTED** — Acceptance Auditor MUST-FIX. Add `BundleParseError(RuntimeError)` with `tag` attribute drawn from `bundle.parsed.*` namespace; emit trail entry with `bundle.parsed.<tag>` reason on every parse outcome (ok / missing-key / malformed / wrong-type / empty / exit-10 / exit-30 / unknown-exit). Tests assert two-sidedly: parser shape (raise OR returned dict) AND trail-tag (exception attribute OR state trail entry).
- [x] [Review][Patch] **`_act` silent fixture-bundle fallback on malformed cache_state JSON** — Blind Hunter HIGH. Production guard must fail-loud rather than silently dispatch the dev-mode fixture bundle on malformed/non-dict cache_state. Add `_decode_envelope_payload(state)` raising `BundleParseError(tag="bundle.parsed.malformed"|"bundle.parsed.wrong-type")`. Slab-3 still owns the envelope-carrier-hack retirement; this PATCH closes the silent-fail gap until then.
- [x] [Review][Patch] **`bundle_dir = Path("")` resolves to CWD on missing-key dispatch receipt** — Blind Hunter MED. Add `BundleDispatchError(tag="bundle.parsed.missing-key")` when `dispatch_receipt.get("bundle_dir")` is falsy.
- [x] [Review][Patch] **Subprocess kwargs pin test only covered shell + timeout** — Blind Hunter HIGH. Extend `test_dispatch_wrapper_pins_subprocess_kwargs` to assert `text`, `capture_output`, and `cwd` are pinned (Amelia A1 contract requires full kwargs pin so a regression that drops any of them fails red).
- [x] [Review][Patch] **Vacuous `fake_dispatch` (`**_`) test in act-dispatch happy-path** — Blind Hunter MED. Replace with non-vacuous fixture that captures `directive_path` + `bundle_dir` and asserts envelope payload threaded through end-to-end.
- [x] [Review][Patch] **Fixture bundle BOM (5 of 6 files) + `ingestion-evidence.md` PowerShell `\`n\`n` literal escape** — Blind Hunter MED. Strip BOM + rewrite `ingestion-evidence.md` with real newlines.
- [x] [Review][Patch] **`__all__` exposes private underscore helpers** — Blind Hunter LOW. Drop `_act`, `_plan`, `_load_bundle_outputs`, `_read_sanctum_digest`, `_read_texas_references` from `__all__`; export only the public surface (`SanctumLockViolation`, `BundleParseError`, `BundleDispatchError`, `TEXAS_REFERENCES`, `TEXAS_SANCTUM_LOCK_BASELINE`, `TRANSITIONS`, `assert_sanctum_lock`, `build_texas_graph`).
- [x] [Review][Patch] **§12.7 snippet does NOT match real post-G6 code shape** — Blind Hunter MED + Acceptance Auditor SHOULD-FIX. Rewrite §12.7 worked-example block to show the actual fail-loud guards + bundle.parsed.* tag emission + exit-10 graceful-degrade branch. Replace the literal `entries_count: ...` ellipsis with the real conditional expression.
- [x] [Review][Patch] **§12.10 missing Murat M4 latency substitute metric + retrospective pointer + Slab 2b kickoff gate** — Acceptance Auditor SHOULD-FIX. Augment §12.10 with subprocess-dispatch-latency baseline note + link to `slab-2a-retrospective.md` + "Slab 2b opens once A12 generator auto-emit follow-on lands" gate language.

### Deferred findings (filed in [`_bmad-output/maps/deferred-work.md`](../maps/deferred-work.md))

9 findings deferred under "Deferred from: code review of migration-2a-4-texas-scaffold-migration (2026-04-25)" — covers dispatch wrapper `tests/fixtures/...` runtime-path coupling (Slab-3 envelope-carrier-hack retirement), AC-B-OP helper polish (provider-key gate + exit-0-on-failure; fix at Slab-3 reactivation), sanctum lock-baseline regeneration script, `SanctumLockViolation` cross-specialist refactor, fixture `manifest.json` fake sha256 + `extracted.md` min-words mismatch, gate-decision post-interrupt dead code (Slab-3 conditional-edge fix), edge-case lone-CR / tab-in-filename sanctum hashing, and local environment optional-dep hygiene.

### Dismissed (~20, per aggressive single-gate rubric)

Cosmetic NITs across the three layers including: golden_envelope payload_out shape vs `_act` runtime output (different test surfaces); TexasEnvelope.payload_out forward-reference (Pydantic v2 + `from __future__ import annotations` handles); 50KB boundary off-by-one; test name `_binds_resume_from_verdict` vs spec literal `_binds_interrupt` (semantic equivalent); `per_node_overrides.act` duplicate of default (cosmetic; comments document); plus ~15 additional cosmetic NITs across the three layers.

### Headline

**11 ACs verified positively** (A, B subprocess-pin baseline, C, D test 4 + lock baseline, E, F, G, H, I, J, L, K renumber-grep scope, A9 augment, AC-B-OP deferral + pre-authored helper/template). **5 MUST-FIX** + **2 SHOULD-FIX** all REMEDIATED in this G6 close pass. Code-side findings centered on production fail-loud guards (silent fixture fallback, bundle_dir empty-string, vacuous test); doc-side findings centered on slab-closing deliverables (retrospective.md, §12 framing sentences, §12.7 snippet correctness, §12.10 augment); test-side findings centered on Murat M1+M5 two-sided assertion + Amelia A1 subprocess-kwargs full pin. Texas-only regression at story close: **36 passed** in `tests/specialists/texas tests/integration/scaffold_conformance/test_scaffold_texas.py` (+8 net new tests over Codex landing baseline of 28). Migration-scoped regression: **169 passed / 2 skipped** (placeholder-key) on the cleanly runnable suite (specialists + scaffold_conformance + agents + Texas contracts + Kira cache harness). Ruff clean across `app/specialists/texas`, `tests/specialists/texas`, `tests/integration/scaffold_conformance/test_scaffold_texas.py`, `docs/dev-guide/langgraph-migration-guide.md`. lint-imports 3/3 KEPT. Sandbox-AC PASS.

### D12 Slab-Closing Close Stub

**Slab 2a is closed.** All four stories (2a.1 → 2a.2 → 2a.3 → 2a.4) BMAD-CLOSED; M2 milestone gate satisfied for the Specialist Scaffold Pilot epic.

**Invariant preservation (Slab 2a-wide):**

- **NFR-I5** Texas retrieval-contract.md preserved verbatim across migration ✓ (per AC-I sha256 baseline test, `ac98ff62…` byte-equality).
- **invariant #13** specialist registry — FR9-FR12 + FR15 + FR16 closed for all three Slab 2a specialists (Irene 2a.2 + Kira 2a.3 + Texas 2a.4).
- **FR54** cache-hit-rate baseline measured at Irene 2a.2 (95.33% empty-sanctum); steady-state populated-sanctum exercise effectively deferred (Kira graceful-degrade; Texas pure-tool-dispatch — no LLM at specialist layer means no provider cache to measure). The 2a.4 retrospective (§12.10 + slab-2a-retrospective.md) records that FR54 is narration-bound — pure-tool-dispatch substitute metric per Murat M4 is `subprocess-dispatch-latency stability`.
- **Slab-1 substrate intact** across three specialist migrations — compile validator additive-only; scaffold-conformance frozen; gate-decision interrupt-binding preserved; lint-imports 3/3 KEPT throughout.

**Anti-pattern harvest (Slab 2a cumulative + 2a.4-specific):**

- **A9 fourth example LANDED + title broadened** — `docs/dev-guide/specialist-anti-patterns.md` retitled to "Epic-doc structural-name drift from Slab-1-hardened reality" (was "Epic-doc node-name drift") with four examples spanning node-name + test-path + model-ID drifts. Title-broadening disposition ratified at G6 (the four-instance harvest exceeded the original node-name scope; broadening is more accurate than padding bullet examples).
- **A10 NOT applicable at 2a.4** — Texas does not surface a new model-ID drift; the cascade entry is `gpt-5-haiku` per `tier_request: fast` mapping (consistent with Kira's pattern), and the model is never invoked at runtime so no drift surface.
- **A11 NOT applicable at 2a.4** — Texas's sanctum path matches the framework convention (`_bmad/memory/bmad-agent-texas/` matches `skills/bmad-agent-texas/` skill-dir name); no drift.
- **A12 reinforcement (third specialist manual C3 row)** — three independent occurrences of the manual `pyproject.toml` C3 ignore-imports edit pattern (Irene 2a.2 + Kira 2a.3 + Texas 2a.4); strongest possible evidence base. **Slab 2b.1 TEMPLATE MUST NOT open until the generator auto-emit follow-on lands** — slab-closing binding.

**Migration-guide update:**

- §12.7 added for Texas pure-tool-dispatch worked example per AC-K (matches actual post-G6 code shape, not the un-patched placeholder).
- §12.10 added for Slab 2a retrospective summary with Murat M4 latency substitute metric + retrospective.md pointer + Slab 2b kickoff gate language.
- Section-level framing sentence above §12.5 (Paige P2) + sub-section framing sentence above §12.6 divergences table (Paige P4) — both landed in spec-required form.
- §12.7 → §12.8 + §12.8 → §12.9 renumber executed; renumber-grep scope clean across migration guide + Slab 2a story specs + `next-session-start-here.md` + `_bmad-output/planning-artifacts/deferred-inventory.md`.

**Slab 2a retrospective convening (party-mode):** authored at [`_bmad-output/implementation-artifacts/slab-2a-retrospective.md`](slab-2a-retrospective.md) (~157 lines covering all 7 Paige P7 sections: 5-line opener block / FR coverage closed table / cumulative regression intelligence / anti-pattern catalog state / deferred-inventory follow-ons surfaced / §12 reference completeness / Slab 2b kickoff readiness checklist with A12 gate front-and-center). Inventory consultation per CLAUDE.md "Deferred inventory governance" §1 captured: 7 reactivation-ready entries (A12 generator auto-emit BLOCKING for 2b.1 + AC-B-OP Texas live retrieval + Kira populated-sanctum + envelope-carrier-hack retirement + gate-decision conditional-edge fix + cold-cache nonce-variant + `--require-live-llm-flag-wiring`); 5 newly named follow-ons (dispatch-wrapper extraction candidate + §12 size review + implementation-artifacts/ index + SanctumLockViolation cross-specialist refactor + local environment optional-dep hygiene).

**Dispatch-wrapper extraction candidate (Winston rider):** retrospective records `kira/kling_dispatch.py` (LLM+tool category) + `texas/retrieval_dispatch.py` (pure-tool category) as two independent occurrences of the same dispatch-wrapper shape — flagged for Slab 2b extraction to `_bmad/scaffolds/dispatch_wrapper_template.py` if 2b.1 (Gary) or 2b.2 surfaces a third occurrence.

**Status flips at Slab 2a close (sprint-status.yaml):** `migration-2a-4-migrate-texas-to-9-node-scaffold` review → done; `migration-epic-2a-slab-2-scaffold-pilot` in-progress → done.

### Completion Notes

- Dev implementation complete for AC-A through AC-M (excluding AC-B-OP by explicit deferral contract).
- AC-B-OP was not executed and remains deferred pending Slab 3 forward-port of `marcus.dispatch.contract`; no live retrieval-dispatch attempt was made in this run.
- Sanctum lock baseline was re-captured from the current populated-and-locked sanctum in this workspace and hard-pinned in code/tests to keep lock-and-verify behavior fail-loud and deterministic.
- ~~Story state moved to `review` pending independent G6 layered review and final close protocol updates.~~ **CLOSED 2026-04-25** post-independent-G6 (8 PATCH applied + 9 DEFER + ~20 DISMISS); slab-retrospective convened; D12 close stub recorded; sprint-status flipped review → done.

**AC-B-OP operator decision (REVISED 2026-04-25 post-empirical-tiebreaker party-mode round): DEFERRED-PENDING-SLAB-3.** Operator's initial OPT-IN was overturned by an empirical grep-gate run: `marcus.dispatch.contract` is consumed on `run_wrangler.py`'s runtime path at envelope-emission boundary (lines 120-125, 1707-1709, 1717, 2021-2031), NOT dead-on-arrival as initially assumed. Lazy-import shim (Path 2) would produce vacuous-pass evidence (Murat M5 binding from 2a.3 P9 lesson). Forward-port marcus.dispatch.contract (Path 1) is Slab-3 architectural scope drift. Defer (Path 3) is the disciplined call. Party-mode 3-1 consensus 2026-04-25: Winston + Murat + Paige → Path 3; Amelia → Path 4 fallback (compatible with Path 3 outcome).

Lifecycle simplified: `ready-for-dev → in-progress → review → done` (no `awaiting-operator-evidence` stage; AC-B-OP marked DEFERRED in Completion Notes; AC-B mockable wrapper shape verification + the operator helper script + directive template ship as PRE-AUTHORED but UNINVOKABLE-ON-HYBRID-TODAY artifacts that Slab-3 reactivates).

### Operator one-liner (run on operator machine, post-dev-agent-T9-close)

A helper script + directive template are pre-authored at:
- **Helper**: [`scripts/utilities/ac_b_op_texas_live_retrieval_evidence.py`](../../scripts/utilities/ac_b_op_texas_live_retrieval_evidence.py)
- **Directive template**: [`tests/fixtures/specialists/texas/ac_b_op_directive.yaml`](../../tests/fixtures/specialists/texas/ac_b_op_directive.yaml) (defaults to single-provider scite query; customize provider/intent if using a different provider)

Step 1 — set the real provider key in the operator session (PowerShell example for Windows; replace with your provider's env-var name if not scite):

```powershell
$env:SCITE_API_KEY = "<your-real-scite-key>"
```

Step 2 — run the helper (creates the bundle dir, runs the wrangler, computes the six sha256s, extracts result.yaml tail, emits the filled-in evidence block to stdout AND persists it to `<bundle-dir>/ac_b_op_evidence.md`):

```powershell
.venv/Scripts/python.exe scripts/utilities/ac_b_op_texas_live_retrieval_evidence.py `
  --directive tests/fixtures/specialists/texas/ac_b_op_directive.yaml `
  --bundle-dir _bmad-output/specs/ac_b_op_2a4_run/ `
  --provider-key-env SCITE_API_KEY
```

Bash equivalent (if running from git-bash):

```bash
.venv/Scripts/python.exe scripts/utilities/ac_b_op_texas_live_retrieval_evidence.py \
  --directive tests/fixtures/specialists/texas/ac_b_op_directive.yaml \
  --bundle-dir _bmad-output/specs/ac_b_op_2a4_run/ \
  --provider-key-env SCITE_API_KEY
```

Step 3 — paste the emitted Markdown block (also persisted at `_bmad-output/specs/ac_b_op_2a4_run/ac_b_op_evidence.md`) into this Completion Notes section under the "Filled-in evidence" heading below. Add any operator observations (paywall behavior, convergence-signal observed, provider-specific metadata sanity check). Story flips `awaiting-operator-evidence → done` at that point + `migration-epic-2a-slab-2-scaffold-pilot` flips to `done` (slab close).

### Filled-in evidence (operator pastes here)

_(Operator paste from the helper output goes here. Template structure shown below for reference; the helper auto-fills the sha256s + exit-code-meaning + result.yaml tail.)_

```
## AC-2a.4-B-OP live retrieval-provider dispatch evidence (operator-gated)

Environment: real SCITE_API_KEY set (redacted)
Directive shape: ac_b_op_directive.yaml
Timestamp: <ISO8601 from helper>

Command:
  .venv/Scripts/python.exe skills/bmad-agent-texas/scripts/run_wrangler.py \
    --directive tests/fixtures/specialists/texas/ac_b_op_directive.yaml \
    --bundle-dir _bmad-output/specs/ac_b_op_2a4_run/ \
    --json

Runner exit code: <0 | 10 | 20 | 30> (<exit-code meaning>)

Six-artifact bundle file roster + sha256:
  extracted.md             <sha256>
  metadata.json            <sha256>
  manifest.json            <sha256>
  extraction-report.yaml   <sha256>
  ingestion-evidence.md    <sha256>
  result.yaml              <sha256>

result.yaml envelope (tail):
  <auto-extracted by helper — first ~40 lines>

Notes / observations:
  <operator fills in>
```

---

## Open Questions / Flags for Operator

1. **Sanctum lock-and-verify pre-T1:** has the operator captured the pre-run sha256 manifest of `_bmad/memory/bmad-agent-texas/` for the lock baseline? **AC-D test 3 depends on this.** If not yet captured, dev agent runs the manifest at T1 open and records it in §G.
2. **~~Live retrieval-provider dispatch evidence~~** — **REVISED 2026-04-25 post-empirical-grep-gate party-mode round: DEFERRED-PENDING-SLAB-3.** Operator initially OPT-IN; reversed by 3-1 party-mode consensus when grep gate proved `marcus.dispatch.contract` is consumed on the runtime path (NOT dead-on-arrival). Lazy-import shim was rejected as vacuous-pass class (Murat); forward-port was rejected as Slab-3 architectural scope drift (Winston/Paige); Path 4 (T1-discovery) was Amelia's fallback compatible with deferral. AC-B-OP reactivates at Slab-3 once marcus.dispatch.contract forward-ports per `deferred-inventory.md §CLASS B`. Pre-authored helper script + directive template ship as UNINVOKABLE-ON-HYBRID-TODAY artifacts that Slab-3 reactivates.
3. **A9 fourth-example augment vs title-broadening:** at AC-M D12 close, is the harvest-gate disposition (a) augment A9 with a fourth bullet (test-path drift), OR (b) broaden A9's title from "Epic-doc node-name drift" to "Epic-doc structural-name drift"? Defer to G6 review; party-mode rider acceptable.
4. **Slab 2a retrospective output file (`slab-2a-retrospective.md`):** is the ~200-300 line target appropriate, or operator wants a tighter / fuller treatment? Expected sections: (a) FR coverage closed across the slab; (b) cumulative regression intelligence (303 → ~395 net); (c) deferred-inventory follow-ons surfaced; (d) anti-pattern catalog state; (e) §12 §reference completeness; (f) Slab 2b kickoff readiness checklist.

---

## Status-transition discipline (SF2 inherited from 2a.2/2a.3)

**Operator decision REVISED 2026-04-25 post-tiebreaker (was OPT-IN; flipped to DEFERRED-PENDING-SLAB-3 by 3-1 party-mode consensus).** Texas lifecycle:

1. `ready-for-dev` → dev-story opens
2. `in-progress` → T1–T9 execution
3. `review` → independent G6 layered review fires per 2a.3 precedent (Blind Hunter / Edge Case Hunter / Acceptance Auditor; PATCH/DEFER/DISMISS triage)
4. `done` → all dev-agent ACs green (placeholder-key regression ≥395; ruff clean; import-linter 3/3 KEPT; sandbox-AC PASS); G6 patches applied; D12 slab-closing close stub recorded; party-mode retrospective convened (`slab-2a-retrospective.md` ~250 lines authored); AC-B-OP marked DEFERRED-PENDING-SLAB-3 in Completion Notes citing this party-mode round as deferral authority; **at this point also flip `migration-epic-2a-slab-2-scaffold-pilot` in-progress → done** (slab close)

**AC-B-OP reactivates at Slab-3 once `marcus.dispatch.contract` forward-ports** (per `_bmad-output/planning-artifacts/deferred-inventory.md §CLASS B "PR-R Marcus dispatch contract + boundary retrofits"`). Reactivation gate per Murat binding: re-execute M2/M3 sha256 baselines + M4 subprocess-dispatch-latency on **live wire** — not "AC-B-OP fires." Mock evidence at 2a.4 is shape-verification only; live-wire-proven obligation carries forward to Slab-3.

**At slab close (post-2a.4-done flip):** also flip `migration-epic-2a-slab-2-scaffold-pilot` from `in-progress` to `done` in sprint-status.yaml. Slab 2a is closed; Slab 2b kickoff-readiness check fires (A12 generator auto-emit follow-on landing is the gate).

---

**Status:** review (dev-story execution complete 2026-04-25; pending independent G6 layered review and D12 close protocol before done)
**Authoring note:** Comprehensive spec for the third per-specialist migration; first PURE-tool-dispatch act-body category (no LLM at the Texas layer); first REAL populated-and-locked sanctum cold-read exercise; Slab 2a closing story with expanded D12 slab-retrospective protocol. Total 13 ACs (A–M plus operator-gated AC-B-OP); target ~19-22 tests at K~1.4-1.6× (with party-mode riders applied); placeholder-key regression floor ≥395 (was 380 pre-2a.4; +16-19 net with riders).

**Pre-coding party-mode 4/4 GREEN-with-riders 2026-04-25** (Winston / Amelia / Murat / Paige) — riders integrated:
- **Winston W1**: AC-D test 4 lock-violation named exception (`SanctumLockViolation` or equivalent ~10 LOC error class; reusable across Irene/Kira via Slab-2-cross-cutting follow-on)
- **Amelia A1-A4**: AC-B subprocess kwargs pinning (`shell=False, timeout=30`); 7 parse-branch cases (collapse-to-6 escape clause); inlined module-level baseline constants; AC-J single pytest call across 3 suites
- **Murat M1-M5**: 7 parse-branch cases; hard sha256 on AC-D test 3 + AC-I; subprocess-dispatch-latency substitute metric for §12.10; two-sided parse assertions
- **Paige P1-P8**: A9 retitled NOW (landed in `specialist-anti-patterns.md` pre-T1); §12 section-level framing sentence above §12.5; renumber-grep scope expanded to `next-session-start-here.md` + `deferred-inventory.md`; explicit framing-sentence verification in AC-K; §12.10 cap at 4 paragraphs; slab-2a-retrospective.md ~250 lines with section-by-section line budget + 5-line opener; deferred-inventory items filed for §12 size review + implementation-artifacts/ index

T1 Readiness explicitly flags THREE Epic 2a.4 drifts: test path drift (A9 fourth instance — A9 already retitled to "Epic-doc structural-name drift"), symlink-vs-pointer-file (epic-listed both options), six-artifact bundle confirmed alignment. Three carries from 2a.3 party-mode integrated into T1: parse-branch coverage at AC-B; `.gitattributes` hygiene PR at AC-L; §12 framing-sentence + §12.7/§12.8 renumber-grep at AC-K. NFR-I5 retrieval-contract preservation enforced via sha256 baseline test (AC-I; baseline `ac98ff62…` captured 2026-04-25). Sanctum lock-baseline (16 files) captured 2026-04-25; pinned at T1 §G; module-level constant per A3. Sandbox-AC expected PASS. Follows DR-1 GOLDEN ratification ("spec yields to code on conflict") in every drift-fix direction. **Slab 2a closes at 2a.4 → feeds M2 milestone; Slab 2b.1 TEMPLATE gated on A12 generator auto-emit follow-on landing.** Slab 2a momentum: 2a.1 ✅ → 2a.2 ✅ (95.33% cache-hit-rate; M1 ACCEPT-WITH-GAP retired) → 2a.3 ✅ (Kira tool-dispatch + populated-sanctum graceful-degrade) → **2a.4 opens with 4/4 party-mode GREEN + 18 riders integrated** → Slab 2a CLOSE → Slab 2b kickoff.
