"""OPERATOR/INPUTS/OUTPUTS/REFERENCE help-text structure (Story 7a.7, AC-7.7-B)."""

from __future__ import annotations

import importlib

import pytest

SHIM_MODULES = [
    "app.marcus.cli.gate_shims.g1_shim",
    "app.marcus.cli.gate_shims.g2c_shim",
    "app.marcus.cli.gate_shims.g3_shim",
    "app.marcus.cli.gate_shims.g4_shim",
]


@pytest.mark.parametrize("module_name", SHIM_MODULES)
def test_shim_help_text_has_four_named_sections_in_order(module_name: str) -> None:
    """Each shim --help carries OPERATOR → INPUTS → OUTPUTS → REFERENCE."""
    from app.marcus.cli.gate_shims._shim_parser import build_shim_parser

    module = importlib.import_module(module_name)
    parser = build_shim_parser(module.GATE_ID)
    help_text = parser.format_help()
    operator_idx = help_text.index("OPERATOR\n========")
    inputs_idx = help_text.index("INPUTS\n======")
    outputs_idx = help_text.index("OUTPUTS\n=======")
    reference_idx = help_text.index("REFERENCE\n=========")
    assert operator_idx < inputs_idx < outputs_idx < reference_idx, (
        f"Section order incorrect for {module_name}"
    )


@pytest.mark.parametrize("module_name", SHIM_MODULES)
def test_shim_help_text_underlines_pinned_at_8_chars(module_name: str) -> None:
    """Underlines (===) length-pinned at 8 chars for grep stability."""
    from app.marcus.cli.gate_shims._shim_parser import build_shim_parser

    module = importlib.import_module(module_name)
    parser = build_shim_parser(module.GATE_ID)
    help_text = parser.format_help()
    # OPERATOR underline is exactly 8 = chars
    assert "OPERATOR\n========\n" in help_text or "OPERATOR\n========" in help_text


@pytest.mark.parametrize("module_name", SHIM_MODULES)
def test_shim_help_outputs_section_documents_exit_codes(module_name: str) -> None:
    """OUTPUTS section names exit codes 0/1/2."""
    from app.marcus.cli.gate_shims._shim_parser import build_shim_parser

    module = importlib.import_module(module_name)
    parser = build_shim_parser(module.GATE_ID)
    help_text = parser.format_help()
    outputs_section = help_text.split("OUTPUTS\n=======")[1].split("REFERENCE")[0]
    assert "exit 0" in outputs_section
    assert "exit 1" in outputs_section
    assert "exit 2" in outputs_section


@pytest.mark.parametrize("module_name", SHIM_MODULES)
def test_shim_help_reference_section_lists_per_gate_doc(module_name: str) -> None:
    """REFERENCE section includes the per-gate operator-reference doc path."""
    from app.marcus.cli.gate_shims._shim_parser import build_shim_parser

    module = importlib.import_module(module_name)
    parser = build_shim_parser(module.GATE_ID)
    help_text = parser.format_help()
    reference_section = help_text.split("REFERENCE\n=========")[1]
    expected_doc = f"docs/conversational-gates/{module.GATE_ID.lower()}-operator-reference.md"
    assert expected_doc in reference_section
