from __future__ import annotations

import pytest

from scripts.utilities.reading_path_derivation import derive_primary_name


@pytest.mark.parametrize(
    ("macro_layout", "text_substructure", "expected"),
    [
        ("split_image_text", "peer_boxes", "split_image_text"),
        ("split_image_text", "comparison_pair", "two_up_comparison"),
        ("two_pane", "comparison_pair", "two_up_comparison"),
        ("two_pane", "peer_boxes", "two_up_comparison"),
        ("multi_column", "peer_boxes", "multi_column"),
        ("text_hero_divider", "hero_message", "text_hero_divider"),
        ("center_out", "hero_message", "center_out"),
        ("diagram_driven", "peer_boxes", "diagram_driven"),
        ("single_text_block", "enumerated_process", "enumerated_process"),
        ("card_grid", "peer_boxes", "grid_quadrant"),
        ("single_text_block", "dense_exposition", "top_down"),
    ],
)
def test_tuple_to_primary_name_shape_pin(
    macro_layout: str,
    text_substructure: str,
    expected: str,
) -> None:
    assert derive_primary_name(macro_layout, text_substructure) == expected
