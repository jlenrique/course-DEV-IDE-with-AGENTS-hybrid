from __future__ import annotations

import pytest
import yaml

from app.specialists.wanda.graph import build_wanda_graph
from tests.integration.scaffold_conformance.scaffold_contract import validate_scaffold
from tests.parity._sanctum_parity_base import REPO_ROOT, SanctumParityTestBase


@pytest.mark.timeout(30)
class TestWandaActivationContract(SanctumParityTestBase):
    specialist_name = "wanda"
    class_template_id = "C"

    def cold_activation_smoke(self) -> None:
        assert build_wanda_graph().nodes

    def test_class_c_scaffold_conformance(self) -> None:
        result = validate_scaffold("wanda", build_wanda_graph())
        assert result.is_conforming
        self.assert_class_template_conformance()

    def test_six_file_bmb_sanctum_pattern(self) -> None:
        self.assert_skill_md_minimal_frontmatter()
        self.assert_sanctum_path_equality()

    def test_gamma_api_client_binding(self) -> None:
        source = (REPO_ROOT / "app" / "specialists" / "wanda" / "_act.py").read_text(
            encoding="utf-8"
        )
        client_source = (REPO_ROOT / "scripts" / "api_clients" / "wondercraft_client.py").read_text(
            encoding="utf-8"
        )
        assert "WondercraftClient" in source
        assert "generate_audio_bed" in source
        assert "class WondercraftClient" in client_source
        assert "requests." not in source

    def test_vcr_cassettes_present(self) -> None:
        cassette_dir = REPO_ROOT / "tests" / "fixtures" / "specialist-replay" / "wanda"
        assert (cassette_dir / "wondercraft_audio_bed_happy_path.yaml").is_file()

    def test_credential_rotation_register_entry(self) -> None:
        path = REPO_ROOT / "state" / "config" / "credential-rotation-register.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        rows = data.get("credentials", [])
        wondercraft = next(row for row in rows if row["provider"] == "wondercraft")
        assert wondercraft["owner"] == "operator"
        assert wondercraft["rotation_cadence_days"] == 90
        assert "WONDERCRAFT_API_KEY" in wondercraft["secret_store_reference"]

    def test_rate_limit_budget_declared(self) -> None:
        path = REPO_ROOT / "app" / "specialists" / "wanda" / "config.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data["rate_limit_per_minute"] > 0
        assert data["daily_budget_usd"] > 0
        assert data["per_invocation_cap_usd"] <= 0.40

    def test_cache_hit_rate_not_applicable(self) -> None:
        source = (REPO_ROOT / "app" / "specialists" / "wanda" / "model_config.yaml").read_text(
            encoding="utf-8"
        )
        assert "REST-API tool-dispatch" in source
        assert not (REPO_ROOT / "tests" / "end_to_end" / "test_wanda_cache_hit_rate.py").exists()

    def test_operator_gated_canary_documented(self) -> None:
        spec = (
            REPO_ROOT
            / "_bmad-output"
            / "implementation-artifacts"
            / "migration-7b-9-wanda-port-shape-onto-scaffold.md"
        ).read_text(encoding="utf-8")
        assert "Operator-gated AC-9-B" in spec
        assert "cost" in spec

    def test_cold_activation_smoke(self) -> None:
        self.cold_activation_smoke()
