from __future__ import annotations

import argparse
import sys

from app.marcus.cli.adhoc_cli import adhoc_ask_cli, build_adhoc_parser
from app.marcus.cli.gate_cli import main as gate_main
from app.marcus.cli.plan_ratify_cli import (
    build_plan_ratify_parser,
    plan_ratify_cli,
)
from app.marcus.cli.trial import (
    build_trial_parser,
    recover_trial_cli,
    resume_trial_cli,
    start_trial_cli,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="app.marcus.cli")
    subparsers = parser.add_subparsers(dest="command")

    trial = subparsers.add_parser("trial")
    build_trial_parser(trial)

    ask = subparsers.add_parser("ask")
    build_adhoc_parser(ask)

    plan_ratify = subparsers.add_parser(
        "plan-ratify",
        help=(
            "Assess source and ratify purpose/audience/workflow/gap-fill; "
            "write planning-ratification.json + ratified-collateral-intent.yaml"
        ),
    )
    build_plan_ratify_parser(plan_ratify)

    return parser


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if argv and argv[0] == "gate":
        return gate_main(argv[1:])
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "ask":
        return adhoc_ask_cli(args)
    if args.command == "plan-ratify":
        return plan_ratify_cli(args)
    if args.command == "trial" and args.trial_command == "start":
        return start_trial_cli(args)
    if args.command == "trial" and args.trial_command == "resume":
        return resume_trial_cli(args)
    if args.command == "trial" and args.trial_command == "recover":
        return recover_trial_cli(args)
    parser.error("a command is required")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
