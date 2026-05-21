from pathlib import Path


def test_end_to_end_harness_contract_scaffold_exists() -> None:
    assert Path("tests/end_to_end").is_dir()
