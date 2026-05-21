"""LangSmith span-tag contract integration test (Story 1.1c, AC-1.1c-D).

Skips cleanly when ``LANGSMITH_API_KEY`` is unset (sandbox-AC discipline:
no operator-side service requirement). When the key is set, exercises the
smoke harness, lets LangSmith export the spans, then asserts every span on
the recent trace carries the four canonical contract tag keys.

Pairs with the unit-tier pin in
`tests/unit/observability/test_span_tag_contract_pin.py` which asserts the
schema constant itself does not drift — the two tiers together close
AC-1.1c-D and AC-1.1c-D2.
"""

from __future__ import annotations

import os
import time
from datetime import UTC, datetime

import pytest

from app.runtime.span_tags import REQUIRED_SPAN_TAG_KEYS
from app.smoke_test import run_smoke


@pytest.mark.live_api
def test_smoke_emits_spans_with_contract_tags() -> None:
    api_key = os.getenv("LANGSMITH_API_KEY")
    if not api_key:
        pytest.skip("LANGSMITH_API_KEY unset; AC-1.1c-D requires the live LangSmith export")

    project = os.getenv("LANGSMITH_PROJECT")
    if not project:
        pytest.skip("LANGSMITH_PROJECT unset; cannot scope the trace lookup")

    try:
        from langsmith import Client
    except ImportError:
        pytest.skip("langsmith SDK not importable; skipping live trace assertion")

    started_at = datetime.now(UTC)
    result = run_smoke(input_value="span-tag-pin")
    assert result.get("smoke") == "ok"

    client = Client(api_key=api_key)
    deadline = time.monotonic() + 30.0
    runs: list = []
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            runs = list(
                client.list_runs(
                    project_name=project,
                    start_time=started_at,
                    limit=20,
                )
            )
        except Exception as exc:  # network / auth churn — retry
            last_error = exc
            time.sleep(2.0)
            continue
        if runs:
            break
        time.sleep(2.0)
    else:
        pytest.skip(
            f"no LangSmith runs surfaced within 30s for project {project!r} "
            f"(last error: {last_error!r}); cannot assert contract"
        )

    missing_per_run: list[tuple[str, set[str]]] = []
    for run in runs:
        tags_payload = getattr(run, "extra", None) or {}
        metadata = tags_payload.get("metadata") or {} if isinstance(tags_payload, dict) else {}
        present = set(metadata.keys())
        missing = set(REQUIRED_SPAN_TAG_KEYS) - present
        if missing:
            missing_per_run.append((str(getattr(run, "id", "?")), missing))

    assert not missing_per_run, (
        "LangSmith span-tag contract violation; runs missing required keys "
        f"({sorted(REQUIRED_SPAN_TAG_KEYS)}): {missing_per_run}"
    )
