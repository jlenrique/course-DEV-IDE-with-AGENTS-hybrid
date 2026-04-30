# /// script
# requires-python = ">=3.10"
# ///
"""G1.5 Cluster Plan Quality Gate — Marcus orchestration wrapper.

Story 20b-2: wraps validate-cluster-plan.py, reads run-constants for
cluster_density, writes gate receipt, generates cluster-plan-review.md
for operator HIL review. Inserted between Prompt 5 and Prompt 6 in the
production workflow for cluster-enabled runs.

Exit codes:
    0 — gate passed or skipped (non-clustered run)
    1 — gate failed (blocking criteria violations found)
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from importlib import util
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

_SCRIPTS_DIR = Path(__file__).resolve().parent
_ROOT = _SCRIPTS_DIR.parents[2]
sys.path.insert(0, str(_ROOT))

from scripts.utilities.run_constants import RunConstantsError, load_run_constants

# Load validate-cluster-plan module dynamically (same dir)
_VALIDATOR_PATH = _SCRIPTS_DIR / "validate-cluster-plan.py"
_validator_spec = util.spec_from_file_location("validate_cluster_plan", _VALIDATOR_PATH)
assert _validator_spec is not None and _validator_spec.loader is not None
_validator_mod = util.module_from_spec(_validator_spec)
_validator_spec.loader.exec_module(_validator_mod)
validate_cluster_plan = _validator_mod.validate_cluster_plan  # type: ignore[attr-defined]
DENSITY_RANGES = _validator_mod.DENSITY_RANGES  # type: ignore[attr-defined]

RECEIPT_FILENAME = "g1.5-cluster-gate-receipt.json"
REVIEW_FILENAME = "cluster-plan-review.md"
MANIFEST_FILENAME = "segment-manifest.yaml"
RUN_CONSTANTS_FILENAME = "run-constants.yaml"

_DENSITY_RANGE_LABELS: dict[str | None, str] = {
    "none": "0 clusters",
    "sparse": "1–2 clusters",
    "default": "3–5 clusters",
    "rich": "6+ clusters",
    None: "unconstrained",
}


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:  # pragma: no cover
        raise RuntimeError("pyyaml is required")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Expected YAML mapping at {path}")
    return raw


def _read_cluster_density(bundle_dir: Path) -> str | None:
    """Read cluster_density from run-constants.yaml; raise on error."""
    try:
        rc = load_run_constants(bundle_dir)
        return rc.cluster_density
    except RunConstantsError:
        raise


def _build_review_doc(
    manifest: dict[str, Any],
    result: dict[str, Any],
    *,
    run_id: str,
    cluster_density: str | None,
    timestamp: str,
) -> str:
    segments = manifest.get("segments", [])
    heads = [s for s in segments if s.get("cluster_role") == "head"]
    interstitials = [s for s in segments if s.get("cluster_role") == "interstitial"]

    cluster_ids: list[str] = []
    for h in heads:
        cid = str(h.get("cluster_id", ""))
        if cid not in cluster_ids:
            cluster_ids.append(cid)

    cluster_count = len(cluster_ids)
    passed = result["passed"]
    errors = result["errors"]
    # 14 criteria (G1.5-01 through G1.5-14)
    criteria_total = 14
    criteria_passed = criteria_total - len(errors)

    status_str = "PASS" if passed else f"FAIL ({len(errors)} errors)"
    density_label = _DENSITY_RANGE_LABELS.get(cluster_density, "unconstrained")

    # Build per-cluster sections
    cluster_sections_parts: list[str] = []
    for cid in cluster_ids:
        head = next((s for s in heads if str(s.get("cluster_id")) == cid), None)
        its = [s for s in interstitials if str(s.get("cluster_id")) == cid]

        arc = head.get("narrative_arc", "—") if head else "—"
        intent = head.get("master_behavioral_intent", "—") if head else "—"
        it_count = head.get("cluster_interstitial_count", len(its)) if head else len(its)

        rows = ["| Position | Type | Isolation Target | Narration Burden |",
                "|----------|------|-----------------|-----------------|",
                "| establish (head) | — | — | — |"]
        for it in its:
            pos = it.get("cluster_position", "—")
            itype = it.get("interstitial_type", "—")
            target = str(it.get("isolation_target") or "—")[:60]
            burden = it.get("narration_burden", "—")
            rows.append(f"| {pos} | {itype} | {target} | {burden} |")

        cluster_sections_parts.append(
            f"## Cluster `{cid}`: {arc}\n\n"
            f"**Master behavioral intent:** {intent}  \n"
            f"**Interstitial count:** {it_count}\n\n"
            + "\n".join(rows)
        )

    cluster_sections = "\n\n---\n\n".join(cluster_sections_parts) if cluster_sections_parts else "_No clusters found._"

    # Validation summary
    if passed:
        validation_summary = f"✅ All {criteria_total} G1.5 criteria passed."
    else:
        error_lines = "\n".join(f"- {e}" for e in errors)
        validation_summary = f"❌ {len(errors)} criteria failed:\n\n{error_lines}"

    return (
        f"# Cluster Plan Review — {run_id}\n\n"
        f"**G1.5 Status:** {status_str} ({criteria_passed}/{criteria_total} criteria)  \n"
        f"**Cluster count:** {cluster_count} ({cluster_density} target: {density_label})  \n"
        f"**Generated:** {timestamp}\n\n"
        "---\n\n"
        f"{cluster_sections}\n\n"
        "---\n\n"
        "## G1.5 Validation Summary\n\n"
        f"{validation_summary}\n\n"
        "---\n\n"
        "## Operator Decision\n\n"
        "Review each cluster above. Confirm:\n"
        "- Every interstitial only reveals, emphasizes, simplifies, or reframes content from its head slide\n"
        "- Each cluster has a visible internal arc (establish → develop/tension → resolve)\n"
        "- Narrative arcs are specific enough to guide narration\n\n"
        "**Select one:**\n\n"
        "[ ] **APPROVE** — cluster plan is sound; advance to Gary dispatch (Prompt 6)\n\n"
        "[ ] **REJECT** — return to Irene for revision\n\n"
        "  Revision notes: _______________________________________________\n\n"
        "---\n\n"
        "*Generated by `run-g1.5-cluster-gate.py`. Regenerate after Irene revises.*\n"
    )


def run_gate(
    bundle_dir: Path,
    *,
    manifest_path: Path | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Run G1.5 gate for a bundle directory.

    Returns a dict with keys: skipped (bool), passed (bool), errors (list).
    Also writes receipt and review doc as side-effects.
    """
    bundle_dir = Path(bundle_dir).resolve()
    try:
        cluster_density = _read_cluster_density(bundle_dir)
    except RunConstantsError:
        # Fail gate on broken run-constants
        return {"skipped": False, "passed": False, "errors": ["run-constants.yaml is invalid or missing"]}

    # Skip for non-clustered runs
    if cluster_density is None or cluster_density == "none":
        return {"skipped": True, "passed": True, "errors": []}

    # Locate manifest
    mpath = manifest_path or (bundle_dir / MANIFEST_FILENAME)
    if not mpath.is_file():
        raise FileNotFoundError(f"Segment manifest not found: {mpath}")

    manifest = _load_yaml(mpath)
    # Inject cluster_density from run-constants if manifest doesn't have it
    if "cluster_density" not in manifest or manifest["cluster_density"] is None:
        manifest["cluster_density"] = cluster_density

    result = validate_cluster_plan(manifest)
    timestamp = datetime.now(timezone.utc).isoformat()
    cluster_ids = {
        str(s["cluster_id"])
        for s in manifest.get("segments", [])
        if s.get("cluster_id") is not None
    }

    # Write receipt
    receipt: dict[str, Any] = {
        "status": "pass" if result["passed"] else "fail",
        "cluster_count": len(cluster_ids),
        "cluster_density": cluster_density,
        "errors": result["errors"],
        "timestamp": timestamp,
    }
    receipt_path = bundle_dir / RECEIPT_FILENAME
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")

    # On pass: generate review doc
    if result["passed"]:
        rid = run_id or _read_run_id(bundle_dir)
        review_doc = _build_review_doc(
            manifest,
            result,
            run_id=rid,
            cluster_density=cluster_density,
            timestamp=timestamp,
        )
        (bundle_dir / REVIEW_FILENAME).write_text(review_doc, encoding="utf-8")

    return {"skipped": False, "passed": result["passed"], "errors": result["errors"]}


def _read_run_id(bundle_dir: Path) -> str:
    try:
        rc = _load_yaml(bundle_dir / RUN_CONSTANTS_FILENAME)
        return str(rc.get("run_id", "UNKNOWN"))
    except Exception:
        return "UNKNOWN"


def main(argv: list[str] | None = None) -> int:
    if yaml is None:  # pragma: no cover
        print("FAIL: pyyaml is required")
        return 1

    parser = argparse.ArgumentParser(
        description="G1.5 Cluster Plan Gate — validates Irene cluster plan before Gary dispatch."
    )
    parser.add_argument("--bundle-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        result = run_gate(bundle_dir=args.bundle_dir, manifest_path=args.manifest)
    except FileNotFoundError as exc:
        print(f"FAIL: {exc}")
        return 1
    except Exception as exc:
        print(f"FAIL: unexpected error — {exc}")
        return 1

    if args.json:
        import json as _json
        print(_json.dumps(result, indent=2))
    elif result["skipped"]:
        print("SKIP — non-clustered run (cluster_density: none); G1.5 gate not required")
    elif result["passed"]:
        print(f"PASS — G1.5 Cluster Plan gate ({len(result['errors'])} errors)")
        print(f"  Review document: {args.bundle_dir / REVIEW_FILENAME}")
        print("  Awaiting operator approval before Gary dispatch.")
    else:
        print(f"FAIL — G1.5 Cluster Plan gate ({len(result['errors'])} blocking errors)")
        for err in result["errors"]:
            print(f"  • {err}")
        print("  Return to Irene for cluster plan revision before proceeding.")

    return 0 if result["skipped"] or result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
