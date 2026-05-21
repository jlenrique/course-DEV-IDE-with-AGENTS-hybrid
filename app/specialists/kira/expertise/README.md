# Kira expertise (L4 — video direction)

Specialist `kira` reads domain references from this directory during the
`plan` stage of its 9-node scaffold (the actual file reads happen in
`graph.py::_assemble_kira_prompt`, called from `_act` per the plan→act
hand-off). Per architecture D5 (sanctum cold-read + cache-prefix
stability), references are loaded by dotted convention from the
operator-facing skill tree at
[`skills/bmad-agent-kling/references/`](../../../../skills/bmad-agent-kling/references/)
— Kira's app-side specialist directory carries pointers, not duplicated
content.

- **mcp_tool:** `kling` (Kling video API dispatch)
- **expertise_tier:** `L4-video-direction`
- **sanctum:** `_bmad/memory/bmad-agent-kling/` (hybrid path; matches skill-dir
  name per `docs/dev-guide/sanctum-reference-conventions.md §1`)

## Sanctum-state convention (Story 2a.3 — first steady-state populated-and-locked epoch)

Per [`docs/dev-guide/sanctum-reference-conventions.md §3`](../../../../docs/dev-guide/sanctum-reference-conventions.md),
2a.3 inaugurates the **populated-and-locked steady-state epoch**. The operator
runs first-breath ceremony BEFORE `bmad-dev-story` opens to populate
`_bmad/memory/bmad-agent-kling/`, then locks the directory for the AC-D
10-invocation cache window. Empty-sanctum graceful-degrade is permitted as a
fallback when first-breath has not yet fired; the sanctum digest then yields
the deterministic empty-sorted-listing sha256 (matching 2a.2's baseline).

## L4 reference set (loaded at prompt-assembly via dotted convention)

| Dotted reference | Source-tree path | Capability |
|---|---|---|
| `content-type-mapping.md` | [skills/bmad-agent-kling/references/content-type-mapping.md](../../../../skills/bmad-agent-kling/references/content-type-mapping.md) | CT — clip type → Kling operation + cost-aware default |
| `context-envelope-schema.md` | [skills/bmad-agent-kling/references/context-envelope-schema.md](../../../../skills/bmad-agent-kling/references/context-envelope-schema.md) | ENV — Marcus delegation envelope schema |
| `init.md` | [skills/bmad-agent-kling/references/init.md](../../../../skills/bmad-agent-kling/references/init.md) | First-breath onboarding (when sanctum sidecar absent) |
| `memory-system.md` | [skills/bmad-agent-kling/references/memory-system.md](../../../../skills/bmad-agent-kling/references/memory-system.md) | Sidecar memory discipline + access boundary |
| `save-memory.md` | [skills/bmad-agent-kling/references/save-memory.md](../../../../skills/bmad-agent-kling/references/save-memory.md) | SM — write-path discipline for sidecar updates |
| `video-prompt-engineering.md` | [skills/bmad-agent-kling/references/video-prompt-engineering.md](../../../../skills/bmad-agent-kling/references/video-prompt-engineering.md) | VP/VQ — prompt structure + quality self-assessment lens |

These references are loaded as text into the act-node prompt assembly via
`graph.py::_read_kira_references` (fixed file order, alphabetical by name; sort
key `relative_to(...).as_posix()` for cross-platform stability per Murat MF3
binding inherited from 2a.2).

The `KIRA_REFERENCES` tuple in `app/specialists/kira/graph.py` is the
load-bearing source of truth for the file-order contract; this README
mirrors that tuple. Drift between the two is detected by
`tests/specialists/kira/test_kira_expertise_readme_lists_l4_references.py`.
