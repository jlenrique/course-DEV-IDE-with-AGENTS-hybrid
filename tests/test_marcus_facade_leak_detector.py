"""Facade-leak detector (AC-B.6, AC-T.6, AC-T.7).

Threat model (M-2 rider — articulated in this docstring per test-design
discipline): the risk under test is "accidental hyphenated-sub-identity
token leakage in any Maya-facing return path or error-message-propagation
channel" — NOT "non-determinism across many iterations."

Parametrization over 3 return paths (happy / error / empty) proves
coverage over the realistic leak-vector space. 50-iter loops were
parametrization theater without an articulated threat model; dropped per
M-2 rider.

Hyphenated token grep (W-4 rider) explicitly checks for ``"marcus-intake"``,
``"marcus-orchestrator"``, and ``"marcus-negotiator"`` — the realistic
leak vector is accidental f-string interpolation like
``f"Error in {INTAKE_MODULE_IDENTITY}"``, not raw identity assignment.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest

from app.marcus.facade import MARCUS_DISPLAY_NAME, get_facade, reset_facade
from app.marcus.lesson_plan.events import EventEnvelope
from app.marcus.lesson_plan.log import LessonPlanLog
from app.marcus.orchestrator.write_api import emit_pre_packet_snapshot

_FORBIDDEN_HYPHENATED_TOKENS: tuple[str, ...] = (
    "marcus-intake",
    "marcus-orchestrator",
    "marcus-negotiator",
)


@pytest.fixture(autouse=True)
def _reset_facade_between_tests() -> Any:
    """Isolate facade state across tests (W-1 rider — lazy accessor hygiene)."""
    reset_facade()
    yield
    reset_facade()


def _assert_no_hyphenated_leak(surface_string: str, context: str) -> None:
    lower = surface_string.lower()
    for token in _FORBIDDEN_HYPHENATED_TOKENS:
        assert token not in lower, (
            f"Hyphenated sub-identity token {token!r} leaked in "
            f"{context}: {surface_string!r}"
        )


@pytest.mark.parametrize("return_path", ["happy", "error", "empty"])
def test_facade_return_paths_name_one_marcus_identity(
    return_path: str, tmp_path: Path
) -> None:
    """AC-T.6 — Maya-facing surfaces render one "Marcus"; no hyphen-token leak."""
    facade = get_facade()

    if return_path == "happy":
        # 30-3a: greet() replaced by run_4a() (loop surface). repr(facade)
        # remains the Maya-surface smoke — renders the one "Marcus"
        # display name per 30-1's AC-B.4 __repr__ contract.
        surface = repr(facade)
        assert MARCUS_DISPLAY_NAME in surface, (
            f"happy path must render MARCUS_DISPLAY_NAME; got {surface!r}"
        )
        _assert_no_hyphenated_leak(surface, "repr(facade)")

    elif return_path == "error":
        # AC-T.7 — negative case: non-Orchestrator invocation of write_api
        # raises; the Maya-facing str(err) must not leak hyphen tokens.
        log = LessonPlanLog(path=tmp_path / "log.jsonl")
        envelope = EventEnvelope(
            event_id=str(uuid4()),
            timestamp=datetime.now(tz=UTC),
            plan_revision=0,
            event_type="pre_packet_snapshot",
            payload={
                "source_ref": {"path": "x.md", "sha256": "a" * 64},
                "pre_packet_artifact_path": "x.md",
                "audience_profile_version": 1,
                "sme_refs": ["x"],
            },
        )
        from app.marcus.orchestrator.write_api import UnauthorizedFacadeCallerError

        with pytest.raises(UnauthorizedFacadeCallerError) as exc_info:
            emit_pre_packet_snapshot(
                envelope, writer="marcus-intake", log=log  # type: ignore[arg-type]
            )
        surface = str(exc_info.value)
        _assert_no_hyphenated_leak(surface, "str(UnauthorizedFacadeCallerError)")

    else:  # empty
        surface = repr(facade)
        assert surface == MARCUS_DISPLAY_NAME
        _assert_no_hyphenated_leak(surface, "repr(facade)")


def test_non_maya_direct_invocation_of_orchestrator_fails() -> None:
    """AC-T.7 / AC-B.7 — non-Maya callers bypassing facade fail.

    R1 amendment 12 binding — facade-leak detector negative case.
    """
    from app.marcus.orchestrator.write_api import UnauthorizedFacadeCallerError

    envelope = EventEnvelope(
        event_id=str(uuid4()),
        timestamp=datetime.now(tz=UTC),
        plan_revision=0,
        event_type="pre_packet_snapshot",
        payload={
            "source_ref": {"path": "x.md", "sha256": "a" * 64},
            "pre_packet_artifact_path": "x.md",
            "audience_profile_version": 1,
            "sme_refs": ["x"],
        },
    )

    with pytest.raises(UnauthorizedFacadeCallerError):
        emit_pre_packet_snapshot(envelope, writer="marcus-intake")  # type: ignore[arg-type]
