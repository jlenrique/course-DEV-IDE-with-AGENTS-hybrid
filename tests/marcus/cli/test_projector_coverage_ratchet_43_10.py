"""Story 43-10 — projector coverage ratchet (RED-first acceptance ratchet).

This is the mechanical form of operator **pin 3** ("ACs name each surface + a
structural coverage test") generalized across EVERY gate content type, so
"closed on a subset" (the exact Epic 42-1 failure — the projector was wired for
G0/G0E only, then the requirement was marked done) becomes structurally
impossible. A subset / G0E-only replay corpus can NEVER re-close the requirement,
because this test names every gate content type by its canonical key below and
fails unless each is EITHER given a bespoke renderer OR explicitly waived on the
shrink-only allowlist.

Pure structural test — no fixtures, no IO, zero live spend. It reads only the
two SSOT collections in ``hil_tabular_projector`` plus the introspectable
registry:

* AC-2 — every canonical type is covered (registered OR allowlisted). Green now
  (43-2 registers zero bespoke renderers, so the allowlist == the full set).
* AC-3 — shrink-only + disjoint invariants: allowlist ⊆ canonical set (no typos)
  AND registry ∩ allowlist == ∅ (cannot both register and waive).
* AC-4 — anti-regression: no canonical type is neither registered nor
  allowlisted; the canonical universe is NAMED here by key (pin 3, mechanical).
* AC-5 — 43-12 (governance close) asserts the allowlist is empty at epic close.

As each bespoke-renderer story (43-1, 43-3…43-9) registers a renderer and deletes
its allowlist row, its type moves allowlist → registry and this test stays green.
Story 43-12 empties ``KNOWN_UNRENDERED_ALLOWLIST`` entirely.
"""

from __future__ import annotations

from app.marcus.cli.hil_tabular_projector import (
    GATE_CONTENT_TYPES,
    KNOWN_UNRENDERED_ALLOWLIST,
    registered_content_types,
)

#: The canonical gate content-type universe, NAMED here by key (AC-4 / pin 3). If a
#: new gate content type is added to ``GATE_CONTENT_TYPES`` in the projector, this
#: expected set must be updated in lockstep — which is exactly the point: a new
#: gate cannot be silently added without a human touching this named list AND
#: providing a renderer or an explicit waiver. Ordered comments map each key to its
#: gate (Epic 43 audit §2). 'directive' = G0 directive composition — named
#: explicitly so a G0E-only replay can never re-close the requirement on a subset.
_EXPECTED_CANONICAL_KEYS: frozenset[str] = frozenset(
    {
        "directive",  # G0 directive composition (the first-felt raw-dump surface)
        "estimator",  # G1.5 run-budget estimator
        "run_constants",  # G1.5 run-constants lock
        "plan_unit",  # G1A PlanUnit ratification
        "per_slide_mode",  # G2B per-slide mode selection
        "variant_ab",  # G2M A/B variant selection
        "literal_visual",  # 06B literal-visual build targets
        "storyboard_targets",  # 07C storyboard build targets
        "motion_plan",  # G2.5 motion-plan status
        "motion_clip",  # G2F motion-clip card
        "storyboard_b",  # G3B storyboard / live-URL card
        "voice_candidates",  # G4A voice-candidate selection
        "input_package",  # G4B input-package preview
        "final_handoff",  # G5 final handoff artifacts + summary
        "research_packet",  # research packet content
        "workbook",  # workbook content
    }
)


def test_canonical_universe_matches_named_keys() -> None:
    """AC-4 (pin 3, mechanical): the SSOT canonical set equals the universe NAMED
    key-by-key in this test. A new gate content type added to the projector's
    ``GATE_CONTENT_TYPES`` cannot pass CI until it is also named here — so a
    subset/G0E-only replay corpus can never silently shrink the reviewed universe.
    """
    assert GATE_CONTENT_TYPES == _EXPECTED_CANONICAL_KEYS


def test_every_canonical_type_is_registered_or_allowlisted() -> None:
    """AC-2 (RED-first coverage): every canonical gate content type is EITHER
    covered by a bespoke renderer OR explicitly waived on the shrink-only
    allowlist. Green now because 43-2 registers zero renderers (allowlist == full
    set); stays green as each bespoke story moves a type registry-ward.
    """
    covered = registered_content_types() | KNOWN_UNRENDERED_ALLOWLIST
    uncovered = GATE_CONTENT_TYPES - covered
    assert uncovered == frozenset(), (
        "gate content type(s) with neither a bespoke renderer nor an explicit "
        f"allowlist waiver: {sorted(uncovered)}"
    )


def test_no_canonical_type_is_orphaned() -> None:
    """AC-4 (anti-regression): stated as the direct contrapositive — there is NO
    canonical type that is neither registered nor allowlisted. A future new gate
    content type therefore cannot be added without a renderer or an explicit
    waiver (it would surface here as an orphan and fail CI).
    """
    orphans = {
        ct
        for ct in GATE_CONTENT_TYPES
        if ct not in registered_content_types() and ct not in KNOWN_UNRENDERED_ALLOWLIST
    }
    assert orphans == set(), (
        f"orphaned gate content type(s) (no renderer, no waiver): {sorted(orphans)}"
    )


def test_allowlist_is_subset_of_canonical_no_typos() -> None:
    """AC-3(a) — shrink-only integrity: every allowlist entry is a real canonical
    key. A stray / mistyped waiver (e.g. 'workbok') fails here rather than silently
    masking an uncovered real type.
    """
    stray = KNOWN_UNRENDERED_ALLOWLIST - GATE_CONTENT_TYPES
    assert stray == frozenset(), (
        f"allowlist entries not in the canonical set (typos/strays): {sorted(stray)}"
    )


def test_registry_and_allowlist_are_disjoint() -> None:
    """AC-3(b) — disjoint invariant: a type that has a bespoke renderer MUST be
    removed from the allowlist. You cannot both register AND waive — this forces
    each bespoke story to DELETE its allowlist row in the same change that calls
    ``register_renderer``.
    """
    both = registered_content_types() & KNOWN_UNRENDERED_ALLOWLIST
    assert both == frozenset(), (
        f"content type(s) both registered and waived — delete the allowlist row: {sorted(both)}"
    )


def test_allowlist_is_shrinking_registry_is_growing_at_43_1() -> None:
    """State pin (updated at 43-1, the first allowlist→registry move): the
    allowlist tightens by exactly one row as each bespoke story registers a
    renderer. This assertion INTENTIONALLY tracks the CURRENT state, not a
    hard-coded full set — later stories (43-3…43-9) move more types registry-ward
    and update this witness in lockstep, and 43-12 empties the allowlist entirely.
    """
    # 43-1 registers the first bespoke renderer: ``directive`` (G0).
    assert registered_content_types() == frozenset({"directive"})
    # …hence ``directive`` has LEFT the allowlist; every other canonical type is
    # still waived (disjoint invariant: registry ∩ allowlist == ∅).
    expected_waived = GATE_CONTENT_TYPES - {"directive"}
    assert expected_waived == KNOWN_UNRENDERED_ALLOWLIST


def test_governance_close_hook_43_12() -> None:
    """AC-5 — 43-12 (governance close) hook, documented as an executable reminder.

    At epic close, Story 43-12 asserts ``KNOWN_UNRENDERED_ALLOWLIST`` is EMPTY —
    every gate content type must have a bespoke renderer, no waivers remain. That
    assertion is:

        assert KNOWN_UNRENDERED_ALLOWLIST == frozenset()

    It CANNOT hold at 43-2 (the allowlist is the full set here), so this test only
    records the contract; it does not yet enforce emptiness. The epic cannot close
    while any row remains.
    """
    # Sanity: the shrink target is a well-formed (immutable) set the 43-12 close
    # can assert-empty against.
    assert isinstance(KNOWN_UNRENDERED_ALLOWLIST, frozenset)
