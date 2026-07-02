"""Capture-layer portability contract for vision recordings (carried-findings D-C2).

The runtime provider (`app.specialists.vision.provider.perceive_png`) sets
``source_png_path`` ABSOLUTE via ``str(path)`` — correct at runtime and
deliberately UNTOUCHED. The live-roundtrip capture harness must normalize that
path to repo-relative posix form BEFORE writing a recording, so committed
fixtures stay portable across machines/drives. Out-of-repo-root paths FAIL
LOUD at capture time (party-ratified: Murat over warn-fallback).

Also carries Winston's fixture-hygiene guard: no committed recording under
``tests/fixtures/vision/recordings/`` may contain a machine-absolute path
(drive-letter, backslash, or leading-'/' POSIX-absolute) in its
``response.source_png_path`` / ``_provenance.source_png`` fields; corrupt
non-object sections yield violation rows instead of crashing the guard.

All tests here are hermetic — no live calls, no network.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from vision_capture_support import normalize_capture_response_paths

REPO_ROOT = Path(__file__).resolve().parents[3]
RECORDINGS_DIR = REPO_ROOT / "tests" / "fixtures" / "vision" / "recordings"

# Drive-letter prefix (C:\ or C:/) — the Windows-absolute smell that made
# recaptured recordings unportable.
_DRIVE_LETTER_RE = re.compile(r"[A-Za-z]:[\\/]")


# ---------------------------------------------------------------------------
# Branch 1: png inside repo root -> normalized to repo-relative posix
# ---------------------------------------------------------------------------


def test_normalizes_absolute_inside_repo_path_to_relative_posix(
    tmp_path: Path,
) -> None:
    fake_root = tmp_path / "repo"
    png = fake_root / "runs" / "compositor" / "visuals" / "slide-01.png"
    png.parent.mkdir(parents=True)
    png.write_bytes(b"png-bytes")

    response = {
        "slide_id": "slide-01",
        "source_png_path": str(png),  # absolute, native separators
        "confidence": "HIGH",
    }
    out = normalize_capture_response_paths(response, repo_root=fake_root)

    assert out is response, "helper mutates-in-place and returns the same dict"
    assert out["source_png_path"] == "runs/compositor/visuals/slide-01.png"
    assert "\\" not in out["source_png_path"]
    assert not _DRIVE_LETTER_RE.search(out["source_png_path"])
    # Untouched sibling keys survive.
    assert out["slide_id"] == "slide-01"
    assert out["confidence"] == "HIGH"


def test_posix_styled_absolute_path_is_normalized_against_repo_root(
    tmp_path: Path,
) -> None:
    """A repo-relative input resolves against cwd, NOT repo root — so the
    helper's resolve()-both-sides contract only guarantees correctness for
    absolute inputs; a relative input that happens to resolve inside the repo
    root is normalized, otherwise it fails loud. Pin the absolute-input
    happy path with a posix-styled absolute string too."""
    fake_root = tmp_path / "repo"
    png = fake_root / "visuals" / "s.png"
    png.parent.mkdir(parents=True)
    png.write_bytes(b"x")

    response = {"source_png_path": str(png).replace("\\", "/")}
    out = normalize_capture_response_paths(response, repo_root=fake_root)
    assert out["source_png_path"] == "visuals/s.png"


@pytest.mark.parametrize("raw", ["", "   "])
def test_fails_loud_on_empty_or_whitespace_source_png_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, raw: str
) -> None:
    """Empty/whitespace path must FAIL LOUD, never silently normalize.

    Defect pinned: ``Path("").resolve()`` is the CWD, so an empty
    ``source_png_path`` used to silently write ``"."`` (or cwd-relative
    garbage) into the recording instead of raising.
    """
    fake_root = tmp_path / "repo"
    fake_root.mkdir()
    monkeypatch.chdir(fake_root)

    response = {"source_png_path": raw}
    with pytest.raises(ValueError, match="empty/whitespace"):
        normalize_capture_response_paths(response, repo_root=fake_root)


def test_fails_loud_when_path_is_repo_root_itself(tmp_path: Path) -> None:
    """The repo root itself normalizes to ``"."`` — not a file, FAIL LOUD.

    Defect pinned: a raw value equal to the repo root used to silently
    write ``"."`` into the recording.
    """
    fake_root = tmp_path / "repo"
    fake_root.mkdir()

    response = {"source_png_path": str(fake_root)}
    with pytest.raises(ValueError, match="repo root itself"):
        normalize_capture_response_paths(response, repo_root=fake_root)


# ---------------------------------------------------------------------------
# Branch 2: png outside repo root -> FAIL LOUD
# ---------------------------------------------------------------------------


def test_fails_loud_when_png_outside_repo_root(tmp_path: Path) -> None:
    fake_root = tmp_path / "repo"
    fake_root.mkdir()
    outside_png = tmp_path / "elsewhere" / "slide-01.png"
    outside_png.parent.mkdir(parents=True)
    outside_png.write_bytes(b"png-bytes")

    response = {"source_png_path": str(outside_png)}
    with pytest.raises(ValueError, match="cannot be made repo-relative"):
        normalize_capture_response_paths(response, repo_root=fake_root)


def test_missing_source_png_path_key_is_a_noop(tmp_path: Path) -> None:
    response = {"slide_id": "slide-01"}
    out = normalize_capture_response_paths(response, repo_root=tmp_path)
    assert out == {"slide_id": "slide-01"}


# ---------------------------------------------------------------------------
# Winston's fixture-hygiene guard: committed recordings must be portable
# ---------------------------------------------------------------------------


def test_committed_recordings_carry_no_machine_absolute_paths() -> None:
    recordings = sorted(RECORDINGS_DIR.glob("*.json"))
    assert recordings, f"no committed recordings found under {RECORDINGS_DIR}"

    violations: list[str] = []
    for recording in recordings:
        data = json.loads(recording.read_text(encoding="utf-8"))
        fields: dict[str, str | None] = {}
        for section_name, field_key in (
            ("response", "source_png_path"),
            ("_provenance", "source_png"),
        ):
            section = data.get(section_name, {})
            if not isinstance(section, dict):
                # A corrupt recording must yield a clean violation row, not
                # crash the guard with AttributeError.
                violations.append(
                    f"{recording.name}: {section_name} is not a JSON object "
                    f"(got {type(section).__name__})"
                )
                continue
            fields[f"{section_name}.{field_key}"] = section.get(field_key)
        for field_name, value in fields.items():
            if value is None:
                violations.append(f"{recording.name}: {field_name} missing")
                continue
            if _DRIVE_LETTER_RE.search(value) or "\\" in value:
                violations.append(
                    f"{recording.name}: {field_name} = {value!r} is not "
                    "repo-relative posix"
                )
            elif value.startswith("/"):
                violations.append(
                    f"{recording.name}: {field_name} = {value!r} is "
                    "machine-absolute (leading '/'), not repo-relative posix"
                )
    assert not violations, (
        "committed vision recordings must hold repo-relative posix paths "
        "(carried-findings D-C2 fixture hygiene):\n" + "\n".join(violations)
    )


@pytest.mark.parametrize(
    ("recording_payload", "expected_fragment"),
    [
        pytest.param(
            {
                "response": {"source_png_path": "/abs/machine/slide-01.png"},
                "_provenance": {"source_png": "runs/ok/slide-01.png"},
            },
            "machine-absolute",
            id="leading-slash-posix-absolute",
        ),
        pytest.param(
            {
                "response": "corrupt-not-a-dict",
                "_provenance": {"source_png": "runs/ok/slide-01.png"},
            },
            "not a JSON object",
            id="non-dict-response",
        ),
    ],
)
def test_hygiene_guard_flags_fabricated_bad_recordings(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    recording_payload: dict,
    expected_fragment: str,
) -> None:
    """Guard-widening pins (carried-findings batch, RED-first):

    - a leading-'/' POSIX-absolute path is machine-absolute and must be
      flagged (the drive-letter/backslash regexes alone miss it);
    - a non-dict ``response`` value must accumulate a clean violation row,
      not crash the guard with AttributeError.

    Fabricates a scratch recording under tmp_path and points the guard at it
    via monkeypatch — no junk files in the committed fixtures.
    """
    (tmp_path / "fabricated.json").write_text(
        json.dumps(recording_payload), encoding="utf-8"
    )
    monkeypatch.setitem(globals(), "RECORDINGS_DIR", tmp_path)
    with pytest.raises(AssertionError, match=expected_fragment):
        test_committed_recordings_carry_no_machine_absolute_paths()
