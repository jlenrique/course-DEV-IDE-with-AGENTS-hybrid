# Specialist Anti-Patterns Catalog

Living catalog of anti-patterns harvested across Slab-1 closure + inherited
from the primary repo's `docs/dev-guide/dev-agent-anti-patterns.md`. Every
Slab 2+ story's dev-agent reads this at T1.

Slab 2 (2a + 2b + 2c) harvest cycle complete. Slab 3 harvest cycle complete.
Slab 4 harvest cycle complete. The catalog remains at 14 entries A1-A14 under
format-freeze v1. Slab 3 and Slab 4 both closed without accepting a new
catalog entry; the live-wire-substrate caution remains documented in deferred
inventory and conditional milestone artifacts unless party-mode consensus later
promotes it to a frozen catalog entry.

MIGRATION COMPLETE - Slab 1+2+3+4+5a harvest cycles all complete; format-freeze
v1 preserved through ship; post-ship harvest continues under same freeze unless
format-version bump.

Slab 1+2+3+4+5a harvest cycle complete; ≥5 entries A1-A14 per FR64;
cross-references in migration-guide §Anti-Patterns Appendix; format-freeze v1
preserved.

> **You-are-here** (Slab 2+ dev-agent reading order at T1):
> 1. [`scaffold-conformance-framework.md`](scaffold-conformance-framework.md) â€” 9-node canonical contract + T1 pre-flight
> 2. [`langgraph-state-idioms.md`](langgraph-state-idioms.md) â€” state-shape idioms (interrupt, Command, Send, reducers)
> 3. [`model-selection-guide.md`](model-selection-guide.md) â€” three-level cascade
> 4. **This catalog** â€” known traps (read before writing ACs)

## Format (frozen â€” changes require party-mode consensus)

**Four-field format** (frozen at Paige 2026-04-22 amendment; version-controlled below):
each entry carries EXACTLY these four fields â€” `name` / `example` / `counter-pattern` /
`slab-of-discovery`. No `severity:`, `priority:`, `frequency:`, `owner:`,
`rationale:` or other supplementary fields. **Adding a field requires party-mode
consensus + version bump of this format-freeze declaration; it is NOT a dev-agent
authority change.**

**Exemplar entry** (match this shape exactly when adding a new entry):

```markdown
### NN. <name>

- **Example:** <concrete instance; cite commit/story/line verbatim>
- **Counter-pattern:** <what to do instead; cite the authoritative framework/doc/test as source of truth>
- **Slab of discovery:** <Slab N or story ID>
```

**Harvest gate** (per Mary round-3 caveat): a new entry requires either
(a) a documented burn (story-closure note citing the actual defect/cycle
cost/rework evidence), OR (b) party-mode consensus that the pattern is real
even without a burn. Prevents speculative entries.

**Format version:** 1 (2026-04-22 initial). Bump on any field-set change.
Format version: 1

## Confirmed Slab-1 entries

### A1. Operator-CLI-on-PATH assumption in dev-agent ACs

- **Example:** Story 1.1b's original ACs required `docker-compose up -d` + `psql
  "$DATABASE_URL" -f init.sql`. Both CLIs were unavailable in the sandbox
  (operator ran Postgres natively; psql was not globally installed), and dev-story
  attempts stalled twice before the `project_no_docker` decision closed the Docker
  branch and the sandbox-AC discipline fixed the psql branch.
- **Counter-pattern:** every dev-agent AC verifies via shipped Python deps
  (`psycopg`, `boto3`, `PyGithub`, `httpx`, etc.) with `pytest.skip(...)` when the
  service is unreachable. Live-CLI evidence that genuinely needs an operator
  machine splits into an `AC-X-A` (dev-agent, skip-on-unreachable) + `AC-X-B`
  (operator-gated, Completion-Notes paste). Enforced at story `ready-for-dev` and
  `bmad-dev-story` open by
  `scripts/utilities/validate_migration_story_sandbox_acs.py`. Reference operator
  memory: `memory/feedback_verify_via_shipped_deps.md`.
- **Slab-of-discovery:** Slab 1 Story 1.1b.

### A2. Architecture-decision relitigation at story-author time

- **Example:** Story 1.1c authoring spent two party-mode rounds redebating
  MCP-in-Slab-1 scope despite the architecture doc having locked the middle-path
  consensus earlier that same day (2026-04-22, 5/5 vote). The author had been
  treating architecture decisions as reopenable at story-author time.
- **Counter-pattern:** decisions live in governance JSONs
  (`docs/dev-guide/migration-story-governance.json` for gate-mode/K-target;
  architecture doc for decision-of-record D1â€“D13). The story author reads the JSON
  rather than re-derives. Amendments require party-mode consensus + version bump
  in the architecture doc, not a story-spec override. Origin of the middle-path
  consensus chain that 1.1c drifted from:
  [`_bmad-output/planning-artifacts/slab1-story-set-A-t1-bundle.md Â§8`](../../_bmad-output/planning-artifacts/slab1-story-set-A-t1-bundle.md).
- **Slab-of-discovery:** Slab 1 Story 1.1c authoring pass.

### A3. Architecture-vs-epics drift uncaught at story-author time

- **Example:** Architecture Â§D3 placed `OperatorVerdict` substrate + Contract C3
  in Slab 1; epics Â§3.3 had drifted to Slab 3. Set-A authoring (2026-04-22)
  initially missed the drift â€” the sandbox-AC validator + gate-mode JSON check
  didn't catch it because it was a scope drift between architecture decisions and
  epics decomposition, not a per-story issue. Mary surfaced the drift at
  set-level party-mode review, adding BLOCKER-1 to the set-level amendments and
  pulling the substrate into Stories 1.2 (`OperatorVerdict`) + 1.4 (`resume_api`
  stub + Contract C3).
- **Counter-pattern:** cross-reference architecture decision-of-record (D1â€“D13)
  against epics decomposition during **set-level** T1 readiness, not only at
  per-story gate-mode lookup. If a set-level review surfaces architecture-vs-epics
  drift, escalate BEFORE individual stories open (BLOCKER-level amendment, not
  silent extension of one story).
- **Slab-of-discovery:** Slab 1 set-A authoring (2026-04-22 set-level review).

### A9. Epic-doc structural-name drift from Slab-1-hardened reality

> **Title broadening (Story 2a.4 party-mode rider P1, 2026-04-25):** Original title was "Epic-doc node-name drift from Slab-1-hardened framework." Broadened to **"Epic-doc structural-name drift from Slab-1-hardened reality"** to cover the four-and-counting concrete instances spanning node names + test paths (and to anticipate bundle-artifact names, scaffold filenames, future tool-registry keys as the same drift class). The three node-name examples below remain unchanged â€” they are now examples *of* the broader structural-name drift, which is what they always were. Adding the path-drift example as #4 under the original title would have produced a discoverability failure (a reader scanning the catalog for path drift skips a "node-name" entry).

- **Example (Story 2a.1, first instance â€” node names):** Epic 2a Story 2a.1 line 555 uses node names `plan/enter_sanctum/load_expertise/reason/act/validate/emit/return/exit_sanctum`; Slab-1-hardened `scaffold_contract.py::SCAFFOLD_NODE_IDS` uses `receive/plan/act/verify/reflect/emit_spans/gate_decision/finalize/handoff`. The sets do not map.
- **Example (Story 2a.2, second instance â€” node names):** Epic 2a.2 lines 584â€“585 use node names `reason/act/validate/emit/return` â€” same drift pattern, different story. Per Paige harvest-gate rule (party-mode 2026-04-24), duplicate patterns augment existing entries rather than creating new ones.
- **Example (Story 2a.3, third instance â€” node names):** Epic 2a.3 line 620 uses `reason node` (canonical name is `plan`) â€” third concrete instance of node-name drift. Confirms the harvest-gate rule's value: a single new entry would have been silently noisy; the augmented A9 entry now carries three independent epic-doc occurrences pointing at the same root cause (epic prose drifted from Slab-1-hardened framework).
- **Example (Story 2a.4, fourth instance â€” test path):** Epic 2a.4 line 647 says *"Texas's current tests (`tests/bmad-agent-texas/...`) exist from primary"*. The hybrid test tree is at `tests/agents/bmad-agent-texas/` (verified â€” contains `test_cross_validator.py` + `test_extraction_validator.py`). Same drift class (epic-prose-vs-Slab-1-hardened-reality) but the entity drifting is a **path component**, not a node name â€” which is why the title needed broadening. This is the fourth concrete instance and the precedent for treating paths, bundle-artifact names, scaffold filenames, and future tool-registry keys as A9-class.
- **Counter-pattern:** Treat epic prose as potentially stale on any structural name. The authoritative sources are: `tests/integration/scaffold_conformance/scaffold_contract.py::SCAFFOLD_NODE_IDS` for node names; the actual hybrid working-tree paths for test directories and source modules; `state/config/pipeline-manifest.yaml` and the per-step pack for pipeline structural names. If drift appears, flag it in T1 readiness and harvest it as an A9 example before story close.
- **Slab-of-discovery:** Slab 2a Story 2a.1; second example confirmed at Story 2a.2; third example confirmed at Story 2a.3; fourth example (and title broadening) confirmed at Story 2a.4 party-mode pre-coding round.

### A10. Epic-doc model-ID + tier drift from shipped registry

- **Example:** Epic 2a.2 lines 587â€“589 say "Irene uses model tier 'long-context balanced'... default resolves to `gpt-4.1`". The shipped registry at `app/models/registry.yaml` has entries `gpt-5.4 / gpt-5-haiku / gpt-5-codex` (NO `gpt-4.1`); `app/models/selection_policy.yaml` has tiers `reasoning / fast / code` (NO "long-context balanced"). The drift is config-cascade-value staleness (distinct from A9's node-name-list staleness).
- **Example (Story 2a.3 second instance):** Epic 2a.3 lines 619â€“621 say "Kira's model tier is 'multimodal'... default resolves to `gpt-4o` per selection policy". Neither value exists in the shipped registry â€” `gpt-4o` is not registered, and tier `multimodal` is not in `selection_policy.yaml`. Kira's video-direction workload maps to `tier_request: fast` per the cost-aware Kira principle, resolving to `gpt-5-haiku`. Per Paige harvest-gate rule, duplicate patterns augment existing entries.
- **Example (Story 2b.1 third instance):** Epic 2b.1 line 691 says "default resolves to `gpt-4.1-mini` per selection policy". Neither value exists in the shipped registry â€” `gpt-4.1-mini` is not registered (registry has `gpt-5.4 / gpt-5-haiku / gpt-5-codex`); "fast & cheap workhorse" is not a registered tier name (selection_policy has `reasoning / fast / code`). Gary's "fast & cheap workhorse" workload maps to `tier_request: fast` per the cost-aware Gary principle, resolving to `gpt-5-haiku`. Three-instance evidence base across Slab 2a + Slab 2b open: Irene `gpt-4.1` + Kira `gpt-4o` + Gary `gpt-4.1-mini`. Per Paige harvest-gate rule, duplicate patterns augment existing entries.
- **Example (Story 2b.2 fourth instance):** Vera's source skill contract names "L2 agentic evaluation" as a tier, but `app/models/selection_policy.yaml` only defines `reasoning / fast / code`. The migration maps Vera's workload to `tier_request: reasoning`, resolving to `gpt-5.4` from the live registry. Same drift class: stale tier naming in story-facing prose vs shipped cascade enum.
- **Example (Story 2b.3 fifth instance):** Quinn-R references "Quality Guardian" tier framing in specialist prose, but the live cascade enum remains `reasoning / fast / code`. Quinn-R's workload maps to `tier_request: reasoning` and resolves to `gpt-5.4`.
- **Counter-pattern:** Read `app/models/registry.yaml` + `app/models/selection_policy.yaml` as the authoritative model-cascade contract. Map specialist workloads to the live `tier_request` enum (`reasoning / fast / code`); resolution flows through the cascade. Document the mapping rationale in the specialist's `model_config.yaml` inline comments. Cross-check against `docs/dev-guide/model-selection-guide.md`.
- **Slab-of-discovery:** Slab 2a Story 2a.2; second example confirmed at Story 2a.3; third example confirmed at Slab 2b Story 2b.1; fourth example confirmed at Slab 2b Story 2b.2; fifth example confirmed at Slab 2b Story 2b.3.

### A11. Epic-doc sanctum/sidecar contract drift from hybrid BMB migration convention

> **Title broadening (Story 2b.1 party-mode rider P-R1, 2026-04-25):** Original title was "Epic-doc sanctum-path drift from hybrid BMB migration convention." Broadened to **"Epic-doc sanctum/sidecar contract drift from hybrid BMB migration convention"** to cover both pure-path drift (Irene) AND parallel-tree contract duality (Gary â€” BMB sanctum + legacy primary-repo SKILL.md sidecar coexisting). Both examples remain unchanged â€” they are now examples *of* the broader contract drift class. Same retitle precedent as A9 at 2a.4: when a second example exposes a wider shape than the first, retitle to keep discoverability working.

- **Example (Story 2a.2, first instance â€” pure path drift):** Epic 2a.2 line 581 says "`_bmad/memory/bmad-agent-irene/` sanctum symlink present". The actual hybrid path is `_bmad/memory/bmad-agent-content-creator/` â€” the convention follows the operator-facing skill-dir name, not the app-side specialist short name. Per CLAUDE.md Â§Custom-agents and Epic-26 BMB-sanctum-migration, hybrid uses **direct directory** (NOT symlink). The drift is persona-tree-migration staleness (distinct from A9 node names + A10 model IDs).
- **Example (Story 2b.1, second instance â€” sidecar contract divergence):** Epic 2b.1 line 681 names skill dir as `skills/bmad-agent-gamma/`; Gary's runtime persona name is `gary`; BMB sanctum convention places the sanctum at `_bmad/memory/bmad-agent-gamma/` (matches skill-dir name per A11 first-example precedent); BUT Gary's SKILL.md activation order separately reads `_bmad/memory/gary-sidecar/index.md` (legacy primary-repo sidecar tree, parallel to and distinct from the BMB sanctum). The LangGraph runtime consumes the BMB sanctum convention (`bmad-agent-gamma`); the SKILL.md sidecar contract is OUT OF SCOPE for the migration. Same drift class as Irene (epic-prose-vs-hybrid-BMB-convention) but the entity drifting is a **dual-tree contract**, not just a path component â€” which is why the title needed broadening.
- **Example (Story 2b.2, third instance â€” sidecar contract divergence):** Vera follows BMB sanctum convention at `_bmad/memory/bmad-agent-fidelity-assessor/` (skill-dir aligned), while legacy activation prose references `_bmad/memory/vera-sidecar/index.md`. The runtime migration reads the BMB sanctum path only; the sidecar tree remains an out-of-scope legacy contract. Same A11 shape as Gary second-instance, confirming recurrence.
- **Example (Story 2b.3, fourth instance â€” sidecar contract divergence):** Quinn-R follows BMB sanctum convention at `_bmad/memory/bmad-agent-quality-reviewer/` (skill-dir aligned), while legacy activation prose references `_bmad/memory/quinn-r-sidecar/index.md`. Runtime migration reads BMB sanctum only; sidecar remains out of scope.
- **Example (Story 2b.5, fifth instance â€” snake_case skill-dir sub-shape):** Tracy runtime uses `skills/bmad_agent_tracy/` (snake_case) while scaffold generator `--from-skill` validation enforces `skills/bmad-agent-*/` (kebab-case), requiring a compatibility alias path for generation even though runtime direct-package imports from snake_case are valid.
- **Example (Story 7c.2, sixth instance - Windows-portability stdout encoding):** Slab 7c §02A Trial-2 run `d44128e9-4e17-4452-a535-989e826cd7da` read `directive.yaml` as UTF-8 and preserved U+202F NARROW NO-BREAK SPACE in YAML, then crashed when the G0 review loop used default `print()` on a Windows cp1252 console. **Symptom:** `UnicodeEncodeError` before operator confirmation. **Root cause:** IO contract drift between UTF-8 fixture bytes and host-console default encoding. **Anti-fix:** requiring `PYTHONIOENCODING=utf-8` as the operator workaround. **Structural fix:** write operator-visible directive text through a UTF-8 byte writer and keep directive file reads/writes UTF-8-explicit or byte-explicit. **Detection guardrail:** cp1252 fixture byte comparison plus a no-`PYTHONIOENCODING` G0 print regression test.
- **Counter-pattern:** Read `docs/dev-guide/sanctum-reference-conventions.md Â§1` as the authoritative path convention. Cross-reference each specialist's `app/specialists/<name>/expertise/README.md` for the dotted-reference idiom. If epic prose names a different sanctum path OR if SKILL.md activation contract names a memory tree distinct from the BMB sanctum, follow the BMB convention for the LangGraph runtime + treat the sidecar contract as out-of-scope unless materially needed + harvest the drift.
- **Slab-of-discovery:** Slab 2a Story 2a.2; second example confirmed at Slab 2b Story 2b.1 + title broadening 2026-04-25; third example confirmed at Slab 2b Story 2b.2; fourth example confirmed at Slab 2b Story 2b.3; fifth example confirmed at Slab 2b Story 2b.5; sixth example confirmed at Slab 7c Story 7c.2.

### A12. Procedural coupling: generator output â†” import-linter contract

- **Example:** The generator at `skills/bmad_create_specialist/scripts/generate.py` validates that emitted `app/specialists/<name>/graph.py` imports `resume_from_verdict` from `app.gates.resume_api` (line 220â€“223 of generate.py). But the generator does NOT auto-update `pyproject.toml`'s import-linter Contract C3 `ignore_imports` list. Every Slab-2+ specialist migration must MANUALLY add `app.specialists.<name>.graph -> app.gates.resume_api` to the ignore list, or import-linter C3 breaks at T2 lint-imports run. With 13 Slab-2b inheritors queued, this is a 14-instance flakiness vector if any dev agent forgets.
- **Counter-pattern:** **RESOLVED at Slab 2a Story 2a.5 (path b shipped 2026-04-25 commit `0a02fa5`).** The generator now auto-emits the C3 `ignore_imports` row atomically alongside the 9-file specialist tree; manual edit no longer required. The historical context below is retained for the anti-pattern's discovery slab + procedural-coupling category illustration. This is **procedural coupling** â€” different category from drift. Two valid resolutions were identified: (a) status quo with documentation (the operator-facing checklist in `langgraph-migration-guide.md Â§12.4` named the manual step) until (b) landed; or (b) extend the generator to atomically append the ignore_imports row with a generated-comment marker. Path (b) was filed as a 2a.1 follow-on defect in `_bmad-output/planning-artifacts/deferred-inventory.md` and is now closed by Story 2a.5.
- **Slab-of-discovery:** Slab 2a Story 2a.2 T2 dev-agent discovery (party-mode 2026-04-24 ratified).

## Inherited from primary repo's `dev-agent-anti-patterns.md`

Migration-relevant subset â€” the full primary-repo catalog at
[`dev-agent-anti-patterns.md`](dev-agent-anti-patterns.md) covers the broader
non-migration contexts. Items below are the ones Slab 2+ migration specialists
will repeatedly hit.

### A4. Silent mutation (G6 MF-1/2/3 on 31-1)

- **Example:** Construct a Pydantic model with validators, then mutate a field
  via attribute assignment. Validators don't re-run.
- **Counter-pattern:** every model that can be mutated has
  `model_config = ConfigDict(validate_assignment=True)`. No exceptions.
- **Slab-of-discovery:** Primary repo Story 31-1 (inherited).

### A5. Naive datetime from `datetime.utcnow()` (G6 MF-4 on 31-1)

- **Example:** `datetime.utcnow()` returns a tz-naive datetime. Deprecated in
  Python 3.12. Passing it to a model with a tz-aware field silently creates drift.
- **Counter-pattern:** `datetime.now(tz=UTC)` always. Add a `field_validator`
  that rejects naive datetimes on every timestamp field. Helper:
  `app.models.state._base.enforce_tz_aware`.
- **Slab-of-discovery:** Primary repo Story 31-1 (inherited).

### A6. Closed enum with only one rejection surface (G5 Murat on 31-1)

- **Example:** Closed-enum field has a Pydantic `Literal[...]` validator but no
  JSON Schema `enum` array check and no `TypeAdapter` round-trip test. External
  jsonschema validators accept values Pydantic would reject.
- **Counter-pattern:** Three-layer rejection per the Pydantic-v2 checklist Â§4.
  `OperatorVerdict.verb` is the reference implementation: `Literal[...]` +
  `model_validator` enforcing no-tamper + schema-pin test asserting JSON Schema
  enum array exact match.
- **Slab-of-discovery:** Primary repo Story 31-1 (inherited).

### A7. K-floor becomes K-ceiling-multiplier

- **Example:** The K test-floor in the story plan is treated as a starting
  minimum and the dev agent pads to 4-6Ã— it. Large parametrized matrices expand
  cases but don't buy new correctness.
- **Counter-pattern:** Target 1.2-1.5Ã— K. Stop when the acceptance matrix is
  closed. Consolidate related parametrized cases into one test function rather
  than splitting across files. See
  [`story-cycle-efficiency.md`](story-cycle-efficiency.md).
- **Slab-of-discovery:** Primary repo Story 31-1 (inherited).

### A8. Mocking the thing you're testing (recurring from 27-0, 27-1, 27-2)

- **Example:** Mocking the retrieval adapter in a test of the adapter ABC. Or
  mocking the file system in a test of a file-writer. The mock hides the
  behavior you need to verify.
- **Counter-pattern:** Use real adapters or real temp files. If the real thing
  is expensive, use fixtures with committed canned output. `tmp_path` is your
  friend.
- **Slab-of-discovery:** Primary repo Epic 27 (inherited).

## How to add an entry

Open a sibling Markdown edit in the same PR that hits the anti-pattern in the
wild. Use the four-field shape:

```markdown
### A<next-ordinal>. <short name>

- **Example:** <the concrete situation that burned someone>
- **Counter-pattern:** <what to do instead; cite the memory / validator / idiom>
- **Slab-of-discovery:** <slab + story where it first surfaced>
```

Do NOT re-author the catalog per story. Do NOT drift the four-field shape. If a
story's anti-pattern doesn't fit the four-field shape, that's a catalog-evolution
signal â€” escalate to party-mode before extending the shape.

## Related

- Primary-repo inheritance source:
  [`dev-agent-anti-patterns.md`](dev-agent-anti-patterns.md)
- Pydantic-v2 idiom checklist:
  [`pydantic-v2-schema-checklist.md`](pydantic-v2-schema-checklist.md)
- Story-cycle efficiency rules (K-floor / gate-mode):
  [`story-cycle-efficiency.md`](story-cycle-efficiency.md)
- Sandbox-AC validator:
  [`../../scripts/utilities/validate_migration_story_sandbox_acs.py`](../../scripts/utilities/validate_migration_story_sandbox_acs.py)


### A13. Loose-typing accumulation across multi-specialist migration

- **Example:** Slab 2b per-specialist wave added multiple dict[str, Any] | None return-shape fields across specialist states before strict dispatch contracts were centralized.
- **Counter-pattern:** Allow temporary loose typing only with a named hardening story and explicit close-time conversion to typed dispatch models plus registry-backed invariants.
- **Slab-of-discovery:** Slab 2b Story 2b.15 (resolved during cross-cutting contract hardening).

### A14. Acceptance criteria drafted against unverified substrate

- **Example:** Story 2c.3 originally referenced a non-existent `15-invariant-audit-matrix.md` artifact, forcing corrective deferral to Slab 5a and a `slab-2c-wondercraft-invariant-stub.md` bridge. Story 2c.2 also made an initial strict receipt-key claim against `WandaDispatchReceipt.wanda_audio` even though the runtime type is loose `dict[str, Any] | None`.
- **Counter-pattern:** During T1, verify every referenced runtime path, artifact path, schema field, and receipt shape against the live tree before writing executable ACs. If the substrate does not exist yet, either narrow the AC to a stub/seed artifact or file the missing substrate as a predecessor story.
- **Slab-of-discovery:** Slab 2c Stories 2c.2 and 2c.3; accepted at Story 2c.4 harvest gate by Mary/Murat/Amelia consensus.

---

## Post-Cycle Harvest

The Slab 1+2+3+4+5a harvest cycle annotation above froze the *retrospective scope* of cycle-by-cycle harvest. Genuinely-new defects discovered post-cycle are filed below per the harvest-gate principle that post-vote discoveries are the most valuable anti-pattern source. Format-freeze v1 (the four-field shape) is preserved.

### A15. Plausible-Token Substrate Contamination

- **Example:** The cost-engineering substrate (Slab 1 model-selection policy, Slab 2a/2b specialist scaffolding, Slab 5a cost-engineering foundation) was seeded with fictitious OpenAI model identifiers (`gpt-5.4`, `gpt-5.4-nano`, `gpt-5.5`, `gpt-5-haiku`, `gpt-5-codex`). None matched OpenAI's real catalog. The fictitious tokens propagated via the scaffold templates (`app/specialists/_scaffold/model_config.yaml` + `skills/bmad-create-specialist/templates/model_config.yaml.template`) so every generated specialist inherited them. They survived the M5 6-agent SHIP-CONDITIONAL verdict, the 15-invariant audit matrix, and the 5a.3 cost-engineering close because the tokens parse, lint, and type-check cleanly — and no test ever called the OpenAI API to verify the IDs were real. First trial run would have 404'd on every specialist call.
- **Counter-pattern:** Any string in shipped config that names an external provider's resource (model ID, capability name, endpoint slug, region code) must be verified against a vendored catalog snapshot at test time. Maintain the snapshot in `tests/fixtures/<provider>_catalog_snapshot.json`; refresh on operator-gated cadence (~quarterly). The lint guard at `tests/test_no_fictitious_model_ids.py` plus the catalog-membership test at `tests/integration/runtime/test_cascade_ids_in_openai_published_catalog.py` together implement the denylist + allowlist for OpenAI. Add at least one live-provider smoke test gated behind `pytest -m live` (see `tests/live/test_openai_cascade_tiers_smoke.py`) so referent validity closes the loop end-to-end. Future M-gate audits should add a "Referent-Validity Audit" step (Mary harvest-gate proposal accepted in 2026-04-26 party-mode round 1).
- **Slab-of-discovery:** Post-Slab-5a operator session 2026-04-26 (this entry). **Slab-of-origin:** Slab 1 model-selection policy + Slab 2a/2b scaffold template propagation. The slab-of-origin/slab-of-discovery split is itself load-bearing — substrate defects can survive multiple multi-agent reviews when the verification criteria audit *internal shape* without ever testing *external referent validity*.

### A16. Composition-vs-Component Audit Gap

- **Example:** The migration's M5 6-agent SHIP-CONDITIONAL vote and 15-invariant audit matrix verified each substrate component's correctness in isolation: Marcus SPOT, sanctum cold-read, manifest deterministic neck, HIL paused, frozen graph, lane separation, learning events, ledger side-effect, etc. — all PRESERVED. But no audit step exercised the components' *composition* end-to-end. The result: TWO substrate gaps surfaced post-vote in the same week, both same defect class — **(a)** Plausible-Token Substrate Contamination (A15: fictitious external referents survived because internal shape was audited but external referent validity was not), and **(b)** missing production-graph-runner (the manifest compiler still produces `_passthrough_node` handlers; `runtime/graphs/v42/` has metadata but no invokable graph; HIL gate pause/resume not wired for live trials; no production TrialEnvelope schema distinct from M3 deterministic envelope; the live OpenAI invocation path exists in `app/models/adapter.py` but no orchestration code composes it end-to-end). The 15-invariant matrix passed because each invariant proved in isolation; nobody tested whether the composition actually runs. Codex's investigation report at `_bmad-output/implementation-artifacts/production-graph-investigation-2026-04-27.md` characterized the gap precisely; reframed via party-mode round 2026-04-27 (Winston + Murat + Quinn-R unanimous GREEN-WITH-CONCERNS) as Slab 6 opener `migration-6-1-production-graph-runner.md` rather than Slab 5a closure rider.
- **Counter-pattern:** Substrate audits MUST include at least one **integration-exercise AC** alongside per-component invariant checks. Component-level verification proves "each piece is correct"; integration-exercise verification proves "they compose into a thing that runs." For the LangGraph runtime specifically: at least one end-to-end test that compiles the manifest into a real `StateGraph`, dispatches at least one specialist node through the dispatch registry to a real LLM call (gated behind `pytest -m live` if cost-bearing), pauses at a HIL gate, accepts an `OperatorVerdict`, and resumes to completion. For future M-gate audits: add a "Composition-Exercise Audit" step alongside the existing "Referent-Validity Audit" (A15 counter-pattern) so both internal shape AND external referent validity AND end-to-end composition are required dimensions, not just first one.
- **Slab-of-discovery:** Post-Slab-5a operator session 2026-04-27 (this entry, the day after A15). **Slab-of-origin:** Slab structure proved layer-by-layer correctness without requiring composition validation; M3 deterministic harness *looked like* a production runner so masked the gap; dispatch-registry promotion was governance-not-consumption (the manifest compiler doesn't actually consume the registry); 5a.2 head-to-head parity compared *artifact outputs* not *execution paths*. The pattern across Slabs 1-5a is "substrate audit verifies internal correctness; composition validation is treated as an operator-presence trial deferred to as late as possible." That deferral is what allowed A15 + A16 to survive multi-agent multi-slab review. Pre-Slab-6 governance gate per Quinn-R round-2027-04-27 ratification: no future MVP/slab vote proceeds without an explicit integration-exercise AC, not just per-component invariant checks.

### A17. Substrate Designed for Isolation, Composition Assumed

- **Example:** When Codex attempted the strict-AC implementation of Slab 6.1 production-graph runner (closing the A16 instance flagged by bmad-code-review of the first attempt), they discovered that the migration's specialist substrate is *structurally hostile to composition*: (a) every specialist's 9-node scaffold has its OWN internal `gate_decision` interrupt that fires before the production-level G1 gate ever fires (the first Texas specialist's gate_decision halted the LangGraph execution with `model_resolution_trail length 0, snapshot next=('02',)`, never reaching G1); (b) the scaffold's two-phase shape (`make_chat_model(...)` lives in `_plan` while `_act` consumes the resolution trail and does tool/envelope work) doesn't map to "single LangGraph node executes specialist work" — composed execution requires multi-node-per-specialist orchestration; (c) the shared `RunState.cache_state.cache_prefix` carrier is OVERWRITTEN per-specialist with specialist-specific JSON, NOT accumulated as a production envelope, so downstream specialists fail (e.g., `CdDirectiveParseError: cd directive cannot be empty`) because upstream specialist output isn't visible in the carrier they were designed to consume. The 14 specialists were built assuming ISOLATED per-specialist execution (the M3 deterministic harness pattern: one specialist at a time, with deterministic state injection between them). They were NOT built assuming composition into a single executing LangGraph that flows production envelope state through them in sequence. The M5 SHIP-CONDITIONAL verdict + bounded-MVP SHIP reframe + Slab 6.1 opener spec all implicitly assumed composition was an implementation-distance away. Codex's strict-AC halt revealed it's a substrate gap — the contracts themselves don't admit composition.
- **Counter-pattern:** Every multi-component contract MUST declare a *composition mode* alongside its isolated mode at design time, with at least one composition fixture before the contract freezes. Specifically, any cross-component carrier (state keys, gate-decision scope, phase-boundary semantics) must be auditable for accumulation-vs-overwrite semantics under composition, not just under isolated execution. **Composition Contract Audit** before any MVP-shape vote: enumerate the cross-component carriers, prove at least one upstream→downstream handoff round-trips on real components, and gate the MVP vote on composition-fixture pass. For the LangGraph runtime specifically: introduce a production envelope state-key (alongside per-specialist scratch carriers) that downstream specialists read from as their canonical input source; design the composition adapter at the runner layer (Path A-prime per 2026-04-27 5-agent party-mode); preserve specialist contracts so each specialist can ALSO run in isolation (M3 harness path stays valid). For other runtimes: equivalent discipline at the relevant composition boundary.
- **Slab-of-discovery:** Post-Slab-5a operator session 2026-04-27 (this entry; same day as A16, distinct defect class). **Slab-of-origin:** Slab 2a/2b specialist scaffolding established the 9-node pattern for isolated execution; never validated under composition. **Distinction from A16:** A16 is "we didn't audit composition." A17 is "the substrate doesn't ADMIT composition" — different defect class, different counter-pattern. A16's counter is auditing harder; A17's counter is admitting the substrate must be redesigned. Conflating them weakens both. Mary harvest-gate authority on naming (per 2026-04-27 round); Murat's alternate name "Contract-Shape Composition Hostility" yields to Mary. Filed under Post-Cycle Harvest subheading; format-freeze v1 preserved (A1-A16 entries unchanged).

---

## Process Anti-Patterns (NEW subheading; 2026-04-27)

The above A1-A17 entries cover *substrate* and *implementation* anti-patterns — defects in code or system design. The entries below cover *process* anti-patterns — defects in governance / gate-process discipline that allow substrate or implementation defects to ship. Filed at 2026-04-27 per Mary harvest-gate authority + Quinn-R 5-agent-party-mode-round process-change recommendation. Format-freeze v1 same four-field shape; numbered P1+ to distinguish from A1+ codebase-anti-patterns.

### P1. (Reserved for future)

(Placeholder; first instance discovered will populate.)

### P2. (Reserved for future)

(Placeholder; first instance discovered will populate.)

### P3. Composition-Shape Vote Without End-to-End Exercise

- **Example:** The migration's M5 SHIP-CONDITIONAL vote (2026-04-26) was reached without any end-to-end composition exercise of the production-graph runner. Subsequent investigation (Codex Phase A 2026-04-27 + Slab 6.1 first-attempt bmad-code-review + Slab 6.1 strict-AC HALT) revealed the runner did not exist as a composed-and-invokable artifact at vote time. The 6-agent party-mode read the spec + the per-component invariant matrix + the trial-replay regression suite + the cost-engineering foundation + the head-to-head control-plane parity — all proved internal correctness — and ratified SHIP-CONDITIONAL on a composition assumption never exercised. This is a process defect distinct from the substrate defect (A17): even if the substrate had cleanly admitted composition, the *vote* itself proceeded without testing that assumption. Five A16 instances + the A17 substrate finding all trace to this single process gap: composition was always assumed implementation-distance away, never exercised before votes.
- **Counter-pattern:** Before any composition-shape MVP/SHIP-CONDITIONAL vote, run ONE real upstream→downstream pair through the proposed substrate end-to-end. The pair MUST be real components (not stubs, not mocks of the composition boundary), not isolated per-component pass-through. The exercise output joins the vote evidence base; if the exercise fails, the vote either (a) RE-SCOPES to bounded-MVP scope that excludes the composition claim, (b) DEFERS until the composition substrate exists, OR (c) GREENs explicitly as a composition-shape vote with the substrate gap named in the conditional-window list. Operationalize via Quinn-R "Composition Smoke" gate added to the slab-opener template: a 30-line throwaway that wires components together end-to-end before the slab spec is ratified. Failing the smoke is not a slab-blocker; it's a vote-evidence-base requirement.
- **Slab-of-discovery:** Post-Slab-5a operator session 2026-04-27 (this entry). **Slab-of-origin:** governance template; the slab-opener template did not require composition-exercise AC at vote time. Pre-Slab-6 governance amendment per Quinn-R 2026-04-27 ratification: slab-opener template gains "Composition Smoke" required step.
