---
name: retrieval-contract
description: Shape 3-Disciplined retrieval contract — intent, acceptance criteria, dispatcher, provider directory
code: RC
---

# Texas Retrieval Contract

This is the single-source-of-truth doc for Texas's Shape 3-Disciplined retrieval foundation (Story 27-0). It is audience-segmented: read the section that matches your role. All three views describe the same underlying contract; none supersedes another.

## TL;DR

- Texas's retrieval subsystem partitions source-fetch work by **knowledge-locality** (Dr. Quinn). Editorial knowledge (intent + acceptance criteria) lives with Tracy; provider-DSL knowledge (query translation, pagination, native signals) lives in per-provider `RetrievalAdapter` subclasses; dispatch + iteration orchestration lives in a thin Texas dispatcher.
- **`provider_hints` is required v1** — no auto-discovery. Tracy / the directive always names the providers.
- **Cross-validation is first-class v1** — `cross_validate: true` fans out to every named provider, merges results by identity key (DOI / video-id / canonical-url), and annotates each row with a structural `ConvergenceSignal`.
- **Operator-locator paths keep their existing CLI shape** — DOCX / PDF / Notion / Box / Playwright directives still work as they did before 27-0; internally they route through the same dispatcher via a degenerate-case transform.
- **Directory is the source of truth** for "what can Texas fetch?" — `provider_directory.list_providers()` (or `run_wrangler.py --list-providers`) is canonical.

## For Tracy (intent authors)

You emit `RetrievalIntent` objects describing WHAT you want, not HOW the provider expresses it. Three knobs:

**`intent: str`** — the natural-language description of what you're looking for. Scite's adapter will translate this into its own query DSL; Consensus's adapter will do its own translation; YouTube's adapter will do its own. You do not know or care about their DSLs.

**`provider_hints: list[ProviderHint]`** — the list of providers to dispatch against. Each entry is `{provider: <id>, params: <dict>}`. Valid provider IDs are whatever `provider_directory.list_providers()` returns for `shape="retrieval"` with `status` in `{ready, stub}`. `params` is opaque to Texas — the named provider's adapter interprets it.

**`acceptance_criteria`** — a three-tier contract:
  - `mechanical`: deterministic predicates Texas evaluates (date ranges, min_results, exclude_ids, license allowlists, duration caps). Texas filters.
  - `provider_scored`: provider-native signals (authority_tier_min, supporting_citations_min). Provider filters on your behalf.
  - `semantic_deferred`: a short string describing semantic judgment you'll do YOURSELF in a post-fetch pass. Texas does NOT evaluate this. Use it to record the intent so the log explains why your worksheet rejected rows Texas accepted.

**`cross_validate: bool`** — set to true when you want scite + Consensus (for example) to both fetch, merge results by DOI, and annotate each row with `convergence_signal: {providers_agreeing, providers_disagreeing, single_source_only}`. The signal is structural only — it tells you whether both providers returned the same DOI, NOT whether they semantically agree about the claim.

**`iteration_budget: int = 3`** — dispatcher tries this many rounds of refinement before giving up. Stay at 3 unless you have a specific reason to widen.

**`convergence_required: bool = True`** — when true, the dispatcher exits early if the next refinement round does not improve over the previous one. Leave this true in v1 (resolves Murat's test-flakiness concern).

### Example intent

```yaml
intent: "peer-reviewed studies on sleep hygiene published since 2020"
provider_hints:
  - {provider: "scite",     params: {mode: "search"}}
  - {provider: "consensus", params: {mode: "search"}}
cross_validate: true
acceptance_criteria:
  mechanical:
    date_range: ["2020-01-01", "2026-12-31"]
    min_results: 5
  provider_scored:
    authority_tier_min: "peer-reviewed"
    supporting_citations_min: 10
  semantic_deferred: "screen out meta-analyses vs primary-research studies in my worksheet"
iteration_budget: 3
convergence_required: true
```

### Scite-specific signals (Story 27-2)

The scite adapter ships ready in Epic 27 and populates `provider_metadata.scite` on every returned row. Signals to design around:

- **Smart-citation classification** — scite returns `supporting_count`, `contradicting_count`, `mentioning_count` + up-to-three context snippets per classification. Use these to express "evidence-bolster" or "contradicting-evidence" constraints in your semantic-deferred pass.
- **Authority tier** — derived from the venue via scite's venue-type table (`SCITE_AUTHORITY_TIERS` in the adapter). `peer-reviewed` > `preprint` > `web`. Mechanical filter via `provider_scored.authority_tier_min`.
- **Paywall degradation** — `full_text_available: false` → body becomes abstract-only, `provider_metadata.scite.known_losses = ["full_text_paywalled"]`. Downstream fidelity pass (Vera) reads the sentinel.
- **Identity key** — DOI (primary) → `scite_paper_id` (preprint fallback) → `source_id`. Cross-validation with Consensus (27-2.5) hinges on DOI agreement.

**Full `provider_metadata.scite` schema** — see [extraction-report-schema.md § Provider Metadata Sub-objects](./extraction-report-schema.md#provider-metadata-sub-objects). Single source of truth lives there.

### Consensus-specific signals (Story 27-2.5)

The Consensus adapter ships ready in Epic 27 and populates `provider_metadata.consensus` on every returned row. Signals to design around:

- **Research-synthesis score** — `consensus_score` is a provider-native agreement-strength signal you can gate with `provider_scored.consensus_score_min` when you want stronger consensus-first retrieval.
- **Study-design metadata** — `study_design_tag` + `sample_size` enable deterministic narrowing (`provider_scored.study_design_allow`, `provider_scored.sample_size_min`) without semantic inference in Texas.
- **Graceful sparsity handling** — when optional provider fields are absent, rows are still emitted and `provider_metadata.consensus.known_losses` records explicit sentinels (`study_design_unknown`, `sample_size_unknown`, `evidence_strength_unknown`, plus `abstract_only`).
- **Identity key** — DOI (primary) → `consensus_paper_id` (fallback) → `source_id`. This is what makes scite+Consensus cross-validation merge by a shared scholarly identity key.
- **Cross-validation interpretation** — if both adapters return the same DOI, `convergence_signal` marks structural convergence even when semantics differ (for example, high scite supporting counts with a low Consensus score). Semantic reconciliation is Tracy's downstream pass.

**Full `provider_metadata.consensus` schema** — see [extraction-report-schema.md § Provider Metadata Sub-objects](./extraction-report-schema.md#provider-metadata-sub-objects) (subsection `provider_metadata.consensus`). That document remains the single schema source of truth.

## For operators (directive authors)

Nothing changes about the directive shapes you already use. DOCX / PDF / Notion / Box / Playwright directives continue to work as they did before Story 27-0. Internally the dispatcher transforms a legacy directive:

```yaml
sources:
  - ref_id: src-001
    provider: local_file
    locator: /path/to/file.md
    role: primary
```

into a degenerate-case `RetrievalIntent` under the hood:

```yaml
intent: "fetch exact locator"
provider_hints: [{provider: "local_file", params: {}}]
kind: "direct_ref"
acceptance_criteria: {mechanical: {exists: true}}
iteration_budget: 1
```

You never see the transform. Output (`extraction-report.yaml`) is byte-identical to pre-27-0 for legacy directives (AC-T.7 regression proof).

### Authoring retrieval-shape directives directly (advanced)

Most operators never write retrieval-shape directives by hand — Tracy (Epic 28) emits them. But since Story 27-2 shipped, they are authorable directly for testing or specialized workflows.

**When to reach for this (vs. staying on legacy directives):**
- You are **testing a retrieval adapter in isolation** (e.g., validating that `scite` returns the right provider_metadata for a known-good query) without standing up Tracy.
- You are running a **specialized query shape** the legacy locator-shape cannot express — natural-language intent + acceptance criteria + multi-provider cross-validation fan-out.
- You are **reproducing a Tracy-emitted intent** during debugging (Tracy's intents ARE retrieval-shape; hand-crafting one lets you bisect whether a bug is in Tracy's emission or in Texas's dispatch).

If your use case is "fetch this exact file / URL," stay on the legacy locator shape — the retrieval dispatcher is the wrong abstraction for that, and the legacy path is byte-identical by design (AC-T.6 regression proof).

The retrieval-shape directive shape:

```yaml
run_id: INTENT-RUN-001
sources:
  - ref_id: src-intent-1
    role: primary
    intent: "peer-reviewed studies on sleep hygiene since 2020"
    provider_hints:
      - {provider: "scite", params: {mode: "search"}}
    acceptance_criteria:
      mechanical: {date_range: ["2020-01-01", "2026-12-31"], min_results: 5}
      provider_scored: {authority_tier_min: "peer-reviewed"}
    iteration_budget: 3
    convergence_required: true
    cross_validate: false
```

Field reference: see §For Tracy above. Cross-validation (multi-provider fan-out) requires at least two `provider_hints` entries and `cross_validate: true`.

**A directive's sources must all share one shape** (v1 constraint): either every row is retrieval-shape (has `intent`+`provider_hints`), or every row is locator-shape (has `provider`+`locator`). Mixed directives exit 30. Split into two directives if both shapes are needed in one pipeline run.

### What's new: the directory

```bash
python skills/bmad-agent-texas/scripts/run_wrangler.py --list-providers
python skills/bmad-agent-texas/scripts/run_wrangler.py --list-providers --shape retrieval
python skills/bmad-agent-texas/scripts/run_wrangler.py --list-providers --status ready
python skills/bmad-agent-texas/scripts/run_wrangler.py --list-providers --json
```

Shows every fetch surface Texas knows about — ready implementations (DOCX, PDF, HTML, Markdown, Notion direct API, Box Drive local FS, Playwright-saved HTML, and any loaded retrieval adapters such as scite/Consensus), ratified stubs (Notion MCP, Box API, Playwright MCP, image, YouTube, plus retrieval placeholders when no live adapter is loaded), and forward-looking backlog entries (OpenAI/ChatGPT). Use this when you're about to ask "can Texas pull from X?" — the directory answers authoritatively.

The `--list-providers` output also includes each provider's required `auth_env_vars` — that's your discovery path for credentials (e.g., `SCITE_USER_NAME`, `SCITE_PASSWORD` for scite; Consensus accepts `CONSENSUS_API_KEY` or `CONSENSUS_USER_NAME` + `CONSENSUS_PASSWORD`). This repo does not ship a top-level `.env.example` file; [`provider_directory.py`](../scripts/retrieval/provider_directory.py) is the authoritative source for per-provider env var requirements. Copy the names into your local `.env` (gitignored) and fill in actual values.

## For dev-agents (extending the base)

Add a new retrieval-shape provider by subclassing `RetrievalAdapter` and declaring `PROVIDER_INFO`. Auto-registration via `__init_subclass__` plugs your adapter into the directory + dispatcher.

```python
from retrieval import (
    AcceptanceCriteria,
    ProviderInfo,
    RetrievalAdapter,
    RetrievalIntent,
    TexasRow,
)

class MyProvider(RetrievalAdapter):
    PROVIDER_INFO = ProviderInfo(
        id="myprov",
        shape="retrieval",
        status="stub",  # flip to "ready" when implementation lands
        capabilities=["search", "citation-count"],
        auth_env_vars=["MYPROV_API_KEY"],
        spec_ref="_bmad-output/implementation-artifacts/27-X-myprov.md",
        notes="One-line description surfaced in `--list-providers` output.",
    )

    def formulate_query(self, intent: RetrievalIntent) -> str:  # deterministic
        ...
    def execute(self, query: str) -> list[dict]:  # auth, pagination, rate limits inside
        ...
    def apply_mechanical(self, results, criteria: dict):
        ...
    def apply_provider_scored(self, results, criteria: dict):
        ...
    def normalize(self, results) -> list[TexasRow]:
        ...
    def refine(self, prev_query, prev_results, criteria: AcceptanceCriteria):
        ...
    def identity_key(self, row: TexasRow) -> str:  # raise NotImplementedError if N/A
        return row.provider_metadata.get("doi") or row.source_id
    def declare_honored_criteria(self) -> set[str]:
        return {"date_range", "min_results", "authority_tier_min"}
```

### Anti-patterns

- ❌ **Do NOT use LLM-in-the-loop for query formulation or refinement.** v1 is deterministic Python only. Lookup tables + string munging, not inference. If your provider genuinely needs semantic expansion, open a new story with its own eval framework.
- ❌ **Do NOT let `refine()` tighten.** Refinement must be monotonically-loosening — drop filters, widen date ranges. If you can't loosen further, return None. Returning a tighter query breaks dispatcher iteration.
- ❌ **Do NOT silently drop unknown acceptance-criteria keys.** Declare what you honor via `declare_honored_criteria()`. Unknown keys get logged in the dispatcher's `refinement_log` — that's the feedback channel to Tracy / operators.
- ❌ **Do NOT bake provider-specific types into the `mcp_client` public surface.** `call_tool(server, tool, args) -> dict` and `list_tools(server) -> list[dict]` are the only surfaces. No `requests.Response` leak; no library-specific exception re-export. This is the Option-X migration escape hatch (AC-C.9).
- ❌ **Do NOT collapse single-provider into the cross-validation merger.** N=1 fan-out is NOT the same code path as N=2+ fan-out; the dispatcher keeps them distinct. Folding them hides cross-validation-specific bugs.
- ❌ **Do NOT retrofit locator-shape providers (DOCX/PDF/Notion/Box/Playwright) to use `RetrievalIntent` at the CLI.** Legacy directive shape stays; internal transform handles routing. AC-T.7 byte-identical regression test is the proof. If you're tempted to rewrite, stop.
- ❌ **Do NOT register an adapter under an already-claimed provider ID.** `register_adapter` raises on ID conflict. If you want to replace a placeholder (e.g., replacing `scite: ratified` with a live scite adapter), either override the placeholder by subclassing + identical `PROVIDER_INFO.id`, or bump the placeholder to a different ID.

### Directory ownership

- **Ready** (`status="ready"`) — implementation lives in the repo, tested, production-safe.
- **Stub** (`status="stub"`) — class exists, not production-complete. `FakeProvider` and in-dev adapters use this.
- **Ratified** (`status="ratified"`) — a story exists in the Epic 27 roster; no implementation yet. Placeholder lives in `provider_directory.py` until the adapter class lands.
- **Backlog** (`status="backlog"`) — not in current-epic roster; reserved forward-looking entry. `openai_chatgpt` is the canonical example (operator directive 2026-04-18).

## Test inheritance

`tests/contracts/test_retrieval_adapter_base.py` is the **explicit inheritance target** for provider-specific contract tests. When you ship a new adapter (27-2 scite, 27-2.5 Consensus, etc.), add a parametrized entry that runs this module's test cases against your adapter — do not reimplement the base tests. This keeps the contract in lockstep across all providers.

## See also

- [`extraction-report-schema.md`](./extraction-report-schema.md) — per-source record schema; v1.1 adds retrieval-shape provenance fields.
- [`_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md`](../../../_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md) — every schema bump with migration notes.
- [`_bmad-output/implementation-artifacts/27-0-retrieval-foundation.md`](../../../_bmad-output/implementation-artifacts/27-0-retrieval-foundation.md) — full AC-B / AC-T / AC-C pinning + party-mode consensus record.
- [`transform-registry.md`](./transform-registry.md) — locator-shape extraction hierarchy (PDF / DOCX / Markdown / Notion / HTML). Still the source of truth for file-format extraction; directory entries mirror.
