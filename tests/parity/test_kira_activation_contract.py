from __future__ import annotations

import pytest
import yaml

from app.specialists.kira.graph import build_kira_graph
from tests.integration.scaffold_conformance.scaffold_contract import validate_scaffold
from tests.parity._sanctum_parity_base import REPO_ROOT, SanctumParityTestBase


@pytest.mark.timeout(30)
class TestKiraActivationContract(SanctumParityTestBase):
    specialist_name = "kira"
    class_template_id = "C"

    def cold_activation_smoke(self) -> None:
        assert build_kira_graph().nodes

    def test_class_c_scaffold_conformance(self) -> None:
        result = validate_scaffold("kira", build_kira_graph())
        assert result.is_conforming
        self.assert_class_template_conformance()

    def test_six_file_bmb_sanctum_pattern(self) -> None:
        self.assert_skill_md_minimal_frontmatter()
        self.assert_sanctum_path_equality()

    def test_gamma_api_client_binding(self) -> None:
        source = (REPO_ROOT / "app" / "specialists" / "kira" / "_act.py").read_text(
            encoding="utf-8"
        )
        client_source = (REPO_ROOT / "scripts" / "api_clients" / "kling_client.py").read_text(
            encoding="utf-8"
        )
        assert "KlingClient" in source
        assert "generate_motion" in source
        assert "def text_to_video(" in client_source
        assert "requests." not in source

    def test_vcr_cassettes_present(self) -> None:
        cassette_dir = REPO_ROOT / "tests" / "fixtures" / "specialist-replay" / "kira"
        assert (cassette_dir / "kling_motion_happy_path.yaml").is_file()
        assert (cassette_dir / "kling_budget_exhaust.yaml").is_file()

    def test_credential_rotation_register_entry(self) -> None:
        path = REPO_ROOT / "state" / "config" / "credential-rotation-register.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        rows = data.get("credentials", [])
        kling = next(row for row in rows if row["provider"] == "kling")
        assert kling["owner"] == "operator"
        assert kling["rotation_cadence_days"] == 90
        assert "KLING_ACCESS_KEY" in kling["secret_store_reference"]

    def test_rate_limit_budget_declared(self) -> None:
        path = REPO_ROOT / "app" / "specialists" / "kira" / "config.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data["rate_limit_per_minute"] > 0
        assert data["daily_budget_usd"] > 0
        assert data["per_invocation_cap_usd"] <= 0.40

    def test_cache_hit_rate_not_applicable(self) -> None:
        source = (REPO_ROOT / "app" / "specialists" / "kira" / "model_config.yaml").read_text(
            encoding="utf-8"
        )
        assert "REST-API tool-dispatch" in source
        assert not (REPO_ROOT / "tests" / "end_to_end" / "test_kira_cache_hit_rate.py").exists()

    def test_operator_gated_canary_documented(self) -> None:
        spec = (
            REPO_ROOT
            / "_bmad-output"
            / "implementation-artifacts"
            / "migration-7b-7-kira-port-shape.md"
        ).read_text(encoding="utf-8")
        assert "Operator-gated AC-7-B" in spec
        assert "cost" in spec

    def test_cold_activation_smoke(self) -> None:
        self.cold_activation_smoke()
