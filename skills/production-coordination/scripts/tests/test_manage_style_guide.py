# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Tests for manage_style_guide.py — style guide parameter management."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import manage_style_guide

SAMPLE_STYLE_GUIDE = {
    "tool_parameters": {
        "gamma": {"default_llm": "claude-3", "style": "professional-medical"},
        "elevenlabs": {"default_voice_id": "voice123", "model_id": "eleven_turbo_v2"},
    }
}


class TempYAML:
    def __init__(self, data: dict | None = None) -> None:
        self._tmpfile = tempfile.NamedTemporaryFile(suffix=".yaml", mode="w", delete=False, encoding="utf-8")
        yaml.dump(data or SAMPLE_STYLE_GUIDE, self._tmpfile, default_flow_style=False)
        self._tmpfile.close()
        self.path = self._tmpfile.name

    def __enter__(self) -> TempYAML:
        return self

    def __exit__(self, *args: object) -> None:
        try:
            Path(self.path).unlink(missing_ok=True)
        except OSError:
            pass


class TestGet(unittest.TestCase):
    def test_get_all_tools(self) -> None:
        with TempYAML() as f:
            args = manage_style_guide.build_parser().parse_args(["--file", f.path, "get"])
            result = manage_style_guide.cmd_get(args)
            self.assertIn("gamma", result["tools"])
            self.assertIn("elevenlabs", result["tools"])

    def test_get_tool_params(self) -> None:
        with TempYAML() as f:
            args = manage_style_guide.build_parser().parse_args(["--file", f.path, "get", "--tool", "gamma"])
            result = manage_style_guide.cmd_get(args)
            self.assertEqual(result["parameters"]["default_llm"], "claude-3")

    def test_get_specific_key(self) -> None:
        with TempYAML() as f:
            args = manage_style_guide.build_parser().parse_args(["--file", f.path, "get", "--tool", "gamma", "--key", "style"])
            result = manage_style_guide.cmd_get(args)
            self.assertEqual(result["value"], "professional-medical")
            self.assertTrue(result["found"])

    def test_get_missing_key(self) -> None:
        with TempYAML() as f:
            args = manage_style_guide.build_parser().parse_args(["--file", f.path, "get", "--tool", "gamma", "--key", "nonexistent"])
            result = manage_style_guide.cmd_get(args)
            self.assertIsNone(result["value"])
            self.assertFalse(result["found"])


class TestSet(unittest.TestCase):
    def test_set_new_value(self) -> None:
        with TempYAML() as f:
            args = manage_style_guide.build_parser().parse_args(["--file", f.path, "set", "gamma", "temperature", "0.7"])
            result = manage_style_guide.cmd_set(args)
            self.assertTrue(result["saved"])
            self.assertEqual(result["value"], 0.7)
            self.assertIsNone(result["previous_value"])

    def test_set_overwrite(self) -> None:
        with TempYAML() as f:
            args = manage_style_guide.build_parser().parse_args(["--file", f.path, "set", "gamma", "default_llm", "gpt-4"])
            result = manage_style_guide.cmd_set(args)
            self.assertEqual(result["value"], "gpt-4")
            self.assertEqual(result["previous_value"], "claude-3")

    def test_set_new_tool(self) -> None:
        with TempYAML() as f:
            args = manage_style_guide.build_parser().parse_args(["--file", f.path, "set", "canva", "brand_template", "medical-v2"])
            result = manage_style_guide.cmd_set(args)
            self.assertTrue(result["saved"])
            self.assertEqual(result["tool"], "canva")

    def test_set_json_value(self) -> None:
        with TempYAML() as f:
            args = manage_style_guide.build_parser().parse_args(["--file", f.path, "set", "gamma", "options", '{"format":"widescreen"}'])
            result = manage_style_guide.cmd_set(args)
            self.assertEqual(result["value"], {"format": "widescreen"})


class TestListTools(unittest.TestCase):
    def test_list_all(self) -> None:
        with TempYAML() as f:
            args = manage_style_guide.build_parser().parse_args(["--file", f.path, "list-tools"])
            result = manage_style_guide.cmd_list_tools(args)
            self.assertEqual(result["count"], 2)
            tool_names = [t["tool"] for t in result["tools"]]
            self.assertIn("gamma", tool_names)

    def test_list_empty(self) -> None:
        with TempYAML(data={"tool_parameters": {}}) as f:
            args = manage_style_guide.build_parser().parse_args(["--file", f.path, "list-tools"])
            result = manage_style_guide.cmd_list_tools(args)
            self.assertEqual(result["count"], 0)


if __name__ == "__main__":
    unittest.main()
