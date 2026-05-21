"""Cora in-graph block-mode guard."""

from __future__ import annotations

import importlib.util
import logging
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.gates.errors import GateError
from app.models.state.story_state import StoryState

LOGGER = logging.getLogger(__name__)


def _load_preclosure_hook() -> tuple[type[Any], Any]:
    hook_path = (
        Path(__file__).resolve().parents[2]
        / "skills"
        / "bmad-agent-cora"
        / "scripts"
        / "preclosure_hook.py"
    )
    spec = importlib.util.spec_from_file_location("cora_preclosure_hook", hook_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"unable to load preclosure hook at {hook_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.PreClosureResult, module.run_preclosure_check


PreClosureResult, run_preclosure_check = _load_preclosure_hook()


def block_mode_node(
    state: StoryState,
    *,
    diff_paths: Sequence[str] | None = None,
    skip_l1: bool = False,
) -> dict[str, object]:
    """Run the pre-closure hook inside the Cora graph."""
    changed_paths = list(diff_paths or [])
    result = run_preclosure_check(
        state.story_id,
        changed_paths,
        skip_l1=skip_l1,
    )
    LOGGER.info(
        "cora block-mode story_id=%s classification=%s permit_closure=%s changed_paths=%d",
        state.story_id,
        result.classification,
        result.permit_closure,
        len(changed_paths),
    )
    if not result.permit_closure:
        raise GateError("cora_block_mode", result.operator_message)
    return {"updated_at": datetime.now(UTC)}

__all__ = ["PreClosureResult", "block_mode_node"]
