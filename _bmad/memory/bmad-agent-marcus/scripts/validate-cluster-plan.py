# /// script
# requires-python = ">=3.10"
# ///
"""G1.5 Cluster Plan Quality Gate — validate Irene Pass 1 cluster plan.

Story 20b-1: validates the cluster metadata in a segment manifest before
Gary dispatch. All checks are deterministic (no LLM perception required).

Usage:
    python validate-cluster-plan.py --manifest <path-to-manifest.yaml> \
        [--cluster-density <none|sparse|default|rich>] [--json]

Exit codes:
    0 — all criteria pass
    1 — one or more criteria fail
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

VALID_INTERSTITIAL_TYPES = frozenset(
    {"reveal", "emphasis-shift", "bridge-text", "simplification", "pace-reset"}
)
VALID_NARRATION_BURDENS = frozenset({"low", "medium", "high"})
VALID_DEVELOP_TYPES = frozenset({"deepen", "reframe", "exemplify"})
VALID_CLUSTER_POSITIONS = frozenset({"establish", "develop", "tension", "resolve"})

# cluster_density → (min_clusters, max_clusters); None max = unbounded
DENSITY_RANGES: dict[str, tuple[int, int | None]] = {
    "none": (0, 0),
    "sparse": (1, 2),
    "default": (3, 5),
    "rich": (6, None),
}

# Cluster metadata fields that must be null for non-clustered segments
CLUSTER_ONLY_FIELDS = (
    "cluster_id",
    "cluster_role",
    "cluster_position",
    "parent_slide_id",
    "interstitial_type",
    "isolation_target",
    "narrative_arc",
    "develop_type",
    "master_behavioral_intent",
    "cluster_interstitial_count",
)


class ClusterPlanError(ValueError):
    """Structured cluster plan validation failure."""


def _seg_id(seg: dict[str, Any]) -> str:
    return str(seg.get("slide_id", "<unknown>"))


def validate_cluster_plan(manifest: dict[str, Any]) -> dict[str, Any]:
    """Validate a cluster plan manifest dict against all G1.5 criteria.

    Args:
        manifest: Dict with keys ``cluster_density`` and ``segments`` (list of segment dicts).

    Returns:
        Dict with ``passed`` (bool) and ``errors`` (list of str, each prefixed with criterion ID).
    """
    errors: list[str] = []
    segments: list[dict[str, Any]] = manifest.get("segments", [])
    cluster_density: str | None = manifest.get("cluster_density")

    # Index segments by slide_id for reference lookups
    by_id: dict[str, dict[str, Any]] = {str(s.get("slide_id", "")): s for s in segments}

    # Partition segments
    heads = [s for s in segments if s.get("cluster_role") == "head"]
    interstitials = [s for s in segments if s.get("cluster_role") == "interstitial"]
    flat = [s for s in segments if s.get("cluster_role") is None]

    # Cluster ID sets
    cluster_ids: set[str] = {str(s["cluster_id"]) for s in heads + interstitials if s.get("cluster_id")}

    # G1.5-01: Every interstitial's parent_slide_id references an existing head
    for seg in interstitials:
        pid = seg.get("parent_slide_id")
        if pid is None or str(pid) not in by_id:
            errors.append(
                f"G1.5-01 [{_seg_id(seg)}]: parent_slide_id {pid!r} does not reference "
                "an existing segment"
            )
        else:
            parent = by_id[str(pid)]
            if parent.get("cluster_role") != "head":
                errors.append(
                    f"G1.5-01 [{_seg_id(seg)}]: parent_slide_id {pid!r} references a "
                    f"non-head segment (role={parent.get('cluster_role')!r})"
                )
            if parent.get("cluster_id") != seg.get("cluster_id"):
                errors.append(
                    f"G1.5-01 [{_seg_id(seg)}]: parent cluster_id "
                    f"{parent.get('cluster_id')!r} != segment cluster_id "
                    f"{seg.get('cluster_id')!r}"
                )

    # G1.5-02: interstitial_type vocabulary
    for seg in interstitials:
        itype = seg.get("interstitial_type")
        if itype not in VALID_INTERSTITIAL_TYPES:
            errors.append(
                f"G1.5-02 [{_seg_id(seg)}]: interstitial_type {itype!r} is not in "
                f"canonical vocabulary {sorted(VALID_INTERSTITIAL_TYPES)}"
            )

    # G1.5-03: non-empty isolation_target
    for seg in interstitials:
        target = seg.get("isolation_target")
        if not target:
            errors.append(
                f"G1.5-03 [{_seg_id(seg)}]: isolation_target is empty or null"
            )

    # G1.5-04: narration_burden validity
    for seg in interstitials:
        burden = seg.get("narration_burden")
        if burden not in VALID_NARRATION_BURDENS:
            errors.append(
                f"G1.5-04 [{_seg_id(seg)}]: narration_burden {burden!r} is not one of "
                f"{sorted(VALID_NARRATION_BURDENS)}"
            )

    # G1.5-05: non-empty narrative_arc on every head
    for seg in heads:
        arc = seg.get("narrative_arc")
        if not arc:
            errors.append(
                f"G1.5-05 [{_seg_id(seg)}]: head segment is missing narrative_arc"
            )

    # G1.5-13: clustered manifest must have cluster_density
    if cluster_ids and cluster_density is None:
        errors.append("G1.5-13: manifest contains clustered segments but cluster_density is null or omitted")

    # G1.5-14: non-empty master_behavioral_intent on every head
    for seg in heads:
        intent = seg.get("master_behavioral_intent")
        if not intent:
            errors.append(
                f"G1.5-14 [{_seg_id(seg)}]: head segment is missing master_behavioral_intent"
            )

    # G1.5-06: develop-position interstitials must have a valid develop_type
    for seg in interstitials:
        if seg.get("cluster_position") == "develop":
            dtype = seg.get("develop_type")
            if dtype not in VALID_DEVELOP_TYPES:
                errors.append(
                    f"G1.5-06 [{_seg_id(seg)}]: develop-position interstitial has "
                    f"develop_type {dtype!r} — must be one of {sorted(VALID_DEVELOP_TYPES)}"
                )

    # G1.5-07: no two develop-position interstitials in the same cluster share develop_type
    develop_by_cluster: dict[str, list[str]] = {}
    for seg in interstitials:
        if seg.get("cluster_position") == "develop":
            cid = str(seg.get("cluster_id", ""))
            dtype = str(seg.get("develop_type", ""))
            develop_by_cluster.setdefault(cid, []).append(dtype)
    for cid, dtypes in develop_by_cluster.items():
        seen: set[str] = set()
        for dt in dtypes:
            if dt in seen:
                errors.append(
                    f"G1.5-07 [cluster={cid}]: develop_type {dt!r} is used more than "
                    "once within this cluster — develop sub-types must be distinct"
                )
            seen.add(dt)

    # G1.5-08: double_dispatch_eligible must be false for all interstitials
    for seg in interstitials:
        if seg.get("double_dispatch_eligible") is not False:
            errors.append(
                f"G1.5-08 [{_seg_id(seg)}]: interstitial has double_dispatch_eligible="
                f"{seg.get('double_dispatch_eligible')!r} — must be false"
            )

    # G1.5-09: cluster_interstitial_count 1–3 for all heads + actual match
    for seg in heads:
        count = seg.get("cluster_interstitial_count")
        if not isinstance(count, int) or count < 1 or count > 3:
            errors.append(
                f"G1.5-09 [{_seg_id(seg)}]: cluster_interstitial_count={count!r} — "
                "must be an integer in [1, 3]"
            )
        else:
            cid = str(seg.get("cluster_id"))
            actual = sum(1 for i in interstitials if str(i.get("cluster_id")) == cid)
            if actual != count:
                errors.append(
                    f"G1.5-09 [{_seg_id(seg)}]: declared cluster_interstitial_count={count} "
                    f"but found {actual} matching interstitials for cluster_id={cid}"
                )

    # G1.5-10: cluster count within density target
    n_clusters = len(cluster_ids)
    density_key = cluster_density if cluster_density in DENSITY_RANGES else "none"
    min_c, max_c = DENSITY_RANGES[density_key]
    if n_clusters < min_c or (max_c is not None and n_clusters > max_c):
        bound_str = f"{min_c}–{max_c}" if max_c is not None else f"{min_c}+"
        errors.append(
            f"G1.5-10: cluster count {n_clusters} is outside target range {bound_str} "
            f"for cluster_density={cluster_density!r}"
        )

    # G1.5-11: head segments must use cluster_position == establish;
    #           all clustered segments must use a valid position
    for seg in heads:
        pos = seg.get("cluster_position")
        if pos != "establish":
            errors.append(
                f"G1.5-11 [{_seg_id(seg)}]: head segment has cluster_position={pos!r} — "
                "must be 'establish'"
            )
    for seg in interstitials:
        pos = seg.get("cluster_position")
        if pos not in VALID_CLUSTER_POSITIONS:
            errors.append(
                f"G1.5-11 [{_seg_id(seg)}]: interstitial has invalid cluster_position="
                f"{pos!r} — must be one of {sorted(VALID_CLUSTER_POSITIONS)}"
            )

    # G1.5-12: non-clustered segments must have null cluster metadata
    for seg in flat:
        for field in CLUSTER_ONLY_FIELDS:
            val = seg.get(field)
            if val is not None:
                errors.append(
                    f"G1.5-12 [{_seg_id(seg)}]: non-clustered segment has {field}="
                    f"{val!r} — must be null for flat segments"
                )

    return {"passed": len(errors) == 0, "errors": errors}


def main(argv: list[str] | None = None) -> int:
    if yaml is None:  # pragma: no cover
        print("FAIL: pyyaml is required")
        return 1

    parser = argparse.ArgumentParser(
        description="G1.5 Cluster Plan Quality Gate — validates Irene Pass 1 cluster plan."
    )
    parser.add_argument("--manifest", type=Path, required=True, help="Path to segment manifest YAML")
    parser.add_argument(
        "--cluster-density",
        choices=["none", "sparse", "default", "rich"],
        default=None,
        help="Override cluster_density (defaults to value in manifest)",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON instead of text")
    args = parser.parse_args(argv)

    if not args.manifest.is_file():
        print(f"FAIL: manifest not found: {args.manifest}")
        return 1

    try:
        raw = yaml.safe_load(args.manifest.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"FAIL: could not parse manifest YAML: {exc}")
        return 1

    if not isinstance(raw, dict):
        print("FAIL: manifest must be a YAML mapping")
        return 1

    if args.cluster_density is not None:
        raw["cluster_density"] = args.cluster_density

    result = validate_cluster_plan(raw)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"{status} — G1.5 Cluster Plan ({len(result['errors'])} errors)")
        for err in result["errors"]:
            print(f"  • {err}")

    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
