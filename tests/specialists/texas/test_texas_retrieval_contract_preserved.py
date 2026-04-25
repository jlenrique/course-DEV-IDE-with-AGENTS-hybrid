from __future__ import annotations

import hashlib
from pathlib import Path

NFR_I5_RETRIEVAL_CONTRACT_BASELINE_SHA256 = (
    "ac98ff6261adcd84b2910e1e21a1d9911a90974d6ac016f875cd835048601dd0"
)


def test_retrieval_contract_sha256_matches_pinned_baseline() -> None:
    source = Path("skills/bmad-agent-texas/references/retrieval-contract.md")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    assert digest == NFR_I5_RETRIEVAL_CONTRACT_BASELINE_SHA256


def test_pointer_file_exists_and_links_to_contract() -> None:
    pointer = Path("app/specialists/texas/expertise/retrieval-contract-ref.md")
    assert pointer.is_file()
    body = pointer.read_text(encoding="utf-8")
    assert "skills/bmad-agent-texas/references/retrieval-contract.md" in body
