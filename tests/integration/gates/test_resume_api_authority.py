"""Resume-API authority test (housekeeping-2 AST-rewrite landed at S6 2026-05-08).

Closes A19 anti-pattern (Class-definition substring scanners go stale when class
names change) by replacing the substring scanner pattern with AST-based
constructor detection.

Original (pre-S6) impl used substring matching `"OperatorVerdict(" in text`,
which (a) trivially matched class definitions like `class Section08BOperatorVerdict(BaseModel):`
NOT direct constructor calls, AND (b) used filename exclusion `path.name == "operator_verdict.py"`
which did NOT match the variant filenames (`operator_verdict_section_*.py`).

The result was a 7+ DISMISS-thread anti-pattern (verdicts 7c.9/10/11/12/13/14/20b
all dismissed `test_no_unauthorized_callers` as PRE-EXISTING noise without escalating
the structural defect to harvest).

This rewrite:
1. AST-walks `app/**/*.py` looking for `ast.Call` nodes
2. Filters for calls whose function name starts with one of:
   - `OperatorVerdict` (root constructor)
   - `Section*OperatorVerdict` (per-section variant constructors at app.models.operator_verdict_section_*.py)
3. Excludes the operator-verdict module family by glob pattern (operator_verdict*.py)
4. Excludes the three authorized verdict-bridge modules (D3 HIL tamper-evidence)
"""

from __future__ import annotations

import ast
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


def _is_operator_verdict_constructor_call(node: ast.Call) -> bool:
    """Return True iff `node` is a Call to a constructor whose name starts with
    'OperatorVerdict' OR matches 'Section*OperatorVerdict' pattern.

    Distinguishes constructor calls from class definitions (which are ast.ClassDef
    nodes; not ast.Call) and from import statements (also not ast.Call).
    """
    func = node.func
    if isinstance(func, ast.Name):
        name = func.id
    elif isinstance(func, ast.Attribute):
        name = func.attr
    else:
        return False
    if name == "OperatorVerdict":
        return True
    # Per-section variants: Section02AOperatorVerdict, Section04AOperatorVerdict, ...
    if name.startswith("Section") and name.endswith("OperatorVerdict"):
        return True
    return False


def _is_authorized_caller(path: Path, root: Path) -> bool:
    """Return True iff `path` is in the authorized-callers set per D3 HIL tamper-evidence
    + post-Slab-7c §section poll-surface family + replay-harness."""
    rel = path.relative_to(root)
    rel_str = str(rel).replace("\\", "/")

    # Original three authorized verdict-bridge modules (D3 HIL tamper-evidence)
    explicit_allowed = {
        "app/mcp_server/tools/gate_decide.py",
        "app/http/gate_endpoint.py",
        "app/marcus/cli/gate_cli.py",
    }
    if rel_str in explicit_allowed:
        return True

    # §section poll-surface family: each §section's poll_surface.py is the
    # per-section verdict bridge. Per ADR 0002 + ADR 0003 (NEW family precedent),
    # each §section package has its own gate code and constructs its own per-§
    # OperatorVerdict variant via the poll_surface module.
    if rel_str.startswith("app/gates/section_") and rel_str.endswith("/poll_surface.py"):
        return True

    # Replay harness: app/marcus/orchestrator/m3_trial.py reconstructs verdicts
    # from persisted trial transcripts during replay-regression. Authorized per
    # FR51 trial-replay regression contract.
    if rel_str == "app/marcus/orchestrator/m3_trial.py":
        return True

    return False


def test_no_unauthorized_callers() -> None:
    """AST-based constructor scanner — replaces pre-S6 substring scanner per A19
    anti-pattern (housekeeping-2 land 2026-05-08).

    Authorized callers per D3 HIL tamper-evidence + ADR 0002/0003 + FR51 replay:
    - app/mcp_server/tools/gate_decide.py
    - app/http/gate_endpoint.py
    - app/marcus/cli/gate_cli.py
    - app/gates/section_*/poll_surface.py (per-§ verdict bridge family)
    - app/marcus/orchestrator/m3_trial.py (replay harness)

    All other constructors (specialists, runtime, models other than operator_verdict
    family) are forbidden — must route through resume_from_verdict() in
    app.gates.resume_api.
    """
    root = Path.cwd()

    # Excluded by glob: operator_verdict.py + operator_verdict_section_*.py family
    # (these modules DEFINE the constructors; calls inside the definition are
    # self-instantiation, not unauthorized bridge construction).
    offenders: list[Path] = []
    for path in (root / "app").rglob("*.py"):
        if _is_authorized_caller(path, root):
            continue
        if path.name == "operator_verdict.py" or path.name.startswith("operator_verdict_section_"):
            continue
        if "tests" in str(path):
            continue

        text = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(text)
        except SyntaxError:
            # Skip files that don't parse (shouldn't happen in app/ but defensive)
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and _is_operator_verdict_constructor_call(node):
                offenders.append(path)
                break  # one offender-flag per file is sufficient

    assert offenders == [], (
        f"Unexpected direct OperatorVerdict constructor calls (AST-detected): "
        f"{[str(p.relative_to(root)) for p in offenders]}\n"
        f"Per D3 HIL tamper-evidence: only the authorized bridge modules + per-§ poll-surface family "
        f"+ replay harness may construct OperatorVerdict / Section*OperatorVerdict. "
        f"Other callers must route through resume_from_verdict() in app.gates.resume_api. "
        f"See _is_authorized_caller() docstring for the full allowed set."
    )
