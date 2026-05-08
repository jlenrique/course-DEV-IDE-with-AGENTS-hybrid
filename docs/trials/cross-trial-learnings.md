---
title: Cross-Trial Learnings Register
authoredAt: 2026-05-07
authority: pre-Trial-3 cleanup S3 (party-mode-ratified at post-S3 review)
purpose: Patterns + run-shape learnings that emerge across trials. NOT a per-trial postmortem index — a synthesis register.
governance: per `docs/trials/methodology.md §7` four-question filing-disposition; entries land here only when no other register applies, OR as cross-trial pattern synthesis.
---

# Cross-Trial Learnings

## How to use this document

**Pre-Trial-N read (5 min, mandatory before opening `launch.md`):** scan the §"By gate / surface" sections for any prior learnings touching the surfaces you'll exercise this trial. Bold **Symptom:** lines are Ctrl-F-friendly; the question to ask is *"has this happened before?"*

**Mid-trial grep (30 sec, ad-hoc):** Ctrl-F a symptom keyword from what you're seeing. If a prior trial saw it, you'll find the learning + recommended next-step inline.

**Post-Trial-N append (10 min, mandatory at postmortem close):** copy your Shape-A Q5 entry from `postmortem.md` into the appropriate `## By gate` section using the entry template at the bottom of this file.

---

## Filing-disposition rules (binding; from methodology.md §7)

When a Trial-N postmortem surfaces a finding, route via four sequential questions (first YES wins):

1. **Anti-pattern reproducible outside trial context?** → `docs/dev-guide/specialist-anti-patterns.md` or `dev-agent-anti-patterns.md`
2. **Backlog work / deferred follow-on?** → `_bmad-output/planning-artifacts/deferred-inventory.md`
3. **Architectural decision shift?** → architecture doc §10 Decision Log
4. **Cross-trial pattern OR per-trial run-shape learning (methodology / cadence / evidence-collection)?** → THIS DOCUMENT

Pattern synthesis runs every 3 trials OR at Epic-close. Trigger firings are bidirectionally cited (inventory ↔ cross-trial).

---

## §A — By gate / surface

### G0 (§02A operator directives composer)

**Symptom: directive composer promotes `.gitkeep` to primary source role; demotes the actual primary `.docx` to supporting.**
- Context: Trial-2 attempts 1, 5, 6, 7, 8 (run-id `db276994-edf4-47a2-83bc-771cc214c3c1`); 5 successive runs producing byte-identical broken corpus-scan directive output.
- Diagnosis: pre-Slab-7c §02A composer was a fallback enumeration of corpus-dir files, NOT LLM-driven semantic role assignment.
- Filed at: deferred-inventory `trial-2-finding-2-directive-composer-corpus-scan-fallback`. CLOSED-BY Story 7c.3a 2026-05-05 (LLM-driven composer body landed at `app/marcus/composers/section_02a/composer.py`).
- Cross-trial implication: if this re-surfaces at Trial-3, the regression is in 7c.3a's contract. Inspect §02A composer's LLM-prompt + corpus-shape interpretation logic.

**Symptom: G0 print crashes Windows console cp1252 stdout on `U+202F` NARROW NO-BREAK SPACE in macOS-screenshot filenames.**
- Context: Trial-2 attempt 1 (run-id `d44128e9-...`).
- Diagnosis: A11 Windows-portability anti-pattern (`PYTHONIOENCODING=utf-8` workaround validated).
- Filed at: deferred-inventory `trial-2-finding-1-g0-print-cp1252-crash`. CLOSED-BY Story 7c.2 (UTF-8 byte writer at `_confirm_or_edit_directive`).
- Cross-trial implication: Trial-3+ should see structural fix; if regression, inspect 7c.2's UTF-8 writer.

### G1 (§04 ingestion quality + Irene Pass-1)

_(empty until Trial-3 fires this gate)_

### G2C (§07C storyboard build + HTML reviewer)

_(empty)_

### G3 (§09 four-artifact lock semantics)

_(empty)_

### G4 (§11 voice selection / §11B input package)

_(empty)_

### G5 (§15 final operator handoff / DESCRIPT bundle)

_(empty)_

---

## §B — By methodology / cadence learning

_(empty until Trial-3 surfaces methodology-shape learnings)_

The kind of entries that land here:
- "I needed an Nth section in launch.md that doesn't exist"
- "log.md voice was too dense to write under attention pressure; trim X"
- "postmortem Shape-A Q5 was hard to fill because Q1-Q4 felt redundant; reshape"

These ARE valid cross-trial learnings; they refine the methodology over time.

---

## §C — Reactivation triggers fired

When a tracked trial fires a deferred-inventory reactivation trigger, record it here AND strikethrough the inventory entry with citation back here.

_(Empty until first tracked trial — Trial-3 — fires triggers. Expected first firings include `Epic 15 reactivation` chain unlocked by `at least one tracked trial run completed` trigger.)_

---

## §D — Cross-trial pattern synthesis

Synthesis section. Populated every 3 trials OR at Epic-close. Each entry names a pattern observed across N trials with N ≥ 3 occurrences (analogous to Mary's DISMISS-thread P2 ratchet at N ≥ 3-5).

_(Empty until 3+ tracked trials complete.)_

---

## §E — Retroactive seed entries (pre-S3)

These entries seed the register from pre-S3 trial history. They are **historical record only** — not subject to the post-S3 filing-disposition rules but useful as the cross-trial baseline future trials grep against.

### Trial-475 (2026-04-28, paused-at-G1)
- **Symptom:** Texas dispatch returned deterministic fixture-stub instead of real retrieval evidence.
- Diagnosis: directive-composition gap; `--input` corpus-path accepted but no upstream code converted to `directive.yaml` for Texas's `dispatch_retrieval`.
- Closed-by: Slab 7b 7b.1 Texas hardening (FR89; fail-loud guardrail) + Slab 7c 7c.3a §02A LLM composer.
- Cross-trial implication: any future trial that lacks a directive YAML at G0 should fail-loud-refuse via Texas guardrail (do NOT silently fall back).

### Trial-2 (2026-05-04, structured-stop)
- **Symptom:** §02A composer corpus-scan fallback OR cp1252 print crash; trial halted at G0 due to broken directive.
- Findings filed: `trial-2-finding-1` (cp1252) + `trial-2-finding-2` (composer fallback) + `trial-2-finding-3` (8-attempt linearization observation; methodology learning).
- Postmortem: `_bmad-output/implementation-artifacts/trial-2-postmortem-2026-05-04.md`.
- Cross-trial implication: STRUCTURED-STOP verdict is a healthy outcome when substrate honors fail-loud contracts. Substrate did its job; trial did not produce trial evidence but DID produce diagnostic evidence (3 findings → 2 closed substrate work).

---

## Entry template (post-Trial-N append)

When operator adds a new entry at trial close, use this shape:

```markdown
**Symptom: <one-sentence symptom; bold for Ctrl-F discoverability>**
- Context: Trial-N attempt M (run-id `<id>`); brief setting
- Diagnosis: <2-3 sentence root cause>
- Filed at: <where the finding lives — anti-pattern / deferred-inventory / architecture / cross-trial-only>
- Cross-trial implication: <what future trial author should know>
```

Hard cap ~150 words per entry. Group within the appropriate §A / §B / §C / §D section.

---

## Lifecycle

This file is updated:
- Per-trial: append entries at postmortem close (operator + Mary harvest-gate)
- Per-3-trials: pattern synthesis pass (operator + Mary)
- Per-Epic-close: roll-up review consumed by `bmad-retrospective`

When an entry's pattern matures into a reproducible-outside-trial-context anti-pattern, it migrates to the anti-pattern catalog (Mary harvest-gate ratification). The cross-trial entry then becomes a one-line stub citing the catalog entry; this preserves cross-trial discoverability without duplicating the prescriptive remediation.
