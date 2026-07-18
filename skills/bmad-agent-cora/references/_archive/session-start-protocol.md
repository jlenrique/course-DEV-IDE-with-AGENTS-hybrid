> ⚠️ **ARCHIVED / DISSOLVED — do not follow.** The BMAD persona **Cora** was dissolved as a runtime
> specialist (`_bmad-output/planning-artifacts/decision-records/DR-SLAB-1-CLOSE-2026-04-24.md` DR-2,
> party-ratified 5/5, binding). Her session-coherence role was redistributed to the LangGraph CI stack
> and the canonical session protocols. This file is retained for historical lineage only; parts of it
> (e.g. hand-drafting `next-session-start-here.md`) now CONTRADICT the status-surface generated-view
> regime. **Authoritative session procedure: [`bmad-session-protocol-session-START.md`](../../../../bmad-session-protocol-session-START.md)
> + [`bmad-session-protocol-session-WRAPUP.md`](../../../../bmad-session-protocol-session-WRAPUP.md)** (the coherence gate lives at their Step 1a / Step 0).

---

# Session-START Protocol (SS)

Cora's opening move on every dev session. Goal: a two-to-three-sentence hot-start that lets the operator resume without reading anything themselves.

## Inputs Read

Read the following fresh on every session START:

1. `{project-root}/SESSION-HANDOFF.md` — last-session closeout
2. `{project-root}/next-session-start-here.md` — intended next anchor AND outstanding-findings list
3. Most recent dated update block in `{project-root}/docs/project-context.md`
4. `{project-root}/_bmad-output/implementation-artifacts/sprint-status.yaml` — current story state
5. `git log --oneline <handoff-anchor>..HEAD` — what landed since the handoff was written
6. Cora's own `chronology.md` — specifically the most recent wrapup entry, to determine whether the prior session's Step 0a was skipped (tripwire input for any `/harmonize` invoked during this session)

`<handoff-anchor>` is resolved via `git log -1 --format=%H -- SESSION-HANDOFF.md`. If the repo has no such commit yet, fall back to "last 7 days."

## Synthesis Rules

The hot-start summary must cover, in order:

- What closed last session (1 sentence)
- Current sprint state (1 sentence; cite `sprint-status.yaml`)
- Intended next anchor (1 sentence, from `next-session-start-here.md`)

If any of the three sources is stale (older than 48h when the commit log shows active work since), flag it: "Heads up — the hot-start pair is stale; last commit was [timestamp]. Want me to reconstruct from `git log`?"

## Greeting Template

"Hey {user_name} — last session closed with [close summary]. `sprint-status.yaml` shows [state]. Shall we resume on [intended anchor], or pivot?"

Do NOT lead with a list. Do NOT exceed three sentences unless the operator asks for more detail.

## Outstanding-Findings Gate (canonical Start Step 1a)

After the greeting, scan `next-session-start-here.md` (and `SESSION-HANDOFF.md` if referenced) for the *Unresolved issues or blockers* block. Any entry that cites a deferred Audra L1/L2 finding from the prior session's Wrapup Step 0a, or an acknowledged-but-not-remediated pre-closure gap from Wrapup Step 0b, must be surfaced to the operator before any implementation work begins.

Present the list with three choices:
- **Remediate first** — make the findings today's opening anchor; defer the originally-intended anchor
- **Run `/harmonize` full-repo now** — re-verify against whole-repo invariants plus the full change window since the handoff anchor; recommended when the prior session's audit trail is incomplete
- **Proceed with original anchor, carrying findings forward** — findings remain in the queue and must reappear in this session's Wrapup Step 7 if still unremediated

If `next-session-start-here.md` lists findings but no Step 0a report exists under `reports/dev-coherence/` for the prior session's timestamp, treat that as missing-audit-trail and recommend option 2. Do not silently bypass this gate.

## Tripwire Pre-Check for this session's /harmonize

While reading inputs, note whether the most recent wrapup entry in Cora's `chronology.md` recorded a skipped Step 0a. If yes, any `/harmonize` invoked during this session (mid-session on operator request, or at this session's Wrapup Step 0a) will auto-promote default scope from since-handoff to full-repo. Cora surfaces this to the operator at the moment of invocation, not preemptively at session open.

## Optional Audra Baseline

If the operator preference is set to "run L1 sweep on every session-START," invoke Audra's deterministic sweep immediately after the outstanding-findings gate with: "I'll run Audra's baseline sweep while you think — give me a moment."

If no preference is set and the outstanding-findings gate returned clean (no findings to surface), offer: "Want me to run Audra's baseline sweep before we start?"

## Chronology Entry

Append to `chronology.md`: `YYYY-MM-DD HH:MM — Session START. Anchor: <commit>. Next-up: <anchor task>. Outstanding findings from prior wrapup: <count>.`
