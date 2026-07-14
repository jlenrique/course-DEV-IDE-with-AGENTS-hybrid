from __future__ import annotations

import json
import re

_CATALOG = re.compile(
    r"## Exact source-span selection catalog.*?```json\n(?P<body>.*?)\n```",
    re.DOTALL,
)


def select_catalog_ids(response_text: str, messages: list[dict[str, str]]) -> str:
    """Upgrade legacy test candidates to the current model-output contract."""
    try:
        payload = json.loads(response_text)
    except json.JSONDecodeError:
        return response_text
    if not isinstance(payload, dict) or not isinstance(payload.get("plan_units"), list):
        return response_text
    prompt = messages[1]["content"]
    match = _CATALOG.search(prompt)
    if match is None:
        raise AssertionError("Pass-1 prompt omitted the exact source-span catalog")
    catalog = json.loads(match.group("body"))
    entries = catalog["entries"]
    exact = {entry["text"]: entry["span_id"] for entry in entries}
    for unit in payload["plan_units"]:
        if not isinstance(unit, dict) or "source_refs" not in unit:
            continue
        refs = unit.pop("source_refs")
        selected: list[str] = []
        for ref in refs:
            span_id = exact.get(ref)
            if span_id is None:
                containing = [
                    entry["span_id"]
                    for entry in entries
                    if isinstance(ref, str) and ref in entry["text"]
                ]
                if len(containing) != 1:
                    raise AssertionError(
                        f"legacy test anchor has no unique catalog span: {ref!r}"
                    )
                span_id = containing[0]
            selected.append(span_id)
        unit["source_ref_ids"] = selected
    return json.dumps(payload)


__all__ = ["select_catalog_ids"]
