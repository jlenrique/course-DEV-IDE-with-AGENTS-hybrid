from __future__ import annotations

import argparse
import sys

from app.marcus.cli.gate_cli import main as gate_main
from app.marcus.cli.trial import build_trial_parser, resume_trial_cli, start_trial_cli


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="app.marcus.cli")
    subparsers = parser.add_subparsers(dest="command")

    trial = subparsers.add_parser("trial")
    build_trial_parser(trial)

    return parser


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if argv and argv[0] == "gate":
        return gate_main(argv[1:])
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "trial" and args.trial_command == "start":
        return start_trial_cli(args)
    if args.command == "trial" and args.trial_command == "resume":
        return resume_trial_cli(args)
    parser.error("a command is required")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
