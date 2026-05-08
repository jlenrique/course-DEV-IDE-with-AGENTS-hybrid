# Trial-3 Postmortem

> **This is the trial-3 skeleton; fill in place.** Originally copied from `docs/trials/trial-N-templates/postmortem.md`. **Shape A is mandatory at trial-close (15 min); Shape B is deferred 48h** (structured findings; recovered-operator energy required). Sally pre-S3 review depletion-empathy beat.

---

## Verdict

**Verdict:** `<PASS / PARTIAL-PASS / STRUCTURED-STOP / FAIL>` (per `methodology.md §5`)

**One-line summary:** `<single sentence: what happened>`

---

## SHAPE A — Reflection (mandatory at trial close; ~15 min)

Five questions, prose answers, no fields. Fill at trial close before the trial-induced-fatigue-headwind hits hard.

### Q1: Did we reach §15 G5 complete?

`<yes / no, paused at gate X / partial-pass — reached G3 but not G5 / structured-stop>`

### Q2: What was the single moment where this trial felt different from the last one?

> _Operator fills — first-person prose; the "different" moment is the load-bearing one. Anchors the trial's distinct contribution to cross-trial-learnings._

### Q3: What did the runtime do that I didn't expect — good or bad?

> _Operator fills — surprises in either direction. The "good surprise" is as load-bearing as the bad one (substrate exceeding expectations is evidence too)._

### Q4: If I had to halt, would I have? Where, and why didn't I?

> _Operator fills — the not-halted-but-could-have moment is exactly where partial-PASS vs structured-stop boundary lives. Capture the judgment call._

### Q5: One thing to add to cross-trial-learnings.md.

> _Operator fills — the bold-symptom one-liner that goes into `cross-trial-learnings.md` post-trial-append step._

---

## SHAPE B — Structured findings (deferred 48h; recovered-operator energy required)

Mark this section explicitly **"PENDING — fill within 48h"** at trial close if you can't author now. Trial-2 postmortem at `_bmad-output/implementation-artifacts/trial-2-postmortem-2026-05-04.md` is the template seed.

### Findings

#### Finding #1: `<short title>`

| Field | Content |
|---|---|
| Surface | `<which §section / gate / specialist surfaced this>` |
| Trigger | `<what condition or input caused this>` |
| Failure mode | `<what observable behavior emerged; expected vs actual>` |
| Anti-pattern mapping | `<A1-A20 or P1-P4 reference if existing; "candidate A21" if new>` |
| Workaround | `<what the operator did to proceed if anything; "halted" if structured-stop>` |
| Permanent-fix shape | `<what would close this for good — story shape, contract change, prompt rewrite, etc.>` |
| Filing target (per §7 routing) | `<anti-pattern catalog / deferred-inventory / architecture D-log / cross-trial-learnings.md>` |

#### Finding #2..#N

(Repeat per orthogonal finding.)

---

## Implications

### What was PROVED by this trial

- `<List substrate / contract / methodology claims that this trial validates>`

### What was SURFACED by this trial

- `<List substrate / contract / methodology gaps or unknowns that this trial revealed>`

### Decisions ratified

- `<deferred-inventory mutations: X closed; Y filed>`
- `<follow-on filings: new entries added>`
- `<scope pivots: any party-mode-ratified scope shifts>`

---

## Cycle metrics

| Metric | Value |
|---|---|
| Wall-clock (launch → close) | `<HH:MM>` |
| Number of attempts | `<N>` |
| Total cost (LLM + APIs) | `$<X>` |
| Tripwire firings | `<count + which>` |
| Broad-regression delta | `<+/- N tests vs pre-trial baseline>` |
| Operator attention-quality (subjective 1-5) | `<N>` |

---

## Harvest discipline (REQUIRED SECTION; one entry per finding minimum)

Per `methodology.md §7` four-question filing-disposition. **First YES wins; do not file in two places.**

### Anti-patterns surfaced (filing target: `specialist-anti-patterns.md` or `dev-agent-anti-patterns.md`)
- `<list with proposed entry name + burn evidence>`

### Deferred-inventory triggers fired (filing target: `deferred-inventory.md` strikethrough closure)
- `<list with entry name + evidence + closure disposition>`

### Architecture decisions shifted (filing target: architecture doc §10 Decision Log)
- `<list with proposed D-entry or modified D-entry>`

### Cross-trial patterns emerging (filing target: `cross-trial-learnings.md`)
- `<list with pattern name + N-th occurrence count + synthesis if N≥3>`

### Routing summary (hygiene check)

| Findings filed → | A: anti-patterns | B: inventory | C: architecture | D: cross-trial |
|---|---|---|---|---|
| Count | `<N>` | `<N>` | `<N>` | `<N>` |

**Confirmation:** `<each finding has exactly ONE filing destination; zero double-filings; zero unfiled findings>`

---

## Forensic evidence pointers (do-not-delete paths)

Future-self investigating this trial needs these paths to remain on disk. Mark as "preserve" in any cleanup pass.

- `state/config/runs/<run-id>/` — runtime artifacts directory
- `<bundle>/` — trial bundle (from launch.md §3 corpus_path)
- `_artifacts/current-trial/<this-trial-id>/` — calibration + engagement decay reports
- `_codex-handoff/<verdict-files>` — per-gate review records (if any)
- `<run-dir>/run/trial-transcript.json` — final transcript

---

## References

- `docs/trials/methodology.md` — methodology this trial follows
- `docs/trials/trial-N/launch.md` — pre-flight intentions and corpus declaration
- `docs/trials/trial-N/log.md` — chronological event stream
- `docs/trials/cross-trial-learnings.md` — register where Q5 entry lands
- `_bmad-output/planning-artifacts/deferred-inventory.md` — register where deferred follow-ons land
- `docs/dev-guide/specialist-anti-patterns.md` + `dev-agent-anti-patterns.md` — registers where anti-patterns land
- `_bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md` — register where D-entries shift
