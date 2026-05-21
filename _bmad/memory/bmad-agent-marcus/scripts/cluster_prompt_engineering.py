"""
Cluster-aware prompt engineering for Story 21-2.

Deterministically renders prompts per cluster using declarative config
(`state/config/prompting.yaml`), applies safety/PII guardrails, binds
visual/interstitial constraints, and emits a stable prompt hash for audit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, TypedDict

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

CONFIG_PATH = Path("state/config/prompting.yaml")


class PromptEngineeringError(ValueError):
    """Structured prompt engineering failure with a machine-readable code."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


class PromptResult(TypedDict):
    prompt_id: str
    prompt_text: str
    audit: Dict[str, Any]


def _require(cond: bool, code: str, msg: str) -> None:
    if not cond:
        raise PromptEngineeringError(code, msg)


def load_prompt_config(path: Path = CONFIG_PATH) -> Dict[str, Any]:
    if yaml is None:  # pragma: no cover
        raise PromptEngineeringError("config_missing", "pyyaml is required")
    if not path.is_file():
        raise PromptEngineeringError("config_missing", f"prompting config not found: {path}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise PromptEngineeringError("config_missing", f"invalid prompting config: {exc}") from exc
    if not isinstance(raw, dict):
        raise PromptEngineeringError("config_missing", "prompting config must be a mapping")
    return raw


def _select_template(config: Dict[str, Any], cluster: Dict[str, Any]) -> Dict[str, Any]:
    templates = config.get("templates") or {}
    slides = cluster.get("slides") or cluster.get("segments") or []
    size = len(slides)
    key = "large" if size >= 8 else "small"
    tmpl = templates.get(key) or templates.get("default")
    _require(tmpl is not None, "config_missing", f"template missing for key: {key}")
    return tmpl


def _approx_tokens(text: str) -> int:
    return len(text.split())


def _check_safety(config: Dict[str, Any], cluster: Dict[str, Any]) -> None:
    safety = config.get("safety") or {}
    blocked: List[str] = safety.get("blocked_terms") or []
    haystack_parts: List[str] = []
    for field in ("goal", "objective"):
        val = cluster.get(field)
        if isinstance(val, str):
            haystack_parts.append(val)
    intents = cluster.get("intents") or []
    haystack_parts.extend([i for i in intents if isinstance(i, str)])
    haystack = " ".join(haystack_parts).lower()
    for term in blocked:
        if term.lower() in haystack:
            raise PromptEngineeringError("safety_violation", f"blocked term detected: {term}")


def _render_constraints(cluster: Dict[str, Any]) -> str:
    constraints = cluster.get("constraints") or {}
    visual = constraints.get("visual_constraints")
    if visual:
        parts = []
        if isinstance(visual, dict):
            for k, v in sorted(visual.items()):
                parts.append(f"{k}: {v}")
        elif isinstance(visual, list):
            parts.extend([str(v) for v in visual])
        else:
            parts.append(str(visual))
        return "; ".join(parts)
    return "none (visual constraints not provided)"


def render_prompt(
    cluster: Dict[str, Any],
    *,
    config: Dict[str, Any] | None = None,
    seed: str | None = None,
) -> PromptResult:
    cfg = config or load_prompt_config()

    # Required fields
    cluster_id = cluster.get("cluster_id")
    intents = cluster.get("intents")
    goal = cluster.get("goal") or cluster.get("objective")
    _require(isinstance(cluster_id, str) and cluster_id.strip(), "missing_required_field", "cluster_id required")
    _require(isinstance(intents, list) and intents, "missing_required_field", "intents list required")
    _require(isinstance(goal, str) and goal.strip(), "missing_required_field", "goal/objective required")

    # Safety checks
    _check_safety(cfg, cluster)

    tmpl = _select_template(cfg, cluster)
    tmpl_body = tmpl.get("body", "")
    tmpl_version = tmpl.get("version", "v1")

    safety_clauses = cfg.get("safety", {}).get("clauses") or []
    safety_section = " | ".join(safety_clauses) if safety_clauses else "stay within cluster scope; no PII"

    constraints_section = _render_constraints(cluster)
    intents_text = "; ".join([str(i) for i in intents])

    prompt_text = tmpl_body.format(
        cluster_id=cluster_id,
        goal=goal,
        intents=intents_text,
        constraints_section=constraints_section,
        safety_section=safety_section,
    ).strip()

    budget_cfg = cfg.get("token_budget", {}) or {}
    max_tokens = int(budget_cfg.get("max_per_prompt", 1000))
    used_tokens = _approx_tokens(prompt_text)
    if used_tokens > max_tokens:
        raise PromptEngineeringError(
            "prompt_over_budget", f"prompt uses {used_tokens} tokens; budget is {max_tokens}"
        )

    hash_source = f"{tmpl_version}|{cluster_id}|{prompt_text}"
    if seed:
        hash_source = f"{seed}|{hash_source}"
    algo = (cfg.get("hashing", {}) or {}).get("algorithm", "sha256")
    h = hashlib.new(algo)
    h.update(hash_source.encode("utf-8"))
    prompt_id = h.hexdigest()

    audit: Dict[str, Any] = {
        "template_version": tmpl_version,
        "constraints_applied": constraints_section != "none (visual constraints not provided)",
        "token_budget_used": used_tokens,
        "token_budget_max": max_tokens,
        "hash_algorithm": algo,
    }
    return {"prompt_id": prompt_id, "prompt_text": prompt_text, "audit": audit}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render a cluster-aware prompt")
    parser.add_argument("--cluster", type=Path, required=True, help="Path to cluster JSON/YAML payload")
    parser.add_argument("--config", type=Path, default=CONFIG_PATH, help="Path to prompting config YAML")
    parser.add_argument("--seed", type=str, default=None, help="Optional determinism seed")
    args = parser.parse_args(argv)

    try:
        if args.cluster.suffix.lower() in {".yaml", ".yml"}:
            raw = yaml.safe_load(args.cluster.read_text(encoding="utf-8"))
        else:
            raw = json.loads(args.cluster.read_text(encoding="utf-8"))
        cfg = load_prompt_config(args.config)
        result = render_prompt(raw, config=cfg, seed=args.seed)
        print(
            json.dumps(
                {
                    "status": "pass",
                    "prompt_id": result["prompt_id"],
                    "audit": result["audit"],
                    "prompt": result["prompt_text"],
                },
                indent=2,
            )
        )
        return 0
    except PromptEngineeringError as exc:
        print(json.dumps({"status": "fail", "code": exc.code, "message": str(exc)}, indent=2))
        return 1
    except Exception as exc:  # pragma: no cover
        print(json.dumps({"status": "fail", "code": "unexpected_error", "message": str(exc)}, indent=2))
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
