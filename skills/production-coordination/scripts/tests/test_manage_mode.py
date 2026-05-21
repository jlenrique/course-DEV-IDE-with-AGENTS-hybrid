# /// script
# requires-python = ">=3.10"
# ///
"""Tests for manage_mode.py — run mode management."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import manage_mode


class TempModeFile:
    def __init__(self, data: dict | None = None) -> None:
        self._tmpfile = tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False, encoding="utf-8")
        if data:
            json.dump(data, self._tmpfile)
        self._tmpfile.close()
        self.path = self._tmpfile.name

    def __enter__(self) -> TempModeFile:
        return self

    def __exit__(self, *args: object) -> None:
        try:
            Path(self.path).unlink(missing_ok=True)
        except OSError:
            pass


class TestGetMode(unittest.TestCase):
    def test_get_default_no_file(self) -> None:
        args = manage_mode.build_parser().parse_args(["--file", "/tmp/nonexistent_mode.json", "get"])
        result = manage_mode.cmd_get(args)
        self.assertEqual(result["mode"], "default")

    def test_get_from_file(self) -> None:
        with TempModeFile({"mode": "ad-hoc", "switched_at": "2026-03-26T15:00:00"}) as f:
            args = manage_mode.build_parser().parse_args(["--file", f.path, "get"])
            result = manage_mode.cmd_get(args)
            self.assertEqual(result["mode"], "ad-hoc")


class TestSetMode(unittest.TestCase):
    def test_set_tracked_alias_normalizes_to_default(self) -> None:
        with TempModeFile({"mode": "ad-hoc"}) as f:
            args = manage_mode.build_parser().parse_args(["--file", f.path, "set", "tracked"])
            result = manage_mode.cmd_set(args)
            self.assertEqual(result["mode"], "default")
            self.assertEqual(result["execution_mode"], "tracked")

    def test_set_ad_hoc(self) -> None:
        with TempModeFile({"mode": "default"}) as f:
            args = manage_mode.build_parser().parse_args(["--file", f.path, "set", "ad-hoc"])
            result = manage_mode.cmd_set(args)
            self.assertEqual(result["mode"], "ad-hoc")
            self.assertEqual(result["previous_mode"], "default")
            self.assertTrue(result["changed"])

    def test_set_default(self) -> None:
        with TempModeFile({"mode": "ad-hoc"}) as f:
            args = manage_mode.build_parser().parse_args(["--file", f.path, "set", "default"])
            result = manage_mode.cmd_set(args)
            self.assertEqual(result["mode"], "default")
            self.assertTrue(result["changed"])

    def test_set_same_mode(self) -> None:
        with TempModeFile({"mode": "default"}) as f:
            args = manage_mode.build_parser().parse_args(["--file", f.path, "set", "default"])
            result = manage_mode.cmd_set(args)
            self.assertFalse(result["changed"])

    def test_set_persists(self) -> None:
        with TempModeFile({"mode": "default"}) as f:
            set_args = manage_mode.build_parser().parse_args(["--file", f.path, "set", "ad-hoc"])
            manage_mode.cmd_set(set_args)

            get_args = manage_mode.build_parser().parse_args(["--file", f.path, "get"])
            result = manage_mode.cmd_get(get_args)
            self.assertEqual(result["mode"], "ad-hoc")

    def test_set_records_timestamp(self) -> None:
        with TempModeFile({"mode": "default"}) as f:
            args = manage_mode.build_parser().parse_args(["--file", f.path, "set", "ad-hoc"])
            result = manage_mode.cmd_set(args)
            self.assertIsNotNone(result["switched_at"])

    def test_set_atomic_write_leaves_no_tmp_file(self) -> None:
        with TempModeFile({"mode": "default"}) as f:
            args = manage_mode.build_parser().parse_args(["--file", f.path, "set", "ad-hoc"])
            manage_mode.cmd_set(args)
            tmp_path = Path(f.path + ".tmp")
            self.assertFalse(tmp_path.exists())


if __name__ == "__main__":
    unittest.main()
