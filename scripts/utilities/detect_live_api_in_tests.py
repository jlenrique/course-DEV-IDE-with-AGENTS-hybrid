"""Detect forbidden third-party live API client imports in tests."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROOTS = (
    REPO_ROOT / "tests" / "parity" / "test_tracy_activation_contract.py",
    REPO_ROOT / "tests" / "parity" / "test_gary_activation_contract.py",
    REPO_ROOT / "tests" / "parity" / "test_kira_activation_contract.py",
    REPO_ROOT / "tests" / "specialists" / "tracy",
    REPO_ROOT / "tests" / "specialists" / "gary",
    REPO_ROOT / "tests" / "specialists" / "kira",
    REPO_ROOT / "tests" / "composition" / "test_tracy_to_texas_chain.py",
    REPO_ROOT / "tests" / "composition" / "test_gary_to_vera_g3_chain.py",
    REPO_ROOT / "tests" / "composition" / "test_kira_to_compositor_chain.py",
    REPO_ROOT / "tests" / "end_to_end" / "test_tracy_cache_hit_rate.py",
)
FORBIDDEN_MODULES = (
    "gamma_client",
    "kling_client",
    "elevenlabs_client",
    "wondercraft_client",
)


def _iter_test_files(roots: tuple[Path, ...]) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        if root.is_file() and root.suffix == ".py":
            files.append(root)
        elif root.is_dir():
            files.extend(sorted(root.rglob("test_*.py")))
    return files


def _violations(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if any(module.endswith(name) for name in FORBIDDEN_MODULES):
                found.append(f"{path.relative_to(REPO_ROOT).as_posix()}:{node.lineno}: {module}")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if any(alias.name.endswith(name) for name in FORBIDDEN_MODULES):
                    found.append(
                        f"{path.relative_to(REPO_ROOT).as_posix()}:{node.lineno}: {alias.name}"
                    )
    return found


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    roots = tuple((REPO_ROOT / arg) if not Path(arg).is_absolute() else Path(arg) for arg in args)
    files = _iter_test_files(roots or DEFAULT_ROOTS)
    violations: list[str] = []
    for path in files:
        violations.extend(_violations(path))
    if violations:
        print("Forbidden live API imports detected:")
        for violation in violations:
            print(violation)
        return 1
    print(f"PASS: scanned {len(files)} test file(s); no forbidden live API imports")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
