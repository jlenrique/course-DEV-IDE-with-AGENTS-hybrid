# Slab 6.1 close — six deferred-inventory entries (ready to paste)

**Purpose:** ready-to-paste Markdown blocks for `_bmad-output/planning-artifacts/deferred-inventory.md` §"Named-But-Not-Filed Follow-Ons" table. Codex (or operator) pastes at Slab 6.1 formal close.

**Source authority:** `_bmad-output/implementation-artifacts/6-1-code-review-2026-04-27.md` (DFR-6.1-1 through DFR-6.1-5) + Slab 6.1 patch dispatch DN-1 deferral.

**Six entries to file:**

---

### Entry 1 — `migration-6-2-promote-dependency-map-into-manifest`

```markdown
| **`migration-6-2-promote-dependency-map-into-manifest`** | Slab 6.1 bmad-code-review DFR-6.1-1 (AA-2) | Slab 6.1 ships with runner-layer deterministic fallback at `_default_dependency_map_for(specialist_id)` (Texas → CD = `source_bundle`; other downstream = `upstream_output`). v4.2 pipeline manifest does not yet declare dependency input keys per specialist node; promotion to manifest is the Slab 6 trial-experience bundle prerequisite to keep specialist evolution clean. Operator-ratified deferral 2026-04-27 to keep Slab 6.1 close tight. | **Tier A prerequisite, ~1pt single-gate.** Promote `dependency_map` declaration into `state/config/pipeline-manifest.yaml` per-node entry; preserve runner-layer fallback as the resolution mechanism for nodes that don't declare keys (backward-compatible). Update Composition Spec §3.6 to reflect manifest-as-source-of-truth post-landing. Reactivate immediately after Slab 6.1 formal close; lands BEFORE Slab 6 trial-experience bundle implementation per `codex-handoff-slab-6-3-through-6-5-trial-experience-bundle.md` Phase 0 prerequisite. |
```

---

### Entry 2 — `slab-6-1-multi-pass-envelope-path-x-or-y`

```markdown
| **`slab-6-1-multi-pass-envelope-path-x-or-y`** | Slab 6.1 bmad-code-review DFR-6.1-2 (EC-2 / AA-3) | `ProductionEnvelope.add_contribution` enforces immutability invariant (one contribution per `specialist_id`). Manifest topology can have repeated specialist nodes (e.g., Irene Pass 1 + Irene Pass 2). Slab 6.1 ships with Path Z ("first contribution wins"; duplicate specialist contributions skipped after first; explicit + logged per bmad-code-review patch P-4). Operator-ratified Path Z 2026-04-27. Path X (node-scoped contribution identity: `<specialist>:<node_index>`) and Path Y (per-pass envelope) are filed as enhancement candidates. | **Substrate enhancement, scope TBD per chosen path.** Reactivate when actual multi-pass production need emerges in trial work — e.g., Irene Pass 1 + Pass 2 both in production manifest; OR specialist back-catalog grows to include genuinely repeated nodes. At reactivation: convene party-mode round to choose Path X vs Path Y; Path X requires envelope schema_version bump (production-envelope.v1 → v2); Path Y requires per-pass-envelope architecture decision. See Composition Spec §3.1 + §10 Decision Log + §12 known limitation #7. |
```

---

### Entry 3 — `replay-regression-pack-hash-drift-pre-slab-6.1`

```markdown
| **`replay-regression-pack-hash-drift-pre-slab-6.1`** | Slab 6.1 bmad-code-review DFR-6.1-3 (AA-7) + N7 trace | Pre-existing pack-hash drift (`013b7ef → 19cde78`) in replay-regression suite + diffs in override confirm token / cost fields. Drift is unrelated to Slab 6.1 rewire (per Codex finding; verified at code review). Replay sweep timed out at 124s during review attempt; no Slab 6.1-specific replay failure set established. Operator-ratified deferral 2026-04-27. | **Investigation, ~2-3pt.** Investigate pack-hash drift root cause; likely needs golden refresh after Slab 6.0 substrate landed but before 6.1 rewire. Re-run replay sweep with extended timeout (or break into chunks) to establish stable failure set; refresh golden baselines per finding; restore replay-regression to GREEN state. Reactivate when next replay-regression failure surfaces in trial work OR scheduled tech-debt cleanup pass. |
```

---

### Entry 4 — `slab-6-1-runner-compiled-edge-traversal`

```markdown
| **`slab-6-1-runner-compiled-edge-traversal`** | Slab 6.1 bmad-code-review DFR-6.1-4 (EC-6) | Production runner currently iterates manifest order, ignoring compiled graph edges. Current v4.2 manifest is linear so this is not blocking at Slab 6.1 close. Required before non-linear branch/conditional production manifests are used. | **Substrate enhancement, ~2-3pt.** Wire production runner to consume compiled graph edges (from `compile_run_graph(...)`) rather than iterating manifest order; add execution-path assertions covering branch/conditional traversal; chain test exercises a non-linear specialist topology. Reactivate when first non-linear manifest topology lands in production OR when v4.3 pack family introduces conditional traversal patterns. See Composition Spec §12 known limitation #8. |
```

---

### Entry 5 — `production-trial-envelope-lifecycle-invariants`

```markdown
| **`production-trial-envelope-lifecycle-invariants`** | Slab 6.1 bmad-code-review DFR-6.1-5 (EC-7) | `ProductionTrialEnvelope` permits impossible lifecycle states; cross-field validators for `completed_at` / `paused_gate` / `cost_report_path` state matrix are absent. Pre-existing issue not introduced by Slab 6.1 rewire. | **Test discipline + schema hardening, ~1-2pt.** Add Pydantic v2 cross-field validators to `ProductionTrialEnvelope`: (a) `completed_at` set XOR `paused_gate` set (cannot be both); (b) `cost_report_path` required if `completed_at` set; (c) `paused_gate` requires associated checkpoint state pointer; (d) state-machine transition tests covering all valid + invalid transitions. Four-file-lockstep: model + JSON Schema regen + golden refresh + new shape-pin tests. Reactivate when first lifecycle-state-confusion incident surfaces in trial OR scheduled tech-debt cleanup pass. See Composition Spec §3.7 + §12 known limitation #9. |
```

---

### Entry 6 — `slab-6-1-langsmith-runner-trace-id-real-binding`

```markdown
| **`slab-6-1-langsmith-runner-trace-id-real-binding`** | Slab 6.1 bmad-code-review DN-1 (AA-5 / EC-5) — operator-ratified deferral 2026-04-27 | Cost rollup works correctly (per-call cost from LangChain runtime is real; live smoke confirmed `total_cost_usd = 0.0325215` from real OpenAI invocation). Deficit is at runner-aggregation level: `ProductionTrialEnvelope.trial_trace_id` records a synthetic placeholder rather than fetching the real LangSmith trace ID. Real specialist invocations DO emit real LangSmith spans with `extra.metadata.trial_id == <trial_id>` propagated correctly. Operator workaround acceptable for bounded-MVP: query LangSmith manually for spans with the trial_id metadata to find the real trace tree. | **LangSmith client wiring, ~2-3pt.** Wire `measure_trial_cost(trial_id)` (or equivalent) to perform live LangSmith fetch at trial close; bind real trace ID into `ProductionTrialEnvelope.trial_trace_id`; preserve synthetic placeholder as fallback for offline mode. Likely needs retry/backoff for LangSmith ingestion latency. N8 trace upgrades from PASS-WITH-GAP to clean PASS at landing. Reactivate when first trial reveals operator-friction on the manual trace-ID workaround OR when audit-trail completeness becomes load-bearing for stakeholder review (e.g., compliance audit; investor demo; etc.). See Composition Spec §3.7 + §12 known limitation #6. |
```

---

## Filing protocol at Slab 6.1 formal close

1. Open `_bmad-output/planning-artifacts/deferred-inventory.md`
2. Locate the §"Named-But-Not-Filed Follow-Ons" table (around line 42-114 per pre-Slab-6.1 state)
3. Append the six rows above in order
4. Update the table-footer counter line: "Total named follow-ons: 45 filed; 3 resolved 2026-04-27" → "Total named follow-ons: 51 filed; 3 resolved 2026-04-27 (+ Slab 6.1 close 2026-04-XX adds 6 entries: migration-6-2-promote-dependency-map-into-manifest + slab-6-1-multi-pass-* + replay-regression-pack-hash-drift-* + slab-6-1-runner-compiled-edge-traversal + production-trial-envelope-lifecycle-invariants + slab-6-1-langsmith-runner-trace-id-real-binding)" (adjust the final counts to actual totals)
5. Update the file header `Last refreshed:` line to the close date
6. Commit as `chore(slab-6.1-close): file 6 deferred-inventory entries per bmad-code-review triage + DN-1 deferral`

After this paste, also flip the existing `5a-2-production-graph-entrypoint-substrate-gap` entry from DEFERRED-CONTINUES to RESOLVED-2026-04-XX per Slab 6.1 formal close protocol (this is a separate edit on a different row).
