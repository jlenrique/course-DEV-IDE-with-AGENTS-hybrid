# Upstream Severance Log

**Purpose:** one-time audit record of the final upstream-to-hybrid
absorption + severance event. After this event, `upstream/master` is no
longer an input source for migration work — the hybrid clone is
operationally self-contained.

**Protocol:** see
[`docs/dev-guide/langgraph-migration-guide.md §8.1`](../../docs/dev-guide/langgraph-migration-guide.md#81-upstream-severance-slab-2).

---

## Event 1 — Final absorption + severance (2026-04-24)

| Field | Value |
|---|---|
| **Event type** | Final absorption from upstream/master, followed by severance |
| **Pre-absorption hybrid HEAD** | `9d4a49c` (chore: deferred-inventory forward-port posture) |
| **Absorption source SHA** | `3ed7c56b0d288c07018ac7fc2401014b8f5967f1` (`3ed7c56`) — upstream/master Sprint #2 close |
| **Post-absorption hybrid HEAD** | `<TBD — this commit>` |
| **Mechanism** | Scoped `git checkout 3ed7c56 -- <paths>` — no merge; hybrid's dev branch history stays linear |
| **Operator directive** | "Big bang; sprint to hybrid operational; sever the relationship with upstream/master; trial-run refinements happen here." |

### Upstream commits absorbed (content delta between freeze and severance)

| SHA | Subject | Migration-relevant content |
|---|---|---|
| `1cc2ee0` | Close Sprint #2 — portable intake + audio production + perception repertoire | **NEW specialist: Wondercraft** (full first-breath scaffold: BOND/CAPABILITIES/CREED/INDEX/MEMORY/PERSONA templates + 6 capability references + init-sanctum.py). Irene Pass-2 authoring template + grammar-riders. Marcus dispatch-registry.yaml. Texas transform-registry + extraction-validator polish. Pre-flight-check strategy matrix. Sensory-bridges image_to_agent.py. |
| `c4f5cbc` | Close 27-5 Notion MCP provider — project-scope fetch layer | Texas: Notion MCP provider (retrieval dispatch extension). |
| `bbb343f` | Close 27-6 Box provider — locator-shape fetch layer | Texas: Box provider (locator-shape fetch). |
| `67f9eef` | Align MCP auth contracts and normalize Sprint 1 story keys | Texas: Consensus provider + scite provider refresh + retrieval-contract polish. Compositor operations polish. |

### Paths absorbed (9 targets, scoped narrowly to specialist skill surfaces)

| Path | Rationale |
|---|---|
| `skills/bmad-agent-content-creator/` (Irene) | Full directory overlay — Pass-2 templates, grammar riders, retrieval-intake contract, motion-gate receipt reader. Irene migrates in Slab 2 or 2b; inputs must reflect latest primary-side refinement. |
| `skills/bmad-agent-texas/` | Full directory overlay — Consensus + Notion MCP + Box providers + retrieval-contract + transform-registry + extraction-validator. Texas is the most-evolved upstream specialist; Slab 2b migration absorbs all of this. |
| `skills/bmad-agent-marcus/references/dispatch-registry.yaml` | Single file — Marcus is Slab 3 scope, but Slab 2b.15 (dispatch-contract hardening) references this registry. Rest of Marcus skill dir stays at hybrid HEAD since Slab 3 rewrites it into `app/specialists/marcus/`. |
| `skills/bmad-agent-wondercraft/` (new specialist) | Full directory overlay — new specialist that lands on primary via Sprint #2 close. **Revises Slab 2c.1 scope** (see Roster Reconciliation §Category B+). |
| `skills/pre-flight-check/references/check-strategy-matrix.md` | Shared skill reference used by Marcus + all specialists at pre-flight. |
| `skills/sensory-bridges/scripts/image_to_agent.py` | Shared skill — Vera + Kira + any specialist needing visual perception calls this. |
| `skills/compositor/scripts/compositor_operations.py` + tests | Compositor wrapper (contract-relevant for Slab 2b.N node bodies that hand off to Descript). |
| `docs/agent-environment.md` | Operator/agent environmental guidance referenced by session-START protocol. |

### Paths explicitly NOT absorbed (primary-repo code/test/config that doesn't fit hybrid layout)

- `marcus/dispatch/contract.py` — primary's top-level `marcus/` module layout; hybrid writes its own `app/models/dispatch/` in Slab 2b.15.
- `scripts/utilities/**` — primary-repo utilities; hybrid migration writes equivalents under `app/` as Slab 2/3 stories progress.
- `tests/test_{notion,box,image}_provider.py` + `tests/wondercraft/test_specialist_dispatch.py` + `tests/marcus_dispatch/test_dispatch_contract.py` + `tests/contracts/test_reading_path_parity.py` — top-level primary tests against primary's orchestration layer; hybrid's Slab 2b.N work authors its own tests under `tests/integration/scaffold_conformance/` and per-specialist `tests/specialists/<name>/`.
- `state/config/reading-path-patterns.yaml` + related state files — primary substrate config; hybrid has its own substrate config under `state/config/pipeline-manifest.yaml`.
- `_bmad-output/implementation-artifacts/*.md` — primary-repo story spec docs (27-3, 24-2, 7-1, PR-R, evidence-bolster, irene-retrieval-intake); these refer to primary orchestration and do not apply to hybrid's migration track.
- `docs/operations-context.md` + `docs/research-knobs-guide.md` — primary operator guidance; not migration-load-bearing.

### Severance cutoff statement

**After this commit, the `upstream` remote is retained for historical `git log upstream/master` reference only.** No further fetch-and-read into migration work; no `git show upstream/master:…` in 2b.N T1 Readiness blocks. If a post-severance incident genuinely requires re-opening the channel (e.g., operator-initiated emergency absorption), treat as a party-mode governance exception with full documentation — not a standing escape hatch.

### Lost upstream content (accepted loss)

The following upstream content was **intentionally not absorbed** and is permanently out-of-reach to hybrid's migration track post-severance. These are acknowledged as acceptable losses under the "sprint to hybrid operational" directive:

- Primary-repo story spec artifacts (listed above) — available via `git log upstream/master` historical lookup if ever needed; not migration-critical.
- Primary-repo orchestration-layer tests and utilities — re-derived by hybrid migration stories.
- Any upstream commits that land **after** `3ed7c56` — all future primary-repo work stays on primary; hybrid becomes the single truth for APP development.

---

## Re-severance events

*(None anticipated. If severance is ever reopened under a party-mode exception, append one entry per event here.)*
