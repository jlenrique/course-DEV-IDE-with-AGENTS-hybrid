"""Coverage receipt — the DERIVED two-axis ledger (T5 + T7 persistence).

The OBSERVED side of the interlock: ``coverage-receipt.json`` projected from joins
that ALREADY exist at the dispatch site (the ``ReconcileView`` pattern) — NO
producer self-report channel, NO coverage store outside the RAI (AC9). The receipt
is the JOIN of two orthogonal axes, NEVER merged (AC4):

  * Axis A — coverage (source→deliverable): per source point, where it was carried
    ``{covered_on_slide, covered_in_narration, both, deliberately_excluded, missing}``.
    Derived by projecting existing joins; the deterministic locator anchor resolves
    FIRST — no anchor → forced ``missing``, regardless of any LLM (AC7). The
    narration role-seed matcher's silent 0/>1 drop (``enrichment_consumption.py:335``)
    becomes a LOGGED ``missing`` here.
  * Axis B — containment (deliverable→source): ``{verbatim_preserved, altered,
    risky}`` via Vera-R7 at report-generation time (this interlock is R7's first
    REPORTING caller, ``voice_provider_text.audit_rhetorical_source_containment``).

vouch_level honesty fuse (AC6, Vera caveat — render-time, code-enforced): no
containment cell renders ``verified`` without a ``vouch_level`` stamp; ``verified``
is reserved for deterministic string/span matches (verbatim/numeric/dosing);
``negation``/``comparator`` → ``advisory_caveat`` (the bag-of-words flipped-negation
false-negative is DISCLOSED, never a green vouch). A ``missing`` point has NO
containment verdict (AC4).
"""

from __future__ import annotations

import logging
import re
from datetime import UTC, datetime
from typing import Any, Final, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, field_validator, model_validator

from app.marcus.lesson_plan.coverage_annotation import CoverageAnnotation
from app.marcus.lesson_plan.source_point import (
    CoverageIntentLiteral,
    RiskFlagLiteral,
    SegmentationGrain,
    SourcePoint,
)
from app.models.state._base import enforce_tz_aware
from app.specialists._shared.voice_provider_text import audit_rhetorical_source_containment

logger = logging.getLogger(__name__)

COVERAGE_RECEIPT_BASENAME: Final[str] = "coverage-receipt.json"
COVERAGE_RECEIPT_ASSET_ID: Final[str] = "coverage-receipt"

# ---------------------------------------------------------------------------
# Closed enums (three red-rejection surfaces each)
# ---------------------------------------------------------------------------

CoverageStatus = Literal[
    "covered_on_slide", "covered_in_narration", "both", "deliberately_excluded", "missing"
]
ContainmentVerdict = Literal["verbatim_preserved", "altered", "risky"]
VouchLevel = Literal["verified", "advisory_caveat", "not_assessed"]

_COVERAGE_STATUS_ADAPTER: TypeAdapter[CoverageStatus] = TypeAdapter(CoverageStatus)
_CONTAINMENT_ADAPTER: TypeAdapter[ContainmentVerdict] = TypeAdapter(ContainmentVerdict)
_VOUCH_ADAPTER: TypeAdapter[VouchLevel] = TypeAdapter(VouchLevel)

COVERAGE_STATUSES: Final[frozenset[str]] = frozenset(_COVERAGE_STATUS_ADAPTER.json_schema()["enum"])
CONTAINMENT_VERDICTS: Final[frozenset[str]] = frozenset(_CONTAINMENT_ADAPTER.json_schema()["enum"])
VOUCH_LEVELS: Final[frozenset[str]] = frozenset(_VOUCH_ADAPTER.json_schema()["enum"])

# Risk flags whose semantic check is a disclosed bag-of-words false-negative (Vera):
# they can NEVER carry a green `verified` vouch.
_ADVISORY_RISK: Final[frozenset[str]] = frozenset({"negation", "comparator"})

_WS_RE: Final[re.Pattern[str]] = re.compile(r"\s+")


def _normalize(text: str) -> str:
    return _WS_RE.sub(" ", text or "").strip().lower()


def _span_present(span: str, surface_text: str | None) -> bool:
    """Deterministic span presence at a resolved anchor (no LLM; AC7)."""
    if not surface_text:
        return False
    return _normalize(span) in _normalize(surface_text)


# ---------------------------------------------------------------------------
# Projected-join input (the anchors that ALREADY exist at the dispatch site)
# ---------------------------------------------------------------------------


class AnchorResolution(BaseModel):
    """The deterministic locator anchor for a ``slide_key`` (projected join, AC7).

    ``slide_present`` is the deterministic locator anchor (a deck slide exists for
    this key). ``narration_ambiguous`` carries the ``:335`` silent 0/>1 role-seed
    drop forward as an EXPLICIT signal so the receipt logs it as ``missing`` rather
    than dropping it silently.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    slide_key: str = Field(..., min_length=1)
    slide_present: bool = Field(
        default=False, description="A deck slide exists for this key (anchor)."
    )
    slide_text: str | None = Field(
        default=None, description="Rendered slide-surface text (for R7)."
    )
    narration_present: bool = Field(
        default=False, description="An UNAMBIGUOUS narration surface exists for this key."
    )
    narration_ambiguous: bool = Field(
        default=False, description="The :335 silent 0/>1 role-seed drop → logged missing."
    )
    narration_text: str | None = Field(default=None, description="Narration-surface text (for R7).")


# ---------------------------------------------------------------------------
# The receipt row (the join of the two axes; vouch_level render-time gate)
# ---------------------------------------------------------------------------


class CoverageReceiptRow(BaseModel):
    """One source point's coverage status × containment verdict + vouch (AC4/AC6).

    Render-time invariants (Vera caveat, code-enforced):
      - a ``missing`` / ``deliberately_excluded`` row has NO containment verdict and
        ``vouch_level == not_assessed`` (a missing point is a pure coverage hole);
      - a containment verdict requires a resolved anchor;
      - ``vouch_level == verified`` is reserved for a deterministic verbatim/numeric/
        dosing match (``verbatim_required`` and NO negation/comparator) and pairs
        only with ``verbatim_preserved`` — never a green vouch on a bag-of-words
        semantic check.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    source_point_id: str = Field(..., min_length=1)
    component_id: str = Field(..., min_length=1, description="Parent join key (AC1).")
    slide_key: str = Field(..., min_length=1)
    human_label: str = Field(
        ..., min_length=1, description="Operator-readable 'Slide N / note'."
    )
    intent_set: tuple[CoverageIntentLiteral, ...] = Field(
        ..., description="The point's intent SET."
    )
    risk_flags: tuple[RiskFlagLiteral, ...] = Field(default=())
    verbatim_required: bool = Field(...)
    coverage_status: CoverageStatus = Field(..., description="Axis A (source→deliverable).")
    containment_verdict: ContainmentVerdict | None = Field(
        default=None, description="Axis B (deliverable→source); None on a missing point."
    )
    vouch_level: VouchLevel = Field(..., description="Honesty fuse (AC6).")
    anchor_resolved: bool = Field(
        ..., description="A deterministic locator anchor resolved (AC7)."
    )
    verbatim_absent: bool = Field(
        default=False,
        description="A verbatim_required span failed deterministic presence at anchor.",
    )
    narration_obligation_unmet: bool = Field(
        default=False,
        description=(
            "A 'detail_in_narration' point whose span reached ONLY the slide (never the "
            "narration) — covered-on-slide does NOT satisfy a narration obligation (AC3). "
            "An independent BLOCK term (FIX 2): money-on-the-line for a must-cover point."
        ),
    )
    planned_on_slide: bool = Field(default=False)
    planned_in_narration: bool = Field(default=False)
    must_cover: bool = Field(
        ..., description="Absence is a money-on-the-line failure (gate input)."
    )
    segmentation: SegmentationGrain = Field(..., description="Load-bearing grain stamp (Irene).")
    r7_report: dict[str, Any] | None = Field(
        default=None,
        description="The R7 audit report behind the containment verdict (audit trail).",
    )

    @field_validator("coverage_status", mode="before")
    @classmethod
    def _rt_status(cls, v: object) -> object:
        return _COVERAGE_STATUS_ADAPTER.validate_python(v)

    @field_validator("vouch_level", mode="before")
    @classmethod
    def _rt_vouch(cls, v: object) -> object:
        return _VOUCH_ADAPTER.validate_python(v)

    @field_validator("containment_verdict", mode="before")
    @classmethod
    def _rt_verdict(cls, v: object) -> object:
        return None if v is None else _CONTAINMENT_ADAPTER.validate_python(v)

    @model_validator(mode="after")
    def _enforce_render_gate(self) -> CoverageReceiptRow:
        if self.coverage_status in {"missing", "deliberately_excluded"}:
            if self.containment_verdict is not None:
                raise ValueError(
                    f"{self.coverage_status} point {self.source_point_id!r} must carry NO "
                    "containment verdict (a coverage hole has no deliverable to contain)"
                )
            if self.vouch_level != "not_assessed":
                raise ValueError(
                    f"{self.coverage_status} point {self.source_point_id!r} must vouch "
                    "'not_assessed' (nothing was assessed)"
                )
        if self.containment_verdict is not None and not self.anchor_resolved:
            raise ValueError(
                f"point {self.source_point_id!r} has a containment verdict but NO resolved "
                "anchor (AC7: the judge never characterizes content off an unresolved anchor)"
            )
        if self.vouch_level == "verified":
            if not self.verbatim_required:
                raise ValueError(
                    f"point {self.source_point_id!r} vouches 'verified' without verbatim_required "
                    "(verified is reserved for deterministic verbatim/numeric/dosing matches, AC6)"
                )
            if set(self.risk_flags) & _ADVISORY_RISK:
                raise ValueError(
                    f"point {self.source_point_id!r} vouches 'verified' but carries a "
                    "negation/comparator risk → must be 'advisory_caveat' (disclosed bag-of-words "
                    "false-negative, AC6/Vera caveat)"
                )
            if self.containment_verdict != "verbatim_preserved":
                raise ValueError(
                    f"point {self.source_point_id!r} vouches 'verified' but verdict is "
                    f"{self.containment_verdict!r} (verified pairs only with verbatim_preserved)"
                )
        return self


class CoverageReceipt(BaseModel):
    """The DERIVED coverage ledger (a RunAssetEntry payload; AC9/AC10).

    Declares its ``segmentation`` grain on its face (Irene caveat — the honest
    denominator). Frozen value object; recomputed by ``derive_coverage_receipt``.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    segmentation: SegmentationGrain = Field(
        ..., description="The grain the whole receipt accounts at (declared, AC10)."
    )
    rows: tuple[CoverageReceiptRow, ...] = Field(default=())
    generated_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))

    @field_validator("generated_at")
    @classmethod
    def _tz(cls, v: datetime) -> datetime:
        return enforce_tz_aware(v)

    @model_validator(mode="after")
    def _enforce_grain_stamp(self) -> CoverageReceipt:
        for row in self.rows:
            if row.segmentation != self.segmentation:
                raise ValueError(
                    f"row {row.source_point_id!r} grain {row.segmentation!r} != receipt grain "
                    f"{self.segmentation!r} (Irene caveat: the stamp is never dropped)"
                )
        return self

    def missing_must_cover(self) -> tuple[CoverageReceiptRow, ...]:
        return tuple(r for r in self.rows if r.must_cover and r.coverage_status == "missing")


def coverage_receipt_json_schema() -> dict[str, Any]:
    return CoverageReceipt.model_json_schema()


def load_coverage_receipt(payload: dict[str, Any]) -> CoverageReceipt:
    return CoverageReceipt.model_validate(payload)


# ---------------------------------------------------------------------------
# Derivation (project existing joins; deterministic anchor FIRST)
# ---------------------------------------------------------------------------


def _human_label(slide_key: str) -> str:
    return f"{slide_key} / note"


def _derive_must_cover(point: SourcePoint) -> bool:
    """A must-cover point: absence is money-on-the-line (AC8 input).

    Deterministic: verbatim-required OR an intent that the point be detailed in
    narration (a detail-in-narration point is NOT satisfied by a slide alone). A
    deliberately-excluded (operator-signed) point is NEVER must-cover.
    """
    if "deliberately_excluded" in point.coverage_intents:
        return False
    return point.verbatim_required or "detail_in_narration" in point.coverage_intents


def _derive_row(
    point: SourcePoint,
    anchor: AnchorResolution | None,
    *,
    clinical_terms: frozenset[str] | None,
) -> CoverageReceiptRow:
    must_cover = _derive_must_cover(point)
    common = dict(
        source_point_id=point.source_point_id,
        component_id=point.component_id,
        slide_key=point.slide_key,
        human_label=_human_label(point.slide_key),
        intent_set=point.coverage_intents,
        risk_flags=point.risk_flags,
        verbatim_required=point.verbatim_required,
        segmentation=point.segmentation,
        must_cover=must_cover,
    )

    # Operator-signed exclusion is a terminal status (no anchor / containment needed).
    if "deliberately_excluded" in point.coverage_intents:
        return CoverageReceiptRow(
            **common, coverage_status="deliberately_excluded", containment_verdict=None,
            vouch_level="not_assessed", anchor_resolved=anchor is not None,
            planned_on_slide=bool(anchor and anchor.slide_present),
            planned_in_narration=bool(anchor and anchor.narration_present),
        )

    # AC7: the deterministic locator anchor resolves FIRST. No anchor → forced missing.
    if anchor is None or not (anchor.slide_present or anchor.narration_present):
        return CoverageReceiptRow(
            **common, coverage_status="missing", containment_verdict=None,
            vouch_level="not_assessed", anchor_resolved=anchor is not None,
            planned_on_slide=False, planned_in_narration=False,
        )

    # The :335 silent role-seed drop surfaces as an explicit signal — log it.
    narration_usable = anchor.narration_present and not anchor.narration_ambiguous
    if anchor.narration_ambiguous:
        logger.warning(
            "coverage: narration role-seed for %r is ambiguous (0/>1 match) → logged missing "
            "for the narration surface (enrichment_consumption.py:335 drop made explicit)",
            point.slide_key,
        )

    planned_on_slide = anchor.slide_present
    planned_in_narration = narration_usable

    on_slide = anchor.slide_present and _span_present(point.verbatim_text, anchor.slide_text)
    in_narration = narration_usable and _span_present(point.verbatim_text, anchor.narration_text)

    # FIX 2: a 'detail_in_narration' obligation is NOT satisfied by slide carriage
    # alone. If the point intends narration detail but its span never reaches the
    # narration surface, the narration obligation is UNMET (a must-cover hole the gate
    # blocks on independently of verbatim_absent).
    narration_obligation_unmet = (
        "detail_in_narration" in point.coverage_intents and not in_narration
    )

    # If a surface EXISTS but the span isn't found there, the point is still
    # "planned" for that surface (a coverage attempt) — coverage_status reflects
    # ACTUAL carriage; verbatim_absent flags the deterministic miss for the gate.
    surface_for_containment: str | None = None
    if on_slide and in_narration:
        status: CoverageStatus = "both"
        surface_for_containment = anchor.slide_text
    elif on_slide:
        status = "covered_on_slide"
        surface_for_containment = anchor.slide_text
    elif in_narration:
        status = "covered_in_narration"
        surface_for_containment = anchor.narration_text
    else:
        # A surface exists but the verbatim span is not carried on it → missing
        # carriage of THIS point (a real coverage hole even though a slide renders).
        status = "missing"

    if status == "missing":
        return CoverageReceiptRow(
            **common, coverage_status="missing", containment_verdict=None,
            vouch_level="not_assessed", anchor_resolved=True,
            planned_on_slide=planned_on_slide, planned_in_narration=planned_in_narration,
            verbatim_absent=point.verbatim_required,
            narration_obligation_unmet=narration_obligation_unmet,
        )

    verdict, vouch, r7_report, verbatim_absent = _derive_containment(
        point, surface_for_containment, clinical_terms=clinical_terms
    )
    return CoverageReceiptRow(
        **common, coverage_status=status, containment_verdict=verdict, vouch_level=vouch,
        anchor_resolved=True, planned_on_slide=planned_on_slide,
        planned_in_narration=planned_in_narration, verbatim_absent=verbatim_absent,
        narration_obligation_unmet=narration_obligation_unmet,
        r7_report=r7_report,
    )


def _derive_containment(
    point: SourcePoint,
    surface_text: str | None,
    *,
    clinical_terms: frozenset[str] | None,
) -> tuple[ContainmentVerdict, VouchLevel, dict[str, Any], bool]:
    """Axis B at a resolved, carried anchor — R7 is the REPORTING caller here (AC6).

    Returns ``(verdict, vouch_level, r7_report, verbatim_absent)``. ``verified`` is
    reserved for a deterministic verbatim/numeric/dosing span match with no
    negation/comparator risk; everything else is ``advisory_caveat`` (disclosed).
    """
    # R7 audit: does the deliverable surface introduce unsourced semantic tokens
    # relative to the source span? (this interlock is R7's first reporting caller.)
    report = audit_rhetorical_source_containment(
        surface_text or "", point.verbatim_text, clinical_terms=clinical_terms
    )
    span_present = _span_present(point.verbatim_text, surface_text)
    advisory_risk = bool(set(point.risk_flags) & _ADVISORY_RISK)

    if point.verbatim_required:
        if span_present and not advisory_risk:
            return "verbatim_preserved", "verified", report, False
        if span_present and advisory_risk:
            # the span is present but its polarity/comparison can't be deterministically
            # vouched (bag-of-words FN) → DISCLOSED advisory, never a green vouch.
            return "verbatim_preserved", "advisory_caveat", report, False
        # FIX 7 (dead-branch resolution): this `span_present is False` path is
        # UNREACHABLE from `_derive_row` — `_derive_containment` is only ever called
        # with `surface_for_containment` set to the surface on which the span WAS found
        # (the `on_slide`/`in_narration` branches guarantee `_span_present == True`).
        # The verbatim-absent case is routed earlier, via the `status == "missing"`
        # branch in `_derive_row` (which stamps `verbatim_absent=point.verbatim_required`
        # and never reaches here). This return is retained as a defensive guard only so
        # the function is total over its signature; the gate's verbatim_absent teeth do
        # NOT depend on it.
        return "altered", "advisory_caveat", report, True

    # Not verbatim-required: a semantic-fidelity judgment, never deterministic.
    if report["status"] == "FAIL":
        return "risky", "advisory_caveat", report, False
    verdict: ContainmentVerdict = "verbatim_preserved" if span_present else "altered"
    return verdict, "advisory_caveat", report, False


def derive_coverage_receipt(
    coverage_annotations: tuple[CoverageAnnotation, ...] | list[CoverageAnnotation],
    anchors: dict[str, AnchorResolution],
    *,
    segmentation: SegmentationGrain = "assertion_level",
    clinical_terms: frozenset[str] | None = None,
    generated_at: datetime | None = None,
) -> CoverageReceipt:
    """Project the authored source points + existing joins into the OBSERVED receipt.

    NO producer self-report: every row is derived from the frozen source points
    (authored side) × the ``anchors`` (the joins that already exist at the dispatch
    site). Deterministic anchor resolves FIRST (AC7). The receipt declares its
    ``segmentation`` grain (AC10).
    """
    rows: list[CoverageReceiptRow] = []
    for ann in coverage_annotations:
        for point in ann.source_points:
            anchor = anchors.get(point.slide_key)
            rows.append(_derive_row(point, anchor, clinical_terms=clinical_terms))
    return CoverageReceipt(
        segmentation=segmentation,
        rows=tuple(rows),
        generated_at=generated_at or datetime.now(tz=UTC),
    )


def coverage_plan_view(
    coverage_annotations: tuple[CoverageAnnotation, ...] | list[CoverageAnnotation],
) -> dict[str, Any]:
    """Project the AUTHORED coverage plan for the G0E decision card (pre-authoring, AC10).

    The PLAN view (vs the derived RECEIPT) — what each source point INTENDS, before
    any deliverable exists. Declares the ``segmentation`` grain on its face (Irene
    caveat). Pure projection over the frozen authored annotations.
    """
    points: list[dict[str, Any]] = []
    grain: str = "assertion_level"
    for ann in coverage_annotations:
        grain = ann.segmentation
        for sp in ann.source_points:
            points.append(
                {
                    "source_point_id": sp.source_point_id,
                    "component_id": sp.component_id,
                    "slide_key": sp.slide_key,
                    "human_label": _human_label(sp.slide_key),
                    "intent_set": list(sp.coverage_intents),
                    "risk_flags": list(sp.risk_flags),
                    "verbatim_required": sp.verbatim_required,
                    "must_cover": _derive_must_cover(sp),
                }
            )
    return {
        "segmentation": grain,
        "n_points": len(points),
        "points": points,
    }


__all__ = [
    "COVERAGE_RECEIPT_ASSET_ID",
    "COVERAGE_RECEIPT_BASENAME",
    "COVERAGE_STATUSES",
    "CONTAINMENT_VERDICTS",
    "VOUCH_LEVELS",
    "AnchorResolution",
    "ContainmentVerdict",
    "CoverageReceipt",
    "CoverageReceiptRow",
    "CoverageStatus",
    "VouchLevel",
    "coverage_plan_view",
    "coverage_receipt_json_schema",
    "derive_coverage_receipt",
    "load_coverage_receipt",
]
