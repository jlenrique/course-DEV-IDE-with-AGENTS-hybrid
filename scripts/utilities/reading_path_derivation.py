"""Pinned derivation from reading-path tuple axes to primary names."""

from __future__ import annotations

from app.models.perception.perception_artifact import MacroLayout, ReadingPath, TextSubstructure


def derive_primary_name(
    macro_layout: MacroLayout | str,
    text_substructure: TextSubstructure | str,
) -> ReadingPath:
    """Project tuple axes to the legacy-compatible ``reading_path`` primary name."""

    if text_substructure == "comparison_pair":
        return "two_up_comparison"
    if macro_layout == "two_pane":
        return "two_up_comparison"
    if text_substructure == "enumerated_process":
        return "enumerated_process"
    if macro_layout == "center_out":
        return "center_out"
    if macro_layout == "diagram_driven":
        return "diagram_driven"
    if macro_layout == "split_image_text":
        return "split_image_text"
    if macro_layout == "multi_column":
        return "multi_column"
    if macro_layout == "card_grid":
        return "grid_quadrant"
    if macro_layout == "text_hero_divider":
        return "text_hero_divider"
    return "top_down"


__all__ = ["derive_primary_name"]
