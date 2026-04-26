from __future__ import annotations

import json
import subprocess
import sys
from importlib import util
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = ROOT / "skills" / "bmad-agent-marcus" / "scripts" / "validate-source-bundle-confidence.py"


def _load_script_module():
    spec = util.spec_from_file_location(
        "validate_source_bundle_confidence_module",
        SCRIPT_PATH,
    )
    assert spec is not None
    assert spec.loader is not None
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


module = _load_script_module()
validate_source_bundle_confidence = module.validate_source_bundle_confidence


def _write_bundle(tmp_path: Path, *, evidence_confidence: str = "high", planning_readiness: str = "ready", receipt_body: str | None = None) -> tuple[Path, Path]:
    bundle = tmp_path / "bundle"
    raw = bundle / "raw"
    raw.mkdir(parents=True)

    (raw / "perception_roadmap.json").write_text(
        json.dumps(
            {
                "artifact_path": str((tmp_path / "APC Content Roadmap.jpg").resolve()),
                "confidence": "HIGH",
                "confidence_rationale": "Minor wording variance possible on smallest labels.",
            }
        ),
        encoding="utf-8",
    )
    (bundle / "metadata.json").write_text(
        json.dumps(
            {
                "provenance": [
                    {
                        "kind": "local_image",
                        "ref": str((tmp_path / "APC Content Roadmap.jpg").resolve()),
                        "note": "sensory-bridges perceive(image,G0); perception raw/perception_roadmap.json; original in raw/APC Content Roadmap.jpg",
                        "fetched_at": "2026-03-30T00:00:00+00:00",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (bundle / "extracted.md").write_text(
        "\n".join(
            [
                "## APC Content Roadmap — sensory bridge (G0)",
                "",
                "**Ingestion:** Official path on `course-content/courses/APC Content Roadmap.jpg`.",
                "",
                "## Bridge confidence",
                "",
                "HIGH: Minor wording variance possible on smallest labels.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (bundle / "ingestion-evidence.md").write_text(
        "\n".join(
            [
                "# Ingestion Evidence",
                "",
                "| source_id | pathway_used | extraction_status | coverage_metric | confidence | bundle_location | provenance_summary | planning_readiness |",
                "|---|---|---|---|---|---|---|---|",
                f"| SRC-ROADMAP-PNG-01 | official image-capable sensory route (`bridge_utils.perceive`) | pass | roadmap transcription present | {evidence_confidence} | bundle | `kind=local_image`; source file APC Content Roadmap.jpg; perception raw/perception_roadmap.json | {planning_readiness} |",
                "",
                "- preflight_reference: bundle/preflight-results.json",
                "- blocked_sources: none",
                "- next_action: continue",
            ]
        ),
        encoding="utf-8",
    )
    receipt = bundle / "receipt.md"
    if receipt_body is None:
        receipt_body = "\n".join(
            [
                "### SRC-ROADMAP-PNG-01 (local_image)",
                "- planning usability: pass",
                "- fidelity usability: pass",
            ]
        )
    receipt.write_text(receipt_body, encoding="utf-8")
    return bundle, receipt


def test_passes_when_confidence_is_inherited_consistently(tmp_path: Path) -> None:
    bundle, receipt = _write_bundle(tmp_path)

    result = validate_source_bundle_confidence(bundle, receipt_path=receipt)

    assert result["status"] == "pass"
    assert result["errors"] == []
    assert result["checked_sources"][0]["official_confidence"] == "high"


def test_fails_when_evidence_downgrades_without_explicit_evidence(tmp_path: Path) -> None:
    bundle, receipt = _write_bundle(tmp_path, evidence_confidence="medium", planning_readiness="conditional")

    result = validate_source_bundle_confidence(bundle, receipt_path=receipt)

    assert result["status"] == "fail"
    assert any("does not inherit official confidence" in msg for msg in result["errors"])
    assert any("planning_readiness is conditional" in msg for msg in result["errors"])


def test_passes_when_receipt_records_explicit_downgrade_evidence(tmp_path: Path) -> None:
    receipt_body = "\n".join(
        [
            "### SRC-ROADMAP-PNG-01 (local_image)",
            "- planning usability: fail",
            "- fidelity usability: fail",
            "- explicit downgrade evidence: full-resolution review found missing fine-print labels in course 2 assessment lane.",
        ]
    )
    bundle, receipt = _write_bundle(
        tmp_path,
        evidence_confidence="medium",
        planning_readiness="conditional",
        receipt_body=receipt_body,
    )

    result = validate_source_bundle_confidence(bundle, receipt_path=receipt)

    assert result["status"] == "pass"


def test_fails_when_receipt_uses_confidence_as_failure_reason_without_explicit_downgrade(tmp_path: Path) -> None:
    receipt_body = "\n".join(
        [
            "### SRC-ROADMAP-PNG-01 (local_image)",
            "- planning usability: fail",
            "- fidelity usability: fail",
            "- failure basis: confidence remains unresolved pending spot-check.",
        ]
    )
    bundle, receipt = _write_bundle(tmp_path, receipt_body=receipt_body)

    result = validate_source_bundle_confidence(bundle, receipt_path=receipt)

    assert result["status"] == "fail"
    assert any("receipt fails planning/fidelity usability on confidence grounds" in msg for msg in result["errors"])


def _write_minimal_bundle_under_repo(repo: Path) -> Path:
    """Same shape as _write_bundle but rooted at *repo* (for run-constants path checks)."""
    bundle = repo / "staging" / "b1"
    raw = bundle / "raw"
    raw.mkdir(parents=True)
    img = repo / "APC Content Roadmap.jpg"
    img.write_text("png", encoding="utf-8")
    (raw / "perception_roadmap.json").write_text(
        json.dumps(
            {
                "artifact_path": str(img.resolve()),
                "confidence": "HIGH",
                "confidence_rationale": "Minor wording variance possible on smallest labels.",
            }
        ),
        encoding="utf-8",
    )
    (bundle / "metadata.json").write_text(
        json.dumps(
            {
                "provenance": [
                    {
                        "kind": "local_image",
                        "ref": str(img.resolve()),
                        "note": "sensory-bridges perceive(image,G0); perception raw/perception_roadmap.json; original in raw/APC Content Roadmap.jpg",
                        "fetched_at": "2026-03-30T00:00:00+00:00",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (bundle / "extracted.md").write_text(
        "\n".join(
            [
                "## APC Content Roadmap — sensory bridge (G0)",
                "",
                "**Ingestion:** Official path on `course-content/courses/APC Content Roadmap.jpg`.",
                "",
                "## Bridge confidence",
                "",
                "HIGH: Minor wording variance possible on smallest labels.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (bundle / "ingestion-evidence.md").write_text(
        "\n".join(
            [
                "# Ingestion Evidence",
                "",
                "| source_id | pathway_used | extraction_status | coverage_metric | confidence | bundle_location | provenance_summary | planning_readiness |",
                "|---|---|---|---|---|---|---|---|",
                "| SRC-ROADMAP-PNG-01 | official | pass | ok | high | bundle | `kind=local_image`; source file APC Content Roadmap.jpg; perception raw/perception_roadmap.json | ready |",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return bundle


def test_run_constants_mismatch_fails(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    bundle = _write_minimal_bundle_under_repo(repo)
    (repo / "primary.pdf").write_text("pdf", encoding="utf-8")
    bad = {
        "run_id": "R1",
        "lesson_slug": "ls",
        "bundle_path": "staging/WRONG",
        "primary_source_file": str((repo / "primary.pdf").resolve()),
        "optional_context_assets": [],
        "theme_selection": "t",
        "theme_paramset_key": "p",
        "execution_mode": "tracked/default",
        "quality_preset": "draft",
    }
    (bundle / "run-constants.yaml").write_text(yaml.safe_dump(bad), encoding="utf-8")

    result = validate_source_bundle_confidence(bundle, repo_root=repo)

    assert result["status"] == "fail"
    assert any("run_constants:" in e for e in result["errors"])


def test_run_constants_aligned_passes_with_repo_root(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    bundle = _write_minimal_bundle_under_repo(repo)
    (repo / "primary.pdf").write_text("pdf", encoding="utf-8")
    good = {
        "run_id": "R1",
        "lesson_slug": "ls-b1",
        "bundle_path": "staging/b1",
        "primary_source_file": str((repo / "primary.pdf").resolve()),
        "optional_context_assets": [],
        "theme_selection": "t",
        "theme_paramset_key": "p",
        "execution_mode": "tracked/default",
        "quality_preset": "draft",
    }
    (bundle / "run-constants.yaml").write_text(yaml.safe_dump(good), encoding="utf-8")

    result = validate_source_bundle_confidence(bundle, repo_root=repo)

    assert result["status"] == "pass"
    assert not any("run_constants:" in e for e in result["errors"])


def test_cli_exit_code_and_output(tmp_path: Path) -> None:
    bundle, receipt = _write_bundle(tmp_path)

    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--bundle-dir",
            str(bundle),
            "--receipt",
            str(receipt),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert data["status"] == "pass"


def test_passes_with_source_file_ingestion_pattern_and_hyphen_heading(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir(parents=True)
    pdf = (tmp_path / "APC C1-M1 Tejal 2026-03-29.pdf").resolve()
    pdf.write_text("pdf", encoding="utf-8")

    (bundle / "metadata.json").write_text(
        json.dumps(
            {
                "provenance": [
                    {
                        "kind": "local_pdf",
                        "ref": str(pdf),
                        "note": "pypdf scanned=24/24",
                        "fetched_at": "2026-04-03T00:00:00+00:00",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (bundle / "extracted.md").write_text(
        "\n".join(
            [
                "## SRC-PRIMARY-PDF-01 - sensory bridge (G0)",
                "",
                f"**Ingestion:** source file {pdf}; official source-wrangler path `wrangle_local_pdf`",
                "",
                "## Bridge confidence",
                "",
                "HIGH: pypdf extraction completed; focus narrowed to Part 1.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (bundle / "ingestion-evidence.md").write_text(
        "\n".join(
            [
                "# Ingestion Evidence",
                "",
                "| source_id | pathway_used | extraction_status | coverage_metric | confidence | bundle_location | provenance_summary | planning_readiness |",
                "|---|---|---|---|---|---|---|---|",
                f"| SRC-PRIMARY-PDF-01 | official | pass | focused | high | extracted.md#SRC-PRIMARY-PDF-01 | source file {pdf}; local_pdf; pypdf scanned=24/24 | ready |",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = validate_source_bundle_confidence(bundle)

    assert result["status"] == "pass"
    assert any(row["source_id"] == "SRC-PRIMARY-PDF-01" for row in result["checked_sources"])


def test_wrapper_module_cli_exit_code_and_output(tmp_path: Path) -> None:
    bundle, receipt = _write_bundle(tmp_path)

    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.utilities.validate_source_bundle_confidence",
            "--bundle-dir",
            str(bundle),
            "--receipt",
            str(receipt),
        ],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(ROOT),
    )

    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert data["status"] == "pass"
