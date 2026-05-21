---
title: HIL Verb Legend — Operator Quick Reference for Trial-3+
authoredAt: 2026-05-07
authority: pre-Trial-3 cleanup S1 P0-10 (Sally + Paige authoring voices)
audience: operator launching a production trial against the post-Slab-7c migrated runtime
purpose: one-page reference mapping each §section HIL surface to its verb-set, the meaning of each verb at that surface, and what `edit` permits. Tape to second monitor before launch.
---

# HIL Verb Legend

When you sit down to launch a trial, you'll get a sequence of decision-card prompts at each gate. Different §sections use different verb-sets — *approve* at one surface and *complete* at another both close the gate, but they signal different things about what the runner does next. **This page is your decoder ring.**

## Master verb glossary (any surface)

| Verb | Meaning | Runner behavior on selection |
|---|---|---|
| **approve** | "I accept this artifact as the gate's authoritative output; record it; resume." | Gate closes; verdict + payload-digest committed to envelope; runner resumes at next manifest node. |
| **edit** | "I want to change something in the artifact before I accept it." | Runner opens edit-payload form; operator-supplied edits merge into artifact; gate re-presents the edited artifact for re-decision. Edit may loop until operator selects a terminating verb (approve / reject / discard / lock / complete). |
| **reject** | "I do NOT accept this artifact; the runner must re-do upstream work or halt." | Gate closes with negative verdict; envelope records rejection-reason; runner halts and surfaces actionable next-steps to operator. NOT the same as `discard` — rejection signals upstream specialist must redo work. |
| **select** | "I am picking one option from a presented list." | Gate closes; selection (e.g., a voice ID, a variant index, a plan-unit row) committed to envelope; runner resumes consuming the selection downstream. |
| **submit** | "I am committing my own input as the artifact." | Gate closes; operator-supplied payload becomes the canonical artifact at this position. Distinct from `approve` (which accepts a runner-produced artifact). |
| **discard** | "I am abandoning this attempt entirely; do NOT record this artifact." | Gate closes; nothing committed to envelope at this position; runner surfaces post-discard options (retry / skip-to-fallback / halt). |
| **complete** | "I declare this stage's outcome final and ready for downstream." | Gate closes; finalization markers + downstream-readiness flag committed. Used at terminal-stage gates (e.g., §15 G5 final operator handoff). |
| **acknowledged** | "I have read this and accept its content as authoritative." | Gate closes; acknowledgement timestamp + operator-id committed. Lighter weight than `approve` — used for advisory artifacts where the operator is not formally accepting an artifact for downstream use, but confirming awareness. |
| **lock** | "I am freezing this artifact; subsequent stages MUST consume this exact version (sha256-pinned)." | Gate closes with lock-flag + payload-digest pinned; downstream consumers fail-closed if the artifact's sha256 changes after lock. Used at four-artifact lock semantics gates (§04.55 G1.5; §09 G3 lock). |

## Per-§section verb-set table

| §section | Gate code | Surface name | Verb-set | What `edit` permits | At-gate context |
|---|---|---|---|---|---|
| §01 | G0 | Activation + Preflight | (no operator decision; runner-internal preflight gate) | n/a | `docs/conversational-gates/g0-operator-reference.md`; preflight runner emits PASS/FAIL deterministically |
| §02 | G0A | Source Authority Map | approve / edit / reject | edit role assignments per source; reject sends Texas back to redo retrieval | `docs/conversational-gates/section-02-operator-reference.md` (S5 stub) |
| §02A | G0 | Operator Directives (LLM-driven directive composer) | approve / edit / reject | edit composed directive text before Texas dispatch | per-§section reference at S5: `section-02a-operator-reference.md`. **Highest-stakes gate of any trial** — wrong directive = wrong corpus shape downstream |
| §03 | G0B | Ingestion + Texas dispatch | approve / edit / reject | edit metadata fields (provenance, role-tags) before Pass-1 | `section-03-operator-reference.md` (S5) |
| §04 | G1 | Ingestion Quality Gate + Irene Pass-1 packet | approve / edit / reject | edit packet content (Pass-1 narration draft); reject sends Irene Pass-1 back | `docs/conversational-gates/g1-operator-reference.md` |
| §04A | G1A | Per-plan-unit ratification | approve / edit / reject (per row) | edit individual plan-unit rows; per-row decision; reject sends specialist back to author | `section-04a-operator-reference.md` (S5) |
| §04.5 | G1.5 | Estimator (per-slide cost preview) | acknowledged / edit / reject | edit cost-line items; acknowledged confirms cost awareness | `section-04.5-operator-reference.md` (S5) |
| §04.55 | G1.5 lock | Run-constants lock | **lock** / edit | edit run-constants (cluster_density, slide-mode-proportions, etc.) before locking; **lock IS irreversible** (sha256-pin downstream) | `section-04.55-operator-reference.md` (S5). **Once locked, downstream consumes via sha256 binding — cannot be unlocked without halting the trial** |
| §05 | G2 (declared; not runner-pause) | Plan ratification | (body-validated; runner does not pause) | n/a — gate is body-validated by specialist | `section-05-operator-reference.md` (S5) |
| §05.5 | G2B | Per-slide presentation mode | approve / edit / reject | edit per-slide presentation mode (visual-led / text-led / motion-led); reject sends Tracy back | `section-05.5-operator-reference.md` (S5) |
| §05B | G1.5 | Storyboard A literal-visual review | (deferred per mapping-checklist; not yet runner-paused) | n/a | `section-05b-operator-reference.md` (S5) |
| §06 | (no gate; pre-dispatch) | Marcus 5-writer pre-dispatch | (no operator decision; Marcus authors envelope contributions) | n/a | W5 partition principle; Slab 7c §06 pre-dispatch |
| §06B | NEW family (no alias) | Literal-visual operator build | submit / edit / discard | edit operator-supplied literal-visual build; discard abandons attempt | `section-06b-operator-reference.md` (S5) |
| §07B | G2M (declared; not runner-pause) | Per-slide A/B variant | select / edit / reject | edit variant text or visual-direction prose; select chooses A or B | `section-07b-operator-reference.md` (S5) |
| §07C | NEW family (no alias) | Storyboard build + HTML reviewer | submit / edit / discard | edit storyboard rows + HTML reviewer config | `section-07c-operator-reference.md` (S5) |
| §07D | G2.5 | Motion-plan polling | approve / edit / reject | edit motion-plan bindings (motion_asset_path per non-static segment) | `section-07d-operator-reference.md` (S5) |
| §07F | G2F (declared; not runner-pause) | Motion gate | (body-validated; not currently runner-paused) | n/a | `section-07f-operator-reference.md` (S5) |
| §08B | G3B | Storyboard B + live-URL | approve / edit / reject | edit Storyboard B rows + live-URL binding | `section-08b-operator-reference.md` (S5) |
| §09 | G3 lock | Four-artifact lock semantics | **lock** / edit | edit any of the four locked artifacts (script, manifest, motion_plan.yaml, authorized-storyboard.json); lock pins all four sha256s | `docs/conversational-gates/g3-operator-reference.md`. **Lock IS irreversible** |
| §10 | (no gate) | Fidelity + Quality Pre-Spend | (advisory; no operator decision) | n/a | `section-10-operator-reference.md` (S5) |
| §11 | G4A | ElevenLabs Voice Selection | select / edit / reject | edit voice metadata or voice-pairing rules; select picks a voice ID per narration profile | `section-11-operator-reference.md` (S5) |
| §11B | G4B | Input Package preview | approve / edit / reject | edit input package fields (chapter markers, voice bindings) before §12 audio generation | `section-11b-operator-reference.md` (S5) |
| §12 | (no gate; specialist) | Audio Generation | (no operator decision; Enrique generates) | n/a | downstream of §11B approval |
| §13 | G5 (declared; not runner-pause) | Quinn-R Pre-Composition QA | (body-validated; not currently runner-paused) | n/a | `section-13-operator-reference.md` (S5) |
| §14 | (no gate; specialist) | Compositor Assembly Bundle | (no operator decision; Compositor assembles) | n/a | deterministic pipeline output |
| §14.5 | (no gate) | Desmond Run-Scoped Operator Brief | (advisory; no operator decision) | n/a | `section-14.5-operator-reference.md` (S5) |
| §15 | G5 | Final Operator Handoff (Descript-ready) | **complete** / edit / reject | edit DESCRIPT-ASSEMBLY-GUIDE.md content; complete = trial ends successfully | `section-15-operator-reference.md` (S5) |

## Critical-path verb decisions in a typical trial

These are the verbs you'll hit in order during a complete production run. Each one closes a gate and moves the runner forward.

1. **§02A G0:** `approve` (the directive is right) → Texas dispatches with that directive
2. **§04 G1:** `approve` (Pass-1 packet is acceptable) → Irene Pass-2 begins
3. **§04A G1A:** `approve` (per-plan-unit; one decision per plan-unit row) → ratification recorded
4. **§04.55 G1.5 lock:** **`lock`** (run-constants frozen; sha256-pinned) → downstream can consume; **IRREVERSIBLE without halt**
5. **§07B G2M:** `select A` or `select B` per slide variant
6. **§07D G2.5:** `approve` (motion-plan bindings acceptable)
7. **§08B G3B:** `approve` (Storyboard B + live URLs OK)
8. **§09 G3 lock:** **`lock`** (four-artifact lock; all sha256-pinned) → §10 can begin
9. **§11 G4A:** `select` (voice ID per narration profile)
10. **§11B G4B:** `approve` (input package OK) → §12 audio generation
11. **§15 G5:** **`complete`** (DESCRIPT-ASSEMBLY-GUIDE acceptable; trial closes successfully)

## What `edit` actually does (mechanics)

When you select `edit` at any surface:

1. The runner pauses without committing the gate verdict.
2. A second prompt appears asking what to change (text input OR a structured form depending on §section).
3. Your edits merge into the artifact (deterministic merge per §section's edit-payload schema).
4. The runner re-presents the edited artifact for re-decision.
5. You can re-edit or pick a terminating verb (approve / reject / discard / lock / complete).

**`edit` does NOT commit to the envelope.** Only terminating verbs commit. You can edit indefinitely until satisfied — but each edit cycle costs operator attention, so prefer to make all needed changes in one edit pass.

## What `reject` does (mechanics)

`reject` is heavier than `discard`:
- **`reject`** = "the upstream specialist's work is wrong; halt the trial; surface actionable next-steps; the operator may re-dispatch the upstream specialist with corrections."
- **`discard`** = "I am abandoning my own input attempt; do not commit anything at this position; offer me retry / skip / halt."

`reject` is rare but powerful. Use when an artifact is so wrong that editing won't fix it (e.g., Texas retrieved the wrong corpus; Irene Pass-1 narrated against the wrong audience profile).

## When in doubt

- **Don't pick `lock` unless you're sure** — it's irreversible without halting the trial. If unsure, pick `edit` to inspect the artifact further; pick `approve` if the gate has a non-lock approve verb.
- **Don't pick `reject` unless the upstream artifact is fundamentally broken** — if it's just rough, pick `edit` instead.
- **At §15 G5, `complete` ends the trial.** The runner emits Trial3Transcript + DESCRIPT-ASSEMBLY-GUIDE.md; you have the production-ready bundle.

## Related references

- `docs/operator/corpus-preparation-guide.md` — what to prepare BEFORE you launch
- `docs/conversational-gates/g0-operator-reference.md` + `g1-operator-reference.md` + `g2c-operator-reference.md` + `g3-operator-reference.md` + `g4-operator-reference.md` — per-gate context (additional §section stubs land at S5)
- `_bmad-output/implementation-artifacts/trial-3-readiness-checklist.md` — the launch playbook
- `docs/trials/methodology.md` (S3 deliverable) — what success / partial-pass / fail looks like for a trial run
