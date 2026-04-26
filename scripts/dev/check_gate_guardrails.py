from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    from app.gates.guardrails import scan_paths

    gate_paths = sorted((ROOT / "app" / "gates").rglob("*.py"))
    scan_paths(gate_paths)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - CLI path
        print(type(exc).__name__, str(exc), file=sys.stderr)
        raise SystemExit(1) from exc
