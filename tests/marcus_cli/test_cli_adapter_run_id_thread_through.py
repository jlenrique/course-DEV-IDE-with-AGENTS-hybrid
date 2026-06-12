from __future__ import annotations

from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from app.marcus.cli import trial as trial_module


def test_start_trial_threads_effective_trial_id_to_section_02a_adapter(
    tmp_path: Path,
) -> None:
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    (corpus_dir / "lesson.md").write_text("lesson", encoding="utf-8")
    runs_root = tmp_path / "runs"
    trial_id = uuid4()
    directive_path = runs_root / str(trial_id) / "directive.yaml"

    def _compose_and_write(**kwargs):
        directive_path.parent.mkdir(parents=True, exist_ok=True)
        directive_path.write_text("run_id: test\nsources: []\n", encoding="utf-8")
        return directive_path, "0" * 64

    with patch.object(
        trial_module,
        "compose_and_write",
        side_effect=_compose_and_write,
    ) as mock_compose:
        result = trial_module.start_trial(
            preset="production",
            input_path=corpus_dir,
            operator_id="operator_test",
            trial_id=trial_id,
            allow_offline_cost_report=True,
            runs_root=runs_root,
            confirm_fn=lambda **_kwargs: "saved-only",
        )

    assert result["status"] == "saved-only"
    kwargs = mock_compose.call_args.kwargs
    assert kwargs["corpus_dir"] == corpus_dir
    assert kwargs["run_dir"] == runs_root / str(trial_id)
    assert kwargs["run_id"] == trial_id
