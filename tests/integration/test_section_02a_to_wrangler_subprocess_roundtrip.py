"""Section 02A to Texas wrangler subprocess round-trip integration ratchet.

AC-34-1-D mock-surface audit:
- No mocks are used in this test module.
- The upstream LLM call is not exercised; fixture replay uses the committed
  Trial-3 attempt-2 forensic directive, so no mock bypasses the Section 02A to
  wrangler boundary.
- The wrangler subprocess is real, the directive write path is real, the
  Section 02A Directive model is real, and no translator layer remains.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from app.composers.section_02a.directive_model import Directive

REPO_ROOT = Path(__file__).resolve().parents[2]
WRANGLER_SCRIPT = (
    REPO_ROOT / "skills" / "bmad-agent-texas" / "scripts" / "run_wrangler.py"
)
FORENSIC_DIRECTIVE_FIXTURE = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "integration"
    / "section_02a"
    / "forensic_directive_trial_3_attempt_2.yaml"
)
FORENSIC_DIRECTIVE_SHA256 = (
    "351a57fbe12aff4a49349c4a646618d92ae38a798ec53eee61668f74f8bbd703"
)


def test_forensic_directive_round_trips_through_wrangler_subprocess(
    tmp_path: Path,
) -> None:
    """AC-34-1-A/B: forensic directive passes real wrangler subprocess."""

    if not FORENSIC_DIRECTIVE_FIXTURE.exists():
        pytest.skip(
            "Forensic Trial-3 attempt-2 directive fixture is missing; copy from "
            "state/config/runs/6a3393f8-f369-4a30-b7c1-b50c60c1d1a2/directive.yaml."
        )

    fixture_sha = hashlib.sha256(FORENSIC_DIRECTIVE_FIXTURE.read_bytes()).hexdigest()
    assert fixture_sha == FORENSIC_DIRECTIVE_SHA256

    forensic_data = yaml.safe_load(
        FORENSIC_DIRECTIVE_FIXTURE.read_text(encoding="utf-8")
    )
    directive = Directive.model_validate(forensic_data)

    directive_yaml_path = tmp_path / "directive.yaml"
    directive_yaml_path.write_text(
        yaml.safe_dump(directive.model_dump(mode="json"), sort_keys=False),
        encoding="utf-8",
    )

    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()

    result = subprocess.run(
        [
            sys.executable,
            str(WRANGLER_SCRIPT),
            "--directive",
            str(directive_yaml_path),
            "--bundle-dir",
            str(bundle_dir),
            "--json",
        ],
        cwd=Path(directive.corpus_dir),
        text=True,
        capture_output=True,
        check=False,
        timeout=60,
    )

    assert result.returncode in {0, 10}, (
        f"Wrangler exited with code {result.returncode}: stdout={result.stdout!r} "
        f"stderr={result.stderr!r}"
    )

    result_yaml = yaml.safe_load(
        (bundle_dir / "result.yaml").read_text(encoding="utf-8")
    )
    assert result_yaml.get("status") in {"complete", "complete_with_warnings"}
    assert result_yaml.get("blocking_issues") == []
    assert "materials" in result_yaml
    assert len(result_yaml["materials"]) >= 1

    primary_rows = [
        material for material in result_yaml["materials"] if material.get("role") == "primary"
    ]
    assert len(primary_rows) >= 1
    assert all("word_count" in row for row in primary_rows)
    assert any(row.get("content_path") == "extracted.md" for row in primary_rows)

    metadata_path = bundle_dir / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    # Story 34-4 extension: sme_refs[] additive emission verification.
    assert "sme_refs" in metadata, (
        f"metadata.json missing 'sme_refs' key: {metadata.keys()}"
    )
    assert len(metadata["sme_refs"]) >= 1, (
        f"metadata.json.sme_refs is empty: {metadata['sme_refs']!r}"
    )

    for i, entry in enumerate(metadata["sme_refs"]):
        assert set(entry.keys()) == {"source_id", "path", "content_digest"}, (
            f"sme_refs[{i}] keys drift: expected {{source_id, path, content_digest}}, "
            f"got {set(entry.keys())}"
        )
        assert isinstance(entry["source_id"], str) and entry["source_id"], (
            f"sme_refs[{i}].source_id must be non-empty string: "
            f"{entry['source_id']!r}"
        )
        assert entry["path"] is None or isinstance(entry["path"], str), (
            f"sme_refs[{i}].path must be str or None: {entry['path']!r}"
        )
        assert (
            isinstance(entry["content_digest"], str)
            and len(entry["content_digest"]) == 64
        ), (
            f"sme_refs[{i}].content_digest must be 64-char sha256 hex: "
            f"{entry['content_digest']!r}"
        )

    assert "provenance" in metadata, "Story 34-4 MUST preserve provenance key"
    assert len(metadata["provenance"]) == len(metadata["sme_refs"]), (
        "sme_refs and provenance must have same cardinality (one entry per outcome)"
    )

    materials_ref_ids = {m["ref_id"] for m in result_yaml["materials"]}
    sme_refs_source_ids = {e["source_id"] for e in metadata["sme_refs"]}
    assert materials_ref_ids == sme_refs_source_ids, (
        f"materials.ref_id set != sme_refs.source_id set: "
        f"materials={materials_ref_ids} sme_refs={sme_refs_source_ids}"
    )
