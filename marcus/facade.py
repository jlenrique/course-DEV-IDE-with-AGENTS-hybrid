"""Single Maya-facing Marcus facade.

This module exposes the ONE surface Maya interacts with. The Marcus
duality split landed in Story 30-1 hides internal sub-package
boundaries behind this facade — Maya experiences one Marcus.

Maya-facing note
----------------

Maya sees ONE Marcus. The facade's return values and ``repr`` all render
"Marcus" — a consolidated single voice. Internal routing identifiers
never surface in Maya-visible strings; R1 amendment 17
(Marcus-as-one-voice) enforcement lives in the test file
``test_no_intake_orchestrator_leak_marcus_duality.py``.

Voice Register — binding on Facade Maya-facing surfaces
-------------------------------------------------------

Every Maya-facing string returned by a Facade method MUST honor:

1. **First person singular.** "I", never "Marcus will" or "the assistant".
2. **Present tense.** Not "I will" or "I was".
3. **No hedges.** No "I'll try to", "maybe I can", "I'm not sure but".
4. **No meta-references.** No "as your assistant", "as an AI".
5. **Ends with a question or an invitation to proceed.** Keeps the
   conversation in Maya's court (Marcus-as-SPOC posture).

The stub :meth:`Facade.greet` at 30-1 pins one example that honors all
five rules. Story 30-3a's real 4A conversation surface inherits these
rules; it does not relax them.

Maya-visibility boundary
------------------------

As of Story 30-1, the facade's return values and :meth:`Facade.__repr__`
are assumed to surface to Maya verbatim unless a later story introduces
a rendering layer. Any future layer inherits the same string discipline;
it does not relax it. A rendering layer MAY sanitize further but MUST
NOT reintroduce hyphenated sub-identity tokens.

Developer discipline note
-------------------------

* 30-1 (structural foundation, done): facade shell with lazy
  accessor, two identity constants, stub ``Facade.greet``, and the
  Voice Register above.
* 30-3a (4A skeleton + lock, this commit): replaces the 30-1
  ``Facade.greet`` stub with :meth:`Facade.run_4a` — the first real 4A
  conversation surface. Runs :class:`marcus.orchestrator.loop.FourALoop`
  under the hood; returns the locked :class:`LessonPlan`.
* 30-3b (next): dial tuning + sync reassessment on top of the loop.
* 30-4+ stories: extend facade dispatch to route Intake artifacts
  through :mod:`marcus.orchestrator.write_api` for log emission.

Lazy-accessor construction (W-1 rider)
--------------------------------------

Do NOT instantiate a module-level ``facade = Facade()`` singleton.
Module-load singletons couple session state to import order and will
bite 30-3a when per-session conversation context lands. Use the lazy
accessor :func:`get_facade` instead; pytest fixtures can call
:func:`reset_facade` to isolate per-test state.
"""

from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final, Literal
from uuid import UUID, uuid4

from app.manifest import load as load_manifest
from app.models.state.run_state import RunState
from app.models.state.sanctum_fingerprint import SanctumFingerprint

if TYPE_CHECKING:
    from marcus.lesson_plan.fit_report import FitReport
    from marcus.lesson_plan.log import LessonPlanLog
    from marcus.lesson_plan.schema import LessonPlan
    from marcus.orchestrator.loop import IntakeCallable
    from marcus.orchestrator.supervisor import SupervisorPreset

MARCUS_IDENTITY: Literal["marcus"] = "marcus"
"""Programming-token identity. Stable key for routing + logging.

Deliberately lowercase — a grep-time structural tripwire. If a developer
ever interpolates ``MARCUS_IDENTITY`` into a Maya-facing string, the
resulting "marcus" reads wrong in a screenshot and QA catches it
instantly. Maya-facing surfaces render from :data:`MARCUS_DISPLAY_NAME`
instead.
"""

MARCUS_DISPLAY_NAME: Final[str] = "Marcus"
"""Maya-facing render constant. All user-visible strings MUST use this."""


class Facade:
    """Maya's single Marcus-facing surface.

    Instances are constructed via :func:`get_facade`; direct
    instantiation is supported but not the idiomatic path.

    Story 30-3a landed :meth:`run_4a` as the real 4A conversation
    entry. Story 30-1's transitional ``greet`` stub was replaced.
    """

    def __init__(
        self,
        *,
        session_id: UUID | None = None,
        sanctum_digest: str | None = None,
        manifest: Any | None = None,
        state: RunState | None = None,
    ) -> None:
        self.session_id = session_id or uuid4()
        self.sanctum_digest = sanctum_digest or ""
        self._manifest = manifest
        self.state = state

    @property
    def marcus_identity(self) -> Literal["marcus"]:
        """Stable programming-token identity (read-only).

        Exposed as a property instead of a mutable class attribute to avoid
        cross-test mutation leaks.
        """
        return MARCUS_IDENTITY

    def __repr__(self) -> str:
        return MARCUS_DISPLAY_NAME

    def run_step(
        self,
        state: Any,
        *,
        preset: SupervisorPreset = "production",
    ) -> Any:
        from marcus.orchestrator.supervisor import Supervisor

        supervisor = Supervisor(preset=preset, manifest=self._manifest)
        return supervisor.run_step(state)

    def run_4a(
        self,
        packet_plan: LessonPlan,
        *,
        intake_callable: IntakeCallable,
        fit_report: FitReport | None = None,
        prior_declined_rationales: tuple[tuple[str, str], ...] = (),
        log: LessonPlanLog | None = None,
        tracy_bridge: Any | None = None,
    ) -> LessonPlan:
        """Drive the 4A conversation loop from an initial plan through plan-lock.

        Maya-facing note
        ----------------

        Maya sees one Marcus. The loop runs under the hood, iterating
        through plan units, recording her scope-decision per unit, and
        returning the locked :class:`LessonPlan` when every unit has
        been ratified.

        Args:
            packet_plan: Initial :class:`LessonPlan` draft — typically
                assembled from the 30-2b pre-packet snapshot plus the
                29-2 fit-report. At this story the caller assembles it;
                30-4 will thread this through the runtime.
            intake_callable: Per-unit prompt callable. Production
                wiring (30-3b) connects this to Maya's real UI; tests
                pass a pre-programmed stub.
            fit_report: Optional 29-2 :class:`FitReport`. Accepted at
                30-3a for future-facing wiring; prior-decline carry-forward
                (R1 amendment 15) is surfaced via the separate
                ``prior_declined_rationales`` kwarg (see below).
            prior_declined_rationales: Tuple of ``(unit_id, rationale)``
                pairs from a previous run. Each becomes a pre-ratified
                ``out-of-scope`` decision with the rationale stored
                verbatim (R1 amendment 15). Maya is NOT prompted for
                units named here.
            log: Optional :class:`LessonPlanLog` for test isolation.
                ``None`` is production default (writes to
                ``state/runtime/lesson_plan_log.jsonl``).
            tracy_bridge: Optional Irene→Tracy bridge adapter. When present,
                plan-lock fanout auto-dispatches in-scope gaps through this
                bridge and records fanout envelopes to the log.

        Returns:
            The locked :class:`LessonPlan` — ``revision`` bumped,
            ``digest`` recomputed, every plan_unit carrying a ratified
            scope-decision.
        """
        # Late imports avoid circulars at module-load time; see
        # TYPE_CHECKING block above for the static-type surface.
        from functools import partial

        from marcus.lesson_plan.log import LessonPlanLog as _LessonPlanLog
        from marcus.orchestrator.dispatch import dispatch_orchestrator_event
        from marcus.orchestrator.fanout import emit_plan_lock_fanout
        from marcus.orchestrator.loop import FourALoop

        resolved_log = log if log is not None else _LessonPlanLog()
        dispatch = partial(dispatch_orchestrator_event, log=resolved_log)

        # fit_report is accepted for forward-compatibility; prior-decline
        # carry-forward flows through the dedicated kwarg per 29-2's
        # PriorDeclinedRationale shape (unit_id + rationale only).
        _ = fit_report  # reserved surface; consumed by downstream stories.

        loop = FourALoop(
            dispatch=dispatch,
            latest_locked_revision=resolved_log.latest_plan_revision(),
        )
        locked_plan = loop.run_4a(
            packet_plan,
            intake_callable=intake_callable,
            prior_declined_rationales=prior_declined_rationales,
        )
        emit_plan_lock_fanout(
            locked_plan,
            dispatch=dispatch,
            bridge=tracy_bridge,
        )
        return locked_plan


_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[1]
_MARCUS_SKILL_PATH: Final[Path] = _REPO_ROOT / "skills" / "bmad-agent-marcus" / "SKILL.md"
_MARCUS_SANCTUM_ROOT: Final[Path] = _REPO_ROOT / "_bmad" / "memory" / "bmad-agent-marcus"
_PIPELINE_MANIFEST_PATH: Final[Path] = _REPO_ROOT / "state" / "config" / "pipeline-manifest.yaml"
_ACTIVATION_FILE_NAME_PATTERN: Final[re.Pattern[str]] = re.compile(r"`([^`]+)`")


def _resolve_activation_allowlist(skill_path: Path | None = None) -> tuple[str, ...]:
    resolved_path = skill_path or _MARCUS_SKILL_PATH
    content = resolved_path.read_text(encoding="utf-8")
    for line in content.splitlines():
        if "Batch-load from sanctum:" not in line:
            continue
        file_names = tuple(_ACTIVATION_FILE_NAME_PATTERN.findall(line))
        if file_names:
            return file_names
        break
    raise ValueError(
        "Marcus sanctum activation allowlist resolved no files from "
        f"{resolved_path}"
    )


def _read_marcus_sanctum_digest(
    *,
    sanctum_root: Path | None = None,
    skill_path: Path | None = None,
) -> str:
    resolved_root = sanctum_root or _MARCUS_SANCTUM_ROOT
    if not resolved_root.is_dir():
        raise FileNotFoundError(
            f"Marcus sanctum directory not found: {resolved_root}"
        )

    allowlist = _resolve_activation_allowlist(skill_path=skill_path)
    digest = hashlib.sha256()
    for file_name in allowlist:
        file_path = resolved_root / file_name
        if not file_path.is_file():
            raise FileNotFoundError(
                f"Marcus sanctum file missing from activation allowlist: {file_path}"
            )
        digest.update(file_name.encode("utf-8"))
        digest.update(b"\n")
        digest.update(file_path.read_bytes())
        digest.update(b"\n")
    return digest.hexdigest()


def get_facade() -> Facade:
    """Return a fresh :class:`Facade` with a fresh sanctum-read session.

    Story 3.1 rebases Marcus activation onto a cold-read discipline:
    every call re-reads the sanctum digest and issues a new session id.
    """
    digest = _read_marcus_sanctum_digest()
    session_id = uuid4()
    manifest = load_manifest(_PIPELINE_MANIFEST_PATH)
    state = RunState(graph_version="v0.1-stub")
    state.marcus_fingerprint = (digest, session_id)
    state.sanctum_fingerprint = SanctumFingerprint(
        content_sha256=digest,
        captured_at=datetime.now(UTC),
    )
    return Facade(
        session_id=session_id,
        sanctum_digest=digest,
        manifest=manifest,
        state=state,
    )


def reset_facade() -> None:
    """Compatibility no-op for legacy tests that still call `reset_facade()`."""
    return None


__all__: Final[tuple[str, ...]] = (
    "MARCUS_IDENTITY",
    "MARCUS_DISPLAY_NAME",
    "Facade",
    "get_facade",
)
# Note: `reset_facade` is a pytest-fixture hook, intentionally NOT exposed via
# `__all__`. Tests import it by name (`from marcus.facade import reset_facade`).
# Keeping it out of `__all__` prevents `from marcus.facade import *` from
# leaking the test-only helper into production namespaces.
