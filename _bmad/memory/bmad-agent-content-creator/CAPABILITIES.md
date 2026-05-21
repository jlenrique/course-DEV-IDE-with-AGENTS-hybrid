# Capabilities

## Built-in

| Code | Name | Description | Source |
|------|------|-------------|--------|
| [BT] | blooms-taxonomy-application | Classify objectives by cognitive level; match content type to Bloom's level | `./references/blooms-taxonomy-application.md` |
| [CD] | cluster-decision-criteria | Cluster decision criteria — evaluate slides for clustering using concept density, visual complexity, pedagogical weight, operator input | `./references/cluster-decision-criteria.md` |
| [DC] | cluster-density-controls | Cluster density controls — CLUSTER_DENSITY run constant, per-slide overrides, interstitial count assignment | `./references/cluster-density-controls.md` |
| [NA] | cluster-narrative-arc-schema | Cluster narrative arc schema — narrative_arc field rules, master_behavioral_intent subordination, develop sub-type assignment | `./references/cluster-narrative-arc-schema.md` |
| [CP] | cluster-planning | Umbrella capability — full Pass 1 cluster planning workflow coordinating CD, NA, DC, IB, CS | `./references/cluster-planning.md` |
| [CL] | cognitive-load-management | Design sequences respecting working memory; apply chunking, scaffolding, dual-coding | `./references/cognitive-load-management.md` |
| [CS] | content-sequencing | Determine optimal presentation order; apply spiral curriculum across modules | `./references/content-sequencing.md` |
| [PQ] | delegation-intent-verification | Review delegated prose for behavioral-intent fulfillment and instructional-structure fit (not a quality gate) | `./references/delegation-intent-verification.md` |
| [WD] | delegation-protocol | Writer delegation protocol — select writer, compose brief, review returns, manage revision rounds | `./references/delegation-protocol.md` |
| [IB] | interstitial-brief-specification | Interstitial brief specification standard — constrained 6-field briefs for Gamma cluster interstitials preserving head-slide lineage | `./references/interstitial-brief-specification.md` |
| [LO] | learning-objective-decomposition | Break course/module/lesson objectives into per-asset targets; trace and flag orphans | `./references/learning-objective-decomposition.md` |
| [MA] | manual-animation-support | Generate manual-tool guidance for operator-built animations; validate imported assets (script-backed) | `./references/manual-animation-support.md` |
| [MC] | motion-perception-confirmation | Validate approved motion assets; produce video perception confirmations for non-static segments (script-backed) | `./references/motion-perception-confirmation.md` |
| [MP] | motion-plan-hydration | Apply Gate 2M decisions from motion_plan.yaml into segment-manifest motion fields (script-backed) | `./references/motion-plan-hydration.md` |
| [IA] | pedagogical-framework | Instructional analysis — decompose source material into instructional components; umbrella for LO/BT/CL/CS | `./references/pedagogical-framework.md` |
| [PC] | perception-contract-enforcement | Enforce Irene's mandatory perception contract before Pass 2 narration (script-backed) | `./references/perception-contract-enforcement.md` |
| [SM] | save-memory | Immediate session-context persistence to Irene's sanctum | `./references/save-memory.md` |
| [SB] | spoken-bridging-language | Spoken pedagogical bridging — align manifest bridge_type with learner-heard intro/outro language per cadence + frequency scale | `./references/spoken-bridging-language.md` |
| [AA] | template-assessment-brief | Assessment alignment template — backward design, Bloom's-level matched items, distractor rationale | `./references/template-assessment-brief.md` |
| [MG] | template-segment-manifest | Segment manifest generation — machine-readable production contract binding narration to visuals, SFX, music, composition metadata | `./references/template-segment-manifest.md` |
| [VR] | visual-reference-injection | Select visual elements from perception artifacts; weave into narration with deictic references (script-backed) | `./references/visual-reference-injection.md` |

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
| `./scripts/__init__.py` | _(add module docstring)_ |
| `./scripts/manifest_visual_enrichment.py` | Segment manifest visual reference enrichment (Story 13.3) |
| `./scripts/manual_animation_workflow.py` | Manual animation guidance and import validation for Epic 14 |
| `./scripts/motion_gate_receipt_reader.py` | Motion Gate receipt reader — published receipt contract for Irene Pass 2 |
| `./scripts/perception_contract.py` | Mandatory perception contract for Irene Pass 2 |
| `./scripts/visual_reference_injector.py` | Visual reference injection for Irene Pass 2 narration |

### User-Provided Tools

_MCP servers, APIs, or services the owner has made available._
