"""AC-T.5 (M-AM-3 extended) + AC-T.5b (Q-R2-A cross-field) — ProducedAsset.fulfills tests."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.marcus.lesson_plan.produced_asset import ProducedAsset


def _build_asset(
    *,
    source_plan_unit_id: str = "unit-a",
    fulfills: str = "unit-a@1",
) -> ProducedAsset:
    return ProducedAsset(
        asset_ref="x",
        modality_ref="slides",
        source_plan_unit_id=source_plan_unit_id,
        asset_path="x.md",
        fulfills=fulfills,
    )


# ---------------------------------------------------------------------------
# AC-T.5 ACCEPT matrix (M-AM-3 extended)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "unit_id, fulfills",
    [
        ("gagne-event-3", "gagne-event-3@5"),
        ("gagne-event-1", "gagne-event-1@0"),  # bootstrap revision
        ("custom.unit_id", "custom.unit_id@999"),
        ("a", "a@1"),  # minimum length
        ("unit_with-dots.and_underscores", "unit_with-dots.and_underscores@42"),
        ("unit-with-dashes", "unit-with-dashes@1"),
        ("u", "u@0"),  # zero revision legal
        (
            "a-very-very-long-unit-id-exceeding-50-chars-but-still-valid",
            "a-very-very-long-unit-id-exceeding-50-chars-but-still-valid@42",
        ),
    ],
)
def test_fulfills_accept_matrix(unit_id: str, fulfills: str) -> None:
    asset = _build_asset(source_plan_unit_id=unit_id, fulfills=fulfills)
    assert asset.fulfills == fulfills


# ---------------------------------------------------------------------------
# AC-T.5 REJECT matrix (M-AM-3 extended)
# ---------------------------------------------------------------------------


_REJECT_CASES_REGEX = [
    ("no-at-sign", "no-at-sign"),
    ("empty@", "empty@"),
    ("@empty", "@empty"),
    ("  @  ", "  @  "),  # whitespace both sides
    ("  gagne-event-3@5  ", "  gagne-event-3@5  "),  # leading/trailing whitespace
    ("a@b@c", "a@b@c"),  # multi-@
    ("GAGNE-EVENT-3@5", "GAGNE-EVENT-3@5"),  # uppercase
    ("UPPER@1", "UPPER@1"),  # uppercase
    ("Gagné-event@1", "Gagné-event@1"),  # unicode in unit_id fails _OPEN_ID_REGEX
    ("gagne-event-3@-1", "gagne-event-3@-1"),  # negative revision
    ("gagne-event-3@ 5", "gagne-event-3@ 5"),  # internal whitespace
    ("", ""),  # empty string
    ("@", "@"),  # bare @
    ("gagne event@5", "gagne event@5"),  # internal space
    ("gagne-event@1.5", "gagne-event@1.5"),  # float revision
    ("unit@abc", "unit@abc"),  # non-integer revision
    ("unit@007", "unit@007"),  # leading-zero revision (M-AM-3 strict-monotonic)
]


@pytest.mark.parametrize(
    "label, fulfills",
    _REJECT_CASES_REGEX,
    ids=[label for label, _ in _REJECT_CASES_REGEX],
)
def test_fulfills_reject_matrix(label: str, fulfills: str) -> None:  # noqa: ARG001
    """Every reject case raises ValidationError whose message cites the value."""
    with pytest.raises(ValidationError) as exc_info:
        _build_asset(
            # Use a matching source_plan_unit_id so the Q-R2-A cross-field
            # validator can't fire first. For regex-only rejection, we want
            # source to match the (malformed) fulfills prefix if splittable;
            # otherwise any plausible value. The fulfills regex validator
            # raises before the model_validator runs.
            source_plan_unit_id="placeholder",
            fulfills=fulfills,
        )
    msg = str(exc_info.value)
    # The regex validator message cites the failing value (via repr).
    assert "fails regex" in msg or "must be a string" in msg, (
        f"Expected regex-failure message; got: {msg[:400]}"
    )


# ---------------------------------------------------------------------------
# Type rejection tests (M-AM-3)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "bad_value",
    [
        pytest.param(123, id="int"),
        pytest.param(None, id="None"),
        pytest.param(["a", "b"], id="list"),
    ],
)
def test_fulfills_type_rejection(bad_value) -> None:
    with pytest.raises(ValidationError):
        _build_asset(fulfills=bad_value)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# AC-T.5b — Q-R2-A cross-field (counterfeit-fulfillment seam)
# ---------------------------------------------------------------------------


def test_q_r2_a_matching_pair_is_accepted() -> None:
    asset = _build_asset(source_plan_unit_id="unit-foo", fulfills="unit-foo@5")
    assert asset.source_plan_unit_id == "unit-foo"
    assert asset.fulfills == "unit-foo@5"


def test_q_r2_a_bootstrap_zero_revision_is_accepted() -> None:
    asset = _build_asset(source_plan_unit_id="unit-a", fulfills="unit-a@0")
    assert asset.fulfills == "unit-a@0"


@pytest.mark.parametrize(
    "source, fulfills",
    [
        ("unit-foo", "unit-bar@5"),
        ("gagne-event-1", "gagne-event-2@0"),
        ("a", "b@42"),
    ],
)
def test_q_r2_a_counterfeit_mismatch_is_rejected(source: str, fulfills: str) -> None:
    with pytest.raises(ValidationError) as exc_info:
        _build_asset(source_plan_unit_id=source, fulfills=fulfills)
    msg = str(exc_info.value)
    assert "counterfeit-fulfillment seam" in msg, (
        f"Q-R2-A error message must contain 'counterfeit-fulfillment seam'; "
        f"got: {msg[:400]}"
    )
    assert "source_plan_unit_id" in msg
    assert source in msg
    # fulfills unit_id portion is mentioned (not full fulfills string needed)
    fulfills_uid = fulfills.split("@", 1)[0]
    assert fulfills_uid in msg


def test_q_r2_a_error_names_tri_phasic_contract() -> None:
    with pytest.raises(ValidationError) as exc_info:
        _build_asset(source_plan_unit_id="unit-a", fulfills="unit-b@1")
    assert "tri-phasic contract violation" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Integration: counterfeit triggers Q-R2-A only AFTER regex passes
# ---------------------------------------------------------------------------


def test_regex_failure_preempts_cross_field_validator() -> None:
    """A malformed fulfills fails the regex validator; model_validator never runs."""
    with pytest.raises(ValidationError) as exc_info:
        _build_asset(source_plan_unit_id="unit-a", fulfills="no-at-sign")
    msg = str(exc_info.value)
    assert "fails regex" in msg
    # The counterfeit message should NOT appear because the field validator
    # blocked it first.
    assert "counterfeit-fulfillment seam" not in msg


# ---------------------------------------------------------------------------
# party-mode 2026-04-19 follow-on: source_plan_unit_id regex pin (was 31-3 SHOULD-FIX#1)
# Closes the trust-the-caller hole where a non-PlanUnit producer could synthesize
# a malformed identifier passing only min_length=1.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "malformed_id",
    [
        "UPPER-CASE",       # uppercase rejected
        "has space",        # whitespace rejected
        "with/slash",       # slash rejected
        "with:colon",       # colon rejected
        "tab\there",        # tab rejected
        "trailing\n",       # newline rejected
    ],
)
def test_source_plan_unit_id_regex_rejects_malformed(malformed_id: str) -> None:
    """Malformed ``source_plan_unit_id`` must fail Pydantic regex validation."""
    with pytest.raises(ValidationError):
        _build_asset(
            source_plan_unit_id=malformed_id,
            fulfills=f"{malformed_id}@5",
        )


def test_source_plan_unit_id_regex_accepts_open_id_chars() -> None:
    """Lowercase + digits + ``._-`` are accepted (matches PlanUnit.unit_id format)."""
    asset = _build_asset(
        source_plan_unit_id="gagne-event-3.v2_alt",
        fulfills="gagne-event-3.v2_alt@7",
    )
    assert asset.source_plan_unit_id == "gagne-event-3.v2_alt"
