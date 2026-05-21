# Transform Registry

Extraction method hierarchy per source type. For each format, methods are listed in priority order — try the default first, fall back in sequence.

## PDF

| Priority | Method | When to Use | Known Limitations |
|----------|--------|-------------|-------------------|
| 1 | `pypdf` (text extraction) | Default for all PDFs | Fails on scanned/image PDFs; can produce stubs on complex layouts |
| 2 | `pdfplumber` | Fallback when pypdf output is thin | Better with tables and complex layouts; slower |
| 3 | Notion MCP cross-pull | When PDF is a known Notion export | Requires Notion page ID; operator must declare provenance |
| 4 | Playwright PDF render + re-extract | When PDF is a web-generated export | Requires the original URL |
| 5 | HIL escalation | All automated methods failed | Operator provides content manually or via alternative format |

**Stub detection heuristic**: If pypdf extracts < 50% of expected words (page_count × 200), immediately try the next method before reporting.

## DOCX

| Priority | Method | When to Use | Known Limitations |
|----------|--------|-------------|-------------------|
| 1 | `python-docx` text extraction | Default | Loses complex formatting; tables become flat text |
| 2 | LibreOffice CLI → plain text | Fallback for complex layouts | Requires LibreOffice installed |
| 3 | Read as ZIP + extract XML | Last resort for corrupted files | Produces raw XML, needs cleanup |

## Markdown (.md)

| Priority | Method | When to Use | Known Limitations |
|----------|--------|-------------|-------------------|
| 1 | Direct file read | Always | Escaped markdown (backslash-prefixed) needs cleanup |

**Note**: MD files with escaped formatting (e.g., `\#` instead of `#`, `\*\*` instead of `**`) should be normalized during extraction. This is common with content exported from rich text editors.

## Notion

| Priority | Method | When to Use | Known Limitations |
|----------|--------|-------------|-------------------|
| 1 | Notion MCP / REST API | Default | Requires NOTION_API_KEY; page must be shared with integration |
| 2 | Playwright page save | When API access fails | Requires browser automation |
| 3 | Exported PDF/HTML | When operator provides a manual export | May lose database/embedded content |

## HTML / URL

| Priority | Method | When to Use | Known Limitations |
|----------|--------|-------------|-------------------|
| 1 | `requests` + HTML-to-text | Simple static pages | Fails on JS-rendered SPAs |
| 2 | Playwright MCP | Dynamic/JS-heavy pages | Slower; requires browser context |
| 3 | Playwright save + offline extract | Auth-walled pages | Operator must authenticate first |

## Future (Placeholder)

These formats are not yet supported but are anticipated:

- **PPTX**: Slide-by-slide text + speaker notes extraction
- **XLSX/CSV**: Tabular data → structured markdown tables
- **Video transcripts (SRT/VTT)**: Timestamp-aware text extraction
- **Scanned PDFs**: OCR pipeline (Tesseract or cloud vision API)
- **Images**: Vision API → structured description
