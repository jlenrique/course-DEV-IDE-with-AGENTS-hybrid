"""Ad-hoc mode persistence guardrail.

Enforces fail-closed behavior for operations that would otherwise persist
institutional production state while run mode is ad-hoc.
"""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
from typing import Any

try:
    from scripts.utilities.file_helpers import project_root
except ModuleNotFoundError:
    try:
        from file_helpers import project_root  # type: ignore[no-redef]
    except ModuleNotFoundError:
        helper_path = Path(__file__).resolve().parent / "file_helpers.py"
        spec = importlib.util.spec_from_file_location("file_helpers_local", helper_path)
        if not spec or not spec.loader:
            raise
        _module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_module)
        project_root = _module.project_root

_BLOCKED_IN_AD_HOC = {
    "production_run_db",
    "coordination_audit_db",
    "quality_gate_db",
    "observability_db",
    "run_context_config",
    "durable_sidecar_write",
    "course_progress_rollup",
    "durable_memory_patterns",
    "durable_memory_chronology",
    "durable_memory_preferences",
}

_ALLOWED_IN_AD_HOC = {
    "transient_session_log",
    "transient_ad_hoc_run",
    "transient_run_context",
    "transient_observability",
}

_MODE_ALIASES = {
    "tracked": "default",
}


def _normalize_mode(mode: str | None) -> str | None:
    """Normalize mode tokens so aliases resolve consistently."""
    if mode is None:
        return None
    token = str(mode).strip().lower()
    token = _MODE_ALIASES.get(token, token)
    if token in {"default", "ad-hoc"}:
        return token
    return None


def _ambiguous_mode_policy() -> str:
    """Resolve ambiguity policy for missing/corrupt mode state.

    `strict` fails closed to ad-hoc mode.
    `lenient` preserves legacy fail-open behavior to default mode.
    """
    value = str(os.getenv("RUN_MODE_AMBIGUOUS", "lenient")).strip().lower()
    return "strict" if value == "strict" else "lenient"


def _resolve_run_mode_details(explicit_mode: str | None = None) -> dict[str, Any]:
    """Resolve run mode with metadata about fallback and ambiguity handling."""
    normalized_explicit = _normalize_mode(explicit_mode)
    if normalized_explicit in {"default", "ad-hoc"}:
        return {
            "mode": normalized_explicit,
            "source": "explicit",
            "ambiguous": False,
            "policy": _ambiguous_mode_policy(),
        }

    policy = _ambiguous_mode_policy()
    path = mode_state_path()
    if not path.exists():
        return {
            "mode": "ad-hoc" if policy == "strict" else "default",
            "source": "missing_state",
            "ambiguous": True,
            "policy": policy,
        }

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {
            "mode": "ad-hoc" if policy == "strict" else "default",
            "source": "invalid_state",
            "ambiguous": True,
            "policy": policy,
        }

    mode = _normalize_mode(str(data.get("mode", "default")))
    if mode not in {"default", "ad-hoc"}:
        return {
            "mode": "ad-hoc" if policy == "strict" else "default",
            "source": "unknown_state_mode",
            "ambiguous": True,
            "policy": policy,
        }

    return {
        "mode": mode,
        "source": "mode_state",
        "ambiguous": False,
        "policy": policy,
    }


def mode_state_path() -> Path:
    """Return the canonical mode-state file path."""
    return project_root() / "state" / "runtime" / "mode_state.json"


def resolve_run_mode(explicit_mode: str | None = None) -> str:
    """Resolve run mode from explicit input or mode_state.json fallback."""
    return str(_resolve_run_mode_details(explicit_mode)["mode"])


def enforce_ad_hoc_boundary(operation: str, run_mode: str | None = None) -> dict[str, Any]:
    """Check whether a persistence operation is allowed in current run mode."""
    details = _resolve_run_mode_details(run_mode)
    mode = str(details["mode"])
    ambiguous = bool(details["ambiguous"])
    strict_ambiguity = ambiguous and details["policy"] == "strict"

    if mode != "ad-hoc":
        return {
            "allowed": True,
            "run_mode": mode,
            "code": "ALLOWED_DEFAULT_MODE",
            "reason": "default mode allows durable persistence",
            "mode_source": details["source"],
            "ambiguity_policy": details["policy"],
        }

    if operation in _ALLOWED_IN_AD_HOC:
        return {
            "allowed": True,
            "run_mode": mode,
            "code": (
                "ALLOWED_AD_HOC_TRANSIENT_STRICT_AMBIGUOUS"
                if strict_ambiguity
                else "ALLOWED_AD_HOC_TRANSIENT"
            ),
            "reason": (
                "ad-hoc mode permits transient-only operations; strict ambiguity policy applied"
                if strict_ambiguity
                else "ad-hoc mode permits transient-only operations"
            ),
            "mode_source": details["source"],
            "ambiguity_policy": details["policy"],
        }

    if operation in _BLOCKED_IN_AD_HOC:
        return {
            "allowed": False,
            "run_mode": mode,
            "code": "NOOP_AD_HOC_AMBIGUOUS_MODE" if strict_ambiguity else "NOOP_AD_HOC",
            "reason": (
                "Ad-hoc mode: production ledger writes forbidden; strict ambiguity policy applied"
                if strict_ambiguity
                else "Ad-hoc mode: production ledger writes forbidden"
            ),
            "mode_source": details["source"],
            "ambiguity_policy": details["policy"],
        }

    return {
        "allowed": False,
        "run_mode": mode,
        "code": "NOOP_AD_HOC_UNKNOWN_OPERATION",
        "reason": f"Ad-hoc mode: operation '{operation}' not whitelisted",
        "mode_source": details["source"],
        "ambiguity_policy": details["policy"],
    }
