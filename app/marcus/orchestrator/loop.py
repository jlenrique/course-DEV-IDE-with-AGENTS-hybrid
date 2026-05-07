"""4A conversation loop — scope-decision intake + plan-lock trigger (Story 30-3a).

Maya-facing note
----------------

Maya interacts with this module indirectly via :class:`marcus.facade.Facade`.
She sees one Marcus; the loop runs under the hood, iterating through plan
units and recording her scope-decision for each before the plan locks.

Developer discipline note
-------------------------

* **30-1 (structural foundation, done):** facade shell, write-API gate,
  NEGOTIATOR_SEAM string sentinel.
* **30-2b (pre-packet emission, done):** Intake → Orchestrator dispatch
  pattern for `pre_packet_snapshot` events.
* **30-3a (this commit):** first real loop. Replaces the 30-1
  `Facade.greet()` stub with :meth:`Facade.run_4a`. Emits three new
  named events — ``plan_unit.created``, ``scope_decision.set``,
  ``plan.locked`` — all via :func:`marcus.orchestrator.dispatch.dispatch_orchestrator_event`.
* **30-3b (next):** dial tuning + sync reassessment on top of this loop.
* **30-4 (plan-lock fanout):** consumes the ``plan.locked`` event this
  story emits and fans out to step 05+.

Single-writer discipline
------------------------

This module NEVER calls :meth:`marcus.lesson_plan.log.LessonPlanLog.append_event`
directly. All log writes route through the caller-injected ``dispatch``
callable, which production callers set to
:func:`marcus.orchestrator.dispatch.dispatch_orchestrator_event`. Tests
may pass a stub callable that captures envelopes for inspection.

Plan-lock invariance (Murat R1)
-------------------------------

Once :attr:`FourAState.locked` is ``True``, any subsequent
:func:`intake_scope_decision` call raises :class:`PlanAlreadyLockedError`
and emits no event. The lock is terminal for the loop's lifetime.

Rationale verbatim (R1 amendment 16)
------------------------------------

Every rationale string passes through unmodified: no ``.strip()``, no
trimming, no parsing, no coercion, no enum. Empty string, emoji,
non-ASCII, mixed whitespace, 10K chars — all stored verbatim and
surfaced verbatim in Marcus's confirmation echo.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from datetime import UTC, datetime
from time import perf_counter
from typing import Final

from pydantic import BaseModel, ConfigDict, Field

from app.marcus.lesson_plan.event_type_registry import (
    EVENT_DIALS_TUNED,
    EVENT_PLAN_LOCKED,
    EVENT_PLAN_UNIT_CREATED,
    EVENT_SCOPE_DECISION_SET,
    EVENT_SCOPE_DECISION_TRANSITION,
)
from app.marcus.lesson_plan.events import EventEnvelope, ScopeDecisionTransition, to_internal_actor
from app.marcus.lesson_plan.gagne_diagnostician import diagnose_lesson_plan
from app.marcus.lesson_plan.log import PlanLockedPayload
from app.marcus.lesson_plan.retrieval_narration_grammar import render_retrieval_narration
from app.marcus.lesson_plan.schema import Dials, LessonPlan, PlanUnit, ScopeDecision

__all__: Final[tuple[str, ...]] = (
    "FourALoop",
    "FourAState",
    "IntakeCallable",
    "PlanAlreadyLockedError",
    "SyncReassessmentResult",
    "intake_scope_decision",
    "sync_reassess_with_irene",
    "tune_unit_dials",
    "trigger_plan_lock_if_ready",
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


_MAYA_SAFE_ALREADY_LOCKED_MESSAGE: str = (
    "This plan is already locked — I can't change its scope now. "
    "Want me to start a fresh plan?"
)


class PlanAlreadyLockedError(PermissionError):
    """Raised by :func:`intake_scope_decision` when called on a locked state.

    Plan-lock is invariant per Murat R1; a locked plan cannot be
    reassessed within the same loop. The only path to a new locked
    plan is a fresh :meth:`FourALoop.run_4a` call with a new packet.

    The exception's :meth:`__str__` returns a Maya-safe, Voice-Register-
    compliant message. Internal-routing detail lives on attribute-scoped
    fields (``debug_detail``) and is never auto-stringified.
    """

    __slots__ = ("debug_detail",)

    def __init__(self, *, unit_id: str, locked_revision: int) -> None:
        super().__init__(_MAYA_SAFE_ALREADY_LOCKED_MESSAGE)
        self.debug_detail: str = (
            f"intake_scope_decision called on locked plan "
            f"(unit_id={unit_id!r}, locked_revision={locked_revision})"
        )


# ---------------------------------------------------------------------------
# FourAState — loop state snapshot
# ---------------------------------------------------------------------------


class FourAState(BaseModel):
    """Snapshot of the 4A loop state at a given step.

    Frozen per the functional-style state-transition pattern: helpers
    like :func:`intake_scope_decision` return a new :class:`FourAState`
    rather than mutating in place.

    Fields:
        draft_plan: The in-progress :class:`LessonPlan`. Mutations go
            via :meth:`LessonPlan.bump_revision` + ``plan_units`` update.
        prior_declined_rationales: Tuple of ``(unit_id, rationale)``
            pairs carried forward from a previous run's Declined entries
            (R1 amendment 15). Units named here are pre-ratified with
            scope=``out-of-scope``; Maya is not prompted for them.
        locked: True iff the plan is locked (terminal state).
        locked_at: Timestamp of the ``plan.locked`` emission (timezone-aware).
        locked_revision: ``plan_revision`` at lock time.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_assignment=True,
        arbitrary_types_allowed=False,
    )

    draft_plan: LessonPlan
    prior_declined_rationales: tuple[tuple[str, str], ...] = Field(
        default_factory=tuple
    )
    reassessment_iterations: int = 0
    locked: bool = False
    locked_at: datetime | None = None
    locked_revision: int | None = None

    @property
    def ratified_units(self) -> frozenset[str]:
        """Plan-unit IDs whose ``scope_decision`` has been ratified or locked."""
        return frozenset(
            unit.unit_id
            for unit in self.draft_plan.plan_units
            if unit.scope_decision is not None
            and unit.scope_decision.state in {"ratified", "locked"}
        )

    @property
    def pending_units(self) -> tuple[str, ...]:
        """Plan-unit IDs still awaiting a ratified scope decision.

        Order follows the draft plan's ``plan_units`` ordering. Prior-
        decline carry-forward (R1-15) pre-ratifies named units at
        loop-start so they don't appear here.
        """
        return tuple(
            unit.unit_id
            for unit in self.draft_plan.plan_units
            if unit.scope_decision is None
            or unit.scope_decision.state == "proposed"
        )


# ---------------------------------------------------------------------------
# Intake callable protocol
# ---------------------------------------------------------------------------


IntakeCallable = Callable[[FourAState, str], tuple[ScopeDecision, str]]
"""Callable signature for per-unit scope-decision intake.

Production wiring (future 30-3b) connects this to Maya's real UI; tests
pass a pre-programmed stub. Called once per pending unit. Returns
``(decision, rationale)`` — the :class:`ScopeDecision` is the full value
object (state=ratified, scope=in-scope/out-of-scope/delegated/blueprint,
ratified_by=maya, ...); rationale is free text stored verbatim.
"""


# ---------------------------------------------------------------------------
# intake_scope_decision — append one ratified decision to the draft
# ---------------------------------------------------------------------------


def intake_scope_decision(
    state: FourAState,
    unit_id: str,
    decision: ScopeDecision,
    rationale: str,
    *,
    dispatch: Callable[[EventEnvelope], None],
) -> FourAState:
    """Record a ratified scope decision + rationale for one plan unit.

    Raises:
        PlanAlreadyLockedError: If ``state.locked == True``. No event
            emitted on this path.
        ValueError: If ``unit_id`` is not in ``state.pending_units`` or
            the draft plan has no matching unit.
    """
    if state.locked:
        raise PlanAlreadyLockedError(
            unit_id=unit_id,
            locked_revision=state.locked_revision or 0,
        )

    # Find the target plan unit.
    unit_index: int | None = None
    for idx, unit in enumerate(state.draft_plan.plan_units):
        if unit.unit_id == unit_id:
            unit_index = idx
            break
    if unit_index is None:
        raise ValueError(
            f"intake_scope_decision: unit_id={unit_id!r} not in draft plan"
        )

    # Replace the unit's scope_decision + rationale (verbatim).
    updated_unit = state.draft_plan.plan_units[unit_index].model_copy(
        update={"scope_decision": decision, "rationale": rationale}
    )
    new_units = list(state.draft_plan.plan_units)
    new_units[unit_index] = updated_unit
    new_plan = state.draft_plan.model_copy(update={"plan_units": new_units})

    # Emit scope_decision.set event.
    envelope = EventEnvelope(
        timestamp=datetime.now(tz=UTC),
        plan_revision=new_plan.revision,
        event_type=EVENT_SCOPE_DECISION_SET,
        payload={
            "unit_id": unit_id,
            "scope": decision.scope,
            "state": decision.state,
            "rationale": rationale,
            "ratified_by": decision.ratified_by,
        },
    )
    dispatch(envelope)

    return state.model_copy(update={"draft_plan": new_plan})


class SyncReassessmentResult(BaseModel):
    """Return shape for Irene sync reassessment runs in Story 30-3b."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    updated_state: FourAState
    irene_budget_ms: int = Field(..., ge=0)
    fallback_used: bool = False
    iteration_index: int = Field(..., ge=1)
    voice_message: str = Field(..., min_length=1)


def tune_unit_dials(
    state: FourAState,
    unit_id: str,
    *,
    enrichment: float | None,
    corroboration: float | None,
    dispatch: Callable[[EventEnvelope], None],
) -> FourAState:
    """Apply operator dial tuning to an in-scope/delegated unit.

    Story 30-3b scope: dials become tunable on top of the 30-3a skeleton.
    Tuning is illegal for out-of-scope/blueprint units.
    """
    if state.locked:
        raise PlanAlreadyLockedError(
            unit_id=unit_id,
            locked_revision=state.locked_revision or 0,
        )

    unit_index: int | None = None
    for idx, unit in enumerate(state.draft_plan.plan_units):
        if unit.unit_id == unit_id:
            unit_index = idx
            break
    if unit_index is None:
        raise ValueError(f"tune_unit_dials: unit_id={unit_id!r} not in draft plan")

    existing = state.draft_plan.plan_units[unit_index]
    if existing.scope_decision is None or existing.scope_decision.scope not in {
        "in-scope",
        "delegated",
    }:
        raise ValueError(
            "dials can only be tuned for units with scope in {'in-scope', 'delegated'}"
        )

    updated_unit = existing.model_copy(
        update={
            "dials": Dials(
                enrichment=enrichment,
                corroboration=corroboration,
            )
        }
    )
    new_units = list(state.draft_plan.plan_units)
    new_units[unit_index] = updated_unit
    new_plan = state.draft_plan.model_copy(update={"plan_units": new_units})

    # G6-Opus 30-3b sweep (party-mode 2026-04-19 follow-on): emit a dedicated
    # `dials.tuned` event rather than reusing `scope_decision.set`. Dial
    # tuning does not change the scope decision; conflating the two would
    # mislead audit consumers (32-3 smoke, future trial-run readers) into
    # treating a dial change as a scope change.
    envelope = EventEnvelope(
        timestamp=datetime.now(tz=UTC),
        plan_revision=new_plan.revision,
        event_type=EVENT_DIALS_TUNED,
        payload={
            "unit_id": unit_id,
            "scope": existing.scope_decision.scope,
            "state": existing.scope_decision.state,
            "ratified_by": existing.scope_decision.ratified_by,
            "dials": updated_unit.dials.model_dump(mode="json") if updated_unit.dials else {},
        },
    )
    dispatch(envelope)
    return state.model_copy(update={"draft_plan": new_plan})


def _voice_message_for_iteration(
    iteration_index: int,
    *,
    recommendation_count: int,
    fallback_used: bool,
    tracy_result: Mapping[str, object] | None,
) -> str:
    cadence = (
        "I rechecked the plan and found {count} scope updates. Want me to apply them now?",
        "I synced with Irene again and found {count} updates this round. Want me to keep going?",
        "I ran one more reassessment pass and found {count} updates. Want me to lock this version?",
    )
    template = cadence[min(iteration_index - 1, len(cadence) - 1)]
    message = template.format(count=recommendation_count)
    if fallback_used:
        message = (
            "I switched to summary reassessment to stay responsive. "
            "Want me to keep the current scope or apply Irene's recommendations?"
        )
    if tracy_result is not None:
        message = f"{message} {render_retrieval_narration(tracy_result)}"
    return message


def sync_reassess_with_irene(
    state: FourAState,
    *,
    source_ref: str,
    dispatch: Callable[[EventEnvelope], None],
    prior_declined_rationales: Mapping[str, str] | None = None,
    tracy_result: Mapping[str, object] | None = None,
    p95_threshold_ms: int = 30_000,
    budget_threshold_ms: int = 30_000,
    time_source: Callable[[], float] = perf_counter,
) -> SyncReassessmentResult:
    """Run Irene sync reassessment and apply recommended scope updates.

    30-3b behavior:
    - Calls Irene diagnostician on the current draft plan.
    - Applies recommended scope updates as ratified system updates.
    - Emits ``scope_decision_transition`` envelopes for each changed unit.
    - Triggers summary-mode fallback messaging when budget breaches the p95 threshold.
    """
    if state.locked:
        unit_id = (
            state.draft_plan.plan_units[0].unit_id
            if state.draft_plan.plan_units
            else "<none>"
        )
        raise PlanAlreadyLockedError(
            unit_id=unit_id,
            locked_revision=state.locked_revision or state.draft_plan.revision,
        )

    plan_for_reassessment = state.draft_plan
    if plan_for_reassessment.digest == "":
        from app.marcus.lesson_plan.digest import compute_digest

        plan_for_reassessment = plan_for_reassessment.model_copy(
            update={"digest": compute_digest(plan_for_reassessment)}
        )

    normalized_prior = dict(prior_declined_rationales or {})

    report = diagnose_lesson_plan(
        plan_for_reassessment,
        source_ref=source_ref,
        prior_declined_rationales=normalized_prior,
        budget_threshold_ms=budget_threshold_ms,
        time_source=time_source,
    )

    new_units = list(state.draft_plan.plan_units)
    updated_count = 0
    for diagnosis in report.diagnoses:
        recommended = diagnosis.recommended_scope_decision
        if diagnosis.unit_id in normalized_prior:
            recommended = "out-of-scope"
        if recommended is None:
            continue
        for idx, unit in enumerate(new_units):
            if unit.unit_id != diagnosis.unit_id or unit.scope_decision is None:
                continue
            if unit.scope_decision.scope == recommended:
                break
            transitioned = ScopeDecision.transition_to(
                unit.scope_decision,
                state="ratified",
                scope=recommended,
                proposed_by="system",
                internal_proposed_by="irene",
                ratified_by="maya",
            )
            new_units[idx] = unit.model_copy(update={"scope_decision": transitioned})
            transition = ScopeDecisionTransition(
                unit_id=unit.unit_id,
                plan_revision=state.draft_plan.revision,
                from_state=unit.scope_decision.state,
                to_state=transitioned.state,
                from_scope=unit.scope_decision.scope,
                to_scope=transitioned.scope,
                actor="system",
                _internal_actor=to_internal_actor("system", "irene"),
                timestamp=datetime.now(tz=UTC),
                rationale_snapshot=unit.rationale,
            )
            dispatch(
                EventEnvelope(
                    timestamp=transition.timestamp,
                    plan_revision=state.draft_plan.revision,
                    event_type=EVENT_SCOPE_DECISION_TRANSITION,
                    payload=transition.model_dump(mode="json"),
                )
            )
            updated_count += 1
            break

    updated_state = state.model_copy(
        update={
            "draft_plan": plan_for_reassessment.model_copy(update={"plan_units": new_units}),
            "reassessment_iterations": state.reassessment_iterations + 1,
        }
    )
    fallback_used = report.irene_budget_ms > p95_threshold_ms
    iteration = updated_state.reassessment_iterations
    voice_message = _voice_message_for_iteration(
        iteration,
        recommendation_count=updated_count,
        fallback_used=fallback_used,
        tracy_result=tracy_result,
    )
    return SyncReassessmentResult(
        updated_state=updated_state,
        irene_budget_ms=report.irene_budget_ms,
        fallback_used=fallback_used,
        iteration_index=iteration,
        voice_message=voice_message,
    )


# ---------------------------------------------------------------------------
# trigger_plan_lock_if_ready — commit the plan if all units ratified
# ---------------------------------------------------------------------------


def trigger_plan_lock_if_ready(
    state: FourAState,
    *,
    dispatch: Callable[[EventEnvelope], None],
    latest_locked_revision: int = 0,
) -> FourAState:
    """Transition to locked state iff every plan unit has a ratified decision.

    Args:
        state: Current loop state.
        dispatch: Orchestrator-side dispatch callable.
        latest_locked_revision: The latest ``plan.locked`` revision already
            in the log; the new lock's revision must be strictly greater.
            Production callers pass :meth:`LessonPlanLog.latest_plan_revision`.

    Returns:
        Either ``state`` unchanged (if pending_units is non-empty) or a
        new :class:`FourAState` with ``locked=True``, ``locked_at`` set,
        ``locked_revision`` set, and the draft plan's revision bumped.
    """
    if state.locked or state.pending_units:
        return state

    next_revision = max(state.draft_plan.revision + 1, latest_locked_revision + 1)
    locked_at = datetime.now(tz=UTC)
    locked_plan = state.draft_plan.model_copy(update={"revision": next_revision})
    # Recompute digest after revision bump so the payload's digest is fresh.
    from app.marcus.lesson_plan.digest import compute_digest

    locked_plan = locked_plan.model_copy(update={"digest": compute_digest(locked_plan)})

    payload = PlanLockedPayload(lesson_plan_digest=locked_plan.digest)
    envelope = EventEnvelope(
        timestamp=locked_at,
        plan_revision=next_revision,
        event_type=EVENT_PLAN_LOCKED,
        payload=payload.model_dump(mode="json"),
    )
    dispatch(envelope)

    return state.model_copy(
        update={
            "draft_plan": locked_plan,
            "locked": True,
            "locked_at": locked_at,
            "locked_revision": next_revision,
        }
    )


# ---------------------------------------------------------------------------
# FourALoop — orchestrates the loop end-to-end
# ---------------------------------------------------------------------------


class FourALoop:
    """End-to-end 4A conversation loop driver.

    Instantiate per Maya session; call :meth:`run_4a` to drive the loop
    from an initial packet + optional fit-report through plan-lock.

    The ``dispatch`` callable is required (single-writer discipline);
    production callers inject
    :func:`marcus.orchestrator.dispatch.dispatch_orchestrator_event`
    (optionally partial-applied with a ``log=`` argument for test
    isolation).
    """

    def __init__(
        self,
        *,
        dispatch: Callable[[EventEnvelope], None],
        latest_locked_revision: int = 0,
    ) -> None:
        self._dispatch = dispatch
        self._latest_locked_revision = latest_locked_revision

    def run_4a(
        self,
        packet_plan: LessonPlan,
        *,
        intake_callable: IntakeCallable,
        prior_declined_rationales: Iterable[tuple[str, str]] = (),
    ) -> LessonPlan:
        """Drive the loop from an initial draft plan through plan-lock.

        Args:
            packet_plan: Initial :class:`LessonPlan` draft (typically
                built from the 30-2b pre-packet handoff + 29-2
                fit-report). At this story the caller assembles it;
                30-4 will thread it through the runtime.
            intake_callable: Per-unit prompt callable. See
                :data:`IntakeCallable`.
            prior_declined_rationales: Iterable of ``(unit_id, rationale)``
                pairs from a previous run to carry forward (R1-15).
                Each entry becomes a pre-ratified ``out-of-scope``
                decision with the rationale stored verbatim — Maya is
                NOT prompted for units named here.

        Returns:
            The locked :class:`LessonPlan` (``revision`` bumped,
            ``digest`` recomputed).
        """
        # Step 1: initial state. Each plan_unit with no scope_decision gets
        # a plan_unit.created event. Prior-decline units get pre-ratified.
        state = FourAState(
            draft_plan=packet_plan,
            prior_declined_rationales=tuple(prior_declined_rationales),
        )
        for unit in packet_plan.plan_units:
            self._emit_plan_unit_created(unit, state.draft_plan.revision)

        # Step 2: preload prior declines (R1-15 carry-forward).
        # Each becomes a pre-ratified out-of-scope decision with the
        # rationale stored verbatim.
        for unit_id, rationale in state.prior_declined_rationales:
            if unit_id not in {u.unit_id for u in state.draft_plan.plan_units}:
                # Prior decline naming a unit absent from this plan —
                # silent-skip (it belongs to a different plan shape).
                continue
            carryforward_decision = ScopeDecision(
                state="ratified",
                scope="out-of-scope",
                proposed_by="system",
                ratified_by="maya",
            )
            state = intake_scope_decision(
                state,
                unit_id,
                carryforward_decision,
                rationale,
                dispatch=self._dispatch,
            )

        # Step 3: drive the intake callable through each pending unit.
        while state.pending_units:
            unit_id = state.pending_units[0]
            decision, rationale = intake_callable(state, unit_id)
            state = intake_scope_decision(
                state, unit_id, decision, rationale, dispatch=self._dispatch
            )

        # Step 4: commit the plan-lock.
        state = trigger_plan_lock_if_ready(
            state,
            dispatch=self._dispatch,
            latest_locked_revision=self._latest_locked_revision,
        )
        if not state.locked:
            raise RuntimeError(
                "Internal invariant failure: all units ratified but "
                "trigger_plan_lock_if_ready did not lock the plan."
            )

        return state.draft_plan

    def _emit_plan_unit_created(self, unit: PlanUnit, plan_revision: int) -> None:
        """Emit one ``plan_unit.created`` event per plan unit."""
        envelope = EventEnvelope(
            timestamp=datetime.now(tz=UTC),
            plan_revision=plan_revision,
            event_type=EVENT_PLAN_UNIT_CREATED,
            payload={
                "unit_id": unit.unit_id,
                "event_type_ref": unit.event_type,
                "weather_band": unit.weather_band,
            },
        )
        self._dispatch(envelope)
