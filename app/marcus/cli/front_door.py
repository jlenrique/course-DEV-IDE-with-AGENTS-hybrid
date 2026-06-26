"""Marcus-SPOC FRONT DOOR — the bundle selection turn (S5).

The front door is the first conversational turn of a production run: Marcus
presents the curated bundle catalog (the 3 ratified bundles) WITH honest
readiness drawn from :func:`app.marcus.lesson_plan.bundle_catalog.bundle_readiness`
and collects the operator's pick. ``fully_proven`` bundles are SELECTABLE;
``partial`` / ``not_yet`` bundles are shown but FLAGGED so Marcus can never run an
unproven bundle as if it were complete (no fabricated motion / workbook output).

Deterministic guard (LOAD-BEARING, mirrors the interlocutor's guard pattern):

- An LLM/model RECOMMENDATION is ADVISORY only. It is surfaced to the operator
  but NEVER auto-selects — the model drives the engine ZERO times.
- Only the operator's EXPLICIT, CONFIRMED pick of a RUNNABLE (fully-proven, unless
  explicitly overridden) bundle yields a :class:`FrontDoorSelection`.
- A hallucinated / unknown bundle id raises :class:`UnknownBundleError` BEFORE any
  selection is returned, so the run is never started against an invented bundle.

This module returns the chosen :class:`ComponentSelection` + seeds; threading it
into the composed run is :func:`app.marcus.cli.trial.start_trial`'s job. The live
HIL leg (a real operator at a real terminal) is deferred to a tracked run; the
offline ACs inject the IO seams.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field

from app.marcus.cli.marcus_spoc import _M, _RULE
from app.marcus.lesson_plan.bundle_catalog import (
    BUNDLE_CATALOG,
    BundleReadiness,
    bundle_readiness,
    get_bundle,
)
from app.models.state.component_selection import ComponentSelection

# Operator-facing flag text per readiness verdict. ``None`` == selectable.
_READINESS_FLAG: dict[BundleReadiness, str | None] = {
    "fully_proven": None,
    "partial": "PROVEN BUT PENDING REPAIR — not runnable as complete yet",
    "not_yet": "NOT YET BUILT — not runnable yet",
}

_CONFIRM_TOKENS = frozenset({"yes", "y", "confirm", "do it"})
_DEFAULT_MAX_ATTEMPTS = 10


class FrontDoorError(RuntimeError):
    """Base class for front-door selection failures."""


class UnknownBundleError(FrontDoorError):
    """The pick is not a known catalog bundle id (hallucinated / typo)."""


class BundleNotRunnableError(FrontDoorError):
    """The picked bundle is not fully proven and was not explicitly overridden."""


class SelectionNotConfirmedError(FrontDoorError):
    """The operator did not explicitly confirm a selectable pick (HIL required)."""


class MissingRequiredInputError(FrontDoorError):
    """A required input (e.g. ``corpus_path``) was not supplied for the bundle."""


@dataclass(frozen=True)
class BundleOption:
    """One catalog row as the front door presents it, with honest readiness."""

    bundle_id: str
    display_name: str
    description: str
    readiness: BundleReadiness
    selectable: bool
    flag: str | None
    required_inputs: tuple[str, ...]


@dataclass(frozen=True)
class FrontDoorSelection:
    """The operator's confirmed choice: the bundle id, its blessed
    :class:`ComponentSelection`, and the collected seed inputs."""

    bundle_id: str
    selection: ComponentSelection
    seeds: dict[str, str] = field(default_factory=dict)


def present_catalog() -> tuple[BundleOption, ...]:
    """Present every catalog bundle with its honest front-door readiness.

    Readiness is read live from :func:`bundle_readiness` (the catalog's min-tier
    honesty layer) so a regressed/unbuilt component flags its bundle as
    non-selectable — the front door cannot offer an honest-looking choice that
    silently can't deliver.
    """
    options: list[BundleOption] = []
    for bundle_id, record in BUNDLE_CATALOG.items():
        readiness = bundle_readiness(record)
        options.append(
            BundleOption(
                bundle_id=bundle_id,
                display_name=record.display_name,
                description=record.description,
                readiness=readiness,
                selectable=readiness == "fully_proven",
                flag=_READINESS_FLAG[readiness],
                required_inputs=record.required_inputs,
            )
        )
    return tuple(options)


def render_catalog(options: Sequence[BundleOption] | None = None) -> str:
    """Render the catalog as Marcus-voiced operator-facing text with honest flags."""
    options = tuple(options) if options is not None else present_catalog()
    lines = [_RULE, "  Marcus-SPOC — choose a lesson bundle"]
    for index, opt in enumerate(options, start=1):
        status = "[selectable]" if opt.selectable else f"[FLAGGED: {opt.flag}]"
        lines.append(f"  {index}. {opt.bundle_id} — {opt.display_name}  {status}")
        lines.append(f"       {opt.description}")
        lines.append(
            f"       readiness={opt.readiness}; needs: {', '.join(opt.required_inputs)}"
        )
    lines.append(
        f"{_M} Pick a bundle by id. I can recommend, but YOU choose — and I will "
        "not run a flagged bundle as if it were complete."
    )
    return "\n".join(lines)


def front_door_select(
    *,
    operator_pick: str,
    confirmed: bool,
    seeds: Mapping[str, str] | None = None,
    recommendation: str | None = None,
    allow_unproven: bool = False,
) -> FrontDoorSelection:
    """Resolve the operator's pick into a runnable :class:`FrontDoorSelection`.

    Deterministic guard order:
      1. ``operator_pick`` must be a known catalog bundle id (else
         :class:`UnknownBundleError` — a hallucinated id never starts a run).
      2. ``confirmed`` must be ``True`` (HIL — the operator's explicit go-ahead).
      3. the bundle must be ``fully_proven`` unless ``allow_unproven`` is set
         (else :class:`BundleNotRunnableError` — no fabricated output).
      4. every ``required_input`` must be present in ``seeds`` (else
         :class:`MissingRequiredInputError`).

    ``recommendation`` is ADVISORY ONLY: it is accepted for surfacing/logging but
    is never consulted in the resolution above — the model never auto-selects.
    """
    del recommendation  # advisory only — NEVER drives the selection (guard A1/A2)

    record = get_bundle(operator_pick)
    if record is None:
        raise UnknownBundleError(
            f"{operator_pick!r} is not a bundle in the closed catalog "
            f"{sorted(BUNDLE_CATALOG)}; refusing to start a run against an "
            "unknown bundle"
        )
    if not confirmed:
        raise SelectionNotConfirmedError(
            f"bundle {record.id!r} was not confirmed by the operator; a front-door "
            "selection requires an explicit confirmation (HIL)"
        )
    readiness = bundle_readiness(record)
    if readiness != "fully_proven" and not allow_unproven:
        raise BundleNotRunnableError(
            f"bundle {record.id!r} readiness is {readiness!r} ({_READINESS_FLAG[readiness]}); "
            "it is not runnable as complete. Pick a fully-proven bundle, or pass "
            "allow_unproven=True to run it knowing the flagged status."
        )
    seeds_map: dict[str, str] = {k: v for k, v in dict(seeds or {}).items()}
    missing = [
        key
        for key in record.required_inputs
        if not str(seeds_map.get(key, "")).strip()
    ]
    if missing:
        raise MissingRequiredInputError(
            f"bundle {record.id!r} requires inputs {list(record.required_inputs)}; "
            f"missing: {missing}"
        )
    return FrontDoorSelection(
        bundle_id=record.id,
        selection=record.selection,
        seeds=seeds_map,
    )


def run_front_door(
    *,
    input_fn: Callable[[str], str],
    output_sink: Callable[[str], None] | None = None,
    seeds: Mapping[str, str] | None = None,
    recommend_fn: Callable[[tuple[BundleOption, ...]], str] | None = None,
    max_attempts: int = _DEFAULT_MAX_ATTEMPTS,
) -> FrontDoorSelection:
    """Drive the operator-facing front-door turn over injected IO seams.

    Presents the catalog (with honest flags), optionally surfaces an ADVISORY
    model recommendation, then loops reading the operator's pick + confirmation.
    A flagged (non-fully-proven) pick is refused at the gate — the operator is
    asked again; the model recommendation never short-circuits the loop. Returns
    the operator's confirmed, runnable :class:`FrontDoorSelection`.
    """
    emit = output_sink or (lambda text: print(text))  # noqa: T201
    options = present_catalog()
    emit(render_catalog(options))
    if recommend_fn is not None:
        recommendation = recommend_fn(options)
        emit(
            f"{_M} My recommendation (advisory — you decide): {recommendation}. "
            "Tell me which bundle you want."
        )

    for _ in range(max_attempts):
        pick = input_fn("bundle> ").strip()
        record = get_bundle(pick)
        if record is None:
            emit(
                f"{_M} {pick!r} isn't a bundle I offer. Choose one of the listed ids."
            )
            continue
        readiness = bundle_readiness(record)
        if readiness != "fully_proven":
            emit(
                f"{_M} {pick} is flagged ({_READINESS_FLAG[readiness]}); I won't run "
                "it as if complete. Pick a selectable bundle."
            )
            continue
        answer = input_fn(f"confirm {pick}? [yes/no] ").strip().lower()
        if answer not in _CONFIRM_TOKENS:
            emit(f"{_M} Not confirmed — pick again.")
            continue
        return front_door_select(
            operator_pick=pick,
            confirmed=True,
            seeds=seeds,
        )

    raise SelectionNotConfirmedError(
        "no confirmed selectable bundle was chosen within the attempt budget"
    )


__all__ = [
    "BundleNotRunnableError",
    "BundleOption",
    "FrontDoorError",
    "FrontDoorSelection",
    "MissingRequiredInputError",
    "SelectionNotConfirmedError",
    "UnknownBundleError",
    "front_door_select",
    "present_catalog",
    "render_catalog",
    "run_front_door",
]
