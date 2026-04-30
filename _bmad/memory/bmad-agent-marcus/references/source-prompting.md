---
name: source-prompting
code: SP
description: Proactive source-material prompting (Notion / Box Drive retrieval before production)
---

# Source Material Prompting

## Purpose

Marcus proactively offers to pull course development notes and reference materials before production tasks begin. Context enrichment before creation beats revision after.

## When to Offer

Before starting any content production task, assess whether source materials would improve the output:

- **New lesson creation** — Offer to pull Notion course development notes for the relevant module/lesson
- **Content revision** — Offer to check Box Drive for updated reference materials
- **Assessment creation** — Offer to pull learning objectives and competency frameworks from Notion
- **Case study development** — Offer to check for existing clinical case references

## Source Channels — Delegated to Texas

Source wrangling is now delegated to **Texas** (`skills/bmad-agent-texas/`), a memory agent with extraction validation, cross-validation, and fallback chains. Marcus sends a wrangling directive and receives a structured result with quality tiers. See `skills/bmad-agent-texas/references/delegation-contract.md` for the full envelope schema.

Texas handles all source channels:
- **Local PDFs** — pypdf extraction with proportionality check and fallback chain
- **Notion** — via `NotionClient` / Notion MCP
- **Box Drive** — local filesystem reads
- **Web pages** — HTTP fetch + HTML-to-text, Playwright for JS-rendered pages
- **Reference/validation assets** — MD files, DOCX versions used to cross-validate primary extraction
- **Course content folders** — `course-content/courses/{course-slug}/` structure

### Delegation Flow

1. Marcus gathers source information from the operator during Prompt 2/2A (source manifest)
2. Marcus sends a wrangling directive to Texas with the source manifest and quality gate thresholds
3. Texas extracts, validates (proportionality + cross-validation), and applies fallbacks as needed
4. Texas returns a structured result: `complete` / `complete_with_warnings` / `blocked`
5. Marcus proceeds, surfaces warnings, or halts based on Texas's status

### Gamma exemplar links
- **Not** plain HTTP fetch: `gamma.app/docs/...` is blocked by design
- Route through **Gary** (export) or Playwright HTML capture, then pass to Texas for ingestion

## Prompting Style

Natural, not mechanical. Examples:
- "Before we build slides for the cardiac assessment lesson — do you have Notion notes on learning objectives for this module? I can pull them to make sure we're aligned from the start."
- "I see there's a Box Drive reference folder for Pharmacology. Want me to check for anything relevant before we draft?"
- "Last time we built a case study, the Notion feedback was really useful for getting the clinical scenario right. Should I pull the latest notes?"

## Integration with Production Planning

When source materials are retrieved, Marcus incorporates them into the specialist context envelope — they become part of the context passed to content-creator, quality-reviewer, and other specialists who need domain grounding.
