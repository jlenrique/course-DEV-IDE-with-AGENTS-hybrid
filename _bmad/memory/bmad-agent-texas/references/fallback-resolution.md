---
name: fallback-resolution
description: Resolve degraded or failed extractions through alternative pathways
code: FR
---

# Fallback Resolution

## What Success Looks Like

When the primary extraction method fails or produces degraded output, you find another way to get the content — or make a well-reasoned decision to substitute a validation asset as the primary source. Downstream agents get usable material regardless of which path produced it. Every fallback decision is documented with evidence.

## Your Approach

### The Fallback Chain

Load `./references/transform-registry.md` for the ordered fallback chain per source type. The general pattern:

1. **Try the next automated extractor** in the chain (e.g., pypdf → pdfplumber → OCR)
2. **Validate each attempt** — run the same quality checks as the primary extraction
3. **If all automated methods produce Tier 3+**, evaluate validation assets as substitutes
4. **If a validation asset covers the needed scope**, propose substitution to Marcus with evidence
5. **If nothing works**, report `blocked` status with specific recommendations for HIL intervention

### Substitution Logic

When considering a validation asset as a substitute for a failed primary extraction:

- **Coverage match**: Does the validation asset cover the scope needed? An MD file covering only Part 1 can't substitute for a full-module extraction, but it *can* substitute for a Part 1–scoped run.
- **Format fitness**: Is the validation asset in a format downstream agents can consume? MD is ideal. DOCX requires transformation. Raw text needs structure.
- **Recency**: Is the validation asset at least as current as the primary source? Check modification dates.
- **Evidence**: Document why the substitution is justified — "PDF extraction yielded 30 words (Tier 4), MD reference contains 1,500 words covering all 6 slides of Part 1, substituting MD as primary source for this scope."

### Indirect Quality Indicators

When you can't directly measure extraction quality (e.g., you don't know the expected word count), use indirect indicators:

- **Section header count** — a 24-page document should have multiple sections. Zero headings from a structured document = extraction failure.
- **Content density** — ratio of substantive text to whitespace/boilerplate. Low density = likely metadata-only extraction.
- **Character diversity** — extraction that's all ASCII from a document with special characters (em-dashes, curly quotes, mathematical symbols) may indicate encoding failure.
- **Page coverage** — if the extractor reports extracting from pages 1-3 of a 24-page document, something truncated.

## Memory Integration

Check MEMORY.md for past fallback patterns. If pypdf consistently fails on Notion-exported PDFs, note that and try the Notion MCP path first for known Notion exports.

## After the Session

Record every fallback decision: what failed, why, what you tried, what worked. These patterns are gold — they turn reactive troubleshooting into proactive extraction strategy.
