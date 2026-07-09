"""Validate S8 full-close proof corpus readiness.

This is a preflight utility only. It does not select a corpus, mutate runtime
state, or prove S8 complete. The operator must name the proof corpus first.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

REPO_REL_COURSES_ROOT = Path("course-content") / "courses"
TEXT_EXTENSIONS = {".md", ".txt", ".yaml", ".yml", ".json", ".csv"}
PDF_EXTENSIONS = {".pdf"}
DOC_OR_DECK_EXTENSIONS = {".docx", ".doc", ".pptx", ".ppt"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+")
URL_RE = re.compile(r"https?://", re.IGNORECASE)
KEBAB_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REQUIRED_CORPUS_DIRS = ("slides", "references", "assessments")

Severity = Literal["error", "warning", "pass"]


@dataclass(frozen=True)
class Finding:
    check_id: str
    severity: Severity
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "check_id": self.check_id,
            "severity": self.severity,
            "message": self.message,
        }


@dataclass(frozen=True)
class CorpusInventory:
    corpus_path: Path
    slug: str
    file_count: int
    pdf_count: int
    doc_or_deck_count: int
    image_count: int
    text_file_count: int
    doi_count: int
    url_count: int

    def as_dict(self) -> dict[str, int | str]:
        return {
            "corpus_path": self.corpus_path.as_posix(),
            "slug": self.slug,
            "file_count": self.file_count,
            "pdf_count": self.pdf_count,
            "doc_or_deck_count": self.doc_or_deck_count,
            "image_count": self.image_count,
            "text_file_count": self.text_file_count,
            "doi_count": self.doi_count,
            "url_count": self.url_count,
        }


@dataclass(frozen=True)
class S8ProofCorpusReport:
    ready: bool
    inventory: CorpusInventory
    findings: tuple[Finding, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "ready": self.ready,
            "inventory": self.inventory.as_dict(),
            "findings": [finding.as_dict() for finding in self.findings],
        }


def _repo_root(path: Path) -> Path | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return Path(result.stdout.strip())


def _text_for_scan(path: Path) -> str:
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def inventory_corpus(corpus_path: Path) -> CorpusInventory:
    files = sorted(path for path in corpus_path.rglob("*") if path.is_file())
    doi_count = 0
    url_count = 0
    text_file_count = 0
    for path in files:
        text = _text_for_scan(path)
        if not text:
            continue
        text_file_count += 1
        doi_count += len(DOI_RE.findall(text))
        url_count += len(URL_RE.findall(text))
    return CorpusInventory(
        corpus_path=corpus_path,
        slug=corpus_path.name,
        file_count=len(files),
        pdf_count=sum(path.suffix.lower() in PDF_EXTENSIONS for path in files),
        doc_or_deck_count=sum(
            path.suffix.lower() in DOC_OR_DECK_EXTENSIONS for path in files
        ),
        image_count=sum(path.suffix.lower() in IMAGE_EXTENSIONS for path in files),
        text_file_count=text_file_count,
        doi_count=doi_count,
        url_count=url_count,
    )


def _is_direct_course_corpus(corpus_path: Path, repo_root: Path | None) -> bool:
    if repo_root is None:
        return REPO_REL_COURSES_ROOT.as_posix() in corpus_path.as_posix()
    try:
        relative = corpus_path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return False
    parts = relative.parts
    return len(parts) == 3 and Path(*parts[:2]) == REPO_REL_COURSES_ROOT


def _has_source_gap_ledger(corpus_path: Path) -> bool:
    return any(
        path.is_file() and "gap" in path.name.lower()
        for path in (corpus_path / "references").glob("*.md")
    )


def _tracked_diffs_outside_corpus(corpus_path: Path) -> list[str]:
    repo_root = _repo_root(corpus_path)
    if repo_root is None:
        return []
    try:
        rel_corpus = corpus_path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        rel_corpus = corpus_path.as_posix()
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "diff", "--name-only", "HEAD", "--"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return []
    changed = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return [
        path
        for path in changed
        if path != rel_corpus and not path.startswith(f"{rel_corpus}/")
    ]


def _attestation_findings(
    *,
    operator_named_slug: str | None,
    expected_slug: str,
    operator_knows_cold: bool,
    fresh_to_pipeline: bool,
    freshness_exception_rationale: str | None,
    adequacy_wrinkle: str | None,
    no_corpus_specific_diffs_acknowledged: bool,
) -> list[Finding]:
    findings: list[Finding] = []
    if operator_named_slug is None:
        findings.append(
            Finding(
                "operator_named_corpus",
                "error",
                "Operator-named S8 proof corpus is required.",
            )
        )
    elif operator_named_slug != expected_slug:
        findings.append(
            Finding(
                "operator_named_corpus",
                "error",
                (
                    f"Operator-named slug '{operator_named_slug}' does not match "
                    f"corpus slug '{expected_slug}'."
                ),
            )
        )
    else:
        findings.append(
            Finding(
                "operator_named_corpus",
                "pass",
                "Operator-named slug matches corpus path.",
            )
        )
    if not operator_knows_cold:
        findings.append(
            Finding(
                "operator_knows_cold",
                "error",
                "Operator must attest they know this material cold.",
            )
        )
    if fresh_to_pipeline:
        findings.append(
            Finding(
                "fresh_to_pipeline",
                "pass",
                "Operator attests the corpus is fresh to the pipeline.",
            )
        )
    elif freshness_exception_rationale and freshness_exception_rationale.strip():
        findings.append(
            Finding(
                "fresh_to_pipeline",
                "pass",
                "Freshness exception is explicitly ratified with rationale.",
            )
        )
    else:
        findings.append(
            Finding(
                "fresh_to_pipeline",
                "error",
                "Operator must attest this corpus is fresh to the pipeline or ratify an exception.",
            )
        )
    if not adequacy_wrinkle or not adequacy_wrinkle.strip():
        findings.append(
            Finding(
                "adequacy_wrinkle",
                "error",
                "A genuine adequacy wrinkle for G0R pressure-testing is required.",
            )
        )
    if not no_corpus_specific_diffs_acknowledged:
        findings.append(
            Finding(
                "no_corpus_specific_diffs_acknowledged",
                "error",
                "Operator must acknowledge zero corpus-specific production diffs.",
            )
        )
    return findings


def evaluate_s8_proof_corpus(
    corpus_path: Path,
    *,
    operator_named_slug: str | None = None,
    operator_knows_cold: bool = False,
    fresh_to_pipeline: bool = False,
    adequacy_wrinkle: str | None = None,
    no_corpus_specific_diffs_acknowledged: bool = False,
    allow_tejal_exception: bool = False,
    allow_source_gaps: bool = False,
    freshness_exception_rationale: str | None = None,
) -> S8ProofCorpusReport:
    corpus_path = corpus_path.resolve()
    inventory = inventory_corpus(corpus_path) if corpus_path.exists() else CorpusInventory(
        corpus_path=corpus_path,
        slug=corpus_path.name,
        file_count=0,
        pdf_count=0,
        doc_or_deck_count=0,
        image_count=0,
        text_file_count=0,
        doi_count=0,
        url_count=0,
    )
    findings: list[Finding] = []
    repo_root = _repo_root(corpus_path.parent if not corpus_path.exists() else corpus_path)

    if not corpus_path.exists():
        findings.append(Finding("corpus_exists", "error", "Corpus path does not exist."))
    elif not corpus_path.is_dir():
        findings.append(Finding("corpus_is_directory", "error", "Corpus path is not a directory."))
    else:
        findings.append(Finding("corpus_exists", "pass", "Corpus path exists as a directory."))

    if _is_direct_course_corpus(corpus_path, repo_root):
        findings.append(
            Finding(
                "standard_layout",
                "pass",
                "Corpus path is under course-content/courses/<lesson_slug>.",
            )
        )
    else:
        findings.append(
            Finding(
                "standard_layout",
                "error",
                "Corpus path must be under course-content/courses/<lesson_slug>.",
            )
        )

    for dirname in REQUIRED_CORPUS_DIRS:
        required_dir = corpus_path / dirname
        if required_dir.is_dir():
            findings.append(
                Finding(
                    f"has_{dirname}_dir",
                    "pass",
                    f"Required directory '{dirname}/' is present.",
                )
            )
        else:
            findings.append(
                Finding(
                    f"has_{dirname}_dir",
                    "error",
                    f"Required directory '{dirname}/' is missing.",
                )
            )

    for filename in ("README.md", "urls.txt"):
        required_file = corpus_path / filename
        if required_file.is_file():
            findings.append(
                Finding(
                    f"has_{filename.lower().replace('.', '_')}",
                    "pass",
                    f"Required file '{filename}' is present.",
                )
            )
        else:
            findings.append(
                Finding(
                    f"has_{filename.lower().replace('.', '_')}",
                    "error",
                    f"Required file '{filename}' is missing.",
                )
            )

    has_gap_ledger = _has_source_gap_ledger(corpus_path)
    if allow_source_gaps and has_gap_ledger:
        findings.append(
            Finding(
                "source_gap_ledger",
                "pass",
                "Source gaps are explicitly allowed and a gap ledger is present.",
            )
        )
    elif allow_source_gaps:
        findings.append(
            Finding(
                "source_gap_ledger",
                "error",
                "Source gaps were allowed, but no references/*gap*.md ledger was found.",
            )
        )

    if KEBAB_SLUG_RE.match(inventory.slug):
        findings.append(Finding("kebab_slug", "pass", "Corpus slug is kebab-case."))
    else:
        findings.append(
            Finding("kebab_slug", "error", "Corpus slug must be lowercase kebab-case.")
        )

    if "tejal" in inventory.slug.lower() and not allow_tejal_exception:
        findings.append(
            Finding(
                "structurally_non_tejal",
                "error",
                "Tejal-family corpus requires explicit BMAD/operator exception for S8 full proof.",
            )
        )
    else:
        findings.append(
            Finding(
                "structurally_non_tejal",
                "pass",
                "Corpus is non-Tejal or exception was explicitly allowed.",
            )
        )

    if inventory.pdf_count >= 1:
        findings.append(Finding("has_pdf", "pass", "At least one PDF is present."))
    elif allow_source_gaps and has_gap_ledger:
        findings.append(
            Finding(
                "has_pdf",
                "warning",
                "No PDF source is present; gap accepted by explicit source-gap ledger.",
            )
        )
    else:
        findings.append(Finding("has_pdf", "error", "At least one PDF source is required."))

    if inventory.doc_or_deck_count >= 1:
        findings.append(
            Finding("has_doc_or_deck", "pass", "At least one DOC/DOCX/PPT/PPTX source is present.")
        )
    elif allow_source_gaps and has_gap_ledger:
        findings.append(
            Finding(
                "has_doc_or_deck",
                "warning",
                "No DOC/DOCX/PPT/PPTX source is present; gap accepted by "
                "explicit source-gap ledger.",
            )
        )
    else:
        findings.append(
            Finding(
                "has_doc_or_deck",
                "error",
                "At least one DOC/DOCX/PPT/PPTX source is required.",
            )
        )

    if inventory.image_count >= 1:
        findings.append(Finding("has_image", "pass", "At least one image source is present."))
    elif allow_source_gaps and has_gap_ledger:
        findings.append(
            Finding(
                "has_image",
                "warning",
                "No image source is present; gap accepted by explicit source-gap ledger.",
            )
        )
    else:
        findings.append(Finding("has_image", "error", "At least one image source is required."))

    if inventory.doi_count >= 1:
        findings.append(
            Finding("doi_indexed", "pass", "At least one DOI is present in text-scannable sources.")
        )
    elif allow_source_gaps and has_gap_ledger:
        findings.append(
            Finding(
                "doi_indexed",
                "warning",
                "No DOI appears in text-scannable sources; gap accepted by "
                "explicit source-gap ledger.",
            )
        )
    else:
        findings.append(
            Finding(
                "doi_indexed",
                "error",
                "At least one DOI is required for literature-rich proof.",
            )
        )

    if inventory.url_count >= 1:
        findings.append(
            Finding(
                "has_url_directive",
                "pass",
                "At least one URL appears in text sources.",
            )
        )
    else:
        findings.append(
            Finding(
                "has_url_directive",
                "warning",
                "No URL directive found; ratified criteria say a URL is ideal.",
            )
        )

    findings.extend(
        _attestation_findings(
            operator_named_slug=operator_named_slug,
            expected_slug=inventory.slug,
            operator_knows_cold=operator_knows_cold,
            fresh_to_pipeline=fresh_to_pipeline,
            freshness_exception_rationale=freshness_exception_rationale,
            adequacy_wrinkle=adequacy_wrinkle,
            no_corpus_specific_diffs_acknowledged=no_corpus_specific_diffs_acknowledged,
        )
    )

    outside_diffs = _tracked_diffs_outside_corpus(corpus_path)
    if outside_diffs:
        findings.append(
            Finding(
                "zero_corpus_specific_production_diffs",
                "error",
                "Tracked diffs exist outside the candidate corpus: "
                + ", ".join(outside_diffs[:8]),
            )
        )
    else:
        findings.append(
            Finding(
                "zero_corpus_specific_production_diffs",
                "pass",
                "No tracked diffs outside the candidate corpus were detected.",
            )
        )

    ready = not any(finding.severity == "error" for finding in findings)
    return S8ProofCorpusReport(
        ready=ready,
        inventory=inventory,
        findings=tuple(findings),
    )


def _print_text_report(report: S8ProofCorpusReport) -> None:
    print(f"ready: {str(report.ready).lower()}")
    for key, value in report.inventory.as_dict().items():
        print(f"{key}: {value}")
    for finding in report.findings:
        print(f"{finding.severity.upper()} {finding.check_id}: {finding.message}")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("corpus_path", type=Path)
    parser.add_argument("--operator-named-slug")
    parser.add_argument("--operator-knows-cold", action="store_true")
    parser.add_argument("--fresh-to-pipeline", action="store_true")
    parser.add_argument("--freshness-exception-rationale")
    parser.add_argument("--adequacy-wrinkle")
    parser.add_argument("--no-corpus-specific-diffs-acknowledged", action="store_true")
    parser.add_argument("--allow-tejal-exception", action="store_true")
    parser.add_argument("--allow-source-gaps", action="store_true")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = evaluate_s8_proof_corpus(
        args.corpus_path,
        operator_named_slug=args.operator_named_slug,
        operator_knows_cold=args.operator_knows_cold,
        fresh_to_pipeline=args.fresh_to_pipeline,
        adequacy_wrinkle=args.adequacy_wrinkle,
        no_corpus_specific_diffs_acknowledged=args.no_corpus_specific_diffs_acknowledged,
        allow_tejal_exception=args.allow_tejal_exception,
        allow_source_gaps=args.allow_source_gaps,
        freshness_exception_rationale=args.freshness_exception_rationale,
    )
    if args.json:
        print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    else:
        _print_text_report(report)
    return 0 if report.ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
