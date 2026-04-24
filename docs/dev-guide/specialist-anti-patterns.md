# Specialist Anti-Patterns Catalog

Living catalog of anti-patterns harvested across Slab-1 closure + inherited
from the primary repo's `docs/dev-guide/dev-agent-anti-patterns.md`. Every
Slab 2+ story's dev-agent reads this at T1.

**Four-field format** (per Paige 2026-04-22 amendment): each entry must carry
`name`, `example`, `counter-pattern`, `slab-of-discovery`. Shape frozen —
entries added in Slab 2+ stories preserve the four fields exactly.

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
