"""Pedagogical annotation overlay (P3 — Irene pass-1).

The additive, never-gating P3 overlay: one :class:`PedagogyAnnotation` per
ANNOTATABLE typed component, layered on top of the P2 universal-md corpus. P3
reads the universal-md FRONT MATTER (DD5) each component already carries
(``component_id`` / ``type`` / ``doc_ordinal`` / ``resolution_status`` /
``locator`` / ``provisional_los``) and emits a Bloom level, a pedagogical role,
a deterministic ``teaches_after`` ordering, the teachable verdict (derived from
the front-matter ``resolution_status``, NEVER from ``citation_resolutions`` —
Texas/Murat M8), and a bounded audit ``rationale``.

ARCHITECTURE (Winston W7/W11):
    ALL P3 logic + the model live in THIS module. It depends only on the
    low-level lesson_plan entity (:mod:`learning_objective`) and the schema base
    helpers; it MUST NOT import from ``app.marcus.orchestrator`` or any
    ``app.*.gates`` module (one-way arrow — the wiring brick imports THIS, never
    the reverse). It also MUST NOT import :mod:`g0_enrichment` (that module
    imports :class:`PedagogyAnnotation`; a back-import would be a cycle) — the
    wiring-time referential invariant duck-types the result instead.

Pydantic-v2 idioms (docs/dev-guide/pydantic-v2-schema-checklist.md):
    - ``ConfigDict(extra="forbid", validate_assignment=True, frozen=True)`` — a
      pedagogy annotation is a frozen value object; ``extra="forbid"`` REJECTS an
      unknown key (e.g. a removed ``companion``) rather than silently dropping it.
    - timezone-aware ``generated_at`` (validator rejects naive datetimes).
    - the closed ``bloom`` + ``pedagogical_role`` enums get THREE red-rejection
      surfaces each: the Pydantic ``Literal`` (construction + assignment), the
      emitted JSON-Schema ``enum`` array, and a ``TypeAdapter`` round-trip
      (``mode="before"`` validator) reached on construction AND re-hydration.
    - ``rationale`` is the audit surface: REQUIRED, non-empty, ``len <= 240``.
    - ``prerequisite_concepts`` is FREE-TEXT, NON-REFERENTIAL (concept phrases,
      not component_ids / objective_ids) — never cross-checked.
"""

from __future__ import annotations

import logging
import re
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Final, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    ValidationError,
    field_validator,
)

from app.marcus.lesson_plan.learning_objective import BloomLevel
from app.marcus.lesson_plan.source_type import SOURCE_TYPES
from app.models.state._base import enforce_tz_aware

if TYPE_CHECKING:  # annotation only — a runtime import would be a cycle
    from app.marcus.lesson_plan.g0_enrichment import G0EnrichmentResult

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Transform identity (W9 — rides the SAME corpus-fingerprint freeze key)
# ---------------------------------------------------------------------------

PEDAGOGY_TRANSFORM_VERSION: Final[str] = "ped-v1"
"""P3 transform version. Bumped on any annotation-logic shape/semantics change;
participates in the corpus-fingerprint freeze key (W9) so a bump invalidates the
frozen result rather than serving a stale annotation set."""

PEDAGOGY_OFFLINE_MODEL: Final[str] = "deterministic-pedagogy-offline"
"""Transform-model marker on the OFFLINE deterministic path (no live spend)."""

PEDAGOGY_LIVE_MODEL: Final[str] = "marcus"
"""Transform-model id on the LIVE path (the pre_gate_marcus seam)."""

# ---------------------------------------------------------------------------
# Coverage taxonomy (which typed components get an annotation)
# ---------------------------------------------------------------------------

LOAD_BEARING_TYPES: Final[frozenset[str]] = frozenset(
    {
        "slide",
        "narration",
        "quiz",
        "workbook",
        "assignment_instructions",
        "discussion_forum",
        "motion_script_storyboard",
        "exercise_lab",
    }
)
"""Typed-component kinds that carry instruction and therefore get an annotation.

``exercise_lab`` is load-bearing (a hands-on instructional activity that teaches),
ruled by Marcus alongside the other instruction-bearing kinds."""

SKIP_TYPES: Final[frozenset[str]] = frozenset(
    {"reference_citation", "rubric", "other"}
)
"""Kinds that are NOT annotated. ``reference_citation`` is provenance (pointed-at,
not taught); ``rubric`` is a grading instrument (pointed-at, not taught); ``other``
is the escape-hatch. (``learning_objective`` is NOT a member of the closed source
taxonomy and was removed — it was a phantom.)"""

# EXHAUSTIVENESS guard (MF-2): the P3 partition MUST cover the entire closed
# source taxonomy plus the ``other`` escape hatch, with no overlap. A future
# taxonomy addition in ``source_type.SOURCE_TYPES`` fails this guard at import
# until P3 assigns the new kind a disposition (load-bearing OR skip). A plain
# ``assert`` would be stripped under ``python -O``; raise explicitly so the
# invariant holds in every run mode.
_P3_TYPE_UNIVERSE: Final[frozenset[str]] = SOURCE_TYPES | frozenset({"other"})
if not LOAD_BEARING_TYPES.isdisjoint(SKIP_TYPES):
    raise RuntimeError(  # pragma: no cover - import-time invariant
        "P3 taxonomy partition overlap: "
        f"{LOAD_BEARING_TYPES & SKIP_TYPES} appear in both LOAD_BEARING_TYPES and SKIP_TYPES"
    )
if (LOAD_BEARING_TYPES | SKIP_TYPES) != _P3_TYPE_UNIVERSE:
    raise RuntimeError(  # pragma: no cover - import-time invariant
        "P3 taxonomy partition is non-exhaustive: "
        f"unassigned={_P3_TYPE_UNIVERSE - (LOAD_BEARING_TYPES | SKIP_TYPES)}, "
        f"phantom={(LOAD_BEARING_TYPES | SKIP_TYPES) - _P3_TYPE_UNIVERSE}"
    )


def is_annotatable(component_type: str | None) -> bool:
    """True iff a component of ``component_type`` gets a P3 annotation.

    Annotatable iff the type is load-bearing. SKIP_TYPES (and any unknown type)
    are not annotated — a deterministic coverage helper, no LLM.
    """
    return component_type in LOAD_BEARING_TYPES


# ---------------------------------------------------------------------------
# Closed enums (three red-rejection surfaces each)
# ---------------------------------------------------------------------------

PedagogicalRole = Literal[
    "definition",
    "motivation",
    "worked_example",
    "synthesis",
    "assessment",
    "practice",
]
"""The closed pedagogical-role set (charter P3)."""

# Surface 3 (TypeAdapter round-trip) for each closed enum — a value outside the
# set is rejected here as well as by the Literal annotation (surface 1) and the
# emitted JSON-Schema enum array (surface 2).
_BLOOM_ADAPTER: TypeAdapter[BloomLevel] = TypeAdapter(BloomLevel)
_ROLE_ADAPTER: TypeAdapter[PedagogicalRole] = TypeAdapter(PedagogicalRole)

PEDAGOGY_BLOOM_LEVELS: Final[frozenset[str]] = frozenset(_BLOOM_ADAPTER.json_schema()["enum"])
PEDAGOGY_ROLES: Final[frozenset[str]] = frozenset(_ROLE_ADAPTER.json_schema()["enum"])

# An lo_ref is a g0-minted objective id (``lo-g0-NNN``). FORMAT is validated on the
# model; the cross-object ``lo_ref ⊆ provisional_los`` containment check is a
# WIRING-time invariant (assert_pedagogy_referential_invariant), not a field rule.
_LO_REF_RE: Final[re.Pattern[str]] = re.compile(r"lo-g0-\d+")

_RATIONALE_MAX_CHARS: Final[int] = 240


# ---------------------------------------------------------------------------
# The annotation model
# ---------------------------------------------------------------------------


class PedagogyAnnotation(BaseModel):
    """One component's P3 pedagogical annotation (additive; never gates).

    Built by :func:`build_pedagogy_annotations` over the P2 universal-md
    front-matter, frozen onto :class:`G0EnrichmentResult.pedagogy_annotations`.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    component_id: str = Field(
        ..., min_length=1, description="The typed component this annotation is about."
    )
    lo_refs: tuple[str, ...] = Field(
        default=(),
        description=(
            "Objective ids (``lo-g0-NNN``) this component serves. FORMAT-checked "
            "here; the ⊆ provisional_los containment check is enforced at wiring time."
        ),
    )
    bloom: BloomLevel = Field(
        ..., description="Revised-Bloom cognitive level (closed set, 3 red surfaces)."
    )
    pedagogical_role: PedagogicalRole = Field(
        ..., description="Closed pedagogical role (3 red surfaces)."
    )
    teaches_after: tuple[str, ...] = Field(
        default=(),
        description=(
            "Component ids this component teaches AFTER (deterministic: every "
            "annotatable component ordered strictly before it by doc_ordinal, "
            "locator). Byte-identical across runs."
        ),
    )
    prerequisite_concepts: tuple[str, ...] = Field(
        default=(),
        description=(
            "FREE-TEXT, NON-REFERENTIAL prerequisite concept phrases (NOT "
            "component_ids / objective_ids). Never cross-checked."
        ),
    )
    assessment_link: str | None = Field(
        default=None,
        description="A component_id this component assesses, or None.",
    )
    teachable: bool = Field(
        ...,
        description=(
            "False iff the front-matter resolution_status is ungrounded/failed "
            "(derived via derive_teachable; NEVER from citation_resolutions)."
        ),
    )
    rationale: str = Field(
        ...,
        description="Audit surface: REQUIRED, non-empty, len <= 240.",
    )
    transform_model: str = Field(
        default=PEDAGOGY_OFFLINE_MODEL,
        min_length=1,
        description="The model/marker that produced this annotation.",
    )
    transform_version: str = Field(
        default=PEDAGOGY_TRANSFORM_VERSION,
        min_length=1,
        description="P3 transform version (participates in the W9 freeze key).",
    )
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=UTC),
        description="Timezone-aware UTC generation time.",
    )

    @field_validator("bloom", mode="before")
    @classmethod
    def _round_trip_bloom(cls, value: object) -> object:
        # Surface 3: TypeAdapter round-trip (reached on construction AND on
        # re-hydration via model_validate / load_pedagogy_annotation).
        return _BLOOM_ADAPTER.validate_python(value)

    @field_validator("pedagogical_role", mode="before")
    @classmethod
    def _round_trip_role(cls, value: object) -> object:
        return _ROLE_ADAPTER.validate_python(value)

    @field_validator("lo_refs")
    @classmethod
    def _validate_lo_ref_format(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for ref in value:
            if not isinstance(ref, str) or not _LO_REF_RE.fullmatch(ref):
                raise ValueError(
                    f"lo_ref {ref!r} is not a g0 objective id (expected 'lo-g0-NNN')"
                )
        return value

    @field_validator("rationale")
    @classmethod
    def _validate_rationale(cls, value: str) -> str:
        # Audit surface: required + non-empty + bounded. (Not the §6 "verbatim
        # free-text" case — this is a generated audit string with a hard bound.)
        if not value or not value.strip():
            raise ValueError("rationale is required and must be non-empty")
        if len(value) > _RATIONALE_MAX_CHARS:
            raise ValueError(
                f"rationale must be <= {_RATIONALE_MAX_CHARS} chars (got {len(value)})"
            )
        return value

    @field_validator("generated_at")
    @classmethod
    def _enforce_tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)


def pedagogy_annotation_json_schema() -> dict[str, Any]:
    """Emit the canonical JSON Schema for the :class:`PedagogyAnnotation` family."""
    return PedagogyAnnotation.model_json_schema()


def load_pedagogy_annotation(payload: dict[str, Any]) -> PedagogyAnnotation:
    """Re-hydrate a :class:`PedagogyAnnotation` from a dict (the loader surface).

    A closed-enum violation (e.g. ``bloom='synthesizing'``) is rejected here too
    (surface-3 round-trip + Literal validator both fire on ``model_validate``), so
    a bad value cannot enter through deserialization.
    """
    return PedagogyAnnotation.model_validate(payload)


# ---------------------------------------------------------------------------
# Front-matter accessors (P3 reads the DD5 universal-md front matter)
# ---------------------------------------------------------------------------


def _rec_id(rec: dict[str, Any]) -> str | None:
    return rec.get("component_id")


def _rec_type(rec: dict[str, Any]) -> str | None:
    return rec.get("type") or rec.get("component_type")


def _rec_ordinal(rec: dict[str, Any]) -> Any:
    return rec.get("doc_ordinal")


def _rec_locator(rec: dict[str, Any]) -> str:
    return rec.get("locator") or ""


def _rec_status(rec: dict[str, Any]) -> Any:
    return rec.get("resolution_status")


def _rec_los(rec: dict[str, Any]) -> list[str]:
    los = rec.get("provisional_los") or []
    return [str(x) for x in los]


def _lo_objective_id(lo: Any) -> str | None:
    """Extract objective_id from a LearningObjective or a plain dict."""
    if isinstance(lo, dict):
        return lo.get("objective_id")
    return getattr(lo, "objective_id", None)


# ---------------------------------------------------------------------------
# Deterministic pure helpers (no LLM)
# ---------------------------------------------------------------------------

# Sentinel doc_ordinal used only for sort-stability when a record's ordinal is
# missing/non-int (the pre-flight rejects such records before annotation, so this
# is defence-in-depth, never the live path).
_ORDINAL_SENTINEL: Final[int] = 1_000_000_000


def _sort_key(rec: dict[str, Any]) -> tuple[int, str, str]:
    """Total, deterministic order key: doc_ordinal, then locator, then id.

    ``doc_ordinal`` is the DOCUMENT-total primary key; ``locator`` is the
    intra-doc secondary key (same-file components tie on doc_ordinal → break by
    locator); ``component_id`` is a final tie-break so the order is TOTAL and
    byte-identical across runs even on identical (doc_ordinal, locator).
    """
    ordinal = _rec_ordinal(rec)
    ordinal_int = ordinal if isinstance(ordinal, int) and not isinstance(ordinal, bool) else (
        _ORDINAL_SENTINEL
    )
    return (ordinal_int, _rec_locator(rec), str(_rec_id(rec)))


def compute_teaches_after(
    component: dict[str, Any],
    all_components_in_doc_order: list[dict[str, Any]],
) -> tuple[str, ...]:
    """Deterministic ``teaches_after``: annotatable components ordered before this one.

    Ordered by numeric ``doc_ordinal`` (document-total) then ``locator`` (intra-doc
    secondary key) then ``component_id`` (total-order tie-break). A component
    teaches_after every ANNOTATABLE component whose sort key is strictly less than
    its own. Pure + byte-identical across runs (no LLM).
    """
    target = _sort_key(component)
    ordered = sorted(all_components_in_doc_order, key=_sort_key)
    return tuple(
        cid
        for rec in ordered
        if is_annotatable(_rec_type(rec))
        and _sort_key(rec) < target
        and (cid := _rec_id(rec)) is not None
    )


def derive_teachable(resolution_status: Any) -> bool:
    """True iff the front-matter resolution_status is exactly ``resolved`` (M8).

    Read from the universal-md FRONT-MATTER ``resolution_status`` ONLY — never
    from ``citation_resolutions`` (Texas/Murat M8: a divergence is resolved in
    favour of the front matter).

    Fail-SAFE WHITELIST (S-5): the closed status set is {resolved, failed,
    ungrounded}, so ``== "resolved"`` is equivalent to the prior blacklist for
    valid data but defaults an UNKNOWN/unexpected status to NOT teachable (a
    blacklist would have defaulted an unknown status to teachable=True).
    """
    return resolution_status == "resolved"


# Deterministic OFFLINE type→role / type→bloom maps (reproducible placeholders;
# the LIVE pass produces the real pedagogy). Every value is a closed-enum member.
_OFFLINE_ROLE_BY_TYPE: Final[dict[str, PedagogicalRole]] = {
    "slide": "definition",
    "narration": "motivation",
    "quiz": "assessment",
    "workbook": "practice",
    "assignment_instructions": "practice",
    "discussion_forum": "synthesis",
    "motion_script_storyboard": "motivation",
    "exercise_lab": "practice",
}
_OFFLINE_BLOOM_BY_TYPE: Final[dict[str, BloomLevel]] = {
    "slide": "understand",
    "narration": "understand",
    "quiz": "apply",
    "workbook": "apply",
    "assignment_instructions": "apply",
    "discussion_forum": "evaluate",
    "motion_script_storyboard": "understand",
    "exercise_lab": "apply",
}


# ---------------------------------------------------------------------------
# Pre-flight + cross-object invariants (wiring-time guards)
# ---------------------------------------------------------------------------


def assert_p2_frontmatter_present(
    components: list[dict[str, Any]],
    provisional_los: list[Any],
) -> None:
    """A10 pre-flight: hard-fail on raw source (no P2 universal-md front matter).

    Raises BEFORE any annotation work if any component record lacks a numeric
    ``doc_ordinal`` or a ``resolution_status``, or if the provisional-LO set
    carries an entry with no ``objective_id``. P3 consumes the P2 universal-md
    front matter — feeding raw source is a hard error, not a silent best-effort.
    """
    for rec in components:
        if not _rec_id(rec):
            raise ValueError(
                "P3 pre-flight: a component record lacks a component_id "
                "(raw source, not P2 universal-md front matter)"
            )
        ordinal = _rec_ordinal(rec)
        if not isinstance(ordinal, int) or isinstance(ordinal, bool):
            raise ValueError(
                f"P3 pre-flight: component {_rec_id(rec)!r} lacks a numeric "
                "doc_ordinal (raw source, not P2 universal-md front matter)"
            )
        if not _rec_status(rec):
            raise ValueError(
                f"P3 pre-flight: component {_rec_id(rec)!r} lacks resolution_status "
                "(raw source, not P2 universal-md front matter)"
            )
    for lo in provisional_los:
        if not _lo_objective_id(lo):
            raise ValueError(
                "P3 pre-flight: a provisional LO lacks an objective_id "
                "(raw source, not P2 universal-md front matter)"
            )


def assert_pedagogy_referential_invariant(result: G0EnrichmentResult) -> None:
    """Wiring-time M5 cross-object guard (mirrors ``assert_run_dissent_invariant``).

    Hard-fail (RAISE) if any annotation references something that does not exist:
      - every ``lo_ref`` ∈ the result's provisional-LO objective_ids;
      - every ``assessment_link`` (when not None) ∈ the component_ids;
      - every ``teaches_after`` id ∈ the component_ids.

    Duck-types ``result`` (reads ``.typed_components`` / ``.provisional_los`` /
    ``.pedagogy_annotations``) so this module needs no runtime import of
    :class:`G0EnrichmentResult` (which would be a cycle).
    """
    component_ids = {c.component_id for c in result.typed_components}
    lo_ids = {lo.objective_id for lo in result.provisional_los}
    for ann in result.pedagogy_annotations:
        for ref in ann.lo_refs:
            if ref not in lo_ids:
                raise ValueError(
                    f"P3 referential invariant: annotation {ann.component_id!r} cites "
                    f"lo_ref {ref!r} which is NOT a provisional LO (fabricated)"
                )
        if ann.assessment_link is not None and ann.assessment_link not in component_ids:
            raise ValueError(
                f"P3 referential invariant: annotation {ann.component_id!r} has "
                f"assessment_link {ann.assessment_link!r} which is NOT a component"
            )
        for tid in ann.teaches_after:
            if tid not in component_ids:
                raise ValueError(
                    f"P3 referential invariant: annotation {ann.component_id!r} has "
                    f"teaches_after id {tid!r} which is NOT a component"
                )


def assert_pedagogy_teachable_consistency(
    annotations: tuple[PedagogyAnnotation, ...] | list[PedagogyAnnotation],
    components: list[dict[str, Any]],
) -> None:
    """M5-c guard: ``teachable`` must match the front-matter resolution_status.

    Catches a tampered annotation (e.g. ``teachable=True`` forced onto a
    front-matter-``failed`` component) — a contradiction the build path can never
    produce but a downstream edit could. RAISE on contradiction.
    """
    status_by_id = {_rec_id(r): _rec_status(r) for r in components}
    for ann in annotations:
        status = status_by_id.get(ann.component_id)
        if status is None:
            continue  # id-existence is the referential invariant's job
        expected = derive_teachable(status)
        if ann.teachable != expected:
            raise ValueError(
                f"P3 teachable contradiction: annotation {ann.component_id!r} has "
                f"teachable={ann.teachable} but front-matter resolution_status="
                f"{status!r} implies teachable={expected}"
            )


# ---------------------------------------------------------------------------
# Offline + live annotation passes
# ---------------------------------------------------------------------------


def _offline_pedagogy_pass(
    components: list[dict[str, Any]],
    provisional_los: list[Any],
    *,
    transform_version: str,
    generated_at: datetime | None,
) -> tuple[PedagogyAnnotation, ...]:
    """Deterministic OFFLINE annotation pass (reproducible; no LLM).

    Mirrors ``g0_enrichment_wiring._offline_pre_pass``: produces deterministic
    placeholder bloom / role / lo_refs / rationale so offline tests are
    byte-stable. Only ANNOTATABLE components get an annotation.
    """
    when = generated_at or datetime.now(tz=UTC)
    valid_lo_ids = {_lo_objective_id(lo) for lo in provisional_los}
    annotations: list[PedagogyAnnotation] = []
    for rec in components:
        ctype = _rec_type(rec)
        if not is_annotatable(ctype):
            continue
        cid = _rec_id(rec)
        role = _OFFLINE_ROLE_BY_TYPE.get(ctype or "", "definition")
        bloom = _OFFLINE_BLOOM_BY_TYPE.get(ctype or "", "understand")
        status = _rec_status(rec)
        teachable = derive_teachable(status)
        lo_refs = tuple(oid for oid in _rec_los(rec) if oid in valid_lo_ids)
        teaches_after = compute_teaches_after(rec, components)
        rationale = (
            f"offline deterministic pedagogy annotation for {cid}: role={role}, "
            f"bloom={bloom}, teachable={teachable}."
        )[:_RATIONALE_MAX_CHARS]
        annotations.append(
            PedagogyAnnotation(
                component_id=str(cid),
                lo_refs=lo_refs,
                bloom=bloom,
                pedagogical_role=role,
                teaches_after=teaches_after,
                prerequisite_concepts=(),
                assessment_link=None,
                teachable=teachable,
                rationale=rationale,
                transform_model=PEDAGOGY_OFFLINE_MODEL,
                transform_version=transform_version,
                generated_at=when,
            )
        )
    return tuple(annotations)


def _content_to_text(content: Any) -> str:
    """Coerce a chat-model ``response.content`` to text.

    Handles a bare str AND the content-block list shape (``[{"type":"text",
    "text":"..."}]``) some adapters return. Anything else degrades to ``""``.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                text = block.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return "".join(parts)
    return ""


def _extract_pedagogy_rows(content: Any) -> list[Any]:
    """S-1 tolerant parse of the live response into the annotation-row list.

    Strips ```json code fences, extracts the first ``{...}`` span when the body
    carries surrounding prose, and handles a non-str ``content`` (content-block
    list). On ANY parse failure (or a non-object / non-list ``annotations``) it
    DEGRADES to ``[]`` (no annotations) with a warning rather than raising —
    pedagogy is ADDITIVE and never gating, so a malformed response yields an
    empty overlay, not a crashed build.
    """
    import json

    text = _content_to_text(content).strip()
    if not text:
        logger.warning("g0-pedagogy live: empty response content; emitting no annotations")
        return []
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    payload: Any = None
    try:
        payload = json.loads(text)
    except (ValueError, TypeError):
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                payload = json.loads(text[start : end + 1])
            except (ValueError, TypeError):
                payload = None
    if not isinstance(payload, dict):
        logger.warning(
            "g0-pedagogy live: response not parseable as a JSON object; "
            "emitting no annotations"
        )
        return []
    rows = payload.get("annotations", [])
    if not isinstance(rows, list):
        logger.warning(
            "g0-pedagogy live: 'annotations' is %s, not a list; emitting no annotations",
            type(rows).__name__,
        )
        return []
    return rows


def _normalize_enum_value(value: Any, valid: frozenset[str]) -> str | None:
    """Normalize a model-supplied enum string (lower/strip/spaces→underscores).

    Returns the normalized value iff it lands in ``valid`` after normalization,
    else ``None`` (caller falls back to the deterministic offline default rather
    than dropping the whole row). A non-str value yields ``None``.
    """
    if not isinstance(value, str):
        return None
    norm = value.strip().lower().replace(" ", "_")
    return norm if norm in valid else None


def _build_live_annotations(
    rows: list[Any],
    *,
    by_id: dict[Any, dict[str, Any]],
    valid_lo_ids: set[Any],
    component_ids: set[Any],
    components: list[dict[str, Any]],
    transform_version: str,
    when: datetime,
) -> tuple[PedagogyAnnotation, ...]:
    """Parse model annotation rows into validated annotations (resilient loop).

    MF-1: EACH row is constructed inside ``try/except`` (mirrors
    ``_parse_live_payload``) — one malformed row is logged + skipped, never
    aborting the whole pass (which would discard every other annotation and crash
    ``build_enrichment_result``). Salvage near-misses before constructing:

      * normalize + clamp ``bloom`` / ``pedagogical_role`` to the closed enums,
        falling back to the deterministic offline default for the component type
        when the model value is unsalvageable (S-2/MF-1);
      * filter ``lo_refs`` by BOTH membership AND the ``lo-g0-NNN`` format, dedup
        (S-2 / NIT);
      * coerce list-shaped fields, never char-splat a string (S-3);
      * drop an ``assessment_link`` that is not a real component id OR is a
        self-link, logging the drop (S-4);
      * derive ``teachable`` from the front-matter status ONLY (M8).
    """
    annotations: list[PedagogyAnnotation] = []
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            logger.warning("g0-pedagogy live: skipping non-dict annotation row %r", row)
            continue
        cid = str(row.get("component_id") or "").strip()
        rec = by_id.get(cid)
        if rec is None and cid:
            # Salvage: the model sometimes echoes the whole Components line
            # ("src-001-c011 (type=slide, locator=…)") as the id. Take the
            # leading token before the first space/paren and re-match.
            head = cid.split("(", 1)[0].split()[0] if cid.split() else ""
            if head in by_id:
                cid, rec = head, by_id[head]
        if not cid or rec is None:
            logger.warning(
                "g0-pedagogy live: skipping row with missing/unknown component_id %r "
                "(not an annotatable component)",
                cid or "<missing>",
            )
            continue
        if cid in seen:
            logger.warning("g0-pedagogy live: duplicate annotation for %r; keeping first", cid)
            continue
        ctype = _rec_type(rec)
        try:
            bloom = _normalize_enum_value(row.get("bloom"), PEDAGOGY_BLOOM_LEVELS) or (
                _OFFLINE_BLOOM_BY_TYPE.get(ctype or "", "understand")
            )
            role = _normalize_enum_value(row.get("pedagogical_role"), PEDAGOGY_ROLES) or (
                _OFFLINE_ROLE_BY_TYPE.get(ctype or "", "definition")
            )
            raw_refs = row.get("lo_refs")
            ref_list = raw_refs if isinstance(raw_refs, list) else ()
            lo_refs = tuple(
                dict.fromkeys(
                    oid
                    for oid in ref_list
                    if oid in valid_lo_ids
                    and isinstance(oid, str)
                    and _LO_REF_RE.fullmatch(oid)
                )
            )
            raw_prereq = row.get("prerequisite_concepts")
            prereq = tuple(raw_prereq) if isinstance(raw_prereq, list) else ()
            link = row.get("assessment_link")
            if link == cid:
                logger.warning(
                    "g0-pedagogy live: dropping self-referential assessment_link on %r", cid
                )
                link = None
            elif link is not None and link not in component_ids:
                logger.warning(
                    "g0-pedagogy live: dropping assessment_link %r on %r (not a component)",
                    link,
                    cid,
                )
                link = None
            ann = PedagogyAnnotation(
                component_id=cid,
                lo_refs=lo_refs,
                bloom=bloom,
                pedagogical_role=role,
                teaches_after=compute_teaches_after(rec, components),
                prerequisite_concepts=prereq,
                assessment_link=link,
                teachable=derive_teachable(_rec_status(rec)),  # M8: front matter wins
                rationale=(str(row.get("rationale") or f"annotation for {cid}"))[
                    :_RATIONALE_MAX_CHARS
                ],
                transform_model=PEDAGOGY_LIVE_MODEL,
                transform_version=transform_version,
                generated_at=when,
            )
        except (ValidationError, ValueError, TypeError) as exc:
            logger.warning(
                "g0-pedagogy live: dropping malformed annotation row for %r (%s); "
                "keeping every other annotation",
                cid or "<missing>",
                exc,
            )
            continue
        seen.add(cid)
        if is_annotatable(ctype) and ann.teachable and not ann.lo_refs:
            logger.warning(
                "g0-pedagogy live: annotatable+teachable component %r has empty lo_refs "
                "(pedagogical orphan — not consumed by P5)",
                cid,
            )
        annotations.append(ann)
    return tuple(annotations)


def _live_pedagogy_pass(
    components: list[dict[str, Any]],
    provisional_los: list[Any],
    chat_model_factory: Any | None,
    *,
    transform_version: str,
    generated_at: datetime | None,
) -> tuple[PedagogyAnnotation, ...]:  # pragma: no cover - live leg
    """REAL P3 pass via the pre_gate_marcus chat-model seam (temp=0, single-pass).

    Mirrors ``g0_enrichment_wiring._live_pre_pass``: a single deterministic
    (temp=0) call, model + version pinned, NO resample. Off the offline test
    path (exercised only by the operator-gated live leg). The teachable verdict
    is ALWAYS derived from the front-matter resolution_status (M8) — never taken
    from the model. The fragile parse + per-row construction live in
    ``_extract_pedagogy_rows`` / ``_build_live_annotations`` (offline-tested).
    """
    when = generated_at or datetime.now(tz=UTC)
    valid_lo_ids = {_lo_objective_id(lo) for lo in provisional_los}
    annotatable = [rec for rec in components if is_annotatable(_rec_type(rec))]
    by_id = {_rec_id(rec): rec for rec in annotatable}
    # S-4: an assessment_link may point at ANY component (the referential
    # invariant allows it), not only annotatable ones.
    component_ids = {_rec_id(rec) for rec in components}

    if chat_model_factory is None:
        from app.models.adapter import make_chat_model

        chat_model_factory = make_chat_model
    handle = chat_model_factory(PEDAGOGY_LIVE_MODEL)
    prompt = _render_live_pedagogy_prompt(annotatable, provisional_los)
    # A11 = SINGLE deterministic pass, no resample. Temperature is bound at
    # construction by make_chat_model (mirror _live_pre_pass — do NOT pass a
    # per-call temperature: gpt-5 is a reasoning model that rejects any
    # temperature other than its default, 400ing on an explicit 0).
    response = handle.chat.invoke([{"role": "user", "content": prompt}])
    rows = _extract_pedagogy_rows(response.content)
    return _build_live_annotations(
        rows,
        by_id=by_id,
        valid_lo_ids=valid_lo_ids,
        component_ids=component_ids,
        components=components,
        transform_version=transform_version,
        when=when,
    )


def _render_live_pedagogy_prompt(
    annotatable: list[dict[str, Any]],
    provisional_los: list[Any],
) -> str:  # pragma: no cover - live leg
    """Build the live P3 prompt block (component front matter + the LO set).

    The per-annotation JSON contract is specified EXPLICITLY (keys + closed
    vocabularies + a verbatim-``component_id`` requirement) so the model echoes
    the id the parser keys on (``_build_live_annotations``) and returns in-enum
    bloom/role. LO statements (not just ids) are included so ``lo_refs`` is a
    meaningful pedagogical mapping rather than an id guess.
    """
    lo_lines = [
        f"- {oid}: {getattr(lo, 'statement', '')}"
        for lo in provisional_los
        if (oid := _lo_objective_id(lo))
    ]
    comp_lines = [
        f'- component_id="{_rec_id(rec)}" type={_rec_type(rec)} '
        f"locator={_rec_locator(rec)}"
        for rec in annotatable
    ]
    bloom_vocab = "|".join(PEDAGOGY_BLOOM_LEVELS)
    role_vocab = "|".join(PEDAGOGY_ROLES)
    return (
        "You are an instructional designer adding a pedagogy overlay. For EACH "
        "component listed below, emit exactly one annotation object. Return ONLY "
        "JSON of this shape (no prose, no markdown fences):\n"
        '{"annotations": [{'
        '"component_id": "<copy VERBATIM from the Components list>", '
        f'"bloom": "<{bloom_vocab}>", '
        f'"pedagogical_role": "<{role_vocab}>", '
        '"lo_refs": ["<objective id(s) this component teaches or assesses>"], '
        '"prerequisite_concepts": ["<short concept>"], '
        '"assessment_link": "<component_id of the quiz/assessment that tests this, or null>", '
        '"rationale": "<=240 char justification for the bloom+role+lo_refs"'
        "}]}\n"
        "Rules: component_id MUST be copied verbatim from the Components list; "
        "lo_refs MUST be chosen only from the Objective ids below (or [] if none "
        "applies); bloom and pedagogical_role MUST be one of the listed values.\n"
        "Objectives:\n" + "\n".join(lo_lines) + "\n"
        "Components:\n" + "\n".join(comp_lines)
    )


def build_pedagogy_annotations(
    components: list[dict[str, Any]],
    provisional_los: list[Any],
    *,
    dispatch_live: bool = False,
    chat_model_factory: Any | None = None,
    transform_version: str = PEDAGOGY_TRANSFORM_VERSION,
    generated_at: datetime | None = None,
) -> tuple[PedagogyAnnotation, ...]:
    """Build per-component P3 annotations over the P2 universal-md front matter.

    Runs the A10 pre-flight, then the OFFLINE deterministic pass (default) or the
    LIVE pass (``dispatch_live=True``; gated exactly like the citation resolver).
    The offline path is what the test surface exercises; the live path is NOT run
    in the offline build.
    """
    assert_p2_frontmatter_present(components, provisional_los)
    if dispatch_live:
        return _live_pedagogy_pass(
            components,
            provisional_los,
            chat_model_factory,
            transform_version=transform_version,
            generated_at=generated_at,
        )
    return _offline_pedagogy_pass(
        components,
        provisional_los,
        transform_version=transform_version,
        generated_at=generated_at,
    )


__all__ = [
    "LOAD_BEARING_TYPES",
    "PEDAGOGY_BLOOM_LEVELS",
    "PEDAGOGY_LIVE_MODEL",
    "PEDAGOGY_OFFLINE_MODEL",
    "PEDAGOGY_ROLES",
    "PEDAGOGY_TRANSFORM_VERSION",
    "SKIP_TYPES",
    "PedagogicalRole",
    "PedagogyAnnotation",
    "assert_p2_frontmatter_present",
    "assert_pedagogy_referential_invariant",
    "assert_pedagogy_teachable_consistency",
    "build_pedagogy_annotations",
    "compute_teaches_after",
    "derive_teachable",
    "is_annotatable",
    "load_pedagogy_annotation",
    "pedagogy_annotation_json_schema",
]
