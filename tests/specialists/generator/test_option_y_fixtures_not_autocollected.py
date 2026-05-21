from __future__ import annotations

from tests.fixtures.specialists.fixture_generated_specialist_for_acceptance_test import (
    EXPECTED_TREE,
)


def test_option_y_fixture_module_is_data_only() -> None:
    assert isinstance(EXPECTED_TREE, list)
    assert len(EXPECTED_TREE) == 9
    assert all(path.startswith(("app/", "tests/")) for path in EXPECTED_TREE)
