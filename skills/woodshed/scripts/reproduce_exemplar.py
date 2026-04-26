"""Reproduce an exemplar using its reproduction-spec.yaml via the tool's API client.

Produces a detailed run-log.yaml capturing exact API calls, prompts, MCP
interactions, response details, and resource usage. All output artifacts are
retained regardless of pass/fail outcome.

Usage:
    python reproduce_exemplar.py <tool> <exemplar_id> [--dry-run]

Example:
    python reproduce_exemplar.py gamma 001-simple-lecture-deck
"""

import argparse
import importlib
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[3]
EXEMPLARS_DIR = PROJECT_ROOT / "resources" / "exemplars"
API_CLIENTS_DIR = PROJECT_ROOT / "scripts" / "api_clients"

TOOL_CLIENT_MAP = {
    "gamma": "gamma_client",
    "elevenlabs": "elevenlabs_client",
    "canvas": "canvas_client",
    "qualtrics": "qualtrics_client",
}

CIRCUIT_BREAKER_DEFAULTS = {
    "max_attempts_per_session": 3,
    "max_total_attempts": 7,
    "max_consecutive_no_improvement": 2,
}


def load_project_env() -> None:
    """Load PROJECT_ROOT/.env keys into process env when missing.

    This mirrors test harness behavior so woodshed runs can use configured
    API credentials without requiring users to export variables manually.
    """
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key and value and key not in os.environ:
            os.environ[key] = value


def load_reproduction_spec(tool: str, exemplar_id: str) -> dict:
    """Load the reproduction spec for an exemplar."""
    spec_path = EXEMPLARS_DIR / tool / exemplar_id / "reproduction-spec.yaml"
    if not spec_path.exists():
        raise FileNotFoundError(
            f"No reproduction-spec.yaml found. Run study_exemplar.py first "
            f"and have the agent draft the spec: {spec_path}"
        )
    return yaml.safe_load(spec_path.read_text(encoding="utf-8"))


def count_previous_attempts(tool: str, exemplar_id: str) -> int:
    """Count total reproduction attempts across all sessions."""
    reproductions_dir = EXEMPLARS_DIR / tool / exemplar_id / "reproductions"
    if not reproductions_dir.exists():
        return 0
    return sum(1 for d in reproductions_dir.iterdir() if d.is_dir())


def check_circuit_breaker(
    tool: str, exemplar_id: str, session_attempt: int
) -> dict | None:
    """Check if circuit breaker limits have been reached.

    Returns None if OK to proceed, or a dict describing which limit was hit.
    """
    total = count_previous_attempts(tool, exemplar_id)
    limits = CIRCUIT_BREAKER_DEFAULTS

    if session_attempt > limits["max_attempts_per_session"]:
        return {
            "limit": "max_attempts_per_session",
            "value": limits["max_attempts_per_session"],
            "actual": session_attempt,
            "message": (
                f"Session attempt limit reached ({limits['max_attempts_per_session']}). "
                "Agent must stop and produce failure report if exemplar is not mastered."
            ),
        }

    if total >= limits["max_total_attempts"]:
        return {
            "limit": "max_total_attempts",
            "value": limits["max_total_attempts"],
            "actual": total,
            "message": (
                f"Total attempt limit reached ({limits['max_total_attempts']} across all sessions). "
                "Agent must produce failure report."
            ),
        }

    return None


def create_attempt_dir(tool: str, exemplar_id: str) -> Path:
    """Create a timestamped directory for this reproduction attempt."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    attempt_dir = (
        EXEMPLARS_DIR / tool / exemplar_id / "reproductions" / timestamp
    )
    output_dir = attempt_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return attempt_dir


def load_api_client(tool: str):
    """Dynamically load the API client module for the given tool."""
    client_module_name = TOOL_CLIENT_MAP.get(tool)
    if not client_module_name:
        raise ValueError(
            f"No API client mapping for tool '{tool}'. "
            f"Known tools: {list(TOOL_CLIENT_MAP.keys())}"
        )

    # Support both direct api_clients imports and scripts.api_clients imports.
    scripts_root = API_CLIENTS_DIR.parent
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    if str(scripts_root) not in sys.path:
        sys.path.insert(0, str(scripts_root))

    try:
        return importlib.import_module(
            f"scripts.api_clients.{client_module_name}"
        )
    except ModuleNotFoundError:
        return importlib.import_module(f"api_clients.{client_module_name}")


def build_run_log(
    tool: str,
    exemplar_id: str,
    spec: dict,
    attempt_dir: Path,
    session_attempt: int,
    cumulative_attempts: int,
) -> dict:
    """Build the initial run-log structure before API execution."""
    exemplar_dir = EXEMPLARS_DIR / tool / exemplar_id
    source_dir = exemplar_dir / "source"
    source_artifacts = []
    if source_dir.exists():
        source_artifacts = [f.name for f in sorted(source_dir.iterdir())]

    return {
        "exemplar_id": exemplar_id,
        "tool": tool,
        "agent": f"bmad-agent-{tool}",
        "timestamp": datetime.now().isoformat(),
        "attempt_number": cumulative_attempts + 1,
        "source_exemplar": {
            "brief_path": str(exemplar_dir / "brief.md"),
            "source_artifacts": source_artifacts,
            "reproduction_spec_path": str(exemplar_dir / "reproduction-spec.yaml"),
        },
        "api_interaction": {
            "method": spec.get("api_method", ""),
            "client": TOOL_CLIENT_MAP.get(tool, "unknown") + ".py",
            "endpoint": None,
            "request_payload": spec.get("parameters", {}),
            "prompt_text": spec.get("parameters", {}).get("additional_instructions")
                or spec.get("parameters", {}).get("text")
                or None,
            "mcp_tool_used": None,
            "mcp_arguments": None,
            "response_status": None,
            "response_summary": None,
            "latency_ms": None,
            "tokens_used": None,
        },
        "output": {
            "artifacts_saved": [],
            "output_type": None,
            "output_format": None,
        },
        "comparison": {
            "rubric_used": "comparison-rubric-template.md",
            "scores": None,
            "overall_result": None,
            "conclusion": None,
        },
        "resources": {
            "session_attempt_number": session_attempt,
            "cumulative_attempts": cumulative_attempts + 1,
            "estimated_token_cost": None,
        },
    }


def reproduce(
    tool: str,
    exemplar_id: str,
    dry_run: bool = False,
    session_attempt: int = 1,
) -> dict:
    """Execute a reproduction attempt with detailed run logging.

    Args:
        tool: Tool name (gamma, elevenlabs, etc.)
        exemplar_id: Exemplar directory name
        dry_run: If True, load spec but don't execute API call
        session_attempt: Which attempt this is within the current session

    Returns:
        Dict with attempt metadata, output path, run log path, and result.
    """
    load_project_env()

    breaker = check_circuit_breaker(tool, exemplar_id, session_attempt)
    if breaker:
        return {
            "status": "circuit_breaker_tripped",
            "circuit_breaker": breaker,
            "message": breaker["message"],
        }

    spec = load_reproduction_spec(tool, exemplar_id)
    cumulative = count_previous_attempts(tool, exemplar_id)
    attempt_dir = create_attempt_dir(tool, exemplar_id)

    spec_copy_path = attempt_dir / "reproduction-spec-used.yaml"
    spec_copy_path.write_text(
        yaml.dump(spec, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )

    run_log = build_run_log(
        tool, exemplar_id, spec, attempt_dir, session_attempt, cumulative
    )

    if dry_run:
        run_log["api_interaction"]["response_status"] = "dry_run"
        run_log["api_interaction"]["response_summary"] = (
            "Spec loaded and validated. No API call executed."
        )
        status = "dry_run"
    else:
        start_time = time.time()
        try:
            client_module = load_api_client(tool)
            api_method = spec.get("api_method", "")
            parameters = spec.get("parameters", {})

            if hasattr(client_module, api_method):
                api_func = getattr(client_module, api_method)
                api_result = api_func(**parameters)
            else:
                api_result = {
                    "error": f"Method '{api_method}' not found in {tool} client"
                }

            elapsed_ms = int((time.time() - start_time) * 1000)

            output_path = attempt_dir / "output" / "api_response.json"
            output_path.write_text(
                json.dumps(api_result, indent=2, default=str),
                encoding="utf-8",
            )

            run_log["api_interaction"]["response_status"] = 200
            run_log["api_interaction"]["response_summary"] = (
                str(api_result)[:500] if api_result else "Empty response"
            )
            run_log["api_interaction"]["latency_ms"] = elapsed_ms
            run_log["output"]["artifacts_saved"] = [str(output_path)]
            run_log["output"]["output_type"] = spec.get(
                "expected_outputs", [{}]
            )[0].get("type") if spec.get("expected_outputs") else None
            run_log["output"]["output_format"] = spec.get(
                "expected_outputs", [{}]
            )[0].get("format") if spec.get("expected_outputs") else None
            status = "completed"

        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            run_log["api_interaction"]["response_status"] = "error"
            run_log["api_interaction"]["response_summary"] = str(e)
            run_log["api_interaction"]["latency_ms"] = elapsed_ms
            status = "error"

    run_log_path = attempt_dir / "run-log.yaml"
    run_log_path.write_text(
        yaml.dump(run_log, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )

    return {
        "status": status,
        "attempt_dir": str(attempt_dir),
        "run_log_path": str(run_log_path),
        "session_attempt": session_attempt,
        "cumulative_attempts": cumulative + 1,
        "circuit_breaker_remaining": {
            "session": CIRCUIT_BREAKER_DEFAULTS["max_attempts_per_session"] - session_attempt,
            "total": CIRCUIT_BREAKER_DEFAULTS["max_total_attempts"] - (cumulative + 1),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reproduce an exemplar via API with detailed run logging."
    )
    parser.add_argument("tool", help="Tool name (gamma, elevenlabs, canvas, etc.)")
    parser.add_argument("exemplar_id", help="Exemplar directory name")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Validate spec without executing API call",
    )
    parser.add_argument(
        "--session-attempt", type=int, default=1,
        help="Which attempt this is within the current session (for circuit breaker)",
    )
    args = parser.parse_args()

    try:
        result = reproduce(
            args.tool, args.exemplar_id,
            dry_run=args.dry_run,
            session_attempt=args.session_attempt,
        )
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(yaml.dump(result, default_flow_style=False, sort_keys=False))


if __name__ == "__main__":
    main()
