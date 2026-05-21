# Capabilities

## Built-in

| Code | Name | Description | Source |
|------|------|-------------|--------|
| [HC] | checkpoint-coord | Human checkpoint coordination and review-gate transitions | `./references/checkpoint-coord.md` |
| [CM] | conversation-mgmt | Conversation management, intent parsing, production planning, workflow orchestration | `./references/conversation-mgmt.md` |
| [MM] | mode-management | Execution mode management (tracked/default vs ad-hoc) and mode-boundary enforcement | `./references/mode-management.md` |
| [PR] | progress-reporting | Progress reporting, status summaries, and error handling | `./references/progress-reporting.md` |
| [SM] | save-memory | Immediate session-context persistence to the Marcus sanctum | `./references/save-memory.md` |
| [SP] | source-prompting | Proactive source-material prompting (Notion / Box Drive retrieval before production) | `./references/source-prompting.md` |
| [SB] | storyboard-procedure | Gary slide storyboard — Marcus-owned review surface before and after Irene Pass 2 | `./references/storyboard-procedure.md` |

## Learned

_Capabilities added by the owner over time. Prompts live in `capabilities/`._

| Code | Name | Description | Source | Added |
|------|------|-------------|--------|-------|

## How to Add a Capability

Tell me "I want you to be able to do X" and we'll create it together.
I'll write the prompt, save it to `capabilities/`, and register it here.
Next session, I'll know how.
Load `./references/capability-authoring.md` for the full creation framework.

## Tools

### Scripts

| Script | Purpose |
|--------|---------|
| `./scripts/build-pass2-inspection-pack.py` | Build reviewer-facing slide and motion inspection artifacts for Prompt 8 |
| `./scripts/cluster_coherence_validation.py` | Cluster Coherence Validation (Story 21-4) |
| `./scripts/cluster_dispatch_sequencing.py` | Cluster Dispatch Sequencing (Story 21-3) |
| `./scripts/cluster_prompt_engineering.py` | Cluster-aware prompt engineering for Story 21-2 |
| `./scripts/cluster_template_library.py` | Cluster template library loader/validator for Story 20c-1 |
| `./scripts/cluster_template_planner.py` | Runtime bridge between clustered slide output and template selection |
| `./scripts/cluster_template_selector.py` | Deterministic content-aware template selector for Story 20c-2 |
| `./scripts/evaluate_cluster_template_selection.py` | Offline comparative evaluator for C1-M1 template-selection iterations |
| `./scripts/generate-production-plan.py` | Generate a skeleton production plan from content type and module structure |
| `./scripts/generate-storyboard.py` | Build a static HTML + JSON storyboard from Gary |
| `./scripts/interstitial_redispatch_protocol.py` | Interstitial re-dispatch protocol (Story 21-5) |
| `./scripts/platform_allocation.py` | Platform allocation intelligence for Marcus (Story G.1) |
| `./scripts/predictive_workflow_optimization.py` | Predictive workflow optimization for Marcus (Story 10.1) |
| `./scripts/prepare-irene-pass2-handoff.py` | Prepare a fresh Irene Pass 2 handoff envelope at bundle root |
| `./scripts/read-mode-state.py` | Read current run mode, last run ID, and session timestamps from the coordination database |
| `./scripts/run-g1.5-cluster-gate.py` | G1.5 Cluster Plan Quality Gate — Marcus orchestration wrapper |
| `./scripts/run-interstitial-redispatch.py` | Manual CLI for Story 21-5 interstitial re-dispatch |
| `./scripts/tool_ecosystem_synthesis.py` | Tool ecosystem monitoring and documentation synthesis (Story G.2) |
| `./scripts/validate-cluster-plan.py` | G1.5 Cluster Plan Quality Gate — validate Irene Pass 1 cluster plan |
| `./scripts/validate-gary-dispatch-ready.py` | Validate Gary dispatch payload readiness for HIL Gate 2 |
| `./scripts/validate-irene-pass2-handoff.py` | Validate Irene Pass 2 completeness - post-Pass-2 check |
| `./scripts/validate-source-bundle-confidence.py` | Validate confidence consistency across source bundle artifacts |
| `./scripts/write-authorized-storyboard.py` | Regenerate authorized storyboard snapshot with full script context for Storyboard B (post-Irene Pass 2) |

### User-Provided Tools

_MCP servers, APIs, or services the owner has made available._
