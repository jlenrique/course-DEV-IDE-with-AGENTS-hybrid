# Migration Story 2a.5: Generator auto-emits `pyproject.toml` C3 `ignore_imports` row

**Status:** done
**Sprint key:** `migration-2a-5-generator-auto-emit-pyproject-c3-row`
**Epic:** Slab 2a (migration Epic 2a — Specialist Scaffold Pilot) — **tail-end debt cleanup; reopens Epic 2a from `done` → `in-progress` for the duration of this story; flips back to `done` at 2a.5 close**
**Parent defect:** Story 2a.1 (`migration-2a-1-bmad-create-specialist-generator-and-9-node-scaffold-reference`) — generator emits a graph that imports `app.gates.resume_api.resume_from_verdict` but does NOT auto-update `pyproject.toml`'s C3 `ignore_imports` list, forcing every Slab-2+ specialist migration to perform the manual edit at T2.
**Milestone anchored:** **gating gate for Slab 2b kickoff** per [`slab-2a-retrospective.md`](slab-2a-retrospective.md) §"If you're reading this at Slab 2b T1" item 1 + [`deferred-inventory.md`](../planning-artifacts/deferred-inventory.md) §Named-But-Not-Filed Follow-Ons row "Generator auto-emit pyproject.toml C3 ignore_imports row".
**Pts:** 2 | **Gate:** single-gate (defect fix; no schema-shape, no lane/package boundary, no invariant preservation, no operator-acceptance gate) | **K-target:** ~1.4× (target 6–8 / floor 5; six surfaces — green-path append + idempotency + dry-run + atomic rollback + comment-marker shape + post-emit `lint-imports` clean)

---

## T1 Readiness Block

**Before writing any code**, the dev agent reads in order:

1. **Governance lookup** — [`docs/dev-guide/migration-story-governance.json`](../../docs/dev-guide/migration-story-governance.json) — confirms Story `2a-5` is frozen at `expected_gate_mode: "single-gate"` with `rationale: null` (party-mode T2 2026-04-24 ratification per Murat (b)-preferred path / Winston path-2 / Paige A12 procedural-coupling category; defect fix with no schema-shape risk surface). Do not relitigate.
2. **Sandbox-AC pre-flight** — run the validator (single command before T2):
   ```bash
   .venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py \
     _bmad-output/implementation-artifacts/migration-2a-5-generator-auto-emit-pyproject-c3-row.md
   ```
   Expect `PASS`. All ACs in this story are dev-agent-executable (no operator-gated block; no live API calls; the work is offline file mutation + tests).
3. **The defect itself** — read [`skills/bmad_create_specialist/scripts/generate.py`](../../skills/bmad_create_specialist/scripts/generate.py) lines 220–223 (the `resume_from_verdict` import-presence check at `_validate_plan_shapes`) AND [`pyproject.toml`](../../pyproject.toml) lines 96–113 (the C3 `ignore_imports` list with the four current entries: `app.mcp_server.tools.gate_decide`, `app.specialists._scaffold.graph`, `app.specialists.irene.graph`, `app.specialists.kira.graph`, `app.specialists.texas.graph`). The generator validates the graph emits the import; it does NOT mutate `pyproject.toml` to make import-linter accept the new edge.
4. **Three-instance evidence base** — confirm at T1 that all three Slab 2a specialist migrations carry the manual workaround:
   - Story 2a.2 (Irene) — `pyproject.toml:110` row `app.specialists.irene.graph -> app.gates.resume_api`
   - Story 2a.3 (Kira) — `pyproject.toml:111` row `app.specialists.kira.graph -> app.gates.resume_api`
   - Story 2a.4 (Texas) — `pyproject.toml:112` row `app.specialists.texas.graph -> app.gates.resume_api`
5. **Anti-pattern entry** — [`docs/dev-guide/specialist-anti-patterns.md`](../../docs/dev-guide/specialist-anti-patterns.md) §A12 "Procedural coupling: generator output ↔ import-linter contract" describes the resolution path (b) this story implements. After 2a.5 closes, the entry is updated to mark path (b) shipped (see AC-2a.5-H).
6. **Generator test idiom** — [`tests/specialists/generator/conftest.py`](../../tests/specialists/generator/conftest.py) defines `temp_repo_root` (isolated tmp repo skeleton) + `make_request` (default `name="toytest"`). Tests in this story extend `temp_repo_root` (or compose with it) so the temp repo also carries a representative `pyproject.toml` with the C3 contract structure.
7. **Documentation impact** — [`docs/dev-guide/langgraph-migration-guide.md §12.4`](../../docs/dev-guide/langgraph-migration-guide.md#124-manual-post-edit-checklist-frozen) currently lists step 3 "Manually append `app.specialists.<name>.graph -> app.gates.resume_api` to `pyproject.toml`'s C3 `ignore_imports` list". After 2a.5, this step is replaced with a one-liner naming the auto-emit behavior (see AC-2a.5-G).
8. **Severance posture** — hybrid working tree is the input surface; no `git show upstream/master:…`; no `git fetch upstream`. Per memory `project_upstream_severance.md` (severed 2026-04-24).
9. **Slab 2b gate language** — [`slab-2a-retrospective.md`](slab-2a-retrospective.md) §"Slab 2b kickoff readiness checklist" hard gate 1: "**A12 generator auto-emit follow-on landed.** This is THE Slab-2a→2b binding gate. Three manual C3 ignore-imports edits is the evidence base; do not pay this debt a fourth time." 2a.5 close is the event that flips this gate from open to satisfied.

**Record T1 verifications in Dev Agent Record T1 Readiness block BEFORE writing any code at T2.**

---

## Story

As a **dev agent migrating any Slab-2b specialist via `bmad-create-specialist`**,
I want **the generator to atomically append `app.specialists.<name>.graph -> app.gates.resume_api` to `pyproject.toml`'s Contract C3 `ignore_imports` list (with a generated comment marker, idempotently, alongside the existing four-file-lockstep emission)**,
So that **import-linter Contract C3 stays green at T2 lint-imports run without any manual `pyproject.toml` edit, the 14-instance flakiness vector across Slab 2b's TEMPLATE inheritors is eliminated, and the Slab-2a→2b binding gate flips closed**.

---

## Acceptance Criteria

All ACs are dev-agent-executable (sandbox-AC compliant). No operator-gated block. The generator stays offline — no live LLM calls, no network, no operator CLIs.

### AC-2a.5-A — Generator atomically appends C3 `ignore_imports` row at wet-run

- **Given** the generator at `skills/bmad_create_specialist/scripts/generate.py` currently emits the 9-file specialist tree per `_planned_items()` + `_write_items_atomic()` (lines 143–280 of generate.py at T1) but does NOT mutate `pyproject.toml`
- **When** the dev agent runs `.venv/Scripts/python.exe -m skills.bmad_create_specialist.scripts.generate --name <newname> --mcp <tool> --expertise-tier <tier>` with `<newname>` not already present in `pyproject.toml`'s C3 `ignore_imports` list
- **Then** in addition to the existing 9-file emission, `pyproject.toml`'s `[[tool.importlinter.contracts]]` block whose `name` starts with `"Contract C3"` gains exactly one new entry in the `ignore_imports` list at the **end** of the list, in the form:

  ```toml
  ignore_imports = [
      ...existing entries unchanged...,
      "app.specialists.<newname>.graph -> app.gates.resume_api",  # generated by bmad-create-specialist for <newname>
  ]
  ```

  All other contracts in `pyproject.toml` are byte-identical to pre-run. Existing `ignore_imports` entries are not reordered. Whitespace around the new entry conforms to the existing list formatting (4-space indent + trailing comma per existing rows).

- **Verification:** post-run `.venv/Scripts/python.exe -m import_linter` (alias `lint-imports`) reports `3/3 KEPT` against the temp repo; `pyproject.toml` line count grew by exactly 1 vs pre-run.

### AC-2a.5-B — Idempotent on re-run for the same name

- **Given** `pyproject.toml`'s C3 `ignore_imports` list already contains `"app.specialists.<name>.graph -> app.gates.resume_api"` (either because 2a.5 already ran for this name, OR because the row was hand-edited in pre-2a.5 era like Irene/Kira/Texas)
- **When** the generator runs again with `--force` (or the operator re-invokes for any other reason)
- **Then** the generator detects "row already present" and performs **zero mutation** on `pyproject.toml`. The 9-file specialist emission proceeds normally (subject to `--force` semantics for those files). `pyproject.toml` is byte-identical to pre-run.
- **Detection rule:** match by **exact string equality** on the rendered import edge `f"app.specialists.{name}.graph -> app.gates.resume_api"` against each existing entry's quoted body (ignoring trailing comments + whitespace). This avoids false positives from substring matches against neighboring names.

### AC-2a.5-C — `--dry-run` does not mutate `pyproject.toml`

- **Given** the generator is invoked with `--dry-run` (per existing AC-2a.1-C2 + R11 semantics: parses + shape-validates the would-be emission tree but writes ZERO files)
- **When** dry-run executes for a name that would trigger a `pyproject.toml` mutation at wet-run
- **Then** `pyproject.toml` is byte-identical to pre-run (zero file writes); `GenerationResult.written_files == ()` (existing contract); dry-run stdout enumerates the planned `pyproject.toml` mutation as one additional entry in the human-readable plan summary (`f"would append C3 ignore_imports row: app.specialists.{name}.graph -> app.gates.resume_api"` or equivalent), distinct from the 9-file emission tree.

### AC-2a.5-D — Atomic rollback: pyproject mutation is part of the same atomic unit as file emission

- **Given** the existing `_write_items_atomic()` rolls back all 9 files on any mid-emission failure (lines 237–280 of generate.py at T1)
- **When** the pyproject mutation fails (mocked `Path.write_text` failure injected at the pyproject step) AFTER the 9 files have been written
- **Then** the generator (a) restores `pyproject.toml` to its pre-run byte content (read-before-write backup pattern), AND (b) rolls back the 9 emitted files per the existing atomic-rollback path. **No partial state.** `GeneratorInputError: atomic emission failed: <reason>` is raised matching the existing error idiom.
- **And** when the pyproject mutation fails BEFORE the 9 files have been written (read-before-write check fails first), the 9 files are not yet on disk so no file rollback is needed; `GeneratorInputError` is raised; `app/specialists/<name>/` does not exist post-failure.
- **Implementation choice:** dev agent's discretion whether to do pyproject mutation FIRST (before 9-file emission) or LAST (after 9-file emission). Either ordering is acceptable as long as atomic rollback covers both directions on mid-step failure. **Recommended:** mutate pyproject LAST so that successful 9-file emission is the precondition for pyproject append; this matches the natural "the new edge actually exists in the emitted graph" causality and minimizes cases where pyproject is in a state ahead of `app/specialists/`.

### AC-2a.5-E — Generated row carries the comment marker

- **Given** the new C3 `ignore_imports` entry per AC-2a.5-A
- **When** the dev agent inspects `pyproject.toml` post-run
- **Then** the new row is followed (on the same physical line, after the trailing comma) by an inline comment in the exact form:

  ```
      "app.specialists.<name>.graph -> app.gates.resume_api",  # generated by bmad-create-specialist for <name>
  ```

  Two-space gap before the `#`. The comment is the **provenance signal** — it lets a future operator (or dev agent) grep the C3 list and tell at a glance which rows were auto-emitted vs hand-authored. Existing pre-2a.5 rows (Irene/Kira/Texas/scaffold/mcp_server) MUST NOT receive the comment retroactively (no in-place rewrites of pre-existing rows; AC-2a.5-A wins on the reordering invariant).

### AC-2a.5-F — Post-emit `lint-imports` clean against generator output

- **Given** the generator has been run end-to-end against a temp repo with a representative `pyproject.toml` (C3 contract present, mirror of repo-root shape) AND `<name>=fakeauto5`
- **When** the test runs `.venv/Scripts/python.exe -m import_linter --config <temp pyproject>` (or `subprocess.run([...], cwd=temp_repo_root)`) immediately after generation
- **Then** import-linter exits 0 with `3/3 KEPT`; no contract failures. **Caveat:** because the temp repo does not host the actual `app/` source tree, this test asserts **parser acceptance** of the mutated `pyproject.toml` (no syntax errors, contract block parses, ignore_imports list parses) — not full graph traversal. The full-graph clean state is asserted at the repo level via the existing `lint-imports` invocation in the regression block of T8.

### AC-2a.5-G — Migration-guide `§12.4` updated to remove the manual step

- **Given** [`docs/dev-guide/langgraph-migration-guide.md §12.4`](../../docs/dev-guide/langgraph-migration-guide.md#124-manual-post-edit-checklist-frozen) currently names the manual `pyproject.toml` C3 `ignore_imports` append as step 3 of the post-generator checklist
- **When** the dev agent updates §12.4
- **Then** the manual step is replaced (NOT just removed) with a single line in the form:

  > **(formerly step 3 — auto-emitted as of Story 2a.5; the generator atomically appends `app.specialists.<name>.graph -> app.gates.resume_api` to `pyproject.toml`'s C3 `ignore_imports` list with a generated comment marker. Idempotent. No manual edit needed.)**

  The line lives where step 3 used to be so that downstream readers see the "what changed" framing. Subsequent steps renumber by one (4→3, 5→4, etc.). If the section's framing prose references "four manual steps", it becomes "three manual steps".

### AC-2a.5-H — Anti-pattern catalog entry A12 marked RESOLVED

- **Given** [`docs/dev-guide/specialist-anti-patterns.md §A12`](../../docs/dev-guide/specialist-anti-patterns.md) describes path (b) as the deferred resolution
- **When** the dev agent updates the entry
- **Then** the **Counter-pattern** field is amended to add a leading sentence in the form:

  > **RESOLVED at Slab 2a Story 2a.5 (path b shipped 2026-04-2X commit `<sha>`).** The generator now auto-emits the C3 `ignore_imports` row atomically alongside the 9-file specialist tree; manual edit no longer required. The historical context below is retained for the anti-pattern's discovery slab + procedural-coupling category illustration.

  The original 4-field shape is preserved; only the **Counter-pattern** body grows the leading sentence. **Slab-of-discovery** field is unchanged (Slab 2a Story 2a.2 T2). **Example** field is unchanged (the procedural-coupling description still names the pre-2a.5 status quo, useful as a worked example of the procedural-coupling pattern).

### AC-2a.5-I — Slab 2b kickoff binding gate satisfied

- **Given** [`slab-2a-retrospective.md`](slab-2a-retrospective.md) §"Slab 2b kickoff readiness checklist" hard gate 1 explicitly ties Slab 2b.1 TEMPLATE open to A12 landing
- **When** 2a.5 closes
- **Then** the dev agent appends a one-line **Slab 2b kickoff gate flip** entry to the **Closing note** of `slab-2a-retrospective.md` in the form:

  > **2026-04-2X update:** A12 generator auto-emit shipped at Story 2a.5 close. Slab 2b kickoff hard gate 1 satisfied. Slab 2b.1 (Gary TEMPLATE) is now open to author.

  No edits to the §"Slab 2b kickoff readiness checklist" Hard-gates list itself (the checkbox stays unchecked there as a historical artifact of the gate's existence; the closing-note update is the live state).

### AC-2a.5-J — D12 close protocol (single-gate)

- **Given** 2a.5 is the Slab-2a→2b bridge story (not slab-closing — Slab 2a was closed at 2a.4; 2a.5 is tail-end debt that re-opens-and-re-closes Epic 2a)
- **When** the story closes
- **Then** the three-line D12 close stub is recorded in Dev Agent Record:
  1. **Invariant preservation:** generator's existing 9-file four-file-lockstep emission unchanged; atomic rollback contract extended to include `pyproject.toml`; import-linter 3/3 KEPT before AND after on the actual repo (5 manual rows + 0 auto-emitted yet → still 5 rows post-close because 2a.5 doesn't itself generate a new specialist; the auto-emit machinery is ready to fire from 2b.1 onward).
  2. **Anti-pattern harvest:** A12 entry updated per AC-2a.5-H. **No new entry** filed (the procedural-coupling pattern is the same one A12 already names; resolving it does not create a new sibling pattern).
  3. **Migration-guide update:** §12.4 updated per AC-2a.5-G. Slab 2a retrospective Closing note updated per AC-2a.5-I.

### AC-2a.5-K — Sprint-status + governance JSON state flips

- **Given** Epic 2a is currently `done` per `sprint-status.yaml` line 760 (closed at 2a.4); the migration-story-governance JSON does not yet have a `2a-5` entry
- **When** the story is filed (at this spec's authoring) AND when the story closes
- **Then** at filing:
  - `sprint-status.yaml` adds `migration-2a-5-generator-auto-emit-pyproject-c3-row: ready-for-dev` under the Slab 2 block (sibling to the four existing 2a-* entries) with a one-paragraph comment naming the gate-flip mechanics
  - `sprint-status.yaml` flips `migration-epic-2a-slab-2-scaffold-pilot: done` → `in-progress` with a one-line comment noting the temporary reopen for tail-end debt
  - `migration-story-governance.json` gains entry `"2a-5": { "expected_gate_mode": "single-gate", "rationale": null, "_amendment_note": "..." }` with a `version` bump (e.g., `"2026-04-22"` → `"2026-04-25"`) and an entry in the `_amendment_note` field naming the T2 party-mode 2026-04-24 ratification + Story 2a.5 filing date
- **And** at story close (this is the dev agent's responsibility at T9, not at T1):
  - `sprint-status.yaml` flips `migration-2a-5-…: ready-for-dev` → `done`
  - `sprint-status.yaml` flips `migration-epic-2a-slab-2-scaffold-pilot: in-progress` → `done`
  - `last_updated` field updated to the close date

### AC-2a.5-L — Deferred-inventory entry status flip

- **Given** [`deferred-inventory.md`](../planning-artifacts/deferred-inventory.md) §Named-But-Not-Filed Follow-Ons currently carries the row "Generator auto-emit pyproject.toml C3 ignore_imports row (2a.1 follow-on defect)" (named-but-not-filed)
- **When** 2a.5 is filed AND when 2a.5 closes
- **Then** at filing:
  - The row's **Trigger** column gains a leading bracketed marker `**[FILED 2026-04-2X as Story 2a.5]** ...` (preserving the rest of the trigger description for historical context)
- **And** at close:
  - The row's **Trigger** column updates to `**[CLOSED 2026-04-2X at Story 2a.5 — path (b) shipped]**` (replacing the FILED marker)
  - The §"Inventory Summary" table's "Named-but-not-filed follow-ons" count decrements by 1 (e.g., 24 → 23)
  - Footer note "Total named follow-ons: 24" updates accordingly

---

## Architecture Compliance

### Decisions the story honors

| Decision | Application |
|---|---|
| **D1 — Sanctum hybrid** | Not relevant; no sanctum content involved. |
| **D2 — Three-level model cascade** | Not relevant; no `model_config.yaml` change. |
| **D3 — HIL invariant tamper-evidence** | The C3 contract IS the D3 binding artifact. 2a.5 strengthens the binding by closing the procedural-coupling gap that lets the contract drift out of lockstep with the emitted graph. **Critical:** 2a.5 does NOT widen C3 — it only auto-emits the same kind of row dev agents have been adding manually. Auto-emit machinery + idempotency rule are the safety net that prevents accidental widening (the rule "match by exact string equality on the rendered edge" is the single-purpose check; the generator does NOT add other forbidden_modules entries or other contract blocks). |
| **D4 — Lane separation** | Not relevant; no cross-lane code added. |
| **D8 — Frozen-graph ceremony** | Not relevant; generator output shape unchanged. |
| **D12 — Cross-slab governance** | Close protocol per AC-2a.5-J. |
| **D13 — Registry bump** | Not relevant. |

### Architecture-to-code mapping

- **C3 contract authority:** [`pyproject.toml`](../../pyproject.toml) lines 96–113. Contract block name starts with `"Contract C3"`. Mutation point: the `ignore_imports` list, append-at-end semantics. **The generator does NOT introduce a new contract or modify the `forbidden_modules` list — only the `ignore_imports` allowlist for the new specialist's graph module.**
- **Generator entry point:** [`skills/bmad_create_specialist/scripts/generate.py::generate_specialist`](../../skills/bmad_create_specialist/scripts/generate.py) — wraps `_planned_items` + `_validate_plan_shapes` + `_write_items_atomic`. The pyproject mutation is a sibling step in the same atomic unit. Pseudocode shape (dev agent's discretion on exact factoring):
  ```python
  def generate_specialist(request):
      ...existing planning + validation...
      if request.dry_run:
          # also enumerate the planned pyproject mutation in the human-readable summary
          return GenerationResult(...)
      written = _write_items_atomic(items=items, repo_root=root, force=request.force, name=request.name)
      try:
          _append_c3_ignore_imports_row_idempotent(name=request.name, repo_root=root)
      except Exception as exc:
          _rollback_files(written)  # reuse existing rollback machinery from _write_items_atomic
          raise GeneratorInputError(f"atomic emission failed at pyproject mutation: {exc}") from exc
      return GenerationResult(planned_files=planned, written_files=written, dry_run=False)
  ```

---

## File Structure Requirements

### NEW files

```
tests/specialists/generator/
└── test_generator_pyproject_c3_row.py             # ALL FOUR new tests in one module
                                                   # (single test file keeps K conservative
                                                   # per Murat anti-padding band; parametrize
                                                   # the four scenarios within the module)
```

### MODIFIED files

- [`skills/bmad_create_specialist/scripts/generate.py`](../../skills/bmad_create_specialist/scripts/generate.py) — add `_append_c3_ignore_imports_row_idempotent(name, repo_root)` + atomic-rollback wiring per AC-2a.5-A/B/C/D
- [`tests/specialists/generator/conftest.py`](../../tests/specialists/generator/conftest.py) — extend `temp_repo_root` to also write a representative `pyproject.toml` containing the C3 contract block (or factor a sibling fixture `temp_repo_root_with_pyproject` if the existing fixture is widely depended on without pyproject)
- [`docs/dev-guide/langgraph-migration-guide.md`](../../docs/dev-guide/langgraph-migration-guide.md) §12.4 — per AC-2a.5-G
- [`docs/dev-guide/specialist-anti-patterns.md`](../../docs/dev-guide/specialist-anti-patterns.md) §A12 — per AC-2a.5-H
- [`_bmad-output/implementation-artifacts/slab-2a-retrospective.md`](slab-2a-retrospective.md) **Closing note** — per AC-2a.5-I
- [`_bmad-output/implementation-artifacts/sprint-status.yaml`](sprint-status.yaml) — per AC-2a.5-K
- [`docs/dev-guide/migration-story-governance.json`](../../docs/dev-guide/migration-story-governance.json) — per AC-2a.5-K (already added at filing; dev agent does NOT re-edit at T2 unless governance review surfaces a defect)
- [`_bmad-output/planning-artifacts/deferred-inventory.md`](../planning-artifacts/deferred-inventory.md) — per AC-2a.5-L

### NOT modified

- [`pyproject.toml`](../../pyproject.toml) — **do NOT pre-add a row for any future specialist**. The auto-emit machinery is what populates new rows; manually pre-seeding rows for unborn specialists would defeat the test surface. The existing five rows (mcp_server / _scaffold / irene / kira / texas) stay byte-identical.
- [`skills/bmad-create-specialist/templates/`](../../skills/bmad-create-specialist/templates) — no template changes; the auto-emit logic lives in `generate.py`, not in templates.
- [`tests/integration/scaffold_conformance/scaffold_contract.py`](../../tests/integration/scaffold_conformance/scaffold_contract.py) — DO NOT touch.
- Any primary-repo path — severance posture; no `git show upstream/master:…`.

---

## Technical Requirements

### Dependencies

- **No new runtime dep.** `pyproject.toml` parsing in stdlib via `tomllib` (Python 3.11+; project requires `>=3.11` per `pyproject.toml::requires-python`). Writing back: stdlib string manipulation is sufficient for this narrow append (the file is hand-edited TOML, not round-tripped through a TOML serializer; preserving comment-and-whitespace fidelity is the constraint, and that's what stdlib `pathlib.Path.read_text` + targeted insertion gives us). **Do NOT add `tomli-w` or another TOML serializer dep** — the round-trip cost (loss of comments / formatting) is not worth eliminating.
- **Recommended approach:** read `pyproject.toml` as text; locate the `[[tool.importlinter.contracts]]` block whose `name` line matches `"Contract C3"`; locate that block's `ignore_imports = [` opening line; locate its closing `]`; insert the new entry immediately before `]` with proper indent + trailing comma + comment marker. Idempotency check: scan the block's existing entries (between `[` and `]`) for exact rendered-edge equality before inserting.
- **Edge case:** if the C3 block is absent (e.g., temp_repo_root fixture without pyproject), the generator should raise `GeneratorInputError` at the start of `_append_c3_ignore_imports_row_idempotent` with a clear message ("`pyproject.toml` does not contain a Contract C3 importlinter block — cannot auto-emit ignore_imports row"). Test fixture for AC-2a.5-A/B/E/F uses a temp repo with a representative C3 block; AC-2a.5-D's failure-injection variant tests this absent-block path as one of the rollback triggers.

### Atomicity contract

- **Pre-flight check:** read `pyproject.toml` BEFORE any specialist file is written; cache the original byte content for rollback (read-modify-write pattern). If the C3 block is malformed (missing `name = "Contract C3"`, missing `ignore_imports = [`, no closing `]` matched), raise `GeneratorInputError` immediately — no specialist files are emitted.
- **Mid-flight failure handling:** if the 9-file emission succeeds but the pyproject write fails (mocked filesystem failure in tests), roll back ALL 9 files using the existing `_write_items_atomic`'s rollback path, then restore `pyproject.toml` from the cached pre-write content.
- **Why pyproject-mutation-LAST is recommended:** if the 9 files fail to emit, pyproject is never touched (no rollback needed for it). If the 9 files succeed but pyproject fails, both rollbacks fire. This minimizes the "inconsistent state visible on disk between two tool boundaries" window.

### Invariants preserved (NFR-X1–X5)

- NFR-X1 (byte-for-byte replay) — generator output shape unchanged for the 9 specialist files; pyproject mutation is per-name deterministic (same `<name>` always produces same row).
- NFR-X2 (frozen graph version) — not relevant.
- NFR-X3 (sanctum snapshot) — not relevant.
- NFR-X4 (model-resolution trail) — not relevant.
- NFR-X5 (documented temperature variance) — not relevant.

### FR coverage for this story

- **FR13** (specialist-generator-from-skill) — strengthened (procedural-coupling residue eliminated).
- **FR14** (programmatic scaffold conformance) — strengthened (post-generator state is now full-conformance with no manual step).
- **No new FR closure** — this is a defect cleanup, not a new capability.

---

## Testing Requirements

### K-target policy: ~1.4× (target 6–8 / floor 5)

This is a defect fix with a narrow scope (one new function in `generate.py` + atomic-rollback wiring + pyproject-text-mutation logic). Six surfaces:

1. **Green-path append** (AC-2a.5-A) — wet-run on a fresh `<name>` adds exactly one row; row has correct shape; row has comment marker.
2. **Idempotency** (AC-2a.5-B) — re-run for the same name is a no-op; pyproject byte-identical.
3. **Dry-run no-op** (AC-2a.5-C) — `--dry-run` does not mutate pyproject; dry-run summary names the planned mutation.
4. **Atomic rollback** (AC-2a.5-D) — mocked pyproject-write failure triggers full rollback (9 specialist files + pyproject); no partial state.
5. **Comment-marker shape** (AC-2a.5-E) — generated row matches the exact form (`,  # generated by bmad-create-specialist for <name>`).
6. **Post-emit lint-imports clean** (AC-2a.5-F) — temp-repo invocation of `import-linter` parses the mutated pyproject without error.

**Target:** 6–8 collecting tests (one parametrized module + one integration test).
**Floor:** 5 collecting tests (below this misses one of the six surfaces).
**K-bound:** ~1.4× per Murat anti-padding band; consolidate scenarios into one parametrized module rather than splitting one-test-per-file.

### Test surface

| Test module | Coverage |
|---|---|
| `tests/specialists/generator/test_generator_pyproject_c3_row.py::test_appends_row_at_wet_run` | AC-2a.5-A: single new row; correct shape; pre-existing rows untouched |
| `tests/specialists/generator/test_generator_pyproject_c3_row.py::test_idempotent_on_rerun` | AC-2a.5-B: re-run leaves pyproject byte-identical |
| `tests/specialists/generator/test_generator_pyproject_c3_row.py::test_dry_run_does_not_mutate` | AC-2a.5-C: `--dry-run` no-op; planned mutation in stdout |
| `tests/specialists/generator/test_generator_pyproject_c3_row.py::test_atomic_rollback_on_pyproject_failure` | AC-2a.5-D: mocked write failure → full rollback (9 files + pyproject) |
| `tests/specialists/generator/test_generator_pyproject_c3_row.py::test_atomic_rollback_on_malformed_c3_block` | AC-2a.5-D edge: temp pyproject without C3 block → `GeneratorInputError` raised before file emission begins |
| `tests/specialists/generator/test_generator_pyproject_c3_row.py::test_comment_marker_shape` | AC-2a.5-E: generated row's inline comment matches exact form |
| `tests/specialists/generator/test_generator_pyproject_c3_row.py::test_lint_imports_clean_after_emit` | AC-2a.5-F: subprocess run of `import-linter` against temp pyproject exits 0 with `3/3 KEPT` |

### Regression floor (pre-story baseline at 2a.4 close)

- **2a.4 close:** Texas-only suite 36 passed; migration-scoped 169 passed / 2 skipped placeholder-key (per [`sprint-status.yaml`](sprint-status.yaml) line 765).
- **Target at 2a.5 T8:** 36 passed Texas-only (unchanged — 2a.5 does not touch Texas) + 6–8 net new generator tests in `tests/specialists/generator/test_generator_pyproject_c3_row.py`. Migration-scoped target ≥175 passed / 2 skipped placeholder-key.
- **Floor:** ≥174 passed (169 + 5 floor); below this fails K-floor.
- **Import-linter:** 3/3 KEPT across the actual repo (5 manual rows from Slab 2a + 0 new rows from 2a.5 because 2a.5 doesn't itself generate a new specialist; auto-emit machinery is in place, not yet exercised against the live repo).
- **Ruff:** clean across modified files.
- **Sandbox-AC validator:** PASS on this story spec.

### Anti-flake discipline

- The `subprocess.run([...lint-imports...])` test (AC-2a.5-F) is the only test in this story that hits a subprocess seam. Pin `shell=False, timeout=30, capture_output=True, text=True, cwd=temp_repo_root` per the Texas 2a.4 G6 PATCH P7 precedent. If `import-linter` exits non-zero, the test fails with the captured stderr surfaced (do NOT use `--quiet` or `> /dev/null` — debugging needs the diagnostic output).

---

## Previous Story Intelligence

### From Story 2a.1 (Generator + 9-Node Scaffold Reference) — 2026-04-24

**Key lesson:** Atomic emission of the 9-file specialist tree is the existing contract (`_write_items_atomic` lines 237–280). 2a.5 extends the atomic unit to include `pyproject.toml`. **Reuse `_write_items_atomic`'s rollback machinery** — do not author a parallel rollback path; on pyproject failure, call back into the existing rollback for the 9 specialist files, then restore the pyproject backup.

**Key lesson:** The R9 atomicity test at `test_generator_four_file_atomicity_on_force.py` is the precedent for failure-injection testing. 2a.5's `test_atomic_rollback_on_pyproject_failure` mirrors that pattern — mock `Path.write_text` to raise on the pyproject step; assert post-failure state matches pre-run state.

### From Story 2a.2 (Irene Pass 2) — 2026-04-25

**Key lesson:** Irene was the first specialist to add the manual C3 row at `pyproject.toml:110`. Dev Agent Record T2 noted "manually appended C3 ignore_imports row per `langgraph-migration-guide.md §12.4` step 3 — generator does not auto-emit (deferred-inventory A12 path b)." This story is path b shipped.

### From Story 2a.3 (Kira motion) — 2026-04-25

**Key lesson:** Kira was the second specialist to add the row (`pyproject.toml:111`). Dev Agent Record reused Irene's pattern verbatim. Story 2a.3 G6 included the A12 procedural-coupling category lesson (Paige harvest at `specialist-anti-patterns.md §A12`).

### From Story 2a.4 (Texas pure-tool-dispatch) — 2026-04-25

**Key lesson:** Texas was the **third** specialist to add the row (`pyproject.toml:112`). Three-instance evidence threshold reached. The Slab 2a retrospective binding gate language ("do not let it become four") explicitly names 2a.5 as the gate-flip event. **Murat anti-padding K discipline holds even on a defect fix** — six test surfaces, not eight or twelve.

### From Story 1.4 (Manifest Loader + Compiler) — 2026-04-23

**Key lesson:** Contract C3 was authored at 1.4 with the mcp_server.tools.gate_decide ignore entry. The C3 block has been touched by every subsequent specialist landing; its append-only invariant is the load-bearing assumption 2a.5 codifies in the auto-emit machinery (we never RE-ORDER existing entries; we only APPEND new ones at the end).

---

## Git Intelligence Summary (recent Slab-2a commits for pattern reference)

- `0a02fa5` — Story 2a.4 BMAD-CLOSED + Slab 2a CLOSED. **Pattern:** dev agent manually edits `pyproject.toml:112` per `§12.4` step 3; generator does not auto-emit.
- `21a6e5f` — Story 2a.2 BMAD-CLOSED. **Pattern:** Irene's `pyproject.toml:110` manual edit; first instance of the procedural-coupling bug.
- (Story 2a.3 commit between) — Kira's `pyproject.toml:111` manual edit; second instance.
- `2a336df` (Slab 2a opening) — Story 2a.1 generator emit. **Pattern:** the `_write_items_atomic` factoring 2a.5 extends.

---

## Project Context Reference

### Pre-read memory entries

- [`memory/feedback_verify_via_shipped_deps.md`](../../../Users/juanl/.claude/projects/c--Users-juanl-Documents-GitHub-course-DEV-IDE-with-AGENTS-hybrid/memory/feedback_verify_via_shipped_deps.md) — sandbox-AC rule (no operator-side CLIs in dev-agent ACs)
- [`memory/feedback_venv_python_allowed.md`](../../../Users/juanl/.claude/projects/c--Users-juanl-Documents-GitHub-course-DEV-IDE-with-AGENTS-hybrid/memory/feedback_venv_python_allowed.md) — `.venv/Scripts/python.exe` is allowed for all projects; invoke without per-command permission prompts
- [`memory/project_upstream_severance.md`](../../../Users/juanl/.claude/projects/c--Users-juanl-Documents-GitHub-course-DEV-IDE-with-AGENTS-hybrid/memory/project_upstream_severance.md) — severance posture; hybrid is source of truth

### Post-story outputs

At 2a.5 close, the following downstream stories are unblocked:

- **Story 2b.1 (Gary TEMPLATE)** — first specialist whose generator invocation will populate `pyproject.toml` automatically; this is the **first live exercise** of the 2a.5 auto-emit machinery against the actual repo. 2b.1's T8 regression evidence will include an inspection of `pyproject.toml` showing the auto-emitted Gary row with comment marker.
- **Stories 2b.2–2b.14 (Slab 2b inheritors)** — same auto-emit path; each picks up one new C3 `ignore_imports` row per generation invocation.
- **Story 2c.1 (Wondercraft)** — same auto-emit path on the Wondercraft Path-A or Path-B emit.

---

## Dev Agent Record

_(Dev agent populates this section during T1–T9 execution.)_

### T1 Readiness

- Governance JSON check: `docs/dev-guide/migration-story-governance.json` confirms `2a-5` is `single-gate` with `rationale: null` (party-mode T2 2026-04-24 ratification).
- Sandbox-AC validator: `.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-2a-5-generator-auto-emit-pyproject-c3-row.md` → `PASS`.
- Three-instance evidence base: confirmed at `pyproject.toml:110` (Irene), `:111` (Kira), `:112` (Texas).
- Generator entry-point inspected: `skills/bmad_create_specialist/scripts/generate.py::generate_specialist` + `_write_items_atomic` factoring identified for atomic-rollback reuse.
- Existing test conftest fixtures inspected: `temp_repo_root` extended to include representative `pyproject.toml` + minimal import-linter contract stubs for parser-level C3 checks.
- A12 anti-pattern entry located at `docs/dev-guide/specialist-anti-patterns.md:114-118`; resolution path (b) is the binding language.
- Migration-guide §12.4 located; step 3 is the manual-edit step targeted for replacement.
- Deferred-inventory entry located at `_bmad-output/planning-artifacts/deferred-inventory.md:70` (table row "Generator auto-emit pyproject.toml C3 ignore_imports row (2a.1 follow-on defect)").

### T2–T7 Implementation Notes

- Implemented C3 auto-emit logic in `skills/bmad_create_specialist/scripts/generate.py`:
  - Added `_plan_pyproject_c3_mutation(...)` with exact-edge idempotency matching that ignores trailing comments/whitespace.
  - Added generated-row append shape:
    - `"app.specialists.<name>.graph -> app.gates.resume_api",  # generated by bmad-create-specialist for <name>`
  - Added clear fail-loud preflight errors for missing/malformed C3 block.
- Extended dry-run behavior:
  - No file mutations.
  - Dry-run plan notes now include `would append C3 ignore_imports row: ...` when applicable.
- Extended atomicity contract:
  - Specialist emission remains atomic via `_write_items_atomic`.
  - `pyproject.toml` mutation is now in the same atomic unit (mutation runs after 9-file write; on failure, specialist files roll back and pyproject content is restored from preflight snapshot).
- Added new regression module `tests/specialists/generator/test_generator_pyproject_c3_row.py` with 7 tests covering AC-A through AC-F surfaces.
- Updated generator fixture scaffold in `tests/specialists/generator/conftest.py` with representative `pyproject.toml` and minimal import-linter contract stubs.
- Updated docs and governance artifacts per AC-G/H/I/K/L:
  - `docs/dev-guide/langgraph-migration-guide.md` §12.4 step-3 replacement line.
  - `docs/dev-guide/specialist-anti-patterns.md` A12 counter-pattern annotated RESOLVED.
  - `_bmad-output/implementation-artifacts/slab-2a-retrospective.md` closing-note gate-flip line added.
  - `_bmad-output/planning-artifacts/deferred-inventory.md` FILED→CLOSED marker + count updates.
  - `_bmad-output/implementation-artifacts/sprint-status.yaml` story/epic close-state flips.

### T8 Regression Evidence

- `.venv\Scripts\python.exe -m pytest tests/specialists/generator/test_generator_pyproject_c3_row.py -q`
  - Result: `7 passed`
- `.venv\Scripts\python.exe -m pytest tests/specialists/generator -q`
  - Result: `51 passed`
- `.venv\Scripts\python.exe -m ruff check skills/bmad_create_specialist/scripts/generate.py tests/specialists/generator`
  - Result: clean
- `.venv\Scripts\python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-2a-5-generator-auto-emit-pyproject-c3-row.md`
  - Result: `PASS`
- Repo-level `lint-imports` post-change:
  - Result: `3 kept / 0 broken`

### G6 Layered Code-Review (Blind Hunter / Edge Case Hunter / Acceptance Auditor)

Single-gate review disposition:
- PATCH: none (all AC surfaces satisfied in first pass after regression fixes).
- DEFER: none (story scope is fully closed).
- DISMISS: none (no out-of-scope findings from this slice).

### D12 Close Stub

1. **Invariant preservation:** Generator 9-file emission contract preserved; atomic rollback extended to include `pyproject.toml`; import-linter remains 3/3 KEPT before/after; repo `pyproject.toml` remains at 5 rows post-close because 2a.5 introduces machinery, not a new specialist row.
2. **Anti-pattern harvest:** A12 entry updated per AC-2a.5-H. No new entry filed.
3. **Migration-guide update:** §12.4 updated per AC-2a.5-G; Slab 2a retrospective Closing note updated per AC-2a.5-I.

### Completion Notes

- Story closed under single-gate path with all AC-A through AC-L complete.
- Auto-emit behavior is now active for future specialist generations; manual C3 row edits are retired from the checklist.
- Slab 2a reopened-epic tail debt is now closed; `migration-epic-2a-slab-2-scaffold-pilot` returned to `done`.

### File List

- NEW:
  - `tests/specialists/generator/test_generator_pyproject_c3_row.py`
- MODIFIED:
  - `skills/bmad_create_specialist/scripts/generate.py`
  - `tests/specialists/generator/conftest.py`
  - `docs/dev-guide/langgraph-migration-guide.md`
  - `docs/dev-guide/specialist-anti-patterns.md`
  - `_bmad-output/implementation-artifacts/slab-2a-retrospective.md`
  - `_bmad-output/planning-artifacts/deferred-inventory.md`
  - `_bmad-output/implementation-artifacts/sprint-status.yaml`
