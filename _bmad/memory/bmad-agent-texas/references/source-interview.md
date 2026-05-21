---
name: source-interview
description: Gather source knowledge from the HIL operator through Marcus
code: SI
---

# Source Interview

## What Success Looks Like

By the end of the interview, you have a complete source manifest for the run — every provider identified, every file located, every role assigned, every known issue surfaced. The operator has told you where the gold is and where the landmines are, and you haven't missed any available assets hiding in the course content folder.

## Your Approach

The source interview happens through Marcus — you never talk to the operator directly. Marcus gathers your questions and relays the operator's answers.

### Discovery

Start by scanning the course content directory (`course-content/courses/{course-slug}/`) to understand what's available. Catalog file types, sizes, and modification dates. Then ask Marcus to confirm with the operator:

- Which files are the **primary sources** for this run? (The content that must be fully extracted)
- Which files serve as **validation references**? (Alternative formats of the same content, useful for cross-checking extraction quality — e.g., an MD version of a PDF, a DOCX of the full module)
- Which files are **supplementary**? (Background material, images, exemplars — not primary extraction targets)
- Are there any **known issues**? (Scanned pages, password protection, Notion exports masquerading as PDFs, content that's been recently updated)
- Are there any **external sources** the operator wants pulled? (Notion pages, URLs, Box folders)
- What is the **expected scope**? ("This is Part 1 of Module 1, covering slides 1-6 and a knowledge check")

### Source Manifest

Build a structured manifest from the interview:

```yaml
source_manifest:
  course_slug: "tejal-APC-C1"
  course_content_dir: "course-content/courses/tejal-APC-C1/"
  sources:
    - ref_id: "src-001"
      provider: "local_file"
      locator: "APC C1-M1 Tejal 2026-03-29.pdf"
      format: "pdf"
      role: "primary"
      description: "Full module PDF, 24 pages"
      known_issues: []
    - ref_id: "src-002"
      provider: "local_file"
      locator: "C1M1Part01.md"
      format: "md"
      role: "validation"
      description: "Part 1 content in markdown — covers slides 1-6 + knowledge check"
      coverage_scope: "part_1_only"
    - ref_id: "src-003"
      provider: "local_file"
      locator: "APC C1-M1 Tejal 2026-03-29.docx"
      format: "docx"
      role: "validation"
      description: "Full module in Word format — broader scope than MD but less structured"
      coverage_scope: "full_module"
```

### Multiple Validation Assets

A key insight: validation assets have different strengths. The MD file may cover only Part 1 but with rich structure (headings, slide-by-slide content). The DOCX may cover the full module but with less markdown structure. When cross-validating, weight each asset by its coverage relevance to the section being checked.

## Memory Integration

Check MEMORY.md for previous source manifests for this course. If you've wrangled `tejal-APC-C1` before, you know what files exist, what extraction methods worked, and what the baseline word counts are. Surface this: "Last time I extracted this PDF, I got 7,514 words across 786 lines. If this run produces significantly less, something changed."

## After the Session

Record the source manifest and any operator-provided context in your session log. Update MEMORY.md with learned source patterns for this course slug.
