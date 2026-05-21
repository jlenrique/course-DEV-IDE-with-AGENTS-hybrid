# Trial-N Launch (Template)

> **Template usage:** copy this file to `docs/trials/trial-N/launch.md` BEFORE you launch Trial-N. Fill placeholders. Read the EXAMPLE block at the top to anchor the shape; then fill the EMPTY block below it. Reads in 5 minutes; fills in 10-15 minutes.

---

## EXAMPLE — what a filled launch.md looks like

(This block is illustrative only — delete after copying the template, OR keep as a comparison anchor while you fill your own launch.)

```yaml
trial_id: trial-3.dry-run-example
date: 2026-05-08
operator: Juanl
branch: dev/langchain-langgraph-foundation
head_sha: e48e107
working_tree: clean
corpus_path: course-content/courses/clinical-judgment-fundamentals-w1/
corpus_shape:
  primary: clinical-judgment-w1-lesson.docx
  supporting: 3 PDFs (textbook chapters); 2 PNG visual exhibits
  optional: urls.txt (4 reachable URLs)
hypothesis: |
  Verify post-Slab-7c substrate executes G0 → G5 cleanly on a FRESH corpus
  (no Tejal-APC carry-forward). Watching: §02A composer correctly identifies
  primary .docx; G2C storyboard build with new corpus shape; G5 Marcus §15
  bundle writer produces coherent DESCRIPT-ASSEMBLY-GUIDE.md.
expected_evidence:
  - Trial3Transcript schema-valid; gate decisions G0/G2C/G3/G4 all approve
  - tripwire ledger green (no TW-7c-* firings beyond known reservations)
  - cost report ≤ $5 (per Murat 7c.21a opt-in budget)
deferred_inventory_triggers_in_play:
  - "Epic 15 reactivation chain (`at least one tracked trial run completed`)"
known_risks:
  - cred-readiness: OPENAI_API_KEY confirmed; ELEVENLABS_API_KEY confirmed
  - corpus risk: first time with non-Tejal corpus; §02A composer LLM-judgment unknown
launch_command: |
  $env:PYTHONIOENCODING="utf-8"
  .\.venv\Scripts\python.exe -m app.marcus.cli trial start `
    --preset production `
    --input course-content/courses/clinical-judgment-fundamentals-w1/ `
    --motion-enabled
verdict_predicted: PASS or PARTIAL-PASS (FRESH corpus first-attempt risk)
```

---

## ACTUAL — fill below

### 1. Identification

| Field | Value |
|---|---|
| trial_id | `trial-3` |
| run_id | `<fill IMMEDIATELY after launch from runner stdout — Murat post-S3 amendment for forensic-trail bidirectionality with log.md>` |
| date | `<YYYY-MM-DD>` |
| operator | `Juanl` |
| branch | `<branch>` |
| head_sha | `<sha>` |
| working_tree | `<clean / N modifications described below>` |

### 2. Pre-flight checklist

Lifted from `docs/trials/methodology.md §3` evidence taxonomy + `_bmad-output/implementation-artifacts/trial-3-readiness-checklist.md §3`. Check each box.

- [ ] `git status` clean (or modifications explicitly named below)
- [ ] `.venv` present + Python ≥3.11
- [ ] `OPENAI_API_KEY` set (`Get-Content .env | Select-String "OPENAI_API_KEY"`)
- [ ] `LANGSMITH_API_KEY` + `DATABASE_URL` set (recommended for tracing + persistence)
- [ ] Per-API smoke env vars set as needed for trial scope (`WONDERCRAFT_API_KEY` / `ELEVENLABS_API_KEY` / `GAMMA_API_KEY` / `KLING_*` / `SCITE_*` / `CONSENSUS_API_KEY`)
- [ ] Corpus directory at `course-content/courses/<lesson_slug>/` (kebab-case slug)
- [ ] Corpus shape valid per `docs/operator/corpus-preparation-guide.md` (primary source + supporting refs; no `.gitkeep` in primary slot; no Notion/Box fetch-shape contamination)
- [ ] Preflight runner GREEN: `python -m skills.pre-flight-check.scripts.preflight_runner --double-dispatch --motion-enabled`
- [ ] Final-launch token GREEN: `pytest tests/trial/test_trial3_readiness.py tests/test_preflight_check.py tests/marcus_capabilities/test_preflight_receipt_contract.py -v`
- [ ] HIL verb legend within thumb-reach (`docs/operator/hil-verb-legend.md` printed / second monitor)
- [ ] `cross-trial-learnings.md` skim done (5 min; check for prior-trial learnings touching the surfaces this trial will exercise)

### 3. Corpus declaration

| Field | Value |
|---|---|
| corpus_path | `course-content/courses/<lesson_slug>/` |
| primary | `<filename>` |
| supporting | `<N files; brief description>` |
| visual exhibits | `<N PNG/JPG/SVG>` |
| urls.txt | `<N URLs / not present>` |
| total file count | `<N>` |

### 4. Trial intentions (prose; 3 questions)

**What corpus and why this corpus?**
> _Operator fills_

**What are you watching for that you didn't watch in Trial-(N-1)?**
> _Operator fills — this question forces continuity with `cross-trial-learnings.md`_

**What evidence would change your understanding of the substrate?**
> _Operator fills — names the hypothesis explicitly_

### 5. Deferred-inventory triggers in play

Names the deferred-inventory entries whose reactivation triggers this trial may fire. (Each fired trigger gets recorded bidirectionally at postmortem close — see `methodology.md §7`.)

- _Operator fills_

### 6. Known risks + tripwires to watch

- _Operator fills (cred-readiness; corpus-risk; tripwire reservations relevant to this trial)_

### 7. Launch command

```
$env:PYTHONIOENCODING="utf-8"
.\.venv\Scripts\python.exe -m app.marcus.cli trial start --preset production --input <corpus-path> [--motion-enabled] [--double-dispatch]
```

### 8. Tape this — taped highlight reel (one screen)

**HIL verb critical-path (from `docs/operator/hil-verb-legend.md` lines 60-73):**
1. §02A G0: `approve` (directive correct)
2. §04 G1: `approve` (Pass-1 packet OK)
3. §04A G1A: `approve` (per-plan-unit; one decision per row)
4. §04.55 G1.5 lock: **`lock`** — IRREVERSIBLE
5. §07B G2M: `select A` or `select B` per slide variant
6. §07D G2.5: `approve` (motion-plan)
7. §08B G3B: `approve` (Storyboard B + live URLs)
8. §09 G3 lock: **`lock`** — IRREVERSIBLE; four-artifact pin
9. §11 G4A: `select` (voice ID)
10. §11B G4B: `approve` (input package)
11. §15 G5: **`complete`** (trial closes successfully)

**FAIL signals — halt and document:**
- Substrate behaves UNEXPECTEDLY (silent corruption; contract violation that didn't fail loud) — `FAIL` verdict
- Operator can't choose between the proposed verbs because the artifact is so wrong neither makes sense — consider `reject`
- Tripwire ledger fires unexpectedly — note + continue OR halt per the tripwire's documented severity

### 9. Predicted verdict

`<PASS / PARTIAL-PASS / STRUCTURED-STOP / FAIL>` — the operator's expectation pre-launch. Compare to actual at postmortem.
