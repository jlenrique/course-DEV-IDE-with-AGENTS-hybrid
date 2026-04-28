# How to add a new specialist

**Purpose:** single consolidated walkthrough from first-breath sanctum through formal close for adding a new scaffold-conformant specialist to the migrated runtime. Replaces the fragmented coverage previously spread across `specialist-migration-template.md`, `specialist-anti-patterns.md`, `scaffold-conformance-framework.md`, `langgraph-migration-guide.md` §12, `composition-specification.md` §5.1, and `slab-6-trial-experience-bundle-governance-discipline.md`.

**Audience:** dev agent OR operator-facilitated dev workflow adding a new specialist (e.g., one of the 6 named-but-unbuilt specialists Mike/Eli/Enrique/Mira/Sally/Kim, or an operationally-discovered specialist not in the original Epic 2b roster).

**Authorship:** drafted 2026-04-28 immediately after Slab 6 bundle close. Living document — extend as new patterns emerge.

**Scope:** post-SHIP migrated runtime. Specialists added here are runtime-graph nodes (Layer 3 per `docs/agent-environment.md`). The pre-migration "agent personality" creation flow is out of scope.

---

## Decision: do you actually need a new specialist?

**Before authoring, confirm:**

1. **Operational need is concrete.** A specialist is non-trivial substrate; don't add one for speculative future use. If you're not sure when the new specialist would fire in production, defer.

2. **No existing specialist can be extended.** Check `state/config/dispatch-registry.yaml` and `app/specialists/` — an existing specialist may already have the right `_act` body category. Extension is cheaper than addition.

3. **Composition implications understood.** New specialist will need a `dependencies:` declaration in `state/config/pipeline-manifest.yaml` (post-Slab-6.2). Identify the specialist's upstream dependencies BEFORE filing.

4. **Composition Spec §11 trigger NOT firing.** If this new specialist surfaces a fan-out / partial-state-mid-execution / gate-precedence-complexity / new-act-body-category need, that's a §11 migration trigger. STOP and surface to operator + party-mode. Do NOT silently add a new specialist that triggers Option C migration territory.

If all four checks pass, proceed.

---

## Three layers (re-cap from `docs/agent-environment.md`)

A migrated specialist exists in three coexisting layers:

| Layer | Path | Role | Authoring |
|---|---|---|---|
| 1 — Sanctum | `_bmad/memory/bmad-agent-<name>/` | WHO the agent is (persona; expertise; persistent learnings) | First-breath ceremony (operator-driven) |
| 2 — Skill | `skills/bmad-agent-<name>/` | HOW to activate in operator/conversational context (entry point + references) | Skill scaffolding (operator-driven) |
| 3 — Specialist node | `app/specialists/<name>/` | HOW to run as a production-runtime node (9-node scaffold) | `bmad-create-specialist` generator (validated in Slab 2c.1) |

**Authoring order matters:** Layers 1 + 2 must exist BEFORE the generator runs. The generator reads from the skill tree; if the skill tree is empty, the generator emits a stub specialist that won't have meaningful behavior.

---

## Step-by-step walkthrough

### Phase 0 — Decision + scoping (operator)

1. **Confirm operational need.** Write a one-paragraph rationale: when does this specialist fire? What does it consume? What does it produce? Save this with the specialist's planning notes.
2. **Identify upstream dependencies.** Which existing specialists' contributions does this new specialist read? (Answer becomes the manifest `dependencies:` declaration.)
3. **Identify `_act` body category.** Pure-LLM (like Irene Pass 2)? Tool-dispatch-with-LLM (like Kira Motion)? Pure-tool-dispatch (like Texas)? Or NEW category? If NEW, surface as §11 trigger candidate FIRST.
4. **File a story spec via `bmad-create-story`** per CLAUDE.md §1. Story key shape: `migration-<slab>-<n>-<specialist-name>-scaffold-migration` if migrating a specialist; `migration-<slab>-<n>-<specialist-name>-greenfield` if filing a greenfield specialist. Spec authoring follows the standard template (see `docs/dev-guide/specialist-migration-template.md` for R1–R14).

### Phase 1 — Sanctum first-breath (operator)

5. **Author Layer 1 sanctum.** Create `_bmad/memory/bmad-agent-<name>/` with:
   - `INDEX.md` — what's in this sanctum + cross-links
   - `PERSONA.md` — voice, principles, communication style
   - `EXPERTISE/` — domain knowledge references the agent owns
   - `MEMORY/` — persistent learnings (initially empty; accumulates over time)
   - Optional: `CHRONOLOGY.md` for cross-session continuity

   Follow `docs/dev-guide/sanctum-reference-conventions.md` for path conventions + dotted-reference idiom.

6. **Validate sanctum loads cleanly.** No automated test for this yet; operator visually inspects + verifies the agent can be activated via `/bmad-agent-<name>` (or whatever invocation the skill defines).

### Phase 2 — Skill scaffolding (operator)

7. **Author Layer 2 skill at `skills/bmad-agent-<name>/`:**
   - `SKILL.md` — activation sequence (read sanctum + load references)
   - `references/` — operator-facing reference docs (cross-link to sanctum)
   - Optional: `scripts/` for helper utilities; `assets/` for examples

8. **Verify skill activates.** Test invocation via Claude Code's Skill tool OR via Cursor command. Confirm sanctum loads + persona embodies correctly.

### Phase 3 — Specialist node generation (dev agent)

9. **Run `bmad-create-specialist` generator:**
   ```bash
   .venv/Scripts/python.exe -m skills.bmad_create_specialist.scripts.generate \
       --from-skill bmad-agent-<name> \
       --emit-c3-row
   ```
   The generator emits the 9-file specialist tree at `app/specialists/<name>/` AND atomically appends the `app.specialists.<name>.graph -> app.gates.resume_api` row to `pyproject.toml` C3 `ignore_imports` list (per Story 2a.5 auto-emit machinery; eliminates the A12 procedural-coupling pattern).

10. **Verify scaffold conformance.** Run:
    ```bash
    .venv/Scripts/python.exe -m pytest tests/integration/scaffold_conformance/test_scaffold_<name>.py -q --tb=short
    ```
    Expected: PASS. Conformance test asserts the specialist has all 9 nodes (`receive`, `plan`, `act`, `verify`, `reflect`, `emit_spans`, `gate_decision`, `finalize`, `handoff`) wired correctly.

### Phase 4 — Implementation (dev agent)

11. **Implement `_plan` node.** Resolves model cascade via `make_chat_model(...)` per per-specialist `model_config.yaml`; populates resolution trail.

12. **Implement `_act` node.** Per chosen body category from Phase 0:
    - **Pure-LLM:** invoke chat model with assembled prompt; extract response into return-shape Pydantic model
    - **Tool-dispatch-with-LLM:** invoke chat model first to produce tool input; subprocess dispatch to skill's runtime script; parse tool output
    - **Pure-tool-dispatch:** subprocess dispatch only; no LLM call at this layer (still resolves model cascade at `_plan` for trail-entry consistency, but chat handle never invoked)

    **CRITICAL:** specialist must remain usable in BOTH M3 isolated harness mode AND production runner composition mode (per `docs/dev-guide/composition-specification.md` §3 + N11 substrate inventory checklist). Reads inputs from `state.cache_state.cache_prefix` (per-specialist scratch); writes outputs to same field for downstream specialists. The adapter at runner layer marshals between cache_prefix and the production envelope.

13. **Implement remaining 7 nodes per scaffold.** `_verify`, `_reflect`, `_emit_spans`, `_gate_decision`, `_finalize`, `_handoff` are mostly boilerplate — copy from `app/specialists/_scaffold/` + customize as needed. Per-specialist `gate_decision` interrupt fires within isolated mode; auto-resolves under production composition by default per Composition Spec §3.5.

14. **Author `app/specialists/<name>/state.py`** if specialist needs domain-specific state extensions. Most specialists don't; the standard `RunState` carrier suffices.

15. **Author `app/specialists/<name>/expertise/README.md`** with dotted-reference table mapping expertise topics to sanctum paths. Test: `tests/specialists/<name>/test_<name>_expertise_readme_lists_l4_references.py` (generator emits stub).

### Phase 5 — Manifest + dispatch registry (dev agent)

16. **Add specialist to `state/config/dispatch-registry.yaml`** under appropriate category. Verify `_status: production`.

17. **Add per-node entry to `state/config/pipeline-manifest.yaml`** with explicit `dependencies:` declaration:
    ```yaml
    nodes:
      - id: <step-id>
        specialist: <name>
        dependencies:
          <downstream-input-key>: <upstream-specialist-id>
    ```
    Per Slab 6.2 `_resolve_dependency_map` resolution, manifest declarations win over runner-layer fallback. If the specialist's primary upstream isn't in the existing fallback table (Texas → CD `source_bundle`; default `upstream_output`), declare explicitly.

18. **Verify manifest validator + circular-dep check pass:**
    ```bash
    .venv/Scripts/python.exe -m scripts.utilities.check_pipeline_manifest_lockstep
    ```
    Expected: exit 0.

### Phase 6 — Tests (dev agent)

19. **Author per-specialist test directory at `tests/specialists/<name>/`** with:
    - `test_<name>_state_shape.py` — Pydantic four-file-lockstep verification
    - `test_<name>_cascade.py` — model cascade resolution
    - `test_<name>_gate_decision.py` — interrupt + auto-verdict
    - `test_<name>_act.py` — primary act-body verification (mocked LLM at boundary)
    - `test_<name>_sanctum.py` — sanctum cold-read (cache prefix byte-stable)
    - `test_<name>_trail.py` — resolution trail entries
    - `test_<name>_envelope_return.py` — return-shape contract
    - Live test (optional): `tests/specialists/<name>/test_<name>_live.py` with `@pytest.mark.llm_live` marker (auto-skip when `OPENAI_API_KEY` placeholder)

20. **Author chain test at `tests/composition/`** per chain-test-per-PR rule (Composition Spec §6):
    - `tests/composition/test_<upstream>_to_<name>_chain.py` exercises the new specialist with at least one upstream specialist end-to-end through `ProductionDispatchAdapter`
    - Assert envelope-state propagation (NOT just output equality)
    - Assert envelope contribution accumulation (both specialists' contributions present in order)
    - Assert downstream input was constructed from upstream contribution (proves dependency_map worked)
    - Use synthetic specialist outputs at LLM-call boundary; cost ~$0

21. **Update `tests/composition/test_specialist_isolation_preserved.py`** parametrize to include the new specialist (verifies isolated execution path still works post-addition).

### Phase 7 — Substrate Inventory Checklist trace (dev agent)

22. **Trace per applicable N-item:**
    - **N1 (External-provider resource ID validity):** verify `model_config.yaml` model_id appears in `tests/fixtures/openai_catalog_snapshot.json` (or equivalent for other providers). Run live cascade-tier smoke per A15 counter-pattern.
    - **N4 (Per-component isolation invariant preserved):** specialist's isolated-execution test passes; M3 deterministic harness path remains valid.
    - **N5 (Cross-component state-flow contract):** dependency_map declaration explicit; missing-upstream fails-loud per Composition Spec §3.6.
    - **N7 (Replay regression verifies execution path):** new specialist contribution's `output_digest` reproducibly computes; replay-regression slice unaffected.
    - **N9 (Operator-witnessed evidence at story close):** operator runs at least one chain test that exercises the new specialist.
    - **N11 (Composition mode declared alongside isolated mode):** specialist usable in both M3 harness AND production runner contexts; chain test proves composition mode.
    - **N12 (Auth model verified via probe):** if specialist uses any new external integration (new MCP server, new API), probe auth model end-to-end before declaring done.

    Other N-items (N2/N3/N6/N8/N10) are typically N/A for new-specialist work; document N/A with rationale.

### Phase 8 — Anti-pattern catalog application (dev agent)

23. **Read `docs/dev-guide/specialist-anti-patterns.md` at T1.** Counter-patterns most likely to apply:
    - **A6** (closed-enum red-rejection) — for any closed-set fields in specialist's contract
    - **A9** (Epic-doc structural-name drift) — verify specialist names align between manifest, dispatch-registry, code paths
    - **A11** (Windows-portability hostile path handling) — use `Path.is_relative_to(...)` not string-prefix checks
    - **A12** (procedural-coupling) — generator auto-emit handles C3 row; verify no manual edits needed
    - **A15** (referent-validity) — model_id must appear in real provider catalog
    - **A17** (substrate designed for isolation, composition assumed) — preserve isolation invariant; declare composition mode

24. **If a NEW pattern surfaces during dev, propose to Mary harvest-gate.** Do NOT silently absorb. New entries get filed at story close.

### Phase 9 — Story spec close + party-mode green-light (operator)

25. **Run `bmad-party-mode` green-light** per CLAUDE.md §2 with Winston + Murat + Paige + Amelia minimum (add Quinn-R + Mary if dual-gate or harvest-gate review applicable). Apply BINDING riders to spec; flip sprint-status `ready-for-party-mode-greenlight → ready-for-dev`.

26. **Run `bmad-dev-story`** per CLAUDE.md sprint governance.

27. **Run `bmad-code-review`** before flipping to done per CLAUDE.md §3. Three-layer (Blind Hunter + Edge Case Hunter + Acceptance Auditor) + N-item trace deliverable per Slab 6.0 governance template.

28. **Triage** per disposition rules (patch / defer / dismiss / decision_needed). Apply patches; file defers in deferred-inventory; justify dismissals; HALT-and-surface decision_needed.

29. **Formal close per discipline doc Gate 6:**
    - sprint-status flip `review → done` with summary annotation
    - deferred-inventory `Last refreshed:` line update + per-finding entries filed
    - Composition Spec §10 Decision Log entry IF specialist surfaces new substrate decision
    - m5-decision close annotation NOT applicable (single specialist addition isn't a milestone)

### Phase 10 — Operator validation (operator)

30. **Run pre-flight health check** with new specialist included:
    ```bash
    .venv/Scripts/python.exe scripts/operator/migration_full_health_check.py
    ```
    Expected: PASS across all slices including the new specialist's isolation + chain test.

31. **Run live cascade-tier smoke** if specialist added new model_id:
    ```bash
    .venv/Scripts/python.exe -m pytest tests/live/test_openai_cascade_tiers_smoke.py -m live -q
    ```

32. **Optional:** queue a tracked trial that exercises the new specialist to verify production composition works end-to-end.

---

## Common pitfalls (extracted from Slab 2 + Slab 6 close cycles)

1. **Skipping Phase 1 (sanctum first-breath)** — generator emits stub; specialist has no meaningful behavior. ALWAYS author sanctum + skill before generator.
2. **Forgetting manifest dependency declaration** — runner falls back to default; specialist may produce wrong-shape output for downstream. Declare explicitly per Slab 6.2.
3. **Modifying the 9-node scaffold structure** — never. The scaffold IS the contract. Customize within nodes; do not add/remove nodes.
4. **Silent state mutation in `_act`** — write to `cache_state.cache_prefix` per per-specialist scratch convention; do NOT touch `production_envelope` directly (adapter's job).
5. **Missing chain test** — chain-test-per-PR rule is BINDING. Without it, A17 risk re-surfaces.
6. **Implicit closed enums** — every closed-set field needs three red-rejection surfaces (Pydantic Literal + JSON Schema enum + shape-pin test) per A6.
7. **Hardcoded paths assuming Linux** — use `Path.is_relative_to(...)` and forward-slash compat; A11 counter-pattern.
8. **Adding before reading anti-pattern catalog** — every entry was earned by an A-class incident; consume the catalog at design time, not re-discover its lessons in production.

---

## See also

- `docs/dev-guide/specialist-migration-template.md` — R1–R14 specialist-migration rules (covers migration-from-primary; this how-to covers greenfield-on-hybrid)
- `docs/dev-guide/specialist-anti-patterns.md` — A1–A17 + P1–P3 catalog
- `docs/dev-guide/scaffold-conformance-framework.md` — 9-node scaffold contract
- `docs/dev-guide/composition-specification.md` — Option B governing reference (especially §5.1 Add a new specialist; this how-to expands that section)
- `docs/dev-guide/substrate-inventory-checklist.md` — N1–N12 standing pre-flight
- `docs/dev-guide/sources-of-truth.md` — comprehensive SSOT registry per topic
- `docs/dev-guide/sanctum-reference-conventions.md` — sanctum path + dotted-reference conventions
- `docs/dev-guide/pydantic-v2-schema-checklist.md` — four-file-lockstep contract for any Pydantic model in specialist's contract
- `docs/dev-guide/langgraph-migration-guide.md` §12 — per-Slab walkthrough (Irene/Kira/Texas/Wanda worked examples)
- `_bmad-output/implementation-artifacts/slab-6-trial-experience-bundle-governance-discipline.md` — six-gate sequence per story
- `CLAUDE.md` — project instructions, sprint governance, sandbox-AC discipline
