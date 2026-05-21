---
name: storyboard-procedure
description: Gary slide storyboard — Marcus-owned review surface before and after Irene Pass 2
code: SB
---

# Gary Slide Storyboard (HIL, pre-Irene and post-Irene)

**Ownership:** Storyboard **creation** (generate HTML/JSON, manifest-derived recap, conversational approval, persist `authorized-storyboard.json`) is **a Marcus skill only**. It is not a separate specialist skill and not owned by Gary or Irene: Gary supplies the dispatch payload, including any additive `literal_visual_publish` receipt when tracked-mode preintegration staging occurred; Irene consumes outputs **after** authorization when the runbook says so. Marcus runs this capability end-to-end for the operator.

## Two Review Views (Same Command, Different Inputs)

- **Before Irene (Pass 2):** Gary dispatch only. HTML renders a reviewer-friendly storyboard surface with ordered slide cards, thumbnails, search/filter controls, script status, script notes, and provenance/orientation metadata. Narration stays *Pending (pre-Pass 2)* for every row.
- **After Irene:** Same generator, add Irene's **segment manifest YAML** (`segments[].gary_slide_id` + `narration_text` per `skills/bmad-agent-content-creator/references/template-segment-manifest.md`). The same review surface shows **slide preview + narration text** inline. Unmatched slides show *No match* rather than silently appearing pending, multi-segment collisions surface as *Multi-match*, and motion-enabled slides expose their approved motion review metadata.

After Gary's Gamma dispatch is packaged, Marcus may generate or **regenerate** the **view-only** storyboard so the operator can review **all slides at once** (creative, literal-text, literal-visual) in run order; after Pass 2, regenerate with `--segment-manifest` to include script. Remote hosted assets remain remote in the storyboard manifest; local slide PNGs remain the review source of truth for Gate 2.

## Procedure

1. **Generate** (from repo root, paths adjusted to the run bundle):

   `.\.venv\Scripts\python.exe skills/bmad-agent-marcus/scripts/generate-storyboard.py generate --payload <gary-dispatch.json|yaml> --out-dir <bundle-dir> [--asset-base <dir>] [--segment-manifest <manifest.yaml>] [--related-assets <assets.json|yaml>] [--print-summary]`

   - Writes `<bundle-dir>/storyboard/storyboard.json` and `.../index.html` (`storyboard_version` 3; `storyboard_view` is `slides_only` or `slides_with_script`).
   - Resolve local PNGs with `--asset-base` when `file_path` is relative to something other than the payload's directory.
   - Remote URLs are preserved as remote preview links rather than downgraded to missing assets.
   - **`--segment-manifest`:** optional Pass 2 YAML; **PyYAML** required when used.
   - **`--related-assets`:** optional JSON/YAML for non-slide run artifacts (video/audio/interactive/source links) appended after slide rows.
   - **`--run-id`:** optional APP run identifier for Channel C log correlation.

2. **Review:** Open `storyboard/index.html` in a browser. The page is static and self-contained: collapsible summary banner (Run details `<details>` element, open by default), ordered slide cards, click-to-expand thumbnails, script/script-notes panels, issue filtering, and a separate related-assets section. Motion-enabled cards use a stacked layout (slide + video in column 1, script spanning column 2) to eliminate dead space. No approval controls live in the page.

3. **Share/export (self-contained snapshot):** When the operator wants to share the storyboard outside the repo, export a sanitized snapshot from the canonical manifest:

   `.\.venv\Scripts\python.exe skills/bmad-agent-marcus/scripts/generate-storyboard.py export --manifest <bundle-dir>/storyboard/storyboard.json`

   - Writes a self-contained folder under repo-root `exports/storyboard-<RUN_ID>/` plus a deterministic zip at `exports/storyboard-<RUN_ID>.zip`.
   - The exported `index.html` lives at the snapshot root for simple browser-open and Pages hosting.
   - Exported files are allowlist-only: `index.html`, `storyboard.json`, and the referenced local review assets needed by the HTML.
   - Local absolute paths are rewritten to snapshot-relative refs before export so the shared package does not leak workstation paths.

4. **Publish (GitHub Pages snapshot):** For tracked/default runs with `GITHUB_PAGES_TOKEN` and a discoverable `site_repo_url`, publish the exact same snapshot tree to the managed public repo:

   `.\.venv\Scripts\python.exe skills/bmad-agent-marcus/scripts/generate-storyboard.py publish --manifest <bundle-dir>/storyboard/storyboard.json`

   - Default destination subtree: `assets/storyboards/<RUN_ID>/`
   - The zip and the published site tree are intentionally the same snapshot shape.
   - Publish is idempotent when the destination already matches the snapshot, and fail-closed when the destination exists with different contents.
   - This is a review-share surface only; it does not replace the canonical in-bundle storyboard manifest or `authorized-storyboard.json`.

5. **Summarize (manifest-only):** Marcus reads aloud the same recap the tool would print:

   `.\.venv\Scripts\python.exe skills/bmad-agent-marcus/scripts/generate-storyboard.py summarize --manifest <bundle-dir>/storyboard/storyboard.json`

6. **Confirm in chat:** Operator explicitly approves after the recap (count, first/last `slide_id`, fidelity counts). In tracked/default runs, do this only after `validate-gary-dispatch-ready.py` returns clean for the dispatch payload.

7. **Authorize (fail closed on overwrite):**

   `.\.venv\Scripts\python.exe skills/bmad-agent-marcus/scripts/write-authorized-storyboard.py --manifest <bundle-dir>/storyboard/storyboard.json --run-id <RUN_ID> --output <bundle-dir>/authorized-storyboard.json`

   - If `--output` already exists, the script **exits with error** and does not overwrite.

8. **Motion-enabled runs only:** After `authorized-storyboard.json` exists and `motion_enabled: true`, Marcus treats the authorized winner deck as the source of truth for **Gate 2M**.

   - Build the run-scoped motion plan from the authorized deck, not from raw Gary output and not from a future segment manifest.
   - Always present a recommendation set before operator designation. Every slide needs a recommended motion type, rationale, source anchor, and confidence label.
   - Recommendations are a starting point only; the operator can override any slide or add more detail.
   - If the operator overrides Marcus's recommendation, require a short `override_reason` so the recommendation and final decision remain auditable.
   - Persist Gate 2M decisions in `context_paths.motion_plan` (`motion_plan.yaml`) keyed by `slide_id`.
   - Reject any Gate 2M payload that references unknown slide IDs or omits authorized slides; do not silently drop stale or incomplete designation keys.
   - `motion_enabled` is the authoritative Epic 14 activation switch. The workflow variant and effective content type are derived from that flag during production-plan generation; they do not independently authorize motion work.
   - If the production plan started from `narrated-deck-video-export`, use `generate-production-plan.py --motion-enabled` to promote the workflow to the motion variant (`gate-2 -> gate-2m -> motion-generation -> motion-gate -> Irene Pass 2`).

Optional: `--strict` on `generate` exits non-zero when any slide has a **missing** local asset (storyboard files are still written).

**Roadmap:** Follow-on expansion and governance wiring continue in `_bmad-output/specs/sb-1-evolving-lesson-storyboard-run-view.md` (Story **SB.1**, Epic **SB**).
