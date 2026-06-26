"""S5 — Marcus-SPOC FRONT DOOR: the bundle selection turn (offline dev-agent ACs).

The front door presents the 3 catalog bundles WITH honest readiness from
``bundle_readiness()``: fully_proven is selectable; partial/not_yet are shown but
FLAGGED so Marcus can never run an unproven bundle as if complete. The
deterministic guard is LOAD-BEARING: an LLM/model RECOMMENDATION is advisory and
NEVER auto-selects — only the operator's explicit, confirmed, runnable pick
yields a :class:`FrontDoorSelection`. The live HIL leg is deferred to a real run.
"""

from __future__ import annotations

import pytest

from app.marcus.cli import front_door as fd
from app.models.state.component_selection import ComponentSelection

# ---------------------------------------------------------------------------
# 1. present_catalog — all 3 bundles with correct, honest readiness
# ---------------------------------------------------------------------------


def test_present_catalog_lists_all_three_bundles_with_readiness() -> None:
    options = {opt.bundle_id: opt for opt in fd.present_catalog()}
    assert set(options) == {
        "narrated-deck",
        "narrated-deck-with-motion",
        "narrated-deck-with-workbook",
    }
    assert options["narrated-deck"].readiness == "fully_proven"
    assert options["narrated-deck-with-motion"].readiness == "partial"
    assert options["narrated-deck-with-workbook"].readiness == "not_yet"


def test_only_fully_proven_is_selectable_others_flagged() -> None:
    options = {opt.bundle_id: opt for opt in fd.present_catalog()}
    b1 = options["narrated-deck"]
    b2 = options["narrated-deck-with-motion"]
    b3 = options["narrated-deck-with-workbook"]
    assert b1.selectable is True and b1.flag is None
    assert b2.selectable is False and b2.flag  # flagged: proven but pending repair
    assert b3.selectable is False and b3.flag  # flagged: not yet built


def test_render_catalog_surfaces_honest_flags_for_unproven_bundles() -> None:
    text = fd.render_catalog()
    assert "narrated-deck" in text
    # The two non-fully-proven bundles must be visibly flagged, not hidden.
    assert "narrated-deck-with-motion" in text
    assert "narrated-deck-with-workbook" in text
    lowered = text.lower()
    assert "pending repair" in lowered  # motion flag
    assert "not yet" in lowered  # workbook flag


# ---------------------------------------------------------------------------
# 2. front_door_select — operator's confirmed pick of B1 -> ComponentSelection{deck}
# ---------------------------------------------------------------------------


def test_pick_b1_returns_deck_only_selection_and_carries_seeds() -> None:
    result = fd.front_door_select(
        operator_pick="narrated-deck",
        confirmed=True,
        seeds={"corpus_path": "course-content/courses/demo"},
    )
    assert isinstance(result, fd.FrontDoorSelection)
    assert result.bundle_id == "narrated-deck"
    assert result.selection == ComponentSelection(deck=True, motion=False, workbook=False)
    assert result.selection.selected_components() == ("deck",)
    assert result.seeds["corpus_path"] == "course-content/courses/demo"


# ---------------------------------------------------------------------------
# 3. Capability gate — a not-fully-proven bundle is NOT silently runnable
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "bundle_id",
    ["narrated-deck-with-motion", "narrated-deck-with-workbook"],
)
def test_unproven_bundle_is_not_runnable(bundle_id: str) -> None:
    with pytest.raises(fd.BundleNotRunnableError):
        fd.front_door_select(
            operator_pick=bundle_id,
            confirmed=True,
            seeds={"corpus_path": "course-content/courses/demo"},
        )


def test_unproven_bundle_runnable_only_under_explicit_override() -> None:
    # The flag is honest, not a hard wall: an EXPLICIT override (a real run that
    # accepts the regressed/pending status) is the only way through.
    result = fd.front_door_select(
        operator_pick="narrated-deck-with-motion",
        confirmed=True,
        seeds={"corpus_path": "course-content/courses/demo"},
        allow_unproven=True,
    )
    assert result.selection == ComponentSelection(deck=True, motion=True, workbook=False)


# ---------------------------------------------------------------------------
# 4. Deterministic guard — model NEVER auto-selects; operator pick proceeds
# ---------------------------------------------------------------------------


def test_hallucinated_pick_is_refused_and_drives_engine_zero_times() -> None:
    drive_calls: list[object] = []

    def _drive(selection: fd.FrontDoorSelection) -> None:
        drive_calls.append(selection)

    with pytest.raises(fd.UnknownBundleError):
        sel = fd.front_door_select(
            operator_pick="narrated-deck-with-everything",  # hallucinated id
            confirmed=True,
            seeds={"corpus_path": "course-content/courses/demo"},
        )
        _drive(sel)  # never reached

    assert drive_calls == []  # ZERO engine drives on an invalid pick


def test_model_recommendation_is_advisory_and_never_overrides_operator_pick() -> None:
    # The model recommends a (hallucinated/other) bundle; the operator picks B1.
    # The recommendation must NOT change what proceeds.
    result = fd.front_door_select(
        operator_pick="narrated-deck",
        confirmed=True,
        seeds={"corpus_path": "course-content/courses/demo"},
        recommendation="narrated-deck-with-workbook",  # advisory only
    )
    assert result.bundle_id == "narrated-deck"
    assert result.selection == ComponentSelection(deck=True, motion=False, workbook=False)


def test_unconfirmed_pick_does_not_proceed() -> None:
    with pytest.raises(fd.SelectionNotConfirmedError):
        fd.front_door_select(
            operator_pick="narrated-deck",
            confirmed=False,
            seeds={"corpus_path": "course-content/courses/demo"},
        )


def test_missing_required_seed_is_refused() -> None:
    with pytest.raises(fd.MissingRequiredInputError):
        fd.front_door_select(
            operator_pick="narrated-deck",
            confirmed=True,
            seeds={},  # corpus_path missing
        )


# ---------------------------------------------------------------------------
# 5. Interactive turn — HIL loop honors the guard (offline, injected IO)
# ---------------------------------------------------------------------------


def test_interactive_turn_returns_operator_confirmed_selectable_pick() -> None:
    inputs = iter(["narrated-deck", "yes"])
    out: list[str] = []
    result = fd.run_front_door(
        input_fn=lambda _prompt: next(inputs),
        output_sink=out.append,
        seeds={"corpus_path": "course-content/courses/demo"},
        recommend_fn=lambda _opts: "narrated-deck-with-workbook",  # advisory
    )
    assert result.bundle_id == "narrated-deck"
    assert result.selection == ComponentSelection(deck=True, motion=False, workbook=False)
    # the advisory recommendation was surfaced but did NOT drive the choice
    assert any("advisory" in line.lower() for line in out)


def test_interactive_turn_refuses_flagged_bundle_then_accepts_selectable() -> None:
    # Operator first tries the flagged motion bundle; the front door refuses to
    # run it as complete, then accepts the selectable deck bundle.
    inputs = iter(["narrated-deck-with-motion", "narrated-deck", "yes"])
    out: list[str] = []
    result = fd.run_front_door(
        input_fn=lambda _prompt: next(inputs),
        output_sink=out.append,
        seeds={"corpus_path": "course-content/courses/demo"},
    )
    assert result.bundle_id == "narrated-deck"
    assert any("flag" in line.lower() or "won't run" in line.lower() for line in out)
