"""Story Q1.1 — AC3: prose ↔ YAML no-silent-drift guard.

Asserts a bijection between the §1.6 assessment-table criterion rows (C1–C5) and
the five machine-block criterion keys, so the prose (which owns meaning/basis) and
the machine block (which owns the numbers) can never drift apart silently.

The bijection is checked on the *criterion ordinal* (C1..C5): every YAML criterion
carries an ``evidence_ref`` that begins with its ``§1.6 C<n>`` tag; every prose
criterion row begins with ``C<n>``. Set-equality of those ordinals fails RED in
BOTH directions:

  * a stray YAML criterion (e.g. a sixth key whose evidence_ref points at a C6 that
    has no prose row) → YAML set ⊋ prose set → RED;
  * a prose row with no backing YAML criterion → prose set ⊋ YAML set → RED.

This reads the committed repo doc + the committed reader (legitimate per the
epic testing doctrine — the drift guard is *about* the real files).

RED-first witness: seeding a sixth machine-block criterion with
``evidence_ref: "§1.6 C6 …"`` (no matching prose row) makes ``yaml_ordinals``
gain ``6`` while ``prose_ordinals`` stays ``{1,2,3,4,5}`` → the assertion fails.
(Demonstrated during development; see the story's Completion Notes.)
"""

from __future__ import annotations

import re

from app.quality.scorecard import _DID_KEY, read_scorecard_block, scorecard_path

_C_TAG_RE = re.compile(r"\bC([1-9])\b")


def _prose_criterion_ordinals(doc_text: str) -> set[int]:
    """Extract the C-ordinals of the §1.6 assessment-table criterion rows.

    The §1.6 table rows look like ``| C1 Neck placement | **4/4** | strong | … |``.
    We take table rows (leading ``|``) whose first cell begins with ``C<n>`` and
    is NOT the ``**Total**`` summary row.
    """
    ordinals: set[int] = set()
    in_16 = False
    for line in doc_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("### 1.6"):
            in_16 = True
            continue
        # The assessment table is the FIRST block after the ### 1.6 header. Stop at
        # the first '####' subsection (e.g. "#### Open leaks") — whose own tables may
        # carry C-prefixed cells — or at the next top-level '### ' section. This keeps
        # the scan confined to the assessment table so a post-table C-cell can't leak.
        if in_16 and (
            stripped.startswith("####")
            or (stripped.startswith("### ") and not stripped.startswith("### 1.6"))
        ):
            break
        if not in_16 or not stripped.startswith("|"):
            continue
        first_cell = stripped.split("|")[1].strip()
        if first_cell.lower().startswith("**total"):
            continue
        m = re.match(r"\**C([1-9])\b", first_cell)
        if m:
            ordinals.add(int(m.group(1)))
    return ordinals


def _yaml_criterion_ordinals(block: dict) -> set[int]:
    """Extract the C-ordinal each machine-block criterion points at via evidence_ref."""
    dim = block["dimensions"][_DID_KEY]
    ordinals: set[int] = set()
    for key, crit in dim["criteria"].items():
        ref = crit.get("evidence_ref")
        assert isinstance(ref, str) and ref, f"criterion {key!r} missing evidence_ref"
        m = _C_TAG_RE.search(ref)
        assert m, f"criterion {key!r} evidence_ref {ref!r} has no C<n> tag"
        ordinals.add(int(m.group(1)))
    return ordinals


def test_prose_and_yaml_criteria_are_in_bijection() -> None:
    doc_text = scorecard_path().read_text(encoding="utf-8")
    block = read_scorecard_block()
    assert isinstance(block, dict), "committed scorecard machine block must be parseable"

    prose_ordinals = _prose_criterion_ordinals(doc_text)
    yaml_ordinals = _yaml_criterion_ordinals(block)

    assert prose_ordinals == {1, 2, 3, 4, 5}, (
        f"expected five §1.6 criterion rows C1–C5, found {sorted(prose_ordinals)}"
    )
    assert yaml_ordinals == prose_ordinals, (
        "prose ↔ YAML criterion drift: "
        f"prose C-rows {sorted(prose_ordinals)} vs YAML criteria {sorted(yaml_ordinals)}"
    )
    # And a hard count check: exactly five YAML criterion keys, one per prose row.
    assert len(block["dimensions"][_DID_KEY]["criteria"]) == 5


# A synthetic §1.6 with a C1–C5 assessment table FOLLOWED by an "#### Open leaks"
# subsection whose own table has a C-prefixed first cell. A correct prose scan stops
# at the first '####' and must NOT harvest the spurious C6 ordinal (FIX-3 boundary).
_SYNTHETIC_16 = """### 1.5 Scoring rubric

irrelevant preamble

### 1.6 Current assessment

| Criterion | Score | Level |
|---|:---:|---|
| C1 Neck placement | 4/4 | strong |
| C2 Bone determinism | 3/4 | strong |
| C3 Fence enforcement | 1/4 | weak |
| C4 Lock discipline | 3/4 | strong |
| C5 Honesty | 2/4 | partial |
| **Total** | 13/20 | B- |

#### Open leaks (the path from 65 → 90)

| Item | Note |
|---|---|
| C6 spurious post-table row | must NOT be harvested |

### Cadence
"""


def test_prose_scan_stops_at_first_subsection_boundary() -> None:
    """FIX-3: a C-prefixed first cell placed in a post-table §1.6 subsection (e.g. the
    '#### Open leaks' list) must not leak a spurious ordinal. The scan stops at the
    first '####' after the '### 1.6' header, so only the assessment-table rows count.
    """
    ordinals = _prose_criterion_ordinals(_SYNTHETIC_16)
    assert ordinals == {1, 2, 3, 4, 5}, (
        f"prose scan leaked past the §1.6 assessment table: {sorted(ordinals)}"
    )


def test_yaml_criterion_keys_are_the_expected_five() -> None:
    """Anti-regression: the five machine-block criterion keys are named here, so a
    silent rename/add/drop in the doc fails CI (companion to the ordinal bijection).
    """
    block = read_scorecard_block()
    assert isinstance(block, dict)
    expected = {
        "neck_placement",
        "bone_determinism",
        "fence_enforcement_default_on",
        "lock_and_contract_discipline",
        "honesty_and_calibration",
    }
    assert set(block["dimensions"][_DID_KEY]["criteria"]) == expected
