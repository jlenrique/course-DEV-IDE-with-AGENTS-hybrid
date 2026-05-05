from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ADR_PATH = REPO_ROOT / "docs" / "dev-guide" / "adr" / "0001-parity-contract-dsl.md"


def _read_adr() -> str:
    return ADR_PATH.read_text(encoding="utf-8")


def test_adr_0001_parity_contract_dsl_exists() -> None:
    assert ADR_PATH.exists(), ADR_PATH.as_posix()


def test_adr_contains_required_decision_sections() -> None:
    text = _read_adr()

    heading_patterns = [
        r"^##\s+\d+\.\s+.*registration.*mechanism",
        r"^##\s+\d+\.\s+.*transport.*declaration.*schema",
        r"^##\s+\d+\.\s+.*refactor.*target",
        r"^##\s+\d+\.\s+.*transport-DSL-completeness",
        r"^##\s+\d+\.\s+.*Decision-then-Foundation",
        r"^##\s+\d+\.\s+.*completeness.*flags",
    ]

    for pattern in heading_patterns:
        assert re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE), pattern


def test_adr_contains_appendix_a_audit_chain_design() -> None:
    text = _read_adr()

    assert re.search(
        r"^##\s+Appendix\s+A:\s+Audit-Chain\s+Integrity\s+Conceptual\s+Design",
        text,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    assert "AuditChainIntegrityError" in text
    assert "AuditChainOrderError" in text
    assert "AuditChainParentLinkError" in text
    assert "app/audit/errors.py" in text
