"""Leg-C — deterministic, split-only ``min_cluster_floor`` honoring for Irene Pass-1.

Consumes the CD-owned ``scripted.min_cluster_floor`` — a STYLE-IDENTITY property
("this style reads as a multi-beat narrative walk; below N beats it collapses to a
stub deck"). AFTER Pass-1 emits its LLM-honest clustering (M clusters), if a floor
N > M is bound, this module SUBDIVIDES existing clusters ONLY at legitimate internal
source-structure seams to reach exactly N — a POST-clustering, split-only, MONOTONE
constraint. It NEVER merges/reorders/reassigns canonical text order, NEVER splits
mid-component, and NEVER severs a figure<->narration bond.

The floor is a SOFT target with source-content veto: when the legitimate seams cannot
honestly reach N, this raises a fail-loud ``ClusterFloorMismatchError``
(styleguide-vs-content mismatch) rather than force a bad, over-fragmenting split.

The byte-identity of the flattened member sequence (``flatten_cluster_members``) is
what protects the 07G VO<->on-screen invariant in unit form: the split reshapes cluster
BOUNDARIES only, never the ordered canonical text.

This module is a PURE leaf (no ``app.marcus`` import, no I/O): it takes the Pass-1
outline + the floor and returns the reshaped outline (or raises). Its fail-loud errors
re-base ``SpecialistDispatchError`` so the production runner's shared
``except SpecialistDispatchError`` routes them through the recoverable error-pause
channel (no parallel error channel).
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any

from app.specialists.dispatch_errors import SpecialistDispatchError

# Ordered member-key contract: a cluster's ordered internal members (the seams the LLM
# already grouped) live under the FIRST of these keys that holds a list. The clustering
# is LLM-emergent, so we detect the member list rather than pin a single rigid key.
_MEMBER_KEYS: tuple[str, ...] = (
    "source_points",
    "components",
    "beats",
    "members",
    "points",
    "segments",
)

CLUSTER_FLOOR_MISMATCH_TAG = "irene.pass1.styleguide-content-mismatch"
DEAD_FLOOR_CONFIG_TAG = "irene.pass1.min-cluster-floor-dead-config"
INVALID_FLOOR_CONFIG_TAG = "irene.pass1.min-cluster-floor-invalid-config"

# Cluster-level identity keys a downstream 07G per-sub-slide join may key on. When a
# cluster is subdivided, each sub-cluster must get a DISTINCT value for any of these
# it carries, or two sub-slides collide on the same id (P4).
_IDENTITY_KEYS: tuple[str, ...] = (
    "id",
    "cluster_id",
    "slide_key",
    "slide_id",
    "key",
)


class ClusterFloorMismatchError(SpecialistDispatchError):  # noqa: N818
    """SOFT-floor veto: floor N cannot be honored by legitimate seams (fail loud)."""

    def __init__(self, message: str, *, tag: str = CLUSTER_FLOOR_MISMATCH_TAG) -> None:
        super().__init__(message, tag=tag)


class DeadFloorConfigError(SpecialistDispatchError):  # noqa: N818
    """A ``min_cluster_floor`` was bound but never consulted at Pass-1 (anti-silent-drop)."""

    def __init__(self, message: str, *, tag: str = DEAD_FLOOR_CONFIG_TAG) -> None:
        super().__init__(message, tag=tag)


class InvalidFloorConfigError(SpecialistDispatchError):  # noqa: N818
    """A ``min_cluster_floor`` (or the outline it applies to) is the wrong TYPE/SHAPE.

    Re-bases ``SpecialistDispatchError`` (P3) so a bad-typed floor — a non-int / 0 /
    negative value, or a non-list outline — routes through the runner's shared
    ``except SpecialistDispatchError`` recoverable error-pause instead of surfacing as
    a bare ``ValueError``/``TypeError`` that bypasses that channel (and is unreachable
    from the SPOC/direct-state path).
    """

    def __init__(self, message: str, *, tag: str = INVALID_FLOOR_CONFIG_TAG) -> None:
        super().__init__(message, tag=tag)


@dataclass(frozen=True)
class FloorConsumption:
    """Receipt proving whether the floor was consulted (the dead-config discriminator)."""

    consulted: bool
    floor: int | None
    clusters_before: int
    clusters_after: int


def cluster_members(cluster: Any) -> tuple[str | None, list[Any]]:
    """Return ``(member_key, members)`` for a cluster, or ``(None, [])`` if it has none."""
    if isinstance(cluster, dict):
        for key in _MEMBER_KEYS:
            value = cluster.get(key)
            if isinstance(value, list):
                return key, value
    return None, []


def flatten_cluster_members(structural_outline: Any) -> list[Any]:
    """The byte-identity witness: the ordered member sequence across all clusters.

    Split-only honoring must leave this sequence UNCHANGED (no merge/reorder/reassign).
    """
    flat: list[Any] = []
    if not isinstance(structural_outline, list):
        return flat
    for cluster in structural_outline:
        _, members = cluster_members(cluster)
        flat.extend(members)
    return flat


def _is_figure(member: Any) -> bool:
    if not isinstance(member, dict):
        return False
    return str(member.get("kind") or member.get("type") or "").strip().lower() == "figure"


def _is_narration(member: Any) -> bool:
    if not isinstance(member, dict):
        return False
    return str(member.get("kind") or member.get("type") or "").strip().lower() in {
        "narration",
        "narrative",
    }


def _has_role_tag(member: Any) -> bool:
    """A member's role is VERIFIABLE iff it declares a non-empty ``kind``/``type``.

    Without a role tag we cannot prove the member is not a figure that needs its
    explaining narration — so a seam adjacent to it cannot be certified safe.
    """
    if not isinstance(member, dict):
        return False
    return bool(str(member.get("kind") or member.get("type") or "").strip())


def _roles_verifiable(members: list[Any]) -> bool:
    """P5 fail-safe pre-check: a cluster may only be split when EVERY member's role is
    verifiable. If ANY member lacks a role tag, splitting is blind (risking a severed
    figure<->narration bond) and is refused — the floor fails safe to the SOFT mismatch.
    """
    return bool(members) and all(_has_role_tag(m) for m in members)


def _seam_is_bonded(members: list[Any], i: int) -> bool:
    """Is the seam AFTER index ``i`` (between ``members[i]`` and ``members[i+1]``)
    INVIOLABLE?

    A seam is bonded (cannot be a split boundary) when ANY of:
    - the left member declares ``bond_next`` (or the right declares ``bond_prev``);
    - both members share a non-null ``bond_group`` id;
    - the figure<->narration atomicity pre-check fires: a ``figure`` member is adjacent
      to a ``narration`` member (either order) — a figure is never severed from its
      explaining narration.
    """
    left = members[i]
    right = members[i + 1]
    if isinstance(left, dict) and left.get("bond_next"):
        return True
    if isinstance(right, dict) and right.get("bond_prev"):
        return True
    if isinstance(left, dict) and isinstance(right, dict):
        lg = left.get("bond_group")
        rg = right.get("bond_group")
        if lg is not None and lg == rg:
            return True
    return (_is_figure(left) and _is_narration(right)) or (
        _is_narration(left) and _is_figure(right)
    )


def _legitimate_seams(members: list[Any]) -> list[int]:
    """Split-after indices that are legitimate internal source-structure boundaries."""
    return [i for i in range(len(members) - 1) if not _seam_is_bonded(members, i)]


def _split_cluster(
    cluster: dict[str, Any], key: str, members: list[Any], chosen_seams: list[int]
) -> list[dict[str, Any]]:
    """Partition ``members`` into contiguous groups at ``chosen_seams`` (split-after).

    Each sub-cluster is RECONSTRUCTED (P4), not shallow-copied, so that:
    - only the CHOSEN member key is carried, holding this sub's contiguous slice — the
      parent's OTHER member-key lists are NOT duplicated into every sibling;
    - all cluster-level metadata is DEEP-COPIED, so mutating one sub's nested metadata
      never aliases a sibling;
    - any cluster-level identity key (``id``/``slide_key``/… ) is made DISTINCT per sub,
      so a downstream 07G per-sub-slide join can never collide two sub-slides.

    The member objects placed under ``key`` are the SAME originals (contiguous slices),
    so ``flatten_cluster_members`` stays byte-identical.
    """
    boundaries = sorted(chosen_seams)
    groups: list[list[Any]] = []
    start = 0
    for boundary in boundaries:
        groups.append(members[start : boundary + 1])
        start = boundary + 1
    groups.append(members[start:])

    subclusters: list[dict[str, Any]] = []
    for idx, group in enumerate(groups):
        sub: dict[str, Any] = {}
        for field, value in cluster.items():
            if field in _MEMBER_KEYS:
                continue  # drop ALL member-key lists; the chosen slice is set below
            sub[field] = copy.deepcopy(value)  # no nested-metadata aliasing across sibs
        sub[key] = group  # ORIGINAL member objects -> flattened byte-identity preserved
        sub["floor_subdivision_index"] = idx  # provenance marker; not member text
        for id_key in _IDENTITY_KEYS:
            base = sub.get(id_key)
            if isinstance(base, (str, int)) and not isinstance(base, bool):
                sub[id_key] = f"{base}#f{idx}"  # DISTINCT identity per sub-cluster
        subclusters.append(sub)
    return subclusters


def honor_min_cluster_floor(structural_outline: Any, floor: Any) -> list[Any]:
    """Return a split-only reshaped outline with >= ``floor`` clusters, or raise.

    Deterministic distribution: clusters are visited in order and each is split at its
    EARLIEST legitimate seams until the deficit is met, so the result is stable. Reaches
    EXACTLY ``floor`` clusters when the seams allow; raises ``ClusterFloorMismatchError``
    (never an over-fragmenting forced split) when they do not.
    """
    if not isinstance(structural_outline, list):
        raise InvalidFloorConfigError(
            "structural_outline must be a list of cluster dicts; "
            f"got {type(structural_outline).__name__}"
        )
    if isinstance(floor, bool) or not isinstance(floor, int) or floor < 1:
        raise InvalidFloorConfigError(
            f"min_cluster_floor must be a positive int; got {floor!r}"
        )

    count = len(structural_outline)
    if floor <= count:
        return list(structural_outline)  # already honored — identity no-op

    deficit = floor - count
    per_cluster: list[tuple[str | None, list[Any], list[int]]] = []
    total_available = 0
    for cluster in structural_outline:
        key, members = cluster_members(cluster)
        # P5 atomicity fail-safe: a cluster contributes splittable seams ONLY when its
        # members' roles are verifiable. A role-less cluster yields ZERO seams — the
        # floor then fails safe to the SOFT mismatch below rather than split blind.
        seams = (
            _legitimate_seams(members)
            if key is not None and _roles_verifiable(members)
            else []
        )
        per_cluster.append((key, members, seams))
        total_available += len(seams)

    if total_available < deficit:
        raise ClusterFloorMismatchError(
            f"min_cluster_floor={floor} cannot be honored: content has {count} "
            f"cluster(s) with only {total_available} legitimate internal seam(s) "
            f"(max reachable {count + total_available}); refusing to over-fragment "
            f"(styleguide-vs-content mismatch)"
        )

    result: list[Any] = []
    for (key, members, seams), cluster in zip(per_cluster, structural_outline, strict=True):
        if deficit <= 0 or not seams:
            result.append(cluster)
            continue
        take = min(len(seams), deficit)
        chosen = seams[:take]
        deficit -= take
        assert key is not None  # seams is non-empty => a member key was found
        result.extend(_split_cluster(cluster, key, members, chosen))
    assert deficit == 0, f"floor distribution left deficit={deficit}"
    return result


def consume_min_cluster_floor(
    envelope_payload: Any, structural_outline: Any
) -> tuple[list[Any], FloorConsumption]:
    """Consult a bound ``min_cluster_floor`` and honor it; return ``(outline, receipt)``.

    When no floor is bound, returns the outline unchanged with a ``consulted=False``
    receipt (quiet). When a floor is bound, honors it (may raise the mismatch veto) and
    returns a ``consulted=True`` receipt. The receipt is the dead-config discriminator.
    """
    before = len(structural_outline) if isinstance(structural_outline, list) else 0
    floor = (
        envelope_payload.get("min_cluster_floor")
        if isinstance(envelope_payload, dict)
        else None
    )
    if floor is None:
        return structural_outline, FloorConsumption(
            consulted=False, floor=None, clusters_before=before, clusters_after=before
        )
    honored = honor_min_cluster_floor(structural_outline, floor)
    return honored, FloorConsumption(
        consulted=True,
        floor=int(floor),
        clusters_before=before,
        clusters_after=len(honored),
    )


def assert_floor_consulted(envelope_payload: Any, consumption: FloorConsumption) -> None:
    """Fail loud if a floor is bound in the payload but was never consulted.

    Discriminating pair (Murat): a consulted floor -> quiet; a bound-but-never-read floor
    -> ``DeadFloorConfigError``. Guards against a future refactor that threads the floor
    but silently drops its consumption (invisible dead config).
    """
    floor = (
        envelope_payload.get("min_cluster_floor")
        if isinstance(envelope_payload, dict)
        else None
    )
    if floor is not None and not consumption.consulted:
        raise DeadFloorConfigError(
            f"min_cluster_floor={floor!r} is bound in the envelope payload but was "
            f"never consulted at Pass-1 (silent dead-config; set-but-never-read)"
        )
