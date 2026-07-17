"""Marcus interlocutor — the LLM-driven, stop-and-chat interlocution REPL (S5).

This is the arc-finale conversational Marcus: a turn-taking REPL over the same
paused-trial engine the scripted ``run_marcus_spoc`` drives, but as a genuine
conversation. At each gate Marcus narrates the real decision card (LLM-phrased,
in persona), then enters a turn loop reading operator free-form input. Each turn
is answered by a real LLM (the house seam, marcus cascade tier). When the
operator's input resolves to a gate decision, Marcus CONFIRMS the validated
verb+payload, then drives ``resume_production_trial`` and advances to the next
gate. Repeats to completion / clean error-pause.

Design (T1 decisions, spec §6/§8):

- **DI seam for the chat model (A4).** ``chat_model: BaseChatModel | None`` is
  constructor-injected; default builds ``make_chat_model("marcus", ...)`` at the
  marcus cascade tier. Offline tests inject a fake ``BaseChatModel``; a live
  model/network call in the offline path RAISES (no silent fall-through).

- **Injected I/O.** ``input_source`` (a callable yielding operator lines) and
  ``output_sink`` (a callable consuming rendered text) are injected so offline
  tests script turns deterministically. The ``--interactive`` entrypoint wires
  real ``input()`` / ``print``.

- **Deterministic guard is LOAD-BEARING (A1/A2).** Before ANY engine drive the
  proposed verb is checked against the gate's allowed verb set and ``select``
  keys are validated by REUSING the engine's own validator
  (``production_runner._merge_selection_into_envelope`` /
  ``_SELECTABLE_KEYS_BY_GATE`` raising ``UnknownSelectionKeyError``). A
  hallucinated/forbidden action results in ZERO engine calls.

- **Confirm-before-forward (A9).** A forward decision requires an explicit
  operator confirmation turn before the engine fires; the confirm text echoes
  the VALIDATED verb+payload, not the model's free text. "no" cancels.

- **Transcript (A8).** Per-turn ``{operator input, Marcus response, structured
  action}`` is persisted to ``marcus-interlocution-<trial>.md`` in the run dir.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import UUID

from langchain_core.language_models import BaseChatModel

from app.marcus.cli.capability_grounding import (
    GroundingContext,
    build_grounding_context,
    load_overlay,
    research_token_precondition,
)
from app.marcus.cli.marcus_spoc import (
    _M,
    _RULE,
    DEFAULT_OPERATOR_ID,
    build_operator_verdict_kwargs,
    narrate_gate,
)
from app.marcus.orchestrator import production_runner
from app.marcus.orchestrator.production_runner import (
    UnknownSelectionKeyError,
    resume_production_trial,
)
from app.models.state.operator_verdict import OperatorVerdict
from app.runtime.economics import RUNS_ROOT

# The closed verb set the engine's OperatorVerdict accepts. A model-proposed verb
# outside this set is hallucinated/forbidden → refused with ZERO engine calls.
ALLOWED_VERBS: frozenset[str] = frozenset({"approve", "edit", "reject", "select"})
FORWARD_VERBS: frozenset[str] = ALLOWED_VERBS  # every accepted verb advances/forwards

_MAX_GATES = 30
_MAX_TURNS_PER_GATE = 40


class GuardRefusal(ValueError):  # noqa: N818
    """A model-proposed action failed the deterministic guard (never driven)."""


@dataclass(frozen=True)
class StructuredAction:
    """The structured action the model emits per turn (parsed defensively).

    A malformed payload (non-JSON, missing ``intent``, unknown shape) is coerced
    to ``intent="chat"`` and NEVER drives the engine.
    """

    intent: str  # "chat" | "decide"
    reply: str = ""
    verb: str | None = None
    edit_payload: Any | None = None
    reject_reason: str | None = None
    confirm_text: str | None = None

    @classmethod
    def parse(cls, raw: str) -> StructuredAction:
        """Defensively parse the model's structured output; malformed → chat."""
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return cls(intent="chat", reply=raw if isinstance(raw, str) else "")
        if not isinstance(data, dict):
            return cls(intent="chat", reply=str(raw))
        intent = data.get("intent")
        if intent not in {"chat", "decide"}:
            # Unknown/missing intent → treat as chat (never drive).
            return cls(intent="chat", reply=str(data.get("reply", raw)))
        return cls(
            intent=intent,
            reply=str(data.get("reply", "")),
            verb=data.get("verb"),
            edit_payload=data.get("edit_payload"),
            reject_reason=data.get("reject_reason"),
            confirm_text=data.get("confirm_text"),
        )


@dataclass(frozen=True)
class ValidatedDecision:
    """A guard-validated, ready-to-drive decision (the ONLY thing that drives)."""

    gate_id: str
    verb: str
    edit_payload: Any | None
    reject_reason: str | None

    def confirm_echo(self) -> str:
        """The confirm text — echoes the VALIDATED verb+payload (A9), not model prose."""
        parts = [f"verb={self.verb}"]
        if self.verb in {"edit", "select"}:
            parts.append(f"payload={self.edit_payload!r}")
        if self.verb == "reject":
            parts.append(f"reason={self.reject_reason!r}")
        return f"{self.gate_id}: " + ", ".join(parts)


def validate_action_against_gate(
    action: StructuredAction, gate_id: str
) -> ValidatedDecision:
    """Deterministic guard (LOAD-BEARING). Reject any unauthorized action.

    Reuses the engine's OWN validator (A1): for ``select`` the key set is checked
    via ``production_runner._merge_selection_into_envelope`` (raising
    ``UnknownSelectionKeyError`` for keys outside ``_SELECTABLE_KEYS_BY_GATE``),
    NOT a parallel copy. A verb outside :data:`ALLOWED_VERBS`, or a malformed
    select payload, raises :class:`GuardRefusal` BEFORE any engine drive.
    """
    if action.intent != "decide":
        raise GuardRefusal("action is not a decision (intent != 'decide')")
    verb = action.verb
    if verb not in ALLOWED_VERBS:
        raise GuardRefusal(
            f"verb {verb!r} is outside the allowed gate verb set {sorted(ALLOWED_VERBS)}"
        )
    if verb in {"edit", "select"}:
        payload = action.edit_payload
        if not isinstance(payload, dict):
            raise GuardRefusal(
                f"verb {verb!r} requires a dict edit_payload; got {type(payload).__name__}"
            )
        if verb == "select":
            # REUSE the engine's validator — raises UnknownSelectionKeyError for
            # any key outside _SELECTABLE_KEYS_BY_GATE[gate_id]. We validate keys
            # only (existing={}), no mutation of real state happens here.
            try:
                production_runner._merge_selection_into_envelope({}, payload, gate_id)
            except UnknownSelectionKeyError as exc:
                raise GuardRefusal(str(exc)) from exc
    return ValidatedDecision(
        gate_id=gate_id,
        verb=verb,
        edit_payload=action.edit_payload,
        reject_reason=action.reject_reason,
    )


@dataclass
class TranscriptEntry:
    """One persisted turn: operator input + Marcus response + structured action."""

    gate_id: str
    operator_input: str
    marcus_response: str
    action: dict[str, Any]


def _system_prompt(grounding: GroundingContext) -> str:
    return (
        "You are Marcus-SPOC, the operator's single point of contact for a course-"
        "production run. You converse honestly and drive the production engine on "
        "the operator's behalf. You may ONLY claim capabilities that the grounding "
        "block below asserts; never up-level a capability_state.\n\n"
        f"{grounding.render()}\n\n"
        "Each turn, respond with a single JSON object: "
        '{"intent": "chat"|"decide", "reply": "<your words>", '
        '"verb": "approve"|"edit"|"reject"|"select" (only when deciding), '
        '"edit_payload": {...} (for edit/select), "reject_reason": "..." (for reject)}. '
        "Use intent=decide ONLY when the operator has clearly chosen a gate action."
    )


def _load(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


class MarcusInterlocutor:
    """The live, LLM-driven stop-and-chat interlocution REPL over a paused trial."""

    def __init__(
        self,
        trial_id: UUID,
        *,
        chat_model: BaseChatModel | None = None,
        input_source: Callable[[str], str] | Iterable[str] | None = None,
        output_sink: Callable[[str], None] | None = None,
        runs_root: Path = RUNS_ROOT,
        operator_id: str = DEFAULT_OPERATOR_ID,
        grounding: GroundingContext | None = None,
        resume_fn: Callable[..., Any] = resume_production_trial,
        # Story 41-3: the call-count throttle was removed; None = unbounded.
        # The old =12 default is moot (a specialist node dispatches whenever
        # live is available, with no per-call budget gate).
        max_specialist_calls: int | None = None,
    ) -> None:
        self.trial_id = trial_id
        self.runs_root = runs_root
        self.run_dir = runs_root / str(trial_id)
        self.operator_id = operator_id
        self._resume_fn = resume_fn
        self._max_specialist_calls = max_specialist_calls
        # DI seam (A4): default to the marcus cascade tier; offline tests inject
        # a fake. We build lazily so a missing seam never fires in offline tests.
        self._chat_model = chat_model
        self._grounding = grounding
        self._output_sink = output_sink or (lambda text: print(text))  # noqa: T201
        self._input_source = _normalize_input_source(input_source)
        self.transcript: list[TranscriptEntry] = []

    # -- seam accessors -----------------------------------------------------

    @property
    def chat_model(self) -> BaseChatModel:
        if self._chat_model is None:
            # No fall-through in the offline path: building the live seam here is
            # the ONLY way a live model would be reached, and it requires the
            # marcus cascade + an API key — a fake must be injected for offline.
            from app.models.adapter import make_chat_model

            self._chat_model = make_chat_model("marcus", tier_request="marcus").chat
        return self._chat_model

    @property
    def grounding(self) -> GroundingContext:
        if self._grounding is None:
            overlay = load_overlay()
            self._grounding = build_grounding_context(
                overlay,
                stale=_overlay_is_stale(),
                research_precondition=research_token_precondition(),
            )
        return self._grounding

    # -- I/O ----------------------------------------------------------------

    def _emit(self, text: str) -> None:
        self._output_sink(text)

    def _ask(self, prompt: str) -> str:
        return self._input_source(prompt)

    # -- model turn ---------------------------------------------------------

    def _model_turn(self, gate_id: str, operator_input: str) -> StructuredAction:
        messages = [
            ("system", _system_prompt(self.grounding)),
            ("system", f"Current gate: {gate_id}."),
            ("human", operator_input),
        ]
        response = self.chat_model.invoke(messages)
        raw = response.content if hasattr(response, "content") else str(response)
        if isinstance(raw, list):  # some chat models return content parts
            raw = "".join(str(part) for part in raw)
        return StructuredAction.parse(str(raw))

    # -- gate loop ----------------------------------------------------------

    def _drive(self, decision: ValidatedDecision, card: dict[str, Any]) -> Any:
        kwargs = build_operator_verdict_kwargs(
            trial_id=self.trial_id,
            gate_id=decision.gate_id,
            card=card,
            verb=decision.verb,
            edit_payload=decision.edit_payload,
            reject_reason=decision.reject_reason,
            operator_id=self.operator_id,
        )
        return self._resume_fn(
            trial_id=self.trial_id,
            verdict=OperatorVerdict(**kwargs),
            runs_root=self.runs_root,
            max_specialist_calls=self._max_specialist_calls,
        )

    def _run_gate(self, gate_id: str, card: dict[str, Any]) -> Any:
        """Turn loop at one gate. Returns the post-drive envelope, or None if the
        operator never decided (input exhausted)."""
        self._emit(narrate_gate(gate_id, card, self.run_dir))
        for _ in range(_MAX_TURNS_PER_GATE):
            try:
                operator_input = self._ask(f"[{gate_id}] you> ")
            except StopIteration:
                return None
            action = self._model_turn(gate_id, operator_input)
            self._emit(f"👤 **Operator:** {operator_input}")
            self._emit(f"{_M} {action.reply}")
            self.transcript.append(
                TranscriptEntry(
                    gate_id=gate_id,
                    operator_input=operator_input,
                    marcus_response=action.reply,
                    action=_action_dict(action),
                )
            )
            if action.intent != "decide":
                continue  # free-form chat turn — keep talking, never drive.
            # Deterministic guard BEFORE any drive (A1/A2 — load-bearing).
            try:
                decision = validate_action_against_gate(action, gate_id)
            except GuardRefusal as refusal:
                msg = (
                    f"{_M} I can't do that here — {refusal}. We stay at {gate_id}; "
                    "tell me a valid decision."
                )
                self._emit(msg)
                self.transcript.append(
                    TranscriptEntry(
                        gate_id=gate_id,
                        operator_input=operator_input,
                        marcus_response=msg,
                        action={"intent": "guard-refused", "reason": str(refusal)},
                    )
                )
                continue  # ZERO engine calls — stay at the gate.
            # Confirm-before-forward (A9): echo the VALIDATED verb+payload.
            if not self._confirm(decision):
                continue  # operator cancelled — stay at the gate, no drive.
            return self._drive(decision, card)
        return None

    def _confirm(self, decision: ValidatedDecision) -> bool:
        echo = decision.confirm_echo()
        self._emit(
            f"{_M} To confirm, I will drive — {echo}. Type 'yes' to proceed, "
            "anything else to cancel."
        )
        try:
            answer = self._ask(f"[{decision.gate_id}] confirm> ")
        except StopIteration:
            return False
        confirmed = answer.strip().lower() in {"yes", "y", "confirm", "do it"}
        self.transcript.append(
            TranscriptEntry(
                gate_id=decision.gate_id,
                operator_input=answer,
                marcus_response=f"confirmation={'accepted' if confirmed else 'cancelled'}",
                action={"intent": "confirm", "echo": echo, "confirmed": confirmed},
            )
        )
        if not confirmed:
            self._emit(f"{_M} Cancelled — we stay at {decision.gate_id}.")
        return confirmed

    # -- REPL ---------------------------------------------------------------

    def run(self) -> list[TranscriptEntry]:
        """Drive the paused trial as a live conversation; persist the transcript."""
        self._emit(
            f"{_M} I'm your single point of contact for this run (trial "
            f"{self.trial_id}). Talk to me — I'll narrate each gate, answer "
            "honestly about what I can do, and drive the engine when you decide."
        )
        for _ in range(_MAX_GATES):
            run = _load(self.run_dir / "run.json") or {}
            status, gate = run.get("status"), run.get("paused_gate")
            if status == "completed":
                self._emit(
                    f"{_RULE}\n{_M} Your lesson is assembled — slides, narration, and the "
                    "Descript hand-off bundle are ready. That's the run, error-free."
                )
                break
            if status == "paused-at-error":
                self._emit(
                    f"{_M} I hit a snag I couldn't auto-resolve "
                    f"({run.get('paused_error_tag')}); pausing for repair. I won't "
                    "rewrite pipeline state on my own."
                )
                break
            if status != "paused-at-gate" or not gate:
                self._emit(f"{_M} Unexpected state ({status}); stopping.")
                break
            card = _load(self.run_dir / f"decision-card-{gate}.json") or {}
            envelope = self._run_gate(gate, card)
            if envelope is None:
                self._emit(f"{_M} (no decision reached at {gate}; ending the session.)")
                break
            nxt = f", next: {envelope.paused_gate}" if envelope.paused_gate else ""
            self._emit(f"{_M} (done — {envelope.status}{nxt})")
        self._persist_transcript()
        return self.transcript

    def _persist_transcript(self) -> Path:
        path = self.run_dir / f"marcus-interlocution-{self.trial_id}.md"
        lines = [f"# Marcus-SPOC interlocution transcript — trial {self.trial_id}", ""]
        for i, entry in enumerate(self.transcript, start=1):
            lines.append(f"## Turn {i} — gate {entry.gate_id}")
            lines.append(f"- **Operator:** {entry.operator_input}")
            lines.append(f"- **Marcus-SPOC:** {entry.marcus_response}")
            lines.append(f"- **Structured action:** `{json.dumps(entry.action)}`")
            lines.append("")
        self.run_dir.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines), encoding="utf-8")
        return path


def run_marcus_interlocutor(
    trial_id: UUID,
    *,
    chat_model: BaseChatModel | None = None,
    input_source: Callable[[str], str] | Iterable[str] | None = None,
    output_sink: Callable[[str], None] | None = None,
    runs_root: Path = RUNS_ROOT,
    grounding: GroundingContext | None = None,
    resume_fn: Callable[..., Any] = resume_production_trial,
    max_specialist_calls: int | None = None,  # Story 41-3: None = unbounded.
) -> list[TranscriptEntry]:
    """Convenience wrapper: construct + run a :class:`MarcusInterlocutor`."""
    return MarcusInterlocutor(
        trial_id,
        chat_model=chat_model,
        input_source=input_source,
        output_sink=output_sink,
        runs_root=runs_root,
        grounding=grounding,
        resume_fn=resume_fn,
        max_specialist_calls=max_specialist_calls,
    ).run()


def _action_dict(action: StructuredAction) -> dict[str, Any]:
    return {
        "intent": action.intent,
        "reply": action.reply,
        "verb": action.verb,
        "edit_payload": action.edit_payload,
        "reject_reason": action.reject_reason,
    }


def _normalize_input_source(
    source: Callable[[str], str] | Iterable[str] | None,
) -> Callable[[str], str]:
    """Coerce the input source into a ``prompt -> line`` callable.

    Accepts a callable (real ``input``), an iterable/iterator of scripted lines
    (offline tests), or ``None`` (defaults to real ``input``). An exhausted
    iterable raises ``StopIteration`` (caught by the loop as "session over").
    """
    if source is None:
        return input
    if callable(source):
        return source  # type: ignore[return-value]
    iterator: Iterator[str] = iter(source)

    def _next(_prompt: str) -> str:
        return next(iterator)

    return _next


def _overlay_is_stale() -> bool:
    """Compute overlay staleness via the S4 helper (best-effort; never fatal)."""
    try:
        from scripts.utilities.generate_capability_overlay import is_stale

        return is_stale()
    except Exception:  # noqa: BLE001 — staleness check must never break the REPL
        return False


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(prog="python -m app.marcus.cli.marcus_interlocutor")
    parser.add_argument("--trial-id", required=True, type=UUID)
    parser.add_argument("--runs-root", required=False)
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Wire real stdin/stdout for a live operator interlocution session.",
    )
    args = parser.parse_args(argv)
    # Load .env so OPENAI_API_KEY (the live marcus-tier model) is available when
    # the REPL is launched directly as a module.
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass
    runs_root = Path(args.runs_root) if args.runs_root else RUNS_ROOT
    # The live REPL: real input()/print, real make_chat_model at marcus tier.
    run_marcus_interlocutor(
        args.trial_id,
        runs_root=runs_root,
        input_source=input if args.interactive else None,
        output_sink=print,  # noqa: T201
    )
    return 0


__all__ = [
    "ALLOWED_VERBS",
    "FORWARD_VERBS",
    "GroundingContext",
    "GuardRefusal",
    "MarcusInterlocutor",
    "StructuredAction",
    "TranscriptEntry",
    "ValidatedDecision",
    "main",
    "run_marcus_interlocutor",
    "validate_action_against_gate",
]


if __name__ == "__main__":
    raise SystemExit(main())
