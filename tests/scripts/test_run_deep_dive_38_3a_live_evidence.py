from __future__ import annotations

import json
from pathlib import Path

from scripts.utilities import run_deep_dive_38_3a_live_evidence as driver


def test_failed_live_attempt_and_ambiguous_journal_are_byte_pinned() -> None:
    observed = driver._assert_failed_evidence_preserved()
    assert set(observed) == set(driver.FAILED_PINS)
    for path, (size, digest) in driver.FAILED_PINS.items():
        assert observed[path] == {"size": size, "sha256": digest}


def test_setup_failure_is_recorded_as_a_failed_first_run_verdict(
    tmp_path: Path, monkeypatch
) -> None:
    evidence_root = tmp_path / "evidence"
    monkeypatch.setattr(driver, "ROOT", tmp_path)
    monkeypatch.setattr(driver, "EVIDENCE_ROOT", evidence_root)
    monkeypatch.setattr(driver, "SOURCE_RUN", tmp_path / "source-run")
    monkeypatch.setattr(driver, "_assert_failed_evidence_preserved", lambda: {})
    monkeypatch.setattr(
        driver.shutil,
        "copytree",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("copy failed")),
    )

    assert driver.main() == 1
    verdict_paths = tuple(evidence_root.glob("deep-dive-38-3a-live-*/verdict.json"))
    assert len(verdict_paths) == 1
    verdict = json.loads(verdict_paths[0].read_text("utf-8"))
    assert verdict["pass"] is False
    assert verdict["first_run_stands"] is True
    assert verdict["error_type"] == "OSError"
    assert verdict["error"] == "copy failed"


def test_attempt_directory_allocator_retries_an_atomic_collision(
    tmp_path: Path, monkeypatch
) -> None:
    evidence_root = tmp_path / "evidence"
    evidence_root.mkdir()
    ids = iter(("aaaaaaaa-0000-4000-8000-000000000000", "bbbbbbbb-0000-4000-8000-000000000000"))
    (evidence_root / "deep-dive-38-3a-live-aaaaaaaa").mkdir()
    monkeypatch.setattr(driver, "EVIDENCE_ROOT", evidence_root)
    monkeypatch.setattr(driver, "uuid4", lambda: next(ids))

    attempt_id, attempt_root = driver._allocate_attempt_root()
    assert attempt_id.startswith("bbbbbbbb")
    assert attempt_root.is_dir()


def test_malformed_residual_journal_cannot_suppress_failure_verdict(
    tmp_path: Path, monkeypatch
) -> None:
    evidence_root = tmp_path / "evidence"
    monkeypatch.setattr(driver, "ROOT", tmp_path)
    monkeypatch.setattr(driver, "EVIDENCE_ROOT", evidence_root)
    monkeypatch.setattr(driver, "SOURCE_RUN", tmp_path / "source-run")
    monkeypatch.setattr(driver, "_assert_failed_evidence_preserved", lambda: {})

    def fail_with_malformed_journal(_source: Path, destination: Path) -> None:
        destination.mkdir()
        (destination / driver.workbook_wiring.DEEP_DIVE_JOURNAL_FILENAME).write_text(
            "not-json", encoding="utf-8"
        )
        raise OSError("copy failed after journal creation")

    monkeypatch.setattr(driver.shutil, "copytree", fail_with_malformed_journal)
    assert driver.main() == 1
    verdict_path = next(evidence_root.glob("deep-dive-38-3a-live-*/verdict.json"))
    verdict = json.loads(verdict_path.read_text("utf-8"))
    assert verdict["error_type"] == "OSError"
    assert "journal_capture_error" in verdict
