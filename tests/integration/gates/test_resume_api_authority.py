from __future__ import annotations

from pathlib import Path


def test_authorized_bridges_call_resume_api() -> None:
    root = Path.cwd()
    targets = [
        root / "app" / "mcp_server" / "tools" / "gate_decide.py",
        root / "app" / "http" / "gate_endpoint.py",
        root / "app" / "marcus" / "cli" / "gate_cli.py",
    ]
    for path in targets:
        text = path.read_text(encoding="utf-8")
        assert "resume_api" in text or "resume_from_verdict" in text


def test_no_unauthorized_callers() -> None:
    root = Path.cwd()
    allowed = {
        (root / "app" / "mcp_server" / "tools" / "gate_decide.py").resolve(),
        (root / "app" / "http" / "gate_endpoint.py").resolve(),
        (root / "app" / "marcus" / "cli" / "gate_cli.py").resolve(),
    }
    offenders: list[Path] = []
    for path in (root / "app").rglob("*.py"):
        if path.resolve() in allowed:
            continue
        text = path.read_text(encoding="utf-8")
        if path.name == "operator_verdict.py":
            continue
        if "OperatorVerdict(" in text and "tests" not in str(path):
            offenders.append(path)
    assert offenders == [], f"unexpected direct OperatorVerdict constructors: {offenders}"
