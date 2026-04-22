---
stepsCompleted: [1, 2, 3, 4, 5, 6]
inputDocuments: []
workflowType: 'research'
lastStep: 6
research_type: 'technical'
research_topic: 'LangChain + LangGraph migration for BMAD-orchestrated production pipeline'
research_goals: 'Plan step-by-step migration that optimally balances probabilistic intelligence (agents) with deterministic behavior — maximizing model use, token efficiency, speed, flexibility, quality, reliability — while preserving Marcus-first orchestration, Pipeline Lockstep regime, party-mode/code-review gates, deferred-inventory governance, Lesson-Planner schema-shape discipline, and BMAD sprint governance'
user_name: 'Juanl'
date: '2026-04-21'
web_research_enabled: true
source_verification: true
---

# Research Report: Technical

**Date:** 2026-04-21
**Author:** Juanl
**Research Type:** Technical

---

## Research Overview

This document is the technical research substrate for migrating the **course-DEV-IDE-with-AGENTS** APP — a 15-step Marcus-orchestrated production pipeline with 17 specialist agents, a Pipeline Lockstep regime, and full Lesson-Planner schema-shape discipline — onto a **LangChain + LangGraph hybrid runtime**. The research deliberately balances **probabilistic intelligence** (specialist subgraphs with rich LLM reasoning surface) against **deterministic behavior** (manifest-driven pipeline spine, schema-validated boundaries, gate-as-`interrupt()` operator authority) across six optimization axes: model use, token efficiency, speed, flexibility, quality, reliability.

The investigation produced **five foundational decisions** (Stage-2 runtime independence as architectural target; bounded big-bang migration in the clone with primary repo as frozen reference; reject-the-LangChain-cage operating principles; HIL operator + Marcus-as-SPOT preserved; specialist scaffold + sanctum-pattern as plug-and-play architecture); **twelve architectural patterns** mapped 1:1 onto substrate-digest invariants; a **five-slab implementation recipe** with concrete acceptance criteria; and a **fully resolved technology stack** (self-hosted OSS LangGraph + Pydantic v2 + `langgraph-checkpoint-postgres` + `AnthropicPromptCachingMiddleware` + MCP-as-bridge + LangSmith). The full **executive summary, strategic impact assessment, and recommended next BMAD step** are in the §Comprehensive Synthesis section at the end of this document.

---

<!-- Content will be appended sequentially through research workflow steps -->

## Technical Research Scope Confirmation

**Research Topic:** LangChain + LangGraph migration for BMAD-orchestrated production pipeline

**Research Goals:** Plan a step-by-step migration that optimally balances probabilistic intelligence (agents) with deterministic behavior — maximizing model use, token efficiency, speed, flexibility, quality, reliability — while preserving Marcus-first orchestration, Pipeline Lockstep regime, party-mode/code-review gates, deferred-inventory governance, Lesson-Planner schema-shape discipline, and BMAD sprint governance.

**Optimization Axes (every option evaluated against these):**

1. Model use (Opus/Sonnet/Haiku routing per node)
2. Token efficiency (context budget, prompt caching, structured output vs tool calls, summarization checkpoints)
3. Speed (latency, parallelism, streaming)
4. Flexibility (node swap, human-in-loop insertion, replay/resume)
5. Quality (gate integration, schema validation, multi-agent review preservation)
6. Reliability (checkpointing, idempotency, error recovery, observability)

**Hard Constraints (preserved, not open questions):**

- Marcus-first orchestration semantics + specialist delegation model
- Pipeline Lockstep regime + block-mode trigger paths
- Party-mode and code-review gates before story `done`
- Deferred-inventory governance
- Lesson-Planner MVP Pydantic-v2 schema-shape discipline
- Story-cycle K-floor rules and BMAD sprint governance

**Technical Research Scope:**

- Architecture Analysis — design patterns, frameworks, system architecture
- Implementation Approaches — development methodologies, coding patterns
- Technology Stack — languages, frameworks, tools, platforms
- Integration Patterns — APIs, protocols, interoperability
- Performance Considerations — scalability, optimization, patterns

**Research Methodology:**

- Current web data with rigorous source verification
- Multi-source validation for critical technical claims
- Confidence level framework for uncertain information
- Comprehensive technical coverage with architecture-specific insights
- Explicit mapping back to the six optimization axes on every option

**Scope Confirmed:** 2026-04-21

---

## Technology Stack Analysis

> *Note on adapted structure*: The standard template's database / cloud-platform sub-sections are not load-bearing here — LangChain/LangGraph is a Python library that runs on any infrastructure. The sub-sections below are adapted to what actually matters for this migration: the runtime, state model, persistence, model integration, and observability stack.

### Core Runtime — LangGraph (Graph) + LangChain (Components)

LangGraph is the production graph runtime; LangChain provides the component library (chat models, tools, prompts, output parsers, runnables). For agent systems beyond a single-LLM call, the LangGraph team's own framing is: **use the graph runtime, pull in LangChain components only as needed**.

- **`StateGraph`** is the foundational primitive: typed state schema → nodes (Python callables) → edges (deterministic, conditional, or `Send` for fan-out). The graph runtime is what makes this production-viable — it provides the structured execution engine with checkpointing and human-in-the-loop support that an ad-hoc `for`-loop over LLM calls cannot match. _Source: [Workflows and agents — LangChain docs](https://docs.langchain.com/oss/python/langgraph/workflows-agents), [LangGraph product page](https://www.langchain.com/langgraph)_
- **Multi-agent topologies** are first-class. LangGraph supports both **supervisor** (centralized orchestrator routes to specialist workers via conditional edges; an official helper exists at `langgraph-supervisor-py`) and **swarm** (decentralized handoffs between peer agents) natively through `StateGraph`. LangChain's 2025 State of AI Agents report measured 57% of enterprise AI deployments using multi-agent architectures. _Source: [langgraph-supervisor-py (GitHub)](https://github.com/langchain-ai/langgraph-supervisor-py), [Supervisor vs Swarm tradeoffs (DEV)](https://dev.to/focused_dot_io/multi-agent-orchestration-in-langgraph-supervisor-vs-swarm-tradeoffs-and-architecture-1b7e), [Databricks: Supervisor architecture at scale](https://www.databricks.com/blog/multi-agent-supervisor-architecture-orchestrating-enterprise-ai-scale)_

**Mapping to existing project**: Marcus → supervisor node; specialists (Irene, Gary, Vera, Texas, Kira, etc.) → worker subgraphs reachable via conditional edges keyed off Marcus's routing decision. The `specialist-registry.yaml` becomes the source-of-truth for the supervisor's edge dispatch table. *Confidence: high — direct pattern match.*

### State Schema — Pydantic v2 (with caveats)

LangGraph state schema can be a `TypedDict`, a Pydantic v2 `BaseModel`, or a `dataclass`. For your repo, **Pydantic v2 is the correct choice** because the Lesson-Planner MVP discipline already mandates it (`validate_assignment=True`, triple-layer red-rejection, UUID4 validation, etc.) and Pydantic schemas give per-node-entry runtime validation.

- **How it works**: When state schema is a Pydantic `BaseModel`, every node receives an instance of the model as its first arg, and validation runs before each node executes. _Source: [Pydantic Base Model as State](https://www.baihezi.com/mirrors/langgraph/how-tos/state-model/index.html), [Use the graph API](https://docs.langchain.com/oss/python/langgraph/use-graph-api), [TypedDict vs Pydantic in LangGraph](https://shazaali.substack.com/p/type-safety-in-langgraph-when-to)_
- **Known edge cases (must design around)**:
  1. Generic types in `BaseModel` state schemas have a documented validation bug — `Field` validation does not fire correctly when generics are involved. _Source: [Issue #4060](https://github.com/langchain-ai/langgraph/issues/4060)_
  2. Pydantic schema validation does not apply to **output** schemas, only input/per-node entry. _Source: [Issue #1977](https://github.com/langchain-ai/langgraph/issues/1977), [Issue #1978](https://github.com/langchain-ai/langgraph/issues/1978)_

**Mapping to existing project**: The pydantic-v2-schema-checklist already in [`docs/dev-guide/pydantic-v2-schema-checklist.md`](docs/dev-guide/pydantic-v2-schema-checklist.md) maps near-1:1 onto LangGraph state design. The "no generics in state schema root" rule becomes a hard discipline; output validation must be enforced **inside nodes** (explicit `model.model_validate()` on emitted state mutations) rather than relying on graph-level output validation. *Confidence: high on the bug; medium on workaround durability — bugs may be fixed in newer LangGraph releases.*

### Persistence & Checkpointing — Tiered by Environment

LangGraph's checkpointer abstraction is what gives you durability, replay, time-travel, and human-in-loop interrupts. Three production-relevant tiers:

| Tier | Backend | Use for | Package |
|---|---|---|---|
| Dev | `MemorySaver` (in-memory) | Local single-shot testing only | `langgraph` (built-in) |
| Light prod / single-node | `SqliteSaver` | Per-developer local sanctum runs, single-host deployments | [`langgraph-checkpoint-sqlite`](https://pypi.org/project/langgraph-checkpoint-sqlite/) |
| Production | `PostgresSaver` | Multi-host, multi-tenant, observable | [`langgraph-checkpoint-postgres`](https://pypi.org/project/langgraph-checkpoint-postgres/) |

**Critical setup gotchas** (2026 best practices):
- For Postgres first-time use, call `.setup()` to create required tables.
- When manually creating Postgres connections, set `autocommit=True` and `row_factory=dict_row`.
- **Each superstep creates a checkpoint** → long-running graphs (your APP runs are long) generate substantial storage volume. Implement a checkpoint cleanup policy from day 1.
- State must be JSON-serializable. The default `JsonPlusSerializer` uses ormsgpack with fallback to extended JSON that handles LangChain/LangGraph types, datetimes, enums.
- For sensitive data, `EncryptedSerializer` is available.
- One of the most powerful production features: **list checkpoints + replay from any prior state** — invaluable for debugging, and a natural fit for your trial-run / pin-actual-commit-hashes discipline.

_Sources: [Mastering LangGraph Checkpointing — 2025](https://sparkco.ai/blog/mastering-langgraph-checkpointing-best-practices-for-2025), [Persistence — LangChain docs](https://docs.langchain.com/oss/python/langgraph/persistence), [LangGraph v0.2 release notes](https://www.langchain.com/blog/langgraph-v0-2)_

**Mapping to existing project**: Checkpointer-as-thread maps cleanly to "per-trial-run state snapshot." Replay capability subsumes part of what Marcus currently does manually with `next-session-start-here.md` continuity. The trial-run / pin-actual-commit-hashes discipline can be reframed as: **commit hash + LangGraph thread_id + checkpoint_id** is the new triple that uniquely identifies "where Marcus is." *Confidence: high.*

### Model Integration — Anthropic (Opus / Sonnet / Haiku) with Prompt Caching

`langchain-anthropic` provides `ChatAnthropic` plus the **`AnthropicPromptCachingMiddleware`** — the latter is the lever that directly attacks your token-efficiency optimization axis.

- **What the middleware does**: automatically injects `cache_control` headers on messages for Anthropic chat models, enabling Claude's prompt caching feature without per-call manual annotation. Reported impact (LangChain announcement): up to **80% latency reduction and 90% cost reduction** on prompts with long static prefixes — exactly the shape of agent-system-prompt-heavy workloads like yours. _Sources: [AnthropicPromptCachingMiddleware reference](https://reference.langchain.com/python/langchain-anthropic/middleware/prompt_caching/AnthropicPromptCachingMiddleware), [Anthropic middleware integration docs](https://docs.langchain.com/oss/python/integrations/middleware/anthropic), [LangChain announcement](https://x.com/LangChainAI/status/1823756691739164840), [Prompt caching — Claude API docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)_
- **Configuration knobs**: cache type (`ephemeral`), TTL (`5m` or `1h`), `min_messages_to_cache` threshold, behavior for unsupported models. Caches are isolated per API key.
- **2026 platform change to track**: Starting **2026-02-05**, prompt caching uses **workspace-level isolation** instead of organization-level on the Claude API and Azure AI Foundry — relevant if you ever multi-tenant the system.
- **Open issue worth watching**: Bedrock Anthropic prompt caching (`cache_control`) support inside `create_agent` system prompt is tracked at [Issue #33635](https://github.com/langchain-ai/langchain/issues/33635) — only matters if you'd ever route through Bedrock; not blocking direct Anthropic API.

**Mapping to existing project**: Marcus's persistent persona/sanctum content + specialist activation prompts are exactly the kind of long static prefix that benefits most from prompt caching. **Recommended pattern**: each specialist subgraph gets its own ChatAnthropic instance with the middleware enabled, and the specialist's persona/sanctum content lives in the cached prefix region. Token savings here are likely the single largest economic lever in the migration. *Confidence: high on the mechanism; medium on the magnitude until measured against your actual sanctum sizes.*

### Observability — LangSmith (or self-hosted alt)

LangSmith is the first-party tracing/observability surface; it integrates natively with LangGraph and surfaces per-node inputs/outputs/timings/tokens, plus supports replays. For a brownfield project with strong governance discipline (party-mode reviews, code-review gates, retrospectives), LangSmith traces become the **evidentiary substrate** for those gates — reviewers look at traces, not just diffs.

*Confidence on the importance: high. Confidence on LangSmith vs alternatives (Langfuse, Arize Phoenix, Helicone): medium — full comparative deferred to Step 3 (integration patterns) or Step 5 (implementation research) if you want it.*

### Technology Adoption Trends (2026 context)

- Multi-agent supervisor pattern is the **dominant production pattern** as of LangChain's 2025 State of AI Agents (57% of enterprise deployments).
- LangGraph v0.2+ shipped expanded checkpointer libraries (Postgres + SQLite as separate packages) — signals the framework is hardening for production durability rather than chasing surface features.
- Prompt caching middleware has moved from "advanced optimization" to "default-on" in 2026 reference docs — your migration should treat it as table-stakes, not an optimization phase.

_Sources: [LangGraph v0.2 release notes](https://www.langchain.com/blog/langgraph-v0-2), [LangGraph: Build Stateful Multi-Agent Systems (mager.co, 2026-03)](https://www.mager.co/blog/2026-03-12-langgraph-deep-dive/), [LangGraph + MCP 2026 guide](https://techbytes.app/posts/langgraph-mcp-multi-agent-workflow-guide-2026/)_

---

### Optimization-Axis Mapping (Stack-Layer)

| Axis | Stack lever |
|---|---|
| Model use | `ChatAnthropic` per-node — different model class per node tier (Opus for Marcus orchestration, Sonnet for specialist reasoning, Haiku for deterministic glue/extraction) |
| Token efficiency | `AnthropicPromptCachingMiddleware` on every long-prefix node; Pydantic state schema → smaller serialized state vs free-text |
| Speed | LangGraph `Send` for parallel specialist fan-out; streaming via `astream_events` |
| Flexibility | Subgraphs per specialist → swap implementations without touching graph topology |
| Quality | Pydantic v2 state validation per-node-entry; LangSmith trace as gate evidence |
| Reliability | `PostgresSaver` checkpointing + replay; `EncryptedSerializer` for sensitive sanctum data |

---

## Migration Strategy Decisions (foundational — locked 2026-04-21)

> *These three decisions were made during Step 2 review and shape what is worth researching in Steps 3–5. They are inputs to the PRD, not open questions.*

### Decision 1 — Runtime independence is the architectural target, reached in stages

The IDE will not stay the runtime host. The end-state is **LangGraph runtime as a long-lived process; IDE as a client** (Stage 2 in the stage model below). Production deployment (Stage 3) is optional and downstream of Stage 2.

| Stage | Runtime location | IDE role | Independence |
|---|---|---|---|
| 0 | IDE conversation | Host + dev surface | None — closes with IDE |
| 1 | Subprocess invoked from IDE | Host | Per-invocation — reproducible from CLI/CI |
| 2 | **Persistent local service** (FastAPI/LangServe or `langgraph dev`) backed by `PostgresSaver` | **Client only** | **Full** — survives IDE close, replayable across sessions |
| 3 | Remote deployment | Client | Production-grade |

Because we are choosing **bounded big-bang** (Decision 2 below), Stage 1 is **skipped as a transitional shape**. Slab 1 lands directly into a Stage-2-shaped runtime so we don't pay a refactor tax later.

### Decision 2 — Bounded big-bang migration in the clone, not incremental per-specialist

The primary repo at the original location continues as the **frozen production reference** for the duration of the migration. The clone (this repo, branch `dev/langchain-langgraph-foundation`) diverges aggressively. We accept that the clone's APP will be **broken end-to-end for weeks** during migration.

**Why this beats incremental:** with a working primary repo as fallback, the costs of incremental migration (bridging code, two-way merge tax, premature design commitments, holding two architectures in head simultaneously) exceed its safety value.

**Migration in architectural slabs**, not feature-by-feature:

| Slab | Scope | "Done" criterion |
|---|---|---|
| 1 | Substrate: state schema base, `PostgresSaver`, `AnthropicPromptCachingMiddleware`, LangSmith, persistent runtime shell (Stage 2 shape) | Empty graph runs end-to-end, checkpointed, observable |
| 2 | All specialists migrated as LangGraph subgraphs (parallel work — they all break together, return together) | Each specialist runnable in isolation against contract tests |
| 3 | Marcus supervisor + routing graph | End-to-end APP run completes (may be lower-quality than primary) |
| 4 | Pipeline Lockstep equivalents + party-mode/code-review gate hooks + governance | Block-mode triggers + gate evidence working in LangGraph world |
| 5 | Trial-run discipline, replay UX, observability polish | Parity with primary repo's production capability |

**Backport policy:** primary→clone backports stop at slab 1 start. Valuable primary-repo improvements made during migration become **forward-ports later** — re-implemented as LangGraph-native versions after slab 5, not merged into a half-migrated tree.

### Decision 3 — Preserve agent intelligence; reject the "LangChain cage" anti-pattern

> *Operator caveat, 2026-04-21:* "We do want to maximize agent intelligence and flexibility in the end — not overly locking in or becoming overly deterministic in a LangChain cage."

LangGraph's structural power can become a structural cage: every decision becomes a deterministic conditional edge, every state field becomes a schema-validated trap, every LLM call becomes tool-calling boilerplate that strips reasoning. The migration's #1 quality risk is **trading agent intelligence for graph determinism**. This is rejected as an architectural principle.

**Operating rules to keep agents intelligent:**

- **Probabilistic-first node design.** A node's default shape is "rich LLM reasoning surface, optionally returning structured state." Tool-calling and rigid structured output are *opt-in per node*, never the default. If a node could be done well by an LLM with a long context, it is not a deterministic node.
- **Routing edges decide *which agent runs next*, not *what the agent will think*.** Conditional edges are dispatch logic, not constraint logic. Agent reasoning happens *inside* the destination node, not *between* nodes.
- **Schema is a boundary, not a corset.** Pydantic state is enforced at slab boundaries (between specialist subgraphs, at the supervisor's input/output) but specialist subgraphs internally are free to use loose `dict`/text-rich working state. Over-typing internal state is a known intelligence-killer.
- **Long context over compression where it pays.** Sanctum content, persona, prior turns — keep them in the cached prefix region rather than aggressively summarizing into structured state. Prompt caching makes "more context" cheap; summarization makes it lossy. Default to the former.
- **Specialists are subgraphs, not tools.** A specialist is a sub-`StateGraph` with its own internal reasoning loop, not a single function-call node. This preserves the kind of multi-turn, self-correcting work specialists already do today (Vera's quality reviews, Irene's grounding passes, Marcus's orchestration deliberation).
- **Deterministic glue stays narrow.** Deterministic nodes exist for: I/O (file reads, retrieval calls), schema validation at boundaries, idempotent gate checks, and Pipeline Lockstep enforcement. Anything that smells like "decision" or "judgment" is an LLM node, not a Python `if`.
- **Model tier follows reasoning depth, not node type.** Opus for orchestration and complex reasoning; Sonnet for specialist work that benefits from long-context-with-judgment; Haiku reserved for genuinely deterministic glue (extraction, validation, format conversion). The default is Sonnet/Opus, not Haiku — token efficiency is achieved via prompt caching, not via downgrading the model.
- **Replay/checkpoint enables exploration, not just recovery.** The reliability infrastructure (`PostgresSaver` + replay) should be used to let agents *try things and roll back* — supporting more probabilistic exploration, not less.

**Anti-pattern watchlist (call out in code review, dismiss with cause if introduced):**
- A specialist implemented as `tool_calling_agent(tools=[...])` with no reasoning surface
- A conditional edge whose router function contains domain logic the LLM should be making
- A Pydantic state model with 30+ fields where the LLM "fills in the blanks"
- Aggressive summarization of conversation history when prompt caching would handle it
- Haiku used for any decision; Sonnet/Opus reserved only for "hard" cases

### Decision 3a — HIL operator + Marcus-as-SPOT is the durable interaction shape (refinement, 2026-04-21)

The operator-in-the-loop role at every gate is **indispensable and preserved**. Marcus remains the **Single Point of Truth (SPOT)** through which the operator directs all production work — not because Marcus is a bottleneck, but because SPOT is the contract that lets a complex APP (many contracts, gates, validations, structural path enforcements) stay coherent under operator-driven flexibility.

**What changes over time, what does not:**

| Aspect | Now | Migration target | Long-term direction |
|---|---|---|---|
| Operator decisions at gates | Required | **Required (unchanged)** | **Required (unchanged)** |
| Operator must re-read context to decide at each gate | Largely manual | Reduced via gate-payload curation (interrupt presents the *minimum decisive context*, not raw state) | Aggressively minimized — gate payload becomes a tight decision card with one-click drill-down to traces/checkpoints |
| Marcus as SPOT for production direction | Yes | **Yes (unchanged)** | **Yes (unchanged)** |
| Operator → Marcus prompt feeding burden | Heavy (manual re-context per turn) | Reduced via cached persona + checkpointed thread state | Minimized via thread-resume + smart context summaries the operator can accept/edit |

**Operating rules added to Decision 3:**

- **Gate payload curation** — every `interrupt()` produces a curated decision card (proposed action + minimum decisive context + drill-down links to LangSmith trace and checkpoint), not raw state dump. Reducing operator cognitive load at gates is a first-class quality goal, not a polish item.
- **SPOT routing is preserved** — operator instructions enter through Marcus only; specialists never receive direct operator instructions. The supervisor-only-routing topology enforces this.
- **Flexibility within structure** — operator can edit any agent proposal at any gate (`{"type": "edit"}` interrupt response), can request alternative paths, can override block-mode triggers with documented exception. The graph encodes the structure; the operator retains directorial authority.
- **No autonomous bypass of operator** — even if a gate could be auto-approved by policy, the migration explicitly preserves the option for operator review. Auto-approve is opt-in per gate, off by default.

### Decision 4 — Specialist Scaffold as Plug-and-Play Architecture (added 2026-04-21)

**Why this is a foundational decision, not an implementation detail:**

The substrate digest counted **17 active specialists today**, plus stubs the operator named for near-term plug-and-play (**Wondercraft** podcast generation, **Canvas** site manipulation, **Qualtrics** survey generation, and others to follow). Without a uniform specialist scaffold:
- Each new specialist re-derives architecture from a precedent (the same 27-2/31-1 anti-pattern that motivated the existing schema-story scaffold)
- Debugging becomes specialist-by-specialist tribal knowledge
- Quality varies (some specialists self-assess, some don't; some emit receipts, some don't)
- Migration cost stays high indefinitely instead of dropping to "fill in the blanks"

The migration's #1 leverage point for long-term velocity is **a single specialist scaffold that all 17 existing specialists re-implement against during slab 2, and every future specialist instantiates from**. The schema-story scaffold pattern at [`docs/dev-guide/scaffolds/schema-story/`](docs/dev-guide/scaffolds/schema-story/) is the proven template — Decision 4 applies the same discipline to a new artifact family: **specialist subgraphs**.

#### The Specialist Scaffold — Subgraph Skeleton (9 named nodes, default behaviors)

Every specialist is a `StateGraph` subgraph with this canonical topology. Specialists subset/no-op nodes they don't need; they cannot rename or reorder them.

| # | Node | Default behavior | Per-specialist override |
|---|---|---|---|
| 1 | `envelope_intake` | Pydantic-v2 validate Marcus envelope; reject malformed; populate working state | Add specialist-specific envelope subclass (e.g., `WondercraftEnvelope` adds `episode_arc`, `voice_palette`) |
| 2 | `cold_load` | Read persona + skill + references FRESH per invocation (Sacred-Truth pattern); cache only at prompt-cache layer | Specify which reference files to load |
| 3 | `reason` | Free-text LLM reasoning (Sonnet default; Opus on `regulated` preset; Haiku banned for reasoning per Decision 3) with prompt-caching middleware on persona/refs prefix | Specialist-specific reasoning prompt; permitted tool list passed to model |
| 4 | `act` | MCP-tool dispatch (default) or direct API call (escape hatch); tools registered declaratively | Bind specialist-specific tools (Wondercraft API, Canvas API, Qualtrics API) via MCP adapter |
| 5 | `perceive` | Multi-modal perception of produced artifact via sensory bridge (image read, audio read, transcript read) | Media specialists implement; pure-data specialists no-op |
| 6 | `assess` | Self-evaluation against quality-criteria.yaml; emit advisories; compute self-confidence score | Specialist provides quality criteria YAML; assess thresholds tuned per quality_preset |
| 7 | `compose_return` | Build typed `SpecialistReturn` payload + **curated decisive_context_for_marcus** card (per Decision 3a — minimum context Marcus needs at gate) | Specify per-specialist payload subclass; author the decisive-context template |
| 8 | `emit_receipt` | Side-effect: write SHA256-signed receipt artifact to gate-receipt path; record in learning-event ledger if applicable gate | Specify receipt schema (extends base `SpecialistReceipt`) |
| 9 | `interrupt_for_operator` *(optional)* | Specialist-initiated HIL — only fires if `assess` confidence below auto-return threshold OR specialist needs decisive operator input mid-task | Specialist defines what triggers escalation and what the decision card looks like |

**Key invariants:**

- **All 9 node names are fixed across specialists.** A debugger or new specialist author looking at any specialist sees the same skeleton.
- **Nodes 1, 7, 8 are mandatory.** Envelope-in, typed-return, receipt-out — no exceptions. Even Dan (single-shot validator-clean) does all three.
- **Nodes 2–6 + 9 are optional.** A pure-deterministic specialist (e.g., a future "format_converter") may have only nodes 1, 4, 7, 8.
- **State is isolated per Decision 3** — each specialist has its own internal Pydantic state schema; envelope/return are the only boundary contracts.

#### Envelope Contract (Marcus → Specialist) — `MarcusEnvelope`

Pydantic v2 base model with required fields. Each specialist adds a subclass with specialist-specific extensions.

```
class MarcusEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    run_id: UUID4
    thread_id: str                                  # LangGraph thread for resume
    request_intent: str                             # operator's natural-language intent (preserved verbatim)
    typed_intent: SpecialistIntent                  # parsed/structured form
    context: SpecialistContext                      # specialist-relevant context excerpts (NOT full sanctum)
    quality_preset: Literal["explore","draft","production","regulated"]
    constraints: list[Constraint]                   # hard limits (budget, time, content rules)
    deadline: datetime | None                       # tz-aware
    callbacks_allowed: list[SpecialistName]         # which OTHER specialists this one may invoke (empty by default — most specialists don't)
    pipeline_step: str                              # §nn.n step that called this specialist
    gate_caller: GateName | None                    # which gate is consuming the return (drives receipt routing)
    reissue_of: UUID4 | None                        # if this is a re-attempt after operator edit/reject
```

**Why typed**: prevents Marcus from accidentally leaking operator-direct prompts to specialists (envelope strictness from substrate digest §3); makes envelope a contract that Marcus's supervisor node validates *before* dispatching.

#### Return Contract (Specialist → Marcus) — `SpecialistReturn`

```
class SpecialistReturn(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    run_id: UUID4
    specialist_id: SpecialistName
    status: Literal["success", "needs_operator", "needs_reroute", "error"]
    payload: SpecialistPayload                      # specialist-specific subclass; the actual work product references
    evidence_refs: list[EvidenceRef]                # files / receipt IDs / LangSmith trace IDs
    advisories: list[Advisory]                      # non-blocking concerns surfaced for operator awareness
    decisive_context_for_marcus: DecisionCard       # PER DECISION 3a — curated minimum context Marcus needs
    self_confidence: float                          # 0.0–1.0; below per-preset threshold → forces needs_operator
    model_calls_made: list[ModelCall]               # token accounting; cache-hit-rate tracked
    receipt_id: ReceiptID                           # ID of the SHA256-signed receipt emitted by node 8
    duration_seconds: float
```

**`DecisionCard` matters most** — it's the operationalization of Decision 3a's gate-payload-curation rule. Operator at the gate sees this card, not raw return state.

#### Quality-Preset Behavior Matrix

Single dial for operator/Marcus to select; cascades through scaffold defaults:

| Preset | Reasoning model | Validator strictness | Self-assess auto-return threshold | Token budget | Use case |
|---|---|---|---|---|---|
| `explore` | Sonnet | Lenient | 0.50 (often returns `needs_operator`) | Generous | Operator is iterating creatively |
| `draft` | Sonnet | Standard | 0.65 | Standard | Default working state |
| `production` | Opus | Strict | 0.80 | Standard, prompt-cache critical | Tracked production runs |
| `regulated` | Opus | Strictest + extra contract validators run | 0.90 (almost always operator-confirmed) | Generous | Compliance-grade work |

Quality preset is a Marcus-envelope field; Marcus selects per operator handshake (substrate digest §1 — two-axis handshake).

#### Sanctum-Based Pattern is the Assumed Working Model (post-migration target for ALL specialists)

The substrate digest noted Marcus is currently the **only specialist on the sanctum pattern** (born 2026-04-17 during Epic 26 migration). All other specialists still use the legacy BMAD layout (just `skills/bmad-agent-<name>/SKILL.md + references/`). **Per operator direction (2026-04-21): sanctum is the working model going forward; the LangGraph hybrid APP assumes every specialist is on sanctum.** This means slab 2 specialist migration is a **two-axis migration per specialist**:

- **Axis 1 — Legacy → Sanctum**: Stand up `_bmad/memory/bmad-agent-<name>/` with INDEX/PERSONA/CREED/BOND/MEMORY/CAPABILITIES per Marcus's pattern.
- **Axis 2 — IDE → LangGraph subgraph**: Stand up `runtime/graphs/specialists/<name>/` against the 9-node scaffold.

These two axes migrate **together** per specialist (one PR, one story), because the LangGraph `cold_load` node reads the sanctum — they are coupled by design, and decoupling them would create transitional shapes the bounded-big-bang strategy (Decision 2) explicitly rejects.

#### Plug-and-Play Generator — `bmad-create-specialist`

A new BMAD skill (built first in slab 2 after the scaffold itself) that lays down the full specialist file tree at known paths — **both axes simultaneously**:

```
skills/bmad-agent-<name>/                          # ───── ACTIVATION + REFERENCES ─────
  SKILL.md                                # cold-start activation per BMAD spec
  README.md                               # operator-facing one-pager
  references/
    contract.yaml                         # envelope subclass + return subclass + quality criteria
    quality-criteria.yaml                 # self-assess thresholds per preset
    tools.yaml                            # MCP tool bindings
    api-reference.md                      # service-specific API documentation (e.g., gamma-api-reference.md)
    prompt-patterns.md                    # what prompt structures work best with this service
    style-bible.md                        # domain-specific style conventions (if applicable)
    examples/
      golden-envelope.json                # canonical input
      golden-return.json                  # canonical output
      success-cases/                      # past successful invocations for few-shot prompt-caching

_bmad/memory/bmad-agent-<name>/                    # ───── SANCTUM (identity + continuity) ─────
  INDEX.md                                # sanctum batch-load order (per Marcus pattern)
  PERSONA.md                              # specialist voice / identity
  CREED.md                                # operating principles + bans (e.g., "never cache style-bible")
  BOND.md                                 # operator preferences scoped to this specialist's domain
  MEMORY.md                               # curated lessons from past invocations
  CAPABILITIES.md                         # auto-generated from references frontmatter — canonical action router
  sessions/                               # per-invocation logs, curated into MEMORY at session close

runtime/graphs/specialists/<name>/                 # ───── LANGGRAPH SUBGRAPH ─────
  __init__.py                             # subgraph instantiation against the 9-node scaffold
  state.py                                # Pydantic state schemas (envelope/return subclasses)
  nodes.py                                # node implementations (most are scaffold defaults)
  tools.py                                # MCP tool bindings (loads from references/tools.yaml)
  sanctum_loader.py                       # Sacred-Truth fresh-read of _bmad/memory/bmad-agent-<name>/

tests/specialists/<name>/
  test_envelope_contract.py               # envelope happy-path + edge cases
  test_return_contract.py                 # return happy-path + status transitions
  test_quality_presets.py                 # behavior across explore/draft/production/regulated
  test_sanctum_load.py                    # sanctum batch-load order + integrity
  test_golden.py                          # golden-input → golden-output regression
```

**Dev work to instantiate a new specialist** (target: < 1 dev-day for a stub like Wondercraft once scaffold is built):

1. Run `bmad-create-specialist <name>` (lays down the full tree above)
2. Author **PERSONA.md** (who is this specialist — short, concrete identity)
3. Author **CREED.md** (operating principles and bans specific to this specialist's domain)
4. Fill **references/api-reference.md** (the service's API surface — parameters, valid values, gotchas, rate limits)
5. Fill **references/prompt-patterns.md** (what prompt structures produce best output for this service)
6. Fill **references/tools.yaml** with MCP tool bindings (Wondercraft endpoints + auth)
7. Fill **references/quality-criteria.yaml** with self-assess thresholds
8. Add 2–4 golden examples in **references/examples/success-cases/**
9. Initialize **MEMORY.md** with seed lessons (operator's prior knowledge of the service, if any) — otherwise blank to be grown by use
10. Override scaffold node defaults ONLY where needed (most specialists won't override `envelope_intake`/`assess`/`compose_return`/`emit_receipt` — those defaults work)
11. Run `pytest tests/specialists/<name>/` → must pass including `test_sanctum_load.py`
12. Run integration test against live API (one-shot)
13. BMAD code-review (layered) → done

**Plug-and-play means**: scaffold absorbs ~80% of boilerplate; dev work is bounded and concentrated on the *expertise surfaces* (api-reference, prompt-patterns, persona/creed, golden examples) — not architecture re-derivation.

#### Specialist Expertise Stack — Where Knowledge Actually Lives (Worked Example: Gary)

The operator's question goes to the foundation: **how does Gary actually become a Gamma expert, and where is that expertise stored?** The answer is a **layered taxonomy** — expertise is distributed across distinct surfaces, each serving a different cognitive function. This taxonomy is binding for the scaffold:

| Layer | Surface | What it holds | How accessed | Mutability |
|---|---|---|---|---|
| **L0 — Background** | LLM training weights | General knowledge ("Gamma is a slide-generation service that takes a prompt and returns slides") | Implicit at every node call | Immutable per model version |
| **L1 — Identity** | Sanctum: `PERSONA.md` | Who Gary is — "slide architect, multi-turn perceiver, never authors final without QA" | `cold_load` node reads fresh per invocation | Curated at sanctum updates |
| **L2 — Principles** | Sanctum: `CREED.md` | What Gary will/won't do — "I read style-bible fresh; I never cache; I never promote final without quality assessment" | `cold_load` node | Curated at sanctum updates (rare; high stakes) |
| **L3 — Operator preferences** | Sanctum: `BOND.md` | Operator-specific preferences — "operator prefers minimal theme, 16:9, dislikes corporate aesthetic, accepts ALL CAPS in headers" | `cold_load` node | Updated when operator expresses new preference |
| **L4 — Accumulated lessons** | Sanctum: `MEMORY.md` | Curated wisdom from past invocations — "dark backgrounds + small text fail accessibility; gradient theme on data-heavy slides reads poorly" | `cold_load` node | **Grows over time** via session-curation pattern |
| **L5 — Domain knowledge** | References: `api-reference.md`, `prompt-patterns.md`, `style-bible.md` | The service's API surface (parameters, valid values, rate limits, gotchas) + prose guidance on what works | `cold_load` reads via `CAPABILITIES.md` load list | **Updated when API changes or operator clarifies style** |
| **L6 — Few-shot examples** | References: `examples/success-cases/*` | Past successful (envelope, return) pairs as in-context demonstrations | `cold_load` reads top-N most relevant for current intent | **Grows over time** when invocations succeed exceptionally well |
| **L7 — Tool surface** | MCP server schemas + `references/tools.yaml` | Typed action interface — what API calls Gary may make, with parameter types | `act` node consumes when calling tool | Updated when API contract changes |
| **L8 — Run-scoped context** | Marcus envelope: `context` + `typed_intent` | The specific request, the run's lesson plan, the source materials Gary needs THIS time | `envelope_intake` node | Per-invocation only |

**The key insight**: expertise is NOT one thing. It's a stack where:
- **L0** gives Gary the linguistic ability to *understand* what Gamma is
- **L1–L4 (sanctum)** give Gary his *identity, principles, and accumulated wisdom* — the WHO and WHY
- **L5–L7 (references + MCP)** give Gary his *domain knowledge and action surface* — the WHAT and HOW
- **L8 (envelope)** gives Gary *this specific job* — the THIS-TIME context

When Gary runs:
1. **`cold_load`** reads L1–L6 fresh (Sacred-Truth pattern). This builds his per-invocation prompt-cached prefix.
2. **`reason`** deliberates how to approach the task, drawing on all loaded layers — free-text, Sonnet/Opus.
3. **`act`** invokes Gamma via L7 (MCP tool with typed schema).
4. **`perceive`** reads back generated slides via sensory bridge.
5. **`assess`** compares output against L5 (style bible) + L4 (past lessons) + quality-criteria thresholds.
6. **`compose_return`** builds typed return + curated `DecisionCard` for Marcus.
7. **`emit_receipt`** writes signed audit artifact.

**How expertise GROWS** (this is how Gary gets better over time):
- After each invocation, the session log lands in `_bmad/memory/bmad-agent-gary/sessions/<date>.md`
- At session close (or epic retrospective), session logs are **curated into MEMORY.md** by Cora-or-equivalent — the *durable* lessons get promoted; transient state is discarded
- If a lesson is **API-level** (e.g., "Gamma's `theme=corporate` parameter actually accepts undocumented values X/Y") → it's promoted to **`references/api-reference.md`** rather than MEMORY
- If a lesson is **prompt-pattern-level** (e.g., "structuring the prompt as 'audience first, then content' produces better slides") → promoted to **`references/prompt-patterns.md`**
- If a lesson is **operator-preference-level** (e.g., "operator now prefers gradient over minimal for emotional content") → promoted to **`BOND.md`**
- If a successful invocation is **exceptionally good** → its (envelope, return) pair is added to **`references/examples/success-cases/`** as a future few-shot

This is the **expertise-curation pipeline** — and it's what makes a sanctum-based specialist *actually grow* across many invocations rather than starting fresh every time. It's also what makes Wondercraft/Canvas/Qualtrics/etc. **plug-and-play with growth potential**: they start with seed expertise (L5–L7 the operator + dev write at instantiation) and accumulate L4 (MEMORY) and L6 (success cases) through use.

**Migration implication for slab 2**:
- The `bmad-create-specialist` generator must lay down **all eight expertise surfaces** (sanctum + references + MCP wiring) for the operator/dev to fill
- The session-curation pipeline (sessions → MEMORY/references promotion) must be a first-class operational pattern, ideally automated where it's safe (Cora-or-equivalent runs it; operator approves promotions per Decision 3a)
- The 17 existing specialists' tribal knowledge — currently scattered across SKILL.md prose, operator's head, and implicit Marcus orchestration patterns — must be **explicitly captured into L4–L6 surfaces** as part of each specialist's migration. This is real work; it's also how the migration *captures and preserves* the value the operator has built.
- The Wondercraft pilot (first new specialist on the scaffold) starts with **L0 + L7 (Wondercraft API) + dev-authored L1/L2/L5** but blank L3/L4/L6 — and grows from there. Acceptance criterion is that the growth pipeline works end-to-end on the pilot.

#### Specialist Anti-Patterns Catalog (new artifact, four-file-lockstep with scaffold)

Mirroring the existing schema discipline ([dev-agent-anti-patterns.md](docs/dev-guide/dev-agent-anti-patterns.md)), a new catalog **specialist-anti-patterns.md** is born during slab 2. Every G6 finding on a specialist story lands as **one PR, four files**: specialist code + scaffold template + specialist-checklist.md + specialist-anti-patterns.md.

Initial anti-patterns to seed the catalog (derived from substrate digest):

1. **Specialist that talks to operator directly** — violates SPOT (substrate §1, §3, surprise #3)
2. **Specialist that mutates run state outside envelope/return** — violates Dan-Marcus contract pattern (substrate §2 Dan brief)
3. **Specialist that caches persona/style-bible across invocations** — violates Sacred-Truth fresh-read (substrate §1, surprise #1)
4. **Specialist that returns raw state instead of `DecisionCard`** — violates Decision 3a gate-payload curation
5. **Specialist that uses Haiku for the `reason` node** — violates Decision 3 model-tier rule
6. **Specialist with 30+ field internal state schema where LLM "fills in blanks"** — violates Decision 3 schema-as-boundary-not-corset
7. **Specialist that calls another specialist not in `callbacks_allowed`** — violates envelope contract; supervisor-only routing
8. **Specialist that emits receipt before `compose_return` validates** — violates audit trail integrity (frozen-at-ship discipline, substrate §4)

#### Migration Slab Implications

This decision **reshapes slab 2**:

- **Slab 2 first deliverable**: the specialist scaffold itself — `runtime/graphs/specialists/_scaffold/`, the `bmad-create-specialist` skill, the four-file-lockstep tooling, the contract base classes, the receipt schema, the quality-preset wiring. Until this lands, no specialist migrates.
- **Slab 2 specialist migration order** (proposed, refine in PRD): start with **2–3 specialists with the cleanest contracts** (Dan/CD, Texas, ElevenLabs) to harden the scaffold; then migrate the rest of the 17 in parallel waves; **then** instantiate the operator-named stubs (Wondercraft, Canvas, Qualtrics) using the now-proven scaffold. Stubs ship faster because the scaffold has burned in real-specialist edge cases first.
- **Slab 2 acceptance criterion**: every existing specialist runs end-to-end through the scaffold against contract tests; at least one stub specialist (Wondercraft is the natural pilot — high media-creation value, well-defined API) is instantiated and ships in slab 2 close.

#### Mapping the Six Optimization Axes to the Scaffold

| Axis | Scaffold lever |
|---|---|
| Model use | `quality_preset` → reasoning-model dial; `act` node uses Haiku for tool-call execution wrappers; `reason` is always Sonnet/Opus per Decision 3 |
| Token efficiency | `cold_load` produces stable cached prefix per specialist; `decisive_context_for_marcus` keeps gate payload tight; envelope `context` is curated excerpts not full sanctum |
| Speed | Specialists invocable in parallel via `Send` from supervisor; `assess` self-confidence avoids unnecessary operator interrupts on high-confidence work |
| Flexibility | New specialist = scaffold instantiation, not architecture re-derivation; tool surface swappable via MCP `tools.yaml` |
| Quality | Mandatory `assess` + receipt + four-file-lockstep anti-patterns catalog; Pydantic envelope/return contracts catch boundary errors |
| Reliability | Receipts SHA256-signed; checkpointer captures per-node state; replay works because all node names are fixed |

### How these decisions reshape the remaining research

- **Step 3 (Integration Patterns)**: deprioritize bridging/adapter patterns and parallel-operation patterns (irrelevant under bounded big-bang). Emphasize: structured-output-vs-tool-calling-vs-text-output trade-offs (per Decision 3), inter-subgraph communication, MCP integration as flexible tool surface, IDE↔runtime protocol options for Stage 2.
- **Step 4 (Architectural Patterns)**: the supervisor topology is locked (Marcus = supervisor). Research focus: subgraph composition patterns that preserve agent intelligence, interrupt/human-in-loop patterns for party-mode and code-review gates, error/retry patterns that don't strip reasoning.
- **Step 5 (Implementation Research)**: production-runtime patterns (Stage 2 shape), per-slab acceptance test patterns, prompt-caching activation patterns at scale, LangSmith trace-as-evidence patterns for governance gates.
- **Step 6 (Synthesis)**: produce the slab model with concrete deliverables per slab, the cage-avoidance design rules as a checklist, and the recommended next BMAD step (PRD).

---

## Integration Patterns Analysis

> *Note on adapted structure*: The standard template's REST/gRPC/AMQP/ESB/SAGA/CQRS sub-sections are not load-bearing here — this is an in-process Python graph runtime, not a microservice mesh. The sub-sections below are adapted to the integration questions that are actually load-bearing for this migration given Decisions 1–3: output modality choice (the core anti-cage lever), inter-subgraph communication, tool surface flexibility (MCP), human-in-loop interrupts (gate integration), IDE↔runtime protocol for Stage 2, and streaming.

### Output Modality Trade-offs — Structured Output vs Tool Calling vs Free-Text Reasoning

This is **the** integration decision that operationalizes Decision 3 (no LangChain cage). Three output modalities, each with a defined role:

| Modality | What it does | Use for | Cost to intelligence |
|---|---|---|---|
| **Structured output** | Forces the model to return a typed object | Routing decisions at conditional edges; cross-subgraph state hand-off; gate verdicts | High if used inside reasoning; low if used at boundaries |
| **Tool calling** | Model selects + parameterizes an action from a registered tool list | I/O actions, retrieval, deterministic side effects, MCP tool invocation | Medium — strips reasoning into discrete steps |
| **Free-text reasoning** | Model produces unconstrained natural-language reasoning | Specialist judgment, deliberation, multi-perspective analysis, deliberative orchestration | None — this is where intelligence lives |

**The principle (per Decision 3)**: free-text is the default mode inside a node; structured output appears only at *boundaries* (subgraph in/out, supervisor routing); tool calling is reserved for action selection, not reasoning. This is the architectural answer to "preserve agent intelligence" — it forces the cage to live at the seams of the graph, not inside the agents.

**Key 2026 quote that makes the case**: *"A model reasoning over a 200-step conversation history to determine its current progress is fundamentally different and worse than reading a clean, structured state object that explicitly encodes current progress, completed steps, pending actions, and intermediate findings."* — i.e., **state schema replaces reasoning ABOUT progress, but does not replace reasoning to PRODUCE progress**. Decision 3's "schema-as-boundary-not-corset" rule is the operational form of this.

The opposite anti-pattern, named in 2026 commentary: *"LangGraph provides the most control. Every transition is developer-defined. Every state mutation is explicit. Every conditional branch is a testable function."* — that's the cage. Used wrong, it converts every specialist into a deterministic function call.

_Sources: [Workflows and agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents), [LangGraph for Enterprise Agent Development (Focused Labs)](https://focused.io/lab/langgraph-enterprise-agent-development), [Tool Calling in LangChain, LangGraph, and MCP](https://dev.to/nikhil_ramank_152ca48266/-tool-calling-in-langchain-langgraph-and-mcp-three-layers-one-intelligent-system-4jf7), [Building Agents With LangGraph Part 2: Tools (SWmansion)](https://blog.swmansion.com/building-agents-with-langgraph-part-2-4-adding-tools-a7955432c220), [What LangGraph Reveals About Controlled Agent Orchestration](https://zaidalissaalmaliki.substack.com/p/unit-23-done-what-langgraph-reveals)_

### Inter-Subgraph Communication — Two Patterns, Each with a Use Case

A specialist subgraph can communicate with the parent graph (Marcus supervisor) two ways:

| Pattern | How | When to use |
|---|---|---|
| **Shared state keys** | Subgraph state schema shares keys with parent → updates flow automatically through shared channels | When the subgraph genuinely contributes to the same conceptual state (e.g., shared `messages` list, shared `artifacts` registry) |
| **Isolated state + transform-in/transform-out** | Subgraph has a different state schema; node function transforms parent → subgraph state, invokes subgraph, transforms result back | **Default for specialists** — keeps each specialist's working state private (per-specialist message history, internal scratchpads) |

**Mapping to existing project**: Each specialist subgraph (Vera, Irene, Gary, Texas, Kira, etc.) uses **isolated state by default**, per Decision 3 ("specialists are subgraphs, not tools" + "schema is a boundary, not a corset"). The supervisor → specialist transformation is the schema boundary; specialist internals are free to use loose working state. Shared-key state is reserved for genuinely cross-cutting fields like a `run_id`, a `pipeline_manifest_version`, or an `artifacts` index.

### Fan-Out (`Send` API) — Power Tool with a Known Bug

LangGraph's **`Send` API** enables map-reduce / dynamic parallel fan-out — the number and configuration of parallel tasks are decided at runtime from graph state. Natural fit for: parallel specialist dispatch (Marcus dispatching multiple specialists concurrently), per-segment fan-out in cluster work, parallel quality-gate checks.

**⚠️ Known issue to design around**: [LangGraph Issue #2581](https://github.com/langchain-ai/langgraph/issues/2581) — fan-out+subgraph aggregation fails to merge subgraph state into the receiving graph state. Workaround: aggregate inside a Python reducer node rather than via the subgraph return path until the bug is resolved. *Confidence: high — the bug is documented in 2026 issues; behavior may change.*

**Per-invocation persistence** supports interrupts, durable execution, and parallel calls while keeping each invocation isolated — important when multiple parallel specialist invocations need separate checkpoint streams.

_Sources: [Subgraphs — LangChain docs](https://docs.langchain.com/oss/python/langgraph/use-subgraphs), [Scaling LangGraph Agents: Parallelization, Subgraphs, Map-Reduce Trade-Offs](https://aipractitioner.substack.com/p/scaling-langgraph-agents-parallelization), [LangGraph Issue #2581 (fan-out/subgraph bug)](https://github.com/langchain-ai/langgraph/issues/2581), [LangGraph Forum: parent state to subgraph via Send](https://forum.langchain.com/t/how-to-propagate-parent-state-to-a-compiled-subgraph-triggered-via-send-api/2328), [LangGraph Forum: subgraph state](https://forum.langchain.com/t/how-does-state-work-in-langgraph-subgraphs/1755)_

### Tool Surface — MCP Adapters as the Flexible Layer

`langchain-mcp-adapters` converts Anthropic MCP tools into LangChain/LangGraph-compatible tools, supports multiple MCP servers simultaneously (stdio + http + sse transports), and gives specialists a unified tool interface without manual MCP client management.

**Why this matters for Decision 3**: a hard-coded Python tool registry on each specialist would lock specialists into a fixed action surface — the opposite of "maximize flexibility." MCP adapters let the same specialist subgraph access **different tool surfaces in different deployments** (local stdio MCP server in dev, remote SSE MCP server in production, mix and match) without code changes. The specialist's intelligence stays portable.

**Mapping to existing project**: This is also an unusually clean integration story given the project already uses MCP servers. The Stage-2 runtime can:
1. Consume external MCP tool servers as specialist tools (current pattern, just LangGraph-wrapped).
2. **Expose the LangGraph runtime itself as an MCP server** — so the IDE (Claude Code) talks to the runtime via the same protocol it already speaks. This is a strong candidate for the IDE↔runtime bridge in Stage 2 (see below).

_Sources: [LangChain Changelog: MCP Adapters](https://changelog.langchain.com/announcements/mcp-adapters-for-langchain-and-langgraph), [langchain-mcp-adapters (GitHub)](https://github.com/langchain-ai/langchain-mcp-adapters), [Model Context Protocol (MCP) — LangChain docs](https://docs.langchain.com/oss/javascript/langchain/mcp), [LangGraph MCP Setup Guide 2026](https://generect.com/blog/langgraph-mcp/), [Complete Guide to langchain-mcp-adapters (Medium)](https://medium.com/@deepakkamboj/the-complete-guide-to-langchain-mcp-adapters-bridging-langchain-and-model-context-protocol-3f5507cbd3ca)_

### Human-in-Loop Interrupts — Governance Gates Integration

LangGraph's `interrupt()` function pauses graph execution mid-node, persists state via the checkpointer, and resumes via `Command(resume=...)` once a human decision arrives. The 2026 `version="v2"` API returns a `GraphOutput` with an `interrupts` attribute containing the actions awaiting review; the human responds with one of:

- `{"type": "approve"}`
- `{"type": "edit", "edited_action": {...}}`
- `{"type": "reject", "message": "..."}`

Resume preserves exact-point continuation by using the same `thread_id`. **Requires a persistent checkpointer in production** (`AsyncPostgresSaver`).

**Mapping to existing project — this is the gate substrate**:

| Existing gate | LangGraph form |
|---|---|
| Party-mode roundtable before story `done` | `interrupt()` after slab/story completion node; review action = "ratify or send-back"; resume continues to next slab/story |
| Code-review (`bmad-code-review`) gate before story closure | `interrupt()` keyed on a `code_review_required` predicate; review action = approve/edit/reject |
| Block-mode trigger paths (Pipeline Lockstep) | `interrupt()` raised by a deterministic precheck node when block-mode trigger paths are touched, requiring explicit operator approval before proceeding |
| Lesson-Planner governance validator failure | `interrupt()` raised by validator node — operator can approve override (with documented exception) or reject and route to remediation |

This is a **major architectural win**: gates stop being out-of-band shell-script hooks and become first-class graph nodes with checkpoint-backed resumability. The "edit" decision type is especially valuable — operators can edit the agent's proposed action before it executes, which matches party-mode's existing "modify the proposal" pattern.

_Sources: [Human-in-the-loop — LangChain docs](https://docs.langchain.com/oss/python/langchain/human-in-the-loop), [Interrupts and Commands in LangGraph (DEV)](https://dev.to/jamesbmour/interrupts-and-commands-in-langgraph-building-human-in-the-loop-workflows-4ngl), [LangGraph interrupt() pattern (BSWEN, 2026-04)](https://docs.bswen.com/blog/2026-04-16-langgraph-human-in-the-loop/), [Production LangGraph interrupt template (KirtiJha/GitHub)](https://github.com/KirtiJha/langgraph-interrupt-workflow-template), [LangGraph + Claude Agent SDK guide 2026 (mager.co)](https://www.mager.co/blog/2026-03-07-langgraph-claude-agent-sdk-ultimate-guide/)_

### IDE ↔ Runtime Protocol (Stage 2 Bridge)

Three viable bridges from the IDE (Claude Code) to a long-lived LangGraph runtime, ranked by fit:

| Option | Fit | Notes |
|---|---|---|
| **MCP server exposing the LangGraph runtime** | ★★★ | Most natural — IDE already speaks MCP; runtime presents specialist subgraphs as MCP tools/resources; Marcus orchestration becomes an MCP-callable graph. Reuses existing IDE infrastructure. |
| **Custom FastAPI + SSE** | ★★ | Maximum control; ergonomic for non-IDE clients (CLI, web UI, CI). Requires hand-rolled streaming protocol. |
| **LangGraph Platform** | ★★ | First-party hosted runtime: built-in persistence, HIL, cron, webhooks, LangGraph Studio. Tradeoff: hosted/commercial; less local-control than MCP-or-FastAPI route. Worth evaluating in Step 5. |
| **LangServe** | ✗ | **Avoid for new builds.** As of 2026, LangChain explicitly recommends LangGraph Platform over LangServe; LangServe receives maintenance + bug fixes only, no new features. Production-grade features (HIL, persistence, cron) are not coming to LangServe. |

**Recommendation for Slab 1 (per Decisions 1 & 3)**: **MCP server as the primary bridge, with FastAPI as escape hatch.** Why:
- Reuses existing IDE↔MCP infrastructure (lowest novelty cost)
- Specialists exposed as MCP tools become callable from CLI/CI/other clients automatically
- Custom FastAPI endpoints can sit alongside the MCP server for web-UI/CI use cases that need bespoke endpoints
- Avoids LangServe (deprecated direction)
- Avoids commitment to LangGraph Platform until measured

_Sources: [LangServe + LangGraph stack (Medium)](https://medium.com/@gaddam.rahul.kumar/langserve-langgraph-a-powerful-agentic-ai-stack-for-full-stack-applications-98931581de2b), [LangServe vs FastAPI](https://www.leanware.co/insights/langserve-vs-fastapi), [Streaming AI Agent with FastAPI & LangGraph 2025-26 guide](https://dev.to/kasi_viswanath/streaming-ai-agent-with-fastapi-langgraph-2025-26-guide-1nkn), [Deploying LangGraph with FastAPI](https://ideentech.com/deploying-langgraph-with-fastapi-a-step-by-step-tutorial/), [LangServe (GitHub)](https://github.com/langchain-ai/langserve)_

### Streaming Patterns

`astream_events(version="v2")` is the canonical streaming API — yields a stream of event dictionaries, each representing a step or transition within the graph. Server-Sent Events (SSE) is the standard wire format for streaming over HTTP. LangServe auto-generates `/invoke`, `/batch`, `/stream`, `/stream_log` endpoints, but per the recommendation above we prefer FastAPI/MCP routes.

**Mapping to existing project**: Streaming is the technical enabler for the IDE-as-client experience — operator sees specialist progress in real-time without blocking, sees `interrupt()` events as soon as they arrive. Combined with checkpointing, streaming enables an "always know where Marcus is" experience that today only exists inside the live IDE conversation.

_Sources: [Streaming — LangChain docs](https://docs.langchain.com/oss/python/langgraph/streaming), [SSE with FastAPI + React + LangGraph](https://www.softgrade.org/sse-with-fastapi-react-langgraph/), [Real-Time AI Apps with LangGraph + FastAPI + Streamlit](https://medium.com/@dharamai2024/building-real-time-ai-apps-with-langgraph-fastapi-streamlit-streaming-llm-responses-like-04d252d4d763)_

---

### Cross-Integration Analysis — Six-Axis Mapping (Integration Layer)

| Axis | Integration lever |
|---|---|
| Model use | Output modality choice per node — free-text/Sonnet|Opus inside specialists, structured-output/Haiku at routing edges |
| Token efficiency | Isolated subgraph state (smaller per-call payloads); `interrupt()` resume from checkpoint avoids re-sending context |
| Speed | `Send` fan-out for parallel specialist dispatch; `astream_events` for non-blocking UX |
| Flexibility | MCP adapters as tool surface (swappable per deployment); specialist subgraphs as isolated units |
| Quality | `interrupt()`-based gates with approve/edit/reject — gates as graph nodes, not out-of-band hooks; structured output validates routing decisions |
| Reliability | Checkpoint+resume across `interrupt()`; same `thread_id` preserves exact-point continuation; per-invocation persistence isolates parallel calls |

### Current APP State — Substrate Digest

> *Status: Ingestion underway via dedicated subagent (2026-04-21). This section will be populated with a structured digest of the existing APP's complexity surface — Marcus persona/protocols, specialist registry, gate inventory, contracts, pipeline-manifest regime, schema discipline, active epics/sprint-status, deferred inventory — so Step 4 architectural patterns and downstream PRD/architecture/epics work inherit accurate grounding rather than generic LangGraph patterns. The digest is intentionally a distillation, not a copy — it captures the shape of complexity each migration slab must preserve.*

#### 1. Marcus — SPOT Orchestrator Shape

**Activation sequence** ([skills/bmad-agent-marcus/SKILL.md](skills/bmad-agent-marcus/SKILL.md)): Marcus emerges stateless every session (Sacred Truth) and activates via cold-start protocol: (1) Load config from `_bmad/config.yaml` + `_bmad/config.user.yaml` if present; (2) Check sanctum existence at `_bmad/memory/bmad-agent-marcus/`; (3) If sanctum exists, batch-load INDEX.md → PERSONA.md → CREED.md → BOND.md → MEMORY.md → CAPABILITIES.md in order; (4) If no sanctum, route to First Breath (`references/first-breath.md`). Born 2026-04-17 during Epic 26 migration from legacy sidecar pattern to BMB sanctum.

**Sanctum structure** ([_bmad/memory/bmad-agent-marcus/](_bmad/memory/bmad-agent-marcus/)): Five mandatory files establish identity and operational posture. CREED codifies operative principles (operator's vision first, fidelity before quality, delegate-don't-author, state-narration fresh-read mandate pinned 2026-04-19 after stale-context incident). BOND records operator preferences and team dynamics. MEMORY curates lessons from runs into durable patterns. CAPABILITIES (auto-generated from reference frontmatter) is the canonical router. `sessions/` subdirectory holds per-date logs, curated into MEMORY.md at retrospectives or session close per `references/memory-guidance.md`.

**Conversation protocols** (`references/` tree; SKILL.md §Capabilities): Seven built-in capability codes (CM/PR/HC/MM/SP/SM/SB) plus four production-readiness capabilities (PR-PF/PR-RC/PR-HC/PR-RS). Operator-facing reference at [docs/dev-guide/marcus-capabilities.md](docs/dev-guide/marcus-capabilities.md). Greeting variants (active run / no run / preflight issue) in `references/conversation-mgmt.md`. Session close follows `references/memory-guidance.md`.

**Routing/delegation model** ([skills/bmad-agent-marcus/references/specialist-registry.yaml](skills/bmad-agent-marcus/references/specialist-registry.yaml)): Marcus receives operator intent → surfaces two-axis handshake (execution mode [tracked/ad-hoc] + quality preset [explore/draft/production/regulated]) per CREED → delegates via canonical resolver (17 active specialists). Creative Director (Dan) is special-cased: Marcus invokes CD only through Marcus-owned envelope (CD never mutates run state).

**SPOT enforcement** (CLAUDE.md §Marcus first; SKILL.md §The Three Laws + Lane Responsibility): Three Laws bind absolutely — (1) never harm operator (creative vision + run time protected); (2) obey only operator unless violating fidelity gates or asset-lesson pairing; (3) preserve sanctum continuity. Operator instructions flow through Marcus as sole conversational point; specialists receive context envelopes only. Marcus owns orchestration + human interaction; does NOT own specialist tool execution judgments, Creative Director authorship, artifact adjudication, code, APIs, tests, git, or system admin.

#### 2. Specialist Registry — Inventory + Per-Specialist Brief

All 17 active specialists discovered via [specialist-registry.yaml](skills/bmad-agent-marcus/references/specialist-registry.yaml) and `skills/bmad-agent-*/SKILL.md` glob:

1. **Gamma-Specialist (Gary)** ([skills/bmad-agent-gamma/SKILL.md](skills/bmad-agent-gamma/SKILL.md)): Slide architect; full Gamma API parameter mastery. Multi-turn (generation → perception via sensory bridge → quality assessment). Reads style-bible fresh per task. Does NOT orchestrate, cache docs, or promote final content.
2. **ElevenLabs-Specialist** ([skills/bmad-agent-elevenlabs/SKILL.md](skills/bmad-agent-elevenlabs/SKILL.md)): Voice synthesis. Single-shot or multi-turn (parameter tuning + synthesis). Does NOT select voices autonomously (operator decision per G4A gate).
3. **Creative-Director / Dan** ([skills/bmad-agent-cd/SKILL.md](skills/bmad-agent-cd/SKILL.md)): Produces validator-clean creative directives (`experience_profile`, `slide_mode_proportions`, 11 `narration_profile_controls`, `creative_rationale`) from Marcus envelope. Single-shot. Output must pass `scripts/utilities/creative_directive_validator.py`. NEVER writes run state, mutates state, or talks to operator outside envelope.
4. **Texas-Specialist** ([skills/bmad-agent-texas/SKILL.md](skills/bmad-agent-texas/SKILL.md)): Retrieval expert with Shape 3-Disciplined contract ([retrieval-contract.md](skills/bmad-agent-texas/references/retrieval-contract.md)). Multi-turn (intent dispatch → provider selection → cross-validation → AC filtering). Multi-provider (scite, Consensus, YouTube, local_file, box, notion, playwright). Requires explicit `provider_hints`; no auto-discovery in v1.
5. **Vera (Fidelity-Assessor)** ([skills/bmad-agent-fidelity-assessor/SKILL.md](skills/bmad-agent-fidelity-assessor/SKILL.md)): Pre-spend quality gate (G4/G5). Source faithfulness, learning-objective alignment, accessibility. Multi-turn perception. Surfaces evidence; does NOT approve.
6. **Quality-Reviewer** ([skills/bmad-agent-quality-reviewer/SKILL.md](skills/bmad-agent-quality-reviewer/SKILL.md)): Post-spend QA (G5/G6). Three hunter modes (Blind, Edge Case, Acceptance Auditor); three-tier findings (MUST-FIX / SHOULD-FIX / DISMISS).
7. **Quinn-R**: Pre-composition QA gate (segment manifest, audio timing, narration fidelity).
8. **Compositor** ([skills/compositor/SKILL.md](skills/compositor/SKILL.md)): Assembly stage (audio/video/captions sync). Multi-call: manifest intake → guide gen → operator-decision injection.
9–14. **Canva, Canvas, Articulate, Vyond, Midjourney, Kling specialists**: Asset producers (infographics, LMS, authoring, video, AI images, video gen). Single-shot or multi-turn per tool API.
15. **CourseArc-Specialist**: LMS integration.
16. **Qualtrics-Specialist**: Assessment platform.
17. **Content-Creator**: Narrative/prose author.

**Multi-turn vs single-shot**: Gamma, ElevenLabs, Texas, Vera, Quinn-R are inherently multi-turn (perception → assessment → return). Others predominantly single-shot. **All invoked through Marcus** except rare debug scenarios. All receive context envelopes only; none write to runtime state or operator-facing artifacts except through Marcus-owned pathways. **All current work runs in IDE-as-conversation mode** (Cursor IDE chat). No standalone invocation paths today.

#### 3. Gate Inventory

**Pipeline Lockstep Manifest Gates** ([state/config/pipeline-manifest.yaml](state/config/pipeline-manifest.yaml)): 15 named gates (G0, G0A, G0B, G1, G1A, G1.5, G2, G2.5, G2B, G2C, G2M, G2F, G3, G3B, G4, G4A, G4B, G5) embedded in 30 pipeline steps (§01→§15). Each gate is a HIL pause with explicit operator confirmation or automated approval path. Receipts in `gate_<id>-<descriptor>-receipt.json` (signed SHA256 pins + operator decision). Learning events emitted at G2C, G3, G4 with event_types `[approval, revision, waiver]` per [learning-event-schema.yaml](state/config/learning-event-schema.yaml).

**K-Floor Gate (Lesson Planner MVP Stories)** ([docs/dev-guide/lesson-planner-story-governance.json](docs/dev-guide/lesson-planner-story-governance.json)): Per-story single-gate vs dual-gate enforced by `scripts/utilities/validate_lesson_planner_story_governance.py`. Schema-shape stories default single-gate; foundation stories default dual-gate. Validator at (a) spec ready-for-dev finalization, (b) T1 of dev-story start. Auto-remediation-first; escalate only on gate-mode/K-policy/policy-file/party-mode-impasse changes.

**Code Review Gate (`bmad-code-review`)** (CLAUDE.md §BMAD sprint governance): Layered — Blind Hunter (coverage/correctness), Edge Case Hunter (boundary), Acceptance Auditor (spec). Required at all story closures. Three-tier findings; MUST-FIX blocks closure; DISMISS aggressive. Caught two HIGH bugs on 27-2 and six MUST-FIXes on 31-1 that unit tests missed.

**Pipeline Lockstep Block-Mode Gate** ([docs/dev-guide/pipeline-manifest-regime.md](docs/dev-guide/pipeline-manifest-regime.md) §Block-Mode Trigger Paths): Any story diff touching trigger paths fires Cora's pre-closure block-mode hook → runs `scripts/utilities/check_pipeline_manifest_lockstep.py`. Exit 0 = closure permitted; non-zero = closure BLOCKED with trace path + operator message. Trigger paths: manifest itself, L1 check, HUD, progress_map, orchestrator, consumer tests, v4.2 pack files (all variants), learning-event schema/capture, generator package.

**Party-Mode Consensus Gates** (CLAUDE.md §BMAD sprint governance): Pre-dev (R1-R2) and post-dev (G5) party-mode rounds for foundation/integration. Stock roster (Winston, Amelia, Murat, Paige) + off-manifest specialists (Cora for governance, Audra for lockstep). Dual-gate stories run both; single-gate stories run post-dev only.

**Trial-Run Gate Receipts** ([next-session-start-here.md](next-session-start-here.md) §Trial Run Status): Recent trial C1-M1-PRES-20260419B (2026-04-19) closed with 15 gates all COMPLETE or PASS_WITH_ADVISORIES. Receipts at §10/§13/§14/§14.5/§15.

#### 4. Pipeline Lockstep Regime — Concrete Surface

**Seven components** (Epic 33 Standing Regime; [pipeline-manifest-regime.md](docs/dev-guide/pipeline-manifest-regime.md)):

| # | Component | Path | Role |
|---|---|---|---|
| 1 | Pipeline manifest | `state/config/pipeline-manifest.yaml` | SSOT: gates, order, names, bitmap, insertion-points, emission topology, block-mode triggers, rationale |
| 2 | L1 lockstep check | `scripts/utilities/check_pipeline_manifest_lockstep.py` | 8 deterministic checks; 0/1/2 exit codes; O/I/A trace under `reports/dev-coherence/<ts>/` |
| 3 | v4.2 generator | `scripts/generators/v42/` | Jinja2 deterministic, no LLM; manifest+templates → byte-identical pack |
| 4 | Block-mode pre-closure hook | `skills/bmad-agent-cora/scripts/preclosure_hook.py` | Classifies change-window via trigger-paths; invokes L1; blocks on non-zero |
| 5 | Consumer rewires | `run_hud.py`, `progress_map.py`, `marcus/orchestrator/workflow_runner.py` | All manifest-sourced at import time; no parallel step lists |
| 6 | Version parameterization | Manifest `pack_version` + L1 `--pack-version` arg | Horizontal scaling to v4.3+ via `scripts/generators/v<N>/` siblings |
| 7 | Meta-test template | [_bmad-output/implementation-artifacts/15-1-lite-marcus.md](_bmad-output/implementation-artifacts/15-1-lite-marcus.md) | Canonical pattern validating substrate catches new-contract introductions |

**Pack version policy** (Tier 1/2/3; frozen-at-ship discipline):
- **Tier 1 (Patch)**: Prose, typos, connective-tissue. Regenerate in place; no version bump; dev-agent authority via Cora's hook.
- **Tier 2 (Minor, v4.2→v4.3)**: New step, removed step, gate semantic change, sub-phase promotion, new event type, new trigger path. Requires party-mode consensus BEFORE dev. New `scripts/generators/v43/` sibling. v4.2 stays on disk for audit.
- **Tier 3 (Major, v4.x→v5)**: Core loop restructure, downstream schema cascade, Marcus contract change, workflow-family restructure. Party-mode at Epic boundary; v4 archived after v5 ships clean.
- **Frozen-at-Ship**: Once pack ships + tracked trial completes, pack is frozen. Post-freeze changes bump version; frozen pack stays on disk as audit reference.

#### 5. Schema Discipline (Lesson-Planner MVP)

**Pydantic v2 idioms enforced** (top 7 from [pydantic-v2-schema-checklist.md](docs/dev-guide/pydantic-v2-schema-checklist.md)):
1. `model_config = ConfigDict(extra="forbid", validate_assignment=True)` on every model. Mandatory — without `validate_assignment`, mutations bypass re-validation (caught MF-1/2/3 on 31-1).
2. Timezone-aware datetimes via `field_validator` rejecting `tzinfo=None`. Never `datetime.utcnow()` (deprecated). Use `datetime.now(tz=UTC)`.
3. UUID4 validation via `field_validator` checking `parsed.version == 4` explicitly. UUID1/3/5 pass naive parse otherwise.
4. **Triple-layer red-rejection on closed enums**: Pydantic `Literal` + JSON Schema `enum` array + `TypeAdapter` round-trip. All three must reject independently. Murat caught missing TypeAdapter on 31-1.
5. Internal audit fields via `Field(exclude=True) + SkipJsonSchema[...]`. No `model_dump(exclude=set())` (Pydantic v2 forbids). Provide opt-in helper (`to_audit_dump()`).
6. Verbatim free-text fields (rationale, commentary) accept empty/single-char/whitespace-only. No `min_length`, regex, normalization.
7. Revision monotonicity as model method (`apply_revision()` raising `StaleRevisionError`), not test helper.

**Governance validator** ([scripts/utilities/validate_lesson_planner_story_governance.py](scripts/utilities/validate_lesson_planner_story_governance.py)): Runs at story finalization and T1 of dev-start. Auto-remediation-first.

**Scaffold pattern** ([docs/dev-guide/scaffolds/schema-story/](docs/dev-guide/scaffolds/schema-story/)): Pre-instantiated stubs at target paths BEFORE dev-story begins. Dev agent extends stubs (never re-derives). When new pitfall caught at G6: fix code + update scaffold + update checklist + update anti-patterns. **One PR, four files.**

#### 6. Active Sprint + Epic Landscape

| Epic | Stories | Status | Anchor |
|---|---|---|---|
| 33 (Standing Regime) | 33-1, 33-1a, 33-2, 33-3, 33-4, 15-1-lite-marcus | in-progress | Substrate live; meta-test READY (depends on 33-1→33-4) |
| 32 (Lesson Planner) | 32-1…32-5 | done (BMAD-closed 2026-04-19) | MVP ratification pending; 5 preflight flags |
| 31 (Lesson Plan Schema) | 31-1/2/3 done; 31-4/5 ready-for-dev | in-progress | Foundation stories, dual-gate |
| 30 (Marcus Duality) | 30-1 done; 30-2a/2b ready-for-dev | in-progress | 30-3a/3b/4/5 queued |
| 29 (Irene + FitReport) | 29-1, 29-2, 29-3 | ready-for-dev | Scaffold-first |
| 28 (Tracy Intake) | 28-1, 28-2, 28-3, 28-4 | ready-for-dev | Reshaped 2026-04-19 (three-modes) |
| 27 (Retrieval Foundation) | 27-0/1/2 done; 27-2.5 ready-for-dev | in-progress | CI 3x flake-detection gate must wire pre-27-2.5 |
| 19–24 (Cluster + Creative) | Wave 2 complete | done | 20c-4/5/6 + 20a-5 deferred |

**Recent epic closures (last 3)**: Epic 33 (substrate + meta-test unlocking Epic 15 chain), Epic 32 (Lesson Planner inventory + 5 governance flags), Epic 31 (31-1/2/3 schema + log + registries).

**Deferred inventory snapshot** ([_bmad-output/planning-artifacts/deferred-inventory.md](_bmad-output/planning-artifacts/deferred-inventory.md)): **41 items total** = 4 backlog epics (Epic 15 Learning, Epic 16 Bounded Autonomy, Epic 17 Research, Epic 18 Additional Assets) + 4 in-epic deferred stories (20c-4, 20c-5, 20c-6, 20a-5) + 13 named-but-not-filed follow-ons (15-1-lite-irene, 15-1-lite-gary, v4.3 substrate, Epic 15 chain 15-2…15-7, Epic 33 retro follow-ons, PR-TR trial-resumption, Texas best-available-medium, Step 02A prior-run directives, HUD per-step expandable summaries, cluster/segment manifest convergence, production intake_callable for 4A, **Irene Pass 2 authoring template (HIGH)**, theatrical-direction synthesis Tier 1+2).

#### 7. Run Lifecycle — End-to-End

**The 15-step pipeline** ([state/config/pipeline-manifest.yaml](state/config/pipeline-manifest.yaml); [docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md](docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md)):

§01 Activation+Preflight (G0) → §02 Source Authority Map (G0A) → §02A Operator Directives (G0B) → §03 Ingestion+Evidence Log → §04 Ingestion Quality+Irene Packet (G1) → §04A Lesson Plan Coauthoring+Scope Lock (G1A) → §04.5 Parent Slide Count Polling (emits `plan_unit.created`) → §04.55 Estimator+Run Constants Lock (emits `plan.locked`) → §4.75 Creative Directive Resolution (Dan) → §05 Irene Pass 1+Gate 1 Fidelity (G2) → §05B Cluster Plan G1.5 → §06 Pre-Dispatch Package Build → §6.2 Cluster Prompt Engineering → §6.3 Cluster Dispatch Sequencing → §06B Literal-Visual Operator Build → §07 Gary Dispatch+Export → §7.5 Cluster Coherence (G2.5) → §07B Variant Selection (G2B) → §07C Storyboard A+Gate 2 Approval (G2C, emits approval/revision/waiver) → §07D Gate 2M Motion Designation → §07E Motion Generation/Import → §07F Motion Gate (G2F) → §08 Irene Pass 2+Segment Manifest → §08B Storyboard B+HIL Review (G3B) → §09 Gate 3 Lock Pass 2 Package (G3, emits) → §10 Fidelity+Quality Pre-Spend (G4, emits) → §11 ElevenLabs Voice Selection HIL (G4A) → §11B Input Package HIL (G4B) → §12 ElevenLabs Audio Generation → §13 Quinn-R Pre-Composition QA (G5) → §14 Compositor Assembly Bundle → §14.5 Desmond Run-Scoped Operator Brief → §15 Operator Handoff (Descript Ready).

**C1-M1-PRES-20260419B trial**: First end-to-end production run completed 2026-04-19. All 15 gates COMPLETE or PASS_WITH_ADVISORIES. ElevenLabs synthesis 14/14 segments (424.74s). Quinn-R PASS_WITH_ADVISORIES (Option A for card-01 + slow-WPM cards 03/06/09 accepted). Receipts signed with SHA256 pins under `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260419b-motion/`.

**Outstanding from trial**: Motion structural-walk pack-vs-walk-spec drift (6 pre-existing findings; Tier-1 prose alignment), Irene Pass 2 authoring template (HIGH; three concrete failure modes captured), theatrical-direction synthesis decision pending operator audio review (Tier 1 per-segment voice_settings or Tier 2 audio-tag model swap).

#### 8. Complexity Surface — Load-Bearing Invariants the Migration MUST Preserve

LangGraph migration must maintain these as graph-level guarantees:

1. **Marcus as single stateless orchestrator entry point.** Cold-starts from sanctum read; no fallback to embedded defaults. Sanctum files are the continuity mechanism.
2. **Specialist delegation via registry + envelope pattern.** Specialists receive context envelopes only; never direct operator commands. Marcus routes all; no ad-hoc specialist jumping except on explicit naming.
3. **Pipeline Lockstep deterministic neck.** Manifest = SSOT; generator = deterministic Jinja2 (no LLM). Trigger-path commits must regenerate pack + pass L1 before closure.
4. **15-gate production pipeline with manifest-driven topology.** No parallel step lists. All consumers read manifest at import time. Each gate is explicit HIL pause with SHA256-signed receipts.
5. **Schema discipline enforcement (Lesson Planner MVP).** Pydantic v2 idioms (14 rules, scaffold-enforced). Triple-layer red-rejection on closed enums. Governance validator gates story lifecycle.
6. **Three-layer quality review at closure.** bmad-code-review (Blind + Edge Case + Acceptance Auditor) catches correctness bugs unit tests miss. MUST-FIX blocks closure.
7. **SPOT enforcement of operator commands.** Marcus obeys only operator; specialists obey only Marcus via envelope. Fidelity (Vera) + quality (Quinn-R) gates are preconditions, never optional.
8. **Dual-gate vs single-gate story review policy.** Per-story policy enforced by validator; foundation/integration dual-gate, peripheral single-gate.
9. **Learning events emission at defined gates.** G2C, G3, G4 emit `approval`/`revision`/`waiver` to append-only ledger. Schema version pinned. Trial proved infrastructure works.
10. **Frozen-at-ship pack discipline.** Once pack ships + tracked trial completes, pack frozen. Post-freeze changes bump version. Pre-closure hook enforces byte-identical regeneration.
11. **K-floor + target-range test discipline.** Floor ≥ K; target 1.2-1.5× K. Parametrized cases count as one. Aggressive G6 DISMISS.
12. **Pydantic governance validator gate on Lesson Planner stories.** Runs at ready-for-dev and T1.
13. **Dan (Creative Director) as single directives emitter.** Marcus envelope only; validator-clean directives only. Never writes run state, never operator-facing.
14. **Deferred inventory as single source of truth for backlog work.** Three binding consultation points (epic retros, session hot-start, story closure with new follow-on).
15. **Session boundary choreography.** Marcus owns production (G0→G6); Cora owns dev-session (START/WRAPUP, harmonization, hot-start-pair). Two lanes do not overlap. SESSION-HANDOFF.md + next-session-start-here.md are the handoff contract.

#### 9. Surprises / Notable Findings

1. **Marcus's "Sacred Truth" — stateless rebirth per session is intentional design**, not a limitation. Cold-start reads sanctum files every time. Surfaces file-corruption bugs earlier than caching would; fresh eyes catch habit-blindness. **LangGraph implication**: memory state must be file-backed and read fresh at cold-start, not held in graph process memory. (Or: thread state is the cold-read substitute, but the *agent-identity* state must remain file-backed.)
2. **Manifest-driven pipeline is a Tier-1 governance surface**, not an implementation detail. Step-order/name/insertion/gate/emission changes require party-mode (Tier-2) or Epic-scope discussion (Tier-3). Manifest is data; generator deterministic. Hand-editing the pack triggers block-mode hook at pre-closure. Load-bearing.
3. **Specialist delegation via envelope is strict, not stylistic.** Even "talk to [specialist]" routes through Marcus activation. Single operator conversation interface; prevents specialist-to-operator leakage. Implication: the LangGraph supervisor pattern needs an envelope contract, not just a router.
4. **Learning events are first-class cargo, not telemetry sidecar.** Gates emit approval/revision/waiver to append-only ledger (§04.5/§07C/§09/§10). This is how Epic 15 inverts production learnings upstream. Trial run proved infrastructure.
5. **Frozen-at-ship enforces historical auditability.** Post-ship changes bump version; previous pack immutable on disk. Production runs can audit against the exact pack generation they used. Cora's hook enforces deterministically.
6. **Schema discipline is four-file lockstep.** New G6 pitfall → fix lands simultaneously in code + scaffold template + checklist + anti-patterns catalog. One PR, four files. Scaffold is the propagation mechanism for next 8+ schema stories.
7. **Dan (Creative Director) is NOT Marcus.** Dan shapes creative framing; output must pass `creative_directive_validator.py` before return. Hard contract, not advice. Operator gives plain-language profile question; Dan returns typed directives downstream specialists consume.
8. **Irene Pass 2 is the highest-friction production step observed in trial.** Validator required exceptional post-hoc repair. Authoring contract is implicit in validator code. **Next work item**: explicit schema + authoring template so Pass 2 output is correct-by-construction. (HIGH priority deferred follow-on.)
9. **Motion structural-walk pack-vs-walk-spec drift is pre-existing**, not introduced by trial. Six markers in motion.yaml don't match v4.2 pack section titles (e.g., expects `## 4) Ingestion...`, actual is `## 04) ...`). Tier-1 prose (dev-agent authority).
10. **Dials-only ceiling is operator-decided, not technical.** Current trial uses dials-only amp-up (speed variance only, uniform voice_settings). Operator audio review → "sufficient" (stay) or "escalate" (Tier 1 per-segment / Tier 2 audio-tag model swap). Experience-design choice, not a technical gap.

#### Migration Implications Summary (substrate digest → graph design)

The APP is a 15-step deterministic production pipeline (§01→§15) orchestrated by Marcus (stateless cold-start via sanctum read) and executed by 17 specialist agents. Pipeline topology is manifest-driven; generator deterministic (Jinja2). Every stage is a gate with HIL pause + SHA256-signed receipt. Learning events flow to append-only ledger from three gates. Schema discipline enforced via Pydantic v2 scaffold + governance validator. Code review is layered (Blind + Edge Case + Acceptance Auditor). First trial run (C1-M1-PRES-20260419B) completed §01→§15 end-to-end 2026-04-19. 41 deferred items tracked.

**Direct mapping to LangGraph design (preview for Step 4):**
- Marcus = supervisor `StateGraph`; sanctum read = cold-start node reading file artifacts (NOT graph-memory); 17 specialists = subgraphs reachable via conditional edges keyed off Marcus's routing decisions
- 15 production steps = sequential graph spine with explicit gate nodes between steps
- Each gate = `interrupt()` node with curated decision-card payload + receipt-emission as side-effect
- Pipeline manifest = static config loaded at graph compile time; manifest changes trigger graph rebuild + L1 check (block-mode hook becomes graph-build CI check)
- Learning event ledger = side-effect append from designated gate nodes (G2C/G3/G4 nodes emit on resume)
- Pydantic v2 state schema with isolated subgraph state (per Decision 3); validators run per-node-entry; governance validator becomes pre-flight node
- Dan envelope = single-shot subgraph callable only by Marcus supervisor node; Dan output passes validator before being added to parent state
- Frozen-at-ship = compiled-graph-version pinned at trial close; new graph version branches in `runtime/graphs/v<N>/`

## Architectural Patterns Analysis

> *Note on adapted structure*: The standard template's microservices/cloud-native/SOLID/database-design sub-sections are not load-bearing here. The sub-sections below are the architectural patterns that operationalize Decisions 1–4 against the substrate digest's complexity surface: top-level topology (hybrid sequential-spine + supervisor dispatcher), Marcus reasoning loop (Plan-and-Execute by default, ReAct on exploration), gate-as-interrupt pattern, sanctum cold-start pattern, manifest-as-graph-config, learning-event side-effect, frozen-graph-version, error/retry/idempotency, time-travel + fork (trial-run discipline), subgraph composition, streaming, observability, dev-graph separation (Cora vs Marcus).

### Top-Level Topology — Hybrid Sequential-Spine + Supervisor Dispatcher

The substrate digest §7 documented a **15-step deterministic pipeline (§01→§15)** with Marcus orchestrating specialist dispatch *within* steps. This is neither pure-supervisor nor pure-sequential — it's a **hybrid**:

- **The 15-step pipeline IS the sequential spine.** It is fixed, manifest-driven, deterministic in step order. LangGraph expresses this as a sequential `StateGraph` with explicit edges between named step nodes (§01_node → §02_node → … → §15_node), no choices about ordering.
- **Within each step, Marcus is a supervisor.** A step node delegates to Marcus's supervisor subgraph; Marcus reads the step's intent + envelope context, decides which specialist(s) to dispatch (sometimes parallel via `Send`), integrates returns, and either advances to the next step or pauses at a gate.
- **Gate nodes sit BETWEEN spine steps.** G0 → §01 → G0A → §02 → G0B → §02A → … → G5 → §13 → §14 → §14.5 → §15. Gate nodes are not specialist work — they are `interrupt()` nodes with curated `DecisionCard` payloads.

This hybrid is well-supported in 2026 LangGraph — the framework natively supports supervisor (centralized coordination), swarm (decentralized handoffs), hierarchical (layered supervisors), and sequential pipeline patterns; most production systems use supervisor for predictability, with hybrid approaches combining both for specific scenarios.

**Why hybrid wins for this APP**: A pure-supervisor topology would require Marcus to re-derive step ordering every invocation — wasteful and fragile against the manifest-as-SSOT discipline (substrate digest §4). A pure-sequential topology cannot express within-step parallel specialist dispatch or operator-driven specialist re-routing. Hybrid lets the spine encode the deterministic 15-step pipeline (manifest-driven, frozen-at-ship-able) while keeping Marcus's supervisor reasoning surface free for within-step decisions.

_Sources: [LangGraph in 2026: Multi-Agent AI Systems (DEV)](https://dev.to/ottoaria/langgraph-in-2026-build-multi-agent-ai-systems-that-actually-work-3h5), [LangGraph TypeScript Multi-Agent Guide](https://langgraphjs.guide/multi-agent/), [Production-Ready AI Pipelines with LangGraph 2026 (Harshith)](https://harshith.org/building-production-ready-ai-pipelines-with-langgraph-stateful-multi-agent-workflows-in-2026/), [LangGraph 2.0 Definitive Guide 2026 (DEV)](https://dev.to/richard_dillon_b9c238186e/langgraph-20-the-definitive-guide-to-building-production-grade-ai-agents-in-2026-4j2b), [LangGraph overview docs](https://docs.langchain.com/oss/python/langgraph/overview)_

### Marcus's Reasoning Loop — Plan-and-Execute Default, ReAct on Exploration

Two canonical agent reasoning patterns exist in LangGraph:

| Pattern | How | Cost | When |
|---|---|---|---|
| **ReAct (Reason+Act loop)** | Iterative LLM-call → tool-call → observe → next-LLM-call until done | Each iteration = one LLM call; latency + cost scales with steps | Exploratory work where the path is unknown; high tool-output-uncertainty |
| **Plan-and-Execute** | Plan once with large model → execute sub-tasks (smaller models or deterministic) → re-plan only if needed | Few large-model calls; sub-tasks cheaper | Long-horizon structured workflows; reported **92% higher accuracy** on complex long-horizon tasks |

**Decision for this APP**: Marcus is **Plan-and-Execute by default**, **ReAct on `explore` quality preset only**.

- **Plan-and-Execute fits the 15-step spine perfectly.** Marcus reads the current step's intent + run state → produces a plan (which specialists to dispatch, in what order, with what envelopes) → executes via specialist subgraphs → integrates returns → advances to next step or pauses at gate. Few Marcus-as-Opus calls per step; specialist subgraphs do the per-specialist reasoning at Sonnet/Opus per the scaffold's `quality_preset`.
- **ReAct is correct for `explore` preset.** When the operator is iterating creatively (substrate digest §1: two-axis handshake), the path is genuinely unknown; Marcus needs to react to specialist returns and reroute mid-step. Higher cost is acceptable because exploration is operator-driven.
- **Plan-and-Execute saves tokens precisely where the APP needs it most**: at the orchestration layer, where Opus-tier reasoning is expensive. Combined with `AnthropicPromptCachingMiddleware` on Marcus's persona+sanctum prefix, the per-step token cost becomes predictable and controllable.
- **ReAct lives inside specialist subgraphs by default.** A multi-turn specialist (Gary, Vera, Texas) runs its own ReAct loop within the `reason→act→perceive→assess→reason` cycle on its node skeleton. This is correct: specialist work IS exploratory at the per-specialist level.

_Sources: [ReAct vs. Plan-and-Execute trade-offs (AGI X Tech)](https://agixtech.com/react-vs-plan-and-execute-which-reasoning-loop-is-better-for-your-agentic-ai/), [Plan-and-Execute Agents (LangChain blog)](https://blog.langchain.com/planning-agents/), [Build a ReAct Agent with LangGraph TS (2026)](https://langgraphjs.guide/agents/react-agent/), [Navigating Modern LLM Agent Architectures (Wollen Labs)](https://www.wollenlabs.com/blog-posts/navigating-modern-llm-agent-architectures-multi-agents-plan-and-execute-rewoo-tree-of-thoughts-and-react), [LangGraph Architecture and Design (Medium)](https://medium.com/@shuv.sdr/langgraph-architecture-and-design-280c365aaf2c)_

### Gate-as-Interrupt-Node Pattern (the operationalization of Decisions 3a + governance gates)

Each of the 15+ named gates (G0, G0A, G0B, G1, G1A, G1.5, G2, G2.5, G2B, G2C, G2M, G2F, G3, G3B, G4, G4A, G4B, G5) becomes a graph node with this canonical shape:

```
gate_node(state) → :
    1. compose curated DecisionCard from state (Decision 3a — minimum decisive context, NOT raw state)
    2. interrupt(decision_card)                          # graph pauses here; checkpointer persists state
    3. on resume:
        - if approve: emit_receipt(...) ; emit_learning_event(...) if applicable; return state
        - if edit: apply edit to state ; emit_receipt(...edited); emit_learning_event(revision); return modified state
        - if reject: emit_receipt(...rejected); emit_learning_event(waiver) if waiver path; route to remediation node
```

**Mappings to existing governance gates** (substrate digest §3):

| Gate type | Implementation |
|---|---|
| Pipeline manifest gates (G0–G5) | Direct `interrupt()` nodes between spine steps; receipt = `gate_<id>-<descriptor>-receipt.json`; learning event emitted at G2C/G3/G4 |
| Pipeline Lockstep block-mode | NOT a runtime gate — it's a **graph-build CI check**. Manifest changes trigger graph rebuild; rebuild script invokes L1 check (`scripts/utilities/check_pipeline_manifest_lockstep.py`); non-zero exit blocks the build (and thus the deploy). Production graph cannot run with un-checked manifest. |
| Lesson-Planner governance validator | Slab-4 work: dev-orchestration-graph (Cora) gate that runs validator before story closure; not in production graph |
| Party-mode roundtable | `interrupt()` node with multi-agent decision card; resume aggregates votes; can use parallel `Send` to invoke party-mode-roster subgraph in parallel |
| `bmad-code-review` | Slab-4 work: dev-orchestration-graph gate before story closure |

**Operator response taxonomy** (mapped from LangGraph's `version="v2"` interrupt API):
- `{"type": "approve"}` → resume with state unchanged
- `{"type": "edit", "edited_action": {...}}` → resume with operator-edited state
- `{"type": "reject", "message": "..."}` → route to remediation node (specialist re-dispatch with edit guidance, OR escalate)

This pattern is what makes Decision 3a's "operator decision authority never weakens" *architecturally enforced* — every gate is a code-level pause that cannot be bypassed without explicitly removing the node.

### Sanctum Cold-Start Pattern (Sacred Truth, Decision 4 + substrate digest surprise #1)

Every specialist subgraph (and Marcus's supervisor subgraph) begins with a `sanctum_load` node:

```
sanctum_load(state) → :
    sanctum_root = f"_bmad/memory/bmad-agent-{specialist_name}/"
    # FRESH READ — no in-process cache
    state.sanctum.persona = read_file(sanctum_root + "PERSONA.md")
    state.sanctum.creed = read_file(sanctum_root + "CREED.md")
    state.sanctum.bond = read_file(sanctum_root + "BOND.md")
    state.sanctum.memory = read_file(sanctum_root + "MEMORY.md")
    state.sanctum.capabilities = read_file(sanctum_root + "CAPABILITIES.md")
    # references load list comes from CAPABILITIES.md frontmatter
    state.references = load_references(specialist_name, state.sanctum.capabilities.references_load_list)
    return state
```

**Critical invariant**: Sanctum content is **not** held in graph process memory across invocations. Even if the same specialist is invoked twice in the same thread, sanctum is re-read both times. This is the file-backed-memory implication of substrate surprise #1.

**Performance protection**: Sanctum content is large (especially MEMORY.md as it accumulates lessons). Token cost is mitigated by `AnthropicPromptCachingMiddleware` — sanctum content lives in the cached prefix region of the LLM call, so the *read* cost is incurred but the *prompt-token* cost is amortized across cache hits within the 5m/1h TTL window.

**Migration implication**: Sanctum file mutation must trigger cache invalidation. The middleware's TTL handles this naturally (post-mutation, next cache miss reloads); no manual invalidation needed unless faster invalidation is critical.

### Manifest-as-Graph-Config Pattern

The pipeline manifest at [`state/config/pipeline-manifest.yaml`](state/config/pipeline-manifest.yaml) is loaded **at graph compile time**, not at runtime, and drives:

- The spine topology (which step nodes exist, in what order)
- Gate node placement (which gates between which steps)
- Learning-event emission points (which gate nodes emit which event types)
- Block-mode trigger paths (consumed by the build-time L1 check, not the runtime graph)
- Pack version (pinned into the compiled graph as a constant; queried by gate-receipt emitters for audit trail)

```
# at graph build time:
manifest = load_manifest("state/config/pipeline-manifest.yaml")
graph_builder = GraphBuilder(manifest=manifest)
for step in manifest.steps:
    graph_builder.add_step_node(step)
for gate in manifest.gates:
    graph_builder.add_gate_node(gate, between=gate.between_steps)
for emission in manifest.learning_event_emissions:
    graph_builder.attach_emission(emission.gate, emission.event_types)
production_graph = graph_builder.compile(checkpointer=PostgresSaver(...))
```

**Implication**: the pipeline manifest is no longer "data consumed by Marcus's prompt-pack" — it's **data that defines the runtime graph**. Manifest changes trigger graph rebuild (via build-time L1 check + regeneration), which is the LangGraph-native form of the existing Pipeline Lockstep regime. This is also the substrate digest invariant #3 enforced *at the framework level*.

### Learning-Event Side-Effect Pattern

Substrate digest §3 + invariant #9: G2C, G3, G4 emit `approval`/`revision`/`waiver` events to the append-only learning-event ledger ([`state/config/learning-event-schema.yaml`](state/config/learning-event-schema.yaml)).

Implementation: gate node's resume branch (after `interrupt()`) calls a side-effect emitter that writes the event to the ledger. The emitter is idempotent (event_id is UUID4 + content hash; duplicate writes are silently dropped). The ledger backend is independent of the LangGraph checkpointer — it's append-only file storage (or, in production, a separate Postgres table) so the audit trail survives even if the runtime checkpoint store is purged.

```
gate_node_g3(state) → :
    decision = interrupt(compose_decision_card(state, gate="G3"))
    receipt_id = emit_receipt(state, decision, gate="G3")
    if decision.type in ("approve", "edit", "reject"):
        emit_learning_event(
            event_type=event_type_for(decision),    # approval | revision | waiver
            run_id=state.run_id,
            gate="G3",
            receipt_id=receipt_id,
            schema_version=state.learning_event_schema_version,
        )
    return apply_decision(state, decision)
```

This pattern is what enables Epic 15 (Learning & Compound Intelligence — currently deferred per substrate §6 deferred inventory) to invert production learnings upstream.

### Frozen-Graph-Version Pattern (Frozen-at-Ship discipline, Decision 4 + substrate §4)

Per substrate digest §4: once a pack ships + a tracked trial-run completes, the pack is frozen; subsequent changes bump version. The LangGraph form:

```
runtime/graphs/
  v42/                       # frozen pack v4.2 graph; immutable
    __init__.py              # exports `build_v42_graph(checkpointer) -> CompiledGraph`
    spine.py                 # 15-step sequential structure, manifest=v4.2
    gate_nodes.py
    supervisor.py            # Marcus subgraph
  v43/                       # in-progress next graph version
    __init__.py
    ...
  v44/                       # deferred until v4.3 ships + trial completes
```

**Activation**: an active production graph is the *latest frozen* version unless explicitly overridden. Trial runs against in-progress versions are tagged `experimental=True` in receipts.

**Audit guarantee**: any past trial run can be reproduced byte-for-byte by activating the frozen graph version it ran against + replaying from its checkpoint thread.

This pattern requires a discipline mirror: every graph version directory must be code-review-clean and ATDD-tested before it can be promoted to "frozen + production" status. This is slab-4 governance work.

### Error / Retry / Idempotency Patterns

Default LangGraph behavior: when a node fails, the graph stops and the error surfaces immediately — failure is first-class, not patched with try/except scattered through code. This default is desirable for this APP (it preserves operator agency: "Marcus failed at G2 because Gary's Gamma API returned 429; do you want to retry, edit, or escalate?").

**Two-layer retry strategy** (both layers, per 2026 best practice):

| Layer | Use | Tool |
|---|---|---|
| HTTP-level (model client) | Transient 429/500/503 from Anthropic API or external service APIs | `ChatAnthropic(max_retries=N)`; MCP tool clients with built-in retry |
| Node-level | Transient failures from a node operation (e.g., specialist tool call) | LangGraph `RetryPolicy(max_attempts=N, initial_interval=..., backoff_factor=...)` |

**Specialist idempotency contract** (Decision 4 enforcement): a specialist invoked with the same `MarcusEnvelope` (same `run_id` + `typed_intent` + `context` hash) must produce the **same `SpecialistReturn` modulo stochastic LLM variance**. This is the property that makes retry safe and parallel `Send` fan-out coordination-free. The receipt's content hash is used to detect duplicate work.

**Known caveat — Pydantic ValidationError gotcha**: LangGraph node retry policies do **not** respect Pydantic v2 ValidationError as retriable ([Issue #6027](https://github.com/langchain-ai/langgraph/issues/6027)). Workaround: `envelope_intake` and `compose_return` nodes wrap Pydantic validation in try/except and return a structured error state rather than raising — the supervisor then routes to either retry (if recoverable) or operator interrupt (if not).

**Compensation pattern**: A specialist that has partial work-in-progress (e.g., Gary mid-way through a multi-slide generation) emits intermediate receipts every N slides; on retry, the next specialist invocation reads the intermediate receipts and resumes from the last checkpoint rather than restarting. This is checkpoint-as-compensation.

**Graceful degradation**: at the graph level, if a specialist fails after retry exhaustion, the supervisor routes to an `interrupt()` rather than letting the graph crash. Operator decides: edit envelope and retry, switch specialists, escalate, or abort.

_Sources: [LangGraph error handling — retry policies (DEV)](https://dev.to/aiengineering/a-beginners-guide-to-handling-errors-in-langgraph-with-retry-policies-h22), [Thinking in LangGraph (LangChain docs)](https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph), [Advanced Error Handling Strategies (Sparkco)](https://sparkco.ai/blog/advanced-error-handling-strategies-in-langgraph-applications), [Best way after retries exhausted (LangGraph forum)](https://forum.langchain.com/t/the-best-way-in-langgraph-to-control-flow-after-retries-exhausted/1574), [Stop Losing LangGraph Progress to 429 Errors](https://www.ezthrottle.network/blog/stop-losing-langgraph-progress), [LangGraph Issue #6027 — Pydantic ValidationError + RetryPolicy](https://github.com/langchain-ai/langgraph/issues/6027)_

### Time-Travel + Fork Pattern (Trial-Run Discipline, formalized)

LangGraph's persistence supports two time-travel operations on a thread:

- **Replay**: invoke graph with a prior checkpoint config → re-execute nodes from that point. *LLM calls, API calls, and interrupts fire again and may return different results* — replay is **not** read-from-cache. Use for debugging non-deterministic failures.
- **Fork**: branch from a prior checkpoint with modified state → creates a new checkpoint that branches from the specified point. Original execution history remains intact. Use for "what if operator had edited differently at G3?"

**Mapping to trial-run discipline** (substrate digest §7 + invariant #15):

| Trial-run operation | LangGraph form |
|---|---|
| Start a trial | New thread with unique `thread_id` keyed off `run_id` (e.g., `c1m1-pres-20260419b`) |
| Resume after operator decision at gate | Same thread, `Command(resume=decision)` from interrupt |
| Reproduce a past trial | Replay from thread's earliest checkpoint with frozen graph version active |
| Explore alternative gate decision | Fork from gate checkpoint with modified decision; new thread spawned, original preserved |
| Compare operator decisions | Compare receipts + LangSmith traces across original and fork threads |
| Restore from disaster | Resume from latest checkpoint of last successful gate |

**Key 2026 caveat**: a known issue exists where time-travel-then-invoke flow can fail to update checkpoint_id ([Issue #4987](https://github.com/langchain-ai/langgraph/issues/4987)) — workaround documented in the issue, but worth tracking for stability. **Confidence: medium** — likely to be fixed, but design assumes manual workaround until verified.

**Checkpoint bloat caveat**: each superstep creates a checkpoint; long-running graphs (your APP runs are long, ~15 gates × multiple specialist invocations per gate) generate substantial Postgres write volume. Implement checkpoint cleanup policy from day 1 (substrate §3 echoes this); also evaluate `JsonPlusSerializer` ormsgpack vs custom serializer for size.

_Sources: [Use time-travel — LangChain docs](https://docs.langchain.com/oss/python/langgraph/use-time-travel), [Time travel in LangGraph (concepts)](https://langchain-ai.github.io/langgraph/concepts/time-travel/), [Debugging Non-Deterministic LLM Agents with Time Travel (DEV)](https://dev.to/sreeni5018/debugging-non-deterministic-llm-agents-implementing-checkpoint-based-state-replay-with-langgraph-5171), [Time Travel in Agentic AI (Towards AI)](https://pub.towardsai.net/time-travel-in-agentic-ai-3063c20e5fe2), [LangGraph Issue #4987 — checkpoint_id update](https://github.com/langchain-ai/langgraph/issues/4987), [The Checkpoint Bloat — Mitigating Write-Amplification (Azguards)](https://azguards.com/distributed-systems/the-checkpoint-bloat-mitigating-write-amplification-in-langgraph-postgres-savers/)_

### Subgraph Composition Pattern

Per Decision 3 (cage avoidance) + Decision 4 (scaffold):

- **Default = isolated state.** Each specialist subgraph has its own state schema. Marcus's supervisor node transforms parent state → `MarcusEnvelope` (specialist input), invokes specialist subgraph, transforms `SpecialistReturn` back into parent state. Specialists never see Marcus's full state.
- **Shared state keys reserved for genuinely cross-cutting fields**: `run_id`, `thread_id`, `pipeline_manifest_version`, `pack_version`, `current_step`, `artifacts_index`. These ride the supervisor's parent state and are *copied* into the envelope, never *referenced* into the subgraph.
- **Fan-out via `Send`** for parallel specialist dispatch (e.g., parallel cluster generation in §6.3). Aggregation via Python reducer node, not subgraph return path (Issue #2581 workaround from Step 3).

### Streaming Pattern

`astream_events(version="v2")` streams every state transition. The IDE-as-client (per Decision 1 Stage 2 + Step 3 MCP recommendation) subscribes via SSE; operator sees specialist progress in real-time. Streaming + checkpointing combine to give the always-know-where-Marcus-is property that today only exists inside the live Claude Code conversation.

### Observability Pattern (LangSmith-as-Evidentiary-Substrate)

Every node emits a LangSmith trace tagged with: `run_id`, `thread_id`, `gate_caller`, `specialist_id`, `quality_preset`, `pipeline_step`, `pack_version`. Trace tags become the search axis for:

- Reviewers in party-mode and code-review gates (Decision 3 — gates consume traces, not just diffs)
- Token/cost accounting per run, per step, per specialist (six-axis token-efficiency lever)
- Cache-hit-rate measurement for prompt-caching middleware effectiveness
- Cross-trial comparison (compare two trial runs of same `run_id` shape across forks)
- Receipt cross-reference: every receipt links to its trace ID; every trace is reachable from its receipt

### Dev-Graph Separation Pattern (Cora ≠ Marcus, substrate invariant #15)

Substrate digest §8 invariant #15: Marcus owns production (G0→G6); Cora owns dev-session (START/WRAPUP, harmonization, hot-start-pair). Two lanes do not overlap.

Architectural form: **two distinct compiled graphs**, two distinct thread namespaces.

- `runtime/graphs/v42/marcus_production_graph.py` — the 15-step production spine + Marcus supervisor + specialist subgraphs. Threads keyed off `run_id`.
- `runtime/graphs/dev_orchestration/cora_dev_graph.py` — session-boundary choreography, story creation, dev-story execution, code-review, validator gates, retrospective. Threads keyed off `dev_session_id`.

The two graphs share only: the `_bmad/memory/` sanctum tree, the deferred-inventory file, and the SESSION-HANDOFF / next-session-start-here pair (the substrate's existing handoff contract). They do not share checkpointer threads, do not share runtime state.

**Why this matters**: separating dev-graph from production-graph keeps each focused, lets them evolve independently, and means a dev-session crash cannot corrupt a production run. Also means the Lesson-Planner governance validator gate (currently a dev-time CLI tool) becomes a **dev-graph node**, not a production-graph node.

---

### Cross-Architectural Analysis — Six-Axis Mapping (Architectural Layer)

| Axis | Architectural lever |
|---|---|
| Model use | Plan-and-Execute reduces Opus calls to plan-points; specialist subgraphs use Sonnet/Opus per `quality_preset`; tool-calling wrappers Haiku |
| Token efficiency | Sanctum cold-load + prompt-cache prefix; isolated subgraph state keeps envelopes small; `DecisionCard`s curate gate payloads (Decision 3a) |
| Speed | Parallel `Send` fan-out for multi-specialist work; streaming via `astream_events`; Plan-and-Execute fewer LLM calls than ReAct |
| Flexibility | Manifest-as-graph-config — pipeline shape changes without code edits; specialist subgraphs swappable behind envelope contract; fork-from-checkpoint for what-if exploration |
| Quality | Gate-as-`interrupt()`-node enforces operator authority architecturally; LangSmith traces as evidentiary substrate for party-mode + code-review; receipts SHA256-signed |
| Reliability | Two-layer retry (HTTP + node); checkpoint-as-compensation; idempotent specialist invocation; frozen-graph-version pattern for audit reproducibility |

### Architectural Patterns Map (Pattern → Substrate Invariant Preserved)

| Pattern | Substrate invariant preserved (digest §8) |
|---|---|
| Hybrid Sequential-Spine + Supervisor | #4 (15-gate manifest-driven topology), #2 (Marcus-only orchestration) |
| Plan-and-Execute (default) + ReAct (explore) | #1 (Marcus stateless orchestrator), Decision 3 (cage avoidance) |
| Gate-as-`interrupt()`-Node | #4 (HIL-paused gates), #6 (3-layer code review), Decision 3a (operator authority) |
| Sanctum Cold-Start (file-backed fresh-read) | #1 (Sacred-Truth fresh-read) |
| Manifest-as-Graph-Config | #3 (Pipeline Lockstep deterministic neck), #10 (frozen-at-ship) |
| Learning-Event Side-Effect | #9 (event ledger emission at G2C/G3/G4) |
| Frozen-Graph-Version | #10 (frozen-at-ship pack discipline), #14 (deferred inventory continuity) |
| Two-Layer Retry + Idempotent Specialists | #6 (correctness review), #11 (K-floor test discipline) |
| Time-Travel + Fork (Trial-Run Discipline) | #9 (learning ledger), #14 (deferred inventory across runs) |
| Subgraph Composition (isolated state) | Decision 3 (cage avoidance), Decision 4 (scaffold) |
| Streaming + Observability | Decision 1 Stage 2 (IDE-as-client) |
| Dev-Graph Separation (Cora ≠ Marcus) | #15 (lane responsibility) |

### Open Questions Surfaced by Step 4 (deferred to Step 5)

1. **Postgres checkpointer cleanup policy** — what TTL/retention rules; does `EncryptedSerializer` impose extra storage cost; how to integrate with frozen-graph-version's audit guarantee
2. **Time-travel checkpoint_id update bug ([Issue #4987](https://github.com/langchain-ai/langgraph/issues/4987))** — verify workaround stable in current LangGraph version; if not, design around or wait for fix
3. **Pydantic ValidationError + RetryPolicy gotcha ([Issue #6027](https://github.com/langchain-ai/langgraph/issues/6027))** — finalize wrap-and-route pattern for envelope_intake / compose_return
4. **Manifest-driven graph rebuild automation** — what triggers rebuild (file watcher? CI? operator command?); how does Cora's block-mode hook integrate
5. **LangGraph Platform vs self-hosted** — still deferred from Step 3; resolve in Step 5 with cost/control trade-off analysis
6. **Slab-4 dev-graph scope** — exactly which dev-time governance becomes nodes in Cora's graph vs stays as CLI tools
7. **Sanctum-to-prompt-cache TTL alignment** — when sanctum mutates, what's the cache invalidation latency; do we need explicit invalidation or is TTL OK

## Implementation Approaches and Technology Adoption

> *Note on adapted structure*: Standard template sections (Team Organization, generic CI/CD, generic DevOps) are present but tightened to this APP's reality (single-operator + small dev team + sanctum + Pipeline Lockstep). Major content: resolutions to Step 3/4 open questions, deployment-shape decision, persistence ops, testing strategy, economics measurement, per-slab recipe, migration timeline, risks, cost optimization, skill requirements.

### Resolutions to Open Questions from Steps 3 & 4

Each open question now resolved (or deferred with stated reason):

| # | Question | Resolution |
|---|---|---|
| 3.1 | Specialist boundary granularity (subgraph vs MCP tool vs Python function) | **Subgraph** if multi-turn reasoning; **MCP tool** if single-call action; **Python function** if pure computation. Codified in `bmad-create-specialist` generator decision tree. |
| 3.2 | Fan-out/subgraph aggregation bug ([Issue #2581](https://github.com/langchain-ai/langgraph/issues/2581)) workaround | Aggregate inside a Python reducer node consuming individual subgraph returns; bypass the subgraph-return aggregation path until upstream fix |
| 3.3 | MCP server contract for IDE bridge | One MCP tool per top-level Marcus operation (start_run, resume_run, fork_run, list_active_runs); one MCP resource per active thread (read-only state inspection); receipts as MCP resources for audit |
| 3.4 | LangGraph Platform vs self-hosted | **Self-hosted** — see §LangGraph Platform vs Self-Hosted Decision below |
| 4.1 | Postgres cleanup policy + serializer cost | Custom TTL via scheduled cleanup job; `JsonPlusSerializer` + ormsgpack as default; `EncryptedSerializer` only for sanctum-bond fields if/when needed; archive to cold storage for frozen-graph-version audit (see §Persistence Operations) |
| 4.2 | Time-travel checkpoint_id update bug ([Issue #4987](https://github.com/langchain-ai/langgraph/issues/4987)) | Manual checkpoint_id tracking in supervisor wrapper; revisit at next LangGraph release |
| 4.3 | Pydantic ValidationError + RetryPolicy ([Issue #6027](https://github.com/langchain-ai/langgraph/issues/6027)) | Wrap Pydantic validation in try/except in `envelope_intake` and `compose_return`; return structured error state via Command; supervisor routes to retry or interrupt |
| 4.4 | Manifest-driven graph rebuild automation | CI-triggered on PR touching trigger paths; local pre-commit hook that runs L1 check + regenerator; Cora's pre-closure hook is the safety net |
| 4.5 | LangGraph Platform vs self-hosted | (same as 3.4) |
| 4.6 | Slab-4 dev-graph scope precision | All dev-time governance becomes Cora-graph nodes: story creation, story validation, code-review (3-hunter), Lesson-Planner validator, L1 lockstep check, retrospective, deferred-inventory consultation |
| 4.7 | Sanctum ↔ prompt-cache TTL alignment | Default 5m TTL on `AnthropicPromptCachingMiddleware`; explicit invalidation hook on sanctum file mutation via file watcher; natural TTL expiry as fallback |

### LangGraph Platform vs Self-Hosted — Decision: **Self-Hosted**

LangGraph offers three deployment shapes in 2026:

| Tier | Cost | Hosting | Fit for this APP |
|---|---|---|---|
| **Open-source self-hosted** | Free (MIT) | Your environment | ★★★ — full control, fits sanctum file-backed model, fits IDE/MCP/FastAPI bridge, fits operator's customization needs |
| **Plus (managed cloud SaaS)** | Metered usage; up to 100K nodes/month free | LangChain Cloud (US/EU residency) | ★ — managed convenience but creates external dependency for production runs; doesn't fit local-first sanctum-backed model |
| **Enterprise** | Premium pricing | Cloud / hybrid VPC / fully self-hosted with platform features | ★★ — flexibility but premium cost; only justified if multi-tenant or compliance-grade hosting required |

**Decision: open-source self-hosted** with optional **LangSmith for observability** (separate, lower-stakes commitment).

**Why self-hosted wins for this APP:**

- **Sanctum is file-backed and operator-curated** — Platform's managed memory features add no value when memory IS the file tree the operator authors and curates. Platform would create a sync layer between sanctum files and platform memory store; that's net additional complexity, not less.
- **Hybrid IDE-as-client / FastAPI / MCP bridge architecture (Decision 1 + Step 3)** is incompatible with the Plus plan's hosted invocation model in Stage 2. The IDE talks to a long-lived local service, not a cloud endpoint, until Stage 3 ships.
- **Bounded big-bang (Decision 2)** means we want full control over the runtime — Platform's opinionated abstractions become migration friction.
- **Cost discipline** — At single-operator scale, 100K nodes/month free tier on Plus is plausibly enough, but the pricing transitions to metered usage; for a 15-step pipeline × ~5 specialist invocations per step × multiple gates × multiple trial runs per day, node counts multiply quickly. Self-hosted on a modest VM costs ~$20–40/month all-in.
- **LangSmith remains a strong recommendation for observability** ($39/seat Plus or free tier with 5K traces/month). Trace evidence for party-mode and code-review gates is first-class value (Decision 3 / Step 4 §Observability). LangSmith is **functionally separable** from LangGraph Platform — pick one without the other.

**Re-evaluation triggers** (revisit Platform if any fire):
- Multi-operator concurrent production runs (today: single operator)
- Compliance regime requires platform-managed audit log beyond LangSmith
- Operational burden of self-hosted (Postgres maintenance, cleanup jobs, etc.) exceeds dev capacity
- Specific Platform-only feature becomes critical (e.g., advanced cron scheduling with platform-managed retries)

_Sources: [LangGraph Pricing Guide (ZenML)](https://www.zenml.io/blog/langgraph-pricing), [LangGraph Platform Pricing (agentsapis)](https://agentsapis.com/langchain/langgraph-pricing/), [LangGraph Pricing 2026 (ShipSquad)](https://shipsquad.ai/pricing/langgraph), [LangSmith Pricing 2026 (MarginDash)](https://margindash.com/langsmith-pricing), [LangSmith Plans and Pricing (LangChain)](https://www.langchain.com/pricing)_

### Persistence Operations — Checkpointer Cleanup, Retention, Audit

**Single Postgres database** (single instance, separate schema for `production_graph` thread store and `dev_graph` thread store; isolation per Step 4 §Dev-Graph Separation).

**Connection management**: Use `ConnectionPool` (psycopg) not raw `Connection` — long-running graphs hit connection timeouts otherwise.

**TTL + retention strategy** (custom — LangGraph Platform's built-in TTL is not available in self-hosted OSS):

| Thread class | Cleanup rule | Implementation |
|---|---|---|
| Active production runs (`thread_id` keyed off `run_id`) | No cleanup while run is open | Status column on a `runs` index table; cleanup excludes `status='active'` |
| Closed production runs ≤ 30 days | Retain in Postgres (replay/fork still possible) | Default — no action |
| Closed production runs > 30 days | Archive to cold storage (S3 / disk) as compressed checkpoint export; delete from Postgres | Scheduled job; export uses `JsonPlusSerializer` round-trip + gzip |
| Frozen-graph-version archives | Permanent — keep Postgres-side index entry pointing to cold storage | Audit guarantee |
| Dev sessions (`dev_session_id`) | Retain ≤ 14 days, then delete (no audit requirement) | Scheduled job |
| Failed/orphaned threads (no resume in 7 days) | Delete | Scheduled job |

**Scheduled job**: implement as a Cora-graph capability or a standalone `scripts/utilities/checkpoint_cleanup.py` cron entry. Write unit tests against fixture threads.

**Serializer**: Default `JsonPlusSerializer` + ormsgpack handles datetimes/enums/UUIDs cleanly; works with Pydantic v2 state schemas. **`EncryptedSerializer`** reserved for sanctum-derived state fields containing operator-personal data (BOND.md operator preferences) — opt-in per state-schema field via `Annotated[..., Encrypt()]`.

**Storage cost (rough)**: each checkpoint at ~10–50 KB for typical state; 15-step run × ~3 checkpoints per step × 2 trials/day × 30 days × 50 KB ≈ 135 MB/month. Postgres storage cost is negligible for a single-operator deployment.

_Sources: [Issue #1138 — Postgres database growing unbounded](https://github.com/langchain-ai/langgraphjs/issues/1138), [Discussion #4400 — Archiving Postgres Checkpointer](https://github.com/langchain-ai/langgraph/discussions/4400), [langgraph-checkpoint-postgres (PyPI)](https://pypi.org/project/langgraph-checkpoint-postgres/), [LangGraph TypeScript Persistence Guide](https://langgraphjs.guide/persistence/), [Understanding Checkpointers, Databases, API Memory and TTL (LangChain Support)](https://support.langchain.com/articles/6253531756-understanding-checkpointers-databases-api-memory-and-ttl?threadId=285c524c-7b58-44e4-89ab-210e6393cc7e)_

### Testing Strategy — Contract Tests + Subgraph Mocking + Trial-Replay Tests

LangGraph testing in 2026 is intentionally framework-light (no first-class testing framework yet — see [Issue #34810](https://github.com/langchain-ai/langchain/issues/34810)); production approach is **pytest + targeted mocking + LangSmith Pytest integration**. For this APP's scaffold-driven design (Decision 4), tests partition cleanly into **four layers**:

#### Layer 1 — Per-Node Unit Tests (no graph)

Each scaffold node tested in isolation. `envelope_intake`, `cold_load`, `reason`, `act`, `perceive`, `assess`, `compose_return`, `emit_receipt`, `interrupt_for_operator`. Mock LLM calls (`unittest.mock.patch` on `ChatAnthropic`); mock MCP tool clients; assert state transitions.

#### Layer 2 — Specialist Subgraph Contract Tests

Each specialist subgraph compiled with `InMemorySaver`; envelope-in / return-out contract tests:
- Happy path: golden envelope → expected return shape
- Edge cases: malformed envelope rejected at `envelope_intake`; downstream node failures route to `interrupt_for_operator`
- Quality preset behavior: `explore` vs `production` produce different model-call patterns (verified via mock call counts)
- Sanctum cold-load integrity: `test_sanctum_load.py` — INDEX/PERSONA/CREED/BOND/MEMORY/CAPABILITIES batch order respected

Subgraph tested **in isolation** — supervisor not invoked. Use LangGraph's documented per-test-recompile pattern: create graph with new checkpointer instance per test for clean state.

#### Layer 3 — Supervisor + Subgraph Integration Tests

Marcus supervisor + 1–N specialist subgraphs together. Specialists' tool-layer mocked (no live API calls); reasoning layers run real (Sonnet) on a fixed seed where possible. Verify:
- Routing: Marcus dispatches the right specialist for a given envelope
- Aggregation: parallel `Send` fan-out reduces correctly via Python reducer (Issue #2581 workaround verified)
- Gate behavior: `interrupt()` fires at expected steps; `Command(resume=...)` continues correctly
- Time-travel: replay from checkpoint produces equivalent state (modulo LLM stochasticity)

#### Layer 4 — Trial-Replay Regression Tests

The strongest test for this APP. After a successful tracked trial run (e.g., C1-M1-PRES-20260419B), the run's checkpoint thread becomes a **golden replay fixture**. CI runs `replay(thread_id=<golden>)` against the current graph version and asserts:
- Same gate sequence fired
- Same receipts emitted (modulo timestamp)
- Same learning events
- Same final pack output (byte-identical via deterministic generator)

Regressions detected by trial-replay catch the kind of cross-cutting failures unit tests miss. **This pattern subsumes the existing meta-test discipline** (`15-1-lite-marcus.md` from substrate digest §4) — that meta-test becomes a trial-replay test in the LangGraph world.

#### LangSmith Pytest integration

LangSmith provides Pytest evaluation framework integration; assert against expected behaviors with bespoke evaluators (semantic checks on Marcus's planning, fidelity checks on Vera's verdicts). Bridges the gap between deterministic unit tests and the inherent stochasticity of LLM nodes.

_Sources: [Test — LangChain docs](https://docs.langchain.com/oss/python/langgraph/test), [Issue #34810 — first-class testing framework](https://github.com/langchain-ai/langchain/issues/34810), [Unit Testing LangGraph (Medium)](https://medium.com/@anirudhsharmakr76/unit-testing-langgraph-testing-nodes-and-flow-paths-the-right-way-34c81b445cd6), [Mocking nodes with pytest (Discussion #3204)](https://github.com/langchain-ai/langgraph/discussions/3204), [LangGraph Testing Framework (DeepWiki)](https://deepwiki.com/langchain-ai/new-langgraph-project/3.2-testing-framework), [Building LLM agents to validate tool use (CircleCI)](https://circleci.com/blog/building-llm-agents-to-validate-tool-use-and-structured-api/), [LangGraph Systems Inspector (Medium)](https://medium.com/@nirdiamant21/langgraph-systems-inspector-an-ai-agent-for-testing-and-verifying-langgraph-agents-a8d1c2400d60)_

### Prompt-Caching Activation at Scale + Economics Measurement

Decision 3 + Step 2 § Model Integration established `AnthropicPromptCachingMiddleware` as the single largest token-economics lever. Step 5 implementation specifics:

**Cache structure per specialist** (cached prefix, then variable suffix):

```
[CACHED PREFIX — refresh per 5m TTL]
  System prompt (specialist persona + creed + capabilities)
  References load list (api-reference, prompt-patterns, style-bible, golden examples)
  MEMORY.md (curated lessons)
  BOND.md (operator preferences)
[VARIABLE SUFFIX — fresh per invocation]
  envelope.typed_intent
  envelope.context (run-scoped excerpts only)
  prior reason/act/perceive/assess turns this invocation
```

The split is engineered so the cached prefix is large (most of the cost) and variable suffix is small (per-invocation cost). Per 2026 Anthropic pricing: cache write = 1.25× input tokens (5m TTL) or 2× (1h TTL); cache read = **0.1× input tokens** — i.e., a cached prefix costs 10% of the uncached price on every reuse.

**Reported real-world impact**: 85–90% reduction on cached input; case studies show $720/month → $72/month after activating prompt caching on agent system prompts.

**Measurement is mandatory** — without telemetry, you can't tell if caching is actually saving money:

- **Cache hit rate metric** per specialist per quality_preset → logged to LangSmith trace tags AND aggregated in a per-run telemetry dashboard
- **Cache write vs cache read separation** — if writes >> reads, the cache isn't being amortized (TTL too short, prefix changing between calls, sanctum mutation invalidating)
- **Per-specialist token cost** rolled up per-run for the operator's economic visibility (becomes part of Desmond's run-scoped operator brief at §14.5)

**Implementation hook**: `compose_return.model_calls_made` field (per Decision 4 contract) accumulates `(input_tokens, cached_tokens, cache_hit_rate)` per call; rolls up at run close into the receipts ledger.

**TTL choice**: Default to **5m** (cheaper writes); switch to **1h** for specialists that are invoked many times per run with stable persona (Marcus supervisor, Gary on multi-cluster runs). Quality_preset extension: `production` and `regulated` get 1h TTL to maximize prefix amortization across long runs.

_Sources: [Anthropic API Pricing 2026 (Finout)](https://www.finout.io/blog/anthropic-api-pricing), [Anthropic Prompt Caching 2026 — Cost, TTL, Latency (AICheckerHub)](https://aicheckerhub.com/anthropic-prompt-caching-2026-cost-latency-guide), [Cut Anthropic API Costs 90% with Prompt Caching (Markaicode)](https://markaicode.com/anthropic-prompt-caching-reduce-api-costs/), [Build Anthropic Dashboard 2026 (Reflex)](https://reflex.dev/blog/build-dashboard-with-anthropic/), [Prompt caching — Claude API Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching), [Pricing — Claude API Docs](https://platform.claude.com/docs/en/about-claude/pricing), [Prompt Caching Is a Must — $720→$72 (Medium)](https://medium.com/@labeveryday/prompt-caching-is-a-must-how-i-went-from-spending-720-to-72-monthly-on-api-costs-3086f3635d63)_

### Per-Slab Implementation Recipe

Each slab below names: scope, deliverables, **acceptance criteria** (the "done" definition for the slab's BMAD code-review + party-mode gates), and **dependencies on prior slabs**.

#### Slab 1 — Substrate (foundation)

**Scope**: Stand up the runtime in Stage-2 shape (per Decision 1 — skip Stage 1 transitional). No specialist migrated yet.

**Deliverables**:
- `runtime/` package skeleton with `runtime/graphs/`, `runtime/state/`, `runtime/scaffold/`, `runtime/persistence/`, `runtime/observability/`
- `PostgresSaver` checkpointer wired with `ConnectionPool`; `JsonPlusSerializer`; cleanup script with cron entry
- `AnthropicPromptCachingMiddleware` integrated; default 5m TTL
- LangSmith integration with run_id/thread_id/specialist_id/gate_caller/quality_preset/pipeline_step/pack_version trace tags
- Persistent local service (FastAPI + MCP server) — IDE↔runtime bridge; SSE streaming via `astream_events(version="v2")`
- State schema base classes (Pydantic v2): `RunState`, `MarcusEnvelope`, `SpecialistReturn`, `DecisionCard`, `Advisory`, `EvidenceRef`, `ReceiptID`
- Empty `production_graph` (manifest-loaded but specialists are stubs returning `{"status": "not_implemented"}`)
- Empty `dev_graph` shell

**Acceptance criteria**:
- Empty production graph runs end-to-end through 15 manifest steps + gate `interrupt()`s; operator can approve/edit/reject every gate
- Resume from checkpoint after operator decision works; fork from prior checkpoint works
- LangSmith trace appears for every node call, properly tagged
- Prompt-cache hit rate ≥ 80% on the second invocation of any persona (proves middleware works)
- All BMAD code-review hunters PASS; party-mode green-light

**Depends on**: Nothing (this is the start).

#### Slab 2 — Specialists (parallel-mass migration)

**Scope**: Build the specialist scaffold; migrate all 17 existing specialists; instantiate Wondercraft pilot stub.

**Deliverables**:
- `runtime/scaffold/specialist/` — the canonical 9-node skeleton with per-node default behaviors
- `bmad-create-specialist` skill (lays down skills + sanctum + runtime + tests trees per Decision 4)
- For each of 17 existing specialists (parallel-wave migration in dependency order: Dan/Texas/ElevenLabs first to harden scaffold, then Gary/Vera/Quinn-R/Compositor/CD adjacent, then bulk of asset-production specialists):
  - **Two-axis migration per specialist** (Decision 4): legacy → sanctum + IDE → LangGraph subgraph
  - Sanctum populated from legacy SKILL.md content (the operator's tribal knowledge captured into L1–L6 expertise stack)
  - Contract tests, golden tests, integration tests
- **Wondercraft pilot specialist** — first plug-and-play instantiation; full L0+L7+L1/L2/L5 seeded; L3/L4/L6 grow from use
- **`specialist-anti-patterns.md`** new artifact + four-file-lockstep tooling mirror

**Acceptance criteria**:
- Every specialist runs end-to-end through scaffold against its contract tests
- Each specialist's invocation produces a SHA256-signed receipt + LangSmith trace + token-cost telemetry
- Specialist sanctum cold-load integrity test passes (INDEX → PERSONA → CREED → BOND → MEMORY → CAPABILITIES order respected)
- Wondercraft pilot runs end-to-end against live Wondercraft API in one integration test; produces a valid podcast artifact
- All specialists invocable from CLI/CI/MCP — no IDE dependency
- All BMAD code-review hunters PASS per specialist; party-mode green-light at end of slab

**Depends on**: Slab 1 complete.

#### Slab 3 — Marcus Supervisor + Routing

**Scope**: Build Marcus's supervisor subgraph; wire it to dispatch all 17 specialists + Wondercraft; enable end-to-end APP run.

**Deliverables**:
- Marcus's supervisor subgraph (Plan-and-Execute default, ReAct on `explore` preset)
- Marcus sanctum populated (already exists — port from current `_bmad/memory/bmad-agent-marcus/`)
- Two-axis handshake (execution mode + quality preset) as graph-input
- Specialist routing logic via `specialist-registry.yaml` resolver (existing artifact, now driving `Send` dispatch)
- Marcus's CD envelope special-case (Dan never operator-facing; only Marcus-envelope-callable)
- Marcus's gate-payload curation (DecisionCards for every gate)

**Acceptance criteria**:
- End-to-end APP run from §01 → §15 completes against the empty/stub artifact-production lanes (specialists return placeholder content but real signatures/contracts)
- Operator approve/edit/reject at every gate with live `DecisionCard`s
- Quality may be lower than primary repo (acceptable — slab 5 closes parity)
- Marcus's plan-and-execute reasoning visible in LangSmith trace; matches manifest step ordering
- Token cost per run measured and reported in operator brief

**Depends on**: Slabs 1, 2 complete.

#### Slab 4 — Pipeline Lockstep + Governance Gates + Dev-Graph

**Scope**: Wire all governance gates; build Cora's dev-graph; pipeline-manifest CI integration.

**Deliverables**:
- Pipeline Lockstep block-mode hook → CI step on PRs touching trigger paths; runs L1 check + regenerator; non-zero exit blocks merge
- Dev-graph (Cora) — all dev-time governance as nodes: story creation, story validation, code-review (3-hunter), Lesson-Planner validator, retrospective, deferred-inventory consultation
- Party-mode roundtable as `interrupt()` node with parallel-`Send` to roster specialists; aggregation in reducer
- Frozen-graph-version pattern wired (`runtime/graphs/v42/` first version; promotion-to-frozen ceremony defined)
- Learning-event side-effect emitters at G2C/G3/G4 fully wired (append-only ledger backend)
- Pydantic ValidationError wrap-and-route pattern (Issue #6027 workaround)

**Acceptance criteria**:
- Block-mode hook catches a deliberate manifest-violating PR in CI; allows a clean PR
- Dev-graph runs a full story-cycle (CS → DS → CR → ER) against a test story
- Party-mode produces a multi-agent verdict; receipt logged
- Learning events from a tracked trial run land correctly in the ledger
- Lesson-Planner governance validator runs at story finalization + T1 in dev-graph

**Depends on**: Slabs 1, 2, 3 complete.

#### Slab 5 — Trial-Run Discipline + Replay UX + Observability Polish

**Scope**: Productionize the trial-run lifecycle; reach parity with primary repo's production capability.

**Deliverables**:
- Trial-replay regression test for C1-M1-PRES-20260419B (golden fixture, asserts byte-identical pack + same gate sequence + same learning events)
- Replay/fork UX in IDE (operator can browse past runs, resume from gate, fork to explore alternative)
- Per-run economics dashboard (token cost, cache hit rate, specialist-time breakdown) integrated into Desmond's §14.5 brief
- Sanctum invalidation hook on file-watcher (sanctum mutation → cache TTL refresh signal)
- Cold-storage archival of closed runs > 30 days
- Migration of remaining historical artifacts
- **Acceptance preflight against primary repo's production capability** — head-to-head trial run; LangGraph version produces equivalent or superior output

**Acceptance criteria**:
- New tracked trial run completes with parity-or-better against primary repo
- Operator can fork a closed run from any gate and produce a divergent valid run
- All five preflight flags from Lesson-Planner MVP F4 ratification (substrate digest §6) addressed in LangGraph form
- Backport policy formally retired; primary repo continues but is no longer ahead

**Depends on**: Slabs 1, 2, 3, 4 complete.

### Migration Timeline + Critical Path

**Estimate (rough; refined in PRD with operator input)**:

| Slab | Wall-clock estimate | Critical path |
|---|---|---|
| 1 | 2–3 weeks | LangGraph + Postgres + middleware + LangSmith setup; sanctum-aware persistence; FastAPI/MCP bridge; Pydantic state base classes |
| 2 | 4–6 weeks | Scaffold first (1 wk); harden via 3 specialists (1 wk); parallel migrate remaining 14 (2–3 wk); Wondercraft pilot (3–5 days). Parallelizable across dev capacity. |
| 3 | 2 weeks | Marcus supervisor + plan-and-execute reasoning + routing; gate DecisionCards; first end-to-end run |
| 4 | 2–3 weeks | Block-mode hook to CI; dev-graph (Cora); party-mode as interrupt; frozen-graph-version ceremony; learning-event ledger |
| 5 | 2 weeks | Trial-replay test; replay/fork UX; economics dashboard; cold-storage archival; head-to-head parity validation |
| **Total** | **12–16 weeks** (with single dev focus) | Single critical path Slab 1 → 2 → 3 → 4 → 5; only intra-Slab-2 parallelism |

**Sensitivity**: Slab 2 dominates the timeline. Acceleration levers: (a) more dev capacity in slab 2 (truly parallelizable across specialists once scaffold is hard); (b) defer 4–5 lower-priority specialists from slab 2 to a slab-2-tail wave (still ship slab 3+ on the core 12 specialists); (c) defer Wondercraft to slab 5.

### Risks + Mitigations

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Sanctum-pattern migration of existing specialists is harder than estimated (tribal knowledge capture is open-ended) | Medium | Medium | Cap each specialist's sanctum-migration scope; "good-enough" L4/L6 acceptable at slab-2 close; growth via use post-slab-5 |
| LangGraph Issue #4987 (checkpoint_id) or #6027 (Pydantic+RetryPolicy) escalates / new framework bug surfaces | Medium | Medium | Workarounds documented; pin LangGraph version per frozen-graph-version; upgrade ceremony required for new pinned version |
| Primary repo continues to mature in parallel; valuable improvements pile up to forward-port | High | Low (by Decision 2 design) | Forward-port post-slab-5 only; deferred-inventory tracks pending forward-ports |
| Plan-and-Execute Marcus produces lower-quality plans than current IDE-Marcus on edge cases | Medium | Medium | ReAct fallback on `explore` preset; trial-replay regression catches regressions; quality_preset upgrade path |
| Prompt-caching cache hit rate disappoints (sanctum mutations too frequent, prefix design fragmented) | Low | High (token economics) | Measurement-first; redesign cache structure if hit rate < 70% on production preset |
| Postgres operational burden (cleanup jobs, schema migrations) > dev capacity | Low | Medium | Standalone cleanup script with tests; LangGraph upgrade ceremony documented; consider managed Postgres if it becomes painful |
| Operator-direct specialist invocation (e.g., "talk to Texas") creates SPOT bypass during migration | Medium | Medium | Slab 2 acceptance criterion explicit: even ad-hoc specialist invocations route through Marcus envelope; operator-direct is a hard violation |
| Bounded big-bang clone is "broken end-to-end for weeks" creates anxiety | Medium | Low (managed by Decision 2) | Slab acceptance criteria are public; primary repo carries production; weekly status update to operator |
| Wondercraft API contract changes mid-migration | Low | Low | Pilot specialist API is well-documented; treat as integration test red-flag if it changes |

### Cost Optimization Strategy (Six-Axis Economics)

Compounded across the migration, the cost story per axis:

| Axis | Strategy | Expected payoff |
|---|---|---|
| Model use | Plan-and-Execute reduces Opus calls; Sonnet for specialist reasoning; Haiku banned from `reason` nodes per Decision 3 | 30–50% Opus calls vs naive supervisor pattern |
| Token efficiency | `AnthropicPromptCachingMiddleware` on every long-prefix specialist + Marcus; sanctum-as-cache-prefix; envelope context = curated excerpts not full state; `DecisionCard`s for gate payloads | **80–90% input-token cost reduction** on cached prefix (industry-typical for this prefix shape) |
| Speed | `Send` parallel fan-out for multi-specialist work; streaming via `astream_events`; Plan-and-Execute fewer LLM calls than ReAct | 2–4× faster on multi-cluster runs; sub-second perceived latency on streaming |
| Flexibility | Scaffold-instantiated specialists < 1 dev-day; manifest-as-config for pipeline shape; fork-from-checkpoint for what-if | New specialist time-to-deploy: weeks → 1 day |
| Quality | LangSmith trace evidence at gates; receipts SHA256-signed; trial-replay regression tests; specialist anti-patterns catalog growing four-file-lockstep | G6 finding rate drop after 3 stories on scaffold |
| Reliability | PostgresSaver checkpointing; two-layer retry; idempotent specialists; frozen-graph-version pattern | <1% trial-run failures from infrastructure; 100% reproducibility on closed trial runs |

### Skill Requirements + Team Organization

**Required dev skills** (in declining order of demand during migration):

1. **Python 3.12+ + Pydantic v2** — substantial. Schema discipline already in-house (Lesson-Planner MVP).
2. **LangGraph + LangChain** — new for the team; ramp-up via slab 1 substrate work; first production-grade muscle by end of slab 2.
3. **PostgreSQL operational** — basic (connection pooling, cleanup jobs, schema migrations). Not deep DBA work.
4. **FastAPI + SSE streaming** — moderate. Standard Python web work.
5. **MCP server authoring** — light. Existing IDE↔MCP infrastructure means patterns are familiar.
6. **Anthropic API + prompt-caching mechanics** — moderate. Critical to slab 1 / slab 2 success.
7. **LangSmith trace authoring + evaluator framework** — moderate; nice-to-have for gate evidence quality.

**Team organization** (single-operator + small-dev assumption):
- **Operator**: directs migration via Marcus; reviews at every party-mode and code-review gate; final say on slab promotion
- **Dev** (1–2): executes slab work; pairs with operator on architectural decisions; runs validators and tests
- **Cora-or-equivalent**: dev-session governance (eventually a sub-graph; today a skill)
- **No dedicated SRE / DBA needed** at single-operator scale

### Implementation Roadmap (synthesized)

1. **Now** → Complete this research (Step 6 synthesis next).
2. **Next BMAD step** → `bmad-create-prd` (migration PRD) using this research as primary input. PRD scopes the slabs as initial PRD sections; locks Decisions 1–4; declares the 12-pattern architectural map as the architectural baseline; pins the LangGraph + Postgres + MCP + LangSmith + self-hosted technology stack.
3. **PRD validation** → `bmad-validate-prd`.
4. **Architecture phase** → `bmad-create-architecture` with this research + PRD as inputs; produces the C4-style architecture diagram, formal contract definitions, frozen-graph-version directory layout, dev-graph specification.
5. **Epics + stories phase** → `bmad-create-epics-and-stories`; each slab becomes 1–2 epics; per-specialist migration in slab 2 becomes a story per specialist (parallelizable).
6. **Implementation readiness check** → `bmad-check-implementation-readiness`.
7. **Implementation** → standard SP → CS/VS → DS → CR → ER per slab/epic; party-mode at slab boundaries; trial-replay regression test gates each slab close.

### Technology Stack Recommendations (final)

| Layer | Selection | Rationale |
|---|---|---|
| Runtime framework | **LangGraph (OSS, latest stable pinned per frozen-graph-version)** | Decision 4; Step 4 patterns |
| Component library | **LangChain (`langchain-anthropic` + `langchain-mcp-adapters`)** | Step 2 + 3 |
| State schema | **Pydantic v2** with discipline checklist | Decision 4 + substrate §5 |
| Persistence | **`langgraph-checkpoint-postgres` + `JsonPlusSerializer` + `EncryptedSerializer` selectively** | Step 2 + Step 5 §Persistence Operations |
| Database | **Single PostgreSQL** (separate schemas for production + dev graphs) | Step 5 §Persistence Operations |
| Model client | **`ChatAnthropic` + `AnthropicPromptCachingMiddleware`** (5m TTL default; 1h on production preset) | Step 2 + Step 5 §Prompt-Caching |
| Tool surface | **MCP via `langchain-mcp-adapters`** | Step 3 + Decision 4 (L7 expertise layer) |
| Bridge protocol | **MCP server (primary) + FastAPI (escape hatch)**; **NOT LangServe** | Step 3 |
| Streaming | **`astream_events(version="v2")` + SSE** | Step 4 |
| Observability | **LangSmith** (free tier sufficient initially; $39/seat Plus when traces > 5K/month) | Step 4 + Step 5 |
| Deployment shape | **Self-hosted** OSS LangGraph; modest VM | Step 5 §LangGraph Platform vs Self-Hosted |
| Testing | **pytest + `unittest.mock` + `InMemorySaver` per-test + LangSmith Pytest integration** | Step 5 §Testing Strategy |

### Skill Development Requirements

Standing up the team for this migration:
- Slab 1 = LangGraph fundamentals + Pydantic-v2-state + Postgres checkpointer = 1 week intensive ramp-up before code starts
- Slab 2 = scaffold authoring + sanctum migration craft = the scaffold itself is the curriculum; first 3 specialists are the practice
- Ongoing = LangGraph release-tracking discipline (pin per frozen-graph-version; upgrade ceremony per Tier-2 / Tier-3 framework changes)

### Success Metrics + KPIs

Slab-by-slab measurable outcomes; tracked across slab close gates:

| KPI | Slab-1 baseline | Slab-5 target |
|---|---|---|
| End-to-end empty-graph run completes | TRUE | (still TRUE) |
| Specialist time-to-deploy (Wondercraft-class stub) | N/A | < 1 dev-day |
| Cache hit rate on production preset (median) | ≥ 80% | ≥ 90% |
| Token cost per trial run (vs current IDE-Marcus baseline) | Measured | ≥ 60% reduction |
| Trial-run reproducibility (replay produces same pack hash) | N/A | 100% |
| Operator decisions per trial run (gate count) | (manifest-defined) | unchanged (Decision 3a — operator authority preserved) |
| Operator cognitive load at gates (subjective; 1–5) | (current baseline) | improved (DecisionCard payload curation) |
| BMAD code-review MUST-FIX rate per specialist story | (current) | declining (scaffold + anti-patterns catalog learning curve) |
| Trial-replay regression test coverage | 0 closed runs | 100% of closed tracked trial runs |

### Open Questions Surfaced by Step 3 (deferred to Step 4 / 5)

1. **Specialist boundary granularity** — at what level does a specialist become a subgraph vs an MCP tool vs a Python function? Likely answer: subgraph if it has multi-turn reasoning; MCP tool if it's a single-call action; Python function if it's pure computation. Architecture phase to formalize.
2. **Fan-out/subgraph aggregation bug workaround** — Issue #2581 needs a documented workaround pattern in our slab 2 design.
3. **MCP server contract for IDE bridge** — what tools/resources does the runtime expose? Likely: one tool per top-level Marcus operation + one resource per active thread/checkpoint. Architecture phase to define.
4. **LangGraph Platform vs self-hosted** — defer evaluation to Step 5 (implementation research).

---

# Comprehensive Synthesis — Five Decisions, Five Slabs, One Sanctum

**A LangChain/LangGraph Migration Strategy for the Marcus-Orchestrated Production APP**

## Executive Summary

The course-DEV-IDE-with-AGENTS APP is, in its current shape, an unusually complete production system: a 15-step deterministic pipeline with 17 specialist agents orchestrated by a stateless-cold-start supervisor (Marcus), governed by an integrated Pipeline Lockstep regime, gated at every consequential step by Human-in-the-Loop (HIL) operator decisions, and disciplined at the schema layer by a four-file-lockstep enforcement of Pydantic v2 idioms. It just completed its first end-to-end tracked production run (C1-M1-PRES-20260419B). It is also entirely IDE-resident — the Claude Code conversation IS the runtime — which is the operating constraint this migration exists to relieve.

The proposed migration moves the runtime onto **LangChain + LangGraph** in a **bounded big-bang** style: the primary repo continues to carry production for the duration; the clone (this repo, `dev/langchain-langgraph-foundation`) diverges aggressively for **12–16 weeks** through five architectural slabs, accepting that the clone will be "broken end-to-end for weeks" as a managed state. The end-state is a long-lived **self-hosted LangGraph runtime** with the IDE acting as client (Stage 2), every specialist instantiated against a **9-node scaffold** with **sanctum-backed identity** (Marcus's pattern, propagated to all 17 + new stubs like Wondercraft), every gate manifesting as a checkpointed `interrupt()` node consuming a **curated DecisionCard** (operator decision authority preserved indefinitely), and prompt-caching middleware delivering **80–90% input-token cost reduction** on the cached sanctum/persona prefix. The migration's #1 quality risk — trading agent intelligence for graph determinism — is rejected as an architectural principle: the "LangChain cage" is named explicitly, and eight operating rules + five anti-patterns are codified to prevent it.

**Key Technical Findings:**

- **Hybrid Sequential-Spine + Supervisor Dispatcher** is the right top-level topology (the 15-step pipeline as the spine; Marcus as supervisor within steps; gates as `interrupt()` nodes between steps) — pure-supervisor or pure-sequential each fail load-bearing constraints
- **Plan-and-Execute** is Marcus's default reasoning loop (ReAct only on `explore` quality preset); reduces Opus calls and matches the manifest-driven structure naturally; reportedly 92% higher accuracy on long-horizon
- **Sanctum cold-start** as Sacred-Truth file-backed fresh-read every invocation, with prompt-caching middleware amortizing the read cost — preserves the existing identity-continuity model perfectly
- **MCP server as IDE↔runtime bridge** — reuses existing IDE↔MCP infrastructure; LangServe explicitly avoided (deprecated direction in 2026)
- **Specialist scaffold (9 fixed nodes)** + **sanctum-backed expertise stack (L0–L8 layered taxonomy)** is the plug-and-play architecture that makes Wondercraft/Canvas/Qualtrics target **<1 dev-day per stub** and brings consistency across all 17 existing specialists
- **Manifest-as-graph-config** turns the existing pipeline manifest into a compile-time topology source — Pipeline Lockstep regime becomes a CI gate at the framework level
- **Frozen-graph-version pattern** maps the existing frozen-at-ship pack discipline directly onto LangGraph; `runtime/graphs/v42/`, `v43/` siblings preserve audit reproducibility byte-for-byte
- **LangSmith as evidentiary substrate** for party-mode and code-review gates (reviewers consume traces, not just diffs)
- Self-hosted OSS LangGraph wins decisively over LangGraph Platform for this APP's shape (sanctum-file-backed memory, hybrid bridge architecture, single-operator scale, bounded-big-bang control needs)

**Top Strategic Recommendations (in order):**

1. **Adopt this research as primary input to a migration PRD.** The next BMAD step is `bmad-create-prd` — see §Recommended Next BMAD Step below.
2. **Lock the five foundational decisions** as PRD assumptions, not open questions: Stage-2 runtime independence target, bounded big-bang in the clone, no-LangChain-cage operating rules, HIL+SPOT preserved indefinitely, specialist scaffold with sanctum pattern.
3. **Plan slab-by-slab, not feature-by-feature.** Five slabs with concrete acceptance criteria (Substrate → Specialists → Marcus → Gates+Lockstep+Dev-Graph → Trial-Run+Polish). Slab 2 is the timeline pivot — parallelize specialist migration once scaffold hardens.
4. **Make `bmad-create-specialist` (the plug-and-play generator) the first deliverable inside Slab 2** — every subsequent specialist migrates faster because of it, and Wondercraft/Canvas/Qualtrics drop in at low cost.
5. **Treat prompt-caching activation, cache-hit-rate measurement, and trial-replay regression tests as Slab-1 acceptance criteria, not Slab-5 polish.** The economic and reliability story depends on these being right from day 1.

## Table of Contents

1. **§Technical Research Scope Confirmation** — Research topic, goals, optimization axes, hard constraints, methodology
2. **§Technology Stack Analysis** — LangGraph runtime + LangChain components; Pydantic v2 state; PostgresSaver checkpointing; AnthropicPromptCachingMiddleware; LangSmith observability; six-axis stack-layer mapping
3. **§Migration Strategy Decisions** — Five foundational decisions:
   - Decision 1: Runtime independence in stages (Stage 2 = persistent local service, IDE as client)
   - Decision 2: Bounded big-bang migration with primary repo as frozen reference; five architectural slabs
   - Decision 3: Reject the LangChain cage — eight operating rules + five anti-patterns
   - Decision 3a: HIL + Marcus-as-SPOT preserved; gate-payload curation reduces operator burden over time, never operator authority
   - Decision 4: Specialist Scaffold as Plug-and-Play Architecture (9 nodes + envelope/return contracts + sanctum-backed expertise stack)
4. **§Integration Patterns Analysis** — Output modality trade-offs (free-text default; structured-output at boundaries; tool-calling for actions); inter-subgraph communication (isolated state default + Send fan-out); MCP adapters; human-in-loop interrupts; IDE↔runtime protocol decision (MCP primary + FastAPI escape hatch); streaming
5. **§Current APP State — Substrate Digest** — Marcus SPOT shape, 17-specialist registry, gate inventory, Pipeline Lockstep regime concrete surface, schema discipline, active sprint+epic landscape, 15-step run lifecycle (C1-M1-PRES-20260419B trial), 15 load-bearing invariants, surprises
6. **§Architectural Patterns Analysis** — 12 patterns:
   - Hybrid Sequential-Spine + Supervisor Dispatcher
   - Plan-and-Execute (default) + ReAct (explore preset)
   - Gate-as-`interrupt()`-Node
   - Sanctum Cold-Start (Sacred Truth)
   - Manifest-as-Graph-Config
   - Learning-Event Side-Effect (idempotent emitter)
   - Frozen-Graph-Version
   - Two-Layer Retry + Idempotent Specialists
   - Time-Travel + Fork (Trial-Run Discipline)
   - Subgraph Composition (isolated state)
   - Streaming + Observability (LangSmith as evidentiary substrate)
   - Dev-Graph Separation (Cora ≠ Marcus → two compiled graphs, two thread namespaces)
7. **§Implementation Approaches and Technology Adoption** — Open-question resolutions; LangGraph Platform vs self-hosted decision; persistence operations (Postgres cleanup + retention + audit); 4-layer testing strategy; prompt-caching activation + economics measurement; per-slab implementation recipe; migration timeline (12–16 weeks) + critical path; risks + mitigations; six-axis cost optimization; skill requirements + team organization; final tech stack; success metrics + KPIs

## Five Foundational Decisions — Consolidated

| # | Decision | One-line essence |
|---|---|---|
| 1 | Runtime independence in stages | End-state = persistent local LangGraph service (Stage 2); IDE is client; Stage 1 (subprocess) skipped to avoid transitional refactor |
| 2 | Bounded big-bang in clone | Primary repo carries production; clone diverges aggressively for 12–16 weeks; five architectural slabs; backports stop, forward-ports later |
| 3 | Reject the LangChain cage | Probabilistic-first nodes; routing edges decide who, not what; schema-as-boundary-not-corset; long-context-over-compression; specialists-as-subgraphs; narrow deterministic glue; model-tier-follows-reasoning; replay-enables-exploration |
| 3a | HIL + SPOT preserved indefinitely | Operator decision authority at every gate is permanent; gate-payload curation reduces re-feeding burden over time; Marcus stays SPOT |
| 4 | Specialist scaffold + sanctum pattern | 9-node subgraph skeleton + typed envelope/return contracts + 9-layer expertise stack (L0 LLM training → L8 envelope context); sanctum (L1–L4) = WHO, references (L5–L6) = WHAT they know, MCP (L7) = WHAT they can do; plug-and-play < 1 dev-day per new specialist after scaffold hardens |

## 12 Architectural Patterns → Substrate Invariants Preserved

| Pattern | Substrate invariant preserved (digest §8) |
|---|---|
| Hybrid Sequential-Spine + Supervisor | #4 (15-gate manifest-driven topology), #2 (Marcus-only orchestration) |
| Plan-and-Execute default + ReAct on `explore` | #1 (Marcus stateless orchestrator), Decision 3 (cage avoidance) |
| Gate-as-`interrupt()`-Node | #4 (HIL-paused gates), #6 (3-layer code review), Decision 3a (operator authority) |
| Sanctum Cold-Start (file-backed fresh-read) | #1 (Sacred-Truth fresh-read) |
| Manifest-as-Graph-Config | #3 (Pipeline Lockstep deterministic neck), #10 (frozen-at-ship) |
| Learning-Event Side-Effect | #9 (event ledger emission at G2C/G3/G4) |
| Frozen-Graph-Version | #10 (frozen-at-ship pack discipline), #14 (deferred inventory continuity) |
| Two-Layer Retry + Idempotent Specialists | #6 (correctness review), #11 (K-floor test discipline) |
| Time-Travel + Fork (Trial-Run Discipline) | #9 (learning ledger), #14 (deferred inventory across runs) |
| Subgraph Composition (isolated state) | Decision 3 (cage avoidance), Decision 4 (scaffold) |
| Streaming + Observability | Decision 1 Stage 2 (IDE-as-client) |
| Dev-Graph Separation (Cora ≠ Marcus) | #15 (lane responsibility) |

## Five-Slab Implementation Path — Consolidated

| Slab | Wall-clock | Delivers | "Done" |
|---|---|---|---|
| 1 — Substrate | 2–3 wk | Runtime skeleton; Postgres+cleanup; AnthropicPromptCachingMiddleware; LangSmith; FastAPI+MCP bridge; state base classes; empty manifest-loaded graph | Empty graph runs end-to-end through 15 steps with operator-driven gate decisions; cache hit rate ≥ 80% on second invocation |
| 2 — Specialists | 4–6 wk | Scaffold + `bmad-create-specialist` + 17 specialist two-axis migrations + Wondercraft pilot + specialist-anti-patterns catalog | Every specialist invocable from CLI/CI/MCP; sanctum cold-load integrity tests pass; Wondercraft produces a real podcast against live API |
| 3 — Marcus + Routing | 2 wk | Marcus supervisor (Plan-and-Execute) + routing + DecisionCards | End-to-end APP run §01→§15 completes (specialist quality may lag primary); operator approve/edit/reject at every gate with live DecisionCards |
| 4 — Lockstep + Gates + Dev-Graph | 2–3 wk | CI block-mode hook; Cora dev-graph; party-mode-as-interrupt; frozen-graph-version ceremony; learning-event ledger; Pydantic+RetryPolicy workaround | Block-mode catches violating PR; full story-cycle runs in dev-graph; learning events from tracked trial run land in ledger |
| 5 — Trial-Run + Polish | 2 wk | Trial-replay regression test; replay/fork UX; economics dashboard; sanctum invalidation hook; cold-storage archival; head-to-head parity validation | New tracked trial run reaches parity-or-better against primary repo; all 5 preflight flags addressed in LangGraph form |

**Critical path**: Slab 1 → 2 → 3 → 4 → 5 sequential; only intra-Slab-2 parallelism. Slab 2 is the timeline lever — parallelize specialist migration across dev capacity once scaffold hardens.

## Strategic Technical Impact Assessment

**What this migration buys**:

- **Independence from the IDE as runtime host** (the original motivating constraint). Production-quality runs become reproducible, replayable, schedulable, observable, and forkable without an open IDE conversation.
- **A specialist-development engine** (the scaffold + sanctum pattern + `bmad-create-specialist` generator) that compresses new specialist time-to-deploy from weeks (current) to **<1 day**. This is a permanent capability — the operator can spin up new media/service specialists at the speed of API contracts changing.
- **Token economics that scale**. Prompt-caching middleware delivers 80–90% input-token cost reduction on the cached sanctum/persona/references prefix. The case-study pattern ($720→$72/month) is realistic for this APP's prefix shape.
- **Reproducibility-by-construction**. Frozen-graph-version + checkpointed trial runs + replay-from-checkpoint mean every closed trial is byte-for-byte reproducible. Audit guarantee becomes architectural, not procedural.
- **Operator authority preserved AND amplified**. HIL + SPOT preserved (Decision 3a). Gate payloads curated as DecisionCards reduce per-decision cognitive load. Fork-from-checkpoint enables what-if exploration that doesn't exist today.
- **The LangChain cage stays out**. Decision 3's eight operating rules + five anti-patterns + the per-specialist `reason`-node free-text default keep agent intelligence intact. The graph absorbs structure at boundaries, not in agent reasoning.

**What this migration costs**:

- **12–16 weeks of clone divergence** with the clone "broken end-to-end" as a managed state. Mitigated by primary repo carrying production for the duration.
- **A LangGraph framework dependency** with versioned upgrade ceremony. Mitigated by frozen-graph-version pinning and a deliberate upgrade Tier-1/2/3 policy.
- **A team ramp-up on LangGraph + Pydantic-v2 LangGraph state + Postgres operational basics**. Mitigated by Slab 1 being the curriculum.

**What this migration does not change**:

- The 15-step production pipeline shape (manifest is preserved, just becomes graph config)
- Marcus's SPOT role with the operator
- Any governance gate's decision-authority semantics
- The schema discipline, the K-floor rules, the four-file-lockstep update pattern
- The deferred-inventory governance regime

## Recommended Next BMAD Step — `bmad-create-prd`

This research is the input artifact for the migration PRD. The next BMAD workflow to invoke (in a fresh context window) is **`bmad-create-prd`** ([CP] in the BMAD catalog).

**What the PRD inherits as locked decisions** (do not re-litigate):
- Decisions 1, 2, 3, 3a, 4 (with their operating rules and anti-patterns)
- The 12 architectural patterns
- The five-slab structure as the implementation skeleton
- The final technology stack (self-hosted OSS LangGraph + Pydantic v2 + `langgraph-checkpoint-postgres` + `AnthropicPromptCachingMiddleware` + MCP bridge + LangSmith + FastAPI escape hatch)

**What the PRD must produce**:
- Migration PRD scoping the LangChain/LangGraph migration as a single multi-slab initiative
- Explicit non-goals (e.g., not a re-architecting of the manifest, not a re-design of specialist roles, not a multi-tenancy push, not a Stage 3 production deploy)
- Success criteria for each slab (drawn from the recipe in §Implementation Approaches §Per-Slab Implementation Recipe)
- Risk register (drawn from §Risks + Mitigations) with explicit operator-acknowledged risk tolerances
- Phased rollout schedule with operator-approvable milestones at slab boundaries
- Cost projection (token economics + Postgres + LangSmith + dev capacity) with measured baseline targets
- Cutover criteria (when does primary repo retire to forward-port mode)
- Operator handshake on bounded big-bang divergence window

**After the PRD**: `bmad-validate-prd` → `bmad-create-architecture` (which produces the formal C4-style architecture, contract definitions, frozen-graph-version directory layout, dev-graph specification — using this research's 12 patterns as architectural baseline) → `bmad-create-epics-and-stories` (each slab → 1–2 epics; per-specialist migration in slab 2 → one story per specialist, parallelizable) → `bmad-check-implementation-readiness` → standard implementation cycle (SP → CS/VS → DS → CR → ER per slab).

## Conclusion

The course-DEV-IDE-with-AGENTS APP is unusually ready for this migration: the substrate is mature (just-closed Epic 33 + first end-to-end trial), the constraints are well-named (manifest-driven pipeline, Pipeline Lockstep, sanctum pattern, schema discipline), and the strategic question (incremental vs big-bang) was correctly answered (big-bang, because the primary repo carries production). The five-decision spine + 12-pattern architecture + five-slab path gives the next phase (PRD → architecture → epics) a fully-grounded foundation rather than a generic LangGraph plan.

The work ahead is substantial but bounded. The reward is a runtime that is independent, observable, replayable, plug-and-play extensible, and fundamentally faithful to the operator's vision of probabilistic intelligence directed through structured operator authority — without the LangChain cage.

---

**Technical Research Completion Date:** 2026-04-22
**Research Period:** 2026-04-21 → 2026-04-22 (single-session intensive)
**Document Length:** Comprehensive — substrate digest + five strategic decisions + 12 architectural patterns + five-slab recipe + tech stack lock-in
**Source Verification:** All technical claims cited with current 2026 sources (LangChain/LangGraph docs, Anthropic API docs, GitHub issues, 2026 case studies)
**Technical Confidence Level:** High on the locked decisions and the recommended path; medium on framework-bug workarounds (Issues #2581, #4987, #6027) which may be fixed in upstream releases

*This document serves as the authoritative technical research substrate for the migration PRD and downstream BMAD planning chain. It is intended to be read by all subsequent BMAD agents (Mary, John, Winston, Murat, Cora, Marcus) as locked input — re-litigating Decisions 1–4 is out of scope; refining their consequences in PRD/architecture/epics IS the next phase's job.*


