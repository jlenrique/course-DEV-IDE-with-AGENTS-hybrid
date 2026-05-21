from __future__ import annotations

import pytest

from app.specialists.compositor import _act as compositor_act
from tests.specialists.compositor._fixtures import compositor_payload


@pytest.mark.timeout(30)
def test_assembly_guide_field_masked_hash_is_stable(tmp_path) -> None:
    payload = compositor_payload(tmp_path)
    first = compositor_act.run_compositor_pipeline(payload)
    first_text = compositor_act.Path(first["assembly_guide_path"]).read_text(encoding="utf-8")

    second = compositor_act.run_compositor_pipeline(payload)
    second_text = compositor_act.Path(second["assembly_guide_path"]).read_text(encoding="utf-8")

    assert first_text != ""
    assert "generated_at" in first_text
    assert compositor_act.mask_assembly_guide(first_text) == compositor_act.mask_assembly_guide(
        second_text
    )
    assert first["assembly_guide_field_masked_hash"] == second["assembly_guide_field_masked_hash"]
