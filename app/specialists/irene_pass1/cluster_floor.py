"""Leg-C R3 — deterministic, split-only ``min_cluster_floor`` honoring at the
REAL Pass-1 surface (``app.specialists.irene_pass1``, dispatched by nodes
04A/05/05B).

PORT of ``app.specialists.irene.cluster_floor`` (the P1–P8-remediated engine
that lived in an unreachable branch — see the D1 adjudication record) with ONLY
the member-detection layer replaced (binding amendment A-3): the old engine
detected a nested cluster-with-members shape via ``_MEMBER_KEYS``; the real
Pass-1 contract is a FLAT ``plan_units[]`` list in the Epic-19/20c cluster
vocabulary (cluster_id / cluster_role head|interstitial / parent_slide_id /
cluster_interstitial_count). Here:

- a CLUSTER is a contiguous run of plan_units sharing a ``cluster_id``;
- its MEMBERS are those plan_units;
- candidate SEAMS are the boundaries between adjacent members, and their
  legitimacy is derived from each unit's ``source_refs[]`` — the verbatim
  source ANCHORS Pass-1 now emits (citations of planning work already done,
  never new structure). Roles at a seam use the FIXED vocabulary
  {figure, narration, claim} (I-3), classified DETERMINISTICALLY from the
  anchor text (image/file/prompt-to-generate markers or a frozen
  ``figure_tokens`` numeral hit -> figure; narration/voiceover markers ->
  narration; other well-formed anchors -> claim).

Splitting a cluster reshapes cluster BOUNDARIES only, in the EXISTING cluster
vocabulary: the trailing part's first unit is promoted to head of a NEW,
distinctly-identified cluster (P4 ``#f{idx}`` minting), following units are
re-parented to it as interstitials, and every affected head's
``cluster_interstitial_count`` is recomputed. NO new plan_units are minted, NO
unit content changes, and the flattened content sequence
(``flatten_plan_content``) stays byte-identical — the 07G VO<->on-screen guard
in unit form. (Deliberate deviation from one clause of the work order: split
products CANNOT stay under the same ``cluster_id`` — the AC#9 arbiter counts
DISTINCT clusters (baseline count_K=7 < N=8), so same-cluster interstitial
growth would make the floor unfalsifiable. See the story Dev Notes "R3 rewire"
section.)

VETO DISCIPLINE (binding, Murat/W-1): an absent / malformed / unresolvable /
role-unverifiable anchor set makes its whole cluster contribute ZERO seams —
NEVER guess-and-split; if the deficit is then unmeetable the floor fails loud
via the SOFT styleguide-vs-content mismatch. Figure<->narration atomicity is
inviolable (a figure unit is never severed from its explaining narration unit;
intra-unit figure+narration bonds are never split because intra-unit seams are
not split at all). Knowledge-check/assessment-shaped clusters are floor-exempt
by construction (I-4). Keep-dense singletons are structurally protected (a
size-1 cluster has no member seams).

This module is a PURE leaf (no I/O, no ``app.marcus`` import). Its fail-loud
errors re-base ``SpecialistDispatchError`` (P3) so the production runner's
shared ``except SpecialistDispatchError`` routes them through the recoverable
error-pause channel. The dead-config guard (D-1) is co-located HERE, with the
dispatched module.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any

from app.specialists._shared.figure_tokens import _figures  # frozen neck, read-only
from app.specialists.dispatch_errors import SpecialistDispatchError

CLUSTER_FLOOR_MISMATCH_TAG = "irene_pass1.styleguide-content-mismatch"
# R7 (Edge#4): the JSON-parse-failure fallback plan (one synthetic unit, no
# source_refs) under a bound floor is the SAME recoverable error class but a
# DISTINCT diagnostic — triage the LLM output format, not the
# styleguide/content pairing. Raised by _act.py, defined here with its family.
CLUSTER_FLOOR_LLM_FALLBACK_TAG = (
    "irene_pass1.styleguide-content-mismatch.llm-format-fallback"
)
DEAD_FLOOR_CONFIG_TAG = "irene_pass1.min-cluster-floor-dead-config"
INVALID_FLOOR_CONFIG_TAG = "irene_pass1.min-cluster-floor-invalid-config"

# The grouping vocabulary the split is ALLOWED to reshape. Everything else on a
# plan_unit is CONTENT and must survive byte-identical (flatten_plan_content).
#
# R3 (D-3 byte-identity, honestly scoped): ``floor_subdivision_index`` is the
# ONE floor-ENGINE-OWNED annotation key (provenance of the honoring, not plan
# state); _act.py scrubs it — and only it — from the MODEL-VISIBLE payload
# copy so a refinement pass cannot fingerprint that a floor ran. Minted ``#f``
# cluster ids are NOT scrubbed/renamed: the honored plan IS the real plan the
# refinement must see; its extra clusters are legitimate downstream state.
# Model-input byte-identity therefore holds for the CREATION pass and for any
# pass given identical incoming plans — not across a pass whose incoming plan
# was itself changed by honoring.
GROUPING_KEYS: frozenset[str] = frozenset(
    {
        "cluster_id",
        "cluster_role",
        "cluster_position",
        "parent_slide_id",
        "cluster_interstitial_count",
        "floor_subdivision_index",
    }
)

# I-3: the FIXED role vocabulary. Expansion = a fresh party round.
ANCHOR_ROLES: tuple[str, ...] = ("figure", "narration", "claim")

# Deterministic anchor-role markers. Narration is checked FIRST (an explicitly
# labelled narration line stays narration even when it speaks a numeral), then
# figure, else claim. Word-boundary regexes avoid substring traps ("paragraph"
# must not hit "graph").
_NARRATION_MARKER_RE = re.compile(
    r"\b(narration|voice-?over|narrator)\b", re.IGNORECASE
)
_FIGURE_MARKER_RE = re.compile(
    r"\b(figure|diagram|chart|graph|illustration|photo|icon|venn|infographic)\b",
    re.IGNORECASE,
)
_FIGURE_SUBSTRING_MARKERS: tuple[str, ...] = (
    "image prompt",
    "image:",
    "![",
    ".png",
    ".jpg",
    ".jpeg",
    ".svg",
    ".webp",
    "design brief",
    "visual:",
)

# I-4: assessment / knowledge-check-shaped units are floor-exempt by
# construction; a cluster containing one contributes zero seams.
_ASSESSMENT_MARKER_RE = re.compile(
    r"knowledge[\s-]?check|\bquiz\b|\bassessment\b|self[\s-]?check|\bq&a\b",
    re.IGNORECASE,
)

# Emission guidance asks for 1-6 short anchors; consumption enforces only the
# lower bound (strict schema: non-empty list of non-empty strings).
MIN_SOURCE_REFS_PER_UNIT = 1


class ClusterFloorMismatchError(SpecialistDispatchError):  # noqa: N818
    """SOFT-floor veto: floor N cannot be honored by legitimate seams (fail loud)."""

    def __init__(self, message: str, *, tag: str = CLUSTER_FLOOR_MISMATCH_TAG) -> None:
        super().__init__(message, tag=tag)


class DeadFloorConfigError(SpecialistDispatchError):  # noqa: N818
    """A ``min_cluster_floor`` was bound but never consulted at Pass-1 (anti-silent-drop)."""

    def __init__(self, message: str, *, tag: str = DEAD_FLOOR_CONFIG_TAG) -> None:
        super().__init__(message, tag=tag)


class InvalidFloorConfigError(SpecialistDispatchError):  # noqa: N818
    """A ``min_cluster_floor`` (or the plan it applies to) is the wrong TYPE/SHAPE.

    Re-bases ``SpecialistDispatchError`` (P3) so a bad-typed floor — a non-int /
    0 / negative value, or a non-list plan — routes through the runner's shared
    recoverable error-pause instead of a bare ``ValueError``/``TypeError``.
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


# --------------------------------------------------------------------------- #
# source_refs schema + deterministic role classification                        #
# --------------------------------------------------------------------------- #
def unit_source_refs(unit: Any) -> list[str] | None:
    """Strict pre-consumption schema check: a unit's ``source_refs`` must be a
    non-empty list of non-empty strings. Malformed/absent -> ``None`` (treated
    as absent; the floor then REFUSES via the soft mismatch, never crashes)."""
    if not isinstance(unit, dict):
        return None
    refs = unit.get("source_refs")
    if not isinstance(refs, list) or len(refs) < MIN_SOURCE_REFS_PER_UNIT:
        return None
    for ref in refs:
        if not isinstance(ref, str) or not ref.strip():
            return None
    return list(refs)


def classify_anchor_role(anchor: Any) -> str | None:
    """Deterministic {figure, narration, claim} classification of ONE anchor.

    Returns ``None`` for a role-UNVERIFIABLE anchor (non-string / blank) — the
    veto discipline then refuses to split anywhere near it.
    """
    if not isinstance(anchor, str) or not anchor.strip():
        return None
    if _NARRATION_MARKER_RE.search(anchor):
        return "narration"
    lowered = anchor.lower()
    if _FIGURE_MARKER_RE.search(anchor) or any(
        marker in lowered for marker in _FIGURE_SUBSTRING_MARKERS
    ):
        return "figure"
    if _figures(anchor):  # frozen-neck numeral hit: numerals are figure material
        return "figure"
    return "claim"


def _unit_roles(unit: Any) -> frozenset[str] | None:
    """The set of anchor roles a unit's ``source_refs`` carry, or ``None`` when
    the refs are malformed/absent or ANY anchor is role-unverifiable (P5
    fail-safe: never split blind)."""
    refs = unit_source_refs(unit)
    if refs is None:
        return None
    roles: set[str] = set()
    for ref in refs:
        role = classify_anchor_role(ref)
        if role is None:
            return None
        roles.add(role)
    return frozenset(roles)


# R2 (Edge#2): the live corpus carries curly apostrophes/quotes (U+2018/19,
# U+201C/1D — e.g. "The Intrapreneur's Maze" with U+2019), en/em-dashes and
# non-breaking spaces; an LLM emitting straight-quote anchors must still
# resolve, else every seam zeroes and a live floor false-vetoes. NFKC + this
# small canonical map is applied to BOTH anchor and source before containment.
# MATCHING ONLY: plan/source text itself is never rewritten.
_CANONICAL_CHARS = str.maketrans(
    {
        "‘": "'",  # left single curly quote
        "’": "'",  # right single curly quote / curly apostrophe
        "‚": "'",  # single low-9 quote
        "‛": "'",  # single high-reversed-9 quote
        "“": '"',  # left double curly quote
        "”": '"',  # right double curly quote
        "„": '"',  # double low-9 quote
        "‟": '"',  # double high-reversed-9 quote
        "–": "-",  # en-dash
        "—": "-",  # em-dash
        "−": "-",  # minus sign
        "‑": "-",  # non-breaking hyphen
        " ": " ",  # non-breaking space (NFKC also maps this; belt+braces)
    }
)


def _normalize_match_text(text: str) -> str:
    """Anchor<->source matching canonicalization: NFKC + quote/dash/space
    canonical map + whitespace-run collapse (markdown line-wrap tolerance)."""
    canonical = unicodedata.normalize("NFKC", text).translate(_CANONICAL_CHARS)
    return " ".join(canonical.split())


def _refs_resolve_in_source(refs: list[str], extracted_source: str) -> bool:
    """Anchors are citations: each must occur verbatim in the source (modulo
    whitespace runs + the R2 quote/dash canonicalization above — a genuinely
    absent anchor still fails containment and vetoes)."""
    haystack = _normalize_match_text(extracted_source)
    return all(_normalize_match_text(ref) in haystack for ref in refs)


def _normalized_unit_refs(unit: Any) -> frozenset[str] | None:
    """A unit's ``source_refs`` in canonical matching form, or ``None`` when
    malformed/absent (same absence semantics as :func:`unit_source_refs`)."""
    refs = unit_source_refs(unit)
    if refs is None:
        return None
    return frozenset(_normalize_match_text(ref) for ref in refs)


def duplicated_anchors(plan_units: list[Any]) -> frozenset[str]:
    """R4 (Edge#3): normalized anchor strings carried by MORE THAN ONE unit.

    An anchor is a citation of the passage ONE unit plans; the same anchor on
    two units makes the seam evidence ambiguous, so it is treated as
    UNRESOLVABLE for seam purposes on ALL units that carry it (veto
    discipline: refuse rather than guess). Duplicates WITHIN a single unit's
    own list are not cross-unit ambiguity and do not count.
    """
    carriers: dict[str, int] = {}
    for unit in plan_units:
        for anchor in _normalized_unit_refs(unit) or frozenset():
            carriers[anchor] = carriers.get(anchor, 0) + 1
    return frozenset(anchor for anchor, count in carriers.items() if count > 1)


def _is_assessment_unit(unit: Any) -> bool:
    if not isinstance(unit, dict):
        return False
    text = f"{unit.get('title') or ''} {unit.get('learning_objective') or ''}"
    return bool(_ASSESSMENT_MARKER_RE.search(text))


# --------------------------------------------------------------------------- #
# flat-plan grouping + the byte-identity witness                                #
# --------------------------------------------------------------------------- #
def group_plan_clusters(plan_units: list[Any]) -> list[tuple[str, list[Any]]]:
    """Contiguous ``(cluster_id, units)`` runs in plan order.

    The real Pass-1 output is contiguous per cluster (head then its
    interstitials); run-grouping preserves the canonical order regardless, so
    honoring can never reorder the flattened plan.
    """
    runs: list[tuple[str, list[Any]]] = []
    current_id: str | None = None
    for idx, unit in enumerate(plan_units):
        raw = unit.get("cluster_id") if isinstance(unit, dict) else None
        cid = str(raw) if raw is not None else f"__unclustered-{idx}"
        if not runs or cid != current_id:
            runs.append((cid, []))
            current_id = cid
        runs[-1][1].append(unit)
    return runs


def count_clusters(plan_units: list[Any]) -> int:
    """The AC#9 arbiter metric: distinct (contiguous-run) cluster count."""
    return len(group_plan_clusters(plan_units))


def flatten_plan_content(plan_units: list[Any]) -> list[dict[str, Any]]:
    """The byte-identity witness: the ordered CONTENT of every plan_unit.

    Split-only honoring must leave this sequence UNCHANGED — it may reshape
    only the ``GROUPING_KEYS`` cluster-boundary vocabulary (07G guard in unit
    form: canonical text/order is never merged, reordered, or reassigned).
    """
    return [
        {k: v for k, v in unit.items() if k not in GROUPING_KEYS}
        if isinstance(unit, dict)
        else unit
        for unit in plan_units
    ]


# --------------------------------------------------------------------------- #
# seam legitimacy (ported bond machinery at the unit level)                     #
# --------------------------------------------------------------------------- #
def _seam_is_bonded(
    left: Any,
    right: Any,
    roles_left: frozenset[str],
    roles_right: frozenset[str],
) -> bool:
    """Is the seam between two adjacent units INVIOLABLE?

    Ported from the old engine's member-seam bond check:
    - explicit ``bond_next`` / ``bond_prev`` / shared non-null ``bond_group``;
    - figure<->narration atomicity: a figure-bearing unit WITHOUT its own
      narration is never severed from an adjacent narration-bearing unit
      (either order). Two SELF-CONTAINED figure+narration units (each carrying
      its own narration — the two-Design-Briefs shape) are legitimately
      separable (D2 resolution).
    """
    if isinstance(left, dict) and left.get("bond_next"):
        return True
    if isinstance(right, dict) and right.get("bond_prev"):
        return True
    if isinstance(left, dict) and isinstance(right, dict):
        lg = left.get("bond_group")
        rg = right.get("bond_group")
        if lg is not None and lg == rg:
            return True
    left_fig_unnarrated = "figure" in roles_left and "narration" not in roles_left
    right_fig_unnarrated = "figure" in roles_right and "narration" not in roles_right
    return (left_fig_unnarrated and "narration" in roles_right) or (
        right_fig_unnarrated and "narration" in roles_left
    )


def _run_seams(
    units: list[Any],
    extracted_source: str | None,
    duplicated: frozenset[str] = frozenset(),
) -> list[int]:
    """Split-after member indices that are legitimate seams for one cluster run.

    Zero seams (the veto) when the run is a singleton, is assessment-shaped
    (I-4), ANY unit's anchors are absent/malformed/unresolvable/role-
    unverifiable, or ANY unit carries a cross-unit DUPLICATED anchor (R4:
    ambiguous citation = unresolvable for seam purposes) — the floor never
    guesses-and-splits.
    """
    if len(units) < 2:
        return []
    if any(_is_assessment_unit(unit) for unit in units):
        return []
    roles_per_unit: list[frozenset[str]] = []
    for unit in units:
        roles = _unit_roles(unit)
        if roles is None:
            return []
        normalized_refs = _normalized_unit_refs(unit)
        assert normalized_refs is not None  # _unit_roles above already validated
        if duplicated and normalized_refs & duplicated:
            return []  # R4 duplicate-anchor veto (diagnosed by the caller)
        if extracted_source is not None:
            refs = unit_source_refs(unit)
            assert refs is not None  # _unit_roles above already validated
            if not _refs_resolve_in_source(refs, extracted_source):
                return []
        roles_per_unit.append(roles)
    return [
        i
        for i in range(len(units) - 1)
        if not _seam_is_bonded(
            units[i], units[i + 1], roles_per_unit[i], roles_per_unit[i + 1]
        )
    ]


# --------------------------------------------------------------------------- #
# the split (P4 distinct identities; counts recomputed; no unit minting)        #
# --------------------------------------------------------------------------- #
def _mint_cluster_id(base: str, idx: int, used: set[str]) -> str:
    minted = f"{base}#f{idx}"
    suffix = idx
    while minted in used:
        suffix += 1
        minted = f"{base}#f{suffix}"
    used.add(minted)
    return minted


def _recount_part(part: list[dict[str, Any]]) -> None:
    """Recompute the head's ``cluster_interstitial_count`` inside one part
    (every dict in ``part`` is already a this-split copy)."""
    interstitials = sum(1 for u in part if u.get("cluster_role") == "interstitial")
    for unit in part:
        if unit.get("cluster_role") == "head":
            unit["cluster_interstitial_count"] = interstitials


def _split_run(
    cluster_id: str,
    units: list[Any],
    chosen_seams: list[int],
    used_cluster_ids: set[str],
) -> list[dict[str, Any]]:
    """Partition one cluster run at ``chosen_seams`` (split-after indices).

    Part 0 keeps the original ``cluster_id``; each trailing part becomes a NEW
    cluster with a DISTINCT minted id (P4): its first unit is promoted to head
    (parent cleared, position anchored per the normalize_clusters head rule),
    following units are re-parented to it as interstitials. Only GROUPING_KEYS
    change, on shallow COPIES — unit content/order is byte-identical and no new
    plan_units are minted.
    """
    boundaries = sorted(chosen_seams)
    groups: list[list[Any]] = []
    start = 0
    for boundary in boundaries:
        groups.append(units[start : boundary + 1])
        start = boundary + 1
    groups.append(units[start:])

    out: list[dict[str, Any]] = []
    for idx, group in enumerate(groups):
        part: list[dict[str, Any]] = []
        if idx == 0:
            for unit in group:
                copied = dict(unit)
                copied["floor_subdivision_index"] = idx
                part.append(copied)
        else:
            minted = _mint_cluster_id(cluster_id, idx, used_cluster_ids)
            head_unit = dict(group[0])
            head_unit["cluster_id"] = minted
            head_unit["cluster_role"] = "head"
            head_unit["parent_slide_id"] = None
            position = head_unit.get("cluster_position")
            if position not in ("establish", "tension", "develop", "resolve"):
                head_unit["cluster_position"] = "establish"
            head_unit["floor_subdivision_index"] = idx
            part.append(head_unit)
            head_uid = str(head_unit.get("unit_id"))
            for unit in group[1:]:
                copied = dict(unit)
                copied["cluster_id"] = minted
                copied["cluster_role"] = "interstitial"
                copied["parent_slide_id"] = head_uid
                copied["floor_subdivision_index"] = idx
                part.append(copied)
        _recount_part(part)
        out.extend(part)
    return out


# --------------------------------------------------------------------------- #
# the honoring                                                                  #
# --------------------------------------------------------------------------- #
def honor_min_cluster_floor(
    plan_units: Any, floor: Any, *, extracted_source: str | None = None
) -> list[Any]:
    """Return a split-only reshaped ``plan_units`` with >= ``floor`` clusters,
    or raise.

    Deterministic distribution (ported): cluster runs are visited in order and
    each is split at its EARLIEST legitimate seams until the deficit is met.
    Reaches EXACTLY ``floor`` clusters when the seams allow; raises
    ``ClusterFloorMismatchError`` (never an over-fragmenting forced split) when
    they do not. When ``extracted_source`` is provided, anchors must
    additionally resolve verbatim into it — and it IS provided on EVERY
    production dispatch: 04A creation obviously, and ALSO the 05/05B
    refinement passes, whose manifest nodes project the same corpus as 04A
    (``dependency_projections.bundle_reference: {from: texas}``,
    ``state/config/pipeline-manifest.yaml:411-414`` and ``:429-435``), so
    carried-forward anchors (A-4) resolve against the SAME extracted source.
    ``extracted_source=None`` (schema+role-only checking) is a DEGRADED
    defensive fallback for a corpus-delivery regression, not a production
    shape. Anchors duplicated across units are unresolvable for seam purposes
    (R4 veto; see :func:`duplicated_anchors`).
    """
    if not isinstance(plan_units, list):
        raise InvalidFloorConfigError(
            f"plan_units must be a list of plan-unit dicts; got {type(plan_units).__name__}"
        )
    if isinstance(floor, bool) or not isinstance(floor, int) or floor < 1:
        raise InvalidFloorConfigError(
            f"min_cluster_floor must be a positive int; got {floor!r}"
        )

    runs = group_plan_clusters(plan_units)
    count = len(runs)
    if floor <= count:
        return list(plan_units)  # already honored — identity no-op

    deficit = floor - count
    duplicated = duplicated_anchors(plan_units)
    seams_per_run: list[list[int]] = []
    dup_vetoed_runs: list[str] = []
    total_available = 0
    for cid, units in runs:
        seams = _run_seams(units, extracted_source, duplicated)
        seams_per_run.append(seams)
        total_available += len(seams)
        # R4 distinct diagnostic: record multi-unit runs zeroed by the
        # duplicate-anchor veto so triage is not misdirected to the generic
        # styleguide-vs-content framing.
        if (
            not seams
            and len(units) >= 2
            and duplicated
            and any(
                (_normalized_unit_refs(unit) or frozenset()) & duplicated
                for unit in units
            )
        ):
            dup_vetoed_runs.append(cid)

    if total_available < deficit:
        dup_note = (
            "; duplicate-anchor veto: cluster(s) "
            f"{sorted(dup_vetoed_runs)} carry a source_refs anchor reused "
            "across multiple units — ambiguous citations are unresolvable for "
            "seam purposes (refuse over guess)"
            if dup_vetoed_runs
            else ""
        )
        raise ClusterFloorMismatchError(
            f"min_cluster_floor={floor} cannot be honored: content has {count} "
            f"cluster(s) with only {total_available} legitimate internal seam(s) "
            f"(max reachable {count + total_available}); refusing to over-fragment "
            f"(styleguide-vs-content mismatch){dup_note}"
        )

    used_cluster_ids = {cid for cid, _ in runs}
    result: list[Any] = []
    for (cid, units), seams in zip(runs, seams_per_run, strict=True):
        if deficit <= 0 or not seams:
            result.extend(units)
            continue
        take = min(len(seams), deficit)
        chosen = seams[:take]
        deficit -= take
        result.extend(_split_run(cid, units, chosen, used_cluster_ids))
    assert deficit == 0, f"floor distribution left deficit={deficit}"
    return result


def consume_min_cluster_floor(
    envelope_payload: Any,
    plan_units: Any,
    *,
    extracted_source: str | None = None,
) -> tuple[list[Any], FloorConsumption]:
    """Consult a bound ``min_cluster_floor`` and honor it; return
    ``(plan_units, receipt)``.

    When no floor is bound, returns the plan unchanged with a
    ``consulted=False`` receipt (quiet). When a floor is bound, honors it (may
    raise the mismatch veto) and returns a ``consulted=True`` receipt. The
    receipt is the dead-config discriminator. Runs at 04A creation AND the
    05/05B refinement passes — the LATEST pass must honor, because refinement
    CONSOLIDATES clusters (live-proven: 04A 10 -> 05/05B 7 on the Part-3
    baseline).
    """
    before = count_clusters(plan_units) if isinstance(plan_units, list) else 0
    floor = (
        envelope_payload.get("min_cluster_floor")
        if isinstance(envelope_payload, dict)
        else None
    )
    if floor is None:
        return plan_units, FloorConsumption(
            consulted=False, floor=None, clusters_before=before, clusters_after=before
        )
    honored = honor_min_cluster_floor(plan_units, floor, extracted_source=extracted_source)
    return honored, FloorConsumption(
        consulted=True,
        floor=int(floor),
        clusters_before=before,
        clusters_after=count_clusters(honored),
    )


def assert_floor_consulted(envelope_payload: Any, consumption: FloorConsumption) -> None:
    """Fail loud if a floor is bound in the payload but was never consulted.

    Discriminating pair (Murat, D-3): a consulted floor -> quiet; a
    bound-but-never-read floor -> ``DeadFloorConfigError``. Guards against a
    future refactor that threads the floor but silently drops its consumption
    (the exact dead-config loop the D1 adjudication found in the OLD wiring).
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


__all__ = [
    "ANCHOR_ROLES",
    "CLUSTER_FLOOR_LLM_FALLBACK_TAG",
    "CLUSTER_FLOOR_MISMATCH_TAG",
    "DEAD_FLOOR_CONFIG_TAG",
    "GROUPING_KEYS",
    "INVALID_FLOOR_CONFIG_TAG",
    "ClusterFloorMismatchError",
    "DeadFloorConfigError",
    "FloorConsumption",
    "InvalidFloorConfigError",
    "assert_floor_consulted",
    "classify_anchor_role",
    "consume_min_cluster_floor",
    "count_clusters",
    "duplicated_anchors",
    "flatten_plan_content",
    "group_plan_clusters",
    "honor_min_cluster_floor",
    "unit_source_refs",
]
