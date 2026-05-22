"""Story 34-2 regression tests for wrangler role union and ignored rows."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml

_THIS_DIR = Path(__file__).resolve().parent
_RUNNER_PATH = _THIS_DIR.parent / "run_wrangler.py"
_FIXTURE_DIR = _THIS_DIR / "fixtures" / "wrangler-golden"


def _load_runner():
    spec = importlib.util.spec_from_file_location(
        "texas_run_wrangler_story_34_2_under_test", _RUNNER_PATH
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["texas_run_wrangler_story_34_2_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


_runner = _load_runner()


def _write_directive(tmp_path: Path, body: dict) -> Path:
    path = tmp_path / "directive.yaml"
    path.write_text(yaml.safe_dump(body, sort_keys=False), encoding="utf-8")
    return path


def _source(ref_id: str, role: str, locator: str = "source.md", **extra: object) -> dict:
    payload = {
        "ref_id": ref_id,
        "provider": "local_file",
        "locator": locator,
        "role": role,
        "description": f"{role} source",
    }
    if role != "ignored":
        payload["expected_min_words"] = 1
    payload.update(extra)
    return payload


def _load(tmp_path: Path, sources: list[dict]) -> dict:
    return _runner._load_directive(
        _write_directive(tmp_path, {"run_id": "TEST-34-2", "sources": sources})
    )


@pytest.mark.parametrize(
    "role",
    [
        "primary",
        "supporting",
        "ignored",
        "validation",
        "supplementary",
        "visual-primary",
        "visual-supplementary",
    ],
)
def test_wrangler_accepts_seven_role_union(role: str, tmp_path: Path) -> None:
    sources = [_source("src-primary", "primary")]
    if role == "ignored":
        sources.append(
            _source(
                "src-role",
                role,
                excluded_reason="llm-classified-out-of-scope",
            )
        )
    elif role != "primary":
        sources.append(_source("src-role", role))

    directive = _load(tmp_path, sources)
    assert {source["role"] for source in directive["sources"]} >= {role}


def test_wrangler_rejects_unknown_role(tmp_path: Path) -> None:
    with pytest.raises(_runner.DirectiveError, match="role must be one of"):
        _load(tmp_path, [_source("src-001", "primary"), _source("src-002", "foo")])


def test_ignored_requires_excluded_reason(tmp_path: Path) -> None:
    with pytest.raises(_runner.DirectiveError, match="excluded_reason MUST"):
        _load(tmp_path, [_source("src-001", "primary"), _source("src-002", "ignored")])


@pytest.mark.parametrize(
    "reason",
    [
        "git-marker-file",
        "macos-metadata",
        "windows-metadata",
        "llm-classified-out-of-scope",
    ],
)
def test_ignored_accepts_closed_excluded_reason_enum(
    reason: str, tmp_path: Path
) -> None:
    directive = _load(
        tmp_path,
        [
            _source("src-001", "primary"),
            _source("src-002", "ignored", excluded_reason=reason),
        ],
    )
    assert directive["sources"][1]["excluded_reason"] == reason


def test_ignored_rejects_unknown_excluded_reason(tmp_path: Path) -> None:
    with pytest.raises(_runner.DirectiveError, match="excluded_reason must be one of"):
        _load(
            tmp_path,
            [
                _source("src-001", "primary"),
                _source("src-002", "ignored", excluded_reason="temporary"),
            ],
        )


def test_non_ignored_forbids_excluded_reason(tmp_path: Path) -> None:
    with pytest.raises(_runner.DirectiveError, match="forbidden on non-ignored"):
        _load(
            tmp_path,
            [
                _source("src-001", "primary"),
                _source(
                    "src-002",
                    "supporting",
                    excluded_reason="llm-classified-out-of-scope",
                ),
            ],
        )


def test_text_sources_require_expected_min_words(tmp_path: Path) -> None:
    with pytest.raises(_runner.DirectiveError, match="expected_min_words required"):
        _load(
            tmp_path,
            [
                _source("src-001", "primary"),
                {
                    "ref_id": "src-002",
                    "provider": "local_file",
                    "locator": "support.md",
                    "role": "supporting",
                    "description": "text support",
                },
            ],
        )


def test_binary_supporting_forbids_expected_min_words(tmp_path: Path) -> None:
    with pytest.raises(_runner.DirectiveError, match="forbidden for binary"):
        _load(
            tmp_path,
            [
                _source("src-001", "primary"),
                _source(
                    "src-002",
                    "supporting",
                    locator="diagram.png",
                    expected_min_words=1,
                ),
            ],
        )


def test_ignored_forbids_expected_min_words(tmp_path: Path) -> None:
    with pytest.raises(_runner.DirectiveError, match="forbidden when role=ignored"):
        _load(
            tmp_path,
            [
                _source("src-001", "primary"),
                _source(
                    "src-002",
                    "ignored",
                    excluded_reason="git-marker-file",
                    expected_min_words=1,
                ),
            ],
        )


def test_only_ignored_sources_do_not_satisfy_primary_presence(tmp_path: Path) -> None:
    with pytest.raises(_runner.DirectiveError, match="no role: primary"):
        _load(
            tmp_path,
            [_source("src-001", "ignored", excluded_reason="git-marker-file")],
        )


def test_ignored_rows_are_filtered_before_materialization(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    bundle = tmp_path / "bundle"
    ignored_locator = str(_FIXTURE_DIR / "validation.md")
    directive = _write_directive(
        tmp_path,
        {
            "run_id": "TEST-34-2-IGNORED",
            "sources": [
                {
                    "ref_id": "src-001",
                    "provider": "local_file",
                    "locator": str(_FIXTURE_DIR / "primary.md"),
                    "role": "primary",
                    "description": "primary source",
                    "expected_min_words": 200,
                },
                {
                    "ref_id": "src-ignored",
                    "provider": "local_file",
                    "locator": ignored_locator,
                    "role": "ignored",
                    "description": "ignored source",
                    "excluded_reason": "llm-classified-out-of-scope",
                },
            ],
        },
    )

    exit_code = _runner.main(["--directive", str(directive), "--bundle-dir", str(bundle)])
    assert exit_code == _runner.EXIT_COMPLETE
    err = capsys.readouterr().err
    assert "filtered ignored source" in err
    assert "src-ignored" in err

    result = yaml.safe_load((bundle / "result.yaml").read_text(encoding="utf-8"))
    assert [material["ref_id"] for material in result["materials"]] == ["src-001"]

    metadata = json.loads((bundle / "metadata.json").read_text(encoding="utf-8"))
    assert [row["ref_id"] for row in metadata["provenance"]] == ["src-001"]

    extracted = (bundle / "extracted.md").read_text(encoding="utf-8")
    assert "ignored source" not in extracted
    assert "src-ignored" not in extracted
