"""CLI bridge for one-shot Marcus ad-hoc asks."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

from app.runtime.cascade_config import normalize_agent_name
from app.marcus.facade import get_facade


def _load_env_if_available() -> None:
    try:
        from scripts.utilities.env_loader import load_env

        load_env()
    except (FileNotFoundError, ImportError):
        pass


def _parse_cascade_override(raw: str | None) -> str | None:
    if raw is None:
        return None
    if "=" not in raw:
        raise ValueError("--cascade-override must use <agent>=<model>")
    agent, model = raw.split("=", 1)
    if normalize_agent_name(agent) != "marcus":
        raise ValueError("ad-hoc ask only invokes Marcus; override agent must be marcus")
    model = model.strip()
    if not model:
        raise ValueError("--cascade-override model must not be empty")
    return model


def run_adhoc_ask(payload: dict[str, Any]) -> dict[str, Any]:
    _load_env_if_available()
    override = _parse_cascade_override(payload.get("cascade_override"))
    response = get_facade().ask(
        payload["prompt"],
        cascade_override=override,
        max_tokens=payload.get("max_tokens"),
        trace=payload.get("trace", True),
    )
    return {
        "status": "ok",
        "response": response.model_dump(mode="json"),
        "transport_kind": "cli",
    }


def adhoc_ask_cli(args: argparse.Namespace) -> int:
    payload = {
        "prompt": args.prompt,
        "cascade_override": args.cascade_override,
        "max_tokens": args.max_tokens,
        "trace": not args.no_trace,
    }
    if not os.getenv("OPENAI_API_KEY"):
        _load_env_if_available()
    if not os.getenv("OPENAI_API_KEY"):
        skipped = {
            "status": "skipped",
            "reason": "OPENAI_API_KEY is required for Marcus ad-hoc ask",
            "transport_kind": "cli",
        }
        if args.json:
            print(json.dumps(skipped, sort_keys=True))
        else:
            print(f"SKIP: {skipped['reason']}", file=sys.stderr)
        return 0

    result = run_adhoc_ask(payload)
    response = result["response"]
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(response["text"])
        tokens = response["tokens"]
        print(
            "cost_usd="
            f"{response['cost_usd']:.8f} model={response['model_used']} "
            f"input_tokens={tokens['input_tokens']} "
            f"output_tokens={tokens['output_tokens']}",
            file=sys.stderr,
        )
    return 0


def build_adhoc_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("prompt")
    parser.add_argument("--cascade-override", required=False)
    parser.add_argument("--max-tokens", required=False, type=int)
    parser.add_argument("--no-trace", action="store_true")
    parser.add_argument("--json", action="store_true")


__all__ = ["adhoc_ask_cli", "build_adhoc_parser", "run_adhoc_ask"]
