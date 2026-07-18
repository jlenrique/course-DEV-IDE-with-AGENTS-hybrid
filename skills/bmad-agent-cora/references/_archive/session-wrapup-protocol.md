> ⚠️ **ARCHIVED / DISSOLVED — do not follow.** The BMAD persona **Cora** was dissolved as a runtime
> specialist (`_bmad-output/planning-artifacts/decision-records/DR-SLAB-1-CLOSE-2026-04-24.md` DR-2,
> party-ratified 5/5, binding). Her session-coherence role was redistributed to the LangGraph CI stack
> and the canonical session protocols. This file is retained for historical lineage only; parts of it
> (e.g. hand-drafting `next-session-start-here.md`) now CONTRADICT the status-surface generated-view
> regime. **Authoritative session procedure: [`bmad-session-protocol-session-START.md`](../../../../bmad-session-protocol-session-START.md)
> + [`bmad-session-protocol-session-WRAPUP.md`](../../../../bmad-session-protocol-session-WRAPUP.md)** (the coherence gate lives at their Step 1a / Step 0).

---

# Session-WRAPUP Protocol (SW)

Cora's closing move on every dev session. This protocol is invoked by the canonical BMAD Wrapup (`bmad-session-protocol-session-WRAPUP.md`) as **Step 0c** — the draft phase of the hot-start pair. Steps 7 and 8 of the canonical Wrapup finalize those drafts after Steps 1–6 have run. Goal: a clean hot-start pair for the next session, plus a memory-sidecar update.

## Relationship to the Canonical Wrapup

The canonical Wrapup protocol calls this skill three times in Step 0 (pre-wrapup coherence and closure):
- **Step 0a** — `/harmonize` (see `harmonization-protocol.md`)
- **Step 0b** — `/preclosure {story_id}` per story flipping to `done` (see `preclosure-protocol.md`)
- **Step 0c** — this SW protocol, which drafts `SESSION-HANDOFF.md` and `next-session-start-here.md`

Because Steps 0a and 0b precede this step, Cora already has Audra's finding-set in hand when drafting the outstanding-items section. The drafts this protocol produces are **drafts**, not final — Steps 7 and 8 of the canonical Wrapup reconcile them against anything added in Steps 1–6 before the operator approves a final write.

## Inputs Read

1. `git log --oneline <session-start-anchor>..HEAD` — what landed this session. Anchor is resolved via `git log -1 --format=%H -- SESSION-HANDOFF.md`.
2. `sprint-status.yaml` current state vs. session-start state
3. The Step 0a `harmonization-summary.md` and Audra trace reports under `reports/dev-coherence/YYYY-MM-DD-HHMM/` (if 0a ran)
4. The Step 0b closure-artifact evidence files under `{report_home}/evidence/ca-*.md` (if any stories flipped to `done`)
5. Any operator remediation decisions made during Steps 0a/0b ("remediate now," "queue for next session," "defer with note," "flip anyway")
6. The operator's stated intent for next session (ask if not already stated)

## Reconciliation Steps

1. Draft an updated `SESSION-HANDOFF.md` covering:
   - Session summary (2-3 sentences)
   - Stories touched
   - Commits landed (`git log --oneline <session-start-anchor>..HEAD`)
   - Outstanding items — explicit enumeration of every Audra finding from Step 0a that was deferred or queued, and every pre-closure gap from Step 0b where the operator proceeded with the flip
   - Decisions taken
   - Link to the Step 0a report home for audit trail

2. Draft an updated `next-session-start-here.md` covering:
   - Intended next anchor task
   - Outstanding findings from Steps 0a/0b that the next session must surface at its own Start Step 1a (outstanding-findings gate)
   - Hot-start-summary seed for next session's opener
   - Branch metadata and startup commands (baseline branch, next working branch, checkout commands)
   - Any operator-declared preferences for the next session

3. Show both drafts to the operator. Ask explicitly: "Happy with these as drafted? I'll patch them after Steps 1-6 run if anything material changes."

4. On operator approval, write both files as drafts. Do not commit them — the operator owns git hygiene, and Steps 7/8 of the canonical Wrapup may patch them further.

5. Update Cora's `index.md` and append to `chronology.md`:
   `YYYY-MM-DD HH:MM — Session WRAPUP (Step 0c draft). Commits landed: <N>. Next-up: <anchor>. Outstanding findings: <count>.`

6. If a cross-session pattern crystallized this session (3+ confirming observations), append to `patterns.md`.

## Forcing Functions

- The operator can always skip WRAPUP (Cora does not block on it). If skipped, Cora logs to `chronology.md`: `YYYY-MM-DD HH:MM — Session WRAPUP skipped: <reason>. Hot-start pair may be stale next session.` The next session's Start Step 1a will surface the missing-audit-trail condition.
- If the operator explicitly asks for a lighter WRAPUP ("just save the handoff, skip the rest"), Cora writes a minimal `SESSION-HANDOFF.md` and marks `next-session-start-here.md` as "operator-deferred." Outstanding findings from Steps 0a/0b must still be included in whatever minimal form is chosen — they are not optional content.
- If Step 0a was skipped (soft-conditional skip because the change window was empty), Cora still runs Step 0c but notes in the `SESSION-HANDOFF.md` validation summary: "Step 0a skipped; next session's tripwire will auto-promote /harmonize to full-repo scope."
