# Trial-3 Attempt-3 — Operator Guide (Authoritative Single-Source)

**Status:** AUTHORITATIVE. Supersedes any prior conflicting Claude statements in this conversation.
**Date:** 2026-05-22
**Posture:** Weed-clearing / substrate-verification trial. Default-accept at every gate.
**Author:** Paige (BMAD tech-writer), synthesizing Marcus + Winston + Amelia (party-mode round 1, unanimous).

---

## 0. Bright-Line Clarification — READ BEFORE LAUNCH

There are **two distinct Marcuses**. Confusing them will cost you a trial run.

| | **Marcus-runtime** | **Marcus-agent (the BMAD persona)** |
|---|---|---|
| **What it is** | LangGraph orchestrator code under `app/marcus/` | A BMAD persona activated via `skills/bmad-agent-marcus/SKILL.md` in a Claude/Codex session |
| **Where it runs** | Inside `python -m app.marcus.cli trial start` | Inside a chat session (Claude Code, Codex, etc.) |
| **What it produces** | DecisionCards at §01→§15 gates; verb prompts on stdout; JSON state on disk | Conversational guidance, specialist routing, postmortem analysis |
| **Can it reason mid-trial?** | 🚫 **No.** It emits a constrained verb set `[c/e/s/x]` (or gate-specific variant). It does not "chat." | ✅ Yes — but **not inside the trial process**. |
| **Your interface during trial** | A CLI prompt accepting a single letter, or a `--verdict-file path.json` on resume | N/A. He is not on the other end of the prompt. |

**Operating implication.** During Trial-3 attempt-3 you are operating **Marcus-runtime** via verbs at a CLI. **Marcus-agent is your pre-flight and post-hoc interlocutor, not your in-flight one.** If you find yourself wanting to paste a multi-paragraph prompt at a gate, **stop** — that's a smell. Pause, exit, and consult Marcus-agent in a separate session (see §7 Escalation).

---

## 1. Pre-Launch Checklist

Run through this top-to-bottom before invoking `trial start`.

- [ ] **Branch state.** Confirm you are on `trial/3-2026-05-21` (or the branch designated by the readiness checklist). `git status` clean or only expected mods.
- [ ] **Virtual env active.** `.venv\Scripts\python.exe --version` returns the expected Python (3.11+).
- [ ] **Postgres native running.** No Docker. `pg_isready` on operator side (operator-gated check; not part of dev-AC). The runtime expects a reachable Postgres per `.env`.
- [ ] **`.env` keys present.** Confirm `OPENAI_API_KEY`, `DATABASE_URL`, `LANGSMITH_API_KEY` + `LANGSMITH_PROJECT` (required by `trial start` unless `--allow-offline-cost-report`), and any provider keys used by the production preset. Do NOT echo values. (`ANTHROPIC_API_KEY` removed 2026-06-10 scrub — zero references in `app/`; OpenAI is the locked provider.)
- [ ] **Encoding:** `$env:PYTHONIOENCODING = "utf-8"` set in the current PowerShell session. Without this, gate prompts emit mojibake on Windows.
- [ ] **Corpus present.** `course-content/courses/tejal-apc-c1-m1-p2-trends/` exists and contains the expected source files.
- [ ] **Two terminals ready.** One for the trial process. One spare PowerShell window (resume commands, jq, ls of run-dir) so you don't Ctrl+C the trial by accident.
- [ ] **Separate Claude/Codex session standing by.** For escalation only. Don't pre-open Marcus-agent unless you hit a smell — pre-opening biases you toward consulting.
- [ ] **Readiness checklist re-read.** `_bmad-output/implementation-artifacts/trial-3-readiness-checklist.md` (refreshed today) — §1-§6 should all be ✅.

---

## 2. Launch Command

Exactly this, in PowerShell, from repo root:

```powershell
$env:PYTHONIOENCODING = "utf-8"
.\.venv\Scripts\python.exe -m app.marcus.cli trial start --preset production --input course-content/courses/tejal-apc-c1-m1-p2-trends/
```

The runtime allocates a fresh trial UUID and writes the run directory under (typically) `state/config/runs/<uuid>/`. **Note the UUID from stdout** — you will need it for any `trial resume`.

---

## 3. G0 In-Process Walkthrough

G0 is **the only gate that prompts in-process** (no exit/resume cycle). Source: `app/marcus/cli/trial.py:104-115`. You will see:

```
G0 — Directive Composition
Composed directive written to: <path>
Review the directive (printed above). Choose:
  [c] confirm and proceed
  [e] edit in $EDITOR, then reload and re-prompt
  [s] save and show path; exit without running the trial
  [x] cancel trial (no specialist dispatch)
At-gate context: docs/conversational-gates/g0-directive-composition.md
Choice [c/e/s/x]:
```

**Verb meanings:**

| Verb | Action | Use when |
|---|---|---|
| `c` | Confirm + proceed to §01 dispatch | **Attempt-3 default.** Directive looks broadly right. |
| `e` | Open `$EDITOR` on the YAML; reload; re-prompt | Directive has a genuine error (wrong corpus, missing role, etc.) |
| `s` | Save directive, exit cleanly, no dispatch | You want to inspect the directive externally and re-launch later |
| `x` | Cancel trial entirely; no specialist dispatch | Substrate corruption smell at G0 itself |

**✅ Attempt-3 recommendation:** Press `c`. This is a weed-clearing run; harvest quality nits to a postmortem, not at the gate.

**⚠️ MANDATORY G0 check before pressing `c` (pre-trial scrub finding 2026-06-10):** scan the printed directive's `role:` lines and confirm **at least one source has `role: primary`** (or `visual-primary`). Composition is LLM-driven and non-deterministic; a scrub dry-run against this exact corpus produced an all-`supporting` directive, which the Texas wrangler **rejects fail-loud** (`run_wrangler.py` primary-presence check) — the trial would halt right after G0 confirm. If no primary is present: press `e` and change the most central content source(s) (the slide files for this corpus) to `role: primary`, then confirm. `role` is on the G0 editable-fields whitelist.

**⚠️ Ctrl+C wrinkle at G0.** G0 is the one fragile spot. If you Ctrl+C during the in-process prompt, the directive file persists but **no checkpoint exists yet**. Recovery: re-run `trial start` with the **same `--trial-id`** (pass it explicitly). The directive is deterministic for the same corpus + run_id, so this is cheap restart, not lost work.

---

## 4. Per-Gate Operator Action Table

After G0, every subsequent gate **pauses-and-exits the process**. The runner writes `run.json` (`status=paused-at-gate`, `paused_gate=<id>`), `checkpoint.json`, and `decision-card-<gate_id>.json`, then returns from the Python function. There is no daemon. You resume via `trial resume --verdict-file verdict.json` (see §5).

**Source for verb sets:** `docs/operator/hil-verb-legend.md:29-57`, cross-checked against `poll_surface` in runtime code.

| Gate | Section | Verb Set | Attempt-3 Default | What `edit` does | Min verdict shape |
|---|---|---|---|---|---|
| G0 | §02A | `c` / `e` / `s` / `x` | **`c`** | `$EDITOR` on YAML directly (only gate that does this) | n/a — in-process |
| G1 | §04 | `approve` / `edit` / `reject` | **`approve`** | Structured JSON; whitelisted fields per plan-unit | `{"verdict":"approve"}` |
| G1A | §04a | `approve` / `edit` / `reject` per plan-unit row | **`approve`** all rows | Per-row JSON list | `{"rows":[{"id":"...","verdict":"approve"}, ...]}` |
| G1.5 | §04.5 | `acknowledged` / `edit` / `reject` | **`acknowledged`** | Structured JSON | `{"verdict":"acknowledged"}` |
| G1.5-lock | §04.55 | `lock` / `edit` | **`lock`** ⚠️ irreversible (sha256-pin) | Structured JSON | `{"verdict":"lock"}` |
| G2B | §05.5 | `approve` / `edit` / `reject` | **`approve`** | Structured JSON | `{"verdict":"approve"}` |
| G2-submit | §06b | `submit` / `edit` / `discard` | **`submit`** | Structured JSON | `{"verdict":"submit"}` |
| G2M | §07b | `select` / `edit` / `reject` | **`select`** (accept top) | Structured JSON | `{"verdict":"select","selection":"..."}` |
| G2.5-submit | §07c | `submit` / `edit` / `discard` | **`submit`** | Structured JSON | `{"verdict":"submit"}` |
| G2.5 | §07d | `approve` / `edit` / `reject` | **`approve`** | Structured JSON | `{"verdict":"approve"}` |
| (§07f) | §07f | body-validated; **not runner-paused** | n/a | n/a | n/a |
| G3B | §08b | `approve` / `edit` / `reject` | **`approve`** | Structured JSON | `{"verdict":"approve"}` |
| G4A | §11 | `select` / `edit` / `reject` | **`select`** | Structured JSON | `{"verdict":"select","selection":"..."}` |
| G4B | §11b | `approve` / `edit` / `reject` | **`approve`** | Structured JSON | `{"verdict":"approve"}` |
| G5 | §15 | `complete` / `edit` / `reject` | **`complete`** | Structured JSON | `{"verdict":"complete"}` |

**Editable-fields whitelist (example, §02A G0):** `description`, `excluded_reason`, `expected_min_words`, `locator`, `provider`, `role`. Other gates have analogous whitelists in their conversational-gate doc.

**Validation:** Pydantic on the verdict JSON; `decision_card_digest` is tamper-checked. If the digest doesn't match, the runtime refuses the verdict — re-read the decision card and rebuild the verdict file against the current digest.

---

## 5. Resume Command + Verdict File Recipe

After every post-G0 pause, the flow is:

1. Read `state/config/runs/<uuid>/decision-card-<gate_id>.json`. This contains the digest you must echo back, the editable-field whitelist, and the verb set.
2. Compose `verdict.json` (next to the decision card, or anywhere — you pass the path).
3. Invoke:

```powershell
.\.venv\Scripts\python.exe -m app.marcus.cli trial resume --trial-id <uuid> --verdict-file .\verdict.json
```

**Minimal verdict template — §02A G0 (illustrative; for `edit` flow):**

```json
{
  "trial_id": "<uuid-from-run.json>",
  "gate_id": "G0",
  "decision_card_digest": "<sha256-copied-verbatim-from-decision-card>",
  "verdict": "edit",
  "edits": {
    "description": "<updated text>",
    "expected_min_words": 600
  }
}
```

For a pure `approve` / `acknowledged` / `submit` / `lock` / `select` / `complete` flow, the `edits` block is omitted and the file is just:

```json
{
  "trial_id": "<uuid>",
  "gate_id": "G1",
  "decision_card_digest": "<sha256>",
  "verdict": "approve"
}
```

Other gates have analogous structures — always copy the digest verbatim from the decision-card file the runner just wrote.

---

## 6. Reference Files — Keep Open During Trial

| File | Why open |
|---|---|
| `docs/operator/hil-verb-legend.md:29-57` | Canonical verb table per gate |
| `docs/conversational-gates/g0-directive-composition.md` | At-gate context for G0 |
| `docs/conversational-gates/<section>.md` | At-gate context for the gate you're currently paused at |
| `app/marcus/cli/trial.py:104-115` | Source of the G0 in-process prompt text |
| `state/config/runs/<uuid>/run.json` | Trial state, `paused_gate`, `status` |
| `state/config/runs/<uuid>/decision-card-<gate_id>.json` | The decision card you're acting on |
| `_bmad-output/implementation-artifacts/trial-3-readiness-checklist.md` | Pre-flight reference |
| This guide | Verb defaults + escalation path |

---

## 7. Escalation — Something Looks Wrong at a Gate

**Do not try to chat with the runtime. It cannot reason.** Follow this chain:

1. **Triage the smell.** Is the DecisionCard obviously corrupted (missing fields, nonsensical digest, wrong gate id)? → `x` (cancel) the trial; this is substrate corruption, file a postmortem. Or is the content merely surprising but the runtime is healthy? → continue to step 2.
2. **Exit to checkpoint.** Post-G0 gates already exit-on-pause automatically — you don't need to do anything; the process has returned. At G0 (in-process), press `s` (save and exit cleanly) — do **not** Ctrl+C unless you have no other option.
3. **Open a SEPARATE Claude or Codex session.** A new chat window. Do not interrupt the paused trial process state.
4. **Activate Marcus-agent.** Read `skills/bmad-agent-marcus/SKILL.md` in the new session and follow its activation sequence (config load → sanctum batch under `_bmad/memory/bmad-agent-marcus/`). Wait for Marcus-agent to be embodied before pasting the DecisionCard.
5. **Show Marcus-agent the evidence.** Paste: the trial-id, the gate id, the full decision-card JSON, and a 1-2 sentence note on what looked wrong. He will route to specialists (Texas, Quinn-R, Vera, Irene, Tracy, Gary, Kira, Wanda, Enrique, Dan, Compositor) as appropriate.
6. **Compose a verdict.** Decide path forward with Marcus-agent's guidance. Compose `verdict.json` per §5.
7. **Resume the original trial.** `trial resume --trial-id <uuid> --verdict-file verdict.json`. The runtime picks up from the checkpoint.

**Out-of-band thinking is fine. In-band chat is impossible.** Winston: "The thinking happens out-of-band; the runtime sees only the verb selection."

---

## 8. Evidence Capture

**Auto-written by the runtime** (no operator action needed):

- `state/config/runs/<uuid>/run.json` — status, paused_gate, trial_id, timestamps
- `state/config/runs/<uuid>/checkpoint.json` — resume state
- `state/config/runs/<uuid>/decision-card-<gate_id>.json` — one per gate paused at
- `state/config/runs/<uuid>/Trial3Transcript.json` — full operator+runtime transcript (on completion)
- `state/config/runs/<uuid>/<various>` — specialist outputs, segment manifests, etc.

**Operator manual preservation if FAIL:**

- Copy the entire `state/config/runs/<uuid>/` directory to a safe location before any retry/cleanup.
- Screenshot or copy any anomalous stdout that didn't end up in `Trial3Transcript.json`.
- Note the timestamp + Marcus-agent session transcript if you escalated mid-trial.
- File a postmortem entry per `docs/trials/methodology.md §7` four-question routing.

---

## 9. Closeout

**On PASS** (G5 completes successfully):

- `Trial3Transcript.json` lands. Confirm presence + non-zero size.
- Run any closeout checks specified in `_bmad-output/implementation-artifacts/trial-3-readiness-checklist.md §7`.
- File the trial result in `docs/trials/cross-trial-learnings.md`.
- Strikethrough any reactivation-trigger firings in `_bmad-output/planning-artifacts/deferred-inventory.md` and cite the trial id.

**On FAIL** (any gate `x`-cancelled, runtime crash, or substrate corruption):

- Preserve the run-dir per §8.
- Open a postmortem session with Marcus-agent (separate chat).
- Route findings per `docs/trials/methodology.md §7` four-question discipline.
- Update `cross-trial-learnings.md` with the failure mode.
- Do **not** retry the same trial-id; allocate a fresh one for attempt-4 (if any).

---

## 10. Prompts to Copy/Paste

**For the weed-clearing trial itself: NONE are needed.** Marcus's posture is explicit: default-accept at every gate, recommend `c` / `approve` / `select` / `acknowledged` / `lock` / `submit` / `complete` per the table in §4. Harvest quality nits to a postmortem — not at the gate.

**ONE template — for escalation only.** If you need to consult Marcus-agent mid-pause, paste this into a fresh Claude or Codex session **after** activating Marcus-agent per `skills/bmad-agent-marcus/SKILL.md`:

```
Marcus, I'm mid-trial and paused at a gate. Need your read.

Trial id: <uuid>
Gate id: <e.g., G2B / §05.5>
Status: paused-at-gate
Decision-card path: state/config/runs/<uuid>/decision-card-<gate_id>.json

Decision card contents (verbatim):
<paste the full JSON>

What looked wrong:
<1-3 sentences — be concrete. "Specialist output empty," "digest field missing,"
"selection set has 0 candidates," etc.>

What I'm considering:
<your draft verb choice + reasoning, OR "no idea, asking you">

Please:
1. Tell me if this is substrate corruption (→ x cancel + postmortem) or
   recoverable (→ edit with specific fixes, or approve-with-caveat).
2. If recoverable, draft the verdict.json edits block.
3. Route to a specialist if you need their read first (Texas / Quinn-R / Vera /
   Irene / Tracy / Gary / Kira / Wanda / Enrique / Dan / Compositor).
```

Fill in the angle-bracket placeholders before sending. Don't pre-author this — only use it when a smell triggers.

---

**End of guide.** Open this side-by-side with the trial terminal. Trust the verb table. Don't chat with the runtime.
