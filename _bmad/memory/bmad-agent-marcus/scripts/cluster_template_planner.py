"""
Runtime bridge between clustered slide output and template selection.

This module consumes clustered `gary_slide_output` rows and emits an advisory
`cluster_template_plan` payload that can be attached to pass2 envelopes.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path
from typing import Any, Dict, Mapping

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))


def _load_module(module_name: str, filename: str):
    module_path = _SCRIPTS_DIR / filename
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:  # pragma: no cover
        raise RuntimeError(f"Unable to load module: {module_name} from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_library_mod = _load_module("cluster_template_library_runtime", "cluster_template_library.py")
_selector_mod = _load_module("cluster_template_selector_runtime", "cluster_template_selector.py")
DEFAULT_TEMPLATE_PATH = _library_mod.DEFAULT_TEMPLATE_PATH
load_cluster_template_library = _library_mod.load_cluster_template_library
select_cluster_template = _selector_mod.select_cluster_template

FORCE_TEMPLATE_RE = re.compile(r"force_template\s*:\s*([a-z0-9\-]+)", re.IGNORECASE)
EXCLUDE_TEMPLATES_RE = re.compile(r"exclude_templates\s*:\s*\[([^\]]*)\]", re.IGNORECASE)
PREFER_TEMPLATES_RE = re.compile(r"prefer_templates\s*:\s*\[([^\]]*)\]", re.IGNORECASE)
CLUSTER_OVERRIDE_RE = re.compile(
    r"cluster\s+([a-zA-Z0-9\-_]+)\s*:\s*force_template\s*=\s*([a-z0-9\-]+)",
    re.IGNORECASE,
)


def load_default_template_library() -> dict[str, Any]:
    return load_cluster_template_library(DEFAULT_TEMPLATE_PATH)


def _parse_template_list(raw: str) -> list[str]:
    values: list[str] = []
    for part in raw.split(","):
        value = part.strip().strip("'\"")
        if value:
            values.append(value)
    return values


def load_operator_template_overrides(operator_directives_path: Path | None) -> dict[str, Any]:
    if operator_directives_path is None or not operator_directives_path.is_file():
        return {"global": {}, "per_cluster": {}}
    text = operator_directives_path.read_text(encoding="utf-8")
    global_overrides: dict[str, Any] = {}
    per_cluster: dict[str, dict[str, Any]] = {}

    force_match = FORCE_TEMPLATE_RE.search(text)
    if force_match:
        global_overrides["force_template"] = force_match.group(1).strip()
    exclude_match = EXCLUDE_TEMPLATES_RE.search(text)
    if exclude_match:
        global_overrides["exclude_templates"] = _parse_template_list(exclude_match.group(1))
    prefer_match = PREFER_TEMPLATES_RE.search(text)
    if prefer_match:
        global_overrides["prefer_templates"] = _parse_template_list(prefer_match.group(1))

    for match in CLUSTER_OVERRIDE_RE.finditer(text):
        cluster_id = match.group(1).strip()
        template_id = match.group(2).strip()
        per_cluster[cluster_id] = {"force_template": template_id}

    return {"global": global_overrides, "per_cluster": per_cluster}


def _master_arc_phase_for_index(index: int, total: int) -> str:
    if total <= 1:
        return "middle"
    ratio = index / max(total - 1, 1)
    if ratio < 0.34:
        return "beginning"
    if ratio < 0.67:
        return "middle"
    return "end"


def _extract_signals_from_head(head_row: Mapping[str, Any]) -> dict[str, float]:
    text = " ".join(
        str(head_row.get(key) or "")
        for key in (
            "visual_description",
            "narrative_arc",
            "head_claim",
            "isolation_target",
            "source_ref",
        )
    ).lower()
    return {
        "single_core_idea": 1.0 if "single" in text or "key point" in text else 0.35,
        "multi_facet": 1.0 if any(k in text for k in ("framework", "multiple", "multi", "system")) else 0.35,
        "data_presence": 1.0 if any(k in text for k in ("data", "chart", "table", "stat", "percent")) else 0.2,
        "contrast_tension": 1.0 if any(k in text for k in ("contrast", "tradeoff", "versus", "tension")) else 0.2,
        "evidence_density": 1.0 if any(k in text for k in ("evidence", "case", "example")) else 0.25,
        "emotional_weight": 1.0 if any(k in text for k in ("story", "stakes", "impact", "emotion")) else 0.25,
        "visual_decomposability": 1.0 if any(k in text for k in ("diagram", "layers", "components", "decompose")) else 0.3,
    }


def _group_cluster_heads(gary_slide_output: list[dict[str, Any]]) -> list[dict[str, Any]]:
    heads: list[dict[str, Any]] = []
    for row in gary_slide_output:
        if not isinstance(row, dict):
            continue
        if str(row.get("cluster_role") or "").strip().lower() != "head":
            continue
        if not str(row.get("cluster_id") or "").strip():
            continue
        heads.append(row)
    heads.sort(key=lambda item: int(item.get("card_number", 10_000)))
    return heads


def build_cluster_template_plan(
    *,
    gary_slide_output: list[dict[str, Any]],
    template_library: dict[str, Any],
    operator_overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not isinstance(gary_slide_output, list):
        raise ValueError("gary_slide_output must be a list")
    heads = _group_cluster_heads(gary_slide_output)
    if not heads:
        return {"schema_version": "1.0", "clusters": []}

    overrides = operator_overrides or {"global": {}, "per_cluster": {}}
    global_overrides = overrides.get("global") if isinstance(overrides, dict) else {}
    if not isinstance(global_overrides, dict):
        global_overrides = {}
    per_cluster = overrides.get("per_cluster") if isinstance(overrides, dict) else {}
    if not isinstance(per_cluster, dict):
        per_cluster = {}

    previous_template_ids: list[str] = []
    recent_pacing_profiles: list[str] = []
    clusters: list[dict[str, Any]] = []
    selected_template_ids_by_cluster: dict[str, str] = {}
    total = len(heads)
    for idx, head in enumerate(heads):
        cluster_id = str(head.get("cluster_id") or "").strip()
        cluster_overrides = per_cluster.get(cluster_id, {}) if cluster_id else {}
        if not isinstance(cluster_overrides, dict):
            cluster_overrides = {}
        force_template = cluster_overrides.get("force_template", global_overrides.get("force_template"))
        selection = select_cluster_template(
            template_library=template_library,
            content_signals=_extract_signals_from_head(head),
            master_arc_phase=_master_arc_phase_for_index(idx, total),
            previous_template_ids=previous_template_ids,
            recent_pacing_profiles=recent_pacing_profiles,
            force_template=force_template,
            exclude_templates=global_overrides.get("exclude_templates", []),
            prefer_templates=global_overrides.get("prefer_templates", []),
        )
        ranking = selection.get("ranking", [])
        selected_row = ranking[0] if ranking else {}
        selected_template_id = str(selection.get("template_id") or "")
        selected_pacing = str(selected_row.get("pacing_profile") or "")
        previous_template_ids.append(selected_template_id)
        if selected_pacing:
            recent_pacing_profiles.append(selected_pacing)
        template_def = next(
            (
                template
                for template in template_library.get("templates", [])
                if isinstance(template, dict) and str(template.get("template_id") or "") == selected_template_id
            ),
            {},
        )
        expected_sequence = template_def.get("interstitial_sequence", []) if isinstance(template_def, dict) else []
        expected_count = template_def.get("interstitial_count") if isinstance(template_def, dict) else None
        template_constraints = {
            "head_word_range": template_def.get("head_word_range") if isinstance(template_def, dict) else None,
            "interstitial_word_ranges": (
                template_def.get("interstitial_word_ranges") if isinstance(template_def, dict) else None
            ),
        }
        clusters.append(
            {
                "cluster_id": cluster_id,
                "head_slide_id": str(head.get("slide_id") or ""),
                "master_arc_phase": selection.get("master_arc_phase"),
                "selected_template_id": selected_template_id,
                "selection_reasons": selection.get("reasons", []),
                "alternatives": selection.get("alternatives", []),
                "selection_ranking": ranking,
                "expected_interstitial_sequence": expected_sequence,
                "expected_interstitial_count": expected_count,
                "template_constraints": template_constraints,
            }
        )
        if cluster_id and selected_template_id:
            selected_template_ids_by_cluster[cluster_id] = selected_template_id
    return {
        "schema_version": "1.0",
        "clusters": clusters,
        "selected_template_ids_by_cluster": selected_template_ids_by_cluster,
    }

