# Trial-3 Attempt-3 — Operator Playbook (End-to-End Driver)

**Date:** 2026-06-11
**Role:** Thin sequencing layer. This document ORDERS the trial-day steps and fills two gaps
(corpus staging + artifact inspection); it does NOT duplicate authoritative content.
**Authoritative companions (open side-by-side):**
- [`trial-3-operator-guide-attempt-3.md`](trial-3-operator-guide-attempt-3.md) — verbs, defaults, escalation, evidence. **Guide §4 verb table is authoritative; verbs echoed here are a convenience mirror.**
- [`trial-3-readiness-checklist.md`](trial-3-readiness-checklist.md) — prerequisites, success criteria, transcript validation.
- `docs/operator/hil-verb-legend.md` — canonical per-gate verb sets.

**Scrub status:** pre-trial confidence scrub completed 2026-06-10 @ `bb81b6f` — VERDICT: GO, Confidence 10/10.
Includes the G0 composer no-primary landmine fix (template + mandatory G0 role-check).

---

## Phase 0 — Corpus staging (DO THIS FIRST; fresh Tejal C1M1 material)

The §02A composer walks the corpus directory **live at `trial start`** — whatever is on disk at launch
is what gets classified and dispatched. Stage content BEFORE any pre-flight checks.

**Canonical corpus path (per repo convention `course-content/courses/<lesson_slug>/`):**

```
course-content/courses/tejal-apc-c1-m1-p2-trends/
├── README.md          # corpus orientation (classified supporting)
├── urls.txt           # flat URL list (allowed in corpus dir per directive-scope convention)
├── slides/            # core teaching content — composer should classify these primary
├── assessments/       # knowledge checks
└── references/        # companion/reading references
```

**Staging steps for the fresh/updated C1M1 material:**

1. **Place updated files** into the structure above (replace or add; delete superseded files —
   the composer classifies EVERY file it finds; stale leftovers become directive rows).
2. **Text formats preferred** (.md / .txt / .docx). Binary media (PNG/PPTX/PDF/MP4) is allowed —
   the composer assigns binary-appropriate rules — but note binary media under `course-content/`
   is **gitignored** (present on disk for the trial, not tracked).
3. **No empty dir, no `.gitkeep`-only content** — composer raises `DirectiveCompositionError` on an
   empty corpus; marker files becoming sources was the Trial-2 degenerate signature.
4. **Re-run the encoding scan** after staging (scrub ENC-CORPUS covered yesterday's files only):
   ```powershell
   # prints NON_CP1252_CODEPOINTS: <n>; n>0 is acceptable (UTF-8 guard landed at trial.py:48-59)
   .\.venv\Scripts\python.exe C:\tmp\scrub_g0_dryrun.py   # also re-rolls the composer dry-run
   ```
   The dry-run re-roll matters: composition is LLM-driven per launch; new content = new
   classification. Confirm `CHECK has_primary: PASS` on the fresh corpus. (If the scratch probe
   script is gone, the G0 role-check in Phase 2 is the deterministic backstop.)
5. **Commit the staged text content** (tracked .md/.txt) before launch so the trial runs against a
   recorded corpus state: `git add course-content/courses/tejal-apc-c1-m1-p2-trends/ && git commit`.

**When:** any time before Phase 1. **Never** edit corpus files after `trial start` — gate-pause
edits go through verdict `edit` payloads, not the filesystem.

---

## Phase 1 — Pre-flight (10 min)

Run the guide §1 checklist top-to-bottom. Condensed command sequence:

```powershell
git status --short                          # clean (corpus commit landed)
git log -1 --oneline                        # note launch SHA
$env:PYTHONIOENCODING = "utf-8"             # per A11; guard also pins this in-process
.\.venv\Scripts\python.exe --version        # 3.11+
.\.venv\Scripts\python.exe -m scripts.utilities.app_session_readiness   # all pass
node scripts/heartbeat_check.mjs            # trial-path APIs green (Botpress fail = ignorable)
.\.venv\Scripts\python.exe -m pytest tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py skills/bmad-agent-texas/scripts/tests/test_run_wrangler_role_enum_union_and_excluded_reason.py skills/bmad-agent-texas/scripts/tests/test_run_wrangler_sme_refs_emission.py tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py -q
# expect: 29 passed
```

`.env` must carry `OPENAI_API_KEY`, `DATABASE_URL`, `LANGSMITH_API_KEY` + `LANGSMITH_PROJECT`
(enforced by `start_trial`), plus production-preset provider keys. Two terminals open; escalation
session NOT pre-opened (guide §1).

---

## Phase 2 — Launch + G0 (in-process gate)

```powershell
$env:PYTHONIOENCODING = "utf-8"
.\.venv\Scripts\python.exe -m app.marcus.cli trial start --preset production --input course-content/courses/tejal-apc-c1-m1-p2-trends/ --operator-id juanl
```

**Note the trial UUID from stdout immediately** — every resume needs it.

At the G0 prompt (directive printed above the prompt):

1. **MANDATORY role-check (scrub finding):** confirm ≥1 source has `role: primary` (or
   `visual-primary`). If all-`supporting`: press `e`, promote the central content source(s)
   (slide files for this corpus) to `primary`, save, confirm. The wrangler rejects no-primary
   directives fail-loud.
2. Sanity-glance locators (no `.gitkeep`, no stale files you meant to delete in Phase 0).
3. Press `c` (attempt-3 default).

**Artifact to inspect at this gate:** the composed directive YAML (path printed in the prompt) +
`model_resolution_trail.json` sidecar in the run dir.

---

## Phase 3 — Gate-by-gate walk (§04 → §15)

After G0 every gate **pauses-and-exits the process** (guide §4). Per pause, the loop is always:

1. `state/config/runs/<uuid>/run.json` → confirm `status=paused-at-gate`, note `paused_gate`.
2. Open `state/config/runs/<uuid>/decision-card-<gate_id>.json` — the card carries the digest you
   must echo, the editable-fields whitelist, AND payload refs/paths to the section's review
   artifacts. **The decision card is the index to what to inspect.**
3. Review the surface for that gate (table below).
4. Compose `verdict.json` (guide §5 recipe; copy `decision_card_digest` verbatim).
5. `.\.venv\Scripts\python.exe -m app.marcus.cli trial resume --trial-id <uuid> --verdict-file .\verdict.json`

| Order | Gate | § | What you're reviewing (inspection surface) | Default* |
|---|---|---|---|---|
| 1 | G1 | §04 | Plan units in the decision card payload — lesson-plan shape vs your C1M1 intent | `approve` |
| 2 | G1A | §04a | Per-plan-unit rows (poll per row) | `approve` all |
| 3 | G1.5 | §04.5 | Estimator output (slide-count/runtime projection) — sanity vs corpus size | `acknowledged` |
| 4 | G1.5-lock | §04.55 | ⚠️ **Irreversible sha256 plan-pin.** Last exit before production spend | `lock` |
| 5 | G2B | §05.5 | Per-slide-mode assignments (creative / literal-text / literal-visual) | `approve` |
| 6 | G2-submit | §06b | Gary dispatch package pre-submit (slide content payloads) | `submit` |
| 7 | G2M | §07b | Per-slide variant selection set — pick top candidate | `select` |
| 8 | G2.5-submit | §07c | **STORYBOARD A** (pre-Pass-2: slides only, narration pending) — see Phase 4 | `submit` |
| 9 | G2.5 | §07d | Post-storyboard approval of the slide set | `approve` |
| — | (§07f) | §07f | Body-validated; runner does NOT pause here | n/a |
| 10 | G3B | §08b | **STORYBOARD B** (post-Pass-2: slides + narration inline) — see Phase 4 | `approve` |
| 11 | G4A | §11 | Voice/audio selection set (Enrique/Wanda outputs) — listen before selecting | `select` |
| 12 | G4B | §11b | Audio/visual input package pre-final-assembly | `approve` |
| 13 | G5 | §15 | Final handoff — **do Phase 5 inspection BEFORE pressing complete** | `complete` |

\* Mirror of guide §4 (authoritative). Weed-clearing posture: default-accept; harvest nits to the
postmortem, not at-gate edits. Any smell → guide §7 escalation chain (pause is already persisted;
open a SEPARATE session for Marcus-agent).

---

## Phase 4 — Storyboard review (A at §07c, B at §08b) — on the Git public site

Storyboard generation is Marcus-owned and baked into the run routines
(`skills/bmad-agent-marcus/scripts/generate-storyboard.py`; runtime emitter at
`app/gates/section_07c/storyboard_html_emitter.py`; §08b poll surface loads Storyboard B for G3B).

**Where you review:** the GitHub Pages public site (`jlenrique.github.io`, published via
`GITHUB_PAGES_TOKEN` — see `docs/admin-guide.md` Tier-1 table). Storyboard A and B land there as
self-contained HTML.

- **Storyboard A (at the §07c pause):** slides-only view — ordered slide cards, thumbnails,
  literal-visual fills, provenance metadata. Narration shows *Pending (pre-Pass 2)* — that is
  correct at this stage, not a defect. Review: slide order, visual fills (no faded/background
  literal-visuals), coverage vs plan units.
- **Storyboard B (at the §08b pause):** same surface + Irene Pass-2 narration inline per slide.
  Review: narration matched to right slides (no *No match* / *Multi-match* rows), motion-enabled
  cards show still + motion clip, script reads in-voice.
- **Fallback if the Pages publish hasn't landed when the gate pauses:** open the local copy —
  `<bundle-dir>/storyboard/index.html` (path referenced from the decision card / run dir), or
  regenerate + export a Pages-ready snapshot per
  `skills/bmad-agent-marcus/references/storyboard-procedure.md` §3 (`generate-storyboard.py export`
  → `exports/storyboard-<RUN_ID>/`).

The HTML is view-only — **approval still happens via the verdict file at the CLI**, never in the page.

---

## Phase 5 — Final artifact inspection (before `complete` at G5)

The §15 bundle writer (`section_15_bundle.py`) only emits on `verb=complete` — so inspect the
assembly inputs BEFORE composing the G5 verdict:

- [ ] **Assembly bundle dir** (path in the G5 decision card): slide exports present (PNG
      production quality), narration audio per segment, captions/VTT if in scope.
- [ ] **Segment manifest** consistency: every segment has its `gary_slide_id` + narration; motion
      segments carry both `visual_file` (still) and `motion_asset_path` (MP4).
- [ ] **Storyboard B final state** on the public site matches the bundle contents.
- [ ] Then press `complete`. **After** completion verify the bundle writer outputs:
  - `<assembly_bundle_path>/DESCRIPT-ASSEMBLY-GUIDE.md` (regenerated; sha256 recorded in bundle)
  - `state/config/runs/<uuid>/Trial3Transcript.json` — non-zero size, then validate:
    ```powershell
    .\.venv\Scripts\python.exe -c "from pathlib import Path; from app.models.trial3_transcript import Trial3Transcript; import json; t = Trial3Transcript.model_validate(json.loads(Path('state/config/runs/<uuid>/Trial3Transcript.json').read_text(encoding='utf-8'))); print(len(t.events), 'events; trial', t.trial_id)"
    ```
  - slab-close evidence pointer recorded in the bundle payload.

**On FAIL at any point:** preserve `state/config/runs/<uuid>/` per guide §8 BEFORE any retry;
never reuse the trial-id for attempt-4.

---

## Phase 6 — Post-trial BMAD analysis (separate chat session, after closeout)

Sequence (PASS or FAIL):

1. **Trial postmortem with Marcus-agent** (fresh session; activate per
   `skills/bmad-agent-marcus/SKILL.md`). Inputs: `Trial3Transcript.json`, run-dir evidence,
   LangSmith trace/cost report, your at-gate nit harvest.
2. **Four-question routing** of every finding per `docs/trials/methodology.md §7`; file harvest
   entries in `docs/trials/cross-trial-learnings.md` (bidirectional citation if any
   deferred-inventory reactivation trigger fired).
3. **`bmad-retrospective` on Epic 34** — binding consultation point (CLAUDE.md deferred-inventory
   governance #1); deliberately sequenced AFTER the trial so it's informed by attempt-3 evidence.
   Includes deferred-inventory review against the new evidence.
4. **Next-steps planning** — candidates already queued (next-session-start-here.md): SCP-2026-05-19
   substrate amendment, Marcus-interactive-experience Epic, doc-currency batch, composer-level
   primary-presence enforcement (scrub follow-on), Epic 15 reactivation on Trial-3 PASS.
5. **Session WRAPUP** per `bmad-session-protocol-session-WRAPUP.md` (push mandatory at Step 12).

---

*Authored 2026-06-11 post-scrub (`bb81b6f`). Artifact paths verified against substrate:
`composer.py`/`cli_adapter.py` (G0), `storyboard_html_emitter.py` + `poll_surface.py` §07c/§08b
(storyboards), `section_15_bundle.py` (G5 bundle), `trial.py` CLI flags. Per-gate review surfaces
beyond those are indexed by each gate's decision card rather than hardcoded here — the card's
payload refs are authoritative for that pause.*
