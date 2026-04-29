# Operator-Control Parity Inventory — Template

**Audience:** dev agents authoring per-specialist operator-control inventory at story-T1 readiness. One filled instance of this template MUST exist for each Slab 7b body-activation specialist before that specialist's class enters dev (per FR104 + FR110 + R5 Winston amendment).

**Authority:** Slab 7b foundational artifact (FR110). Authored 2026-04-29.

**Output path convention:** `_bmad-output/implementation-artifacts/operator-control-inventory-<specialist_name>.md` (one file per specialist; created at story-T1; refined through story close).

---

## How to use this template

1. Copy this template to `_bmad-output/implementation-artifacts/operator-control-inventory-<specialist_name>.md`.
2. Fill in the header: specialist name + class designation + story ID.
3. Walk the legacy v4.2 prompt pack (`docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`) for every operator-control lever that gates this specialist's behavior. Record each in §"Legacy levers (input)".
4. For each legacy lever, identify the migrated counterpart on the LangGraph runtime + record in §"Migrated levers (output)".
5. Document any back-compat shims in §"Back-compat shim status".
6. Pin the end-to-end test that asserts each migrated lever changes specialist behavior. Pointers in §"End-to-end test pointer".
7. Use §"Notes / deviations" only when the table-form doesn't capture a quirk.

The reviewer at story-close consumes this inventory verbatim against the specialist's chain-test PR (NFR-CG14). Drift between inventory + chain-test = HALT.

---

# [Filled instance starts here]

**Specialist:** `<specialist_name>` (e.g., `texas`, `gary`, `irene`)
**Class:** `<A | B | C | C+ | D1 | D2>` (per Slab 7b PRD D14 taxonomy)
**Story:** `<story-id>` (e.g., `7b.1-texas-hardening`)
**Authored at:** `<YYYY-MM-DD>` (ISO date; T1 readiness timestamp)
**Last updated at:** `<YYYY-MM-DD>` (refresh through story close)

---

## §"Legacy levers (input)"

Operator-control inputs that gate this specialist's behavior on the legacy v4.2 runtime. One row per lever.

| Lever | Type | Default | Pre-7b path / file | Source-of-truth (legacy v4.2 prompt pack section) |
|---|---|---|---|---|
| `<lever_name>` | env-var \| CLI-flag \| config-file-key \| sidecar-override | `<value>` | `<path>` | `<§N.N reference>` |

Repeat row per lever. If specialist has no operator-control levers (rare; almost every specialist has at least implicit ones via Marcus's directive payload), state explicitly: *"This specialist has no legacy operator-control levers; configuration is solely via Marcus's directive envelope."*

## §"Migrated levers (output)"

Operator-control levers on the migrated LangGraph runtime that map to legacy levers.

| Migrated lever | Type | Maps to legacy lever | Behavior delta (legacy → migrated) | Migrated path / file |
|---|---|---|---|---|
| `<migrated_lever_name>` | env-var \| CLI-flag \| config-file-key \| state-key \| directive-payload-field | `<legacy_lever_name>` | `<text describing semantic change, if any>` | `<path>` |

If a legacy lever has NO migrated counterpart, that's a **gap** to flag in §"Notes / deviations" + report to story author for either (a) restoring the lever, or (b) documenting why the lever is dropped (essential-function preservation under different mechanism per CLAUDE.md SG-2 framing).

## §"Back-compat shim status"

For each migrated lever, the back-compat shim status. Used to track legacy invocation patterns the migrated runtime still accepts.

- [ ] **Live shim** at `<path>` — legacy invocation accepted; documented sunset date `<YYYY-MM-DD>`
- [ ] **Sunset** as of `<YYYY-MM-DD>` — legacy invocation rejected with operator-readable error; remediation pointer to migrated lever
- [ ] **N/A** — no shim needed; legacy lever directly mapped to migrated counterpart

## §"Coverage status"

Per-lever PASS/PARTIAL/MISSING tag for aggregation. Allows Cora's parity test (NFR-I-substrate-floor) to aggregate per-specialist inventory artifacts without re-parsing prose.

| Lever | Coverage | Rationale |
|---|---|---|
| `<lever_name>` | PASS \| PARTIAL \| MISSING | `<short text; required if PARTIAL/MISSING>` |

## §"End-to-end test pointer"

Each migrated lever MUST have an end-to-end test asserting the lever changes specialist behavior. Test pointer convention:

- **File:** `tests/parity/test_<specialist_name>_activation_contract.py`
- **Test:** `test_<lever_name>_changes_behavior` (or class-shaped equivalent per FR105 NFR-I10 + R5 Winston amendment)

| Migrated lever | Test pointer |
|---|---|
| `<migrated_lever_name>` | `tests/parity/test_<specialist_name>_activation_contract.py::test_<lever_name>_changes_behavior` |

If the test does not yet exist (T1-readiness state), pointer reads `<not-yet-authored>` with target file path; updated to actual test ID at story close.

## §"Notes / deviations"

Free-prose section (10-15 lines max) for the rare case where a specialist has a quirk that doesn't fit the table-form. Examples:

- **Texas** retrieval: configuration is via `directive.yaml` (Marcus-composed; Texas does not consume env-var levers directly). All "legacy levers" are actually directive-payload fields. Document the directive-payload schema as the lever inventory.
- **Gary** Gamma API: rate-limit budget per NFR-CG20 lives in `app/specialists/gary/config.yaml`, not as an operator env-var. Document config-file-key shape rather than env-var prose.
- **Compositor (Class D2)**: pipeline-greenfield; legacy levers don't apply (no pre-7b Compositor existed). Inventory documents *intended* operator-control surface for the deterministic pipeline (e.g., `--strict-determinism` CLI flag) rather than legacy→migrated mapping.

This section is the safety valve; do NOT use it to dodge the table-form. If a specialist has 5+ levers that don't fit the table, that signals the template needs amendment — file a follow-on in deferred-inventory.

---

## Status field (closing the inventory)

At story close, the inventory header is amended:

```
**Inventory status:** ratified (story <story-id> closed <YYYY-MM-DD>)
**Reviewed by:** [reviewer agent ID + date]
**Aggregation status:** rolled into `docs/operator/legacy-vs-langgraph-control-parity.md` row <N>
```

The Slab 7b integration story (Wave 6) consumes all 11 ratified inventories + assembles them into the operator-control parity table extension (FR104).
