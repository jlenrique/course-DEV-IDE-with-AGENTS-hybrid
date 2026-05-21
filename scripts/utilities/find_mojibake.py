"""Find text files that still contain known mojibake byte sequences (after UTF-8 decode)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.utilities.normalize_mojibake import KNOWN_MOJIBAKE_SEQUENCES  # noqa: E402


def _contains_known_mojibake(text: str) -> bool:
    return any(bad in text for bad, _ in KNOWN_MOJIBAKE_SEQUENCES)


def main() -> int:
    root = os.path.abspath(".")
    hits: list[str] = []
    skip = {"node_modules", ".git", ".venv", "__pycache__", ".mypy_cache", ".ruff_cache"}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip]
        for name in filenames:
            if not name.endswith(
                (".md", ".yaml", ".yml", ".mdc", ".py", ".json", ".txt", ".toml")
            ) or name.startswith("."):
                continue
            path = os.path.join(dirpath, name)
            try:
                with open(path, encoding="utf-8", errors="replace") as f:
                    text = f.read()
            except OSError:
                continue
            if _contains_known_mojibake(text):
                hits.append(path)
    for p in sorted(hits):
        print(os.path.relpath(p, root))
    print("---", len(hits), "files with known mojibake sequences", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
