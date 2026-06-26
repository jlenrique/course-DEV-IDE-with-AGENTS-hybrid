"""S4 — curated bundle catalog: shape-pin, composer wiring, capability-tier honesty.

The catalog is the declarative layer the S5 front door reads to honestly grey out
or flag bundles whose components are not yet proven. These tests pin:
  * the ratified 3 bundles exist with the expected component sets;
  * each bundle's ComponentSelection composes via the REAL composer (not just data);
  * the capability-tier query reports min-tier readiness correctly;
  * closed-enum rejection on unknown bundle id / unknown tier;
  * registry immutability (MappingProxyType / frozen).
"""

from __future__ import annotations

import pytest

from app.manifest import load
from app.manifest.lanes import DEFAULT_RUN_MANIFEST_PATH
from app.marcus.lesson_plan import bundle_catalog as bc
from app.marcus.lesson_plan.composition import compose_manifest
from app.models.state.component_selection import ComponentSelection

# ---------------------------------------------------------------------------
# 1. Catalog shape-pin: the 3 ratified bundles with expected component sets
# ---------------------------------------------------------------------------


def test_catalog_has_exactly_the_three_ratified_bundles() -> None:
    assert set(bc.BUNDLE_CATALOG) == {
        "narrated-deck",
        "narrated-deck-with-motion",
        "narrated-deck-with-workbook",
    }


def test_b1_narrated_deck_is_deck_only() -> None:
    rec = bc.BUNDLE_CATALOG["narrated-deck"]
    assert rec.selection.selected_components() == ("deck",)
    assert rec.selection == ComponentSelection(deck=True, motion=False, workbook=False)


def test_b2_with_motion_is_deck_and_motion() -> None:
    rec = bc.BUNDLE_CATALOG["narrated-deck-with-motion"]
    assert rec.selection.selected_components() == ("deck", "motion")
    assert rec.selection == ComponentSelection(deck=True, motion=True, workbook=False)


def test_b3_with_workbook_is_deck_motion_workbook() -> None:
    rec = bc.BUNDLE_CATALOG["narrated-deck-with-workbook"]
    assert rec.selection.selected_components() == ("deck", "motion", "workbook")
    assert rec.selection == ComponentSelection(deck=True, motion=True, workbook=True)


def test_every_bundle_record_carries_display_metadata() -> None:
    for bundle_id, rec in bc.BUNDLE_CATALOG.items():
        assert rec.id == bundle_id
        assert rec.display_name.strip()
        assert rec.description.strip()
        assert rec.required_inputs  # non-empty


def test_required_inputs_are_additive_b1_subset_b2_subset_b3() -> None:
    b1 = set(bc.BUNDLE_CATALOG["narrated-deck"].required_inputs)
    b2 = set(bc.BUNDLE_CATALOG["narrated-deck-with-motion"].required_inputs)
    b3 = set(bc.BUNDLE_CATALOG["narrated-deck-with-workbook"].required_inputs)
    assert "corpus_path" in b1
    assert b1 <= b2 <= b3


# ---------------------------------------------------------------------------
# 2. Composer wiring: each bundle's selection composes WITHOUT error
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "bundle_id",
    ["narrated-deck", "narrated-deck-with-motion", "narrated-deck-with-workbook"],
)
def test_each_bundle_selection_composes_via_real_composer(bundle_id: str) -> None:
    """Proves the catalog is wired to the real composer, not just inert data."""
    manifest = load(DEFAULT_RUN_MANIFEST_PATH)
    rec = bc.BUNDLE_CATALOG[bundle_id]
    composed = compose_manifest(manifest, rec.selection)
    assert composed.nodes  # a real, non-empty composed manifest


def test_workbook_bundle_composes_a_distinct_graph_from_motion_bundle() -> None:
    manifest = load(DEFAULT_RUN_MANIFEST_PATH)
    b2 = compose_manifest(
        manifest, bc.BUNDLE_CATALOG["narrated-deck-with-motion"].selection
    )
    b3 = compose_manifest(
        manifest, bc.BUNDLE_CATALOG["narrated-deck-with-workbook"].selection
    )
    b2_ids = {n.id for n in b2.nodes}
    b3_ids = {n.id for n in b3.nodes}
    assert b3_ids != b2_ids
    assert b3_ids - b2_ids  # workbook adds at least one node (the stub)


# ---------------------------------------------------------------------------
# 3. Capability-tier query: min-tier readiness logic
# ---------------------------------------------------------------------------


def test_seed_capability_tiers_reflect_current_reality() -> None:
    assert bc.component_capability("deck").tier == "proven_wired"
    assert bc.component_capability("motion").tier == "proven_regressed_repairable"
    assert bc.component_capability("workbook").tier == "mechanism_only_never_produced"


def test_b1_is_fully_proven() -> None:
    assert bc.min_capability_tier("narrated-deck") == "proven_wired"
    assert bc.bundle_readiness("narrated-deck") == "fully_proven"


def test_b2_is_partial_because_motion_is_regressed() -> None:
    assert bc.min_capability_tier("narrated-deck-with-motion") == (
        "proven_regressed_repairable"
    )
    assert bc.bundle_readiness("narrated-deck-with-motion") == "partial"


def test_b3_is_not_yet_because_workbook_is_mechanism_only() -> None:
    assert bc.min_capability_tier("narrated-deck-with-workbook") == (
        "mechanism_only_never_produced"
    )
    assert bc.bundle_readiness("narrated-deck-with-workbook") == "not_yet"


def test_readiness_accepts_a_record_too() -> None:
    rec = bc.BUNDLE_CATALOG["narrated-deck"]
    assert bc.bundle_readiness(rec) == "fully_proven"
    assert bc.min_capability_tier(rec) == "proven_wired"


def test_get_bundle_returns_none_for_unknown() -> None:
    assert bc.get_bundle("no-such-bundle") is None
    assert bc.get_bundle("narrated-deck") is bc.BUNDLE_CATALOG["narrated-deck"]


def test_query_on_unknown_bundle_id_raises() -> None:
    with pytest.raises(KeyError):
        bc.bundle_readiness("no-such-bundle")
    with pytest.raises(KeyError):
        bc.min_capability_tier("no-such-bundle")


# ---------------------------------------------------------------------------
# 4. Closed-enum red-rejection
# ---------------------------------------------------------------------------


def test_unknown_bundle_id_rejected_at_construction() -> None:
    with pytest.raises(Exception):  # noqa: B017 — pydantic ValidationError on closed enum
        bc.BundleRecord(
            id="podcast-bundle",  # type: ignore[arg-type]
            display_name="x",
            selection=ComponentSelection(),
            required_inputs=("corpus_path",),
            description="x",
        )


def test_unknown_tier_rejected_at_construction() -> None:
    with pytest.raises(Exception):  # noqa: B017
        bc.ComponentCapability(component="deck", tier="experimental")  # type: ignore[arg-type]


def test_unknown_component_rejected_at_construction() -> None:
    with pytest.raises(Exception):  # noqa: B017
        bc.ComponentCapability(component="podcast", tier="shelf")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 5. Registry immutability
# ---------------------------------------------------------------------------


def test_bundle_catalog_is_immutable() -> None:
    with pytest.raises(TypeError):
        bc.BUNDLE_CATALOG["narrated-deck"] = None  # type: ignore[index]


def test_capability_registry_is_immutable() -> None:
    with pytest.raises(TypeError):
        bc.CAPABILITY_TIERS["deck"] = None  # type: ignore[index]


def test_bundle_record_is_frozen() -> None:
    rec = bc.BUNDLE_CATALOG["narrated-deck"]
    with pytest.raises(Exception):  # noqa: B017 — frozen ValidationError
        rec.display_name = "mutated"  # type: ignore[misc]
