from __future__ import annotations

import pytest
import yaml

from app.specialists.enrique.graph import build_enrique_graph
from tests.integration.scaffold_conformance.scaffold_contract import validate_scaffold
from tests.parity._sanctum_parity_base import REPO_ROOT, SanctumParityTestBase


@pytest.mark.timeout(30)
class TestEnriqueActivationContract(SanctumParityTestBase):
    specialist_name = "enrique"
    class_template_id = "C"

    def cold_activation_smoke(self) -> None:
        assert build_enrique_graph().nodes

    def test_class_c_scaffold_conformance(self) -> None:
        result = validate_scaffold("enrique", build_enrique_graph())
        assert result.is_conforming
        self.assert_class_template_conformance()

    def test_six_file_bmb_sanctum_pattern(self) -> None:
        self.assert_skill_md_minimal_frontmatter()
        self.assert_sanctum_path_equality()

    def test_gamma_api_client_binding(self) -> None:
        source = (REPO_ROOT / "app" / "specialists" / "enrique" / "_act.py").read_text(
            encoding="utf-8"
        )
        client_source = (REPO_ROOT / "scripts" / "api_clients" / "elevenlabs_client.py").read_text(
            encoding="utf-8"
        )
        assert "ElevenLabsClient" in source
        assert "text_to_speech" in source
        assert "def text_to_speech(" in client_source
        assert "requests." not in source

    def test_vcr_cassettes_present(self) -> None:
        cassette_dir = REPO_ROOT / "tests" / "fixtures" / "specialist-replay" / "enrique"
        assert (cassette_dir / "elevenlabs_voice_preview.yaml").is_file()
        assert (cassette_dir / "elevenlabs_narration_happy_path.yaml").is_file()

    def test_credential_rotation_register_entry(self) -> None:
        path = REPO_ROOT / "state" / "config" / "credential-rotation-register.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        rows = data.get("credentials", [])
        elevenlabs = next(row for row in rows if row["provider"] == "elevenlabs")
        assert elevenlabs["owner"] == "operator"
        assert elevenlabs["rotation_cadence_days"] == 90
        assert "ELEVENLABS_API_KEY" in elevenlabs["secret_store_reference"]

    def test_rate_limit_budget_declared(self) -> None:
        path = REPO_ROOT / "app" / "specialists" / "enrique" / "config.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data["rate_limit_per_minute"] > 0
        assert data["daily_budget_usd"] > 0
        assert data["per_invocation_cap_usd"] <= 0.40

    def test_cache_hit_rate_not_applicable(self) -> None:
        source = (REPO_ROOT / "app" / "specialists" / "enrique" / "model_config.yaml").read_text(
            encoding="utf-8"
        )
        assert "REST-API tool-dispatch" in source
        assert not (REPO_ROOT / "tests" / "end_to_end" / "test_enrique_cache_hit_rate.py").exists()

    def test_operator_gated_canary_documented(self) -> None:
        spec = (
            REPO_ROOT
            / "_bmad-output"
            / "implementation-artifacts"
            / "migration-7b-8-enrique-port-shape.md"
        ).read_text(encoding="utf-8")
        assert "Operator-gated AC-8-B" in spec
        assert "cost" in spec

    def test_voice_selection_hil_contract_write_parity(self, tmp_path) -> None:
        from app.specialists.enrique import _act as enrique_act

        class FakeClient:
            def list_voices(self) -> list[dict[str, object]]:
                return [{"voice_id": "voice-a", "name": "A", "preview_url": "https://cdn/a.mp3"}]

        enrique_act.build_voice_selection_contract(
            {"bundle_path": str(tmp_path)},
            client=FakeClient(),  # type: ignore[arg-type]
        )
        assert (tmp_path / "voice-selection" / "voice-preview-options.json").is_file()
        assert (tmp_path / "voice-selection" / "voice-selection-review.md").is_file()
        assert (tmp_path / "voice-selection" / "voice-selection.json").is_file()

    def test_cold_activation_smoke(self) -> None:
        self.cold_activation_smoke()
