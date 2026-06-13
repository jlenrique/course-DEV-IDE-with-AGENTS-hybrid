---
title: 'Taxonomy re-base — live-path classes (gary/texas/kira/vera) + gary fabricated-roster kill + ninth-seam regex widening'
type: 'bugfix'
created: '2026-06-12'
status: 'done'
baseline_commit: 'e9edc61'
checkpoint_1: 'approved via operator standing directive ("go ahead with the rebase now"; push-after-remediation pattern established this session)'
context:
  - '{project-root}/_bmad-output/planning-artifacts/deferred-inventory.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Five tagged error classes on the live trial path are bare `RuntimeError`s — `GaryActError`, `ReceiptParseError` (gary), `BundleParseError` (texas), `KiraActError` (kira), `FTRParseError` (vera). Any raise mid-walk kills the process and loses paid work instead of error-pausing recoverably (the cycle-5 crash class; rider `tagged-error-taxonomy-systematic-rebase`). Riding with gary's re-base per the deferred-work tie: gary's fabricated `slide-01` roster (`gary/_act.py:95`, the slides-leg ninth-seam sibling) and the ninth-seam regex's multi-key/multi-row blind spot.

**Approach:** Re-base each class onto `SpecialistDispatchError` (which subclasses `RuntimeError`, so every existing `except RuntimeError`/named handler is preserved — no dual base needed, unlike the ValueError-based G5 classes). Catch-site audit per class (Amelia discipline): each is caught exactly once, by name, in its own module's `act()` — re-base does not change those. Kill gary's fabrication with a starvation raise via the newly recoverable `GaryActError`. Then widen the ninth-seam regex (safe only after gary's literal is gone). Retire the five EXCLUSIONS rows (the reverse-existence pin demands it).

## Boundaries & Constraints

**Always:** Each re-based class keeps its name, docstring, and tag-carrying constructor semantics (base provides them — delete redundant `__init__`s). Live-path behavior identical on success paths; failure paths change crash→error-pause only. Catch-site grep evidence recorded per class. EXCLUSIONS shrink-only.

**Ask First:** Re-basing any class beyond the five named (the remaining 13 exclusions are later slices). Touching kira/wanda `DEFAULT_BUNDLE_PATH`. Any change to gary's non-empty-roster behavior.

**Never:** No gate-engine/fold/manifest changes. No new fixture branches. Do not roster gary in ALLOWED_FIXTURE_MODULES — the fabrication dies instead.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Any of the 5 raises mid-walk | live trial | Runner error-pauses; `trial recover` resumes | typed tag persisted, walk progress kept |
| Existing named catch sites | each module's `act()` | Unchanged (caught by name) | trail-append + re-raise as today |
| Gary payload with no slides | `{}` / missing keys | REFUSE — no fabricated roster | `GaryActError`, tag `gamma.slides.starved` |
| Gary payload with real slides | live path (node 07 is grounded) | Unchanged | N/A |
| Multi-key/multi-row inline roster literal in app/ | `[{"slide_id": "s1", "title": "x"}]` | Ninth-seam ratchet catches it | audit test fails naming module |

</frozen-after-approval>

## Code Map

- `app/specialists/dispatch_errors.py:15` -- base is `RuntimeError`-derived; identical `(message, *, tag)` ctor
- `app/specialists/gary/_act.py:32-37,92-103` -- GaryActError + fabricated roster; catch site `:273`
- `app/specialists/gary/graph.py:40-45` -- ReceiptParseError; no named catch site anywhere (raise-only)
- `app/specialists/texas/_act.py:36-41` -- BundleParseError; catch `:344`; module already imports the base
- `app/specialists/kira/_act.py:23-28` -- KiraActError; catch `:259`
- `app/specialists/vera/_act.py:39-44` -- FTRParseError; catch `:326`
- `tests/contracts/test_specialist_error_taxonomy.py` -- retire 5 rows; extend `test_known_rebased_classes`
- `tests/audit/test_no_silent_fixture_fallbacks.py` -- widen regex; gary evasion variants
- `tests/specialists/gary/` (new pin file) -- starvation raise + family membership, PIN-AUD-2R style

## Tasks & Acceptance

**Execution:**
- [x] `app/specialists/gary/_act.py` -- re-base GaryActError (drop redundant `__init__`; import base); `_slides` empty → raise `gamma.slides.starved` -- crash class retired + fabrication killed
- [x] `app/specialists/gary/graph.py` -- re-base ReceiptParseError -- same
- [x] `app/specialists/texas/_act.py` -- re-base BundleParseError -- same
- [x] `app/specialists/kira/_act.py` -- re-base KiraActError -- same (prerequisite for the future motion-arc starvation raise per the motion investigation)
- [x] `app/specialists/vera/_act.py` -- re-base FTRParseError -- same
- [x] `tests/contracts/test_specialist_error_taxonomy.py` -- delete the 5 qualified EXCLUSIONS rows; add the 5 classes to `test_known_rebased_classes` -- shrink-only honored, membership pinned
- [x] `tests/audit/test_no_silent_fixture_fallbacks.py` -- widen ninth-seam regex to tolerate extra keys/rows; add gary-shape evasion variants -- the live near-instance class is now catchable with zero offenders
- [x] `tests/specialists/gary/test_gary_slides_starvation_pin.py` -- NEW: empty-payload raise pinned (tag + zero fabrication in source, PIN-AUD-2R style)
- [x] `_bmad-output/planning-artifacts/deferred-inventory.md` -- annotate `tagged-error-taxonomy-systematic-rebase` entry: live-path tranche executed, 13 exclusions remain

**Acceptance Criteria:**
- Given each of the five classes, then `issubclass(cls, SpecialistDispatchError)` AND `issubclass(cls, RuntimeError)` both hold
- Given `gary_act._slides({})`, then `GaryActError` raises with tag `gamma.slides.starved` and the literal fabricated roster is absent from source
- Given the widened regex, then it matches single-key, multi-key, multi-row, whitespace, and renamed-id literal rosters; does not match variable-built rosters; and the app/ scan reports zero unrostered offenders
- Given the full battery (specialists + contracts + audit + marcus integration + lockstep + lint-imports + ruff), then green with no new failures vs the ambient roster

## Spec Change Log

## Verification

**Commands:**
- `.\.venv\Scripts\python.exe -m pytest tests/specialists/ tests/contracts/test_specialist_error_taxonomy.py tests/audit/ tests/integration/marcus/ tests/composition/test_gary_to_vera_g3_chain.py -q` -- expected: green (ambient roster aside)
- `.\.venv\Scripts\python.exe scripts/utilities/check_pipeline_manifest_lockstep.py` -- expected: exit 0
- `.\.venv\Scripts\lint-imports.exe` -- expected: 13 kept, 0 broken
- `.\.venv\Scripts\ruff.exe check <touched files>` -- expected: clean

## Suggested Review Order

**The re-base (crash → error-pause)**

- The family base every class joins: RuntimeError-derived, `(message, *, tag)` ctor — handlers preserved by construction
  [`dispatch_errors.py:15`](../../app/specialists/dispatch_errors.py#L15)

- Gary, the live-path archetype (catch site unchanged at its own `act()`)
  [`gary/_act.py:33`](../../app/specialists/gary/_act.py#L33)

- The other four: same one-line shape
  [`gary/graph.py:41`](../../app/specialists/gary/graph.py#L41) · [`texas/_act.py:36`](../../app/specialists/texas/_act.py#L36) · [`kira/_act.py:24`](../../app/specialists/kira/_act.py#L24) · [`vera/_act.py:40`](../../app/specialists/vera/_act.py#L40)

**The fabrication kill (gary's ninth-seam sibling)**

- Empty roster now refuses recoverably instead of inventing a placeholder deck
  [`gary/_act.py:102`](../../app/specialists/gary/_act.py#L102)

- PIN: behavior + source-absence, PIN-AUD-2R style
  [`test_gary_slides_starvation_pin.py:1`](../../tests/specialists/gary/test_gary_slides_starvation_pin.py#L1)

**Ratchet turns**

- EXCLUSIONS 18→13 (five rows retired; reverse-existence pin enforced the retirement)
  [`test_specialist_error_taxonomy.py:36`](../../tests/contracts/test_specialist_error_taxonomy.py#L36)

- Membership + constructor-semantics pin (blind-hunter patch: issubclass alone can't catch ctor drift)
  [`test_specialist_error_taxonomy.py:117`](../../tests/contracts/test_specialist_error_taxonomy.py#L117)

- Ninth-seam regex widened to multi-key/multi-row (safe only after gary's literal died)
  [`test_no_silent_fixture_fallbacks.py:38`](../../tests/audit/test_no_silent_fixture_fallbacks.py#L38)

- Evasion-variant pins incl. gary's retired two-key shape
  [`test_no_silent_fixture_fallbacks.py:88`](../../tests/audit/test_no_silent_fixture_fallbacks.py#L88)

**Governance**

- TW-7c-4 allowlist tranche block (+ pre-existing duplicate-row dedup, ruff B033)
  [`test_audit_tw_7c_4_no_live_dispatch_scope_creep.py:200`](../../tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py#L200)

- Inventory tranche annotation (remaining 13 enumerated)
  [`deferred-inventory.md:591`](../planning-artifacts/deferred-inventory.md#L591)
