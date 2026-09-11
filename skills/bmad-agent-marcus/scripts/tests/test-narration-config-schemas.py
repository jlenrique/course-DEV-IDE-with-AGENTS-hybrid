"""Tests for narration config YAML schemas.

Validates narration-grounding-profiles.yaml and narration-script-parameters.yaml
for structural correctness, required fields, and cross-file consistency with the
G4 fidelity contract.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[4]
CONFIG_DIR = ROOT / "state" / "config"
PROFILES_PATH = CONFIG_DIR / "narration-grounding-profiles.yaml"
PARAMS_PATH = CONFIG_DIR / "narration-script-parameters.yaml"
G4_CONTRACT_PATH = CONFIG_DIR / "fidelity-contracts" / "g4-narration-script.yaml"
VERA_G4_PROTOCOL_PATH = (
    ROOT / "skills" / "bmad-agent-fidelity-assessor" / "references" / "gate-evaluation-protocol.md"
)

FIDELITY_CLASSES = {"creative", "literal-text", "literal-visual"}


# ---- Fixture: load YAML files ----

@pytest.fixture(scope="module")
def profiles() -> dict:
    assert PROFILES_PATH.exists(), f"Missing: {PROFILES_PATH}"
    return yaml.safe_load(PROFILES_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def params() -> dict:
    assert PARAMS_PATH.exists(), f"Missing: {PARAMS_PATH}"
    return yaml.safe_load(PARAMS_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def g4_contract() -> dict:
    assert G4_CONTRACT_PATH.exists(), f"Missing: {G4_CONTRACT_PATH}"
    return yaml.safe_load(G4_CONTRACT_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def vera_g4_protocol_text() -> str:
    assert VERA_G4_PROTOCOL_PATH.exists(), f"Missing: {VERA_G4_PROTOCOL_PATH}"
    return VERA_G4_PROTOCOL_PATH.read_text(encoding="utf-8")


# ---- Narration Grounding Profiles Tests ----

class TestNarrationGroundingProfiles:
    VALID_STANCES = {"explain-behind", "read-along", "guided-interpretation"}

    def test_schema_version_present(self, profiles: dict) -> None:
        assert "schema_version" in profiles

    def test_profiles_key_exists(self, profiles: dict) -> None:
        assert "profiles" in profiles
        assert isinstance(profiles["profiles"], dict)

    def test_all_fidelity_classes_have_profiles(self, profiles: dict) -> None:
        profile_keys = set(profiles["profiles"].keys())
        assert profile_keys == FIDELITY_CLASSES

    @pytest.mark.parametrize("fidelity_class", sorted(FIDELITY_CLASSES))
    def test_profile_has_required_fields(self, profiles: dict, fidelity_class: str) -> None:
        profile = profiles["profiles"][fidelity_class]
        required = {"slide_role", "source_role", "stance", "min_source_claims", "description"}
        missing = required - set(profile.keys())
        assert not missing, f"{fidelity_class} missing: {missing}"

    @pytest.mark.parametrize("fidelity_class", sorted(FIDELITY_CLASSES))
    def test_min_source_claims_is_non_negative_int(self, profiles: dict, fidelity_class: str) -> None:
        val = profiles["profiles"][fidelity_class]["min_source_claims"]
        assert isinstance(val, int) and val >= 0

    @pytest.mark.parametrize("fidelity_class", sorted(FIDELITY_CLASSES))
    def test_profile_stance_is_valid(self, profiles: dict, fidelity_class: str) -> None:
        stance = profiles["profiles"][fidelity_class]["stance"]
        assert stance in self.VALID_STANCES

    def test_creative_profile_demands_source_primary(self, profiles: dict) -> None:
        creative = profiles["profiles"]["creative"]
        assert creative["source_role"] == "primary"
        assert creative["min_source_claims"] >= 1


# ---- Narration Script Parameters Tests ----

class TestNarrationScriptParameters:
    def test_schema_version_present(self, params: dict) -> None:
        assert "schema_version" in params
        assert params["schema_version"] == "1.1"

    REQUIRED_TOP_LEVEL = [
        "narration_density",
        "slide_echo",
        "visual_narration",
        "terminology_treatment",
        "pedagogical_bridging",
        "engagement_stance",
        "source_depth",
        "pronunciation_sensitivity",
        "runtime_variability",
        "narration_profile_controls",
    ]

    @pytest.mark.parametrize("section", REQUIRED_TOP_LEVEL)
    def test_top_level_section_exists(self, params: dict, section: str) -> None:
        assert section in params, f"Missing top-level section: {section}"

    # -- narration_density --

    def test_density_target_wpm_in_range(self, params: dict) -> None:
        wpm = params["narration_density"]["target_wpm"]
        assert 100 <= wpm <= 200, f"target_wpm {wpm} outside plausible range"

    def test_density_min_lt_mean_lt_max(self, params: dict) -> None:
        d = params["narration_density"]
        assert d["min_words_per_slide"] < d["mean_words_per_slide"] < d["max_words_per_slide"]

    def test_cluster_narration_ranges_configured(self, params: dict) -> None:
        cluster = params["narration_density"]["cluster_narration"]
        assert cluster["cluster_head_word_range"] == [80, 140]
        assert cluster["interstitial_word_range"] == [25, 40]

    # -- slide_echo --

    VALID_ECHO_VALUES = {"verbatim", "paraphrase", "inspired"}

    def test_slide_echo_default_is_valid(self, params: dict) -> None:
        assert params["slide_echo"]["default"] in self.VALID_ECHO_VALUES

    def test_slide_echo_per_fidelity_covers_all_classes(self, params: dict) -> None:
        overrides = set(params["slide_echo"]["per_fidelity_override"].keys())
        assert overrides == FIDELITY_CLASSES

    @pytest.mark.parametrize("fidelity_class", sorted(FIDELITY_CLASSES))
    def test_slide_echo_override_values_valid(self, params: dict, fidelity_class: str) -> None:
        val = params["slide_echo"]["per_fidelity_override"][fidelity_class]
        assert val in self.VALID_ECHO_VALUES

    # -- visual_narration --

    def test_visual_narration_deictic_valid(self, params: dict) -> None:
        valid = {"none", "minimal", "moderate", "frequent"}
        assert params["visual_narration"]["deictic_references"] in valid

    def test_visual_narration_depth_valid(self, params: dict) -> None:
        valid = {"identify", "summarize", "detailed"}
        assert params["visual_narration"]["description_depth"] in valid

    def test_visual_narration_reference_function_valid(self, params: dict) -> None:
        valid = {"annotation", "audience_guidance"}
        assert params["visual_narration"]["reference_function"] in valid

    def test_visual_narration_orientation_policy_valid(self, params: dict) -> None:
        valid = {"brief_only", "allowed", "none"}
        assert params["visual_narration"]["orientation_cue_policy"] in valid

    def test_visual_narration_meta_language_policy_valid(self, params: dict) -> None:
        valid = {"allowed", "discouraged", "forbidden"}
        assert params["visual_narration"]["meta_slide_language"] in valid

    def test_visual_narration_forbidden_phrases_is_list(self, params: dict) -> None:
        phrases = params["visual_narration"]["forbidden_meta_phrases"]
        assert isinstance(phrases, list)
        assert phrases, "forbidden_meta_phrases should not be empty when policy is configured"

    # -- terminology_treatment --

    def test_terminology_strategy_valid(self, params: dict) -> None:
        valid = {"inline_appositive", "parenthetical_aside", "no_gloss"}
        assert params["terminology_treatment"]["gloss_strategy"] in valid

    def test_terminology_audience_valid(self, params: dict) -> None:
        valid = {"novice", "intermediate", "expert"}
        assert params["terminology_treatment"]["audience_assumption"] in valid

    def test_terminology_domain_filter_is_list(self, params: dict) -> None:
        assert isinstance(params["terminology_treatment"]["gloss_domain_filter"], list)

    # -- pedagogical_bridging --

    def test_bridging_transition_style_valid(self, params: dict) -> None:
        valid = {"conceptual", "sequential", "question_driven", "narrative_arc"}
        assert params["pedagogical_bridging"]["transition_style"] in valid

    def test_bridge_frequency_scale_valid(self, params: dict) -> None:
        valid = {"minimal", "moderate", "rich"}
        assert params["pedagogical_bridging"]["bridge_frequency_scale"] in valid

    def test_spoken_bridge_policy_configured(self, params: dict) -> None:
        pol = params["pedagogical_bridging"]["spoken_bridge_policy"]
        assert pol["enforcement"] in {"off", "warn", "error"}
        assert isinstance(pol["intro_phrase_patterns"], list)
        assert isinstance(pol["outro_phrase_patterns"], list)
        assert len(pol["intro_phrase_patterns"]) >= 1
        assert len(pol["outro_phrase_patterns"]) >= 1

    def test_cluster_bridge_policy_configured(self, params: dict) -> None:
        policy = params["pedagogical_bridging"]["within_cluster_bridge_policy"]
        assert policy["default"] == "none"
        assert policy["tension_position_override"] == "pivot"

    def test_cluster_boundary_bridge_style_configured(self, params: dict) -> None:
        style = params["pedagogical_bridging"]["cluster_boundary_bridge_style"]
        assert style["mode"] == "synthesis_plus_forward_pull"
        assert style["target_seconds"] == [15, 20]
        assert style["target_words"] == [37, 50]

    # -- engagement_stance --

    def test_engagement_posture_valid(self, params: dict) -> None:
        valid = {"lecturer", "collegial_guide", "coach", "storyteller"}
        assert params["engagement_stance"]["posture"] in valid

    # -- source_depth --

    def test_source_depth_creative_valid(self, params: dict) -> None:
        valid = {"describe_visual", "teach_behind", "full_synthesis"}
        assert params["source_depth"]["creative_slides"] in valid

    def test_source_depth_literal_valid(self, params: dict) -> None:
        valid = {"confirm_visible", "light_enrich", "full_synthesis"}
        assert params["source_depth"]["literal_slides"] in valid

    # -- pronunciation_sensitivity --

    def test_pronunciation_auto_flag_is_bool(self, params: dict) -> None:
        assert isinstance(params["pronunciation_sensitivity"]["auto_flag"], bool)

    # -- runtime_variability --

    def test_runtime_variability_enabled_is_bool(self, params: dict) -> None:
        assert isinstance(params["runtime_variability"]["enabled"], bool)

    def test_runtime_variability_required_fields_non_empty(self, params: dict) -> None:
        fields = params["runtime_variability"]["required_manifest_fields"]
        assert isinstance(fields, list)
        assert len(fields) >= 5

    def test_runtime_variability_bridge_types_present(self, params: dict) -> None:
        bridge_types = params["runtime_variability"]["bridge_cadence"]["accepted_bridge_types"]
        assert isinstance(bridge_types, list)
        assert bridge_types
        assert "pivot" in bridge_types
        assert "cluster_boundary" in bridge_types

    def test_runtime_variability_cluster_override_enabled(self, params: dict) -> None:
        cadence = params["runtime_variability"]["bridge_cadence"]
        assert cadence["cluster_bridge_cadence_override"] is True

    # -- narration_profile_controls --

    def test_profile_controls_narrator_source_authority_valid(self, params: dict) -> None:
        valid = {"source-grounded", "balanced", "slide-led"}
        assert params["narration_profile_controls"]["narrator_source_authority"] in valid

    def test_profile_controls_slide_content_density_valid(self, params: dict) -> None:
        valid = {"lean", "adaptive", "dense"}
        assert params["narration_profile_controls"]["slide_content_density"] in valid

    def test_profile_controls_elaboration_budget_valid(self, params: dict) -> None:
        valid = {"low", "medium", "high"}
        assert params["narration_profile_controls"]["elaboration_budget"] in valid

    def test_profile_controls_connective_weight_valid(self, params: dict) -> None:
        valid = {"light", "balanced", "heavy"}
        assert params["narration_profile_controls"]["connective_weight"] in valid

    def test_profile_controls_callback_frequency_valid(self, params: dict) -> None:
        valid = {"sparse", "moderate", "frequent"}
        assert params["narration_profile_controls"]["callback_frequency"] in valid

    def test_profile_controls_visual_narration_coupling_valid(self, params: dict) -> None:
        valid = {"loose", "balanced", "tight"}
        assert params["narration_profile_controls"]["visual_narration_coupling"] in valid

    def test_profile_controls_rhetorical_richness_valid(self, params: dict) -> None:
        valid = {"restrained", "balanced", "expressive"}
        assert params["narration_profile_controls"]["rhetorical_richness"] in valid

    def test_profile_controls_vocabulary_register_valid(self, params: dict) -> None:
        valid = {"accessible", "professional", "specialist"}
        assert params["narration_profile_controls"]["vocabulary_register"] in valid

    def test_profile_controls_arc_awareness_valid(self, params: dict) -> None:
        valid = {"low", "medium", "high"}
        assert params["narration_profile_controls"]["arc_awareness"] in valid

    def test_profile_controls_narrative_tension_valid(self, params: dict) -> None:
        valid = {"low", "medium", "high"}
        assert params["narration_profile_controls"]["narrative_tension"] in valid

    def test_profile_controls_emotional_coloring_valid(self, params: dict) -> None:
        valid = {"neutral", "warm", "vivid"}
        assert params["narration_profile_controls"]["emotional_coloring"] in valid


# ---- Cross-file consistency tests ----

class TestCrossFileConsistency:
    def test_g4_gate_name_mentions_segment_manifest(self, g4_contract: dict) -> None:
        assert g4_contract["gate_name"] == "Narration Script + Segment Manifest"

    def test_g4_source_of_truth_references_segment_manifest_template(
        self, g4_contract: dict
    ) -> None:
        source_of_truth = g4_contract["source_of_truth"]
        assert source_of_truth["schema_ref"] == (
            "skills/bmad-agent-content-creator/references/template-narration-script.md"
        )
        assert source_of_truth["schema_ref_secondary"] == (
            "skills/bmad-agent-content-creator/references/template-segment-manifest.md"
        )

    def test_g4_07_references_config_files(self, g4_contract: dict) -> None:
        """G4-07 must reference both narration config files."""
        criteria = g4_contract["criteria"]
        g4_07 = next((c for c in criteria if c["id"] == "G4-07"), None)
        assert g4_07 is not None, "G4-07 criterion not found in contract"
        refs = g4_07.get("config_refs", [])
        assert any("narration-grounding-profiles" in r for r in refs)
        assert any("narration-script-parameters" in r for r in refs)

    def test_g4_07_requires_perception(self, g4_contract: dict) -> None:
        criteria = g4_contract["criteria"]
        g4_07 = next((c for c in criteria if c["id"] == "G4-07"), None)
        assert g4_07 is not None
        assert g4_07["requires_perception"] is True

    def test_g4_09_references_config_files(self, g4_contract: dict) -> None:
        criteria = g4_contract["criteria"]
        g4_09 = next((c for c in criteria if c["id"] == "G4-09"), None)
        assert g4_09 is not None, "G4-09 criterion not found in contract"
        refs = g4_09.get("config_refs", [])
        assert any("narration-grounding-profiles" in r for r in refs)
        assert any("narration-script-parameters" in r for r in refs)

    def test_g4_09_requires_perception(self, g4_contract: dict) -> None:
        criteria = g4_contract["criteria"]
        g4_09 = next((c for c in criteria if c["id"] == "G4-09"), None)
        assert g4_09 is not None
        assert g4_09["requires_perception"] is True

    def test_g4_08_perception_lineage_present(self, g4_contract: dict) -> None:
        criteria = g4_contract["criteria"]
        g4_08 = next((c for c in criteria if c["id"] == "G4-08"), None)
        assert g4_08 is not None, "G4-08 criterion not found in contract"
        assert g4_08["evaluation_type"] == "deterministic"
        assert g4_08["requires_perception"] is False

    def test_g4_10_references_runtime_policy(self, g4_contract: dict) -> None:
        criteria = g4_contract["criteria"]
        g4_10 = next((c for c in criteria if c["id"] == "G4-10"), None)
        assert g4_10 is not None, "G4-10 criterion not found in contract"
        refs = g4_10.get("config_refs", [])
        assert any("narration-script-parameters" in r for r in refs)
        assert g4_10["evaluation_type"] == "deterministic"
        assert g4_10["requires_perception"] is False

    def test_g4_11_references_runtime_policy(self, g4_contract: dict) -> None:
        criteria = g4_contract["criteria"]
        g4_11 = next((c for c in criteria if c["id"] == "G4-11"), None)
        assert g4_11 is not None, "G4-11 criterion not found in contract"
        refs = g4_11.get("config_refs", [])
        assert any("narration-script-parameters" in r for r in refs)
        assert g4_11["evaluation_type"] == "deterministic"
        assert g4_11["requires_perception"] is False

    def test_g4_12_references_script_policy(self, g4_contract: dict) -> None:
        criteria = g4_contract["criteria"]
        g4_12 = next((c for c in criteria if c["id"] == "G4-12"), None)
        assert g4_12 is not None, "G4-12 criterion not found in contract"
        refs = g4_12.get("config_refs", [])
        assert any("narration-grounding-profiles" in r for r in refs)
        assert any("narration-script-parameters" in r for r in refs)
        assert g4_12["evaluation_type"] == "agentic"
        assert g4_12["requires_perception"] is True

    def test_g4_contract_includes_cluster_criteria_16_to_19(
        self,
        g4_contract: dict,
    ) -> None:
        criteria = {c["id"]: c for c in g4_contract["criteria"]}
        for criterion_id in ("G4-16", "G4-17", "G4-18", "G4-19"):
            assert criterion_id in criteria, f"{criterion_id} missing in G4 contract"
            assert criteria[criterion_id]["scope"] == "cluster"
            assert criteria[criterion_id]["severity"] == "high"
            assert criteria[criterion_id]["description"]
            assert criteria[criterion_id]["check_type"]
        assert criteria["G4-18"]["evaluation_type"] == "agentic"

    def test_vera_protocol_documents_g4_16_to_g4_19_cluster_extensions(
        self, vera_g4_protocol_text: str
    ) -> None:
        assert "G4-16" in vera_g4_protocol_text
        assert "G4-17" in vera_g4_protocol_text
        assert "G4-18" in vera_g4_protocol_text
        assert "G4-19" in vera_g4_protocol_text
        assert "master_behavioral_intent" in vera_g4_protocol_text
        assert "No new concepts" in vera_g4_protocol_text
        assert "Cluster arc integrity" in vera_g4_protocol_text

    def test_g4_07_only_applies_to_creative(self, g4_contract: dict) -> None:
        criteria = g4_contract["criteria"]
        g4_07 = next((c for c in criteria if c["id"] == "G4-07"), None)
        assert g4_07 is not None
        assert g4_07["fidelity_class"] == ["creative"]

    def test_profiles_min_source_claims_aligns_with_g407_intent(
        self, profiles: dict, g4_contract: dict
    ) -> None:
        """Creative profile min_source_claims >= 1 matches G4-07's requirement."""
        creative_min = profiles["profiles"]["creative"]["min_source_claims"]
        assert creative_min >= 1

    def test_source_depth_creative_default_not_describe_visual(self, params: dict) -> None:
        """Creative slides should default to teach_behind or full_synthesis, not describe_visual."""
        val = params["source_depth"]["creative_slides"]
        assert val != "describe_visual", "Creative slides must go deeper than describe_visual"

    def test_g4_criterion_ids_sequential(self, g4_contract: dict) -> None:
        """All G4 criteria IDs must be sequential G4-01, G4-02, ..., G4-NN."""
        ids = [c["id"] for c in g4_contract["criteria"]]
        expected = [f"G4-{str(i).zfill(2)}" for i in range(1, len(ids) + 1)]
        assert ids == expected

    def test_g4_ids_are_mirrored_in_vera_protocol(
        self,
        g4_contract: dict,
        vera_g4_protocol_text: str,
    ) -> None:
        criteria_ids = [c["id"] for c in g4_contract["criteria"]]
        for criterion_id in criteria_ids:
            assert criterion_id in vera_g4_protocol_text, f"{criterion_id} missing in Vera G4 protocol"
