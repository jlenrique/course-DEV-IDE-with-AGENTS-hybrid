# Slab 1 Story-Set A — Shared T1 Context Bundle

**Authored:** 2026-04-22 via party-mode standing-team authoring pass.
**Scope:** 8 stories — 1.1c, 1.1d (NEW), 1.2, 1.3, 1.4, 1.5, 1.6, 1.7. All 8 stories reference this bundle at their T1 readiness step instead of re-listing identical architecture/PRD/governance reading sets. Per-story Dev Notes only need to call out story-specific anti-patterns, scaffold pointers, and AC-level decisions that diverge from the bundle.

**Authoring rationale:** Stories 1.1a and 1.1b each individually re-derived the same T1 reading set, which is one of the root causes of the slow-pace concern raised by the operator on 2026-04-22. Authoring 8 stories with one shared T1 bundle is the cheapest way to amortize T1 context cost across the set without losing per-story rigor.

---

## §0a Set-Level Amendments Applied 2026-04-22 (post green-light review)

The set-level party-mode green-light review surfaced two blockers and 14 in-spec amendments. All were applied 2026-04-22 per operator disposition ("honor architecture and add 1.1a microfix"). Resolutions:

- **BLOCKER-1 — Architecture-vs-epics drift on `OperatorVerdict` substrate.** Honored architecture §D3 Slab-1 distribution. `OperatorVerdict` Pydantic added as 8th model in **Story 1.2**. `app/gates/resume_api.py` signature stub + import-linter Contract C3 + ledger verdict-event shape stub added to **Story 1.4** (AC-1.4-E1). Epics §3.3 still owns the runtime wiring (resume path, full bridge modules) — Slab 1 ships substrate only.
- **BLOCKER-2 — `mcp` SDK absent from `requirements.lock`.** **Story 1.1a re-opened** for a micro-fix adding `mcp` to the install list (10th dep) + relock; closes back to `done` after import-smoke green. The "nine-package locked starting palette" wording in architecture is amended to "ten-package palette as of 2026-04-22 micro-fix."
- **In-spec amendments applied across 1.1c, 1.1d, 1.2, 1.4, 1.5, 1.6, 1.7** + governance JSON Pts/K bumps for 1.2/1.3/1.7. See per-story Dev Notes for the explicit "Amendment 2026-04-22" entries.

## §0 Set-A Dependency Graph + Execution Order

```
1.1a-microfix (mcp dep) ── 1.1c ── 1.1d
       │                     │
       │                     ├── 1.2 (incl. OperatorVerdict) ── 1.3 ── 1.4 (incl. resume_api stub + C3) ── 1.6 ── 1.7
       │                     │
       │                     └── 1.5  (parallel-eligible after 1.1b)
       │
       └── (1.1a + 1.1b were done; 1.1a re-opened only for mcp dep micro-fix)
```

**Authoring order:** parallel — all 8 specs landed in one pass; amendments applied 2026-04-22.
**Dev-execution order:** 1.1a-microfix FIRST (adds `mcp` to lockfile so 1.1c can import it), then strict serial 1.1c → 1.2 → 1.3 → 1.4 → 1.6 → 1.7, with 1.1d immediately after 1.1c (consumes 1.1c's MCP code substrate) and 1.5 slotted parallel any time after 1.1b (touches checkpoint/Postgres only, no upstream code dep).

**Slab 1 close gate:** all 8 stories `done` per `sprint-status.yaml`; 1.1d transport-parity test green; M1 acceptance evidence pack assembled per architecture §M1 evidence checklist.

---

## §1 Architecture — Decisions Loaded for All Set-A Stories

Source: [`architecture-langchain-langgraph-migration.md`](architecture-langchain-langgraph-migration.md). Read these decision sections at T1; per-story specs cite specific decision IDs that touch their AC.

| Decision | Title | Set-A stories that touch it |
|---|---|---|
| D1 | Sanctum Snapshot Strategy (hybrid: inline OR content-hash) | 1.2 (state base classes incl. SanctumFingerprint); 1.4 (compiler reads sanctum) |
| D2 | Three-Level Model-Cascade Code Location + Override Flow | 1.3 (selector + adapter); 1.4 (compiler validation); 1.6 (registry use in stub manifest) |
| D3 | HIL Invariant Tamper-Evidence (`app/gates/**` scheduler-forbidden + `OperatorVerdict` tamper-evidence + `resume_api` import-linter contract C3) | 1.2 (`OperatorVerdict` Pydantic model — 8th model in 1.2's set per 2026-04-22 BLOCKER resolution); 1.4 (`app/gates/resume_api.py` stub + Contract C3 + ledger verdict-event shape stub + compile-time scheduler-import enforcement) |
| D4 | Cora ⊥ Marcus Lane Separation | 1.4 (compiler instantiates separate StateGraphs by lane) |
| D5 | Sanctum Cold-Read Discipline + Cache-Prefix Stability | 1.2 (CacheState model); not deeply exercised until Slab 2 |
| D6 | Manifest-as-Graph-Config Loader | 1.4 (loader + compiler); 1.6 (manifest migration) |
| D7 | Operator-Surface Contract — Three-Transport Parity (MCP+FastAPI+CLI) | 1.1c (MCP code substrate + FastAPI runtime); 1.1d (MCP smoke + parity); 1.7 (docs surface) |
| D8 | Frozen-Graph-Version Ceremony | 1.1c (runtime_server reads frozen-graph dir; minimal); full at Slab 4 |
| D9 | Milestone Evidence Bullets | 1.7 (docs roll-up); applies cross-set |
| D10 | Slab 2 Sub-Structure (2a/2b/2c) | not directly; Slab 1 close opens Slab 2 |
| D11 | Slab 5 Split (5a/5b) | not directly |
| D12 | Cross-Slab Governance Artifact Ownership Protocol | 1.7 closing-story commit message follows D12's three-line protocol |
| D13 | Model-Registry Mid-Migration Bump Procedure | 1.3 (registry shape); 1.6 (registry referenced in stub manifest) |

**Amendment F** (single→triple-story split for Slab 1 kickoff) — already applied; 1.1a/1.1b done; 1.1c is the third leg, with 1.1d added as a sibling per 2026-04-22 middle-path consensus.

**Amendment E** (LangGraph State Idioms doc) — Slab 1 deliverable; lands in 1.7. State models authored in 1.2 must follow the six idioms documented there (and previewed below in §3).

**Amendment G** (Sanctum CLONE-FORK-NOTICE) — already shipped in 1.1b.

**Amendment H** (Survey-and-Discard) — historical (architecture authoring); no live impact on Set-A.

**Amendment I** (LangGraph idiom sanity check throwaway) — Slab 1 deliverable as throwaway docs only; 1.7 owns it if we author it.

---

## §2 PRD — Functional + Non-Functional Requirements Loaded for All Set-A Stories

Source: [`prd-langchain-langgraph-migration.md`](prd-langchain-langgraph-migration.md). The Set-A stories collectively close FR coverage on the FRs below — read all of them at T1.

### Runtime platform FRs (set-A primary scope)

- **FR1** persistent runtime → 1.1c (`app/runtime/server.py` boots)
- **FR2** operator-surface contract — MCP + FastAPI + CLI compound contract → 1.1c (FastAPI runtime + MCP code substrate); 1.1d (MCP smoke + FastAPI↔MCP parity); 3.4 (verdict parity, Slab 3)
- **FR3** Postgres checkpointing → 1.1b (init SQL); 1.5 (retention + cleanup)
- **FR4** thread-pause survival ≥48hr → indirectly via 1.5 (retention)
- **FR5** checkpoint cleanup → 1.5
- **FR6** LangSmith tracing — 100% trace coverage at single-operator volume → 1.1c (LangSmith span-tag contract); 1.3 (resolution-trail spans)
- **FR7** trace-per-node with span tag set `{trial_id, node_id, agent, lane}` → 1.1c
- **FR8** manifest-as-graph-config topology → 1.4 (loader + compiler); 1.6 (real manifest migrated)
- **FR17–FR21** three-level model-selection cascade (per-call → per-specialist → registry default; auto-select policy) → 1.3
- **FR22–FR23** model-resolution trail in every LLM span; cache-prefix stability → 1.3 (resolution trail in adapter)
- **FR24** runtime model-override + cache-invalidation warning — pre-submission portion only in Slab 1 → 1.3 stub; full closure at Slab 3 Story 3.5
- **FR25** model_config.yaml lint-at-compile → 1.4 (compiler validation pass)
- **FR54** baseline measurement (token-cost) → measurement scaffolding only in 1.7
- **FR58** LangSmith tracing substrate → 1.1c
- **FR59** sanctum invalidation hook stub → 1.7 (stub only; full at Slab 4 Story 4.6)
- **FR60** forward-port freeze policy commit → activated at 1.1a `done` (already in effect on this branch)

### Non-functional requirements (set-A scope)

- **NFR-S1** API-key secret management (`.env` discipline + `!.env.example` negation) → already shipped in 1.1a; reaffirmed at every story that adds env vars
- **NFR-S2** FastAPI 127.0.0.1-only bind → 1.1c
- **NFR-M2** model_config.yaml lint at compile-time → 1.4
- **NFR-M3** four-tier test strategy → already scaffolded in 1.1b; per-story tests respect tier placement
- **NFR-M4** K-floor 1.2–1.5× discipline → per-story K target tracked in `migration-story-governance.json`
- **NFR-M5** Pydantic four-file lockstep (model + validator + tests + golden fixture) → 1.2, 1.3, 1.4, 1.6 (all schema-shape stories)
- **NFR-M6** living anti-patterns catalog → 1.7 stub
- **NFR-M7** migration guide kept current → 1.7 skeleton
- **NFR-X1–X5** reproducibility — byte-for-byte replay; frozen graph versions; sanctum snapshot; model selections + auto-select fallback trail; documented temperature variance → state models in 1.2 must encode all five; compiler in 1.4 enforces frozen-graph-version load
- **NFR-O4** resolution-trail spans → 1.3
- **NFR-P3** checkpoint ≤500ms → measured in 1.5

---

## §3 Pydantic v2 + LangGraph State Idioms — 14 Idioms + 6 Idioms

**Authoritative sources:**
- [`docs/dev-guide/pydantic-v2-schema-checklist.md`](../../docs/dev-guide/pydantic-v2-schema-checklist.md) — 14 idioms (G6 MUST-FIX harvest from primary repo)
- [`docs/dev-guide/scaffolds/schema-story/`](../../docs/dev-guide/scaffolds/schema-story/) — pre-instantiated schema-story scaffold; **stories 1.2, 1.3, 1.4, 1.6 must use this scaffold** rather than re-derive Pydantic shape from scratch
- [`docs/dev-guide/dev-agent-anti-patterns.md`](../../docs/dev-guide/dev-agent-anti-patterns.md) — anti-pattern catalog
- [`docs/dev-guide/story-cycle-efficiency.md`](../../docs/dev-guide/story-cycle-efficiency.md) — K-floor + gate-mode policy

### Pydantic v2 — 14 idioms (load all at T1 for 1.2/1.3/1.4/1.6)

1. `model_config = ConfigDict(validate_assignment=True, extra="forbid")` (unless permissive bag with named justification)
2. Timezone-aware datetimes via `datetime.now(UTC)` or `Annotated[datetime, AfterValidator(_require_tz_aware)]`
3. UUID4 for identity fields: `uuid_field: UUID = Field(default_factory=uuid4)`
4. Closed enums via `Literal[...]` over `Enum` where possible
5. Triple-layer red-rejection on closed enums (field-level + model-validator + schema-pin test)
6. `Field(exclude=True, json_schema_extra={"SkipJsonSchema": True})` for audit-only fields
7. Frozen identity: `model_config = ConfigDict(frozen=True)` for value objects
8. Cross-field validators: `@model_validator(mode="after")`
9. `Field(default_factory=...)` for mutable defaults (never bare `[]` or `{}`)
10. `model_dump(by_alias=True, exclude_none=True)` for stable serialization
11. JSON Schema emission shape-pin tests (golden fixture per model)
12. Round-trip equivalence test (`m == Model.model_validate(m.model_dump())`)
13. Forbidden-field rejection test (extra fields raise ValidationError)
14. Discriminated unions where shape varies (`Field(discriminator='kind')`)

### LangGraph state idioms — 6 idioms (load at T1 for 1.2/1.4)

1. **Graph state is Pydantic `BaseModel`, NOT `TypedDict`** — PRD mandate; even though LangGraph docs push TypedDict
2. Reducer fields via `Annotated[list, operator.add]` — when needed; `Field(default_factory=list)` interaction
3. `Command(goto=..., update=...)` return types — shape, when to `goto` vs `update`
4. `Send()` fan-out payloads — Pydantic-serializable payload requirement
5. `interrupt()` checkpoint payloads — UUID4 + timezone-aware datetime discipline carries over
6. `RetryPolicy` + Pydantic interaction — placeholder until Slab 4 Story 4.7 (known gap; do NOT silently work around)

---

## §4 Sandbox-AC Discipline (apply to every Set-A story)

Source: [`docs/dev-guide/migration-ac-sandbox-inventory.json`](../../docs/dev-guide/migration-ac-sandbox-inventory.json) + [`scripts/utilities/validate_migration_story_sandbox_acs.py`](../../scripts/utilities/validate_migration_story_sandbox_acs.py).

**Rule:** every dev-agent AC must verify via shipped Python deps, not operator-side CLIs.

**Already-burned blockers** (do not repeat in Set-A):
- **Docker / docker-compose** — removed from architecture 2026-04-22; native Postgres only
- **psql** — operator CLI; use `psycopg` + `pytest.skip(...)` when `DATABASE_URL` unreachable

**Forbidden CLIs in dev-agent ACs:** `docker`, `docker-compose`, `psql`, `pg_dump`, `pg_ctl`, `aws`, `gcloud`, `az`, `gh`, `kubectl`, `helm`, `redis-cli`, `mongo`, `mongosh`, `mysql`, `curl`, `wget`. Use the shipped Python equivalents: `psycopg`, `boto3`, `PyGithub`, `httpx`, etc. If a live-CLI smoke check is genuinely needed (e.g., operator-machine evidence), split the AC into AC-X-A (dev-agent-executable, skip-on-unreachable) + AC-X-B (operator-gated, Completion-Notes paste).

**Run the validator** at story `ready-for-dev` AND at `bmad-dev-story` open per CLAUDE.md migration governance section. Batch all 8 specs at once for the set.

---

## §5 Gate Mode + K-Floor — Frozen per Story

Source: [`docs/dev-guide/migration-story-governance.json`](../../docs/dev-guide/migration-story-governance.json) (version 2026-04-22).

| Story | Gate | K target | Rationale |
|---|---|---|---|
| 1.1c | single | ~1.5× | substrate-bootstrap + MCP code; smoke kept narrow |
| 1.1d | single | ~1.5× (1.2–1.8) | MCP transport smoke + parity; not schema/lane/invariant |
| 1.2 | dual | ~1.5× | schema-shape — RunState/StoryState/Specialist*/SanctumFingerprint/CacheState/NodeCheckpoint |
| 1.3 | dual | ~1.4× | schema-shape — PipelineRegistry + ModelSelectionPolicy |
| 1.4 | dual | ~1.5× | schema-shape (PipelineManifest) + compile-time topology contract |
| 1.5 | single | ~1.3× | additive operational policy; no schema |
| 1.6 | dual | ~1.4× | manifest schema change for the migrated v4.2 manifest |
| 1.7 | single | ~1.3× | docs + scaffold-conformance framework + anti-pattern stub; no schema |

**Do not relitigate gate mode at story-authoring time.** Reading the JSON IS the decision.

---

## §6 Cross-Story Anti-Patterns Harvested from 1.1a + 1.1b

Slab 1's first two stories surfaced two preventable failure modes. Every Set-A story spec must encode the avoidance.

1. **Operator-CLI assumption in dev-agent AC.** Caused 1.1b to block twice (Docker AC, psql AC). Fix: sandbox-AC validator + the `verify-via-shipped-deps` rule encoded in §4. Memory: [feedback_verify_via_shipped_deps](../../../.claude/projects/c--Users-juanl-Documents-GitHub-course-DEV-IDE-with-AGENTS-hybrid/memory/feedback_verify_via_shipped_deps.md).
2. **Architecture-decision relitigation at story-author time.** Spent two party-mode rounds re-deciding MCP-in-Slab-1 mid-set authoring. Fix: gate mode + scope decisions live in the JSON governance file; story author reads, doesn't re-derive. Architecture amendments require party-mode + version bump in the architecture doc, not a story-spec override.
3. **K-floor framing hazard for substrate-bootstrap stories.** 1.1a flagged that the K-floor framework doesn't fit cleanly when a story creates zero pytest nodes (substrate-bootstrap pattern). Set-A stories that face this should explicitly note "substrate-bootstrap K framing — verification signals counted as command-equivalence checks, not pytest nodes" in Dev Notes rather than fudge the K count.

---

## §7 Per-Story Dev-Spec Stub Shape (use this as starting template)

Each Set-A story file should have:

1. **Header:** title + Status + sprint key + epic + milestone + position in set
2. **Story:** As-a / I-want / So-that
3. **Acceptance Criteria:** Given/When/Then blocks per AC; mark `(dev-agent-executable)` or `(operator-gated)` per sandbox-AC discipline
4. **Tasks / Subtasks:** T1 reading (cite this bundle by section, not by re-listing) → T2-N implementation → final commit
5. **Dev Notes:** ONLY story-specific anti-patterns, scaffold pointers, and AC-level decisions that diverge from this bundle
6. **References:** point to bundle §X for shared context; per-story sources for anything not in bundle
7. **Dev Agent Record:** model used + debug log + completion notes + file list + change log + review findings (placeholder for dev fill-in)

**Aim:** per-story spec under ~250 lines (vs. 1.1a/1.1b's 200-225 lines each, which had ~80 lines of repeated T1 context that this bundle now centralizes).

---

## §8 MIDDLE-PATH Consensus Origin (preserve for forensic value)

The 1.1c / 1.1d split came from a two-round party-mode consensus on 2026-04-22:

- **Round 1:** 2 IN Slab 1 (Winston, Mary) vs 3 DEFER to Slab 2 (Amelia, Murat, Paige). No consensus.
- **Round 2:** Orchestrator proposed MIDDLE PATH (MCP code in Slab 1, smoke split). 5/5 agents endorsed after pivot evidence:
  - Amelia: `mcp` PyPI SDK matured past Epic 27's hand-rolled era; subprocess round-trip ~40-60 LOC, not 150-250
  - Murat: real subprocess + same minimal LangGraph node behind both transports = byte-equivalent parity assertion is falsifiable, not fake-of-fake
  - Paige: inverted transport-parity matrix (3 columns × 3 rows: code/smoke/parity) reads as visible roadmap, not gap
  - Winston: substrate claim preserved (D7+FR2 honored) without per-PR flake vector
  - Mary: FR2 compound contract is about substrate presence + reachability at M1, not per-PR coverage; D7 didn't adjudicate per-PR-vs-milestone smoke cadence

**Why this matters for Set-A authoring:** when 1.1c and 1.1d specs reference each other ("shared minimal LangGraph node," "transport-parity envelope exceptions table"), the dev agent must understand the consensus logic to avoid re-litigating at implementation time. Treat the consensus as a decision-of-record equivalent to an architecture amendment; cite this §8 when the dev agent asks "why is the MCP code in 1.1c but the smoke in 1.1d?"

---

## §9 Closeout Hygiene (Slab 1 close, after all 8 stories `done`)

Per CLAUDE.md migration governance + sprint governance:

1. Update `_bmad-output/implementation-artifacts/sprint-status.yaml` first (each story to `done`; epic to `done` when last story closes)
2. Update `next-session-start-here.md` second
3. Compile M1 acceptance evidence pack per architecture §M1 evidence checklist; 1.1d transport-parity test green is part of it
4. `bmad-retrospective` skill on Epic 1 close per CLAUDE.md §Deferred inventory governance — review `deferred-inventory.md` against new Slab 1 substrate
5. Slab 1 closing-story (1.7) commit message follows D12 three-line protocol citing FR60 freeze status, sanctum-fork notice baseline, and frozen-graph v42 directory state

---

## §10 Forward Pointers (Set-A → downstream slabs)

Items deliberately staged for downstream slabs; do NOT pull into Set-A:

- **Slab 2 specialist scaffold migrations** (Epic 2a/2b/2c) — depends on Set-A close + 1.7's scaffold-conformance framework
- **Slab 3 Marcus orchestration** (Epic 3) — depends on 1.4 compiler + 1.1c FastAPI + 1.1d MCP parity baseline; 3.4 three-transport verdict parity inherits 1.1d's two-transport baseline + adds CLI leg
- **Slab 4 graph-compile-time CI hook** (Story 4.1) — Set-A's compiler in 1.4 is the substrate; CI promotion is Slab 4
- **Slab 4 Cora dev-graph** (Story 4.2) — separate StateGraph compilation; relies on 1.4 compiler shape supporting two graphs
- **Slab 4 frozen-graph ceremony** (Story 4.5) — Set-A creates the directory + minimal contents; Slab 4 codifies the ceremony
- **Slab 4 RetryPolicy + Pydantic workaround** (Story 4.7) — 1.2 must NOT silently work around the known gap; flag explicitly as "Slab 4 deliverable" per LangGraph state idiom #6

---

**This bundle is the single source of truth for Set-A T1 context. Per-story specs reference this file by §-pointer; if a story-spec contradicts the bundle, the bundle wins. Bundle revisions require party-mode amendment (no quiet drift).**
