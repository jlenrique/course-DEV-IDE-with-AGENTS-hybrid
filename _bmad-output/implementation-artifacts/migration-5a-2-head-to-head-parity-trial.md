# Migration Story 5a.2: Head-to-Head Parity Trial vs Primary

**Status:** ready-for-dev
**Sprint key:** `migration-5a-2-head-to-head-parity-trial`
**Epic:** Slab 5a — M5 acceptance gate.
**Pts:** 5 | **Gate:** dual (per governance JSON `5a-2.expected_gate_mode = "dual-gate"`, rationale: `operator_acceptance_gate`). **K-target:** ~1.3× (target 12 / floor 9).

**Predecessor:** 5a.1 done. Drafted-for-queue.

---

## T1 Readiness Block

1. Governance: `5a-2.expected_gate_mode = "dual-gate"` (operator_acceptance_gate).
2. **Substrate:** primary-repo trial reference set — `_bmad-output/parity-baselines/` directory state at T1 (likely doesn't exist; 5a.2 may need to fetch from upstream/master @ 3ed7c56 frozen reference).
3. **Trial corpus** — operator supplies same input content that primary used (e.g., `C1-M1-PRES-20260419B`); pin location at T1.
4. **§01-§15 pipeline** stable per pipeline-manifest.yaml + Slab 4 close.
5. **LangSmith trace capture** — Slab-2/3 spans wired; trace export tooling per FR42 (4.3 close).
6. **Marcus-envelope baseline** from 3.6 W-R7 captured at `tests/fixtures/marcus/baseline_envelope/<YYYY-MM-DD>/`.
7. **Texas AC-B-OP live** evidence from 3.6 (or DEFERRED state from 2c.4 hard-gate inheritance — verify M2 + M3 verdict states).
8. **Side-by-side artifact comparison tooling** — likely shipped per 2c.1 diff-evidence Markdown precedent (`git diff --no-index --no-color` + structural-match scoring).
9. **5-agent party-mode roster** pinned (Winston + Murat + Paige + Quinn-R + Amelia per 2c.3 + 3.6 + 4.7 inheritance).
10. Severance posture (upstream/master @ 3ed7c56 frozen reference; primary trial baselines mined from frozen ref, NOT live forward-port).

### TEMPLATE scope decisions

**Decision #1 — Bounded scope:** (a) operator runs same input content through clone producing new tracked trial `C1-M1-PRES-<clone-date>`; (b) artifacts produced at §01→§15; (c) LangSmith trace captures every node; (d) side-by-side artifact comparison vs primary-repo baseline; (e) per-artifact parity-or-better judgment recorded; (f) divergence rationale captured in M5 Required Evidence; (g) party-mode multi-persona review (5-agent per Decision #4); (h) consensus GREEN/YELLOW/RED recorded with rider findings. NOT in scope: economics measurement (5a.3); invariant audit (5a.4); ship verdict (5a.5).

**Decision #2 — Primary baseline source:** mine from upstream/master @ 3ed7c56 frozen reference per MEMORY.md `project_upstream_severance` (NOT live forward-port). Operator provides path to primary trial artifact set; if absent, AC-A halts pre-trial.

**Decision #3 — Side-by-side comparison methodology (mirror 2c.1 AC-C two-tier per Murat M-R2-2c.1):** TIER 1 = file-presence ≥80% (clone produces same artifact set); TIER 2 = structural-match ≥60% on files-in-both-trees (per-line semantic match excluding timestamps/UUIDs/run-IDs). Diff-evidence artifact at `_bmad-output/implementation-artifacts/5a-2-parity-evidence-<clone-date>.md`.

**Decision #4 — 5-agent party-mode (mirror 2c.3 + 3.6 + 4.7):** Winston + Murat + Paige + Quinn-R + Amelia. Per-agent verdict-token-on-its-own-line + 150-char body. Consensus 4-enum (GREEN/YELLOW/RED + GREEN-WITH-RIDERS); per-agent 6-enum (adds ABSTAIN).

---

## Story

As an **operator validating migration MVP bar per FR52**,
I want **a new tracked trial run `C1-M1-PRES-<clone-date>` produced in the clone against the same input content as a primary-repo trial + side-by-side artifact comparison + party-mode multi-persona review with consensus verdict**,
So that **FR52 is met + M5 operator sign-off has evidence base**.

---

## Acceptance Criteria

### AC-5a.2-A — Trial run + LangSmith trace capture

- **Given** primary trial baseline located at T1; operator-supplied input content path
- **When** operator runs the clone trial via CLI: `app.marcus.cli trial start --preset production --input <corpus-path>`
- **Then** §01→§15 executes; new tracked trial `C1-M1-PRES-<clone-date>` registers; LangSmith trace captures every node.
- **Test pin:** N/A (operator-driven E2E; evidence in Dev Agent Record §T8 trial-run log + final RunState fixture per 3.6 AC-A precedent).

### AC-5a.2-B — Side-by-side artifact comparison per Decision #3 two-tier (DUAL-GATE acceptance gate-1)

- **Given** primary baseline + clone trial both complete
- **When** the dev agent (or operator) runs comparison tooling
- **Then** diff-evidence Markdown produced at `_bmad-output/implementation-artifacts/5a-2-parity-evidence-<clone-date>.md` with TIER 1 (file-presence ≥80%) + TIER 2 (structural-match ≥60%) scores; per-artifact parity-or-better verdict; divergence rationale per file.
- **Test pin:** `tests/migration/test_5a_2_parity_evidence_present.py` — 1 test asserting evidence file exists + 2 required §-headers (Tier 1 / Tier 2) + score regex matches numeric ≥ thresholds.

### AC-5a.2-C — 5-agent party-mode parity verdict (Decision #4; mirror 2c.3+3.6+4.7)

- **Given** parity evidence assembled per AC-B
- **When** dev convenes 5-agent party-mode with prompt: "M5 head-to-head parity verdict review for clone trial vs primary baseline. Full evidence: §01-§15 trial output + LangSmith trace + 5a-2-parity-evidence Markdown. Verdict (one of 6 per-agent enum): GREEN-LIGHT / GREEN-WITH-RIDERS / CONDITIONAL-GREEN / YELLOW / RED / ABSTAIN. Roster fixed at 5 (Winston + Murat + Paige + Quinn-R + Amelia)."
- **Then** verbatim per-agent recording at `_bmad-output/implementation-artifacts/5a-2-parity-verdict.md` mirroring 2c.3 + 3.6 + 4.7 pattern; 4-enum consensus.
- **Test pin:** `tests/migration/test_5a_2_party_mode_5_agent_recording.py` — 1 test (mirror 3.6 AC-F + 4.7 AC-C structural assertion).

### AC-5a.2-D — Anti-pattern catalog harvest

NO new entries expected; if parity-pattern surfaces (e.g., "structural-match scoring weighted incorrectly across artifact types"), file as candidate per harvest-gate.

### AC-5a.2-E — TEMPLATE compliance

R1, R6, R8 honored.

### AC-5a.2-F — D12 close protocol (DUAL-gate; operator_acceptance_gate; FIVE-line)

1. Invariant preservation: FR52; trial reproducibility against frozen primary baseline.
2. Anti-pattern harvest: N/A unless surfaced.
3. Migration-guide update: §"Head-to-Head Parity" added.
4. TEMPLATE compliance: R1, R6, R8.
5. Dual-gate gate-2 (operator parity-acceptance review).

### AC-5a.2-G — Sprint-status state-flips at filing AND close.

---

## File Structure Requirements

### NEW files

- `_bmad-output/implementation-artifacts/{5a-2-parity-evidence-<clone-date>, 5a-2-parity-verdict}.md`
- `app/replay/parity_comparison.py` (callable for two-tier scoring per Decision #3)
- `tests/migration/{test_5a_2_parity_evidence_present, test_5a_2_party_mode_5_agent_recording}.py`

### MODIFIED files

- `_bmad-output/implementation-artifacts/sprint-status.yaml` — per AC-G.
- `docs/dev-guide/langgraph-migration-guide.md` — §"Head-to-Head Parity" added.

---

## Testing Requirements

**K-target ~1.3× (target 12 / floor 9).** AC-A:0 (operator-driven) + AC-B:1 + AC-C:1 = **2 K-floor**. RIDER: parity_comparison.py unit tests — file-presence scoring + structural-match scoring + per-artifact divergence-rationale-generation = +6 (3 orthogonal properties × 2 fixture variants → 3 parametrize-collapse units + 3 distinct property assertions); + AC-B 2-enum-tier parametrize → +2 = honest **9 K-floor (meets floor)**.

Sandbox-AC PASS.

---

## Dev Agent Record

_(Populated during T1–T9 execution.)_

### Operator Trial-Run Evidence (per AC-A)

_(Operator pastes here)_

### 5-Agent Party-Mode Parity Verdict (per AC-C)

_(Recorded verbatim under ### Winston / ### Murat / ### Paige / ### Quinn-R / ### Amelia headers in 5a-2-parity-verdict.md)_
