# BMB Sanctum Alignment Checklist

**Audience:** dev agents at story-T1 (authoring per-specialist parity contract); reviewers at story-close (verifying SG-4 compliance); cold-pickup operators (orientation to the alignment landscape).

**Status:** Slab 7b foundational artifact (FR108). Authored 2026-04-29. Replaces precedent-by-example references to "Marcus/Irene/Dan/Texas pattern" with a structured rubric.

**Authority:** This document is the canonical reference for SG-4 sanctum alignment per Slab 7b PRD. The structural parity-test (`tests/parity/test_skill_md_sanctum_alignment.py`, FR101) and the human reviewer both consume this document. If the test contract and this document drift, this document is authoritative — amend the test to match.

---

## §1 Purpose & audience

The Standing Guardrail SG-4 (introduced by Slab 7b PRD) requires every body-activation story to either (a) align its specialist with the standard BMB sanctum pattern, OR (b) document an explicit, party-mode-ratified exception. This checklist defines what "aligned" means in concrete, auto-checkable terms — and what an acceptable exception looks like.

The mental-model risk SG-4 prevents: shipping Slab 7b with two activation patterns ("BMB-aligned specialists" + "legacy not-yet-migrated specialists") that compound attention-tax across every future operator session and every sprint. The operator's framing: **"you don't get two mental models forever."**

**Three audiences read this document:**
- **Dev agent at T1 readiness** — produces a new specialist body activation; needs to know what artifacts must exist post-story.
- **Reviewer at story-close** — verifies the AC; references this document to adjudicate close-or-HALT.
- **Cold-pickup operator** — returns to the project after a gap; needs orientation to which agents are aligned and why some aren't.

→ See §7 for the script that enforces §3.

---

## §2 When to use

| Context | Sub-section to read |
|---|---|
| **T1 readiness** for any Slab 7b body-activation story | §3 + §4 + §6 (worked examples for the specialist's class) |
| **Story-close review** of a body-activation PR | §3 (auto-checkable) + §5 (if option-b invoked) + §7 (script contract) |
| **Cold-pickup operator orientation** | §1 + §4 + §6 |
| **Authoring a NEW option-b documented exception** | §5 + `docs/dev-guide/sanctum-exception-categories.json` (closed allowlist) + party-mode consensus |

---

## §3 Required sanctum artifacts (auto-checkable list)

→ See §7 for the script that enforces this list.

For a specialist `<name>` to be considered **option-a sanctum-aligned**, the following structural artifacts MUST exist:

### §3.1 SKILL.md at the legacy skill quarantine path

**Path:** `skills/bmad-agent-<name>/SKILL.md` (per CLAUDE.md §"Custom agents vs registered BMAD personas" — the legacy skill quarantine is the operator-facing entry point; this is intentional and not a defect)

**Required frontmatter keys** (minimal; the SKILL.md is the entry point, not the source of truth):
- `name` (string; matches `bmad-agent-<name>`)
- `description` (string; one-line role summary + activation trigger)

The SKILL.md "On Activation" section MUST reference the sanctum directory path (per §3.2). The activation prose pattern: "*Read `_bmad/memory/bmad-agent-<name>/INDEX.md` first; then load PERSONA, CREED, BOND, MEMORY, CAPABILITIES per INDEX.*"

### §3.2 Sanctum directory at the canonical location

**Path:** `_bmad/memory/bmad-agent-<name>/` (NOT `<name>-sidecar/` — the `-sidecar/` suffix indicates option-b documented exception per §5)

The sanctum directory MUST contain the 6-file BMB pattern:

| File | Role | Auto-check |
|---|---|---|
| `INDEX.md` | Sanctum directory; lists standard files + session log + capabilities + references | Exists; contains "Standard Files" section |
| `PERSONA.md` | Who I am (name, voice, style, evolution log) | Exists; non-empty |
| `CREED.md` | What I believe (values, principles, boundaries, dominion) | Exists; non-empty |
| `BOND.md` | Who I serve (operator preferences, course organization, quality expectations) | Exists; non-empty |
| `MEMORY.md` | What I know (curated long-term knowledge) | Exists (may be near-empty for new agents) |
| `CAPABILITIES.md` | What I can do (built-in + learned + tools) | Exists; non-empty |

### §3.3 Optional artifacts (recommended; not failed by parity-test)

- `sessions/` subdirectory — raw per-session notes (`YYYY-MM-DD.md`)
- `capabilities/` subdirectory — owner-taught capability prompts
- `references/` subdirectory — copied from skill bundle (per Slab 2a.4 Texas pattern)
- `access-boundaries.md` — read/write/deny zones (some agents include this)

### §3.4 SKILL.md activation-order convention (manual-eyeball; see §4)

The activation prose MUST follow the canonical pattern: read INDEX.md → load standard files per INDEX → fall back to "First Breath" if sanctum is absent (cold-emerge case).

---

## §4 Activation-pattern verification (manual-eyeball)

Auto-checkable artifacts (§3) are necessary but not sufficient. The reviewer additionally verifies:

### §4.1 SKILL.md names sanctum batch correctly

The SKILL.md "On Activation" prose names the sanctum directory by its actual path (`_bmad/memory/bmad-agent-<name>/`). Drift example: SKILL.md cites `_bmad/memory/<name>-sidecar/` but sanctum lives at `_bmad/memory/bmad-agent-<name>/` — that's a copy-paste defect.

### §4.2 INDEX.md sanctum keys resolve to existing files

INDEX.md lists Standard Files; each listed file MUST exist on disk. Drift example: INDEX.md lists `references/storyboard-procedure.md` but file doesn't exist.

### §4.3 PERSONA.md voice matches operator-facing samples (when applicable)

If the agent has prior operator-facing prose (e.g., from a brainstorming session, a chat log, or a prior production run), PERSONA.md voice should be consistent with that prior prose. This is operator-judgment, not rule-based. The reviewer flags inconsistency to the operator; operator adjudicates.

### §4.4 Specialist-registry entry present (if Marcus-routed)

If the specialist is Marcus-orchestration-routed, the entry in `skills/bmad-agent-marcus/references/specialist-registry.yaml` MUST exist with the specialist's class designation per Slab 7b D14 amendment (A/B/C/C+/D1/D2).

---

## §5 Documented-exception pattern (option-b)

Some specialists legitimately don't fit the BMB pattern. Examples:
- **Cora-sidecar** (canonical option-b precedent) — operator-control authority that lives as a hook, not a conversational specialist; sanctum-shaped persona accumulation doesn't apply.
- **Class-D2 pipeline-greenfield specialists** (Compositor, per Slab 7b D20 amendment) — deterministic pipelines without LLM calls; persona-shaped continuity doesn't apply.

### §5.1 When option-b is permitted

Option-b is permitted if and only if the specialist's nature falls into a category enumerated in `docs/dev-guide/sanctum-exception-categories.json` (FR109 closed allowlist). The initial allowlist:
- `sidecar-hook` (Cora precedent — operator-control authority living as runtime hook)
- (Class-D2 pipeline-greenfield is handled via D14/D20 taxonomy as Class-D2 sidecar variant — NOT option-b exception per Slab 7b R5/R6/R8/R9 amendments. See §5.4 below.)

If a specialist's nature does NOT fall into an existing allowlist category, the dev agent MUST open a party-mode round to ratify a new category — silent invocation of option-b without an allowlist entry is a HALT-AND-REMEDIATE governance failure.

### §5.2 Required exception-block content

When option-b is invoked, the specialist's `SKILL.md` MUST contain a stable `## Sanctum exception` H2 anchor section with:

```markdown
## Sanctum exception

<!-- sanctum-exception:<category-id> -->

**Category:** `<category-id>` (from `docs/dev-guide/sanctum-exception-categories.json`)
**Precedent:** [link to canonical precedent specialist]
**Party-mode ratification:** [link to ratification record in story planning artifact]

### Rationale

<at least 80 chars of prose; MUST reference "sanctum activation" or "BMB pattern" by name explaining why this specialist legitimately deviates>
```

The HTML comment `<!-- sanctum-exception:<category-id> -->` is a parity-test grep target; it MUST be present immediately below the H2 heading.

### §5.3 Cora-sidecar precedent (concrete paste-pattern)

See `skills/bmad-agent-cora/SKILL.md` §"Sanctum exception" (FR112 anchor section). Future Slab 7b (and beyond) authors invoking option-b copy that block verbatim and adjust the `<category-id>`, `<rationale>`, and `<precedent>` fields.

### §5.4 Class-D2 pipeline-greenfield is NOT option-b

Per Slab 7b D20 amendment (R9 close): Compositor and other Class-D2 pipeline-greenfield specialists follow the **scaffold-v0.2-D2-pipeline variant** (FR111) which is canonical inside the BMB regime, NOT an exception. Class-D2 specialists are identified by `class: D2` in the per-specialist registry; the parity-test skips sanctum-presence checks for `class: D2` rows. No exception block, no allowlist category, no party-mode ratification required for Class-D2 specialists invoking the variant.

This is the **two-sidecar disambiguation** (per FR108 §8 glossary): "Cora-sidecar" (option-b documented exception) and "Class-D2 sidecar variant" (scaffold pattern) are distinct concepts that share a noun.

---

## §6 Worked examples

### §6.1 Standard activation (option-a) — Marcus precedent

Marcus is the canonical option-a precedent. His SKILL.md and sanctum together exemplify the pattern.

**SKILL.md** at `skills/bmad-agent-marcus/SKILL.md`:

```yaml
---
name: bmad-agent-marcus
description: Creative Production Orchestrator for health-sciences / medical-education course content. Use when the user asks to talk to Marcus or requests the production orchestrator.
---
```

Plus prose body including an "On Activation" section that names `_bmad/memory/bmad-agent-marcus/INDEX.md` as the first read.

**Sanctum** at `_bmad/memory/bmad-agent-marcus/`:
- `INDEX.md` — sanctum directory
- `PERSONA.md` — voice + style + evolution
- `CREED.md` — principles + standing orders + boundaries + dominion
- `BOND.md` — operator + team + domain + preferences
- `MEMORY.md` — operator patterns + run history + routing learnings
- `CAPABILITIES.md` — built-in + learned + tools

Plus optional `sessions/`, `capabilities/`, `references/` subdirectories.

**This is the alignment shape Class-A/B/C/C+/D1 specialists target.** Texas, Irene (`bmad-agent-content-creator`), Dan (`bmad-agent-cd`), Desmond all follow this pattern.

### §6.2 Documented-exception activation (option-b) — Cora precedent

Cora is the canonical option-b precedent. See `skills/bmad-agent-cora/SKILL.md` §"Sanctum exception" for the full paste-pattern target.

Cora's deviation: Cora is a runtime hook (operator-control authority for substrate-coherence checks), not a conversational specialist. Persona-shaped continuity doesn't apply because Cora has no operator dialogue surface; the substrate gates are her only interaction shape. Cora's `_bmad/memory/cora-sidecar/` directory holds her hook configuration (NOT the BMB persona pattern).

The `<!-- sanctum-exception:sidecar-hook -->` marker in Cora's SKILL.md makes the exception parity-test-grepable.

### §6.3 Additional examples (deferred follow-on)

Additional worked examples for **Irene, Dan, Texas** are deferred to a follow-on doc — filed in `_bmad-output/planning-artifacts/deferred-inventory.md` §"Named-But-Not-Filed Follow-Ons" as `bmb-checklist-additional-worked-examples-irene-dan-texas`. They reactivate once the Slab 7b Wave 1 parity stories close and the patterns stabilize.

The two examples in §6.1 + §6.2 are sufficient for the Slab 7b dev cycle: option-a + option-b coverage with stable canonical precedents.

---

## §7 Auto-check script contract

The structural parity-test (`tests/parity/test_skill_md_sanctum_alignment.py`, FR101) implements this contract.

**Inputs:**
- The 11-specialist roster from SG-1 (loaded from `slab-7b-specialist-activation-eleven.md` frontmatter `slab7bSpecialistRoster`)
- For each specialist: class designation (A/B/C/C+/D1/D2)

**Per-specialist checks (`<name>` enumerated):**

| Check | Pass condition | Fail behavior |
|---|---|---|
| C-1 SKILL.md exists | `skills/bmad-agent-<name>/SKILL.md` exists | FAIL (not skip) |
| C-2 SKILL.md frontmatter parseable | YAML frontmatter parses; contains `name` and `description` keys | FAIL with key list |
| C-3 SKILL.md `name` matches | `name == f"bmad-agent-<name>"` | FAIL with mismatch |
| C-4 If `class: D2` (Compositor variant) | Skip C-5/C-6/C-7; assert scaffold-v0.2-D2-pipeline contract instead per FR111 | (variant branch) |
| C-5 Sanctum directory exists | `_bmad/memory/bmad-agent-<name>/` exists OR `# Sanctum exception` block present in SKILL.md | FAIL (no fallback) |
| C-6 If sanctum exists, 6-file BMB pattern present | `INDEX.md`, `PERSONA.md`, `CREED.md`, `BOND.md`, `MEMORY.md`, `CAPABILITIES.md` all exist + non-empty | FAIL with missing-file list |
| C-7 If `# Sanctum exception` block present | HTML comment `<!-- sanctum-exception:<category> -->` present; `<category>` matches a row in `sanctum-exception-categories.json`; `### Rationale` subsection ≥80 chars referencing "sanctum activation" or "BMB pattern" | FAIL with allowlist mismatch or rationale-too-short |
| C-8 Cold-activation smoke (FM-25 mitigation) | Simulate operator typing `talk to <name>` in fresh session; assert SKILL.md loads + sanctum batch loads + persona activates without error | FAIL with stack trace |

**Outputs:**
- Exit code 0 = all 11 specialists PASS
- Exit code non-zero = governance failure; ≥1 specialist failed; output names the specialist + failed check + remediation pointer

**Cadence:**
- Bound to `.github/workflows/specialist-parity.yml` per NFR-I9
- Required check; red blocks merge per FR102

---

## §8 Glossary

- **BMB** — BMad Method Builder; the workflow producing sanctum-shaped specialist agents.
- **Sanctum** — `_bmad/memory/bmad-agent-<name>/` directory holding persistent persona + continuity artifacts (6-file BMB pattern).
- **Sanctum-aligned** — a specialist whose SKILL.md + sanctum dir + 6 files all conform to §3 + §4.
- **Option-a** — the alignment path; SKILL.md + full sanctum + 6 files.
- **Option-b** — the documented-exception path; closed-allowlist category + party-mode ratification + `# Sanctum exception` block in SKILL.md.
- **Sidecar (Cora-style)** — a documented exception where the specialist's persistent state lives at `_bmad/memory/<name>-sidecar/` rather than the canonical `_bmad/memory/bmad-agent-<name>/`. **Used because the specialist is a runtime hook, not a conversational specialist.** *See option-b.*
- **Sidecar variant (Class-D2 pipeline-greenfield style)** — a scaffold pattern at `docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/` for greenfield specialists where the pipeline-stage artifact lives in a sibling directory to the specialist's main story scaffold. **Distinct from Cora sidecar; the two terms share a noun but address different concerns.** *See FR111 scaffold.*

> **DISAMBIGUATION CALLOUT:** "Sidecar (Cora-style)" and "Sidecar variant (Class-D2 style)" are unrelated concepts. Cora-sidecar is a **runtime/parity exception**; D2-sidecar-variant is an **authoring/scaffold layout**. Do not conflate.

---

## Errata + version history

- **2026-04-29** — Initial authoring (Slab 7b Wave 0 foundational artifact). Content derived from P0 path-verification sweep + R1 party-mode scoping consensus + R5/R6/R7/R8/R9 PRD amendments. Resolves R6 Mary's path-precision concerns: SKILL.md path is `skills/bmad-agent-<name>/SKILL.md` (NOT `app/specialists/<name>/SKILL.md` as PRD draft initially stated); required keys are `name` + `description` (NOT `agent_name` + `sanctum_path` + `activation_order`); BMB alignment marker is sanctum-dir-existence + 6-file pattern, NOT YAML frontmatter keys.
