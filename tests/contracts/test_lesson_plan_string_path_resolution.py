"""String-path resolution pins (drift micro-batch, party consensus 2026-06-12).

The 2026-05-07 namespace retirement (top-level ``marcus`` -> ``app.marcus``)
was pinned by import-linter contract M5 — which reads *imports* and is
structurally blind to dotted/slashed paths living in STRING literals. The
drift audit found two registries carrying retired ``marcus.*`` strings that
no checker read (`producer_class_path`, nine `module_path` rows, and the
coverage-manifest AST checker's canonical-import token), and the stale rows
made ``build_coverage_manifest`` crash on its own default inventory.

Two layered pins (Murat ruling):

1. Resolution — every string path in the registries must actually resolve
   (importlib for dotted class paths; Path.exists for file paths). Catches
   stale strings we don't know about yet.
2. Grep-ratchet — the retired prefix may not reappear in app/ string-space
   at all. Catches strings that *resolve* through a leftover shim but are
   still wrong (resolvable != correct).
"""

from __future__ import annotations

import importlib
import re
from pathlib import Path

from app.marcus.lesson_plan.coverage_manifest import DEFAULT_COVERAGE_INVENTORY
from app.marcus.lesson_plan.modality_registry import MODALITY_REGISTRY

REPO_ROOT = Path(__file__).resolve().parents[2]

# Retired prefix in either dotted or slashed form, NOT already preceded by
# the canonical app prefix. Both lookbehinds are fixed-width.
_RETIRED_PREFIX = re.compile(r"(?<!app\.)(?<!app/)\bmarcus[./]lesson_plan")


def test_every_producer_class_path_resolves_via_importlib() -> None:
    checked = 0
    for entry in MODALITY_REGISTRY.values():
        if entry.producer_class_path is None:
            continue
        module_name, _, class_name = entry.producer_class_path.rpartition(".")
        module = importlib.import_module(module_name)
        assert hasattr(module, class_name), (
            f"{entry.modality_ref}: {entry.producer_class_path} imports but "
            f"{class_name!r} is not defined on {module_name}"
        )
        checked += 1
    assert checked >= 1  # blueprint at minimum; guards a hollowed registry


def test_every_non_deferred_coverage_module_path_exists_on_disk() -> None:
    for entry in DEFAULT_COVERAGE_INVENTORY:
        if entry.deferred:
            # Deferred rows are audit-incomplete reminders for files that do
            # not exist yet (32-2a); existence is asserted only at claim time.
            continue
        assert (REPO_ROOT / entry.module_path).exists(), (
            f"step {entry.step_id}: module_path {entry.module_path!r} does "
            "not exist relative to the repo root — _resolve_status would "
            "raise 'done but module does not exist' for a done owner story"
        )


def test_retired_marcus_prefix_absent_from_app_string_space() -> None:
    offenders: list[str] = []
    for path in (REPO_ROOT / "app").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for match in _RETIRED_PREFIX.finditer(text):
            line_no = text.count("\n", 0, match.start()) + 1
            offenders.append(f"{path.relative_to(REPO_ROOT).as_posix()}:{line_no}")
    assert offenders == [], (
        "retired top-level `marcus` prefix found in app/ string-space "
        "(import-linter M5 cannot see strings — fix to app.marcus / "
        f"app/marcus): {offenders}"
    )
