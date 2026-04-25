# Specialist Anti-Patterns Catalog

Living catalog of anti-patterns harvested across Slab-1 closure + inherited
from the primary repo's `docs/dev-guide/dev-agent-anti-patterns.md`. Every
Slab 2+ story's dev-agent reads this at T1.

> **You-are-here** (Slab 2+ dev-agent reading order at T1):
> 1. [`scaffold-conformance-framework.md`](scaffold-conformance-framework.md) — 9-node canonical contract + T1 pre-flight
> 2. [`langgraph-state-idioms.md`](langgraph-state-idioms.md) — state-shape idioms (interrupt, Command, Send, reducers)
> 3. [`model-selection-guide.md`](model-selection-guide.md) — three-level cascade
> 4. **This catalog** — known traps (read before writing ACs)

## Format (frozen — changes require party-mode consensus)

**Four-field format** (frozen at Paige 2026-04-22 amendment; version-controlled below):
each entry carries EXACTLY these four fields — `name` / `example` / `counter-pattern` /
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
  architecture doc for decision-of-record D1–D13). The story author reads the JSON
  rather than re-derives. Amendments require party-mode consensus + version bump
  in the architecture doc, not a story-spec override. Origin of the middle-path
  consensus chain that 1.1c drifted from:
  [`_bmad-output/planning-artifacts/slab1-story-set-A-t1-bundle.md §8`](../../_bmad-output/planning-artifacts/slab1-story-set-A-t1-bundle.md).
- **Slab-of-discovery:** Slab 1 Story 1.1c authoring pass.

### A3. Architecture-vs-epics drift uncaught at story-author time

- **Example:** Architecture §D3 placed `OperatorVerdict` substrate + Contract C3
  in Slab 1; epics §3.3 had drifted to Slab 3. Set-A authoring (2026-04-22)
  initially missed the drift — the sandbox-AC validator + gate-mode JSON check
  didn't catch it because it was a scope drift between architecture decisions and
  epics decomposition, not a per-story issue. Mary surfaced the drift at
  set-level party-mode review, adding BLOCKER-1 to the set-level amendments and
  pulling the substrate into Stories 1.2 (`OperatorVerdict`) + 1.4 (`resume_api`
  stub + Contract C3).
- **Counter-pattern:** cross-reference architecture decision-of-record (D1–D13)
  against epics decomposition during **set-level** T1 readiness, not only at
  per-story gate-mode lookup. If a set-level review surfaces architecture-vs-epics
  drift, escalate BEFORE individual stories open (BLOCKER-level amendment, not
  silent extension of one story).
- **Slab-of-discovery:** Slab 1 set-A authoring (2026-04-22 set-level review).

### A9. Epic-doc node-name drift from Slab-1-hardened framework

- **Example:** Epic 2a Story 2a.1 line 555 uses node names `plan/enter_sanctum/load_expertise/reason/act/validate/emit/return/exit_sanctum`; Slab-1-hardened `scaffold_contract.py::SCAFFOLD_NODE_IDS` uses `receive/plan/act/verify/reflect/emit_spans/gate_decision/finalize/handoff`. The sets do not map.
- **Example (Story 2a.2 second instance):** Epic 2a.2 lines 584–585 use node names `reason/act/validate/emit/return` — same drift pattern, different story. Per Paige harvest-gate rule (party-mode 2026-04-24), duplicate patterns augment existing entries rather than creating new ones.
- **Counter-pattern:** Read `tests/integration/scaffold_conformance/scaffold_contract.py::SCAFFOLD_NODE_IDS` as the authoritative node-name contract and treat epic prose as potentially stale. If drift appears, flag it in T1 readiness and harvest it as an anti-pattern before story close.
- **Slab-of-discovery:** Slab 2a Story 2a.1; second example confirmed at Story 2a.2.

### A10. Epic-doc model-ID + tier drift from shipped registry

- **Example:** Epic 2a.2 lines 587–589 say "Irene uses model tier 'long-context balanced'... default resolves to `gpt-4.1`". The shipped registry at `app/models/registry.yaml` has entries `gpt-5.4 / gpt-5-haiku / gpt-5-codex` (NO `gpt-4.1`); `app/models/selection_policy.yaml` has tiers `reasoning / fast / code` (NO "long-context balanced"). The drift is config-cascade-value staleness (distinct from A9's node-name-list staleness).
- **Counter-pattern:** Read `app/models/registry.yaml` + `app/models/selection_policy.yaml` as the authoritative model-cascade contract. Map specialist workloads to the live `tier_request` enum (`reasoning / fast / code`); resolution flows through the cascade. Document the mapping rationale in the specialist's `model_config.yaml` inline comments. Cross-check against `docs/dev-guide/model-selection-guide.md`.
- **Slab-of-discovery:** Slab 2a Story 2a.2.

### A11. Epic-doc sanctum-path drift from hybrid BMB migration convention

- **Example:** Epic 2a.2 line 581 says "`_bmad/memory/bmad-agent-irene/` sanctum symlink present". The actual hybrid path is `_bmad/memory/bmad-agent-content-creator/` — the convention follows the operator-facing skill-dir name, not the app-side specialist short name. Per CLAUDE.md §Custom-agents and Epic-26 BMB-sanctum-migration, hybrid uses **direct directory** (NOT symlink). The drift is persona-tree-migration staleness (distinct from A9 node names + A10 model IDs).
- **Counter-pattern:** Read `docs/dev-guide/sanctum-reference-conventions.md §1` as the authoritative path convention. Cross-reference each specialist's `app/specialists/<name>/expertise/README.md` for the dotted-reference idiom. If epic prose names a different sanctum path, follow the framework + harvest the drift.
- **Slab-of-discovery:** Slab 2a Story 2a.2.

### A12. Procedural coupling: generator output ↔ import-linter contract

- **Example:** The generator at `skills/bmad_create_specialist/scripts/generate.py` validates that emitted `app/specialists/<name>/graph.py` imports `resume_from_verdict` from `app.gates.resume_api` (line 220–223 of generate.py). But the generator does NOT auto-update `pyproject.toml`'s import-linter Contract C3 `ignore_imports` list. Every Slab-2+ specialist migration must MANUALLY add `app.specialists.<name>.graph -> app.gates.resume_api` to the ignore list, or import-linter C3 breaks at T2 lint-imports run. With 13 Slab-2b inheritors queued, this is a 14-instance flakiness vector if any dev agent forgets.
- **Counter-pattern:** This is **procedural coupling** — different category from drift. Two valid resolutions: (a) status quo with documentation (the operator-facing checklist in `langgraph-migration-guide.md §12.4` names the manual step) until (b) lands; or (b) extend the generator to atomically append the ignore_imports row with a generated-comment marker. Path (b) is filed as a 2a.1 follow-on defect in `_bmad-output/planning-artifacts/deferred-inventory.md` §Named-But-Not-Filed Follow-Ons, blocking Slab-2b.1 TEMPLATE open. Until path (b) lands, the manual step in §12.4 is the canonical countermeasure.
- **Slab-of-discovery:** Slab 2a Story 2a.2 T2 dev-agent discovery (party-mode 2026-04-24 ratified).

## Inherited from primary repo's `dev-agent-anti-patterns.md`

Migration-relevant subset — the full primary-repo catalog at
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
- **Counter-pattern:** Three-layer rejection per the Pydantic-v2 checklist §4.
  `OperatorVerdict.verb` is the reference implementation: `Literal[...]` +
  `model_validator` enforcing no-tamper + schema-pin test asserting JSON Schema
  enum array exact match.
- **Slab-of-discovery:** Primary repo Story 31-1 (inherited).

### A7. K-floor becomes K-ceiling-multiplier

- **Example:** The K test-floor in the story plan is treated as a starting
  minimum and the dev agent pads to 4-6× it. Large parametrized matrices expand
  cases but don't buy new correctness.
- **Counter-pattern:** Target 1.2-1.5× K. Stop when the acceptance matrix is
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
signal — escalate to party-mode before extending the shape.

## Related

- Primary-repo inheritance source:
  [`dev-agent-anti-patterns.md`](dev-agent-anti-patterns.md)
- Pydantic-v2 idiom checklist:
  [`pydantic-v2-schema-checklist.md`](pydantic-v2-schema-checklist.md)
- Story-cycle efficiency rules (K-floor / gate-mode):
  [`story-cycle-efficiency.md`](story-cycle-efficiency.md)
- Sandbox-AC validator:
  [`../../scripts/utilities/validate_migration_story_sandbox_acs.py`](../../scripts/utilities/validate_migration_story_sandbox_acs.py)
