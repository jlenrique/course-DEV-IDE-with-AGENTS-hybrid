"""Story Q1.3 — the anti-believed-green honesty pins + meta-ratchet (RED-first).

The whole point (consensus rule #3): **each pin compares a machine-block CLAIM
against a CODE-COMPUTED reality — doc↔code, never doc↔doc.** A pin that only
checks the doc against itself is worthless, so every pin below cites a code
source, and — post code-review — every pin **iterates over EVERY dimension** in
the machine block, so coverage is structural (a future ``cost_efficiency``
dimension is automatically subject to the same pins; it cannot pass vacuously on
a DID-only assertion):

  * **(a) fence-claim consistency** → ``app.quality.signals``: for every
    ``derivation: signal-derived`` criterion the machine-block ``level`` must
    equal the reader's live output; AND the set of mechanical criteria is decided
    by CODE (``_SIGNAL_DERIVED_READERS``), not the doc's self-declared
    ``derivation`` — relabeling C3 to dodge the pin is itself RED (R3).
  * **(b) leak-count reconciliation** → ``open_leak_count_signal``:
    the DID dimension's ``open_leaks`` must equal the count of ``did_leak:``-tagged
    OPEN entries. **GL-14:** GREEN on a seeded fixture; on the REAL repo a hard
    reconciliation pin (Q1.5 removed the ``xfail(strict=True)`` once the 5 leaks were
    tagged in the ``## DID Scorecard Leak Registry``).
  * **(c) score-arithmetic** → the §1.5 rubric: score↔level↔band↔sum consistent.

**GL-6 meta-ratchet** (AC2): a NAMED canonical dimension universe + a pin
registry + :func:`test_every_dimension_has_a_honesty_pin` (0-dimension block is
itself a violation — no vacuous pass), mirroring the 43-10 structural form.

**GL-11 / GL-12** (AC3): ``trend`` is compared to ``trend_from_history`` (no
painted arrows). The evidence-gated upgrade guard runs as a STANDING pin over the
real block + the real newest-strictly-prior history snapshot, and the
**doc↔ledger mirror** pin (:func:`test_newest_history_mirrors_current_block`)
makes "inflate the doc without appending to history" impossible — so the guard
cannot be silently kept a forever-no-op. Any INCREASE must cite an ``evidence_ref``
AND advance ``as_verified``; unknown/malformed prior levels are treated
conservatively (a real increase can never slip). Downgrades are free.

**AC5 / GL-9 doctrine:** every pin passes TODAY by AGREEING WITH REALITY, and a
companion proof shows it goes RED under a **seeded** dishonest edit — via a
fixture / an in-memory ``deepcopy`` mutation, **NEVER** by mutating the real doc.

**Honest residual (anti-believed-green, stated plainly):** the trend/history axis
is a JUDGMENT-HISTORY ledger, not observed system state. These pins enforce the
doc↔ledger mirror, a mandatory append on every doc change, and evidence-gated
increases — but they CANNOT mechanically detect a *coordinated* fabrication of
BOTH the doc and the ledger in one edit. That residual is a review / governance
concern, not a mechanical guarantee.

Pure-structural + hermetic-fixture where possible (like 43-10). No live calls, no
``--run-live``. Reads the committed doc + committed readers (legitimate per the
epic testing doctrine — the pins are *about* the real files).
"""

from __future__ import annotations

import copy
import re
import textwrap
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from app.quality.history import (
    latest_prior_snapshot,
    newest_snapshot,
    trend_from_history,
)
from app.quality.scorecard import (
    _COST_KEY,
    _DID_KEY,
    _EXPECTED_CANONICAL_DIMENSION_KEYS,
    read_scorecard_block,
)
from app.quality.signals import (
    _DEFERRED_INVENTORY_REL,
    _repo_root,
    _strip_archived_section,
    _strip_fenced_code,
    _strip_html_comments,
    budget_stop_default_signal,
    cost_leak_count_signal,
    fences_enabled_signal,
    level_from_signal,
    open_leak_count_signal,
)

#: Captures the slug after a line-anchored ``did_leak:`` tag (mirrors the count
#: regex ``signals._DID_LEAK_LINE_RE`` but also captures the slug token). Used by the
#: slug-set IDENTITY pin (FIX-1) — the count pins reconcile through the integer 5 and
#: cannot catch a slug that was typo'd/renamed while the count stayed 5.
_DID_LEAK_SLUG_RE = re.compile(r"(?m)^[\s>]*(?:[-*+]\s+)?did_leak:\s*(\S+)")
#: Q2.1 — the cost_efficiency slug namespace (``cost_leak:``), a SEPARATE per-dimension
#: namespace so the cost identity/count reconciliation never collides with DID's.
_COST_LEAK_SLUG_RE = re.compile(r"(?m)^[\s>]*(?:[-*+]\s+)?cost_leak:\s*(\S+)")


def _registry_did_leak_slugs() -> set[str]:
    """The OPEN ``did_leak:`` slugs in the real deferred-inventory registry — read the
    SAME way ``open_leak_count_signal`` counts them (fenced code / HTML comments /
    archived section stripped) so the identity set and the count agree on scope."""
    text = (_repo_root() / _DEFERRED_INVENTORY_REL).read_text(encoding="utf-8")
    open_text = _strip_archived_section(_strip_html_comments(_strip_fenced_code(text)))
    return {m.group(1) for m in _DID_LEAK_SLUG_RE.finditer(open_text)}


def _registry_cost_leak_slugs() -> set[str]:
    """The OPEN ``cost_leak:`` slugs in the real deferred-inventory registry — read the
    SAME way ``cost_leak_count_signal`` counts them (Q2.1 per-dimension identity pin)."""
    text = (_repo_root() / _DEFERRED_INVENTORY_REL).read_text(encoding="utf-8")
    open_text = _strip_archived_section(_strip_html_comments(_strip_fenced_code(text)))
    return {m.group(1) for m in _COST_LEAK_SLUG_RE.finditer(open_text)}


def _machine_block_leak_slugs(dim: dict[str, Any]) -> set[str]:
    """The slug set from a dimension's structured machine-block ``leaks`` list."""
    leaks = dim.get("leaks")
    if not isinstance(leaks, list):
        return set()
    return {leak.get("slug") for leak in leaks if isinstance(leak, dict)}

# --------------------------------------------------------------------------- #
# §1.5 rubric, encoded here as the score-arithmetic pin's source of truth.
# score→allowed level(s): 4=strong/uniform · 3=strong · 2=partial · 1=weak · 0=absent
# --------------------------------------------------------------------------- #
_SCORE_TO_LEVELS: dict[int, frozenset[str]] = {
    4: frozenset({"strong", "uniform"}),
    3: frozenset({"strong"}),
    2: frozenset({"partial"}),
    1: frozenset({"weak"}),
    0: frozenset({"absent"}),
}

_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _iso_ok(value: Any) -> bool:
    """True iff ``value`` is a ``YYYY-MM-DD`` string safe to order lexically."""
    return isinstance(value, str) and bool(_ISO_DATE_RE.match(value))


def _as_str(value: Any) -> str | None:
    """None-safe stringify. The machine-block ``as_of``/``as_verified`` parse to
    ``datetime.date`` (bare YAML dates) while the ledger stores ISO strings — both
    normalize to the same ``YYYY-MM-DD`` here."""
    return str(value) if value is not None else None


def _int_score(value: Any) -> int | None:
    """A real integer score, or ``None`` if malformed. ``bool`` is an ``int``
    subclass and must NEVER coerce to 0/1 (R5b) — a ``score: true`` is malformed,
    not a weak criterion."""
    if isinstance(value, bool):
        return None
    return value if isinstance(value, int) else None


#: §1.5 band boundary table: A ≥90 · B 75–89 · B− 60–74 · C 40–59 · D <40.
def _band_for_score(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "B-"
    if score >= 40:
        return "C"
    return "D"


#: The signal-derived criteria and the CODE reader whose live output their level
#: must equal (pin (a)). **This — not the doc's self-declared ``derivation`` — is
#: the authority on which criteria are mechanical (R3).** Only C3 is purely
#: mechanical today; C2/C4 are judgment-with-evidence and C1/C5 are judgment.
_SIGNAL_DERIVED_READERS: dict[str, Callable[[], Any]] = {
    "fence_enforcement_default_on": fences_enabled_signal,
    # Q2.1 — cost_efficiency CE1 is purely mechanical (mirrors DID C3): the env-
    # INDEPENDENT production-preset posture is default_budget_enforced=False → weak.
    "budget_stop_default_on": budget_stop_default_signal,
}

#: GL-6 pin registry — each canonical dimension → the honesty-pins registered for
#: it (by this module's test-function names). ``test_every_dimension_has_a_honesty_pin``
#: fails unless every machine-block dimension appears here with ≥1 pin. Adding a
#: dimension to the machine block WITHOUT registering a pin here → RED (the 42-1
#: believed-green class the 43-10 ratchet kills, generalized to dimensions).
_HONESTY_PIN_REGISTRY: dict[str, frozenset[str]] = {
    _DID_KEY: frozenset(
        {
            "test_signal_derived_levels_match_readers",  # pin (a) fence-claim
            "test_leak_count_reconciles_on_real_repo",  # pin (b) leak-count (GL-14)
            "test_score_arithmetic_is_internally_consistent",  # pin (c) arithmetic
        }
    ),
    # Q2.1 — cost_efficiency MUST register ≥1 pin or the GL-6 meta-ratchet
    # (test_every_dimension_has_a_honesty_pin) reds it. Its three pins mirror DID's:
    # (a) budget-fence-claim, (b) cost leak-count + slug identity, (c) arithmetic.
    _COST_KEY: frozenset(
        {
            "test_cost_budget_fence_claim_matches_reader",  # pin (a) budget-fence-claim
            "test_cost_leak_count_reconciles_on_real_repo",  # pin (b) cost leak-count
            "test_cost_score_arithmetic_is_internally_consistent",  # pin (c) arithmetic
        }
    ),
}


# ============================ pure honesty-pin helpers ============================
# All block-level helpers ITERATE over every dimension (R2): coverage is structural.


def _signal_derived_violations(block: dict[str, Any]) -> list[str]:
    """Pin (a), doc-driven half: every criterion the DOC labels ``signal-derived``
    must have its claimed ``level`` equal its reader's CODE-computed level.
    Iterates all dimensions. Returns doc↔code contradictions (empty == honest)."""
    violations: list[str] = []
    for dim_key, dim in (block.get("dimensions") or {}).items():
        for key, crit in (dim.get("criteria") or {}).items():
            if not isinstance(crit, dict) or crit.get("derivation") != "signal-derived":
                continue
            reader = _SIGNAL_DERIVED_READERS.get(key)
            if reader is None:
                violations.append(
                    f"{dim_key}.{key}: derivation=signal-derived but no registered reader"
                )
                continue
            derived = level_from_signal(key, reader())
            if crit.get("level") != derived:
                violations.append(
                    f"{dim_key}.{key}: machine-block level {crit.get('level')!r} != "
                    f"reader-derived {derived!r}"
                )
    return violations


def _mechanical_criteria_violations(block: dict[str, Any]) -> list[str]:
    """Pin (a), CODE-driven half (R3 anti-de-mechanization): for each criterion the
    CODE knows is mechanical (``_SIGNAL_DERIVED_READERS``), assert it (i) STILL
    declares ``derivation: signal-derived`` (relabeling it to judgment to dodge the
    pin → RED) AND (ii) its level == the reader output. A code-known mechanical
    criterion that has vanished from every dimension is also a violation."""
    violations: list[str] = []
    dims = block.get("dimensions") or {}
    for key, reader in _SIGNAL_DERIVED_READERS.items():
        found = False
        derived = level_from_signal(key, reader())
        for dim_key, dim in dims.items():
            crit = (dim.get("criteria") or {}).get(key)
            if not isinstance(crit, dict):
                continue
            found = True
            if crit.get("derivation") != "signal-derived":
                violations.append(
                    f"{dim_key}.{key}: code-known mechanical criterion is de-mechanized "
                    f"(derivation={crit.get('derivation')!r}, expected 'signal-derived')"
                )
            if crit.get("level") != derived:
                violations.append(
                    f"{dim_key}.{key}: level {crit.get('level')!r} != reader-derived {derived!r}"
                )
        if not found:
            violations.append(
                f"{key}: code-known mechanical criterion is absent from every dimension"
            )
    return violations


def _reconcile(open_leaks_claim: Any, open_leak_count: Any) -> bool:
    """Pin (b) core: the hand-carried ``open_leaks`` equals the CODE-counted
    ``did_leak:`` open-tag count. Fail-soft: a ``None`` count (unavailable reader)
    or a ``bool`` never reconciles."""
    return (
        _int_score(open_leaks_claim) is not None
        and _int_score(open_leak_count) is not None
        and open_leaks_claim == open_leak_count
    )


def _arithmetic_violations(dim: dict[str, Any]) -> list[str]:
    """Pin (c) as a pure function over ONE dimension: score↔level (per §1.5) +
    Σscore/max→/100 == headline + band == §1.5 boundary. Hardened: a missing
    ``criteria`` mapping returns a clean violation, not a KeyError (R5a); a ``bool``
    score is malformed, never coerced to 0/1 (R5b)."""
    violations: list[str] = []
    crit = dim.get("criteria")
    if not isinstance(crit, dict) or not crit:
        return [f"dimension has no criteria mapping (got {type(crit).__name__})"]
    total = 0
    max_sum = 0
    for key, c in crit.items():
        if not isinstance(c, dict):
            violations.append(f"{key}: criterion is not a mapping")
            continue
        score = _int_score(c.get("score"))
        level = c.get("level")
        allowed = _SCORE_TO_LEVELS.get(score) if score is not None else None
        if allowed is None or level not in allowed:
            violations.append(
                f"{key}: score {c.get('score')!r} ↔ level {level!r} violates §1.5"
            )
        if score is not None:
            total += score
        cmax = _int_score(c.get("max"))
        if cmax is not None:
            max_sum += cmax
    if max_sum <= 0:
        violations.append(f"criterion max sum is {max_sum} (expected > 0)")
        return violations
    normalized = round(total / max_sum * 100)
    headline = _int_score(dim.get("score"))
    if headline is None or normalized != headline:
        violations.append(
            f"Σscore {total}/{max_sum} normalizes to {normalized} != headline {dim.get('score')!r}"
        )
    if headline is not None:
        expected_band = _band_for_score(headline)
        if dim.get("band") != expected_band:
            violations.append(
                f"band {dim.get('band')!r} != §1.5 band for {headline} ({expected_band!r})"
            )
    return violations


def _dimensions_without_pins(
    dimension_keys: set[str], registry: dict[str, frozenset[str]]
) -> set[str]:
    """The dimensions present in the machine block that have NO registered
    honesty-pin. A future pin-less dimension surfaces here → RED."""
    return {d for d in dimension_keys if not registry.get(d)}


def _coverage_violations(
    dimension_keys: set[str], registry: dict[str, frozenset[str]]
) -> set[str]:
    """GL-6 core: pin-less dimensions PLUS the vacuous-block guard (R5d) — a
    0-dimension block is itself a violation, never a silent pass."""
    if not dimension_keys:
        return {"<no dimensions in machine block>"}
    return _dimensions_without_pins(dimension_keys, registry)


def _mirror_projection_block(dim_key: str, dim: dict[str, Any]) -> dict[str, Any]:
    return {
        "dimension": dim_key,
        "score": dim.get("score"),
        "band": dim.get("band"),
        "levels": {
            k: (c or {}).get("score") for k, c in (dim.get("criteria") or {}).items()
        },
        "open_leaks": dim.get("open_leaks"),
        "as_of": _as_str(dim.get("as_of")),
        "as_verified": _as_str(dim.get("as_verified")),
    }


def _mirror_projection_snapshot(snap: dict[str, Any]) -> dict[str, Any]:
    return {
        "dimension": snap.get("dimension"),
        "score": snap.get("score"),
        "band": snap.get("band"),
        "levels": dict(snap.get("levels") or {}),
        "open_leaks": snap.get("open_leaks"),
        "as_of": _as_str(snap.get("as_of")),
        "as_verified": _as_str(snap.get("as_verified")),
    }


def _mirror_violations(block: dict[str, Any], path: Path | None = None) -> list[str]:
    """R1 (HIGH): the NEWEST history entry per dimension must content-match the
    current machine block ({dimension, score, band, levels, open_leaks, as_of,
    as_verified}). A doc change not reflected in the ledger (append for a new
    ``as_of`` / update-in-place for a same-day edit) → RED. This makes "inflate the
    doc without touching history" impossible and guarantees the evidence-gated
    guard gets a real prior on the next re-score."""
    violations: list[str] = []
    for dim_key, dim in (block.get("dimensions") or {}).items():
        newest = newest_snapshot(dim_key, path)
        if newest is None:
            violations.append(
                f"{dim_key}: no history snapshot mirrors the current block "
                "(append one to docs/quality/scorecard-history.jsonl)"
            )
            continue
        want = _mirror_projection_block(dim_key, dim)
        got = _mirror_projection_snapshot(newest)
        if want != got:
            violations.append(
                f"{dim_key}: newest history entry does not mirror the block — "
                f"block={want} ledger={got}"
            )
    return violations


def evidence_gated_upgrade_violations(
    dim: dict[str, Any], prior_snapshot: dict[str, Any] | None
) -> list[str]:
    """GL-11 guard over ONE dimension: any criterion/headline INCREASE vs the
    latest PRIOR snapshot must cite (i) a non-empty ``evidence_ref`` AND (ii) an
    ``as_verified`` advance (a bumped ``as_of`` alone — prose edited, evidence NOT
    re-checked — must not suffice; that split is the whole point). **Downgrades are
    free.** Conservative on malformed prior data (R5c): a missing ``levels`` map or
    a non-numeric prior level is treated as "cannot prove it's not an increase" →
    the increase requires evidence. With no prior snapshot (first-run) → ``[]``."""
    if prior_snapshot is None:
        return []
    cur_verified = _as_str(dim.get("as_verified"))
    prior_verified = prior_snapshot.get("as_verified")
    verified_advanced = (
        _iso_ok(cur_verified) and _iso_ok(prior_verified) and cur_verified > prior_verified
    )
    prior_levels = prior_snapshot.get("levels")
    levels_ok = isinstance(prior_levels, dict)
    violations: list[str] = []
    for key, c in (dim.get("criteria") or {}).items():
        if not isinstance(c, dict):
            continue
        cur = _int_score(c.get("score"))
        if cur is None:
            continue
        prev = _int_score(prior_levels.get(key)) if levels_ok else None
        # Unknown / malformed prior → conservative increase (R5c): must not slip.
        is_increase = prev is None or cur > prev
        if not is_increase:
            continue
        if not verified_advanced:
            violations.append(
                f"{key} rose to {cur} (prior {prev}) without an as_verified advance "
                "(stale evidence — a bumped as_of does NOT suffice)"
            )
        ev = c.get("evidence_ref")
        if not (isinstance(ev, str) and ev.strip()):
            violations.append(
                f"{key} rose to {cur} (prior {prev}) without citing an evidence_ref"
            )
    cur_head = _int_score(dim.get("score"))
    prev_head = _int_score(prior_snapshot.get("score"))
    head_increase = cur_head is not None and (prev_head is None or cur_head > prev_head)
    if head_increase and not verified_advanced:
        violations.append(
            f"headline rose to {cur_head} (prior {prev_head}) without an as_verified advance"
        )
    return violations


# ============================ shared fixtures/helpers ============================


def _clear_fence_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for env in (
        "MARCUS_NARRATION_FIGURE_FIDELITY_ACTIVE",
        "MARCUS_COVERAGE_GATE_ACTIVE",
        "MARCUS_UDAC_ACTIVE",
    ):
        monkeypatch.delenv(env, raising=False)


def _real_block() -> dict[str, Any]:
    block = read_scorecard_block()
    assert isinstance(block, dict), "committed scorecard machine block must be parseable"
    return block


#: The seeded baseline history snapshot (mirrors docs/quality/scorecard-history.jsonl).
_BASELINE_SNAPSHOT: dict[str, Any] = {
    "as_of": "2026-07-19",
    "dimension": _DID_KEY,
    "score": 65,
    "band": "B-",
    "levels": {
        "neck_placement": 4,
        "bone_determinism": 3,
        "fence_enforcement_default_on": 1,
        "lock_and_contract_discipline": 3,
        "honesty_and_calibration": 2,
    },
    "open_leaks": 5,
    "as_verified": "2026-07-19",
}


def _did_dim_with(mutate: Callable[[dict[str, Any]], None]) -> dict[str, Any]:
    """A deepcopy of the real DID dimension with ``mutate`` applied — never touches
    the real doc."""
    dim = copy.deepcopy(_real_block()["dimensions"][_DID_KEY])
    mutate(dim)
    return dim


# ================================= PIN (a) fence-claim =================================


def test_signal_derived_levels_match_readers(monkeypatch: pytest.MonkeyPatch) -> None:
    """Pin (a) GREEN today: every signal-derived criterion's level == its reader's
    live output. Concretely C3 == level_from_signal(fences_enabled_signal()) ==
    'weak' (the env-INDEPENDENT default-OFF production posture)."""
    _clear_fence_env(monkeypatch)
    _clear_budget_env(monkeypatch)  # CE1's env-live reader now also runs in this scan
    block = _real_block()
    assert _signal_derived_violations(block) == []
    c3 = block["dimensions"][_DID_KEY]["criteria"]["fence_enforcement_default_on"]
    derived = level_from_signal("fence_enforcement_default_on", fences_enabled_signal())
    assert c3["level"] == derived == "weak"


def test_code_known_mechanical_criteria_not_de_mechanized(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """R3 GREEN today: CODE (not the doc) decides which criteria are mechanical.
    Each ``_SIGNAL_DERIVED_READERS`` criterion still declares ``signal-derived`` and
    matches its reader output."""
    _clear_fence_env(monkeypatch)
    _clear_budget_env(monkeypatch)  # CE1's env-live reader is in _SIGNAL_DERIVED_READERS
    assert _mechanical_criteria_violations(_real_block()) == []


def test_de_mechanization_is_caught(monkeypatch: pytest.MonkeyPatch) -> None:
    """R3 RED-under-seeded-edit: relabel C3's ``derivation`` to judgment-with-evidence
    AND bump its level — the doc-driven pin (a) would SKIP it (the believed-green
    hole), but the CODE-driven pin catches BOTH the de-mechanization and the level
    lie. Real doc untouched."""
    _clear_fence_env(monkeypatch)
    block = copy.deepcopy(_real_block())
    c3 = block["dimensions"][_DID_KEY]["criteria"]["fence_enforcement_default_on"]
    c3["derivation"] = "judgment-with-evidence"  # dodge attempt
    c3["level"] = "strong"  # the inflation being hidden
    # Doc-driven half now skips C3 (it no longer self-declares signal-derived):
    assert _signal_derived_violations(block) == []
    # …but the code-driven half catches it on both counts:
    violations = _mechanical_criteria_violations(block)
    assert any("de-mechanized" in v for v in violations), violations
    assert any("reader-derived" in v for v in violations), violations


def test_fence_claim_pin_reds_on_dishonest_level(monkeypatch: pytest.MonkeyPatch) -> None:
    """AC5 RED-under-seeded-edit: bump C3 to 'strong' in an in-memory copy WITHOUT
    the env-gate default flipping → the pin (a) comparison FAILS. The real doc is
    never touched."""
    _clear_fence_env(monkeypatch)
    block = copy.deepcopy(_real_block())
    block["dimensions"][_DID_KEY]["criteria"]["fence_enforcement_default_on"][
        "level"
    ] = "strong"
    violations = _signal_derived_violations(block)
    assert any("fence_enforcement_default_on" in v for v in violations), violations


@pytest.mark.parametrize("dishonest", ["strong", "partial", "uniform"])
def test_fence_claim_pin_reds_on_any_inflated_level(
    monkeypatch: pytest.MonkeyPatch, dishonest: str
) -> None:
    """AC5: any inflation of C3 above the reader-derived 'weak' (with fences still
    default-OFF) is caught."""
    _clear_fence_env(monkeypatch)
    block = copy.deepcopy(_real_block())
    block["dimensions"][_DID_KEY]["criteria"]["fence_enforcement_default_on"][
        "level"
    ] = dishonest
    assert _signal_derived_violations(block) != []


# ================================= PIN (b) leak-count =================================

_FIXTURE_INVENTORY_3 = textwrap.dedent(
    """\
    # Deferred Inventory (fixture)

    ## Named-But-Not-Filed Follow-Ons

    ### open-one
    did_leak: true — counted.

    ### open-two
    did_leak: yes — counted.

    ### open-three
    did_leak: true — counted.
    """
)


def test_leak_count_reconciles_on_fixture(tmp_path: Path) -> None:
    """Pin (b) GREEN on a seeded fixture (GL-14): a fixture inventory with 3
    ``did_leak:`` open tags reconciles against a seeded ``open_leaks: 3``. This
    proves the reconciliation LOGIC while the real repo is RED-pending."""
    inv = tmp_path / "inv.md"
    inv.write_text(_FIXTURE_INVENTORY_3, encoding="utf-8")
    count = open_leak_count_signal(inv)["open_leak_count"]
    assert count == 3
    assert _reconcile(3, count) is True  # seeded open_leaks:3 ↔ 3 tags


def test_leak_count_pin_reds_when_fixture_tag_struck(tmp_path: Path) -> None:
    """AC5 RED-under-seeded-edit: strike one ``did_leak:`` tag in the FIXTURE while
    the claimed ``open_leaks`` stays 3 → reconciliation FAILS (3 != 2). The real
    inventory is never touched."""
    inv = tmp_path / "inv.md"
    inv.write_text(_FIXTURE_INVENTORY_3, encoding="utf-8")
    assert _reconcile(3, open_leak_count_signal(inv)["open_leak_count"]) is True
    struck = _FIXTURE_INVENTORY_3.replace(
        "### open-three\ndid_leak: true — counted.\n", "### open-three\n(closed)\n"
    )
    inv.write_text(struck, encoding="utf-8")
    count = open_leak_count_signal(inv)["open_leak_count"]
    assert count == 2
    assert _reconcile(3, count) is False  # stale claim 3 vs real 2 → RED


def test_leak_count_reconciles_on_real_repo() -> None:
    """Pin (b) on the REAL repo — now a HARD GREEN pin (GL-14 self-clearing FIRED).
    Q1.5 tagged the 5 ``did_leak:`` entries in the ``## DID Scorecard Leak Registry``
    of ``deferred-inventory.md``, so ``open_leak_count_signal()`` == 5 == the DID
    dimension's ``open_leaks`` (5 == 5) and the reconciliation passes by AGREEING
    WITH REALITY. Q1.3 shipped this as ``xfail(strict=True)`` (open_leaks hand-carried
    while 0 tags existed); Q1.5 removed that marker once the tags landed, promoting it
    to the standing doc↔code reconciliation.

    **Scope (FIX-2):** the ``did_leak:`` tags are DID-specific, so this reconciles the
    DID dimension's ``open_leaks`` ONLY — NOT every dimension. A future Q2/Q3 dimension
    carries its own (differently-namespaced) leak accounting; reconciling the single
    global DID count against a Q2/Q3 ``open_leaks`` would red this DID pin spuriously.
    Per-dimension leak namespacing (a per-dimension tag namespace + reader) is that
    later story's concern.

    Anti-drift: strike any one ``did_leak:`` tag → the count drops to 4, 5 != 4, and
    this pin goes RED (proven by ``test_leak_count_pin_reds_when_fixture_tag_struck``
    on the fixture path)."""
    did = _real_block()["dimensions"][_DID_KEY]
    count = open_leak_count_signal()["open_leak_count"]
    assert _reconcile(did.get("open_leaks"), count), (
        f"{_DID_KEY}: open_leaks {did.get('open_leaks')!r} != counted did_leak: tags {count}"
    )
    # Q1.4b (AC1) — fuller reconciliation: the STRUCTURED machine-block ``leaks`` list
    # (each {rank, criterion, slug, lane}) must also match ``open_leaks`` in length
    # (checked only when the list is present + open_leaks is a clean int — additive, so
    # this never spuriously reds a dimension that has not yet added a ``leaks`` list).
    leaks = did.get("leaks")
    open_leaks = did.get("open_leaks")
    if isinstance(leaks, list) and isinstance(open_leaks, int) and not isinstance(
        open_leaks, bool
    ):
        assert len(leaks) == open_leaks, (
            f"{_DID_KEY}: structured leaks len {len(leaks)} != open_leaks {open_leaks}"
        )


# ============================ PIN (b') leak-slug IDENTITY (FIX-1) ============================


def test_machine_block_leak_slugs_match_registry_identity() -> None:
    """FIX-1 — SSOT slug IDENTITY reconciliation the count pins lack.

    Pin (b) reconciles through the integer 5 (registry ``did_leak:`` count ==
    ``open_leaks`` == structured ``len(leaks)``); a slug that is TYPO'd in the machine
    block or RENAMED in the registry keeps all three at 5 and every count pin green
    while the slugs have silently diverged. This pin asserts SET EQUALITY of the two
    slug identities — the machine-block ``leaks`` slugs vs the registry ``did_leak:``
    slugs — so an identity drift is caught even when the counts still reconcile."""
    did = _real_block()["dimensions"][_DID_KEY]
    assert _machine_block_leak_slugs(did) == _registry_did_leak_slugs()


def test_slug_identity_pin_reds_on_seeded_slug_typo_while_counts_stay_green() -> None:
    """FIX-1 RED-first: typo ONE machine-block leak slug on a COPY → the identity pin
    RED (set inequality) while the count pins stay green (len==open_leaks==5), proving
    the identity pin catches drift the count-only reconciliation misses."""
    block = copy.deepcopy(_real_block())
    did = block["dimensions"][_DID_KEY]
    did["leaks"][0]["slug"] = "gary-export-typo"  # rename one slug; count unchanged
    # Identity pin RED — the machine-block slug set no longer equals the registry set.
    assert _machine_block_leak_slugs(did) != _registry_did_leak_slugs()
    # Count pins STILL green — everything still reconciles through the integer 5.
    assert len(did["leaks"]) == did["open_leaks"] == 5


# ================================= PIN (c) score-arithmetic =================================


def test_score_arithmetic_is_internally_consistent() -> None:
    """Pin (c) GREEN today, over EVERY dimension (R2): score↔level per §1.5 +
    Σscore/max→/100 == headline + band == §1.5 boundary. Doc↔code: the arithmetic
    RULE is the code source. (R7: no brittle insertion-order literal — the check is
    the ``_arithmetic_violations`` computation, robust to YAML key reorder.)"""
    block = _real_block()
    problems = {
        dk: v for dk, dv in block["dimensions"].items() if (v := _arithmetic_violations(dv))
    }
    assert problems == {}, problems
    dim = block["dimensions"][_DID_KEY]
    assert dim["score"] == 65 and dim["band"] == "B-"  # DID numbers unchanged


def test_arithmetic_pin_covers_every_dimension_not_just_did() -> None:
    """R2: a SEEDED 2nd dimension with an arithmetic inconsistency is caught by the
    same (parametrized-over-all-dimensions) arithmetic pin — proving coverage is not
    DID-only. Real block never mutated."""
    block = copy.deepcopy(_real_block())
    block["dimensions"]["cost_efficiency"] = {
        "as_of": "2026-07-19",
        "as_verified": "2026-07-19",
        "score": 99,  # inconsistent: Σ = 1/4 → 25, not 99
        "band": "A",
        "criteria": {"c1": {"level": "weak", "score": 1, "max": 4}},
        "open_leaks": 0,
        "trend": "baseline",
    }
    problems = {
        dk: v for dk, dv in block["dimensions"].items() if (v := _arithmetic_violations(dv))
    }
    assert "cost_efficiency" in problems, problems


def test_arithmetic_pin_handles_missing_criteria_without_keyerror() -> None:
    """R5a: a dimension missing its ``criteria`` mapping returns a clean violation,
    never a KeyError."""
    violations = _arithmetic_violations({"score": 65, "band": "B-"})  # no 'criteria'
    assert violations and any("criteria" in v for v in violations)


def test_arithmetic_pin_rejects_bool_score_not_coerced_to_one() -> None:
    """R5b: a ``score: true`` must be flagged malformed, NEVER silently treated as
    the integer 1 (which would let a dishonest bool pass score↔level + arithmetic)."""
    dim = _did_dim_with(
        lambda d: d["criteria"]["fence_enforcement_default_on"].update(score=True)
    )
    violations = _arithmetic_violations(dim)
    assert any(
        "fence_enforcement_default_on" in v and "violates §1.5" in v for v in violations
    ), violations
    # And the bool did NOT count as 1 toward the sum → the headline also fails.
    assert any("normalizes" in v for v in violations), violations


@pytest.mark.parametrize(
    ("mutate", "needle"),
    [
        pytest.param(lambda d: d.update(band="A"), "band", id="fat-fingered-band"),
        pytest.param(lambda d: d.update(score=80), "normalizes", id="fat-fingered-headline"),
        pytest.param(
            lambda d: d["criteria"]["fence_enforcement_default_on"].update(score=4),
            "normalizes",
            id="fat-fingered-criterion-score",
        ),
        pytest.param(
            lambda d: d["criteria"]["honesty_and_calibration"].update(level="strong"),
            "violates §1.5",
            id="score-level-mismatch",
        ),
    ],
)
def test_score_arithmetic_pin_reds_on_seeded_edit(mutate, needle: str) -> None:
    """AC5 RED-under-seeded-edit: fat-finger the band / headline / a criterion
    score / a score↔level pairing in an in-memory copy → pin (c) FAILS. Real doc
    untouched."""
    dim = _did_dim_with(mutate)
    violations = _arithmetic_violations(dim)
    assert any(needle in v for v in violations), violations


# ================================= GL-6 meta-ratchet =================================


def test_every_dimension_has_a_honesty_pin() -> None:
    """AC2 / GL-6 (CRITICAL): every dimension in the v2 machine block has ≥1
    registered honesty-pin; a 0-dimension block is itself a violation (R5d — no
    vacuous pass). A future dimension added without registering a pin → RED."""
    block = _real_block()
    dim_keys = set(block["dimensions"])
    assert dim_keys, "machine block declares zero dimensions"
    without = _coverage_violations(dim_keys, _HONESTY_PIN_REGISTRY)
    assert without == set(), f"dimension(s) with no registered honesty-pin: {sorted(without)}"


def test_meta_ratchet_rejects_zero_dimension_block() -> None:
    """R5d: a 0-dimension machine block must NOT pass the coverage check vacuously."""
    assert _coverage_violations(set(), _HONESTY_PIN_REGISTRY) != set()


def test_canonical_universe_matches_machine_block() -> None:
    """AC2 no-typo/no-orphan: the NAMED canonical dimension universe (Q1.1's
    ``_EXPECTED_CANONICAL_DIMENSION_KEYS``) equals the machine-block dimension keys
    — a silent add/rename/drop fails here."""
    block = _real_block()
    assert set(_EXPECTED_CANONICAL_DIMENSION_KEYS) == set(block["dimensions"])


def test_pin_registry_keys_are_canonical_no_orphans() -> None:
    """AC2: the registry names only canonical dimensions (no typo/orphan), and
    every registered pin is a real test function in this module (no dangling
    reference)."""
    canonical = set(_EXPECTED_CANONICAL_DIMENSION_KEYS)
    stray = set(_HONESTY_PIN_REGISTRY) - canonical
    assert stray == set(), f"registry keys not in the canonical universe: {sorted(stray)}"
    for dim, pins in _HONESTY_PIN_REGISTRY.items():
        assert pins, f"{dim} registered with an empty pin set"
        for pin_name in pins:
            assert callable(globals().get(pin_name)), (
                f"registered pin {pin_name!r} for {dim} is not a test in this module"
            )


def test_meta_ratchet_reds_on_pinless_dimension() -> None:
    """AC2 seeded-RED: a future dimension present in the block but absent from the
    registry surfaces as pin-less → RED. (Uses a seeded key set — the real block
    is never mutated. ``cost_efficiency`` is now a REGISTERED dimension, so the
    hypothetical unpinned key is a fresh future dimension.)"""
    seeded_keys = {_DID_KEY, _COST_KEY, "some_future_unpinned_dimension"}
    without = _coverage_violations(seeded_keys, _HONESTY_PIN_REGISTRY)
    assert without == {"some_future_unpinned_dimension"}


# ================================= R1 doc↔ledger mirror =================================


def test_newest_history_mirrors_current_block() -> None:
    """R1 (HIGH) STANDING pin: the newest history entry per dimension content-matches
    the current machine block. Closes the upgrade-guard bypass — a doc inflation that
    never appends to scorecard-history.jsonl goes RED here, guaranteeing the guard
    gets a real prior on the next re-score. GREEN today (baseline mirrors the block)."""
    assert _mirror_violations(_real_block()) == []


def test_mirror_pin_reds_on_doc_inflation_without_history_append(tmp_path: Path) -> None:
    """R1 RED-under-seeded-edit: inflate a fixture block's score WITHOUT updating its
    paired newest-history entry → the mirror pin goes RED. Real files untouched."""
    import json as _json

    hist = tmp_path / "h.jsonl"
    hist.write_text(_json.dumps(_BASELINE_SNAPSHOT) + "\n", encoding="utf-8")
    block = copy.deepcopy(_real_block())
    block["dimensions"][_DID_KEY]["score"] = 80  # inflate; ledger still says 65
    violations = _mirror_violations(block, hist)
    assert any(_DID_KEY in v and "mirror" in v for v in violations), violations


# ================================= GL-11 computed-trend =================================


def test_trend_is_computed_not_painted() -> None:
    """AC3 / GL-11: the machine-block ``trend`` equals ``trend_from_history`` (delta
    vs the latest prior snapshot). Today both == 'baseline' (only the seeded 2026-
    07-19 entry exists). Doc↔code: the history log is the code source."""
    dim = _real_block()["dimensions"][_DID_KEY]
    assert dim["trend"] == trend_from_history(_DID_KEY) == "baseline"


def test_trend_pin_reds_on_hand_painted_arrow(tmp_path: Path) -> None:
    """AC5 RED-under-seeded-edit: a hand-painted ``trend: rising`` with no
    supporting history disagrees with the computed 'baseline' → the pin would go
    RED. (Uses a fixture empty/one-entry history — the real log is never touched.)"""
    empty = tmp_path / "empty.jsonl"
    empty.write_text("", encoding="utf-8")
    computed = trend_from_history(_DID_KEY, empty)
    assert computed == "baseline"
    painted = "rising"
    assert painted != computed  # doc's painted arrow contradicts the computed trend


def test_trend_computes_rising_and_falling(tmp_path: Path) -> None:
    """GL-11/GL-12 witness: with a real prior snapshot, the trend is COMPUTED from
    the score delta — so an honest 'rising'/'falling' is earned, not painted."""
    log = tmp_path / "h.jsonl"
    import json as _json

    prior = dict(_BASELINE_SNAPSHOT)
    rising = {**_BASELINE_SNAPSHOT, "as_of": "2026-08-01", "score": 72}
    log.write_text(
        _json.dumps(prior) + "\n" + _json.dumps(rising) + "\n", encoding="utf-8"
    )
    assert trend_from_history(_DID_KEY, log) == "rising"
    falling = {**_BASELINE_SNAPSHOT, "as_of": "2026-08-01", "score": 60}
    log.write_text(
        _json.dumps(prior) + "\n" + _json.dumps(falling) + "\n", encoding="utf-8"
    )
    assert trend_from_history(_DID_KEY, log) == "falling"


def test_trend_first_run_degrade_on_absent_history(tmp_path: Path) -> None:
    """GL-12 first-run degrade: an absent / empty history yields 'baseline', never a
    fabricated arrow."""
    assert trend_from_history(_DID_KEY, tmp_path / "nope.jsonl") == "baseline"
    empty = tmp_path / "empty.jsonl"
    empty.write_text("\n\n", encoding="utf-8")
    assert trend_from_history(_DID_KEY, empty) == "baseline"


# ================================= R4 history date-hardening =================================


def test_trend_degrades_on_malformed_newest_as_of(tmp_path: Path) -> None:
    """R4a: a malformed/missing ``as_of`` on the newest-APPENDED entry → 'baseline'
    (cannot trust the freshest write), rather than silently computing a trend off an
    older entry."""
    import json as _json

    log = tmp_path / "h.jsonl"
    good = dict(_BASELINE_SNAPSHOT)
    corrupt = {**_BASELINE_SNAPSHOT, "as_of": "not-a-date", "score": 90}
    log.write_text(
        _json.dumps(good) + "\n" + _json.dumps(corrupt) + "\n", encoding="utf-8"
    )
    assert trend_from_history(_DID_KEY, log) == "baseline"


def test_trend_uses_max_by_date_not_file_order(tmp_path: Path) -> None:
    """R4b: ``current`` is the max-BY-VALIDATED-DATE snapshot, not ``entries[-1]`` —
    an out-of-order append (an older-dated entry written last) cannot mislead the
    computed trend."""
    import json as _json

    log = tmp_path / "h.jsonl"
    newer = {**_BASELINE_SNAPSHOT, "as_of": "2026-08-01", "score": 72}
    older = {**_BASELINE_SNAPSHOT, "as_of": "2026-07-19", "score": 65}
    # file order: newer FIRST, older appended last (out of order)
    log.write_text(
        _json.dumps(newer) + "\n" + _json.dumps(older) + "\n", encoding="utf-8"
    )
    # current = max-by-date = 2026-08-01 (72); prior = 2026-07-19 (65) → rising.
    assert trend_from_history(_DID_KEY, log) == "rising"


def test_trend_same_date_tiebreak_is_later_in_file(tmp_path: Path) -> None:
    """R4c: when two entries share the max ``as_of``, the later-in-file entry wins
    (deterministic tie-break). Here the later same-day entry equals the prior score
    → 'flat'; if the tie-break were the earlier same-day entry it would be 'rising'."""
    import json as _json

    log = tmp_path / "h.jsonl"
    prior = {**_BASELINE_SNAPSHOT, "as_of": "2026-07-19", "score": 65}
    same_day_high = {**_BASELINE_SNAPSHOT, "as_of": "2026-08-01", "score": 70}
    same_day_low = {**_BASELINE_SNAPSHOT, "as_of": "2026-08-01", "score": 65}
    log.write_text(
        _json.dumps(prior)
        + "\n"
        + _json.dumps(same_day_high)
        + "\n"
        + _json.dumps(same_day_low)
        + "\n",
        encoding="utf-8",
    )
    # later-in-file same-day entry (65) wins → 65 vs prior 65 → flat.
    assert trend_from_history(_DID_KEY, log) == "flat"


# ================================= GL-11 evidence-gated upgrade =================================


def test_evidence_gated_upgrade_guard_holds_on_real_block() -> None:
    """AC3 / GL-11 STANDING pin over the real block + each dimension's real
    newest-strictly-prior history snapshot. Today the only snapshot shares the
    block's ``as_of`` → no strictly-prior → honest no-op; the mirror pin guarantees
    a real prior appears on the next re-score, activating this guard automatically."""
    block = _real_block()
    problems: dict[str, list[str]] = {}
    for dim_key, dim in block["dimensions"].items():
        prior = latest_prior_snapshot(dim_key, _as_str(dim.get("as_of")))
        v = evidence_gated_upgrade_violations(dim, prior)
        if v:
            problems[dim_key] = v
    assert problems == {}, problems
    # explicit no-op witness for DID today:
    did = block["dimensions"][_DID_KEY]
    assert latest_prior_snapshot(_DID_KEY, _as_str(did.get("as_of"))) is None


def test_upgrade_guard_reds_on_increase_without_as_verified_advance() -> None:
    """AC5 RED: C3 rises 1→3 but ``as_verified`` stays 2026-07-19 (only ``as_of``
    bumped — prose edited, evidence NOT re-checked) → guard FAILS. This is exactly
    why as_of/as_verified are split: a stale evidence citation must not suffice."""
    dim = _did_dim_with(
        lambda d: (
            d.update(as_of="2026-08-01", as_verified="2026-07-19"),
            d["criteria"]["fence_enforcement_default_on"].update(score=3),
        )
    )
    violations = evidence_gated_upgrade_violations(dim, _BASELINE_SNAPSHOT)
    assert any("as_verified" in v for v in violations), violations


def test_upgrade_guard_reds_on_increase_without_evidence_ref() -> None:
    """AC5 RED: C3 rises with ``as_verified`` advanced but its ``evidence_ref``
    emptied → guard FAILS (an increase must CITE evidence)."""
    dim = _did_dim_with(
        lambda d: (
            d.update(as_verified="2026-08-01"),
            d["criteria"]["fence_enforcement_default_on"].update(score=3, evidence_ref=""),
        )
    )
    violations = evidence_gated_upgrade_violations(dim, _BASELINE_SNAPSHOT)
    assert any("evidence_ref" in v for v in violations), violations


def test_upgrade_guard_conservative_on_malformed_prior_levels() -> None:
    """R5c: a prior snapshot MISSING its ``levels`` map (or with a non-numeric level)
    must NOT let a real increase slip — the guard treats it conservatively and still
    requires evidence + as_verified advance."""
    prior_no_levels = {**_BASELINE_SNAPSHOT}
    prior_no_levels.pop("levels")
    dim = _did_dim_with(
        lambda d: (
            d.update(as_of="2026-08-01", as_verified="2026-07-19"),  # NOT advanced
            d["criteria"]["fence_enforcement_default_on"].update(score=3),
        )
    )
    violations = evidence_gated_upgrade_violations(dim, prior_no_levels)
    assert any("as_verified" in v for v in violations), violations


def test_upgrade_guard_allows_earned_increase() -> None:
    """AC3 GREEN path: an increase that BOTH advances ``as_verified`` AND cites a
    (fresh) evidence_ref is allowed — a fence turned ON, re-verified on a new date."""
    dim = _did_dim_with(
        lambda d: (
            d.update(as_verified="2026-08-01"),
            d["criteria"]["fence_enforcement_default_on"].update(
                score=3, evidence_ref="§1.6 C3 · Leak 1 CLOSED — fences ON by default"
            ),
        )
    )
    assert evidence_gated_upgrade_violations(dim, _BASELINE_SNAPSHOT) == []


def test_upgrade_guard_allows_free_downgrade() -> None:
    """AC3: downgrades are FREE — lowering a score needs no evidence/as_verified
    advance."""
    dim = _did_dim_with(lambda d: d["criteria"]["neck_placement"].update(score=3))
    assert evidence_gated_upgrade_violations(dim, _BASELINE_SNAPSHOT) == []


# =============================================================================== #
# Story Q2.1 — cost_efficiency dimension honesty pins (the 3 registered in
# _HONESTY_PIN_REGISTRY[_COST_KEY]) + their RED-under-seeded proofs. These reuse the
# SAME pure helpers as the DID pins (_signal_derived_violations, _reconcile,
# _arithmetic_violations, _machine_block_leak_slugs) — the helpers already iterate
# EVERY dimension, so coverage is structural. Doc↔code: each compares a machine-block
# CLAIM against a CODE-computed reality (a signal reader / the deferred-inventory
# registry / the §2.5 arithmetic rule), never doc↔doc.
# =============================================================================== #


def _clear_budget_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MARCUS_TRIAL_BUDGET_USD", raising=False)


# --------------------------- pin (a) budget-fence-claim --------------------------- #


def test_cost_budget_fence_claim_matches_reader(monkeypatch: pytest.MonkeyPatch) -> None:
    """Pin (a) for cost_efficiency, GREEN today: the signal-derived CE1
    (``budget_stop_default_on``) level equals its reader's live output —
    ``level_from_signal("budget_stop_default_on", budget_stop_default_signal())`` ==
    ``weak`` (the env-INDEPENDENT production-preset posture: no default budget →
    ``check_trial_budget(total, None)=='no-cap'`` → opt-in). The shared
    ``_signal_derived_violations`` scan (over every dimension) is also clean."""
    _clear_budget_env(monkeypatch)
    _clear_fence_env(monkeypatch)
    block = _real_block()
    assert _signal_derived_violations(block) == []
    ce1 = block["dimensions"][_COST_KEY]["criteria"]["budget_stop_default_on"]
    derived = level_from_signal("budget_stop_default_on", budget_stop_default_signal())
    assert ce1["level"] == derived == "weak"


def test_cost_budget_fence_claim_reds_on_dishonest_level(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """AC3 / GL-9 RED-under-seeded-edit: bump CE1 to ``strong`` on an in-memory copy
    WITHOUT a default budget wired → the pin (a) comparison FAILS (reader still says
    ``weak``). The real doc is never touched. This is the exact anti-overclaim guard:
    a claimed budget-enforced/cost-fenced level cannot pass while the preset default is
    no-cap."""
    _clear_budget_env(monkeypatch)
    block = copy.deepcopy(_real_block())
    block["dimensions"][_COST_KEY]["criteria"]["budget_stop_default_on"][
        "level"
    ] = "strong"
    violations = _signal_derived_violations(block)
    assert any("budget_stop_default_on" in v for v in violations), violations


@pytest.mark.parametrize("dishonest", ["strong", "partial", "uniform"])
def test_cost_budget_fence_claim_reds_on_any_inflated_level(
    monkeypatch: pytest.MonkeyPatch, dishonest: str
) -> None:
    """AC3: any inflation of CE1 above the reader-derived ``weak`` (with no default
    budget wired) is caught."""
    _clear_budget_env(monkeypatch)
    block = copy.deepcopy(_real_block())
    block["dimensions"][_COST_KEY]["criteria"]["budget_stop_default_on"][
        "level"
    ] = dishonest
    assert _signal_derived_violations(block) != []


def test_cost_ce1_is_signal_derived_others_are_judgment_with_evidence() -> None:
    """The honest derivation split: CE1 is ``signal-derived`` (the reader owns the
    level); CE2/CE3/CE4 are ``judgment-with-evidence`` (a real signal block carries the
    facts, the level is an authored §2.6 judgment). No unverified signal awards a clean
    level: ``level_from_signal`` returns ``None`` for the judgment-with-evidence keys."""
    crit = _real_block()["dimensions"][_COST_KEY]["criteria"]
    assert crit["budget_stop_default_on"]["derivation"] == "signal-derived"
    for key in ("cost_posture_honesty", "cost_drift_monitoring", "cost_transparency"):
        c = crit[key]
        assert c["derivation"] == "judgment-with-evidence"
        assert c["level"] == "strong"
        assert isinstance(c["signal"], dict)
        assert c["signal"]["reader"].startswith("app.quality.signals.")
        assert isinstance(c["evidence_ref"], str) and c["evidence_ref"]
        # judgment-with-evidence → no mechanical derivation → never a clean auto-award.
        assert level_from_signal(key, c["signal"]) is None


# --------------------------- pin (b) cost leak-count + slug identity --------------- #


def test_cost_leak_count_reconciles_on_real_repo() -> None:
    """Pin (b) for cost_efficiency: the dimension's ``open_leaks`` == the count of
    ``cost_leak:``-tagged OPEN entries in the ``## Cost-Efficiency Scorecard Leak
    Registry`` == ``len(leaks)`` == 1. A per-dimension ``cost_leak:`` namespace (NOT the
    global DID ``did_leak:`` count — that would spuriously red per FIX-2). Anti-drift:
    strike the ``cost_leak:`` tag → count drops to 0, 1 != 0 → RED."""
    dim = _real_block()["dimensions"][_COST_KEY]
    count = cost_leak_count_signal()["cost_leak_count"]
    assert _reconcile(dim.get("open_leaks"), count), (
        f"{_COST_KEY}: open_leaks {dim.get('open_leaks')!r} != counted cost_leak: {count}"
    )
    leaks = dim.get("leaks")
    open_leaks = dim.get("open_leaks")
    if isinstance(leaks, list) and isinstance(open_leaks, int) and not isinstance(
        open_leaks, bool
    ):
        assert len(leaks) == open_leaks, (
            f"{_COST_KEY}: structured leaks len {len(leaks)} != open_leaks {open_leaks}"
        )


def test_cost_machine_block_leak_slugs_match_registry_identity() -> None:
    """AC4 reconcile-by-IDENTITY (retro AI-Q2) for cost_efficiency: SET EQUALITY of the
    machine-block ``leaks`` slugs vs the registry ``cost_leak:`` slugs — a slug typo /
    rename that keeps the count at 1 is caught here, which a count-only reconciliation
    misses."""
    dim = _real_block()["dimensions"][_COST_KEY]
    assert _machine_block_leak_slugs(dim) == _registry_cost_leak_slugs()


def test_cost_slug_identity_reds_on_seeded_typo_while_count_stays_green() -> None:
    """AC4 RED-first: typo the cost machine-block leak slug on a COPY → the identity pin
    RED (set inequality) while the count still reconciles (len==open_leaks==1)."""
    block = copy.deepcopy(_real_block())
    dim = block["dimensions"][_COST_KEY]
    dim["leaks"][0]["slug"] = "cost-efficiency-typo"
    assert _machine_block_leak_slugs(dim) != _registry_cost_leak_slugs()
    assert len(dim["leaks"]) == dim["open_leaks"] == 1


# --------------------------- pin (c) cost score-arithmetic ------------------------ #


def test_cost_score_arithmetic_is_internally_consistent() -> None:
    """Pin (c) for cost_efficiency: score↔level per §2.5 + Σscore/max→/100 == headline
    + band == the shared §1.5/§2.5 boundary. 1+3+3+3 = 10/16 → 62 → B-. Doc↔code: the
    arithmetic RULE is the code source (``_arithmetic_violations``)."""
    dim = _real_block()["dimensions"][_COST_KEY]
    assert _arithmetic_violations(dim) == [], _arithmetic_violations(dim)
    assert dim["score"] == 62 and dim["band"] == "B-"
