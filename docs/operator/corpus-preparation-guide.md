---
title: Corpus Preparation Guide — Operator Pre-Trial Preparation
authoredAt: 2026-05-07
authority: pre-Trial-3 cleanup S1 P0-11 (Sally + Paige authoring voices)
audience: operator preparing course-content corpus for a production trial
purpose: shape your corpus correctly before launching `trial start`. A well-shaped corpus is the difference between Texas dispatching successfully and Trial-3 halting at G0.
---

# Corpus Preparation Guide

This guide covers what to do **before** you run `python -m app.marcus.cli trial start --input <corpus-path>`. The migrated runtime expects your corpus in a specific shape; corpus-preparation mistakes are the most common cause of early-trial halt (Trial-2 finding #2 closed by Slab 7c.3a; Trial-3 still requires correct corpus shape on the operator's side).

## The convention (load-bearing)

**Corpus directory location:** `course-content/courses/<lesson_slug>/`

NOT `sources/`. NOT `corpus/`. NOT `tests/fixtures/`. The migrated runtime reads from `course-content/courses/` exclusively.

**`<lesson_slug>` shape:** kebab-case, descriptive, unique per lesson:
- ✅ `tejal-apc-c1-m1` (Tejal APC Course-1 Module-1)
- ✅ `clinical-judgment-fundamentals-w1`
- ❌ `lesson1` (not unique enough)
- ❌ `tejal_apc_c1_m1` (snake_case wrong; convention is kebab-case)
- ❌ `Tejal-APC-C1-M1` (mixed case wrong)

## Required content (corpus directory contents)

Every corpus directory MUST contain:

1. **One primary source document** — the canonical lesson reference. Typically:
   - `.docx` (Word document) — most common
   - `.pdf` — accepted
   - `.md` (Markdown) — accepted for born-digital sources
   - File name should signal primary status (e.g., `C1M1Part01.md` is fine; `random-notes.md` is ambiguous)

2. **At least one of:** supporting reference materials (additional context the lesson draws from):
   - PDFs of textbook chapters
   - PowerPoint decks (`.pptx`)
   - Article exports
   - Image assets (PNG/JPG referenced in the lesson)

That's the minimum. A corpus with only a primary source + zero supporting refs is technically valid but Texas's retrieval will be sparse.

## Optional content

3. **Visual exhibits** — diagrams, charts, photos referenced by the lesson. PNG / JPG / SVG supported. Place at the top of the corpus dir (no subdirs needed).

4. **`urls.txt` (flat file; one URL per line)** — when supporting references live at public URLs (academic articles, web resources). Texas's retrieval can fetch these via the directive composer.

   Example `urls.txt`:
   ```
   https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9876543/
   https://www.uptodate.com/contents/clinical-judgment-fundamentals
   https://my.clevelandclinic.org/health/articles/12345
   ```

   **`urls.txt` is a flat file, NOT a directive.** It tells Texas "these URLs are part of my corpus." The §02A directive composer will compose retrieval directives FROM these URLs (not the other way around).

5. **Subject-matter expert notes** — operator's own annotations or learning objectives, plain `.md` or `.txt`. Texas treats these as supporting refs.

## What stays OUT of the corpus directory

- **Notion fetch-shape directives** — these are LIVE-FETCH requests, not corpus content. Notion fetches go through Marcus's `fetch_notion_page` skill, NOT through corpus directory scanning. (See feedback memory: `corpus_directory_scope`.)
- **Box virtual-directory URLs** — same as Notion; live-fetch through directive, not corpus content.
- **Playwright-fetched URL lists** — same as above.
- **Retrieval-shape sources** — anything that needs to be fetched at runtime (live API, database query, WebView snapshot).
- **`.tmp/` files** — staging artifacts; not corpus content.
- **Git metadata** — `.git/`, `.gitignore`, etc. — not corpus content (Texas would skip these anyway, but cleanliness matters).
- **`.DS_Store` / `Thumbs.db`** — OS-level junk.

## Pre-launch corpus checklist

Run through this before invoking `trial start`:

- [ ] Corpus directory exists at `course-content/courses/<lesson_slug>/` (NOT elsewhere)
- [ ] `<lesson_slug>` is kebab-case, descriptive, and unique
- [ ] Primary source document is present and identifiable (file name signals primary status)
- [ ] At least one supporting reference is present
- [ ] No directive content is in the corpus directory (Notion / Box / Playwright fetch-shape requests are NOT in corpus)
- [ ] No `.tmp/` or staging files leaked into the directory
- [ ] If using `urls.txt`, each URL is reachable (curl-test or browser-test before launch)
- [ ] Visual exhibits referenced by the primary source are present (image filenames match what the source cites)
- [ ] No `.git/` or OS-junk files

## What `trial start` does with your corpus

When you invoke `python -m app.marcus.cli trial start --input course-content/courses/<lesson_slug> [...]`:

1. The runner accepts the `--input` path.
2. The §02A directive composer (LLM-driven; closed Trial-2 finding #2) reads your corpus directory + any `urls.txt` + your operator-supplied directives template (if any).
3. The composer materializes a `directive.yaml` at `<run-dir>/run/directive.yaml`. **This is the high-stakes artifact.** It represents Texas's retrieval intent.
4. **You review the directive at G0.** This is the §02A operator decision — `approve` if the directive correctly captures your corpus's retrieval shape, `edit` to adjust, `reject` if fundamentally wrong.
5. After G0 approval, Texas's `dispatch_retrieval(directive_path, bundle_dir)` produces real retrieval evidence into the bundle.

**Key insight:** the corpus directory is your INPUT; the `directive.yaml` is the runtime-composed RETRIEVAL PLAN. If your corpus is shaped wrong, the directive will be wrong, and the trial will go sideways — but you can catch that at G0 if you read the directive carefully.

## FRESH-corpus-specific notes (Trial-3+)

Trial-3 (and every subsequent trial) starts from a **fresh corpus** — not a Trial-2 carry-forward. Per operator declaration 2026-05-07: *"no more use of prior course material as a crutch. we'll start with fresh course source material — total start from zero."*

This means:
- Do NOT seed your corpus directory with files from `tests/fixtures/specialists/texas/` or any prior-trial bundle.
- Do NOT carry forward the Trial-2 Tejal corpus contents into the Trial-3 directory.
- Each trial corpus is its own thing.
- Trial-2 fixtures may remain on disk for forensic comparison (Murat's recommendation — keep `tests/agents/bmad-agent-texas/test_cross_validator.py:195` Tejal path satisfiable) but they don't seed Trial-3.

## Common mistakes (and how to avoid them)

| Mistake | Symptom | Fix |
|---|---|---|
| Corpus at `sources/` instead of `course-content/courses/<slug>/` | Texas dispatches against empty bundle; trial halts at G0 with "directive composer found no corpus" | Move corpus to canonical path before launch |
| `.gitkeep` placed in directory but no real content | Trial-2 regression: gitkeep gets promoted to "primary source" by directive composer fallback | Don't use `.gitkeep` files in corpus dirs; or ensure real content is present in same dir |
| Notion-URL-shape directive committed as corpus content | Directive composer attempts to treat URL list as a primary source | Move URLs to `urls.txt` (flat file in corpus dir) — composer will treat as fetch-shape |
| Mixed case slug (`Tejal-APC-C1`) | Path mismatch downstream | Use kebab-case lower throughout |
| Non-unique slug (`lesson1`) | Multiple trials collide on same path | Always use descriptive unique slug |
| Visual exhibits referenced but not present | Pass-1 narration draft references missing images; G1 fails | Verify all referenced images are in corpus dir |
| `urls.txt` present but URLs unreachable | Texas retrieval times out OR returns empty pages | Curl-test each URL before launch |

## Related references

- `docs/operator/hil-verb-legend.md` — what each HIL verb means at each gate
- `_bmad-output/implementation-artifacts/trial-3-readiness-checklist.md` — full launch playbook
- `_bmad-output/implementation-artifacts/migration-7c-3a-section-02a-llm-directive-composer-body.md` — §02A composer's expected corpus shape (developer reference)
- `docs/trials/methodology.md` (S3 deliverable) — how corpus shape relates to trial-success criteria
- `docs/conversational-gates/g0-operator-reference.md` — what to look for when reviewing the §02A directive at G0
