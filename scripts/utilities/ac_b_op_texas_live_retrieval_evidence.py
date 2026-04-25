"""AC-2a.4-B-OP operator helper — live retrieval-provider dispatch evidence capture.

Story 2a.4 (Texas migration) AC-B-OP is operator-gated: dev-agent verifies the
mockable wrapper shape; live retrieval-provider dispatch (scite / Consensus / etc.)
runs on operator machine with real provider keys + the resulting six-artifact
bundle pasted into the spec's Completion Notes.

This helper orchestrates the run + auto-fills the Completion Notes evidence block.

Invocation (operator machine, post-dev-agent-T9-close):

    .venv/Scripts/python.exe scripts/utilities/ac_b_op_texas_live_retrieval_evidence.py \\
        --directive tests/fixtures/specialists/texas/ac_b_op_directive.yaml \\
        --bundle-dir _bmad-output/specs/ac_b_op_2a4_<timestamp>/ \\
        --provider-key-env SCITE_API_KEY

The script:
  1. Verifies you're running under .venv (warns otherwise — provider SDKs may be missing).
  2. Verifies the named provider-key env var is set (fails loud if not).
  3. Runs `skills/bmad-agent-texas/scripts/run_wrangler.py` against the directive.
  4. Captures exit code + stdout/stderr.
  5. Computes sha256 for each of the six bundle artifacts (extracted.md, metadata.json,
     manifest.json, extraction-report.yaml, ingestion-evidence.md, result.yaml).
  6. Reads `result.yaml` and extracts the relevant tail (status + bundle_reference +
     per-source provider summary).
  7. Emits the filled-in AC-2a.4-B-OP evidence block to stdout (Markdown), ready to
     paste into the spec's Completion Notes.

Outputs are also persisted to `<bundle-dir>/ac_b_op_evidence.md` so the operator
has a permanent copy alongside the bundle.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WRANGLER_PATH = REPO_ROOT / "skills" / "bmad-agent-texas" / "scripts" / "run_wrangler.py"
SIX_ARTIFACTS = (
    "extracted.md",
    "metadata.json",
    "manifest.json",
    "extraction-report.yaml",
    "ingestion-evidence.md",
    "result.yaml",
)
EXIT_CODE_MEANINGS = {
    0: "complete (all sources tier 1)",
    10: "complete_with_warnings (some sources tier 2)",
    20: "blocked (any source tier 3/4 after fallbacks)",
    30: "directive/IO error",
}


def _check_venv() -> None:
    in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix) or "VIRTUAL_ENV" in os.environ
    if not in_venv:
        print(
            "WARNING: not running under a venv; provider SDKs (scite, consensus, etc.) "
            "may be missing. Recommend: .venv/Scripts/python.exe scripts/utilities/...",
            file=sys.stderr,
        )


def _check_provider_key(env_var: str) -> None:
    value = os.environ.get(env_var)
    if not value:
        print(
            f"ERROR: provider key env var {env_var!r} not set. AC-B-OP requires a "
            f"real provider key on the operator machine. Set it and re-invoke.",
            file=sys.stderr,
        )
        sys.exit(2)
    if value.strip() in {"placeholder", "sk-placeholder", ""}:
        print(
            f"ERROR: provider key {env_var!r} appears to be a placeholder. AC-B-OP "
            f"needs a real key.",
            file=sys.stderr,
        )
        sys.exit(2)


def _run_wrangler(directive: Path, bundle_dir: Path) -> tuple[int, str, str]:
    bundle_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str(WRANGLER_PATH),
        "--directive",
        str(directive),
        "--bundle-dir",
        str(bundle_dir),
        "--json",
    ]
    print(f"Running: {' '.join(cmd)}", file=sys.stderr)
    proc = subprocess.run(  # noqa: S603 — wrangler script + repo-internal paths only
        cmd,
        shell=False,
        check=False,
        capture_output=True,
        text=True,
        timeout=300,  # 5-minute ceiling for a single-directive live dispatch
    )
    return proc.returncode, proc.stdout, proc.stderr


def _sha256_or_missing(path: Path) -> str:
    if not path.is_file():
        return "<MISSING>"
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _result_yaml_tail(bundle_dir: Path, max_lines: int = 40) -> str:
    result_path = bundle_dir / "result.yaml"
    if not result_path.is_file():
        return "<result.yaml NOT WRITTEN — runner failed before envelope emission>"
    text = result_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text
    return "\n".join(lines[:max_lines]) + f"\n... <truncated; full file at {result_path}>"


def _render_evidence_block(
    *,
    directive: Path,
    bundle_dir: Path,
    provider_key_env: str,
    exit_code: int,
    sha256_map: dict[str, str],
    result_tail: str,
    timestamp: str,
) -> str:
    artifact_lines = "\n".join(
        f"  {name:<24} {sha256_map[name]}" for name in SIX_ARTIFACTS
    )
    exit_meaning = EXIT_CODE_MEANINGS.get(exit_code, "<unknown>")
    return f"""## AC-2a.4-B-OP live retrieval-provider dispatch evidence (operator-gated)

Environment: real {provider_key_env} set (redacted)
Directive shape: {directive.name}
Timestamp: {timestamp}

Command:
  .venv/Scripts/python.exe skills/bmad-agent-texas/scripts/run_wrangler.py \\
    --directive {directive} \\
    --bundle-dir {bundle_dir} \\
    --json

Runner exit code: {exit_code} ({exit_meaning})

Six-artifact bundle file roster + sha256:
{artifact_lines}

result.yaml envelope (tail):

```yaml
{result_tail}
```

Notes / observations:
  <operator fills in any provider-specific observations — paywall behavior,
   convergence-signal, cross-validation outcome, etc.>
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="AC-2a.4-B-OP operator helper — live retrieval-provider dispatch evidence."
    )
    parser.add_argument(
        "--directive",
        type=Path,
        required=True,
        help="Path to retrieval directive YAML.",
    )
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        required=True,
        help="Directory where the six-artifact bundle will be written.",
    )
    parser.add_argument(
        "--provider-key-env",
        type=str,
        default="SCITE_API_KEY",
        help="Name of env var holding the real provider key (default: SCITE_API_KEY).",
    )
    parser.add_argument(
        "--evidence-output",
        type=Path,
        default=None,
        help=(
            "Optional path to write the evidence block (default: <bundle-dir>/ac_b_op_evidence.md)."
        ),
    )
    args = parser.parse_args(argv)

    if not args.directive.is_file():
        print(f"ERROR: directive not found at {args.directive}", file=sys.stderr)
        return 2

    _check_venv()
    _check_provider_key(args.provider_key_env)

    timestamp = datetime.now(UTC).isoformat(timespec="seconds")
    exit_code, stdout, stderr = _run_wrangler(args.directive, args.bundle_dir)

    if stdout:
        print(f"--- runner stdout ---\n{stdout}", file=sys.stderr)
    if stderr:
        print(f"--- runner stderr ---\n{stderr}", file=sys.stderr)

    sha256_map = {name: _sha256_or_missing(args.bundle_dir / name) for name in SIX_ARTIFACTS}
    result_tail = _result_yaml_tail(args.bundle_dir)

    evidence = _render_evidence_block(
        directive=args.directive,
        bundle_dir=args.bundle_dir,
        provider_key_env=args.provider_key_env,
        exit_code=exit_code,
        sha256_map=sha256_map,
        result_tail=result_tail,
        timestamp=timestamp,
    )

    print(evidence)

    output_path = args.evidence_output or (args.bundle_dir / "ac_b_op_evidence.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(evidence, encoding="utf-8")
    print(f"\n[evidence persisted to {output_path}]", file=sys.stderr)

    # Helper exits 0 on successful capture even if wrangler exited non-zero —
    # operator wants the evidence block regardless of dispatch outcome (a non-zero
    # exit IS the evidence in some cases).
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
