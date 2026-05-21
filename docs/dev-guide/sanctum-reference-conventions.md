# Sanctum Reference Conventions

> **Audience:** Slab-2+ specialist authors and dev agents. Established by Story 2a.2 (party-mode 2026-04-24 MF7 binding). Inherited by 2a.3 (Kira), 2a.4 (Texas), and all 13 Slab-2b TEMPLATE inheritors.

## What this doc covers

When a migrated specialist references its sanctum content from inside an `app/specialists/<name>/expertise/README.md`, what convention does the dotted-reference idiom follow? What path does the sanctum live at? How is the sanctum fingerprint computed? And how do operators sequence sanctum-population ceremony relative to a story's open/close?

This doc is the canonical reference for those questions. The Pydantic-v2 model + the generator emit the **shape**; this doc names the **convention**.

---

## §1 — Path convention (hybrid clone)

Sanctum directories live at `_bmad/memory/bmad-agent-<skill-dir-name>/`, where `<skill-dir-name>` matches the **operator-facing skill directory**, not the app-side specialist short name.

| Specialist (app-side) | Skill directory (operator-facing) | Sanctum path |
|---|---|---|
| `irene` | `skills/bmad-agent-content-creator/` | `_bmad/memory/bmad-agent-content-creator/` |
| `gary` | `skills/bmad-agent-gamma/` (TBD per Slab-2b authoring) | `_bmad/memory/bmad-agent-gamma/` |
| `kira` | `skills/bmad-agent-kling/` | `_bmad/memory/bmad-agent-kling/` |
| `texas` | `skills/bmad-agent-texas/` | `_bmad/memory/bmad-agent-texas/` |
| `tracy` | `skills/bmad-agent-tracy/` | `_bmad/memory/bmad-agent-tracy/` |

**Drift caught at Story 2a.2:** Epic 2a.2 line 581 said the sanctum was at `_bmad/memory/bmad-agent-irene/`. The actual hybrid path is `_bmad/memory/bmad-agent-content-creator/`. Per CLAUDE.md §Custom-agents and Epic-26 BMB-sanctum-migration, hybrid uses **direct directory** (not symlink). The framework wins per DR-1 GOLDEN ratification — the spec yields to code on conflict. See [`specialist-anti-patterns.md` §A11](./specialist-anti-patterns.md) for the harvested entry.

---

## §2 — Dotted-reference idiom (`expertise/README.md`)

Each migrated specialist's `app/specialists/<name>/expertise/README.md` lists sanctum L-tier references by **dotted-reference convention**: a markdown table with `Dotted reference | Source-tree path | Pass-N step` columns. The sanctum directory itself does not duplicate the reference content; instead it carries the operator-curated continuity files (BOND, CREED, INDEX, MEMORY, PERSONA, etc.) populated at first-breath ceremony.

References are loaded as text into the LLM-invoking node (typically `_act`) at runtime via deterministic file reads — file order is fixed (alphabetical), missing files emit a deterministic placeholder so prompt shape is invariant across environments. See `app/specialists/irene/graph.py::_read_pass_2_references` for the canonical implementation.

### Class-C+ four-file sidecar pattern

Story 7b.5 establishes Tracy as the Class-C+ seed exemplar. Class-C+ sanctum
directories use a four-file BMB pattern:

- `INDEX.md`
- `PERSONA.md`
- `chronology.md`
- `access-boundaries.md`

This is intentionally distinct from the Class-A six-file BMB pattern
(`INDEX.md`, `PERSONA.md`, `CREED.md`, `BOND.md`, `MEMORY.md`,
`CAPABILITIES.md`). Class-C+ port-shape roles carry lighter continuity and
focus on activation-time intent shaping plus access boundaries.

---

## §3 — Empty-sanctum vs populated-and-locked: the activation epoch split

**Story 2a.2** establishes the **activation-baseline** measurement convention:

> **Empty-sanctum is the activation-story baseline (2a.2).** Populated-and-locked is the steady-state shape downstream stories operate against; 2a.3 onward exercises dotted-reference resolution against curated populated personas. The empty case here is the **measurement floor**, not the template.

The `SanctumFingerprint.compute(...)` operation produces a deterministic empty-string sorted-listing for empty directories, with sha256 = `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`. This is the load-bearing property for **FR54 cache-hit-rate baseline** measurement: an uncontrolled sanctum payload during the 10-invocation cache window introduces non-determinism into the cache prefix and collapses cache-hit-rate to 0%.

**Two valid epochs:**

| Epoch | When | Pattern | Carried metric |
|---|---|---|---|
| **Activation** | Story 2a.2 — first real LLM-invoking specialist | Empty sanctum for story duration | `baseline_tokens` (FR54 floor measurement) |
| **Steady-state** | Story 2a.3 onward | Populated-then-locked sanctum (operator first-breath population BEFORE dev-story opens, lock for cache window) | `steady_state_tokens` (FR54 steady-state measurement) |

**New tracked metric for 2a.3 close (Murat T4 binding):**
```
sanctum_context_cost = steady_state_tokens − baseline_tokens
```

---

## §4 — Operator sanctum-ceremony timing discipline (MF6 binding)

To prevent mid-story sanctum mutation from collapsing cache-hit-rate to 0%, the operator follows ONE of these patterns at story open:

1. **Empty for duration** (activation-baseline epoch — 2a.2 only): clear the sanctum directory before `bmad-dev-story` opens. Lock the empty state for the duration of the AC-D 10-invocation window. Recover by un-archiving + re-running first-breath after the story closes.
2. **Populated-and-locked** (steady-state epoch — 2a.3 onward): operator runs proper first-breath ceremony BEFORE `bmad-dev-story` opens. Lock the directory for the AC-D 10-invocation window. No mid-story mutation.

**Lockability micro-protocol** (Murat MF6 / Slab-2a.2 deferred):

```bash
# Pre-run baseline (empty case): assert count == 0
ls _bmad/memory/bmad-agent-<name>/ | wc -l

# Per-AC-D-invocation guard: re-assert before each invocation
# Post-run identity check: re-assert after invocation 10
```

For the populated case (2a.3+), the lock-and-verify protocol generalizes to:
- Pre-run: `find _bmad/memory/bmad-agent-<name>/ -type f -exec sha256sum {} +` → manifest
- Per-invocation: re-hash + diff against manifest; abort + fail-loud on drift
- Post-run: re-hash; byte-identical to pre-run or run is invalidated
- Filesystem-level enforcement (operator-gated): `chmod -R a-w` for the run window

**No mid-story sanctum mutation** is allowed during the AC-D cache-hit-rate measurement window. Mutation between invocations 1 and 10 invalidates the OpenAI prompt-prefix cache.

---

## §5 — Mapping back to architecture

This convention realizes architecture decisions:

- **D1** Sanctum hybrid (content-hash-per-checkpoint addressing via `SanctumFingerprint`)
- **D5** Sanctum cold-read + cache-prefix stability (cold-read at `_plan` node; the reference set bundled into the LLM-invoking node's prompt)
- **NFR-X3** Sanctum reproducibility (deterministic fingerprint across invocations)
- **NFR-I6** Cache-prefix stability (byte-identical prompt across N in-process invocations)
- **FR15** Sanctum cold-read (first per-specialist exercise at Story 2a.2)
- **FR54** Cache-hit-rate baseline (activation at Story 2a.2; steady-state from 2a.3 onward)

---

## §6 — Anti-pattern cross-references

When implementing or migrating a specialist, watch for these traps:

- [Anti-pattern A11](./specialist-anti-patterns.md) — Epic-doc sanctum-path drift from hybrid BMB migration convention. Caught at 2a.2 T1 (Epic 2a.2 line 581 stale).
- [Anti-pattern A12](./specialist-anti-patterns.md) — Procedural coupling between generator output and import-linter contract maintenance. Caught at 2a.2 T2 (pyproject.toml C3 ignore_imports row required per Slab-2+ specialist).

---

**Maintenance:** This doc is the single source of truth for sanctum-reference conventions across all Slab-2+ specialist migrations. Updates land at retrospective close + when a new specialist surfaces an edge case (e.g., 2a.3 Kira motion confirms the populated-and-locked steady-state pattern).
