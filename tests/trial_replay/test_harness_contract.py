from pathlib import Path


def test_trial_replay_harness_contract_scaffold_exists() -> None:
    assert Path("tests/trial_replay").is_dir()
