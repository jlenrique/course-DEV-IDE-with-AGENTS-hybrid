"""Leg-C — deterministic split-only min_cluster_floor honoring (Irene Pass-1).

RED-first: ``app.specialists.irene.cluster_floor`` does not exist yet. These pin
the offline honoring/safety ACs:

- AC#4  split-only, flattened-member byte-identity (the 07G guard in unit form);
- AC#5  figure<->narration atomicity (the bond is never severed);
- AC#6  SOFT floor / source-content veto (unreachable floor -> fail-loud mismatch,
        never an over-fragmenting forced split);
- AC#7  dead-config discriminating pair (consulted -> quiet; set-but-never-read
        -> raise).

Hermetic: no network, no DB, no live-LLM. Fixtures of Pass-1 output, not real
model calls.
"""

from __future__ import annotations

import pytest

from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.irene.cluster_floor import (
    ClusterFloorMismatchError,
    DeadFloorConfigError,
    FloorConsumption,
    assert_floor_consulted,
    consume_min_cluster_floor,
    flatten_cluster_members,
    honor_min_cluster_floor,
)


def _tag(member: dict) -> dict:
    """Ensure a fixture member carries a verifiable role tag (P5 fail-safe).

    Under the P5 atomicity fail-safe, a cluster whose members lack figure/narration
    role tags cannot be split blind (we cannot prove a figure is not being severed
    from its narration). These honoring fixtures therefore carry an explicit
    ``kind`` so the split is role-verifiable; members that already declare a
    ``kind``/``type`` (figure/narration) are left untouched.
    """
    if isinstance(member, dict) and not (member.get("kind") or member.get("type")):
        return {**member, "kind": "content"}
    return member


def _outline(*member_lists: list[dict]) -> list[dict]:
    return [
        {"cluster_intent": f"c{idx}", "source_points": [_tag(m) for m in members]}
        for idx, members in enumerate(member_lists)
    ]


# --------------------------------------------------------------------------- AC#4
def test_floor_at_or_below_count_is_a_noop() -> None:
    outline = _outline([{"text": "a"}, {"text": "b"}], [{"text": "c"}])
    # M == 2; floor 2 (== M) and floor 1 (< M) both leave the outline unchanged.
    assert honor_min_cluster_floor(outline, 2) == outline
    assert honor_min_cluster_floor(outline, 1) == outline


def test_split_only_reaches_floor_and_preserves_flattened_bytes() -> None:
    outline = _outline(
        [{"text": "a"}, {"text": "b"}, {"text": "c"}],
        [{"text": "d"}, {"text": "e"}],
    )  # M=2; c0 has 2 internal seams, c1 has 1 => 3 splits available
    before = flatten_cluster_members(outline)
    honored = honor_min_cluster_floor(outline, 4)  # need +2
    # (a) reached the floor by SUBDIVIDING (never merging)
    assert len(honored) >= 4
    # (b) the flattened member sequence is byte-identical to pre-floor
    assert flatten_cluster_members(honored) == before
    # exact-floor discipline: split only as much as needed
    assert len(honored) == 4


def test_split_never_reorders_or_reassigns_members() -> None:
    outline = _outline([{"text": "a"}, {"text": "b"}, {"text": "c"}, {"text": "d"}])
    honored = honor_min_cluster_floor(outline, 3)
    flat = [m["text"] for m in flatten_cluster_members(honored)]
    assert flat == ["a", "b", "c", "d"]  # canonical order intact


# --------------------------------------------------------------------------- AC#5
def test_figure_narration_bond_is_never_split() -> None:
    outline = _outline(
        [
            {"text": "setup"},
            {"kind": "figure", "text": "fig1"},
            {"kind": "narration", "text": "explains fig1"},
            {"text": "wrap"},
        ]
    )  # M=1; legit seams = after 'setup' and after 'narration'; the figure|narration
    # seam is BONDED and unavailable.
    honored = honor_min_cluster_floor(outline, 3)
    assert len(honored) == 3
    # the figure and its narration must live in the SAME sub-cluster
    for sub in honored:
        texts = [m.get("text") for m in sub["source_points"]]
        if "fig1" in texts:
            assert "explains fig1" in texts, f"figure severed from its narration: {texts}"
            break
    else:  # pragma: no cover - defensive
        pytest.fail("figure sub-cluster not found")


def test_bond_only_cluster_cannot_be_split_raises_mismatch() -> None:
    # A cluster that is ONLY a figure+narration bond has zero legitimate seams; a
    # floor above the count must fail loud, never sever the bond.
    outline = _outline(
        [{"kind": "figure", "text": "fig"}, {"kind": "narration", "text": "reads fig"}]
    )
    with pytest.raises(ClusterFloorMismatchError):
        honor_min_cluster_floor(outline, 2)


# --------------------------------------------------------------------------- AC#6
def test_soft_floor_unreachable_fails_loud_without_overfragmenting() -> None:
    outline = _outline([{"text": "a"}, {"text": "b"}])  # M=1, one seam => max 2
    with pytest.raises(ClusterFloorMismatchError) as exc:
        honor_min_cluster_floor(outline, 5)
    assert "mismatch" in str(exc.value).lower()
    # a fail-loud mismatch is a recoverable dispatch error, not a bare crash
    assert isinstance(exc.value, SpecialistDispatchError)


def test_floor_exactly_at_max_reachable_succeeds() -> None:
    outline = _outline([{"text": "a"}, {"text": "b"}])  # max reachable = 2
    honored = honor_min_cluster_floor(outline, 2)
    assert len(honored) == 2
    assert flatten_cluster_members(honored) == flatten_cluster_members(outline)


def test_floor_one_beyond_max_reachable_fails() -> None:
    outline = _outline([{"text": "a"}, {"text": "b"}])  # max reachable = 2
    with pytest.raises(ClusterFloorMismatchError):
        honor_min_cluster_floor(outline, 3)


# --------------------------------------------------------------------------- AC#7
def test_consume_consulted_when_floor_bound() -> None:
    payload = {"min_cluster_floor": 3}
    outline = _outline([{"text": "a"}, {"text": "b"}, {"text": "c"}])
    honored, consumption = consume_min_cluster_floor(payload, outline)
    assert consumption.consulted is True
    assert consumption.floor == 3
    assert len(honored) == 3
    assert_floor_consulted(payload, consumption)  # quiet


def test_consume_quiet_when_no_floor_bound() -> None:
    outline = _outline([{"text": "a"}])
    honored, consumption = consume_min_cluster_floor({}, outline)
    assert consumption.consulted is False
    assert honored == outline
    assert_floor_consulted({}, consumption)  # quiet


def test_set_but_never_read_floor_raises_dead_config() -> None:
    # Discriminating partner: a floor is bound but consumption never ran.
    never_read = FloorConsumption(
        consulted=False, floor=None, clusters_before=1, clusters_after=1
    )
    with pytest.raises(DeadFloorConfigError) as exc:
        assert_floor_consulted({"min_cluster_floor": 3}, never_read)
    assert isinstance(exc.value, SpecialistDispatchError)


# --------------------------------------------------------------------- P3 (review)
@pytest.mark.parametrize("bad_floor", ["3", 0, -2, 2.5, True, None])
def test_bad_typed_floor_raises_dispatch_error_not_bare(bad_floor: object) -> None:
    """P3: a non-int/0/negative/bad-shape floor must re-base ``SpecialistDispatchError``
    so the runner's shared handler routes it to the recoverable error-pause — NOT a
    bare ``ValueError``/``TypeError`` that bypasses that channel."""
    outline = _outline([{"text": "a"}, {"text": "b"}])
    with pytest.raises(SpecialistDispatchError):
        honor_min_cluster_floor(outline, bad_floor)


def test_bad_shape_outline_raises_dispatch_error_not_bare() -> None:
    """P3: a non-list outline must fail loud as a ``SpecialistDispatchError``."""
    with pytest.raises(SpecialistDispatchError):
        honor_min_cluster_floor("not-a-list", 3)


# --------------------------------------------------------------------- P4 (review)
def test_subclusters_have_distinct_identities() -> None:
    """P4: split-out sub-clusters must NOT alias the parent's cluster-level id /
    slide_key (07G per-sub-slide join collision)."""
    cluster = {
        "id": "c1",
        "slide_key": "sk1",
        "cluster_intent": "walk",
        "source_points": [
            {"kind": "content", "text": "a"},
            {"kind": "content", "text": "b"},
            {"kind": "content", "text": "c"},
        ],
    }
    honored = honor_min_cluster_floor([cluster], 3)
    assert len(honored) == 3
    ids = [sub.get("id") for sub in honored]
    slide_keys = [sub.get("slide_key") for sub in honored]
    assert len(set(ids)) == len(ids), f"duplicate sub-cluster ids: {ids}"
    assert len(set(slide_keys)) == len(slide_keys), f"duplicate slide_keys: {slide_keys}"


def test_non_chosen_member_key_lists_not_duplicated() -> None:
    """P4: a non-chosen member-key list must NOT be shallow-copied into every sub."""
    cluster = {
        "source_points": [
            {"kind": "content", "text": "a"},
            {"kind": "content", "text": "b"},
            {"kind": "content", "text": "c"},
        ],
        # a SECOND member-key list the resolver did NOT choose (source_points wins)
        "components": ["X", "Y", "Z"],
    }
    honored = honor_min_cluster_floor([cluster], 3)
    assert len(honored) == 3
    duplicated = [sub for sub in honored if sub.get("components") == ["X", "Y", "Z"]]
    assert not duplicated, "non-chosen member-key list duplicated into sub-clusters"


def test_mutating_sub_nested_metadata_does_not_alias_sibling() -> None:
    """P4: nested cluster metadata must be deep-copied, not aliased across siblings."""
    cluster = {
        "meta": {"tags": []},
        "source_points": [
            {"kind": "content", "text": "a"},
            {"kind": "content", "text": "b"},
            {"kind": "content", "text": "c"},
        ],
    }
    honored = honor_min_cluster_floor([cluster], 3)
    assert len(honored) >= 2
    honored[0]["meta"]["tags"].append("mutated")
    assert honored[1]["meta"]["tags"] == [], "sibling nested metadata was aliased"


def test_split_still_preserves_flattened_member_identity_after_p4() -> None:
    """P4 guardrail: the flattened member OBJECTS survive the reconstruction."""
    cluster = {
        "id": "c1",
        "source_points": [
            {"kind": "content", "text": "a"},
            {"kind": "content", "text": "b"},
            {"kind": "content", "text": "c"},
        ],
    }
    before = flatten_cluster_members([cluster])
    honored = honor_min_cluster_floor([cluster], 3)
    assert flatten_cluster_members(honored) == before


# --------------------------------------------------------------------- P5 (review)
def test_roleless_cluster_under_floor_fails_safe_to_mismatch() -> None:
    """P5: a cluster whose members carry NO role tags cannot be split blind under a
    bound floor N>M — fail-safe to the SOFT mismatch, never a silent split (protects
    the figure<->narration atomicity / 07G VO<->on-screen invariant)."""
    # Built RAW (bypassing _outline's role tagging) so the members are role-LESS.
    outline = [
        {"cluster_intent": "c0", "source_points": [{"text": "a"}, {"text": "b"}, {"text": "c"}]},
    ]
    with pytest.raises(ClusterFloorMismatchError):
        honor_min_cluster_floor(outline, 3)


def test_partial_role_tags_still_fail_safe() -> None:
    """P5: if ANY member of a to-be-split cluster lacks a role tag, refuse (we cannot
    prove the untagged member is not a figure needing its narration)."""
    outline = [
        {
            "cluster_intent": "c0",
            "source_points": [
                {"kind": "content", "text": "a"},
                {"text": "b"},  # NO role tag
                {"kind": "content", "text": "c"},
            ],
        },
    ]
    with pytest.raises(ClusterFloorMismatchError):
        honor_min_cluster_floor(outline, 3)
