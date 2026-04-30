# Capabilities

## Built-in

| Code | Name | Description | Source |
|------|------|-------------|--------|
| [EV] | extract-and-validate | Extract source content and validate quality before delivery | `./references/extract-and-validate.md` |
| [FR] | fallback-resolution | Resolve degraded or failed extractions through alternative pathways | `./references/fallback-resolution.md` |
| [SI] | source-interview | Gather source knowledge from the HIL operator through Marcus | `./references/source-interview.md` |

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

Prefer crafting your own tools over depending on external ones.

### Scripts

| Script | Purpose |
|--------|---------|
| `./scripts/extraction_validator.py` | Proportionality checks, quality tier classification |
| `./scripts/cross_validator.py` | Compare extraction against reference assets |

### User-Provided Tools

_MCP servers, APIs, or services the owner has made available._
