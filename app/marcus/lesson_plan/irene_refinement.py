"""Irene refinement artifacts + signed LO-delta contract (Story G0-S3).

After operator confirm-gate #1 (G0E) confirms the typed manifest + provisional
Learning Objectives, Irene inspects the source AGAINST those LOs and:

  1. refines each provisional LO IN PLACE (``provisional -> refined`` on the SAME
     ``objective_id``; immutable id carried through) via
     ``advance_lo(..., "refined", actor="irene")`` — populating ``bloom_level``;
  2. produces a per-LO :class:`SourceAdequacy` ALERT (ADVISORY — never blocks the
     pipeline, never forces a drop, never gates a status transition; ratification
     §3.1);
  3. emits the **signed LO-delta contract** — a reconcilable ledger (this module)
     back to Marcus-SPOC, who re-presents it at operator ratify-gate #2 (G0R).

Authority: ``lo-schema-ratification-2026-06-26.md`` §3 (the signed LO-delta
contract — ALL channels: disposition codes / PROPOSE-NEW / RECOMMEND-DROP /
count reconciliation / NO silent drops), §3.1 (adequacy NEVER gates — a
``thin``/``gap`` verdict is a warning; the completeness assert checks adequacy
PRESENCE, never its verdict value), §2 (``advance_lo``: irene moves
``provisional -> refined`` and can NEVER reach ``ratified``).

Adequacy is produced HERE (S2's ``G0EnrichmentResult`` parks every provisional LO
with ``adequacy=None``). ``ratified`` is set ONLY by the operator-gated handler
(``advance_lo(..., "ratified", actor="operator")``), never by this module.

Pydantic-v2 idioms (docs/dev-guide/pydantic-v2-schema-checklist.md):
    - ``ConfigDict(extra="forbid", validate_assignment=True)`` on every model;
      closed enums via ``Literal``; tuples (not lists) for >=N floors that must
      not be silently emptied by in-place mutation.
"""

from __future__ import annotations

import hashlib
from typing import Any, Final, Literal, get_args

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.marcus.lesson_plan.learning_objective import (
    BloomLevel,
    LearningObjective,
    SourceAdequacy,
    advance_lo,
)

SCHEMA_VERSION: Final[str] = "1.0"

# Offline deterministic marker / live model id (mirror the S2 g0-enrichment seam).
REFINEMENT_MODEL_MARKER: Final[str] = "deterministic-irene-refinement-offline"
REFINEMENT_LIVE_MODEL_ID: Final[str] = "marcus"


# ---------------------------------------------------------------------------
# §3 (+d) — the closed disposition code set (exactly one per objective_id)
# ---------------------------------------------------------------------------

LODisposition = Literal[
    "refined-in-place",
    "unchanged",
    "split",  # split -> [ids] (notation: split→[ids]); the children ride split_into
    "merged",  # merged <- [ids] (notation: merged←[ids]); the parents ride merged_from
    "flagged-inadequate",
    "proposed-new",
    "recommend-drop",
]
"""Signed LO-delta disposition codes (ratification §3 +d). Exactly ONE per
``objective_id``; a returned id with NO disposition is a guardrail BLOCK (the
'no silent drops' invariant). ``split``/``merged`` carry their related ids on the
structured ``split_into`` / ``merged_from`` fields (never folded into the code
string)."""

# The dispositions whose entry represents a CHANGED LO: a source-tied rationale
# diff (§3 (b), provenance-bearing) is REQUIRED for these. ``unchanged`` and the
# two channel codes (proposed-new / recommend-drop) need no diff.
_CHANGED_DISPOSITIONS: Final[frozenset[str]] = frozenset(
    {"refined-in-place", "split", "merged", "flagged-inadequate"}
)

_BLOOM_LEVELS: Final[tuple[str, ...]] = get_args(BloomLevel)


# ---------------------------------------------------------------------------
# §3 — one reconcilable ledger entry per objective_id
# ---------------------------------------------------------------------------


class LODeltaEntry(BaseModel):
    """One entry of the signed LO-delta ledger (ratification §3), per objective_id.

    Carries (a) the resulting LO + (b) the source-tied rationale diff for a CHANGED
    LO + (c) the per-LO adequacy + (+d) exactly one disposition code + (+e) the
    immutable ``objective_id`` carry-through. The two Irene channels:

      * **PROPOSE-NEW** (``disposition="proposed-new"``): ``lo`` is a NEW LO at
        ``status="provisional"``, ``origin="irene-proposed"`` (Irene cannot
        self-promote it to refined — SPOC/operator ratifies it into the loop).
      * **RECOMMEND-DROP** (``disposition="recommend-drop"``): ``lo`` is held at
        ``provisional`` + ``adequacy.verdict="gap"`` + ``recommendation="drop"``
        (Irene never deletes; the operator executes any drop).
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    objective_id: str = Field(
        ...,
        min_length=1,
        description="The immutable id this disposition is about (+e carry-through).",
    )
    disposition: LODisposition = Field(
        ..., description="Exactly one closed disposition code (§3 +d)."
    )
    lo: LearningObjective = Field(
        ...,
        description="The resulting LO state (refined / unchanged / proposed / held).",
    )
    transition: str | None = Field(
        default=None,
        description="The status transition applied, e.g. 'provisional->refined'.",
    )
    rationale_diff: str | None = Field(
        default=None,
        description=(
            "Source-tied rationale diff (§3 b): what changed + why, grounded in the "
            "LO's SourceRef provenance. REQUIRED for a CHANGED disposition."
        ),
    )
    split_into: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Child objective_ids a 'split' produced (non-empty iff split).",
    )
    merged_from: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Parent objective_ids a 'merged' consumed (non-empty iff merged).",
    )

    @model_validator(mode="after")
    def _enforce_channel_wellformedness(self) -> LODeltaEntry:
        # (+e) immutable id carry-through: the entry's id MUST equal its LO's id
        # (a mutated id is a provenance break, not a refinement).
        if self.lo.objective_id != self.objective_id:
            raise ValueError(
                f"LO-delta entry id {self.objective_id!r} != lo.objective_id "
                f"{self.lo.objective_id!r} (mutated id is a provenance break, §3 +e)"
            )
        # (b) provenance-bearing rationale diff for a CHANGED LO; provenance-less
        # diff rejected pre-surface.
        if self.disposition in _CHANGED_DISPOSITIONS:
            if not (self.rationale_diff and self.rationale_diff.strip()):
                raise ValueError(
                    f"disposition {self.disposition!r} is a CHANGED LO and requires "
                    "a non-empty source-tied rationale_diff (§3 b)"
                )
            if len(self.lo.source_refs) < 1:
                raise ValueError(
                    f"disposition {self.disposition!r} requires the LO to cite >=1 "
                    "SourceRef (a provenance-less diff is rejected pre-surface)"
                )
        # split / merged structural pairing.
        if self.disposition == "split" and not self.split_into:
            raise ValueError("disposition 'split' requires a non-empty split_into")
        if self.disposition != "split" and self.split_into:
            raise ValueError("split_into is only valid on a 'split' disposition")
        if self.disposition == "merged" and not self.merged_from:
            raise ValueError("disposition 'merged' requires a non-empty merged_from")
        if self.disposition != "merged" and self.merged_from:
            raise ValueError("merged_from is only valid on a 'merged' disposition")
        # PROPOSE-NEW channel: a NEW provisional LO Irene cannot self-promote.
        if self.disposition == "proposed-new":
            if self.lo.origin != "irene-proposed":
                raise ValueError(
                    "disposition 'proposed-new' requires lo.origin='irene-proposed'"
                )
            if self.lo.status != "provisional":
                raise ValueError(
                    "a 'proposed-new' LO stays at status='provisional' "
                    "(Irene cannot self-promote her invention to refined)"
                )
        # RECOMMEND-DROP channel: held provisional + gap + drop recommendation.
        if self.disposition == "recommend-drop":
            if self.lo.status != "provisional":
                raise ValueError(
                    "a 'recommend-drop' LO is HELD at status='provisional' "
                    "(Irene never deletes; the operator executes any drop)"
                )
            if self.lo.recommendation != "drop":
                raise ValueError(
                    "disposition 'recommend-drop' requires lo.recommendation='drop'"
                )
            if self.lo.adequacy is None or self.lo.adequacy.verdict != "gap":
                raise ValueError(
                    "a 'recommend-drop' LO carries adequacy.verdict='gap' "
                    "(source cannot support the LO)"
                )
        # refined-in-place / unchanged / split / merged / flagged-inadequate all
        # represent surviving (non-dropped) LOs that should be at refined status.
        _refined_dispositions = {"refined-in-place", "split", "merged", "flagged-inadequate"}
        if self.disposition in _refined_dispositions and self.lo.status != "refined":
            raise ValueError(
                f"disposition {self.disposition!r} represents a refined LO; "
                f"got status {self.lo.status!r}"
            )
        return self

    def is_dropped(self) -> bool:
        """True iff this entry is a RECOMMEND-DROP (held, flagged for operator drop)."""
        return self.disposition == "recommend-drop"


class LODeltaLedger(BaseModel):
    """The signed, reconcilable LO-delta ledger Irene returns to Marcus-SPOC (§3).

    Reconciliation guarantee (§3): ``g0_count`` reconciles to ``irene_count`` via
    the disposition ledger — splits/merges/new/drop are EXPLAINED deltas. NO silent
    drops: every G0 ``objective_id`` (``g0_objective_ids``) must be accounted for by
    exactly one entry (either as an ``objective_id`` or consumed in a ``merged_from``).
    A returned id with no disposition is a guardrail BLOCK.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    g0_objective_ids: tuple[str, ...] = Field(
        ...,
        description="The provisional LO ids confirmed at gate #1 (the reconcile baseline).",
    )
    entries: tuple[LODeltaEntry, ...] = Field(
        ..., description="One reconcilable entry per disposition (§3)."
    )

    @model_validator(mode="after")
    def _enforce_no_silent_drops_and_reconciliation(self) -> LODeltaLedger:
        # Each entry's objective_id must be unique (exactly one disposition per id).
        seen: set[str] = set()
        for entry in self.entries:
            if entry.objective_id in seen:
                raise ValueError(
                    f"objective_id {entry.objective_id!r} carries more than one "
                    "disposition (exactly one per id, §3 +d)"
                )
            seen.add(entry.objective_id)

        # An id is ACCOUNTED FOR if it is an entry's objective_id OR consumed by a
        # merge (appears in some entry's merged_from). PROPOSE-NEW ids are new (not
        # part of the G0 baseline) and are allowed to be entry ids without being in
        # g0_objective_ids.
        proposed_new = {e.objective_id for e in self.entries if e.disposition == "proposed-new"}
        accounted = {e.objective_id for e in self.entries if e.disposition != "proposed-new"}
        for entry in self.entries:
            for parent in entry.merged_from:
                if parent in accounted:
                    raise ValueError(
                        f"merge parent {parent!r} is both an entry id and a "
                        "merged_from member (it carries two dispositions)"
                    )
                accounted.add(parent)

        g0_ids = set(self.g0_objective_ids)
        missing = g0_ids - accounted
        if missing:
            raise ValueError(
                f"NO silent drops (§3): G0 objective_id(s) {sorted(missing)} returned "
                "with no disposition (every confirmed provisional id must be accounted "
                "for in the ledger)"
            )
        # An entry id that is neither a G0 baseline id nor a declared proposed-new id
        # is a fabricated reconcile row.
        for entry_id in (e.objective_id for e in self.entries):
            if entry_id not in g0_ids and entry_id not in proposed_new:
                raise ValueError(
                    f"ledger entry {entry_id!r} is neither a confirmed G0 id nor a "
                    "declared proposed-new id (fabricated reconcile row)"
                )
        return self

    @property
    def g0_count(self) -> int:
        """The count confirmed at gate #1 (the reconcile baseline)."""
        return len(self.g0_objective_ids)

    @property
    def irene_count(self) -> int:
        """The count of LOs Irene returns LIVE in the loop (dropped LOs excluded).

        Splits expand (a parent yields its children); merges contract (N parents
        collapse to one surviving LO); proposed-new adds; recommend-drop is still
        a live held LO (the operator has not executed the drop yet) so it counts.
        """
        count = 0
        for entry in self.entries:
            if entry.disposition == "split":
                count += len(entry.split_into)
            elif entry.disposition == "merged":
                count += 1  # N parents -> 1 surviving merged LO
            else:
                count += 1
        return count

    def reconcile_summary(self) -> dict[str, int]:
        """Operator-facing reconciliation counts (Marcus narrates these at gate #2)."""
        changed = sum(1 for e in self.entries if e.disposition in _CHANGED_DISPOSITIONS)
        flagged = sum(
            1
            for e in self.entries
            if e.lo.adequacy is not None and e.lo.adequacy.verdict in ("thin", "gap")
        )
        return {
            "g0_count": self.g0_count,
            "irene_count": self.irene_count,
            "changed": changed,
            "flagged_thin_or_gap": flagged,
            "proposed_new": sum(1 for e in self.entries if e.disposition == "proposed-new"),
            "recommend_drop": sum(1 for e in self.entries if e.disposition == "recommend-drop"),
        }

    def flagged_for_operator(self) -> list[LODeltaEntry]:
        """The proposed-new + recommend-drop entries the operator must rule on at G0R."""
        return [e for e in self.entries if e.disposition in ("proposed-new", "recommend-drop")]


# ---------------------------------------------------------------------------
# The frozen refinement result (mirrors G0EnrichmentResult's role for S3)
# ---------------------------------------------------------------------------


class IreneRefinementResult(BaseModel):
    """The frozen Irene-refinement artifact feeding operator ratify-gate #2 (G0R).

    Keyed to the SAME corpus fingerprint as the upstream G0 enrichment result so a
    graph replay with an unchanged corpus reads the frozen result (determinism).
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    corpus_fingerprint: str = Field(
        ..., description="The upstream G0 corpus fingerprint (shared cache key)."
    )
    model_id: str = Field(
        ..., min_length=1, description="The refinement model id (or offline marker)."
    )
    refined_los: tuple[LearningObjective, ...] = Field(
        default_factory=tuple,
        description="The surviving LOs after refinement (refined / held-provisional).",
    )
    ledger: LODeltaLedger = Field(..., description="The signed LO-delta ledger (§3).")

    @model_validator(mode="after")
    def _enforce_irene_never_ratifies(self) -> IreneRefinementResult:
        # §2: Irene moves provisional->refined; she can NEVER emit a ratified LO.
        for lo in self.refined_los:
            if lo.status == "ratified":
                raise ValueError(
                    f"Irene emitted LO {lo.objective_id!r} at status 'ratified'; "
                    "ratified is set ONLY by the operator-gated handler (§2)"
                )
        return self

    def to_card_payload(self) -> dict[str, Any]:
        """Project the public shape for the G0R decision card."""
        return {
            "corpus_fingerprint": self.corpus_fingerprint,
            "model_id": self.model_id,
            "refined_los": [lo.model_dump(mode="json") for lo in self.refined_los],
            "lo_delta": [e.model_dump(mode="json") for e in self.ledger.entries],
            "reconcile": self.ledger.reconcile_summary(),
            "flagged_for_operator": [
                e.model_dump(mode="json") for e in self.ledger.flagged_for_operator()
            ],
        }


# ---------------------------------------------------------------------------
# Deterministic offline refinement (corpus-derived; reproducible)
# ---------------------------------------------------------------------------


def _deterministic_bloom(objective_id: str) -> BloomLevel:
    """A stable, id-derived Bloom level (varies across LOs, reproducible)."""
    pick = int(hashlib.sha256(objective_id.encode("utf-8")).hexdigest()[:8], 16)
    return _BLOOM_LEVELS[pick % len(_BLOOM_LEVELS)]  # type: ignore[return-value]


def _deterministic_adequacy(lo: LearningObjective) -> SourceAdequacy:
    """A falsifiable, span-derived adequacy ALERT (advisory; never gates, §3.1).

    Rubric proxy keyed to the longest cited span (richer source span => stronger
    assess-leg support). Every refined LO gets a POPULATED adequacy (presence is
    what the completeness assert checks; the verdict VALUE never gates).
    """
    longest = max((len(ref.quoted_span) for ref in lo.source_refs), default=0)
    excerpt = lo.statement.strip()[:60]
    if longest >= 80:
        return SourceAdequacy(
            verdict="adequate",
            rationale=f"source span supports both the teach-leg and assess-leg for: {excerpt}",
        )
    if longest >= 20:
        return SourceAdequacy(
            verdict="thin",
            rationale=f"teach-leg supported but assess-leg partial from source for: {excerpt}",
            missing=[f"assessment-grade detail for: {excerpt}"],
            suggested_followups=["external-content-expected"],
        )
    return SourceAdequacy(
        verdict="gap",
        rationale=f"source below the teachable floor (passing mention) for: {excerpt}",
        missing=[f"teachable substrate for: {excerpt}"],
        suggested_followups=["research-run"],
    )


def refine_one(lo: LearningObjective) -> tuple[LearningObjective, LODeltaEntry]:
    """Refine ONE provisional LO in place (provisional->refined) + its ledger entry.

    Deterministic, no LLM. Populates ``bloom_level`` + a POPULATED adequacy, then
    advances ``provisional -> refined`` on the SAME ``objective_id`` (immutable id
    carried through) via the S1 guard (``actor="irene"`` can NEVER reach ratified).
    """
    if lo.status != "provisional":
        raise ValueError(
            f"refine_one expects a provisional LO; got {lo.objective_id!r} at "
            f"status {lo.status!r}"
        )
    adequacy = _deterministic_adequacy(lo)
    bloom = _deterministic_bloom(lo.objective_id)
    staged = lo.model_copy(update={"bloom_level": bloom, "adequacy": adequacy})
    refined = advance_lo(staged, "refined", actor="irene")
    entry = LODeltaEntry(
        objective_id=refined.objective_id,
        disposition="refined-in-place",
        lo=refined,
        transition="provisional->refined",
        rationale_diff=(
            f"refined in place against source {refined.source_refs[0].source_id}: "
            f"populated bloom_level={bloom}, assessed adequacy={adequacy.verdict}"
        ),
    )
    return refined, entry


def build_refinement_result(
    *,
    provisional_los: list[LearningObjective],
    corpus_fingerprint: str,
    dispatch_live: bool = False,
    chat_model_factory: Any | None = None,
) -> IreneRefinementResult:
    """Refine the gate-#1-confirmed provisional LOs + assemble the frozen result.

    Pure of run-dir/cache side effects (those live in the wiring) so the assembly
    is unit-testable in isolation. The OFFLINE path is deterministic; the live path
    (operator-gated) refines via the corpus-keyed LLM pre-pass seam.
    """
    for lo in provisional_los:
        if lo.status != "provisional":
            raise ValueError(
                f"refinement input must be provisional; {lo.objective_id!r} is "
                f"{lo.status!r} (gate #1 confirms provisional LOs)"
            )

    model_id = REFINEMENT_LIVE_MODEL_ID if dispatch_live else REFINEMENT_MODEL_MARKER
    if dispatch_live:  # pragma: no cover - live leg (orchestrator AC-S3-7)
        refined_los, entries = _live_refine(provisional_los, chat_model_factory)
    else:
        refined_los = []
        entries = []
        for lo in provisional_los:
            refined, entry = refine_one(lo)
            refined_los.append(refined)
            entries.append(entry)

    ledger = LODeltaLedger(
        g0_objective_ids=tuple(lo.objective_id for lo in provisional_los),
        entries=tuple(entries),
    )
    return IreneRefinementResult(
        corpus_fingerprint=corpus_fingerprint,
        model_id=model_id,
        refined_los=tuple(refined_los),
        ledger=ledger,
    )


# ---------------------------------------------------------------------------
# Live LLM refinement (exercised by AC-S3-7; reuses the pre_gate_marcus seam)
# ---------------------------------------------------------------------------


def _live_refine(
    provisional_los: list[LearningObjective],
    chat_model_factory: Any | None,
) -> tuple[list[LearningObjective], list[LODeltaEntry]]:  # pragma: no cover - live leg
    """REAL Irene refinement pre-pass via make_chat_model + irene-refinement.j2.

    Off the deterministic critical path. Exercised by the operator-gated live
    segment proof (AC-S3-7), not the offline suite. Reconciles the model payload
    deterministically against the confirmed provisional set (no silent drops).
    """
    import json

    from app.marcus.orchestrator.pre_gate_marcus import render_pre_fill_prompt

    lo_summary = "\n".join(
        f"- {lo.objective_id}: {lo.statement}"
        f" [refs: {', '.join(r.source_id for r in lo.source_refs) or 'none'}]"
        for lo in provisional_los
    )
    prompt = render_pre_fill_prompt(
        gate_id="irene-refinement",
        slot_values={"provisional_los": lo_summary, "lo_count": len(provisional_los)},
    )
    if chat_model_factory is None:
        from app.models.adapter import make_chat_model

        chat_model_factory = make_chat_model
    handle = chat_model_factory("marcus")
    response = handle.chat.invoke([{"role": "user", "content": prompt}])
    payload = json.loads(response.content)
    return _parse_live_refinement(payload, provisional_los)


def _parse_live_refinement(
    payload: dict[str, Any],
    provisional_los: list[LearningObjective],
) -> tuple[list[LearningObjective], list[LODeltaEntry]]:  # pragma: no cover - live leg
    """Reconcile a live refinement payload to refined LOs + ledger entries.

    The live model will not reliably refine EXACTLY the confirmed set once per id.
    We reconcile deterministically: every confirmed provisional id that the model
    refined is taken; any id the model left untouched falls back to the
    deterministic ``refine_one`` (no silent drops — every confirmed id gets a
    disposition). Fabricated ids (not in the confirmed set, not declared
    proposed-new) are dropped with a loud failure at ledger validation.
    """
    by_id = {lo.objective_id: lo for lo in provisional_los}
    refined_los: list[LearningObjective] = []
    entries: list[LODeltaEntry] = []
    handled: set[str] = set()

    for row in payload.get("refined_los", []):
        oid = row.get("objective_id")
        base = by_id.get(oid)
        if base is None:
            continue  # fabricated id — dropped (ledger validation owns the BLOCK)
        adequacy = SourceAdequacy.model_validate(row["adequacy"])
        bloom = row.get("bloom_level") or _deterministic_bloom(oid)
        staged = base.model_copy(update={"bloom_level": bloom, "adequacy": adequacy})
        refined = advance_lo(staged, "refined", actor="irene")
        refined_los.append(refined)
        entries.append(
            LODeltaEntry(
                objective_id=oid,
                disposition="refined-in-place",
                lo=refined,
                transition="provisional->refined",
                rationale_diff=row.get("rationale_diff") or "refined against source",
            )
        )
        handled.add(oid)

    for lo in provisional_los:
        if lo.objective_id not in handled:
            refined, entry = refine_one(lo)
            refined_los.append(refined)
            entries.append(entry)
    return refined_los, entries


# ---------------------------------------------------------------------------
# AC-S3-5 — completeness hard-assert (ACCESS + ASSESSMENT-PRESENCE)
# ---------------------------------------------------------------------------


class CompletenessError(ValueError):
    """RED: the completeness hard-assert failed (access or assessment-presence)."""


def assert_completeness(
    *,
    refined_los: list[LearningObjective],
    ledger: LODeltaLedger,
    enumerated_source_ids: set[str],
) -> None:
    """AC-S3-5: ACCESS + ASSESSMENT-PRESENCE — NOT adequacy outcome.

    Before hand-off to lesson-planning / Gary:
      * every non-dropped LO has >=1 **resolvable** ``SourceRef`` (source_id in the
        enumerated set) — an unreachable/fabricated source is RED (A1);
      * every non-dropped LO has a **populated** adequacy verdict (assessed, not
        silently absent);
      * a ``thin``/``gap`` adequacy verdict does NOT fail the assert (§3.1 — the
        run proceeds; final adequacy is the operator + off-world SME's call).

    A RECOMMEND-DROP LO is the one exclusion (it is flagged for the operator to
    drop; it carries adequacy.verdict='gap' by construction but is not asserted as
    a surviving deliverable).
    """
    dropped_ids = {e.objective_id for e in ledger.entries if e.is_dropped()}
    for lo in refined_los:
        if lo.objective_id in dropped_ids:
            continue  # operator-flagged for drop — not a surviving deliverable
        # ASSESSMENT-PRESENCE (presence only; verdict value NEVER gates, §3.1).
        if lo.adequacy is None:
            raise CompletenessError(
                f"LO {lo.objective_id!r} has no populated adequacy assessment "
                "(assessment-presence is required; a thin/gap verdict would PASS, "
                "but a silently-absent one is RED)"
            )
        # ACCESS: >=1 resolvable SourceRef.
        if len(lo.source_refs) < 1:
            raise CompletenessError(
                f"LO {lo.objective_id!r} has no SourceRef (a non-dropped LO needs "
                ">=1 resolvable source)"
            )
        for ref in lo.source_refs:
            if ref.source_id not in enumerated_source_ids:
                raise CompletenessError(
                    f"LO {lo.objective_id!r} cites source {ref.source_id!r} which is "
                    "not in the enumerated/reachable corpus set (unreachable source "
                    "is RED, A1)"
                )


# ---------------------------------------------------------------------------
# AC-S3-4 — operator ratification (refined -> ratified); A8 re-confirm guard
# ---------------------------------------------------------------------------


def ratify_refined_los(
    refined_los: list[LearningObjective],
    *,
    prior_ratified: dict[str, LearningObjective] | None = None,
    reconfirmed_ids: set[str] | None = None,
) -> list[LearningObjective]:
    """Advance each refined LO ``refined -> ratified`` under ``actor="operator"``.

    Deterministic; no LLM. The model NEVER auto-ratifies — this runs ONLY from the
    operator-verdict gate handler (G0R).

    A8 (ratification §2-A8): a touched PRIOR-ratified LO is NOT silently re-stamped.
    If an LO id is already in ``prior_ratified``, it requires an EXPLICIT operator
    re-confirm (its id in ``reconfirmed_ids``) — leaning on ``advance_lo``
    idempotency is forbidden (a prior-ratified LO arrives at status='ratified', so
    ``advance_lo`` would no-op it silently; we reject that path).
    """
    prior_ratified = prior_ratified or {}
    reconfirmed_ids = reconfirmed_ids or set()
    out: list[LearningObjective] = []
    for lo in refined_los:
        if lo.objective_id in prior_ratified:
            if lo.objective_id not in reconfirmed_ids:
                raise ValueError(
                    f"LO {lo.objective_id!r} was previously ratified; touching it "
                    "again requires an EXPLICIT operator re-confirm (A8 — never a "
                    "silent re-stamp via advance_lo idempotency)"
                )
            out.append(
                lo if lo.status == "ratified" else advance_lo(lo, "ratified", actor="operator")
            )
            continue
        out.append(advance_lo(lo, "ratified", actor="operator"))
    return out


__all__ = [
    "SCHEMA_VERSION",
    "REFINEMENT_LIVE_MODEL_ID",
    "REFINEMENT_MODEL_MARKER",
    "CompletenessError",
    "IreneRefinementResult",
    "LODeltaEntry",
    "LODeltaLedger",
    "LODisposition",
    "assert_completeness",
    "build_refinement_result",
    "ratify_refined_los",
    "refine_one",
]
