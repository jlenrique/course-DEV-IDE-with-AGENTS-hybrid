"""M5 pre-vote audit — operator readiness checklist as executable script.

Run BEFORE the 5a.5 6-agent party-mode vote convenes. Verifies that all
preconditions for an honest M5 ship verdict are met:

  - 5a.1-5a.4 all `done` per sprint-status
  - M2 / M3 / M4 verdict states known + classified (resolved / pending / blocked)
  - Operator addenda landed where required
  - Economics ≥50% reduction + ≥80% cache-hit-rate bars verified (or NOT-MEASURED)
  - Parity score from 5a.2 evidence ≥60% (or NOT-MEASURED)
  - 15-invariant audit matrix CREATED at 5a.4 close
  - Anti-patterns catalog at FR64 final state

Outputs go/no-go recommendation per PRD §FR60-62 thresholds:

  - SHIP-READY → all conditions resolved + bars met → vote SHIP path likely viable
  - SHIP-CONDITIONAL → some conditions outstanding but bounded-window-resolvable → vote SHIP-CONDITIONAL path
  - ITERATE-RECOMMENDED → bars not met OR substrate gaps → vote ITERATE path
  - ROLLBACK-CANDIDATE → critical bar failure (cost <30% per PRD §Cost Projection) → vote ROLLBACK path

Usage:
    .venv/Scripts/python.exe scripts/utilities/m5_pre_vote_audit.py
    .venv/Scripts/python.exe scripts/utilities/m5_pre_vote_audit.py --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

REPO_ROOT = Path(__file__).resolve().parents[2]

VerdictRec = Literal["SHIP-READY", "SHIP-CONDITIONAL", "ITERATE-RECOMMENDED", "ROLLBACK-CANDIDATE"]


@dataclass
class AuditFinding:
    name: str
    state: Literal["PASS", "WARN", "FAIL", "NOT-MEASURED", "NOT-SHIPPED"]
    detail: str
    impact: str = ""  # what this finding implies for verdict path


def _check_predecessors_done() -> AuditFinding:
    """5a.1 + 5a.2 + 5a.3 + 5a.4 all `done`."""
    sprint = REPO_ROOT / "_bmad-output" / "implementation-artifacts" / "sprint-status.yaml"
    if not sprint.is_file():
        return AuditFinding("predecessors_done", "FAIL", "sprint-status.yaml not found", impact="cannot proceed")
    content = sprint.read_text(encoding="utf-8")
    expected = ["migration-5a-1-", "migration-5a-2-", "migration-5a-3-", "migration-5a-4-"]
    states = {}
    for prefix in expected:
        m = re.search(rf"^  {re.escape(prefix)}[a-z0-9-]+:\s*([a-z-]+)", content, re.MULTILINE)
        states[prefix.rstrip("-")] = m.group(1) if m else "NOT-FOUND"
    not_done = {k: v for k, v in states.items() if v != "done"}
    if not_done:
        return AuditFinding(
            "predecessors_done",
            "FAIL",
            f"5a.1-5a.4 not all done: {not_done}",
            impact="vote BLOCKED until predecessors close",
        )
    return AuditFinding("predecessors_done", "PASS", "5a.1-5a.4 all done")


def _check_milestone_states() -> dict[str, AuditFinding]:
    """M2 / M3 / M4 verdict states from acceptance-verdict artifacts."""
    artifacts = [
        ("M2", REPO_ROOT / "_bmad-output" / "implementation-artifacts" / "slab-2c-m2-acceptance-verdict.md", "Wondercraft AC-D-OP"),
        ("M3", REPO_ROOT / "_bmad-output" / "implementation-artifacts" / "slab-3-m3-acceptance-verdict.md", "Texas AC-B-OP M1-M5"),
        ("M4", REPO_ROOT / "_bmad-output" / "implementation-artifacts" / "slab-4-m4-acceptance-verdict.md", "M2/M3 carry-forward"),
    ]
    findings = {}
    for milestone, path, gate_desc in artifacts:
        if not path.is_file():
            findings[milestone] = AuditFinding(
                f"{milestone}_verdict",
                "FAIL",
                f"verdict artifact missing: {path.name}",
                impact=f"{milestone} carries to BLOCK or ITERATE",
            )
            continue
        content = path.read_text(encoding="utf-8")
        if "GREEN-LIGHT" in content and "CONDITIONAL" not in content.split("Consensus verdict:")[1][:100] if "Consensus verdict:" in content else False:
            findings[milestone] = AuditFinding(
                f"{milestone}_verdict",
                "PASS",
                f"GREEN-LIGHT (operator addendum landed for {gate_desc})",
            )
        elif "GREEN-WITH-RIDERS" in content:
            findings[milestone] = AuditFinding(
                f"{milestone}_verdict",
                "WARN",
                f"GREEN-WITH-RIDERS ({gate_desc}; riders documented)",
                impact=f"{milestone} acceptable for SHIP path; riders carry as named follow-ons",
            )
        elif "CONDITIONAL-GREEN" in content:
            findings[milestone] = AuditFinding(
                f"{milestone}_verdict",
                "WARN",
                f"CONDITIONAL-GREEN-PENDING-OPERATOR-ADDENDUM ({gate_desc})",
                impact=f"{milestone} carries to SHIP-CONDITIONAL OR resolve pre-vote via operator-window addendum",
            )
        elif "RED" in content or "ROLLBACK" in content:
            findings[milestone] = AuditFinding(
                f"{milestone}_verdict",
                "FAIL",
                f"RED or ROLLBACK indicated ({gate_desc})",
                impact=f"{milestone} blocks SHIP; recommend ROLLBACK or ITERATE",
            )
        else:
            findings[milestone] = AuditFinding(
                f"{milestone}_verdict",
                "WARN",
                f"verdict state unclear in {path.name}",
                impact=f"{milestone} requires manual review",
            )
    return findings


def _check_economics_bars() -> AuditFinding:
    """5a.3 ≥50% cost-reduction + ≥80% cache-hit-rate median bars."""
    baselines_dir = REPO_ROOT / "_bmad-output" / "economics-baselines"
    if not baselines_dir.is_dir():
        return AuditFinding(
            "economics_bars",
            "NOT-MEASURED",
            "_bmad-output/economics-baselines/ not present (5a.3 not yet shipped or baseline absent)",
            impact="vote requires economics evidence; defer until measured",
        )
    baseline_files = list(baselines_dir.glob("*.json"))
    if not baseline_files:
        return AuditFinding(
            "economics_bars",
            "NOT-MEASURED",
            "baselines dir present but no .json baselines",
            impact="vote requires economics evidence; defer until measured",
        )
    # Heuristic: parse first baseline file for cost_reduction_percentage
    try:
        baseline = json.loads(baseline_files[0].read_text(encoding="utf-8"))
        reduction = baseline.get("cost_reduction_percentage", baseline.get("reduction_pct"))
        cache_hit_median = baseline.get("cache_hit_rate_median")
        if reduction is None:
            return AuditFinding(
                "economics_bars",
                "WARN",
                f"baseline {baseline_files[0].name} present but no cost_reduction_percentage field",
                impact="manual review; verify economics CLI ran correctly",
            )
        if reduction >= 0.50 and (cache_hit_median is None or cache_hit_median >= 0.80):
            return AuditFinding(
                "economics_bars",
                "PASS",
                f"≥50% reduction met ({reduction:.0%}); cache_hit_median {cache_hit_median or 'n/a'}",
            )
        elif reduction >= 0.30:
            return AuditFinding(
                "economics_bars",
                "WARN",
                f"reduction {reduction:.0%} below 50% bar (PRD §Cost Projection: defaults Revise/Iterate)",
                impact="vote ITERATE-recommended unless operator overrides",
            )
        else:
            return AuditFinding(
                "economics_bars",
                "FAIL",
                f"reduction {reduction:.0%} below 30% bar (PRD §Cost Projection: defaults Revise OR Rollback)",
                impact="vote ROLLBACK-CANDIDATE; operator must justify SHIP override",
            )
    except Exception as exc:
        return AuditFinding("economics_bars", "WARN", f"baseline parse failed: {exc}", impact="manual review")


def _check_parity_score() -> AuditFinding:
    """5a.2 head-to-head parity evidence Markdown TIER 1 + TIER 2 scores."""
    parity_files = list((REPO_ROOT / "_bmad-output" / "implementation-artifacts").glob("5a-2-parity-evidence-*.md"))
    if not parity_files:
        return AuditFinding(
            "parity_score",
            "NOT-MEASURED",
            "no 5a-2-parity-evidence-*.md found (5a.2 not yet shipped or evidence not landed)",
            impact="vote requires parity evidence; defer until measured",
        )
    content = parity_files[0].read_text(encoding="utf-8")
    # Heuristic: find tier scores
    tier1_match = re.search(r"file-presence[^0-9]*([\d.]+)%?", content, re.IGNORECASE)
    tier2_match = re.search(r"structural-match[^0-9]*([\d.]+)%?", content, re.IGNORECASE)
    tier1 = float(tier1_match.group(1)) if tier1_match else None
    tier2 = float(tier2_match.group(1)) if tier2_match else None
    if tier1 is None or tier2 is None:
        return AuditFinding(
            "parity_score",
            "WARN",
            f"parity evidence file {parity_files[0].name} present but scores not parseable",
            impact="manual review",
        )
    # Normalize to fraction if percent-style
    if tier1 > 1: tier1 = tier1 / 100
    if tier2 > 1: tier2 = tier2 / 100
    if tier1 >= 0.80 and tier2 >= 0.60:
        return AuditFinding("parity_score", "PASS", f"TIER 1 {tier1:.0%} (≥80%); TIER 2 {tier2:.0%} (≥60%)")
    elif tier1 >= 0.60 and tier2 >= 0.40:
        return AuditFinding(
            "parity_score",
            "WARN",
            f"TIER 1 {tier1:.0%} / TIER 2 {tier2:.0%} below ≥80%/≥60% bars",
            impact="vote ITERATE OR SHIP-WITH-RIDERS based on operator judgment",
        )
    else:
        return AuditFinding(
            "parity_score",
            "FAIL",
            f"parity scores too low: TIER 1 {tier1:.0%} / TIER 2 {tier2:.0%}",
            impact="vote ITERATE or ROLLBACK; substantial divergence from primary",
        )


def _check_invariant_matrix() -> AuditFinding:
    """5a.4 15-invariant audit matrix CREATION (long-deferred from 2c.3 BLOCKER B1)."""
    path = REPO_ROOT / "_bmad-output" / "implementation-artifacts" / "15-invariant-audit-matrix.md"
    if not path.is_file():
        return AuditFinding(
            "invariant_matrix",
            "NOT-SHIPPED",
            "15-invariant-audit-matrix.md not found (5a.4 not yet shipped)",
            impact="vote BLOCKED; 5a.4 must close before 5a.5 vote",
        )
    content = path.read_text(encoding="utf-8")
    invariant_rows = len(re.findall(r"^\| (?!Invariant|---)", content, re.MULTILINE))
    violated = content.count("VIOLATED")
    deferred = content.count("DEFERRED")
    if violated > 0:
        return AuditFinding(
            "invariant_matrix",
            "FAIL",
            f"matrix shipped with {invariant_rows} rows but {violated} VIOLATED status entries",
            impact="vote ITERATE or ROLLBACK; invariant violation cannot SHIP",
        )
    return AuditFinding(
        "invariant_matrix",
        "PASS" if invariant_rows >= 15 else "WARN",
        f"matrix shipped: {invariant_rows} rows (expected ≥15); {deferred} DEFERRED",
    )


def _check_antipatterns_final() -> AuditFinding:
    """Anti-patterns catalog FR64 final ≥5 entries."""
    path = REPO_ROOT / "docs" / "dev-guide" / "specialist-anti-patterns.md"
    if not path.is_file():
        return AuditFinding("antipatterns_final", "FAIL", "specialist-anti-patterns.md not found")
    content = path.read_text(encoding="utf-8")
    entries = len(re.findall(r"^### A\d+\.", content, re.MULTILINE))
    cycle_complete = "harvest cycle complete" in content.lower() or "harvest CLOSED" in content
    if entries >= 5 and cycle_complete:
        return AuditFinding(
            "antipatterns_final",
            "PASS",
            f"{entries} entries; harvest-cycle-complete annotation present",
        )
    elif entries >= 5:
        return AuditFinding(
            "antipatterns_final",
            "WARN",
            f"{entries} entries (≥5 met) but no harvest-cycle-complete annotation",
            impact="5a.4 AC-C may not have closed; verify before vote",
        )
    else:
        return AuditFinding(
            "antipatterns_final",
            "FAIL",
            f"{entries} entries (<5 minimum per FR64)",
            impact="FR64 not met; ITERATE or BLOCK",
        )


def _recommend_verdict(findings: list[AuditFinding]) -> tuple[VerdictRec, str]:
    """Synthesize verdict recommendation from findings."""
    has_fail = any(f.state == "FAIL" for f in findings)
    has_warn = any(f.state == "WARN" for f in findings)
    has_not_shipped = any(f.state == "NOT-SHIPPED" for f in findings)
    has_not_measured = any(f.state == "NOT-MEASURED" for f in findings)

    if has_not_shipped:
        return "ITERATE-RECOMMENDED", "Predecessor stories incomplete; vote BLOCKED until 5a.x close"
    if has_fail:
        # Check for ROLLBACK-CANDIDATE specifically
        for f in findings:
            if f.state == "FAIL" and "ROLLBACK" in f.impact.upper():
                return "ROLLBACK-CANDIDATE", f"Critical bar failure: {f.name} — {f.detail}"
        return "ITERATE-RECOMMENDED", f"Substantive failures present; SHIP not advisable"
    if has_not_measured:
        return "SHIP-CONDITIONAL", "Some bars not yet measured; vote SHIP-CONDITIONAL with named-window OR defer"
    if has_warn:
        return "SHIP-CONDITIONAL", "Conditional milestones outstanding OR riders present; vote SHIP-CONDITIONAL or SHIP-WITH-RIDERS"
    return "SHIP-READY", "All bars met + all milestones resolved; SHIP path viable"


def run_audit() -> dict[str, Any]:
    findings = []
    findings.append(_check_predecessors_done())
    milestone_findings = _check_milestone_states()
    findings.extend(milestone_findings.values())
    findings.append(_check_economics_bars())
    findings.append(_check_parity_score())
    findings.append(_check_invariant_matrix())
    findings.append(_check_antipatterns_final())
    recommendation, rationale = _recommend_verdict(findings)
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "findings": [
            {"name": f.name, "state": f.state, "detail": f.detail, "impact": f.impact}
            for f in findings
        ],
        "recommendation": recommendation,
        "rationale": rationale,
    }


def render_text(audit: dict[str, Any]) -> str:
    lines = [
        "=== M5 Pre-Vote Audit ===",
        f"Timestamp: {audit['timestamp']}",
        "",
        "--- Findings ---",
    ]
    glyph = {"PASS": "[OK]", "WARN": "[WARN]", "FAIL": "[FAIL]", "NOT-MEASURED": "[?]", "NOT-SHIPPED": "[--]"}
    for f in audit["findings"]:
        g = glyph[f["state"]]
        lines.append(f"{g} {f['name']}: {f['detail']}")
        if f["impact"]:
            lines.append(f"        impact: {f['impact']}")
    lines.append("")
    lines.append(f"=== RECOMMENDATION: {audit['recommendation']} ===")
    lines.append(f"Rationale: {audit['rationale']}")
    lines.append("")
    lines.append("Note: this audit is ADVISORY for the 5a.5 6-agent party-mode vote.")
    lines.append("Operator + party-mode verdict is authoritative; this script de-risks decision-load.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()
    audit = run_audit()
    output = json.dumps(audit, indent=2) if args.json else render_text(audit)
    print(output)
    # Exit code reflects recommendation severity
    rec = audit["recommendation"]
    if rec == "SHIP-READY":
        return 0
    if rec == "SHIP-CONDITIONAL":
        return 0  # acceptable; operator may proceed with SHIP-CONDITIONAL
    if rec == "ITERATE-RECOMMENDED":
        return 1
    if rec == "ROLLBACK-CANDIDATE":
        return 2
    return 1


if __name__ == "__main__":
    sys.exit(main())
