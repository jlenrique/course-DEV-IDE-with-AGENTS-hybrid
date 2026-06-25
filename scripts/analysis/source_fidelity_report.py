"""Source-fidelity report CLI — L2 numeric provenance audit (WARN-ONLY).

Runs the L2 source-provenance audit
(`app.specialists._shared.source_fidelity_audit.audit_numeric_provenance`) on a
trial run. It is READ-ONLY on the run except for writing the report into the
run's ``exports/`` directory.

It loads:
  - the delivered NARRATION from the trial's
    ``exports/segment-manifest-storyboard-b.yaml`` (segments' ``narration_text``
    joined), and
  - the SOURCE corpus (default
    ``course-content/courses/tejal-apc-c1-m1-p2-trends/slides/*.md`` — all slide
    markdown concatenated).

NON-GATING: this is measurement-only. The audit never blocks; the report is
written and printed for human review.

Run:
    PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe \
        scripts/analysis/source_fidelity_report.py \
        --trial-id c2c6dcbf-5734-42d0-b525-2ea3212aa3f0
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import yaml  # noqa: E402

from app.specialists._shared.source_fidelity_audit import (  # noqa: E402
    audit_numeric_provenance,
)

DEFAULT_CORPUS_DIR = (
    REPO_ROOT
    / "course-content"
    / "courses"
    / "tejal-apc-c1-m1-p2-trends"
    / "slides"
)


def _runs_dir() -> Path:
    return REPO_ROOT / "state" / "config" / "runs"


def load_narration(trial_id: str) -> str:
    """Join all segments' ``narration_text`` from the storyboard-b manifest."""
    manifest = (
        _runs_dir()
        / trial_id
        / "exports"
        / "segment-manifest-storyboard-b.yaml"
    )
    if not manifest.exists():
        raise FileNotFoundError(f"manifest not found: {manifest}")
    data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    segments = data.get("segments", []) if isinstance(data, dict) else []
    parts = [
        str(seg.get("narration_text", "")).strip()
        for seg in segments
        if isinstance(seg, dict) and seg.get("narration_text")
    ]
    return "\n\n".join(p for p in parts if p)


def load_source_corpus(corpus_dir: Path) -> str:
    """Concatenate all ``*.md`` slide markdown in ``corpus_dir`` (sorted)."""
    if not corpus_dir.exists():
        raise FileNotFoundError(f"corpus dir not found: {corpus_dir}")
    md_files = sorted(corpus_dir.glob("*.md"))
    if not md_files:
        raise FileNotFoundError(f"no *.md slides in corpus dir: {corpus_dir}")
    return "\n\n".join(f.read_text(encoding="utf-8") for f in md_files)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trial-id", required=True, help="trial run id")
    parser.add_argument(
        "--corpus",
        default=None,
        help=(
            "source corpus directory of *.md slides "
            f"(default: {DEFAULT_CORPUS_DIR})"
        ),
    )
    args = parser.parse_args(argv)

    corpus_dir = Path(args.corpus) if args.corpus else DEFAULT_CORPUS_DIR

    narration_text = load_narration(args.trial_id)
    source_text = load_source_corpus(corpus_dir)

    report = audit_numeric_provenance(narration_text, source_text)
    report["trial_id"] = args.trial_id
    report["corpus_dir"] = str(corpus_dir)

    exports_dir = _runs_dir() / args.trial_id / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)
    out_path = exports_dir / "source-fidelity-report.json"
    out_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\n[written] {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
