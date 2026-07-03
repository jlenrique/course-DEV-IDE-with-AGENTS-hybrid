"""RED-first reliability spine for the gh-pages styleguide-picker emitter/decoder.

Arc ``styleguide-picker-gh-pages-publish`` (green-light record 2026-07-03). This
file exercises the amendment ledger's decode-side invariants (A3/A4/A5), the
JS<->Python anti-drift parity tooth, and the static-page markup contract
(A1/A2/A6). Authored before ``picker_html_emitter.py`` existed
(ModuleNotFoundError RED recorded in the run report).
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from app.marcus.orchestrator.picker_html_emitter import (
    PICKER_ENCODER_JS,
    SELECTION_CODE_GRAMMAR,
    build_selection_code,
    decode_picker_selection_code,
    render_picker_static_html,
)
from app.marcus.orchestrator.styleguide_picker import PickerError

GOLDEN_PATH = Path(__file__).with_name("picker_selection_golden.json")
RUN_TAG = "abc12345"


# --------------------------------------------------------------------- fixtures
def _write_ssot(tmp_path: Path) -> Path:
    """A minimal but schema-faithful SSOT with each lifecycle/visibility tier."""
    ssot = tmp_path / "gamma-style-guides.yaml"
    payload = {
        "schema_version": "1.0",
        "style_guides": {
            "alpha-style": {
                "lifecycle": "permanent",
                "presentation": {"display_name": "Alpha", "distinguishing": "clean"},
            },
            "beta-style": {
                "lifecycle": "permanent",
                "presentation": {"display_name": "Beta", "distinguishing": "bold"},
            },
            "gamma-candidate": {
                "lifecycle": "candidate",
                "presentation": {"display_name": "Gamma", "distinguishing": "trial"},
            },
            "delta-deprecated": {
                "lifecycle": "deprecated",
                "presentation": {"display_name": "Delta", "distinguishing": "retired"},
            },
            "epsilon-probe": {
                "lifecycle": "candidate",
                "presentation": {
                    "display_name": "Epsilon",
                    "distinguishing": "scaffold",
                    "visibility": "probe",
                },
            },
        },
    }
    ssot.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return ssot


def _roster() -> list[dict]:
    return [
        {
            "name": "alpha-style",
            "display_name": "Alpha",
            "distinguishing": "clean",
            "narrative": {},
            "probe": False,
            "lifecycle": "permanent",
            "card_dimensions": "",
            "thumbnail_ref": None,
            "example_url": None,
            "last_used": None,
        },
        {
            "name": "gamma-candidate",
            "display_name": "Gamma",
            "distinguishing": "trial",
            "narrative": {},
            "probe": False,
            "lifecycle": "candidate",
            "card_dimensions": "",
            "thumbnail_ref": None,
            "example_url": None,
            "last_used": None,
        },
    ]


# ---------------------------------------------------------------- A5 reject matrix
def test_decode_rejects_missing_sgp_prefix(tmp_path: Path) -> None:
    ssot = _write_ssot(tmp_path)
    with pytest.raises(PickerError, match="(?i)SGP-"):
        decode_picker_selection_code(
            "XXX-abc12345-A:alpha-style", expected_run_tag=RUN_TAG, ssot_path=ssot
        )


def test_decode_rejects_charset_violation(tmp_path: Path) -> None:
    ssot = _write_ssot(tmp_path)
    with pytest.raises(PickerError, match="(?i)character|charset"):
        decode_picker_selection_code(
            "SGP-abc12345-A:alpha-style!", expected_run_tag=RUN_TAG, ssot_path=ssot
        )


def test_decode_rejects_over_length_before_parsing(tmp_path: Path) -> None:
    ssot = _write_ssot(tmp_path)
    huge = "SGP-abc12345-A:" + ("a" * 300)
    with pytest.raises(PickerError, match="(?i)length|256|long"):
        decode_picker_selection_code(huge, expected_run_tag=RUN_TAG, ssot_path=ssot)


def test_decode_rejects_bad_slot_regex_uppercase_slug(tmp_path: Path) -> None:
    ssot = _write_ssot(tmp_path)
    # STRICT case: an uppercased slug must not be coerced to a match.
    with pytest.raises(PickerError, match="(?i)slot|slug"):
        decode_picker_selection_code(
            "SGP-abc12345-A:Alpha-Style", expected_run_tag=RUN_TAG, ssot_path=ssot
        )


def test_decode_requires_slot_a(tmp_path: Path) -> None:
    ssot = _write_ssot(tmp_path)
    with pytest.raises(PickerError, match="(?i)slot a|version a|required"):
        decode_picker_selection_code(
            "SGP-abc12345-B:beta-style", expected_run_tag=RUN_TAG, ssot_path=ssot
        )


def test_decode_rejects_duplicate_slot_label(tmp_path: Path) -> None:
    ssot = _write_ssot(tmp_path)
    with pytest.raises(PickerError, match="(?i)duplicate"):
        decode_picker_selection_code(
            "SGP-abc12345-A:alpha-style A:beta-style",
            expected_run_tag=RUN_TAG,
            ssot_path=ssot,
        )


def test_decode_rejects_unknown_slug(tmp_path: Path) -> None:
    ssot = _write_ssot(tmp_path)
    with pytest.raises(PickerError, match="no-such-style"):
        decode_picker_selection_code(
            "SGP-abc12345-A:no-such-style", expected_run_tag=RUN_TAG, ssot_path=ssot
        )


def test_decode_rejects_deprecated_slug(tmp_path: Path) -> None:
    ssot = _write_ssot(tmp_path)
    with pytest.raises(PickerError, match="(?i)deprecated"):
        decode_picker_selection_code(
            "SGP-abc12345-A:delta-deprecated", expected_run_tag=RUN_TAG, ssot_path=ssot
        )


def test_decode_rejects_probe_slug(tmp_path: Path) -> None:
    ssot = _write_ssot(tmp_path)
    with pytest.raises(PickerError, match="(?i)probe"):
        decode_picker_selection_code(
            "SGP-abc12345-A:epsilon-probe", expected_run_tag=RUN_TAG, ssot_path=ssot
        )


def test_decode_rejects_empty_and_whitespace(tmp_path: Path) -> None:
    ssot = _write_ssot(tmp_path)
    for bad in ("", "   ", "\t\n"):
        with pytest.raises(PickerError, match="(?i)empty"):
            decode_picker_selection_code(bad, expected_run_tag=RUN_TAG, ssot_path=ssot)


def test_decode_rejects_embedded_whitespace(tmp_path: Path) -> None:
    ssot = _write_ssot(tmp_path)
    # a double inter-slot space is embedded whitespace, never single-space-trimmed.
    with pytest.raises(PickerError, match="(?i)slot|whitespace"):
        decode_picker_selection_code(
            "SGP-abc12345-A:alpha-style  B:beta-style",
            expected_run_tag=RUN_TAG,
            ssot_path=ssot,
        )


def test_decode_rejects_b_equals_a(tmp_path: Path) -> None:
    ssot = _write_ssot(tmp_path)
    with pytest.raises(PickerError, match="(?i)same|identical|both"):
        decode_picker_selection_code(
            "SGP-abc12345-A:alpha-style B:alpha-style",
            expected_run_tag=RUN_TAG,
            ssot_path=ssot,
        )


def test_decode_trims_leading_trailing_whitespace(tmp_path: Path) -> None:
    ssot = _write_ssot(tmp_path)
    got = decode_picker_selection_code(
        "  SGP-abc12345-A:alpha-style  ", expected_run_tag=RUN_TAG, ssot_path=ssot
    )
    assert got == {"A": "alpha-style"}


# ---------------------------------------------------------------- A3 run_tag bind
def test_decode_rejects_run_tag_mismatch(tmp_path: Path) -> None:
    ssot = _write_ssot(tmp_path)
    with pytest.raises(PickerError, match="(?i)stale|foreign|run"):
        decode_picker_selection_code(
            "SGP-otherrun-A:alpha-style", expected_run_tag=RUN_TAG, ssot_path=ssot
        )


def test_decode_rejects_bad_run_tag_charset(tmp_path: Path) -> None:
    ssot = _write_ssot(tmp_path)
    # ':' is inside the code charset whitelist but not a legal run_tag character.
    with pytest.raises(PickerError, match="(?i)run.tag|tag"):
        decode_picker_selection_code(
            "SGP-ab:12-A:alpha-style", expected_run_tag="ab:12", ssot_path=ssot
        )


# ---------------------------------------------------------------- A4 no mis-mapping
def test_transposition_asymmetry(tmp_path: Path) -> None:
    ssot = _write_ssot(tmp_path)
    code = build_selection_code(RUN_TAG, {"A": "alpha-style", "B": "beta-style"})
    got = decode_picker_selection_code(code, expected_run_tag=RUN_TAG, ssot_path=ssot)
    assert got == {"A": "alpha-style", "B": "beta-style"}
    assert got != {"A": "beta-style", "B": "alpha-style"}


# ---------------------------------------------------------------- round-trip
def test_round_trip_a_only(tmp_path: Path) -> None:
    ssot = _write_ssot(tmp_path)
    picks = {"A": "alpha-style"}
    code = build_selection_code(RUN_TAG, picks)
    assert decode_picker_selection_code(
        code, expected_run_tag=RUN_TAG, ssot_path=ssot
    ) == picks


def test_round_trip_a_and_b(tmp_path: Path) -> None:
    ssot = _write_ssot(tmp_path)
    picks = {"A": "alpha-style", "B": "beta-style"}
    code = build_selection_code(RUN_TAG, picks)
    assert decode_picker_selection_code(
        code, expected_run_tag=RUN_TAG, ssot_path=ssot
    ) == picks


# ---------------------------------------------------------------- A5 parity tooth
def _golden() -> list[dict]:
    return json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))


def test_python_twin_matches_golden() -> None:
    for row in _golden():
        assert build_selection_code(row["run_tag"], row["picks"]) == row["code"]


def test_decoder_accepts_golden(tmp_path: Path) -> None:
    ssot = _write_ssot(tmp_path)
    for row in _golden():
        got = decode_picker_selection_code(
            row["code"], expected_run_tag=row["run_tag"], ssot_path=ssot
        )
        assert got == row["picks"]


def test_grammar_constant_is_frozen_shape() -> None:
    # The grammar lives in ONE place; both encoder + decoder reference it.
    assert SELECTION_CODE_GRAMMAR == "SGP-{run_tag}-A:{slug}[ B:{slug}]"


def test_js_encoder_matches_python_twin_via_node() -> None:
    """Anti-drift tooth: the embedded JS ``buildSelectionCode`` must emit exactly
    what the Python twin (and the golden fixture) emit."""
    node = shutil.which("node")
    if node is None:
        pytest.skip("node not available; Python-twin/golden parity still covers the tooth")
    golden = _golden()
    harness = (
        PICKER_ENCODER_JS
        + "\nconst rows = "
        + json.dumps(golden)
        + ";\n"
        + "const out = rows.map(r => buildSelectionCode(r.run_tag, r.picks));\n"
        + "process.stdout.write(JSON.stringify(out));\n"
    )
    result = subprocess.run(
        [node, "-e", harness], capture_output=True, text=True, timeout=30, check=True
    )
    emitted = json.loads(result.stdout)
    assert emitted == [row["code"] for row in golden]


# ---------------------------------------------------------------- A1/A2/A6 markup
def test_static_html_is_complete_document() -> None:
    html = render_picker_static_html(_roster(), run_tag=RUN_TAG)
    assert html.lstrip().lower().startswith("<!doctype html>")
    assert "</html>" in html
    assert "<link" not in html.lower()
    assert "<script src" not in html.lower()


def test_static_html_bakes_run_tag_and_encoder() -> None:
    html = render_picker_static_html(_roster(), run_tag=RUN_TAG)
    assert RUN_TAG in html
    assert "function buildSelectionCode" in html


def test_static_html_versions_radiogroup_in_words() -> None:
    html = render_picker_static_html(_roster(), run_tag=RUN_TAG)
    assert 'role="radiogroup"' in html
    assert "1 version" in html
    assert "2 versions" in html


def test_static_html_copy_button_disabled_until_pick() -> None:
    html = render_picker_static_html(_roster(), run_tag=RUN_TAG)
    assert 'aria-disabled="true"' in html
    # a readonly, always-visible selectable code surface (A2)
    assert "readonly" in html
    assert 'aria-live="polite"' in html


def test_static_html_shows_candidate_chip() -> None:
    html = render_picker_static_html(_roster(), run_tag=RUN_TAG)
    assert "CANDIDATE" in html
    assert "thumbnails/" in html or "no live render" in html


# ---------------------------------------------------------- MUST-1 producer run_tag guard
@pytest.mark.parametrize(
    "bad_tag",
    [
        "apc-c1m1",  # hyphen -> decoder partition('-') mis-split (fail-late)
        "../evil",  # path traversal into the publish subdir / receipt path
        "</script><script>alert(1)",  # injection: json.dumps does NOT neutralize </script>
        "",  # empty
        "run tag",  # embedded whitespace
    ],
)
def test_build_selection_code_rejects_bad_run_tag(bad_tag: str) -> None:
    with pytest.raises(PickerError, match="(?i)run_tag|malformed"):
        build_selection_code(bad_tag, {"A": "alpha-style"})


@pytest.mark.parametrize(
    "bad_tag",
    ["apc-c1m1", "../evil", "</script><script>alert(1)", "", "run tag"],
)
def test_render_static_html_rejects_bad_run_tag(bad_tag: str) -> None:
    with pytest.raises(PickerError, match="(?i)run_tag|malformed"):
        render_picker_static_html(_roster(), run_tag=bad_tag)
