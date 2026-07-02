# ADDENDUM — carried-findings a-batch witness (appended 2026-07-02, remediation batch)

Appended per the carried-findings remediation work order (R5), party record
`carried-findings-remediation-greenlight-party-record-2026-07-02.md`.
Branch: `dev/carried-findings-enum-refresh-2026-07-02`.

## (i) A1 current-color-at-HEAD statement (restated)

`tests/marcus_capabilities/test_pr_rc.py::test_pr_rc_normalizes_halt_fixture`
**failed at HEAD** with `assert 125.0 == 135.0` (parsed fixture value 125.0 vs
the sweep-corrupted pin 135.0) — the dev ran it at HEAD before any edit; this
restates that observed color. The pin was reverted `135.0` → `125.0` this
session (working tree), restoring the true Story-era value; the sibling
`mutation-witness-130-red.txt` in this directory separately proves the test's
teeth (fixture mutated to 130.0 → RED `assert 130.0 == 125.0`).

## (ii) 195be7c9 audit result table

Audit of every hunk in `195be7c9` (s2-marcus-collapse Phase-5/6/7,
2026-05-07). Its commit message documents a genuine import-linter
contract-count `12 -> 13` sweep ("6 import-linter contract count tests:
12 -> 13 contracts kept") plus string-literal `marcus.X` -> `app.marcus.X`
edits, and disclaims semantics changes. The `12x` -> `13x` numeric sweep
**substring-over-matched** three unrelated numeric pins (collateral victims):

| # | File / pin | Corruption | Status |
|---|---|---|---|
| 1 | `tests/marcus_capabilities/test_pr_rc.py` — `motion_budget.max_credits` pin | `125.0` -> `135.0` (the `12`->`13` sweep matched the `12` inside `125`) | **FIXED** (a-batch; reverted to `125.0`; RED-at-HEAD + mutation witness in this directory) |
| 2 | `tests/test_marcus_facade_roundtrip.py:74` — unique-instance count pin | `128` -> `138` (impossible pin: test spawns `range(128)`) | **FIXED** (this remediation batch; RED `assert 128 == 138` captured, reverted to `128`, GREEN; adjudicated in `contracts-triage-ledger-2026-07-02.md` Appendix row A1) |
| 3 | `tests/test_structural_walk.py:421` — `sequence_doc_parity_specs` count pin | `12` -> `13` (real count is 12; the in-file enumerating comment lists exactly 12) | **FIXED** (this remediation batch; RED `assert 12 == 13` captured, reverted to `12`, GREEN; ledger Appendix row A2) |

**Facade-surface weakening note (same commit, distinct from the numeric
sweep):** `tests/contracts/test_marcus_facade_is_public_surface.py` had its
exact-tuple pin `tuple(marcus.__all__) == ("get_facade",)` replaced by a
weaker presence check `callable(getattr(marcus_pkg, "get_facade", None))` —
an intentional-looking post-S2 rewrite ("no longer a pure shim"), but it is a
contract-strength reduction (exact public-surface pin -> existence check)
recorded here for auditor visibility.

**All other hunks conforming:** the remaining `195be7c9` test-file edits were
verified as conforming string edits (`marcus.X` -> `app.marcus.X` path/import
literals) and the six genuine import-linter contract-count `12 -> 13` bumps
its message documents. No further collateral numeric-pin victims found.
