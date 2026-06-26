"""Status-conditional invariant table + enum red-rejection + adequacy rules.

Story G0-S1 AC-S1-1 / AC-S1-2 / AC-S1-4. RED-first.

Central advisory contract (ratification 3.1): the LO status invariants assert
adequacy PRESENCE only; the adequacy VERDICT value (thin/gap) is never part of
any LO invariant and never gates a transition.
"""

from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError

from app.marcus.lesson_plan.learning_objective import (
    AdequacyFollowup,
    AdequacyVerdict,
    BloomLevel,
    Confidence,
    LearningObjective,
    LOStatus,
    SourceAdequacy,
    SourceRef,
)


def _ref() -> SourceRef:
    return SourceRef(source_id="s1", locator="p1", quoted_span="the span")


def _adq(verdict: str = "adequate", missing: list[str] | None = None) -> SourceAdequacy:
    if missing is None:
        missing = [] if verdict == "adequate" else ["the assess-leg"]
    return SourceAdequacy(verdict=verdict, rationale="r", missing=missing)  # type: ignore[arg-type]


def _lo(**overrides) -> LearningObjective:
    base = {
        "objective_id": "obj-1",
        "statement": "Analyze the macro trends",
        "status": "provisional",
        "confidence": "medium",
    }
    base.update(overrides)
    return LearningObjective(**base)


# --------------------------------------------------------------------------- #
# AC-S1-2 — status invariant table, every cell                                #
# --------------------------------------------------------------------------- #
def test_provisional_minimal_is_valid() -> None:
    lo = _lo()
    assert lo.status == "provisional"
    assert lo.source_refs == ()
    assert lo.adequacy is None
    assert lo.bloom_level is None


def test_provisional_allows_zero_source_refs_and_null_adequacy() -> None:
    lo = _lo(source_refs=[], adequacy=None, bloom_level=None)
    assert lo.source_refs == ()


def test_provisional_recommend_drop_channel_is_valid() -> None:
    # Ratification 3 (e-channel): an LO held at provisional + adequacy.verdict=gap
    # + recommendation=drop is a VALID shape (provisional places no positive
    # adequacy requirement). Proves provisional does not forbid adequacy.
    lo = _lo(
        adequacy=_adq("gap", missing=["any source support"]),
        recommendation="drop",
    )
    assert lo.status == "provisional"
    assert lo.adequacy is not None
    assert lo.adequacy.verdict == "gap"
    assert lo.recommendation == "drop"


def test_refined_requires_at_least_one_source_ref() -> None:
    with pytest.raises(ValidationError):
        _lo(status="refined", source_refs=[], adequacy=_adq())


def test_refined_requires_adequacy_present() -> None:
    with pytest.raises(ValidationError):
        _lo(status="refined", source_refs=[_ref()], adequacy=None)


def test_refined_with_refs_and_adequacy_is_valid() -> None:
    lo = _lo(status="refined", source_refs=[_ref()], adequacy=_adq())
    assert lo.status == "refined"


def test_refined_does_not_require_bloom_level() -> None:
    lo = _lo(status="refined", source_refs=[_ref()], adequacy=_adq(), bloom_level=None)
    assert lo.bloom_level is None


def test_ratified_requires_bloom_level() -> None:
    with pytest.raises(ValidationError):
        _lo(
            status="ratified",
            source_refs=[_ref()],
            adequacy=_adq(),
            bloom_level=None,
        )


def test_ratified_requires_source_refs_and_adequacy_too() -> None:
    with pytest.raises(ValidationError):
        _lo(status="ratified", source_refs=[], adequacy=_adq(), bloom_level="analyze")
    with pytest.raises(ValidationError):
        _lo(
            status="ratified",
            source_refs=[_ref()],
            adequacy=None,
            bloom_level="analyze",
        )


def test_ratified_with_everything_is_valid() -> None:
    lo = _lo(
        status="ratified",
        source_refs=[_ref()],
        adequacy=_adq(),
        bloom_level="analyze",
    )
    assert lo.status == "ratified"


# --------------------------------------------------------------------------- #
# validate_assignment re-checks the table on mutation                         #
# --------------------------------------------------------------------------- #
def test_mutating_status_to_refined_without_substrate_rejects() -> None:
    lo = _lo()
    with pytest.raises(ValidationError):
        lo.status = "refined"


def test_mutating_source_refs_empty_on_refined_rejects() -> None:
    lo = _lo(status="refined", source_refs=[_ref()], adequacy=_adq())
    with pytest.raises(ValidationError):
        lo.source_refs = []


def test_source_refs_is_an_immutable_tuple() -> None:
    # T11: a list source_refs could be emptied IN PLACE (.clear()/.pop()) on a
    # refined/ratified LO, silently dropping below the >=1 floor without firing
    # validate_assignment. A tuple makes in-place mutation impossible.
    lo = _lo(status="refined", source_refs=[_ref()], adequacy=_adq())
    assert isinstance(lo.source_refs, tuple)
    with pytest.raises(AttributeError):
        lo.source_refs.clear()  # type: ignore[attr-defined]


def test_model_copy_update_bypasses_validation_documented_limitation() -> None:
    # T11 honesty: model_copy(update=...) does NOT re-run validators (a documented
    # Pydantic-v2 behavior). This test PINS that reality so it is a known,
    # intentional limitation rather than a silent surprise: callers MUST route
    # transitions through advance_lo (which re-validates), never model_copy.
    lo = _lo()  # provisional, no refs/adequacy/bloom
    bypassed = lo.model_copy(update={"status": "ratified"})
    # The value invariants are NOT enforced on this path -> an inconsistent
    # object is produced. Documented; advance_lo is the sanctioned path.
    assert bypassed.status == "ratified"
    assert bypassed.source_refs == ()


# --------------------------------------------------------------------------- #
# objective_id open-id anchoring (T11: fullmatch, not match)                   #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("bad_id", ["obj-1\n", "obj-1\nmore", "obj 1", "OBJ-1", "obj/1", ""])
def test_objective_id_rejects_non_fullmatch(bad_id: str) -> None:
    # A trailing newline ("obj-1\n") slips past `^...$` under re.match because $
    # matches before a terminal \n -- and this id becomes the DB key. fullmatch
    # anchors the whole string.
    with pytest.raises(ValidationError):
        _lo(objective_id=bad_id)


# --------------------------------------------------------------------------- #
# SourceRef non-empty fields (T11: the refined+ provenance floor must be real) #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("field", ["source_id", "locator", "quoted_span"])
@pytest.mark.parametrize("empty", ["", "   ", "\t"])
def test_source_ref_rejects_empty_field(field: str, empty: str) -> None:
    base = {"source_id": "s1", "locator": "p1", "quoted_span": "span"}
    base[field] = empty
    with pytest.raises(ValidationError):
        SourceRef(**base)


def test_refined_lo_with_empty_source_ref_is_rejected() -> None:
    # The whole point of A9: a refined LO with one all-empty SourceRef must NOT
    # satisfy the >=1 provenance floor with zero real provenance.
    with pytest.raises(ValidationError):
        _lo(
            status="refined",
            source_refs=[SourceRef(source_id="", locator="", quoted_span="")],
            adequacy=_adq(),
        )


# --------------------------------------------------------------------------- #
# AC-S1-2 — adequacy is ADVISORY: verdict VALUE never part of any LO invariant #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("verdict", ["adequate", "thin", "gap"])
def test_refined_lo_valid_for_every_adequacy_verdict(verdict: str) -> None:
    # The LO is equally valid at refined regardless of the verdict value: only
    # adequacy PRESENCE is asserted, never thin-vs-gap-vs-adequate.
    lo = _lo(
        status="refined",
        source_refs=[_ref()],
        adequacy=_adq(verdict),
    )
    assert lo.adequacy is not None
    assert lo.adequacy.verdict == verdict


@pytest.mark.parametrize("verdict", ["adequate", "thin", "gap"])
def test_ratified_lo_valid_for_every_adequacy_verdict(verdict: str) -> None:
    lo = _lo(
        status="ratified",
        source_refs=[_ref()],
        adequacy=_adq(verdict),
        bloom_level="evaluate",
    )
    assert lo.adequacy is not None
    assert lo.adequacy.verdict == verdict


# --------------------------------------------------------------------------- #
# SourceAdequacy internal well-formedness (missing cardinality, NOT a gate)    #
# --------------------------------------------------------------------------- #
def test_adequate_allows_empty_missing() -> None:
    adq = SourceAdequacy(verdict="adequate", rationale="all clauses covered", missing=[])
    assert adq.missing == []


@pytest.mark.parametrize("verdict", ["thin", "gap"])
def test_thin_or_gap_requires_nonempty_concrete_missing(verdict: str) -> None:
    with pytest.raises(ValidationError):
        SourceAdequacy(verdict=verdict, rationale="r", missing=[])  # type: ignore[arg-type]
    with pytest.raises(ValidationError):
        # whitespace-only is not concrete
        SourceAdequacy(verdict=verdict, rationale="r", missing=["  "])  # type: ignore[arg-type]


@pytest.mark.parametrize("verdict", ["thin", "gap"])
def test_thin_or_gap_with_concrete_missing_is_valid(verdict: str) -> None:
    adq = SourceAdequacy(
        verdict=verdict,  # type: ignore[arg-type]
        rationale="the assess-leg is absent",
        missing=["a worked numeric example for the 23% figure"],
    )
    assert adq.missing


def test_suggested_followups_default_empty() -> None:
    adq = SourceAdequacy(verdict="adequate", rationale="r", missing=[])
    assert adq.suggested_followups == []


# --------------------------------------------------------------------------- #
# AC-S1-4 — closed-enum three-surface red rejection                           #
# --------------------------------------------------------------------------- #
_ENUM_CASES = [
    (
        BloomLevel,
        ["remember", "understand", "apply", "analyze", "evaluate", "create"],
        "synthesize",
    ),
    (LOStatus, ["provisional", "refined", "ratified"], "draft"),
    (Confidence, ["high", "medium", "low"], "certain"),
    (AdequacyVerdict, ["adequate", "thin", "gap"], "perfect"),
    (
        AdequacyFollowup,
        ["research-run", "external-content-expected", "special-artifact-guidance"],
        "ignore-it",
    ),
]


@pytest.mark.parametrize("enum_type,valid,bad", _ENUM_CASES)
def test_enum_type_adapter_round_trip_rejects_red(enum_type, valid, bad) -> None:
    # Surface 3: external validators (TypeAdapter) see the same closed set.
    adapter = TypeAdapter(enum_type)
    for value in valid:
        assert adapter.validate_python(value) == value
    with pytest.raises(ValidationError):
        adapter.validate_python(bad)


def test_bloom_level_rejects_red_on_construction_and_assignment() -> None:
    # Surface 1: the Pydantic validator (construction + assignment).
    with pytest.raises(ValidationError):
        _lo(
            status="ratified",
            source_refs=[_ref()],
            adequacy=_adq(),
            bloom_level="synthesize",
        )
    lo = _lo(status="refined", source_refs=[_ref()], adequacy=_adq())
    with pytest.raises(ValidationError):
        lo.bloom_level = "synthesize"  # type: ignore[assignment]


def test_status_rejects_red_on_construction() -> None:
    with pytest.raises(ValidationError):
        _lo(status="draft")


def test_confidence_rejects_red_on_construction() -> None:
    with pytest.raises(ValidationError):
        _lo(confidence="certain")


def test_adequacy_verdict_rejects_red_on_construction() -> None:
    with pytest.raises(ValidationError):
        SourceAdequacy(verdict="perfect", rationale="r", missing=["x"])  # type: ignore[arg-type]
