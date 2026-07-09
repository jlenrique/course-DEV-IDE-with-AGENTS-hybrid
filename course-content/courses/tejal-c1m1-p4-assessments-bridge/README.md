# Corpus - tejal-c1m1-p4-assessments-bridge

**S8 proof intent:** S8 full-close composed proof.
**Expected bundle:** `narrated-deck-with-workbook` (deck + motion + workbook).
**HIL operator:** `juanl`.
**Tejal exception:** allowed by explicit operator declaration on 2026-07-08 because Tejal C1M1 is the only real course-content family currently available. HAI 510 and PHS 620 remain syllabus/reference fixtures and are deferred from this proof.

## Source

- **Source of truth:** `course-content/courses/tejal-c1m1-fresh-outline/source-outline.md`
- **Section pulled:** `Part 4: Assessments & The Bridge to Module 2`
- **Curated from:** the source-outline Part 4 section, lines 581-735 in the current local snapshot.
- **Raw sibling snapshot:** `course-content/courses/tejal-c1m1-p4-assessments-bridge-raw/part4-assessments-bridge.md`

This corpus intentionally mirrors the Part 2 / Part 3 curated shape while keeping the raw extracted source outside the curated corpus directory so recursive ingestion does not double-count.

## Layout

- `slides/` - **PRIMARY bridge material**: the summary / bridge-to-Module-2 closing video storyboard and narration. Part 4 does not provide a conventional multi-slide lecture sequence.
- `assessments/` - **PRIMARY assessment and workbook material**: Discussion Post 3, comprehensive module knowledge check, Innovation Leader Playbook Entry #1, and the master grading rubric.
- `references/` - **SUPPORTING provenance and gaps**: source notes, conceptual-pillar carry-forward, and the explicit source-gap ledger.
- `urls.txt` - flat URL/provenance list. The Part 4 section itself does not provide new external HTTP readings.

## Known Gaps

- No standalone Part 4 lecture-slide deck is present in the source section.
- No Part 4 source PDF is present in the source section.
- No Part 4 image/media folder is present in the source section.
- No DOI-indexed reference appears inside the Part 4 section.
- Motion source is only a high-level bridge-video storyboard, not a rendered motion asset.

These are intentional evidence records, not placeholders. Downstream generation must fail loud or request source if it needs assets that Part 4 does not actually provide.

## Proof Notes

The adequacy wrinkle is material: Part 4 is assessment/bridge-heavy relative to Parts 2 and 3. G0R should pressure-test whether this source is adequate for a full narrated-deck + motion + workbook production claim and must surface gaps rather than invent missing slide, media, or motion source.
