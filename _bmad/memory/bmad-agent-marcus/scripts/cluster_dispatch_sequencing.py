"""
Cluster Dispatch Sequencing (Story 21-3).

Creates deterministic dispatch plans for cluster prompts using declarative policy
(`state/config/dispatch.yaml`). Supports ordering, batching, retry/backoff, and
cycle detection. Produces a plan hash for audit/telemetry.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

CONFIG_PATH = Path("state/config/dispatch.yaml")


class DispatchPlanError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def load_dispatch_config(path: Path = CONFIG_PATH) -> Dict[str, Any]:
    if yaml is None:  # pragma: no cover
        raise DispatchPlanError("config_missing", "pyyaml is required")
    if not path.is_file():
        raise DispatchPlanError("config_missing", f"dispatch config not found: {path}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise DispatchPlanError("config_missing", f"invalid dispatch config: {exc}") from exc
    if not isinstance(raw, dict):
        raise DispatchPlanError("config_missing", "dispatch config must be a mapping")
    return raw


def _topo_sort(nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Build graph
    indeg: Dict[str, int] = {}
    edges: Dict[str, Set[str]] = defaultdict(set)
    node_by_id: Dict[str, Dict[str, Any]] = {}
    for n in nodes:
        cid = str(n.get("cluster_id"))
        node_by_id[cid] = n
        indeg.setdefault(cid, 0)
        for dep in n.get("depends_on", []) or []:
            dep_id = str(dep)
            edges[dep_id].add(cid)
            indeg[cid] = indeg.get(cid, 0) + 1
            indeg.setdefault(dep_id, 0)

    q = deque([cid for cid, deg in indeg.items() if deg == 0])
    ordered: List[str] = []
    while q:
        cid = q.popleft()
        ordered.append(cid)
        for nxt in edges.get(cid, []):
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                q.append(nxt)

    if len(ordered) != len(indeg):
        raise DispatchPlanError("invalid_policy", "cycle detected in dependencies")

    # Return nodes in topo order; missing nodes are ignored (already validated)
    return [node_by_id[c] for c in ordered if c in node_by_id]


def _order_nodes(nodes: List[Dict[str, Any]], policy: Dict[str, Any]) -> List[Dict[str, Any]]:
    ordering = policy.get("ordering", "priority_size_id")
    if ordering == "manifest":
        return nodes
    # Default: priority desc, size desc, id tiebreak
    return sorted(
        nodes,
        key=lambda n: (
            -int(n.get("priority", 0)),
            -int(n.get("size", 0)),
            str(n.get("cluster_id")),
        ),
    )


def _batch(nodes: List[Dict[str, Any]], batch_size: int) -> List[List[Dict[str, Any]]]:
    if batch_size <= 0:
        batch_size = 1
    return [nodes[i : i + batch_size] for i in range(0, len(nodes), batch_size)]


def _plan_hash(plan: Dict[str, Any], algo: str = "sha256") -> str:
    h = hashlib.new(algo)
    h.update(json.dumps(plan, sort_keys=True).encode("utf-8"))
    return h.hexdigest()


def generate_dispatch_plan(
    clusters: List[Dict[str, Any]],
    *,
    config: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    cfg = config or load_dispatch_config()
    policy = cfg.get("policy") or {}
    batch_size = int(policy.get("batch_size", 1))
    hash_algo = (cfg.get("hashing", {}) or {}).get("algorithm", "sha256")

    # Validate required fields
    for c in clusters:
        if not c.get("cluster_id"):
            raise DispatchPlanError("missing_required_field", "cluster_id required on all clusters")

    # Topological order to respect dependencies
    ordered = _topo_sort(clusters)
    ordered = _order_nodes(ordered, policy)
    batches = _batch(ordered, batch_size)

    retries_cfg = cfg.get("retries", {}) or {}
    backoff_cfg = cfg.get("backoff", {}) or {}

    steps: List[Dict[str, Any]] = []
    for batch_index, batch in enumerate(batches):
        for item in batch:
            cid = str(item.get("cluster_id"))
            step = {
                "cluster_id": cid,
                "priority": int(item.get("priority", 0)),
                "batch_index": batch_index,
                "attempts": {
                    "max": int(retries_cfg.get("max_attempts", 1)),
                    "retryable_statuses": retries_cfg.get("retryable_statuses", []),
                    "backoff": {
                        "initial": backoff_cfg.get("initial", 1.0),
                        "factor": backoff_cfg.get("factor", 2.0),
                        "jitter": backoff_cfg.get("jitter", 0.1),
                        "max": backoff_cfg.get("max", 30.0),
                    },
                },
                "idempotency_key": f"dispatch:{cid}",
            }
            steps.append(step)

    plan = {"steps": steps, "batches": len(batches), "policy": policy}
    plan_hash = _plan_hash(plan, algo=hash_algo)
    plan["plan_hash"] = plan_hash
    return plan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a cluster dispatch plan")
    parser.add_argument("--clusters", type=Path, required=True, help="Path to clusters JSON/YAML list")
    parser.add_argument("--config", type=Path, default=CONFIG_PATH, help="Path to dispatch config YAML")
    args = parser.parse_args(argv)

    try:
        if args.clusters.suffix.lower() in {".yaml", ".yml"}:
            clusters = yaml.safe_load(args.clusters.read_text(encoding="utf-8"))
        else:
            clusters = json.loads(args.clusters.read_text(encoding="utf-8"))
        cfg = load_dispatch_config(args.config)
        plan = generate_dispatch_plan(clusters, config=cfg)
        print(json.dumps({"status": "pass", "plan": plan}, indent=2))
        return 0
    except DispatchPlanError as exc:
        print(json.dumps({"status": "fail", "code": exc.code, "message": str(exc)}, indent=2))
        return 1
    except Exception as exc:  # pragma: no cover
        print(json.dumps({"status": "fail", "code": "unexpected_error", "message": str(exc)}, indent=2))
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
