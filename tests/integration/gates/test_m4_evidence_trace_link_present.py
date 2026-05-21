from __future__ import annotations

from app.gates.party_mode_as_interrupt import finding_record_has_trace_link


def test_m4_evidence_trace_link_present() -> None:
    finding_record = {
        "finding_id": "FR42-1",
        "summary": "Trace evidence attached",
        "trace_link": "https://smith.langchain.com/traces/trace-123",
    }

    assert finding_record_has_trace_link(finding_record) is True
