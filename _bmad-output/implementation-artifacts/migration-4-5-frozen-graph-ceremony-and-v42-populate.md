# Migration Story 4.5: Frozen-Graph-Version Ceremony Doc + v42 Populate + Bump Policy

**Status:** ready-for-dev
**Sprint key:** `migration-4-5-frozen-graph-ceremony-and-v42-populate`
**Epic:** Slab 4 — M4 gate.
**Pts:** 3 | **Gate:** single (per governance JSON `4-5.expected_gate_mode = "single-gate"`, rationale: null). **K-target:** ~1.2× (target 8 / floor 7).

**Predecessor:** 4.1 + 4.2 + 4.3 + 4.4 done. Drafted-for-queue.

---

## T1 Readiness Block

1. Governance: `4-5.expected_gate_mode = "single-gate"`.
2. **Substrate: `runtime/graphs/v42/`** — Slab-1 stub per epic 4.5 wording; verify at T1.
3. **`docs/dev-guide/frozen-graph-version-ceremony.md`** — does NOT exist; 4.5 authors.
4. **D8 Tier-1/2/3 bump policy** — architecture decision-of-record D8; verify in `architecture-langchain-langgraph-migration.md`.
5. **Pack-version policy precedent** — CLAUDE.md §"Pipeline lockstep regime" §"Pack version bumps are governance, not technical" already codifies Tier-1/2/3 for packs; 4.5 extends to frozen-graph-version.
6. **Compiled-graph-digest** — SHA-256 of compiled StateGraph introspection per epic AC.
7. **Dispatch-registry-snapshot interim** — 2b.15 dispatch-registry-hardening shipped `_status: interim`; 4.5 references this snapshot, M5 reconciles per `slab-3-m5-dispatch-registry-swap` deferred-inventory entry.
8. Severance posture.

### Substrate sweep

- `runtime/graphs/v42/` — verify presence + current contents.
- `state/config/dispatch-registry.yaml` — 2b.15 substrate `_status: interim` (verified 2026-04-25 per Slab-2b close).
- `pipeline-manifest.yaml` per 4.1 substrate-aware adaptation.
- `dev-graph-manifest.yaml` per 4.2 close.

### TEMPLATE scope decisions

**Decision #1 — Bounded scope:** (a) `docs/dev-guide/frozen-graph-version-ceremony.md` codifying Tier-1/2/3 bump policy + worked examples (v42→v42.1 + v42→v43) + rollback procedure; (b) `runtime/graphs/v42/` populated with manifest-snapshot + dev-graph-manifest-snapshot + pack-version + dispatch-registry-snapshot (interim) + compiled-graph-digest; (c) digest stability test. NOT in scope: M5 dispatch-registry swap (deferred to `slab-3-m5-dispatch-registry-swap` entry); sanctum hook (4.6).

**Decision #2 — Tier-1/2/3 policy alignment with pack-version policy:** Tier-1 = patch (prose/connective-tissue; dev-agent authority gated by Cora's block-mode hook); Tier-2 = minor (new pipeline step / new node; party-mode consensus); Tier-3 = major (new pack family / structural reshape; party-mode consensus + version bump in architecture doc). Policy doc cross-references CLAUDE.md §"Pipeline lockstep regime" §"Pack version bumps are governance, not technical."

**Decision #3 — Compiled-graph-digest stability across runs:** SHA-256 of canonical-JSON serialization of compiled StateGraph introspection (node IDs sorted lexically + edge tuples sorted lexically + manifest schema_version + pack-version). Test asserts byte-identical digest across re-compiles of same manifest.

---

## Story

As a **governance author of reproducibility discipline per FR43+FR44**,
I want **`docs/dev-guide/frozen-graph-version-ceremony.md` codifying Tier-1/2/3 bump policy + `runtime/graphs/v42/` populated + compiled-graph-digest stable across runs**,
So that **FR43+FR44 are met and D8 ceremony is first-class documentation for M4 close + Slab-5a invariant audit**.

---

## Acceptance Criteria

### AC-4.5-A — `docs/dev-guide/frozen-graph-version-ceremony.md` authored

- **Given** doc does NOT exist
- **When** dev authors with Tier-1/2/3 policy per Decision #2 + worked v42→v42.1 example + worked v42→v43 example + rollback procedure
- **Then** doc ≥80% of the outline; cross-references from `docs/dev-guide/langgraph-migration-guide.md` §7 added.
- **Test pin:** `tests/migration/test_frozen_graph_ceremony_doc_present.py` — 1 test asserting file exists + ≥4 required §-headers (Tier-1/2/3 / v42→v42.1 example / v42→v43 example / Rollback).

### AC-4.5-B — `runtime/graphs/v42/` populated per epic AC

- **Given** v42/ stub state per Slab-1
- **When** dev authors:
  - `runtime/graphs/v42/manifest-snapshot.yaml` (snapshot of current pipeline-manifest.yaml)
  - `runtime/graphs/v42/dev-graph-manifest-snapshot.yaml` (snapshot of current dev-graph-manifest.yaml from 4.2)
  - `runtime/graphs/v42/pack-version.txt` (e.g., `v4.2.0`)
  - `runtime/graphs/v42/dispatch-registry-snapshot.yaml` (interim snapshot per 2b.15 `_status: interim`; M5 reconciles)
  - `runtime/graphs/v42/compiled-graph-digest.txt` (SHA-256 hex)
- **Then** all 5 artifacts present + digest is stable across runs.
- **Test pin:** `tests/migration/test_v42_artifacts_present.py` — 1 test asserting all 5 artifacts exist + non-empty.

### AC-4.5-C — Compiled-graph-digest stability test

- **Given** `compute_compiled_graph_digest(manifest_snapshot, pack_version, dispatch_registry_snapshot) -> str` per Decision #3
- **When** invoked twice against the same manifest snapshot
- **Then** digest byte-identical across runs
- **Test pin:** `tests/migration/test_compiled_graph_digest_stable.py` — 2 tests (parametrize-collapsible to 1): same-input → same-digest + different-input → different-digest.

### AC-4.5-D — Anti-pattern catalog harvest

NO new entries expected.

### AC-4.5-E — TEMPLATE compliance

R1, R6, R8 honored.

### AC-4.5-F — D12 close protocol (single-gate; FOUR-line)

1. Invariant preservation: FR43+FR44 met; D8 ceremony first-class.
2. Anti-pattern harvest: N/A.
3. Migration-guide update: §7 (Frozen-Graph Ceremony) added.
4. TEMPLATE compliance: R1, R6, R8.

### AC-4.5-G — Sprint-status state-flips.

---

## File Structure Requirements

### NEW files

- `docs/dev-guide/frozen-graph-version-ceremony.md`
- `runtime/graphs/v42/{manifest-snapshot, dev-graph-manifest-snapshot, dispatch-registry-snapshot}.yaml + pack-version.txt + compiled-graph-digest.txt`
- `app/runtime/compiled_graph_digest.py` — `compute_compiled_graph_digest()` callable
- `tests/migration/{test_frozen_graph_ceremony_doc_present, test_v42_artifacts_present, test_compiled_graph_digest_stable}.py`

### MODIFIED files

- `docs/dev-guide/langgraph-migration-guide.md` — §7 cross-references.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — per AC-G.

---

## Testing Requirements

**K-target ~1.2× (target 8 / floor 7).** AC-A:1 + AC-B:1 + AC-C:2 parametrize → 1 = **3 K-floor**. RIDER: AC-A doc-content assertion (≥4 §-headers; required-content regex per Tier-1/2/3 enum) → +1; AC-B per-artifact orthogonal property (5 artifacts → 5 distinct properties; parametrize-collapse OK to 1 K-floor since same property "exists + non-empty") + AC-B-rider for digest-format-pin test → +1; AC-C different-input-different-digest → +1; total honest **6 K-floor**. Below floor 7. Operator may recalibrate to ~1.0× (target 6 / floor 5) at story-open OR add `test_pack_version_text_format` orthogonal property to reach floor 7.

Sandbox-AC PASS.

---

## Dev Agent Record

_(Populated during T1–T9 execution.)_
