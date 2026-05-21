# Corpus — tejal-apc-c1-m1-p2-trends

**Source:** [Tejal C1M1 Outline](https://www.notion.so/Tejal-C1M1-Outline-75c02e8c7930832bb7e3819afe23ef9b)
**Section pulled:** Part 2: The Macro Trends & The Case for Change (Chapters 2 & 3) — from the "C1M1: Gemini Updated" outline (block id `77902e8c-7930-8249-a434-017f4e96b477`).
**Pull timestamp (UTC):** 2026-05-21T23:37:47Z
**Pulled via:** Notion MCP (`project-0-course-DEV-IDE-with-AGENTS-hybrid-notion`); rendered by `.tmp/notion_pull_tejal_c1m1_part2.py`.
**Integration:** `BMAD-Agentic-Course-Content-DEV [2026-03-26]:` (integration id `32f02e8c-7930-814b-909b-00274acc39bc`)

## Layout

- `slides/` — **PRIMARY material**: the 5 narrated slides of Part 2 + the Part 2 Summary slide. Each file contains the Visual Format spec, the image-generation prompt (where present), the Narration / Speaker Notes, and the References.
- `references/` — **SUPPORTING**: external embedded material referenced by Part 2 (intro YouTube video + required-reading Medium article).
- `assessments/` — **SUPPORTING**: Chapter 2 + Chapter 3 Knowledge Check quizzes (5 questions each). Kept distinct from slides so §02A's role assignment can treat them as ancillary.
- `urls.txt` — flat URL list per the corpus-preparation-guide convention. §02A currently skips this file but it is preserved for human reference + downstream tooling.

## Trial-3 launch command (from repo root)

```powershell
$env:PYTHONIOENCODING="utf-8"
.\.venv\Scripts\python.exe -m app.marcus.cli trial start --preset production --input course-content/courses/tejal-apc-c1-m1-p2-trends/
```

**Note on motion:** the trial uses **per-slide motion mode designation at gate §05.5 (G1.5)** — operator declares each slide as `narrated-deck` (static) or `motion-enabled-narrated-lesson` (with Kira video) during the trial gate flow, NOT as a launch-time global flag. The stale `--motion-enabled` flag references in older docs are doc drift; the CLI doesn't accept that flag. See `app/models/operator_verdict_section_05_5.py::PerSlideMode`.

## Provenance for forensic audit

- **Notion page URL:** https://www.notion.so/Tejal-C1M1-Outline-75c02e8c7930832bb7e3819afe23ef9b
- **Notion page id (raw):** `75c02e8c7930832bb7e3819afe23ef9b`
- **Part 2 H2 block id:** `3aa02e8c-7930-8292-ac18-01d8c9d1c8b8`
- **Chapter 2 Knowledge Check block id:** `18c02e8c-7930-8247-bb52-8106d4e5cf61`
- **Chapter 3 Knowledge Check block id:** `d2f02e8c-7930-8351-981a-81bb4552f543`
- The pull is reproducible by re-running `.tmp/notion_pull_tejal_c1m1_part2.py` from the repo root. If the Notion source content changes after this pull, re-running will refresh the corpus; the operator should explicitly decide whether to re-launch the trial against the refreshed corpus or stay on this snapshot.
