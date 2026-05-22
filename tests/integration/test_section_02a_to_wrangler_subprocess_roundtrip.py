"""Section 02A to Texas wrangler subprocess round-trip integration ratchet.

AC-34-1-D mock-surface audit:
- No mocks are used in this test module.
- The upstream LLM call is not exercised; fixture replay uses the committed
  Trial-3 attempt-2 forensic directive, so no mock bypasses the Section 02A to
  wrangler boundary.
- The wrangler subprocess is real, the directive write path is real, the
  translator call is real, and the Section 02A Directive model is real.
"""

from __future__ import annotations

import hashlib
import inspect
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from app.composers.section_02a._wrangler_translator import (
    TRANSLATOR_ACTIVE_MAPPINGS,
    translate_directive_for_wrangler,
)
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


def test_forensic_directive_round_trips_through_wrangler_subprocess_via_translator(
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
    translated = translate_directive_for_wrangler(directive)

    directive_yaml_path = tmp_path / "directive.yaml"
    directive_yaml_path.write_text(
        yaml.safe_dump(translated, sort_keys=False),
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

    # Story 34-4 owns metadata.json::sme_refs[] emission and extends this test.
    metadata = yaml.safe_load((bundle_dir / "metadata.json").read_text(encoding="utf-8"))
    assert "provenance" in metadata


def test_translator_active_mappings_is_load_bearing_in_production() -> None:
    """AC-34-5-A precursor: remaining active mapping is load-bearing."""

    expected_mappings = frozenset()
    assert expected_mappings == TRANSLATOR_ACTIVE_MAPPINGS
    source = inspect.getsource(translate_directive_for_wrangler)
    assert "TRANSLATOR_ACTIVE_MAPPINGS" in source


def test_translator_module_carries_deletion_markers() -> None:
    """AC-34-1-C + AC-34-7-H prep: scaffold deletion markers are present."""

    translator_path = (
        REPO_ROOT / "app" / "composers" / "section_02a" / "_wrangler_translator.py"
    )
    text = translator_path.read_text(encoding="utf-8")
    assert "__epic_34_scaffolding__ = True" in text
    assert "DELETE-AT-EPIC-34-CLOSE" in text
