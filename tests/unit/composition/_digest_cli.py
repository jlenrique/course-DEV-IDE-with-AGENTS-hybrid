"""Subprocess entrypoint for the determinism floor (floor a).

Invoked under varying PYTHONHASHSEED in a fresh interpreter so the digest is
proven hashseed-independent (canonical-JSON + sha256, no set-iteration order in
the hashed payload). Prints the two-part digest as a single JSON line.

Usage: python -m tests.unit.composition._digest_cli deck,motion
"""

from __future__ import annotations

import json
import sys

from app.marcus.lesson_plan.composition import compose_and_digest
from app.models.state.component_selection import ComponentSelection


def main(argv: list[str]) -> int:
    selected = set(argv[1].split(",")) if len(argv) > 1 and argv[1] else {"deck"}
    sel = ComponentSelection(
        deck="deck" in selected,
        motion="motion" in selected,
        workbook="workbook" in selected,
    )
    d = compose_and_digest(sel)
    sys.stdout.write(
        json.dumps(
            {
                "input_closure_digest": d.input_closure_digest,
                "composed_graph_digest": d.composed_graph_digest,
                "digest_schema_version": d.digest_schema_version,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
