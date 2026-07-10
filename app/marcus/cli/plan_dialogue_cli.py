"""Marcus CLI: interactive planning dialogue (Mine 2A).

Thin pre-start REPL that elicits purpose/audience/workflow/gap-fill/LOs,
confirm-before-writes ratification companions + ratified-los.json, and
persists a transcript. Reuses assess/ratify/write — does not rewrite the
planning engine or the in-trial gate interlocutor.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import yaml

from app.marcus.cli.plan_ratify_cli import (
    _GAP_FILL,
    _WORKFLOWS,
    _assess,
    _load_collateral,
    _parse_considered,
)
from app.marcus.lesson_plan.planning_context import load_planning_context
from app.marcus.lesson_plan.planning_ratification import (
    GapFillTradeoff,
    PlanningRatificationError,
    ratify_planning_decision,
    write_ratification_artifacts,
)
from app.marcus.lesson_plan.source_assessment import SourceAssessmentError

InputSource = Callable[[str], str]
OutputSink = Callable[[str], None]


class PlanDialogueError(ValueError):
    """Raised when interactive planning cannot proceed honestly."""


@dataclass
class DialogueTurn:
    """One operator/Marcus exchange in the planning transcript."""

    prompt: str
    operator: str
    marcus: str


@dataclass
class PlanDialogueSession:
    """Scriptable planning dialogue with confirm-before-write."""

    output_dir: Path
    assess_args: argparse.Namespace
    input_source: InputSource
    output_sink: OutputSink
    turns: list[DialogueTurn] = field(default_factory=list)
    purpose: str = ""
    audience: str = ""
    workflow: str = ""
    gap_fill_chosen: str = ""
    gap_fill_considered: str = ""
    gap_fill_rationale: str = ""
    learning_objectives: list[str] = field(default_factory=list)
    collateral_spec: Path | None = None

    def _ask(self, prompt: str, *, allow_empty: bool = False) -> str:
        self.output_sink(prompt)
        try:
            raw = self.input_source(prompt)
        except EOFError as exc:
            raise PlanDialogueError(
                "malformed REPL input: unexpected EOF while eliciting planning fields"
            ) from exc
        text = (raw or "").strip()
        marcus = f"received: {text!r}" if text else "received empty input"
        self.turns.append(DialogueTurn(prompt=prompt, operator=raw or "", marcus=marcus))
        if not text and not allow_empty:
            raise PlanDialogueError(f"malformed REPL input: empty response for {prompt!r}")
        return text

    def _confirm(self, summary: str) -> bool:
        echo = (
            "Confirm write of planning-ratification.json + "
            "ratified-collateral-intent.yaml + ratified-los.json?\n"
            f"{summary}\n"
            "Type yes / y / confirm to write, or no to abort:"
        )
        answer = self._ask(echo, allow_empty=False).lower()
        return answer in {"yes", "y", "confirm", "do it"}

    def elicit(self) -> None:
        """Elicit planning fields via turn loop (scriptable)."""
        self.output_sink("Marcus planning dialogue — elicit purpose → LOs → confirm.")
        self.purpose = self._ask("Purpose (instructional intent):")
        self.audience = self._ask("Audience:")
        workflow = self._ask(
            f"Workflow ({', '.join(_WORKFLOWS)}):"
        )
        if workflow not in _WORKFLOWS:
            raise PlanDialogueError(
                f"malformed REPL input: unknown workflow {workflow!r}; "
                f"allowed={list(_WORKFLOWS)}"
            )
        self.workflow = workflow
        considered = self._ask(
            f"Gap-fill options considered (comma-separated; from {', '.join(_GAP_FILL)}):"
        )
        chosen = self._ask(f"Gap-fill chosen (one of considered):")
        if chosen not in _GAP_FILL:
            raise PlanDialogueError(
                f"malformed REPL input: unknown gap-fill chosen {chosen!r}"
            )
        self.gap_fill_considered = considered
        self.gap_fill_chosen = chosen
        self.gap_fill_rationale = self._ask(
            "Gap-fill rationale (short):",
            allow_empty=True,
        )
        lo_raw = self._ask(
            "Learning objectives (semicolon-separated statements; LO ratification UX):"
        )
        self.learning_objectives = [
            part.strip() for part in lo_raw.split(";") if part.strip()
        ]
        if not self.learning_objectives:
            raise PlanDialogueError(
                "malformed REPL input: at least one learning objective required"
            )

    def write_artifacts(self) -> dict[str, Path]:
        """Assess, ratify, write companions + ratified-los + transcript."""
        assessment = _assess(self.assess_args)
        considered = _parse_considered(self.gap_fill_considered)
        gap_fill = GapFillTradeoff(
            chosen=self.gap_fill_chosen,  # type: ignore[arg-type]
            considered=considered,
            rationale=self.gap_fill_rationale or "",
        )
        collateral = _load_collateral(self.collateral_spec)
        record = ratify_planning_decision(
            assessment=assessment,
            purpose=self.purpose,
            audience=self.audience,
            workflow=self.workflow,  # type: ignore[arg-type]
            gap_fill=gap_fill,
            collateral=collateral,
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = write_ratification_artifacts(record, self.output_dir)
        los_path = self._write_ratified_los()
        transcript_path = self._persist_transcript()
        paths = dict(paths)
        paths["ratified_los"] = los_path
        paths["transcript"] = transcript_path
        return paths

    def _write_ratified_los(self) -> Path:
        payload: dict[str, Any] = {
            "ratified_los": [
                {
                    "objective_id": f"plan-lo-{index:03d}",
                    "statement": statement,
                    "bloom_level": "",
                    "status": "ratified",
                    "actor": "operator",
                    "source": "plan-dialogue",
                }
                for index, statement in enumerate(self.learning_objectives, start=1)
            ]
        }
        path = self.output_dir / "ratified-los.json"
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return path

    def _persist_transcript(self) -> Path:
        lines = [
            "# Marcus-SPOC planning dialogue transcript",
            f"written_at: {datetime.now(UTC).isoformat()}",
            f"output_dir: {self.output_dir}",
            "",
        ]
        for i, turn in enumerate(self.turns, start=1):
            lines.extend(
                [
                    f"## Turn {i}",
                    f"**Prompt:** {turn.prompt}",
                    f"**Operator:** {turn.operator}",
                    f"**Marcus:** {turn.marcus}",
                    "",
                ]
            )
        path = self.output_dir / "marcus-planning-dialogue.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    def run(self) -> dict[str, Path]:
        """Full elicit → confirm → write cycle."""
        self.elicit()
        summary = (
            f"purpose={self.purpose!r}\n"
            f"audience={self.audience!r}\n"
            f"workflow={self.workflow!r}\n"
            f"gap_fill={self.gap_fill_chosen!r}\n"
            f"los={len(self.learning_objectives)}"
        )
        if not self._confirm(summary):
            raise PlanDialogueError("operator aborted before write (confirm declined)")
        return self.write_artifacts()


def build_plan_dialogue_parser(parser: argparse.ArgumentParser) -> None:
    """Attach plan-dialogue flags to ``parser``."""
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory for ratification companions (default: runs/<uuid>/)",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--corpus-dir", type=Path, help="Curated corpus leaf")
    source.add_argument(
        "--course-root",
        type=Path,
        help="Course-source root (requires proposal + module)",
    )
    parser.add_argument("--proposal-path", type=Path)
    parser.add_argument("--module-id")
    parser.add_argument(
        "--operator-focus",
        default="Plan from available source; note gaps honestly.",
    )
    parser.add_argument("--corpus-id", default="")
    parser.add_argument("--collateral-spec", type=Path)
    parser.add_argument(
        "--script",
        type=Path,
        help=(
            "Optional YAML/JSON script of operator answers (non-TTY liveproof). "
            "Keys: purpose, audience, workflow, gap_fill_considered, "
            "gap_fill_chosen, gap_fill_rationale, learning_objectives, confirm"
        ),
    )


def _script_input_source(answers: list[str]) -> InputSource:
    queue = list(answers)

    def _next(_prompt: str) -> str:
        if not queue:
            raise PlanDialogueError("malformed REPL input: script exhausted early")
        return queue.pop(0)

    return _next


def _load_script(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        payload = yaml.safe_load(text)
    else:
        payload = json.loads(text)
    if not isinstance(payload, dict):
        raise PlanDialogueError("plan-dialogue --script must be a JSON/YAML object")
    required = (
        "purpose",
        "audience",
        "workflow",
        "gap_fill_considered",
        "gap_fill_chosen",
        "learning_objectives",
        "confirm",
    )
    missing = [key for key in required if key not in payload]
    if missing:
        raise PlanDialogueError(f"plan-dialogue script missing keys: {missing}")
    los = payload["learning_objectives"]
    if isinstance(los, list):
        lo_line = "; ".join(str(item).strip() for item in los if str(item).strip())
    else:
        lo_line = str(los).strip()
    return [
        str(payload["purpose"]),
        str(payload["audience"]),
        str(payload["workflow"]),
        str(payload["gap_fill_considered"]),
        str(payload["gap_fill_chosen"]),
        str(payload.get("gap_fill_rationale") or ""),
        lo_line,
        str(payload["confirm"]),
    ]


def run_plan_dialogue(
    args: argparse.Namespace,
    *,
    input_source: InputSource | None = None,
    output_sink: OutputSink | None = None,
) -> dict[str, Path]:
    """Run interactive (or scripted) planning dialogue; return written paths."""
    output_dir = args.output_dir
    if output_dir is None:
        output_dir = Path("runs") / str(uuid4())
    output_dir = Path(output_dir)

    if input_source is None:
        if args.script is not None:
            input_source = _script_input_source(_load_script(Path(args.script)))
        else:
            input_source = lambda prompt: input(prompt)  # noqa: E731
    if output_sink is None:
        output_sink = print

    # Reuse plan-ratify assess arg shape (namespace fields).
    assess_ns = argparse.Namespace(
        corpus_dir=args.corpus_dir,
        course_root=args.course_root,
        proposal_path=args.proposal_path,
        module_id=args.module_id,
        operator_focus=args.operator_focus,
        corpus_id=args.corpus_id,
    )
    session = PlanDialogueSession(
        output_dir=output_dir,
        assess_args=assess_ns,
        input_source=input_source,
        output_sink=output_sink,
        collateral_spec=args.collateral_spec,
    )
    return session.run()


def plan_dialogue_cli(args: argparse.Namespace) -> int:
    """CLI entry: exit 0 on success, 2 on validation/dialogue failure."""
    try:
        paths = run_plan_dialogue(args)
        ctx = load_planning_context(paths["companion"].parent)
        if ctx is None or not ctx.has_framing():
            raise PlanDialogueError(
                "post-write load_planning_context missing framing (consumer proof failed)"
            )
    except (
        PlanDialogueError,
        PlanningRatificationError,
        SourceAssessmentError,
        ValueError,
        OSError,
        json.JSONDecodeError,
        yaml.YAMLError,
    ) as exc:
        print(f"plan-dialogue failed: {exc}", file=sys.stderr)
        return 2
    print(f"wrote companion: {paths['companion']}")
    print(f"wrote s8_intent: {paths['s8_intent']}")
    print(f"wrote ratified_los: {paths['ratified_los']}")
    print(f"wrote transcript: {paths['transcript']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="plan-dialogue")
    build_plan_dialogue_parser(parser)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    return plan_dialogue_cli(args)


__all__ = [
    "PlanDialogueError",
    "PlanDialogueSession",
    "build_plan_dialogue_parser",
    "build_parser",
    "main",
    "plan_dialogue_cli",
    "run_plan_dialogue",
]
