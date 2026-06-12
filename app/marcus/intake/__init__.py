"""Marcus-Intake: steps 01-04 + 4A pre-packet construction.

This sub-package is part of the Marcus duality split landed in Story 30-1.

Maya-facing note
----------------

Maya never imports from this package. She interacts with a single Marcus
facade (``marcus.facade.get_facade()``). The sub-package exists internally
to isolate the ingestion + pre-packet-construction side of Marcus from the
conversation-orchestration side — a developer-ergonomics boundary, not a
user-visible one.

Developer discipline note
-------------------------

* 30-1 (structural foundation, this commit): module shell + identity
  constant only. **No pipeline code** lands here at 30-1.
* 30-2a (refactor-only lift): lifts existing extraction code into this
  package. Byte-identical regression guard (see
  ``tests/test_marcus_golden_trace_regression.py``).
* 30-2b (new emission feature): adds the ``pre_packet_snapshot`` emission
  feature on top of the 30-2a lift; emission routes through
  :mod:`marcus.orchestrator.write_api` (single-writer rule, R1 amendment 13).

LIFT-TARGET registry (30-2a + beyond)
-------------------------------------

Pre-30-1 source surfaces targeted for lift into this package:

* **LIFTED at 30-2a**: ``scripts/utilities/prepare-irene-packet.py`` →
  :mod:`marcus.intake.pre_packet`. Byte-identical move of
  ``prepare_irene_packet()``; CLI script retained as a thin shim. See
  ``_bmad-output/implementation-artifacts/30-2a-pre-packet-extraction-lift.md``.
* **OUT OF 30-2a SCOPE — deferred**: ``scripts/utilities/marcus_prompt_harness.py``.
  Validation/reporting harness spanning steps 1-8; only a narrow slice
  pertains to intake. Lift (if ever) belongs in a dedicated harness-refactor
  story, not in the 30-2a pre-packet lift.
* **OUT OF 30-2a SCOPE — prompt-layer, not Python**: Marcus-skill intake
  prompts in ``_bmad/`` skill files. Prompt content, not Python modules;
  no lift applicable.
* **OUT OF 30-2a SCOPE — data, not code**: ``_bmad/memory/marcus-sidecar/``
  persisted envelope shapes. Not Python modules; no lift applicable.

All lift work preserves pre-30-1 behavior byte-identical (modulo the four
locked normalization rules: timestamps / UUID4 / SHA-256 / repo-root). See
``_bmad-output/specs/30-1-golden-trace-baseline-capture-plan.md``.

Single-writer discipline
------------------------

Intake-side code MUST NOT call
:func:`app.marcus.lesson_plan.log.LessonPlanLog.append_event` directly. All
log writes route through :func:`marcus.orchestrator.write_api.emit_pre_packet_snapshot`,
which the facade's internal dispatch invokes on Intake's behalf. R1
amendment 13 (Quinn single-writer rule); enforced by
``tests/contracts/test_marcus_single_writer_routing.py``.
"""

from __future__ import annotations

from typing import Final, Literal

INTAKE_MODULE_IDENTITY: Literal["marcus-intake"] = "marcus-intake"
"""Programming-token identity for the Intake half of the Marcus duality.

String-equal to the 31-2 ``WriterIdentity`` Literal value. Used for log
writer-identity routing and internal audit — NOT a Maya-facing string.
See :data:`app.marcus.lesson_plan.log.WriterIdentity`.
"""

# ---- merged from legacy app/marcus/intake.py flat module (S2 merge 2026-05-07) ----
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.marcus.orchestrator.write_api import append_event


class PrePacketSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    run_id: str = Field(..., min_length=1)
    source_ref: str = Field(..., min_length=1)
    operator_prompt: str = Field(..., min_length=1)
    normalized_payload: dict[str, Any] = Field(default_factory=dict)


def extract_pre_packet(state: Any) -> PrePacketSnapshot:
    bundle = getattr(state, "input_bundle", {})
    snapshot = PrePacketSnapshot.model_validate(
        {
            "run_id": getattr(state, "run_id", "unknown-run"),
            "source_ref": bundle.get("source_ref", "unknown-source"),
            "operator_prompt": bundle.get("operator_prompt", ""),
            "normalized_payload": dict(bundle),
        }
    )
    event = {
        "event_type": "pre_packet_snapshot",
        "actor": "Marcus",
        "snapshot": snapshot.model_dump(mode="json"),
    }
    append_event(state, event)
    return snapshot


__all__: Final[tuple[str, ...]] = (
    "INTAKE_MODULE_IDENTITY",
    "PrePacketSnapshot",
    "extract_pre_packet",
)
