from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

from scripts.utilities.operator_directives_defaults import (
    DirectiveDefaultSource,
    discover_step_02a_directives_default,
    render_step_02a_default_prompt,
    write_operator_directives_from_choice,
)


def _run_constants(
    bundle: Path,
    *,
    run_id: str,
    lesson_slug: str = "lesson-alpha",
) -> None:
    bundle.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": run_id,
        "lesson_slug": lesson_slug,
        "bundle_path": bundle.as_posix(),
        "primary_source_file": "source.pdf",
        "optional_context_assets": [],
        "theme_selection": "theme-a",
        "theme_paramset_key": "theme-a-default",
        "execution_mode": "tracked/default",
        "quality_preset": "production",
    }
    (bundle / "run-constants.yaml").write_text(yaml.safe_dump(payload), encoding="utf-8")


def _directives(run_id: str, focus: str = "Focus on Part 1.") -> str:
    return "\n".join(
        [
            f"run_id: {run_id}",
            "timestamp: 2026-04-28T10:00:00Z",
            "poll_started_utc: 2026-04-28T09:57:00Z",
            "reply_eligible_utc: 2026-04-28T10:00:00Z",
            "poll_close_utc: 2026-04-28T10:12:00Z",
            "poll_status: submitted",
            "operator: Juanl",
            "focus_directives:",
            f"  - {focus}",
            "exclusion_directives:",
            "  - Ignore appendix.",
            "special_treatment_directives:",
            "  - Preserve diagram.",
            "",
        ]
    )


def _write_directives(bundle: Path, *, run_id: str, focus: str = "Focus on Part 1.") -> Path:
    path = bundle / "operator-directives.md"
    path.write_text(_directives(run_id, focus), encoding="utf-8")
    return path


def test_discovers_latest_same_lesson_prior_directives(tmp_path: Path) -> None:
    root = tmp_path / "source-bundles"
    current = root / "current"
    older = root / "older"
    newer = root / "newer"
    other_lesson = root / "other-lesson"
    for bundle, run_id, slug in (
        (current, "RUN-CURRENT", "lesson-alpha"),
        (older, "RUN-OLDER", "lesson-alpha"),
        (newer, "RUN-NEWER", "lesson-alpha"),
        (other_lesson, "RUN-OTHER", "lesson-beta"),
    ):
        _run_constants(bundle, run_id=run_id, lesson_slug=slug)
        if bundle != current:
            _write_directives(bundle, run_id=run_id)

    os.utime(older / "operator-directives.md", (1000, 1000))
    os.utime(newer / "operator-directives.md", (2000, 2000))
    os.utime(other_lesson / "operator-directives.md", (3000, 3000))

    default = discover_step_02a_directives_default(current)

    assert default is not None
    assert default.source == DirectiveDefaultSource.PRIOR_RUN
    assert default.run_id == "RUN-NEWER"
    assert default.bundle_path == newer
    assert "focus_directives" in default.content


def test_rendered_named_defaults_include_source_attribution_and_sections(tmp_path: Path) -> None:
    root = tmp_path / "source-bundles"
    current = root / "current"
    prior = root / "prior"
    _run_constants(current, run_id="RUN-CURRENT")
    _run_constants(prior, run_id="RUN-PRIOR")
    _write_directives(prior, run_id="RUN-PRIOR")

    default = discover_step_02a_directives_default(current)
    assert default is not None

    rendered = render_step_02a_default_prompt(default, bundle_root=current)

    assert "RUN-PRIOR" in rendered
    assert "source bundle:" in rendered
    assert "operator-directives.md" in rendered
    assert "focus_directives" in rendered
    assert "exclusion_directives" in rendered
    assert "special_treatment_directives" in rendered


@pytest.mark.parametrize("choice", ["accept", "modify", "replace"])
def test_explicit_accept_modify_replace_write_paths(tmp_path: Path, choice: str) -> None:
    root = tmp_path / "source-bundles"
    current = root / "current"
    prior = root / "prior"
    _run_constants(current, run_id="RUN-CURRENT")
    _run_constants(prior, run_id="RUN-PRIOR")
    _write_directives(prior, run_id="RUN-PRIOR")

    default = discover_step_02a_directives_default(current)
    assert default is not None

    modified = _directives("RUN-CURRENT", "Modified directive.")
    replacement = _directives("RUN-CURRENT", "Replacement directive.")
    written = write_operator_directives_from_choice(
        current,
        choice=choice,
        default=default,
        modified_content=modified if choice == "modify" else None,
        replacement_content=replacement if choice == "replace" else None,
    )

    text = written.read_text(encoding="utf-8")
    if choice == "accept":
        assert "RUN-PRIOR" in text
    elif choice == "modify":
        assert "Modified directive." in text
    else:
        assert "Replacement directive." in text


def test_no_prior_bundle_preserves_no_default_path(tmp_path: Path) -> None:
    root = tmp_path / "source-bundles"
    current = root / "current"
    _run_constants(current, run_id="RUN-CURRENT")

    assert discover_step_02a_directives_default(current) is None


def test_current_bundle_directives_take_precedence_over_older_defaults(tmp_path: Path) -> None:
    root = tmp_path / "source-bundles"
    current = root / "current"
    prior = root / "prior"
    _run_constants(current, run_id="RUN-CURRENT")
    _run_constants(prior, run_id="RUN-PRIOR")
    _write_directives(current, run_id="RUN-CURRENT")
    _write_directives(prior, run_id="RUN-PRIOR")

    default = discover_step_02a_directives_default(current)

    assert default is not None
    assert default.source == DirectiveDefaultSource.CURRENT_RUN
    assert default.run_id == "RUN-CURRENT"
    assert default.bundle_path == current


def test_invalid_prior_directives_falls_through_to_no_prior_path(tmp_path: Path) -> None:
    root = tmp_path / "source-bundles"
    current = root / "current"
    prior = root / "prior"
    _run_constants(current, run_id="RUN-CURRENT")
    _run_constants(prior, run_id="RUN-PRIOR")
    (prior / "operator-directives.md").write_text("run_id: RUN-PRIOR\n", encoding="utf-8")

    assert discover_step_02a_directives_default(current) is None


def test_deterministic_tiebreak_on_identical_mtime(tmp_path: Path) -> None:
    root = tmp_path / "source-bundles"
    current = root / "current"
    prior_a = root / "prior-a"
    prior_b = root / "prior-b"
    _run_constants(current, run_id="RUN-CURRENT")
    _run_constants(prior_a, run_id="RUN-100")
    _run_constants(prior_b, run_id="RUN-200")
    _write_directives(prior_a, run_id="RUN-100")
    _write_directives(prior_b, run_id="RUN-200")
    os.utime(prior_a / "operator-directives.md", (2000, 2000))
    os.utime(prior_b / "operator-directives.md", (2000, 2000))

    default = discover_step_02a_directives_default(current)

    assert default is not None
    assert default.run_id == "RUN-200"
