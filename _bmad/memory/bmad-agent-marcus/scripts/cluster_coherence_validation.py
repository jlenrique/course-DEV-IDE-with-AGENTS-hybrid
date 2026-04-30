"""
Cluster Coherence Validation (Story 21-4).

Validates generated outputs against cluster manifests, visual constraints, and
sequencing expectations. Produces deterministic report hashes and pass/warn/block
decisions. Read-only: does not mutate content.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

CONFIG_PATH = Path("state/config/validation.yaml")


class CoherenceValidationError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def load_validation_config(path: Path = CONFIG_PATH) -> Dict[str, Any]:
    if yaml is None:  # pragma: no cover
        raise CoherenceValidationError("config_missing", "pyyaml is required")
    if not path.is_file():
        raise CoherenceValidationError("config_missing", f"validation config not found: {path}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise CoherenceValidationError("config_missing", f"invalid validation config: {exc}") from exc
    if not isinstance(raw, dict):
        raise CoherenceValidationError("config_missing", "validation config must be a mapping")
    return raw


def _hash_report(payload: Dict[str, Any], algo: str = "sha256") -> str:
    h = hashlib.new(algo)
    h.update(json.dumps(payload, sort_keys=True).encode("utf-8"))
    return h.hexdigest()


def _check_required(manifest: Dict[str, Any], outputs: List[Dict[str, Any]]) -> List[str]:
    errors: List[str] = []
    manifest_ids = [str(s.get("slide_id")) for s in manifest.get("segments", [])]
    output_ids = {str(o.get("slide_id")) for o in outputs}
    for sid in manifest_ids:
        if sid not in output_ids:
            errors.append(f"missing_output:{sid}")
    return errors


def _check_ordering(manifest: Dict[str, Any], outputs: List[Dict[str, Any]]) -> List[str]:
    errors: List[str] = []
    manifest_ids = [str(s.get("slide_id")) for s in manifest.get("segments", [])]
    output_ids = [str(o.get("slide_id")) for o in outputs]
    if manifest_ids != output_ids:
        errors.append("ordering_mismatch")
    return errors


def _check_constraints(outputs: List[Dict[str, Any]], constraints: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    required_terms = constraints.get("required_terms") or []
    forbidden_terms = constraints.get("forbidden_terms") or []
    for out in outputs:
        text = (out.get("text") or "").lower()
        sid = str(out.get("slide_id"))
        for term in required_terms:
            if term.lower() not in text:
                errors.append(f"missing_required_term:{sid}:{term}")
        for term in forbidden_terms:
            if term.lower() in text:
                errors.append(f"forbidden_term:{sid}:{term}")
    return errors


def _check_conflicts(outputs: List[Dict[str, Any]]) -> List[str]:
    errors: List[str] = []
    for out in outputs:
        text = (out.get("text") or "").lower()
        sid = str(out.get("slide_id"))
        if "conflict" in text:
            errors.append(f"conflict_detected:{sid}")
    return errors


def validate_cluster(
    *,
    manifest: Dict[str, Any],
    outputs: List[Dict[str, Any]],
    constraints: Dict[str, Any] | None = None,
    sequencing_expectations: Dict[str, Any] | None = None,
    config: Dict[str, Any] | None = None,
    seed: str | None = None,
) -> Dict[str, Any]:
    cfg = config or load_validation_config()
    hash_algo = (cfg.get("hashing", {}) or {}).get("algorithm", "sha256")
    constraints = constraints or {}

    if not isinstance(outputs, list):
        raise CoherenceValidationError("invalid_output_format", "outputs must be a list")

    errors: List[str] = []
    errors.extend(_check_required(manifest, outputs))
    errors.extend(_check_ordering(manifest, outputs))
    errors.extend(_check_constraints(outputs, constraints))
    errors.extend(_check_conflicts(outputs))

    seq_expected = sequencing_expectations or {}
    seq_expected_ids = seq_expected.get("expected_ids")
    if seq_expected_ids:
        out_ids = [str(o.get("slide_id")) for o in outputs]
        if out_ids != [str(x) for x in seq_expected_ids]:
            errors.append("sequencing_violation")

    # Score: simple heuristic based on errors count
    score = max(0, 1.0 - 0.1 * len(errors))
    decision = "pass" if not errors else "fail"
    report = {
        "decision": decision,
        "score": score,
        "violations": errors,
        "seed": seed,
    }
    report_hash = _hash_report(report, algo=hash_algo)
    report["report_hash"] = report_hash
    return report


def validate_interstitial_replacement(
    *,
    head_output: Dict[str, Any],
    replacement_output: Dict[str, Any],
    constraints: Dict[str, Any] | None = None,
    config: Dict[str, Any] | None = None,
    seed: str | None = None,
) -> Dict[str, Any]:
    """Run coherence validation for a replacement interstitial against head context only."""
    head_id = str(head_output.get("slide_id") or "").strip()
    replacement_id = str(replacement_output.get("slide_id") or "").strip()
    if not head_id or not replacement_id:
        raise CoherenceValidationError(
            "missing_required_field",
            "head_output.slide_id and replacement_output.slide_id are required",
        )
    manifest = {"segments": [{"slide_id": head_id}, {"slide_id": replacement_id}]}
    outputs = [
        {"slide_id": head_id, "text": str(head_output.get("text") or "")},
        {"slide_id": replacement_id, "text": str(replacement_output.get("text") or "")},
    ]
    return validate_cluster(
        manifest=manifest,
        outputs=outputs,
        constraints=constraints,
        sequencing_expectations={"expected_ids": [head_id, replacement_id]},
        config=config,
        seed=seed,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate cluster coherence")
    parser.add_argument("--manifest", type=Path, required=True, help="Path to manifest YAML")
    parser.add_argument("--outputs", type=Path, required=True, help="Path to generated outputs JSON/YAML")
    parser.add_argument("--constraints", type=Path, help="Path to constraints JSON/YAML", default=None)
    parser.add_argument("--config", type=Path, default=CONFIG_PATH, help="Path to validation config YAML")
    parser.add_argument("--seed", type=str, default=None)
    args = parser.parse_args(argv)

    try:
        manifest = yaml.safe_load(args.manifest.read_text(encoding="utf-8"))
        outputs = (
            yaml.safe_load(args.outputs.read_text(encoding="utf-8"))
            if args.outputs.suffix.lower() in {".yaml", ".yml"}
            else json.loads(args.outputs.read_text(encoding="utf-8"))
        )
        constraints = (
            yaml.safe_load(args.constraints.read_text(encoding="utf-8"))
            if args.constraints
            else None
        )
        cfg = load_validation_config(args.config)
        report = validate_cluster(
            manifest=manifest,
            outputs=outputs,
            constraints=constraints,
            sequencing_expectations=None,
            config=cfg,
            seed=args.seed,
        )
        print(json.dumps({"status": "pass", "report": report}, indent=2))
        return 0 if report["decision"] == "pass" else 1
    except CoherenceValidationError as exc:
        print(json.dumps({"status": "fail", "code": exc.code, "message": str(exc)}, indent=2))
        return 1
    except Exception as exc:  # pragma: no cover
        print(json.dumps({"status": "fail", "code": "unexpected_error", "message": str(exc)}, indent=2))
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
