"""Marcus CLI: assess source → ratify planning decision → write artifacts.

Thin adapter over ``source_assessment`` + ``planning_ratification``. Does not
implement a planning workflow engine or rewrite the SPOC REPL.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

import yaml

from app.marcus.course_source.input_bundle import build_lesson_planning_input_bundle
from app.marcus.lesson_plan.collateral_spec import CollateralSpec
from app.marcus.lesson_plan.planning_ratification import (
    GapFillChoice,
    GapFillTradeoff,
    PlanningRatificationError,
    ratify_planning_decision,
    write_ratification_artifacts,
)
from app.marcus.lesson_plan.source_assessment import (
    SourceAssessmentError,
    assess_from_corpus_dir,
    assess_from_input_bundle,
)

_WORKFLOWS: tuple[str, ...] = (
    "narrated-deck",
    "narrated-deck-with-motion",
    "narrated-deck-with-workbook",
)
_GAP_FILL: tuple[str, ...] = (
    "synthesize",
    "wait",
    "ask_operator",
    "ask_sme",
    "lighter_collateral",
    "none",
)


def build_plan_ratify_parser(parser: argparse.ArgumentParser) -> None:
    """Attach plan-ratify flags to ``parser``."""
    parser.add_argument("--purpose", required=True, help="Instructional purpose")
    parser.add_argument("--audience", required=True, help="Target audience")
    parser.add_argument(
        "--workflow",
        required=True,
        choices=_WORKFLOWS,
        help="Production workflow / catalog bundle id",
    )
    parser.add_argument(
        "--gap-fill-chosen",
        required=True,
        choices=_GAP_FILL,
        help="Selected gap-fill disposition",
    )
    parser.add_argument(
        "--gap-fill-considered",
        required=True,
        help="Comma-separated gap-fill options considered (must include chosen)",
    )
    parser.add_argument(
        "--gap-fill-rationale",
        default="",
        help="Short rationale for the gap-fill choice",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Directory for planning-ratification.json + intent YAML",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--corpus-dir",
        type=Path,
        help="Curated corpus leaf (rich path)",
    )
    source.add_argument(
        "--course-root",
        type=Path,
        help="Course-source root (thin path; requires proposal + module)",
    )
    parser.add_argument(
        "--proposal-path",
        type=Path,
        help="Module metadata proposal YAML (required with --course-root)",
    )
    parser.add_argument(
        "--module-id",
        help="Module id (required with --course-root)",
    )
    parser.add_argument(
        "--operator-focus",
        default="Plan from available source; note gaps honestly.",
        help="Operator focus string for input-bundle assessment",
    )
    parser.add_argument(
        "--corpus-id",
        default="",
        help="Optional corpus id override for --corpus-dir",
    )
    parser.add_argument(
        "--collateral-spec",
        type=Path,
        help="JSON/YAML CollateralSpec (required for workbook workflow)",
    )


def _parse_considered(raw: str) -> tuple[GapFillChoice, ...]:
    parts = tuple(p.strip() for p in raw.split(",") if p.strip())
    if not parts:
        raise PlanningRatificationError(
            "gap-fill-considered must list at least one option"
        )
    for part in parts:
        if part not in _GAP_FILL:
            raise PlanningRatificationError(
                f"unknown gap-fill option in considered: {part!r}"
            )
    return parts  # type: ignore[return-value]


def _load_collateral(path: Path | None) -> CollateralSpec | None:
    if path is None:
        return None
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        payload = yaml.safe_load(text)
    else:
        payload = json.loads(text)
    if not isinstance(payload, dict):
        raise PlanningRatificationError("collateral-spec must be a JSON/YAML object")
    return CollateralSpec.model_validate(payload)


def _assess(args: argparse.Namespace):
    if args.corpus_dir is not None:
        corpus_id = args.corpus_id or args.corpus_dir.name
        return assess_from_corpus_dir(args.corpus_dir, corpus_id=corpus_id)
    if args.course_root is None:
        raise PlanningRatificationError("assessment source required")
    if args.proposal_path is None or not args.module_id:
        raise PlanningRatificationError(
            "--course-root requires --proposal-path and --module-id"
        )
    bundle = build_lesson_planning_input_bundle(
        course_root=args.course_root,
        proposal_path=args.proposal_path,
        module_id=args.module_id,
        operator_focus=args.operator_focus,
    )
    return assess_from_input_bundle(bundle)


def run_plan_ratify(args: argparse.Namespace) -> dict[str, Path]:
    """Assess, ratify, and write artifacts. Raises on validation failure."""
    assessment = _assess(args)
    considered = _parse_considered(args.gap_fill_considered)
    gap_fill = GapFillTradeoff(
        chosen=args.gap_fill_chosen,  # type: ignore[arg-type]
        considered=considered,
        rationale=args.gap_fill_rationale or "",
    )
    collateral = _load_collateral(args.collateral_spec)
    record = ratify_planning_decision(
        assessment=assessment,
        purpose=args.purpose,
        audience=args.audience,
        workflow=args.workflow,  # type: ignore[arg-type]
        gap_fill=gap_fill,
        collateral=collateral,
    )
    return write_ratification_artifacts(record, Path(args.output_dir))


def plan_ratify_cli(args: argparse.Namespace) -> int:
    """CLI entry: exit 0 on success, 2 on validation/assessment failure."""
    try:
        paths = run_plan_ratify(args)
    except (
        PlanningRatificationError,
        SourceAssessmentError,
        ValueError,
        OSError,
        json.JSONDecodeError,
        yaml.YAMLError,
    ) as exc:
        print(f"plan-ratify failed: {exc}", file=sys.stderr)
        return 2
    print(f"wrote companion: {paths['companion']}")
    print(f"wrote s8_intent: {paths['s8_intent']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="plan-ratify")
    build_plan_ratify_parser(parser)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    return plan_ratify_cli(args)


__all__ = [
    "build_plan_ratify_parser",
    "build_parser",
    "main",
    "plan_ratify_cli",
    "run_plan_ratify",
]
