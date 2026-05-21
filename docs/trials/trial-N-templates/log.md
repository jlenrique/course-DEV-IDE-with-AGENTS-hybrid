# Trial-N Log (Template)

> **Template usage:** copy this file to `docs/trials/trial-N/log.md`. Fill DURING the trial OR compile from runtime artifacts immediately after. Append-only timeline; minimal interpretation, maximum fidelity. Postmortem interprets; log records.

---

## Format rules

- **Append-only.** Do not rewrite earlier entries.
- **One entry per gate decision** (or per attempt if multiple launches).
- **Texture note** is the load-bearing field — 1-3 sentences capturing the moment, not just the verb chosen.
- **Evidence-paste appendix** at the bottom for raw artifacts (run-id directories, transcript-validate output, cost reports).

---

## Timeline (chronological; append-only)

### Attempt 1

**Pre-launch state (paste from `launch.md` §1-2):**
- trial_id, date, operator, branch, head_sha, working_tree

**Launch invocation:**
```
<paste exact CLI command>
```

**Run-id (from runner output):**
- `<run-id>`

**Run-dir:**
- `state/config/runs/<run-id>/`

---

#### G0 — §02A operator directives composer

| Field | Value |
|---|---|
| Timestamp | `<HH:MM:SS>` |
| Verb chosen | `<approve / edit / reject>` |
| Texture | `<1-3 sentences: what did the directive look like? what made you confident or hesitant? did the LLM correctly identify primary vs supporting? did .gitkeep get filtered correctly?>` |
| Evidence | `<run-dir>/run/directive.yaml` (sha256: `<digest>`) |

#### G1 — §04 ingestion quality + Irene Pass-1 packet

| Field | Value |
|---|---|
| Timestamp | `<HH:MM:SS>` |
| Verb chosen | `<approve / edit / reject>` |
| Texture | `<1-3 sentences>` |
| Evidence | `<bundle>/irene-packet.md`; `<run-dir>/run/decisions/g1.json` |

#### G1A — §04A per-plan-unit ratification

| Field | Value |
|---|---|
| Timestamp | `<HH:MM:SS>` |
| Verb chosen | `<approve / edit / reject (per row)>` |
| Texture | `<1-3 sentences; multiple rows: summarize across or itemize if interesting>` |
| Evidence | `<run-dir>/run/decisions/g1a.json` |

#### G1.5 lock — §04.55 run-constants lock

| Field | Value |
|---|---|
| Timestamp | `<HH:MM:SS>` |
| Verb chosen | `<lock / edit>` |
| Texture | `<1-3 sentences; what did you confirm before locking? — IRREVERSIBLE>` |
| Evidence | `<run-dir>/run/run-constants.yaml` (sha256: `<digest>`) |

#### G2B — §05.5 per-slide presentation mode

| Field | Value |
|---|---|
| Timestamp | `<HH:MM:SS>` |
| Verb chosen | `<approve / edit / reject>` |
| Texture | `<1-3 sentences>` |
| Evidence | `<run-dir>/run/decisions/g2b.json` |

#### G2C — §07C storyboard build + HTML reviewer

| Field | Value |
|---|---|
| Timestamp | `<HH:MM:SS>` |
| Verb chosen | `<approve / edit / reject>` |
| Texture | `<1-3 sentences>` |
| Evidence | `<bundle>/authorized-storyboard.json`; `<bundle>/storyboard/index.html` |

#### G2.5 — §07D motion-plan polling

| Field | Value |
|---|---|
| Timestamp | `<HH:MM:SS>` |
| Verb chosen | `<approve / edit / reject>` |
| Texture | `<1-3 sentences>` |
| Evidence | `<bundle>/motion_plan.yaml` |

#### G3B — §08B Storyboard B + live URL

| Field | Value |
|---|---|
| Timestamp | `<HH:MM:SS>` |
| Verb chosen | `<approve / edit / reject>` |
| Texture | `<1-3 sentences>` |
| Evidence | `<bundle>/storyboard-b/`; live URL |

#### G3 lock — §09 four-artifact lock semantics

| Field | Value |
|---|---|
| Timestamp | `<HH:MM:SS>` |
| Verb chosen | `<lock / edit>` |
| Texture | `<1-3 sentences; FOUR artifacts pinned by sha256: script + manifest + motion_plan.yaml + authorized-storyboard.json. IRREVERSIBLE.>` |
| Evidence | locked sha256 set: `<digest>` × 4 |

#### G4A — §11 ElevenLabs voice selection

| Field | Value |
|---|---|
| Timestamp | `<HH:MM:SS>` |
| Verb chosen | `<select / edit / reject>` |
| Texture | `<1-3 sentences; voice ID + narration profile match>` |
| Evidence | `<bundle>/voice-selection.json` |

#### G4B — §11B input package preview

| Field | Value |
|---|---|
| Timestamp | `<HH:MM:SS>` |
| Verb chosen | `<approve / edit / reject>` |
| Texture | `<1-3 sentences>` |
| Evidence | `<bundle>/input-package.json` |

#### G5 — §15 final operator handoff (DESCRIPT-ready)

| Field | Value |
|---|---|
| Timestamp | `<HH:MM:SS>` |
| Verb chosen | `<complete / edit / reject>` |
| Texture | `<1-3 sentences; trial closes successfully if `complete`>` |
| Evidence | `<bundle>/DESCRIPT-ASSEMBLY-GUIDE.md`; `<run-dir>/run/trial-transcript.json` |

---

### Attempt 2 (if needed)

_(Trial-2 demonstrated 8-attempt linearization works well; structure subsequent attempts identically with their own run-ids.)_

---

## Inline forensic notes (free-form append)

Paste anything that doesn't fit the per-gate cells: error stacks, unexpected runtime behavior, screenshots, log paths, Slack-thread excerpts, etc.

---

## Evidence-paste appendix (raw artifacts)

### Trial transcript (final)

```json
<paste contents of <run-dir>/run/trial-transcript.json OR cite path>
```

### Cost report

```json
<paste contents OR cite path>
```

### Tripwire ledger entries (this trial)

```yaml
<paste relevant tripwire_events: entries from sprint-status.yaml>
```

### Other artifacts

- `<run-dir>/run/decisions/`: per-gate decision records
- `<bundle>/`: trial bundle directory
- `_artifacts/current-trial/`: calibration tripwire + engagement decay reports (per gate_runner.py post-S1 P0-2)
