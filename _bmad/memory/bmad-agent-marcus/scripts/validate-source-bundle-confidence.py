# /// script
# requires-python = ">=3.10"
# ///
"""Validate confidence consistency across source bundle artifacts.

This protects Prompt 3/4 against confidence drift between:
- raw sensory perception outputs
- extracted.md bridge confidence notes
- ingestion-evidence.md confidence/readiness rows
- optional Prompt 4 receipt
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.utilities.file_helpers import project_root  # noqa: E402
from scripts.utilities.run_constants import (  # noqa: E402
    RunConstantsError,
    load_run_constants,
    validate_run_id_for_bundle,
)


CONFIDENCE_ORDER = {"low": 0, "medium": 1, "high": 2}
SENSORY_HEADING_RE = re.compile(r"^##\s+(.+?)\s+[—-]\s+sensory bridge(?:\s+\(G0\))?\s*$")
BRIDGE_CONFIDENCE_RE = re.compile(r"^(HIGH|MEDIUM|LOW):\s*(.*)$")
SOURCE_FILE_RE = re.compile(r"source file\s+([^;]+)", re.IGNORECASE)
INGESTION_ON_PATH_RE = re.compile(r"\bon `([^`]+)`")
INGESTION_SOURCE_FILE_RE = re.compile(r"source file\s+([^;]+)", re.IGNORECASE)
PERCEPTION_PATH_RE = re.compile(r"perception\s+(raw/[^;]+\.json)", re.IGNORECASE)
DOWNGRADE_RE = re.compile(r"explicit\s+downgrade\s+evidence\s*:\s*(.+)", re.IGNORECASE)


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def _parse_markdown_table(text: str) -> list[dict[str, str]]:
    lines = text.splitlines()
    start = None
    for idx, line in enumerate(lines):
        if line.strip().startswith("|"):
            start = idx
            break
    if start is None or start + 2 >= len(lines):
        return []

    header = [cell.strip() for cell in lines[start].strip().strip("|").split("|")]
    rows: list[dict[str, str]] = []
    for line in lines[start + 2 :]:
        if not line.strip().startswith("|"):
            break
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != len(header):
            continue
        rows.append(dict(zip(header, cells, strict=True)))
    return rows


def _parse_extracted_bridge_confidences(text: str) -> list[dict[str, str]]:
    lines = text.splitlines()
    blocks: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    in_bridge_confidence = False

    for line in lines:
        heading_match = SENSORY_HEADING_RE.match(line.strip())
        if heading_match:
            if current:
                blocks.append(current)
            current = {"heading": heading_match.group(1), "artifact_ref": "", "confidence": "", "rationale": ""}
            in_bridge_confidence = False
            continue

        if current is None:
            continue

        if line.startswith("**Ingestion:**"):
            path_match = INGESTION_ON_PATH_RE.search(line)
            if path_match:
                current["artifact_ref"] = path_match.group(1).strip()
            else:
                source_match = INGESTION_SOURCE_FILE_RE.search(line)
                if source_match:
                    current["artifact_ref"] = source_match.group(1).strip()
            continue

        if line.strip() == "## Bridge confidence":
            in_bridge_confidence = True
            continue

        if in_bridge_confidence and line.strip():
            confidence_match = BRIDGE_CONFIDENCE_RE.match(line.strip())
            if confidence_match:
                current["confidence"] = confidence_match.group(1).lower()
                current["rationale"] = confidence_match.group(2).strip()
            in_bridge_confidence = False

    if current:
        blocks.append(current)

    return blocks


def _parse_receipt_sections(text: str) -> dict[str, dict[str, Any]]:
    sections: dict[str, dict[str, Any]] = {}
    current_id: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("### SRC-"):
            current_id = stripped.removeprefix("### ").split()[0]
            sections[current_id] = {"raw": []}
            continue
        if current_id is None:
            continue
        sections[current_id]["raw"].append(stripped)
        if stripped.startswith("- ") and ":" in stripped:
            key, value = stripped[2:].split(":", 1)
            sections[current_id][key.strip().lower()] = value.strip()
        downgrade_match = DOWNGRADE_RE.search(stripped)
        if downgrade_match:
            sections[current_id]["explicit_downgrade_evidence"] = downgrade_match.group(1).strip()
    return sections


def _basename(value: str) -> str:
    return Path(value).name.lower()


def validate_source_bundle_confidence(
    bundle_dir: Path,
    *,
    receipt_path: Path | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    metadata = _load_json(bundle_dir / "metadata.json")
    extracted = (bundle_dir / "extracted.md").read_text(encoding="utf-8", errors="replace")
    evidence_text = (bundle_dir / "ingestion-evidence.md").read_text(encoding="utf-8", errors="replace")
    receipt_text = (
        receipt_path.read_text(encoding="utf-8", errors="replace") if receipt_path else None
    )

    evidence_rows = _parse_markdown_table(evidence_text)
    extracted_blocks = _parse_extracted_bridge_confidences(extracted)
    receipt_sections = _parse_receipt_sections(receipt_text) if receipt_text else {}

    extracted_by_basename = {
        _basename(block["artifact_ref"]): block
        for block in extracted_blocks
        if block.get("artifact_ref")
    }

    errors: list[str] = []
    warnings: list[str] = []
    checked_sources: list[dict[str, Any]] = []

    if (bundle_dir / "run-constants.yaml").is_file():
        root = repo_root if repo_root is not None else project_root()
        try:
            rc = load_run_constants(bundle_dir, root=root, verify_paths_exist=False)
            for hint in validate_run_id_for_bundle(rc, bundle_dir):
                warnings.append(f"run_constants: {hint}")
        except RunConstantsError as exc:
            errors.append(f"run_constants: {exc}")

    for row in evidence_rows:
        source_id = row.get("source_id", "")
        summary = row.get("provenance_summary", "")
        source_match = SOURCE_FILE_RE.search(summary)
        if not source_match:
            continue

        source_file = source_match.group(1).strip()
        basename = _basename(source_file)

        provenance = next(
            (
                item
                for item in metadata.get("provenance", [])
                if isinstance(item, dict) and _basename(str(item.get("ref", ""))) == basename
            ),
            None,
        )
        if provenance is None:
            warnings.append(f"No metadata provenance match for {source_id} ({source_file})")
            continue

        perception_path = None
        note = str(provenance.get("note", ""))
        perception_match = PERCEPTION_PATH_RE.search(note)
        if perception_match:
            perception_path = bundle_dir / Path(perception_match.group(1))

        official_confidence = None
        official_rationale = None
        if perception_path and perception_path.is_file():
            perception_data = _load_json(perception_path)
            official_confidence = str(perception_data.get("confidence", "")).lower()
            official_rationale = str(perception_data.get("confidence_rationale", "")).strip()

        extracted_block = extracted_by_basename.get(basename)
        if extracted_block and extracted_block.get("confidence"):
            extracted_confidence = extracted_block["confidence"]
            if official_confidence is None:
                official_confidence = extracted_confidence
                official_rationale = extracted_block.get("rationale", "")
            elif extracted_confidence != official_confidence:
                errors.append(
                    f"{source_id}: extracted.md bridge confidence ({extracted_confidence}) does not match raw perception confidence ({official_confidence})"
                )

        if official_confidence is None:
            continue

        evidence_confidence = row.get("confidence", "").strip().lower()
        planning_readiness = row.get("planning_readiness", "").strip().lower()
        receipt_section = receipt_sections.get(source_id, {})
        explicit_downgrade_evidence = str(
            receipt_section.get("explicit_downgrade_evidence", "")
        ).strip()

        if evidence_confidence != official_confidence and not explicit_downgrade_evidence:
            errors.append(
                f"{source_id}: ingestion-evidence confidence ({evidence_confidence}) does not inherit official confidence ({official_confidence}) and no explicit downgrade evidence was recorded"
            )

        if official_confidence == "high" and planning_readiness in {"conditional", "blocked"} and not explicit_downgrade_evidence:
            errors.append(
                f"{source_id}: planning_readiness is {planning_readiness} even though official confidence is high and no explicit downgrade evidence was recorded"
            )

        raw_text = "\n".join(receipt_section.get("raw", [])) if receipt_section else ""
        mentions_confidence_downgrade = any(
            token in raw_text.lower()
            for token in ("confidence", "spot-check", "spot check", "downgrade")
        )
        if (
            official_confidence == "high"
            and not explicit_downgrade_evidence
            and receipt_section
            and mentions_confidence_downgrade
            and (
                receipt_section.get("planning usability", "").lower() == "fail"
                or receipt_section.get("fidelity usability", "").lower() == "fail"
            )
        ):
            errors.append(
                f"{source_id}: receipt fails planning/fidelity usability on confidence grounds despite high official confidence and no explicit downgrade evidence"
            )

        checked_sources.append(
            {
                "source_id": source_id,
                "source_file": source_file,
                "official_confidence": official_confidence,
                "official_rationale": official_rationale,
                "evidence_confidence": evidence_confidence,
                "planning_readiness": planning_readiness,
                "receipt_checked": bool(receipt_section),
                "explicit_downgrade_evidence": explicit_downgrade_evidence,
            }
        )

    return {
        "status": "pass" if not errors else "fail",
        "bundle_dir": str(bundle_dir),
        "receipt_path": str(receipt_path) if receipt_path else None,
        "errors": errors,
        "warnings": warnings,
        "checked_sources": checked_sources,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate source bundle confidence consistency")
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        required=True,
        help="Path to source bundle directory containing extracted.md, metadata.json, and ingestion-evidence.md",
    )
    parser.add_argument(
        "--receipt",
        type=Path,
        default=None,
        help="Optional Prompt 4 receipt markdown path for cross-checking gate interpretation",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root for run-constants.yaml bundle_path resolution (default: auto-discovered)",
    )
    args = parser.parse_args()

    try:
        result = validate_source_bundle_confidence(
            args.bundle_dir,
            receipt_path=args.receipt,
            repo_root=args.repo_root,
        )
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "pass" else 1
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "fail",
                    "errors": [f"validator_exception: {type(exc).__name__}: {exc}"],
                },
                indent=2,
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
